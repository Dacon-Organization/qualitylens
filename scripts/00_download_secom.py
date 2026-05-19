"""UCI SECOM 원본을 data/raw/ 로 다운로드.

본선장 오프라인 대비로 원본을 git에 직접 커밋하므로, 이 스크립트는
재현·신규 개발자·CI 용도. 본선장에서는 실행 불필요.

CLI::

    python scripts/00_download_secom.py
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "secom.data": "https://archive.ics.uci.edu/ml/machine-learning-databases/secom/secom.data",
    "secom_labels.data": "https://archive.ics.uci.edu/ml/machine-learning-databases/secom/secom_labels.data",
}

EXPECTED_ROWS = {
    "secom.data": 1567,
    "secom_labels.data": 1567,
}


def download(name: str, url: str) -> Path:
    dest = RAW_DIR / name
    if dest.exists():
        print(f"[skip] {name} 존재 — {dest.stat().st_size:,} bytes")
        return dest
    print(f"[download] {url}")
    urllib.request.urlretrieve(url, dest)
    print(f"  → {dest} ({dest.stat().st_size:,} bytes)")
    return dest


def verify(name: str, path: Path) -> None:
    rows = path.read_text().strip().splitlines()
    expected = EXPECTED_ROWS[name]
    assert len(rows) == expected, f"{name}: rows {len(rows)} != {expected}"
    print(f"[verify] {name} rows={len(rows)} OK")


def main() -> int:
    for name, url in FILES.items():
        path = download(name, url)
        verify(name, path)
    print("\n=== UCI SECOM 다운로드 완료 ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
