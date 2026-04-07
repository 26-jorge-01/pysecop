import pandas as pd
import time
import numpy as np
import sys
import os

# Add pysecop to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pysecop.data.processor import DataProcessor
from pysecop.data.config import DATASETS

def generate_mock_data(n=100000):
    print(f"Generating {n} mock records...")
    data = {
        "url_proceso": [f"{{'url': 'https://community.secop.gov.co/Public/Tendering/OpportunityDetail/Index?noticeUID=UID-{i}'}}" for i in range(n)],
        "fecha_firma": ["2023-01-01T00:00:00.000" if i % 2 == 0 else "01/01/2023 12:00:00 AM" for i in range(n)],
        "nombre_entidad": [f"ENTIDAD {i}" for i in range(n)],
        "es_pyme": ["Si" if i % 3 == 0 else "No" for i in range(n)],
    }
    return pd.DataFrame(data)

def run_benchmark():
    df = generate_mock_data(100000)
    config = DATASETS.get("SECOP_II")
    
    # We need to ensure columns match what config expects or what get_col can find
    # The current DataProcessor uses config.url_columns etc.
    
    print("Starting Benchmark (current implementation)...")
    start_time = time.time()
    processed_df = DataProcessor.process_dataset(df, config)
    end_time = time.time()
    
    print(f"Time taken for 100,000 rows: {end_time - start_time:.4f} seconds")
    print(f"First 3 URLs:\n{processed_df['url_proceso'].head(3)}\n")
    print(f"First 3 Dates:\n{processed_df['fecha_firma'].head(3)}\n")

if __name__ == "__main__":
    run_benchmark()
