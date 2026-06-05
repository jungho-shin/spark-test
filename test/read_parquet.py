import pandas as pd

file_path = r"D:\TAOS9938\Workspace\srt\data\019e98a8-7ceb-7841-b7e0-758793a17594_0_2_0.parquet"

df = pd.read_parquet(file_path)
print(df)