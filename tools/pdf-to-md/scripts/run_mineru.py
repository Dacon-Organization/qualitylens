#!/usr/bin/env python3
"""
MinerU CLI conversion runner.
Run via mineru venv Python (has mineru).
Usage: python run_mineru.py <input> --output-dir <dir> [--lang korean] [--chapter-aware]
Output: JSON metadata to stdout; writes <stem>.mineru.md to output-dir.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from score import measure, quality_flags, score


def find_mineru_cli() -> str | None:
    """Find the mineru CLI binary."""
    cli = shutil.which("mineru")
    if cli:
        return cli
    # Check common venv locations
    candidates = [
        Path.home() / ".pdf-to-md-venv" / "bin" / "mineru",
        Path.home() / "Projects/Education/MinerU/.venv/bin/mineru",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


def run_cli(src: Path, out_dir: Path, lang: str = "korean") -> dict:
    """Run MinerU via CLI subprocess."""
    mineru = find_mineru_cli()
    if not mineru:
        raise RuntimeError("mineru CLI not found — run setup.py first")

    cli_out = out_dir / "mineru_raw"
    cli_out.mkdir(parents=True, exist_ok=True)

    cmd = [
        mineru,
        "-p",
        str(src),
        "-o",
        str(cli_out),
        "-b",
        "pipeline",
        "-m",
        "txt",
        "-l",
        lang,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"MinerU CLI failed: {result.stderr[-500:]}")

    # MinerU output: cli_out/<stem>/txt/<stem>.md
    stem = src.stem
    md_candidates = list(cli_out.glob(f"**/{stem}.md"))
    if not md_candidates:
        md_candidates = list(cli_out.glob("**/*.md"))
    if not md_candidates:
        raise FileNotFoundError(f"MinerU produced no .md in {cli_out}")

    md_src = md_candidates[0]
    md_file = out_dir / f"{stem}.mineru.md"
    shutil.copy(md_src, md_file)

    # Copy images if present
    img_src = md_src.parent / "images"
    if img_src.exists():
        img_dst = out_dir / "images"
        if img_dst.exists():
            shutil.rmtree(img_dst)
        shutil.copytree(img_src, img_dst)

    text = md_file.read_text(encoding="utf-8")
    m = measure(text)
    return {
        "tool": "mineru",
        "score": score(m),
        "metrics": m,
        "quality_flags": quality_flags(m),
        "output_file": str(md_file),
    }


def run_api(
    src: Path, out_dir: Path, lang: str = "korean", chapter_aware: bool = False
) -> dict:
    """Run MinerU via Python API (chapter-aware for books)."""
    from mineru.cli.common import do_parse, read_fn
    from pypdf import PdfReader

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = src.stem
    pdf_bytes = read_fn(src)
    text = ""

    # Chapter-aware: split by TOC outline
    if chapter_aware:
        reader = PdfReader(str(src))
        toc = reader.outline
        chapters = []
        if toc:

            def recurse(items):
                for item in items:
                    if isinstance(item, list):
                        recurse(item)
                    else:
                        try:
                            page = reader.get_page_number(item.page)
                            chapters.append({"title": item.title, "page": page})
                        except Exception:
                            pass

            recurse(toc)
        if chapters:
            chapters.sort(key=lambda x: x["page"])
            total = len(reader.pages)
            result_parts = []
            tmp = out_dir / "_tmp_chapters"
            for i, ch in enumerate(chapters):
                end = (
                    chapters[i + 1]["page"] - 1 if i + 1 < len(chapters) else total - 1
                )
                safe = re.sub(r'[\/*?:"<>|]', "", ch["title"]).replace(" ", "_")
                ch_dir = tmp / safe
                ch_dir.mkdir(parents=True, exist_ok=True)
                do_parse(
                    output_dir=str(ch_dir),
                    pdf_file_names=[safe],
                    pdf_bytes_list=[pdf_bytes],
                    p_lang_list=[lang],
                    backend="pipeline",
                    parse_method="auto",
                    start_page_id=ch["page"],
                    end_page_id=end,
                    f_dump_md=True,
                    f_dump_middle_json=False,
                    f_dump_model_output=False,
                    f_dump_orig_pdf=False,
                    f_dump_content_list=False,
                    f_draw_layout_bbox=False,
                    f_draw_span_bbox=False,
                )
                md = ch_dir / safe / "auto" / f"{safe}.md"
                if md.exists():
                    result_parts.append(
                        f"# {ch['title']}\n\n" + md.read_text(encoding="utf-8")
                    )
            text = "\n\n".join(result_parts) + "\n"
            if tmp.exists():
                shutil.rmtree(tmp)
        else:
            chapter_aware = False  # fall through to simple mode

    if not chapter_aware:
        tmp_dir = out_dir / "_tmp_single"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        do_parse(
            output_dir=str(tmp_dir),
            pdf_file_names=[stem],
            pdf_bytes_list=[pdf_bytes],
            p_lang_list=[lang],
            backend="pipeline",
            parse_method="auto",
            f_dump_md=True,
            f_dump_middle_json=False,
            f_dump_model_output=False,
            f_dump_orig_pdf=False,
            f_dump_content_list=False,
            f_draw_layout_bbox=False,
            f_draw_span_bbox=False,
        )
        md = tmp_dir / stem / "auto" / f"{stem}.md"
        text = md.read_text(encoding="utf-8") if md.exists() else ""
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)

    md_file = out_dir / f"{stem}.mineru.md"
    md_file.write_text(text, encoding="utf-8")
    m = measure(text)
    return {
        "tool": "mineru-api",
        "score": score(m),
        "metrics": m,
        "quality_flags": quality_flags(m),
        "output_file": str(md_file),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--lang", default="korean")
    parser.add_argument("--chapter-aware", action="store_true")
    parser.add_argument(
        "--api", action="store_true", help="Use Python API instead of CLI"
    )
    args = parser.parse_args()

    src = Path(args.input).expanduser().resolve()
    out_dir = Path(args.output_dir).expanduser().resolve() / "mineru"

    try:
        if args.api or args.chapter_aware:
            result = run_api(
                src, out_dir, lang=args.lang, chapter_aware=args.chapter_aware
            )
        else:
            result = run_cli(src, out_dir, lang=args.lang)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"tool": "mineru", "error": str(exc), "score": -(10**9)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
