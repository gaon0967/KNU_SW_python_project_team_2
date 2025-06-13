# emergency_contacts_to_sqlite.py

import requests
import pandas as pd
import sqlite3
import os # os 모듈 추가

# --- [수정됨] 저장될 DB 파일의 경로를 지정합니다. ---
# 'real_python_project'는 실제 Django 프로젝트 폴더 이름입니다.
# 이 스크립트가 data_B_project에서 실행된다고 가정합니다.
output_folder = 'real_python_project'
db_filename = os.path.join(output_folder, "emergency_agencies.db")
# ----------------------------------------------------

JSON_API_URL = "https://www.safekorea.go.kr/idsiSFK/neo/ext/json/emrInfoList/emrInfoList.json"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Referer': 'https://www.safekorea.go.kr/'
}

try:
    response = requests.get(JSON_API_URL, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    all_agencies_data = []
    current_sido_name = ""

    for item in data:
        agency_name = item.get('name', '이름없음')
        website_url = item.get('url', '주소없음')
        
        if agency_name.endswith(('광역시', '특별시', '도', '특별자치도')):
            current_sido_name = agency_name
        
        all_agencies_data.append({
            "province": current_sido_name,
            "agency_name": agency_name,
            "website_url": website_url
        })

    if all_agencies_data:
        # 출력 폴더가 없으면 생성
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        df = pd.DataFrame(all_agencies_data)
        conn = sqlite3.connect(db_filename)
        df.to_sql('agencies', conn, if_exists='replace', index=False)
        conn.close()
        print(f"✅ DB 파일이 올바른 경로에 재생성되었습니다: {db_filename}")

except Exception as e:
    print(f"오류 발생: {e}")