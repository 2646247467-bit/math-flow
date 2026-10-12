# Module family: attention

Extra checks for attention-style modules (Self/Cross-Attention, SRA, Linear Attention, Deformable Attention, etc.).

## Must define

- Whether Q/K/V come from the same tensor (self) or different tensors (cross)
- Head layout: $h$, $d_h$, and whether shapes are `(B, h, N, d_h)` or `(B, N, h, d_h)`
- Similarity form: scaled dot-product, additive, cosine, kernelized, etc.
- Softmax / normalization axis
- Any spatial/token reduction on K/V (e.g. SRA pooling, stride, depthwise conv) with exact pre/post shapes
- Output projection $W_O$ and residual path if claimed by the paper

## 推荐步骤粒度

多头注意力通常压缩为以下语义阶段：

1. Q/K/V 投影与多头变形（可一步完成，直接输出 $Q_h,K_h,V_h$）
2. 缩放点积与 Softmax（直接输出注意力权重 $A$）
3. Value 聚合与多头合并（直接输出合并后的特征）
4. 输出投影
5. 残差相加（仅当属于模块边界时）

若 K/V 具有空间缩减、稀疏采样或其他论文创新，应把该过程单独成步。

## Common failure modes to avoid

- Forgetting $\sqrt{d_h}$ scaling when the paper uses scaled dot-product
- Writing `(B, N, N)` attention maps without the head axis when multi-head is used
- Omitting the reduction ratio $r$ shape effect in SRA-like blocks
- Mixing sequence-first and channel-first layouts mid-flow without a transpose step
- 把“权重计算”和“Value 聚合”全部塞入同一步，导致关键注意力矩阵不可见
- 为投影、reshape、transpose 分别创建只使用一次的冗余中间符号
