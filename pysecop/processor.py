import pandas as pd
import numpy as np
import re
import gc
import warnings
from typing import List, Optional, Any
from .config import DatasetConfig
from .logging_setup import get_logger

logger = get_logger(__name__)

class DataProcessor:
    """
    Modular data processor for SECOP datasets.
    """
    
    @staticmethod
    def clean_url(url: str) -> str:
        """
        Extracts a clean URL from potentially messy JSON strings or raw text.
        """
        if not isinstance(url, str) or url.lower() == 'nan' or not url.strip():
            return ""
        
        # 1. Try to extract URL using regex if it's wrapped in JSON-like structure
        # Matches content between quotes that looks like a URL
        url_match = re.search(r'https?://[^\s\'"{}?]+', url)
        if url_match:
            return url_match.group(0).rstrip('/')

        # 2. Fallback to basic string cleaning if regex fails
        url = url.strip()
        for char in ["'", '"', '{', '}', ' ']:
            url = url.replace(char, "")
        
        # Remove known Socrata fragments if they persist
        url = url.replace("url:", "").replace("?numconstancia=", "")
        
        return url.rstrip('/')

    @staticmethod
    def clean_date_string(date: str) -> str:
        """
        Normalizes various Socrata date formats to YYYY-MM-DD.
        """
        if not isinstance(date, str) or date.lower() == 'nan' or not date.strip():
            return ""
        
        date = date.strip()
        
        # Handle formats like "2023-01-01T00:00:00.000"
        if 'T' in date:
            date = date.split('T')[0]
            
        # Handle formats like "01/01/2023 12:00:00 AM"
        date = date.replace('12:00:00 AM', '').replace('12:00:00 PM', '').strip()
        
        return date

    @staticmethod
    def is_valid_date(date_str: Any) -> bool:
        try:
            date = pd.to_datetime(date_str)
            if pd.Timestamp.min <= date <= pd.Timestamp.max:
                return True
        except:
            return False
        return False

    @classmethod
    def process_dataset(cls, df: pd.DataFrame, config: DatasetConfig) -> pd.DataFrame:
        """
        Apply cleaning steps based on dataset configuration.
        """
        if df.empty:
            return df

        df = df.copy()

        # 1. Clean URLs
        for col in config.url_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).apply(cls.clean_url)

        # 2. Clean Dates
        for col in config.date_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).apply(cls.clean_date_string)
                # Handle possible empty strings before to_datetime
                df[col] = df[col].replace("", None)
                df[col] = pd.to_datetime(df[col], errors='coerce')


        # 3. Basic Text Cleaning (Lowering)
        for col in config.text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.lower()
                # Additional regex-based cleaning from CleanData.py could be added here if needed

        # 4. Binary/Categorical encoding
        for col in config.categorical_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.lower()
                mapping = {
                    'si': 1, 'no': 0, 'válido': 1, 'no válido': 0, 
                    'true': 1, 'false': 0, 'nan': -1, 'no definido': -1
                }
                df[col] = df[col].map(lambda x: mapping.get(x, -1))

        return df
