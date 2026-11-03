# AGENTS.md — Research Kit 核心骨架

> 任何模型 / 智能体接入本 Research Kit，**先读这份**。这是最低限度须知，也是「可控调研流程」的单一可信入口。
> 本文件是**产品骨架**，可整体克隆 / 采用；不依赖具体业务域（A股、电商、飞书等），框架以可插拔模块接入。
>
> **位置与路径**：本文件位于 `references/` 下，属按需查阅的配置文档；套件顶层只留 `SKILL.md` 入口。
> 文中所有路径**相对套件根目录**书写（如 `references/skills/research-core/SKILL.md`）。

---

## 一句话
把「行业分析 + 经营分析」方法固化成 **带门禁的可控调研流程**：骨架与具体方法分离、框架即模块、主线五选一（drill/entry/diagnostic/inductive/scenario）、结论可进状态机（可选复用层）、可审计、可续做。

---

## 铁律（门禁优先）
1. **不硬编码路径 / 密钥**：用 `<workspace>/` 占位；密钥运行态注入，文档只描述「放哪」。
2. **门禁优先**：每阶段设有进入 / 退出标准，未过门禁不得进入下一阶段（防半成品交付）。
3. **主线五选一、不可混跑**：drill（下钻选优）/ entry（进入测绘）/ diagnostic（诊断归因）/ inductive（归纳洞察）/ scenario（情景推演），逻辑错位即作废。选线边界见 `references/ROUTING.md`。
4. **框架即模块**：行业分析（宏观 / 产业链 / 竞争 / 用户画像 / 市场容量）、经营分析（渠道 / Cohort / 漏斗 / 单元经济 / 健康度）各以独立 skill 模块接入，自带方法论 + 反方论点清单 + 口径登记。具体方法放 `references/skills/method-*/`，按语境匹配加载，无契合则回退通用骨架。
5. **结论进状态机（可选）**：claim 走 `open → validated / falsified`，证伪留痕、不删不改。**状态机自 2026-11-02 起降级为可选复用层**——一次性 / 轻量任务不强制；仅月频重跑 / 跨会话续做 / 多人协作才启用。
6. **先加载、后回写（按需）**：续做旧项目时 `load_context` 加载上下文；收尾**按需**回写 `research-state.yaml`。不回写仅意味本次未进跨会话复用层，不再等于"每次从零开始"——准确性由报告内联引用 + 口径块 + 反方≥5 保障。

---

## 可控调研流程图

```
[1 立项 / 加载上下文] ── load_context --project <PID>
        │
[2 定义问题与边界] ◀─ 门禁 G1：驱动问题 + scope_in/scope_out + 交付物（三件套）
        │
[3 选调研主线] ── drill(下钻) | entry(进入) | diagnostic(诊断) | inductive(归纳) | scenario(推演)
        │          五选一；边界与决策树见 references/ROUTING.md；跨 Track 用父子 task 串起
        │
[4 分模块证据采集] ── 按所选主线加载对应 骨架 skill；按语境匹配加载 method skill（无契合则回退通用骨架）
        │
[5 阶段门禁 Gate] ── 证据充分？反方≥5条？口径一致？
        │     否 ─────► 回 [4] 补数（带 depends_on 入 queue）
        ▼     是
[6 写 claim 台账] ── focus / claims(证据+数据指针) / confidence / status
        │
[7 结论校验] ── status: open → validated / falsified
        │
[8 回写状态机 + 监控（可选）] ── 仅跨会话续做时更新 research-state.yaml，monitor 带阈值告警
        │
[9 产出交付] ── output/ → 确认 → archive/raw/（带 frontmatter）
```

---

## 阶段门禁（Gate）定义

| 门禁 | 进入条件 | 退出条件（须全部满足） |
|---|---|---|
| G1 立项 | 用户给出业务目标 | 驱动问题可量化 + 边界明确 + 交付物形态确定 |
| G2 选线 | G1 通过 | 5 种 Track（drill/entry/diagnostic/inductive/scenario）其一选定，且理由成立（见 `references/ROUTING.md`） |
| G3 采集 | G2 通过 | 所有必填模块已执行，原始证据可追溯 |
| G4 成稿 | 证据采集完成 | 反方论点 ≥5 条；关键口径已登记；claim 与证据可互指 |
| G5 校验 | G4 通过 | 每条 claim 标注 confidence + status；无悬空结论 |
| G_rubric 交付自检 | G5 通过 | rubric 前置清单 7 条全过（内联引用 / 口径块 / 反方≥5 / 落盘 / 脚本校验 / 独立源 / judgment），否则不交付 |
| G6 回写（可选） | G5 通过 | 跨会话续做时才需更新 research-state.yaml；一次性任务可跳过，准确性由报告内联引用保障 |

