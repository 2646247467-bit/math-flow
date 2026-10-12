# Workflow

Follow this checklist every run. Copy it mentally and mark progress.

```text
Math-Flow Progress:
- [ ] 1. Identify module + source mode + module family
- [ ] 2. Freeze symbol & shape assumptions
- [ ] 3. 按语义阶段撰写第 1–4 节，并使用命名输入输出
- [ ] 4. Verify tensor-graph producers/consumers
- [ ] 5. Run audit_math_flow.py and fix errors
- [ ] 6. Deliver card (+ audit-report.json when file-based)
```

## Step 1 — Bound the problem

Record:

- module name;
- 来源模式（`论文公式` / `论文结构` / `通用定义`）；
- module family;
- available evidence (equation numbers, section titles, figure ids, code paths).

在“论文公式”或“论文结构”模式下，若论文版本与教材通用版本不同，必须优先采用论文版本。

## Step 2 — Freeze inputs and assumptions

Before Section 3:

1. Define every input tensor with $\in \mathbb{R}^{\ldots}$.
2. List learnable parameters that change shape.
3. State missing hyper-parameters as `[Assumption]` (example: batch $B$, heads $h$, reduction ratio $r$).
4. Prefer `(B, C, H, W)` for image feature maps and `(B, N, C)` for token sequences unless the paper uses another layout; document the layout once.

## 步骤 3——按语义阶段展开数据流

每一步应对应读者能理解的完整计算阶段，而不是一个底层算子。

可以合并：

- 线性投影与紧随其后的 reshape/transpose；
- 缩放点积与 Softmax；
- 多头合并与输出投影；
- 仅用于过渡且不被复用的相邻操作。

必须拆开：

- 中间结果被多个步骤复用或形成分支；
- 残差/门控需要显式展示多输入；
- 合并后无法清楚表达维度变化；
- 论文明确将其作为独立创新阶段讨论。

例如多头自注意力通常使用 4–6 个阶段，而非把每次 reshape、transpose、scale 都拆成独立步骤。

每一步填写：`输入张量` / `数学公式` / `输出张量` / `维度变换` / `作用`。

Branch / residual guidance:

- Branch: reuse the same upstream name (e.g. `X`) in multiple later **Inputs** lines.
- Residual: `X:(...) + F:(...) -> Y:(...)` with both names previously defined.
- Multi-output: list every produced name on **Outputs**.

## Step 4 — Close the loop on outputs

Section 4 must state:

- final symbol(s) and shape(s);
- residual/identity paths if present;
- how the tensor feeds the next block (e.g. FFN, residual add, decoder cross-attn).

Final symbols must be produced by some Section-3 step.

## Step 5 — Self-check before audit

- Section order locked: 1 → 2 → 3 → 4
- 第 2/4 节形状与第 3 节计算式全部为块级 `$$` 公式
- 不存在复杂行内 `$...$`（含 `\in`、上下标、命令等）
- 输入张量名称均可追溯
- 块公式的 `$$` 各自独占一行，花括号配对，数学环境内无中文或 Markdown
- 全部标题、字段名、解释文字均为中文

## Step 6 — Audit

Run the bundled auditor on the draft file.

- Treat every `error` as a delivery blocker.
- `warning` is reserved for non-blocking style hints only; contract violations must be errors.
