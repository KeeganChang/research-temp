# ROUTING.md — 5 种 Track 的使用边界与选线决策

> 本文件回答「用户这个问题，该走哪条 Track」。流程与门禁见 `references/skills/research-core/SKILL.md`；各 Track 的具体定义见 `references/skills/research-track-*/`。**选线不写死**——直接按任务描述套本决策树判定，不依赖任何登记表。
> 选线发生在门禁 **G2**；选错主线 = 逻辑错位 = 结论作废。
>
> **⚡ 每任务选线速查见 `references/ROUTING-quick.md`（仅 §一+§二，≈800 tok）。本文件是完整版，§三 反模式 / §四 配合 / §五 method 清单 / §六 扩展 按需才读。**
>
> **位置与路径**：本文件位于 `references/` 下；文中路径**相对套件根目录**书写。

---

## 一、5 种 Track 一句话边界

| Track | 推理方向 | 一句话 | 落点（交付） | 典型提问 |
|-------|----------|--------|--------------|----------|
| **drill** 下钻选优 | 演绎·总→分 | 大池子里哪个最优？ | 最优子集 + 正反论点 | 选哪个赛道/标的/环节/平台？ |
| **entry** 进入测绘 | 横向·context→players | 能不能进、怎么进？ | 机会区/禁区 + 玩家地图 | 进不进某市场/平台？ |
| **diagnostic** 诊断归因 | 逆向·果→因 | 为什么偏离目标？ | 根因诊断 + 修复 | 转化/营收为什么掉？ |
| **inductive** 归纳洞察 | 归纳·样本→规律 | 数据里藏着什么规律？ | 分群/模式 + 洞察 | 用户怎么分、谁值钱？ |
| **scenario** 情景推演 | 推演·现在→未来 | 如果…会怎样？ | 情景矩阵 + 触发 | 市场规模多大、敏感性？ |

---

## 二、决策树（G2 用）

1. 用户是否已有一个**现状/对象**，要找「为什么」→ **diagnostic**
2. 否则，用户要的是「从数据里找规律/分群」→ **inductive**
3. 否则，用户要的是「推演未来/测算规模」→ **scenario**
4. 否则，用户要的是「选一个最优的 X」（标的/赛道/环节/人群子集/平台）→ **drill**
5. 否则，用户要的是「进入/布局一个新对象（市场/平台/品类）」→ **entry**
6. 仍无法判定 → 退回 G1 澄清驱动问题，**不得强行选线**

> 优先级：diagnostic > inductive > scenario > drill > entry。
> 先排除「已有对象要解释/归纳/推演」，剩下的才是「选（drill）」或「进（entry）」。

---

## 三、边界冲突与反模式（用错的典型）

- **drill 变 entry**：把「选标的」跑成「市场进入」→ 多做了玩家地图，却没给短名单。
- **diagnostic 变 drill**：把「经营诊断」跑成「下钻选优」→ 只找最优环节，却没定位根因。
- **inductive 变 scenario**：把「用户分群」跑成「情景推演」→ 给了规模预测，却没给可行动分群。
- **scenario 变 inductive**：把「测算规模」跑成「归纳洞察」→ 给了分群，却没给假设依赖与敏感性。
- **entry 变 drill**：把「进不进市场」跑成「选哪个标的」→ 跳过了准入/玩家格局，直接给标的。

---

## 四、Track 之间的配合（非互斥场景）

同一条链不可混跑（铁律 #3）；跨 Track 用**父子 task** 串起：

- **entry → diagnostic**：先测绘市场（entry），再诊断自身适配度（diagnostic）。
- **drill → scenario**：选出标的后做敏感性推演（scenario）定仓位。
- **inductive → drill**：先归纳高价值客群（inductive），再下钻找对应标的（drill）。
- **diagnostic → scenario**：定位根因后，推演修复方案的情景收益。

实现方式：父项目选一条主 Track，`research-state.yaml` 的 `node.parent` 串起子 task 选另一条 Track，互不污染。

---

## 五、Track 与 method 的关系

- **Track** 决定「推理方向 + 门禁 + 交付形态」（5 种，常驻路由分类）。
- **method 技能**提供某语境的固化打法（算法 / 口径 / 反方清单），`belongs_to_track` 指向所属 Track，如 `method-topdown`→drill（含 A股 细化）、`method-market-entry`→entry。
- research-core **按语境匹配 belongs_to_track 一致的 method** 加载；Track 骨架本身始终启用。

当前 method 清单（新增/启停须同步本表与 `SKILL.md` 构成表）：

| method | 所属 Track | 加载方式 |
|---|---|---|
| `method-topdown` | drill | 语境契合「投资/资产选择（A股 景气链）」时按需加载 |
| `method-sector-momentum` | drill | 语境契合「行业景气度监测」时按需加载 |
| `method-market-entry` | entry | 语境契合「市场/平台进入（PEST→players）」时按需加载 |
| `method-ecommerce-ops` | diagnostic | 语境契合「电商/直播电商经营诊断（含大促战报诊断与复盘）」时按需加载 |
| （inductive / scenario 暂无 method） | — | 直接用对应 Track 通用骨架 |
- 方法**不再用 `enabled` 开关**：按任务语境匹配其 described 领域加载；**无契合 method 即兜底回退通用骨架**，不强行套用领域口径。

选完 Track 与 method 后，还需定预算档（shape × cost class）——见 **§七 Effort 预算** 与 `references/rules/effort.md`。

---

## 六、扩展：新增 Track / method

- **新增一条 Track**：在 `references/skills/` 下建 `research-track-<x>/SKILL.md`，frontmatter 标 `type: track`、`depends_on: [research-core]`；骨架只写「推理方向、问什么、门禁、交付形态」，不绑业务域。`research-core` 按 `project.yaml` 的 `track` 字段（由 G2 动态判定后写入）路由到此。
- **新增某语境打法**：复制 `references/skills/method-topdown/` 成 `references/skills/<your-method>/`，填 `belongs_to_track` 指向某 Track，门禁自动生效，不改 core。
- 选线是**动态判定**（见 §二 决策树），不依赖任何写死的登记表；本文件即选线权威。

---

## 七、Effort 预算（路由第三步：Track → method → Effort）

选完 Track（§二）与 method（§五）后，还需定「这次花多少力气」——即执行形态 `shape` × 成本档 `cost class`（启发式，详见 `references/rules/effort.md`）：

- **shape**：`straightforward`（直球）/ `breadth`（横向切分）/ `depth`（纵向多视角）。method 技能声明其默认 shape。
- **cost class**：`S / M / L / XL`，默认取该 shape 的 `default_cost`；重型任务显式选档并写入项目记录。
- **可权衡**：偏离预算须记理由（记入 `research-state.yaml` 节点或交付物 method note）；**升到 `XL` 必须人工确认**。
- 与门禁互补：G1–G6 管流程推进，Effort 管花费上限；`tool_calls` / `sources` 为整个 work package 跨 worker 总额。

> 本步对应 GitHub v3.0 的「路由第三步」，本地回填于 2026-11-05。门禁 G1–G6 与 G_rubric 不变。

## 引用

- 流程与门禁：`references/skills/research-core/SKILL.md` ｜ 编排：`references/skills/research-core/SKILL.md`
- Effort 预算（shape × cost class）：`references/rules/effort.md` ｜ 硬约束红线 H1–H12：`references/rules/constraints.md`
