import pandas as pd
import numpy as np
import re
import gc
import warnings
from typing import List, Optional, Any
from .config import DatasetConfig
from ..utils.logging import get_logger

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

        # Helper to get column name if it exists (either original or unified)
        def get_col(original_col, unified_name=None):
            if original_col in df.columns:
                return original_col
            if unified_name and unified_name in df.columns:
                return unified_name
            return None

        # 1. Clean URLs
        for col in config.url_columns:
            target = get_col(col, "url_proceso")
            if target:
                # Vectorized URL extraction
                df[target] = df[target].astype(str).str.extract(r'(https?://[^\s\'"{}?]+)', expand=False).str.rstrip('/')
                df[target] = df[target].fillna("")

        # 2. Clean Dates
        unified_date_map = {
            "fecha_de_cargue_en_el_secop": "fecha_firma",
            "fecha_de_firma_del_contrato": "fecha_firma",
            "fecha_ini_ejec_contrato": "fecha_inicio",
            "fecha_fin_ejec_contrato": "fecha_fin",
            "fecha_de_firma": "fecha_firma",
            "fecha_de_inicio_del_contrato": "fecha_inicio",
            "fecha_de_fin_del_contrato": "fecha_fin",
            "ultima_actualizacion": "ultima_actualizacion"
        }
        for col in config.date_columns:
            target = get_col(col, unified_date_map.get(col))
            if target:
                # Vectorized date cleaning and parsing
                # Step 1: Basic string cleaning
                temp_date = df[target].astype(str).str.strip().str.replace('T.*', '', regex=True)
                temp_date = temp_date.str.replace(' 12:00:00 (AM|PM)', '', regex=True)
                
                # Step 2: Parse with pandas (vectorized)
                df[target] = pd.to_datetime(temp_date, errors='coerce')


        # 3. Basic Text Cleaning (Lowering)
        for col in config.text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.lower()

        # 4. Binary/Categorical encoding
        unified_cat_map = {
            "es_postconflicto": "es_postconflicto",
            "espostconflicto": "es_postconflicto",
            "es_mipyme": "es_pyme",
            "es_pyme": "es_pyme"
        }
        for col in config.categorical_columns:
            target = get_col(col, unified_cat_map.get(col))
            if target:
                df[target] = df[target].astype(str).str.lower()
                mapping = {
                    'si': 1, 'no': 0, 'válido': 1, 'no válido': 0, 
                    'true': 1, 'false': 0, 'nan': -1, 'no definido': -1
                }
                df[target] = df[target].map(mapping).fillna(-1).astype(int)

        # 5. Enforce full schema consistency for original columns if they should be there
        for col in config.columns:
            if col not in df.columns:
                # Only add if it's not present as a unified column
                # This check is a bit complex, but for simplicity we'll just ensure the col exists
                # if normalization hasn't happened yet.
                df[col] = None

        return df
