# MBC 라디오 음악 크롤러

이 프로젝트는 MBC 라디오 프로그램의 음악 재생 목록을 크롤링하여 PostgreSQL 데이터베이스에 저장하는 애플리케이션입니다.

## 프로젝트 개요

- MBC 라디오 미니웹의 음악 재생 목록 데이터를 자동으로 수집
- 날짜, 제목, 아티스트, 설명 등의 정보를 추출하여 구조화된 형태로 저장
- 진행 상황을 추적하고 실패한 데이터 수집 시도를 기록

## 기술 스택

- **Python 3.x**
- **BeautifulSoup4**: HTML 파싱
- **Requests**: HTTP 요청 처리
- **Psycopg2**: PostgreSQL 데이터베이스 연결
- **python-dotenv**: 환경 변수 관리

## 설치 방법

1. 저장소를 클론합니다:
```bash
git clone https://github.com/dongjunson/my-radio-crawler.git
cd my-radio-crawler
```

2. 필요한 패키지를 설치합니다:
```bash
pip install -r requirements.txt
```

3. 환경 설정:
   - 데이터베이스 연결 정보를 설정하거나 `main.py` 파일 내 설정 정보를 직접 수정합니다.
   - 필요에 따라 `.env` 파일을 생성하여 환경 변수를 관리할 수 있습니다.

## 사용 방법

1. 프로그램 실행:
```bash
python main.py
```

2. 크롤링 과정:
   - 프로그램은 MBC 라디오 미니웹에서 seqID를 기준으로 순차적으로 데이터를 수집합니다.
   - 이전에 중단된 지점부터 크롤링을 계속 진행합니다.
   - 수집한 데이터는 PostgreSQL 데이터베이스에 저장됩니다.

## 데이터베이스 구조

### 주요 테이블

1. **music_data**: 수집된 음악 정보 저장
   - seqID: 웹페이지 시퀀스 ID
   - broadcast_date: 방송 날짜
   - number: 곡 번호
   - title: 곡 제목
   - artist: 아티스트
   - description: 곡 설명

2. **last_successful_seq**: 마지막으로 성공적으로 처리된 seqID 기록
   - seqID: 성공적으로 처리된 웹페이지 시퀀스 ID
   - updated_at: 업데이트 시간

3. **failed_dates**: 처리에 실패한 날짜 정보 기록
   - seqID: 실패한 웹페이지 시퀀스 ID
   - original_date: 원본 날짜 텍스트
   - error_reason: 실패 이유
   - created_at: 기록 생성 시간

## 주요 기능

- 한국어 날짜 형식을 ISO 표준 날짜 형식으로 변환
- 크롤링 진행 상황 추적 및 중단 시 이어서 진행
- 오류 발생 시 해당 정보를 기록하여 추후 분석 가능
- 서버 부하 방지를 위한 요청 간 지연 시간 설정 