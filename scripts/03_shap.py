"""T3 — SHAP 사전 계산.

T2 모델을 로드해 test set 전체에 대해 SHAP value를 한 번 계산하고
직렬화한다. 본선장에서는 절대 재계산하지 않는다 (codex-bridge/token-saving.md).

산출물:
- ``models/shap_explainer.pkl`` — TreeExplainer 인스턴스
- ``models/shap_values_test.pkl`` — test set 전체 shap value (n × p)
- ``models/shap_top20.csv`` — 평균 |SHAP| 상위 20 피처
- ``models/shap_per_sample.pkl`` — 데모 4건 샘플별 SHAP value
- ``data/processed/shap_demo.png`` — 발표용 백업 이미지 1장

CLI::

    python scripts/03_shap.py
"""

from __future__ import annotations

from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")  # 헤드리스 환경 (Streamlit Cloud 등)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from _i18n import setup_korean_font

setup_korean_font()  # 한글 라벨 깨짐 방지 (Windows/macOS/Linux 자동 감지)

ROOT = Path(__file__).resolve().parent.parent
PROC_DIR = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "models"

# %% [markdown]
# ## 1. 모델·데이터 로드


model = joblib.load(MODEL_DIR / "xgb_secom.joblib")
X_test = pd.read_pickle(PROC_DIR / "secom_X_test.pkl")
demo_sample = pd.read_pickle(PROC_DIR / "demo_sample.pkl")
print(f"모델 로드 / test {X_test.shape} / demo {demo_sample.shape}")

# %% [markdown]
# ## 2. TreeExplainer 생성


explainer = shap.TreeExplainer(model)
joblib.dump(explainer, MODEL_DIR / "shap_explainer.pkl")
print(f"Explainer 저장 → {MODEL_DIR / 'shap_explainer.pkl'}")

# %% [markdown]
# ## 3. Test set 전체 SHAP value 사전 계산


shap_values_test = explainer.shap_values(X_test)
# XGBoost binary: 2D 배열 그대로
shap_arr = (
    shap_values_test if isinstance(shap_values_test, np.ndarray) else shap_values_test[1]
)
joblib.dump(shap_arr, MODEL_DIR / "shap_values_test.pkl")
print(f"shap_values_test 저장 → shape {shap_arr.shape}")

# %% [markdown]
# ## 4. 평균 |SHAP| 상위 20 피처


mean_abs = np.abs(shap_arr).mean(axis=0)
top20 = (
    pd.DataFrame({"sensor": X_test.columns, "mean_abs_shap": mean_abs})
    .sort_values("mean_abs_shap", ascending=False)
    .head(20)
    .reset_index(drop=True)
)
top20.to_csv(MODEL_DIR / "shap_top20.csv", index=False)
print("\n상위 20 피처:")
print(top20.to_string())

# %% [markdown]
# ## 5. 데모 4건 샘플별 SHAP


demo_shap = explainer.shap_values(demo_sample)
demo_shap_arr = demo_shap if isinstance(demo_shap, np.ndarray) else demo_shap[1]
demo_shap_df = pd.DataFrame(
    demo_shap_arr,
    columns=demo_sample.columns,
    index=demo_sample.index,
)
joblib.dump(demo_shap_df, MODEL_DIR / "shap_per_sample.pkl")
print(f"\n데모 SHAP 저장 → shape {demo_shap_df.shape}")

# %% [markdown]
# ## 6. 발표용 백업 이미지 — top 15 bar plot


fig, ax = plt.subplots(figsize=(8, 5))
top15 = top20.head(15)
ax.barh(top15["sensor"][::-1], top15["mean_abs_shap"][::-1], color="#58a6ff")
ax.set_xlabel("mean |SHAP|")
ax.set_title("QualityLens — 상위 15 기여 센서")
plt.tight_layout()
fig.savefig(PROC_DIR / "shap_demo.png", dpi=120)
plt.close(fig)
print(f"백업 이미지 → {PROC_DIR / 'shap_demo.png'}")

# %% [markdown]
# ## 7. 센서 그룹별 평균 기여도
# 591개 센서를 100단위로 그룹핑 → radar/bar 차트 데이터


def sensor_group(name: str) -> str:
    """sensor_042 → group_000."""
    try:
        idx = int(name.split("_")[1])
        return f"group_{idx // 100:03d}"
    except (IndexError, ValueError):
        return "group_unknown"


group_contrib = (
    pd.DataFrame({"sensor": X_test.columns, "mean_abs_shap": mean_abs})
    .assign(group=lambda d: d["sensor"].map(sensor_group))
    .groupby("group", as_index=False)["mean_abs_shap"]
    .mean()
    .sort_values("mean_abs_shap", ascending=False)
)
group_contrib.to_csv(MODEL_DIR / "shap_group.csv", index=False)
print("\n그룹별 평균 기여도:")
print(group_contrib.to_string(index=False))

print("\n=== T3 완료 ===")
print("모든 SHAP 산출물이 사전 계산되어 본선장 재계산 불필요.")
print("다음: app/ (T4 Streamlit UI)")
