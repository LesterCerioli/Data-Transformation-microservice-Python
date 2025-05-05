from typing import Dict, Any
import pandas as pd
from app.etl.transformers.data_lake_transformer import DataLakeTransformer


class DataQualityTransformer(DataLakeTransformer):
    def _calculate_quality_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate data quality metrics for a DataFrame.
        
        Args:
            df: Input DataFrame to analyze
            
        Returns:
            Dictionary containing completeness and uniqueness metrics
            Format: {
                "completeness": {column_name: completeness_score},
                "uniqueness": {column_name: uniqueness_score}
            }
            
        Raises:
            ValueError: If input DataFrame is empty
        """
        if df.empty:
            raise ValueError("Cannot calculate metrics for empty DataFrame")
            
        if len(df) == 0:
            return {
                "completeness": {},
                "uniqueness": {}
            }
            
        return {
            "completeness": {
                col: float(1 - df[col].isnull().mean()) 
                for col in df.columns
            },
            "uniqueness": {
                col: float(df[col].nunique() / max(1, len(df)))  # Avoid division by zero
                for col in df.columns
            }
        }

    def transform_database_data(self, *args, **kwargs) -> Dict[str, Any]:
        """Transform database data with added quality metrics.
        
        Returns:
            Dictionary containing:
            - data: Original transformed data
            - metadata: Includes quality_metrics
            - raw_data: Original raw data
        """
        try:
            data = super().transform_database_data(*args, **kwargs)
            df = pd.DataFrame(data["data"])
            
            if not df.empty:
                data["metadata"]["quality_metrics"] = self._calculate_quality_metrics(df)
            else:
                data["metadata"]["quality_metrics"] = {
                    "completeness": {},
                    "uniqueness": {}
                }
                
            return data
            
        except Exception as e:
            self.logger.error(f"Data quality transformation failed: {str(e)}")
            raise