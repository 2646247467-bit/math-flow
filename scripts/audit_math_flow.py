#!/usr/bin/env python3
"""Audit a Math-Flow card against the fixed four-section output contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SECTION_HEADINGS = {
    1: r"^##\s+1\.\s+模块原理总结\s+\(Module Principle Summary\)\s*$",
    2: r"^##\s+2\.\s+具体输入定义\s+\(Specific Input Definition\)\s*$",
    3: r"^##\s+3\.\s+完整数据流转过程\s+\(Complete Mathematical Data Flow\)\s*$",
    4: r"^##\s+4\.\s+具体输出总结\s+\(Specific Output Summary\)\s*$",
}

HEADER_FIELDS = (
    "Module:",
    "Source mode:",
    "Module family:",
    "Source coverage:",
    "Assumptions:",
    "Layout convention:",
)

SOURCE_MODES = ("paper-equation", "paper-structure", "canonical-fallback")
MODULE_FAMILIES = (
    "attention",
    "convolution",
    "normalization",
    "aggregation",
    "recurrent",
    "generic",
)

DIM_RE = re.compile(
    r"\*\*Dimension Transformation:\*\*\s*`([^`]+)`",
    re.I,
)
STEP_RE = re.compile(r"^####\s+Step\s+(\d+)\s*:", re.M)
SHAPE_ARROW_RE = re.compile(
    r"\(([BCHWNd_hqr,\s]+)\)\s*(?:->|→)\s*\(([BCHWNd_hqr,\s]+)\)"
)
BLOCK_MATH_RE = re.compile(r"\$\$[\s\S]+?\$\$")
INLINE_MEMBER_RE = re.compile(r"\$[^$\n]*\\in[^$\n]*\$")


def finding(level: str, code: str, message: str, **details: Any) -> dict[str, Any]:
    item: dict[str, Any] = {"level": level, "code": code, "message": message}
    if details:
        item["details"] = details
    return item


def section_body(card: str, number: int) -> str:
    pattern = (
        rf"^##\s+{number}\.\s+[^\n]*\n(.*?)(?=^##\s+\d+\.\s+|\Z)"
    )
    match = re.search(pattern, card, re.M | re.S)
    return match.group(1) if match else ""


def header_value(card: str, label: str) -> str | None:
    match = re.search(rf">\s*{re.escape(label)}\s*(.+)$", card, re.M)
    return match.group(1).strip() if match else None


def audit(card: str) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []

    for label in HEADER_FIELDS:
        if header_value(card, label) is None:
            findings.append(
                finding("error", "missing_header_field", f"Missing header field: {label}")
            )

    mode = header_value(card, "Source mode:")
    if mode and mode not in SOURCE_MODES:
        findings.append(
            finding(
                "error",
                "invalid_source_mode",
                f"Source mode must be one of {SOURCE_MODES}",
                value=mode,
            )
        )

    family = header_value(card, "Module family:")
    if family and family not in MODULE_FAMILIES:
        findings.append(
            finding(
                "error",
                "invalid_module_family",
                f"Module family must be one of {MODULE_FAMILIES}",
                value=family,
            )
        )

    if mode == "canonical-fallback":
        coverage = header_value(card, "Source coverage:") or ""
        if "Canonical" not in coverage and "canonical" not in coverage:
            findings.append(
                finding(
                    "warning",
                    "canonical_coverage_mismatch",
                    "canonical-fallback should declare Canonical knowledge coverage",
                )
            )

    positions: list[tuple[int, int]] = []
    for number, pattern in SECTION_HEADINGS.items():
        match = re.search(pattern, card, re.M)
        if not match:
            findings.append(
                finding(
                    "error",
                    "missing_section",
                    f"Missing or mistitled Section {number}",
                    expected=pattern,
                )
            )
        else:
            positions.append((number, match.start()))

    if len(positions) == 4:
        ordered = [n for n, _ in sorted(positions, key=lambda item: item[1])]
        if ordered != [1, 2, 3, 4]:
            findings.append(
                finding(
                    "error",
                    "section_order",
                    "Sections must appear in order 1→2→3→4",
                    observed=ordered,
                )
            )

    body2 = section_body(card, 2)
    if body2 and not INLINE_MEMBER_RE.search(body2):
        findings.append(
            finding(
                "warning",
                "input_shape_missing",
                "Section 2 should define inputs with $...\\in\\mathbb{R}^{...}$",
            )
        )

    body3 = section_body(card, 3)
    steps = STEP_RE.findall(body3)
    if not steps:
        findings.append(
            finding("error", "no_steps", "Section 3 must contain #### Step k: headings")
        )
    else:
        expected = [str(i) for i in range(1, len(steps) + 1)]
        if steps != expected:
            findings.append(
                finding(
                    "warning",
                    "step_numbering",
                    "Step numbering should be contiguous starting at 1",
                    observed=steps,
                )
            )

    if body3 and not BLOCK_MATH_RE.search(body3):
        findings.append(
            finding("error", "no_block_math", "Section 3 must include block LaTeX formulas")
        )

    dim_lines = DIM_RE.findall(body3)
    if steps and len(dim_lines) < len(steps):
        findings.append(
            finding(
                "error",
                "missing_dim_transform",
                "Each Step should include **Dimension Transformation:** `...`",
                steps=len(steps),
                dim_lines=len(dim_lines),
            )
        )

    for line in dim_lines:
        if not SHAPE_ARROW_RE.search(line) and "->" not in line and "→" not in line:
            findings.append(
                finding(
                    "warning",
                    "dim_arrow_format",
                    "Dimension transform should use `(in) -> (out)`",
                    value=line,
                )
            )

    # Continuity heuristic for simple unary transforms only (skip matmul "x" lines).
    simple_pairs: list[tuple[str, str]] = []
    for line in dim_lines:
        if " x " in line or " × " in line:
            continue
        match = re.search(r"\(([^)]+)\)\s*(?:->|→)\s*\(([^)]+)\)", line)
        if match:
            simple_pairs.append(
                (normalize_shape(match.group(1)), normalize_shape(match.group(2)))
            )

    for index in range(len(simple_pairs) - 1):
        out_shape = simple_pairs[index][1]
        in_shape = simple_pairs[index + 1][0]
        if out_shape != in_shape:
            findings.append(
                finding(
                    "warning",
                    "dimension_chain_gap",
                    "Possible dimension-chain discontinuity between consecutive simple steps",
                    step=index + 1,
                    out_shape=out_shape,
                    next_in_shape=in_shape,
                )
            )

    body4 = section_body(card, 4)
    if body4 and not re.search(r"\\in\s*\\mathbb\{R\}", body4) and not re.search(
        r"\([BCHWNd,\s]+\)", body4
    ):
        findings.append(
            finding(
                "warning",
                "output_shape_missing",
                "Section 4 should state the final tensor shape",
            )
        )

    errors = sum(1 for item in findings if item["level"] == "error")
    warnings = sum(1 for item in findings if item["level"] == "warning")
    status = "pass" if errors == 0 else "fail"

    return {
        "status": status,
        "error_count": errors,
        "warning_count": warnings,
        "findings": findings,
        "stats": {
            "steps": len(steps),
            "dimension_transforms": len(dim_lines),
            "simple_shape_pairs": len(simple_pairs),
        },
    }


def normalize_shape(shape: str) -> str:
    parts = [part.strip() for part in shape.split(",")]
    return ", ".join(parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("card", type=Path, help="Path to math-flow-*.md")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional audit-report.json path",
    )
    args = parser.parse_args(argv)

    if not args.card.is_file():
        print(f"error: card not found: {args.card}", file=sys.stderr)
        return 2

    report = audit(args.card.read_text(encoding="utf-8"))
    report["card_path"] = str(args.card)

    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
