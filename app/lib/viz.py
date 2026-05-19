"""공용 시각화 함수 — plotly 기반."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def gauge_proba(proba: float, threshold: float = 0.5) -> go.Figure:
    """이상 확률을 게이지 차트로."""
    color = "#ff7b72" if proba >= threshold else "#7ee787"
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=proba * 100,
            number={"suffix": "%", "valueformat": ".1f"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": color},
                "steps": [
                    {"range": [0, threshold * 100], "color": "#1f2630"},
                    {"range": [threshold * 100, 100], "color": "#2d1f24"},
                ],
                "threshold": {
                    "line": {"color": "white", "width": 2},
                    "thickness": 0.75,
                    "value": threshold * 100,
                },
            },
            title={"text": "이상 확률"},
        )
    )
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
    return fig


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
    df = pd.DataFrame(
        {"index": range(len(proba_series)), "proba": proba_series.values}
    )
    fig = px.line(df, x="index", y="proba", title="시간대별 이상 확률")
    fig.add_hline(y=0.5, line_dash="dash", line_color="orange")
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20))
    return fig
