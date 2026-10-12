# Output contract

Default deliverable:

```text
math-flow-<module-slug>.md
```

Also emit when auditing from a file:

```text
audit-report.json
```

## Evidence-status header (required)

Place this block at the top of the card, before Section 1:

```markdown
> Module: <name>
> Source mode: paper-equation / paper-structure / canonical-fallback
> Module family: attention / convolution / normalization / aggregation / recurrent / generic
> Source coverage: Full module equations / Partial description / Canonical knowledge only
> Assumptions: <semicolon-separated list, or None>
> Layout convention: e.g. tokens (B, N, C) / image (B, C, H, W)
```

## Fixed body structure (mandatory)

**必须严格遵循以下 4 段结构，不得跳过任一节。** Section headings must match exactly:

### 1. 模块原理总结 (Module Principle Summary)

- Provide a concise summary of the module's core theoretical principle and its purpose in the network (e.g., "What problem does it solve?", "What is its core mathematical innovation?").
- Keep this conceptual and high-level before diving into the specific math.

### 2. 具体输入定义 (Specific Input Definition)

- Define all specific input variables mathematically.
- Explicitly state the initial tensor shapes/dimensions using standard notation (e.g., $X \in \mathbb{R}^{B \times C \times H \times W}$ for image features, or $P \in \mathbb{R}^{B \times N \times 3}$ for point clouds).
- Explain the physical/semantic meaning of each specific input (e.g., Query, Key, Value, or Coordinate inputs).

### 3. 完整数据流转过程 (Complete Mathematical Data Flow)

Break down the module's internal processes sequentially. For EACH step in the flow, provide:

- **Operation Name:** The name of the process (e.g., Linear Projection, Spatial Reduction, Feature Concatenation).
- **Mathematical Formula:** The exact mathematical operation. Use block LaTeX for standalone equations (e.g., $$Q = X W_q$$).
- **Dimension Transformation:** Show exactly how the tensor shape changes in this specific step (e.g., `(B, N, C) -> (B, N, D)`).
- **Explanation:** A brief description of what this step achieves functionally.

Use this per-step template:

```markdown
#### Step k: <Operation Name>

**Mathematical Formula:**

$$
<equation>
$$

**Dimension Transformation:** `(in_shape) -> (out_shape)`

**Explanation:** <一句话功能说明>
```

### 4. 具体输出总结 (Specific Output Summary)

- Define the final specific output variable.
- State its final tensor shape.
- Briefly explain what this output represents and how it seamlessly feeds into the next module of the network.

## Formatting Rules

- Use inline LaTeX `$equation$` for variables in text and block LaTeX `$$equation$$` for standalone formulas. Ensure no spaces between the `$` and the equation.
- Be highly specific about matrix multiplications, element-wise operations (Hadamard product $\odot$), concatenations, and nonlinear activations.
- If the user does not specify hyperparameter sizes, explicitly state your reasonable assumptions (e.g., assuming batch size $B$, sequence length $N$, hidden dimension $d$).
- Always respond in Chinese, maintaining academic and rigorous engineering terminology.

## Quality gates (block delivery)

Block final delivery when:

- any of Sections 1–4 is missing or out of order;
- an input/output lacks symbol or shape;
- a Section-3 step lacks formula or dimension transformation;
- dimension chain is discontinuous without an explicit reshape/view step;
- `canonical-fallback` is used but assumptions are hidden;
- auditor reports any `error`.
