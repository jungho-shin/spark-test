from pyspark.sql import SparkSession
import pandas as pd
import numpy as np
import uuid
import time

from App.create_data_spark_connect import start_time

print("🚀 Spark Connect 서버에 연결 중...")
spark = SparkSession.builder.remote("sc://localhost:15002").getOrCreate()
print("✅ 연결 성공!\n")

table_name = "nessie.herb24.detection_logs"

# 1. 🌟 핵심: DB(카탈로그)에서 기존 테이블의 스키마를 동적으로 읽어오기!
print(f"📂 [{table_name}] 테이블의 스키마를 불러옵니다...")
# spark.table()로 테이블을 껍데기만 읽은 뒤 .schema 속성을 가져옵니다.
table_schema = spark.table(table_name).schema

print("✅ 불러온 스키마 구조:")
for field in table_schema.fields:
    print(f"  - {field.name}: {field.dataType}")
print()

# 2. Pandas & Numpy를 이용한 50만 건 초고속 생성 (기존과 동일)
print("⏳ Pandas로 50만 건의 랜덤 데이터를 생성합니다...")
start_time = time.time()
n = 500000

user_ids = np.random.randint(1, 10001, size=n)
herbs = np.random.choice(['홍삼', '당귀', '감초', '도라지', '인삼', '천남성', '하수오', '천마'], size=n)
confidences = np.round(np.random.uniform(0.5, 1.0, size=n), 4)
latitudes = np.round(np.random.uniform(33.0, 38.0, size=n), 6)
longitudes = np.round(np.random.uniform(126.0, 130.0, size=n), 6)
oses = np.random.choice(['Android', 'iOS'], size=n)

start_ts = np.datetime64('2025-01-01T00:00:00')
random_seconds = np.random.randint(0, 31536000, size=n)
detect_times = start_ts + np.array(random_seconds, dtype='timedelta64[s]')
detect_ids = [str(uuid.uuid4()) for _ in range(n)]

pdf = pd.DataFrame({
    'detect_id': detect_ids,
    'user_id': user_ids,
    'herb_name': herbs,
    'confidence': confidences,
    'latitude': latitudes,
    'longitude': longitudes,
    'device_os': oses,
    'detect_time': detect_times
})

pandas_gen_time = time.time()
print(f"✅ Pandas 데이터 50만 건 생성 완료! (소요 시간: {pandas_gen_time - start_time:.2f}초)\n")

# 3. 데이터 적재 (불러온 스키마 적용)
print("🔄 동적 스키마를 적용하여 Iceberg 테이블에 적재합니다...")
# 사람이 짠 StructType 대신, 카탈로그에서 읽어온 table_schema를 그대로 입힙니다!

start_time = time.time()
spark_df = spark.createDataFrame(pdf, schema=table_schema)
end_time = time.time()

es_time =  (end_time - start_time)

print(f" es_time : {es_time}")

# 기존 테이블에 밀어 넣기
spark_df.writeTo(table_name).append()

end_time = time.time()
print(f"✅ 50만 건 Iceberg 적재 완료! (적재 소요 시간: {end_time - pandas_gen_time:.2f}초)\n")

# 4. 최종 결과 검증
print("📊 현재 테이블의 총 데이터 누적 건수:")
spark.sql(f"SELECT count(*) as total_count FROM {table_name}").show()