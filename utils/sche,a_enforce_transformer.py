from typing import Dict


class SchemaEnforcerTransformer(DataLakeTransformer):
    def __init__(self, extractor: UniversalDataExtractor, schema: Dict):
        super().__init__(extractor)
        self.schema = schema  # Example: {"id": "int", "name": "str", "timestamp": "datetime"}

    def _enforce_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply schema rules to DataFrame"""
        for column, dtype in self.schema.items():
            if column not in df.columns:
                raise ValueError(f"Missing required column: {column}")
            if dtype == "datetime":
                df[column] = pd.to_datetime(df[column], errors="coerce")
            else:
                df[column] = df[column].astype(dtype, errors="ignore")
        return df

    def transform_api_data(self, *args, **kwargs) -> Dict:
        data = super().transform_api_data(*args, **kwargs)
        data["data"] = self._enforce_schema(pd.DataFrame(data["data"])).to_dict("records")
        return data