from typing import Dict, List, Any, Optional, Union
import logging
import pandas as pd
from datetime import datetime
import hashlib
import json
import numpy as np

from app.etl.extractors.lucas_technology_service_extractor import UniversalDataExtractor

class UniversalDataTransformer:
    

    def save_to_data_lake(
        self,
        transformed_data: Dict[str, Any],
        storage_path: str,
        format: str = 'parquet',
        partition_cols: Optional[List[str]] = None
    ) -> str:
        """
        Save transformed data to data lake storage
        
        Args:
            transformed_data: Output from transform methods
            storage_path: Base storage path
            format: Output format (parquet, json, csv)
            partition_cols: Columns to partition by
            
        Returns:
            Path where data was saved
        """
        try:
            df = pd.DataFrame(transformed_data['data'])
            source_info = transformed_data['source']
            
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            source_name = source_info.get('source_name', 
                                       source_info.get('endpoint', 'unknown'))
            
            # Clean source name for filesystem
            source_name_clean = "".join(
                c if c.isalnum() else "_" for c in str(source_name)
            )
            
            
            save_handlers = {
                'partitioned': self._save_partitioned,
                'non-partitioned': self._save_non_partitioned
            }
            
            handler_key = 'partitioned' if partition_cols else 'non-partitioned'
            output_path = save_handlers[handler_key](
                df, storage_path, source_name_clean, format, partition_cols, timestamp
            )
            
            
            metadata_path = output_path.replace(f"data.{format}", "metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(transformed_data['metadata'], f)
            
            self.logger.info(f"Data successfully saved to {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")
            raise

    def _save_partitioned(
        self,
        df: pd.DataFrame,
        storage_path: str,
        source_name_clean: str,
        format: str,
        partition_cols: List[str],
        timestamp: str
    ) -> str:
        """Save data with partitioning"""
        
        partition_values = [
            f"{col}={df[col].iloc[0]}" 
            for col in partition_cols 
            if col in df.columns
        ]
        
        output_path = f"{storage_path}/{source_name_clean}/{'/'.join(partition_values)}/data.{format}"
        df.drop(columns=partition_cols).to_parquet(output_path)
        return output_path

    def _save_non_partitioned(
        self,
        df: pd.DataFrame,
        storage_path: str,
        source_name_clean: str,
        format: str,
        _: Any,  # Ignore partition_cols
        timestamp: str
    ) -> str:
        """Save data without partitioning"""
        output_path = f"{storage_path}/{source_name_clean}/{timestamp}/data.{format}"
        
        
        format_handlers = {
            'parquet': lambda: df.to_parquet(output_path),
            'json': lambda: df.to_json(output_path, orient='records', lines=True),
            'csv': lambda: df.to_csv(output_path, index=False)
        }
        
        handler = format_handlers.get(format)
        if not handler:
            raise ValueError(f"Unsupported format: {format}")
        handler()
        
        return output_path