from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, LongType, DoubleType, TimestampType
import pandas as pd
import numpy as np
import uuid
import time

print("🚀 Spark Connect 서버에 연결 중...")
spark = SparkSession.builder.remote("sc://localhost:15002").getOrCreate()
print("✅ 연결 성공!\n")

# 1. Spark용 명시적 스키마 정의 (Pandas -> Spark 번역표)
spark_schema = StructType([
    StructField("detect_id", StringType(), True),
    StructField("user_id", LongType(), True),
    StructField("herb_name", StringType(), True),
    StructField("confidence", DoubleType(), True),
    StructField("latitude", DoubleType(), True),
    StructField("longitude", DoubleType(), True),
    StructField("device_os", StringType(), True),
    StructField("detect_time", TimestampType(), True)
])

# 2. Pandas & Numpy를 이용한 50만 건 초고속 생성
print("⏳ Pandas로 50만 건의 랜덤 데이터를 생성합니다...")
start_time = time.time()
n = 500000

# Numpy의 배열 연산을 활용하여 C언어급 속도로 데이터 생성
user_ids = np.random.randint(1, 10001, size=n)
herbs = np.random.choice(['홍삼', '당귀', '감초', '도라지', '인삼', '천남성', '하수오', '천마'], size=n)
confidences = np.round(np.random.uniform(0.5, 1.0, size=n), 4)
latitudes = np.round(np.random.uniform(33.0, 38.0, size=n), 6)
longitudes = np.round(np.random.uniform(126.0, 130.0, size=n), 6)
oses = np.random.choice(['Android', 'iOS'], size=n)

# 시간(Timestamp) 데이터 생성 (2025년 1년치 랜덤)
start_ts = np.datetime64('2025-01-01T00:00:00')
random_seconds = np.random.randint(0, 31536000, size=n)
detect_times = start_ts + np.array(random_seconds, dtype='timedelta64[s]')

# UUID 생성 (List Comprehension이 가장 빠름)
detect_ids = [str(uuid.uuid4()) for _ in range(n)]

# 생성된 배열들을 모아서 하나의 Pandas DataFrame으로 조립
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

# 3. 데이터 적재 (Append)
print("🔄 데이터를 Spark로 넘겨 Iceberg 테이블에 적재합니다...")
# Pandas DF에 미리 짜둔 스키마를 강제로 입혀서 Spark DF로 변환
spark_df = spark.createDataFrame(pdf, schema=spark_schema)

# 기존 테이블에 밀어 넣기 (writeTo.append)
spark_df.writeTo("nessie.herb24.detection_logs").append()

end_time = time.time()
print(f"✅ 50만 건 Iceberg 적재 완료! (적재 소요 시간: {end_time - pandas_gen_time:.2f}초)\n")

# 4. 최종 결과 검증
print("📊 현재 테이블의 총 데이터 누적 건수:")
spark.sql("SELECT count(*) as total_count FROM nessie.herb24.detection_logs").show()