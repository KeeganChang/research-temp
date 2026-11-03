# ROADMAP.md — 规划 · 进度 · 场景 · 待办 · 设计演进史

> **单一规划文档**（2026-10-30 由 `MILESTONE.md` / `PROGRESS.md` / `SCENARIO.md` / `TODO.md` 合并而来，原 prototype/ 设计稿演进史并入 §7）。
> 给"往哪走、做到哪了、当年为何这么定"一个统一去处。系统架构见 `ARCHITECTURE.md`；变更逐条见 `CHANGELOG.md`。

---

## 1. 里程碑总览（M1 / M2 / M3）

| 里程碑 | 目标 | 完成标准 | 状态 |
|--------|------|----------|------|
| **M1 · 框架设计** | 确立本地优先 AI 知识基础设施的整体架构、铁律、频率分层、度量与数据源方案 | `AGENTS.md` / `ARCHITECTURE.md` / `README.md` 三件套齐备；`prototype/01–09` 设计稿归档；脚本校验链（`validate_frontmatter` / `load_context` / `new_project`）跑通；命令风格统一为 `python -m` | ✅ 已完成（2026-09-22）|
| **M2 · 跑通行业研究闭环** | 用 research-assistant 套件跑一个真实行业的完整闭环，验证框架可用 | 一份可交付的行业研究报告（六段式 + 兑现度矩阵）→ 校验 → 入 `archive/raw/行业/` → wiki 双链 → 对应 claim 落 `research-state.yaml`；template 回跑约定生效 | 🔄 待终核（P03 芯片行业深度 + P04 国内芯片 PEST 已产出并回写状态机；wiki 双链段待核）|
| **M3 · 数据源与度量自动化** | 把度量与数据源方案落地为可运行管道 | `data/` + `catalog.yaml` 建好；世界银行 1 数据集跑通"抓数→入库→查询→引用"；`metrics.py` / `query_data.py` / `refresh_monitors.py` / `feishu_stats.py` 就位；命中率 / 复盘次数报表可出；证据 Tier1-3 标注落地 | ⬜ 规划中（高优先级待办）|

> 资讯日频管线（lark base 多维表格 + 卡片推送）优先级一般，列入 M3 之后或独立跟踪，不阻塞 M2/M3。

---

## 2. 当前进度与已确认基线

### 2.1 阶段状态
| 阶段 | 状态 | 说明 |
|------|------|------|
| 0 开发核心对齐 | ✅ 已认可 | 可沉淀/复用/迁移/审计；三层核心资产 |
| 1 组件清单（5 大块） | ✅ 已收尾 | 已查实 WorkBuddy 配置 |
| 2 分工 | ✅ 已定 | 见 §3 |
| 3 技术栈 | ✅ 已定 | 模型层 = 调用方 chat 模型，不配 API（见 §3.3）|
| 4 流程确认 | ✅ 框架已定 | SSOT 双域分离已裁定（AGENTS 铁律#2）|

### 2.2 已确认基线（2026-09-19）
- **基础工具链**：`obsidian` + `python` + `git`
- **知识库策略**：**本地为主**（Obsidian vault + 本地文件）；**飞书出报告 + 跨平台分享**
- **文件夹基线（最终结构）**：`docs/`(README/ARCHITECTURE/CHANGELOG/ROADMAP) · `archive/`(Obsidian vault: raw/wiki/inbox) · `output/` · `memory/`(MEMORY.md+*.jsonl) · `.workbuddy/memory/`(按日) · `secrets/`+`.env` · `script/` · `.workbuddy/skills/` · `AGENTS.md`(项目指令/CLAUDE.md等价)
- **WorkBuddy 实际落点（已查实）**：
  - skills → 用户级 `~/.workbuddy/skills/` / 项目级 `{ws}/.workbuddy/skills/`（**本项目选项目级**）
  - memory → 项目级 `{ws}/.workbuddy/memory/`（`YYYY-MM-DD.md`）+ 项目级 `memory/`（`MEMORY.md` + `*.jsonl`）
  - 身份文件 `SOUL.md` / `IDENTITY.md` / `USER.md` 在 `~/.workbuddy/`（用户级，全局通用）
  - 项目指令：`AGENTS.md`（根目录，neutral 写法，自动加载，CLAUDE.md 等价）

