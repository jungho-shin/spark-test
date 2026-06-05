import os
import sys
from pathlib import Path
from pyspark.sql import SparkSession

os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable


def load_data_with_spark(csv_path):
    print("🚀 1. Spark Session 초기화 및 StarRocks 커넥터 다운로드 중...")
    # Spark 3.5용 StarRocks 커넥터를 maven 리포지토리에서 자동 다운로드합니다.
    spark = SparkSession.builder \
        .appName("Herb24_Spark_to_StarRocks") \
        .config("spark.jars.packages", "com.starrocks:starrocks-spark-connector-3.5_2.12:1.1.2,mysql:mysql-connector-java:8.0.33") \
        .getOrCreate()

    print(f"📦 2. CSV 데이터 읽어오기: {csv_path}")
    # CSV 파일을 Spark DataFrame으로 로드
    df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(str(csv_path))

    # 데이터 스키마 확인 (선택 사항)
    df.printSchema()

    print("⚡ 3. StarRocks로 병렬 분산 적재 시작...")
    # 커넥터를 사용해 StarRocks 테이블에 꽂아 넣습니다.
    # HTTP 포트(8030)와 JDBC 포트(9030)를 모두 사용합니다.
    df.write.format("starrocks") \
        .option("starrocks.fe.http.url", "localhost:8030") \
        .option("starrocks.fe.jdbc.url", "jdbc:mysql://localhost:9030/herb24") \
        .option("starrocks.table.identifier", "herb24.detection_logs") \
        .option("starrocks.user", "root") \
        .option("starrocks.password", "") \
        .mode("append") \
        .save()

    print("✅ Spark를 통한 StarRocks 대용량 적재 완료!")
    spark.stop()


if __name__ == "__main__":
    # 경로 설정 (디렉토리 구조에 맞게 조절하세요)
    script_dir = Path(__file__).resolve().parent.parent
    csv_filename = script_dir / "herb24_100k_data.csv"

    # 파일 존재 여부 확인 후 실행
    if csv_filename.exists():
        load_data_with_spark(csv_filename)
    else:
        print(f"❌ 에러: CSV 파일을 찾을 수 없습니다. 경로: {csv_filename}")