from datetime import datetime
from typing import Dict, Any
import logging
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


class BootstrapETLPipelineExtract:
    def __init__(self, api_client, s3_client):
        self.api_client = api_client
        self.s3_client = s3_client
    
    def run(self) -> Dict[str, Any]:
        """Execute the bootstrap ETL pipeline"""
        try:
            # Step 1: Fetch bootstrap data from FPL API
            logger.info("[STEP] BOOTSTRAP EXTRACT - Fetching bootstrap data from FPL API")
            bootstrap_data = self.api_client.get_bootstrap_data()
            
            if bootstrap_data is None:
                logger.error("[STEP_FAILED] BOOTSTRAP EXTRACT - Failed to fetch bootstrap data from FPL API")
                return {
                    "success": False,
                    "error": "Failed to fetch bootstrap data from FPL API"
                }
            
            # Step 2: Generate filename with timestamp
            now = datetime.now(ZoneInfo("Australia/Sydney"))
            filename = f"bootstrap_{now.strftime('%Y%m%d')}.json"
            
            # Step 3: Save to S3 (S3DataLake will handle enrichment with timestamps)
            logger.info(f"[STEP] BOOTSTRAP EXTRACT - Saving bootstrap data to S3 with filename: {filename}")
            s3_path = self.s3_client.save_json(bootstrap_data, "bootstrap", filename)
            
            # Step 4: Calculate success metrics
            players_count = len(bootstrap_data.get("elements", []))
            teams_count = len(bootstrap_data.get("teams", []))
            gameweeks_count = len(bootstrap_data.get("events", []))
            
            logger.info(f"[STEP_COMPLETE] BOOTSTRAP EXTRACT - Data processing completed - Players: {players_count}, Teams: {teams_count}, Gameweeks: {gameweeks_count}")
            logger.info(f"[STEP_COMPLETE] BOOTSTRAP EXTRACT - S3 upload completed - Path: {s3_path}")
            
            return {
                "success": True,
                "data": bootstrap_data,
                "players_count": players_count,
                "teams_count": teams_count,
                "gameweeks_count": gameweeks_count,
                "s3_path": s3_path,
                "extraction_timestamp": now.strftime("%Y-%m-%dT%H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"[PIPELINE_FAILED] BOOTSTRAP EXTRACT - {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }