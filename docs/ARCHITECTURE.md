# ARCHITECTURE.md — 系统架构与数据流

> 给 AI 与人类的架构总览：这套本地知识基础设施由什么组成、数据怎么流动。
> 先读 `AGENTS.md` 拿铁律；设计演进与关键决策见 `ROADMAP.md` §设计演进史。

---

## 1. 设计核心

不造新框架。把**可移植的操作指令（skill + 优化提示词）**当作核心资产，叠加：

1. **单一可信源（SSOT）** —— 知识只存一份（`archive/`，即 Obsidian vault），多平台只是视图/镜像，不分裂。
2. **闭环知识回路** —— 捕获 → 整理 → 生成 → 确认 → 归档 → 检索复用，每步都有"人读 + 机读"产出。
3. **配置即规范** —— 分类体系、标签、阈值写成 yaml，改配置即改行为，不碰代码。

目标：让智力资产**可沉淀、可复用、可迁移、可审计**。

---

## 2. 组件地图

```
<workspace>/
├── AGENTS.md                 # AI 接入先读（铁律 + 目录地图）
├── docs/                     # 设计文档（README / ARCHITECTURE / CHANGELOG / ROADMAP）
│   └── ARCHITECTURE.md       # 本文件：架构与数据流
├── archive/                  # ★ SSOT = Obsidian vault
│   ├── raw/<子类>/           #   已分类原始笔记 / 附件 / 数据源
│   ├── wiki/<主题>/          #   整理后知识库（双链 + MOC，Obsidian 兼容）
│   └── inbox/                #   待分类暂存
├── output/<类型>/            # 产出确认前暂存（HTML / PPT / 报告草稿）
├── research/<PID>-<slug>/     # ★ 调研项目层：每业务一份状态机（project.yaml + research-state.yaml）；_shared/ 跨项目方法论
├── data/                     # 结构化数据源（sqlite/csv）+ catalog.yaml 数据字典（字段口径 SSOT）；不进 vault
├── metrics/                  # ⏳ 效果度量（规划中，未建）：pubs.yaml + report.md + cited_by.json
├── config/                   # 分类体系（受控词表）
│   ├── types.yaml            #   受控 6 类（type），模型不自动新建
│   └── tags.yaml             #   半开放标签库 + 别名归一 + 阈值
├── memory/                   # 顶层经验
│   ├── MEMORY.md             #   精华经验（更新记 CHANGELOG）
│   └── *.jsonl               #   模型跑通 / 碰壁经验
├── secrets/<服务>.env        # ⏳ 开发用 API（飞书 / MCP 等），按需创建，不入库
├── .env                      # 项目运行密钥（与 secrets/ 不冲突），不入库
├── script/                   # 脚本（git 跟踪，一律 python -m script.<module> 调用）
│   ├── load_context.py       #   加载项目状态 + 父子 rollup（--list/--project/--lint/--json）
│   ├── new_project.py        #   新建调研项目（--parent 建子 task）
│   ├── snapshot_url.py       #   网页可检索文本快照（不存截图）
│   ├── validate_frontmatter.py
│   └── gen_ecommerce_data.py / analyze_ecommerce.py   # P05 数据生成与 SQL 分析
└── .workbuddy/
    ├── skills/               # 项目级 skill（file-manager / hotspot-tracking / research-kit / wiki-skill）
    └── memory/YYYY-MM-DD.md  # 按日工作日志（WorkBuddy 原生）
```

---

## 3. 分层

| 层 | 组件 | 职责 |
|----|------|------|
| 配置层 | `config/types.yaml` `config/tags.yaml` | 受控词表 + 别名 + 阈值，定义"怎么分类"（跨项目共用） |
| **项目层** | `research/<PID>-<slug>/{project,research-state}.yaml` | **一个业务调研一份状态机**：目标/边界 + 结论/监控/待办/数据集；`_shared/` 存跨项目方法论 |
| 存储层 | `archive/`(vault) · `output/` · `memory/` | 知识的落盘与版本（笔记按 type 分目录，用 frontmatter `project` 标记归属） |
| 能力层 | `.workbuddy/skills/`：research-kit（含 research-html / research-ppt 渲染子技能）/ wiki-skill / file-manager / hotspot-tracking | 具体能力（调研 / 整理 / 规范 / 生成）|
| 工具层 | `script/` | 校验等原子脚本（git 跟踪）|
| 接入层 | `AGENTS.md` · `secrets/` · `.env` | AI 入口、密钥注入 |

