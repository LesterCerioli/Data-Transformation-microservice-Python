from typing import Dict
import pandas as pd
from app.etl.extractors.lucas_technology_service_extractor import UniversalDataExtractor
from app.etl.transformers.data_lake_transformer import DataLakeTransformer

class BusinessRulesTransformer(DataLakeTransformer):
    def __init__(self, extractor: UniversalDataExtractor, rules_config: Dict):
        """
        Applies business rules to transformed data
        
        Args:
            extractor: Data extractor instance
            rules_config: Dictionary of business rules configuration
                         Example: {"price": {"convert_currency": "USD"}}
        """
        super().__init__(extractor)
        self.rules = rules_config
        # Initialize exchange rates cache
        self._exchange_rates = {}

    def _get_exchange_rate(self, currency: str) -> float:
        """
        Get exchange rate for target currency (implementation example)
        
        Args:
            currency: Target currency code (e.g., "USD")
            
        Returns:
            Exchange rate from base currency to target currency
            
        Note: In production, you would:
        - Fetch rates from a financial API
        - Cache results appropriately
        - Handle rate lookup failures
        """
        
        rates = {
            'USD': 1.0,    # Base currency
            'EUR': 0.85,
            'GBP': 0.75,
            'JPY': 110.0
        }
        
        if currency not in rates:
            raise ValueError(f"Unsupported currency: {currency}")
            
        return rates[currency]

    def _apply_business_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply configured business rules to DataFrame
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with business rules applied
        """
        if "price" in df.columns and "convert_currency" in self.rules.get("price", {}):
            target_currency = self.rules["price"]["convert_currency"]
            try:
                rate = self._get_exchange_rate(target_currency)
                df["price_usd"] = df["price"] * rate
            except ValueError as e:
                self.logger.error(f"Currency conversion failed: {e}")
                
        return df

    def transform_file_data(self, *args, **kwargs) -> Dict:
        """
        Transform file data with business rules applied
        
        Returns:
            Dictionary with transformed data and metadata
        """
        data = super().transform_file_data(*args, **kwargs)
        df = pd.DataFrame(data["data"])
        df = self._apply_business_rules(df)
        data["data"] = df.to_dict("records")
        return data