# docs/ — 文档导航与新手上手

> **本目录只保留 4 个当前生效的文档**（2026-10-30 收敛，详见 `ROADMAP.md` §设计演进史）。早期设计稿已并入 `ROADMAP.md` §设计演进史，旧文件见 `.workbuddy/_trash/2026-10-30-docs-consolidation/`。
> **AI 接入工作区先读根目录 `AGENTS.md`（铁律 + 目录地图）。**

---

## 1. 这是什么

本地优先的 **AI 知识基础设施**。核心资产不是某个应用，而是**可移植的操作指令层（skill + 优化提示词）**——能在 Obsidian / 飞书 / WorkBuddy 之间搬动。

三层核心资产：
1. **可移植的操作指令层**：Prompts / Skills 即代码。
2. **单一可信数据源（SSOT）**：知识只存一份（`archive/` = Obsidian vault），多平台只是视图/镜像。
3. **闭环知识回路**：捕获 → 结构化 → 生成 → 归档索引 → 检索复用。

目标：让个人/小团队的智力资产**可沉淀、可复用、可迁移、可审计**。

---

## 2. 文档地图（4 个文件，按用途查）

| 你要什么 | 读这个文件 |
|---|---|
| **AI 不能违反什么 / 目录在哪** | 根目录 `AGENTS.md`（不在 docs/） |
| 系统架构 / 数据流 / 目录职责 | `ARCHITECTURE.md` |
| **变更总账（按时间倒序，追加式）** | `CHANGELOG.md` |
| 里程碑 / 进度 / 场景 / 待办 / 设计演进史 | `ROADMAP.md` |

> 一句话分工：**AGENTS 管"AI 不能违反什么"，ARCHITECTURE 管"系统长什么样"，CHANGELOG 管"改了什么"，ROADMAP 管"往哪走、做到哪了、当年为何这么定"。**

---

## 3. 第一次上手路径

1. 读 `AGENTS.md` 的 9 条铁律（尤其 #1 不硬编码绝对路径 / #2 `archive` 是 SSOT / #3 笔记必带 frontmatter）。
2. 看 `ARCHITECTURE.md` 的组件地图与主数据流图，建立"知识怎么流动"的直觉。
3. 读 `ROADMAP.md`：先 §里程碑总览看 M1/M2/M3 状态，再 §设计演进史理解当年关键决策（分类四维、频率分层、5 Track 等）。
4. 真正跑一次调研：
   - `load_context.py --list` 看有哪些项目；
   - 没有就 `new_project.py` 建一个；
   - 调研产出先落 `output/`，确认后移 `archive/raw/<子类>/` 并写 frontmatter；
   - `validate_frontmatter.py` 校验通过；
   - 把结论回写该项目的 `research-state.yaml`（focus / claims / monitors / queue / datasets）；
   - 走 `wiki-skill` 整理进 `archive/wiki/`。
5. 卡住按第 4 节查对应文档。

---

## 4. 常用命令（抄了就能跑）

> 运行方式：**用项目本地环境，不要裸 `python`**。优先 `uv run python -m script.xxx`，或 `.venv/Scripts/python.exe -m script.xxx`。

**已可用：**
```bash
# 1) 调研前加载上下文（上次结论 / 监控 / 待办 / 已归档数据集）
uv run python -m script.load_context --list
uv run python -m script.load_context --project P01

# 2) 新建一个调研项目（从 research/_template/ 复制）
uv run python -m script.new_project --id P03 --name "美国储能" --track drill

# 3) 校验笔记 frontmatter（落入 archive/raw 前必过）
uv run python -m script.validate_frontmatter
```

**规划中（接口已定、脚本待写，详见 `ROADMAP.md` §待办）：**
```bash
uv run python -m script.metrics           # 查看命中率/复盘次数（--apply 回写）
uv run python -m script.query_data --list # 数据源目录
uv run python -m script.refresh_monitors  # 按 monitor 定义回填指标 + 触发告警
```

> 跑 skill 本身：在 WorkBuddy 直接调用，或用 `claude -p` 调起本系统 skill。**不配置大模型 API**——抽取/打标/分析由当前会话的 chat 模型执行，密钥只用于飞书/MCP 等外部服务。

---

## 5. 卡住了去哪查

| 我想知道… | 去看 |
|-----------|------|
| AI 不能违反什么 / 目录在哪 | `AGENTS.md`（根目录） |
| 系统由什么组成、数据怎么流 | `ARCHITECTURE.md` |
| 里程碑 / 进度 / 20 个场景 / 待办 / 当年设计决策 | `ROADMAP.md` |
| 变更记录（谁、何时、为何改） | `CHANGELOG.md` |
| 分类 / 打标逻辑 | `config/types.yaml` + `config/tags.yaml` + `ROADMAP.md` §设计演进史 |
| 调研怎么选线（5 Track） | `.workbuddy/skills/research-kit/references/ROUTING.md` |
| 目录 / 命名 / frontmatter / 安全删除 | `.workbuddy/skills/file-manager/`（SKILL.md + USER-GUIDE.md + references/） |
| 经验沉淀 | `memory/MEMORY.md` + `.workbuddy/memory/YYYY-MM-DD.md` |

---

## 6. 来自实战的避坑（必读）

- **路径/密钥零硬编码**（铁律#1）：文档与 skill 一律用 `<workspace>/` 占位或相对路径；密钥只在运行态由 `secrets/`+`.env` 注入。
- **SSOT 分两套**：研究知识以本地 `archive/` 为 SSOT；日频资讯流的 SSOT 是云端 lark base（此域铁律#2 暂不适用，待最终裁定）。
- **A股色规**：涨红跌绿、货币用 ¥。
- **本机 shell 不稳**：凡文件操作 / 批量处理 / 含中文输出，**优先用 Python 脚本**（写盘后 Read 验证），别硬刚 shell 报错；脚本开头 `sys.stdout.reconfigure(encoding="utf-8")`。
- **改了东西记 CHANGELOG**（`CHANGELOG.md`），经验沉淀进 `memory/`。
