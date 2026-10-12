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
    1: r"^##\s+1\.\s+模块原理总结\s*$",
    2: r"^##\s+2\.\s+具体输入定义\s*$",
    3: r"^##\s+3\.\s+完整数据流转过程\s*$",
    4: r"^##\s+4\.\s+具体输出总结\s*$",
}

HEADER_FIELDS = (
    "模块：",
    "来源模式：",
    "模块类型：",
    "来源覆盖：",
    "假设：",
    "布局约定：",
)

SOURCE_MODES = ("论文公式", "论文结构", "通用定义")
MODULE_FAMILIES = (
    "注意力",
    "卷积",
    "归一化",
    "聚合",
    "循环",
    "通用",
)

STEP_SPLIT_RE = re.compile(r"^####\s+步骤\s+(\d+)\s*：\s*(.+?)\s*$", re.M)
NAMED_TENSOR_RE = re.compile(r"\b([A-Za-z][A-Za-z0-9_^]*)\s*:\s*\(([^)]+)\)")
ANON_ARROW_RE = re.compile(r"^\s*\(([^)]+)\)\s*(?:->|→)\s*\(([^)]+)\)\s*$")
BLOCK_MATH_RE = re.compile(r"(?m)^\$\$\s*\n([^\n](?:[\s\S]*?[^\n])?)\n\$\$\s*$")
INLINE_MATH_RE = re.compile(r"(?<!\$)\$([^$\n]+)\$(?!\$)")
SIMPLE_INLINE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]*$")
FIELD_RES = {
    "inputs": re.compile(r"\*\*输入张量：\*\*\s*(.+?)(?:\n\s*\n|\n\*\*|\Z)", re.S),
    "outputs": re.compile(r"\*\*输出张量：\*\*\s*(.+?)(?:\n\s*\n|\n\*\*|\Z)", re.S),
    "dim": re.compile(
        r"\*\*维度变换：\*\*\s*(.+?)(?:\n\s*\n|\n\*\*|\Z)", re.S
    ),
    "explanation": re.compile(
        r"\*\*作用：\*\*\s*(.+?)(?:\n\s*\n|\n\*\*|\n####\s+|\Z)", re.S
    ),
    "formula_label": re.compile(r"\*\*数学公式：\*\*"),
}

BINARY_OPS = (" x ", " × ", " + ", " odot ", " ⊕ ")
FORBIDDEN_LATEX = (
    r"\[",
    r"\]",
    r"\(",
    r"\)",
    r"\begin{equation",
    r"\end{equation",
    r"\tag",
    "```",
)


def finding(level: str, code: str, message: str, **details: Any) -> dict[str, Any]:
    item: dict[str, Any] = {"level": level, "code": code, "message": message}
    if details:
        item["details"] = details
    return item


def section_body(card: str, number: int) -> str:
    pattern = rf"^##\s+{number}\.\s+[^\n]*\n(.*?)(?=^##\s+\d+\.\s+|\Z)"
    match = re.search(pattern, card, re.M | re.S)
    return match.group(1) if match else ""


def header_value(card: str, label: str) -> str | None:
    match = re.search(rf">\s*{re.escape(label)}\s*(.+)$", card, re.M)
    return match.group(1).strip() if match else None


def normalize_shape(shape: str) -> str:
    parts = [part.strip() for part in shape.split(",")]
    return ", ".join(parts)


