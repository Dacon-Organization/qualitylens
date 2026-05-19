"""모델·데이터 로드 헬퍼.

모든 무거운 객체는 ``@st.cache_resource``, DataFrame 가공은 ``@st.cache_data``.
산출물이 없으면 더미를 반환해 UI가 끝까지 동작하도록 폴백.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
PROC_DIR = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "models"


@st.cache_resource
def load_model():
    path = MODEL_DIR / "xgb_secom.joblib"
    if not path.exists():
        return None
    return joblib.load(path)


@st.cache_resource
def load_explainer():
    path = MODEL_DIR / "shap_explainer.pkl"
    if not path.exists():
        return None
    return joblib.load(path)


@st.cache_data
def load_test_set() -> tuple[pd.DataFrame, pd.Series]:
    x_path = PROC_DIR / "secom_X_test.pkl"
    y_path = PROC_DIR / "secom_y_test.pkl"
    if not (x_path.exists() and y_path.exists()):
        return _dummy_test()
    return pd.read_pickle(x_path), pd.read_pickle(y_path)


@st.cache_data
def load_demo_sample() -> pd.DataFrame:
    path = PROC_DIR / "demo_sample.pkl"
    if not path.exists():
        X, _ = _dummy_test()
        return X.head(4)
    return pd.read_pickle(path)


@st.cache_data
def load_demo_result() -> pd.DataFrame:
    path = PROC_DIR / "demo_result.csv"
    if not path.exists():
        sample = load_demo_sample()
        return pd.DataFrame(
            {
                "sample_id": sample.index,
                "pred_proba": np.linspace(0.15, 0.85, len(sample)),
                "pred_label": [0, 0, 1, 1][: len(sample)],
            }
        )
    return pd.read_csv(path)


@st.cache_data
def load_thresholds() -> pd.DataFrame:
    path = MODEL_DIR / "threshold_table.csv"
    if not path.exists():
        X, _ = _dummy_test()
        return pd.DataFrame(
            {
                "sensor": X.columns,
                "mean_pass": X.mean().values,
                "std_pass": X.std().values,
                "lower": (X.mean() - 2 * X.std()).values,
                "upper": (X.mean() + 2 * X.std()).values,
            }
        )
    return pd.read_csv(path)


@st.cache_data
def load_shap_top20() -> pd.DataFrame:
    path = MODEL_DIR / "shap_top20.csv"
    if not path.exists():
        X, _ = _dummy_test()
        rng = np.random.default_rng(42)
        return (
            pd.DataFrame(
                {
                    "sensor": X.columns[:20],
                    "mean_abs_shap": rng.uniform(0.05, 0.5, 20),
                }
            )
            .sort_values("mean_abs_shap", ascending=False)
            .reset_index(drop=True)
        )
    return pd.read_csv(path)


@st.cache_data
def load_shap_per_sample() -> pd.DataFrame | None:
    path = MODEL_DIR / "shap_per_sample.pkl"
    if not path.exists():
        return None
    return joblib.load(path)


@st.cache_data
def load_shap_waterfall_demo() -> dict | None:
    """S-2 사전 패키지 — base_value + 샘플별 top 10 features/values/shap."""
    path = MODEL_DIR / "shap_waterfall_demo.pkl"
    if not path.exists():
        return None
    return joblib.load(path)


@st.cache_data
def load_shap_values_test():
    """test set 전체 SHAP values (numpy array) — Dependence Plot용."""
    path = MODEL_DIR / "shap_values_test.pkl"
    if not path.exists():
        return None
    return joblib.load(path)


def _dummy_test() -> tuple[pd.DataFrame, pd.Series]:
    rng = np.random.default_rng(42)
    X = pd.DataFrame(
        rng.normal(size=(200, 30)),
        columns=[f"sensor_{i:03d}" for i in range(30)],
    )
    y = pd.Series(rng.choice([0, 1], size=200, p=[0.93, 0.07]))
    return X, y


def status_banner() -> None:
    """모델·데이터 존재 여부를 한눈에 표시."""
    model = load_model()
    if model is None:
        st.warning(
            "⚠️ 모델·데이터 산출물이 없습니다. `scripts/01_preprocess.py` → "
            "`02_train.py` → `03_shap.py` 순으로 실행하세요. "
            "지금은 더미 데이터로 UI 동작만 확인 가능합니다."
        )
