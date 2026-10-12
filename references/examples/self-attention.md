# 自注意力示例

触发语：`使用math-flow解析论文中自注意力模块`

---

> 模块：自注意力
> 来源模式：通用定义
> 模块类型：注意力
> 来源覆盖：仅通用知识
> 假设：批大小 B；序列长度 N；输入维度 C；投影维度 d=C；头数 h；单头维度 d_h=d/h
> 布局约定：序列 (B, N, C)

## 1. 模块原理总结

自注意力通过查询、键和值计算序列内部的相关性，并对全局信息进行加权聚合，使每个位置都能根据内容选择性地获取其他位置的信息。

## 2. 具体输入定义

- 输入特征：批量序列特征。

$$
X\in\mathbb{R}^{B\times N\times C}
$$

- 投影矩阵：

$$
W_Q,W_K,W_V\in\mathbb{R}^{C\times d},\quad W_O\in\mathbb{R}^{d\times C}
$$

## 3. 完整数据流转过程

#### 步骤 1：查询、键、值投影与多头变形

**输入张量：** `X:(B, N, C)`

**数学公式：**

$$
Q_h=\operatorname{reshape}(XW_Q),\quad K_h=\operatorname{reshape}(XW_K),\quad V_h=\operatorname{reshape}(XW_V)
$$

**输出张量：** `Q_h:(B, h, N, d_h), K_h:(B, h, N, d_h), V_h:(B, h, N, d_h)`

**维度变换：** `X:(B, N, C) -> Q_h:(B, h, N, d_h), K_h:(B, h, N, d_h), V_h:(B, h, N, d_h)`

**作用：** 一步完成三组线性投影与多头布局变换，避免引入只用于过渡的投影张量。

#### 步骤 2：缩放点积与权重归一化

**输入张量：** `Q_h:(B, h, N, d_h), K_h:(B, h, N, d_h)`

**数学公式：**

$$
A=\operatorname{softmax}_{N}\left(\frac{Q_hK_h^{\mathsf{T}}}{\sqrt{d_h}}\right)
$$

**输出张量：** `A:(B, h, N, N)`

**维度变换：** `Q_h:(B, h, N, d_h) x K_h:(B, h, N, d_h) -> A:(B, h, N, N)`

**作用：** 直接得到各注意力头在键序列维上的归一化权重。

#### 步骤 3：值聚合与多头合并

**输入张量：** `A:(B, h, N, N), V_h:(B, h, N, d_h)`

**数学公式：**

$$
H=\operatorname{reshape}(AV_h)
$$

**输出张量：** `H:(B, N, d)`

**维度变换：** `A:(B, h, N, N) x V_h:(B, h, N, d_h) -> H:(B, N, d)`

**作用：** 对值向量加权聚合，并直接合并所有注意力头。

#### 步骤 4：输出投影

**输入张量：** `H:(B, N, d)`

**数学公式：**

$$
Y=HW_O
$$

**输出张量：** `Y:(B, N, C)`

**维度变换：** `H:(B, N, d) -> Y:(B, N, C)`

**作用：** 将多头聚合特征映射回输入通道维度。

## 4. 具体输出总结

- 最终输出：融合全局上下文后的序列特征，可继续进入残差连接、归一化层或前馈网络。

$$
Y\in\mathbb{R}^{B\times N\times C}
$$
