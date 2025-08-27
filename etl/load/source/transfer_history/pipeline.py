import sys
import os
import logging

# Add the etl directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from snowflake_client.snowflake_client import SnowflakeClient

logger = logging.getLogger(__name__)

def run_transfer_history_source():
    """
    Execute transfer_history source table creation and data loading pipeline
    
    1. Create source table
    2. Insert daily transfer data (NO TRUNCATE - appends data)
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
        logger.info("Creating SOURCE_TRANSFER_HISTORY table")
        snowflake_client.execute_sql_file("load/source/transfer_history/create_transfer_history_table.sql")
        
        # Step 2: Insert daily transfer data (NO TRUNCATE)
        logger.info("Inserting daily transfer data from STAGING_BOOTSTRAP to SOURCE_TRANSFER_HISTORY")
        rows_affected = snowflake_client.execute_sql_file("load/source/transfer_history/insert_transfer_history_data.sql")
        
        result["rows_loaded"] = rows_affected or 0
        result["success"] = True
        
        logger.info(f"Successfully loaded {result['rows_loaded']} transfer history records")
        
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Transfer history source pipeline failed: {e}")
        raise
    
    finally:
        if snowflake_client:
            snowflake_client.close()
    
    return result

if __name__ == "__main__":
    run_transfer_history_source()