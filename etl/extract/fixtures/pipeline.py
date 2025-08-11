from datetime import datetime
from typing import Dict, Any
import logging
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


class FixturesETLPipelineExtract:
    def __init__(self, api_client, s3_client):
        self.api_client = api_client
        self.s3_client = s3_client
    
    def run(self) -> Dict[str, Any]:
        """Execute the fixtures ETL pipeline"""
        try:
            # Step 1: Fetch fixtures data from FPL API
            logger.info("Fetching fixtures data from FPL API...")
            fixtures_data = self.api_client.get_fixtures()
            
            if fixtures_data is None:
                return {
                    "success": False,
                    "error": "Failed to fetch fixtures data from FPL API"
                }
            
            # Step 2: Process fixtures data - the API returns a list directly
            if isinstance(fixtures_data, list):
                processed_data = {
                    "fixtures": fixtures_data,
                    "metadata": {
                        "total_fixtures": len(fixtures_data)
                    }
                }
            else:
                processed_data = fixtures_data
            
            # Step 3: Generate filename with timestamp
            now = datetime.now(ZoneInfo("Australia/Sydney"))
            filename = f"fixtures_{now.strftime('%Y%m%d')}.json"
            
            # Step 4: Save to S3 (S3DataLake will handle enrichment with timestamps)
            logger.info(f"Saving fixtures data to S3 with filename: {filename}")
            s3_path = self.s3_client.save_json(processed_data, "fixtures", filename)
            
            # Step 5: Calculate success metrics
            fixtures_count = len(fixtures_data) if isinstance(fixtures_data, list) else len(fixtures_data.get("fixtures", []))
            
            logger.info(f"Fixtures ETL completed successfully.")
            logger.info(f"Fixtures: {fixtures_count}")
            logger.info(f"S3 path: {s3_path}")
            
            return {
                "success": True,
                "data": processed_data,
                "fixtures_count": fixtures_count,
                "s3_path": s3_path,
                "extraction_timestamp": now.strftime("%Y-%m-%dT%H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Fixtures ETL pipeline failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }