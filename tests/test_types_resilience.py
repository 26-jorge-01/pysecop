import pytest
from pysecop import SecopClient, DATASETS
from pysecop.utils.normalizer import SmartNormalizer

def test_smart_normalizer_numeric():
    config = DATASETS["SECOP_II"]
    # nit_entidad is numeric in SECOP II
    col = "nit_entidad"
    
    assert SmartNormalizer.normalize_value("900000000-1", col, config) == "9000000001"
    assert SmartNormalizer.normalize_value(12345, col, config) == "12345"
    assert SmartNormalizer.normalize_value("NIT: 800.123.456", col, config) == "800.123.456"
    assert SmartNormalizer.normalize_value("Invalid", col, config) == "0"

def test_smart_normalizer_boolean():
    config = DATASETS["SECOP_II"]
    # es_pyme is boolean in SECOP II
    col = "es_pyme"
    
    assert SmartNormalizer.normalize_value("Si", col, config) == "true"
    assert SmartNormalizer.normalize_value("no", col, config) == "false"
    assert SmartNormalizer.normalize_value(True, col, config) == "true"
    assert SmartNormalizer.normalize_value(1, col, config) == "true"
    assert SmartNormalizer.normalize_value("Maybe", col, config) == "false"

def test_smart_normalizer_date():
    config = DATASETS["SECOP_II"]
    # fecha_de_firma is date in SECOP II
    col = "fecha_de_firma"
    
    # Standard format
    assert "'2026-01-01T00:00:00.000'" in SmartNormalizer.normalize_value("2026-01-01", col, config)
    # Flexible format
    assert "'2026-05-20T00:00:00.000'" in SmartNormalizer.normalize_value("20 May 2026", col, config)
    # Invalid date
    assert SmartNormalizer.normalize_value("Not a date", col, config) == "NULL"

def test_smart_normalizer_list():
    config = DATASETS["SECOP_II"]
    col = "nit_entidad"
    
    values = ["900-1", 8002]
    expected = "(9001, 8002)"
    assert SmartNormalizer.normalize_list(values, col, config) == expected

def test_search_built_query(mocker):
    # Mocking the Socrata client to avoid actual network calls
    client = SecopClient()
    mock_get = mocker.patch.object(client.client, 'get', return_value=[])
    mocker.patch.object(client, 'get_available_columns', return_value=["nit_entidad"])
    
    # Searching SECOP II (where nit_entidad is numeric) with a string input
    client.search(datasets=["SECOP_II"], nit_entidad="900000000-1")
    
    # Verify the generated query has NO quotes around the NIT
    args, kwargs = mock_get.call_args
    query_str = kwargs.get('query', '')
    assert "nit_entidad = 9000000001" in query_str
    assert "nit_entidad = '9000000001'" not in query_str
