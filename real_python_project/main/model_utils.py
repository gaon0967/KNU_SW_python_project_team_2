import pandas as pd
import joblib
import os
from django.conf import settings

def load_model_and_predict(district_name):
    # 모델 경로
    model_path = os.path.join(settings.BASE_DIR, 'xgb_model.pkl')
    print(f"DEBUG (model_utils): 모델 파일 경로: {model_path}")
    if not os.path.exists(model_path):
        return None, "❌ 모델 파일을 찾을 수 없습니다."

    try:
        model = joblib.load(model_path)
    except Exception as e:
        return None, f"❌ 모델 로드 오류: {e}"

    # CSV 경로
    csv_path = os.path.join(settings.BASE_DIR, 'final_merged_with_coords.csv')
    print(f"DEBUG: CSV 파일 경로: {csv_path}")
    if not os.path.exists(csv_path):
        return None, "❌ 데이터 파일을 찾을 수 없습니다."

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return None, f"❌ CSV 로드 오류: {e}"

    # 해당 자치구 데이터 추출
    target_row = df[df['자치구'] == district_name]
    if target_row.empty:
        return None, f"❌ '{district_name}' 데이터를 찾을 수 없습니다."

    features = ['총인구수', '사망자수', '부상자수', '신호등횡단보도수']
    missing_cols = [col for col in features if col not in target_row.columns]
    if missing_cols:
        return None, f"❌ 필요한 컬럼이 없습니다: {missing_cols}"

    X = target_row[features]

    # 예측 (해당 자치구의 교통사고 발생건수를 여기서 예측함함)
    try:
        predicted_value = model.predict(X)[0]
    except Exception as e:
        return None, f"❌ 예측 오류: {e}"

    # 전체 구 예측값 생성
    try:
        all_X = df[features]
        df['예측값'] = model.predict(all_X)
    except Exception as e:
        return None, f"❌ 전체 예측 오류: {e}"

    # 순위 계산
    df_sorted = df.sort_values(by='예측값', ascending=True).reset_index(drop=True)
    rank_series = df_sorted[df_sorted['자치구'] == district_name].index
    if not rank_series.empty:
        rank = rank_series[0] + 1
    else:
        return None, f"❌ 순위를 계산할 수 없습니다."

    # 중요 feature 추출
    try:
        importances = model.feature_importances_
        most_important_feature_index = importances.argmax()
        most_important_feature_name = features[most_important_feature_index]
    except Exception:
        most_important_feature_name = None

    # 이유 생성
    if rank == 1:
        reason = f"{district_name}는 교통 안전도가 매우 높아 가장 안전한 지역 중 하나입니다."
    elif rank <= 5:
        reason = f"{district_name}는 교통 안전도가 높은 편에 속합니다."
    elif rank <= 15:
        reason = f"{district_name}는 평균적인 교통 안전도를 보입니다."
    else:
        if most_important_feature_name:
            feature_val = X[most_important_feature_name].iloc[0]
            reason = (
                f"{district_name}는 교통 안전도를 개선할 필요가 있습니다. "
                f"특히 '{most_important_feature_name}' (수치: {feature_val}) 변수에 주의가 필요합니다."
            )
        else:
            reason = f"{district_name}는 교통 안전도를 개선할 필요가 있습니다."

    return rank, reason
