---
name: file-manager
version: 0.2.0
description: 本地知识库的目录结构、文件命名、frontmatter 规范与安全删除规则。定义 archive/(Obsidian vault: raw/wiki/inbox)、output/、memory/、secrets/、script/ 的落位，以及研究笔记的命名与元数据约定。所有归档动作（research 落盘、wiki-skill 产出、outputs 确认后入档）都须遵守本 skill。
---

# file-manager

本地知识资产管理系统的目录与文件规范。本 skill 不内联规则细节，只定义权威结构与引用指向；具体规则见 `references/`。

## 一、目录结构（权威）

```
<workspace>/
├── AGENTS.md                  # 项目常驻上下文（CLAUDE.md 等价）
├── archive/                   # Obsidian vault = 单一可信数据源(SSOT)
│   ├── raw/                   # 原始收集（md/附件/数据源），经 wiki-skill 整理进 wiki/
│   ├── wiki/                  # 整理后知识库（双链 + MOC，Obsidian 兼容）
│   └── inbox/                 # 待分类暂存
├── output/                    # 产出确认前暂存（HTML/PPT/报告草稿）
├── memory/                    # 顶层经验：MEMORY.md + *.jsonl（模型跑通/碰壁经验）
├── secrets/                   # 开发用 API 密钥（飞书/MCP 等），不入库
├── .env                       # 项目运行密钥（与 secrets/ 不冲突）
├── script/                    # 脚本（validate_frontmatter.py 等），git 跟踪
├── docs/                      # 设计文档 README/MILESTONE/PROGRESS/CHANGELOG/SCENARIO/TODO
└── .workbuddy/
    ├── skills/                # 项目级 skills（本 skill + wiki-skill）
    └── memory/                # 按日 md（YYYY-MM-DD.md）
```

规则要点：
- `archive/` 是 SSOT；飞书只作为出报告 / 分享的视图，不反向写入。
- `raw/` 进 → `wiki/` 出（由 `wiki-skill` 处理），双链与 MOC 在 raw→wiki 阶段生成。
- `output/` 下的产出经人工确认后再移入 `archive/raw/`。

## 二、命名规则

### 2.1 归档文件命名（archive/raw/ 等）

```
<日期>_<类别>_<主题>_v<版本>.<ext>
```

- 日期：`YYYYMMDD`（如 20260919）
- 类别：research 子类（资讯 / 行业 / 公司 / 热点 / 宏观 / 个人配置…）或产出类型（报告 / 仪表盘 / 分析）
- 主题：短横线连接 slug（如 `宁德时代-财报`）
- 版本：`v1` `v2`… 大改递增
- 例：`20260919_公司_宁德时代-财报_v1.md`、`20260919_宏观_CPI-PPI_v1.csv`

### 2.2 调研项目目录命名（research/）

一个业务调研 = 一个项目目录，格式：

```
research/<PID>-<slug>[-<YYYYMMDD>]/
```

- **`<PID>`**：项目 ID，`P` + 两位数字（如 `P03`）。**是跨文件稳定引用键**——笔记 frontmatter 写 `project: P03`、状态机 `research-state.yaml` 互相引用都靠它；**改名 / 换 slug 不影响引用**。
- **`<slug>`**：英文短横线人读后缀，由 `--name` 的拉丁字符自动派生（`slugify`：去非字母数字、转小写、截断 24 位），或显式 `--slug xxx` 覆盖。例：`P04-pest`（名含 "PEST" 被保留）、`P02-us-crypto`、`P03-cn-chip`（手动指定）。
- **`[-<YYYYMMDD>]`**：可选日期后缀，**仅观察类 / 快照型项目**带（如 `P01-hotspot-20260919`），常青主题不加（如 `P02-us-crypto`）。
- 创建命令（统一 `python -m` 模块式，详见 AGENTS.md 铁律 #9）：
  `python -m script.new_project --id P03 --name "芯片行业深度" --track A [--slug cn-chip-20260904]`
- ⚠️ 目录名是"人读标签"，**可改名不影响 PID 引用**（如 `P03-project` → `P03-cn-chip-20260904` 零断链，内部只用 ID 互指）。

## 三、frontmatter（研究笔记强制）

所有 `archive/raw/*.md` 必须含 YAML frontmatter，由 `script/validate_frontmatter.py` 校验：

```yaml
source: 来源名              # 必填，文本
url: https://...            # 必填，http/https 开头
fetched_at: 2026-09-19      # 必填，YYYY-MM-DD（YAML 会自动转 date，脚本已兼容）
type: structured|unstructured   # 必填
confidence: high|medium|low     # 必填（抽取置信度）
```

- `type=structured` 建议带 `data_file:` 指向同目录 csv/json/sqlite。
- 数据源留痕：非结构化 → md + 原件；结构化 → csv/json（单次）或 sqlite（cron 定时），本地为 SSOT。

## 四、删除策略（详见 references/safe-delete.md）

- 工作区（`<workspace>`）内可任意 CRUD（完全访问模式）。
- 删除默认进回收站（可逆），不用硬删；禁止吞错；删后必须验证。
- 工作区外个人目录（Desktop/Downloads 等）仅只读扫描，谨慎操作。

## 五、引用

- 使用者手册：`USER-GUIDE.md`（面向使用者的功能说明）
- 安全删除规则：`references/safe-delete.md`
- 命名与 frontmatter 细则：`references/naming-and-frontmatter.md`
- 校验脚本：`script/validate_frontmatter.py`
