import time
from pathlib import Path
import pandas as pd

RAW_DIR = Path(__file__).parent / "data" / "raw"
csv_path = RAW_DIR / "nyc311_raw_20261029_201332.csv"
parquet_path = RAW_DIR / "nyc311_raw_20261029_201332.parquet"

cols = ["borough", "complaint_type"]

def best_time(fn, runs=5):
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        result = fn()
        times.append(time.perf_counter() - start)
    return min(times), result

csv_secs, df_csv = best_time(lambda: pd.read_csv(csv_path, usecols=cols))
pq_secs, df_pq = best_time(lambda: pd.read_parquet(parquet_path, columns=cols))

print(f"CSV:     {csv_secs:.3f} s  shape={df_csv.shape}")
print(f"Parquet: {pq_secs:.3f} s  shape={df_pq.shape}")
print(f"Parquet was {csv_secs / pq_secs:.1f}x faster")
print()
print(df_pq["borough"].value_counts(dropna=False))