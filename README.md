# `math-flow` Skill

[English](README_EN.md)

`math-flow` 用于把论文中的算法模块拆成**可复核的数学数据流**：先给原理，再定义输入张量，再逐步写出公式与维度变换，最后给出输出如何接入后续网络。

它适合精读深度学习 / 计算机视觉论文里的具体模块（Attention、SRA、Conv 变体、归一化、聚合等），而不是写整篇论文摘要。

## 适合用它做什么

- 搞清某个模块「输入是什么、中间怎么变、输出什么形状」
- 对照论文公式核对实现时的 tensor layout
- 在公式缺失时，用结构化重建标出 `[Analysis]` / `[Assumption]`
- 用内置审计脚本检查四段结构与维度书写是否完整

## 典型请求

```text
使用math-flow解析论文中Self-Attention模块
```

```text
使用math-flow解析论文中SRA模块
```

```text
这篇只有框图没有公式。使用math-flow解析论文中Cross-Attention模块。
```

## 你需要提供

- 模块名称（必需）
- 论文公式 / 原文摘录 / PDF 页 / 仓库实现（可选但强烈建议）
- 已知超参：如 $B,N,C,d,h,r$（可选；缺失时会显式假设）

## 工作方式

1. 读取 `manifest.yaml` 与 `static/core/` 契约。
2. 判定来源模式：`paper-equation` / `paper-structure` / `canonical-fallback`。
3. 选择模块族 fragment（attention、convolution、…）。
4. 生成固定四段 Math-Flow 卡片 + 页眉状态行。
5. 运行 `scripts/audit_math_flow.py`，错误修复后交付。

## 产出

- `math-flow-<module>.md`：页眉 + 第 1–4 节
- `audit-report.json`：结构 / 维度书写审计结果

### 四段结构（不可变）

1. 模块原理总结 (Module Principle Summary)
2. 具体输入定义 (Specific Input Definition)
3. 完整数据流转过程 (Complete Mathematical Data Flow)
4. 具体输出总结 (Specific Output Summary)

## 安装

### Cursor 个人 Skill

将本仓库克隆到：

```text
~/.cursor/skills/math-flow
```

Windows 示例：

```powershell
git clone <your-repo-url> "$env:USERPROFILE\.cursor\skills\math-flow"
```

### 项目级 Skill

复制或子模块到：

```text
.cursor/skills/math-flow
```

## 运行审计

```bash
python scripts/audit_math_flow.py path/to/math-flow-self-attention.md --output audit-report.json
```

运行单测：

```bash
python -m unittest discover -s tests -v
```

## 仓库结构

```text
math-flow/
├── SKILL.md                 # Agent 路由入口
├── manifest.yaml            # 声明式加载与模块族轴
├── static/core/             # 原则 / 工作流 / 输出契约
├── static/fragments/        # 模块族专项检查
├── references/              # 记号、来源标注、示例
├── scripts/audit_math_flow.py
├── tests/
├── evals/evals.json
└── agents/openai.yaml
```

## 边界

- 一次聚焦**一个模块**，不生成整篇论文精读卡（请用 `nature-paper-card` 一类技能）。
- 不把缺失公式伪装成论文原文；canonical 模式必须写明假设。
- 不在普通运行中临时编写替代审计脚本。

## License

MIT — 见 [LICENSE](LICENSE)
