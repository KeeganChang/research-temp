---
name: research-kit
description: 带门禁的可控调研流程套件（行业分析 + 经营分析）。任何调研的主入口：加载上下文 → 按任务描述在 5 种方法级 Track（drill/entry/diagnostic/inductive/scenario）中动态选一 → 分模块采集 → 过 6 道门禁(G1–G6) → 写状态机。顶层只放本文件；编排、Track 骨架、method 技能与配置文档均在 references/ 下按需查阅。
type: suite
version: 2.0
---

# Research Kit 套件（编排入口）

把「行业分析 + 经营分析」固化为**带门禁的可控调研流程**。本文件是唯一入口，其余内容**按需到 `references/` 下取用**，不要一次性全读。

## 怎么开始

1. **读编排核心**：`references/skills/research-core/SKILL.md` —— 门禁与状态机回写都在这里，所有调研必经。
2. **选 Track**（5 选 1）：依据**任务描述**套 `references/ROUTING.md` 决策树动态判定，**不读预设字段、不写死**。
   - **drill 下钻选优**（演绎·总→分）→ `references/skills/research-track-drill/`
   - **entry 进入测绘**（横向·context→players）→ `references/skills/research-track-entry/`
   - **diagnostic 诊断归因**（逆向·果→因）→ `references/skills/research-track-diagnostic/`
   - **inductive 归纳洞察**（归纳·样本→规律）→ `references/skills/research-track-inductive/`
   - **scenario 情景推演**（推演·现在→未来）→ `references/skills/research-track-scenario/`
3. **接框架**：每个业务框架（用户画像、渠道分析、Cohort 客群…）走 `references/skills/research-module/` 模板接入，门禁自动生效。
4. **要具体打法**：按语境按需加载 `references/skills/method-*/`（见「硬规矩」与 `references/ROUTING.md` §五）。

## 何时读哪个文件（按需，勿全读）

| 你要做什么 | 去读 |
|---|---|
| 跑一次调研 / 门禁细节 / 状态机回写 | `references/skills/research-core/SKILL.md` |
| 判断该走哪条 Track | `references/ROUTING.md`（选线权威） |
| 看完整流程图 + G1–G6 门禁定义 + 技能路由 | `references/skills/research-core/SKILL.md` |
| 采用本套件 / 接入新框架 / 目录说明 | `references/README.md` |
| 新建项目的状态机文件长什么样 | `references/templates/research-state.yaml` |
| 某语境的具体算法与口径 | `references/skills/method-*/SKILL.md` |

## 套件内构成

| 路径（相对本目录） | 角色 | 启用方式 |
|---|---|---|
| `references/skills/research-core/` | 编排 + 6道门禁(G1–G6) + 状态机回写 | 是 |
| `references/skills/research-track-drill/` | Track 骨架：下钻选优 | 是 |
| `references/skills/research-track-entry/` | Track 骨架：进入测绘 | 是 |
| `references/skills/research-track-diagnostic/` | Track 骨架：诊断归因 | 是 |
| `references/skills/research-track-inductive/` | Track 骨架：归纳洞察 | 是 |
| `references/skills/research-track-scenario/` | Track 骨架：情景推演 | 是 |
| `references/skills/research-module/` | 任意框架接入模板（含 Cohort 示例） | 是 |
| `references/skills/method-topdown/` | method：景气链（→drill，含 A股 细化 a1/a2/a3） | 按需·语境匹配 |
| `references/skills/method-market-entry/` | method：市场进入（→entry） | 按需·语境匹配 |
| `references/skills/method-ecommerce-ops/` | method：电商经营诊断（→diagnostic） | 按需·语境匹配 |
| `references/skills/method-sector-momentum/` | method：行业景气度横截面跟踪（→drill） | 按需·语境匹配 |
| `references/AGENTS.md` | 核心原则（铁律）+ 配置与规范入口指针（详细定义在各专文件） | — |
| `references/ROUTING.md` | 5 种 Track 使用边界 + 选线决策树（选线权威） | — |
| `references/README.md` | 采用 / 接入新框架 / 目录结构 | — |
| `references/templates/research-state.yaml` | 状态机模板（含 node 关系层） | — |

## 硬规矩

- **按需取用**：顶层只留本入口；内部文档一律按需读，不要启动时全量加载。
- **method 按语境按需加载**：`skills/method-*` 承载具体算法 / 口径 / 反方清单，**不再用 `enabled` 开关**；按任务语境匹配其 described 领域加载，无契合 method 时回退该 Track 通用骨架（兜底），不强行套用领域口径。
- **同一项目只选一条 Track**（G2 锁死），不可混跑；跨 Track 用父子 task 串起。
- **多 task 单方向派生**：子节点只写 `node.parent`，父子关系与汇总由 `load_context` 运行时建图，**不双写、不改父文件**。
- **不自建框架类别**：新框架走 `research-module` 模板，门禁自动生效。
- **不跳过门禁**：门禁失败必须显式退回，不得「假装通过」。

## 命令入口

- `/research-init` — 新建立项（出任务信息确认清单，含 Track 方式；G1 未过不落盘）
- `/research-load` — 续做中断任务（定位断点后等确认再推进）
- `/research` — 全流程编排

## 引用

- 流程与门禁（G1–G6 + G_rubric）：`references/skills/research-core/SKILL.md`（AGENTS.md 只列原则与入口）
- 选线边界与决策：`references/ROUTING.md`
- 状态机：`references/templates/research-state.yaml`
- 编排细节：`references/skills/research-core/SKILL.md`
