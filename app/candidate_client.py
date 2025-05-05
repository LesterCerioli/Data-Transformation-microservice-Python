import requests
import hmac
import hashlib
import time
import logging
from config import AppConfig

class CandidateClient:
    def __init__(self):
        self.config = AppConfig()
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self):
        """Configure commons headers"""
        self.session.headers.update({
            "User-Agent": "LTS-Python-Client/1.0",
            "Accept": "application/json",
            "X-API-Source": "python-microservice"
        })

    def _generate_auth_headers(self, body: str) -> dict:
        """Generate authentication headers using environment variables"""
        timestamp = str(int(time.time()))
        signature = hmac.new(
            key=self.config.request_secret.encode(),
            msg=f"{timestamp}{body}".encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        return {
            "X-API-Signature": signature,
            "X-API-Timestamp": timestamp
        }

    def get_candidates(self) -> list:
        """Busca candidatos de forma segura"""
        try:
            body = ""  # Pode ser usado para assinar o corpo se necessário
            headers = self._generate_auth_headers(body)
            
            response = self.session.get(
                self.config.full_url,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as error:
            logging.error(f"Falha na requisição: {error}")
            raise