### 2.3 已决事项（查漏补缺 8 项，全 ✅）
| # | 缺口 | 结论 |
|---|------|------|
| 1 | skills/memory 落点 | skills→`.workbuddy/skills`；memory 双轨（.workbuddy/memory 按日 + 项目 memory/）|
| 2 | 层级 | 项目级 `.workbuddy/skills`（团队共享）+ 用户级 `~/.workbuddy/skills`（个人习惯）|
| 3 | secrets 存储 | 双轨：`secrets/`(基建API) + `.env`(项目密钥)，均 gitignore；连接器OAuth由平台托管 |
| 4 | vault 关系 | `archive/` 即 Obsidian vault（SSOT），含 raw/wiki/inbox |
| 5 | outputs/archive 协同 | `output/` 暂存(确认前) → `archive/raw/` → wiki-skill → `archive/wiki/` |
| 6 | git 边界 | **仅 `script/` 入库**；本地知识库(archive/memory/docs)不入库，靠 CHANGELOG + 每日 .workbuddy/memory/ 记录更新 |
| 7 | 典型场景 | 已给 20 场景（见 §4）|
| 8 | 飞书适配边界 | 仅出报告+分享(只读镜像)；协作编辑暂缓。~~RUtable 写入~~ **2026-11-04 作废**（事实层已废止，数据唯一归属地是报告本身） |

---

## 3. 组件架构与分工

### 3.1 五大块组件映射（基于真实配置）
- **大块一 · 文件与归档（file & archive / vault）**：`file-manager`（结构/命名/落位规则）；`wiki-skill`（raw→抽实体/双链/MOC，吸收原 indexer）；`archive/` 即 Obsidian vault（SSOT）。
- **大块二 · 工具能力（atomic）**：`analysis` / `frontend` / `scraper` / `markitdown`（python + WorkBuddy skill）；**`research-kit` 单列一大类技能**（5 Track + method-*）。
- **大块三 · 隐私与环境（privacy & env）**：skills 项目级；memory 双轨；`secrets` 双轨；`env-manifest`（WSL/Hermes/K8s；uv/nvm 版本锁定）。
- **大块四 · 平台适配器（adapters）**：`obsidian-adapter`（极薄/可省）；`feishu-adapter`（出报告 + 分享）；`claw-adapter`（跨平台日程聚合）。
- **大块五 · 知识迁移（migration）**：`migrate-research`（合并进 wiki-skill）；`migrate-ai-dev`（沉淀为 memory/jsonl）；`sync`（本地为主，飞书为镜像）。

### 3.2 分工（谁做 / 依赖 / IO 边界）
| 组件 | 执行者 | 依赖 | 输入 → 输出 |
|------|--------|------|------------|
| `file-manager` | chat 模型按 `SKILL.md` + `references/` 执行 | `config/*`、`script/validate_frontmatter.py` | 任意文件 → 合规命名 + frontmatter + 落位 |
| `wiki-skill` | chat 模型执行（**当前手工，待脚本化**）| `archive/raw/`、file-manager | `raw/*.md` → `archive/wiki/` 双链笔记 + `MOC.md` |
| `research-kit`（各 Track）| chat 模型 + 检索/抓取 | `config/`、file-manager、外部数据源 | 主题 → `output/` → 人工确认 → `archive/raw/<type>/` |
| 分类引擎（待建）| 规则匹配 + chat 模型打标 | `types.yaml`、`tags.yaml` | `inbox/` → 写 frontmatter + 移入 `raw/<type>/`；低 conf → `tags.proposed.yaml` |
| `script/`（校验 / 密钥）| Python 本地运行 | pyyaml | md → 校验结果；`secrets/`+`.env` → 运行态密钥 |
| 平台适配器（obsidian/feishu/claw）| 待办 | 核心稳定后 | — |

**边界原则**：能力层（skill）由 chat 模型驱动；**确定性逻辑放脚本**（校验、密钥读取、双链完整性检查），**不确定逻辑放提示词/模型**（抽取、打标、分析）。

