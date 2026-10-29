---
name: research-core
description: Research Assistant 的编排与门禁控制核心。负责加载上下文、推进阶段、把结论回写状态机。任何调研的主入口都必须经过本技能。仅路由 enabled: true 的 method skill；enabled: false 的默认不参与。
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
- 若为新建：`new_project --id <PID> --name "..." --track <drill|entry|diagnostic|inductive|scenario>`，生成 `research/<PID>-<slug>/` 及 `research-state.yaml`。track 值由 G2 按 `ROUTING.md` 决策树动态确定，**不预置、不写死**。
- 建子 task：`new_project --parent <父PID>`，只需在新节点写 `node.parent`，**不改父文件**。
- **门禁 G1 未过不得进入 Step 1。**

### Step 1 — 立项门禁 G1
校验三件套：
1. 驱动问题（可量化、可证伪）
2. `scope_in` / `scope_out`（边界）
3. 交付物形态（报告 / 表格 / 卡片）

不满足 → 退回向用户澄清，不推进。

### Step 2 — 选线门禁 G2（按任务描述套 `ROUTING.md` 决策树五选一，不写死）
- **drill** 下钻选优：演绎·总→分，落点「最优子集 + 多空」。
- **entry** 进入测绘：横向·context→players，落点「机会区/禁区 + 玩家地图」。
- **diagnostic** 诊断归因：逆向·果→因，落点「根因诊断 + 修复」。
- **inductive** 归纳洞察：归纳·样本→规律，落点「分群/模式 + 洞察」。
- **scenario** 情景推演：推演·现在→未来，落点「情景矩阵 + 触发」。
- 选线**不写死**：直接依据「任务描述」套用 `ROUTING.md` 决策树判定，而非读某个预设字段；判定结果写回 `project.yaml` 的 `track` 字段仅作续做记录。同一条链不可混跑（铁律 #3），跨 Track 用父子 task 串起。

### Step 3 — 分模块采集（G3）
- 按所选 Track 加载对应**骨架**技能（research-track-<drill|entry|diagnostic|inductive|scenario>）。
- **仅路由 `enabled: true` 的 method skill**（如 `method-topdown` 景气链，默认 `enabled: false`）；未启用的默认不参与，除非用户显式启用。
- 每个业务框架以 `research-module` 模板接入，逐模块执行；每模块产原始证据+数据指针写入 `datasets` 防重复抓数。

### Step 4 — 成稿门禁 G4
逐项核查（任一不满足 → 回 Step 3 补数，带 `depends_on` 入 `queue`）：
- [ ] 反方论点 ≥ 5 条（且至少 1 条为时间维度）
- [ ] 关键口径已登记（单位 / 口径冲突处理）
- [ ] 每条 claim 与证据可互指（evidence ↔ data 指针）

### Step 5 — 校验门禁 G5
- 每条 claim 标注 `confidence`（high/medium/low）与 `status`（open → validated/falsified）。
- 无「悬空结论」（即无证据支撑的断言）。

### Step 6 — 回写门禁 G6
- 更新 `research-state.yaml`：focus / claims / monitors（带阈值）/ queue / datasets。
- 多 task 项目：只回写**本节点**的 `research-state.yaml`，父节点的汇总由 `load_context` 按 `node.parent` 运行时派生，不手写。
- `monitors` 须设 `last` 观测值与 `as_of`，触发阈值时生成 `queue` 条目。
- **未回写 = 本次调研不可续做，视为未完成。**

## 护栏（硬约束）
- 不自建框架类别，新框架走 `research-module` 模板接入。
- 方法技能（method）默认 `enabled: false`，不参与自动路由；启用须显式置 `enabled: true`。
- 不跳过门禁；门禁失败必须显式退回，不得「假装通过」。
- 所有路径用 `<workspace>/` 占位，密钥不落文档。

## 引用
- 状态机模板：`templates/research-state.yaml`
- 门禁定义：根 `AGENTS.md`
- 骨架（5 种 Track）：research-track-drill / -entry / -diagnostic / -inductive / -scenario
- 方法技能（均默认不启用）：method-topdown（景气链，→drill）/ method-market-entry（市场进入，→entry）/ method-sector-momentum（行业景气度横截面，→drill）/ method-ecommerce-ops（电商经营诊断，→diagnostic）
