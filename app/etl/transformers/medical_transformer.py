from typing import Dict, List, Optional, Any, Union
import logging
import pandas as pd
from datetime import datetime
from dateutil.parser import parse
import hashlib
import json

class MedicalDataTransformer:
    def __init__(self, extractor: Any, anonymize_fields: Optional[List[str]] = None):
        """
        Medical data transformer for FHIR, PostgreSQL, and Elasticsearch sources
        
        Args:
            extractor: Instance of MedicalAppExtractor
            anonymize_fields: List of fields to anonymize (e.g., ['patient_id', 'name'])
        """
        self.extractor = extractor
        self.logger = logging.getLogger(__name__)
        self.anonymize_fields = anonymize_fields or []
        
        # Standard FHIR code systems
        self.fhir_code_systems = {
            'loinc': 'http://loinc.org',
            'snomed': 'http://snomed.info/sct',
            'icd10': 'http://hl7.org/fhir/sid/icd-10'
        }

    def transform_fhir_data(self, resource_type: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Transform FHIR resources into standardized format
        
        Args:
            resource_type: FHIR resource type (Patient, Observation, etc.)
            params: Search parameters
            
        Returns:
            Dictionary with keys:
            - 'data': Transformed records
            - 'metadata': Extraction metadata
            - 'source': Source information
        """
        try:
            raw_data = self.extractor.get_fhir_resource(resource_type, params)
            df = pd.DataFrame(raw_data)
            
            
            if resource_type.lower() == 'patient':
                df = self._transform_patient_data(df)
            elif resource_type.lower() == 'observation':
                df = self._transform_observation_data(df)
            
            
            df = self._standardize_data_types(df)
            df = self._anonymize_data(df)
            
            return {
                'data': df.to_dict(orient='records'),
                'metadata': self._generate_metadata(raw_data, source_type='fhir'),
                'source': {
                    'type': 'fhir',
                    'resource_type': resource_type,
                    'params': params
                }
            }
        except Exception as e:
            self.logger.error(f"FHIR transformation failed: {e}")
            raise

    def transform_pg_data(self, query: str, params: Optional[tuple] = None) -> Dict[str, Any]:
        """
        Transform PostgreSQL medical records
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Dictionary with keys:
            - 'data': Transformed records
            - 'metadata': Extraction metadata
            - 'source': Source information
        """
        try:
            raw_data = self.extractor.get_pg_medical_records(query, params)
            df = pd.DataFrame(raw_data)
            
            # Standardize common medical fields
            if 'birth_date' in df.columns:
                df['birth_date'] = pd.to_datetime(df['birth_date'], errors='coerce')
            if 'record_date' in df.columns:
                df['record_date'] = pd.to_datetime(df['record_date'], errors='coerce')
            
            df = self._standardize_data_types(df)
            df = self._anonymize_data(df)
            
            return {
                'data': df.to_dict(orient='records'),
                'metadata': self._generate_metadata(raw_data, source_type='postgresql'),
                'source': {
                    'type': 'postgresql',
                    'query': query,
                    'params': params
                }
            }
        except Exception as e:
            self.logger.error(f"PostgreSQL transformation failed: {e}")
            raise

    def transform_es_data(self, index: str, query: Dict, size: int = 100) -> Dict[str, Any]:
        """
        Transform Elasticsearch medical data
        
        Args:
            index: Index name
            query: Elasticsearch query
            size: Result size
            
        Returns:
            Dictionary with keys:
            - 'data': Transformed records
            - 'metadata': Extraction metadata
            - 'source': Source information
        """
        try:
            raw_data = self.extractor.get_es_medical_data(index, query, size)
            df = pd.DataFrame(raw_data)
            
            
            for col in df.columns:
                if isinstance(df[col].iloc[0], dict):
                    df = pd.concat([df.drop([col], axis=1), pd.json_normalize(df[col])], axis=1)
            
            df = self._standardize_data_types(df)
            df = self._anonymize_data(df)
            
            return {
                'data': df.to_dict(orient='records'),
                'metadata': self._generate_metadata(raw_data, source_type='elasticsearch'),
                'source': {
                    'type': 'elasticsearch',
                    'index': index,
                    'query': query,
                    'size': size
                }
            }
        except Exception as e:
            self.logger.error(f"Elasticsearch transformation failed: {e}")
            raise

    def _transform_patient_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize FHIR Patient resources"""
        if 'name' in df.columns:
            df['name'] = df['name'].apply(
                lambda x: ' '.join([n['given'][0] for n in x if 'given' in n]) if isinstance(x, list) else x
            )
        
        if 'telecom' in df.columns:
            df['phone'] = df['telecom'].apply(
                lambda x: next((t['value'] for t in x if t['system'] == 'phone'), None) if isinstance(x, list) else None
            )
            df['email'] = df['telecom'].apply(
                lambda x: next((t['value'] for t in x if t['system'] == 'email'), None) if isinstance(x, list) else None
            )
        
        if 'address' in df.columns:
            df['address'] = df['address'].apply(
                lambda x: ', '.join(filter(None, [
                    x[0].get('line', [''])[0],
                    x[0].get('city', ''),
                    x[0].get('state', ''),
                    x[0].get('postalCode', '')
                ])) if isinstance(x, list) and len(x) > 0 else None
            )
        
        return df

    def _transform_observation_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize FHIR Observation resources"""
        if 'code' in df.columns:
            df['code_system'] = df['code'].apply(
                lambda x: x['coding'][0]['system'] if isinstance(x, dict) and 'coding' in x else None
            )
            df['code_value'] = df['code'].apply(
                lambda x: x['coding'][0]['code'] if isinstance(x, dict) and 'coding' in x else None
            )
        
        if 'valueQuantity' in df.columns:
            df['value'] = df['valueQuantity'].apply(
                lambda x: x.get('value') if isinstance(x, dict) else None
            )
            df['unit'] = df['valueQuantity'].apply(
                lambda x: x.get('unit') if isinstance(x, dict) else None
            )
        
        if 'effectiveDateTime' in df.columns:
            df['timestamp'] = pd.to_datetime(df['effectiveDateTime'], errors='coerce')
        
        return df

    def _standardize_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure consistent data types across sources"""
        
        date_cols = [col for col in df.columns if any(kw in col.lower() for kw in ['date', 'time'])]
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        
        
        for col in df.select_dtypes(include='object').columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except Exception:
                pass
        
        return df

    def _anonymize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Anonymize sensitive fields"""
        for field in self.anonymize_fields:
            if field in df.columns:
                df[field] = df[field].apply(
                    lambda x: hashlib.sha256(str(x).encode()).hexdigest() if pd.notnull(x) else x
                )
        return df

    def _generate_metadata(self, data: Any, source_type: str) -> Dict[str, Any]:
        """Generate standardized metadata for all transformations"""
        timestamp = datetime.utcnow().isoformat() + "Z"
        data_hash = hashlib.md5(
            json.dumps(data, sort_keys=True, default=str).encode()
        ).hexdigest()
        
        return {
            "transform_timestamp": timestamp,
            "source_type": source_type,
            "data_hash": data_hash,
            "record_count": len(data) if hasattr(data, '__len__') else 1,
            "schema_version": "1.1"
        }

    def save_to_data_lake(self, transformed_data: Dict[str, Any], storage_path: str, format: str = 'parquet') -> str:
        """
        Save transformed data to data lake storage
        
        Args:
            transformed_data: Output from transform methods
            storage_path: Base storage path
            format: Output format (parquet, json, csv)
            
        Returns:
            Path where data was saved
        """
        try:
            df = pd.DataFrame(transformed_data['data'])
            source_info = transformed_data['source']
            
            
            date_str = datetime.utcnow().strftime("%Y%m%d")
            resource_type = source_info.get('resource_type', source_info.get('index', 'unknown'))
            output_path = f"{storage_path}/{source_info['type']}/{resource_type}/{date_str}/data.{format}"
            
            
            if format == 'parquet':
                df.to_parquet(output_path)
            elif format == 'json':
                df.to_json(output_path, orient='records', lines=True)
            elif format == 'csv':
                df.to_csv(output_path, index=False)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            
            metadata_path = output_path.replace(f"data.{format}", "metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(transformed_data['metadata'], f)
            
            self.logger.info(f"Data successfully saved to {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")
            raise