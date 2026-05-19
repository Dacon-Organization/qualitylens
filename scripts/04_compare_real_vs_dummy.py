"""T4 — real vs dummy 비교 보고서.

real 과 dummy 산출물을 둘 다 로드해서:
1. 데이터 비교 표 (행수, 피처수, 결측, 불량 비율)
2. 분포 비교 PNG (상위 5개 피처)
3. 모델 성능 표 (ROC-AUC, PR-AUC, MCC, F1)
4. 임계값 곡선 (ROC, PR)
5. SHAP Top 10 겹침 분석
6. 데모 4건 Waterfall 비교
7. 결론 요약 자동 문장

산출물:
- ``docs/validation/real_vs_dummy_report.md``
- ``assets/charts/validation/*.png``

CLI::

    python scripts/04_compare_real_vs_dummy.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    matthews_corrcoef,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.lib.fonts import setup_matplotlib

setup_matplotlib()

PROC_DIR = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "models"
DOCS_DIR = ROOT / "docs" / "validation"
CHARTS_DIR = ROOT / "assets" / "charts" / "validation"
DOCS_DIR.mkdir(parents=True, exist_ok=True)
CHARTS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 1. 데이터 로딩 헬퍼
# ---------------------------------------------------------------------------


def load_bundle(suffix: str) -> dict:
    """suffix = '_real' or '_dummy'."""
    return {
        "X_test": pd.read_pickle(PROC_DIR / f"secom_X_test{suffix}.pkl"),
        "y_test": pd.read_pickle(PROC_DIR / f"secom_y_test{suffix}.pkl"),
        "model": joblib.load(MODEL_DIR / f"xgb_secom{suffix}.joblib"),
        "shap_top20": pd.read_csv(MODEL_DIR / f"shap_top20{suffix}.csv"),
        "waterfall_demo": joblib.load(MODEL_DIR / f"shap_waterfall_demo{suffix}.pkl"),
        "thresholds": pd.read_csv(MODEL_DIR / f"threshold_table{suffix}.csv"),
    }


real = load_bundle("_real")
dummy = load_bundle("_dummy")


# ---------------------------------------------------------------------------
# 2. 데이터 비교 표
# ---------------------------------------------------------------------------


def data_summary(name: str, bundle: dict) -> dict:
    X = bundle["X_test"]
    y = bundle["y_test"]
    return {
        "source": name,
        "rows": len(X),
        "features": X.shape[1],
        "missing_rate": float(X.isna().mean().mean()),
        "fail_rate": float(y.mean()),
    }


data_table = pd.DataFrame([data_summary("real", real), data_summary("dummy", dummy)])


# ---------------------------------------------------------------------------
# 3. 분포 비교 — 상위 5개 피처 히스토그램
# ---------------------------------------------------------------------------

top_features = real["shap_top20"].head(5)["sensor"].tolist()
common_features = [f for f in top_features if f in dummy["X_test"].columns]

fig, axes = plt.subplots(1, max(len(common_features), 1), figsize=(4 * max(len(common_features), 1), 3))
if len(common_features) <= 1:
    axes = [axes] if len(common_features) == 1 else [plt.gca()]
elif not hasattr(axes, "__iter__"):
    axes = [axes]
for ax, feat in zip(axes, common_features):
    ax.hist(real["X_test"][feat].dropna(), bins=30, alpha=0.5, label="real", color="#1f77b4")
    if feat in dummy["X_test"].columns:
        ax.hist(dummy["X_test"][feat].dropna(), bins=30, alpha=0.5, label="dummy", color="#ff7f0e")
    ax.set_title(feat, fontsize=10)
    ax.legend(fontsize=8)
plt.tight_layout()
dist_png = CHARTS_DIR / "distribution_top5.png"
fig.savefig(dist_png, dpi=120)
plt.close(fig)


# ---------------------------------------------------------------------------
# 4. 모델 성능 표
# ---------------------------------------------------------------------------


def perf_summary(name: str, bundle: dict) -> dict:
    proba = bundle["model"].predict_proba(bundle["X_test"])[:, 1]
    pred_default = (proba >= 0.5).astype(int)
    fpr, tpr, thr = roc_curve(bundle["y_test"], proba)
    j_idx = int(np.argmax(tpr - fpr))
    best_thr = float(thr[j_idx])
    pred_opt = (proba >= best_thr).astype(int)
    return {
        "source": name,
        "roc_auc": roc_auc_score(bundle["y_test"], proba),
        "pr_auc": average_precision_score(bundle["y_test"], proba),
        "mcc_default": matthews_corrcoef(bundle["y_test"], pred_default),
        "mcc_opt": matthews_corrcoef(bundle["y_test"], pred_opt),
        "f1_opt": f1_score(bundle["y_test"], pred_opt),
        "best_threshold": best_thr,
    }


perf_table = pd.DataFrame([perf_summary("real", real), perf_summary("dummy", dummy)])


# ---------------------------------------------------------------------------
# 5. ROC + PR 곡선 겹쳐 그리기
# ---------------------------------------------------------------------------

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
for name, bundle, color in (("real", real, "#1f77b4"), ("dummy", dummy, "#ff7f0e")):
    proba = bundle["model"].predict_proba(bundle["X_test"])[:, 1]
    fpr, tpr, _ = roc_curve(bundle["y_test"], proba)
    p, r, _ = precision_recall_curve(bundle["y_test"], proba)
    ax1.plot(fpr, tpr, color=color, label=name)
    ax2.plot(r, p, color=color, label=name)
ax1.plot([0, 1], [0, 1], "k--", alpha=0.3)
ax1.set(xlabel="FPR", ylabel="TPR", title="ROC")
ax1.legend()
ax2.set(xlabel="Recall", ylabel="Precision", title="PR")
ax2.legend()
plt.tight_layout()
curves_png = CHARTS_DIR / "roc_pr_curves.png"
fig.savefig(curves_png, dpi=120)
plt.close(fig)


# ---------------------------------------------------------------------------
# 6. SHAP Top 10 겹침 분석
# ---------------------------------------------------------------------------

real_top10 = set(real["shap_top20"].head(10)["sensor"])
dummy_top10 = set(dummy["shap_top20"].head(10)["sensor"])
overlap = real_top10 & dummy_top10
only_real = real_top10 - dummy_top10
only_dummy = dummy_top10 - real_top10


# ---------------------------------------------------------------------------
# 7. 데모 4건 Waterfall 비교 (단순 표)
# ---------------------------------------------------------------------------


def waterfall_table(bundle: dict, name: str) -> pd.DataFrame:
    rows = []
    for sid, data in bundle["waterfall_demo"]["samples"].items():
        rows.append({
            "source": name,
            "sample_id": sid,
            "final_logit": data["final_logit"],
            "top_features": ", ".join(data["features"][:3]),
        })
    return pd.DataFrame(rows)


waterfall_compare = pd.concat([
    waterfall_table(real, "real"),
    waterfall_table(dummy, "dummy"),
])


# ---------------------------------------------------------------------------
# 8. 결론 요약 자동 문장
# ---------------------------------------------------------------------------

real_roc = perf_table.iloc[0]["roc_auc"]
dummy_roc = perf_table.iloc[1]["roc_auc"]
diff = real_roc - dummy_roc
overlap_pct = len(overlap) / 10 * 100

if diff > 0.05:
    _perf_sentence = "실데이터가 명확히 우수."
elif diff < -0.05:
    _perf_sentence = "더미가 더 잘 분류 — 실데이터의 노이즈·불균형 도전 큼."
else:
    _perf_sentence = "실데이터·더미 성능이 유사 — 더미가 합리적으로 설계됨."

conclusion = f"""## 결론 요약

