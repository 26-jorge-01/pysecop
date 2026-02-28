import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from pysecop.client import SecopClient
from pysecop.query_builder import QueryBuilder
from pysecop.config import DATASETS

@pytest.fixture
def mock_socrata():
    with patch("pysecop.client.Socrata") as mock:
        yield mock

def test_secop_client_fetch(mock_socrata):
    mock_instance = mock_socrata.return_value
    mock_instance.get.return_value = [{"col1": "val1"}]
    
    client = SecopClient()
    df = client.fetch("SECOP_I", "select *")
    
    assert not df.empty
    assert df["col1"].iloc[0] == "val1"
    mock_instance.get.assert_called_once()

def test_secop_client_fetch_invalid_dataset():
    client = SecopClient()
    with pytest.raises(ValueError, match="Dataset 'INVALID' not found"):
        client.fetch("INVALID", "select *")

def test_get_contracts_by_ids(mock_socrata):
    mock_instance = mock_socrata.return_value
    mock_instance.get.return_value = [{"id": "123"}]
    
    client = SecopClient()
    results = client.get_contracts_by_ids(["123"], id_type="numero_contrato")
    
    assert "SECOP_I" in results
    assert "SECOP_II" in results
    assert mock_instance.get.call_count == 2
