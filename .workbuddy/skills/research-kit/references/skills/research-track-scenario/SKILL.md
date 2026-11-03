---
name: research-track-scenario
description: 方法级 Track — 情景推演（Scenario）。推演「现在→未来」：假设设定→模型/测算→情景分支→触发监控。落点是「情景矩阵 + 敏感性 + 触发阈值」。不绑业务，具体框架由 belongs_to_track: scenario 的 method skill 提供。
type: track
version: 1.0
depends_on: [research-core]
---

# research-track-scenario — 情景推演（Scenario）

> 方法级 Track 之一。推理方向 = **推演·现在→未来**。用于「如果…会怎样？规模/敏感性多大？」。

## 适用
目标：在给定假设下推演结果分布，辅助决策与预案。典型：TAM/SAM/SOM 测算、敏感性分析、what-if、容量/规模预测。

## 通用四段（每段带门禁）

### S1 边界 / 假设设定
- 问题：关键驱动变量与假设是什么？不确定性区间多宽？
- 门禁：核心假设可枚举、有不确定性区间，方可测算。

### S2 模型 / 测算
- 方法：自上而下 / 自下而上交叉验证（如 TAM/SAM/SOM）、单元经济模型。
- 门禁：测算口径一致、可复算，方可分支。

### S3 情景分支
- 问题：乐观 / 基准 / 悲观下结果分布如何？
- 门禁：三档情景覆盖合理尾部，方可成稿。

### S4 触发与监控
- 问题：什么信号会让基准→乐观/悲观？如何监控？
- 门禁：给出触发指标与阈值（回写 monitors），方可交付。

## 反方（G4 强制 ≥5 条）
含「假设失效」「外推过度（基数谬误）」「单位/口径错配」「忽略二阶效应」「黑天鹅未进分布」。

## 交付形态
情景矩阵（三档）+ 敏感性表 + 触发阈值。落 `claims`，回写 `monitors`。

## 接入
- 具体框架：belongs_to_track: scenario 的 method skill（如 market-sizing、sensitivity）。
- 注意：须显式标注「假设依赖」，防止把单点测算当确定性结论。

## 引用
- 编排：research-core ｜ 边界路由：references/ROUTING-quick.md
