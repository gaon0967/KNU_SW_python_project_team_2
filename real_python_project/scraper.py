# real_python_project/scraper.py
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, date
import re
import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from main.models import DailyUpdate

def get_articles_from_page(page_url):
    """
    주어진 URL의 게시판 페이지에서 게시글 목록을 파싱하여 반환합니다.
    """
    articles = []
    print(f"\n--- 페이지 크롤링 시작: {page_url} ---")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7', 
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        response = requests.get(page_url, headers=headers, timeout=20) # 타임아웃 20초로 늘림
        response.raise_for_status() 

        soup = BeautifulSoup(response.text, 'html.parser')

        rows = soup.select('table.table_style1.mobile tbody tr')

        
        print(f"DEBUG: 'table.table_style1.mobile tbody tr' 셀렉터로 찾은 행의 수: {len(rows)}")

        if not rows:
            print("DEBUG: 지정된 셀렉터로 게시글 행을 찾을 수 없습니다. 셀렉터 오류일 가능성이 높습니다.")
            main_table = soup.select_one('table.table_style1.mobile')
            if main_table:
                print(f"DEBUG: 테이블 HTML 일부: {main_table.prettify()[:500]}...")
            else:
                print("DEBUG: 'table.table_style1.mobile' 테이블 자체를 찾을 수 없습니다.")

        for row in rows:
            tds = row.find_all('td')
            
   
            if len(tds) != 6:
                print(f"  - 경고: 필터링된 행 (td 개수가 6개가 아님: {len(tds)}). HTML: {row.get_text(strip=True)[:50]}")
                continue
            
            # 첫 번째 td(번호)가 숫자인지 확인 (게시글 번호)
            try:
                article_num_str = tds[0].get_text(strip=True)
                int(article_num_str) 
            except ValueError:
                print(f"  - 경고: 필터링된 행 (번호 '{article_num_str}'가 숫자 아님). HTML: {row.get_text(strip=True)[:50]}")
                continue

            try:
                # 제목: 두 번째 td (index 1) 안의 div.wrap 안의 <a> 태그
                title_tag = tds[1].select_one('div.wrap > a') 
                if not title_tag:
                    print(f"  - 경고: 제목 태그(div.wrap > a)를 찾을 수 없음. 행 스킵. HTML: {row.get_text(strip=True)[:50]}")
                    continue

                title = title_tag.get_text(strip=True)
                detail_url_path = title_tag['href']
                base_url = "https://www.mois.go.kr"
                detail_url = f"{base_url}{detail_url_path}"


                author = tds[3].get_text(strip=True)

     
                reg_date_str = tds[4].get_text(strip=True)
                
        
                try:
                    received_at = datetime.combine(datetime.strptime(reg_date_str.rstrip('.'), '%Y.%m.%d').date(), datetime.min.time())
            
                except ValueError:
                    print(f"  - 경고: 날짜 형식 오류 '{reg_date_str}'. 게시글 스킵: {title}")
                    continue

                # 상세 내용 가져오기
                content = get_article_content(detail_url)
                if "오류로 인해 내용을 가져올 수 없음" in content: # 오류 메시지 포함 시 스킵
                    print(f"  - 경고: 상세 내용 가져오기 실패. 게시글 스킵: {title}")
                    continue

                articles.append({
                    'title': title,
                    'content': content,
                    'source': f"행정안전부 보도자료 ({author})",
                    'received_at': received_at,
                    'original_url': detail_url
                })
                # print(f"  - 게시글 추가: {title}") # 성공적으로 추가될 때 출력
            except Exception as e:
                print(f"  - 경고: 개별 게시글 파싱 중 예상치 못한 오류 발생: {e} - 행 HTML: {row.get_text(strip=True)[:100]}...")
                continue

    except requests.exceptions.RequestException as e:
        print(f"  - 오류: 페이지 요청 실패 ({page_url}): {e}. 상태 코드: {response.status_code if 'response' in locals() else 'N/A'}")
    except Exception as e:
        print(f"  - 오류: HTML 파싱 실패 ({page_url}): {e}")
    
    print(f"--- 페이지 크롤링 종료: {page_url} (찾은 게시글 수: {len(articles)}) ---")
    return articles

