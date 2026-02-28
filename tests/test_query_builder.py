import pytest
from pysecop.query_builder import QueryBuilder

def test_query_builder_select():
    qb = QueryBuilder()
    qb.select(["col1", "col2"])
    assert qb.build() == "select col1, col2"

def test_query_builder_where_in():
    qb = QueryBuilder()
    qb.where_in("col1", ["val1", 2])
    assert qb.build() == "where col1 in ('val1', 2)"

def test_query_builder_where_in_empty():
    qb = QueryBuilder()
    qb.where_in("col1", [])
    assert qb.build() == ""

def test_query_builder_limit_offset():
    qb = QueryBuilder()
    qb.limit(10).offset(5)
    assert qb.build() == "limit 10 offset 5"

def test_query_builder_order():
    qb = QueryBuilder()
    qb.order("col1", "DESC")
    assert qb.build() == "order col1 DESC"

def test_query_builder_full():
    qb = QueryBuilder()
    qb.select(["a", "b"]).where_in("c", [1]).limit(10).order("a")
    expected = "select a, b where c in (1) order a ASC limit 10"
    assert qb.build() == expected
