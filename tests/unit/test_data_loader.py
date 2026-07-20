"""data_loader.resolve_source 단위 테스트."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))


def test_explicit_real(monkeypatch):
    monkeypatch.delenv("DEMO_MODE", raising=False)
    from app.lib import data_loader

    monkeypatch.setattr(data_loader, "_real_artifacts_complete", lambda: True)
    assert data_loader.resolve_source("real") == "real"


def test_explicit_real_falls_back_when_artifacts_missing(monkeypatch):
    monkeypatch.delenv("DEMO_MODE", raising=False)
    from app.lib import data_loader

    monkeypatch.setattr(data_loader, "_real_artifacts_complete", lambda: False)
    assert data_loader.resolve_source("real") == "dummy"


def test_explicit_dummy(monkeypatch):
    monkeypatch.delenv("DEMO_MODE", raising=False)
    from app.lib.data_loader import resolve_source

    assert resolve_source("dummy") == "dummy"


def test_env_var_real(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "real")
    from app.lib import data_loader

    monkeypatch.setattr(data_loader, "_real_artifacts_complete", lambda: True)
    assert data_loader.resolve_source() == "real"


def test_env_var_dummy(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "dummy")
    from app.lib.data_loader import resolve_source

    assert resolve_source() == "dummy"


def test_invalid_env_falls_back_to_auto(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "garbage")
    from app.lib.data_loader import resolve_source

    result = resolve_source()
    assert result in ("real", "dummy")
