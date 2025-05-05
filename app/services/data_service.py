import requests
from typing import Dict, List, Optional
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
from functools import partial

class CandidateDataService:
    def __init__(self, 
                 base_api_url: str,
                 poll_interval: int = 60,
                 max_workers: int = None):
        """
        Initialize the data service with configurable parallel processing
        
        Args:
            base_api_url: Base URL of the Next.js API
            poll_interval: Seconds between polling for new data
            max_workers: Number of parallel workers (defaults to CPU count * 2)
        """
        self.base_api_url = base_api_url.rstrip('/')
        self.poll_interval = poll_interval
        self.max_workers = max_workers or multiprocessing.cpu_count() * 2
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self._setup_session()
        self.logger.info(f"Initialized with {self.max_workers} workers")

    def _setup_session(self):
        """Configure common headers for API requests"""
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "CandidateDataService/1.0"
        })

    def fetch_candidates_by_lastname(self, last_name: str) -> List[Dict]:
        """
        Fetch candidates from Next.js API by last name
        
        Args:
            last_name: Last name to search for
            
        Returns:
            List of candidate dictionaries
        """
        try:
            url = f"{self.base_api_url}/candidates/{last_name}"
            self.logger.info(f"Fetching candidates from: {url}")
            
            response = self.session.get(
                url,
                timeout=10
            )
            response.raise_for_status()
            
            candidates = response.json()
            self.logger.info(f"Found {len(candidates)} candidates for last name '{last_name}'")
            return candidates
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed for last name '{last_name}': {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching candidates: {e}")
            raise

    def process_candidates(self, raw_candidates: List[Dict], batch_size: int = 100) -> List[Dict]:
        """
        Process candidates with automatic batch parallelization
        
        Args:
            raw_candidates: List of raw candidate dictionaries
            batch_size: Number of candidates per batch (default 100)
            
        Returns:
            List of processed candidates with error handling
        """
        if not raw_candidates:
            return []

        # Process in parallel batches
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            batches = [
                raw_candidates[i:i + batch_size] 
                for i in range(0, len(raw_candidates), batch_size)
            ]
            
            process_func = partial(self._process_batch, logger=self.logger)
            futures = [executor.submit(process_func, batch) for batch in batches]
            
            results = []
            for future in as_completed(futures):
                try:
                    results.extend(future.result())
                except Exception as e:
                    self.logger.error(f"Batch processing failed: {e}")
        
        return results

    @staticmethod
    def _process_batch(batch: List[Dict], logger: logging.Logger = None) -> List[Dict]:
        """Process a single batch of candidates"""
        processed = []
        for candidate in batch:
            try:
                processed.append(CandidateDataService._process_candidate(candidate))
            except Exception as e:
                if logger:
                    logger.warning(f"Error processing candidate {candidate.get('id')}: {e}")
                processed.append({
                    "id": candidate.get("id"),
                    "error": str(e),
                    "originalData": candidate
                })
        return processed

    @staticmethod
    def _process_candidate(candidate: Dict) -> Dict:
        """Process a single candidate with all fields from Next.js API"""
        processed = {
            "id": CandidateDataService._get_clean_value(candidate, "id"),
            "cpf": CandidateDataService._get_clean_value(candidate, "cpf"),
            "firstName": CandidateDataService._get_clean_value(candidate, "firstName"),
            "lastName": CandidateDataService._get_clean_value(candidate, "lastName"),
            "fullName": f"{candidate.get('firstName', '').strip()} {candidate.get('lastName', '').strip()}".strip(),
            "email": CandidateDataService._normalize_email(candidate.get("email")),
            "telephone": CandidateDataService._format_phone(candidate.get("telephone")),
            "city": CandidateDataService._get_clean_value(candidate, "city"),
            "state": CandidateDataService._normalize_state(candidate.get("state")),
            "country": CandidateDataService._normalize_country(candidate.get("country")),
            "createdAt": CandidateDataService._parse_date(candidate.get("createdAt")),
            "updatedAt": CandidateDataService._parse_date(candidate.get("updatedAt")),
            "processedAt": datetime.now().isoformat(),
            "_originalData": {
                k: v for k, v in candidate.items() 
                if k not in ['id', 'firstName', 'lastName', 'email', 
                            'telephone', 'city', 'state', 'country', 'cpf',
                            'createdAt', 'updatedAt']
            }
        }
                
        required_fields = ['id', 'firstName', 'lastName', 'cpf']
        for field in required_fields:
            if not processed.get(field):
                raise ValueError(f"Missing required field: {field}")
                
        return processed

    @staticmethod
    def _get_clean_value(data: Dict, key: str, default: Optional[str] = None) -> Optional[str]:
        """Clean and get a value from dictionary"""
        value = data.get(key, default)
        return value.strip() if isinstance(value, str) else value

    @staticmethod
    def _normalize_email(email: Optional[str]) -> Optional[str]:
        """Normalize email address"""
        if not email:
            return None
        return email.lower().strip()

    @staticmethod
    def _format_phone(phone: Optional[str]) -> Optional[str]:
        """Format phone number consistently"""
        if not phone:
            return None
            
        digits = ''.join(filter(str.isdigit, str(phone)))
        
        if len(digits) == 11:  # Brazilian format with DDD + 9 digits
            return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
        elif len(digits) == 10:  # Brazilian format with DDD + 8 digits
            return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
        return digits

    @staticmethod
    def _normalize_state(state: Optional[str]) -> Optional[str]:
        """Normalize state to 2-letter uppercase code"""
        if not state:
            return None
        return str(state).upper().strip()[:2]

    @staticmethod
    def _normalize_country(country: Optional[str]) -> str:
        """Normalize country name"""
        if not country:
            return "Brasil"
        country = str(country).strip().lower()
        return "Brasil" if country in ("br", "brasil", "brazil") else country.title()

    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[str]:
        """Parse and standardize date format"""
        if not date_str:
            return None
            
        try:
            if 'Z' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00')).isoformat()
            return datetime.fromisoformat(date_str).isoformat()
        except (ValueError, AttributeError):
            return date_str