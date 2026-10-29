---
name: research-macro
description: 宏观分析研究子类。调研市场资金面/宏观数据的行业分布与周期阶段，产出带 frontmatter 的结构化报告，归档至 archive/raw/宏观/，并可交 wiki-skill 整理进知识库。用于"热钱流向""风格切换""北向配置""行业景气对比"等宏观研判。
---

# research-macro — 宏观分析研究子类

> `research` 大类下的**宏观分析**子类，是 **Track A 景气链 Top-Down 的第一段**（macro → industry → company）。
> 模板：`archive/raw/宏观/20260919_宏观_热钱流动行业分析_v1.md`（属项目 **P01 · 2026-09-19 行业热点观察**）。
> 与下游分工：**macro 回答"钱在哪"**，锁定热钱最集中的行业后交接 `research-industry`（这条链谁真赚到钱），再交 `research-company`（落到单个标的）。

## 何时用
- 需要判断"钱正在流向哪些行业"、市场风格是否切换、外资/机构在配置什么。
- 需要给团队（12 人 A 股多智能体工作流）提供**资金面宏观输入**。
- 需要为某个行业/公司研究提供自上而下的资金与周期背景。

## 铁律
1. **多口径交叉验证，禁止单一数据源下结论**（单一口径最易误导）。
2. **必须给出反方论点**（估值/拥挤/杠杆/外部/业绩兑现），否则报告不可用。
3. **A股色规：▲红=涨、▼绿=跌，货币 ¥**。
4. 落盘必须带 frontmatter 并通过 `script/validate_frontmatter.py` 校验。
5. 不硬编码路径与私密信息（见 `AGENTS.md` 铁律）。

## 输入契约
| 项 | 说明 |
|----|------|
| 主题 | 如"国内热钱流动的行业情况" |
| 数据窗口 | 日 / 周 / 季度 / 半年度 / YTD，须显式声明 |
| 可选聚焦 | 指定要深度分析的行业（默认取"资金最集中"的那个）|

## 方法论：四路资金交叉验证（核心）

| 资金路 | 口径 | 观测窗口 | 回答什么 |
|--------|------|---------|---------|
| 主力资金 | 大单/机构净流入 | 日 / 周 | 最短周期"钱去哪了" |
| 北向资金（陆股通）| 外资持仓与流入 | 季 / 半年 | 聪明钱中期配置 |
| 游资 / 龙虎榜 | 上榜席位买卖 | 日 | 短线投机热度 |
| ETF 申赎 | 被动资金方向 | 半年 | 居民/机构被动迁移 |

**交叉验证要点**：四路指向一致 = 强信号；出现背离时（如北向加、主力撤）要**显式解释背离**（通常 = 外资中期配置 vs 国内短周期调仓），不要回避。

**必看的分化信号**：概念板 YTD 对比——区分"**有业绩的硬件**"与"**靠叙事的泛概念**"。这是理解行情结构的关键，别把"AI"当成一个整体。

## 输出契约

落盘路径：`archive/raw/宏观/<日期>_宏观_<主题>_v<版本>.md`
结构化明细（如有）：同目录同名 `.csv`（frontmatter 用 `data_file` 指向）。

**frontmatter（必填）**
```yaml
source: "综合 Wind / Choice / 证券时报 / 新浪财经 等多源公开数据"
url: "<代表来源 URL，须 http(s) 开头>"
fetched_at: YYYY-MM-DD
type: 宏观
structure: unstructured      # 分析型报告；纯数据表为 structured
confidence: high|medium|low
tags: [热钱, 资金流向, ...]   # 经 config/tags.yaml 别名归一
keywords: [电子, 半导体, ...]
reason: "一句话分类理由（可审计）"
data_file: <同名 .csv>       # 可选
project: P01                # 所属调研项目（新建/确认：script/load_context.py --list）
```

**正文结构（建议）**
0. 核心结论（先给结论，3–4 条）
1. 口径定义（本文"XX"指什么）
2. 全景（四路资金表格 + 关键分化）
3. 深度分析：最集中行业（产业链拆解 / 基本面驱动 / 资金结构）
4. **反方论点 / 风险（强制章节，无过滤）**
5. 与团队已知领域的勾连（落到具体标的/专项）
6. 数据源与置信度（含局限说明）

## 执行流程
1. **先跑 `script/load_context.py --project <PID>`** 加载该项目状态机（没有所属项目就先 `script/new_project.py` 建一个，或在加载全部的情况下开工）
2. 检索多源数据（按四路资金口径分别取数，标注窗口与来源）
3. 交叉验证 → 形成结论与分化判断
4. 选定"资金最集中"行业做深度拆解（产业链 + 基本面 + 资金结构）→ **这是交给下游 `research-industry` 的接力棒，必须显式点名**
5. 写**反方论点**（估值分位 / 拥挤度 / 杠杆获利盘 / 外部灰犀牛 / 业绩兑现）
6. 落 `output/` 暂存 → 用户确认 → 移 `archive/raw/宏观/`（frontmatter 标 `project: <PID>`）
7. 跑 `script/validate_frontmatter.py` 校验
8. **回写本项目 `research/<PID>/research-state.yaml`**：新增 claims（带 evidence/data 指针）、建 monitors（周度主力净流入 / PE 历史分位 / 北向持仓占比）、queue 补 Q 条目（跨项目方法论提升到 `research/_shared/`）
9. 交 **wiki-skill** 抽实体建双链 → `archive/wiki/` + 更新 `MOC.md`

## 反方论点清单（写第 4 章时逐项过）
- **估值**：PE/PB 历史分位是否 >90%？龙头 PE 是否脱离行业？
- **拥挤**：机构持仓集中度、前十大重仓占比、是否历史高位？
- **杠杆获利盘**：累计涨幅多大？跌 20% 主力是否仍盈利？
- **外部**：美联储路径、地缘、汇率、海外映射（费城半导体等）
- **业绩兑现**：涨幅是否已 price-in？财报窗口临近？风险提示公告密度？
- **历史类比**：与过往抱团终局（2021 白酒 / 2022 新能源）的结构相似度

## 常用监控指标（可作"过热预警"）
- 目标行业**周度**主力净流入
- 目标行业 **PE 历史分位**
- 北向**该行业持仓占比**

## 引用
- 规范：`.workbuddy/skills/file-manager/`（`USER-GUIDE.md`、`references/naming-and-frontmatter.md`）
- 分类：`config/types.yaml`、`config/tags.yaml`、`docs/prototype/06-分类与标签方案.md`
- 校验：`script/validate_frontmatter.py`
- 主线：`docs/prototype/07-调研主线方法论.md`（Track A 第一段）
- 下游：`.workbuddy/skills/research-industry/` → `.workbuddy/skills/research-company/` → `.workbuddy/skills/wiki-skill/`
- 状态机（按项目）：`research/<PID>/research-state.yaml` + `script/load_context.py --project <PID>`（新建项目：`script/new_project.py`）
- 范例：`archive/raw/宏观/20260919_宏观_热钱流动行业分析_v1.md` 及其 wiki 版（项目 P01 · 2026-09-19 行业热点观察）
