#!/usr/bin/env python3
"""
pdf-to-md: Zero-choice automatic PDF/PPTX to Markdown converter.

Usage:
    python convert.py <file>                    # auto-detect output folder
    python convert.py <file> --output <dir>     # custom output directory
    python convert.py <file> --dry-run          # show routing plan, don't convert

Reads ~/.pdf_to_md_config.json for venv Python paths.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).parent / "scripts"
CONFIG_PATH = Path.home() / ".pdf_to_md_config.json"

SCORE_THRESHOLD = 500  # below this → "low confidence" warning


# ── Config ───────────────────────────────────────────────────────────────────


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        print("ERROR: Not set up. Run: python setup.py", file=sys.stderr)
        sys.exit(1)
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def py_for(config: dict, tool: str) -> str:
    """Return the Python binary path for a given tool."""
    if tool == "mineru":
        return (
            config.get("mineru_python")
            or config.get("pdf_master_python")
            or sys.executable
        )
    return config.get("pdf_master_python") or sys.executable


# ── Detection ─────────────────────────────────────────────────────────────────


def detect_file_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "pdf"
    if suffix in (".pptx", ".ppt"):
        return "pptx"
    raise ValueError(
        f"Unsupported file type: {suffix} — only PDF and PPTX are supported"
    )


def detect_pdf_info(path: Path, config: dict) -> dict:
    python = py_for(config, "pdf_master")
    result = subprocess.run(
        [python, str(SCRIPTS / "detect.py"), str(path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0 or not result.stdout.strip():
        print(f"  [warn] PDF detection failed: {result.stderr[:200]}", file=sys.stderr)
        return {
            "type": "digital",
            "language": "unknown",
            "layout": "book",
            "columns": 1,
            "tagged": False,
            "page_count": 0,
            "has_outline": False,
        }
    return json.loads(result.stdout)


# ── Runner subprocess ─────────────────────────────────────────────────────────


def run_tool(script: str, args: list[str], python: str, timeout: int = 300) -> dict:
    cmd = [python, str(SCRIPTS / script)] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.stdout.strip():
            parsed = parse_tool_json(result.stdout)
            if parsed is not None:
                return parsed
            tail = (result.stdout + "\n" + result.stderr)[-500:]
            return {"tool": script, "error": f"invalid JSON output: {tail}", "score": -(10**9)}
        return {"tool": script, "error": result.stderr[-500:], "score": -(10**9)}
    except subprocess.TimeoutExpired:
        return {"tool": script, "error": "timeout", "score": -(10**9)}
    except Exception as exc:
        return {"tool": script, "error": str(exc), "score": -(10**9)}


def parse_tool_json(stdout: str) -> dict | None:
    """Parse runner JSON even when a dependency writes log lines to stdout."""
    text = stdout.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    for line in reversed(text.splitlines()):
        candidate = line.strip()
        if not candidate.startswith("{"):
            continue
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    return None


# ── Routing ───────────────────────────────────────────────────────────────────


def plan_pdf(info: dict, config: dict, output_dir: Path, src: str) -> list[dict]:
    """Return list of {script, args, python, label} dicts to try."""
    pdf_py = py_for(config, "pdf_master")
    mineru_py = py_for(config, "mineru")
    base_args = [src, "--output-dir", str(output_dir)]
    plans = []

    if info.get("type") == "scanned":
        # Scanned: OCR only — MinerU OCR mode is best available
        print("  [route] scanned PDF → MinerU OCR mode")
        plans.append(
            {
                "script": "run_mineru.py",
                "args": base_args + ["--lang", "korean"],
                "python": mineru_py,
                "label": "mineru-ocr",
            }
        )

    elif info.get("layout") == "slides" and info.get("language") in ("korean", "mixed"):
        print("  [route] Korean lecture slides → ODL struct_tree + MinerU CLI")
        if info.get("tagged"):
            plans.append(
                {
                    "script": "run_odl.py",
                    "args": base_args,
                    "python": pdf_py,
                    "label": "odl-struct-tree",
                }
            )
        plans.append(
            {
                "script": "run_mineru.py",
                "args": base_args + ["--lang", "korean"],
                "python": mineru_py,
                "label": "mineru-cli",
            }
        )

    elif info.get("layout") == "slides":
        print("  [route] English slides → docling + ODL")
        plans.append(
            {
                "script": "run_docling.py",
                "args": base_args,
                "python": pdf_py,
                "label": "docling",
            }
        )
        if info.get("tagged"):
            plans.append(
                {
                    "script": "run_odl.py",
                    "args": base_args,
                    "python": pdf_py,
                    "label": "odl-struct-tree",
                }
            )

    elif info.get("layout") == "book" and info.get("has_outline"):
        print("  [route] book with TOC → MinerU API (chapter-aware) + fitz fallback")
        plans.append(
            {
                "script": "run_mineru.py",
                "args": base_args
                + [
                    "--api",
                    "--chapter-aware",
                    "--lang",
                    "korean" if info.get("language") == "korean" else "en",
                ],
                "python": mineru_py,
                "label": "mineru-api-chapters",
            }
        )
        plans.append(
            {
                "script": "run_fitz.py",
                "args": base_args,
                "python": pdf_py,
                "label": "fitz",
            }
        )

    elif info.get("columns", 1) == 2:
        print("  [route] 2-column paper → ODL (reading order) + fitz")
        plans.append(
            {
                "script": "run_odl.py",
                "args": base_args + ["--no-struct-tree"],
                "python": pdf_py,
                "label": "odl-xycut",
            }
        )
        plans.append(
            {
                "script": "run_fitz.py",
                "args": base_args,
                "python": pdf_py,
                "label": "fitz",
            }
        )

    else:
        print("  [route] general digital PDF → fitz + docling")
        plans.append(
            {
                "script": "run_fitz.py",
                "args": base_args,
                "python": pdf_py,
                "label": "fitz",
            }
        )
        plans.append(
            {
                "script": "run_docling.py",
                "args": base_args,
                "python": pdf_py,
                "label": "docling",
            }
        )

    return plans


def plan_pptx(config: dict, output_dir: Path, src: str) -> list[dict]:
    pdf_py = py_for(config, "pdf_master")
    base_args = [src, "--output-dir", str(output_dir)]
    print("  [route] PPTX → docling + pptx-direct")
    return [
        {
            "script": "run_docling.py",
            "args": base_args,
            "python": pdf_py,
            "label": "docling",
        },
        {
            "script": "run_pptx.py",
            "args": base_args,
            "python": pdf_py,
            "label": "pptx-direct",
        },
    ]


# ── Output layout ─────────────────────────────────────────────────────────────


def output_layout(src: Path, config: dict, output_arg: str | None) -> tuple[Path, Path, Path]:
    """Return (markdown_dir, report_dir, candidate_dir)."""
    if output_arg:
        markdown_dir = Path(output_arg).expanduser().resolve()
        report_dir = markdown_dir
        candidate_dir = markdown_dir
        return markdown_dir, report_dir, candidate_dir

    base_dir = src.parent
    markdown_dir = base_dir / "markdown"
    report_dir = base_dir / ".reports"
    candidate_dir = report_dir / "candidates" / src.stem
    print("  [layout] 입력 파일 폴더 아래 markdown/ 및 .reports/ 사용")
    return markdown_dir, report_dir, candidate_dir


# ── Main ──────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Auto-convert PDF/PPTX to Markdown.")
    parser.add_argument("input", help="PDF or PPTX file path")
    parser.add_argument(
        "--output", default=None, help="Override Markdown output directory"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show routing plan, skip conversion"
    )
    args = parser.parse_args()

    src = Path(args.input).expanduser().resolve()
    if not src.exists():
        print(f"ERROR: File not found: {src}", file=sys.stderr)
        sys.exit(1)

    config = load_config()
    out_dir, report_dir, candidate_dir = output_layout(src, config, args.output)

    print(f"\n[pdf-to-md] {src.name}")
    file_type = detect_file_type(src)

    if file_type == "pdf":
        print("  Detecting PDF characteristics...")
        info = detect_pdf_info(src, config)
        print(
            f"  type={info.get('type')} lang={info.get('language')} "
            f"layout={info.get('layout')} cols={info.get('columns')} "
            f"tagged={info.get('tagged')} pages={info.get('page_count')}"
        )
        plans = plan_pdf(info, config, candidate_dir, str(src))
    else:
        info = {}
        plans = plan_pptx(config, candidate_dir, str(src))

    if args.dry_run:
        print("\n[dry-run] Would run:")
        for p in plans:
            print(f"  {p['label']}: {p['script']}")
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    candidate_dir.mkdir(parents=True, exist_ok=True)

    # Run all candidates
    print(f"  Running {len(plans)} candidate tool(s)...")
    results = []
    for plan in plans:
        print(f"    → {plan['label']}...", end=" ", flush=True)
        result = run_tool(plan["script"], plan["args"], plan["python"])
        if "error" in result and result.get("score", 0) <= -(10**9):
            print(f"FAILED ({result['error'][:60]})")
        else:
            print(f"score={result.get('score', 0)}")
        results.append(result)

    # Pick winner
    viable = [
        r for r in results if "output_file" in r and r.get("score", -(10**9)) > -(10**9)
    ]
    if not viable:
        print("\nERROR: All conversion attempts failed.", file=sys.stderr)
        for r in results:
            print(
                f"  {r.get('tool')}: {r.get('error', 'unknown error')}", file=sys.stderr
            )
        sys.exit(1)

    winner = max(viable, key=lambda r: r["score"])
    winner_file = Path(winner["output_file"])

    # Copy winner to final output, rewriting local image links to a per-document folder.
    final = out_dir / f"{src.stem}.md"
    text = winner_file.read_text(encoding="utf-8")

    # Copy images into a shared images/<document-stem>/ folder.
    img_src = winner_file.parent / "images"
    if img_src.exists():
        img_dst = out_dir / "images" / src.stem
        if img_dst.exists():
            shutil.rmtree(img_dst)
        shutil.copytree(img_src, img_dst)
        image_prefix = f"images/{src.stem}/"
        text = text.replace("](images/", f"]({image_prefix}")
        text = text.replace("](./images/", f"]({image_prefix}")

    final.write_text(text, encoding="utf-8")

    # Report
    confidence = "low" if winner["score"] < SCORE_THRESHOLD else "normal"
    flags = winner.get("quality_flags", [])
    print(
        f"\n  Winner: {winner.get('tool')} (score={winner['score']}, confidence={confidence})"
    )
    if flags:
        print(f"  Flags:  {', '.join(flags)}")
    print(f"  Output: {final}")

    if confidence == "low":
        print(
            "\n  [!] Low confidence result. Consider running with --dry-run to inspect routing,"
        )
        print("      or check the candidate files in the output subdirectories.")

    # Write routing report
    report = {
        "input": str(src),
        "file_type": file_type,
        "detection": info,
        "winner": winner.get("tool"),
        "confidence": confidence,
        "quality_flags": flags,
        "final_output": str(final),
        "candidates": [{k: v for k, v in r.items() if k != "text"} for r in results],
    }
    report_file = report_dir / f"{src.stem}.route.json"
    report_file.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  Report: {report_file}")


if __name__ == "__main__":
    main()
