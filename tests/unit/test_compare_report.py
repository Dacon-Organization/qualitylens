"""04_compare_real_vs_dummy.py 산출물 어설션."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def test_report_md_exists():
    md = ROOT / "docs" / "validation" / "real_vs_dummy_report.md"
    assert md.exists(), f"보고서 부재: {md}"
    text = md.read_text(encoding="utf-8")
    assert "데이터 비교" in text
    assert "모델 성능" in text
    assert "SHAP Top 10 겹침" in text
    assert "결론 요약" in text


def test_charts_exist():
    charts_dir = ROOT / "assets" / "charts" / "validation"
    assert (charts_dir / "distribution_top5.png").exists()
    assert (charts_dir / "roc_pr_curves.png").exists()
