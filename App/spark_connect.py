import os
import time

import pandas as pd
from pathlib import Path
from pyspark.sql import SparkSession


def load_data_via_connect(csv_path):
    print("🌐 1. Spark Connect Server 연결 중 (sc://localhost:15002)...")

    # [Point] 클라이언트는 복잡한 설정 없이 서버 주소만 필요합니다.
    # 모든 Iceberg/Hive 설정은 이미 Docker의 spark-connect 서버가 들고 있습니다.
    spark = SparkSession.builder \
        .remote("sc://localhost:15002") \
        .getOrCreate()

    print(f"🐼 2. Pandas로 데이터 읽기: {csv_path.name}")
    # Spark Connect에서 로컬 파일을 직접 spark.read.csv로 읽으려면 서버에 파일이 있어야 하므로,
    # 클라이언트의 파일을 Pandas로 먼저 읽는 것이 가장 확실한 방법입니다.
    pdf = pd.read_csv(csv_path)

    # 시간 데이터 포맷팅 (Pandas object -> datetime64)
    pdf['detect_time'] = pd.to_datetime(pdf['detect_time'])

    print(f"🚀 3. Pandas DF -> Spark DF 변환 및 전송 (건수: {len(pdf)})")
    # Arrow를 통해 Spark 서버로 데이터가 전송됩니다.
    n_start_time = time.time()
    sdf = spark.createDataFrame(pdf)
    n_end_time = time.time()
    print(f" createDataFrame : {n_end_time - n_start_time} ")

    print("⚡ 4. Iceberg 테이블 적재 시작 (hive.test_db.detection_logs)...")
    # 스키마가 없다면 생성, 있다면 덮어쓰기/추가
    # 처음 생성 시에는 createOrReplace(), 이후엔 append() 추천
    n_start_time = time.time()
    sdf.writeTo("hive.test_db.detection_logs") \
        .tableProperty("write.format.default", "parquet") \
        .createOrReplace()
    n_end_time = time.time()
    print(f" createOrReplace : {n_end_time - n_start_time} ")

    print("✅ 5. 적재 데이터 검증 (Spark SQL)")
    # SQL 쿼리도 Connect 서버에서 실행되어 결과만 리턴받습니다.
    n_start_time = time.time()
    count_df = spark.sql("SELECT count(*) as total FROM hive.test_db.detection_logs")
    n_end_time = time.time()
    print(f" count : {n_end_time - n_start_time} ")
    count_df.show()

    spark.sql("SELECT * FROM hive.test_db.detection_logs LIMIT 5").show(truncate=False)

    print("🎉 Iceberg 적재 완료!")
    print("StarRocks 조회 확인:")
    print("  SELECT * FROM iceberg_catalog.test_db.detection_logs LIMIT 10;")

    # 연결 종료
    spark.stop()


if __name__ == "__main__":
    # 데이터 경로 설정 (부모 디렉토리의 CSV 파일)
    script_dir = Path(__file__).resolve().parent.parent
    csv_filename = script_dir / "herb24_100k_data.csv"

    if csv_filename.exists():
        load_data_via_connect(csv_filename)
    else:
        print(f"❌ 에러: CSV 파일을 찾을 수 없습니다. 경로: {csv_filename}")