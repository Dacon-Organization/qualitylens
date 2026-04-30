# Feature Engineering

## 목표
591개 센서 → **50~80개** 최종 피처로 압축
(모델 성능 유지 + 과적합 방지 + SHAP 해석 가능성 확보)

## 처리 순서
```
전처리된 DataFrame
  → 1. 분산 기반 필터링
  → 2. 상관 기반 중복 제거
  → 3. 도메인 파생 피처 생성
  → 4. 최종 피처 선택 (모델 기반)
  → Output: 50~80개 피처 DataFrame
```

---

## 1. 분산 기반 필터링

```python
from sklearn.feature_selection import VarianceThreshold

# 분산 임계값: 전체 분산의 하위 10% 제거
variances = X_train.var()
threshold = variances.quantile(0.10)

selector = VarianceThreshold(threshold=threshold)
selector.fit(X_train)
X_train = selector.transform(X_train)
X_test  = selector.transform(X_test)
```

---

## 2. 상관 기반 중복 제거

```python
CORR_THRESHOLD = 0.95  # 0.95 이상이면 중복으로 간주

corr_matrix = pd.DataFrame(X_train).corr().abs()
upper_tri = corr_matrix.where(
    np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
)

# 상관관계 높은 쪽 컬럼 제거 (더 높은 결측률 가진 쪽)
cols_to_drop = [col for col in upper_tri.columns
                if any(upper_tri[col] > CORR_THRESHOLD)]

X_train = X_train.drop(columns=cols_to_drop)
X_test  = X_test.drop(columns=cols_to_drop)
# 예상: ~400 → ~150개
```

---

## 3. 도메인 파생 피처

SECOM은 익명 센서이므로 **통계적 파생 피처** 위주로 생성.

### 변화율 (Rate of Change)
```python
# 시계열 순서가 유지된 경우에만 유효
for col in key_sensors:
    df[f'{col}_diff'] = df[col].diff().fillna(0)
```

### Rolling Mean (이동 평균)
```python
WINDOW = 5  # 직전 5개 샘플 기준

for col in key_sensors:
    df[f'{col}_roll_mean'] = df[col].rolling(window=WINDOW, min_periods=1).mean()
    df[f'{col}_roll_std']  = df[col].rolling(window=WINDOW, min_periods=1).std().fillna(0)
```

### 센서 비율 (Sensor Ratios)
```python
# 물리적으로 의미 있는 쌍 (Kaggle 데이터셋 적용)
df['temp_pressure_ratio']   = df['temperature'] / (df['pressure'] + 1e-6)
df['vibration_rpm_ratio']   = df['vibration']   / (df['rpm'] + 1e-6)
df['flow_pressure_ratio']   = df['flow_rate']   / (df['pressure'] + 1e-6)
```

### 센서 그룹 통계 (SECOM 적용)
```python
# 공정 그룹별 (sensor-profiling.md의 process_group 기반)
for group_id in [0, 1, 2, 3]:
    group_cols = profile[profile['process_group'] == group_id].index.tolist()
    df[f'group_{group_id}_mean'] = df[group_cols].mean(axis=1)
    df[f'group_{group_id}_std']  = df[group_cols].std(axis=1)
```

---

## 4. 최종 피처 선택 (모델 기반)

### XGBoost Feature Importance
```python
import xgboost as xgb

# 빠른 초기 중요도 계산 (전체 피처 대상)
model_tmp = xgb.XGBClassifier(n_estimators=100, random_state=42)
model_tmp.fit(X_train, y_train)

importances = pd.Series(model_tmp.feature_importances_, index=feature_names)
top_features = importances.nlargest(70).index  # 상위 70개 선택

X_train_final = X_train[top_features]
X_test_final  = X_test[top_features]
```

---

## 피처 수 목표 요약
| 단계 | 피처 수 |
|------|---------|
| 원본 SECOM | 591 |
| 고결측 제거 후 | ~400 |
| 분산 필터 후 | ~250 |
| 상관 제거 후 | ~150 |
| 파생 피처 추가 | ~170 |
| 최종 선택 | **50~80** |

---

## 주의사항
- rolling/diff 파생 피처는 train/test 모두에 동일 방식 적용
- 파생 피처 생성은 Imputation **전**에 수행하지 말 것 (NaN 전파 위험)
- 최종 피처 목록은 `selected_features.json`으로 저장 → 추론 시 재사용
