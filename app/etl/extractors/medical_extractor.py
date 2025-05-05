import requests
from typing import Dict, List, Optional, Union, Any
import logging
from urllib.parse import urljoin

from psycopg2 import connect
from elasticsearch import Elasticsearch
from datetime import datetime

class MedicalAppExtractor:
    def __init__(self, 
                 api_base_url: Optional[str] = None,
                 auth_token: Optional[str] = None,
                 pg_config: Optional[Dict] = None,
                 es_config: Optional[Dict] = None):
        """
        Multi-source medical data extractor
        
        Args:
            api_base_url: FHIR API base URL
            auth_token: OAuth2 token for API
            pg_config: PostgreSQL config dict
                {'host':'', 'port':'', 'dbname':'', 'user':'', 'password':''}
            es_config: Elasticsearch config dict
                {'hosts':[], 'http_auth':('user','pass')}
        """
        
        self.api_base_url = api_base_url
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
        
        self.pg_conn = None
        self.es_client = None
        
        if api_base_url and auth_token:
            self._setup_api_session(auth_token)
        if pg_config:
            self._setup_postgres(pg_config)
        if es_config:
            self._setup_elasticsearch(es_config)

    
    def _setup_api_session(self, auth_token: str):
        """Configure FHIR API session"""
        self.session.headers.update({
            "Accept": "application/fhir+json",
            "Authorization": f"Bearer {auth_token}",
            "User-Agent": "MedicalExtractor/3.0"
        })

    def get_fhir_resource(self, 
                         resource_type: str, 
                         params: Optional[Dict] = None) -> List[Dict]:
        """
        Generic FHIR resource extractor
        
        Args:
            resource_type: FHIR resource type (Patient, Observation, etc.)
            params: Search parameters
            
        Returns:
            List of processed resources
        """
        try:
            data = self._fhir_get(resource_type, params or {})
            return [self._process_resource(entry["resource"]) 
                   for entry in data.get("entry", [])]
        except Exception as e:
            self.logger.error(f"FHIR extraction failed: {e}")
            raise

    
    def _setup_postgres(self, config: Dict):
        """Initialize PostgreSQL connection"""
        try:
            self.pg_conn = connect(**config)
            self.logger.info("PostgreSQL connection established")
        except Exception as e:
            self.logger.error(f"PostgreSQL connection failed: {e}")
            raise

    def get_pg_medical_records(self,
                             query: str,
                             params: Optional[tuple] = None) -> List[Dict]:
        """
        Extract medical records from PostgreSQL
        
        Args:
            query: SQL query with parameter placeholders (%s)
            params: Query parameters
            
        Returns:
            List of records as dictionaries
        """
        if not self.pg_conn:
            raise ConnectionError("PostgreSQL not configured")
        
        try:
            with self.pg_conn.cursor() as cursor:
                cursor.execute(query, params or ())
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"PostgreSQL extraction failed: {e}")
            raise

    
    def _setup_elasticsearch(self, config: Dict):
        """Initialize Elasticsearch client"""
        try:
            self.es_client = Elasticsearch(**config)
            if self.es_client.ping():
                self.logger.info("Elasticsearch connection established")
            else:
                raise ConnectionError("Could not connect to Elasticsearch")
        except Exception as e:
            self.logger.error(f"Elasticsearch connection failed: {e}")
            raise

    def get_es_medical_data(self,
                          index: str,
                          query: Dict,
                          size: int = 100) -> List[Dict]:
        """
        Search medical data in Elasticsearch
        
        Args:
            index: Index/indices to search
            query: Elasticsearch query DSL
            size: Maximum results to return
            
        Returns:
            List of hit _source documents
        """
        if not self.es_client:
            raise ConnectionError("Elasticsearch not configured")
        
        try:
            response = self.es_client.search(
                index=index,
                body=query,
                size=size
            )
            return [hit["_source"] for hit in response["hits"]["hits"]]
        except Exception as e:
            self.logger.error(f"Elasticsearch query failed: {e}")
            raise

    
    def _fhir_get(self, endpoint: str, params: Dict) -> Dict:
        """Execute FHIR API request"""
        url = urljoin(f"{self.api_base_url}/", endpoint)
        response = self.session.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()

    def _process_resource(self, resource: Dict) -> Dict:
        """Standardize FHIR resource format"""
        resource_type = resource["resourceType"]
        
        if resource_type == "Patient":
            return self._sanitize_patient(resource)
        elif resource_type == "Observation":
            return self._transform_observation(resource)
        else:
            return resource  

    
    def close(self):
        """Clean up all connections"""
        if self.session:
            self.session.close()
        if self.pg_conn:
            self.pg_conn.close()
        if self.es_client:
            self.es_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()