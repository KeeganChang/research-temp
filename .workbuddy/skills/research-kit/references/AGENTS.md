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

## 核心原则（铁律，门禁优先）
1. **不硬编码路径 / 密钥**：用 `<workspace>/` 占位；密钥运行态注入，文档只描述「放哪」。
2. **门禁优先**：每阶段设有进入 / 退出标准，未过门禁不得进入下一阶段（防半成品交付）。
3. **主线五选一、不可混跑**：drill（下钻选优）/ entry（进入测绘）/ diagnostic（诊断归因）/ inductive（归纳洞察）/ scenario（推演），选线边界见 `references/ROUTING.md`。
4. **框架即模块**：行业 / 经营分析各以独立 skill 模块接入，自带方法论 + 反方清单 + 口径登记；具体方法放 `references/skills/method-*/`，按语境匹配加载，无契合则回退通用骨架。
5. **结论进状态机（可选）**：claim 走 `open → validated / falsified`，证伪留痕、不删不改。状态机自 2026-11-02 起降级为可选复用层——一次性 / 轻量任务不强制。
6. **先加载、后回写（按需）**：续做旧项目时 `load_context` 加载上下文；收尾按需回写 `research-state.yaml`。不回写仅意味未进跨会话复用层，准确性由报告内联引用 + 口径块 + 反方≥5 保障。

---

## 配置与规范入口（详细定义在各文件，本处只列入口，不内嵌）
| 主题 | 去读（相对套件根） |
|------|------|
| 编排 + 6 道门禁（G1–G6）+ 交付门禁 G_rubric + 状态机回写 | `references/skills/research-core/SKILL.md` |
| 5 种 Track 使用边界 + 选线决策树 | `references/ROUTING.md` |
| 状态机字段模板（六段：node / focus / claims / monitors / queue / datasets） | `references/templates/research-state.yaml` |
| 交付形态与载体分层（`output_target`: local / lark / workbuddy_library） | `references/delivery-standard.md` |
| 交付前自检清单（rubric 前置 7 条 + 后置五维） | `references/report-rubric-v1.md` |
| 框架接入模板（新增模块） | `references/skills/research-module/` |
| 套件采用 / 目录说明 | `references/README.md` |
| 顶层编排入口 | `SKILL.md`（本目录上层） |

**Track 骨架（业务中立，5 选 1）**：`research-track-drill` / `-entry` / `-diagnostic` / `-inductive` / `-scenario`（均在 `references/skills/` 下，只定义推理方向 / 门禁 / 交付形态，不绑行业）。
**method 技能（按语境匹配，无开关）**：`method-topdown`（→drill）/ `method-market-entry`（→entry）/ `method-ecommerce-ops`（→diagnostic）/ `method-sector-momentum`（→drill），均按需·语境匹配，无契合回退通用骨架。

---

## 知识回路
加载上下文 → 选主线 → 分模块采集 → 门禁 → 写 claim → 校验 → 回写 → 交付 → 检索复用

---

## 你要做 X，先看哪
- **新建一个任务** → `/research-init`（任务信息确认清单：任务内容 + 边界 + 交付物 + Track 方式）
- **续做中断的任务** → `/research-load`（加载状态机、定位断点、从断点继续）
- **开始一项调研** → 过 G1 → 选 Track（5 种，边界与决策树见 `references/ROUTING.md`）→ 按模块执行 → 过 G4/G5 → 回写（可选）
- **接入一个新框架（如 Cohort 客群分析）** → 复制 `references/skills/research-module` 模板
- **加载 / 自检旧项目** → `load_context --project <PID>`（`--lint` 只读自检，`--all` 含归档项目）
