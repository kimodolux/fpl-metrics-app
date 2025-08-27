import sys
import os
import logging

# Add the etl directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from snowflake_client.snowflake_client import SnowflakeClient

logger = logging.getLogger(__name__)

def run_players_source():
    """
    Execute players source table creation and data loading pipeline
    
    1. Create source table
    2. Execute copy from stage with unflatten
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
        
        # Step 1: Create source table
        logger.info("Creating SOURCE_PLAYERS table")
        snowflake_client.execute_sql_file("load/source/players/create_players_table.sql")
        
        # Step 2: Clear existing data
        logger.info("Truncating SOURCE_PLAYERS table")
        snowflake_client.truncate_table("SOURCE_PLAYERS")
        
        # Step 3: Execute copy from stage with unflatten
        logger.info("Unflattening data from STAGING_BOOTSTRAP to SOURCE_PLAYERS")
        rows_affected = snowflake_client.execute_sql_file("load/source/players/unflatten_players_data.sql")
        
        result["rows_loaded"] = rows_affected or 0
        result["success"] = True
        
        logger.info(f"Successfully loaded {result['rows_loaded']} players records")
        
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Players source pipeline failed: {e}")
        raise
    
    finally:
        if snowflake_client:
            snowflake_client.close()
    
    return result

if __name__ == "__main__":
    run_players_source()