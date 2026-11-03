# Research Kit 核心骨架

> 把「行业分析 + 经营分析」方法固化为**带门禁的可控调研流程**的**自包含套件（starter kit）**。是单一可信源；并入既有项目只是可选副线。
>
> **位置与路径**：本文件位于 `references/` 下；文中路径**相对套件根目录**书写。
> 套件顶层只保留 `SKILL.md`（加载入口），其余内容（含本文件、骨架、method、模板）都在 `references/` 下**按需查阅**。

## 这是什么

- 顶层 `SKILL.md`：唯一加载入口（怎么开始、何时读哪个文件、硬规矩）。
- 配置文档（本目录内）：
  - `AGENTS.md`：核心原则（铁律）+ 配置与规范入口指针（流程图/门禁/状态机/路由的详细定义见 research-core 与各专文件）。
  - `ROUTING.md`：5 种 Track 的使用边界与选线决策树（G2 依据，选线权威，不写死）。
  - `README.md`：本文件（采用方式 / 接入新框架 / 目录结构）。
  - `templates/research-state.yaml`：跨会话状态机模板（node 关系层 + focus/claims/monitors/queue/datasets）。
  - `research-project-naming.md`：调研项目目录命名（`<PID>-<slug>[-<YYYYMMDD>]`）的唯一权威；file-manager 不重复定义，只指向本文件。
- 5 种**方法级 Track 骨架**（默认启用，按推理方向划分，不绑业务）→ `skills/research-track-*`：
  - `research-track-drill`：下钻选优（演绎·总→分）
  - `research-track-entry`：进入测绘（横向·context→players）
  - `research-track-diagnostic`：诊断归因（逆向·果→因）
  - `research-track-inductive`：归纳洞察（归纳·样本→规律）
  - `research-track-scenario`：情景推演（推演·现在→未来）
- 编排与模板（默认启用）：
  - `research-core`：编排 + 门禁控制（主入口，所有调研必经）
  - `research-module`：任意框架接入模板（宏观、用户画像、渠道、Cohort 客群…）
- **method 技能**（某语境的固化打法，`belongs_to_track` 指向某 Track，**按语境按需加载，无契合回退通用骨架**）：
  - `method-topdown`：景气链（→ drill），含 A股 细化 a1/a2/a3
  - `method-market-entry`：市场进入（→ entry）
  - `method-ecommerce-ops`：电商经营诊断（→ diagnostic）
  - `method-sector-momentum`：行业景气度横截面跟踪（→ drill）
- 命令入口：`/research-init`（新建，出确认清单）、`/research-load`（续做中断任务）、`/research`（全流程编排）。

## 为什么「可控」

三层控制机制（详见 `references/skills/research-core/SKILL.md`）：
1. **结构控制**：5 种 Track 由 G2 单选其一、不可混跑；Track 内部模块有固定上下游，防逻辑错位。
2. **门禁控制**：每阶段进/出标准，含「反方≥5条 + 口径登记」，防半成品与确认偏误。
3. **状态机控制**：claim 走 open→validated/falsified（证伪留痕），监控带阈值告警，防结论漂移与每次从零开始。

## 如何采用

**推荐：整体克隆为独立套件（单一真源）**
- 把 `research-kit/` 整目录放进你的 `.workbuddy/skills/`（顶层 `SKILL.md` 即加载入口，`references/` 自动随行）。
- 业务框架按 `skills/research-module/` 模板往 `references/skills/` 里加（如 cohort-analysis、channel-analysis），不另建类别。

**可选：并入既有项目**
- 仅当你已有自己的 `AGENTS.md` 且不愿引入独立套件时，才把本套件的「铁律」段落 merge 进你的 `AGENTS.md`（其余规范按 research-core / templates 等各自采用，避免双份逻辑）。
- ⚠️ 注意：并入会造成双份逻辑，需自行保证后续只在一处维护（违背 SSOT）。

## 如何接入一个新框架（如 Cohort 客群分析）

1. 复制 `references/skills/research-module/` → `references/skills/cohort-analysis/`。
2. 按模板填：核心问题 / 输入口径 / 处理 SOP / 反方≥5 / 交付物 / 模块门禁。
3. 在 `references/skills/research-core/SKILL.md` 的方法技能清单登记，并声明 `belongs_to_track`（drill / entry / diagnostic / inductive / scenario）；同步在 `references/AGENTS.md` 的 method 列表补一行。
4. 无需改 research-core，门禁自动生效。

## 骨架 / 方法 与按需加载

套件把「骨架」与「具体方法」分离：
- **Track 骨架**（`skills/research-track-*`）：只定义推理方向、问题、门禁、交付形态，不绑定任何行业 / 市场。
- **method 技能**（`skills/method-*`）：某语境的固化打法（算法 / 口径 / 反方清单），`belongs_to_track` 指向某 Track。

**按语境按需加载约定**：method 不再用 `enabled` 开关；research-core 按任务语境匹配其 described 领域加载，无契合则回退通用骨架。
理由：默认启用会把非该语境的任务错误路由到该口径（如把 SaaS 漏斗诊断错误套成电商口径）。

示例：`method-topdown` 提供 四路资金验证 → 六段式产业链+兑现度 → 分子/分母三分法+相对收益 的固化流程（A股 细化见其目录内 a1/a2/a3）。

## 多 task：单方向派生

- 每个 task 是 `research/` 下的**平铺目录**，父子关系写在子节点 `research-state.yaml` 的 `node.parent`。
- `children` / `depth` 不存储，由 `load_context` 运行时建图；父状态 rollup 自动派生。
- 新增 task = 建新节点 + 写 `parent`，**不改父文件**。
- 建法：`new_project --id T1 --name "..." --track <track> --parent P03`。

## 目录结构

```
research-kit/
├── SKILL.md                    # 唯一加载入口（顶层只留它）
└── references/                 # 其余内容，按需查阅
    ├── AGENTS.md               # 核心原则（铁律）+ 配置与规范入口指针
    ├── ROUTING.md              # 5 种 Track 使用边界 + 选线决策树（选线权威）
    ├── README.md               # 本文件
    ├── templates/
    │   └── research-state.yaml # 状态机模板（含 node 关系层）
    ├── research-project-naming.md  # 调研项目目录命名（唯一权威）
    └── skills/
        ├── research-core/             # 编排 + 门禁控制
        ├── research-track-drill/      # Track: 下钻选优
        ├── research-track-entry/      # Track: 进入测绘
        ├── research-track-diagnostic/ # Track: 诊断归因
        ├── research-track-inductive/  # Track: 归纳洞察
        ├── research-track-scenario/   # Track: 情景推演
        ├── method-topdown/            # method: 景气链（→drill，含 a1/a2/a3，按需·语境匹配）
        ├── method-market-entry/       # method: 市场进入（→entry，按需·语境匹配）
        ├── method-ecommerce-ops/      # method: 电商经营诊断（→diagnostic，按需·语境匹配）
        ├── method-sector-momentum/    # method: 行业景气横截面（→drill，按需·语境匹配）
        └── research-module/           # 框架接入模板
```