def get_article_content(article_url):
    """
    주어진 게시글 상세 URL에서 내용을 파싱하여 반환합니다.
    """
    try:
 

        soup = BeautifulSoup(response.text, 'html.parser')

        content_element = soup.select_one('.view_cont') 
     

        if content_element:
            # 스크립트, 스타일 태그 제거 (이 부분은 보통 그대로 둡니다)
            for script_or_style in content_element(['script', 'style']):
                script_or_style.decompose()

            # 이미지 태그 제거
            for img_tag in content_element.find_all('img'):
                img_tag.decompose()

            # 첨부파일 관련 링크나 span 태그 제거
            for file_info_tag in content_element.select('.file_info, .file_list, span.file_ico'):
                 file_info_tag.decompose()

            content = content_element.get_text(separator='\n', strip=True)
            content = re.sub(r'\s+', ' ', content).strip()

            return content[:2000] # 너무 길어지지 않게 제한

        print(f"  - 경고: 상세 페이지 ({article_url})에서 내용 요소를 찾을 수 없습니다.") # 디버깅용
        return "내용 없음" 
    except requests.exceptions.RequestException as e:
        print(f"  - 오류: 상세 페이지 요청 실패 ({article_url}): {e}")
        return "오류로 인해 내용을 가져올 수 없음"
    except Exception as e:
        print(f"  - 오류: 상세 내용 파싱 실패 ({article_url}): {e}")
        return "오류로 인해 내용을 가져올 수 없음"
    

def scrape_and_save_press_releases(start_page=1, max_pages_to_scrape=None, delay=1.5):
    """
    지정된 페이지 범위의 행정안전부 보도자료를 크롤링하여 DailyUpdate 모델에 저장합니다.
    max_pages_to_scrape: 크롤링할 최대 페이지 수 (None이면 가능한 모든 페이지)
    delay: 각 페이지 요청 사이의 지연 시간 (초)
    """
    base_list_url = "https://www.mois.go.kr/frt/bbs/type001/commonSelectBoardList.do?bbsId=BBSMSTR_000000000336&pageIndex="
    all_new_updates_to_create = []
    page_index = start_page
    scraped_page_count = 0

    print("=== 행정안전부 보도자료 크롤링 시작 ===")

    while True:
        current_page_url = f"{base_list_url}{page_index}"
        articles_on_page = get_articles_from_page(current_page_url)
        
        # --- DEBUG: 페이지별 크롤링 결과 확인 ---
        print(f"DEBUG: Page {page_index} - get_articles_from_page 반환: {len(articles_on_page)}개 항목")
        # --- DEBUG End ---

        if not articles_on_page:
            print(f"페이지 {page_index}에서 더 이상 게시글을 찾을 수 없거나 마지막 페이지입니다. 크롤링을 종료합니다.")
            break 

        found_new_data_on_this_page = False
        for article_data in articles_on_page:
           
            if not DailyUpdate.objects.filter(
                title=article_data['title'], 
                received_at=article_data['received_at'] 
            ).exists():
                all_new_updates_to_create.append(DailyUpdate(
                    title=article_data['title'],
                    content=article_data['content'],
                    source=article_data['source'],
                    received_at=article_data['received_at'],
                    original_url=article_data['original_url'] 
                ))
                found_new_data_on_this_page = True
                print(f"  - 새로운 게시글 추가 예정: '{article_data['title']}'")
            else:
                print(f"  - '{article_data['title']}' (날짜: {article_data['received_at'].strftime('%Y.%m.%d %H:%M')}) - 이미 존재하여 스킵.")
        
        # 현재 페이지에서 새로운 데이터를 하나도 찾지 못했다면, 이전에 이미 다 크롤링한 페이지라는 의미
    
        if not found_new_data_on_this_page and page_index > 1:
            print(f"페이지 {page_index}에서 새로운 게시글을 찾지 못하여 크롤링을 종료합니다.")
            break

        scraped_page_count += 1
        if max_pages_to_scrape and scraped_page_count >= max_pages_to_scrape:
            print(f"설정된 최대 페이지({max_pages_to_scrape})에 도달했습니다. 크롤링을 종료합니다.")
            break
        
        page_index += 1
        time.sleep(delay) 

    if all_new_updates_to_create:
        DailyUpdate.objects.bulk_create(all_new_updates_to_create, ignore_conflicts=True)
        print(f"총 {len(all_new_updates_to_create)}개의 새로운 보도자료를 데이터베이스에 추가했습니다.")
    else:
        print("새롭게 추가된 보도자료가 없습니다.")
    
    print("=== 크롤링 완료 ===")

if __name__ == "__main__":
 
    print("\n--- 테스트 크롤링: 최근 5페이지 (조기 종료 비활성화) ---")
    scrape_and_save_press_releases(start_page=1, max_pages_to_scrape=5, delay=2)
    print("\n테스트 크롤링 완료. DB에서 확인하세요.")

