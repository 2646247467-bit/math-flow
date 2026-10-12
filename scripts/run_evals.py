#!/usr/bin/env python3
"""Execute Math-Flow eval fixtures against the bundled auditor."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_auditor():
    path = ROOT / "scripts" / "audit_math_flow.py"
    spec = importlib.util.spec_from_file_location("audit_math_flow", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_one(audit_fn, case: dict[str, Any]) -> dict[str, Any]:
    card_path = ROOT / case["card"]
    report = audit_fn(card_path.read_text(encoding="utf-8"))
    expect = case.get("expect", {})
    errors: list[str] = []

    status = expect.get("status")
    if status is not None and report["status"] != status:
        errors.append(f"status want={status} got={report['status']}")

    min_steps = expect.get("min_steps")
    if min_steps is not None and report["stats"]["steps"] < min_steps:
        errors.append(
            f"min_steps want>={min_steps} got={report['stats']['steps']}"
        )

    max_steps = expect.get("max_steps")
    if max_steps is not None and report["stats"]["steps"] > max_steps:
        errors.append(
            f"max_steps want<={max_steps} got={report['stats']['steps']}"
        )

    codes = {item["code"] for item in report["findings"]}
    for code in expect.get("require_codes", []):
        if code not in codes:
            errors.append(f"missing required code: {code}")

    for code in expect.get("forbid_codes", []):
        if code in codes:
            errors.append(f"unexpected code: {code}")

    return {
        "id": case["id"],
        "name": case["name"],
        "ok": not errors,
        "errors": errors,
        "report_status": report["status"],
        "codes": sorted(codes),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evals",
        type=Path,
        default=ROOT / "evals" / "evals.json",
        help="Path to evals.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional JSON report path",
    )
    args = parser.parse_args(argv)

    payload = json.loads(args.evals.read_text(encoding="utf-8"))
    audit_mod = load_auditor()
    results = [run_one(audit_mod.audit, case) for case in payload["evals"]]
    failed = [item for item in results if not item["ok"]]
    summary = {
        "skill_name": payload.get("skill_name"),
        "version": payload.get("version"),
        "total": len(results),
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "results": results,
    }

    text = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
