# evaluation — 성능 평가 지표

## Primary Metric: MCC (Matthews Correlation Coefficient)

### 공식

```
MCC = (TP × TN − FP × FN) / sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN))
```

### 해석

| MCC 값 | 의미 |
|--------|------|
| +1.0 | 완벽한 예측 |
| 0.0 | 랜덤 예측과 동일 |
| -1.0 | 완전히 반대 예측 |
| > 0.5 | 실용적으로 유효한 모델 |
| > 0.7 | 목표 기준선 (반도체 품질관리) |

### 불균형 데이터에 MCC를 쓰는 이유

- Accuracy: PASS만 예측해도 93.4% → 무의미
- F1-Score: TN(정상 판정)을 무시 → 과신 위험
- MCC: TP/TN/FP/FN 모두 반영 → 6.6% 불균형에서도 신뢰 가능

```python
from sklearn.metrics import matthews_corrcoef
mcc = matthews_corrcoef(y_true, y_pred)
```

## Threshold 최적화: Youden's J Statistic

```python
from sklearn.metrics import roc_curve

def find_best_threshold_mcc(y_true, y_prob):
    """MCC를 직접 최대화하는 threshold 탐색"""
    thresholds = np.linspace(0.1, 0.9, 81)
    best_mcc, best_thresh = -1, 0.5
    for t in thresholds:
        y_pred = (y_prob >= t).astype(int)
        mcc = matthews_corrcoef(y_true, y_pred)
        if mcc > best_mcc:
            best_mcc, best_thresh = mcc, t
    return best_thresh, best_mcc

# Youden's J (보조 참고용): sensitivity + specificity - 1
fpr, tpr, thresholds = roc_curve(y_true, y_prob)
youden_j = tpr - fpr
best_thresh_youden = thresholds[np.argmax(youden_j)]
```

> 규칙: MCC 최적화 threshold를 primary로 사용. Youden's J는 검증용.

## Secondary Metrics

```python
from sklearn.metrics import (
    precision_recall_curve, average_precision_score,
    f1_score, roc_auc_score, classification_report
)

# Precision-Recall AUC (클래스 불균형 시 ROC-AUC보다 신뢰도 높음)
pr_auc = average_precision_score(y_true, y_prob)

# F1-Score (threshold 적용 후)
f1 = f1_score(y_true, y_pred)

# Per-class report
print(classification_report(y_true, y_pred, target_names=["PASS", "FAIL"]))
```

## Confusion Matrix 시각화 규칙

```python
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

def plot_confusion_matrix(y_true, y_pred, threshold):
    cm = confusion_matrix(y_true, y_pred)
    labels = [["TN\n(정상→PASS)", "FP\n(정상→FAIL 오경보)"],
              ["FN\n(불량→PASS 누락)", "TP\n(불량→FAIL 감지)"]]
    # FN(누락)을 가장 중요한 셀로 강조 — 빨간색 하이라이트
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
    ax.set_title(f"Confusion Matrix (threshold={threshold:.3f})")
    ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
    return fig
```

- FN(불량 누락) > FP(오경보): 반도체 불량 누락이 더 치명적 → threshold 낮춤 고려
- 시각화 저장: `outputs/confusion_matrix_fold{n}.png`

## 평가 요약 출력 형식

```
=== Fold 3 Evaluation ===
MCC        : 0.7234
PR-AUC     : 0.8102
F1-Score   : 0.7456
Threshold  : 0.380
TP/FP/TN/FN: 48 / 12 / 890 / 8
```
