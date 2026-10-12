# Notation conventions

Use these defaults unless the paper defines others. State deviations in the card header `Layout convention` field.

## Common layouts

| Domain | Default shape | Notes |
|--------|---------------|-------|
| Image features | $X \in \mathbb{R}^{B \times C \times H \times W}$ | channel-first |
| Token / sequence | $X \in \mathbb{R}^{B \times N \times C}$ | batch, length, channel |
| Point cloud | $P \in \mathbb{R}^{B \times N \times 3}$ | optionally with features $F \in \mathbb{R}^{B \times N \times C}$ |
| Attention scores | $A \in \mathbb{R}^{B \times h \times N_q \times N_k}$ | include head axis when multi-head |

## Symbols

- $B$: batch size
- $C$: channel / embedding width
- $H, W$: spatial height/width
- $N$: token or point count
- $d$: projected width; $d_h = d / h$ for head width
- $h$: number of heads
- $r$: reduction ratio (SRA-like)

## Dimension transformation grammar

Write shapes in contiguous ASCII tuples:

```text
(B, N, C) -> (B, N, d)
```

For multi-operand steps, show the contracting product:

```text
(B, h, N, d_h) x (B, h, d_h, N) -> (B, h, N, N)
```

If only a view changes, still add a step named `Reshape` / `Transpose` / `Permute`.

## Operator specificity

- Matrix product: juxtaposition or $\times$ with axes implied by shapes
- Batched matmul: state batch/head axes as broadcasted
- Element-wise: use $\odot$ or explicit `element-wise`
- Softmax: name the axis, e.g. $\mathrm{softmax}_{N_k}(\cdot)$
