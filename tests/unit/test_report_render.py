"""report_render.write / build_index 단위 테스트."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from app.lib import report_render


def test_write_minimal(tmp_path, monkeypatch):
    monkeypatch.setattr(report_render, "REPORTS_DIR", tmp_path)
    sections = [{"title": "테스트 섹션", "body_html": "<p>안녕</p>"}]
    path = report_render.write("preprocessing", "real", sections)
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "01. T1 전처리 (real)" in text
    assert "테스트 섹션" in text
    assert "🟢 real" in text


def test_write_invalid_stage_raises():
    import pytest

    with pytest.raises(ValueError):
        report_render.write("not_a_stage", "real", [])


def test_build_index_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(report_render, "REPORTS_DIR", tmp_path)
    path = report_render.build_index()
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "QualityLens 검증 리포트" in text
    for label in ("T1 전처리", "T2 모델 학습", "T3 SHAP 분석", "real vs dummy 비교", "Playwright E2E 검증"):
        assert label in text
