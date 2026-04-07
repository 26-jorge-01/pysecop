import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from pysecop import SecopClient, QueryBuilder
from pysecop.utils import normalize_dataframe, get_unified_columns

def test_search_offset_parameter():
    """
    Verify that the offset parameter is correctly passed to the QueryBuilder.
    """
    client = SecopClient()
    # Mock get_available_columns to return a list of columns
    client.get_available_columns = MagicMock(return_value=["nombre_entidad", "nit_entidad"])
    
    with patch.object(client.client, 'get', return_value=[]) as mock_get:
        client.search(datasets=["SECOP_II"], limit=10, offset=500)
        
        # Verify that the query passed to client.get includes 'offset 500'
        args, kwargs = mock_get.call_args
        query = kwargs.get('query', '')
        assert "offset 500" in query
        assert "limit 10" in query

def test_unified_schema_enforcement():
    """
    Verify that normalize_dataframe ensures all unified columns are present.
    """
    # Create a minimal DF with only one column
    df = pd.DataFrame({"nombre_entidad": ["Entity A"]})
    dataset_key = "SECOP_II"
    
    normalized_df = normalize_dataframe(df, dataset_key)
    
    # Get all unified columns
    unified_cols = get_unified_columns("contracts")
    
    # Check that ALL unified columns are present
    for col in unified_cols:
        assert col in normalized_df.columns
        
    # Check that non-mapped columns are preserved (if any were added)
    df_with_extra = pd.DataFrame({
        "nombre_entidad": ["Entity A"],
        "extra_legacy_metadata": ["Some Data"]
    })
    normalized_extra = normalize_dataframe(df_with_extra, dataset_key)
    assert "extra_legacy_metadata" in normalized_extra.columns
    assert normalized_extra["extra_legacy_metadata"].iloc[0] == "Some Data"

def test_rate_limit_backoff():
    """
    Verify that SecopClient.fetch implements exponential backoff on 429 errors.
    In v1.3.0+, it uses a shared-state backoff.
    """
    client = SecopClient()
    client.get_available_columns = MagicMock(return_value=["col1"])
    
    # Mock response with status_code 429
    mock_response = MagicMock()
    mock_response.status_code = 429
    
    # Mock Exception with .response attribute
    error_429 = Exception("Rate limit exceeded")
    error_429.response = mock_response
    
    with patch.object(client.client, 'get', side_effect=[error_429, error_429, [{"col1": "data"}]]) as mock_get:
        # We need to simulate time passing for the backoff calculation
        # instead of just patching sleep, since we calculate wait_time based on time.time()
        # We provide a long list of times to avoid StopIteration
        times = [100.0 + i*0.1 for i in range(100)] 
        with patch('time.time', side_effect=times):
            with patch('time.sleep') as mock_sleep:
                # Should succeed on the 3rd try (after 2 retries)
                df = client.fetch("SECOP_II", "select *", limit=1)
                
                assert not df.empty
                assert mock_get.call_count == 3
                # It should sleep at least twice for the backoff logic (wait_time or jitter)
                assert mock_sleep.call_count >= 2

def test_fetch_max_retries_exceeded():
    """
    Verify that fetch eventually raises if 429 persists.
    """
    client = SecopClient()
    client.get_available_columns = MagicMock(return_value=["col1"])
    
    mock_response = MagicMock()
    mock_response.status_code = 429
    error_429 = Exception("Rate limit exceeded")
    error_429.response = mock_response
    
    # 6 failures (initial + 5 retries)
    with patch.object(client.client, 'get', side_effect=[error_429] * 8) as mock_get:
        with patch('time.sleep') as mock_sleep:
            with pytest.raises(Exception) as excinfo:
                client.fetch("SECOP_II", "select *", limit=1)
            assert "Rate limit exceeded" in str(excinfo.value)
            assert mock_get.call_count == 6 # Max 5 retries means 6 total attempts
