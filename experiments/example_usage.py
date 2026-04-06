from pysecop import SecopClient, DATASETS
import pandas as pd

def main():
    # 1. Initialize Client
    client = SecopClient()

    # 2. Unified Search across SECOP I & II
    # Jackass-Proof: You can now provide formatted NITs (with dashes/dots) 
    # and they will be automatically cleaned for numeric fields in SECOP II!
    provider_nit = "899999027" 
    
    print(f"Executing Unified Search for NIT: {provider_nit}...")
    # search() automatically:
    # - Fetches from both SECOP version
    # - Consolidates results into a single DataFrame
    # - Synchronizes column names (Unified Schema)
    # - Standardizes dates, URLs, and categorical fields
    # - Adds a 'source' column
    df = client.search(nit_entidad=provider_nit, limit=100)

    if not df.empty:
        print(f"\nSuccessfully retrieved {len(df)} consolidated records.")
        print("\nSummary by Source:")
        print(df["source"].value_counts())
        
        print(f"\nFinal Matrix Columns: {len(df.columns)}")
        
        # Verify specific SECOP I columns that the user asked about
        special_cols = ['cumple_sentencia_t302', 'uid', 'anno_cargue_secop']
        found_special = [c for c in special_cols if c in df.columns]
        print(f"Verified Source-Specific Columns: {found_special}")

        print("\nTop 5 Unified results (Displaying first 5 core columns):")
        core_cols = ["source", "nombre_entidad", "valor_del_contrato", "fecha_de_firma", "estado_contrato"]
        # Ensure we only try to display columns that were actually retrieved
        display_cols = [c for c in core_cols if c in df.columns]
        print(df[display_cols].head())
        
        # Tip for the user
        if 'cumple_sentencia_t302' in df.columns:
            print(f"\nSample data for 'cumple_sentencia_t302' (from SECOP I rows):")
            print(df[df['source'] == 'SECOP I']['cumple_sentencia_t302'].head())
    else:
        print("No records found for the given criteria.")

    # 3. Targeted searching by ID
    print("\nSearching by specific Contract ID...")
    # This also uses the unified engine under the hood
    contract_df = client.get_contracts_by_ids(["CO1.PNN.123456"], id_type="numero_contrato")
    
    if not contract_df.empty:
        print(f"Found contract in source: {contract_df['source'].iloc[0]}")
        print(f"Contract Object: {contract_df['objeto_contrato'].iloc[0]}")

if __name__ == "__main__":
    main()
