# Module family: attention

Extra checks for attention-style modules (Self/Cross-Attention, SRA, Linear Attention, Deformable Attention, etc.).

## Must define

- Whether Q/K/V come from the same tensor (self) or different tensors (cross)
- Head layout: $h$, $d_h$, and whether shapes are `(B, h, N, d_h)` or `(B, N, h, d_h)`
- Similarity form: scaled dot-product, additive, cosine, kernelized, etc.
- Softmax / normalization axis
- Any spatial/token reduction on K/V (e.g. SRA pooling, stride, depthwise conv) with exact pre/post shapes
- Output projection $W_O$ and residual path if claimed by the paper

## Common failure modes to avoid

- Forgetting $\sqrt{d_h}$ scaling when the paper uses scaled dot-product
- Writing `(B, N, N)` attention maps without the head axis when multi-head is used
- Omitting the reduction ratio $r$ shape effect in SRA-like blocks
- Mixing sequence-first and channel-first layouts mid-flow without a transpose step
