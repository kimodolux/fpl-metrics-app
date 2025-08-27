import sys
import os
import logging

# Add the etl directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from snowflake_client.snowflake_client import SnowflakeClient

logger = logging.getLogger(__name__)

def run_events_source():
    """
    Execute events source table creation and data loading pipeline
    
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
        logger.info("Creating SOURCE_EVENTS table")
        snowflake_client.execute_sql_file("load/source/events/create_events_table.sql")
        
        # Step 2: Clear existing data
        logger.info("Truncating SOURCE_EVENTS table")
        snowflake_client.truncate_table("SOURCE_EVENTS")
        
        # Step 3: Execute copy from stage with unflatten
        logger.info("Unflattening data from STAGING_BOOTSTRAP to SOURCE_EVENTS")
        rows_affected = snowflake_client.execute_sql_file("load/source/events/unflatten_events_data.sql")
        
        result["rows_loaded"] = rows_affected or 0
        result["success"] = True
        
        logger.info(f"Successfully loaded {result['rows_loaded']} events records")
        
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Events source pipeline failed: {e}")
        raise
    
    finally:
        if snowflake_client:
            snowflake_client.close()
    
    return result

if __name__ == "__main__":
    run_events_source()