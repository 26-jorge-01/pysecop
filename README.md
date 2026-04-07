# pysecop 🇨🇴

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**pysecop** is a high-performance Python package designed to interact seamlessly with Colombia's Public Procurement Data (SECOP I & II). 

It abstracts the complexity of the Socrata (SODA) API, handles messy government data cleaning, and provides a fluent interface for building complex queries that are ready for Machine Learning and Big Data pipelines.

---

## 🚀 Why pysecop?

Public procurement data is the foundation of transparency and market intelligence. However, raw government APIs often return inconsistent formats, "polluted" URL strings, and fragmented schemas. `pysecop` solves this by providing:

-   🏗️ **Fluent SoQL Builder**: Build complex Socrata queries without writing a single line of raw SQL.
-   🧹 **Automated Data Hygiene**: Pre-configured **vectorized processors** for dates, URLs, and categorical encoding (v1.3.0+).
-   🚀 **Native Parallel Fetching**: Auto-sliced concurrent requests for high-throughput historical data scavenging.
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

### Parallel Ingestion & Native Slicing (v1.3.0+)

For high-throughput pipelines, `pysecop` now supports **Native Parallel Slicing**. It automatically partitions large requests into concurrent worker threads with shared-state rate limiting:

```python
# Automatic High-Throughput (Auto-calculates concurrency and slices offsets)
df = client.search(limit=250000) # Slices into 5 concurrent batches internally
```

> [!TIP]
> **Shared-State Resilience**: Version 1.3.0+ includes internal **Global Backoff**. If one thread hits a `429 Too Many Requests`, the entire client pauses correctly across all threads to protect your IP reputation.

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
