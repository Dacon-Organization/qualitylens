#!/usr/bin/env python3
"""
ODL (opendataloader-pdf) conversion runner.
Run via pdf-master venv Python (has opendataloader_pdf).
Usage: python run_odl.py <input> --output-dir <dir> [--no-struct-tree]
Output: JSON metadata to stdout; writes <stem>.md to output-dir.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from score import measure, quality_flags, score


def run(src: Path, out_dir: Path, use_struct_tree: bool = True) -> dict:
    import opendataloader_pdf

    out_dir.mkdir(parents=True, exist_ok=True)
    opendataloader_pdf.convert(
        input_path=str(src),
        output_dir=str(out_dir),
        format="markdown",
        use_struct_tree=use_struct_tree,
        image_output="off",
    )
    md_file = out_dir / f"{src.stem}.md"
    if not md_file.exists():
        candidates = list(out_dir.glob("*.md"))
        if not candidates:
            raise FileNotFoundError(f"ODL produced no .md in {out_dir}")
        md_file = sorted(candidates)[-1]

    text = md_file.read_text(encoding="utf-8")
    m = measure(text)
    return {
        "tool": "odl",
        "score": score(m),
        "metrics": m,
        "quality_flags": quality_flags(m),
        "output_file": str(md_file),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--no-struct-tree", action="store_true")
    args = parser.parse_args()

    src = Path(args.input).expanduser().resolve()
    out_dir = Path(args.output_dir).expanduser().resolve() / "odl"

    try:
        result = run(src, out_dir, use_struct_tree=not args.no_struct_tree)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"tool": "odl", "error": str(exc), "score": -(10**9)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
