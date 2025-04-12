import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import psycopg2
from time import sleep
from urllib.parse import quote_plus
from datetime import datetime
import re
from utils import convert_korean_date_to_iso

# 환경 변수 로드
load_dotenv()

# Supabase 연결 정보
password = quote_plus("chyk8125!@#")
host = "aws-0-ap-northeast-2.pooler.supabase.com"
port = "5432"
database = "postgres"
user = "postgres.wzsgtagctsakerwmrurw"

conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"

# 데이터베이스 연결
conn = psycopg2.connect(conn_string)
cur = conn.cursor()

# 테이블 생성 (broadcast_date를 DATE 타입으로 변경)
cur.execute('''
CREATE TABLE IF NOT EXISTS music_data (
    seqID INTEGER,
    broadcast_date DATE,
    number INTEGER,
    title TEXT,
    artist TEXT,
    description TEXT,
    PRIMARY KEY(seqID, number)
)
''')

# 마지막 성공한 seqID를 저장할 테이블 생성
cur.execute('''
CREATE TABLE IF NOT EXISTS last_successful_seq (
    id SERIAL PRIMARY KEY,
    seqID INTEGER NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# 실패한 날짜를 저장할 테이블 생성 (이미 존재하면 유지)
cur.execute('''
CREATE TABLE IF NOT EXISTS failed_dates (
    seqID INTEGER PRIMARY KEY,
    original_date TEXT,
    error_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

# 최대 seqID
MAX_SEQ_ID = 7000
BASE_URL = "https://miniweb.imbc.com/Music/View?seqID={}&progCode=RAMFM300"

headers = {
    'User-Agent': 'Mozilla/5.0'
}

# 마지막으로 성공적으로 저장된 seqID 확인
cur.execute("SELECT seqID FROM last_successful_seq ORDER BY id DESC LIMIT 1")
last_saved_seq_id = cur.fetchone()
last_saved_seq_id = last_saved_seq_id[0] if last_saved_seq_id else 0
print(f"마지막으로 저장된 seqID: {last_saved_seq_id}")

try:
    for seqID in range(last_saved_seq_id + 1, MAX_SEQ_ID + 1):
        url = BASE_URL.format(seqID)
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"[{seqID}] 페이지를 가져오는 데 실패했습니다.")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')

        # 날짜 추출
        date_tag = soup.select_one(".view-title .title")
        if not date_tag:
            print(f"[{seqID}] 날짜 정보가 없습니다.")
            # 실패한 날짜 정보 저장
            cur.execute('''
                INSERT INTO failed_dates (seqID, original_date, error_reason)
                VALUES (%s, %s, %s)
                ON CONFLICT (seqID) DO UPDATE SET
                    original_date = EXCLUDED.original_date,
                    error_reason = EXCLUDED.error_reason
            ''', (seqID, None, "날짜 정보가 없습니다"))
            conn.commit()
            continue

        broadcast_date_str = date_tag.get_text(strip=True)
        iso_date = convert_korean_date_to_iso(broadcast_date_str)
        
        if not iso_date:
            print(f"[{seqID}] 날짜 형식 변환에 실패했습니다: {broadcast_date_str}")
            # 실패한 날짜 정보 저장
            cur.execute('''
                INSERT INTO failed_dates (seqID, original_date, error_reason)
                VALUES (%s, %s, %s)
                ON CONFLICT (seqID) DO UPDATE SET
                    original_date = EXCLUDED.original_date,
                    error_reason = EXCLUDED.error_reason
            ''', (seqID, broadcast_date_str, "날짜 형식 변환 실패"))
            conn.commit()
            continue

        # 먼저 해당 날짜의 기존 데이터 삭제
        cur.execute('DELETE FROM music_data WHERE broadcast_date = %s', (iso_date,))
        
        # 곡 리스트 추출
        rows = soup.select("table.list-type tbody tr")
        inserted_count = 0
        
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 3:
                continue

            number = int(cols[0].get_text(strip=True))
            title = cols[1].select_one(".title").get_text(strip=True) if cols[1].select_one(".title") else ""
            artist = cols[2].select_one(".singer").get_text(strip=True) if cols[2].select_one(".singer") else ""
            description = cols[3].get_text(strip=True) if len(cols) > 3 else ""

            # music_data 테이블에 데이터 삽입
            cur.execute('''
            INSERT INTO music_data (seqID, broadcast_date, number, title, artist, description)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''', (seqID, iso_date, number, title, artist, description))
            inserted_count += 1

        # failed_dates 테이블에서 해당 seqID 삭제
        cur.execute('DELETE FROM failed_dates WHERE seqID = %s', (seqID,))

        # last_successful_seq 테이블에 seqID 추가
        cur.execute('''
            INSERT INTO last_successful_seq (seqID)
            VALUES (%s)
        ''', (seqID,))

        conn.commit()
        
        print(f"[{seqID}] {iso_date} - {inserted_count}곡 저장 완료")
        sleep(0.3)  # 서버 과부하 방지

except Exception as e:
    print(f"오류 발생: {str(e)}")
finally:
    # 실패한 날짜 통계 출력
    cur.execute("SELECT COUNT(*) FROM failed_dates")
    failed_count = cur.fetchone()[0]
    print(f"\n총 {failed_count}개의 날짜 변환 실패 기록이 있습니다.")
    
    # 실패한 날짜 목록 출력
    cur.execute("SELECT seqID, original_date, error_reason FROM failed_dates ORDER BY seqID")
    failed_records = cur.fetchall()
    if failed_records:
        print("\n실패한 날짜 목록:")
        for record in failed_records:
            print(f"seqID: {record[0]}, 원본 날짜: {record[1]}, 실패 이유: {record[2]}")
    
    conn.close()
    print("데이터베이스 연결이 닫혔습니다.")