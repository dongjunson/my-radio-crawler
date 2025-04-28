import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, jsonify
import re
import psycopg2
from urllib.parse import quote_plus
from utils import convert_korean_date_to_iso
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)

# Supabase 연결 정보
password = quote_plus(os.getenv("DB_PASSWORD"))
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")

# 환경 변수 검증
required_env_vars = ["DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME", "DB_USER"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>크롤링 디버거</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .step { margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .success { background-color: #e6ffe6; }
        .error { background-color: #ffe6e6; }
        .raw-data { background-color: #f5f5f5; padding: 10px; border-radius: 3px; white-space: pre-wrap; }
        button { padding: 10px; margin: 5px; cursor: pointer; }
        .hidden { display: none; }
        select { padding: 8px; margin: 10px 0; font-size: 16px; }
    </style>
</head>
<body>
    <h1>크롤링 디버거</h1>
    
    <div class="step">
        <h3>SeqID 선택</h3>
        <select id="seqSelect" onchange="updateSeqId()">
            {% for seq in seq_list %}
            <option value="{{ seq }}">{{ seq }}</option>
            {% endfor %}
        </select>
        
        <div style="margin-top: 15px;">
            <h4>특정 SeqID 입력</h4>
            <input type="number" id="customSeqId" placeholder="SeqID 직접 입력">
            <button onclick="setCustomSeqId()">설정</button>
        </div>
    </div>
    
    <div class="step" id="step1">
        <h3>1단계: URL 접속 확인</h3>
        <button onclick="checkUrl()">URL 확인하기</button>
        <div id="urlResult" class="hidden"></div>
    </div>

    <div class="step" id="step2">
        <h3>2단계: HTML 내용 확인</h3>
        <button onclick="checkHtml()">HTML 확인하기</button>
        <div id="htmlResult" class="hidden"></div>
    </div>

    <div class="step" id="step3">
        <h3>3단계: 날짜 추출</h3>
        <button onclick="checkDate()">날짜 확인하기</button>
        <div id="dateResult" class="hidden"></div>
    </div>

    <div class="step" id="step4">
        <h3>4단계: 곡 목록 추출</h3>
        <button onclick="checkSongs()">곡 목록 확인하기</button>
        <div id="songsResult" class="hidden"></div>
    </div>

    <div class="step" id="step5">
        <h3>5단계: 데이터베이스 저장</h3>
        <button onclick="saveToDatabase()">데이터베이스에 저장</button>
        <div id="dbResult" class="hidden"></div>
    </div>

    <script>
        let currentSeqId = document.getElementById('seqSelect').value;

        function updateSeqId() {
            currentSeqId = document.getElementById('seqSelect').value;
            resetResults();
        }
        
        function setCustomSeqId() {
            const customId = document.getElementById('customSeqId').value;
            if (customId && !isNaN(customId)) {
                currentSeqId = customId;
                resetResults();
                alert(`SeqID가 ${customId}로 설정되었습니다.`);
            } else {
                alert('유효한 SeqID를 입력해주세요.');
            }
        }
        
        function resetResults() {
            // 결과 초기화
            ['urlResult', 'htmlResult', 'dateResult', 'songsResult', 'dbResult'].forEach(id => {
                document.getElementById(id).classList.add('hidden');
            });
        }

        function showResult(elementId, data, isError = false) {
            const element = document.getElementById(elementId);
            element.className = isError ? 'error' : 'success';
            element.innerHTML = typeof data === 'object' ? JSON.stringify(data, null, 2) : data;
            element.classList.remove('hidden');
        }

        async function checkUrl() {
            const response = await fetch(`/check_url/${currentSeqId}`);
            const data = await response.json();
            showResult('urlResult', data.message, !data.success);
        }

        async function checkHtml() {
            const response = await fetch(`/check_html/${currentSeqId}`);
            const data = await response.json();
            showResult('htmlResult', data.message, !data.success);
        }

        async function checkDate() {
            const response = await fetch(`/check_date/${currentSeqId}`);
            const data = await response.json();
            showResult('dateResult', data.message, !data.success);
        }

        async function checkSongs() {
            const response = await fetch(`/check_songs/${currentSeqId}`);
            const data = await response.json();
            showResult('songsResult', data.message, !data.success);
        }

        async function saveToDatabase() {
            const response = await fetch(`/save_to_db/${currentSeqId}`);
            const data = await response.json();
            showResult('dbResult', data.message, !data.success);
        }
    </script>
</body>
</html>
'''

def get_failed_seqs():
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()
        
        # failed_dates 테이블에서 seqID 가져오기
        cur.execute('SELECT seqID FROM failed_dates ORDER BY seqID')
        seqs = [row[0] for row in cur.fetchall()]
        
        return seqs
    except Exception as e:
        print(f"데이터베이스 에러: {e}")
        return []
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

@app.route('/')
def home():
    seq_list = get_failed_seqs()
    return render_template_string(HTML_TEMPLATE, seq_list=seq_list)

@app.route('/check_url/<int:seq_id>')
def check_url(seq_id):
    url = f"https://miniweb.imbc.com/Music/View?seqID={seq_id}&progCode=RAMFM300"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'message': f'URL 접속 성공!\nURL: {url}\n상태 코드: {response.status_code}'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'URL 접속 실패\nURL: {url}\n상태 코드: {response.status_code}'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'오류 발생: {str(e)}'
        })

@app.route('/check_html/<int:seq_id>')
def check_html(seq_id):
    url = f"https://miniweb.imbc.com/Music/View?seqID={seq_id}&progCode=RAMFM300"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        main_content = soup.select_one('.view-content')
        if main_content:
            html_preview = main_content.prettify()
        else:
            html_preview = soup.prettify()
        return jsonify({
            'success': True,
            'message': f'HTML 내용:\n{html_preview}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'HTML 파싱 오류: {str(e)}'
        })

@app.route('/check_date/<int:seq_id>')
def check_date(seq_id):
    url = f"https://miniweb.imbc.com/Music/View?seqID={seq_id}&progCode=RAMFM300"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        date_tag = soup.select_one(".view-title .title")
        
        if not date_tag:
            return jsonify({
                'success': False,
                'message': '날짜 태그를 찾을 수 없습니다.'
            })
        
        date_text = date_tag.get_text(strip=True)
        iso_date = convert_korean_date_to_iso(date_text)
        
        return jsonify({
            'success': True,
            'message': f'원본 날짜: {date_text}\nISO 형식 변환: {iso_date}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'날짜 추출 오류: {str(e)}'
        })

@app.route('/check_songs/<int:seq_id>')
def check_songs(seq_id):
    url = f"https://miniweb.imbc.com/Music/View?seqID={seq_id}&progCode=RAMFM300"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.select("table.list-type tbody tr")
        
        songs = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 3:
                continue
                
            song = {
                'number': cols[0].get_text(strip=True),
                'title': cols[1].select_one(".title").get_text(strip=True) if cols[1].select_one(".title") else "",
                'artist': cols[2].select_one(".singer").get_text(strip=True) if cols[2].select_one(".singer") else "",
                'description': cols[3].get_text(strip=True) if len(cols) > 3 else ""
            }
            songs.append(song)
        
        return jsonify({
            'success': True,
            'message': f'총 {len(songs)}개의 곡이 발견되었습니다:\n' + '\n'.join([
                f"{song['number']}. {song['title']} - {song['artist']}" for song in songs
            ])
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'곡 목록 추출 오류: {str(e)}'
        })

@app.route('/save_to_db/<int:seq_id>')
def save_to_db(seq_id):
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()

        url = f"https://miniweb.imbc.com/Music/View?seqID={seq_id}&progCode=RAMFM300"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')

        # 날짜 추출
        date_tag = soup.select_one(".view-title .title")
        if not date_tag:
            raise Exception("날짜 정보를 찾을 수 없습니다.")

        broadcast_date_str = date_tag.get_text(strip=True)
        iso_date = convert_korean_date_to_iso(broadcast_date_str)
        if not iso_date:
            raise Exception(f"날짜 형식 변환 실패: {broadcast_date_str}")

        # 먼저 해당 날짜의 기존 데이터 삭제
        cur.execute('DELETE FROM music_data WHERE broadcast_date = %s', (iso_date,))
        
        # 곡 목록 추출 및 저장
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
            ''', (seq_id, iso_date, number, title, artist, description))
            inserted_count += 1

        # failed_dates 테이블에서 해당 seqID 삭제
        cur.execute('DELETE FROM failed_dates WHERE seqID = %s', (seq_id,))

        # last_successful_seq 테이블에 seqID 추가
        cur.execute('''
            INSERT INTO last_successful_seq (seqID)
            VALUES (%s)
        ''', (seq_id,))

        conn.commit()

        return jsonify({
            'success': True,
            'message': f'''처리 완료:
- 해당 날짜({iso_date})의 기존 데이터 삭제
- {inserted_count}개의 곡 데이터 저장
- failed_dates 테이블에서 seqID {seq_id} 삭제
- last_successful_seq 테이블에 seqID {seq_id} 추가'''
        })

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        return jsonify({
            'success': False,
            'message': f'데이터베이스 저장 중 오류 발생: {str(e)}'
        })
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5001) 