---
name: research-track-entry
description: 方法级 Track — 进入测绘（Entry/Landscape）。横向「context→players」：环境/准入→目标对象→相邻/替代→用户→玩家，落点是「机会区/禁区/观察哨 + 玩家地图」。不绑业务，具体打法由 belongs_to_track: entry 的 method skill（如 `method-market-entry`）提供；骨架本身不含业务口径。
type: track
version: 1.0
depends_on: [research-core]
---

# research-track-entry — 进入测绘（Entry / Landscape）

> 方法级 Track 之一。只定义问题、门禁、三条通用判别点与交付形态；具体打法由 belongs_to_track: entry 的 method skill 按语境按需加载（无契合回退本骨架）。

## 适用
目标：判断「能不能进、怎么进、谁在赚」。落点 = **机会区 / 禁区 / 观察哨 + 玩家地图**。推理方向 = **横向铺开**。
典型：新市场进入、跨境电商选平台、竞争格局测绘、品类扩张评估。

## 五段（含通用判别点）

### E1 环境 / 准入
- **判别点① 准入优先于需求**：先问合不合法、有无牌照/资质门槛；需求再大，准入不过 = 零。

### E2 目标对象
- 方法：对象规模 / 增速 / 结构性拐点识别。

### E3 相邻 / 替代
- **判别点② 被禁/受限对象要追「需求重定向的承接方」**：它们往往拿到合规溢价 + 机构入口 + 定价权。

### E4 用户 / 需求
- **判别点③ 渗透拆成 `客单价 × 频次`**：高渗透 + 低客单价 ≠ 大市场。
- 方法：Persona + 分群 + 需求分层。

### E5 玩家
- 方法：玩家地图（份额 / 护城河 / 商业模式）。
- 通用判别：区分 β 与 α；同涨同跌 = 假分散。

## 反方（G4 强制 ≥5 条）
含准入被拒情景、替代品类吞噬、客单价陷阱、监管突变等，由具体 method/domain skill 补充。

## 交付形态
机会区 / 禁区 / 观察哨清单 + 玩家地图（份额 + 护城河 + 商业模式）。回写 `claims` 与 `monitors`。

## 接入
- 具体打法：belongs_to_track: entry 的 method skill（如 `method-market-entry`）按语境按需加载（无契合回退本骨架）。
- 未启用域时，只输出骨架级结论。

## 引用
- 编排：research-core ｜ 边界路由：references/ROUTING-quick.md
