# Preprocessing

## 처리 순서
```
원본 DataFrame
  → 1. 고결측 센서 제거 (>40%)
  → 2. 상수/저분산 피처 제거
  → 3. KNN Imputation (결측치 대체)
  → 4. StandardScaler (train fit → train/test transform)
  → Output: X_train_scaled, X_test_scaled
```

---

## 1. 고결측 센서 제거

```python
MISSING_THRESHOLD = 0.40  # 40% 초과 시 드롭

missing_rate = X_train.isnull().mean()
cols_to_drop = missing_rate[missing_rate > MISSING_THRESHOLD].index

X_train = X_train.drop(columns=cols_to_drop)
X_test  = X_test.drop(columns=cols_to_drop)
# 기준: train 기준으로 결정, test에 동일 적용
```

---

## 2. 상수 / 근-제로 분산 제거

```python
from sklearn.feature_selection import VarianceThreshold

selector = VarianceThreshold(threshold=0.0)  # 상수 컬럼 제거
selector.fit(X_train)

X_train = selector.transform(X_train)
X_test  = selector.transform(X_test)
```

- 분산이 0인 컬럼: 정보 없음, 무조건 제거
- 근-제로 분산 (threshold 조정): feature-engineering.md 참조

---

## 3. KNN Imputation

```python
from sklearn.impute import KNNImputer

KNN_K = 5  # 이웃 수

imputer = KNNImputer(n_neighbors=KNN_K)
imputer.fit(X_train)  # train만으로 fit

X_train_imputed = imputer.transform(X_train)
X_test_imputed  = imputer.transform(X_test)
```

### 선택 이유
- 센서 간 상관관계를 활용한 추정 → 단순 Median보다 정확
- 단점: 고차원(591)에서 느림 → 결측 센서 제거 후 적용 권장

### 대안 (빠른 실험 시)
```python
from sklearn.impute import SimpleImputer
imputer = SimpleImputer(strategy='median')  # median이 mean보다 이상치에 강함
```

---

## 4. StandardScaler

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
scaler.fit(X_train_imputed)  # train만으로 fit — Data Leakage 방지 핵심

X_train_scaled = scaler.transform(X_train_imputed)
X_test_scaled  = scaler.transform(X_test_imputed)
```

### 주의사항
- `fit`은 반드시 train에만 — test 정보가 scaler에 유입되면 Leakage
- XGBoost는 스케일링 불필요하지만 SHAP 시각화 가독성을 위해 적용
- 강한 비대칭 센서는 먼저 `np.log1p()` 변환 후 스케일링

---

## 5. Pipeline 통합 (권장 구현)

```python
from sklearn.pipeline import Pipeline

preprocessing_pipeline = Pipeline([
    ('imputer', KNNImputer(n_neighbors=5)),
    ('scaler',  StandardScaler()),
])

preprocessing_pipeline.fit(X_train)
X_train_processed = preprocessing_pipeline.transform(X_train)
X_test_processed  = preprocessing_pipeline.transform(X_test)
```

Pipeline 객체는 `joblib.dump()`로 저장 → 실시간 추론 시 재사용.

---

## 체크리스트
- [ ] 결측 처리 기준: train 기반으로 결정, test에 동일 적용
- [ ] scaler.fit(): train에만 호출
- [ ] 전처리 파이프라인 저장 (`preprocessing_pipeline.pkl`)
- [ ] 원본 컬럼 수 → 처리 후 컬럼 수 로그 출력
