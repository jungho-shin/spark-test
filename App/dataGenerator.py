import csv
import random
import uuid
from datetime import datetime, timedelta
import time


def generate_herb_data(filename, num_rows=100000):
    print(f"🌿 [약초 24] {num_rows}건의 가상 빅데이터 생성을 시작합니다...")
    start_time = time.time()

    # 약초 종류 (정상 약초와 독초 섞음)
    herbs = ["산삼", "도라지", "당귀", "하수오", "인삼", "영지버섯", "천마", "독미나리", "천남성"]
    os_list = ["Android", "iOS"]

    # 기준 날짜 설정
    base_time = datetime(2025, 1, 1)

    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # CSV 헤더 (StarRocks 테이블 만들 때 쓸 컬럼들)
        writer.writerow(
            ["detect_id", "user_id", "herb_name", "confidence", "latitude", "longitude", "device_os", "detect_time"])

        batch = []
        for i in range(1, num_rows + 1):
            detect_id = str(uuid.uuid4())
            user_id = random.randint(1, 10000)
            herb_name = random.choice(herbs)
            confidence = round(random.uniform(0.50, 0.99), 4)  # AI 확신도 (50~99%)
            lat = round(random.uniform(33.0, 38.0), 6)  # 한국 위도
            lon = round(random.uniform(126.0, 131.0), 6)  # 한국 경도
            device_os = random.choice(os_list)

            # 1년치 랜덤 시간 부여
            delta_seconds = random.randint(0, 365 * 24 * 60 * 60)
            detect_time = (base_time + timedelta(seconds=delta_seconds)).strftime('%Y-%m-%d %H:%M:%S')

            batch.append([detect_id, user_id, herb_name, confidence, lat, lon, device_os, detect_time])

            # 메모리 관리를 위해 1만 건마다 디스크에 쓰기
            if i % 10000 == 0:
                writer.writerows(batch)
                batch = []
                print(f"진행 상황: {i} / {num_rows} 건 생성 완료...")

        # 남은 찌꺼기 데이터 쓰기
        if batch:
            writer.writerows(batch)

    end_time = time.time()
    print(f"✅ 생성 완료! 파일명: {filename} (소요 시간: {round(end_time - start_time, 2)}초)")


if __name__ == "__main__":
    # 원하는 파일명과 건수를 입력하세요. (기본 10만 건)
    generate_herb_data("../herb24_100k_data.csv", 500000)
    # generate_herb_data("../herb24_100k_data.csv", 100)