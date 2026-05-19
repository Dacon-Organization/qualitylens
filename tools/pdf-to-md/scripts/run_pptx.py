#!/usr/bin/env python3
"""
python-pptx direct extraction runner.
Run via pdf-master venv Python (has python-pptx).
Usage: python run_pptx.py <input.pptx> --output-dir <dir>
Output: JSON metadata to stdout; writes <stem>.pptx.md to output-dir.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from score import measure, quality_flags, score


def clean_text(text: str) -> str:
    text = "".join(ch if ch >= " " or ch in "\t\n" else " " for ch in text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def image_ext(image) -> str:
    ext = (getattr(image, "ext", "") or "").lower().lstrip(".")
    if ext:
        return ext
    content_type = (getattr(image, "content_type", "") or "").lower()
    if "/" in content_type:
        return content_type.rsplit("/", 1)[-1].replace("x-", "")
    return "bin"


def save_image(blob: bytes, ext: str, image_dir: Path, slide_idx: int, image_idx: int) -> str:
    image_dir.mkdir(parents=True, exist_ok=True)
    safe_ext = re.sub(r"[^a-z0-9]+", "", ext.lower()) or "bin"
    filename = f"slide-{slide_idx:03d}-image-{image_idx:02d}.{safe_ext}"
    (image_dir / filename).write_bytes(blob)
    return filename


def add_text_entries(shape, entries: list[str], slide_idx: int):
    if not hasattr(shape, "text_frame") or shape.text_frame is None:
        return
    for para in shape.text_frame.paragraphs:
        text = clean_text(para.text)
        if not text or text == str(slide_idx):
            continue
        indent = "  " * para.level
        entry = f"{indent}- {text}"
        if not entries or entries[-1] != entry:
            entries.append(entry)


def add_picture_entry(shape, entries: list[str], image_dir: Path, slide_idx: int, image_state: dict):
    try:
        image = shape.image
        blob = image.blob
    except Exception:
        return

    digest = hashlib.sha256(blob).hexdigest()
    filename = image_state["files"].get(digest)
    if filename is None:
        image_state["count"] += 1
        filename = save_image(blob, image_ext(image), image_dir, slide_idx, image_state["count"])
        image_state["files"][digest] = filename

    entries.append(f"![Slide {slide_idx} image {image_state['count']}](images/{filename})")
    image_state["emitted"].add(digest)


def walk_shapes(shapes, entries: list[str], image_dir: Path, slide_idx: int, image_state: dict):
    from pptx.enum.shapes import MSO_SHAPE_TYPE

    ordered = sorted(
        shapes,
        key=lambda s: (getattr(s, "top", 0) or 0, getattr(s, "left", 0) or 0),
    )
    for shape in ordered:
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            walk_shapes(shape.shapes, entries, image_dir, slide_idx, image_state)
            continue
        if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
            add_picture_entry(shape, entries, image_dir, slide_idx, image_state)
            continue
        add_text_entries(shape, entries, slide_idx)


def add_unseen_blip_images(slide, entries: list[str], image_dir: Path, slide_idx: int, image_state: dict):
    """Catch embedded images that python-pptx did not expose as picture shapes."""
    rel_ns = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    for blip in slide.element.xpath('.//*[local-name()="blip"]'):
        rid = blip.get(f"{rel_ns}embed")
        if not rid:
            continue
        try:
            part = slide.part.related_part(rid)
            blob = part.blob
        except Exception:
            continue
        digest = hashlib.sha256(blob).hexdigest()
        if digest in image_state["emitted"]:
            continue
        ext = Path(str(part.partname)).suffix.lstrip(".") or "bin"
        image_state["count"] += 1
        filename = save_image(blob, ext, image_dir, slide_idx, image_state["count"])
        image_state["files"][digest] = filename
        image_state["emitted"].add(digest)
        entries.append(f"![Slide {slide_idx} image {image_state['count']}](images/{filename})")


def run(src: Path, out_dir: Path) -> dict:
    from pptx import Presentation

    prs = Presentation(str(src))
    lines = [f"# {src.stem}", ""]
    image_dir = out_dir / "images"
    total_images = 0
    for idx, slide in enumerate(prs.slides, 1):
        entries = []
        image_state = {"count": 0, "files": {}, "emitted": set()}
        walk_shapes(slide.shapes, entries, image_dir, idx, image_state)
        add_unseen_blip_images(slide, entries, image_dir, idx, image_state)
        total_images += image_state["count"]
        if entries:
            lines.append(f"## Slide {idx}")
            lines.append("")
            lines.extend(entries)
            lines.append("")

    text = "\n".join(lines).strip() + "\n"
    out_dir.mkdir(parents=True, exist_ok=True)
    md_file = out_dir / f"{src.stem}.pptx.md"
    md_file.write_text(text, encoding="utf-8")

    m = measure(text)
    return {
        "tool": "pptx-direct",
        "score": score(m),
        "metrics": m,
        "quality_flags": quality_flags(m),
        "output_file": str(md_file),
        "images_extracted": total_images,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    src = Path(args.input).expanduser().resolve()
    out_dir = Path(args.output_dir).expanduser().resolve() / "pptx"

    try:
        result = run(src, out_dir)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"tool": "pptx-direct", "error": str(exc), "score": -(10**9)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
