# `math-flow` Skill

[中文](README.md)

`math-flow` deconstructs a single academic-paper module into a **reviewable mathematical data flow**: principle → typed inputs → step-wise formulas with tensor shapes → outputs that feed the next block.

It targets deep-learning / computer-vision modules (Attention, SRA, conv variants, normalization, aggregation, …), not whole-paper summarization.

## Good fit

- Recover exact input/intermediate/output shapes for a module
- Cross-check implementations against paper equations
- Reconstruct math from prose/figures with explicit `[Analysis]` / `[Assumption]` labels
- Validate card structure with the bundled auditor

## Example prompts

```text
使用math-flow解析论文中Self-Attention模块
```

```text
使用math-flow解析论文中SRA模块
```

Near-synonyms in English also work, e.g. “Run math-flow on the SRA module and show tensor shapes.”

## Inputs you should provide

- Module name (required)
- Paper equations / excerpts / PDF / reference implementation (optional, strongly recommended)
- Known hyperparameters such as $B,N,C,d,h,r$ (optional; otherwise stated as assumptions)

## How it works

1. Load `manifest.yaml` and `static/core/` contracts.
2. Choose a source mode: `paper-equation` / `paper-structure` / `canonical-fallback`.
3. Load one module-family fragment.
4. Emit the fixed four-section card plus status header.
5. Run `scripts/audit_math_flow.py` and fix errors before delivery.

## Outputs

- `math-flow-<module>.md`
- `audit-report.json`

### Fixed sections

1. Module Principle Summary
2. Specific Input Definition
3. Complete Mathematical Data Flow
4. Specific Output Summary

## Install

Clone into the Cursor personal skills directory:

```bash
git clone <your-repo-url> ~/.cursor/skills/math-flow
```

Or vendor it as a project skill under `.cursor/skills/math-flow`.

## Audit, evals & tests

```bash
python scripts/audit_math_flow.py path/to/math-flow-self-attention.md --output audit-report.json
python scripts/run_evals.py
python -m unittest discover -s tests -v
```

`evals/evals.json` references executable fixtures with expected auditor `status` and required error codes.

## License

MIT — see [LICENSE](LICENSE)
