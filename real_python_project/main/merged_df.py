import pandas as pd
import glob
import os

print("스크립트 실행 시작.")

# 1. 인구 데이터 불러오기
try:
    people_file_path = 'data/people/등록인구_20250611134139.csv'
    if not os.path.exists(people_file_path):
        print(f"오류: '{people_file_path}' 파일을 찾을 수 없습니다. 경로와 파일명을 확인하세요.")
        exit()

    people_df = pd.read_csv(people_file_path, encoding='utf-8', skiprows=2)
    people_df = people_df[['동별(2)', '소계']]
    people_df.columns = ['자치구', '총인구수']
    people_df = people_df.groupby('자치구', as_index=False).sum()
    print("1. 인구 데이터 로드 및 처리 완료.")
    print(f"people_df head:\n{people_df.head()}\n")
except Exception as e:
    print(f"인구 데이터 처리 중 오류 발생: {e}")
    exit()

# 2. 교통사고 연도별 데이터 병합
accident_files = sorted(glob.glob('data/traffic accident/교통사고+현황(구별)_20*.xlsx'))
if not accident_files:
    print("경고: 교통사고 엑셀 파일을 찾을 수 없습니다. 'data/traffic accident/' 디렉토리를 확인하세요.")
    accident_df = pd.DataFrame(columns=['자치구', '발생건수', '사망자수', '부상자수'])
else:
    accident_df_list = []
    for file in accident_files:
        try:
            year = file[-9:-5]
            temp_df = pd.read_excel(file, skiprows=1)
            # 필요한 컬럼만 선택하기 전에 컬럼이 있는지 확인 (선택 사항)
            expected_cols = ['자치구1', '자치구', '발생건수', '1만대당발생', '사망자수', '10만명당_사망', '부상자수']
            if len(temp_df.columns) < 7:
                 print(f"경고: 파일 '{file}'의 컬럼 수가 예상보다 적습니다. 실제 컬럼: {temp_df.columns.tolist()}")
                 continue

            temp_df = temp_df.iloc[:, :7]
            temp_df.columns = expected_cols
            temp_df['연도'] = int(year)
            accident_df_list.append(temp_df[['자치구', '발생건수', '사망자수', '부상자수', '연도']])
        except Exception as e:
            print(f"교통사고 파일 '{file}' 처리 중 오류 발생: {e}")
            continue

    if accident_df_list:
        accident_df = pd.concat(accident_df_list)
        accident_df = accident_df.groupby('자치구', as_index=False)[['발생건수', '사망자수', '부상자수']].mean()
        print("2. 교통사고 데이터 로드 및 처리 완료.")
        print(f"accident_df head:\n{accident_df.head()}\n")
    else:
        print("오류: 유효한 교통사고 데이터가 처리되지 않았습니다. accident_df가 비어있습니다.")
        accident_df = pd.DataFrame(columns=['자치구', '발생건수', '사망자수', '부상자수'])

# 3. 신호등 및 횡단보도 데이터
try:
    signal_file_path = 'data/Traffic light/서울특별시_자치구별 신호등 및 횡단보도 위치 및 현황.xlsx'
    if not os.path.exists(signal_file_path):
        print(f"오류: '{signal_file_path}' 파일을 찾을 수 없습니다. 경로와 파일명을 확인하세요.")
        exit()

    signal_df = pd.read_excel(
        signal_file_path,
        header=3
    )
    signal_df.columns = signal_df.columns.str.strip()

    if '자치구' in signal_df.columns:
        signal_count = signal_df['자치구'].value_counts().reset_index()
        signal_count.columns = ['자치구', '신호등횡단보도수']
        print("3. 신호등 및 횡단보도 데이터 로드 및 처리 완료.")
        print(f"signal_count head:\n{signal_count.head()}\n")
    else:
        raise KeyError(f"'{signal_file_path}' 파일에 '자치구' 컬럼이 존재하지 않습니다. 실제 컬럼: {signal_df.columns.tolist()}")

except KeyError as ke:
    print(f"신호등 데이터 처리 중 오류 발생: {ke}")
    exit()
except Exception as e:
    print(f"신호등 데이터 처리 중 일반 오류 발생: {e}")
    exit()

# 4. 교통안전지수 데이터는 제외합니다.
print("4. 교통안전지수 데이터는 병합에서 제외합니다.")

# ✅ 병합
print("데이터프레임 병합 시도 중 (교통안전지수 제외)...")
try:
    merged_df = people_df.merge(accident_df, on='자치구', how='inner') \
                         .merge(signal_count, on='자치구', how='inner')
    print("데이터프레임이 성공적으로 병합되었습니다.")
except Exception as e:
    print(f"데이터프레임 병합 중 오류 발생: {e}")
    print("'자치구' 컬럼의 값들이 각 데이터프레임에서 일관적인지 확인해 주세요.")
    print(f"Unique '자치구' in people_df: {people_df['자치구'].unique()}")
    print(f"Unique '자치구' in accident_df: {accident_df['자치구'].unique()}")
    print(f"Unique '자치구' in signal_count: {signal_count['자치구'].unique()}")
    exit()

# ✅ 확인
print("\n--- 최종 병합된 DataFrame 정보 ---")
print(merged_df.info())
print("\n--- 병합된 DataFrame의 고유 '자치구' ---")
print(merged_df['자치구'].unique())
print("\n--- Head of Merged DataFrame ---")
print(merged_df.head())

print("\n스크립트 실행 완료.")


# 병합 완료 후 파일 저장
output_path = "data/final_merged_with_coords.csv"
merged_df.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"\n✅ 병합된 데이터가 '{output_path}' 경로에 저장되었습니다.")

# 💡 여기부터 XGBoost 모델 학습 코드
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import pandas as pd
import numpy as np

# 병합된 데이터 불러오기
df = pd.read_csv('data/final_merged_with_coords.csv')

# 특성과 타깃 정의
X = df[['총인구수', '사망자수', '부상자수', '신호등횡단보도수']]
y = df['발생건수']

# 학습용/검증용 데이터 분할
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 모델 생성 및 학습
model = XGBRegressor(n_estimators=100, max_depth=4, random_state=42)
model.fit(X_train, y_train)

#모델 예측
y_pred = model.predict(X_test)

# RMSE 계산: MSE → 제곱근
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
print(f"\n✅ RMSE (평균 제곱근 오차): {rmse:.2f}")


# 변수 중요도 시각화 (선택)
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'Malgun Gothic'  # ✅ 한글 폰트 설정
matplotlib.rcParams['axes.unicode_minus'] = False

feature_importance = model.feature_importances_
features = X.columns

plt.figure(figsize=(8, 4))
plt.bar(features, feature_importance)
plt.title("📊 변수 중요도 (XGBoost)")
plt.ylabel("중요도")
plt.xlabel("변수")
plt.tight_layout()
plt.show()