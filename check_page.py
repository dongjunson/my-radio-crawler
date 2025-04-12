import requests
from bs4 import BeautifulSoup

def check_page_structure(seq_id):
    # 웹페이지 URL
    url = f"https://miniweb.imbc.com/Music/View?seqID={seq_id}&progCode=RAMFM300"
    
    # 헤더 설정
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    
    # 웹페이지 요청
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        # HTML 파싱
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"\n=== seqID {seq_id} 페이지 구조 ===")
        
        # 페이지 제목 확인
        title = soup.select_one(".view-title .title")
        print(f"제목: {title.get_text(strip=True) if title else '제목 없음'}")
        
        # 테이블 구조 확인
        table = soup.select_one("table.list-type")
        if table:
            print("테이블이 존재합니다.")
            # 테이블 헤더 확인
            headers = table.select("thead th")
            print("테이블 헤더:")
            for header in headers:
                print(f"- {header.get_text(strip=True)}")
            
            # 테이블 내용 확인
            rows = table.select("tbody tr")
            print(f"총 {len(rows)}개의 행이 있습니다.")
            if rows:
                print("첫 번째 행의 내용:")
                cols = rows[0].find_all("td")
                for i, col in enumerate(cols):
                    print(f"열 {i+1}: {col.get_text(strip=True)}")
                
                # CSS 클래스 확인
                print("\nCSS 클래스 구조:")
                for i, col in enumerate(cols):
                    print(f"열 {i+1} 클래스: {col.get('class', ['없음'])}")
        else:
            print("테이블이 존재하지 않습니다.")
    else:
        print(f"페이지를 가져오는데 실패했습니다. 상태 코드: {response.status_code}")

# 두 ID의 페이지 구조 비교
check_page_structure(6941)
