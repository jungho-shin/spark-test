
#pandas_to_iceberg_type*


#스키마 조정 상황

🛠️ 상황 1: 특정 컬럼을 빼고 싶을 때 (Drop Column)
DB에는 device_os 컬럼이 있지만, 오늘 들어온 Pandas 데이터에는 이 컬럼이 없어서 스키마에서 빼고 싶을 때 쓰는 방법입니다.

Python
from pyspark.sql.types import StructType
```commandline
# 1. 원래 스키마 읽어오기
original_schema = spark.table("nessie.herb24.detection_logs").schema

# 2. 파이썬의 리스트 내포(List Comprehension)로 특정 컬럼만 쏙 빼기!
modified_fields = [
    field for field in original_schema.fields 
    if field.name != "device_os"  # device_os 컬럼은 제외해라!
]

# 3. 새로운 스키마로 재조립
adjusted_schema = StructType(modified_fields)

# 4. 적용
spark_df = spark.createDataFrame(pdf, schema=adjusted_schema)
```

🛠️ 상황 2: 특정 컬럼의 타입(Type)을 강제로 바꾸고 싶을 때 (Cast/Change Type)
DB에는 confidence가 DOUBLE로 되어있는데, 메모리를 아끼기 위해 혹은 Pandas 구조상 Spark에 넣을 때 FLOAT나 STRING으로 잠시 바꿔서 밀어 넣고 싶을 때 사용합니다.

Python
from pyspark.sql.types import StructType, StructField, StringType

```commandline
original_schema = spark.table("nessie.herb24.detection_logs").schema

# 빈 리스트를 준비하고 부품을 하나씩 검사하며 옮겨 담습니다.
adjusted_fields = []

for field in original_schema.fields:
    if field.name == "confidence":
        # confidence 컬럼을 만나면, 원래 타입을 무시하고 강제로 StringType으로 바꿔치기!
        adjusted_fields.append(StructField("confidence", StringType(), True))
    else:
        # 나머지는 원래 부품 그대로 넣기
        adjusted_fields.append(field)

# 새로운 스키마로 재조립
adjusted_schema = StructType(adjusted_fields)

# 적용
spark_df = spark.createDataFrame(pdf, schema=adjusted_schema)
```


