from datetime import datetime
from typing import Dict, Any
import logging
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


class PlayerDetailsETLPipelineExtract:
    def __init__(self, api_client, s3_client):
        self.api_client = api_client
        self.s3_client = s3_client
    
    def run(self) -> Dict[str, Any]:
        """Execute the player details ETL pipeline"""
        try:
            # Step 1: Fetch bootstrap data to get all player IDs
            logger.info("Fetching bootstrap data to get player IDs...")
            bootstrap_data = self.api_client.get_bootstrap_data()
            
            if bootstrap_data is None:
                return {
                    "success": False,
                    "error": "Failed to fetch bootstrap data from FPL API"
                }
            
            # Step 2: Extract player IDs from bootstrap data
            players = bootstrap_data.get("elements", [])
            player_ids = [player["id"] for player in players]
            
            logger.info(f"Found {len(player_ids)} players to fetch detailed data for")
            
            # Step 3: Fetch detailed player data in parallel
            logger.info("Fetching detailed player data...")
            player_details = self.api_client.get_multiple_players_parallel(
                player_ids=player_ids,
                max_workers=20  # Same as weekly for consistency
            )
            
            if not player_details:
                return {
                    "success": False,
                    "error": "No player details were successfully fetched"
                }
            
            # Step 4: Generate filename with timestamp
            now = datetime.now(ZoneInfo("Australia/Sydney"))
            filename = f"player_details_{now.strftime('%Y%m%d')}.json"
            
            # Step 5: Save to S3 (S3DataLake will handle enrichment with timestamps)
            logger.info(f"Saving {len(player_details)} player details to S3 with filename: {filename}")
            s3_path = self.s3_client.save_json(player_details, "player_details", filename)
            
            # Step 6: Calculate success metrics
            successful_players = len(player_details)
            failed_players = len(player_ids) - successful_players
            
            logger.info(f"Player Details ETL completed successfully.")
            logger.info(f"Players fetched: {successful_players}, Failed: {failed_players}")
            logger.info(f"S3 path: {s3_path}")
            
            return {
                "success": True,
                "data": player_details,
                "players_fetched": successful_players,
                "players_failed": failed_players,
                "total_players": len(player_ids),
                "s3_path": s3_path,
                "extraction_timestamp": now.strftime("%Y-%m-%dT%H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Player Details ETL pipeline failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }