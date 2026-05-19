"""Playwright MCP 캡처 결과를 HTML 보고서로 묶는 헬퍼.

MCP 호출 자체는 Claude Code 세션에서 직접 수행하고, 이 스크립트는
``assets/qa/playwright/`` 에 모인 PNG 들을 ``docs/reports/05_playwright_qa.html`` 로 묶는다.

CLI::

    python tests/e2e/run_playwright_qa.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from app.lib.report_render import write as write_report, build_index  # noqa: E402

QA_DIR = ROOT / "assets" / "qa" / "playwright"


def list_screenshots(subdir: str) -> list[Path]:
  target = QA_DIR / subdir
  if not target.exists():
    return []
  return sorted(target.glob("*.png"))


def gallery_html(title: str, shots: list[Path]) -> str:
  if not shots:
    return f"<p><em>{title} 스크린샷 없음</em></p>"
  items = "\n".join(
    f'<figure style="margin:8px;display:inline-block;width:300px;vertical-align:top;">'
    f'<img src="../../{p.relative_to(ROOT).as_posix()}" alt="{p.name}" '
    f'style="width:100%;border:1px solid #d0d7de;border-radius:4px;">'
    f'<figcaption style="font-size:12px;color:#656d76;text-align:center;margin-top:4px;">'
    f'{p.name}</figcaption>'
    f'</figure>'
    for p in shots
  )
  return f'<div>{items}</div>'


def main() -> int:
  real_shots = list_screenshots("real")
  dummy_shots = list_screenshots("dummy")
  golden_shots = list_screenshots("golden_path")

  pass_real = "✅" if len(real_shots) >= 5 else "❌"
  pass_dummy = "✅" if len(dummy_shots) >= 5 else "❌"
  pass_golden = "✅" if len(golden_shots) >= 5 else "❌"

  summary_html = (
    '<table style="border-collapse:collapse;">'
    '<thead><tr>'
    '<th style="border:1px solid #d0d7de;padding:6px 10px;">트랙</th>'
    '<th style="border:1px solid #d0d7de;padding:6px 10px;">스크린샷</th>'
    '<th style="border:1px solid #d0d7de;padding:6px 10px;">상태</th>'
    '</tr></thead><tbody>'
    f'<tr><td style="border:1px solid #d0d7de;padding:6px 10px;">트랙 ① real (5페이지)</td>'
    f'<td style="border:1px solid #d0d7de;padding:6px 10px;">{len(real_shots)}/5</td>'
    f'<td style="border:1px solid #d0d7de;padding:6px 10px;">{pass_real}</td></tr>'
    f'<tr><td style="border:1px solid #d0d7de;padding:6px 10px;">트랙 ① dummy (5페이지)</td>'
    f'<td style="border:1px solid #d0d7de;padding:6px 10px;">{len(dummy_shots)}/5</td>'
    f'<td style="border:1px solid #d0d7de;padding:6px 10px;">{pass_dummy}</td></tr>'
    f'<tr><td style="border:1px solid #d0d7de;padding:6px 10px;">트랙 ② 골든 패스 (5단계)</td>'
    f'<td style="border:1px solid #d0d7de;padding:6px 10px;">{len(golden_shots)}/5</td>'
    f'<td style="border:1px solid #d0d7de;padding:6px 10px;">{pass_golden}</td></tr>'
    '</tbody></table>'
  )

  sections = [
    {"title": "1. 어설션 결과 요약", "body_html": summary_html},
    {"title": "2. 트랙 ① real 스크린샷", "body_html": gallery_html("트랙 ① real", real_shots)},
    {"title": "3. 트랙 ① dummy 스크린샷", "body_html": gallery_html("트랙 ① dummy", dummy_shots)},
    {"title": "4. 트랙 ② 골든 패스 스크린샷", "body_html": gallery_html("트랙 ② 골든 패스", golden_shots)},
  ]
  out = write_report("playwright_qa", source="real", sections=sections)
  idx = build_index()
  total = len(real_shots) + len(dummy_shots) + len(golden_shots)
  print(f"보고서 생성: {out}")
  print(f"인덱스 갱신: {idx}")
  print(f"총 {total}장 스크린샷 묶음 (real {len(real_shots)} / dummy {len(dummy_shots)} / golden {len(golden_shots)})")
  return 0


if __name__ == "__main__":
  sys.exit(main())
