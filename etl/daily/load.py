#!/usr/bin/env python3
import os
import sys
import logging
from dotenv import load_dotenv

# Add the etl directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.S3Config import S3Config
from config.SnowflakeConfig import SnowflakeConfig
from snowflake.snowflake_loader import SnowflakeLoader
from daily.load_pipeline import DailyETLPipelineLoad


def setup_logging():
    """Configure logging for the daily load pipeline"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('/tmp/fpl_daily_load.log')
        ]
    )


def load_s3_configuration():
    """Load S3 configuration from environment variables"""
    load_dotenv()
    
    # Required S3 environment variables
    bucket_name = os.getenv('S3_BUCKET_NAME')
    if not bucket_name:
        raise ValueError("S3_BUCKET_NAME environment variable is required")
    
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    if not aws_access_key_id or not aws_secret_access_key:
        raise ValueError("AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables are required")
    
    # Optional S3 environment variables
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    
    return S3Config(
        bucket_name=bucket_name,
        region=aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )


def load_snowflake_configuration():
    """Load Snowflake configuration from environment variables"""
    load_dotenv()
    
    # Required Snowflake environment variables
    required_vars = [
        'SNOWFLAKE_ACCOUNT',
        'SNOWFLAKE_USER', 
        'SNOWFLAKE_PASSWORD',
        'SNOWFLAKE_WAREHOUSE',
        'SNOWFLAKE_DATABASE',
        'SNOWFLAKE_SCHEMA'
    ]
    
    config_values = {}
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            raise ValueError(f"{var} environment variable is required")
        config_values[var.lower().replace('snowflake_', '')] = value
    
    # Optional Snowflake variables
    role = os.getenv('SNOWFLAKE_ROLE')
    if role:
        config_values['role'] = role
    
    return SnowflakeConfig(**config_values)


def main():
    """Main entry point for daily load pipeline"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    pipeline = None
    
    try:
        logger.info("Starting FPL Daily Load Pipeline")
        
        # Load configurations
        s3_config = load_s3_configuration()
        snowflake_config = load_snowflake_configuration()
        
        logger.info(f"Loaded S3 config for bucket: {s3_config.bucket_name}")
        logger.info(f"Loaded Snowflake config for account: {snowflake_config.account}")
        
        # Initialize components
        snowflake_loader = SnowflakeLoader(snowflake_config)
        
        # Create and run load pipeline
        pipeline = DailyETLPipelineLoad(
            snowflake_loader=snowflake_loader,
            s3_config=s3_config
        )
        
        result = pipeline.run()
        
        if result["success"]:
            logger.info(f"Daily load completed successfully!")
            logger.info(f"Rows loaded: {result['rows_loaded']}")
            logger.info(f"S3 file: {result['s3_file_path']}")
            logger.info(f"Load timestamp: {result['load_timestamp']}")
            sys.exit(0)
        else:
            logger.error(f"Daily load failed: {result['error']}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error in daily load pipeline: {str(e)}")
        sys.exit(1)
    
    finally:
        # Always close connections
        if pipeline:
            pipeline.close()


if __name__ == "__main__":
    main()