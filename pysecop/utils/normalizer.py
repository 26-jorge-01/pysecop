import pandas as pd
import re
from typing import Any, Optional, Union, List
from ..data import DatasetConfig
from .logging import get_logger

logger = get_logger(__name__)

class SmartNormalizer:
    """
    Intelligent normalizer that casts user inputs to the appropriate SODA types
    based on dataset configuration.
    """
    
    @staticmethod
    def normalize_value(value: Any, column: str, config: DatasetConfig) -> str:
        """
        Normalize a single value for a given column and dataset configuration.
        Returns a string formatted for a SOQL WHERE clause.
        """
        if value is None:
            return "NULL"

        # Determine target type from config
        if column in config.numeric_columns:
            return SmartNormalizer._to_numeric(value, column)
        elif column in config.boolean_columns:
            return SmartNormalizer._to_boolean(value, column)
        elif column in config.date_columns:
            return SmartNormalizer._to_date(value, column)
        else:
            # Default to string (text)
            return f"'{value}'"

    @staticmethod
    def _to_numeric(value: Any, column: str) -> str:
        """
        Strips non-numeric characters (except decimal points) and returns a number string.
        Handles NITs with dashes by stripping the dash.
        """
        if isinstance(value, (int, float)):
            return str(value)
        
        # If it's a string, strip everything except digits and dots
        clean_val = re.sub(r'[^0-9.]', '', str(value))
        
        if not clean_val:
            logger.warning(f"Could not convert '{value}' to numeric for column '{column}'. Using 0.")
            return "0"
            
        return clean_val

    @staticmethod
    def _to_boolean(value: Any, column: str) -> str:
        """
        Maps common truthy/falsy values to 'true'/'false'.
        """
        truthy = {'true', '1', 't', 'y', 'yes', 'si', 's'}
        falsy = {'false', '0', 'f', 'n', 'no'}
        
        val_str = str(value).lower().strip()
        if val_str in truthy:
            return "true"
        elif val_str in falsy:
            return "false"
        else:
            logger.warning(f"Ambiguous boolean value '{value}' for column '{column}'. Using 'false'.")
            return "false"

    @staticmethod
    def _to_date(value: Any, column: str) -> str:
        """
        Parses dates into SODA-compatible ISO-8601 strings.
        """
        try:
            # Use pandas for robust flexible parsing
            dt = pd.to_datetime(value)
            # SODA expects 'YYYY-MM-DDTHH:MM:SS.000'
            return f"'{dt.strftime('%Y-%m-%dT%H:%M:%S.000')}'"
        except (ValueError, TypeError):
            logger.warning(f"Could not parse date '{value}' for column '{column}'. Using NULL.")
            return "NULL"

    @staticmethod
    def normalize_list(values: List[Any], column: str, config: DatasetConfig) -> str:
        """
        Normalizes a list of values for a SOQL IN clause.
        """
        normalized = [SmartNormalizer.normalize_value(v, column, config) for v in values]
        return f"({', '.join(normalized)})"
