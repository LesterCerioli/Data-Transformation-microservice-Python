import requests
from typing import Dict, List, Any, Optional, Union
import logging
from urllib.parse import urljoin

class UniversalDataExtractor:
    def __init__(self):
        """
        Universal extractor for any type of data
        """
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        self._setup_session()

    def _setup_session(self):
        """Configure default headers"""
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "UniversalExtractor/1.0"
        })

    def from_api(
        self,
        base_url: str,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        auth: Optional[tuple] = None
    ) -> Union[List[Dict], Dict]:
        """
        Extract data from any REST API
        
        Args:
            base_url: Base URL (e.g., 'https://api.example.com')
            endpoint: Resource path (e.g., '/products')
            params: Query parameters (optional)
            headers: Custom headers (optional)
            auth: (username, password) tuple for basic auth (optional)
        
        Returns:
            Raw API data (list or dict)
        """
        url = urljoin(base_url, endpoint)
        
        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                auth=auth,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            raise

    def from_database(
        self,
        query: str,
        db_connection: Any  # Could be SQLAlchemy, psycopg2, etc.
    ) -> List[Dict]:
        """
        Extract data from any database
        
        Args:
            query: SQL query or similar
            db_connection: Database connection
            
        Returns:
            List of records
        """
        try:
            
            cursor = db_connection.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        except Exception as e:
            self.logger.error(f"Database extraction failed: {e}")
            raise

    def from_file(
        self,
        file_path: str,
        file_type: str = 'json'  # json, csv, parquet, etc.
    ) -> Any:
        """
        Extract data from local/remote files
        
        Args:
            file_path: File path or URL
            file_type: File type (json/csv/parquet)
            
        Returns:
            Parsed file contents
            
        Raises:
            ValueError: If unsupported file type is provided
            Exception: For file loading errors
        """
        file_handlers = {
            'json': lambda: self._load_json(file_path),
            'csv': lambda: self._load_csv(file_path),
            
        }
        
        try:
            handler = file_handlers.get(file_type.lower())
            if handler is None:
                raise ValueError(f"Unsupported file type: {file_type}")
            return handler()
        except Exception as e:
            self.logger.error(f"File extraction failed: {e}")
            raise

    def _load_json(self, file_path: str) -> Any:
        """Load JSON file"""
        import json
        with open(file_path) as f:
            return json.load(f)

    def _load_csv(self, file_path: str) -> List[Dict]:
        """Load CSV file"""
        import pandas as pd
        return pd.read_csv(file_path).to_dict('records')

    def close(self):
        """Release resources"""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()