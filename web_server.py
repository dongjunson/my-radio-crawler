from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from datetime import datetime
import json
import psycopg2
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

app = FastAPI()

# 템플릿 디렉토리 설정
templates = Jinja2Templates(directory="templates")

# 정적 파일 디렉토리 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# 데이터베이스 연결 설정
db_config = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def get_db_connection():
    """데이터베이스 연결을 생성하는 함수"""
    return psycopg2.connect(**db_config)

def get_failed_dates():
    """실패한 날짜 목록을 데이터베이스에서 가져오는 함수"""
    failed_dates = {}
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # failed_dates 테이블에서 실패한 날짜와 에러 메시지를 가져오는 쿼리
        query = """
        SELECT 
            seqID,
            original_date,
            error_reason,
            created_at
        FROM failed_dates
        ORDER BY created_at DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print("\n=== 실패한 날짜 목록 ===")
        for seqID, original_date, error_reason, created_at in results:
            print(f"SeqID: {seqID}")
            print(f"원본 날짜: {original_date}")
            print(f"에러 이유: {error_reason}")
            print(f"생성 시간: {created_at}")
            print("-" * 50)
            
            # 날짜를 키로 사용하고, 필요한 정보를 포함하는 구조로 변경
            date_key = original_date if original_date else f"Unknown Date (SeqID: {seqID})"
            if date_key not in failed_dates:
                failed_dates[date_key] = {
                    'count': 1,
                    'last_error': error_reason
                }
            else:
                failed_dates[date_key]['count'] += 1
                if error_reason:
                    failed_dates[date_key]['last_error'] = error_reason
            
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    return failed_dates

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """메인 페이지"""
    failed_dates = get_failed_dates()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "failed_dates": failed_dates}
    )

@app.get("/failed-dates", response_class=HTMLResponse)
async def read_failed_dates(request: Request):
    """실패한 날짜 목록 페이지"""
    failed_dates = get_failed_dates()
    return templates.TemplateResponse(
        "failed_dates.html",
        {"request": request, "failed_dates": failed_dates}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 