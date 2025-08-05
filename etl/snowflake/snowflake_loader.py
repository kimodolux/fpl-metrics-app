import snowflake.connector
import logging
import os
from config.SnowflakeConfig import SnowflakeConfig

logger = logging.getLogger(__name__)


class SnowflakeLoader:
    def __init__(self, config: SnowflakeConfig):
        self.config = config
        self.connection = self._create_connection()
        self.bucket_name = None  # Will be set when creating S3 stage
        self.sql_dir = os.path.join(os.path.dirname(__file__), 'sql')
    
    def _read_sql_file(self, filename: str) -> str:
        """Read SQL content from a file in the sql directory"""
        file_path = os.path.join(self.sql_dir, filename)
        try:
            with open(file_path, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            logger.error(f"SQL file not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading SQL file {file_path}: {e}")
            raise
    
    def _create_connection(self):
        """Create Snowflake connection using configuration"""
        connection_params = {
            'account': self.config.account,
            'user': self.config.user,
            'password': self.config.password,
            'warehouse': self.config.warehouse,
            'database': self.config.database,
            'schema': self.config.schema
        }
        
        if self.config.role:
            connection_params['role'] = self.config.role
            
        return snowflake.connector.connect(**connection_params)
    
    def ensure_bootstrap_table_exists(self):
        """Create both staging and final bootstrap tables if they don't exist"""
        # Read SQL from external files
        create_staging_table_sql = self._read_sql_file('create_bootstrap_staging.sql')
        create_final_table_sql = self._read_sql_file('create_bootstrap_raw.sql')
        
        cursor = self.connection.cursor()
        try:
            cursor.execute(create_staging_table_sql)
            logger.info("Ensured fpl_bootstrap_staging table exists")
            cursor.execute(create_final_table_sql)
            logger.info("Ensured fpl_bootstrap_raw table exists")
            
            # Create transformed table
            self._ensure_transformed_table_exists(cursor)
        finally:
            cursor.close()
    
    def _ensure_transformed_table_exists(self, cursor):
        """Create transformed table with same structure as raw table"""
        create_transformed_table_sql = self._read_sql_file('create_bootstrap_transformed.sql')
        
        cursor.execute(create_transformed_table_sql)
        logger.info("Ensured fpl_bootstrap_transformed table exists")
    
    def create_s3_stage(self, bucket_name: str, aws_key_id: str, aws_secret_key: str):
        """Create or replace S3 stage for data loading"""
        self.bucket_name = bucket_name
        
        create_stage_sql = f"""
        CREATE OR REPLACE STAGE fpl_s3_stage
        URL = 's3://{bucket_name}/'
        CREDENTIALS = (
            AWS_KEY_ID = '{aws_key_id}'
            AWS_SECRET_KEY = '{aws_secret_key}'
        )
        FILE_FORMAT = (TYPE = 'JSON' COMPRESSION = 'GZIP')
        """
        
        cursor = self.connection.cursor()
        try:
            cursor.execute(create_stage_sql)
            logger.info(f"Created S3 stage for bucket: {bucket_name}")
        finally:
            cursor.close()
    
    def load_bootstrap_file(self, s3_file_path: str):
        """Load a single bootstrap file from S3 into Snowflake table using two-step process"""
        if not self.bucket_name:
            raise ValueError("S3 stage not created. Call create_s3_stage() first.")
        
        cursor = self.connection.cursor()
        try:
            # Step 1: Clear staging table and load raw JSON
            logger.info("Clearing staging table...")
            cursor.execute("TRUNCATE TABLE fpl_bootstrap_staging")
            
            # Step 2: Load JSON into staging table
            copy_into_staging_sql = f"""
            COPY INTO fpl_bootstrap_staging (raw_data, extraction_timestamp, extraction_date, s3_file_path)
            FROM (
                SELECT 
                    parse_json($1),
                    to_timestamp($1:extraction_timestamp),
                    to_date($1:extraction_date),
                    's3://{self.bucket_name}/{s3_file_path}'
                FROM @fpl_s3_stage/{s3_file_path}
            )
            """
            
            logger.info("Loading JSON into staging table...")
            cursor.execute(copy_into_staging_sql)
            
            # Step 3: Insert from staging into final table with column extraction
            insert_raw_sql = self._read_sql_file('update_bootstrap_raw.sql')
            
            logger.info("Inserting flattened data into raw table...")
            cursor.execute(insert_raw_sql)
            
            # Get row count from final table for this load
            cursor.execute("SELECT COUNT(*) FROM fpl_bootstrap_raw WHERE s3_file_path = %s", (f's3://{self.bucket_name}/{s3_file_path}',))
            rows_loaded = cursor.fetchone()[0]
            
            logger.info(f"Loaded {rows_loaded} rows from {s3_file_path}")

            # Step 4: Run transformation
            transformed_rows = self.transform_bootstrap_data()
            
            logger.info(f"Transformed {transformed_rows} rows")
            
            return rows_loaded
            
        finally:
            cursor.close()
    
    def transform_bootstrap_data(self):
        cursor = self.connection.cursor()
        try:
            # Read transformation SQL from external file
            transform_sql = self._read_sql_file('update_bootstrap_transformed.sql')
            
            logger.info("Running transformation step...")    
            cursor.execute(transform_sql)
            
            # Get count of transformed rows for today's data
            cursor.execute("SELECT COUNT(*) FROM fpl_bootstrap_transformed WHERE DATE(extraction_date) = CURRENT_DATE()")
            transformed_rows = cursor.fetchone()[0]
            
            return transformed_rows
            
        finally:
            cursor.close()
    
    def close(self):
        """Close Snowflake connection"""
        if self.connection:
            self.connection.close()
            logger.info("Closed Snowflake connection")