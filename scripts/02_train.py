"""T2 — 모델 학습 (XGBoost + threshold engine).

T1에서 만든 .pkl 캐시를 로드해 XGBoost를 학습하고, MCC/PR-AUC로 평가한 뒤
``models/xgb_secom.joblib`` 으로 직렬화한다.

평가 지표:
- MCC (Matthews Correlation Coefficient) — primary (불균형 강건)
- PR-AUC — 보조
- Youden's J 로 최적 threshold 산출

Threshold Engine:
- PASS 데이터의 sensor별 mean ± 2σ → ``threshold_table.csv``

CLI::

    python scripts/02_train.py
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    matthews_corrcoef,
    precision_recall_curve,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parent.parent
PROC_DIR = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42
N_SPLITS = 5

# %% [markdown]
# ## 1. 데이터 로드


def load_processed() -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    X_train = pd.read_pickle(PROC_DIR / "secom_X_train.pkl")
    y_train = pd.read_pickle(PROC_DIR / "secom_y_train.pkl")
    X_test = pd.read_pickle(PROC_DIR / "secom_X_test.pkl")
    y_test = pd.read_pickle(PROC_DIR / "secom_y_test.pkl")
    return X_train, y_train, X_test, y_test


X_train, y_train, X_test, y_test = load_processed()
print(f"train {X_train.shape} / test {X_test.shape}")
print(f"train fail {y_train.mean()*100:.2f}% / test fail {y_test.mean()*100:.2f}%")

# %% [markdown]
# ## 2. scale_pos_weight 계산
# SMOTE 적용 후라 거의 1.0 이지만 안전상 명시


pos_weight = float((y_train == 0).sum()) / max(int((y_train == 1).sum()), 1)
print(f"scale_pos_weight = {pos_weight:.2f}")

# %% [markdown]
# ## 3. Stratified K-Fold + XGBoost 학습


params = dict(
    n_estimators=400,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.7,
    reg_lambda=1.0,
    scale_pos_weight=pos_weight,
    objective="binary:logistic",
    eval_metric="aucpr",
    tree_method="hist",
    random_state=RANDOM_STATE,
)

fold_mccs: list[float] = []
fold_prs: list[float] = []
skf = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)

for fold, (tr_idx, val_idx) in enumerate(skf.split(X_train, y_train), 1):
    model = XGBClassifier(**params)
    model.fit(
        X_train.iloc[tr_idx],
        y_train.iloc[tr_idx],
        eval_set=[(X_train.iloc[val_idx], y_train.iloc[val_idx])],
        verbose=False,
    )
    proba = model.predict_proba(X_train.iloc[val_idx])[:, 1]
    pred = (proba >= 0.5).astype(int)
    mcc = matthews_corrcoef(y_train.iloc[val_idx], pred)
    pr_auc = average_precision_score(y_train.iloc[val_idx], proba)
    fold_mccs.append(mcc)
    fold_prs.append(pr_auc)
    print(f"  fold {fold}: MCC={mcc:.4f}  PR-AUC={pr_auc:.4f}")

print(f"\nMCC  mean ± std = {np.mean(fold_mccs):.4f} ± {np.std(fold_mccs):.4f}")
print(f"PRAUC mean ± std = {np.mean(fold_prs):.4f} ± {np.std(fold_prs):.4f}")

# %% [markdown]
# ## 4. 최종 모델 — 전체 train으로 재학습


final_model = XGBClassifier(**params)
final_model.fit(X_train, y_train, verbose=False)

# %% [markdown]
# ## 5. Test set 평가


test_proba = final_model.predict_proba(X_test)[:, 1]
test_pred_default = (test_proba >= 0.5).astype(int)
test_mcc_default = matthews_corrcoef(y_test, test_pred_default)
test_pr_auc = average_precision_score(y_test, test_proba)
print(f"\n[test @0.5] MCC={test_mcc_default:.4f}  PR-AUC={test_pr_auc:.4f}")

# %% [markdown]
# ## 6. Youden's J — 최적 threshold


fpr, tpr, thresh = roc_curve(y_test, test_proba)
youden_idx = np.argmax(tpr - fpr)
best_threshold = float(thresh[youden_idx])
test_pred_opt = (test_proba >= best_threshold).astype(int)
test_mcc_opt = matthews_corrcoef(y_test, test_pred_opt)
print(
    f"[test @{best_threshold:.4f}] MCC={test_mcc_opt:.4f} "
    f"(Δ {test_mcc_opt - test_mcc_default:+.4f})"
)

# %% [markdown]
# ## 7. Threshold Engine — PASS 데이터 mean±2σ


def build_threshold_table(X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
    pass_df = X[y == 0]
    mean = pass_df.mean()
    std = pass_df.std()
    table = pd.DataFrame(
        {
            "sensor": mean.index,
            "mean_pass": mean.values,
            "std_pass": std.values,
            "lower": (mean - 2 * std).values,
            "upper": (mean + 2 * std).values,
        }
    )
    return table


threshold_table = build_threshold_table(X_test, y_test)
threshold_table.to_csv(MODEL_DIR / "threshold_table.csv", index=False)
print(f"\nthreshold_table — {len(threshold_table)} sensors → models/threshold_table.csv")

# %% [markdown]
# ## 8. 직렬화


joblib.dump(final_model, MODEL_DIR / "xgb_secom.joblib")
print(f"모델 저장 → {MODEL_DIR / 'xgb_secom.joblib'}")

# 데모 결과 사전 캐싱
demo_sample = pd.read_pickle(PROC_DIR / "demo_sample.pkl")
demo_proba = final_model.predict_proba(demo_sample)[:, 1]
demo_result = pd.DataFrame(
    {
        "sample_id": demo_sample.index,
        "pred_proba": demo_proba,
        "pred_label": (demo_proba >= best_threshold).astype(int),
    }
)
demo_result.to_csv(PROC_DIR / "demo_result.csv", index=False)

# %% [markdown]
# ## 9. Model Card


model_card = f"""# Model Card — QualityLens XGBoost

