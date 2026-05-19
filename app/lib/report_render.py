"""단계별 HTML 보고서 자동 생성 헬퍼.

각 스크립트(``01_preprocess.py`` 등)의 마지막에 다음 한 줄을 호출하면
``docs/reports/0X_<stage>.html`` 이 생성된다::

    from app.lib.report_render import write, build_index
    write("preprocessing", source=SOURCE, sections=[...])

각 section 은 dict::

    {"title": "1. 데이터 형상", "body_html": "<table>...</table>"}

plotly 그래프 임베드 헬퍼:
    embed_plotly(fig) -> str  # <div> + JS 초기화 블록 반환
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Sequence
from zoneinfo import ZoneInfo

from .fonts import html_font_face_css

ROOT = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = ROOT / "docs" / "reports"
VENDOR_DIR = ROOT / "assets" / "vendor"
KST = ZoneInfo("Asia/Seoul")

STAGES = {
    "preprocessing": ("01", "T1 전처리"),
    "training": ("02", "T2 모델 학습"),
    "shap": ("03", "T3 SHAP 분석"),
    "compare": ("04", "real vs dummy 비교"),
    "playwright_qa": ("05", "Playwright E2E 검증"),
}


def _plotly_script_tag() -> str:
    """오프라인 폴백: 로컬 미러가 있으면 상대경로, 없으면 CDN."""
    local = VENDOR_DIR / "plotly.min.js"
    if local.exists():
        # docs/reports/X.html → ../../assets/vendor/plotly.min.js
        return '<script src="../../assets/vendor/plotly.min.js"></script>'
    return '<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>'


def embed_plotly(fig, div_id: str | None = None) -> str:
    """plotly figure 를 단독 <div> + 초기화 JS 로 변환."""
    import plotly

    div_id = div_id or f"plot_{id(fig)}"
    fig_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return f"""
<div id="{div_id}" style="width:100%;height:480px;"></div>
<script>
  Plotly.newPlot("{div_id}", {fig_json}.data, {fig_json}.layout, {{responsive: true}});
</script>"""


def _html_template(title: str, source: str, sections_html: str) -> str:
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    badge_color = "#1e7c3a" if source == "real" else "#c89400"
    badge_text = "🟢 real (UCI SECOM)" if source == "real" else "🟡 dummy (폴백)"
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>QualityLens · {title}</title>
  {_plotly_script_tag()}
  <style>
    {html_font_face_css()}
    body {{ max-width: 1080px; margin: 32px auto; padding: 0 24px; color: #1f2328; }}
    header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #d0d7de; padding-bottom: 12px; }}
    h1 {{ margin: 0; font-size: 22px; }}
    .badge {{ background: {badge_color}; color: white; padding: 6px 12px; border-radius: 6px; font-size: 12px; }}
    .meta {{ color: #656d76; font-size: 13px; }}
    .section {{ margin: 28px 0; }}
    .section h2 {{ font-size: 18px; border-bottom: 1px solid #eaeef2; padding-bottom: 6px; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    th, td {{ border: 1px solid #d0d7de; padding: 6px 10px; text-align: left; }}
    th {{ background: #f6f8fa; }}
    img {{ max-width: 100%; border: 1px solid #eaeef2; border-radius: 4px; }}
    footer {{ margin-top: 48px; padding-top: 12px; border-top: 1px solid #d0d7de; font-size: 12px; color: #656d76; }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>{title}</h1>
      <div class="meta">생성: {now}</div>
    </div>
    <span class="badge">{badge_text}</span>
  </header>
  {sections_html}
  <footer>
    QualityLens · 2026 스마트 공장 운영 시스템 MVP 해커톤 · 본선 발표 부록
    · <a href="index.html">← 인덱스</a>
  </footer>
</body>
</html>
"""


def write(stage: str, source: str, sections: Sequence[dict]) -> Path:
    """sections: [{"title": "1. ...", "body_html": "..."}, ...]"""
    if stage not in STAGES:
        raise ValueError(f"unknown stage: {stage}. valid: {list(STAGES)}")
    num, label = STAGES[stage]
    title = f"{num}. {label} ({source})"
    sections_html = "\n".join(
        f'<div class="section"><h2>{s["title"]}</h2>{s["body_html"]}</div>'
        for s in sections
    )
    html = _html_template(title, source, sections_html)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / f"{num}_{stage}.html"
    path.write_text(html, encoding="utf-8")
    print(f"[report_render] → {path}")
    return path


def build_index() -> Path:
    """5개 보고서 카드 + 생성 시각 인덱스 페이지."""
    cards = []
    for stage, (num, label) in STAGES.items():
        report = REPORTS_DIR / f"{num}_{stage}.html"
        exists = report.exists()
        status = "✅" if exists else "⏳"
        link = f'<a href="{num}_{stage}.html">' if exists else "<span>"
        link_close = "</a>" if exists else "</span>"
        cards.append(f"""
<div class="card">
  {link}
    <div class="num">{num}</div>
    <div class="label">{status} {label}</div>
  {link_close}
</div>""")
    cards_html = "\n".join(cards)
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    html = f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>QualityLens · 검증 리포트 인덱스</title>
  <style>
    {html_font_face_css()}
    body {{ max-width: 980px; margin: 32px auto; padding: 0 24px; color: #1f2328; }}
    h1 {{ margin: 0 0 8px; }}
    .meta {{ color: #656d76; font-size: 13px; margin-bottom: 24px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; }}
    .card {{ border: 1px solid #d0d7de; border-radius: 8px; padding: 18px; background: white; transition: transform .15s; }}
    .card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,.06); }}
    .card a {{ text-decoration: none; color: inherit; display: block; }}
    .num {{ font-size: 24px; font-weight: 700; color: #58a6ff; }}
    .label {{ margin-top: 6px; font-size: 14px; }}
    footer {{ margin-top: 36px; padding-top: 12px; border-top: 1px solid #d0d7de; font-size: 12px; color: #656d76; }}
  </style>
</head>
<body>
  <h1>QualityLens 검증 리포트</h1>
  <div class="meta">생성: {now} · 본선 발표 부록</div>
  <div class="grid">
    {cards_html}
  </div>
  <footer>
    P-A 실데이터 통합·검증 산출물 — spec: smart-factory-hackathon/docs/spec_p_a_real_data_integration.md
  </footer>
</body>
</html>
"""
    path = REPORTS_DIR / "index.html"
    path.write_text(html, encoding="utf-8")
    print(f"[report_render] index → {path}")
    return path
