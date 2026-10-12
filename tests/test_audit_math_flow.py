#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_math_flow.py"
RUN_EVALS = ROOT / "scripts" / "run_evals.py"
EXAMPLE = ROOT / "references" / "examples" / "self-attention.md"
FIXTURES = ROOT / "evals" / "fixtures"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AuditMathFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit_mod = load_module(SCRIPT, "audit_math_flow")

    def test_example_self_attention_passes_semantic_steps(self) -> None:
        report = self.audit_mod.audit(EXAMPLE.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "pass", report)
        self.assertGreaterEqual(report["stats"]["steps"], 4)
        self.assertLessEqual(report["stats"]["steps"], 6)

    def test_residual_named_add_passes(self) -> None:
        card = (FIXTURES / "residual_add_ok.md").read_text(encoding="utf-8")
        report = self.audit_mod.audit(card)
        self.assertEqual(report["status"], "pass", report)

    def test_missing_section_fails(self) -> None:
        card = EXAMPLE.read_text(encoding="utf-8")
        card = card.replace(
            "## 4. 具体输出总结",
            "## 4. Output",
        )
        report = self.audit_mod.audit(card)
        self.assertEqual(report["status"], "fail")
        codes = {item["code"] for item in report["findings"]}
        self.assertIn("missing_section", codes)

    def test_missing_step_formula_is_error(self) -> None:
        card = (FIXTURES / "missing_step_formula.md").read_text(encoding="utf-8")
        report = self.audit_mod.audit(card)
        self.assertEqual(report["status"], "fail")
        codes = {item["code"] for item in report["findings"]}
        self.assertIn("step_missing_formula", codes)
        levels = {
            item["code"]: item["level"]
            for item in report["findings"]
            if item["code"] == "step_missing_formula"
        }
        self.assertEqual(levels["step_missing_formula"], "error")

    def test_unknown_input_tensor_is_error(self) -> None:
        card = (FIXTURES / "unknown_input.md").read_text(encoding="utf-8")
        report = self.audit_mod.audit(card)
        codes = {item["code"] for item in report["findings"]}
        self.assertIn("unknown_input_tensor", codes)
        self.assertEqual(report["status"], "fail")

    def test_anonymous_residual_is_error(self) -> None:
        card = (FIXTURES / "anonymous_residual.md").read_text(encoding="utf-8")
        report = self.audit_mod.audit(card)
        codes = {item["code"] for item in report["findings"]}
        self.assertIn("anonymous_multi_io", codes)
        self.assertEqual(report["status"], "fail")

    def test_canonical_coverage_mismatch_is_error(self) -> None:
        card = (FIXTURES / "canonical_bad_coverage.md").read_text(encoding="utf-8")
        report = self.audit_mod.audit(card)
        codes = {item["code"] for item in report["findings"]}
        self.assertIn("canonical_coverage_mismatch", codes)
        self.assertEqual(report["status"], "fail")

    def test_per_step_missing_inputs_is_error(self) -> None:
        card = (FIXTURES / "residual_add_ok.md").read_text(encoding="utf-8")
        card = card.replace("**输入张量：** `X:(B, N, C), F:(B, N, C)`\n\n", "")
        report = self.audit_mod.audit(card)
        codes = {item["code"] for item in report["findings"]}
        self.assertIn("step_missing_inputs", codes)

    def test_unrenderable_latex_is_error(self) -> None:
        card = (FIXTURES / "residual_add_ok.md").read_text(encoding="utf-8")
        card = card.replace("Y=X+F", r"Y=\text{中文}+F")
        report = self.audit_mod.audit(card)
        codes = {item["code"] for item in report["findings"]}
        self.assertIn("invalid_latex", codes)

    def test_complex_inline_math_is_error(self) -> None:
        card = (FIXTURES / "complex_inline_math.md").read_text(encoding="utf-8")
        report = self.audit_mod.audit(card)
        codes = {item["code"] for item in report["findings"]}
        self.assertIn("complex_inline_math", codes)
        self.assertIn("input_shape_missing", codes)
        self.assertEqual(report["status"], "fail")

    def test_executable_evals_all_pass(self) -> None:
        runner = load_module(RUN_EVALS, "run_evals")
        payload = json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
        results = [runner.run_one(self.audit_mod.audit, case) for case in payload["evals"]]
        failed = [item for item in results if not item["ok"]]
        self.assertEqual(failed, [], failed)


if __name__ == "__main__":
    unittest.main()