def parse_named_tensors(text: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for name, shape in NAMED_TENSOR_RE.findall(text or ""):
        found[name] = normalize_shape(shape)
    return found


def extract_names_from_math(text: str) -> set[str]:
    names: set[str] = set()
    blocked = {"mathbb", "mathrm", "operatorname", "text", "mathsf", "operatorname", "in"}
    for formula in BLOCK_MATH_RE.findall(text or ""):
        for match in re.finditer(
            r"([A-Za-z][A-Za-z0-9_]*(?:\s*,\s*[A-Za-z][A-Za-z0-9_]*)*)\s*\\in",
            formula,
        ):
            for name in re.findall(r"[A-Za-z][A-Za-z0-9_]*", match.group(1)):
                if name not in blocked:
                    names.add(name)
        for name in re.findall(r"\b([A-Za-z][A-Za-z0-9_]*)\s*=", formula):
            if name not in blocked:
                names.add(name)
    names.update(parse_named_tensors(text).keys())
    return names


def extract_section2_tensor_names(body2: str) -> set[str]:
    return extract_names_from_math(body2)


def audit_complex_inline_math(text: str, where: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for match in INLINE_MATH_RE.finditer(text or ""):
        content = match.group(1).strip()
        if not SIMPLE_INLINE_RE.fullmatch(content):
            findings.append(
                finding(
                    "error",
                    "complex_inline_math",
                    f"{where} 含有复杂行内公式，必须改为块级 $$ 公式",
                    value=content,
                )
            )
    return findings


def block_math_has_member(text: str) -> bool:
    return any(r"\in" in formula for formula in BLOCK_MATH_RE.findall(text or ""))


def split_steps(body3: str) -> list[dict[str, Any]]:
    matches = list(STEP_SPLIT_RE.finditer(body3 or ""))
    steps: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body3)
        steps.append(
            {
                "number": match.group(1),
                "title": match.group(2).strip(),
                "body": body3[start:end],
            }
        )
    return steps


def field_text(step_body: str, key: str) -> str | None:
    match = FIELD_RES[key].search(step_body)
    if not match:
        return None
    if key in {"formula_label"}:
        return match.group(0)
    return match.group(1).strip()


def latex_issues(formula: str) -> list[str]:
    issues: list[str] = []
    for token in FORBIDDEN_LATEX:
        if token in formula:
            issues.append(f"包含禁用写法 `{token}`")
    if re.search(r"[\u4e00-\u9fff]", formula):
        issues.append("数学环境中包含中文")
    if formula.count("{") != formula.count("}"):
        issues.append("花括号数量不匹配")
    if "$" in formula:
        issues.append("数学块内部包含额外的 `$`")
    return issues


def dim_is_multi_or_binary(dim_text: str) -> bool:
    if "," in dim_text and "->" in dim_text.replace("→", "->").split("->")[-1]:
        # multi-output on RHS
        rhs = dim_text.replace("→", "->").split("->")[-1]
        if NAMED_TENSOR_RE.search(rhs) and "," in rhs:
            return True
    return any(op in dim_text for op in BINARY_OPS)


def audit_step(
    step: dict[str, Any],
    known: dict[str, str],
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    findings: list[dict[str, Any]] = []
    number = step["number"]
    body = step["body"]
    produced: dict[str, str] = {}

    inputs_text = field_text(body, "inputs")
    outputs_text = field_text(body, "outputs")
    dim_text = field_text(body, "dim")
    explanation = field_text(body, "explanation")
    has_formula_label = field_text(body, "formula_label") is not None
    block_math = BLOCK_MATH_RE.findall(body)

    if inputs_text is None:
        findings.append(
            finding("error", "step_missing_inputs", f"步骤 {number} 缺少 **输入张量：**", step=number)
        )
    if not has_formula_label:
        findings.append(
            finding(
                "error",
                "step_missing_formula_label",
                f"步骤 {number} 缺少 **数学公式：**",
                step=number,
            )
        )
    if not block_math:
        findings.append(
            finding(
                "error",
                "step_missing_formula",
                f"步骤 {number} 缺少规范的三行块级 LaTeX 公式",
                step=number,
            )
        )
    if outputs_text is None:
        findings.append(
            finding(
                "error", "step_missing_outputs", f"步骤 {number} 缺少 **输出张量：**", step=number
            )
        )
    if dim_text is None:
        findings.append(
            finding(
                "error",
                "step_missing_dim_transform",
                f"步骤 {number} 缺少 **维度变换：**",
                step=number,
            )
        )
    if explanation is None or not explanation.strip():
        findings.append(
            finding(
                "error",
                "step_missing_explanation",
                f"步骤 {number} 缺少 **作用：**",
                step=number,
            )
        )

    input_tensors = parse_named_tensors(inputs_text or "")
    output_tensors = parse_named_tensors(outputs_text or "")

    if inputs_text is not None and not input_tensors:
        findings.append(
            finding(
                "error",
                "step_inputs_unparsed",
                f"步骤 {number} 的输入张量必须使用 名称:(形状)",
                step=number,
                value=inputs_text,
            )
        )
    if outputs_text is not None and not output_tensors:
        findings.append(
            finding(
                "error",
                "step_outputs_unparsed",
                f"步骤 {number} 的输出张量必须使用 名称:(形状)",
                step=number,
                value=outputs_text,
            )
        )

    for name in input_tensors:
        if name not in known:
            findings.append(
                finding(
                    "error",
                    "unknown_input_tensor",
                    f"Step {number} input `{name}` is not defined yet",
                    step=number,
                    tensor=name,
                )
            )

    for formula in block_math:
        for issue in latex_issues(formula):
            findings.append(
                finding(
                    "error",
                    "invalid_latex",
                    f"步骤 {number} 的 LaTeX 无法保证稳定渲染：{issue}",
                    step=number,
                )
            )

    if dim_text is not None:
        dim_line = " ".join(line.strip() for line in dim_text.splitlines() if line.strip())
        # strip surrounding backticks if present
        dim_line = dim_line.strip().strip("`")
        has_arrow = "->" in dim_line or "→" in dim_line
        if not has_arrow:
            findings.append(
                finding(
                    "error",
                    "dim_arrow_format",
                    f"Step {number} dimension transform must contain -> or →",
                    step=number,
                    value=dim_line,
                )
            )

        named_in_dim = parse_named_tensors(dim_line)
        anon = ANON_ARROW_RE.match(dim_line)
        multi_input = len(input_tensors) >= 2
        multi_output = len(output_tensors) >= 2
        if anon and (multi_input or multi_output or dim_is_multi_or_binary(dim_line)):
            findings.append(
                finding(
                    "error",
                    "anonymous_multi_io",
                    f"Step {number} branches/residuals/multi-IO must use named tensors",
                    step=number,
                    value=dim_line,
                )
            )
        if not named_in_dim and not anon:
            # allow named form without matching ANON
            if has_arrow and not NAMED_TENSOR_RE.search(dim_line):
                findings.append(
                    finding(
                        "error",
                        "dim_unparsed",
                        f"Step {number} dimension transform could not be parsed",
                        step=number,
                        value=dim_line,
                    )
                )

        # Shape consistency: Outputs shapes should match named RHS when present
        if "->" in dim_line or "→" in dim_line:
            rhs = re.split(r"->|→", dim_line, maxsplit=1)[1]
            rhs_tensors = parse_named_tensors(rhs)
            for name, shape in output_tensors.items():
                if name in rhs_tensors and rhs_tensors[name] != shape:
                    findings.append(
                        finding(
                            "error",
                            "output_dim_mismatch",
                            f"Step {number} output `{name}` shape mismatches Dimension Transformation",
                            step=number,
                            outputs_shape=shape,
                            dim_shape=rhs_tensors[name],
                        )
                    )

    produced.update(output_tensors)
    return findings, produced


def audit(card: str) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []

    for label in HEADER_FIELDS:
        if header_value(card, label) is None:
            findings.append(
                finding("error", "missing_header_field", f"Missing header field: {label}")
            )

    mode = header_value(card, "来源模式：")
    if mode and mode not in SOURCE_MODES:
        findings.append(
            finding(
                "error",
                "invalid_source_mode",
                f"Source mode must be one of {SOURCE_MODES}",
                value=mode,
            )
        )

    family = header_value(card, "模块类型：")
    if family and family not in MODULE_FAMILIES:
        findings.append(
            finding(
                "error",
                "invalid_module_family",
                f"Module family must be one of {MODULE_FAMILIES}",
                value=family,
            )
        )

    if mode == "通用定义":
        coverage = header_value(card, "来源覆盖：") or ""
        if coverage != "仅通用知识":
            findings.append(
                finding(
                    "error",
                    "canonical_coverage_mismatch",
                    "来源模式为“通用定义”时，来源覆盖必须为“仅通用知识”",
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

    findings.extend(audit_complex_inline_math(card, "全文"))

    body2 = section_body(card, 2)
    if body2 and not block_math_has_member(body2):
        findings.append(
            finding(
                "error",
                "input_shape_missing",
                "第 2 节必须用块级 $$ 公式定义输入形状（含 \\in）",
            )
        )

    known: dict[str, str] = {}
    for name in extract_section2_tensor_names(body2):
        known[name] = known.get(name, "")

    body3 = section_body(card, 3)
    steps = split_steps(body3)
    if not steps:
        findings.append(
            finding("error", "no_steps", "第 3 节必须包含 `#### 步骤 k：名称` 标题")
        )
    else:
        expected = [str(i) for i in range(1, len(steps) + 1)]
        observed = [step["number"] for step in steps]
        if observed != expected:
            findings.append(
                finding(
                    "error",
                    "step_numbering",
                    "Step numbering must be contiguous starting at 1",
                    observed=observed,
                )
            )

    produced_all: dict[str, str] = {}
    for step in steps:
        step_findings, produced = audit_step(step, known)
        findings.extend(step_findings)
        for name, shape in produced.items():
            known[name] = shape
            produced_all[name] = shape

    body4 = section_body(card, 4)
    if body4:
        if not block_math_has_member(body4):
            findings.append(
                finding(
                    "error",
                    "output_shape_missing",
                    "第 4 节必须用块级 $$ 公式给出最终输出形状（含 \\in）",
                )
            )
        final_names = extract_names_from_math(body4)
        for name in final_names:
            if name not in produced_all:
                findings.append(
                    finding(
                        "error",
                        "final_output_not_produced",
                        f"第 4 节输出 `{name}` 未在第 3 节产生",
                        tensor=name,
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
            "known_tensors": len(known),
            "produced_tensors": len(produced_all),
        },
    }


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