> 交付形态与载体分层见 `references/delivery-standard.md`（Lark Doc 为主 + 三段式内联 + Sheet 退 reference）；交付前自检清单见 `references/report-rubric-v1.md`。

---

## 状态机（research-state.yaml）

跨会话记忆（模板见 `references/templates/research-state.yaml`），六段：
- `node`：**关系层**（见下「多 task」）
- `focus`：当前焦点问题
- `claims`：结论台账（evidence 证据笔记 + data 数据指针 + confidence + status）
- `monitors`：监控指标（上次观测值 + 告警阈值）
- `queue`：待办（含 depends_on）
- `datasets`：已归档数据集索引（防重复抓数）

`status` 生命周期：`open → validated / falsified`（证伪不删，留作教训）。

### 多 task：单方向派生（不嵌套）
- 每个 task = 一个平铺目录 `research/<ID>-<slug>/`，父子**靠 `node.parent` 表达**，不用嵌套目录。
- `children` / `depth` **不存储**，由 `load_context` 按 `parent` 运行时建图（避免双写漂移）。
- **新增一个 task = 只建一个新节点并写它的 `parent`，不改父文件。**
- 父节点总状态（rollup）由子节点派生，不手维护：任一 `paused`→paused；否则任一 `active`→active；子节点全 `done/archived`→done。

---

## 技能路由

| 技能 | 职责 |
|---|---|
| `research-core` | 编排 + 门禁控制：load_context、阶段推进、回写状态机 |
| `research-track-drill` | Track **骨架（业务中立）**：下钻选优，演绎·总→分 |
| `research-track-entry` | Track **骨架（业务中立）**：进入测绘，横向·context→players |
| `research-track-diagnostic` | Track **骨架（业务中立）**：诊断归因，逆向·果→因 |
| `research-track-inductive` | Track **骨架（业务中立）**：归纳洞察，归纳·样本→规律 |
| `research-track-scenario` | Track **骨架（业务中立）**：情景推演，推演·现在→未来 |
| `method-topdown` | method 技能：景气链（→ drill），含 A股 细化 a1/a2/a3，**按需·语境匹配** |
| `method-market-entry` | method 技能：市场进入，→ entry，**按需·语境匹配** |
| `method-ecommerce-ops` | method 技能：电商经营诊断（→ diagnostic），**按需·语境匹配** |
| `method-sector-momentum` | method 技能：行业景气度横截面跟踪，资金流 × 月度景气 → 四象限（→ drill），**按需·语境匹配**；下钻标的转 `method-topdown` A3 |
| `research-module` | 框架接入模板：任意行业 / 经营分析框架按模板接入为模块 |

> **方法技能（method）约定**：具体打法放 `references/skills/method-*/`，按语境匹配加载（不再用 `enabled` 开关），无契合则回退通用骨架；新增打法复制 `references/skills/method-topdown/` 即可，不改 core。

---

## 知识回路
加载上下文 → 选主线 → 分模块采集 → 门禁 → 写 claim → 校验 → 回写 → 交付 → 检索复用

---

## 你要做 X，先看哪
- **新建一个任务** → `/research-init`（任务信息确认清单：任务内容 + 边界 + 交付物 + Track 方式）
- **续做中断的任务** → `/research-load`（加载状态机、定位断点、从断点继续）
- **开始一项调研** → 过 G1 → 选 Track（5 种，边界与决策树见 `references/ROUTING.md`；按任务描述动态判定，不写死）→ 按模块执行 → 过 G4/G5 → 回写
- **接入一个新框架（如 Cohort 客群分析）** → 复制 `references/skills/research-module` 模板，填方法论 / 反方 / 口径 / 交付物
- **加载一个具体方法（如 A股 景气链 / 电商经营诊断）** → 当任务语境契合其 described 领域时由 research-core 按语境自动加载；无契合语境回退通用骨架
- **续做旧项目（命令行）** → `load_context --project <PID>`（会自动带上其子 task；archived 项目默认隐藏，显式指定仍可加载，`--all` 全列）
- **状态机出问题 / 想自检** → `load_context --lint`（**只读**，不改文件）：受控词表（track / claim status）+ 门禁必填（confidence / status / monitor 阈值）+ 悬空引用（parent / evidence / depends_on / dataset 路径）+ 陈旧度。级别 严重 > 警告 > 提示，**有严重项退出码 1**；`--lint --json` 机读；归档项目（`research/_archive/`）一并纳入