### 3.3 技术栈（仅已确认组件）
| 层 | 选型 | 说明 |
|----|------|------|
| **模型 / 推理** | **调用方 chat 模型**（WorkBuddy / `claude -p`）| **不配大模型 API、不选型后端**；抽取/打标/分析由当前会话模型执行，密钥仅用于飞书/MCP 等外部服务 |
| 存储 | 本地文件系统 + Obsidian（`archive/` = vault，SSOT）| md + csv/json（单次）+ sqlite（cron）|
| 配置 | YAML（`config/types.yaml`、`config/tags.yaml`）| 改配置即改行为，不碰代码 |
| 脚本 | Python 3（`script/`，依赖 pyyaml）| `validate_frontmatter.py`、`load_secrets.py` |
| 版本 | git（**仅 `script/` 入库**）| 知识库不入库，靠 `CHANGELOG.md` + 每日 `.workbuddy/memory/` |
| 格式转换 | markitdown（md 侧索引）| 原件保真存 `archive/`，md 用于分类/检索/双链 |
| 平台 | Obsidian（读）+ 飞书/lark-cli（出报告，**待办**）| 飞书不反向写 |

---

## 4. 使用场景清单（20 个，状态）

**① 文件与归档**
- S01 项目初始化 + 知识整理（wiki-skill）✏️ 改写待确认：建骨架 + `archive/raw/`→wiki-skill→`archive/wiki/`
- S02 随手文档归档 ✅：散件按「日期_类别_主题_v版本」入 `archive/<类别>/`
- S03 索引/MOC 自动维护 ✂️ 删除（并入 wiki-skill）
- S04 inbox 批量整理 ✅：`inbox/` 预览落位；md 走 wiki-skill，其余走 file-manager

**② 工具能力**
- S05 网页资料抓取转存 ✅：scraper → md → `archive/raw/`
- S06 财报 PDF 抽取 ⬜：markitdown → `archive/raw/`
- S07 A股宏观数据分析 ⬜：analysis
- S08 分析出 HTML 仪表盘 ⏸️ 延迟：frontend(HTML)，涨红跌绿 ¥（列入待办）
- S09 分析出 PPT 汇报 ⏸️ 延迟：frontend(PPT)（列入待办）
- S10 行业动态定时抓取 ⬜：scraper 定时 → `archive/raw/`

**③ 隐私与环境**
- S11 API 密钥安全调用 ✏️：`secrets/`（基建 API）或 `.env`（项目密钥），gitignore
- S12 开发环境一键声明 ⬜：env-manifest
- S13 外发内容脱敏 ⬜：隐私边界扫描

**④ 平台适配器**
- S14 本地 vault → 飞书只读镜像 ⬜：`archive/`(wiki) → 飞书文档只读副本
- ~~S15 报告推送飞书多维表格~~ ❌ **2026-11-04 作废**：RUtable 事实层已废止，元信息改由报告内汇总表 + 脚注承载，不再单独建 bitable。
- S16 Claw 日程入知识库 ⬜：claw-adapter
- S17 wikilink 保真 ✏️ 重指 wiki-skill（raw→wiki 阶段已做）

**⑤ 知识迁移**
- S18 历史调研迁移 ⏸️ 延迟：合并进 wiki-skill（旧笔记丢 `archive/raw/` 跑一次），不单独建引擎
- S19 AI 开发知识沉淀 skill ⬜：踩坑/架构决策 → skill / `memory/*.jsonl`
- S20 本地↔飞书冲突裁决 ⬜：sync 按规则裁决

---

## 5. Research / Frontend 输入-输出契约

### 5.1 Research（独立技能大类，输入多源、必须保留数据源）
| 子类 | 输入 | 处理 | 输出落点 |
|------|------|------|---------|
| 每日资讯 | 新闻/公告流 | 结构化摘要 + 标签 | `output/` → 确认 → `archive/raw/资讯/` |
| 行业调研 | 研报 PDF、网页、行业数据 | 深度分析 + 结论 | `output/` → `archive/raw/行业/` |
| 公司研究 | 财报 PDF、公告、估值数据 | 公司档案 | `archive/raw/公司/` + `archive/wiki/公司/` |
| 热点追踪 | 突发事件/话题 | 时间线 + 多视角观点 | `output/` → `archive/raw/热点/` |
| 个人配置 | 组合前述 | 聚合看板数据 | `output/` → `archive/raw/个人/` |
| 宏观分析 | 宏观数据（GDP/CPI/PPI/PMI/LPR/货币）| 周期阶段 + 趋势判断 | `output/` → `archive/raw/宏观/` |

