"""데이터·모델 로드 통합 — real 우선 → dummy 폴백.

기존 ``app/lib/load.py`` 의 각 함수를 이 모듈에 위임하면서, 산출물 경로를
``_real`` / ``_dummy`` 접미사로 분기한다. 환경변수 ``DEMO_MODE`` 또는
명시 인자 ``source`` 로 강제 가능.

세션 상태:
    st.session_state['_data_source'] : 'real' | 'dummy'  (사이드바 배지용)
"""

from __future__ import annotations

import os
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
PROC_DIR = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "models"

VALID_SOURCES = ("real", "dummy")


def resolve_source(explicit: str | None = None) -> str:
    """우선순위: 명시 인자 > 환경변수 DEMO_MODE > 자동 감지 (real 우선).

    PR-27: 명시 "real" 요청이라도 핵심 산출물 부재 시 dummy로 graceful fallback.
    Streamlit Cloud 무료 티어/git LFS 미적용 환경에서 _real 산출물 일부만 push된 경우 대응.
    fallback 발생 시 session_state["_real_fallback"]=True로 표시 → 사이드바 안내.
    """
    forced = explicit or os.getenv("DEMO_MODE")
    if forced in VALID_SOURCES:
        if forced == "real" and not _real_artifacts_complete():
            # 사용자 선택은 real이지만 산출물 부재 → 데이터만 dummy fallback
            try:
                st.session_state["_real_fallback"] = True
            except Exception:
                pass
            return "dummy"
        if forced == "real":
            try:
                st.session_state["_real_fallback"] = False
            except Exception:
                pass
        return forced
    return _detect_default_source()


def _real_artifacts_complete() -> bool:
    """real 모드 정상 동작에 필요한 핵심 산출물 7종 모두 존재 여부."""
    required = [
        MODEL_DIR / "xgb_secom_real.joblib",
        MODEL_DIR / "shap_explainer_real.pkl",
        MODEL_DIR / "shap_per_sample_real.pkl",
        MODEL_DIR / "shap_values_test_real.pkl",
        MODEL_DIR / "shap_waterfall_demo_real.pkl",
        PROC_DIR / "secom_X_test_real.pkl",
        PROC_DIR / "secom_y_test_real.pkl",
    ]
    return all(p.exists() for p in required)


def _detect_default_source() -> str:
    return "real" if _real_artifacts_complete() else "dummy"


def _set_session_source(source: str) -> None:
    if "_data_source" not in st.session_state or st.session_state["_data_source"] != source:
        st.session_state["_data_source"] = source


def current_source() -> str:
    """이미 결정된 세션 소스 반환 (없으면 자동 결정)."""
    if "_data_source" in st.session_state:
        return st.session_state["_data_source"]
    source = resolve_source()
    _set_session_source(source)
    return source


@st.cache_resource
def load_model(source: str | None = None):
    source = resolve_source(source)
    _set_session_source(source)
    path = MODEL_DIR / f"xgb_secom_{source}.joblib"
    if not path.exists():
        return None
    return joblib.load(path)


@st.cache_resource
def load_explainer(source: str | None = None):
    source = resolve_source(source)
    path = MODEL_DIR / f"shap_explainer_{source}.pkl"
    if not path.exists():
        return None
    return joblib.load(path)


@st.cache_data
def load_test_set(source: str | None = None) -> tuple[pd.DataFrame, pd.Series]:
    source = resolve_source(source)
    x_path = PROC_DIR / f"secom_X_test_{source}.pkl"
    y_path = PROC_DIR / f"secom_y_test_{source}.pkl"
    if not (x_path.exists() and y_path.exists()):
        raise FileNotFoundError(
            f"산출물 부재 ({source}): {x_path.name} 또는 {y_path.name}. "
            f"scripts/01_preprocess.py --source {source} 실행 필요."
        )
    return pd.read_pickle(x_path), pd.read_pickle(y_path)


@st.cache_data
def load_demo_sample(source: str | None = None) -> pd.DataFrame:
    source = resolve_source(source)
    path = PROC_DIR / f"demo_sample_{source}.pkl"
    if not path.exists():
        raise FileNotFoundError(f"demo_sample_{source}.pkl 부재")
    return pd.read_pickle(path)


