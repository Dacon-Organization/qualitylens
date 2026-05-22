"""PR-18 단위 테스트 — 색맹 친화 UI (Okabe-Ito).

검증 8건:
1. TIER 색상값이 Okabe-Ito 표준 hex
2. TIER에 plotly marker_symbol 존재
3. render_tier_badge에 기호(●▲■) + 텍스트 라벨 포함
4. risk_tier() 임계값 분기 정확성 (정상/경고/위험)
5. dashboard_cards _PALETTE 색상 통일
6. viz_advanced PALETTE 색상 통일
7. 배지에 두꺼운 테두리 (border) 포함
8. OKABE_ITO 8색 모두 정의
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from app.lib.viz import (  # noqa: E402
    DANGER_THRESHOLD,
    OKABE_ITO,
    TIER_DANGER,
    TIER_NORMAL,
    TIER_WARN,
    WARN_THRESHOLD,
    render_tier_badge,
    risk_tier,
)


# -----------------------------------------------------------------------------
# Test 1 — Okabe-Ito 표준 hex 사용
# -----------------------------------------------------------------------------


def test_tier_colors_are_okabe_ito():
    """3단계 TIER 색상이 Okabe-Ito 표준 팔레트에서 선택됨."""
    assert TIER_NORMAL.color == "#009E73"  # Bluish Green
    assert TIER_WARN.color == "#E69F00"     # Orange
    assert TIER_DANGER.color == "#D55E00"   # Vermillion


def test_okabe_ito_palette_complete():
    """Okabe-Ito 8색 모두 정의."""
    expected_keys = {
        "black", "orange", "sky_blue", "bluish_green",
        "yellow", "blue", "vermillion", "reddish_purple",
    }
    assert set(OKABE_ITO.keys()) >= expected_keys
    # 모두 유효한 hex
    hex_pattern = re.compile(r"^#[0-9A-Fa-f]{6}$")
    for name, color in OKABE_ITO.items():
        assert hex_pattern.match(color), f"{name}={color} is not valid hex"


# -----------------------------------------------------------------------------
# Test 2 — Plotly marker_symbol 정의
# -----------------------------------------------------------------------------


def test_tier_has_plotly_marker():
    """각 TIER에 plotly marker_symbol 존재 (색맹 사용자용 형태 구분)."""
    assert TIER_NORMAL.plotly_marker == "circle"
    assert TIER_WARN.plotly_marker == "triangle-up"
    assert TIER_DANGER.plotly_marker == "square"


def test_tier_has_geometric_symbol():
    """각 TIER에 텍스트 기호 (●▲■) 존재."""
    assert TIER_NORMAL.symbol == "●"
    assert TIER_WARN.symbol == "▲"
    assert TIER_DANGER.symbol == "■"


# -----------------------------------------------------------------------------
# Test 3 — render_tier_badge: 색상 외 중복 정보 전달
# -----------------------------------------------------------------------------


def test_badge_includes_symbol_and_text():
    """배지 HTML에 기호 + 한글 라벨 + 이모지 모두 포함."""
    html = render_tier_badge(0.7)  # 위험 영역
    assert "■" in html, "기하 기호 ■ 필요"
    assert "위험" in html, "한글 라벨 필요"
    assert "🔴" in html, "이모지 필요"
    # 색맹 친화 핵심: 색에만 의존하지 않음 → 형태 + 텍스트 둘 다


def test_badge_has_thick_border():
    """배지에 두꺼운 테두리 (border 3px) 존재 — 형태 식별 강화."""
    html = render_tier_badge(0.4)
    assert "border:3px" in html


@pytest.mark.parametrize(
    "proba,expected_symbol,expected_label",
    [
        (0.1, "●", "정상"),
        (0.35, "▲", "경고"),
        (0.6, "■", "위험"),
    ],
)
def test_badge_matches_tier(proba, expected_symbol, expected_label):
    """proba 값별 배지에 올바른 기호 + 라벨 매핑."""
    html = render_tier_badge(proba)
    assert expected_symbol in html
    assert expected_label in html


# -----------------------------------------------------------------------------
# Test 4 — risk_tier 임계값 분기
# -----------------------------------------------------------------------------


def test_risk_tier_thresholds():
    """임계값 경계 정확성."""
    assert risk_tier(0.0) == TIER_NORMAL
    assert risk_tier(WARN_THRESHOLD - 0.01) == TIER_NORMAL
    assert risk_tier(WARN_THRESHOLD) == TIER_WARN
    assert risk_tier(DANGER_THRESHOLD - 0.01) == TIER_WARN
    assert risk_tier(DANGER_THRESHOLD) == TIER_DANGER
    assert risk_tier(1.0) == TIER_DANGER


# -----------------------------------------------------------------------------
# Test 5 — dashboard_cards _PALETTE 통일
# -----------------------------------------------------------------------------


def test_dashboard_palette_okabe_ito():
    from app.lib.dashboard_cards import _PALETTE

    assert _PALETTE["win"] == "#009E73"
    assert _PALETTE["warn"] == "#E69F00"
    assert _PALETTE["bad"] == "#D55E00"
    assert _PALETTE["info"] == "#0072B2"


# -----------------------------------------------------------------------------
# Test 6 — viz_advanced PALETTE 통일
# -----------------------------------------------------------------------------


def test_viz_advanced_palette_okabe_ito():
    from app.lib.viz_advanced import PALETTE

    assert PALETTE["normal"] == "#009E73"
    assert PALETTE["warn"] == "#E69F00"
    assert PALETTE["danger"] == "#D55E00"
    assert PALETTE["info"] == "#0072B2"