---

## 4. 主数据流（知识回路）

```
  抓取 / 产出 / 外部知识
        │
        ▼
  archive/inbox/  ──────────────┐
        │                        │
        │   ① 规则先匹配 config   │  config/types.yaml ──┐
        │────────────────────────┘  config/tags.yaml ───┤ 受控词表 + 别名 + 阈值
        │   ② 漏网者：模型打标      │                      │
        ▼       （多标签 + conf）   │                      │
   分类引擎 ── conf≥阈值 且 命中已有类 ──► ③ 写 frontmatter
        │                                      + 移入 archive/raw/<type>/
        │                                                      │
        └── 未命中 / 低 conf ──► config/tags.proposed.yaml      │
                                  + 留 inbox 待人工批准         │
                                                                ▼
                                          ④ wiki-skill：raw → wiki（双链 + MOC）
                                                                │
                                          ⑤ 检索复用 / output 生成 / 飞书视图
```

要点：
- **落点双写**：分类既写 frontmatter，也移动文件到 `archive/raw/<type>/`，避免"元数据说 A、文件夹说 B"。
- **不自动建类**：`type` 严格受控（6 类）；`tags` 允许 AI 新增，但经别名归一后写入 `config/tags.yaml` 并留痕。
- **可审计**：proposed 标签带来源与日期；frontmatter 的 `reason` 记录分类理由。

---

## 5. 各能力的数据流

- **research-kit（调研主入口）**：抓取/分析 → 产出先落 `output/` → 确认后移 `archive/raw/<子类>/` → 走 wiki-skill。
- **交付渲染**：`research-html`（自包含单页 HTML）/ `research-ppt`（PPTX，含母版风格锁 `extract_master_style.py`），按 `delivery-standard.md` 的 `output_target` 切换；lark 为默认主交付。
- **wiki-skill**：`archive/raw/` → 抽实体、建 `[[双链]]`、组织 `archive/wiki/`、生成 MOC。Obsidian 兼容。
- **file-manager**：纯规范（目录/命名/frontmatter/安全删除），被所有落盘动作遵守；使用者手册见其 `USER-GUIDE.md`。

---

## 6. SSOT 与多平台

- **本地 `archive/` 是权威**。飞书/lark 只出报告、分享，不反向编辑（防漂移）。
- 结构化数据源：单次 → csv/json，cron → sqlite，本地为 SSOT；`data/catalog.yaml` 登记字段口径。
- **RUtable（飞书多维表格事实层）已废止**（2026-11-04 裁决）。原设想的「unit 文件 / 指标表 / 段落引用注释」体系经 A/B 实测被否：报告手写、unit 另存一份，二者必然不一致，而脚本查不出数值差异。**数据的唯一归属地是报告本身**（汇总表 + 脚注），由 `.workbuddy/skills/research-kit/references/data-integrity.md` 的取数纪律保障准确性。仅当「跨产物复用 + 追责追溯 + 单份报告装不下」三条同时成立才重启，且必须先证明报告确实承载不了。

---

## 6.1 调研项目层（为什么要有 `research/`）

一次只跑一个调研时，单文件 `config/research-state.yaml` 够用；**同时跑两个业务**就出问题：
焦点是谁的、监控指标属于哪条线、待办优先级跨线混排——上下文互相串味。

拆法（详见 `research/README.md`）：

| 层 | 位置 | 存什么 |
|----|------|--------|
| 全局受控词表 | `config/types.yaml` `config/tags.yaml` | 分类与标签（跨项目共用，不随项目走） |
| **项目状态机** | `research/<PID>-<slug>/research-state.yaml` | 该项目的 focus / claims / monitors / queue / datasets |
| 项目元信息 | `research/<PID>-<slug>/project.yaml` | 驱动问题 / scope_in / scope_out / 交付物 |
| **跨项目方法论** | `research/_shared/research-state.yaml` | 换个项目还能用的判别规则（带 `derived_from` 溯源） |

