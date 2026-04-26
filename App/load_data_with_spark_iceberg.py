# load_to_iceberg.py
import os
import sys
from pathlib import Path
from pyspark.sql import SparkSession

os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable


def load_data_to_iceberg(csv_path):
    print("🚀 1. Spark Session 초기화 (Iceberg + Hive Metastore Catalog)...")
    spark = (
        SparkSession.builder
        .appName("Herb24_Spark_to_Iceberg")
        .config(
            "spark.jars.packages",
            "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.0,"
            "org.apache.iceberg:iceberg-aws-bundle:1.5.0,"
            "org.apache.hadoop:hadoop-aws:3.3.4",
        )
        # === Iceberg 카탈로그: HMS 기반 ===
        .config("spark.sql.catalog.hive", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.hive.type", "hive")
        .config("spark.sql.catalog.hive.uri", "thrift://localhost:9083")
        .config("spark.sql.catalog.hive.warehouse", "s3a://warehouse/")
        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        )
        # === MinIO(S3A) 자격증명 ===
        .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000")
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin")
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin")
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config(
            "spark.hadoop.fs.s3a.aws.credentials.provider",
            "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
        )
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .getOrCreate()
    )

    print(f"📦 2. CSV 데이터 읽어오기: {csv_path}")
    df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(str(csv_path))
    )

    df.printSchema()
    print(f"총 {df.count()} 건 로드됨")

    print("⚡ 3. HMS Iceberg 테이블로 적재 시작...")
    # 네임스페이스(DB)가 없으면 생성 — location을 s3a://로 명시
    spark.sql(
        "CREATE NAMESPACE IF NOT EXISTS hive.test_db "
        "LOCATION 's3a://warehouse/test_db.db'"
    )
    df.writeTo("hive.test_db.detection_logs").createOrReplace()

    print("✅ 4. 적재 검증...")
    spark.sql("SELECT count(*) as total FROM hive.test_db.detection_logs").show()
    spark.sql("SELECT * FROM hive.test_db.detection_logs LIMIT 5").show(truncate=False)

    print("🎉 Iceberg 적재 완료! StarRocks에서 조회 가능:")
    print("  SELECT * FROM iceberg_catalog.test_db.detection_logs LIMIT 10;")

    spark.stop()


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent.parent
    csv_filename = script_dir / "herb24_100k_data.csv"

    if csv_filename.exists():
        load_data_to_iceberg(csv_filename)
    else:
        print(f"❌ 에러: CSV 파일을 찾을 수 없습니다. 경로: {csv_filename}")