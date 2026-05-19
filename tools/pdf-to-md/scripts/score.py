#!/usr/bin/env python3
"""Quality scoring for conversion results. No external dependencies."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


@dataclass
class ConversionResult:
    tool: str
    text: str
    output_file: str = ""
    error: str = ""

    @property
    def metrics(self) -> dict:
        return measure(self.text)

    @property
    def score(self) -> int:
        return score(self.metrics)

    @property
    def quality_flags(self) -> list:
        return quality_flags(self.metrics)


def measure(text: str) -> dict:
    lines = text.splitlines()
    heading_lines = [l for l in lines if l.startswith("#")]
    image_refs = re.findall(r"!\[[^\]]*\]\(([^)]*)\)", text)
    real_image_refs = [ref for ref in image_refs if ref.strip()]
    dup_headings = sum(
        1
        for i in range(1, len(heading_lines))
        if heading_lines[i].strip() == heading_lines[i - 1].strip()
    )
    return {
        "chars": len(text),
        "korean_chars": sum(1 for c in text if "가" <= c <= "힣"),
        "heading_count": len(heading_lines),
        "table_count": text.count("| "),
        "image_count": len(real_image_refs),
        "image_placeholder": text.count("<!-- image -->") + text.count("![]()"),
        "duplicate_lines": sum(
            1
            for i in range(1, len(lines))
            if lines[i].strip() and lines[i] == lines[i - 1]
        ),
        "duplicate_headings": dup_headings,
        "blank_lines": sum(1 for l in lines if not l.strip()),
        "bullet_lines": sum(1 for l in lines if l.lstrip().startswith("- ")),
    }


def score(metrics: dict) -> int:
    return (
        metrics["chars"] * 1
        + metrics["korean_chars"] * 2
        + metrics["heading_count"] * 40
        + metrics["table_count"] * 30
        + metrics["image_count"] * 120
        + metrics["bullet_lines"] * 10
        - metrics["image_placeholder"] * 10
        - metrics["duplicate_lines"] * 5
        - metrics["duplicate_headings"] * 20
    )


def quality_flags(metrics: dict) -> List[str]:
    flags = []
    headings = max(metrics["heading_count"], 1)
    cph = metrics["chars"] / headings
    kph = metrics["korean_chars"] / headings
    if headings >= 20 and cph < 80:
        flags.append("sparse-text-per-slide")
    if headings >= 20 and kph < 25:
        flags.append("low-korean-density")
    if metrics["image_placeholder"] >= 20 and cph < 150:
        flags.append("image-heavy-deck")
    if metrics["duplicate_headings"] >= 5:
        flags.append("duplicate-headings")
    if metrics["chars"] < 200:
        flags.append("nearly-empty")
    return flags


def best(results: List[ConversionResult]) -> ConversionResult:
    viable = [r for r in results if r.text and not r.error]
    if not viable:
        raise ValueError("All conversion attempts failed")
    return max(viable, key=lambda r: r.score)
