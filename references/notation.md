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

## Named tensor grammar

Write tensors as `Name:(shape)` inside Inputs / Outputs / Dimension Transformation.

```text
X:(B, N, C)
Q:(B, h, N, d_h)
```

### Unary

```text
X:(B, N, C) -> Q:(B, N, d)
```

### Matmul / bmm

```text
Q:(B, h, N, d_h) x KT:(B, h, d_h, N) -> Scores:(B, h, N, N)
```

### Residual / element-wise add

```text
X:(B, N, C) + F:(B, N, C) -> Y:(B, N, C)
```

### Element-wise mul (Hadamard)

```text
G:(B, N, C) odot H:(B, N, C) -> Z:(B, N, C)
```

Use ASCII `odot` in the dimension line; keep $\odot$ in LaTeX formulas.

### Multi-output split

```text
Z:(B, N, 3d) -> Q:(B, N, d), K:(B, N, d), V:(B, N, d)
```

### Branches

No special arrow is required. Define `X` once, then list `X:(...)` again in later steps' **Inputs**.

### Residuals with identity path

Treat the skip tensor as an ordinary named input to an add/fuse step. Do not hide it inside an anonymous `(B,N,C) -> (B,N,C)` line.

## Operator specificity

- Matrix product: juxtaposition in formulas; `x` in dimension lines
- Batched matmul: keep batch/head axes explicit in shapes
- Element-wise: $\odot$ in LaTeX; `odot` or `+` in dimension lines
- Softmax: name the axis, e.g. $\mathrm{softmax}_{N_k}(\cdot)$
- Layout-only ops still get their own Step (`Reshape` / `Transpose` / `Permute`)
