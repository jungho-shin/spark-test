from pyspark.sql import SparkSession

if __name__ == "__main__":
    spark = SparkSession.builder \
        .remote("sc://tst-server:15002") \
        .getOrCreate()

    spark.sql("CREATE NAMESPACE IF NOT EXISTS hive.test_db")

    # 연결 종료
    spark.stop()
