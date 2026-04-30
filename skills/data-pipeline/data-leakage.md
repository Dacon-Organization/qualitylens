# Data Leakage 방지 Pipeline

## Data Leakage란?
학습 데이터에 테스트/미래 정보가 유입되어 실제 환경보다 과도하게 높은 성능이 나오는 현상.
→ 모델이 실제 배포 시 성능 급락의 주요 원인.

---

## 1. Stratified Train/Test Split

```python
from sklearn.model_selection import StratifiedShuffleSplit

# Stratified: 불균형 클래스(6.6% Fail)의 비율을 train/test에 동일하게 유지
splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)

for train_idx, test_idx in splitter.split(X, y):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

# 비율 확인
print(f"Train Fail rate: {y_train.mean():.3f}")
print(f"Test  Fail rate: {y_test.mean():.3f}")
# 두 값이 거의 같아야 함 (~0.066)
```

---

## 2. 전처리 Leakage 방지 규칙

| 작업 | 올바른 방법 | 잘못된 방법 (Leakage) |
|------|------------|----------------------|
| 결측치 대체 | `imputer.fit(X_train)` 후 transform | 전체 데이터로 fit |
| 스케일링 | `scaler.fit(X_train)` 후 transform | 전체 데이터로 fit |
| 분산 필터 | `X_train.var()` 기준으로 선택 | 전체 데이터로 var() |
| 상관 제거 | `X_train.corr()` 기준으로 선택 | 전체 데이터로 corr() |
| SMOTE | Split 이후 train에만 | Split 이전 전체에 적용 |
| Feature Selection | train 기준 importance | test 정보 포함 선택 |

---

## 3. Leakage-Safe Pipeline 구조

```python
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_score

# 전처리 + 모델을 하나의 Pipeline으로 묶음
# → CV 시 fold마다 독립적으로 fit
full_pipeline = Pipeline([
    ('imputer',   KNNImputer(n_neighbors=5)),
    ('scaler',    StandardScaler()),
    ('selector',  VarianceThreshold()),
    ('model',     XGBClassifier(scale_pos_weight=13.0, random_state=42)),
])

# Cross-Validation (각 fold에서 전처리 독립 수행)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(full_pipeline, X_train, y_train,
                          cv=cv, scoring='roc_auc')
print(f"CV AUC: {scores.mean():.4f} ± {scores.std():.4f}")
```

---

## 4. 타임스탬프 Leakage (시계열 주의)

SECOM은 시계열 데이터. 랜덤 분할 시 미래 정보 유입 가능.

```python
# 옵션 1: 시간 순 분할 (권장 — 실제 환경 모사)
cutoff_idx = int(len(df) * 0.8)
X_train = df.iloc[:cutoff_idx]
X_test  = df.iloc[cutoff_idx:]

# 옵션 2: 랜덤 분할 (빠른 실험용, 시계열 무시)
# StratifiedShuffleSplit 사용 (위 코드 참조)
```

→ **대회/데모 목적**: 랜덤 분할 허용  
→ **실제 배포 목적**: 시간 순 분할 필수

---

## 5. Leakage 검증 체크리스트

```python
# 검증 1: train/test 분포 유사성
from scipy.stats import ks_2samp
for col in X_train.columns[:10]:  # 샘플 확인
    stat, p = ks_2samp(X_train[col], X_test[col])
    if p < 0.05:
        print(f"경고: {col} 분포 불일치 (p={p:.4f})")

# 검증 2: test 성능이 train 성능보다 과도하게 높은지 확인
# train AUC ≈ test AUC (±0.05 범위 내) → 정상
# test AUC >> train AUC → Leakage 강력 의심
```

---

## 체크리스트
- [ ] Split은 모든 전처리보다 먼저 수행
- [ ] fit()은 오직 X_train에만 호출
- [ ] SMOTE는 train split 이후에만
- [ ] Pipeline 사용으로 CV Leakage 방지
- [ ] 시계열 특성 고려한 분할 방식 결정
