# Class Balance

## 문제 현황
- UCI SECOM 불량률: **6.6%** (104 Fail / 1,567 total)
- 극단적 불균형 → 모델이 정상으로만 예측해도 93.4% 정확도 달성 가능
- **Recall (재현율)** 이 핵심 지표 — 불량을 놓치는 것이 더 위험

---

## 전략 선택 기준

| 조건 | 권장 전략 |
|------|-----------|
| 빠른 베이스라인 필요 | `class_weight` in XGBoost |
| 데이터 수 충분 (>500 minority) | SMOTE |
| 데이터 수 부족 (<100 minority) | SMOTE + Borderline-SMOTE 병행 |
| 불균형 비율 < 5% | SMOTE 우선 고려 |
| 불균형 비율 5~20% | class_weight 먼저 시도 |

→ SECOM의 경우 (104 Fail): **SMOTE + class_weight 병행 실험** 권장

---

## 1. SMOTE

```python
from imblearn.over_sampling import SMOTE

smote = SMOTE(
    k_neighbors=5,            # 이웃 수
    sampling_strategy='auto', # minority class를 majority 수준으로 오버샘플링
    random_state=42,
)

# 반드시 train에만 적용
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

# 적용 금지: X_test, X_val
```

### 결과 확인
```python
print(f"Before SMOTE: {Counter(y_train)}")
print(f"After  SMOTE: {Counter(y_train_resampled)}")
# Before: {0: 1360, 1: 100}  (예시)
# After:  {0: 1360, 1: 1360}
```

---

## 2. class_weight (XGBoost)

```python
import xgboost as xgb

# scale_pos_weight = negative_count / positive_count
neg_count = (y_train == 0).sum()
pos_count = (y_train == 1).sum()
scale_pos_weight = neg_count / pos_count  # SECOM: ~13.0

model = xgb.XGBClassifier(
    scale_pos_weight=scale_pos_weight,
    random_state=42,
    # ... 나머지 하이퍼파라미터
)
```

---

## 3. SMOTE 변형 (고급)

```python
# Borderline-SMOTE: 경계선 근처 샘플만 오버샘플링 → 노이즈 감소
from imblearn.over_sampling import BorderlineSMOTE
bsmote = BorderlineSMOTE(kind='borderline-1', random_state=42)

# SMOTE + Tomek Links: 오버샘플링 후 경계 노이즈 제거
from imblearn.combine import SMOTETomek
smotetomek = SMOTETomek(random_state=42)
```

---

## 4. 평가 지표 설정

클래스 불균형 상황에서 Accuracy는 무의미 → 아래 지표 우선:

```python
from sklearn.metrics import classification_report, roc_auc_score

print(classification_report(y_test, y_pred))
# 주요: Recall (불량 탐지율), F1-score, AUC-ROC

auc = roc_auc_score(y_test, y_pred_proba)
```

| 지표 | 목표값 | 의미 |
|------|--------|------|
| Recall (Fail) | ≥ 0.80 | 불량 80% 이상 탐지 |
| Precision (Fail) | ≥ 0.60 | 경보 정확도 |
| AUC-ROC | ≥ 0.85 | 전반적 분류 성능 |

---

## 체크리스트
- [ ] SMOTE는 train split 이후에만 적용
- [ ] test/val 세트에 SMOTE 절대 미적용
- [ ] class_weight vs SMOTE 성능 비교 실험 수행
- [ ] Recall 우선 최적화 (불량 미탐지 cost > 과경보 cost)
