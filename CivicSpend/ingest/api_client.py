"""USAspending API client."""
import time
import requests
from typing import Dict, List, Optional
from datetime import datetime

API_BASE = "https://api.usaspending.gov/api/v2"
RATE_LIMIT_DELAY = 0.2  # 5 requests per second

class USAspendingClient:
    """Client for USAspending.gov API."""
    
    def __init__(self):
        self.session = requests.Session()
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Enforce rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()
    
    def _request(self, endpoint: str, payload: Dict, max_retries: int = 3) -> Dict:
        """Make API request with retry logic."""
        url = f"{API_BASE}/{endpoint}"
        
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                response = self.session.post(url, json=payload, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                wait = 2 ** attempt
                time.sleep(wait)
        
        return {}
    
    def fetch_awards(
        self,
        state: str,
        start_date: str,
        end_date: str,
        limit: int = 100,
        page: int = 1
    ) -> Dict:
        """Fetch awards for a state and date range."""
        payload = {
            "filters": {
                "time_period": [
                    {"start_date": start_date, "end_date": end_date}
                ],
                "place_of_performance_scope": "domestic",
                "place_of_performance_locations": [
                    {"state": state}
                ]
            },
            "page": page,
            "limit": limit,
            "sort": "Award Amount",
            "order": "desc"
        }
        
        return self._request("search/spending_by_award", payload)
