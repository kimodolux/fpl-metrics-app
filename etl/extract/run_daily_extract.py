import os
import sys
import logging

# Add the etl directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from s3.s3_datalake import S3DataLake
from api.fpl_client import FPLAPIClient
from extract.player_details.pipeline import PlayerDetailsETLPipelineExtract
from extract.fixtures.pipeline import FixturesETLPipelineExtract
from extract.bootstrap.pipeline import BootstrapETLPipelineExtract

def run_daily_extract_pipelines():
    """Run all extract pipelines in sequence."""
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.info("Starting extract staging pipeline...")

    s3_client = S3DataLake()
    api_client = FPLAPIClient(
        rate_limit_delay=0.05,
        max_retries=3
    )

    try:
        # Run Bootstrap pipeline
        pipeline = BootstrapETLPipelineExtract(api_client=api_client, s3_client=s3_client)
        result = pipeline.run()
        if result["success"]:
            logger.info(f"Bootstrap ETL completed successfully!")
            logger.info(f"Players processed: {result['players_count']}")
            logger.info(f"Teams processed: {result['teams_count']}")
            logger.info(f"Gameweeks processed: {result['gameweeks_count']}")
            logger.info(f"S3 path: {result['s3_path']}")
            logger.info(f"Extraction timestamp: {result['extraction_timestamp']}")
            sys.exit(0)
        else:
            logger.error(f"Bootstrap ETL failed: {result['error']}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error in Bootstrap ETL: {str(e)}")
        sys.exit(1)