import pandas as pd
import time
from sodapy import Socrata
from typing import List, Dict, Any, Optional, Union
from .data import DATASETS, DEFAULT_DOMAIN, DatasetConfig, DataProcessor
from .core import QueryBuilder
from .utils import get_logger, normalize_dataframe, get_search_filters, consolidate_dataframes
from .utils.normalizer import SmartNormalizer

logger = get_logger(__name__)

class SecopClient:
    def __init__(self, app_token: Optional[str] = None):
        """
        Initialize the SecopClient.
        :param app_token: Socrata App Token (optional, but recommended for higher limits)
        """
        self.client = Socrata(DEFAULT_DOMAIN, app_token)
        self._column_cache: Dict[str, List[str]] = {}

    def get_available_columns(self, dataset_id: str) -> List[str]:
        """
        Fetch available columns for a dataset and cache them.
        """
        if dataset_id in self._column_cache:
            return self._column_cache[dataset_id]
        
        logger.debug(f"Fetching schema for dataset {dataset_id}...")
        try:
            metadata = self.client.get_metadata(dataset_id)
            columns = [col['fieldName'] for col in metadata.get('columns', [])]
            self._column_cache[dataset_id] = columns
            return columns
        except Exception as e:
            logger.error(f"Error fetching metadata for {dataset_id}: {e}")
            return []

    def fetch(self, dataset_key: str, query: Union[str, QueryBuilder], limit: int = 1000) -> pd.DataFrame:
        """
        Fetch data from a specific dataset.
        """
        config = DATASETS.get(dataset_key)
        if not config:
            raise ValueError(f"Dataset '{dataset_key}' not found in configuration.")

        available_cols = self.get_available_columns(config.id)
        
        if isinstance(query, QueryBuilder):
            # Check if requested columns are available
            if query._select:
                requested_cols = query._select
                valid_cols = [c for c in requested_cols if c in available_cols]
                missing_cols = set(requested_cols) - set(valid_cols)
                if missing_cols:
                    logger.warning(f"Fields missing from API in {dataset_key}: {missing_cols}")
                
                # Update query to only include available columns
                # We create a temporary query builder for building the string
                temp_qb = QueryBuilder()
                temp_qb._select = valid_cols
                temp_qb._where = query._where
                temp_qb._limit = query._limit
                temp_qb._offset = query._offset
                temp_qb._order = query._order
                soql_query = temp_qb.build()
            else:
                soql_query = query.build()
        else:
            soql_query = query

        logger.info(f"Fetching from {config.name} ({config.id})...")
        logger.debug(f"Query: {soql_query}")

        # Rate Limit Resilience: Exponential Backoff for 429
        max_retries = 3
        backoff = 1.0
        results = []
        for i in range(max_retries + 1):
            try:
                results = self.client.get(config.id, query=soql_query, content_type="json")
                break
            except Exception as e:
                # Check for 429 status code in requests exception
                if hasattr(e, 'response') and getattr(e.response, 'status_code', None) == 429 and i < max_retries:
                    logger.warning(f"Rate limited (429). Retrying in {backoff}s... ({i+1}/{max_retries})")
                    time.sleep(backoff)
                    backoff *= 2.0
                else:
                    raise
        
        df = pd.DataFrame.from_dict(results)
        
        # Ensure all expected columns are present (filled with None/NaN if missing)
        # This makes the package resilient to missing fields by providing a consistent schema
        expected_cols = config.columns if config.columns else (query._select if isinstance(query, QueryBuilder) and query._select else [])
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None

        if not df.empty:
            logger.info(f"Retrieved {len(df)} records from {dataset_key}.")
            # Reorder columns to match expected order if possible
            existing_expected = [c for c in expected_cols if c in df.columns]
            other_cols = [c for c in df.columns if c not in expected_cols]
            df = df[existing_expected + other_cols]
        else:
            logger.warning(f"No records found for {dataset_key}.")
            # Return empty DF with expected columns
            df = pd.DataFrame(columns=expected_cols)
            
        return df

    def search(self, datasets: List[str] = ["SECOP_I", "SECOP_II"], limit: int = 1000, offset: int = 0, resource_type: str = "contracts", **kwargs) -> pd.DataFrame:
        """
        Generalized search across multiple datasets using unified column names.
        
        :param datasets: List of dataset keys to search in (e.g., ["SECOP_I", "SECOP_II"])
        :param limit: Maximum number of records per dataset
        :param offset: Pagination offset for the search results
        :param resource_type: Type of resource being searched (e.g., "contracts")
        :param kwargs: Search filters using unified or original column names
        """
        all_dfs = []
        for dataset_key in datasets:
            config = DATASETS.get(dataset_key)
            if not config:
                logger.warning(f"Dataset {dataset_key} not found in configuration.")
                continue
            
            qb = QueryBuilder()
            # To achieve the 'Matrix-in-Blocks' consolidation, we fetch all columns
            # Mapped ones will be unified, and unique ones will be preserved as sparse blocks.
            qb.select([])
            
            # Map search filters to original names
            filters = get_search_filters(dataset_key, resource_type=resource_type, **kwargs)
            for col, val in filters.items():
                if isinstance(val, list):
                    # Smart normalization for IN clauses
                    normalized_list = SmartNormalizer.normalize_list(val, col, config)
                    qb.where_custom(f"{col} in {normalized_list}")
                else:
                    # Smart normalization for single equality clauses
                    normalized_val = SmartNormalizer.normalize_value(val, col, config)
                    qb.where_custom(f"{col} = {normalized_val}")
            
            qb.limit(limit)
            if offset > 0:
                qb.offset(offset)
            
            try:
                df = self.fetch(dataset_key, qb)
                if not df.empty:
                    # Process with DataProcessor (handles dates, urls, etc.)
                    df = DataProcessor.process_dataset(df, config)
                    # Add source mark
                    df['source'] = dataset_key.replace('_', ' ')
                    # Normalize to unified columns
                    df = normalize_dataframe(df, dataset_key, resource_type=resource_type)
                    all_dfs.append(df)
            except Exception as e:
                logger.error(f"Error searching in {dataset_key}: {e}")

        if not all_dfs:
            return pd.DataFrame()
            
        return consolidate_dataframes(all_dfs)

    def get_contracts_by_ids(self, ids: List[str], id_type: str = "id_contratista", limit: int = 10000) -> pd.DataFrame:
        """
        Backwards compatible high-level method to fetch contracts.
        Now returns a single consolidated DataFrame.
        """
        # Map old id_types to new unified names (Standardized on SECOP II)
        compat_mapping = {
            "documento_proveedor": "documento_proveedor",
            "id_contratista": "documento_proveedor",
            "nit_entidad": "nit_entidad",
            "numero_contrato": "id_contrato",
            "id_contrato": "id_contrato"
        }
        search_field = compat_mapping.get(id_type, id_type)
        
        return self.search(limit=limit, **{search_field: ids})
