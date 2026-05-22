"""작업 대시보드 컴포넌트 — KPI / Verdict / Numbered / Comparison (PR-24 + PR-27 dark mode fix).

참조 `team_comparison_dashboard_v0.1.html` 패턴 적용:
- 4열 KPI 그리드 (큰 숫자 + 색상 코딩)
- Verdict 박스 (.win/.warn/.bad 상태 배경)
- Numbered list (원형 배지 + 단계별 해설)
- Comparison table (색상 코딩 비교표)

PR-27 핫픽스:
- 모든 카드/박스 배경 #ffffff 강제 + 테두리 (Streamlit 다크 모드에서도 텍스트 가시성 확보)
- 텍스트 color: #0d1117 명시 (다크 배경에서 검정 텍스트 깨짐 방지)
- numbered_step HTML 들여쓰기 제거 → markdown 코드블록 오인 방지 (사용자 보고한 raw HTML 표시 문제)
"""

from __future__ import annotations

import streamlit as st


# PR-18 — Okabe-Ito 색맹 친화 팔레트 (viz.py와 통일)
_PALETTE = {
    "win": "#009E73",      # Bluish Green
    "warn": "#E69F00",     # Orange
    "bad": "#D55E00",      # Vermillion
    "info": "#0072B2",     # Blue
    "neutral": "#6e7681",  # Gray (보조)
    "accent": "#CC79A7",   # Reddish Purple
}


def kpi_card(
    label: str,
    value: str,
    delta: str = "",
    color: str = "info",
    icon: str = "",
) -> str:
    """4열 그리드용 KPI 카드 HTML — PR-27 다크 모드 호환 (배경 흰색 강제)."""
    color_hex = _PALETTE.get(color, _PALETTE["info"])
    delta_color = _PALETTE["win"] if not delta.startswith("-") else _PALETTE["bad"]
    delta_html = (
        f'<div style="font-size:13px;color:{delta_color};margin-top:6px;font-weight:600;">{delta}</div>'
        if delta else ""
    )
    icon_html = f'<div style="font-size:28px;margin-bottom:4px;">{icon}</div>' if icon else ""
    # 들여쓰기 제거 (markdown 코드블록 인식 방지)
    return (
        f'<div style="background:#ffffff;border-left:5px solid {color_hex};'
        f'border:1px solid #d0d7de;border-left-width:5px;padding:18px 22px;'
        f'border-radius:10px;height:100%;min-height:130px;box-shadow:0 2px 6px rgba(0,0,0,0.05);">'
        f'{icon_html}'
        f'<div style="font-size:13px;color:#6e7681;margin-bottom:6px;">{label}</div>'
        f'<div style="font-size:32px;font-weight:800;color:#0d1117;line-height:1.1;">{value}</div>'
        f'{delta_html}'
        f'</div>'
    )


def verdict_box(status: str, message: str) -> str:
    """상태별 배경색 박스 — PR-27 다크 모드에서도 가시성."""
    color_hex = _PALETTE.get(status, _PALETTE["info"])
    icon = {"win": "✅", "warn": "⚠️", "bad": "🚨"}.get(status, "ℹ️")
    return (
        f'<div style="padding:14px 20px;background:#ffffff;border:1px solid #d0d7de;'
        f'border-left:5px solid {color_hex};border-radius:8px;margin:8px 0;'
        f'font-size:15px;color:#0d1117;box-shadow:0 2px 6px rgba(0,0,0,0.05);">'
        f'<span style="font-size:18px;margin-right:8px;">{icon}</span>'
        f'{message}'
        f'</div>'
    )


def numbered_step(steps: list[str]) -> str:
    """원형 배지 + 단계별 해설 — PR-27 들여쓰기 제거 (markdown 코드블록 오인 fix)."""
    items_html = ""
    for i, step in enumerate(steps, 1):
        items_html += (
            f'<li style="margin-bottom:10px;display:flex;align-items:flex-start;gap:12px;'
            f'color:#0d1117;">'
            f'<span style="display:inline-flex;align-items:center;justify-content:center;'
            f'width:28px;height:28px;border-radius:50%;background:{_PALETTE["info"]};'
            f'color:#fff;font-weight:700;font-size:14px;flex-shrink:0;">{i}</span>'
            f'<span style="font-size:14px;color:#0d1117;line-height:1.5;">{step}</span>'
            f'</li>'
        )
    return (
        f'<ol style="list-style:none;padding:12px 16px;margin:8px 0;background:#ffffff;'
        f'border:1px solid #d0d7de;border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,0.05);">'
        f'{items_html}'
        f'</ol>'
    )


def comparison_table(
    rows: list[dict],
    headers: list[str],
    color_rule: str = "delta",
) -> str:
    """색상 코딩 비교표 — PR-27 다크 모드 호환 (한 줄 HTML)."""
    head = "".join(
        f'<th style="padding:10px 12px;text-align:left;background:{_PALETTE["info"]};'
        f'color:#fff;font-weight:600;">{h}</th>'
        for h in headers
    )
    body_rows = ""
    for row in rows:
        cells = ""
        for h in headers:
            val = row.get(h, "")
            color = "#0d1117"
            weight = 400
            if h == "변화" or h == "Δ":
                if str(val).startswith("+"):
                    color = _PALETTE["win"]
                    weight = 600
                elif str(val).startswith("-"):
                    color = _PALETTE["bad"]
                    weight = 600
            cells += (
                f'<td style="padding:10px 12px;color:{color};font-weight:{weight};">{val}</td>'
            )
        body_rows += f'<tr style="border-bottom:1px solid #d0d7de;background:#ffffff;">{cells}</tr>'
    return (
        f'<div style="background:#ffffff;border:1px solid #d0d7de;border-radius:8px;'
        f'overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,0.05);">'
        f'<table style="width:100%;border-collapse:collapse;font-size:14px;">'
        f'<thead><tr>{head}</tr></thead>'
        f'<tbody>{body_rows}</tbody>'
        f'</table></div>'
    )


def alert_gradient_card(title: str, message: str, severity: str = "warn") -> str:
    """진행 중 이상 알림 — PR-27 다크 모드 호환 (배경 흰색)."""
    color_hex = _PALETTE.get(severity, _PALETTE["warn"])
    return (
        f'<div style="background:#ffffff;border:1px solid #d0d7de;border-left:5px solid {color_hex};'
        f'padding:18px 24px;border-radius:10px;margin:12px 0;'
        f'box-shadow:0 2px 8px rgba(0,0,0,0.08);">'
        f'<div style="font-size:16px;font-weight:700;color:{color_hex};margin-bottom:6px;">{title}</div>'
        f'<div style="font-size:14px;color:#0d1117;line-height:1.5;">{message}</div>'
        f'</div>'
    )


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
