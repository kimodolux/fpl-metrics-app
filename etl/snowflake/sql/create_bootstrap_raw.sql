CREATE TABLE IF NOT EXISTS fpl_bootstrap_raw (
    -- Metadata columns
    extraction_timestamp TIMESTAMP_NTZ,
    extraction_date DATE,
    s3_file_path STRING,
    
    -- Player identification
    player_id INTEGER,
    code INTEGER,
    web_name STRING,
    first_name STRING,
    second_name STRING,
    team INTEGER,
    team_code INTEGER,
    element_type INTEGER,
    
    -- Performance metrics
    total_points INTEGER,
    points_per_game FLOAT,
    minutes INTEGER,
    goals_scored INTEGER,
    assists INTEGER,
    clean_sheets INTEGER,
    goals_conceded INTEGER,
    
    -- Cost and ownership
    now_cost INTEGER,
    selected_by_percent FLOAT,
    transfers_in INTEGER,
    transfers_out INTEGER,
    transfers_in_event INTEGER,
    transfers_out_event INTEGER,
    
    -- Advanced stats
    influence FLOAT,
    creativity FLOAT,
    threat FLOAT,
    ict_index FLOAT,
    expected_goals FLOAT,
    expected_assists FLOAT,
    expected_goal_involvements FLOAT,
    expected_goals_conceded FLOAT,
    
    -- Status and availability
    status STRING,
    chance_of_playing_next_round INTEGER,
    chance_of_playing_this_round INTEGER,
    in_dreamteam BOOLEAN,
    dreamteam_count INTEGER,
    
    -- Performance indicators
    form FLOAT,
    event_points INTEGER,
    value_form FLOAT,
    value_season FLOAT,
    
    -- Additional metadata
    news STRING,
    news_added TIMESTAMP_NTZ,
    photo STRING,
    
    -- Cost change indicators
    cost_change_event INTEGER,
    cost_change_start INTEGER,
    cost_change_event_fall INTEGER,
    cost_change_start_fall INTEGER
)