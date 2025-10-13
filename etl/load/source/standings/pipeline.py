import sys
import os
import logging

# Add the etl directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from snowflake_client.snowflake_client import SnowflakeClient

logger = logging.getLogger(__name__)

def run_standings_source():
    """
    Execute standings dimension table creation and calculation pipeline

    1. Create DIM_STANDINGS table
    2. Truncate existing data
    3. Calculate standings from SOURCE_FIXTURES and SOURCE_TEAMS
    """

    snowflake_client = None
    result = {
        "success": False,
        "error": None,
        "rows_loaded": 0
    }

    try:
        # Initialize Snowflake client
        snowflake_client = SnowflakeClient()

        # Step 1: Create DIM_STANDINGS table
        logger.info("Creating DIM_STANDINGS table")
        snowflake_client.execute_sql_file("load/source/standings/create_dim_standings.sql")

        # Step 2: Clear existing data
        logger.info("Truncating DIM_STANDINGS table")
        snowflake_client.truncate_table("DIM_STANDINGS")

        # Step 3: Calculate standings from fixtures and teams
        logger.info("Calculating standings from SOURCE_FIXTURES and SOURCE_TEAMS")
        rows_affected = snowflake_client.execute_sql_file("load/source/standings/calculate_standings.sql")

        result["rows_loaded"] = rows_affected or 0
        result["success"] = True

        logger.info(f"Successfully calculated standings for {result['rows_loaded']} teams")

    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Standings source pipeline failed: {e}")
        raise

    finally:
        if snowflake_client:
            snowflake_client.close()

    return result

if __name__ == "__main__":
    run_standings_source()
