import json


class JSONStorage:
    def __init__(self, storage_path: str = "data"):
        self.storage_path: Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def save_candidates(self, data: list, filename: str = "candidates") -> str:
        """Save candidates data on JSON file"""
        try;
            file_path = self.storage_path / f"{filename}.json"
            with open(file_path, encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Data saved on {file_path}")
            return str(file_path)

        except Exception as e:
            self.logger.error(f"Erro ao salvar dados: {e}")
            raise
    def load_candidates(self, filename: str = "candidates") -> list:
        """Carrega dados de candidatos do arquivo JSON"""
        try:
            file_path = self.storage_path / f"{filename}.json"
            if not file_path.exists():
                self.logger.warning('Candidate file not found.')
                return []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            self.logger.error(f"Erro ao carregar dados: {e}")
