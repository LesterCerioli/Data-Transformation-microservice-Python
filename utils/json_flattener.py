
from typing import Dict
from app.etl.transformers.data_lake_transformer import DataLakeTransformer


class JSONFlattenerTransformer(DataLakeTransformer):
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Recursively flatten nested dictionaries"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            elif isinstance(v, list):
                
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        items.extend(
                            self._flatten_dict(item, f"{new_key}_{i}", sep).items()
                        )
            else:
                items.append((new_key, v))
        return dict(items)

    def transform_api_data(self, *args, **kwargs) -> Dict:
        data = super().transform_api_data(*args, **kwargs)
        flattened = [self._flatten_dict(record) for record in data["data"]]
        data["data"] = flattened
        return data

