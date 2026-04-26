from pyspark.sql import SparkSession
import time

print("🚀 Spark Connect 서버에 연결 중...")
spark = SparkSession.builder.remote("sc://localhost:15002").getOrCreate()
print("✅ 연결 성공!\n")

# 1. 네임스페이스 및 테이블 생성 (기존과 동일)
spark.sql("CREATE NAMESPACE IF NOT EXISTS nessie.herb24")


# # ✨ 핵심 추가: 기존에 만든 4컬럼짜리 테이블을 완전히 삭제합니다!
# print("🗑️ 기존의 구형 테이블을 삭제합니다...")
# spark.sql("DROP TABLE IF EXISTS nessie.herb24.detection_logs")

create_table_query = """
CREATE TABLE IF NOT EXISTS nessie.herb24.detection_logs (
    detect_id STRING,
    user_id BIGINT,
    herb_name STRING,
    confidence DOUBLE,
    latitude DOUBLE,
    longitude DOUBLE,
    device_os STRING,
    detect_time TIMESTAMP
)
USING iceberg
PARTITIONED BY (months(detect_time), bucket(4, user_id))
TBLPROPERTIES (
    'format-version' = '2',
    'write.update.mode' = 'merge-on-read',
    'write.delete.mode' = 'merge-on-read',
    'write.target-file-size-bytes' = '134217728'
)
"""
spark.sql(create_table_query)
print("✅ 테이블 준비 완료!\n")

# 2. 30만 건 데이터 생성 (Spark 내장 함수 활용)
print("⏳ 30만 건의 랜덤 데이터를 생성하고 적재합니다. (잠시만 기다려주세요...)")
start_time = time.time()

# spark.range(300000)으로 30만 개의 빈 행을 만들고, selectExpr로 가짜 데이터를 채웁니다.
df = spark.range(300000).selectExpr(
    "uuid() as detect_id",
    "cast(rand() * 10000 as bigint) + 1 as user_id", # 1~10000번 유저 랜덤
    "element_at(array('홍삼', '당귀', '감초', '도라지', '인삼', '천남성', '하수오', '천마'), cast(rand() * 8 as int) + 1) as herb_name",
    "round(rand() * 0.5 + 0.5, 4) as confidence", # 0.5 ~ 1.0 랜덤
    "round(33.0 + rand() * 5.0, 6) as latitude",  # 한국 위도 근처 랜덤
    "round(126.0 + rand() * 4.0, 6) as longitude", # 한국 경도 근처 랜덤
    "element_at(array('Android', 'iOS'), cast(rand() * 2 as int) + 1) as device_os",
    "timestamp('2025-01-01 00:00:00') + interval 1 second * cast(rand() * 31536000 as int) as detect_time" # 2025년 1년치 랜덤 시간
)

# 3. Iceberg 테이블에 병렬 적재 (DataFrame API 사용)
df.writeTo("nessie.herb24.detection_logs").append()

end_time = time.time()
print(f"✅ 30만 건 데이터 적재 완료! (소요 시간: {end_time - start_time:.2f}초)\n")

# 4. 검증: 전체 데이터 건수 및 샘플 5건 출력
print("📊 현재 테이블의 총 데이터 건수:")
spark.sql("SELECT count(*) as total_count FROM nessie.herb24.detection_logs").show()

print("🔍 샘플 데이터 5건:")
spark.sql("SELECT * FROM nessie.herb24.detection_logs LIMIT 5").show()