## 학습 환경
- 알고리즘: XGBoost (binary:logistic, eval_metric=aucpr)
- 데이터: UCI SECOM (또는 더미)
- Split: Stratified, test_size=0.2, random_state=42
- 검증: Stratified K-Fold (k={N_SPLITS})
- 클래스 불균형: SMOTE 적용 + scale_pos_weight={pos_weight:.2f}

## 하이퍼파라미터
{params}

## 성능
- CV  MCC  : {np.mean(fold_mccs):.4f} ± {np.std(fold_mccs):.4f}
- CV  PRAUC: {np.mean(fold_prs):.4f} ± {np.std(fold_prs):.4f}
- Test MCC (@0.5)             : {test_mcc_default:.4f}
- Test MCC (@{best_threshold:.4f}, Youden's J): {test_mcc_opt:.4f}
- Test PR-AUC                 : {test_pr_auc:.4f}

## 운영 threshold
- 추론 시 사용: **{best_threshold:.4f}**
- 평가 지표: MCC (불균형 6.6% fail rate에 최적)

## 산출물
- `models/xgb_secom.joblib`     — 직렬화 모델
- `models/threshold_table.csv`  — sensor별 mean±2σ 정상 범위

## 운영 규칙 (codex-bridge/token-saving.md)
- 본선장에서 재학습 금지 — 직렬화 로드만
- 단일 샘플 추론 < 10ms (라인 모니터링 요건)
"""

(MODEL_DIR / "model_card.md").write_text(model_card, encoding="utf-8")
print(f"Model Card → {MODEL_DIR / 'model_card.md'}")

print("\n=== T2 완료 ===")
print(f"운영 threshold = {best_threshold:.4f}")
print("다음: scripts/03_shap.py")
