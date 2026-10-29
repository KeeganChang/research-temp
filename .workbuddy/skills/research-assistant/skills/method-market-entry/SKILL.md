---
name: method-market-entry
description: 市场进入方法技能。是 research-track-entry（进入测绘）在「市场/平台进入」语境的具体实现：国别PEST→行业→相邻/替代→画像→players。belongs_to_track: entry。enabled: false（具体分析默认不启用），置 true 后参与路由。
type: method
version: 1.2
belongs_to_track: entry
enabled: false
depends_on: [research-core, research-track-entry]
---

# method-market-entry — 市场进入方法（entry track 的具体实现）

> 本技能是 `research-track-entry`（进入测绘**通用骨架**）在**市场/平台进入**语境的固化打法。骨架定义问法/门禁；本技能提供「市场进入怎么跑」。
>
> **默认不启用**（`enabled: false`）：具体分析属于可选加固，默认开启会抢通用路由。需要时把 frontmatter 的 `enabled` 改为 `true`，本技能即作为 entry 的实现参与调度——**一行开关，不动骨架**。

## 与骨架的映射
| 骨架阶段 | 本技能实现 |
|---|---|
| E1 环境 / 准入 | 国别 PEST + 准入/资质门槛审查 |
| E2 目标对象 | 目标行业规模/增速/结构性拐点 |
| E3 相邻 / 替代 | 相邻/替代行业 + 被禁品类的需求重定向承接方 |
| E4 用户 / 需求 | Persona + 分群 + 渗透率拆客单价×频次 |
| E5 玩家 | 玩家地图（份额/护城河/商业模式）|

## 关键判别点（须在 G4 体现）
- ① 准入优先于需求：准入不过，需求再大也 = 零。
- ② 被禁/受限品类追「需求重定向的承接方」（合规溢价 + 机构入口 + 定价权）。
- ③ 渗透拆成 `客单价 × 频次`：高渗透 + 低客单价 ≠ 大市场。

## 交付物
机会区 / 禁区 / 观察哨清单 + 玩家地图（份额 + 护城河 + 商业模式）。

## 引用
- 骨架：research-track-entry ｜ 编排：research-core
