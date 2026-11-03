---
description: 加载一个中断/进行中的调研任务——读取状态机、定位中断点、从断点继续按门禁推进。
argument-hint: "<PID 或 项目关键词>"
---

你是 Research Kit 的**续做入口**。本命令负责把上一次未完成的调研接回来，避免「每次从零开始」。

**只读`load_context`，本命令本身不写任何状态文件**（回写只在门禁 G6 环节显式进行）。

## 本次目标项目

$1

## 执行步骤

### Step 1 · 定位项目
若用户给的是关键词而非 PID，先列清单：

```
uv run python -m script.load_context --list
```

命中多个候选时，让用户确认选哪个；无法命中则提示改用 `/research-init` 新建。

### Step 2 · 加载状态机
```
uv run python -m script.load_context --project <PID> --files
```
重点读取：`focus`（当前焦点）/ `claims`（结论台账）/ `monitors`（监控指标 + 阈值）/ `queue`（待办队列）/ `datasets`（已归档数据，防重复抓数）。

需要机读可用 `--json`；只看未完成结论用 `--only open`。

> 状态机本身可疑（ID 对不上、引用悬空、缺 confidence）时先跑 `uv run python -m script.load_context --lint`
> —— **只读自检**，按 严重 / 警告 / 提示 三级报问题，不改任何文件；有严重项退出码 1。

### Step 3 · 定位中断点（关键动作）
按下表自上而下**首个不成立**的项即中断点，从该处续做：

| 断点 | 判据 | 续做动作 |
|---|---|---|
| **G1 立项** | `project.yaml` 缺驱动问题 / 边界 / 交付物 | 回到 `/research-init` 补齐三件套 |
| **G2 选线** | `project.yaml` 的 `track` 为空或理由不成立 | 重跑选线（依据任务描述 + `references/ROUTING.md`） |
| **G3 采集** | 有 focus 但 claims 为空 | 按所选 Track 骨架分模块采集证据 |
| **G4 成稿** | claims 有内容，但反方 <5 条 / 口径未登记 / 证据不可互指 | 补反方 + 登记口径 + 补齐 claim↔evidence 指针 |
| **G5 校验** | claims 缺 `confidence` 或 `status` | 给每条 claim 标 confidence + status |
| **G6 回写** | `updated_at` 陈旧 / monitors 缺阈值或 `as_of` | 回写 `research-state.yaml` 并设 monitor 阈值 |
| **已闭环** | 以上均通过 | 走交付：叙述报告 → `output/` → 确认 → `archive/raw/<type>/` |

### Step 4 · 向用户汇报断点
用简短摘要说明「上次做到哪、还差什么」，然后**等待用户确认**再推进。示例：

```
上次进度：已到 G4 成稿
已完成：13 条 claims（8 validated / 5 open）、4 个 monitors
缺口：反方仅 3 条（须 ≥5，缺时间维度）
下一步：我建议先补反方 —— 是否开始？
```

## 门禁

- 续做时**不得重跑已完成阶段**（重复抓数、覆盖已有结论）。
- 门禁失败必须**显式退回**，不得「假装通过」。
- 只有到了 G6 才允许回写 `research-state.yaml`。

## 引用

- 状态机五段：`research/<PID>/research-state.yaml`
- 流程/门禁总纲：`.workbuddy/skills/research-kit/references/skills/research-core/SKILL.md`
- 新建任务：`/research-init`
- 全流程编排：`/research`
