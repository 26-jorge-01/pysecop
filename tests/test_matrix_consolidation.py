import pytest
import pandas as pd
from unittest.mock import MagicMock
from pysecop.client import SecopClient
from pysecop.data.config import COLUMN_MAPPING

def test_matrix_consolidation_logic(mocker):
    """
    Verifies that search() produces a consolidated DataFrame that is a union
    of mapped and unmapped columns (Matrix-in-Blocks).
    """
    client = SecopClient()
    
    # Mock SECOP I response: Has a mapped column and a unique SECOP I column
    # mapped: nit_de_la_entidad -> nit_entidad
    # unique: unique_secop_i
    mock_secop_i = [
        {"nombre_entidad": "Entidad 1", "nit_de_la_entidad": "123", "unique_secop_i": "val_i"}
    ]
    
    # Mock SECOP II response: Has a mapped column and a unique SECOP II column
    # mapped: nit_entidad -> nit_entidad
    # unique: unique_secop_ii
    mock_secop_ii = [
        {"nombre_entidad": "Entidad 2", "nit_entidad": "456", "unique_secop_ii": "val_ii"}
    ]
    
    # Patch the Socrata.get method
    mock_get = mocker.patch("sodapy.Socrata.get")
    mock_get.side_effect = [mock_secop_i, mock_secop_ii]
    
    # Execute search
    df = client.search(datasets=["SECOP_I", "SECOP_II"], entidad="Entidad")
    
    # Assertions
    assert not df.empty
    
    # Check for unified column
    assert "nit_entidad" in df.columns
    # The original native name should NOT be present (renamed)
    assert "nit_de_la_entidad" not in df.columns
    
    # Check for unique columns (Matrix-in-Blocks)
    assert "unique_secop_i" in df.columns
    assert "unique_secop_ii" in df.columns
    
    # Verify values and NaNs
    # Row 0 (SECOP I) should have unique_secop_i but NaN for unique_secop_ii
    row_i = df[df["source"] == "SECOP I"].iloc[0]
    assert row_i["unique_secop_i"] == "val_i"
    assert pd.isna(row_i["unique_secop_ii"])
    
    # Row 1 (SECOP II) should have unique_secop_ii but NaN for unique_secop_i
    row_ii = df[df["source"] == "SECOP II"].iloc[0]
    assert row_ii["unique_secop_ii"] == "val_ii"
    assert pd.isna(row_ii["unique_secop_i"])

if __name__ == "__main__":
    pytest.main([__file__])
