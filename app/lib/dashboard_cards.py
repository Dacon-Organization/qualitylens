"""작업 대시보드 컴포넌트 — KPI / Verdict / Numbered / Comparison (PR-24).

참조 `team_comparison_dashboard_v0.1.html` 패턴 적용:
- 4열 KPI 그리드 (큰 숫자 + 색상 코딩)
- Verdict 박스 (.win/.warn/.bad 상태 배경)
- Numbered list (원형 배지 + 단계별 해설)
- Comparison table (색상 코딩 비교표)

사용자 처방 Step 11+12 (이력 의미 + 비즈니스 임팩트) 핵심 모듈.
"""

from __future__ import annotations

import streamlit as st


_PALETTE = {
    "win": "#3fb950",
    "warn": "#d29922",
    "bad": "#f85149",
    "info": "#1f6feb",
    "neutral": "#6e7681",
    "accent": "#8957e5",
}


def kpi_card(
    label: str,
    value: str,
    delta: str = "",
    color: str = "info",
    icon: str = "",
) -> str:
    """4열 그리드용 KPI 카드 HTML."""
    color_hex = _PALETTE.get(color, _PALETTE["info"])
    delta_color = _PALETTE["win"] if not delta.startswith("-") else _PALETTE["bad"]
    delta_html = (
        f'<div style="font-size:13px;color:{delta_color};margin-top:6px;font-weight:600;">{delta}</div>'
        if delta
        else ""
    )
    icon_html = f'<div style="font-size:28px;margin-bottom:4px;">{icon}</div>' if icon else ""
    return f"""
    <div style="
        background: linear-gradient(135deg, {color_hex}18, {color_hex}05);
        border-left: 5px solid {color_hex};
        padding: 18px 22px;
        border-radius: 10px;
        height: 100%;
        min-height: 130px;
    ">
        {icon_html}
        <div style="font-size:13px;color:#6e7681;margin-bottom:6px;">{label}</div>
        <div style="font-size:32px;font-weight:800;color:#0d1117;line-height:1.1;">{value}</div>
        {delta_html}
    </div>
    """


def verdict_box(status: str, message: str) -> str:
    """상태별 배경색 박스 — .win/.warn/.bad."""
    color_hex = _PALETTE.get(status, _PALETTE["info"])
    icon = {"win": "✅", "warn": "⚠️", "bad": "🚨"}.get(status, "ℹ️")
    return f"""
    <div style="
        padding: 14px 20px;
        background: {color_hex}20;
        border-left: 5px solid {color_hex};
        border-radius: 8px;
        margin: 8px 0;
        font-size: 15px;
        color: #0d1117;
    ">
        <span style="font-size:18px;margin-right:8px;">{icon}</span>
        {message}
    </div>
    """


def numbered_step(steps: list[str]) -> str:
    """원형 배지 + 단계별 해설 numbered list."""
    items = []
    for i, step in enumerate(steps, 1):
        items.append(
            f"""
            <li style="margin-bottom:10px;display:flex;align-items:flex-start;gap:12px;">
                <span style="
                    display:inline-flex;
                    align-items:center;
                    justify-content:center;
                    width:28px;
                    height:28px;
                    border-radius:50%;
                    background:{_PALETTE['info']};
                    color:#fff;
                    font-weight:700;
                    font-size:14px;
                    flex-shrink:0;
                ">{i}</span>
                <span style="font-size:14px;color:#0d1117;line-height:1.5;">{step}</span>
            </li>
            """
        )
    return f'<ol style="list-style:none;padding:0;margin:8px 0;">{"".join(items)}</ol>'


def comparison_table(
    rows: list[dict],
    headers: list[str],
    color_rule: str = "delta",
) -> str:
    """색상 코딩 비교표 HTML.

    rows 예시: [{"label": "이번주", "value": 42, "prev": 38, "delta": "+10.5%"}, ...]
    color_rule: "delta" — delta 값 부호로 색 결정 (양수 초록, 음수 빨강)
    """
    head = "".join(
        f'<th style="padding:10px 12px;text-align:left;background:#1f6feb;color:#fff;font-weight:600;">{h}</th>'
        for h in headers
    )
    body_rows = []
    for row in rows:
        cells = []
        for h in headers:
            val = row.get(h, "")
            color = "#0d1117"
            if h == "변화" or h == "Δ":
                if str(val).startswith("+"):
                    color = _PALETTE["win"]
                elif str(val).startswith("-"):
                    color = _PALETTE["bad"]
            cells.append(
                f'<td style="padding:10px 12px;color:{color};font-weight:{600 if h in ("변화", "Δ") else 400};">{val}</td>'
            )
        body_rows.append(f'<tr style="border-bottom:1px solid #d0d7de;">{"".join(cells)}</tr>')
    return f"""
    <table style="width:100%;border-collapse:collapse;font-size:14px;">
        <thead><tr>{head}</tr></thead>
        <tbody>{"".join(body_rows)}</tbody>
    </table>
    """


def alert_gradient_card(title: str, message: str, severity: str = "warn") -> str:
    """진행 중 이상에 대한 gradient 배경 카드 (참조 dashboard 패턴)."""
    color_hex = _PALETTE.get(severity, _PALETTE["warn"])
    return f"""
    <div style="
        background: linear-gradient(135deg, {color_hex}28, #ffffff);
        border-left: 5px solid {color_hex};
        padding: 18px 24px;
        border-radius: 10px;
        margin: 12px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    ">
        <div style="font-size:16px;font-weight:700;color:{color_hex};margin-bottom:6px;">{title}</div>
        <div style="font-size:14px;color:#0d1117;line-height:1.5;">{message}</div>
    </div>
    """


def render_kpi_grid(cards: list[dict]) -> None:
    """KPI 4열 그리드 렌더 (Streamlit 헬퍼)."""
    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        with col:
            st.markdown(
                kpi_card(
                    label=card["label"],
                    value=card["value"],
                    delta=card.get("delta", ""),
                    color=card.get("color", "info"),
                    icon=card.get("icon", ""),
                ),
                unsafe_allow_html=True,
            )
