# Example: Self-Attention

Trigger: `使用math-flow解析论文中Self-Attention模块`

---

> Module: Self-Attention
> Source mode: canonical-fallback
> Module family: attention
> Source coverage: Canonical knowledge only
> Assumptions: batch $B$; sequence length $N$; input width $C$; projected width $d=C$; heads $h$ with $d_h=d/h$; layout `(B, N, C)`
> Layout convention: tokens (B, N, C)

## 1. 模块原理总结 (Module Principle Summary)

Self-Attention 通过对同一特征序列构造 Query / Key / Value，用相似度加权聚合全局上下文，使每个位置都能依赖任意其他位置。其核心数学创新是用缩放点积注意力将序列建模为可并行的加权求和，而非递推依赖。

## 2. 具体输入定义 (Specific Input Definition)

- 输入特征：$X \in \mathbb{R}^{B \times N \times C}$，每个 token 的特征向量。`[Canonical]`
- 投影矩阵：$W_Q, W_K, W_V \in \mathbb{R}^{C \times d}$，$W_O \in \mathbb{R}^{d \times C}$。`[Canonical]`

## 3. 完整数据流转过程 (Complete Mathematical Data Flow)

#### Step 1: Linear Projection (Q/K/V)

**Mathematical Formula:**

$$
Q = X W_Q,\quad K = X W_K,\quad V = X W_V
$$

**Dimension Transformation:** `(B, N, C) -> (B, N, d)`（对 $Q,K,V$ 各自成立）

**Explanation:** 将输入映射到查询、键、值空间，为相似度计算与特征聚合做准备。

#### Step 2: Multi-Head Reshape

**Mathematical Formula:**

$$
Q \leftarrow \mathrm{Reshape}(Q) \in \mathbb{R}^{B \times h \times N \times d_h}
$$

（$K,V$ 同理）

**Dimension Transformation:** `(B, N, d) -> (B, h, N, d_h)`

**Explanation:** 将通道维拆成多头，使各子空间可并行学习不同关系模式。

#### Step 3: Scaled Dot-Product Attention

**Mathematical Formula:**

$$
A = \mathrm{softmax}\left(\frac{Q K^{\top}}{\sqrt{d_h}}\right),\quad
H = A V
$$

**Dimension Transformation:**  
`QK^T: (B, h, N, d_h) x (B, h, d_h, N) -> (B, h, N, N)`；  
`AV: (B, h, N, N) x (B, h, N, d_h) -> (B, h, N, d_h)`

**Explanation:** 用缩放点积得到注意力权重，再对 Value 做加权求和，聚合全局上下文。

#### Step 4: Concatenate Heads + Output Projection

**Mathematical Formula:**

$$
Y = \mathrm{Concat}(H_1,\ldots,H_h)\, W_O
$$

**Dimension Transformation:** `(B, h, N, d_h) -> (B, N, d) -> (B, N, C)`

**Explanation:** 合并多头表示并投影回原通道维，得到可与残差/FFN 衔接的输出特征。

## 4. 具体输出总结 (Specific Output Summary)

- 最终输出：$Y \in \mathbb{R}^{B \times N \times C}$
- 语义：与输入同形状的上下文增强特征；通常经残差连接与 LayerNorm 后送入 FFN 或下一 Transformer Block。
