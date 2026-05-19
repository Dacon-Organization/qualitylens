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


# === SHAP Waterfall + Dependence (S-2) =====================================
# 기획서 약속 G2: "글로벌 피처 중요도 + 개별 Waterfall + Dependence Plot"
# plotly 직접 구현 — shap.plots는 matplotlib 의존이라 Streamlit Cloud 호환성 ↓


def shap_waterfall(
    features: list[str],
    shap_values: list[float],
    base_value: float,
    sample_values: list[float] | None = None,
) -> go.Figure:
    """plotly waterfall — base_value → 누적 SHAP → 최종 logit.

    Args:
        features: 표시할 피처 이름 (절댓값 큰 순으로 미리 정렬 권장)
        shap_values: 각 피처의 SHAP value (부호 유지)
        base_value: 모델 expected_value
        sample_values: 피처별 원본 값 (라벨에 표시, 옵션)
    """
    # 절댓값 큰 순으로 정렬 → 영향력이 큰 피처가 위쪽
    order = sorted(range(len(features)), key=lambda i: abs(shap_values[i]), reverse=True)
    features = [features[i] for i in order]
    shap_values = [shap_values[i] for i in order]
    if sample_values is not None:
        sample_values = [sample_values[i] for i in order]

    final_value = base_value + sum(shap_values)

    # waterfall 라벨: 센서명 + (실제값) — 길이 제한
    labels = []
    for i, f in enumerate(features):
        if sample_values is not None:
            labels.append(f"{f}<br><span style='font-size:11px;color:#8b949e'>값={sample_values[i]:+.2f}</span>")
        else:
            labels.append(f)

    x_labels = ["base"] + labels + ["최종"]
    measures = ["absolute"] + ["relative"] * len(shap_values) + ["total"]
    y_values = [base_value] + shap_values + [final_value]

    fig = go.Figure(
        go.Waterfall(
            x=x_labels,
            measure=measures,
            y=y_values,
            text=[f"{v:+.3f}" for v in y_values],
            textposition="outside",
            connector={"line": {"color": "#30363d"}},
            increasing={"marker": {"color": "#f85149"}},  # 양수 = 이상 확률 ↑ = 빨강
            decreasing={"marker": {"color": "#3fb950"}},  # 음수 = 정상 확률 ↑ = 녹색
            totals={"marker": {"color": "#58a6ff"}},
        )
    )
    fig.update_layout(
        title="SHAP Waterfall — base → 누적 → 최종",
        height=480,
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=80),
        xaxis_tickangle=-30,
        yaxis_title="logit (SHAP 누적)",
    )
    return fig


def shap_dependence(
    sensor: str,
    feature_values: pd.Series,
    shap_values_for_sensor: pd.Series,
    highlight_sample_id: int | None = None,
) -> go.Figure:
    """plotly dependence plot — 피처값 vs SHAP value 산점도."""
    df = pd.DataFrame(
        {
            "value": feature_values.values,
            "shap": shap_values_for_sensor.values,
            "sample_id": feature_values.index,
        }
    )
    fig = px.scatter(
        df,
        x="value",
        y="shap",
        color="shap",
        color_continuous_scale=["#3fb950", "#1f2630", "#f85149"],
        color_continuous_midpoint=0,
        title=f"Dependence Plot — {sensor} (피처값 ↔ SHAP)",
        hover_data=["sample_id"],
    )
    fig.add_hline(y=0, line_dash="dash", line_color="#8b949e", opacity=0.4)
    if highlight_sample_id is not None and highlight_sample_id in df["sample_id"].values:
        row = df[df["sample_id"] == highlight_sample_id].iloc[0]
        fig.add_trace(
            go.Scatter(
                x=[row["value"]],
                y=[row["shap"]],
                mode="markers",
                marker=dict(size=18, color="#d2a8ff", line=dict(color="white", width=2)),
                name=f"샘플 #{highlight_sample_id}",
                showlegend=True,
            )
        )
    fig.update_layout(
        height=380,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title=f"{sensor} 값 (스케일링됨)",
        yaxis_title="SHAP value",
    )
    return fig


# ==========================================================================


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
