from datetime import datetime
from typing import Dict, Any
import logging
from zoneinfo import ZoneInfo
from snowflake.snowflake_loader import SnowflakeLoader
from config.S3Config import S3Config

logger = logging.getLogger(__name__)


class DailyETLPipelineLoad:
    def __init__(self, snowflake_loader: SnowflakeLoader, s3_config: S3Config):
        self.snowflake_loader = snowflake_loader
        self.s3_config = s3_config
        
        # Initialize Snowflake infrastructure
        self._setup_snowflake_infrastructure()
    
    def _setup_snowflake_infrastructure(self):
        """Set up Snowflake tables and S3 stage"""
        logger.info("Setting up Snowflake infrastructure...")
        
        # Ensure bootstrap table exists
        self.snowflake_loader.ensure_bootstrap_table_exists()
        
        # Create S3 stage for data loading
        if not self.s3_config.aws_access_key_id or not self.s3_config.aws_secret_access_key:
            raise ValueError("AWS credentials are required for S3 stage creation")
            
        self.snowflake_loader.create_s3_stage(
            bucket_name=self.s3_config.bucket_name,
            aws_key_id=self.s3_config.aws_access_key_id,
            aws_secret_key=self.s3_config.aws_secret_access_key
        )
        
        logger.info("Snowflake infrastructure setup complete")
    
    def generate_todays_s3_path(self) -> str:
        """Generate S3 file path for today's bootstrap extract"""
        now = datetime.now(ZoneInfo("Australia/Sydney"))
        
        # Assume extract runs at 7 AM daily - files are now compressed with gzip
        filename = f"bootstrap_{now.strftime('%Y%m%d')}.json.gz"
        s3_path = f"{self.s3_config.prefix}/bootstrap/year={now.year}/month={now.month:02d}/day={now.day:02d}/{filename}"
        
        return s3_path
    
    def load_file(self, s3_file_path: str) -> Dict[str, Any]:
        """Load a specific S3 file into Snowflake"""
        try:
            logger.info(f"Loading file from S3: {s3_file_path}")
            
            rows_loaded = self.snowflake_loader.load_bootstrap_file(s3_file_path)
            
            logger.info(f"Successfully loaded {rows_loaded} rows from {s3_file_path}")
            
            return {
                "success": True,
                "rows_loaded": rows_loaded,
                "s3_file_path": s3_file_path
            }
            
        except Exception as e:
            logger.error(f"Failed to load file {s3_file_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "s3_file_path": s3_file_path
            }
    
    def run(self) -> Dict[str, Any]:
        """Run complete load pipeline for today's extracted data"""
        try:
            # Generate path for today's extract
            s3_file_path = self.generate_todays_s3_path()
            
            logger.info(f"Starting daily load pipeline for: {s3_file_path}")
            
            # Load the file
            result = self.load_file(s3_file_path)
            
            if result["success"]:
                # Add load metadata
                result["load_timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                logger.info("Daily load pipeline completed successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"Daily load pipeline failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def close(self):
        """Close Snowflake connection"""
        self.snowflake_loader.close()