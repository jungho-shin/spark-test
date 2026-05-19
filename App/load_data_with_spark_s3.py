import uuid
from datetime import datetime
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("local-to-minio")
    .master("local[*]")
    # MinIO 접근에 필요한 라이브러리 (Spark 3.5.0 = hadoop 3.3.4)
    .config("spark.jars.packages",
            "org.apache.hadoop:hadoop-aws:3.3.4,"
            "com.amazonaws:aws-java-sdk-bundle:1.12.262")
    # MinIO 엔드포인트 설정
    .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000")
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin")
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin")
    .config("spark.hadoop.fs.s3a.path.style.access", "true")   # MinIO 필수
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .config("spark.hadoop.fs.s3a.aws.credentials.provider",
            "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
    .config("spark.sql.shuffle.partitions", "4")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

# 데이터 생성 (메모리 상에 존재)
df = spark.createDataFrame(
    [(1, "Leen", "KR", 77.5),
     (2, "Youn",  "US", 82.1),
     (3, "Park", "KR", 65.3),
     (4, "Sim", "US", 71.0)],
    schema=["id", "name", "country", "score"],
)

# ─── 식별자가 포함된 파일명 생성 ──────────────────────
BUCKET   = "lake"
now      = datetime.now()
ts       = now.strftime("%Y%m%d_%H%M%S")
uid      = uuid.uuid4().hex[:8]
filename = f"people_{ts}_{uid}.parquet"      # 예: people_20260519_134215_a3f9c2e1.parquet

tmp_dir    = f"s3a://{BUCKET}/_tmp/{uid}"
final_path = f"s3a://{BUCKET}/people/{filename}"

# 1) Spark가 임시 디렉토리에 단일 part 파일로 쓰기
(df.coalesce(1)
   .write
   .mode("overwrite")
   .option("compression", "snappy")
   .parquet(tmp_dir))

# 2) JVM Hadoop FileSystem API로 part 파일을 원하는 이름으로 이동
hadoop_conf = spark._jsc.hadoopConfiguration()
URI         = spark._jvm.java.net.URI
HPath       = spark._jvm.org.apache.hadoop.fs.Path
FileSystem  = spark._jvm.org.apache.hadoop.fs.FileSystem
fs          = FileSystem.get(URI(f"s3a://{BUCKET}/people/"), hadoop_conf)

# 임시 디렉토리에서 part-*.parquet 찾기
part_file = next(
    s.getPath() for s in fs.listStatus(HPath(tmp_dir))
    if s.getPath().getName().endswith(".parquet")
)

# 기존 동일 이름 파일이 있으면 삭제 (overwrite)
final_hpath = HPath(final_path)
if fs.exists(final_hpath):
    fs.delete(final_hpath, False)

# rename (S3A 내부적으로 copy + delete)
fs.rename(part_file, final_hpath)
# 임시 디렉토리 삭제
fs.delete(HPath(tmp_dir), True)

print(f"✅ saved: {final_path}")

# 3) 다시 읽기
df2 = spark.read.parquet(final_path)
df2.show()

spark.stop()