import sys
import os
import logging

# Add the etl directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from load.source.events.pipeline import run_events_source
from load.source.fixtures.pipeline import run_fixtures_source
from load.source.player_fixtures.pipeline import run_player_fixtures_source
from load.source.player_history.pipeline import run_player_history_source
from load.source.players.pipeline import run_players_source
from load.source.teams.pipeline import run_teams_source
from load.source.transfer_history.pipeline import run_transfer_history_source

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_daily_load_pipelines():
    """Run all load pipelines in sequence."""
    logger.info("Starting transfer history source pipeline...")
    try:
        result = run_transfer_history_source()
        if result.get("success", False):
            logger.info(f"✅ Transfer history source completed successfully - Rows loaded: {result.get('rows_loaded', 0)}")
        else:
            logger.error(f"❌ Transfer history source failed - Error: {result.get('error', 'Unknown error')}")
        logger.info(f"Pipeline result: {result}")
    
    except Exception as e:
        logger.error(f"❌ Transfer history source pipeline failed with exception: {e}")
        raise


if __name__ == "__main__":
    run_daily_load_pipelines()