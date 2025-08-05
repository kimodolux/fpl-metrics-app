from datetime import datetime, date
from typing import Dict, Any, Optional
import logging
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


class DailyETLPipelineExtract:
    def __init__(self, api_client, s3_client):
        self.api_client = api_client
        self.s3_client = s3_client
    
    def run(self) -> Dict[str, Any]:
        """Execute the daily ETL pipeline"""
        try:
            # Step 1: Fetch bootstrap data from FPL API
            logger.info("Fetching bootstrap data from FPL API...")
            bootstrap_data = self.api_client.get_bootstrap_data()
            
            if bootstrap_data is None:
                return {
                    "success": False,
                    "error": "Failed to fetch bootstrap data from FPL API"
                }
            
            # Step 2: Generate filename with timestamp
            now = datetime.now(ZoneInfo("Australia/Sydney"))
            filename = f"bootstrap_{now.strftime('%Y%m%d')}.json"
            
            # Step 3: Save to S3 (S3DataLake will handle enrichment)
            logger.info(f"Saving bootstrap data to S3 with filename: {filename}")
            s3_path = self.s3_client.save_json(bootstrap_data, "bootstrap", filename)
            
            # Step 5: Calculate success metrics
            players_count = len(bootstrap_data.get("elements", []))
            
            logger.info(f"Daily ETL completed successfully. Players: {players_count}, S3 path: {s3_path}")
            
            return {
                "success": True,
                "data": bootstrap_data,
                "players_count": players_count,
                "s3_path": s3_path,
                "extraction_timestamp": now.strftime("%Y-%m-%dT%H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Daily ETL pipeline failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }