# DataLake 전체 파이프라인 실행 가이드

## 아키텍처

```
┌──────────────────────────────────────────────────────────┐
│                    DataLake Stack                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐  ┌───────────┐  ┌──────────────┐      │
│  │   MinIO     │  │  Nessie   │  │ Spark        │      │
│  │ (S3 Store)  │  │ (Metadata)│  │ (Processing) │      │
│  └─────────────┘  └───────────┘  └──────────────┘      │
│                                                          │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │  Kudu Cluster    │  │ StarRocks Cluster │           │
│  │ ┌──────────────┐ │  │ ┌──────────────┐  │           │
│  │ │ Master       │ │  │ │ FE           │  │           │
│  │ ├──────────────┤ │  │ ├──────────────┤  │           │
│  │ │ Tablet Svr 1 │ │  │ │ BE           │  │           │
│  │ └──────────────┘ │  │ └──────────────┘  │           │
│  └──────────────────┘  └──────────────────┘            │
│         ▲                                                │
│         │ (Impala writes)                               │
│  ┌──────────────┐                                        │
│  │   Impala     │                                        │
│  └──────────────┘                                        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## 데이터 흐름

```
1. Impala → Kudu (대량 데이터 삽입)
           ↓
2. StarRocks reads Kudu via Kudu Catalog
           ↓
3. StarRocks stores data (native tables)
           ↓
4. Applications query StarRocks
```

## 실행 단계

### 1단계: 전체 서비스 시작

```bash
cd datalake
docker-compose up -d

# 서비스 확인
docker-compose ps
```

**포트 맵핑:**
- MinIO: `9001` (http://localhost:9001)
- Nessie: `19120` (http://localhost:19120)
- Spark: `8080`, `7077`
- Kudu Master: `8050` (UI), `7050` (RPC)
- Kudu TServer: `8051` (UI), `7051` (RPC)
- StarRocks FE: `8030` (UI), `9030` (Query)
- StarRocks BE: `8040` (UI), `9060`, `9070`
- Impala: `25000` (UI), `21050`

### 2단계: StarRocks 초기화 (Catalog 생성)

```bash
# 초기화 스크립트 실행
bash datalake/01-init-starrocks.sh
```

**생성되는 것:**
- Kudu Catalog: `kudu_catalog`
- Iceberg Catalog: `iceberg_catalog`
- 기본 테이블: `sr_orders`, `sr_customers`, `sr_products`

### 3단계: Kudu에 데이터 삽입 (Impala 이용)

```bash
# Impala를 통해 Kudu에 대량 데이터 삽입
bash datalake/02-insert-kudu-data.sh
```

**삽입 데이터:**
- `kudu_orders`: 1000 rows
- `kudu_customers`: 100 rows
- `kudu_products`: 50 rows

### 4단계: StarRocks에서 Kudu 데이터 읽기 및 저장

```bash
# StarRocks를 통해 Kudu 데이터 읽기 및 StarRocks에 저장
bash datalake/03-insert-starrocks-data.sh
```

**처리 내용:**
- Kudu에서 데이터 조회 (Kudu Catalog via StarRocks)
- StarRocks native 테이블에 데이터 삽입
- 확장 데이터 생성 및 삽입 (10배 확장)
- 최종 통계 출력

## 빠른 실행 (한 번에 모두)

```bash
# 1. 디렉토리 이동
cd datalake

# 2. 모든 서비스 시작
docker-compose up -d

# 3. 모든 초기화 스크립트 실행 (순서 중요!)
sleep 30  # 서비스 안정화 대기
bash 01-init-starrocks.sh
sleep 20
bash 02-insert-kudu-data.sh
sleep 20
bash 03-insert-starrocks-data.sh
```

## 데이터 조회

### StarRocks 직접 조회

```bash
# StarRocks에 접속
mysql -h localhost -P 9030 -u root

# 쿼리 예제
USE default;

-- Kudu의 Orders 데이터 조회
SELECT COUNT(*) FROM kudu_catalog.kudu_default.kudu_orders;

-- StarRocks Orders 데이터 조회
SELECT COUNT(*) FROM sr_orders;

-- JOIN 쿼리 (Kudu + StarRocks)
SELECT 
    o.order_id,
    c.customer_name,
    p.product_name,
    o.amount
FROM kudu_catalog.kudu_default.kudu_orders o
JOIN kudu_catalog.kudu_default.kudu_customers c ON o.customer_id = c.customer_id
JOIN sr_products p ON CAST(p.product_id AS INT) = o.order_id % 50
LIMIT 10;
```

### Impala 직접 사용

```bash
# Impala 셸 접속
impala-shell -i localhost:21050

# Kudu 테이블 조회
USE kudu_default;
SELECT * FROM kudu_orders LIMIT 10;
SELECT COUNT(*) FROM kudu_customers;
SELECT * FROM kudu_products;
```

### Kudu Web UI

```
http://localhost:8050 (Master)
http://localhost:8051 (Tablet Server)
```

## 카탈로그 쿼리

### Kudu Catalog 테이블 조회

```sql
USE kudu_catalog;
SHOW TABLES;

-- 테이블 상세 정보
DESC kudu_default.kudu_orders;
```

### Iceberg Catalog 테이블 조회

```sql
USE iceberg_catalog;
SHOW TABLES;
```

## 성능 모니터링

### StarRocks Web UI
```
http://localhost:8030
```
- Queries: 실행된 쿼리 목록
- Backend: BE 노드 상태
- System: 시스템 정보

### Kudu Web UI
```
http://localhost:8050/tables
```
- 테이블 목록과 상태
- Tablet 분포
- I/O 통계

### Impala Web UI
```
http://localhost:25000
```
- 쿼리 실행 통계
- 메모리 사용량

## 트러블슈팅

### 컨테이너 로그 확인
```bash
docker-compose logs starrocks-fe
docker-compose logs starrocks-be
docker-compose logs kudu-master
docker-compose logs impala
```

### 재시작
```bash
# 특정 서비스 재시작
docker-compose restart starrocks-fe
docker-compose restart kudu-master

# 전체 중지 및 시작
docker-compose down
docker-compose up -d
```

### MySQL/Impala 클라이언트 설치

#### macOS
```bash
brew install mysql-client
brew install impala-shell
```

#### Ubuntu/Debian
```bash
sudo apt-get install mysql-client
sudo apt-get install impala-shell
```

#### CentOS/RHEL
```bash
sudo yum install mysql
sudo yum install impala-shell
```

## 주요 대기 시간

- 서비스 시작 후 안정화: ~30초
- StarRocks 초기화: ~10초
- Kudu 데이터 삽입: ~20초
- StarRocks 데이터 읽기/삽입: ~15초

**전체 소요 시간: ~3-4분**

## 참고사항

1. **데이터 볼륨**: 테스트용으로 소량의 데이터를 사용합니다.
   - 프로덕션: INSERT INTO SELECT 쿼리의 LIMIT 절 제거

2. **스키마 매핑**: Kudu의 PRIMARY KEY 제약사항 고려
   - Kudu는 기본 키가 필수입니다.

3. **성능 최적화**:
   - PARTITION 설정으로 쿼리 성능 향상
   - BUCKETS 수 조정으로 분산 최적화

4. **백업**:
   - 실제 운영은 별도의 백업 전략이 필요합니다.
