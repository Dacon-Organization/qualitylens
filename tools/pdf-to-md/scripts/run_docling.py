#!/usr/bin/env python3
"""
Docling conversion runner (PDF and PPTX).
Run via pdf-master venv Python (has docling).
Usage: python run_docling.py <input> --output-dir <dir>
Output: JSON metadata to stdout; writes <stem>.docling.md to output-dir.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from score import measure, quality_flags, score


def run(src: Path, out_dir: Path) -> dict:
    from docling.document_converter import DocumentConverter

    result = DocumentConverter().convert(str(src))
    text = result.document.export_to_markdown()
    if not text.endswith("\n"):
        text += "\n"

    out_dir.mkdir(parents=True, exist_ok=True)
    md_file = out_dir / f"{src.stem}.docling.md"
    md_file.write_text(text, encoding="utf-8")

    m = measure(text)
    return {
        "tool": "docling",
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
    out_dir = Path(args.output_dir).expanduser().resolve() / "docling"

    try:
        result = run(src, out_dir)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"tool": "docling", "error": str(exc), "score": -(10**9)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
