# MBC 라디오 음악 크롤러

MBC 라디오의 음악 방송 데이터를 수집하고 저장하는 크롤러 프로젝트입니다.

## 주요 기능

- MBC 라디오 음악 방송 데이터 자동 수집
- PostgreSQL 데이터베이스에 데이터 저장
- 실패한 날짜 추적 및 재시도 기능
- 웹 인터페이스를 통한 데이터 조회

## 프로젝트 구조

```
.
├── main.py              # 메인 크롤러 스크립트
├── web_server.py        # 웹 서버 구현
├── debug_crawler.py     # 디버깅용 크롤러
├── retry_failed_dates.py # 실패한 날짜 재시도 스크립트
├── view_db.py           # 데이터베이스 조회 도구
├── insert_data.py       # 데이터 삽입 도구
├── check_page.py        # 페이지 확인 도구
├── utils.py             # 유틸리티 함수
├── templates/           # 웹 템플릿 디렉토리
└── requirements.txt     # 프로젝트 의존성
```

## 설치 방법

1. Python 3.8 이상 설치
2. 가상환경 생성 및 활성화:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # 또는
   .venv\Scripts\activate  # Windows
   ```
3. 의존성 설치:
   ```bash
   pip install -r requirements.txt
   ```

## 환경 설정

`.env` 파일을 생성하고 다음 환경 변수를 설정하세요:

```
DB_PASSWORD=your_password
DB_HOST=your_host
DB_PORT=your_port
DB_NAME=your_database
DB_USER=your_username
```

## 사용 방법

### 크롤러 실행
```bash
python main.py
```

### 웹 서버 실행
```bash
python web_server.py
```

### 실패한 날짜 재시도
```bash
python retry_failed_dates.py
```

## 데이터베이스 스키마

### music_data 테이블
- seqID: INTEGER (Primary Key)
- broadcast_date: DATE
- number: INTEGER
- title: TEXT
- artist: TEXT
- description: TEXT

### last_successful_seq 테이블
- id: SERIAL (Primary Key)
- seqID: INTEGER
- updated_at: TIMESTAMP

### failed_dates 테이블
- seqID: INTEGER (Primary Key)
- original_date: TEXT
- error_reason: TEXT
- created_at: TIMESTAMP

## 의존성

- requests==2.31.0
- beautifulsoup4==4.12.2
- sqlalchemy==2.0.23
- pymysql==1.1.0
- psycopg2-binary==2.9.9
- python-dotenv==1.0.0
- fastapi==0.109.2
- uvicorn==0.27.1
- jinja2==3.1.3
- flask==3.0.2

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 