"""
테이블 실제 저장 경로 확인
"""
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .remote("sc://localhost:15002") \
    .getOrCreate()

print("📌 테이블 실제 location 확인:")
spark.sql("DESCRIBE EXTENDED nessie.herb24.detection_logs") \
    .filter("col_name = 'Location'") \
    .show(truncate=False)

print("\n📌 테이블 properties 확인:")
spark.sql("SHOW TBLPROPERTIES nessie.herb24.detection_logs").show(truncate=False)

spark.stop()