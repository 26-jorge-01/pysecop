import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from pysecop import SecopClient, DATASETS

@pytest.fixture
def mock_socrata():
    with patch("pysecop.client.Socrata") as mock:
        mock_instance = mock.return_value
        # Mock get_metadata to return some columns
        mock_instance.get_metadata.return_value = {"columns": [{"fieldName": "estado_del_proceso"}]}
        # Mock get to return empty results but captured
        mock_instance.get.return_value = []
        yield mock

def test_secop_i_contracts_mandatory_filter(mock_socrata):
    mock_instance = mock_socrata.return_value
    client = SecopClient()
    
    # Search specifically in SECOP I for contracts
    client.search(datasets=["SECOP_I"], resource_type="contracts")
    
    # Check that the query contains the mandatory filter
    args, kwargs = mock_instance.get.call_args
    query = kwargs.get("query", "")
    assert "upper(estado_del_proceso) = 'ADJUDICADO'".lower() in query.lower()

def test_secop_ii_processes_resolution(mock_socrata):
    mock_instance = mock_socrata.return_value
    client = SecopClient()
    
    # Search specifically in SECOP II for processes
    # SECOP_II should resolve to SECOP_II_PROCESOS (p6dx-8zbt)
    client.search(datasets=["SECOP_II"], resource_type="processes")
    
    # Check that it called the correct dataset ID
    args, kwargs = mock_instance.get.call_args
    dataset_id = args[0]
    assert dataset_id == "p6dx-8zbt"

def test_processes_mapping_usage(mock_socrata):
    mock_instance = mock_socrata.return_value
    client = SecopClient()
    
    # Search for processes using a unified field 'estado'
    # SECOP_II_PROCESOS maps 'estado' to 'estado_del_procedimiento' (via my COLUMN_MAPPING)
    client.search(datasets=["SECOP_II"], resource_type="processes", estado="ACTIVO")
    
    # Check that the query used the mapped field name
    args, kwargs = mock_instance.get.call_args
    query = kwargs.get("query", "")
    assert "estado_del_procedimiento = 'ACTIVO'".lower() in query.lower()
