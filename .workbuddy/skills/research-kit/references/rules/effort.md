# 执行预算启发式 Effort（shape × cost class）

> **来源**：GitHub `keegan-zh1/research-assistant` v3.0 的 `config/effort.yaml` + `references/analysis/execution.md`，2026-11-05 回填本地。
> **性质**：**启发式起点，不是质量证明**。它回答「这次调研花多少力气」，与 G1–G6 门禁互补——门禁管流程推进，本文件管花费上限。
> **单一维护地**：未来 `script/route_methods.py`（或等价选线脚本）以本文件的 YAML 块为唯一数据源；method 技能只声明其默认 `shape`，`cost class` 默认取该 shape 的 `default_cost`。
> **可权衡项**：标注「heuristic」的执行形态 / 预算 / 搜索顺序可权衡，但**偏离须记录理由**（记入 `research-state.yaml` 节点或交付物的 method note）。XL 档必须人工确认。

---

## 0. 何时用

每次调研在「选完 Track（G2）→ 选定 method」之后，定预算档：

- 轻量（一次性 / 答案唯一）：可不显式选档，默认按 method 的 `shape` 走其 `default_cost`。
- 重型（对外 / 入决策 / 多人协作 / 跨会话）：**必选** shape + cost class，并写入项目记录。

---

## 1. 执行形态 shapes

| shape | 名称 | 何时用 | 拆分方式 | 最大 worker | 默认 cost |
|---|---|---|---|---|---|
| `straightforward` | 直球查询 | 单个事实 / 单指标 / 单一权威源即可答 | 不拆；主 agent 直出，或派 1 个只读 worker 取证据 | 1 | S |
| `breadth` | 横向切分 | 能按对象 / Track / 平台 / 地区切成边界清晰、互不重叠的子问题 | 先定对象清单 + 统一对比口径，再按对象拆；同口径下聚合 | 5 | M |
| `depth` | 纵向多视角 | 单一核心问题需多类型源 / 多方法 / 多替代解释 | 定义 2–4 个互补视角（如自报 / 外部验证 / 反证 / 替代机制），各取证据后在主分析类型下综合 | 4 | M |

> `breadth` 与本地 `references/rules/granularity.md` 的「扇出轴白名单（对象·子行业·情景）」一致；`depth` 的多视角互补即本地「反方 ≥5 + 多视角」的结构化版。

---

## 2. 成本档 cost_classes

| 档 | tool_calls | sources | workers | 相对 token 成本 | 确认要求 |
|---|---|---|---|---|---|
| `S` | 10 | 15 | 1 | 低 | 无 |
| `M` | 45 | 50 | 3 | 中 | 无 |
| `L` | 100 | 120 | 5 | 高 | 记理由（record_reason） |
| `XL` | 不设上限 | 不设上限 | 不设上限 | 极高 | **人工确认（human）**；确认时须给出实际预算 |

> `tool_calls` / `sources` 是**整个 work package 跨所有 worker 的总额**，不是单 worker 上限。

---

## 3. 预算策略 budget_policy

- **计量单位**：一个 work package 执行一次；`tool_calls` 与 `sources` 为所有 worker 的合计。
- **worker 上限**：生效上限 = `min(shape.max_workers, cost_class.workers)`。
- **用量记录**：项目记录（`research-state.yaml` 节点，或交付物 method note）。
- **预算耗尽（on_exhausted）**：停止扩张；报告「已发现什么 / 仍缺什么 / 继续的预期价值 / 建议的新 cost class」。
- **升级（escalation）**：
  - 档内调整：主 agent 可在合同档内重新分配。
  - 升到 `L`：主 agent 在项目记录记理由后继续。
  - 升到 `XL`：**需人工确认**；XL 无默认上限，确认时须声明实际预算。

---

## 4. 委派简报 delegation_brief

派发给子 worker 的简报须含：

- `node_id` · `question` · `routing`（Track + method）
- `shape` · `inputs_and_definitions`（统一口径）· `source_guidance`
- `output_contract` · `boundaries` · `budget` · `stopping_conditions` · `read_only_declaration`

---

## 5. 机器可读源（单一数据源）

```yaml
# schema_version: '1.0'
# 单一维护地；若未来写 route_methods.py，以本块为准。
shapes:
  straightforward: { name: Straightforward query, max_workers: 1, default_cost: S }
  breadth:        { name: Horizontal split,    max_workers: 5, default_cost: M }
  depth:          { name: Vertical multi-perspective, max_workers: 4, default_cost: M }
cost_classes:
  S:  { tool_calls: 10,  sources: 15,  workers: 1, relative_token_cost: low,       confirmation: none }
  M:  { tool_calls: 45,  sources: 50,  workers: 3, relative_token_cost: medium,    confirmation: none }
  L:  { tool_calls: 100, sources: 120, workers: 5, relative_token_cost: high,      confirmation: record_reason }
  XL: { tool_calls: null, sources: null, workers: null, relative_token_cost: very_high, confirmation: human }
budget_policy:
  workers_rule: min(shape.max_workers, cost_class.workers)
  on_exhausted: stop expanding; report found/missing/expected_value/suggested_class
  escalation: { to_L: record_reason, to_XL: human_confirmation_with_actual_budget }
```

---

## 6. 与本地门禁 / 纪律的关系

- 本文件是**启发式（可权衡）**，与 `references/ROUTING.md` 的 Track/ method 选线共同构成「路由第三步」；门禁 G1–G6 与 G_rubric 不变，仍硬卡。
- 偏离预算须记理由，呼应本地「铁律：删后验证 / 显式证据再行动」的可审计传统。
- XL 强制人工确认，呼应 `references/rules/constraints.md` 的 H5（人类权威）。
