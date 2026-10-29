---
name: research-module
description: 框架接入模板。任意行业分析 / 经营分析框架（宏观、用户画像、渠道分析、Cohort 客群分析…）复制本模板即可接入 Research Assistant，自带方法论、反方清单、口径登记与门禁条件。
type: module-template
version: 1.0
depends_on: [research-core]
---

# research-module — 框架接入模板

> 用法：复制本目录为 `skills/<your-framework>/`，按下方必填段填写。每个模块独立、可插拔，经 research-core 门禁调度。

---

## 必填字段

### 1. 元信息（SKILL.md frontmatter）
```yaml
name: <framework-id>
description: <一句话说明本框架解决什么问题、何时调用>
type: module
version: 1.0
depends_on: [research-core]
belongs_to_track: drill | entry | diagnostic | inductive | scenario   # 归属主线
```

### 2. 核心问题
本框架回答什么？必须可量化、可证伪。

### 3. 输入数据口径（SSOT）
- 必需字段、单位、时间窗口、来源分层（Tier1 官网 / Tier2 二手 / Tier3 转述）。
- **口径冲突处理规则**：如两份来源数值矛盾，以何为准、如何标注。

### 4. 处理 SOP（方法）
- 步骤化，每步可复核。
- 引用标准方法（如 Cohort：N日留存矩阵、滚动留存、LTV 折现假设）。

### 5. 反方论点清单（门禁 G4 强制）
- 至少 5 条，至少 1 条为时间维度。
- 每条写明「什么情况下本结论会错」。

### 6. 输出交付物
- 交付形态（表 / 图 / 结论短句）+ 落位（output/ → archive/raw）。
- 关键指标定义（避免歧义，如「留存」指首日还是首单）。

### 7. 模块门禁条件（局部 Gate）
- 本模块「可交付」的最小通过条件（证据充分性 / 口径一致性 / 反方齐备）。

---

## 示例：Cohort 客群分析模块（骨架）
- **核心问题**：客户在 N 日后还留得住吗？客群生命周期价值多少？
- **输入口径**：用户 ID + 首行为日期 + 行为日期；留存定义 = 首单后第 N 日是否活跃；LTV 折现假设单列。
- **SOP**：建同期群 → 算 N日/滚动留存 → 拆客单价×频次 → 估算 LTV → 衰退率诊断。
- **反方**：口径不一致导致虚高；高渗透低客单价陷阱；促销扭曲留存；季节错配；样本截断（新群未成熟）。
- **交付物**：留存曲线 + 客群 LTV 分层表。
- **门禁**：留存定义已登记 + 反方≥5 + 与证据可互指。

---

## 引用
- 编排与门禁：research-core
- 主线骨架：research-track-drill / -entry / -diagnostic / -inductive / -scenario
