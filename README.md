# 웹 크롤링 및 데이터베이스 저장 프로젝트

이 프로젝트는 Python을 사용하여 웹 페이지를 크롤링하고 MySQL 데이터베이스에 저장하는 예제입니다.

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 환경 변수 설정:
`.env` 파일을 생성하고 다음 내용을 추가하세요:
```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/database_name
```

## 사용 방법

1. `main.py` 파일에서 `target_url` 변수를 크롤링하고 싶은 웹사이트 URL로 변경하세요.

2. 스크립트 실행:
```bash
python main.py
```

## 주요 기능

- 웹 페이지 크롤링
- BeautifulSoup을 사용한 HTML 파싱
- MySQL 데이터베이스에 데이터 저장
- 에러 처리 및 로깅

## 데이터베이스 스키마

`scraped_data` 테이블:
- id: 자동 증가 기본 키
- title: 웹 페이지 제목
- content: 웹 페이지 내용
- url: 크롤링된 URL 