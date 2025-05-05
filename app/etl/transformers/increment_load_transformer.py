from app.etl.transformers.data_lake_transformer import DataLakeTransformer

class IncrementLoadTransformer(DataLakeTransformer):
    def __init__(self, extractor: Any, id_field: str, timestamp_field: str):
        """
        Transformer for handling incremental data loads
        
        Args:
            extractor: Data extractor instance
            id_field: Name of the unique ID field
            timestamp_field: Name of the timestamp field for tracking changes
        """
        super().__init__(extractor)
        self.id_field = id_field
        self.timestamp_field = timestamp_field
        self.logger = logging.getLogger(__name__)

    def transform_database_data(self, query: str, db_connection: Any, **kwargs) -> Dict:
        """
        Transform data with incremental load tracking
        
        Args:
            query: SQL query to execute
            db_connection: Database connection object
            **kwargs: Additional arguments
            
        Returns:
            Dictionary containing:
            - 'data': Transformed records
            - 'metadata': Includes incremental load information
        """
        try:
            raw_data = self.extractor.from_database(query, db_connection)
            df = pd.DataFrame(raw_data)
            
            # Add incremental load metadata
            max_timestamp = df[self.timestamp_field].max()
            record_ids = df[self.id_field].unique().tolist()
            
            transformed_data = {
                'data': df.to_dict(orient='records'),
                'metadata': {
                    'max_timestamp': str(max_timestamp),
                    'record_ids': record_ids,
                    **self._generate_metadata(raw_data, source_type='database')
                }
            }
            
            return transformed_data
            
        except Exception as e:
            self.logger.error(f"Incremental load transformation failed: {e}")
            raise