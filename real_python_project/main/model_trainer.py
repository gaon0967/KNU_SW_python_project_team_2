import pandas as pd
import joblib
from xgboost import XGBRegressor
import os

# BASE_DIR 설정 (현재 파일 기준으로 상위 경로)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

csv_path = os.path.join(BASE_DIR, 'final_merged_with_coords.csv')

# 데이터 불러오기
df = pd.read_csv('C:/Users/yues7/data_B_project/real_python_project/final_merged_with_coords.csv')


# 특징(X), 타깃(y) 정의 (학습 데이터 정의)
X = df[['총인구수', '사망자수', '부상자수', '신호등횡단보도수']]
y = df['발생건수']

# 모델 생성 및 학습
model = XGBRegressor(n_estimators=100, max_depth=4, random_state=42)
model.fit(X, y)

# 모델 저장 경로 설정
model_path = os.path.join(BASE_DIR, 'xgb_model.pkl')
joblib.dump(model, model_path)

print("✅ 모델 학습 및 저장 완료!")
