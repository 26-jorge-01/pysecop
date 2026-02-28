from pysecop import SecopClient, QueryBuilder, DATASETS, DataProcessor
import pandas as pd

def main():
    # 1. Initialize Client
    client = SecopClient()

    # 2. Define search parameters (e.g., specific provider documents)
    provider_ids = ["901000000", "800000000"] # Example IDs
    
    # 3. Use high-level method to fetch from both SECOP I and II
    print("Fetching contracts by provider IDs...")
    raw_results = client.get_contracts_by_ids(provider_ids, id_type="documento_proveedor")

    # 4. Process and clean results automatically using the config
    processed_results = {}
    for dataset_key, df in raw_results.items():
        if not df.empty:
            print(f"Processing {dataset_key}...")
            config = DATASETS[dataset_key]
            processed_results[dataset_key] = DataProcessor.process_dataset(df, config)
            print(f"Cleaned {len(processed_results[dataset_key])} records for {dataset_key}.")
            print(processed_results[dataset_key].head(2))

    # Example of a custom query using QueryBuilder
    print("\nExecuting custom query for SECOP II...")
    qb = QueryBuilder()
    qb.select(["id_contrato", "valor_del_contrato", "nombre_entidad"])
    qb.where_custom("valor_del_contrato > 100000000")
    qb.limit(5)
    
    custom_df = client.fetch("SECOP_II", qb)
    if not custom_df.empty:
        clean_custom_df = DataProcessor.process_dataset(custom_df, DATASETS["SECOP_II"])
        print("Custom Query Results (Cleaned):")
        print(clean_custom_df)

if __name__ == "__main__":
    main()