**数据源存储（核心问题）**
- **非结构化**（文章/PDF/新闻）：markitdown 转 md → 存 `archive/raw/`，**原始件一并保留**；provenance 写 frontmatter。
- **结构化·单次/一次性**：存 `archive/raw/<类别>/<主题>.csv` 或 `.json`（本地副本为 SSOT）。
- **结构化·定时/cron**：存 `archive/raw/<类别>/<主题>.sqlite`（或 `.db`），按时间 append；本地为 SSOT，飞书 bitable 仅视图（待决）。
- **统一 provenance**：每条 research note 带 YAML frontmatter（source / url / fetched_at / type / structure / confidence，详见 `ARCHITECTURE.md` §3 与 `file-manager` 规范）。
- **调研必须保留数据源**：`archive/raw/` 留原始 + `archive/wiki/` 留 `[[引用链接]]` 回指原始。

### 5.2 Front-end（转换层，不生产内容）
| 子类 | 输入 | 处理（skill 转换）| 输出 |
|------|------|------|------|
| HTML 仪表盘 | research 产出 md / 结构化数据 | md→交互 HTML（涨红跌绿 ¥）| `output/html/<主题>_v<n>.html` |
| PPT 汇报 | 同份分析 / 报告 md | md→PPT（模板可换）| `output/pptx/<主题>_v<n>.pptx` |
| 飞书分发 | 上述产出 | **lark-cli** 发飞书 | 飞书文档/多维表格/消息（形式多种，暂缓确认）|

> 前端是「转换层」，只把 `output/` 或 `archive/wiki/` 的内容渲染成 HTML/PPT；分发渠道本轮先不确认。

---

## 6. 待办 Backlog（延迟项）

> 已确认方向、但**暂不实现**的项目，按框架依赖排序。完成后从本表划掉并更新 `CHANGELOG.md`。

### ✅ 已完成（本表归档，详见 CHANGELOG）
- [x] **模型后端选型**（2026-09-19 定）：不配大模型 API，直接用 WorkBuddy / `claude -p` 等 chat 模型调用 skill；密钥仅用于飞书/MCP 等外部服务。
- [x] **file-manager 规范落地**：目录/命名/frontmatter/安全删除（SKILL + USER-GUIDE + references）。
- [x] **vault 忽略配置**：`archive/.obsidianignore` 排除 `*.sqlite/*.db`、临时物与系统文件。
- [x] **secrets / .env 读取接口**：`script/load_secrets.py`（相对定位 workspace 根，不打印值）。
- [x] **`memory/*.jsonl` 格式规范** + 5 条真实经验。
- [x] **wiki-skill 首次跑通（pilot）**：宏观报告 → 8 篇双链笔记 + MOC。
- [x] **研究状态机 = 跨会话记忆**：五段式 + `script/load_context.py`。
- [x] **调研项目层**：`research/<PID>-<slug>/{project,research-state}.yaml` + `_shared/` + `_template/`。
- [x] **两条调研主线 → 5 Track 套件化**（2026-10-30）：`research-assistant`（drill/entry/diagnostic/inductive/scenario + method-*）。
- [x] **分类引擎（手工跑通）**：`config/types.yaml` + `config/tags.yaml` 驱动；暂不自动化（牺牲可控性）。

### 一、框架闭环后才做（高优先级）
- [ ] **S18 migrate-research → 合并进 wiki-skill**（最终不单独建引擎；前置：wiki-skill 自动化完成）
- [ ] **frontend 技能**（HTML 仪表盘 / PPT 汇报 / lark-cli 发飞书）

