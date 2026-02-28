# Portfolio Use Cases: pysecop

`pysecop` is more than a wrapper—it's an enabler for high-impact analytics. Here are three strategic use cases demonstrating how this package can be used to solve complex business problems.

## 1. Corruption Detection & Anomaly Analysis (Forensics)

**The Problem**: Public procurement often hides patterns of bid-rigging or anomalous pricing that are invisible to manual review.

**The pysecop Solution**:
Using `QueryBuilder`, we can extract all contracts for a specific "high-risk" category and apply statistical anomaly detection (e.g., Isolation Forest or IQR) to identify outliers in contract values relative to the average for that region.

```python
# Extracting data for anomaly detection
qb.select(["documento_proveedor", "valor_del_contrato", "nombre_entidad"]) \
  .where_custom("tipo_de_contrato = 'Suministros'")
# ... analysis with Scikit-learn
```

**Portfolio takeaway**: Demonstrates an understanding of **Risk Management** and **Unsupervised Learning** applied to public data.

---

## 2. Market Intelligence & Supplier Graph Analysis

**The Problem**: Government entities struggle to identify if they are over-reliant on a single supplier or if "shell companies" are winning multiple contracts under different names.

**The pysecop Solution**:
By fetching contracts from both SECOP I and II using `get_contracts_by_ids` and processing them into a unified format with `DataProcessor`, you can build a **Supplier Interaction Graph**. Node attributes would include "Average Contract Value" and edges would represent shared contracts between entities and suppliers.

**Portfolio takeaway**: Showcases skills in **Network Theory**, **Entity Resolution**, and **Multi-source Data Integration**.

---

## 3. Real-time Monitoring for Public Transparency (ETL/MLOps)

**The Problem**: Transparency portals are often updated with significant delays, hindering investigative journalism or citizen oversight.

**The pysecop Solution**:
`pysecop`’s Docker-ready nature and simplified API make it the perfect "Infection Point" for an ETL pipeline. By running the client inside a scheduled task (e.g., Airflow or GitHub Actions), changes in contract status can be streamed to a vector database for RAG-based transparency bots.

**Portfolio takeaway**: Highlights expertise in **Data Engineering Lifecycle**, **Containerization**, and **Infrastructure as Code**.

---

## Summary of Business Impact

| Strategic Goal | pysecop Contribution | Outcome |
| :--- | :--- | :--- |
| **Transparency** | Programmatic access to filtered data. | Increased citizen trust and oversight. |
| **Efficiency** | Automated cleaning and normalization. | Reductions in ETL development time by ~60%. |
| **Intelligence** | High-fidelity data for ML models. | Early detection of procurement fraud. |
