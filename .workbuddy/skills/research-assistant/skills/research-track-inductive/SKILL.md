---
name: research-track-inductive
description: 方法级 Track — 归纳洞察（Inductive）。归纳「样本→规律」：数据归集→分群/模式识别→规律验证→洞察提炼。落点是「客群/模式分层 + 可行动洞察」。不绑业务，具体框架由 belongs_to_track: inductive 的 method skill 提供。
type: track
version: 1.0
depends_on: [research-core]
---

# research-track-inductive — 归纳洞察（Inductive）

> 方法级 Track 之一。推理方向 = **归纳·样本→规律**。用于「我有一堆数据，告诉我藏着什么分群/规律」。

## 适用
目标：从原始行为/样本数据中归纳出稳定分群或可行动规律。典型：Cohort 客群分析、RFM、Persona、聚类分群、模式挖掘。

## 通用四段（每段带门禁）

### I1 数据 / 样本归集
- 问题：用什么样本？时间窗、口径、覆盖是否足以归纳？
- 门禁：样本量与时窗足够、口径已登记，方可分群。

### I2 分群 / 模式识别
- 方法：RFM / 聚类 / 同期群 / 序列模式，产出分层。
- 门禁：分层有业务可解释性（非纯统计噪声），方可验证。

### I3 规律验证
- 问题：分层/规律是否稳定？换样本/换时段是否成立？
- 门禁：通过稳定性或外推验证，方可提炼洞察。

### I4 洞察提炼
- 问题：哪条规律可转化为行动（定价/触达/产品）？
- 门禁：每条洞察绑定一个可行动建议，方可成稿。

## 反方（G4 强制 ≥5 条）
含「口径不一致导致虚高」「高渗透低客单价陷阱」「样本截断（新群未成熟）」「季节/促销扭曲」「过拟合（分群不可泛化）」。

## 交付形态
客群/模式分层图 + 洞察卡（规律→行动）。落 `claims`，回写 `monitors`（如关键分群规模变化）。

## 接入
- 具体框架：belongs_to_track: inductive 的 method skill（如 cohort-analysis、rfm、persona）。
- 注意：分层须带「可解释性 + 稳定性」双验证，防止统计噪声当洞察。

## 引用
- 编排：research-core ｜ 边界路由：ROUTING.md ｜ 登记：TRACKS.md
