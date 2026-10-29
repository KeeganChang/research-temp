---
name: research-assistant
description: 带门禁的可控调研流程套件（行业分析 + 经营分析）。任何调研的主入口：加载上下文 → 在 5 种方法级 Track（drill/entry/diagnostic/inductive/scenario）中选一 → 分模块采集 → 过 6 道门禁(G1–G6) → 写状态机。内含 research-core(编排)、research-track-*(5种骨架)、research-module(框架接入模板)，以及 method-topdown(景气链,含A股细化)/method-market-entry/method-ecommerce-ops/method-sector-momentum(行业景气横截面) 四个 method 技能（具体分析默认不启用）。
type: suite
version: 1.5
---

# Research Assistant 套件（编排入口）

本套件把「行业分析 + 经营分析」固化为**带门禁的可控调研流程**，是 Research Assistant 服务的骨架。

## 怎么开始
1. 读取并遵循 `skills/research-core/SKILL.md` —— 它是编排与门禁控制核心，所有调研必经。
2. 按业务选一条 Track（5 选 1，边界与决策树见 `ROUTING.md`；按任务描述动态判定，不写死）：
   - **drill 下钻选优**：`skills/research-track-drill/`
   - **entry 进入测绘**：`skills/research-track-entry/`
   - **diagnostic 诊断归因**：`skills/research-track-diagnostic/`
   - **inductive 归纳洞察**：`skills/research-track-inductive/`
   - **scenario 情景推演**：`skills/research-track-scenario/`
3. 每个业务框架（用户画像、渠道分析、Cohort 客群…）走 `skills/research-module/` 模板接入，门禁自动生效。

## 套件内构成
| 路径 | 角色 | 默认启用 |
|---|---|---|
| `skills/research-core/` | 编排 + 6道门禁(G1–G6) + 状态机回写 | 是 |
| `skills/research-track-drill/` | Track 骨架：下钻选优（演绎·总→分） | 是 |
| `skills/research-track-entry/` | Track 骨架：进入测绘（横向·context→players） | 是 |
| `skills/research-track-diagnostic/` | Track 骨架：诊断归因（逆向·果→因） | 是 |
| `skills/research-track-inductive/` | Track 骨架：归纳洞察（归纳·样本→规律） | 是 |
| `skills/research-track-scenario/` | Track 骨架：情景推演（推演·现在→未来） | 是 |
| `skills/method-topdown/` | method 技能：景气链（→ drill），含 A股 细化 a1/a2/a3 | **否(enabled:false)** |
| `skills/method-market-entry/` | method 技能：市场进入，→ entry | **否(enabled:false)** |
| `skills/method-ecommerce-ops/` | method 技能：电商经营诊断，→ diagnostic | **否(enabled:false)** |
| `skills/method-sector-momentum/` | method 技能：行业景气度横截面跟踪（资金流 × 月度景气 → 四象限），→ drill | **否(enabled:false)** |
| `skills/research-module/` | 任意框架接入模板（含 Cohort 示例） | 是 |
| `templates/research-state.yaml` | 跨会话状态机模板（含 node 关系层） | — |
| `AGENTS.md` | 完整流程图 + 门禁定义 + 技能路由 | — |
| `ROUTING.md` | 5 种 Track 使用边界 + 选线决策树（选线权威，不写死） | — |

## 硬规矩
- 方法技能（method，承载具体算法 / 口径 / 反方清单）默认 `enabled: false`，不参与自动路由；启用须显式置 `enabled: true`。
- 同一项目只选一条 Track（G2 锁死），同一条链不可混跑；跨 Track 用父子 task 串起。
- 多 task 用**单方向派生**：子节点只写 `node.parent`，父子关系与汇总由 `load_context` 运行时建图，**不双写、不改父文件**。
- 不自建框架类别；新框架走 `research-module` 模板，门禁自动生效。
- 不跳过门禁；门禁失败必须显式退回，不得「假装通过」。

## 引用
- 完整流程与门禁：`AGENTS.md`
- 选线边界与决策：`ROUTING.md`（动态按任务描述判定）
- 状态机：`templates/research-state.yaml`
- 编排细节：`skills/research-core/SKILL.md`
