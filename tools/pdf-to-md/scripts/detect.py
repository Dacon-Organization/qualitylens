#!/usr/bin/env python3
"""
Detect PDF characteristics for routing decisions.
Requires fitz (pymupdf) — run via pdf-master venv Python.

Usage: python detect.py <file.pdf>
Output: JSON to stdout
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass


@dataclass
class PDFInfo:
    type: str  # "digital" | "scanned"
    language: str  # "korean" | "english" | "mixed"
    layout: str  # "slides" | "book" | "paper"
    columns: int  # 1 | 2
    tagged: bool  # has PDF tag tree (enables ODL struct_tree)
    page_count: int
    has_outline: bool  # has TOC / bookmark outline


def detect_pdf(path: str) -> PDFInfo:
    import fitz  # PyMuPDF — in pdf-master venv

    doc = fitz.open(path)
    total_pages = len(doc)
    sample_n = min(5, total_pages)

    texts = [doc[i].get_text() for i in range(sample_n)]
    full = "".join(texts)
    per_page = len(full) / sample_n if sample_n else 0

    # Tagged PDFs always have a structure tree — they're digital by definition
    tagged = False
    try:
        xref = doc.pdf_catalog()
        if xref:
            cat = doc.xref_object(xref)
            tagged = "/MarkInfo" in cat or "/StructTreeRoot" in cat
    except Exception:
        pass

    is_scanned = (not tagged) and (per_page < 50)

    korean = sum(1 for c in full if "가" <= c <= "힣")
    kr_ratio = korean / max(len(full), 1)
    if kr_ratio > 0.15:
        language = "korean"
    elif kr_ratio > 0.05:
        language = "mixed"
    else:
        language = "english"

    layout = "book"
    columns = 1
    if total_pages > 0:
        rect = doc[0].rect
        w, h = rect.width, rect.height
        aspect = w / h if h > 0 else 1.0
        if aspect >= 1.2:
            layout = "slides"
        else:
            blocks = doc[0].get_text("blocks")
            text_blocks = [b for b in blocks if b[4].strip()]
            if text_blocks:
                mid = w / 2
                left_n = sum(1 for b in text_blocks if b[0] < mid - 30)
                right_n = sum(1 for b in text_blocks if b[0] > mid + 30)
                if left_n >= 2 and right_n >= 2:
                    layout = "paper"
                    columns = 2

    has_outline = bool(doc.get_toc())
    doc.close()

    return PDFInfo(
        type="scanned" if is_scanned else "digital",
        language=language,
        layout=layout,
        columns=columns,
        tagged=tagged,
        page_count=total_pages,
        has_outline=has_outline,
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: detect.py <file.pdf>"}))
        sys.exit(1)
    try:
        info = detect_pdf(sys.argv[1])
        print(json.dumps(asdict(info), ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)
