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

def run_weekly_extract_pipelines():
    """Run all extract pipelines in sequence."""

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.info("[PIPELINE_START] WEEKLY EXTRACT - Starting extract staging pipeline")

    s3_client = S3DataLake()
    api_client = FPLAPIClient(
        rate_limit_delay=0.05,
        max_retries=3
    )

    results = []

    try:
        # Run Bootstrap pipeline
        logger.info("[STEP] WEEKLY EXTRACT - Running Bootstrap pipeline")
        pipeline = BootstrapETLPipelineExtract(api_client=api_client, s3_client=s3_client)
        result = pipeline.run()
        if result["success"]:
            logger.info(f"[STEP_COMPLETE] BOOTSTRAP EXTRACT - Completed successfully - Players: {result['players_count']}, Teams: {result['teams_count']}, Gameweeks: {result['gameweeks_count']}")
            results.append(result)
        else:
            logger.error(f"[STEP_FAILED] BOOTSTRAP EXTRACT - {result['error']}")
            raise Exception(f"Bootstrap extract failed: {result['error']}")

        # Run fixtures pipeline
        logger.info("[STEP] WEEKLY EXTRACT - Running Fixtures pipeline")
        pipeline = FixturesETLPipelineExtract(api_client=api_client, s3_client=s3_client)
        result = pipeline.run()
        if result["success"]:
            logger.info(f"[STEP_COMPLETE] FIXTURES EXTRACT - Completed successfully - Fixtures: {result['fixtures_count']}")
            results.append(result)
        else:
            logger.error(f"[STEP_FAILED] FIXTURES EXTRACT - {result['error']}")
            raise Exception(f"Fixtures extract failed: {result['error']}")

        # Run player details pipeline
        logger.info("[STEP] WEEKLY EXTRACT - Running Player Details pipeline")
        pipeline = PlayerDetailsETLPipelineExtract(api_client=api_client, s3_client=s3_client)
        result = pipeline.run()
        if result["success"]:
            logger.info(f"[STEP_COMPLETE] PLAYER DETAILS EXTRACT - Completed successfully - Players fetched: {result['players_fetched']}, Failed: {result['players_failed']}")
            results.append(result)
        else:
            logger.error(f"[STEP_FAILED] PLAYER DETAILS EXTRACT - {result['error']}")
            raise Exception(f"Player details extract failed: {result['error']}")

        logger.info("[PIPELINE_COMPLETE] WEEKLY EXTRACT - All pipelines completed successfully")
        return {"success": True, "results": results}

    except Exception as e:
        logger.error(f"[PIPELINE_FAILED] WEEKLY EXTRACT - {str(e)}")
        raise


if __name__ == "__main__":
    run_weekly_extract_pipelines()