- **모델 성능**: 실데이터 ROC-AUC = {real_roc:.3f}, 더미 = {dummy_roc:.3f} (Δ {diff:+.3f}).
  {_perf_sentence}
- **SHAP Top 10 겹침**: {len(overlap)}/10 ({overlap_pct:.0f}%). 공통 센서: {sorted(overlap) if overlap else '없음'}.
- **익명화 한계 주의**: SECOM 센서 의미 라벨은 익명화되어 있어 "어떤 센서가 식각 온도인지" 검증 불가.
  본 보고서는 분포·기여도 패턴만 검증하며, 라벨 매핑은 발표 단계의 기획 가정.
- **본선 발표 활용**: `slides_outline.md` Slide 4 의 "Real Data Verified" 문구에 ROC-AUC = {real_roc:.3f} 인용 가능.
"""


# ---------------------------------------------------------------------------
# 9. 마크다운 출력
# ---------------------------------------------------------------------------

md = f"""# real vs dummy 비교 보고서

> 생성: scripts/04_compare_real_vs_dummy.py 자동 실행 산출물
> Spec: smart-factory-hackathon/docs/spec_p_a_real_data_integration.md

## 1. 데이터 비교

{data_table.to_markdown(index=False, floatfmt='.4f')}

## 2. 분포 비교 (상위 5개 SHAP 피처)

