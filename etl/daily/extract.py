#!/usr/bin/env python3
import os
import sys
import logging
from dotenv import load_dotenv

# Add the etl directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.S3Config import S3Config
from s3.s3_datalake import S3DataLake
from api.fpl_client import FPLAPIClient
from daily.extract_pipeline import DailyETLPipelineExtract


def setup_logging():
    """Configure logging for the daily pipeline"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('/tmp/fpl_daily_etl.log')
        ]
    )


def load_configuration():
    """Load configuration from environment variables"""
    load_dotenv()
    
    # Required environment variables
    bucket_name = os.getenv('S3_BUCKET_NAME')
    if not bucket_name:
        raise ValueError("S3_BUCKET_NAME environment variable is required")
    
    # Optional environment variables
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    return S3Config(
        bucket_name=bucket_name,
        region=aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )


def main():
    """Main entry point for daily ETL pipeline"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting FPL Daily ETL Pipeline")
        
        # Load configuration
        s3_config = load_configuration()
        logger.info(f"Loaded configuration for bucket: {s3_config.bucket_name}")
        
        # Initialize components
        api_client = FPLAPIClient(
            rate_limit_delay=0.2,  # Be respectful with single daily request
            max_retries=3
        )
        s3_client = S3DataLake(s3_config)
        
        # Run daily pipeline
        pipeline = DailyETLPipelineExtract(api_client=api_client, s3_client=s3_client)
        result = pipeline.run()
        
        if result["success"]:
            logger.info(f"Daily ETL completed successfully!")
            logger.info(f"Players processed: {result['players_count']}")
            logger.info(f"S3 path: {result['s3_path']}")
            logger.info(f"Extraction timestamp: {result['extraction_timestamp']}")
            sys.exit(0)
        else:
            logger.error(f"Daily ETL failed: {result['error']}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error in daily ETL: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()