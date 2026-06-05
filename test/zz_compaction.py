"""
Iceberg detection_logs 테이블 Compaction 예제
- catalog: nessie / 파티션 없는 테이블 기준
"""

from pyspark.sql import SparkSession
from datetime import datetime, timedelta

TABLE_LOCATION = "s3a://warehouse/herb24/detection_logs_23932ee7-c309-46e1-9bd1-d33c865b964f"

spark = SparkSession.builder \
    .remote("sc://localhost:15002") \
    .getOrCreate()

print("✅ Spark Connect 연결 성공")

# ─────────────────────────────────────────────
# 1. GC 활성화 (expire_snapshots/orphan 정리에 필요)
# ─────────────────────────────────────────────
print("\n⚙️  GC 활성화...")
spark.sql("""
    ALTER TABLE nessie.herb24.detection_logs
    SET TBLPROPERTIES ('gc.enabled' = 'true')
""")
print("✅ GC 활성화 완료")

# ─────────────────────────────────────────────
# 2. Compaction 전 파일 현황 확인
# ─────────────────────────────────────────────
print("\n📂 Compaction 전 파일 현황:")
spark.sql("""
    SELECT
        COUNT(*)                                         AS file_count,
        ROUND(SUM(file_size_in_bytes) / 1024 / 1024, 2) AS total_size_mb,
        ROUND(AVG(file_size_in_bytes) / 1024 / 1024, 2) AS avg_file_size_mb,
        SUM(record_count)                                AS total_records
    FROM nessie.herb24.detection_logs.files
""").show(truncate=False)

print("\n📊 현재 총 데이터 건수:")
spark.sql("SELECT COUNT(*) AS total_count FROM nessie.herb24.detection_logs").show()

# ─────────────────────────────────────────────
# 3. Compaction 수행 (binpack 전략)
#    현재 파일이 이미 ~106MB → min-file-size 조건 완화
# ─────────────────────────────────────────────
print("\n🔄 Compaction 시작 (binpack)...")
spark.sql("""
    CALL nessie.system.rewrite_data_files(
        table    => 'nessie.herb24.detection_logs',
        strategy => 'binpack',
        options  => map(
            'target-file-size-bytes', '536870912',
            'min-file-size-bytes',    '1',
            'max-file-size-bytes',    '805306368',
            'min-input-files',        '2'
        )
    )
""").show()

print("✅ Compaction 완료")

# ─────────────────────────────────────────────
# 4. Compaction 후 파일 현황 확인
# ─────────────────────────────────────────────
print("\n📂 Compaction 후 파일 현황:")
spark.sql("""
    SELECT
        COUNT(*)                                         AS file_count,
        ROUND(SUM(file_size_in_bytes) / 1024 / 1024, 2) AS total_size_mb,
        ROUND(AVG(file_size_in_bytes) / 1024 / 1024, 2) AS avg_file_size_mb,
        SUM(record_count)                                AS total_records
    FROM nessie.herb24.detection_logs.files
""").show(truncate=False)

# ─────────────────────────────────────────────
# 5. 스냅샷 정리
# ─────────────────────────────────────────────
print("\n📋 현재 스냅샷 목록 (최근 10개):")
spark.sql("""
    SELECT snapshot_id, committed_at, operation
    FROM nessie.herb24.detection_logs.snapshots
    ORDER BY committed_at DESC
    LIMIT 10
""").show(truncate=False)

older_than = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
print(f"\n🧹 오래된 스냅샷 제거 (기준: {older_than}, 최근 3개 유지)...")
spark.sql(f"""
    CALL nessie.system.expire_snapshots(
        table       => 'nessie.herb24.detection_logs',
        older_than  => TIMESTAMP '{older_than}',
        retain_last => 3
    )
""").show()

# ─────────────────────────────────────────────
# 6. 고아(orphan) 파일 정리
# ─────────────────────────────────────────────
print("\n🧹 고아(orphan) 파일 제거...")
spark.sql(f"""
    CALL nessie.system.remove_orphan_files(
        table      => 'nessie.herb24.detection_logs',
        older_than => TIMESTAMP '{older_than}',
        location   => '{TABLE_LOCATION}'
    )
""").show()

# ─────────────────────────────────────────────
# 7. 최종 검증
# ─────────────────────────────────────────────
print("\n📊 최종 총 데이터 건수 (데이터 손실 없는지 확인):")
spark.sql("SELECT COUNT(*) AS total_count FROM nessie.herb24.detection_logs").show()

print("\n✅ 모든 작업 완료")
spark.stop()