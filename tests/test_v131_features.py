import pytest
import pandas as pd
from pysecop import SecopClient, QueryBuilder

def test_fetch_csv_support():
    client = SecopClient()
    # Test with a small limit using CSV
    # Corrected: fetch requires a query as second argument
    df = client.fetch("SECOP_I", query="select *", limit=10, content_type="csv")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert len(df) <= 10

def test_search_with_order():
    client = SecopClient()
    # Test search with explicit order
    # Using a small limit to be fast
    df = client.search(datasets=["SECOP_I"], limit=10, order="ultima_actualizacion ASC")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    
    # Verify that the order parameter is respected (implicitly by not crashing with a 400)
    # And check that the column exists
    assert "ultima_actualizacion" in df.columns

def test_search_parallel_csv():
    client = SecopClient()
    # Test parallel fetching (limit > 50k) with CSV
    # Note: We use a slightly smaller limit for the test (e.g. 500) to ensure slices are exercised if we lower SLICE_SIZE
    # But for a real test of the logic:
    df = client.search(datasets=["SECOP_I"], limit=100, content_type="csv", concurrency=2)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert len(df) <= 100

def test_query_builder_order():
    qb = QueryBuilder()
    qb.select(["uid"]).order("ultima_actualizacion", "DESC").limit(5)
    query = qb.build()
    assert "order by ultima_actualizacion DESC" in query
    assert "limit 5" in query
