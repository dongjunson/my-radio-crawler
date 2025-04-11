import os
from dotenv import load_dotenv
import psycopg2
from urllib.parse import quote_plus

# 환경 변수 로드
load_dotenv()

# Supabase 연결 정보
password = quote_plus("chyk8125!@#")
host = "aws-0-ap-northeast-2.pooler.supabase.com"
port = "5432"
database = "postgres"
user = "postgres.wzsgtagctsakerwmrurw"

conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"

try:
    # 데이터베이스 연결 시도
    conn = psycopg2.connect(
        conn_string,
        connect_timeout=10
    )
    print("✅ 데이터베이스 연결 성공!")
    
    # 테이블 생성
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS music_data (
        seqID INTEGER,
        broadcast_date TEXT,
        number INTEGER,
        title TEXT,
        artist TEXT,
        description TEXT,
        PRIMARY KEY(seqID, number)
    );
    """)
    conn.commit()
    print("✅ 테이블 생성 완료!")
    
    conn.close()
    
except Exception as e:
    print(f"❌ 데이터베이스 연결 실패: {str(e)}")
    print("\n연결 문자열 확인:")
    print(conn_string) 