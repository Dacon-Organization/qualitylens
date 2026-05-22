"""신규 시각화 모듈 (PR-22) — 5페이지 P0/P1 차트 확장.

기존 viz.py는 변경 최소화. 신규 차트는 모두 이 모듈에 통합.

함수 목록:
- violin_normal_anomaly: 정상/이상 분포 비교 (P2)
- correlation_heatmap: 상관 행렬 히트맵 (P2)
- boxplot_violations: 위반 센서 분포 박스플롯 (P3)
- roi_bar: ROI 막대 (P3 — 예상 절감)
- cumulative_trend: 누적 추세 라인 (P4)
- confusion_matrix: 혼동행렬 (P4)
- pareto_cumulative: Pareto 누적 곡선 (P5 보강)
- kpi_summary_chart: 24h 타임라인 + Top5 (메인)
- top_violations_bar: 가장 자주 위반하는 센서 Top N (메인)

설계 원칙:
- 모든 차트 plotly 기반, 한국어 라벨
- 색맹 친화 색상 (Okabe-Ito 일부)
- 큰 카드(메인) vs 작은 카드(다른 페이지) 일관 layout
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# === 색상 팔레트 (Okabe-Ito 기반 — PR-18 대비) ============================
PALETTE = {
    "normal": "#3fb950",      # 초록
    "warn": "#d29922",        # 주황
    "danger": "#f85149",      # 빨강
    "info": "#1f6feb",        # 파랑
    "neutral": "#6e7681",     # 회색
    "accent": "#8957e5",      # 보라
    "highlight": "#e8c547",   # 노랑
}


# === P2 — 정상/이상 분포 비교 (Violin) =====================================
def violin_normal_anomaly(
    values_normal: pd.Series,
    values_anomaly: pd.Series,
    sensor_name: str = "센서",
) -> go.Figure:
    """정상 샘플 vs 이상 샘플의 분포 비교.

    "이 센서가 이상일 때 vs 정상일 때 어떻게 다른가?" 비전문가용 직관 차트.
    """
    fig = go.Figure()
    fig.add_trace(
        go.Violin(
            y=values_normal,
            name="정상 (PASS)",
            box_visible=True,
            meanline_visible=True,
            line_color=PALETTE["normal"],
            fillcolor=PALETTE["normal"],
            opacity=0.6,
            side="negative",
        )
    )
    fig.add_trace(
        go.Violin(
            y=values_anomaly,
            name="이상 (FAIL)",
            box_visible=True,
            meanline_visible=True,
            line_color=PALETTE["danger"],
            fillcolor=PALETTE["danger"],
            opacity=0.6,
            side="positive",
        )
    )
    fig.update_layout(
        title=f"{sensor_name} — 정상 vs 이상 분포 비교",
        yaxis_title=f"{sensor_name} 값",
        height=400,
        margin=dict(l=40, r=40, t=60, b=40),
        violinmode="overlay",
        showlegend=True,
    )
    return fig


# === P2 — 상관 행렬 히트맵 ================================================
def correlation_heatmap(
    df: pd.DataFrame,
    title: str = "상위 N 센서 상관 행렬",
) -> go.Figure:
    """주요 센서 간 상관관계 — 같이 움직이는 센서 패턴 감지."""
    corr = df.corr()
    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.index,
            colorscale="RdBu_r",
            zmin=-1,
            zmax=1,
            colorbar=dict(title="상관계수"),
            hovertemplate=(
                "<b>%{y}</b> ↔ <b>%{x}</b><br>"
                "상관계수: %{z:.3f}<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title=title,
        height=500,
        margin=dict(l=80, r=40, t=60, b=80),
        xaxis=dict(tickangle=-45),
    )
    return fig


# === P3 — 위반 센서 박스플롯 ==============================================
def boxplot_violations(
    violation_df: pd.DataFrame,
    sensor_col: str = "sensor",
    deviation_col: str = "deviation",
    title: str = "위반 센서 편차 분포",
) -> go.Figure:
    """우선순위 정렬된 위반 센서별 σ 편차 시각화."""
    if violation_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="✅ 위반 센서 없음 — 정상 운영 중",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color=PALETTE["normal"]),
        )
        fig.update_layout(height=350)
        return fig

    df_sorted = violation_df.sort_values(deviation_col, ascending=True).tail(10)
    colors = [
        PALETTE["danger"] if d > 4 else PALETTE["warn"] if d > 3 else PALETTE["info"]
        for d in df_sorted[deviation_col]
    ]
    fig = go.Figure(
        go.Bar(
            y=df_sorted[sensor_col],
            x=df_sorted[deviation_col],
            orientation="h",
            marker=dict(color=colors),
            hovertemplate="<b>%{y}</b><br>편차: %{x:.2f}σ<extra></extra>",
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title="편차 (σ)",
        yaxis_title="센서",
        height=400,
        margin=dict(l=120, r=40, t=60, b=40),
    )
    fig.add_vline(x=3, line_dash="dash", line_color=PALETTE["warn"], annotation_text="3σ")
    fig.add_vline(x=4, line_dash="dash", line_color=PALETTE["danger"], annotation_text="4σ")
    return fig


# === P3 — ROI 막대 차트 ===================================================
def roi_bar(
    sensors: list[str],
    expected_savings_kr: list[float],
    title: str = "센서별 예상 절감액 (조치 시)",
) -> go.Figure:
    """조치 시 예상 비용 절감 (ROI) — 만원 단위."""
    fig = go.Figure(
        go.Bar(
            x=sensors,
            y=expected_savings_kr,
            marker=dict(color=PALETTE["info"]),
            text=[f"{v:,.0f}만원" for v in expected_savings_kr],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>예상 절감: %{y:,.0f}만원<extra></extra>",
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title="센서",
        yaxis_title="예상 절감 (만원)",
        height=380,
        margin=dict(l=60, r=40, t=60, b=80),
    )
    return fig


# === P4 — 누적 추세 라인 ==================================================
def cumulative_trend(
    df: pd.DataFrame,
    timestamp_col: str = "timestamp",
    proba_col: str = "pred_proba",
    title: str = "시간대별 이상률 누적 추세",
) -> go.Figure:
    """timestamp 기반 누적 이상 건수 + 평균 이상 확률 듀얼 축."""
    if timestamp_col not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text=f"timestamp 컬럼 없음 — 누적 추세 생략",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=PALETTE["neutral"]),
        )
        return fig

    df_sorted = df.sort_values(timestamp_col).copy()
    df_sorted["is_anomaly"] = (df_sorted[proba_col] >= 0.5).astype(int)
    df_sorted["cumulative_anomaly"] = df_sorted["is_anomaly"].cumsum()
    df_sorted["rolling_proba"] = df_sorted[proba_col].rolling(window=5, min_periods=1).mean()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=df_sorted[timestamp_col],
            y=df_sorted["cumulative_anomaly"],
            name="누적 이상 건수",
            line=dict(color=PALETTE["danger"], width=2.5),
            mode="lines",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=df_sorted[timestamp_col],
            y=df_sorted["rolling_proba"],
            name="이상 확률 (5점 이동평균)",
            line=dict(color=PALETTE["info"], width=2, dash="dot"),
            mode="lines",
        ),
        secondary_y=True,
    )
    fig.update_layout(
        title=title,
        height=380,
        margin=dict(l=60, r=60, t=60, b=40),
        hovermode="x unified",
    )
    fig.update_xaxes(title="시각")
    fig.update_yaxes(title="누적 이상 건수", secondary_y=False)
    fig.update_yaxes(title="이상 확률", secondary_y=True, range=[0, 1])
    return fig


# === P4 — 혼동행렬 ========================================================
def confusion_matrix(
    y_true: pd.Series | np.ndarray,
    y_pred: pd.Series | np.ndarray,
    title: str = "혼동행렬 (실제 vs 예측)",
) -> go.Figure:
    """이진 분류 confusion matrix — TP/FP/TN/FN 한눈에."""
    if hasattr(y_true, "to_numpy"):
        y_true = y_true.to_numpy()
    if hasattr(y_pred, "to_numpy"):
        y_pred = y_pred.to_numpy()
    tn = int(((y_true == 0) & (y_pred == 0)).sum())
    fp = int(((y_true == 0) & (y_pred == 1)).sum())
    fn = int(((y_true == 1) & (y_pred == 0)).sum())
    tp = int(((y_true == 1) & (y_pred == 1)).sum())

    z = [[tn, fp], [fn, tp]]
    text = [
        [f"TN: {tn}<br>(정확)", f"FP: {fp}<br>(오탐)"],
        [f"FN: {fn}<br>(놓침)", f"TP: {tp}<br>(정확)"],
    ]
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=["예측 정상", "예측 이상"],
            y=["실제 정상", "실제 이상"],
            text=text,
            texttemplate="%{text}",
            textfont={"size": 14},
            colorscale=[[0, "#1f6feb20"], [1, PALETTE["info"]]],
            showscale=False,
        )
    )
    total = tn + fp + fn + tp
    accuracy = (tn + tp) / total * 100 if total else 0
    fig.update_layout(
        title=f"{title} · 정확도 {accuracy:.1f}%",
        height=380,
        margin=dict(l=60, r=40, t=60, b=40),
    )
    return fig


# === P5 — Pareto 누적 곡선 (보강) =========================================
def pareto_cumulative(
    df: pd.DataFrame,
    category_col: str = "sensor",
    value_col: str = "mean_abs_shap",
    title: str = "Pareto 분석 — 80/20 누적 곡선",
) -> go.Figure:
    """막대 + 누적 % 라인 + 80% 기준선."""
    df_sorted = df.sort_values(value_col, ascending=False).copy()
    df_sorted["cumulative_pct"] = (
        df_sorted[value_col].cumsum() / df_sorted[value_col].sum() * 100
    )

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=df_sorted[category_col],
            y=df_sorted[value_col],
            name="기여도",
            marker=dict(color=PALETTE["info"]),
            hovertemplate="<b>%{x}</b><br>기여도: %{y:.4f}<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=df_sorted[category_col],
            y=df_sorted["cumulative_pct"],
            name="누적 %",
            mode="lines+markers",
            line=dict(color=PALETTE["danger"], width=2.5),
            marker=dict(size=8),
            hovertemplate="<b>%{x}</b><br>누적: %{y:.1f}%<extra></extra>",
        ),
        secondary_y=True,
    )
    # 80% 기준선
    fig.add_hline(
        y=80, line_dash="dash", line_color=PALETTE["warn"],
        secondary_y=True,
        annotation_text="80% 기준선",
    )
    fig.update_layout(
        title=title,
        height=420,
        margin=dict(l=60, r=60, t=60, b=80),
        hovermode="x unified",
    )
    fig.update_xaxes(title="센서 (영향도 순)", tickangle=-45)
    fig.update_yaxes(title="평균 |SHAP|", secondary_y=False)
    fig.update_yaxes(title="누적 (%)", range=[0, 105], secondary_y=True)

    # 80% 달성에 필요한 센서 수 계산
    n_for_80 = int((df_sorted["cumulative_pct"] <= 80).sum()) + 1
    fig.add_annotation(
        x=0.02,
        y=0.95,
        xref="paper",
        yref="paper",
        text=f"📌 상위 <b>{n_for_80}개</b> 센서가 전체 영향도의 80% 차지",
        showarrow=False,
        font=dict(size=12, color=PALETTE["danger"]),
        bgcolor="#fff",
        bordercolor=PALETTE["warn"],
        borderwidth=1,
        borderpad=4,
    )
    return fig


# === 메인 — 24h 타임라인 + Top5 위반 (KPI 보강) ============================
def top_violations_bar(
    violation_counts: dict[str, int],
    title: str = "가장 자주 위반하는 센서 Top 5",
) -> go.Figure:
    """누적 위반 횟수 기준 상위 N개 센서."""
    if not violation_counts:
        fig = go.Figure()
        fig.add_annotation(
            text="아직 위반 이력 없음",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=PALETTE["normal"]),
        )
        fig.update_layout(height=280)
        return fig

    sorted_items = sorted(violation_counts.items(), key=lambda kv: kv[1], reverse=True)[:5]
    sensors = [s for s, _ in sorted_items]
    counts = [c for _, c in sorted_items]
    fig = go.Figure(
        go.Bar(
            x=counts,
            y=sensors,
            orientation="h",
            marker=dict(color=PALETTE["danger"]),
            text=counts,
            textposition="outside",
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title="위반 횟수",
        yaxis=dict(autorange="reversed"),
        height=280,
        margin=dict(l=100, r=40, t=60, b=40),
    )
    return fig


# === PR-17 — Cpk 공정 능력 게이지 ==========================================
def cpk_gauge(
    cpk: float,
    cp: float | None = None,
    title: str = "공정 능력 지수 (Cpk)",
) -> go.Figure:
    """Cpk 게이지 — 4단계 컬러 구간 (부적합 / 개선 / 양호 / 우수).

    Parameters
    ----------
    cpk : 실제 공정 능력 (편향 반영)
    cp : 잠재 능력 (옵션, 부제목에 표시)
    """
    # 색상 (Okabe-Ito 호환)
    if cpk < 1.0:
        bar_color = PALETTE["danger"]
        tier = "🔴 부적합"
    elif cpk < 1.33:
        bar_color = PALETTE["warn"]
        tier = "🟡 개선 필요"
    elif cpk < 1.67:
        bar_color = PALETTE["normal"]
        tier = "🟢 양호"
    else:
        bar_color = PALETTE["info"]
        tier = "🌟 우수"

    subtitle = f"<br><span style='font-size:14px;color:#6e7681'>{tier}"
    if cp is not None:
        subtitle += f" · Cp={cp:.2f}"
    subtitle += "</span>"

    # 게이지 범위 0~2.5 (제조 실무 통상 범위)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=cpk,
            number={"valueformat": ".2f", "font": {"size": 36}},
            gauge={
                "axis": {"range": [0, 2.5], "tickvals": [0, 1.0, 1.33, 1.67, 2.5]},
                "bar": {"color": bar_color, "thickness": 0.7},
                "steps": [
                    {"range": [0, 1.0], "color": "#ffe0e0"},
                    {"range": [1.0, 1.33], "color": "#fff4d6"},
                    {"range": [1.33, 1.67], "color": "#dfffdb"},
                    {"range": [1.67, 2.5], "color": "#d6e8ff"},
                ],
                "threshold": {
                    "line": {"color": PALETTE["danger"], "width": 3},
                    "thickness": 0.75,
                    "value": 1.33,  # AIAG SPC 표준 기준선
                },
            },
            title={"text": title + subtitle, "font": {"size": 16}},
        )
    )
    fig.update_layout(
        height=320,
        margin=dict(l=20, r=20, t=80, b=20),
        paper_bgcolor="white",
    )
    return fig


def cpk_card_html(
    cpk: float,
    cp: float,
    tier_label: str,
    interpretation: str,
    color: str = "#3fb950",
) -> str:
    """Cpk 결과를 HTML 카드로 — st.markdown(html, unsafe_allow_html=True)."""
    return f"""
    <div style="
        background:#ffffff;
        border:1px solid #d0d7de;
        border-left: 5px solid {color};
        padding: 16px 20px;
        border-radius: 8px;
        color:#0d1117;
    ">
        <div style="font-size:12px;color:#6e7681;margin-bottom:6px;">공정 능력 평가</div>
        <div style="font-size:28px;font-weight:800;color:#0d1117;">
            Cpk = {cpk:.2f}
            <span style="font-size:14px;color:#6e7681;font-weight:400;"> · Cp = {cp:.2f}</span>
        </div>
        <div style="font-size:14px;color:{color};font-weight:700;margin-top:6px;">
            {tier_label}
        </div>
        <div style="font-size:13px;color:#0d1117;margin-top:8px;line-height:1.5;">
            {interpretation}
        </div>
    </div>
    """


# === KPI 카드 HTML (메인 + 종합 대시보드 공용) =============================
def kpi_card_html(
    label: str,
    value: str,
    delta: str = "",
    color: str = "info",
    icon: str = "",
) -> str:
    """4열 그리드용 KPI 카드 HTML — st.markdown(html, unsafe_allow_html=True)."""
    color_hex = PALETTE.get(color, PALETTE["info"])
    delta_html = (
        f'<div style="font-size:12px;color:{PALETTE["normal"]};margin-top:4px;">{delta}</div>'
        if delta
        else ""
    )
    icon_html = f'<span style="font-size:24px;">{icon}</span>' if icon else ""
    return f"""
    <div style="
        background: linear-gradient(135deg, {color_hex}15, {color_hex}05);
        border-left: 5px solid {color_hex};
        padding: 16px 20px;
        border-radius: 8px;
        height: 100%;
    ">
        {icon_html}
        <div style="font-size:12px;color:#6e7681;margin-bottom:4px;">{label}</div>
        <div style="font-size:28px;font-weight:800;color:#0d1117;">{value}</div>
        {delta_html}
    </div>
    """
