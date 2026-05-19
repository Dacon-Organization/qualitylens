"""공용 시각화 함수 — plotly 기반."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# === 3단계 위험 등급 (S-1) =================================================
# 기획서 약속: "정상/경고/위험 3단계 컬러 코딩 → 비전문가도 즉시 이상 인지"

WARN_THRESHOLD = 0.30
DANGER_THRESHOLD = 0.50


@dataclass(frozen=True)
class RiskTier:
    code: str  # "normal" | "warn" | "danger"
    label: str  # "정상" | "경고" | "위험"
    color: str  # hex
    emoji: str


TIER_NORMAL = RiskTier("normal", "정상", "#3fb950", "🟢")
TIER_WARN = RiskTier("warn", "경고", "#d29922", "🟡")
TIER_DANGER = RiskTier("danger", "위험", "#f85149", "🔴")


def risk_tier(proba: float) -> RiskTier:
    """이상 확률 → 3단계 등급. 기획서 평가 기준 1번 (즉시 인지)."""
    if proba >= DANGER_THRESHOLD:
        return TIER_DANGER
    if proba >= WARN_THRESHOLD:
        return TIER_WARN
    return TIER_NORMAL


# ==========================================================================


def gauge_proba(proba: float, threshold: float = DANGER_THRESHOLD) -> go.Figure:
    """이상 확률 게이지 — 3단계 컬러 구간 적용."""
    tier = risk_tier(proba)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=proba * 100,
            number={"suffix": "%", "valueformat": ".1f"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": tier.color},
                "steps": [
                    {"range": [0, WARN_THRESHOLD * 100], "color": "#1f2d22"},
                    {
                        "range": [WARN_THRESHOLD * 100, DANGER_THRESHOLD * 100],
                        "color": "#2d2820",
                    },
                    {"range": [DANGER_THRESHOLD * 100, 100], "color": "#2d1f24"},
                ],
                "threshold": {
                    "line": {"color": "white", "width": 2},
                    "thickness": 0.75,
                    "value": threshold * 100,
                },
            },
            title={"text": f"이상 확률 ({tier.emoji} {tier.label})"},
        )
    )
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def render_tier_badge(proba: float) -> str:
    """Streamlit markdown용 컬러 배지 HTML."""
    tier = risk_tier(proba)
    return (
        f'<div style="display:inline-block;padding:6px 16px;border-radius:20px;'
        f'background:{tier.color};color:white;font-weight:700;font-size:15px;">'
        f"{tier.emoji} {tier.label} · {proba*100:.1f}%"
        f"</div>"
    )


def shap_top_bar(top: pd.DataFrame, n: int = 15) -> go.Figure:
    df = top.head(n).iloc[::-1]
    fig = px.bar(
        df,
        x="mean_abs_shap",
        y="sensor",
        orientation="h",
        title=f"상위 {n} 기여 센서",
        color_discrete_sequence=["#58a6ff"],
    )
    fig.update_layout(height=420, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def proba_timeline(proba_series: pd.Series) -> go.Figure:
    """시계열 차트 — 3단계 컬러 구간 배경 + 임계값 라인."""
    df = pd.DataFrame(
        {"index": range(len(proba_series)), "proba": proba_series.values}
    )
    fig = px.line(df, x="index", y="proba", title="시간대별 이상 확률")

    # 3단계 컬러 구간 배경
    fig.add_hrect(
        y0=0, y1=WARN_THRESHOLD, fillcolor=TIER_NORMAL.color, opacity=0.08, line_width=0
    )
    fig.add_hrect(
        y0=WARN_THRESHOLD,
        y1=DANGER_THRESHOLD,
        fillcolor=TIER_WARN.color,
        opacity=0.10,
        line_width=0,
    )
    fig.add_hrect(
        y0=DANGER_THRESHOLD,
        y1=1.0,
        fillcolor=TIER_DANGER.color,
        opacity=0.10,
        line_width=0,
    )
    fig.add_hline(
        y=WARN_THRESHOLD, line_dash="dot", line_color=TIER_WARN.color, opacity=0.6
    )
    fig.add_hline(
        y=DANGER_THRESHOLD, line_dash="dash", line_color=TIER_DANGER.color, opacity=0.8
    )
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20))
    return fig
