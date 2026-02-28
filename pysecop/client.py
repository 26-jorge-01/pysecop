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

    def fetch(self, dataset_key: str, query: Union[str, QueryBuilder], limit: int = 1000) -> pd.DataFrame:
        """
        Fetch data from a specific dataset.
        """
        config = DATASETS.get(dataset_key)
        if not config:
            raise ValueError(f"Dataset '{dataset_key}' not found in configuration.")

        if isinstance(query, QueryBuilder):
            soql_query = query.build()
        else:
            soql_query = query

        logger.info(f"Fetching from {config.name} ({config.id})...")
        logger.debug(f"Query: {soql_query}")

        results = self.client.get(config.id, query=soql_query, content_type="json")
        df = pd.DataFrame.from_dict(results)
        
        if not df.empty:
            logger.info(f"Retrieved {len(df)} records from {dataset_key}.")
        else:
            logger.warning(f"No records found for {dataset_key}.")
            
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
