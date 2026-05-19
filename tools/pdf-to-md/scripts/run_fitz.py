#!/usr/bin/env python3
"""
fitz (PyMuPDF) raw text extraction runner.
Run via pdf-master venv Python (has pymupdf/fitz).
Usage: python run_fitz.py <input> --output-dir <dir>
Output: JSON metadata to stdout; writes <stem>.fitz.md to output-dir.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from score import measure, quality_flags, score


def run(src: Path, out_dir: Path) -> dict:
    import fitz

    doc = fitz.open(str(src))
    parts = []
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            parts.append(f"## Page {i + 1}\n\n{text}")
    doc.close()

    text = "\n\n".join(parts) + "\n"
    out_dir.mkdir(parents=True, exist_ok=True)
    md_file = out_dir / f"{src.stem}.fitz.md"
    md_file.write_text(text, encoding="utf-8")

    m = measure(text)
    return {
        "tool": "fitz",
        "score": score(m),
        "metrics": m,
        "quality_flags": quality_flags(m),
        "output_file": str(md_file),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    src = Path(args.input).expanduser().resolve()
    out_dir = Path(args.output_dir).expanduser().resolve() / "fitz"

    try:
        result = run(src, out_dir)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"tool": "fitz", "error": str(exc), "score": -(10**9)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
