
import hashlib
import pandas as pd
from typing import Dict, List
from app.etl.extractors.lucas_technology_service_extractor import UniversalDataExtractor
from app.etl.transformers.data_lake_transformer import DataLakeTransformer


class PrivateTransform(DataLakeTransformer):
    def __init__(self, extractor: UniversalDataExtractor, sensitive_fields: List[str]):
        """
        Transformer for handling sensitive data by hashing specified fields
        
        Args:
            extractor: Instance of UniversalDataExtractor
            sensitive_fields: List of field names containing sensitive data
        """
        super().__init__()
        self.extractor = extractor
        self.sensitive_fields = sensitive_fields
        
    def hash_sensitive_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Replace sensitive values with deterministic hashes
        
        Args:
            df: Input DataFrame containing sensitive data
            
        Returns:
            DataFrame with sensitive fields hashed
        """
        for field in self.sensitive_fields:
            if field in df.columns:
                df[field] = df[field].apply(
                    lambda x: hashlib.sha256(str(x).encode()).hexdigest() if pd.notnull(x) else x
                )
        return df
    
    def transform_database_data(self, query: str, db_connection: Any, **kwargs) -> Dict:
        """
        Transform database data with sensitive field hashing
        
        Args:
            query: SQL query to execute
            db_connection: Database connection object
            **kwargs: Additional arguments
            
        Returns:
            Dictionary containing:
            - 'data': Transformed records with hashed sensitive fields
            - 'metadata': Transformation metadata
        """
        try:
            
            raw_data = self.extractor.from_database(query, db_connection)
            df = pd.DataFrame(raw_data)
            
            
            df = self.hash_sensitive_data(df)
            
            
            df = self._standardize_data_types(df)
            
            return {
                'data': df.to_dict(orient='records'),
                'metadata': self._generate_metadata(raw_data, source_type='database')
            }
            
        except Exception as e:
            self.logger.error(f"Database transformation failed: {e}")
            raise