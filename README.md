# pysecop 🇨🇴

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**pysecop** is a high-performance Python package designed to interact seamlessly with Colombia's Public Procurement Data (SECOP I & II). 

It abstracts the complexity of the Socrata (SODA) API, handles messy government data cleaning, and provides a fluent interface for building complex queries that are ready for Machine Learning and Big Data pipelines.

---

## 🚀 Why pysecop?

Public procurement data is the foundation of transparency and market intelligence. However, raw government APIs often return inconsistent formats, "polluted" URL strings, and fragmented schemas. `pysecop` solves this by providing:

-   🏗️ **Fluent SoQL Builder**: Build complex Socrata queries without writing a single line of raw SQL.
-   🧹 **Automated Data Hygiene**: Pre-configured processors for dates, URLs, and categorical encoding.
-   🔗 **Unified Schema**: High-level methods to join data across SECOP I and SECOP II seamlessly.
-   🐳 **Production Ready**: Fully Dockerized and tested for mission-critical ETL environments.

---

## 🛠️ Quick Start

### Installation

```bash
pip install pysecop
```

### Unified Search (SECOP I & II)

The most powerful feature of `pysecop` is the ability to search across both SECOP I and SECOP II with a single command and get a single, consolidated DataFrame. The engine includes **Intelligent Input Resilience**, allowing you to provide formatted IDs (like NITs with dashes) that are automatically cleaned for the backend.

```python
from pysecop import SecopClient

client = SecopClient()

# Search by NIT across both datasets simultaneously (automatic ID cleaning)
df = client.search(nit_entidad="900000000-1")

# The result is a single, consolidated "Matrix-in-Blocks" DataFrame
print(df[["source", "nombre_entidad", "valor_del_contrato", "estado_contrato"]].head())
```

> [!TIP]
> Use standardized column names like `documento_proveedor`, `nit_entidad`, and `valor_del_contrato` to search across all data regardless of the original government field names.

---

## 🏛️ Project Architecture

The system follows a modular design to ensure scalability and ease of maintenance:

```mermaid
graph LR
    A[SecopClient] -->|Builds| B[QueryBuilder]
    A -->|Authenticates| C[Socrata API]
    C -->|Returns Raw| D[DataFrame]
    D -->|Refines| E[DataProcessor]
    E -->|Output| F[Analysis Ready Data]
```

For a deeper dive into the system design, check out the [Architecture Deep Dive](docs/ARCHITECTURE.md).

---

## 📂 Documentation Layers

-   **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Technical design, data flow, and architectural trade-offs.
-   **[GUIDE.md](docs/GUIDE.md)**: Full API reference, installation, and extension guide.
-   **[USE_CASES.md](docs/USE_CASES.md)**: Business value, anti-corruption use cases, and market intelligence examples.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
