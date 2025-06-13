# main/views.py

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import sqlite3
import os
from django.views.decorators.csrf import csrf_exempt
import json
from .models import DailyUpdate
from django.db.models import Q 
from .forms import PostForm
from .models import Post
from .model_utils import load_model_and_predict
import pandas as pd



def rehome(request):
    return render(request, 'main/rehome.html')

def dashboard_4(request):
    return render(request, 'main/dashboard_4.html')

def dashboard_3(request):
    return render(request, 'main/dashboard_3.html')

def dashboard_2(request):
    return render(request, 'main/dashboard_2.html')

def dashboard_1(request):
    return render(request, 'main/dashboard_1.html')

def how_to_use(request):
    return HttpResponse("이든길 사용방법 페이지는 준비 중입니다.")




def emergency_contacts_view(request):
    # settings.py에 정의된 BASE_DIR를 사용하여 DB 파일의 절대 경로를 만듭니다.
    db_path = os.path.join(settings.BASE_DIR, 'emergency_agencies.db')
    
    agencies_by_province = {}
    conn = None # conn 변수 초기화
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # 'agencies' 테이블에서 데이터 조회
        # (이전 스크래핑 코드에서 컬럼명을 영어로 변경했으므로, 영어로 조회)
        cur.execute("SELECT * FROM agencies ORDER BY province, agency_name")
        
        rows = cur.fetchall()

        # DB에서 가져온 데이터를 광역별로 그룹핑
        for row in rows:
            agency = dict(row)
            province = agency.get('province')
            agency_name = agency.get('agency_name')

            if not province:
                continue

            # 새로운 광역 그룹 생성
            if province not in agencies_by_province:
                agencies_by_province[province] = {
                    'province_data': None,
                    'districts': []
                }
            
            # 현재 항목이 광역 자체 정보일 경우
            if province == agency_name:
                agencies_by_province[province]['province_data'] = agency
            # 상세 기초(시/군/구) 정보일 경우
            else:
                agencies_by_province[province]['districts'].append(agency)

    except sqlite3.OperationalError:
        print(f"오류: 데이터베이스 파일('{db_path}')을 찾을 수 없거나 'agencies' 테이블이 없습니다.")
        print("스크래핑 스크립트를 먼저 실행하여 DB 파일을 생성했는지 확인해주세요.")
        agencies_by_province = {} # 오류 발생 시 빈 데이터를 전달
    except Exception as e:
        print(f"데이터베이스 조회 중 오류 발생: {e}")
        agencies_by_province = {}
    finally:
        if conn:
            conn.close()

    context = {
        'agencies_by_province': agencies_by_province
    }
    return render(request, 'main/emergency_contacts.html', context)


@csrf_exempt
def receive_daily_update(request):
    # POST 요청인지 먼저 확인
    if request.method == 'POST':

        # --- 디버깅을 위한 print문 추가 ---
        print("="*30)
        print("DEBUG: 헤더 전체 내용:", request.headers) # 헤더 전체를 출력해서 이름 오타 확인

        received_key = request.headers.get("X-API-KEY")
        print("DEBUG: Make.com에서 받은 키 값:", received_key)

        correct_key = settings.MAKE_API_KEY
        print("DEBUG: settings.py에 설정된 정답 키:", correct_key)

        # 두 값이 같은지 비교
        if received_key == correct_key:
            print("DEBUG: 두 키 값이 일치합니다!")
        else:
            print("DEBUG: !!! 두 키 값이 일치하지 않습니다 !!!")
        print("="*30)
        # --- 디버깅 끝 ---

        # 기존의 키 비교 로직
        if not received_key or received_key != correct_key:
            return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)

        # 키가 일치하면 아래 성공 로직 실행
        try:
            data = json.loads(request.body)
            title = data.get('title')
            content = data.get('content')
            source = data.get('source', 'Unknown')

            if not title or not content:
                return JsonResponse({'status': 'error', 'message': 'Missing title or content'}, status=400)

            DailyUpdate.objects.create(
                title=title,
                content=content,
                source=source
            )
            return JsonResponse({'status': 'success', 'message': 'Data received successfully'}, status=200)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # POST가 아닌 다른 메소드 요청일 경우
    return JsonResponse({'status': 'error', 'message': f'Method {request.method} not allowed.'}, status=405)


def daily_status_page(request):
    # 데이터베이스에 저장된 모든 DailyUpdate 객체를 가져옵니다.
    # 최신순으로 정렬하기 위해 order_by('-received_at')를 사용합니다.
    all_updates = DailyUpdate.objects.all().order_by('-received_at')
    
    # 'updates'라는 키(이름표)로 템플릿에 데이터를 전달합니다.
    context = {
        'updates': all_updates
    }
    
    # 'main/daily_status.html' 템플릿을 렌더링하면서 context 데이터를 함께 보냅니다.
    return render(request, 'main/daily_status.html', context)

def community_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('community')          # 저장 후 자기 자신으로 리다이렉트
    else:
        form = PostForm()

    posts = Post.objects.order_by('-created_at')      # 기존 글 목록

    return render(request,
                  'main/community.html',
                  {'form': form, 'posts': posts})

def quiz_start(request):
    return render(request, 'main/quiz_start.html')

def safety_check_view(request):
    df = pd.read_csv('final_merged_with_coords.csv')
    districts = df['자치구'].unique()

    selected = request.GET.get('district')
    result_shown = False
    rank, reason = None, ""

    if selected:
        rank, reason = load_model_and_predict(selected)
        result_shown = True

    return render(request, 'main/safety_check.html', {
        'districts': districts,
        'selected': selected,
        'rank': rank,
        'reason': reason,
        'result_shown': result_shown
    })
    
    