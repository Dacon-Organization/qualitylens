"""PR-21 회귀 테스트 — Mode + 상태 전역화 fix.

목표: 다음 5건 검증
1. resolve_source 명시 인자 우선 (cache 키 분리 보장)
2. data_loader cached 함수 시그니처에 source 인자 존재
3. demo.ensure_demo_state 호출 후 session_state 일관성
4. demo.get_source 호출 후 _data_source 반환
5. demo.has_user_data / get_user_data SSoT 동작

Streamlit session_state는 dict로 모킹.
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))


# -----------------------------------------------------------------------------
# Fixture — st.session_state를 dict 모킹
# -----------------------------------------------------------------------------


class FakeSessionState(dict):
    """st.session_state를 dict처럼 동작시키되 attribute 접근도 허용."""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value


@pytest.fixture
def mock_streamlit(monkeypatch):
    """streamlit.session_state를 dict로 모킹 + sidebar/markdown no-op."""
    import streamlit as st

    fake_state = FakeSessionState()
    monkeypatch.setattr(st, "session_state", fake_state)

    # sidebar/title/markdown/divider/caption/radio no-op (테스트에서 렌더 불필요)
    fake_sidebar = MagicMock()
    fake_sidebar.title = MagicMock()
    fake_sidebar.divider = MagicMock()
    fake_sidebar.caption = MagicMock()
    fake_sidebar.markdown = MagicMock()
    monkeypatch.setattr(st, "sidebar", fake_sidebar)
    return fake_state


# -----------------------------------------------------------------------------
# 테스트 1: resolve_source 명시 인자 우선 (기존 검증 강화)
# -----------------------------------------------------------------------------


def test_resolve_source_explicit_priority(monkeypatch):
    """명시 인자가 환경변수 + 자동 감지보다 우선."""
    monkeypatch.setenv("DEMO_MODE", "real")
    from app.lib.data_loader import resolve_source

    # 명시 dummy 인자가 env real을 무시
    assert resolve_source("dummy") == "dummy"
    # None이면 env 사용
    assert resolve_source(None) == "real"


# -----------------------------------------------------------------------------
# 테스트 2: cached 함수 시그니처에 source 인자 존재
# -----------------------------------------------------------------------------


def test_cached_loaders_accept_source_arg():
    """모든 cached 로더가 source 키워드 인자를 받아야 cache 키 분리 가능."""
    from app.lib import data_loader

    targets = [
        "load_model",
        "load_explainer",
        "load_test_set",
        "load_demo_sample",
        "load_demo_result",
        "load_thresholds",
        "load_shap_top20",
        "load_shap_per_sample",
        "load_shap_waterfall_demo",
        "load_shap_values_test",
    ]

    for name in targets:
        fn = getattr(data_loader, name)
        # st.cache_* 데코레이터로 감싸진 후에도 inspect 가능
        sig = inspect.signature(fn)
        assert "source" in sig.parameters, (
            f"{name} 시그니처에 'source' 인자 부재 — 캐시 키 분리 불가"
        )


def test_sidebar_badge_status_banner_accept_source():
    """sidebar_badge / status_banner도 source 인자 받아야 정확한 mode 표시."""
    from app.lib import data_loader

    for name in ("sidebar_badge", "status_banner"):
        fn = getattr(data_loader, name)
        sig = inspect.signature(fn)
        assert "source" in sig.parameters, (
            f"{name} 시그니처에 'source' 인자 부재 — PR-21 fix 누락"
        )


# -----------------------------------------------------------------------------
# 테스트 3: ensure_demo_state 호출 후 session_state 일관성
# -----------------------------------------------------------------------------


def test_ensure_demo_state_initializes_keys(mock_streamlit):
    """ensure_demo_state 호출 후 4개 SSoT 키 모두 일관성 있게 설정."""
    from app.lib.demo import ensure_demo_state

    is_demo, source = ensure_demo_state()

    # 기본은 데모 모드
    assert is_demo is True
    assert source == "dummy"

    # session_state 4개 키 모두 설정됨
    assert "_demo_mode_radio" in mock_streamlit
    assert "_demo_mode" in mock_streamlit
    assert "_data_source" in mock_streamlit
    assert mock_streamlit["_demo_mode"] is True
    assert mock_streamlit["_data_source"] == "dummy"


def test_ensure_demo_state_real_when_radio_changed(mock_streamlit):
    """radio가 실데이터로 선택되면 source가 real로 동기화."""
    from app.lib.demo import ensure_demo_state

    # 사용자가 radio에서 실데이터 선택했다고 가정
    mock_streamlit["_demo_mode_radio"] = "실데이터 (UCI SECOM)"

    is_demo, source = ensure_demo_state()

    assert is_demo is False
    assert source == "real"
    assert mock_streamlit["_data_source"] == "real"


# -----------------------------------------------------------------------------
# 테스트 4: get_source() — 캐시 키 일치를 위한 헬퍼
# -----------------------------------------------------------------------------


def test_get_source_returns_dummy_default(mock_streamlit):
    """초기 상태에서 get_source() → 'dummy' 반환 (안전한 기본)."""
    from app.lib.demo import get_source

    assert get_source() == "dummy"


def test_get_source_respects_data_source_key(mock_streamlit):
    """_data_source 키가 이미 설정되어 있으면 그 값을 반환 (페이지 이동 후 일관성)."""
    from app.lib.demo import get_source

    mock_streamlit["_data_source"] = "real"
    mock_streamlit["_demo_mode_radio"] = "실데이터 (UCI SECOM)"

    assert get_source() == "real"


# -----------------------------------------------------------------------------
# 테스트 5: user_data SSoT (Step 3 — 사용자 PM 처방)
# -----------------------------------------------------------------------------


def test_has_user_data_false_initially(mock_streamlit):
    """초기에 업로드 데이터 없음."""
    from app.lib.demo import has_user_data

    assert has_user_data() is False


def test_user_data_ssot_after_upload(mock_streamlit):
    """업로드 데이터가 session_state["user_data"]에 저장되면 모든 페이지에서 동일하게 읽힘."""
    import pandas as pd

    from app.lib.demo import get_user_data, get_user_data_meta, has_user_data

    sample_df = pd.DataFrame({"sample_id": [1, 2], "pred_proba": [0.1, 0.9]})
    mock_streamlit["user_data"] = sample_df
    mock_streamlit["user_data_meta"] = {"n_samples": 2, "n_features": 591}

    assert has_user_data() is True
    assert get_user_data() is sample_df
    assert get_user_data_meta() == {"n_samples": 2, "n_features": 591}


def test_get_user_data_meta_default_empty(mock_streamlit):
    """user_data_meta가 없으면 빈 dict 반환 (안전한 graceful)."""
    from app.lib.demo import get_user_data_meta

    assert get_user_data_meta() == {}