- **项目发现靠扫描** `research/*/project.yaml`，不维护 index 注册表（避免两处漂移）。
- 笔记仍在 `archive/raw/<子类>/` 按 type 存（SSOT 不按项目切分），靠 frontmatter `project` 与路径互指。
- 当前项目：`P01`（行业热点观察 · 半导体/AI算力链，drill）· `P02`（美国加密市场进入，entry）· `P03`/`P04`（国产芯片，drill/entry）· `P05`（电商经营诊断，diagnostic）· `P06`（A股行业景气横截面，drill）。P06 之下派生三级银行链：`T1`（银行行业深度）→ `T1.1`（杭州银行个股）/ `T1.2`（银行行业框架）。

### 6.2 `data/` vs `artifacts/` vs `archive/` —— 三处放数据的边界

最容易混淆的**不是路径，是职责**。用**三问判定**：

| 问一句 | 命中 → 放这 | 特征 |
|--------|------------|------|
| 换个调研项目还能用吗？ | **`data/`** | 跨项目复用的数据源（sqlite/csv）+ `data/catalog.yaml` 口径字典；**必须登记 catalog**（否则同类口径事故重演） |
| 是**这次**调研的过程痕迹吗？ | **`research/<PID>/artifacts/`** | 随项目走，整个目录搬 migrating 即迁移；脚本可重生成 |
| 是已经变成结论的知识吗？ | **`archive/raw/`** | vault SSOT，带 frontmatter + 双链 + type 受控 6 类 |

**⚠️ 同名陷阱**：`artifacts/raw/` 的 raw = **未加工的数据**；`archive/raw/` 的 raw = **未经 wiki 整理的原始笔记**。两个「raw」同音不同义，因此 artifacts 内**禁用 `raw/` 这个名字**。

**artifacts 内部按「处理阶段」分级**（不是按知识主题）：

```
research/<PID>/artifacts/
├── 00_input/      外部取回、未加工（API payload / 网页快照）   ← 不用 raw/，避与 archive/raw 撞名
├── 10_work/       脚本与中间结果（可重生成），脚本放 10_work/script/
└── 90_output/     交付物（报告 HTML / 待推送 CSV）
```

数字前缀表达流水线顺序；`gen_manifest.py` 靠父目录名自动判 stage。

**为什么不借用 `archive/` 的 type 分类（资讯/行业/公司/热点/宏观/个人配置）**：那是**知识主题轴**，服务于检索与双链；artifacts 需要的是**处理阶段轴**，服务于溯源与重算。
**借鉴的是命名而非分类**：文件名沿用 `<日期>_<类别>_<主题>_v<版本>.<ext>`（见 file-manager）；而任何从 artifacts **提升**成 `data/` 的东西，按 `data/catalog.yaml` 的字段登记（grain / generated_by / reproducible / coverage / caveats）—— 这才是真正该借的标准。

> P06 为 2026-10-30 之前创建，**保持平铺不改**：当时 6 个脚本依赖同目录相对路径（如 `open("analysis_v2.json")`），改目录会打断可复算；stage 改由文件内容判别（`apiData`/`docData` → raw），已足够准确。新项目一律用上面的三层结构。

---

## 7. 待决 → 已决（设计已收口，进入实现）

| 议题 | 结论 |
|------|------|
| **模型调用方式** | **不配大模型 API、不选型模型后端**。直接用 WorkBuddy / `claude -p` 等 chat 模型调用本系统 skill（research-kit / wiki-skill / 分类引擎）；抽取、打标、分析由当前会话的 chat 模型执行。密钥只用于飞书/MCP 等外部服务（见 `secrets/`）。 |
| **首个端到端 pilot** | 已启动：宏观分析（热钱行业流动）→ frontmatter 校验 → 入 `archive/raw/宏观/` → wiki-skill 整理。见 `archive/raw/宏观/20260919_宏观_热钱流动行业分析_v1.md`。 |
| 分类引擎 | config 受控词表 + 模型打标 + proposed 流程（见 `config/types.yaml` + `config/tags.yaml`，演化史见 `ROADMAP.md` §设计演进史）。 |
| 飞书适配器 / Claw 适配器 | 下游，库里有内容再接（列入 `ROADMAP.md` §待办）。HTML / PPT 渲染侧已实现（`research-html` / `research-ppt`）。 |

详见 `AGENTS.md`（铁律与目录地图）+ `ROADMAP.md`（里程碑 / 进度 / 场景 / 待办 / 设计演进史）。
