# Workflow

Follow this checklist every run. Copy it mentally and mark progress.

```text
Math-Flow Progress:
- [ ] 1. Identify module + source mode + module family
- [ ] 2. Freeze symbol & shape assumptions
- [ ] 3. Draft Sections 1–4
- [ ] 4. Verify dimension-chain continuity
- [ ] 5. Run audit_math_flow.py and fix errors
- [ ] 6. Deliver card (+ audit-report.json when file-based)
```

## Step 1 — Bound the problem

Record:

- module name;
- source mode (`paper-equation` / `paper-structure` / `canonical-fallback`);
- module family;
- available evidence (equation numbers, section titles, figure ids, code paths).

If both a paper variant and a common textbook variant exist, prefer the paper variant in `paper-*` modes.

## Step 2 — Freeze inputs and assumptions

Before Section 3:

1. Define every input tensor with $\in \mathbb{R}^{\ldots}$.
2. List learnable parameters that change shape.
3. State missing hyper-parameters as `[Assumption]` (example: batch $B$, heads $h$, reduction ratio $r$).
4. Prefer `(B, C, H, W)` for image feature maps and `(B, N, C)` for token sequences unless the paper uses another layout; document the layout once.

## Step 3 — Expand the data flow

Decompose into the smallest steps that change math or shape. Typical atoms:

- linear / conv projection
- reshape, transpose, permute, flatten
- matmul / bmm
- element-wise ops (`+`, $\odot$, broadcast)
- reductions (mean/sum/max, softmax over a named axis)
- normalization / activation
- concat / stack / split
- interpolate / patch merge / gather

For each step, fill the Section-3 template from the output contract. Do not skip broadcasting axes; name the softmax/reduce dimension.

## Step 4 — Close the loop on outputs

Section 4 must state:

- final symbol(s) and shape(s);
- residual/identity paths if present;
- how the tensor feeds the next block (e.g. FFN, residual add, decoder cross-attn).

If the module returns multiple tensors (e.g. attn weights + features), define each.

## Step 5 — Self-check before audit

- Section order locked: 1 → 2 → 3 → 4
- No unexplained shape jumps
- LaTeX: inline `$...$`, block `$$...$$`, no spaces inside the delimiters next to the fence markers incorrectly; no spaces between `$` and equation content
- Chinese prose + bilingual required headings

## Step 6 — Audit

Run the bundled auditor on the draft file. Treat `error` findings as blockers and `warning` findings as fix-or-justify.
