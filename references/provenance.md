# 来源与诚实性规则

Math-Flow cards must remain usable when the source is incomplete.

## 标签

| 标签 | 含义 | 典型用途 |
|-------|---------|-------------|
| `[论文]` | 论文公式、图或正文直接支持 | 原式或仅做记号统一的公式 |
| `[分析]` | 根据文字或框图重建 | 无闭式公式但算法意图明确 |
| `[假设]` | 来源缺失时作出的设定 | $B$、$h$、填充策略等 |
| `[通用定义]` | 论文外的标准定义 | “通用定义”来源模式 |

## Mode policy

### 论文公式

- Prefer paper symbol names.
- 如果改名，在第 2 节增加“符号对应”条目。
- Do not replace a paper-specific reduction with a textbook attention block.

### 论文结构

- Reconstruct step-by-step math that implements the described module.
- 重建公式标为 `[分析]`。
- 若存在两种同样合理的重建，选择更简洁者，并在“假设”中说明歧义。

### 通用定义

- Allowed when the user names a well-known module without paper text.
- 状态头“来源覆盖”必须为“仅通用知识”。
- State which canonical variant you use (e.g. Vaswani et al. scaled dot-product MHSA).

## Forbidden

- Presenting guesses as paper equations
- Borrowing hyperparameters from an unrelated implementation silently
- Dropping residual connections that the paper includes
- Changing Q/K/V sharing (self vs cross) without evidence
