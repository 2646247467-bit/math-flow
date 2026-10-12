---
name: math-flow
description: >-
  Deconstruct academic paper modules (especially deep learning / computer vision)
  into a principle summary plus exact mathematical data flow with tensor shapes.
  Use when the user says 使用math-flow解析论文中[模块名称]模块 (e.g. 使用math-flow解析论文中SRA模块,
  使用math-flow解析论文中Self-Attention模块), or asks for math-flow / 数学数据流 / 张量维度流转解析.
---

# Math-Flow — Router

将论文中的算法模块拆解为：**原理摘要 + 可复核的数学数据流 + 逐步张量维度变换**。

本 skill 不是论文摘要、代码讲解或通用公式默写。默认产出一份固定四段结构的 Math-Flow 卡片，并在来源不足时显式标注假设，而不是静默补全。

## Architecture

- `static/core/`：原则、工作流、输出契约（始终加载）
- `static/fragments/module_family/`：按模块族加载的专项检查
- `references/`：记号约定、来源标注、完整示例（按需读取）
- `scripts/audit_math_flow.py`：结构与维度链审计（草稿完成后运行）

## Routing protocol

每次调用都必须按下列顺序执行。

### 1. Load manifest and core

Read [manifest.yaml](manifest.yaml), then read every file listed under `always_load`. Do not generate the Math-Flow card from this router alone.

### 2. Extract the target module

From the user request, extract:

- module name (e.g. `SRA`, `Self-Attention`);
- optional paper source (PDF, excerpt, equation, repo implementation);
- optional hyper-parameters ($B$, $N$, $C$, $d$, $h$, …).

If the module name is missing, ask once for the module name before drafting.

### 3. Establish source mode

Choose exactly one mode and state it in the card header:

| Mode | When | Rule |
|------|------|------|
| `paper-equation` | Paper gives explicit equations for the module | Prefer paper symbols and formulas; cite equation/section |
| `paper-structure` | Paper describes the module in text/figure without closed-form equations | Reconstruct a faithful math flow; mark reconstructed steps as `[Analysis]` |
| `canonical-fallback` | No reliable paper text for this module | Use the standard/canonical definition; mark assumptions explicitly |

Never silently mix a textbook variant with a paper-specific variant.

### 4. Classify module family

Using `manifest.yaml` → `axes.module_family`, select one primary family and load its fragment:

- `attention`
- `convolution`
- `normalization`
- `aggregation`
- `recurrent`
- `generic` (default when uncertain)

### 5. Draft the fixed 4-section card

Apply in order:

1. core principles
2. selected module-family fragment
3. core workflow
4. output contract

Read [references/notation.md](references/notation.md) before writing shapes.  
Read [references/provenance.md](references/provenance.md) before labeling assumptions or reconstructions.  
Read [references/examples/self-attention.md](references/examples/self-attention.md) only if you need a worked template.

Default deliverable filename: `math-flow-<module>.md` (ASCII slug). Also acceptable: reply inline with the same 4-section body plus header.

### 6. Audit before final delivery

1. Resolve `SKILL_DIR` as the directory containing this loaded `SKILL.md`.
2. Write the draft to a file when possible.
3. Run:

```text
python "SKILL_DIR/scripts/audit_math_flow.py" PATH/TO/math-flow-<module>.md \
  --output PATH/TO/audit-report.json
```

4. If the auditor reports any `error`, fix and re-audit. Do not deliver with unresolved errors.
5. Never invent a replacement auditor during a normal run.

## Trigger Condition

Activate when the user input matches or contains:

```text
使用math-flow解析论文中[模块名称]模块
```

Examples: `使用math-flow解析论文中SRA模块`, `使用math-flow解析论文中Self-Attention模块`.

Near-synonym triggers: explicit requests for math-flow / 数学数据流 / 张量维度流转解析 of a paper module.

## Language

Always respond in Simplified Chinese for explanatory prose. Keep symbols, operator names, and established English technical terms in canonical form. Section titles must follow the output contract exactly (bilingual headings).

## Additional resources

- User docs: [README.md](README.md) / [README_EN.md](README_EN.md)
- Evals: [evals/evals.json](evals/evals.json)
