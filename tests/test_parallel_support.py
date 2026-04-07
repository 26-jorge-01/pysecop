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
        with patch('time.sleep') as mock_sleep:
            # Should succeed on the 3rd try (after 2 retries)
            df = client.fetch("SECOP_II", "select *", limit=1)
            
            assert not df.empty
            assert mock_get.call_count == 3
            assert mock_sleep.call_count == 2
            # Verify exponential backoff sequence: 1.0, 2.0
            mock_sleep.assert_any_call(1.0)
            mock_sleep.assert_any_call(2.0)

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
    
    # 4 failures (initial + 3 retries)
    with patch.object(client.client, 'get', side_effect=[error_429] * 5) as mock_get:
        with patch('time.sleep') as mock_sleep:
            with pytest.raises(Exception) as excinfo:
                client.fetch("SECOP_II", "select *", limit=1)
            assert "Rate limit exceeded" in str(excinfo.value)
            assert mock_get.call_count == 4 # Max 3 retries means 4 total attempts