![distribution]({dist_png.relative_to(ROOT).as_posix()})

## 3. 모델 성능

{perf_table.to_markdown(index=False, floatfmt='.4f')}

## 4. ROC · PR 곡선

![roc_pr]({curves_png.relative_to(ROOT).as_posix()})

## 5. SHAP Top 10 겹침

- **겹침 ({len(overlap)}/10)**: {sorted(overlap) if overlap else '(없음)'}
- **real 만**: {sorted(only_real) if only_real else '(없음)'}
- **dummy 만**: {sorted(only_dummy) if only_dummy else '(없음)'}

## 6. 데모 4건 Waterfall 비교

{waterfall_compare.to_markdown(index=False, floatfmt='.4f')}

{conclusion}
"""

md_path = DOCS_DIR / "real_vs_dummy_report.md"
md_path.write_text(md, encoding="utf-8")
print(f"마크다운 보고서 → {md_path}")
print(f"차트 → {dist_png}, {curves_png}")

# %% [markdown]
# ## 10. HTML 보고서 출력 (P-A G3)

from app.lib.report_render import write as write_report

dist_rel = dist_png.relative_to(ROOT).as_posix()
curves_rel = curves_png.relative_to(ROOT).as_posix()

sections = [
    {
        "title": "1. 데이터 비교",
        "body_html": data_table.to_html(index=False, float_format="%.4f"),
    },
    {
        "title": "2. 분포 비교 (상위 5개 SHAP 피처)",
        "body_html": f'<img src="../../{dist_rel}" alt="distribution">',
    },
    {
        "title": "3. 모델 성능",
        "body_html": perf_table.to_html(index=False, float_format="%.4f"),
    },
    {
        "title": "4. ROC · PR 곡선",
        "body_html": f'<img src="../../{curves_rel}" alt="roc_pr">',
    },
    {
        "title": "5. SHAP Top 10 겹침",
        "body_html": (
            f"<p>겹침 {len(overlap)}/10</p>"
            f"<p>공통: {sorted(overlap) if overlap else '(없음)'}</p>"
            f"<p>real만: {sorted(only_real) if only_real else '(없음)'}</p>"
            f"<p>dummy만: {sorted(only_dummy) if only_dummy else '(없음)'}</p>"
        ),
    },
    {
        "title": "6. 결론 요약",
        "body_html": (
            f"<p>실데이터 ROC-AUC = {real_roc:.3f}, 더미 = {dummy_roc:.3f} (Δ {diff:+.3f})</p>"
            f"<p>SHAP Top 10 겹침: {overlap_pct:.0f}%</p>"
        ),
    },
]
write_report("compare", source="real", sections=sections)

print("\n=== T4 비교 보고서 완료 ===")
