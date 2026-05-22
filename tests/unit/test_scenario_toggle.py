"""PR-9F 단위 테스트 — 시나리오 토글 (session_state 우회 패턴).

설계 핵심 (Critical Pitfall C-1 회피):
- demo_sidebar() 반환 시그니처 bool 유지 (호출처 5곳 무변경)
- 시나리오는 session_state["_scenario"]로 별도 노출
- 옵셔널 읽기: get_scenario() 미설정 시 "NORMAL" 폴백

검증 8건:
1. SCENARIOS 3종 정의 (NORMAL/WARN/ANOMALY)
2. SCENARIO_LABELS / SCENARIO_DESCRIPTIONS 모두 매핑
3. get_scenario() 미설정 시 "NORMAL" 폴백
4. set_scenario() 정상 동작 + 잘못된 값 ValueError
5. filter_samples_by_scenario NORMAL → 정상 샘플만
6. filter_samples_by_scenario ANOMALY → 이상 샘플만
7. filter_samples_by_scenario WARN → 경고 영역만
8. pred_proba 컬럼 부재 시 전체 폴백
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))


# -----------------------------------------------------------------------------
# Fixture — st.session_state를 dict로 모킹
# -----------------------------------------------------------------------------


class FakeSessionState(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value


@pytest.fixture(autouse=True)
def mock_streamlit_session(monkeypatch):
    """st.session_state를 FakeSessionState로 대체."""
    import streamlit as st
    fake = FakeSessionState()
    monkeypatch.setattr(st, "session_state", fake)
    yield fake


# -----------------------------------------------------------------------------
# Test 1 — SCENARIOS 3종 정의
# -----------------------------------------------------------------------------


def test_scenarios_defined():
    from app.lib.demo import SCENARIOS

    assert SCENARIOS == ["NORMAL", "WARN", "ANOMALY"]


def test_scenario_labels_complete():
    from app.lib.demo import SCENARIO_DESCRIPTIONS, SCENARIO_LABELS, SCENARIOS

    for s in SCENARIOS:
        assert s in SCENARIO_LABELS
        assert s in SCENARIO_DESCRIPTIONS
        assert len(SCENARIO_LABELS[s]) > 0
        assert len(SCENARIO_DESCRIPTIONS[s]) > 0


# -----------------------------------------------------------------------------
# Test 2 — get_scenario / set_scenario
# -----------------------------------------------------------------------------


def test_get_scenario_default_normal():
    """미설정 시 'NORMAL' 폴백."""
    from app.lib.demo import get_scenario

    assert get_scenario() == "NORMAL"


def test_set_scenario_updates_state():
    from app.lib.demo import get_scenario, set_scenario

    set_scenario("ANOMALY")
    assert get_scenario() == "ANOMALY"

    set_scenario("WARN")
    assert get_scenario() == "WARN"


def test_set_scenario_invalid_raises():
    from app.lib.demo import set_scenario

    with pytest.raises(ValueError):
        set_scenario("INVALID_SCENARIO")


# -----------------------------------------------------------------------------
# Test 3 — filter_samples_by_scenario
# -----------------------------------------------------------------------------


def _make_demo_result():
    """4건 데모: 0.10/0.35/0.55/0.85 — 정상/경고/이상/이상."""
    return pd.DataFrame(
        {
            "sample_id": [101, 202, 303, 404],
            "pred_proba": [0.10, 0.35, 0.55, 0.85],
            "pred_label": [0, 0, 1, 1],
        }
    )


def test_filter_normal_scenario():
    from app.lib.demo import filter_samples_by_scenario

    df = _make_demo_result()
    indices = filter_samples_by_scenario(df, scenario="NORMAL")
    assert indices == [0]  # 0.10만 < 0.30


def test_filter_warn_scenario():
    from app.lib.demo import filter_samples_by_scenario

    df = _make_demo_result()
    indices = filter_samples_by_scenario(df, scenario="WARN")
    assert indices == [1]  # 0.35만 ≥ 0.30 & < 0.50


def test_filter_anomaly_scenario():
    from app.lib.demo import filter_samples_by_scenario

    df = _make_demo_result()
    indices = filter_samples_by_scenario(df, scenario="ANOMALY")
    assert indices == [2, 3]  # 0.55, 0.85 ≥ 0.50


def test_filter_uses_get_scenario_when_none():
    from app.lib.demo import filter_samples_by_scenario, set_scenario

    df = _make_demo_result()
    set_scenario("ANOMALY")
    indices = filter_samples_by_scenario(df, scenario=None)
    assert indices == [2, 3]


def test_filter_missing_proba_column_returns_all():
    from app.lib.demo import filter_samples_by_scenario

    df = pd.DataFrame({"sample_id": [1, 2, 3]})  # pred_proba 없음
    indices = filter_samples_by_scenario(df, scenario="NORMAL")
    assert indices == [0, 1, 2]


def test_filter_empty_match_returns_all_fallback():
    """시나리오에 맞는 샘플 없으면 전체 폴백."""
    from app.lib.demo import filter_samples_by_scenario

    # 모두 정상 영역
    df = pd.DataFrame({"pred_proba": [0.01, 0.02, 0.03]})
    indices = filter_samples_by_scenario(df, scenario="ANOMALY")
    # 빈 결과 → 전체 폴백
    assert indices == [0, 1, 2]


# -----------------------------------------------------------------------------
# Test 4 — demo_sidebar 반환 시그니처 보존 (Critical Pitfall C-1)
# -----------------------------------------------------------------------------


def test_demo_sidebar_signature_unchanged():
    """demo_sidebar()는 여전히 bool 반환 — 호출처 5곳 무변경 보장.

    `from __future__ import annotations` 환경에서 annotation은 문자열 평가됨
    → typing.get_type_hints()로 실제 타입 resolve.
    """
    import typing

    from app.lib.demo import demo_sidebar

    hints = typing.get_type_hints(demo_sidebar)
    return_type = hints.get("return")
    assert return_type is bool, (
        f"demo_sidebar() return type must remain `bool`, got {return_type}"
    )
