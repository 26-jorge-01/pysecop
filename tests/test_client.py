import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from pysecop import SecopClient, QueryBuilder, DATASETS

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
    df = client.get_contracts_by_ids(["123"], id_type="numero_contrato")
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "source" in df.columns
    # With 2 mocks returning 1 record each, we expect 2 total
    assert len(df) == 2
    assert mock_instance.get.call_count == 2
