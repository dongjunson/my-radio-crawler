import os
from dotenv import load_dotenv
import psycopg2
import pandas as pd

# 환경 변수 로드
load_dotenv()

# 데이터베이스 연결 설정
db_config = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

print("데이터베이스 연결 시도 중...")
print(f"호스트: {db_config['host']}")
print(f"포트: {db_config['port']}")
print(f"사용자: {db_config['user']}")
print(f"데이터베이스: {db_config['database']}")

try:
    # 데이터베이스 연결
    conn = psycopg2.connect(**db_config)
    print("데이터베이스 연결 성공!")

    # SQL 쿼리 실행
    query = """
    SELECT broadcast_date, number, title, artist, description 
    FROM music_data 
    ORDER BY broadcast_date DESC, number ASC
    LIMIT 20
    """

    # pandas를 사용하여 결과를 DataFrame으로 변환
    df = pd.read_sql_query(query, conn)

    # 결과 출력
    print("\n최근 20개 방송의 음악 차트:")
    print(df.to_string(index=False))

except Exception as e:
    print(f"\n오류 발생: {str(e)}")
    print(f"오류 유형: {type(e).__name__}")
finally:
    if 'conn' in locals():
        conn.close()
        print("\n데이터베이스 연결 종료") 