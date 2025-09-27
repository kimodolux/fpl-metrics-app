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
    logger.info("[PIPELINE_START] DAILY EXTRACT - Starting extract staging pipeline")

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
            logger.info(f"[PIPELINE_COMPLETE] BOOTSTRAP EXTRACT - Completed successfully - Players: {result['players_count']}, Teams: {result['teams_count']}, Gameweeks: {result['gameweeks_count']}")
            logger.info(f"[STEP_COMPLETE] BOOTSTRAP EXTRACT - S3 upload - Path: {result['s3_path']}")
            logger.info(f"[STEP_COMPLETE] BOOTSTRAP EXTRACT - Extraction timestamp: {result['extraction_timestamp']}")
            return result
        else:
            logger.error(f"[PIPELINE_FAILED] BOOTSTRAP EXTRACT - {result['error']}")
            raise Exception(f"Bootstrap extract failed: {result['error']}")

    except Exception as e:
        logger.error(f"[PIPELINE_FAILED] BOOTSTRAP EXTRACT - Fatal error: {str(e)}")
        raise