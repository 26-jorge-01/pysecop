import pytest
import pandas as pd
import numpy as np
from pysecop.processor import DataProcessor
from pysecop.config import DatasetConfig

def test_clean_url():
    # Standard format
    assert DataProcessor.clean_url("{'url': 'https://example.com'}") == "https://example.com"
    # Mixed quotes and spaces
    assert DataProcessor.clean_url("{ 'url ' : 'https://example.com' ? numconstancia= ' }") == "https://example.com"
    # Plain URL
    assert DataProcessor.clean_url("https://example.com/") == "https://example.com"
    # Messy JSON-like
    assert DataProcessor.clean_url("{url: 'http://test.com', some: 'other'}") == "http://test.com"
    # Invalid/Empty
    assert DataProcessor.clean_url(None) == ""
    assert DataProcessor.clean_url("nan") == ""
    assert DataProcessor.clean_url("   ") == ""

def test_clean_date_string():
    # ISO format
    assert DataProcessor.clean_date_string("2023-01-01T00:00:00.000") == "2023-01-01"
    # US format with AM/PM
    assert DataProcessor.clean_date_string("2023-01-01 12:00:00 AM") == "2023-01-01"
    # Plain date
    assert DataProcessor.clean_date_string("2023-01-01") == "2023-01-01"
    # Empty/NaN
    assert DataProcessor.clean_date_string("nan") == ""
    assert DataProcessor.clean_date_string("") == ""

def test_process_dataset_basic():
    config = DatasetConfig(
        id="test", name="test", description="test",
        url_columns=["url"],
        date_columns=["date"],
        categorical_columns=["is_valid"]
    )
    df = pd.DataFrame({
        "url": ["{'url': 'http://test.com'}"],
        "date": ["2023-01-01T00:00:00.000"],
        "is_valid": ["si"]
    })
    
    processed = DataProcessor.process_dataset(df, config)
    
    assert processed["url"].iloc[0] == "http://test.com"
    assert processed["is_valid"].iloc[0] == 1
    assert pd.api.types.is_datetime64_any_dtype(processed["date"])

def test_process_dataset_empty():
    config = DatasetConfig(id="test", name="test", description="test")
    df = pd.DataFrame()
    processed = DataProcessor.process_dataset(df, config)
    assert processed.empty
