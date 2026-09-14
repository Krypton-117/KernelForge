# Kernel-Forge

Kernel-Forge 是一个面向 **Kernel 铸造** 的本地整合包。它把论文与文档依据、可复用的方法、外部工具连接和跨会话连续性放在一起，帮助我们持续研究、设计、验证和迭代 Learner-Kernel。

它本身不是 Learner-Kernel，而是铸造 Learner-Kernel 所需的研究与工程底座：

- **Method Bank**：保存可复用、可追溯的方法卡片。
- **PaperPipe / PaperQA**：管理论文，检索内容并保留引用依据。
- **Context7 MCP**：查询带版本的外部技术文档。
- **agent-handoff**：保存项目状态，使工作可以跨会话恢复。

当前版本是 Kernel-Forge v0.1，使用 Conda base 环境运行。

## Method Bank

Method Bank 是 Kernel-Forge 中最核心、也是我们自己编写的部分。它不是普通的笔记目录，而是一个可以被程序检索和复用的方法库。

一张方法卡片记录一个相对稳定的做法：它解决什么问题、适用于什么范围、执行时有哪些约束、怎样判断结果可靠，以及它来自哪篇论文或哪份文档的哪个位置。方法、来源和定位信息分开保存，因此同一个方法可以关联多个证据来源，来源也可以被多个方法复用。方法还可以经历候选、审核和修订过程。

它产生的缘由很简单：铸造 Kernel 时，真正容易丢失的不是某个文件，而是“当时为什么这样做、依据在哪里、下次遇到类似问题该复用哪套步骤”。把这些经验写成可检索、可追溯的方法卡片，Kernel 的形成过程就从一次性探索变成可以积累的工程资产。

它的创新思想也在这里：我们保存的不是零散结论，而是连接 **问题 → 方法 → 证据 → 审核** 的最小闭环。这样，后续设计可以先检索已有方法，再针对具体情境取回原始证据；新方法也能在保留出处和判断过程的前提下加入库中。

Method Bank 使用 SQLite/FTS5 存储，并通过 MCP 提供方法和来源的写入、检索、读取及审核接口。实现位于 [`method-bank/`](method-bank/)，接口约定见 [`docs/METHOD_SCHEMA.md`](docs/METHOD_SCHEMA.md)。

## 使用

使用现有 Conda **base** Python 3.12.9：

```powershell
$py = '<conda-base-python>'
& $py -X utf8 -m unittest discover -s method-bank/tests -v
& $py -X utf8 method-bank/src/kernel_forge_method_bank/server.py
```

PaperPipe、PaperQA 和 Context7 的配置与上游文档见 [`docs/TOOLING.md`](docs/TOOLING.md)。项目状态恢复入口是 [`WORKSTATE.md`](WORKSTATE.md) 和 [`AGENT_HANDOFF.md`](AGENT_HANDOFF.md)。

测试使用的论文只存在于本地验证数据目录，不随仓库发布；重新验证时按工具文档自行获取对应来源。

## Contributors

- **Krypton-117**：构想、需求与方向。
- **OpenAI Codex（AI 编程助手）**：代码实现、测试与文档整理。

## 许可证

Kernel-Forge 自己编写的代码采用 MIT License，见 [`LICENSE`](LICENSE)。依赖的 skill、MCP、库、论文和文档仍受各自上游许可证、版权和服务条款约束。