### 二、需实现的核心组件（中优先级）
- [ ] **效果度量：结论命中率 + 复盘次数**（方案见 §7 + `config/` 阈值）：建 `metrics/`（`pubs.yaml` + `report.md` + `cited_by.json`）+ `script/metrics.py`（默认只读，`--apply` 回写）。claim 新增字段 `created_at` / `last_verified_at` / `recheck_count` / `cited_by` / `outcome`。
- [ ] **数据源层：自动刷新 + 条件查询**（高优先级；先只确认方案）：建 `data/` + `data/catalog.yaml`（字段口径 SSOT）+ `script/query_data.py`（`--list`/`--describe`/`--query`，先读 catalog 再查询）；首个数据源 = 世界银行。
- [ ] **`script/refresh_monitors.py`**：按 monitor 定义自动回填 `last`/`as_of`，触发阈值则在 `queue` 生成待办。
- [ ] **飞书报告浏览统计**（`script/feishu_stats.py`）：`GET /open-apis/drive/v1/files/{file_token}/statistics`；前提：租户开启"文档访问记录功能"（待实测）+ 调用身份有文档管理权限；降级：自建跳转短链计数 / 卡片按钮回调。
- [ ] **P01 · 短名单收敛（Q-P01-01）**：暂缓，先确认整体框架细节。
- [~] **wiki-skill 自动化**：流程已验证但未脚本化（chat 模型 + `script/` 辅助校验双链完整性/孤儿/重名）。
- [~] **research 各子类 skill 模板化**：宏观/行业/公司已建，其余 3 个（每日资讯/热点追踪/个人配置）暂缓，等实际场景跑通再模板化。
- [ ] **P02 · HOOD 现金流口径核实**：暂缓。
- [ ] **env-manifest**：WSL/Hermes/K8s 环境声明 + uv/nvm 版本锁定。

### 三、平台适配器（低优先级，等核心稳定）
- [ ] **obsidian-adapter**（极薄/可省）· **feishu-adapter**（出报告 + 分享）· **claw-adapter**（跨平台日程聚合）· **sync/S20**（本地↔飞书冲突裁决）

### 四、待决策（未定项，阻塞上述部分）
- ~~结构化数据是否上飞书 bitable(RUtable) 查询？~~ ✅ **2026-11-04 已裁决：不上，RUtable 整体废止**。本地 csv/json/sqlite 为 SSOT，飞书仅呈现视图；报告自带汇总表 + 脚注即承载元信息。重启前提见 `ARCHITECTURE.md` §6。
- [ ] 效果度量：prompt/skill 优化的回归集与量化指标如何建（建议：以 `memory/experience.jsonl` 的 `status` + wiki 笔记复用次数作为初代度量）
- [ ] 下载 `TradingAgents` / `sherlock` 两仓库到 `skills/`（阻塞：shell 不可靠 + 沙箱网络受限）

---

## 7. 设计演进史与关键决策

> 早期设计稿（原 `docs/prototype/01–09`）已并入本節；旧文件见 `.workbuddy/_trash/2026-10-30-docs-consolidation/`。本節只沉淀**仍影响现在的关键决策**，不重复细节。

### 7.1 当年待定项 → 最终落地形态
| 当年待定项 | 最终落地形态（当前真相在哪）|
|---|---|
| 系统形态 | WorkBuddy 项目级 Skill + 多智能体配置（非独立 CLI / Web 应用）|
| 模型后端 | 直接调用方 chat 模型，**不配置大模型 API** |
| 提示词是核心资产 | 落地为 `.workbuddy/skills/`：`research-kit`（调研套件）/ `wiki-skill` / `file-manager` / `hotspot-tracking` |
| 文件系统即数据库 | `archive/`(SSOT vault) + `config/`(受控词表) + `research/`(项目状态机) + `data/`(数据源) + `metrics/`(度量) |
| 调研主线 | **5 Track 体系**（drill/entry/diagnostic/inductive/scenario + method-*），取代原 Track A/B（2026-10-30）|

### 7.2 分类与标签（原 `06`，现行依据：`config/types.yaml` + `config/tags.yaml`）
- **四维字段模型**：`type`(受控 6 类，永不自动新建) / `tags`(半开放，别名归一) / `keywords`(抽取) / `reason`(理由)。
- **MVP 流程（A 骨架 + B 规则前置 + C 不自动建类）**：① 规则先匹配 config → ② 漏网者模型打标（多标签+conf）→ ③ conf≥阈值且命中已有类 → 自动写 frontmatter 并移入 `archive/raw/<类>/` → ④ 未命中/低 conf → 进 `config/tags.proposed.yaml` + 留 `inbox/` 待人工批准 → ⑤ 批准后合入 `config/tags.yaml`。
- **护栏**：不自动建类、多标签、别名归一、幂等、proposed 带来源可审计。
- 阈值：`auto_apply: 0.85` / `suggest: 0.60`（低 conf 在 `reason` 写 `conf=0.xx` 留痕）。

