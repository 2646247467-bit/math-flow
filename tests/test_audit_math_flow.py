#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_math_flow.py"
EXAMPLE = ROOT / "references" / "examples" / "self-attention.md"


def load_auditor():
    spec = importlib.util.spec_from_file_location("audit_math_flow", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AuditMathFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit_mod = load_auditor()

    def test_example_self_attention_passes(self) -> None:
        card = EXAMPLE.read_text(encoding="utf-8")
        report = self.audit_mod.audit(card)
        self.assertEqual(report["status"], "pass", report)
        self.assertGreaterEqual(report["stats"]["steps"], 3)

    def test_missing_section_fails(self) -> None:
        card = EXAMPLE.read_text(encoding="utf-8")
        card = card.replace(
            "## 4. 具体输出总结 (Specific Output Summary)",
            "## 4. Output",
        )
        report = self.audit_mod.audit(card)
        self.assertEqual(report["status"], "fail")
        codes = {item["code"] for item in report["findings"]}
        self.assertIn("missing_section", codes)


if __name__ == "__main__":
    unittest.main()
