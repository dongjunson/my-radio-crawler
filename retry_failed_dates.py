import requests
from bs4 import BeautifulSoup
import psycopg2
from urllib.parse import quote_plus
from time import sleep
import os
from dotenv import load_dotenv
from utils import convert_korean_date_to_iso

load_dotenv()

# Supabase 연결 정보
password = quote_plus(os.getenv('DB_PASSWORD'))
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
database = os.getenv('DB_NAME')
user = os.getenv('DB_USER')

conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"

def process_failed_dates():
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()

        # failed_dates 테이블에서 모든 seqID 가져오기
        cur.execute('SELECT seqID FROM failed_dates ORDER BY seqID')
        failed_seqs = [row[0] for row in cur.fetchall()]
        
        if not failed_seqs:
            print("처리할 실패한 seqID가 없습니다.")
            return

        print(f"총 {len(failed_seqs)}개의 실패한 seqID를 처리합니다.")
        
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        
        for seq_id in failed_seqs:
            print(f"\n처리 중: seqID {seq_id}")
            url = f"https://miniweb.imbc.com/Music/View?seqID={seq_id}&progCode=RAMFM300"
            
            try:
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    print(f"[{seq_id}] 페이지를 가져오는 데 실패했습니다.")
                    continue

                soup = BeautifulSoup(response.content, 'html.parser')

                # 날짜 추출
                date_tag = soup.select_one(".view-title .title")
                if not date_tag:
                    print(f"[{seq_id}] 날짜 정보가 없습니다.")
                    continue

                broadcast_date_str = date_tag.get_text(strip=True)
                iso_date = convert_korean_date_to_iso(broadcast_date_str)
                
                if not iso_date:
                    print(f"[{seq_id}] 날짜 형식 변환에 실패했습니다: {broadcast_date_str}")
                    continue

                # 곡 리스트 추출
                rows = soup.select("table.list-type tbody tr")
                if not rows:
                    print(f"[{seq_id}] 곡 목록이 없습니다.")
                    continue

                inserted_count = 0
                success = True
                
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) < 3:
                        continue

                    try:
                        number = int(cols[0].get_text(strip=True))
                        title = cols[1].select_one(".title").get_text(strip=True) if cols[1].select_one(".title") else ""
                        artist = cols[2].select_one(".singer").get_text(strip=True) if cols[2].select_one(".singer") else ""
                        description = cols[3].get_text(strip=True) if len(cols) > 3 else ""

                        # music_data 테이블에 데이터 삽입
                        cur.execute('''
                        INSERT INTO music_data (seqID, broadcast_date, number, title, artist, description)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (seqID, number) DO UPDATE SET
                            broadcast_date = EXCLUDED.broadcast_date,
                            title = EXCLUDED.title,
                            artist = EXCLUDED.artist,
                            description = EXCLUDED.description
                        ''', (seq_id, iso_date, number, title, artist, description))
                        inserted_count += 1
                    except Exception as e:
                        print(f"[{seq_id}] 곡 데이터 처리 중 오류 발생: {str(e)}")
                        success = False
                        break

                if success and inserted_count > 0:
                    # 모든 곡 데이터가 성공적으로 저장된 경우에만
                    # failed_dates 테이블에서 해당 seqID 삭제
                    cur.execute('DELETE FROM failed_dates WHERE seqID = %s', (seq_id,))

                    # last_successful_seq 테이블에 seqID 추가
                    cur.execute('''
                        INSERT INTO last_successful_seq (seqID)
                        VALUES (%s)
                    ''', (seq_id,))

                    conn.commit()
                    print(f"[{seq_id}] {iso_date} - {inserted_count}곡 저장 완료")
                else:
                    print(f"[{seq_id}] 데이터 저장 실패")
                    conn.rollback()

                sleep(0.3)  # 서버 과부하 방지

            except Exception as e:
                print(f"[{seq_id}] 처리 중 오류 발생: {str(e)}")
                conn.rollback()
                continue

    except Exception as e:
        print(f"데이터베이스 오류: {str(e)}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    process_failed_dates() 