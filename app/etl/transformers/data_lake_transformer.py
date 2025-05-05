import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import logging
import hashlib
import pandas as pd

from app.etl.extractors.lucas_technology_service_extractor import UniversalDataExtractor

class DataLakeTransformer:
    def __init__(self, extractor: UniversalDataExtractor):
        """
        Transforms extracted data into raw format suitable for data lakes
        
        Args:
            extractor: Instance of UniversalDataExtractor
        """
        self.extractor = extractor
        self.logger = logging.getLogger(__name__)
        
    def _generate_metadata(self, data: Any, source: str) -> Dict:
        """Generate standard metadata for all data loads"""
        timestamp = datetime.utcnow().isoformat() + "Z"
        data_hash = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
        
        return {
            "load_timestamp": timestamp,
            "source_system": source,
            "data_hash": data_hash,
            "record_count": len(data) if isinstance(data, list) else 1,
            "schema_version": "1.0"
        }
    
    def _convert_to_dataframe(self, data: Any) -> pd.DataFrame:
        """Convert various data formats to pandas DataFrame"""
        if isinstance(data, pd.DataFrame):
            return data
        elif isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            return pd.DataFrame([data])
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
    
    def _standardize_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure consistent data types across sources"""
        for col in df.columns:
            # Convert string dates to datetime
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col])
                except (ValueError, TypeError):
                    pass
            
            
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col])
                except (ValueError, TypeError):
                    pass
        
        return df
    
    def transform_api_data(
        self,
        base_url: str,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        auth: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """
        Extract and transform API data for data lake
        
        Returns:
            Dict with 'data' and 'metadata' keys
        """
        raw_data = self.extractor.from_api(
            base_url=base_url,
            endpoint=endpoint,
            params=params,
            headers=headers,
            auth=auth
        )
        
        df = self._convert_to_dataframe(raw_data)
        df = self._standardize_data_types(df)
        
        source_name = f"API:{base_url}{endpoint}"
        metadata = self._generate_metadata(raw_data, source_name)
        
        return {
            "data": df.to_dict(orient='records'),
            "metadata": metadata,
            "raw_data": raw_data  # Keep original for traceability
        }
    
    def transform_database_data(
        self,
        query: str,
        db_connection: Any,
        source_name: str
    ) -> Dict[str, Any]:
        """
        Extract and transform database data for data lake
        
        Returns:
            Dict with 'data' and 'metadata' keys
        """
        raw_data = self.extractor.from_database(
            query=query,
            db_connection=db_connection
        )
        
        df = self._convert_to_dataframe(raw_data)
        df = self._standardize_data_types(df)
        
        metadata = self._generate_metadata(raw_data, source_name)
        
        return {
            "data": df.to_dict(orient='records'),
            "metadata": metadata,
            "raw_data": raw_data  # Keep original for traceability
        }
    
    def transform_file_data(
        self,
        file_path: str,
        file_type: str = 'json',
        source_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract and transform file data for data lake
        
        Returns:
            Dict with 'data' and 'metadata' keys
        """
        raw_data = self.extractor.from_file(
            file_path=file_path,
            file_type=file_type
        )
        
        df = self._convert_to_dataframe(raw_data)
        df = self._standardize_data_types(df)
        
        if source_name is None:
            source_name = f"FILE:{file_path}"
        
        metadata = self._generate_metadata(raw_data, source_name)
        
        return {
            "data": df.to_dict(orient='records'),
            "metadata": metadata,
            "raw_data": raw_data  # Keep original for traceability
        }
    
    def save_to_raw_zone(
        self,
        transformed_data: Dict[str, Any],
        storage_path: str,
        format: str = 'parquet'
    ) -> str:
        """
        Save transformed data to raw zone of data lake
        
        Args:
            transformed_data: Output from transform methods
            storage_path: Destination path (local or cloud)
            format: Output format (parquet, json, csv)
            
        Returns:
            Path where data was saved
        """
        try:
            df = self._convert_to_dataframe(transformed_data['data'])
            
            # Create timestamped path
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            source_name_clean = "".join(
                c if c.isalnum() else "_" 
                for c in transformed_data['metadata']['source_system']
            )
            output_path = f"{storage_path}/{source_name_clean}/{timestamp}/data.{format}"
            
            
            if format == 'parquet':
                df.to_parquet(output_path)
            elif format == 'json':
                df.to_json(output_path, orient='records', lines=True)
            elif format == 'csv':
                df.to_csv(output_path, index=False)
            else:
                raise ValueError(f"Unsupported format: {format}")
                        
            metadata_path = f"{storage_path}/{source_name_clean}/{timestamp}/metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(transformed_data['metadata'], f)
            
            self.logger.info(f"Data successfully saved to {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")
            raise