import sys
import os
import logging

# Add the etl directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from load.stage.bootstrap.pipeline import run_bootstrap_staging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_daily_load_pipelines():
    """Run all load pipelines in sequence."""
    logger.info("Starting bootstrap staging pipeline...")
    
    try:
        result = run_bootstrap_staging()
        if result.get("success", False):
            logger.info(f"✅ Bootstrap staging completed successfully - Rows loaded: {result.get('rows_loaded', 0)}")
        else:
            logger.error(f"❌ Bootstrap staging failed - Error: {result.get('error', 'Unknown error')}")
        logger.info(f"Pipeline result: {result}")

    except Exception as e:
        logger.error(f"❌ Bootstrap staging pipeline failed with exception: {e}")
        raise


if __name__ == "__main__":
    run_daily_load_pipelines()