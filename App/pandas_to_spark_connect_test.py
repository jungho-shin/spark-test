import pandas as pd
import numpy as np
import time


# 1. Spark Connect 세션 연결
# 컨테이너 포트 15002가 spark-connect 포트입니다.
from pyspark.sql.connect.session import SparkSession
# spark = SparkSession.builder.remote("sc://localhost:15002").get_session()
spark = SparkSession.builder.remote("sc://server.pc:15002").getOrCreate()

## 실험 결과
## sp-conn  On server : Pnadas DF 0.15 createDataFrame : 0.11 count : 4.29
## sp-conn  On remote : Pnadas DF 0.27 createDataFrame : 0.15 count : 21.96
## sp       On local  : Pnadas DF 0.25 createDataFrame : 2.06 count : 4.21

#
# from pyspark.sql import SparkSession
# spark = SparkSession.builder.appName("aa") \
#     .config("spark.driver.memory", "8g") \
#     .config("spark.executor.memory", "8g") \
#     .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
#     .config("spark.sql.execution.arrow.pyspark.fallback.enabled", "true") \
#     .getOrCreate()

print("--- 데이터 생성 시작 (50만 건) ---")
start_time = time.time()

# 2. 15개 컬럼을 가진 샘플 데이터 생성
num_rows = 300_000
data = {
    "id": np.arange(num_rows),
    "name": [f"user_{i}" for i in range(num_rows)],
    "age": np.random.randint(18, 90, size=num_rows),
    "salary": np.random.uniform(3000, 10000, size=num_rows),
    "score_a": np.random.rand(num_rows),
    "score_b": np.random.rand(num_rows),
    "score_c": np.random.rand(num_rows),
    "category": np.random.choice(['A', 'B', 'C', 'D'], size=num_rows),
    "is_active": np.random.choice([True, False], size=num_rows),
    "timestamp": pd.date_range("2026-01-01", periods=num_rows, freq="S"),
    "col_11": np.random.randn(num_rows),
    "col_12": np.random.randn(num_rows),
    "col_13": np.random.randn(num_rows),
    "col_14": np.random.randn(num_rows),
    "col_15": np.random.randn(num_rows)
}

pdf = pd.DataFrame(data)
end_time = time.time()
print(f"Pandas DF 생성 완료: {end_time - start_time:.4f} 초")

# 3. Pandas -> Spark Connect 변환 속도 측정
print("\n--- Spark Connect로 데이터 전송 및 변환 시작 ---")
conv_start_time = time.time()


n_start_time = time.time()
# createDataFrame 시 Arrow 최적화가 자동으로 적용됩니다.
sdf = spark.createDataFrame(pdf)
n_end_time = time.time()

print(f" createDataFrame : {n_end_time -n_start_time } ")

# Spark는 Lazy Evaluation이므로, 실제 데이터를 처리하게 만들어야 전송 속도가 잡힙니다.

n_start_time = time.time()
count = sdf.count()
n_end_time = time.time()

print(f" count : {n_end_time -n_start_time } ")

conv_end_time = time.time()
print(f"Spark Connect 변환 및 Count 완료: {conv_end_time - conv_start_time:.4f} 초")
print(f"총 처리 건수: {count} 건")

# 데이터 확인
sdf.show(5)