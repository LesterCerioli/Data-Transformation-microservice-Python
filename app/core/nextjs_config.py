

import os
from urllib.parse import urljoin


class NextJsConfig:
    def __init__(self):
        self.BASE_URL = os.getenv("NEXT_PUBLIC_API_BASE_URL") 
        self.API_PATH = os.getenv("NEXT_API_CANDIDATES_PATH")  # Sem fallback!

        if not self.BASE_URL or not self.API_PATH:
            raise ValueError(
                "Variáveis de ambiente obrigatórias não definidas: "
                "NEXT_PUBLIC_API_BASE_URL e NEXT_API_CANDIDATES_PATH"
            )
    @property
    def full_url(self):
        return urljoin(self.BASE_URL, self.API_PATH)
    
    @property
    def candidates_path(self) -> str:
        return os.getenv("NEXT_API_CANDIDATES_PATH")
    
    @property
    def request_secret(self) -> str:
        return os.getenv("API_REQUEST_SECRET")  # Chave para validação
    

