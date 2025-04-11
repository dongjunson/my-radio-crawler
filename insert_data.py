import os
from dotenv import load_dotenv
import psycopg2
from urllib.parse import quote_plus
import json

# 환경 변수 로드
load_dotenv()

# Supabase 연결 정보
password = quote_plus("chyk8125!@#")
host = "aws-0-ap-northeast-2.pooler.supabase.com"
port = "5432"
database = "postgres"
user = "postgres.wzsgtagctsakerwmrurw"

conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"

def insert_music_data(data):
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()
        
        # 데이터 삽입
        for item in data:
            cur.execute("""
                INSERT INTO music_data 
                (seqID, broadcast_date, number, title, artist, description)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (seqID, number) DO NOTHING
            """, (
                item['seqID'],
                item['broadcast_date'],
                item['number'],
                item['title'],
                item['artist'],
                item['description']
            ))
        
        conn.commit()
        print(f"✅ {len(data)}개의 데이터가 성공적으로 삽입되었습니다.")
        
    except Exception as e:
        print(f"❌ 데이터 삽입 중 오류 발생: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

# 테스트 데이터
test_data = [
    {
        "seqID": 1,
        "broadcast_date": "2024-03-20",
        "number": 1,
        "title": "테스트 곡 1",
        "artist": "테스트 아티스트 1",
        "description": "테스트 설명 1"
    },
    {
        "seqID": 1,
        "broadcast_date": "2024-03-20",
        "number": 2,
        "title": "테스트 곡 2",
        "artist": "테스트 아티스트 2",
        "description": "테스트 설명 2"
    }
]

if __name__ == "__main__":
    insert_music_data(test_data) 