# Changelog

All notable changes to this project will be documented in this file.

## [1.3.0] - 2026-10-12

### Changed

- 第 2/4 节形状定义强制使用块级 `$$`，禁止复杂行内 `$...$`
- 行内公式仅允许简单标识符（如 `$X$`）；含 `\in`、上下标、命令者一律报错
- 状态头假设改为纯 ASCII，不再夹杂复杂行内公式
- 示例与评测 fixture 同步为块公式写法

## [1.2.0] - 2026-10-12

### Changed

- 输出标题、状态头和步骤字段统一为中文
- 增加稳定 LaTeX 子集与渲染审计：三行块公式、配对花括号、禁用冲突环境
- 步骤粒度由“单算子原子步骤”改为“语义完整阶段”
- 自注意力示例由 13 个细碎步骤压缩为 4 个语义阶段
- 可执行评测新增最大步骤数约束，防止过度拆分回归

## [1.1.0] - 2026-10-12

### Changed

- Contract/auditor aligned: former soft blockers are now hard `error`s
- Per-step validation for Inputs / formula / Outputs / Dimension Transformation / Explanation
- Dimension model upgraded from linear chain to named tensor graph (branch / residual / multi-IO)
- Self-Attention example split into atomic steps (13 steps)
- `evals/evals.json` now drives executable fixtures via `scripts/run_evals.py`
- Expanded unit tests covering pass/fail auditor codes

## [1.0.0] - 2026-10-12

### Added

- Router-style `SKILL.md` with declarative `manifest.yaml`
- Core contracts: principles, workflow, output contract (fixed 4-section card)
- Module-family fragments: attention / convolution / normalization / aggregation / recurrent / generic
- Source modes: `paper-equation` / `paper-structure` / `canonical-fallback`
- References for notation and provenance labeling
- Worked example: Self-Attention
- Bundled auditor `scripts/audit_math_flow.py` + unit tests
- Eval prompts in `evals/evals.json`
- Bilingual README and MIT license
