import requests
import time
import logging
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class FPLAPIClient:
    def __init__(
            self,
            base_url: str = "https://fantasy.premierleague.com/api", 
            rate_limit_delay: float = 0.1,
            max_retries: int = 3
        ):
        self.base_url = base_url
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FPL-ETL-Pipeline/1.0'
        })
    
    def get_with_retry(self, url: str) -> Optional[Dict]:
        """Get data from URL with retry logic and exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                time.sleep(self.rate_limit_delay)
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == self.max_retries - 1:
                    logger.error(f"All attempts failed for {url}")
                    return None
                time.sleep(2 ** attempt)
        return None
    
    def get_bootstrap_data(self) -> Optional[Dict]:
        """Fetch bootstrap-static data containing all player information"""
        url = f"{self.base_url}/bootstrap-static/"
        logger.info("Fetching bootstrap data...")
        return self.get_with_retry(url)
    
    def get_player_details(self, player_id: int) -> Optional[Dict]:
        """Fetch detailed data for a specific player"""
        url = f"{self.base_url}/element-summary/{player_id}/"
        return self.get_with_retry(url)
    
    def get_fixtures(self) -> Optional[Dict]:
        """Fetch fixture list for the season"""
        url = f"{self.base_url}/fixtures/"
        return self.get_with_retry(url)
    
    def get_multiple_players_parallel(
            self, player_ids: List[int], 
            max_workers: int = 10
        ) -> Dict[int, Dict]:
        """Fetch player details in parallel with thread pool"""
        results = {}
        failed_ids = []
        
        logger.info(f"Fetching details for {len(player_ids)} players with {max_workers} workers...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all requests
            future_to_id = {
                executor.submit(self.get_player_details, player_id): player_id 
                for player_id in player_ids
            }
            
            # Collect results
            for future in as_completed(future_to_id):
                player_id = future_to_id[future]
                try:
                    result = future.result()
                    if result:
                        results[player_id] = result
                    else:
                        failed_ids.append(player_id)
                except Exception as e:
                    logger.error(f"Error fetching player {player_id}: {e}")
                    failed_ids.append(player_id)
        
        if failed_ids:
            logger.warning(f"Failed to fetch {len(failed_ids)} players: {failed_ids[:10]}...")
        
        logger.info(f"Successfully fetched {len(results)} player details")
        return results