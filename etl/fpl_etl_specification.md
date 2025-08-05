# Fantasy Premier League ETL Implementation Specification

## Overview
Build a dual-mode ETL pipeline to collect Fantasy Premier League data for price change analysis. The system captures daily price/transfer data and weekly comprehensive player data, storing raw JSON in S3 and loading into Snowflake for analysis.

## Business Requirements

### Primary Goal
Track FPL player price changes to predict future price movements based on transfer patterns and performance data.

### Key Insights Needed
- Daily price changes and transfer momentum
- Player performance vs price correlations  
- Ownership trends and their impact on pricing
- Historical patterns for price change prediction

## Technical Architecture

```
FPL API → Raw JSON → S3 Data Lake → Snowflake → Analysis
```

### Data Sources
- **Daily**: `https://fantasy.premierleague.com/api/bootstrap-static/` (1 API call)
- **Weekly**: Bootstrap + `https://fantasy.premierleague.com/api/element-summary/{player_id}/` (~600 API calls)

### Storage Strategy
- **S3**: Partitioned by date (`year=2024/month=08/day=04/`)
- **Snowflake**: Raw JSON tables with analytical views
- **No preprocessing**: Store raw API responses directly

## Implementation Requirements

### 1. Daily ETL Pipeline
**Schedule**: Every day at 7:00 AM  
**Runtime**: ~30 seconds  
**API Calls**: 1 request  

**Process**:
1. Fetch bootstrap-static data
2. Add extraction metadata (timestamp, date)
3. Save raw JSON to S3: `s3://bucket/fpl-data/bootstrap/year=2024/month=08/day=04/bootstrap_20240804_070000.json`
4. Load into Snowflake table: `fpl_bootstrap_raw`

**Key Data Points Captured**:
- `now_cost` (player prices)
- `transfers_in_event`, `transfers_out_event` (daily transfers)
- `selected_by_percent` (ownership)
- `form`, `total_points` (performance)

### 2. Weekly ETL Pipeline  
**Schedule**: Every Monday at 6:00 AM  
**Runtime**: ~15 minutes  
**API Calls**: 600+ requests (1 bootstrap + 1 per player)

**Process**:
1. Fetch bootstrap-static data (get player IDs)
2. Fetch detailed data for each player in parallel
3. Save all raw JSON responses to S3
4. Load into Snowflake tables: `fpl_bootstrap_raw`, `fpl_players_raw`

**Additional Data Captured**:
- Match history (`history` array in player JSON)
- Upcoming fixtures (`fixtures` array)
- Detailed performance statistics

### 3. Infrastructure Requirements

#### S3 Configuration
- **Bucket Type**: General Purpose (not Directory buckets)
- **Lifecycle Policy**: 
  - Standard → Standard-IA (30 days)
  - Standard-IA → Glacier (90 days)
  - Glacier → Deep Archive (365 days)
- **Encryption**: Server-side encryption (SSE-S3)
- **Versioning**: Enabled
- **Expected Cost**: ~$0.01/month

#### Snowflake Setup
- **Database**: `FPL_DATA`
- **Schema**: `RAW` 
- **Warehouse**: Small size with auto-suspend
- **Expected Cost**: ~$4/month

#### AWS IAM Policy
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject", 
                "s3:ListBucket",
                "s3:GetBucketLocation"
            ],
            "Resource": [
                "arn:aws:s3:::your-fpl-data-lake",
                "arn:aws:s3:::your-fpl-data-lake/*"
            ]
        }
    ]
}
```

## Data Schema Design

### Raw Storage Tables

#### fpl_bootstrap_raw
```sql
CREATE TABLE fpl_bootstrap_raw (
    raw_data VARIANT,
    extraction_timestamp TIMESTAMP_NTZ,
    extraction_date DATE,
    s3_file_path STRING
);
```

#### fpl_players_raw  
```sql
CREATE TABLE fpl_players_raw (
    raw_data VARIANT,
    extraction_timestamp TIMESTAMP_NTZ,
    extraction_date DATE,
    s3_file_path STRING
);
```

### Analytical Views

#### fpl_daily_prices (View)
```sql
CREATE VIEW fpl_daily_prices AS
SELECT 
    extraction_date,
    player.value:id::INT as player_id,
    player.value:web_name::STRING as player_name,
    player.value:now_cost::INT / 10.0 as price_millions,
    player.value:transfers_in_event::INT as transfers_in_event,
    player.value:transfers_out_event::INT as transfers_out_event,
    (player.value:transfers_in_event::INT - player.value:transfers_out_event::INT) as net_transfers_event,
    player.value:selected_by_percent::FLOAT as ownership_percent,
    player.value:form::FLOAT as form,
    player.value:total_points::INT as total_points
FROM fpl_bootstrap_raw,
     LATERAL FLATTEN(input => raw_data:api_response:elements) as player;
```

#### fpl_price_changes (View)
```sql
CREATE VIEW fpl_price_changes AS
SELECT 
    today.player_id,
    today.player_name,
    today.extraction_date,
    today.price_millions as current_price,
    yesterday.price_millions as previous_price,
    (today.price_millions - yesterday.price_millions) as price_change_millions
FROM fpl_daily_prices today
JOIN fpl_daily_prices yesterday 
    ON today.player_id = yesterday.player_id 
    AND yesterday.extraction_date = today.extraction_date - 1
WHERE today.price_millions != yesterday.price_millions;
```

## Technical Implementation Details

### Core Pipeline Components

#### 1. S3DataLake Class
**Responsibilities**:
- Generate partitioned S3 keys
- Save JSON with metadata enrichment
- Handle AWS credentials and client creation

**Key Methods**:
- `save_json(data, data_type, filename)` → returns S3 key
- `_generate_s3_key(data_type, filename)` → creates partition path

#### 2. FPLAPIClient Class
**Responsibilities**:
- HTTP requests with retry logic and rate limiting
- Parallel processing for weekly player data
- Error handling and logging

**Configuration**:
- Rate limit: 0.1-0.2 seconds between requests
- Max retries: 3 with exponential backoff
- Timeout: 30 seconds per request
- Max workers: 8 for weekly, 1 for daily

#### 3. SnowflakeLoader Class
**Responsibilities**:
- Create S3 stages and file formats
- Execute COPY INTO commands from S3
- Manage database connections

### Error Handling Strategy
- **API failures**: Log and continue (don't fail entire pipeline)
- **Partial data**: Accept incomplete datasets, track missing players
- **Retry logic**: Exponential backoff for transient failures
- **Monitoring**: Log success/failure rates, data volumes

### Rate Limiting & API Etiquette
- **Daily**: 0.2 second delays (respectful single requests)
- **Weekly**: 0.1 second delays (faster for bulk operations)  
- **User-Agent**: Include identifier for API monitoring
- **Circuit breaker**: Stop on consecutive failures

## Key Analytical Queries

### Price Change Detection
```sql
SELECT player_name, price_change_millions, extraction_date
FROM fpl_price_changes 
WHERE extraction_date >= CURRENT_DATE() - 7
ORDER BY ABS(price_change_millions) DESC;
```

### Transfer Momentum Analysis
```sql
SELECT 
    player_name,
    SUM(net_transfers_event) OVER (
        PARTITION BY player_id 
        ORDER BY extraction_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as transfers_7day
FROM fpl_daily_prices 
WHERE extraction_date = CURRENT_DATE() - 1
ORDER BY ABS(transfers_7day) DESC;
```

### Price Prediction Features
```sql  
SELECT 
    player_id,
    net_transfers_event,
    AVG(net_transfers_event) OVER (...) as transfers_3day_avg,
    ownership_percent - LAG(ownership_percent) OVER (...) as ownership_change,
    LEAD(price_millions) OVER (...) - price_millions as next_day_price_change
FROM fpl_daily_prices;
```

## Deployment Configuration

### Environment Variables
```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=AKIA........................
AWS_SECRET_ACCESS_KEY=abc123........................
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-fpl-data-lake

# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your-account.region.cloud
SNOWFLAKE_USER=fpl_etl_user
SNOWFLAKE_PASSWORD=strong_password
SNOWFLAKE_WAREHOUSE=FPL_ETL_WH
SNOWFLAKE_DATABASE=FPL_DATA
SNOWFLAKE_SCHEMA=RAW

# Pipeline Configuration
ETL_MODE=daily  # or weekly
PLAYER_LIMIT=50  # for testing only
```

### Dependencies
```
requests==2.31.0
boto3==1.28.17
snowflake-connector-python==3.3.1
python-dotenv==1.0.0
```

## Orchestration Options

### Option 1: Cron Jobs (Simple)
```bash
# Daily at 7 AM
0 7 * * * /usr/bin/python3 /path/to/pipeline.py daily

# Weekly on Monday at 6 AM  
0 6 * * 1 /usr/bin/python3 /path/to/pipeline.py weekly
```

### Option 2: Apache Airflow (Recommended)
- **Daily DAG**: Simple, 10-minute timeout
- **Weekly DAG**: Complex, 2-hour timeout, data quality checks
- **Monitoring**: Email alerts, success/failure tracking

## Success Criteria

### Technical Metrics
- **Daily pipeline**: >99% success rate, <2 minute runtime
- **Weekly pipeline**: >95% success rate, <20 minute runtime
- **Data completeness**: >98% of players captured daily
- **API reliability**: <1% 4xx/5xx error rate

### Business Metrics  
- **Price change detection**: Capture all daily changes within 24 hours
- **Prediction accuracy**: Baseline model >60% accuracy for next-day price changes
- **Data latency**: Analysis available within 2 hours of FPL updates

## Monitoring & Maintenance

### Data Quality Checks
```sql
-- Daily data freshness
SELECT MAX(extraction_date), COUNT(*) FROM fpl_daily_prices;

-- Missing players detection  
SELECT COUNT(DISTINCT player_id) FROM fpl_daily_prices 
WHERE extraction_date = CURRENT_DATE() - 1;

-- Price change anomalies
SELECT COUNT(*) FROM fpl_price_changes 
WHERE ABS(price_change_millions) > 0.5;  -- Unusually large changes
```

### Operational Tasks
- **Weekly**: Review failed API calls, data completeness
- **Monthly**: Rotate AWS access keys, review costs
- **Seasonally**: Archive old data, update player lists

## Expected Outcomes

### Data Volume
- **Daily**: ~500 player records, ~100KB JSON
- **Weekly**: ~500 players × 30 games history = ~15,000 records
- **Annual**: ~180 daily files + 52 weekly files = ~500MB total

### Cost Estimates
- **S3 storage**: $0.01/month
- **S3 requests**: $0.02/month  
- **Snowflake compute**: $4.00/month
- **Total**: ~$4/month

### Research Capabilities
- Price change pattern identification
- Transfer momentum modeling
- Performance-price correlation analysis
- Ownership trend impact quantification
- Multi-factor price prediction models

## Implementation Priority

1. **Phase 1** (Week 1): Daily pipeline, basic S3/Snowflake setup
2. **Phase 2** (Week 2): Weekly pipeline, comprehensive data collection  
3. **Phase 3** (Week 3): Analytical views, basic queries
4. **Phase 4** (Week 4+): Advanced analysis, prediction modeling

This specification provides complete technical requirements for implementing a production-ready FPL ETL pipeline focused on price change analysis and prediction research.