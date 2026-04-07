import pandas as pd
from typing import Dict, List, Any, Optional, Union
from ..data.config import COLUMN_MAPPING

def get_mapped_column(dataset_key: str, unified_name: str, resource_type: str = "contracts") -> str:
    """
    Get the original column name for a given unified name in a specific dataset and resource type.
    If no mapping exists, returns the unified name as is.
    """
    resource_mapping = COLUMN_MAPPING.get(resource_type, {})
    dataset_mapping = resource_mapping.get(dataset_key, {})
    return dataset_mapping.get(unified_name, unified_name)

def get_reverse_mapping(dataset_key: str, resource_type: str = "contracts") -> Dict[str, str]:
    """
    Get a mapping of original column names to unified names for a given dataset and resource type.
    """
    resource_mapping = COLUMN_MAPPING.get(resource_type, {})
    dataset_mapping = resource_mapping.get(dataset_key, {})
    return {v: k for k, v in dataset_mapping.items()}

def get_unified_columns(resource_type: str = "contracts") -> List[str]:
    """
    Get all unique unified column names for a given resource type across all datasets.
    """
    resource_mapping = COLUMN_MAPPING.get(resource_type, {})
    unified_cols = set()
    for dataset_mapping in resource_mapping.values():
        unified_cols.update(dataset_mapping.keys())
    return sorted(list(unified_cols))

def normalize_dataframe(df: pd.DataFrame, dataset_key: str, resource_type: str = "contracts") -> pd.DataFrame:
    """
    Rename columns in a DataFrame from their original names to unified names.
    Columns that are not in the mapping are left as is (Zero-Loss Sparse Matrix).
    Ensures all unified columns are present even if filled with None.
    """
    if df.empty:
        # Still return a DF with the unified schema
        unified_cols = get_unified_columns(resource_type)
        return pd.DataFrame(columns=unified_cols)
    
    reverse_map = get_reverse_mapping(dataset_key, resource_type)
    # Only rename columns that exist in the DataFrame
    rename_cols = {old: new for old, new in reverse_map.items() if old in df.columns}
    
    df = df.rename(columns=rename_cols)
    
    # Enforce full unified schema consistency
    # This prevents Postgres schema mismatch errors during parallel ingestion
    unified_cols = get_unified_columns(resource_type)
    for col in unified_cols:
        if col not in df.columns:
            df[col] = None
            
    return df

def get_search_filters(dataset_key: str, resource_type: str = "contracts", **kwargs) -> Dict[str, Any]:
    """
    Translate unified field names in kwargs to original field names for the dataset and resource type.
    """
    filters = {}
    resource_mapping = COLUMN_MAPPING.get(resource_type, {})
    dataset_mapping = resource_mapping.get(dataset_key, {})
    
    for key, value in kwargs.items():
        # If the key is a unified name, map it. Otherwise, use it as is.
        original_key = dataset_mapping.get(key, key)
        filters[original_key] = value
        
    return filters

def consolidate_dataframes(dfs: List[pd.DataFrame], source_col: str = "source") -> pd.DataFrame:
    """
    Consolidate multiple DataFrames into one, ensuring they all have the source column.
    """
    if not dfs:
        return pd.DataFrame()
        
    # Filter out empty DataFrames
    valid_dfs = [df for df in dfs if not df.empty]
    
    if not valid_dfs:
        # Return an empty DF with all columns from the first DF if possible
        return pd.DataFrame(columns=dfs[0].columns if dfs else [])
        
    return pd.concat(valid_dfs, ignore_index=True, sort=False)
