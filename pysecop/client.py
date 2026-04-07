import pandas as pd
import time
from sodapy import Socrata
from typing import List, Dict, Any, Optional, Union
from .data import DATASETS, DEFAULT_DOMAIN, DatasetConfig, DataProcessor
from .core import QueryBuilder
from .utils import get_logger, normalize_dataframe, get_search_filters, consolidate_dataframes
from .utils.normalizer import SmartNormalizer
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import io

logger = get_logger(__name__)

class SecopClient:
    def __init__(self, app_token: Optional[str] = None):
        """
        Initialize the SecopClient.
        :param app_token: Socrata App Token (optional, but recommended for higher limits)
        """
        self.client = Socrata(DEFAULT_DOMAIN, app_token)
        self._column_cache: Dict[str, List[str]] = {}
        self._backoff_lock = threading.Lock()
        self._next_request_time = 0.0

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

    def fetch(self, dataset_key: str, query: Union[str, QueryBuilder], limit: int = 1000, content_type: str = "json") -> pd.DataFrame:
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
            # Enforce limit for raw strings if not present to avoid 400 when passing it separately
            if "limit " not in soql_query.lower():
                # Add space if needed
                if not soql_query.strip().endswith(";"):
                    soql_query = soql_query.strip() + f" limit {limit}"

        logger.info(f"Fetching from {config.name} ({config.id})...")
        logger.debug(f"Query: {soql_query}")

        # Rate Limit Resilience: Exponential Backoff for 429 (Thread-Safe)
        max_retries = 5 # Increased for parallel environment
        initial_backoff = 2.0
        results = []
        
        for i in range(max_retries + 1):
            # Check if we are currently backed off
            wait_time = self._next_request_time - time.time()
            if wait_time > 0:
                time.sleep(wait_time)

            try:
                # SODA 2.0 Rule: If $query is used, no other $ parameters (like $limit) can be specified separately.
                # By embedding limit/order/etc. into soql_query, we ensure compatibility.
                results = self.client.get(config.id, content_type, query=soql_query)
                break
            except Exception as e:
                is_429 = hasattr(e, 'response') and getattr(e.response, 'status_code', None) == 429
                if is_429 and i < max_retries:
                    with self._backoff_lock:
                        # Only increase backoff if another thread hasn't already done it
                        if self._next_request_time <= time.time():
                            current_backoff = initial_backoff * (2 ** i)
                            self._next_request_time = time.time() + current_backoff
                            logger.warning(f"Rate limited (429). Global backoff: {current_backoff}s. ({i+1}/{max_retries})")
                        else:
                            logger.debug("Rate limited (429). Waiting for existing backoff...")
                    
                    # Small jitter to avoid synchronized retries
                    time.sleep(0.1 * (i + 1)) 
                else:
                    raise
        
        if content_type == "csv":
            # sodapy parses CSV into a list of lists automatically
            if isinstance(results, list) and len(results) > 0:
                df = pd.DataFrame(results[1:], columns=results[0])
            elif isinstance(results, str):
                df = pd.read_csv(io.StringIO(results))
            else:
                df = pd.DataFrame(results)
        else:
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

    def search(self, datasets: List[str] = ["SECOP_I", "SECOP_II"], limit: int = 1000, offset: int = 0, resource_type: str = "contracts", concurrency: Optional[int] = None, order: Optional[str] = None, content_type: str = "json", **kwargs) -> pd.DataFrame:
        """
        Generalized search across multiple datasets using unified column names.
        Supports high-throughput parallel fetching using internal slicing.
        
        :param datasets: List of dataset keys to search in (e.g., ["SECOP_I", "SECOP_II"])
        :param limit: Maximum number of records per dataset
        :param offset: Pagination offset for the search results
        :param resource_type: Type of resource being searched (e.g., "contracts")
        :param concurrency: Number of parallel workers. If None, auto-calculated based on limit.
        :param kwargs: Search filters using unified or original column names
        """
        # Automatic concurrency management
        # If limit is large (>50,000), we slice it.
        # Socrata max limit per request is usually 50,000.
        SLICE_SIZE = 50000
        
        if concurrency is None:
            if limit > SLICE_SIZE:
                concurrency = min(8, (limit // SLICE_SIZE) + 1)
            else:
                concurrency = 1

        all_dfs = []
        
        # We use a ThreadPoolExecutor to handle parallel fetching
        # We need to process each dataset, and if concurrency > 1, slice the work for that dataset.
        with ThreadPoolExecutor(max_workers=max(1, concurrency)) as executor:
            future_to_task = {}
            
            for dataset_key in datasets:
                config = DATASETS.get(dataset_key)
                if not config:
                    logger.warning(f"Dataset {dataset_key} not found in configuration.")
                    continue
                
                # Partition the work for this dataset
                num_slices = max(1, (limit + SLICE_SIZE - 1) // SLICE_SIZE) if concurrency > 1 else 1
                for i in range(num_slices):
                    current_slice_offset = offset + (i * SLICE_SIZE)
                    current_slice_limit = min(SLICE_SIZE, limit - (i * SLICE_SIZE))
                    
                    if current_slice_limit <= 0:
                        break
                        
                    future = executor.submit(self._fetch_and_process_slice, dataset_key, config, current_slice_limit, current_slice_offset, resource_type, order=order, content_type=content_type, **kwargs)
                    future_to_task[future] = (dataset_key, current_slice_offset)

            for future in as_completed(future_to_task):
                dataset_key, slice_offset = future_to_task[future]
                try:
                    df = future.result()
                    if not df.empty:
                        all_dfs.append(df)
                except Exception as e:
                    logger.error(f"Error fetching slice {slice_offset} for {dataset_key}: {e}")

        if not all_dfs:
            return pd.DataFrame()
            
        return consolidate_dataframes(all_dfs)

    def _fetch_and_process_slice(self, dataset_key: str, config: Any, limit: int, offset: int, resource_type: str, order: Optional[str] = None, content_type: str = "json", **kwargs) -> pd.DataFrame:
        """Helper for parallel fetching of slices."""
        qb = QueryBuilder()
        qb.select([]) # Matrix-in-Blocks strategy: fetch all
        
        # Map search filters to original names
        filters = get_search_filters(dataset_key, resource_type=resource_type, **kwargs)
        for col, val in filters.items():
            if isinstance(val, list):
                normalized_list = SmartNormalizer.normalize_list(val, col, config)
                qb.where_custom(f"{col} in {normalized_list}")
            else:
                normalized_val = SmartNormalizer.normalize_value(val, col, config)
                qb.where_custom(f"{col} = {normalized_val}")
        
        qb.limit(limit)
        if offset > 0:
            qb.offset(offset)
        
        if order:
            # We assume order is like "ultima_actualizacion ASC"
            col_part = order.split(' ')[0]
            dir_part = order.split(' ')[1] if ' ' in order else "ASC"
            qb.order(col_part, dir_part)
            
        df = self.fetch(dataset_key, qb, content_type=content_type)
        if not df.empty:
            df = DataProcessor.process_dataset(df, config)
            df['source'] = dataset_key.replace('_', ' ')
            df = normalize_dataframe(df, dataset_key, resource_type=resource_type)
        return df

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