### 7.3 框架细节拍板（原 `08` 拍板记录，2026-09-20；S1 于 2026-10-30 作废）
| ID | 结论 | 影响 |
|---|---|---|
| D1 | git 纳入 `script/ config/ .workbuddy/skills/ docs/ research/*.yaml`（archive/memory/secrets 仍排除）| `.gitignore` |
| D2 | 可选字段白名单 + 未知字段告警 + `project` 准必填 | `validate_frontmatter.py` |
| D3 | 单 `url` 保留主源，多来源用可选 `sources:` 列表（含 tier）| frontmatter 规范 |
| D4 | 文件名日期恒为抓取日 + 可选 `as_of` 记数据窗口 | 命名规范 |
| D5 | 数据/结论变 → `v+1`；错字格式 → 原地改 | 版本规则 |
| D6 | `load_context.py --lint` 只读校验状态机 | `script/load_context.py` |
| D7 | `_shared` 提升门槛：≥2 项目适用 或 曾推翻结论 | `research/README.md` |
| D8 | `done` 项目移 `_archive/`；`--list` 默认隐藏 | `load_context.py` |
| D9 | 建 `config/wiki-categories.yaml`（wiki 独立受控词表）| wiki-skill |
| D10 | 空类型目录用到再建 | — |
| D11 | 笔记移动进 vault；HTML/PPT 留 `output/<类型>/` | file-manager |
| D12 | 低 conf 在 `reason` 写 `conf=0.xx` | `config/tags.yaml` |
| **E1** | 资讯日频**不进 wiki、不做双链**（只 frontmatter + 日汇总）| wiki-skill |
| **E2** | 新增顶层 `metrics/` 与 `data/`，均不进 vault | `AGENTS.md`、`.obsidianignore` |
| **E3** | 命中率成熟期默认 **90 天**（行业/公司可降 60）| `script/metrics.py` |
| **E4** | 飞书"文档访问记录功能"是否具备 —— 待实测 | `script/feishu_stats.py` |
| **E5** | 首个接入数据源 = **世界银行** | `data/catalog.yaml` |
| ~~S1~~ | **2026-10-30 作废**：A/B 升级为 5 Track 且不可混跑 | `research/_template/project.yaml`、套件 `ROUTING.md` |

### 7.4 频率分层与度量（原 `09`，M3 现行方案）
- **频率分层（硬结论：日频×全手工=必然崩）**：

| type | 频率 | 处理深度 | 进 wiki？ |
|---|---|---|---|
| 资讯 | 日频 | frontmatter + 一句话摘要 + 当日汇总（不抽取/不双链）| **否** |
| 行业 | 月频 | 完整六段式 + 三维打分 | 是 |
| 公司 | 随行业（月频）| 五段式 + 分子/分母三分法 | 是 |
| 宏观 | 季频 | 四路资金交叉验证 | 是 |
| 热点 | 不定期 | 新建项目目录 | 是 |

- **度量双轨**：A. 内在价值（主）= 结论被后续独立调研引用（命中率）；B. 外在触达（辅）= 飞书 uv/pv（仅分享出去的报告记）。
- **命中判定**：`cited_by` 含**非自身 evidence** 的笔记 = hit；存活 ≥90 天且 `cited_by` 空 = miss；`falsified` 单列。命中率 = hit/(hit+miss)。
- **证据可信度 Tier1-3**（评价报告质量，与"数据管线"是两件事）：Tier1 一手官方 / Tier2 二手机构 / Tier3 转述社媒；关键结论至少 1 个 Tier1 或 2 个独立 Tier2 交叉验证；反方也标 Tier。验收 = 报告质量而非数据源等级。
- **数据源**：`data/catalog.yaml` 是字段口径 SSOT（CATL 成本口径冲突的根因就是口径没写死）；查询顺序"先读 catalog，再查询"。
