import snowflake.connector
import boto3
import logging
import os
from dataclasses import dataclass
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List


logger = logging.getLogger(__name__)

@dataclass
class SnowflakeConfig:
    """Snowflake configuration for data warehouse"""
    account: str
    user: str
    password: str
    warehouse: str
    database: str
    schema: str

def get_secret(parameter_name):
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(
        Name=parameter_name,
        WithDecryption=True
    )
    return response['Parameter']['Value']

class SnowflakeClient:
    """Generic Snowflake client for executing SQL and managing connections"""
    
    def __init__(self):
        self.connection = self._create_connection("prd")
    
    def _create_connection(self, env):
        """Create Snowflake connection using configuration"""
        if env == 'prd':
            connection_params = {
                'account': get_secret("SNOWFLAKE_ACCOUNT"),
                'user': get_secret("SNOWFLAKE_USER"),
                'password': get_secret("SNOWFLAKE_PASSWORD"),
                'warehouse': get_secret("SNOWFLAKE_WAREHOUSE"),
                'database': get_secret("SNOWFLAKE_DATABASE"),
                'schema': get_secret("SNOWFLAKE_SCHEMA"),
                'role': get_secret("SNOWFLAKE_ROLE"),
            }   
            return snowflake.connector.connect(**connection_params)

        else:

            load_dotenv()
            connection_params = {
                'account': os.getenv("SNOWFLAKE_ACCOUNT"),
                'user': os.getenv("SNOWFLAKE_USER"),
                'password': os.getenv("SNOWFLAKE_PASSWORD"),
                'warehouse': os.getenv("SNOWFLAKE_WAREHOUSE"),
                'database': os.getenv("SNOWFLAKE_DATABASE"),
                'schema': os.getenv("SNOWFLAKE_SCHEMA"),
                'role': os.getenv("SNOWFLAKE_ROLE"),
            }   
            return snowflake.connector.connect(**connection_params)
    
    def execute_sql(self, sql: str, params: Optional[tuple] = None) -> Optional[Any]:
        """Execute SQL and return results"""
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            # Return results if it's a SELECT statement
            if sql.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            
            # Return affected rows count for DML statements
            return cursor.rowcount
            
        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            logger.error(f"SQL: {sql}")
            raise
        finally:
            cursor.close()
    
    def execute_sql_file(self, sql_file_path: str, params: Optional[tuple] = None) -> Optional[Any]:
        """Execute SQL from a file"""
        try:
            with open(sql_file_path, 'r') as f:
                sql = f.read().strip()
            
            logger.info(f"Executing SQL file: {sql_file_path}")
            return self.execute_sql(sql, params)
            
        except FileNotFoundError:
            logger.error(f"SQL file not found: {sql_file_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading SQL file {sql_file_path}: {e}")
            raise
    
    def execute_multiple_sql_files(self, sql_files: List[str]) -> Dict[str, Any]:
        """Execute multiple SQL files and return results"""
        results = {}
        
        for sql_file in sql_files:
            try:
                result = self.execute_sql_file(sql_file)
                results[sql_file] = {"success": True, "result": result}
                logger.info(f"Successfully executed: {sql_file}")
            except Exception as e:
                results[sql_file] = {"success": False, "error": str(e)}
                logger.error(f"Failed to execute {sql_file}: {e}")
        
        return results
    
    def copy_into_table(self, table_name: str, stage_path: str, file_format: Optional[Dict[str, str]] = None) -> int:
        """Generic COPY INTO command for loading data from stage"""
        format_clause = ""
        if file_format:
            format_options = " ".join([f"{k} = {v}" for k, v in file_format.items()])
            format_clause = f"FILE_FORMAT = ({format_options})"
        
        copy_sql = f"""
        COPY INTO {table_name}
        FROM @{stage_path}
        {format_clause}
        """
        
        logger.info(f"Loading data into {table_name} from {stage_path}")
        return self.execute_sql(copy_sql)
    
    def get_row_count(self, table_name: str, where_clause: Optional[str] = None) -> int:
        """Get row count from a table with optional WHERE clause"""
        sql = f"SELECT COUNT(*) FROM {table_name}"
        if where_clause:
            sql += f" WHERE {where_clause}"
        
        result = self.execute_sql(sql)
        return result[0][0] if result else 0
    
    def truncate_table(self, table_name: str) -> None:
        """Truncate a table"""
        sql = f"TRUNCATE TABLE {table_name}"
        logger.info(f"Truncating table: {table_name}")
        self.execute_sql(sql)
    
    def close(self):
        """Close Snowflake connection"""
        if self.connection:
            self.connection.close()
            logger.info("Closed Snowflake connection")