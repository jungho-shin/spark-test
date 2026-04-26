import os
from pathlib import Path

import requests
import time


def stream_load_to_starrocks(file_path):
    print(f"🚀 StarRocks로 '{file_path}' 데이터 적재를 시작합니다...")
    start_time = time.time()

    # StarRocks API 주소 (데이터베이스: herb24, 테이블: detection_logs)
    ## TODO 원래는 FE 주소로 보내지만
    ## 지금은 BE 로
    url = "http://localhost:8040/api/herb24/detection_logs/_stream_load"

    # Stream Load 설정 헤더
    headers = {
        "column_separator": ",",  # CSV 구분자
        "skip_header": "1",  # 첫 번째 줄(컬럼명) 건너뛰기
        "Expect": "100-continue"  # 대용량 파일 전송 안정성 확보
    }

    try:
        # 파일을 바이너리 읽기 모드로 열어서 통째로 HTTP PUT 전송
        with open(file_path, 'rb') as f:
            response = requests.put(
                url,
                headers=headers,
                auth=('root', ''),  # StarRocks 기본 계정 (비밀번호 없음)
                data=f
            )

        print("==================")

        result = response.json()
        end_time = time.time()

        # 결과 확인
        if result.get("Status") == "Success":
            print(f"✅ 업로드 성공! 벼락같은 속도: {round(end_time - start_time, 2)}초")
            print(f"📊 적재된 행 개수: {result.get('NumberLoadedRows')} 건")
        else:
            print("❌ 업로드 실패!")
            print(f"상세 에러: {result.get('Message')}")
            print(result)

    except FileNotFoundError:
        print(f"❌ 에러: '{file_path}' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
    except Exception as e:
        print(f"❌ 에러 발생: {e}")


if __name__ == "__main__":
    # 아까 만든 10만 건 CSV 파일명

    # script_dir = os.path.dirname(os.path.abspath(__file__))
    #
    # print(script_dir)
    script_dir = Path(__file__).resolve().parent.parent
    csv_filename = script_dir / "herb24_100k_data.csv"

    stream_load_to_starrocks(csv_filename)


    # csv_filename = "herb24_100k_data.csv"
    # stream_load_to_starrocks(csv_filename)