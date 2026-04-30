# train-pipeline — XGBoost 학습 파이프라인

## 클래스 불균형 처리

```python
# scale_pos_weight: FAIL이 소수 클래스 (label=1)
n_neg = (y_train == 0).sum()   # PASS 수
n_pos = (y_train == 1).sum()   # FAIL 수
scale_pos_weight = n_neg / n_pos   # ≈ 14.2 (6.6% fail rate 기준)
```

## XGBoost 기본 하이퍼파라미터

```python
params = {
    "objective": "binary:logistic",
    "eval_metric": "logloss",          # early stopping용 (MCC는 직접 최적화 불가)
    "scale_pos_weight": scale_pos_weight,
    "n_estimators": 1000,              # early stopping으로 실제 수 결정
    "max_depth": 6,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.3,           # 591 features → 약 177개 샘플링
    "min_child_weight": 5,             # 노이즈 과적합 방지
    "gamma": 0.1,
    "reg_alpha": 0.1,                  # L1
    "reg_lambda": 1.0,                 # L2
    "random_state": 42,
    "tree_method": "hist",             # 대용량 데이터 속도 최적화
    "device": "cuda",                  # GPU 사용 가능 시 (없으면 "cpu")
}
```

## Stratified K-Fold CV (k=5)

```python
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBClassifier
import joblib

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
fold_models = []
fold_metrics = []

for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
    X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
    y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]

    model = XGBClassifier(**params, early_stopping_rounds=50)
    model.fit(
        X_tr, y_tr,
        eval_set=[(X_val, y_val)],
        verbose=100
    )

    # Threshold 최적화 후 MCC 계산 (evaluation.md 참조)
    y_prob = model.predict_proba(X_val)[:, 1]
    best_thresh, mcc = find_best_threshold_mcc(y_val, y_prob)

    fold_models.append(model)
    fold_metrics.append({
        "fold": fold + 1,
        "best_iteration": model.best_iteration,
        "val_mcc": mcc,
        "best_threshold": best_thresh,
    })
    print(f"Fold {fold+1} | MCC: {mcc:.4f} | Threshold: {best_thresh:.3f} | Iter: {model.best_iteration}")
```

## 최종 모델 선택

```python
# 방법 1: 전체 데이터로 재학습 (best_iteration 평균 사용)
avg_best_iter = int(np.mean([m["best_iteration"] for m in fold_metrics]))
final_model = XGBClassifier(**{**params, "n_estimators": avg_best_iter})
final_model.fit(X, y)

# 방법 2: 최고 fold 모델 사용 (빠른 실험)
best_fold_idx = np.argmax([m["val_mcc"] for m in fold_metrics])
final_model = fold_models[best_fold_idx]
```

## 학습 로깅

```python
# fold_metrics를 DataFrame으로 저장
import pandas as pd
metrics_df = pd.DataFrame(fold_metrics)
metrics_df.to_csv("outputs/cv_results.csv", index=False)
print(f"\nMean CV MCC: {metrics_df['val_mcc'].mean():.4f} ± {metrics_df['val_mcc'].std():.4f}")

# Feature importance 저장 (top 30)
feat_imp = pd.Series(
    final_model.feature_importances_,
    index=X.columns
).sort_values(ascending=False).head(30)
feat_imp.to_csv("outputs/feature_importance.csv")
```

## 주의사항

- `colsample_bytree=0.3`: 591개 피처에서 과적합 방지 필수
- Early stopping은 `logloss` 기준 → 최종 평가는 MCC로 별도 계산
- GPU 없는 환경: `device="cpu"`, `tree_method="hist"` 유지
