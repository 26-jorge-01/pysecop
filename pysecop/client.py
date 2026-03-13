import pandas as pd
from sodapy import Socrata
from typing import List, Dict, Any, Optional, Union
from .config import DATASETS, DEFAULT_DOMAIN, DatasetConfig
from .query_builder import QueryBuilder
from .logging_setup import get_logger

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

        results = self.client.get(config.id, query=soql_query, content_type="json")
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

    def get_contracts_by_ids(self, ids: List[str], id_type: str = "documento_proveedor", limit: int = 10000) -> Dict[str, pd.DataFrame]:
        """
        High-level method to fetch contracts from both SECOP I and SECOP II by provider IDs or similar.
        """
        results = {}
        
        # Mapping for different ID types across datasets
        mapping = {
            "documento_proveedor": {
                "SECOP_I": "identificacion_del_contratista",
                "SECOP_II": "documento_proveedor"
            },
            "nit_entidad": {
                "SECOP_I": "nit_de_la_entidad",
                "SECOP_II": "nit_entidad"
            },
            "numero_contrato": {
                "SECOP_I": "numero_de_contrato",
                "SECOP_II": "id_contrato"
            }
        }

        if id_type not in mapping:
            raise ValueError(f"Unsupported id_type: {id_type}. Use one of {list(mapping.keys())}")

        for dataset_key in ["SECOP_I", "SECOP_II"]:
            col_name = mapping[id_type][dataset_key]
            config = DATASETS[dataset_key]
            
            qb = QueryBuilder()
            qb.select(config.columns)
            qb.where_in(col_name, ids)
            qb.limit(limit)
            
            results[dataset_key] = self.fetch(dataset_key, qb)

        return results
