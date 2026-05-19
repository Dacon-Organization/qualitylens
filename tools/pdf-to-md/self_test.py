#!/usr/bin/env python3
"""Post-install smoke test for pdf-to-md."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

CONFIG_PATH = Path.home() / ".pdf_to_md_config.json"
ROOT = Path(__file__).parent


def check_import(python: str, label: str, code: str, required: bool) -> bool:
    result = subprocess.run([python, "-c", code], capture_output=True, text=True)
    ok = result.returncode == 0
    status = "OK" if ok else ("SKIP" if not required else "FAIL")
    print(f"{status:4} {label}")
    if not ok and required:
        detail = (result.stderr or result.stdout).strip()
        if detail:
            print(f"     {detail.splitlines()[-1]}")
    return ok or not required


def main() -> int:
    parser = argparse.ArgumentParser(description="Check pdf-to-md installation.")
    parser.add_argument(
        "--sample",
        help="Optional PDF/PPTX path. Runs converter dry-run routing against it.",
    )
    args = parser.parse_args()

    if not CONFIG_PATH.exists():
        print(f"FAIL config not found: {CONFIG_PATH}")
        print("Run install.command, install.ps1, or setup.py first.")
        return 1

    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    pdf_py = cfg.get("pdf_master_python")
    mineru_py = cfg.get("mineru_python") or pdf_py
    if not pdf_py:
        print("FAIL pdf_master_python missing in config")
        return 1

    print(f"Config: {CONFIG_PATH}")
    print(f"PDF tools Python: {pdf_py}")
    print(f"MinerU Python: {mineru_py}")
    print()

    checks = [
        check_import(pdf_py, "pymupdf", "import fitz", True),
        check_import(pdf_py, "python-pptx", "import pptx", True),
        check_import(
            pdf_py,
            "docling",
            "from docling.document_converter import DocumentConverter",
            False,
        ),
        check_import(pdf_py, "opendataloader-pdf", "import opendataloader_pdf", False),
        check_import(mineru_py, "mineru", "import mineru", False),
    ]

    if args.sample:
        sample = Path(args.sample).expanduser().resolve()
        if not sample.exists():
            print(f"FAIL sample not found: {sample}")
            return 1
        with tempfile.TemporaryDirectory(prefix="pdf-to-md-self-test-") as tmp:
            print()
            print(f"Dry-run sample: {sample.name}")
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "convert.py"),
                    str(sample),
                    "--output",
                    tmp,
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
            )
            if result.stdout:
                print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="", file=sys.stderr)
            checks.append(result.returncode == 0)

    return 0 if all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
