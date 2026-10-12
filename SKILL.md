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

选择一种来源模式，并在输出状态头中使用对应中文值：

| 状态头取值 | 适用情况 | 规则 |
|------|------|------|
| `论文公式` | 论文给出明确公式 | 优先沿用论文符号，并注明公式或章节 |
| `论文结构` | 论文只有文字或框图描述 | 忠实重建数学流，并标注为 `[分析]` |
| `通用定义` | 没有可靠的论文材料 | 使用标准定义，并显式标注假设 |

不得静默混用教材通用版本与论文特有版本。

### 4. Classify module family

依据 `manifest.yaml` → `axes.module_family` 选择一个模块类型并加载相应片段。内部路由键与状态头中文值对应如下：

- `attention` → `注意力`
- `convolution` → `卷积`
- `normalization` → `归一化`
- `aggregation` → `聚合`
- `recurrent` → `循环`
- `generic` → `通用`（无法确定时）

### 5. Draft the fixed 4-section card

Apply in order:

1. core principles
2. selected module-family fragment
3. core workflow
4. output contract

撰写时：

- 第 2/3/4 节中所有形状定义与计算式一律使用三行块级 `$$` 公式；
- 行内 `$...$` 仅允许极简单符号（如 `$X$`、`$N$`），禁止行内写 `\in`、上下标或命令；
- 第 3 节按语义完整阶段拆分；每一步包含**输入张量**、**数学公式**、**输出张量**、**维度变换**、**作用**；
- 分支、残差和多输入输出使用命名张量语法。

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
5. Optionally run executable evals: `python "SKILL_DIR/scripts/run_evals.py"`.
6. Never invent a replacement auditor during a normal run.

## Trigger Condition

Activate when the user input matches or contains:

```text
使用math-flow解析论文中[模块名称]模块
```

Examples: `使用math-flow解析论文中SRA模块`, `使用math-flow解析论文中Self-Attention模块`.

Near-synonym triggers: explicit requests for math-flow / 数学数据流 / 张量维度流转解析 of a paper module.

## 语言

所有输出标题、字段名、状态信息和解释文字均使用简体中文。仅保留论文固有模块名、标准缩写及数学符号。章节标题严格使用输出契约规定的纯中文标题。

## Additional resources

- User docs: [README.md](README.md) / [README_EN.md](README_EN.md)
- Evals: [evals/evals.json](evals/evals.json)
