import logging
import sys
import os
from typing import Optional, Dict, Any

# Add the etl directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from load.snowflake_client import SnowflakeClient
from s3.s3_datalake import generate_config

logger = logging.getLogger(__name__)

def create_s3_stage(
    snowflake_client: SnowflakeClient,
    stage_name: str,
    bucket_name:str,
    file_format: Optional[Dict[str, str]] = None
) -> None:
    """Create or replace S3 stage for data loading"""
    default_format = {
        'TYPE': "'JSON'",
        'COMPRESSION': "'GZIP'"
    }

    s3config = generate_config()
    
    format_options = file_format or default_format
    format_clause = " ".join([f"{k} = {v}" for k, v in format_options.items()])
    
    create_stage_sql = f"""
    CREATE OR REPLACE STAGE {stage_name}
    URL = 's3://{bucket_name}/'
    CREDENTIALS = (
        AWS_KEY_ID = '{s3config.aws_access_key_id}'
        AWS_SECRET_KEY = '{s3config.aws_secret_access_key}'
    )
    FILE_FORMAT = ({format_clause})
    """
    
    try:
        logger.info(f"Creating S3 stage {stage_name} for bucket {bucket_name}")
        snowflake_client.execute_sql(create_stage_sql)
        logger.info(f"Successfully created S3 stage {stage_name}")
    except Exception as e:
        logger.error(f"Failed to create S3 stage {stage_name}: {e}")
        raise


def load_s3_to_staging(
    snowflake_client: SnowflakeClient,
    stage_name: str,
    s3_file_path: str,
    staging_table: str,
) -> int:
    """Load raw JSON from S3 into staging table"""

    copy_sql = f"""
    COPY INTO {staging_table} (raw_data, extraction_timestamp, extraction_date, s3_file_path)
    FROM (
        SELECT 
            parse_json($1),
            to_timestamp($1:extraction_timestamp),
            to_date($1:extraction_date),
            '{s3_file_path}'
        FROM @{stage_name}/{s3_file_path}
    )
    """
    
    try:
        logger.info(f"Loading {s3_file_path} into {staging_table}")
        rows_affected = snowflake_client.execute_sql(copy_sql)
        logger.info(f"Successfully loaded {rows_affected} rows from {s3_file_path}")
        return rows_affected or 0
    except Exception as e:
        logger.error(f"Failed to load {s3_file_path} into {staging_table}: {e}")
        raise


def load_s3_files_to_staging_pipeline(
    staging_table_sql_file: str,
    staging_table_name: str,
    s3_file_path: str,
    bucket_name: str,
    stage_name: str = "fpl_s3_stage",
) -> Dict[str, Any]:
    """
    Complete pipeline to load multiple S3 files into a staging table
    
    Args:
        staging_table_name: Name of the staging table
        s3_file_path: List of S3 file paths to load
        stage_name: Name for the Snowflake stage (default: fpl_s3_stage)
    
    Returns:
        Dict with pipeline results including total rows loaded and file results
    """
    
    snowflake_client = None
    result = {
        "success": False,
        "rows_loaded": 0,
        "error": None
    }
    
    try:
        # Initialize Snowflake client
        snowflake_client = SnowflakeClient()
        
        # Step 1: Create staging table
        snowflake_client.execute_sql_file(staging_table_sql_file)
        
        # Step 2: Clear staging table
        snowflake_client.truncate_table(staging_table_name)
        
        # Step 3: Create S3 stage
        create_s3_stage(
            snowflake_client,
            stage_name,
            bucket_name
        )
        
        try:
            rows_loaded = load_s3_to_staging(
                snowflake_client,
                stage_name,
                s3_file_path,
                staging_table_name
            )
            result["rows_loaded"] = rows_loaded
            result["success"] = True
        except Exception as e:
            logger.error(f"Failed to process file {s3_file_path}: {e}")
        
        
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Pipeline failed: {e}")
        raise
    
    finally:
        if snowflake_client:
            snowflake_client.close()
    
    return result