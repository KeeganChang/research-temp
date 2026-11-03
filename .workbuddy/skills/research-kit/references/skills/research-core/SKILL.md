---
name: research-core
description: Research Kit 的编排与门禁控制核心。负责加载上下文、推进阶段、按任务复杂度决定是否回写状态机（状态机为可选复用层，非每轮回写门禁）。任何调研的主入口都必须经过本技能。按语境匹配 belongs_to_track 一致的 method skill；无契合 method 时回退通用骨架。
type: orchestration
version: 1.2
---

# research-core — 编排与门禁控制

## 职责
本技能是调研流程的「交通指挥」。它不生产结论，只保证**流程可控、结论可审计、会话可续做**。

## 触发条件
- 用户开启一项新的调研 / 续做旧项目 / 接入新框架模块时。

## 执行流程（严格按门禁推进）

### Step 0 — 定位项目
- 若为续做：`load_context --project <PID>` 读取 `focus / claims / monitors / queue / datasets`。
- 若为新建：`new_project --id <PID> --name "..." --track <drill|entry|diagnostic|inductive|scenario>`，生成 `research/<PID>-<slug>/` 及 `research-state.yaml`。track 值由 G2 按 `references/ROUTING.md` 决策树动态确定，**不预置、不写死**。
- 建子 task：`new_project --parent <父PID>`，只需在新节点写 `node.parent`，**不改父文件**。
- **门禁 G1 未过不得进入 Step 1。**

### Step 1 — 立项门禁 G1
校验三件套：
1. 驱动问题（可量化、可证伪）
2. `scope_in` / `scope_out`（边界）
3. 交付物形态（报告 / 表格 / 卡片）

不满足 → 退回向用户澄清，不推进。

### Step 2 — 选线门禁 G2（按任务描述套 `references/ROUTING.md` 决策树五选一，不写死）
- **drill** 下钻选优：演绎·总→分，落点「最优子集 + 多空」。
- **entry** 进入测绘：横向·context→players，落点「机会区/禁区 + 玩家地图」。
- **diagnostic** 诊断归因：逆向·果→因，落点「根因诊断 + 修复」。
- **inductive** 归纳洞察：归纳·样本→规律，落点「分群/模式 + 洞察」。
- **scenario** 情景推演：推演·现在→未来，落点「情景矩阵 + 触发」。
- 选线**不写死**：直接依据「任务描述」套用 `references/ROUTING.md` 决策树判定，而非读某个预设字段；判定结果写回 `project.yaml` 的 `track` 字段仅作续做记录。同一条链不可混跑（铁律 #3），跨 Track 用父子 task 串起。

### Step 3 — 分模块采集（G3）
- 按所选 Track 加载对应**骨架**技能（research-track-<drill|entry|diagnostic|inductive|scenario>）。
- **按语境加载 method skill**：G2 选定 Track 后，若任务语境契合某 `method-*` 的 described 领域（belongs_to_track 一致），则加载该 method；**无契合 method 时兜底 = 仅用该 Track 通用骨架**（agent 与用户按骨架 D1–D3 自行定义口径），不加载任何领域 method。
- 每个业务框架以 `research-module` 模板接入，逐模块执行；每模块产原始证据+数据指针写入 `datasets` 防重复抓数。
- 资讯 / 新闻类来源：调用 `script/snapshot_url.py` 存**可检索文本快照**（URL / fetched_at / meta / sha256 + `_index.json`），不存截图；快照作为可核查证据，不进正文。

### Step 4 — 成稿门禁 G4
逐项核查（任一不满足 → 回 Step 3 补数，带 `depends_on` 入 `queue`）：
- [ ] 反方论点 ≥ 5 条（且至少 1 条为时间维度）
- [ ] 关键口径已登记（单位 / 口径冲突处理）
- [ ] 每条 claim 与证据可互指（evidence ↔ data 指针）

### Step 5 — 校验门禁 G5
- 每条 claim 标注 `confidence`（high/medium/low）与 `status`（open → validated/falsified）。
- 无「悬空结论」（即无证据支撑的断言）。

### Step 5.5 — 交付门禁 G_rubric（前置清单，见 `references/report-rubric-v1.md`）
交付前逐条过 rubric §1 前置自检清单，**任一未过不得交付**：
- [ ] 每个关键数字有内联引用（来源文件 + 短引文 + 抓取时间），无 `[UNSOURCED]`
- [ ] 顶部有口径块（单位 / 基准日 / 缺月处理 / 代理指标 / caveat）
- [ ] 反方 ≥5 条，且至少 1 条为时间维度
- [ ] 原始返回独立落盘（服务复算），不进报告正文
- [ ] 结论由脚本生成 / 校验，无手写数字与计算值矛盾
- [ ] 若多源：标注每个来源发布方，≥2 路真正独立源
- [ ] 判断类结论标 `kind: judgment`，并记录被否决的备选

> 重型输出（对外 / 入决策 / 多人协作）另须过 rubric §2 后置五维评分（通过线 ≥8/10 且任一维≠0）。
> 交付形态与载体分层见 `references/delivery-standard.md`（Lark Doc 为主 + 三段式内联 + Sheet 退 reference）。

### Step 6 — 回写（可选 · 状态机为复用层，非门禁）
- **状态机自 2026-11-02 起降级为可选复用层**（见证据链精简方案 v1.1 §3.4）：一次性 / 轻量任务**不强制**回写；仅**月频重跑 / 跨会话续做 / 多人协作**才启用项目层与 `research-state.yaml`。
- 启用时：更新 `research-state.yaml`：focus / claims / monitors（带阈值）/ queue / datasets。
  - 多 task 项目：只回写**本节点**的 `research-state.yaml`，父节点的汇总由 `load_context` 按 `node.parent` 运行时派生，不手写。
  - `monitors` 须设 `last` 观测值与 `as_of`，触发阈值时生成 `queue` 条目。
- **准确性保障由「报告内联引用 + 口径块 + 反方≥5」承担**，不依赖状态机；因此**未回写不再等于"未完成"**，仅意味本次结论未登记进跨会话复用层。

## 护栏（硬约束）
- 不自建框架类别，新框架走 `research-module` 模板接入。
- 方法技能（method）按语境按需加载，不靠 `enabled` 开关；无契合语境回退通用骨架（兜底）。
- 不跳过门禁；门禁失败必须显式退回，不得「假装通过」。
- 所有路径用 `<workspace>/` 占位，密钥不落文档。

## 引用
- 状态机模板：`references/templates/research-state.yaml`（**可选复用层**，非必写）
- 门禁定义：本文件 Step 1–6（G1–G6 + 交付门禁 G_rubric）
- 骨架（5 种 Track）：research-track-drill / -entry / -diagnostic / -inductive / -scenario
- 方法技能（按语境按需加载，无契合回退通用骨架）：method-topdown（景气链·A股，→drill）/ method-market-entry（市场进入，→entry）/ method-sector-momentum（行业景气度横截面，→drill）/ method-ecommerce-ops（电商经营诊断，→diagnostic）
- 报告质量评分卡（前置自检 + 后置五维）：`references/report-rubric-v1.md`
- 交付标准（Lark Doc 为主 / 三段式内联 / Sheet 退 reference / 文件级粒度 / 一次性也推 Doc）：`references/delivery-standard.md`
- Lark Doc 主交付模板：`references/templates/lark-doc-delivery.md`
