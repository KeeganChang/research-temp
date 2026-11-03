---
description: 新建一个调研任务——先逐项确认「任务信息清单」（任务内容 / 边界 / 交付物 / Track 方式），确认后再落盘项目目录。
argument-hint: "<任务描述 或 主题>"
---

你是 Research Kit 的**立项入口**。本命令负责把用户的模糊需求收敛成一张**可确认的任务信息清单**，经用户签字确认后才建项目。

**不要**在清单未被确认前执行 `new_project`。

## 本次任务描述

$1

## 执行步骤

### Step 1 · 拆解任务内容
从上述描述中提炼（缺失项标「待用户补充」，不要替用户臆造）：
- **驱动问题**：一句话，须**可量化、可证伪**（不能用「研究一下 X」这种不可证伪句式）。
- **背景/动机**：为什么现在做、为谁做。
- **已有信息**：用户手上已有哪些数据/材料（用于后续 `datasets` 防重复抓数）。

### Step 2 · 建议 Track 方式（5 选 1，按任务描述判定，不写死）
依据 `research-kit/references/ROUTING.md` 的决策树，结合本任务描述推荐**唯一**一条 Track，并写明推荐理由：

| Track | 一句话边界 |
|---|---|
| `drill` | 全集里哪个最好？（可横向比较的候选集） |
| `entry` | 能不能进 / 怎么进 / 谁在赚？ |
| `diagnostic` | 为何偏离目标？根因在哪？ |
| `inductive` | 数据里藏着什么分群 / 规律？ |
| `scenario` | 如果…会怎样？规模多大？ |

> 判定依据来自**任务描述本身**，而非任何预设字段。若两条 Track 都说得通，指出歧义、让用户二选一（同一次调研不可混跑多条 Track，铁律 #3）。

### Step 3 · 建议边界与交付物
- `scope_in` / `scope_out`（边界写清，防范围蔓延）
- 交付物形态：报告 / 表格 / 卡片 / 数据集
- 是否需接入具体 method（如 A股/投资场景可启用 `method-topdown`；电商经营诊断可启用 `method-ecommerce-ops`；均默认 `enabled: false`）

### Step 4 · 输出确认清单（核心动作）
用下表呈现，**逐条请用户确认或修改**：

```
| 项 | 内容 | 状态 |
|---|---|---|
| PID | P0x（若 ID 冲突脚本会报错，届时改） | ☐ |
| 项目名 | 一句话 | ☐ |
| 驱动问题 | …… | ☐ |
| Track 方式 | <五选一>（理由：……） | ☐ |
| scope_in | …… | ☐ |
| scope_out | …… | ☐ |
| 交付物 | …… | ☐ |
| 接入 method/domain | 无 / <name> | ☐ |
```

### Step 5 · 确认后落盘
用户确认后再执行（`-m` 模块式调用）：

```
uv run python -m script.new_project --id <PID> --name "<项目名>" --track <drill|entry|diagnostic|inductive|scenario> [--slug <后缀>] [--question "<驱动问题>"]
```

然后把 `scope_in` / `scope_out` / `deliverables` 补进生成的 `research/<PID>-<slug>/project.yaml`。

## 门禁

- **G1**：驱动问题可量化可证伪 + 边界清 + 交付物形态定 → 三项齐备才算通过，**否则退回 Step 1 向用户澄清，不得勉强落盘**。
- **G2**：Track 五选一且理由成立。

## 引用

- 选线边界与决策树：`research-kit/references/ROUTING.md`
- 流程/门禁总纲：`.workbuddy/skills/research-kit/references/skills/research-core/SKILL.md`
- 续做（加载中断任务）：`/research-load`