@st.cache_data
def load_demo_result(source: str | None = None) -> pd.DataFrame:
    source = resolve_source(source)
    path = PROC_DIR / f"demo_result_{source}.csv"
    if not path.exists():
        raise FileNotFoundError(f"demo_result_{source}.csv 부재")
    return pd.read_csv(path)


@st.cache_data
def load_thresholds(source: str | None = None) -> pd.DataFrame:
    source = resolve_source(source)
    path = MODEL_DIR / f"threshold_table_{source}.csv"
    if not path.exists():
        raise FileNotFoundError(f"threshold_table_{source}.csv 부재")
    return pd.read_csv(path)


@st.cache_data
def load_shap_top20(source: str | None = None) -> pd.DataFrame:
    source = resolve_source(source)
    path = MODEL_DIR / f"shap_top20_{source}.csv"
    if not path.exists():
        raise FileNotFoundError(f"shap_top20_{source}.csv 부재")
    return pd.read_csv(path)


@st.cache_data
def load_shap_per_sample(source: str | None = None):
    source = resolve_source(source)
    path = MODEL_DIR / f"shap_per_sample_{source}.pkl"
    if not path.exists():
        return None
    return joblib.load(path)


@st.cache_data
def load_shap_waterfall_demo(source: str | None = None) -> dict | None:
    source = resolve_source(source)
    path = MODEL_DIR / f"shap_waterfall_demo_{source}.pkl"
    if not path.exists():
        return None
    return joblib.load(path)


@st.cache_data
def load_shap_values_test(source: str | None = None):
    source = resolve_source(source)
    path = MODEL_DIR / f"shap_values_test_{source}.pkl"
    if not path.exists():
        return None
    return joblib.load(path)


def sidebar_badge(source: str | None = None) -> None:
    """사이드바 배지 — 현재 소스 + PR-27 graceful fallback 알림.

    PR-21: source 인자 명시 지원 (demo_sidebar() 선택 결과 정확 반영).
    PR-27: real 산출물 부재로 dummy fallback 시 명확한 안내 표시.
    """
    # PR-27: 사용자가 선택한 모드와 실제 사용 source 분리
    user_choice = st.session_state.get("_demo_mode_radio", "")
    user_wants_real = user_choice.startswith("실데이터")

    if source is None:
        source = st.session_state.get("_data_source") or current_source()

    fallback_active = st.session_state.get("_real_fallback", False)

    if user_wants_real and fallback_active:
        # 사용자는 real 원하지만 산출물 부재 → 명확한 안내
        st.sidebar.markdown(
            "<div style='padding:6px 10px;border-radius:6px;background:#c89400;"
            "color:white;font-size:12px;display:inline-block;'>🟡 real → dummy 폴백</div>",
            unsafe_allow_html=True,
        )
        st.sidebar.caption(
            "⚠️ 실데이터 산출물(xgb_secom_real.joblib 등 7종)이 Cloud에 없어 데모로 폴백. "
            "로컬에서 `scripts/01~03_*.py --source real` 실행 후 LFS push 시 정상 동작."
        )
    elif source == "real":
        st.sidebar.markdown(
            "<div style='padding:6px 10px;border-radius:6px;background:#1e7c3a;"
            "color:white;font-size:12px;display:inline-block;'>🟢 real (UCI SECOM)</div>",
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown(
            "<div style='padding:6px 10px;border-radius:6px;background:#c89400;"
            "color:white;font-size:12px;display:inline-block;'>🟡 dummy (데모)</div>",
            unsafe_allow_html=True,
        )


def status_banner(source: str | None = None) -> None:
    """상단 status 배너 — 산출물 부재 시 경고.

    PR-21: source 인자 받아 정확한 source의 모델 상태 확인.
    """
    try:
        model = load_model(source=source)
    except Exception as exc:
        st.error(f"모델 로드 실패: {exc}")
        return
    if model is None:
        st.warning(
            "⚠️ 모델 산출물이 없습니다. `scripts/01_preprocess.py --source real` → "
            "`02_train.py --source real` → `03_shap.py --source real` 순으로 실행하세요."
        )
