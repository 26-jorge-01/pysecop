# Developer Guide: pysecop

This guide provides detailed information on how to use, extend, and maintain the `pysecop` package.

## Installation

```bash
pip install .
# or for development
pip install -e .
```

## Basic Usage

### Fetching Contracts by Individual IDs
The most common use case is looking up specific contracts or providers.

```python
from pysecop import SecopClient

client = SecopClient()
results = client.get_contracts_by_ids(
    ids=["901000000", "801234567"], 
    id_type="documento_proveedor"
)

# Returns a dict with DataFrames for SECOP_I and SECOP_II
df_i = results["SECOP_I"]
df_ii = results["SECOP_II"]
```

## Advanced Querying with `QueryBuilder`

For complex filtering, use the `QueryBuilder` to generate SoQL.

```python
from pysecop import SecopClient, QueryBuilder

client = SecopClient()
qb = QueryBuilder()

qb.select(["id_contrato", "valor_del_contrato", "nombre_entidad"]) \
  .where_custom("valor_del_contrato > 500000000") \
  .where_in("departamento", ["Bogotá D.C.", "Antioquia"]) \
  .order("valor_del_contrato", "DESC") \
  .limit(100)

df = client.fetch("SECOP_II", qb)
```

## Integrated Data Processing

Data from SECOP is often "dirty". Use the `DataProcessor` to clean it based on the predefined configuration.

```python
from pysecop import DataProcessor, DATASETS

config = DATASETS["SECOP_II"]
clean_df = DataProcessor.process_dataset(df, config)
```

## Extending the Library

### Adding a New Dataset
To add a new Socrata dataset (e.g., SECOP II Processes):
1.  Open `pysecop/config.py`.
2.  Define a new `DatasetConfig` instance with the `id` from `datos.gov.co`.
3.  Add it to the `DATASETS` dictionary.

### Modifying Cleaning Logic
If a column requires a new type of cleaning:
1.  In `DataProcessor.py`, add a new `@staticmethod` for the cleaning logic.
2.  Update `process_dataset` to apply this method to the appropriate columns.

## Development and Testing

### Running Tests
We use `pytest` for all unit tests.

```bash
pytest tests/
```

### Docker Support
The project includes a `Dockerfile` for containerized execution, ensuring specific Python environments and dependencies are locked.

```bash
docker build -t pysecop .
```
