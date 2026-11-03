# CHANGELOG.md — 变更与决策日志

> 记录设计决策与重大变更，按时间倒序。每次架构/组件决策在此留痕。
>
> **2026-10-30 注**：`docs/` 已收敛为 **README / ARCHITECTURE / CHANGELOG / ROADMAP** 四个文件。原 `prototype/` 设计稿（01–09 + README）并入 `ROADMAP.md` §设计演进史；旧文件（含 MILESTONE / PROGRESS / SCENARIO / TODO / DESIGN）移至 `.workbuddy/_trash/2026-10-30-docs-consolidation/`，**可逆恢复**。历史条目中对旧路径的引用保留原文不改写，以免损伤变更记录本身。

## 2026-11-01 · 证据链呈现层（artifacts / manifests 收口 · P06 试点）

**背景裁决（用户拍板，改变了原设计方向）**
1. 网页/资讯类数据源 **必须存快照** —— 但存的是**去标签正文 + 元信息**，不是截图（截图不可检索、体积大、无法校验）。
2. manifest **粒度定为「文件级」**，拒绝观测级/字段级 DAG（过度设计）。粒度不足时用**切分文件**解决，而不是把台账做细。
3. 证据链最终落在 **lark sheet（多 tab：口径/数据源/计算方式/分析）** —— 但按铁律 #2，lark 只是**呈现视图**，本地 yaml/json 是 SSOT，**单向同步、禁止反向写**。
4. **目标不是硬机器追溯，而是「准确呈现发现与结论 + 增强可读性」** —— 正确性由「呈现层脚本生成而非手写」顺带获得，不再单独上阻塞式门禁。

**新增脚本（`script/`，git 跟踪）**
- `script/snapshot_url.py` —— 网页快照抓取器。存 ①去标签正文 .txt（含 URL/fetched_at/meta 发布时间/sha256 抬头）②可选原始 .html ③`_index.json` 登记表（append + 按 sha256 去重）。回答"网页会改会 404"的存证问题。
- `script/gen_manifest.py` —— **文件级**产物台账生成器。输出 `research/<PID>/manifests/artifacts.yaml`（path/bytes/sha256/mtime/stage）；`--check` 做漂移检测（修改/新增/丢失，有变更退出码 1）。**stage 靠文件内容判别而非文件名**：含 `apiData`/`docData` 的 json = 接口原文 → raw，避免把 13 个原始返回误判成 derived。
- `script/gen_evidence_sheet.py` —— 证据链工作表生成器，**7 个 tab**：`00_概览`/`01_口径`/`02_数据源`/`03_计算方式`/`04_结论与证据`/`05_监控与失效`/`06_待办与缺口`。支持 `--csv-dir`（UTF-8 BOM，可直接拖入 lark sheet）/ `--md` 预览 / `--seed-caliber`。
  - `03_计算方式` 的「输入 → 脚本 → 输出」靠**源码同一行是否出现写入动作**（`"w"`/`write_text`/`dump(`）自动推导，**不维护手工映射表**；推导不出时显式标 ⚠ 而非静默留空。
  - `04_结论与证据` 新增 **「结论自检」列**：自指检查（是否只指向自生成报告）+ **反方 ≥5 门禁** + status 缺失检查。

**P06 试点产出**
- 新建 `research/P06-sector-momentum-20261030/caliber.yaml` —— 9 条指标口径字典，含 **`kind: measured | judgment` 二分**（判定类显式标注不可完全复算）；四象限归类与 α 判定均标 judgment 并记录"换阈值即换结论"。
- 生成 `manifests/artifacts.yaml`（24 文件 · 467KB · raw=13/derived=2/report=3/script=6）、`manifests/evidence_sheet.json`、`manifests/evidence_csv/` × 7 CSV。
- **⚠️ 台账当场揪出违规**：P06 的 6 条 claim 中 **5 条不满足「反方 ≥5」硬规矩**（C-P06-04 同涨同跌、C-P06-06 K型分化 **0 条反方**），仅 C-P06-01 通过。待补。

**lark 呈现层上线**（首个刊 publishing 视图）
- 新建飞书电子表格《P06 A股行业景气度 · 证据链 2026-10-30》，**7 个 tab 全部位写入 + 样式 + 条件格式**已落：
  <https://gcnyro8kdjoa.feishu.cn/sheets/PP4asTZZThkKUXtURutcahCYnNf>
  - token `PP4asTZZThkKUXtURutcahCYnNf`；表头冻结首行首列、按 tab 定制列宽、长文本换行、浅灰边框。
  - **条件格式**（这是"呈现层"真正的价值）：`04_结论与证据` 按「结论自检」列自动着色 —— 含 ⚠ 整行浅黄、含 ✓ 整行浅绿。哨兵已验：H2（C-P06-01 通过）绿、H5（C-P06-04 反方 0 条）黄。
  - 重新同步链：`research-state.yaml`/`caliber.yaml` → `gen_manifest` → `gen_evidence_sheet --csv-dir` → 拖入 lark。**单向，禁止反向写**。
- `research-state.yaml` 新增 **`views:` 段**：登记呈现层视图的 URL/token/tabs/单向同步方向，把"lark 不是 SSOT"这条约束写进状态机本身。

**`data/` vs `artifacts/` vs `archive/` 边界判定（写入 ARCHITECTURE.md §6.2）**
- **三问判定**：换个项目还能用→`data/`（须登记 `catalog.yaml`）；是这次调研的过程痕迹→`artifacts/`；已成结论的知识→`archive/raw/`。
- **⚠️ 同名陷阱**：两个「raw」不同义（未加工数据 vs 未整理笔记）→ artifacts 内**禁用 `raw/` 目录名**，改用 `00_input/ 10_work/ 90_output/` 三层（数字前缀表达流水线顺序，gen_manifest 靠父目录名自动判 stage）。
- **借鉴的是命名不是分类**：archive 的 `type`（资讯/行业/公司/热点/宏观/个人配置）是**知识主题轴**，artifacts 需要的是**处理阶段轴**，不可混用。文件名沿用 file-manager 的 `<日期>_<类别>_<主题>_v<版本>.<ext>`。
- **P06 不 reorganize**（撤回上次建议）：上次理由是"stage 会被误判"，但已改用内容判别（`apiData`/`docData`）解决；而改目录会打断 6 个脚本的同目录相对路径依赖、牺牲可复算 —— 为纯美观不划算。新标准只对**新项目**生效。

## 2026-10-30
- **`method-ecommerce-ops` 首个端到端案例落地（P05 · diagnostic）+ 补齐数据层 Baseline**：把电商经营分析从「只有方法文档」变成「有数据、有 SQL、有结论」的可复现链路。① **新建 `data/catalog.yaml`**（此前长期空缺的口径字典：登记 8 个派生指标的定义/单位/caveats + 7 张表的粒度与不变式 + 5 条数据源局限），`query_data.py` 的登记层从此有据可依。② **新建 `script/gen_ecommerce_data.py`**：合成 2025-01-01~2026-10-30 共 668 天 × 4 渠道的账户级漏斗明细 **3,518,088 行**（22 秒、seed 固定可复现），核心设计是 **step_* 严格嵌套单调蕴含**（生成后用 SQL 校验违规行必须为 0）——这是「账户口径 cohort-locked」能免 JOIN 成立的前提；`acq_source`(自然/付费) 与 `fact_ad_daily.spend` 同源推导，使 ROI 与漏斗可自洽互算。③ **新建 `script/analyze_ecommerce.py`**：16 个 SQL 查询覆盖 M1–M5 / R1–R2，支持 `--channel` / `--start,--end` / `--baseline,--current` / `--only`，输出 CSV + 汇总 md + SQL 全集。④ **归因核心 = GMV 四因素分解**（规模/结构/效率/客单，残差 0 闭合），结构效应解析为 `曝光量 × Δ自然占比 × (自然每曝光支付率 − 付费每曝光支付率) × 基线客单价`，直接回答「把曝光从自然搬向付费到底亏多少」。⑤ 新项目 **`research/P05-ecommerce-ops-20261030`**（7 条 claim × 各 ≥5 条反方含时间维度、7 个带阈值 monitor、6 项 P0–P2 队列），正文 `archive/raw/公司/20261030_公司_电商直播经营漏斗诊断_v1.md` + 18 个证据 CSV（含专项 `Q08-2026Q3-funnel`）。
  - **主结论**：自然占比下滑的性质是「**付费稀释**」而非「自然萎缩」——抖音自然曝光 21 个月仅 0.98x（零增长）、付费 1.77x；抖音 GMV +¥71,777 全靠规模效应 +¥134,160，被结构迁移 −¥43,118 与客单下滑 −¥23,118 吃掉 49.4%；四渠道付费每曝光支付率均低于自然（1.33~1.64 倍）且单位成本 21 个月涨 8.3%~27.5%，形成「低效资产 + 涨价 + 加仓」三重挤压；可修复空间上限 ¥46,415/季度（抖音占 76.3%）。
  - **口径层面的硬发现（两条，已写进 catalog caveats）**：ⓐ **账户口径在长窗口会失真**——跑满 668 天时「至少进入过一次」的比例虚高到 62.31%，故头版漏斗必须跑有界窗口（取 2026Q3）；ⓑ **曝光口径 vs 账户口径差最多 25.6pp**（抖音进入率 11.23% vs 36.84%，每账户平均被曝光 4.13 次），两口径不可混用，且四因素分解必须用曝光口径（行级才可加）。
  - **过程中返工两次**：ⓐ 首版 ROI 算出 **105 倍**（投放成本给得太低）→ 按目标 ROI 反推重标定 oCPM 等效成本，ROI 落到 3.1~6.0；ⓑ 曝光→进入率 22~34% 远高于直播行业真实水平（8~14%）→ 下调并同步把曝光量 ×2 以补统计质量。**绝对转化率仍偏行业上沿**，故报告明示「结论依赖相对结构与归因分解，不依赖绝对基准值」。
- **修复两个生成器隐蔽 bug**：ⓐ 主播每天固定取前 3 名（`HOST_WEIGHTS[:n]`），另 2 名从未出场 → 集中度分析失真，改为**按权重无放回抽签**；ⓑ `dim_account.first_seen` 全部落在分析窗口内，导致「新增 vs 存量」对照永远只有一类 → 账户池加入 45% 的**窗口前老客**（负偏移），`available[]` 改用 `bisect` 计算。修复后 Q12 显示 5 名主播 Top1 占 GMV 53.7~57.4%，Q15 显示存量支付转化 7.75% vs 新增 5.11%。
- **git 化 skills/commands 打通 worktree（含修两个隐藏 bug）**：此前 `.gitignore` 的 `/*` 让 `.workbuddy` 零跟踪，`git worktree` 只能 checkout 已跟踪文件 → 等于不可用。精细放行 `.workbuddy/skills/` 与 `.workbuddy/commands/`（`memory/` 仍不入库，守 09-19 策略），建分支 `infra/track-workbuddy-skills` → ff-merge 回 master，worktree `F:/workspace-ecommerce-test` @ `verify/ecommerce-diagnostic`。期间挖出两个真 bug：① **`.gitignore:18` 的 `skills/` 匹配任意层级同名目录**，把 `research-assistant/skills/` 整套子技能吞掉（第一次提交的 34 个文件里实际一个子技能都没入库）→ 加 `!.workbuddy/**/skills/` 修正，**同时更正先前「Grep 在 .workbuddy 下不下钻是环境特性」的错误结论——真正原因是 ripgrep 尊重 gitignore**；② `script/` 三个脚本（`load_context.py` / `load_secrets.py` / `new_project.py`）从未入库。
- **`docs/` 文档收敛为 4 文件 + 全仓引用同步**（用户 2026-10-30 定：控制在 3~5 个、重新分工）：原 20 个文件（9 顶层 + 11 prototype 设计稿）按职责重划 —— `README.md`（导航 + 新手上手，合并原 README + DESIGN）、`ARCHITECTURE.md`（架构与数据流，保留）、`CHANGELOG.md`（变更总账，追加式不改写历史）、`ROADMAP.md`（里程碑 M1/M2/M3 + 进度 + 20 场景 + 待办 Backlog + **设计演进史**）。原 prototype/06–09 的现行依据（分类四维字段 + 阈值 0.85/0.60、D1–D12 与 E1–E5 拍板记录、S1 作废、频率分层与度量双轨、数据源 catalog 口径 SSOT）全部沉淀进 `ROADMAP.md` §7。同步修正 4 处活跃引用：`.workbuddy/skills/file-manager/SKILL.md`（docs 目录树改述新 4 文件）、`AGENTS.md`（目录地图 + 分类指向 + 设计演进路径）、`docs/ARCHITECTURE.md`（4 处内部指向改指 ROADMAP/config）、`script/validate_frontmatter.py`（规则注释改指 `ARCHITECTURE.md` §3 + file-manager 命名细则）。
- **5 Track 迁移收尾（旧 `track: A/B` 全面退场）**：P01/P03→`drill`、P02/P04→`entry`（P06 本就是 drill），四个项目 `project.yaml` 的 `skills:` 字段同步从**已归档的旧技能名**（research-macro / research-industry / research-company / research-market）改为新名 `[research-core, research-track-<track>, method-<x>]`；`_shared` 的「不属于 A/B 任一主线」注释改写。`load_context --list` 复验 5 项目 track 正常。顺带清掉全仓活文档断链：`research-track-entry` description 里写错的 `track-market-entry`→`method-market-entry`（并删已取消的 domain 层表述）、`prompts/PEST行业宏观环境分析_v1.md` 的 `related_skills`、`docs/MILESTONE.md` M2 行（引用已归档 skill + 状态"行业样例待跑"已过时→"待终核"）、`research/P04` 的 queue 条目、`docs/prototype/08` 拍板表 **S1（允许 A/B/A+B）作废**（与铁律 #3 冲突）。**`docs/README.md` 是错位文件**（内容实为 prototype 归档说明）→ 移入 `docs/prototype/README.md` 并更新过时行，docs 根重建真正的导航 README。`docs/prototype/07`（两条主线）加 deprecated 头指向 `references/ROUTING.md`。历史日志（CHANGELOG/TODO）与 `archive/raw/` 归档笔记**保留旧叫法不改**。
- **`load_context` 补齐两个已拍板未实现的部件（D6 / D8）**：① **`--lint` 状态机只读自检**——校验受控词表（track 5 种 / claim status 三值 / 项目 ID 唯一）、门禁必填（claim 的 confidence+status、monitor 的 threshold+as_of、updated_at）、悬空引用（`node.parent` / claim 的 evidence·data 路径 / queue 的 depends_on / dataset 路径）、状态机六段齐备、父已 done 但子仍有 open 结论；三级输出 严重 > 警告 > 提示，**有严重项退出码 1**，支持 `--json`（schema `research-lint/v1`），`research/_archive/` 下归档项目一并纳入。② **`--all` 归档显示开关**——`archived` 项目默认在清单中隐藏并提示条数，`--all` 才列出；**显式 `--project <ID>` 指定的 archived 项目仍可加载**（显式优先）。实测：现有 6 项目自检 0 问题；负向测试（故意造坏项目）如期捕获 4 严重 + 6 警告并退出 1，测试项目已入 `.workbuddy/_trash/`。同步 `docs/DESIGN.md` 命令表、套件 `references/AGENTS.md`、`/research-load` 命令；`docs/prototype/08` 拍板表 D6/D8 标注已实现。
- **`method-sector-momentum` 启用 + 回跑 v2（补齐 v1 缺失分析）**：`enabled` 置 `true`（用户显式开启），version 1.0→1.1，同步 4 处文档表述（主 SKILL 启用方式 / `references/AGENTS.md` 路由表 / `research-core` 引用行 / 顶层 SKILL 构成表）。按「模板回跑」约定回跑上次交付：**数据窗口不变**（月度序列复用 `series.json`；资金流重拉同一交易日 2026-10-29 以补登结构化字段）。补齐三项 v1 缺失：① **M1 流出侧对照表**（电子 -253 亿、通信 -89 亿、计算机/有色 -10 亿，并标 `lower_bound`）② **M4 双维交叉四象限**（v1 只给两张并列图、未交叉 = 未产出结论）③ **M5 同涨同跌量化**（月度环比相关矩阵 + 独立性排名）。产出 `output/sector_monthly/industry_sentiment_2026_v2.html`（含四象限散点、12×12 相关矩阵热力图、口径登记表）。**回跑结论**：双高主推 3 个（银行 / 煤炭 / 石油石化，其中银行是唯一真 α——双高中最独立、振幅最低 17）；脉冲 5 个；双低 4 个。**最重要发现**：2026-10-29 全市场超 4700 只个股下跌，当日资金流被**避险属性**主导，导致"脉冲"象限系统性虚高（国防军工资金第 1 但近 3 月 -4.8%）→ 已固化为 SKILL.md 的「M4 大跌日修正」硬规矩 + 反方 #2 加强。另回灌：象限划分规则（资金用方向、景气用近 3 月动量而非 YTD、散点用符号平方根压缩）、`lower_bound` 处理、按行业名定向匹配正则、行业资金流应取 `docList` 正文而非 `apiRecall`（后者返回单指数且值全 0）。
- **新增 research-assistant 套件 method 技能 `method-sector-momentum`（行业景气度横截面跟踪，→ drill）**：把「近一周行业资金净流入 Top10 + 近一年月度景气度热力图」这一实测跑通的框架沉淀为可复用方法。归属判定套 `ROUTING.md` 决策树：非 diagnostic / 非 inductive / 非 scenario → 「从申万 31 个行业全集选最优子集」= **drill**。**新建而非并入 `method-topdown`**：后者是纵深链 A1→A2→A3、交付「标的短名单」，本方法停在行业层横截面、交付「景气图谱 + 四象限 + 行业短名单」，二者父子非包含（衔接：本方法出行业短名单 → 交 topdown A3 下钻）。任务清单拆为 M0 定全集与口径基线 / M1 资金面横截面 / M2 时序景气采集 / M3 景气矩阵与路径 / **M4 双维交叉四象限** / M5 归因标注与 β-α 剥离 / R1 反方与失效检验，映射骨架 D1–D3；配套 `data-recipes.md` 收录取数配方与实测坑。`enabled: false`（具体分析默认不启用）。同步套件根 `SKILL.md` 构成表（version 1.4→1.5）+ `AGENTS.md` 技能路由表。实测回灌要点：① M4 交叉是决策增值点，只出图不交叉视为未产出结论；② 叙述结论必须脚本生成（曾手写"红利正收益"与计算值 -10.7% 矛盾）；③ 板块资金主力统计无周度聚合，"近一周"须明示为最新交易日快照；④ 板块名查询措辞需 fallback；⑤ 接口缺月会造成跨月累计被误读为单月。
- **新增 research-assistant 套件 method 技能 `method-ecommerce-ops`（电商经营诊断）**：将以「多平台直播电商」为案例的经营分析框架沉淀为可复用方法域。核对时发现套件已升级（version 1.2 → 1.3）：原 Track A/B + domain 结构已换为 **5 种方法级 Track（drill/entry/diagnostic/inductive/scenario）+ method 技能** 体系，并新增 `ROUTING.md`（G2 选线权威，含决策树，diagnostic 优先级最高）。据此**修正先前偏保守的落点判断**：该框架不走 `research-module`，而应建成 `belongs_to_track: diagnostic` 的 method 技能（仿 `method-topdown`）——因 `research-track-diagnostic` 原文即列明其适用为「经营健康度诊断、漏斗转化诊断、渠道归因」。`enabled: false` 默认不启用（diagnostic 亦用于 SaaS/门店等非电商场景，避免抢路由），显式启用才参与 research-core 路由。分析任务清单拆为七段 M1–M5 + R1–R2，映射到骨架 DG1–DG4，含 G4 强制反方 ≥5 条与关键口径登记。同步更新套件 `SKILL.md` 构成表 + version→1.3、`research-track-diagnostic` 接入章节互链（双向可发现）。

## 2026-10-10
- **A股热点周报推送飞书文档（原任务②落地）**：westock 拉取最新一周数据 → 生成 `output/weekly_report_20261010.html` → 走 lark-doc 从零创作工作流（data-report genre）落为飞书云文档。文档 URL https://my.feishu.cn/docx/G0YQd4HBQodsOqxxRKCcBRlInwf，本地 SSOT 落档 `archive/raw/热点/20261010_热点_A股近一周热点追踪周报_v1.md`。本期定调：科技硬件退潮、内容/资源/券商接棒。

## 2026-10-09
- **hotspot 卡片交互链路修复（后端对齐 + 公网激活指南）**：修 4 个根因 bug——① 卡片按钮 `source_id` 原为 `s1/s2/s3` 与 `card_counter.py` 的 `src1/src2/src3` 对不上；②「🔗 打开」原为 `open_url`（飞书不回传，点击永远 0）；③ `build_card()` 生成旧布局，点赞刷新会闪回；④ `do_POST` 只认旧版事件格式。修复：卡片 `source_id` 改 `src1/2/3`、打开改 `callback(action=open)`；`SOURCES` 重排对齐；`build_card()` 读 S2 模板注入实时计数；`_extract_event` 兼容飞书 legacy/schema2.0/`url_verification` 三种推送。本地 `verify_backend.py`+`http_verify.py` 回归跑通（challenge 校验、点赞→update_card、打开→open_url、sqlite 计数正确）。重发修复版卡片到「A股热点雷达」(oc_1b3459db9672aa3b9f58a5ad9f068df0)，message_id `om_x100b63bac6c720a4b10039d35f9d636`（key=hotspot-20261009-v3）；旧卡 `om_x100b6348324c3ca8b39cde849afc6ce` 因 source_id 错需手动删。部署指南见 `skills/hotspot-tracking/references/deploy_callback.md`（公网暴露 + 飞书事件订阅 Request URL 配 `/feishu/callback` + 加「卡片回传交互」事件），沙箱无公网入口，该步须用户在自环境执行。
- **hotspot-tracking 卡片升级（S2 落地飞书）**：把 HTML 看板确认的 S2 设计落回 `skills/hotspot-tracking/assets/card_interactive_hotspot.json`（标题即数据源链接 + Tier 常显 + 结论 + 来源 + 🔗打开 + 👍赞 + 计数占位）；规避 Card 2.0 schema 坑（border_color 用 blue-100、button.type 用 default、panel 删 background_color）；三数据源 URL 取自 `data/base_sync.json`。发送成功，群「A股热点雷达」(oc_1b3459db9672aa3b9f58a5ad9f068df0)，message_id `om_x100b6348324c3ca8b39cde849afc6ce`。计数当前占位 0，待后端部署 + 飞书 Request URL 配通后实时回写 Base。
- **飞书开放平台后台清单（交互激活收尾）**：补充 `skills/hotspot-tracking/references/feishu_console_checklist.md`（后台 4 步填法 + 权限表 + 错误码排查）。关键纠偏：官方文档明确 `card.action.trigger` 回调「权限要求暂无」——卡片点击回调不需要任何额外 API 权限，已修正 deploy_callback.md 中"开通 im:message"的误述；生效三要素 = Request URL(Webhook) + card.action.trigger 回调 + 发布新版本（不发布报 200340）。区分"回调配置"与"事件配置"页签。

## 2026-09-24
- **P03 芯片行业深度研究（Track A ② 行业）**：新建项目 `research/P03-project/`，按 research-industry 六段式方法论产出 `archive/raw/行业/20260924_行业_芯片行业深度_v1.md` + `.csv`。核心结论：2026 为 AI 单点拉动的"非典型超级周期"（价涨非量涨）；**兑现分层**（存储/设备真兑现、先进封装半兑现、EDA/光刻机未兑现）；**国产化三级梯队**（成熟制程/清洗/DRAM 第一、刻蚀/沉积/CMP/先进封装第二、EDA/光刻机/HBM 第三）；反噬风险在 2027 云厂商 Capex 降速与日本 2026-05-29 管制。状态机已回写 6 条 claims + 5 个 monitors + 5 条 queue。
- **数据来源**：WebSearch 实时抓取 2026 行业数据（IBS/Yole/WSTS/SEMI/TrendForce/中信/伯恩斯坦 + A股 2026H1 中报），已按 Tier1-3 分级标注于报告 §8。
- **P03 项目目录重命名**：`research/P03-project/` -> `research/P03-cn-chip-20260904/`
- **P04 国内芯片行业 PEST 环境分析（Track B 市场进入视角）**：新建项目 `research/P04-pest/`，按 research-market 五段式①国别宏观+PEST 产出 `archive/raw/行业/20260924_行业_国内芯片行业PEST_v1.md` + `.csv`。四维特写：P(美 MATCH 法案 2026-04-02 生效/日本 2026-05-29 管制/十五五/大基金三期 3440 亿) / E(市场规模口径冲突 Omdia 8120.8 亿 vs 协会 1.7 万亿差 3 倍，并列不平均；设备国产化率 21%→43%) / S(研发强度 15% vs 25%、专利败诉率 60%、中低端过剩) / T(中芯 5nm 风险量产/长存 232 层/长电 HBM3E 良率 99.5%/第三代半导体；EUV/EDA/HBM 代差为硬禁区)。Track B 关键增量：被禁品类→需求重定向(Chiplet/RISC-V/第三代半导体/国产设备材料验证加速)→承接方合规溢价+政策+资本+订单。状态机回写 7 claims + 5 monitors + 4 queue。与 P03(Track A 景气度) 互补：PEST 解释环境成因，P03 给标的兑现度。（slug 占位 project 改为 cn-chip，强调国产化角度；用户指定日期 20260904，与创建日 0924 不一致，按用户原串保留）。内部链接均走 ID P03（frontmatter project: P03、状态机引用），无断链；`load_context --list` 仍正确识别。

- **file-manager 补「调研项目目录命名」规范 + 命令写法统一**：`SKILL.md` 命名规则拆为 2.1 归档文件 / 2.2 项目目录（`research/<PID>-<slug>[-<YYYYMMDD>]/`，含 `cn-chip`/`pest`/`us-crypto` 示例，强调 PID 为稳定引用键、slug 可改名零断链）；`references/naming-and-frontmatter.md`、`USER-GUIDE.md` 同步加项目目录小节；USER-GUIDE 校验命令由旧式 `python script/...` 改为 `python -m script.validate_frontmatter` 并指回 AGENTS.md 铁律 #9（命令规范权威出处）。
- **P04 项目目录重命名（按 file-manager 最新规范）**：`research/P04-pest/` → `research/P04-cn-chip-pest/`（slug 由占位 `pest` 升级为 `cn-chip-pest`，与 P03 `cn-chip` 同域；PEST 为环境扫描而非日期快照，按规范 `[-<YYYYMMDD>]` 可选、此处不加）。内部链接均走 ID P04（frontmatter `project: P04`、状态机互指），无断链；`load_context --list` 仍正确识别。

## 2026-09-23
- **MILESTONE 重定为交付里程碑 M1/M2/M3**：新增 `## 0.5 里程碑总览`——M1 框架设计（✅ 已完成）、M2 跑通行业研究闭环（🔄 下一步）、M3 数据源与度量自动化（⬜ 规划中）；原"确认流程（阶段1–4）"保留为推导依据；§1 阶段4 状态更新为"框架已定（M1 完成）+ SSOT 双域分离已裁定"，§5 推进顺序的"下一跳/之后"改为指向 M2/M3。
- **铁律#2 裁定 SSOT 双域分离**（AGENTS.md）：研究域（宏观/行业/公司/热点/个人配置）SSOT=本地 `archive/`(Obsidian vault)，飞书/lark 对研究产出不反向写；资讯域（日频）独立管线，采集→lark 卡片→**lark base 多维表格** 为其云端 SSOT（不入 `archive/`、不做双链、无 claim）；两域互不反向写、互不混源。
- **docs/09 补证据可信度 Tier1-3 章节**（§2.6）：区分①证据 Tier（评价报告质量，采集侧分级）与②数据管线（§三工程实现）是两件事；Tier1 一手官方 / Tier2 二手机构 / Tier3 转述社媒 及采信规则；强调验收=报告质量而非数据源等级、关键结论需交叉验证、反方也标 Tier、与命中率/复盘次数共构"质量×复用"验收。

## 2026-09-22
- **新增 `docs/DESIGN.md`（新手指引）**：定位为"人类新手从零上手"，明确与 `AGENTS.md`（AI 接入铁律+目录地图）和 `docs/ARCHITECTURE.md`（系统架构与数据流）的边界——AGENTS 管"AI 不能违反什么"、ARCHITECTURE 管"系统长什么样"、DESIGN 管"你第一次怎么动手"。含能力地图、目录速览、常用命令（区分已可用与规划中）、上手路径、查文档索引、实战避坑。
- **修正 `docs/ARCHITECTURE.md` 组件树**：补回被遗漏的 `research/`、`data/`、`metrics/` 三个关键目录（与 `AGENTS.md` 目录地图一致）。
- **修 `docs/prototype/09` 交叉引用**：`docs/08` → `08-框架细节确认清单.md`（同目录兄弟文件）。
- **prototype 内容复核**：`docs/prototype/` 下 9 个设计稿主题互不重复、无重复标题、无 `product/` 或旧 `docs/0X` 残留路径，确认为已归档设计草稿的权威集合，无需删除重复内容；状态索引见 `docs/README.md`。
- **记忆沉淀**：`memory/MEMORY.md` 运行环境段新增铁律"**shell 报错就用 Python 试**"（本机 Bash/PowerShell 不稳，`mv`/`mkdir` 静默不落盘、内联 unicode Python 段错误、PowerShell 不展开通配符、stdout 常被吞 → 文件操作/批量/含中文输出优先用 Python 脚本写盘+Read 验证）。
- **命令风格统一为 `python -m`**：`script/*.py` 一律改为模块式 `python -m script.<模块>`（如 `uv run python -m script.load_context --list`）。已批量改写实时指令文档 `docs/DESIGN.md`、`AGENTS.md`、`research/README.md`、`archive/wiki/MOC.md`，并同步修正 4 个脚本内部的 usage 串（与脚本实际输出一致）。历史/设计类文档（CHANGELOG/TODO/MILESTONE/SCENARIO/`docs/prototype/*`）属变更记录，未改。
- **命令风格全量统一（续）**：按用户要求把"统一成 `-m` 风格、包括以后"贯彻到底——全仓扫描并转换所有**命令式**引用：① `docs/prototype/07`（2 处 `python script/`）+ `research/_template/research-state.yaml` + `research/_archive/legacy-research-state-v1.yaml` 的 `python script/x.py` → `-m`；② `docs/prototype/09` 里的运行命令示例（周期跑 / 走 / 推荐入口 / refresh_monitors / query_data）改为 `python -m` 式，而"新增 `script/metrics.py`"等**文件创建引用**保持路径式（有意区分：运行命令用 `-m`，文件引用用路径）；③ 其余 CHANGELOG/TODO/MILESTONE/SCENARIO/08/06 里的 `` `script/x.py` `` 属文件/变更叙述，保持路径不变。④ **AGENTS.md 铁律 #9** 写入面向未来的命令约定（运行 `script/` 脚本必须 `python -m script.<module>`，禁止 `python script/x.py`）。

## 2026-09-19
- 确立**开发核心**：让智力资产可沉淀/复用/迁移/审计（三层核心资产：可移植指令层 / SSOT / 知识回路）。
- 确认**基础工具链**：obsidian + python + git；知识库**本地为主**，飞书出报告 + 跨平台分享。
- 确认**文件夹基线**：skills / memory / docs(README/MILESTONE/PROGRESS/CHANGELOG)。
- 查实 **WorkBuddy 存储模型**：skills 用户级 `~/.workbuddy/skills`、项目级 `{ws}/.workbuddy/skills`；memory 三层（云端/用户级 MEMORY.md/工作区 memory/）；身份文件 SOUL/IDENTITY/USER 在用户级。
- 产出 `MILESTONE.md`（含 5 大块映射 + 查漏补缺清单 8 项）、`PROGRESS.md`、`CHANGELOG.md`。
- **待决（早期）**：secrets 存储位置、vault 与 workspace 目录关系、outputs 与 vault 协同、git 边界、典型使用场景清单、飞书适配边界。
- 后续决策（同日）：secrets 双轨（secrets/ + .env）、archive=vault(SSOT)、research 加「宏观分析」子类、结构化数据 csv/json(单次)/sqlite(cron)、frontend 与 S18 入待办、git 仅跟踪 script/。
- `file-manager` 落地 `.workbuddy/skills/`（SKILL.md + references/ 规则文档），绝对路径改为 `<workspace>` 占位，不硬编码私密信息。
- `config/` 拆分为 `types.yaml`(受控6类) + `tags.yaml`(标签库+别名+阈值)；file-manager 改 `USER-GUIDE.md`，新增 `ARCHITECTURE.md`（架构+数据流，位于 docs/），`AGENTS.md` 收敛为 AI 接入先读。
- **模型调用方式确定**：直接用 WorkBuddy / `claude -p` 等 chat 模型调用，**不配大模型 API**。
- **首个 pilot 启动**：国内热钱行业流动宏观分析 → `archive/raw/宏观/20260919_宏观_热钱流动行业分析_v1.md`（+ 同目录 CSV 数据源）。结论：热钱高度集中于电子/半导体（AI 算力硬件链），需警惕高估值高拥挤逼空风险。
- **wiki-skill 首次执行（pilot 收尾，知识回路跑通）**：`archive/raw/宏观/` 报告 → 抽实体 → `archive/wiki/` 产出 8 篇双链笔记（`宏观/20260919_宏观_热钱流动行业分析`、`行业/半导体`、`行业/AI算力`、`行业/存储芯片`、`资金/北向资金`、`资金/主力资金`、`资金/风格切换`、`公司/宁德时代`）+ `archive/wiki/MOC.md` 知识地图。
- 基础设施补齐：`archive/.obsidianignore`（排除 sqlite/db/临时物，原件保留）、`script/load_secrets.py`（secrets/.env 安全读取接口，相对定位 workspace 根、不打印值）、`memory/experience.schema.md` + `memory/experience.jsonl`（模型跑通/碰壁经验格式规范 + 5 条真实经验）。
- MILESTONE 推进：阶段1 组件清单 ✅ 收尾；新增 **§6 分工**（谁做/依赖/IO 边界）与 **§7 技术栈**（模型层 = 调用方 chat 模型，不配 API）；阶段1–3 均已定，剩阶段4 流程确认。
- `docs/TODO.md` 重构：新增"✅ 已完成"区，划掉模型后端选型/file-manager/vault忽略配置/secrets接口/jsonl规范/wiki-skill pilot；保留 wiki-skill 自动化、research 子类模板、分类引擎、frontend、适配器与 2 项待决策。
- **research 子类模板化启动**：新增 `.workbuddy/skills/research-macro/SKILL.md`（宏观分析子类）——由 pilot 反推，含四路资金交叉验证方法论、输入/输出契约、frontmatter 模板、强制反方论点清单、执行流程与常用监控指标；可作为其余 5 个 research 子类的模板参照。
- **新增「研究状态机」= 跨会话记忆（本轮核心）**：`config/research-state.yaml`（五段：`focus` 当前焦点 / `claims` 结论台账 / `monitors` 监控指标带阈值 / `queue` 待办队列 / `datasets` 已归档数据集索引）+ 读取端 `script/load_context.py`（md 人读 / `--json` 机读 / `--files` 列数据文件 / `--only <status>` 过滤；零硬编码，上溯 `AGENTS.md` 定位 workspace 根）。**解决的问题**：调研结论/建议散落在 md 正文，下次会话读不到、要重做。每条结论强制带 `evidence`(证据笔记) + `data`(结构化记录) 指针，status 走 open→validated/falsified（证伪不删，留作教训）。已写入 10 条结论（宏观 5 + 行业 5）、4 个监控指标、4 项待办。
- **`research(行业)` 子类首轮完成**：《半导体 / AI 算力链深度分析》→ `archive/raw/行业/20260919_行业_半导体AI算力链深度_v1.md` + 同目录 CSV（frontmatter 校验通过，2 文件 0 错误）。核心结论：算力链在 2026H1 已兑现到利润表但**兑现分层**（光模块/算力芯片/代工真兑现，存储是周期×国产替代，先进封装+HBM 是需求最刚性而国产最薄弱）；七家 AI 芯片公司仅海光+寒武纪真正盈利（占 70.4%）；**最大雷在 2027**（美五大云 capex 增速 +100%→+22%，阿里/腾讯自由现金流已净流出）；波动极端（YTD 温和但振幅 102%/86%，距高点 -31%/-39%）。
- **wiki-skill 第二次执行**：由行业报告整理出 4 篇实体笔记 `archive/wiki/行业/`（[[存储与HBM]] / [[先进封装]] / [[光模块]] / [[半导体设备]]），MOC 更新为「调研笔记(raw层) + 行业/产业链」双节、**过热预警由三指标扩为四指标**（新增 M-04 全球云 capex 增速），并加入结论台账与加载命令说明。
- **决策（用户定）**：分类引擎**由 chat 模型手工执行已跑通，暂不自动化**（自动化会牺牲可控性与可审计性），脚本化推迟并记入 TODO；两个 GitHub 仓库下载**不再追**（本会话 shell 不可靠 + 网络受限）。
- `AGENTS.md` 新增铁律 #7：**调研前先 `script/load_context.py` 加载上下文、调研后回写 `research-state.yaml`**；目录地图与"你要做 X 先看哪"同步补充。
- 环境：本轮 PowerShell 可用，已建 `F:\workspace\.venv`（pyyaml），可直接 `\.venv\Scripts\python.exe script/xxx.py`；`load_context.py` 首次运行暴露 **GBK 控制台 UnicodeEncodeError**（`✓` 无法编码），已修（stdout 强制 UTF-8 + 改 ASCII 标记 `[OK]/[MISSING]`）。
- **`research-industry` skill 模板化完成**：`.workbuddy/skills/research-industry/SKILL.md`，由行业首轮反推。核心 = **六段式拆解**（① 需求被财报证实 ② 供给侧量/价/产能 ③ Why now 三条同时发生 ④ 产业链三级梯队分层 ⑤ 环节玩家地图 ⑥ comps + idea shortlist），贯穿一根线「兑现度」，产出《兑现度矩阵》与《国产化水位三级梯队》两个可复用表格格式。铁律新增：单靠口号不许下结论（拿不出客户 capex/收入增速/出货量则标 `confidence: low`）、必须区分周期与成长、**反方论点 ≥5 条且至少 1 条是时间维度的失效点**。至此 research 六大子类已建 2 个（macro / industry）。
- **细分赛道三维打分（含一次自我证伪）**：`archive/raw/行业/20260919_行业_半导体细分赛道三维打分_v1.md` + CSV。打分体系 G(收入增速30%) / C(现金流质量35%，以净现比为主) / V(订单能见度35%)，并对重资产项额外扣自由现金流。结果 **设备 4.03 > 代工 3.70 > 光模块 3.60 > 封测 3.40 > 算力芯片 3.10 > 存储 3.08**，与纯收入增速排序**几乎完全颠倒**。关键证据：中际旭创净现比 13.2%、倒推 Q2 单季经营现金流 -15.69 亿（Q1 +33.68 亿）、**合同负债仅占营收 0.05%**；海光盈利 17.98 亿而经营现金流 -4.28 亿；北方华创净现比 111.98% 且 FCF +28.85 亿（六环节唯一）。**上一版 idea shortlist 第 1 位（中际旭创）的依据被证否**，对应 claim `C-20260919-12` 标记 **falsified 并保留作教训**（符合"证伪不删"的状态机原则）。
- **`research(公司)` 子类首轮完成（CATL）**：`archive/raw/公司/20260919_公司_宁德时代-资金面撤离重估_v1.md` + CSV。结论 **「杀的是分母里的叙事，不是分子里的业绩，但分子有三道裂缝」**。业绩端：H1 营收 2769.17 亿 +54.80%、归母 432.84 亿 +41.98%、经营现金流 602.17 亿、净现比 139.12%、**储能收入 +87.54%**（第二曲线已成立）、拟 200–400 亿回购注销。裂缝端：**毛利率三连降 28.21%→24.80%→23.15%**（两季 -5.06pct，Q2 增收 +56.91% > 增利 +36.46%）、合同负债较年初 **-25.9%**、存货 +38.39% / 应付债券 +728.01%。资金端：9 月 ▼-16.94%、单周主力净流出 **63.79 亿列全市场第一**、PE(TTM) 由 29.41x 压至 **16.44x**；且发现**卖方 100% 买入评级 vs 买方主动偏股基金持股比例 -0.99pct** 的背离。CATL wiki 笔记借此完成财报交叉验证，confidence 由 medium 升 high。
- **新方法论文沉淀**：新建 `archive/wiki/方法/净现比与合同负债.md`，固化两条判别原则：① A 股重资产制造业「收入增速+订单指引」必须配「净现比+合同负债」，且要再扣一层自由现金流；② 当「高现金流+低估值」与「负现金流+高估值」并存时驱动变量是**资金的故事偏好**，判断轮动应盯**资金边际流向**而非静态估值差（"便宜"可以持续更久，缺的不是价值是催化）。两条已被当周实际资金流向事后验证一次。
- **研究状态机扩充**：claims 新增 C-11~C-17（含 1 条 falsified、2 条方法论），monitors 新增 M-05（中际旭创现金流）/ M-06（宁德毛利率）/ M-07（北方华创合同负债），合计 17 条结论 + 7 个监控指标；queue 收口 Q-02 / Q-04 为 done 并新增 Q-05~Q-07。
- **`load_context.py` JSON 序列化 bug 修复（真 bug）**：`--json` 模式原会抛 TypeError。根因：**YAML 会把 `YYYY-MM-DD` 自动解析成 `datetime.date` 对象，而 `json.dumps` 默认无法序列化**——此前只测过 md 模式，故未暴露。已加 `default=str` 修复并验证通过。这与 `validate_frontmatter.py` 早先的 `_date_to_str` 是**同一类坑**（YAML 日期自动类型转换）。
- 校验：`archive/raw` 4 个 md、`archive/wiki` 14 个 md 均 frontmatter 校验 **0 错误**。
- **确立两条调研主线（Track A / Track B）**：`docs/prototype/07-调研主线方法论.md`。**Track A 景气链 Top-Down**（宏观资金 → 行业景气 → 龙头公司，产出可交易标的短名单，已跑通三段，对应 research-macro / research-industry / research-company）；**Track B 特定行业市场进入调研**（国别宏观+PEST → 目标行业 → **相邻/替代行业** → 用户画像 → 主要 players，产出机会区/禁区/观察哨 + 玩家地图，对应新增 `research-market`）。关键差异：Track B 第一步必须问"合不合法"而非"有没有需求"。`config/research-state.yaml` 新增 `tracks` 段。
- **新增 `research-market` skill（Track B 模板）**：`.workbuddy/skills/research-market/SKILL.md` —— 五段式流程 + Track B 三个独有判别点（准入优先于需求 / 追需求重定向的承接方 / 客单价×频次拆解）+ 强制反方论点清单（监管时间轴、收入是某种 β、集中度、需求见顶、成本刚性、口径陷阱）+ 输出契约。
- **Track B 首跑：美国加密资产市场进入调研**（三篇 + 3 份 CSV，frontmatter 校验 0 错误）：
  - `archive/raw/宏观/20260919_宏观_美国宏观与PEST基线_v1.md` —— GDP 32.38 万亿 / 人均 94,430 **但家庭收入中位数仅约 80k**（基尼 46.5，K 型分化）；**监管三档**：GENIUS 已生效、SEC/CFTC 五分类已发布、**CLARITY Act 2026-09 参议院未达 60 票失败**。
  - `archive/raw/行业/20260919_行业_美国加密资产市场进入调研_v1.md` —— ⭐ **结构性发现：美国零售 CFD 非法**（CEA §2(c)(2)(D) + §2(e)，ECP 门槛 1,000 万美元），需求被重定向至 CME 微型期货 / 期权 / **Kalshi 预测市场**（唯一 CFTC 注册 DCM）；承接方因此获得合规溢价 + 机构入口 + 定价权（CME 加密业务 GAAP 经营利润率 65%）。用户画像：**6,700 万人持有（每 4 个成人 1 个）但计划加仓者过半 ≤$5,000 → 小额高频，变现靠频次不靠 AUM**。
  - `archive/raw/公司/20260919_公司_美国加密与衍生品主要玩家_v1.md` —— COIN/HOOD/BLSH/Circle/CME/IBIT 财务对照。**玩家分化根因是商业模式**：HOOD 市值 1,077 亿 = COIN 512 亿的 2 倍，而年化收入接近；差异在 ROE 22.01% vs 10.05%、净利率 41.80% vs 17.55%。COIN 深度更深但**费用占年化收入 88%**、EPS 预期被砍 -44%。⚠️ **HOOD 经营现金流 -33.70 亿与净利 +18.83 亿严重背离，标 low confidence 待查 10-K**（A 股沉淀的净现比方法论在美股的直接应用）。另：**BTC ETF Q2 已连续第三个季度净流出**，AUM 增长靠升值掩盖赎回 → "机构持续进场"叙事需修正。
- **wiki-skill 第三次执行**：新增 6 篇笔记 `archive/wiki/`（[[美国宏观与PEST]] / [[美国加密资产]] / [[稳定币]] / [[CFD与预测市场]] / [[Coinbase]] / [[Robinhood]]）+ 方法论 [[需求重定向与监管准入]]（准入优先于需求、追重定向承接方、渗透率拆客单价×频次、区分 β 与 α、同涨同跌=假分散）。MOC 重构为「Track A / Track B」双分区并加 Track B 五观察哨。
- **研究状态机扩充**：claims 新增 C-18~C-24（Track B 7 条，含 1 条方法论），monitors 新增 M-08~M-11，queue 新增 Q-05~Q-07（核实 HOOD 现金流口径 / 三组数据口径核实 / 跨境监管对照），datasets 新增 3 条。合计 **24 条结论 + 11 个监控指标**。
- **【结构变更】新增调研项目层 `research/`，状态机按项目拆分**（用户指出：两个业务调研共用一个 `config/research-state.yaml` 不合理）：
  - 旧 `config/research-state.yaml` → `research/_archive/legacy-research-state-v1.yaml`（保留迁移底稿，不再被读取）。
  - **P01** `research/P01-hotspot-20260919/`（Track A · 半导体/AI算力链）：15 条结论（含 1 条 falsified）+ 7 监控 + 6 待办。
  - **P02** `research/P02-us-crypto/`（Track B · 美国加密市场进入）：6 条结论 + 4 监控 + 5 待办。
  - **`_shared/`**：跨项目方法论 3 条（C-16/C-17/C-24），带 `derived_from` 溯源到原项目与原结论——**方法论独立于项目存活**，项目结束也不沉睡。
  - 每项目两份文件：`project.yaml`（驱动问题 / scope_in / scope_out / 交付物 / track）+ `research-state.yaml`（focus / claims / monitors / queue / datasets）。
  - 新增 `research/_template/` 与 `script/new_project.py`（`--id P03 --name ... --track B` 一键生成，已存在则报错不覆盖）。
  - `script/load_context.py` 升级 v2：`--list` / `--project <PID>`（逗号分隔多个）/ `--no-shared` / `--files` / `--only` / `--json`；**项目靠扫描 `research/*/project.yaml` 发现，不建 index 注册表**（避免注册表与项目文件两处漂移）；旧单文件仍在时自动退化为兼容模式并告警。
  - 归档笔记 frontmatter 新增可选 `project: P01|P02`（7 篇已回填），`script/validate_frontmatter.py` 校验其格式（`^P\d{2}$`）；`archive/` 仍按 type 分目录不按项目切分，靠路径与 frontmatter 互指。
  - 文档同步：`AGENTS.md`（铁律 #8 + 目录地图 + 入口）、`docs/ARCHITECTURE.md`（新增 §6.1 项目层）、`docs/prototype/07-调研主线方法论.md`、`docs/TODO.md`、`archive/wiki/MOC.md`。
  - ID 约定：迁移内容保留旧 ID（`C-20260919-nn`）不断链；新结论用 `C-<PID>-<nn>` / `M-<PID>-<nn>` / `Q-<PID>-<nn>`。
- **【改名】P01 → 「2026-09-19 行业热点观察」**：项目原名"半导体 / AI 算力链景气度追踪"覆盖过窄（实际含 宏观资金面 → 半导体/AI 算力链 → CATL 公司重估 三层），改为**按日期的观察类项目**。目录 `research/P01-semi-ai-chain/` → **`research/P01-hotspot-20260919/`**，`project.yaml` 的 `name` / `question` / `scope_in` / `deliverables` / `notes` 同步改写，`research-state.yaml` 的 `focus.topic` 同步。**目录命名约定更新为 `P<编号>-<slug>-<YYYYMMDD>`**（观察类带日期，便于按日归档、后续可建同名新项目）。全量引用同步：`archive/wiki/MOC.md`、`docs/ARCHITECTURE.md`、`docs/TODO.md`、`docs/prototype/07-调研主线方法论.md`、`research/README.md`、两篇归档笔记正文、`.workbuddy/memory/`。**笔记正文不再硬编码项目目录**，改为"项目 P01 的 `research-state.yaml`"——避免下次改名再断链。
- **新增 `research-company` skill（Track A 第三段模板）**：`.workbuddy/skills/research-company/SKILL.md`，由 CATL 首轮（`20260919_公司_宁德时代-资金面撤离重估_v1.md`）反推。核心是**分子 / 分母三分法**：
  - **五段式**：① 业绩侧（报告期财务表 + 业务拆分找第二曲线 + 现金流质地）→ ② **分子的裂缝**（毛利率 ≥3 季趋势 / 合同负债方向 / 资产负债表变重 / 现金流与利润背离）→ ③ 估值与资金（三口径 PE + 估值压缩幅度 + 同期资金对立面 + 三方行为表 + ⚠️ 口径异常）→ ④ 同业横截面（判别市场在定价质地还是叙事）→ ⑤ **三分法定性**（估值 / 基本面 / 时间 + 下一个验证点）。
  - **铁律 8 条**，其中最关键：**下跌 ≠ 错杀**——找不到不能用"风格切换"解释的分子裂缝，才允许下"错杀"结论且须标 `confidence: medium`；**现金流质量是硬门槛**（承接 `_shared` C-17）。
  - **财务质量检查清单 9 项**（毛利率趋势 / 净现比 / 收入现金比 / 合同负债 / 存货 vs 收入 / 应收 vs 收入 / 经营现金流 vs 利润 / 有息负债 / FCF）。
  - 反方论点清单 8 项，含"硬反方"（有没有一条负面证据不能用杀估值解释）与时间维度失效点。
  - 输出契约章节号固定，`type: 公司`，落 `archive/raw/公司/`，frontmatter 带 `project`。
- **【回跑】CATL v1 → v2：research-company 模板首次实证**（2026-09-20）：`archive/raw/公司/20260919_公司_宁德时代-资金面撤离重估_v2.md`（沿用 v1 CSV，frontmatter 加 `supersedes`，篇首加"数据窗口与口径声明"）。**模板逼出 4 项 v1 遗漏**：
  - **单季净现比**：H1 139.12% 拆开是 Q1 **162.4%** → Q2 **117.7%**（环比 -44.7pct），利润质量**斜率向下**——只看半年汇总完全看不到。
  - **相对收益**：单周 ▼-8.64% vs 创业板指 ▲+1.52% = **-10.16pct**，电力设备行业 -35.55 亿而电子 +140.09 亿 → **彻底的个股负 alpha + 赛道级再分配**，不是板块 beta。
  - **前瞻 PE 入表**：2026E 14.46x（65 家）/ 2027E 11.53x（53 家）/ 2028E 9.60x。
  - **营业成本口径冲突**（登记不结论）：分部成本累计同比 -1.78%/-1.56% 与整体毛利率三连降方向矛盾。
  - 定性明确为 **「部分错杀」**（估值叙事错杀 + 基本面真实边际转弱 + 时间待 1Q27 排产）。
  - 状态机回写：新增 **C-P01-01~03**；C-20260919-04 转 **validated**；monitors +M-08（单季净现比）/ M-09（基金持股比例）；queue +Q-P01-03/04/05（成本口径核实 / 短名单强制单季拆分 / 补应收·资本开支·筹码）。P01 现有 **18 结论 / 9 监控 / 6 待办**。
  - **模板回灌 9 处修订**：新增铁律「相对收益对照」「结论必须明确定性 错杀/部分错杀/非错杀」；财务清单 9 → **11 项**（+筹码结构、+口径一致性自检）；输出契约加篇首口径块、§0 上游 claim 校验结果、§5 反方论点"能否用杀估值解释"列、§7 **建议监控项表**；新增 **「模板回跑（recheck）约定」**章节。
  - **待办（用户定暂缓）**：剩余 3 个子类（每日资讯 / 热点追踪 / 个人配置）暂不模板化，套 research-company 骨架即可；新增条目 **P02 · HOOD 现金流口径核实**（经营现金流 -33.70 亿 vs 净利 +18.83 亿，疑为客户现金托管/清算口径，需查 10-K）。
  - 同步：`research-macro` 补 `load_context` + 回写步骤与下游链；`research-industry` 补下游 `research-company` 与 `project` 字段；`AGENTS.md` 技能段列出四子类分工；`docs/TODO.md` 三分法条目由待办转为已完成。

## 2026-09-20（续）

- **调研动作挂起 + 框架细节清点**（用户定：目前优先级是先确认整体框架细节）
  - `docs/TODO.md` 新增 **P01 · 短名单收敛（Q-P01-01）**，标"暂缓，先确认框架细节"；同批挂起 Q-P01-02 / 03 / 05。项目内 priority 仍为 P0，全局排序在框架确认之后。
  - 新增 **`docs/prototype/08-框架细节确认清单.md`**：
    - §一 已定基线契约速查（SSOT / 目录 / 命名 / frontmatter / 分类 / 项目层 / 状态机 / 主线 / 脚本 / git / 色规），本次不重议。
    - §二 **12 条待确认项 D1–D12**，每条含 现状 → 风险 → 选项 → 建议：D1 git 跟踪范围 / D2 扩展字段入 schema / D3 多来源 url / D4 文件名日期语义 / D5 版本升级规则 / D6 状态机 schema 校验 / D7 `_shared` 提升门槛 / D8 项目归档与清单隐藏 / D9 wiki 分类词表 / D10 空类型目录 / D11 `output/` 流转与留存 / D12 标签阈值落地。
    - §三 5 条次要项（track 允许 A+B / csv 入索引 / 效果度量 / 飞书 RUtable / experience.jsonl 消费）。
    - §四 拍板记录空表（确认后填，并回写本 CHANGELOG）。

- **方案审查（solution-clarifier）+ 频率/度量/数据源方案定稿**（2026-09-20）
  - 用 `skills/common/solution-clarifier.md` 流程审查现行方案，先拆隐含假设（单人使用 / 瓶颈在沉淀而非取数 / 手工优先是长期路线…）再收口为一个关键问题；用户答复后进入交付。
  - **用户定的四条前提**：系统服务个人；频率 = 资讯**日频** / 行业**月频**（顺带公司）/ 宏观**季频** / 热点**不定期**；**数据治理不降级**（长期执行）；衡量指标 = **结论命中率 + 复盘次数**；数据源自动刷新为高优先级待办（先确认方案）。
  - 新增 **`docs/prototype/09-度量与数据源方案.md`**：
    - §一 **频率分层治理**——日频资讯**不进 wiki、不做双链**（只 frontmatter + 日汇总），手工成本集中到低频高价值的行业/宏观/公司；月频/季频天然对应"模板回跑 + supersedes"，成为复跑节拍器。
    - §二 **度量**：双轨（内在价值 cited_by 为主 / 飞书 uv·pv 为辅，且对个人自用 pv 权重应低）；claim 新增 6 个可选字段；命中判定规则可机读（cited_by 含非自身 evidence 的笔记 = hit，成熟期 90 天无引用 = miss，falsified 单列）；`metrics/` + `script/metrics.py`。
    - §二.4 **飞书浏览数已核实官方接口** `GET /open-apis/drive/v1/files/{file_token}/statistics`（返回 uv/pv/like_count），两个前提：租户需开启"文档访问记录功能" + 调用身份需文档管理权限（缺一 403）；降级用自建跳转短链或卡片回调。
    - §三 **数据源**：当前结构"约定已具备、缺三件"（目录 / catalog 数据字典 / query 入口）；建议 `data/` + `catalog.yaml`（字段口径写死，避免重演 CATL 成本口径冲突）+ `script/query_data.py`；首个数据源选世界银行；后续 `refresh_monitors.py` 让 13 个监控指标自动回填。
  - `docs/08` 拍板记录填入：治理类 D1–D12 按建议默认值生效；新增 E1–E5（E4 飞书前提待实测）。
  - `AGENTS.md` 目录地图新增 `data/` 与 `metrics/`（均不进 vault）；`docs/TODO.md` 新增三条实现待办（度量 / 数据源层 / 飞书统计）。

## 2026-09-24（续）· 飞书三件套交付（P01 热点播报）

- **P01 热点追踪 → 飞书三件套**（用户："一个个来解决" + 追加调整）
  - ① Base「A股热点追踪-原始信号源」：建表 + 7 条信号源记录；**用户追加调整**：删独立 URL 列，链接并入「标题」做成可点击 `[标题](url)`。base_token `GqZ8bhLL5aThICsG4bGcOnQIn6Z` / table `tbl0JYm0AstPfJeu`。
  - ② Doc「A股近一周热点追踪（2026-09-24）」：从 `archive/raw/热点/20260924_热点_A股近一周热点追踪_v1.md` 导入（去 frontmatter + 顶部交叉引用 Base 链接）；document_id `HjQ8dlqOYoVcHWxRcPQcnx9qnle`。
  - ③ 群「A股热点雷达」+ 交互卡片：建群 chat_id `oc_1b3459db9672aa3b9f58a5ad9f068df0`；Card 2.0 热点弹框（核心信号 + Top3 + 双按钮跳转 Base/Doc）于 23:36 以 user 身份发送成功，message_id `om_x100b6460788bf8a4b316f978817069f`。
  - 权限：user 身份缺 `im:message.send_as_user` → 走 OAuth 设备授权（auth qrcode 扫码）补权后发送。
  - 分层：**本地 `archive/` 为 SSOT，飞书 base/doc/群 为分享视图**（Doc 顶部已注明本地路径）。

## 2026-09-25 · 热点卡片交互化（点赞 / 点击计数 / 投票 / 下钻）

- `hotspot-tracking` skill 新增 `scripts/card_counter.py`（stdlib `http.server` + `sqlite3`，零依赖）：数据源点赞 `like_count`、打开链接 `click_count`（callback 返回 `open_url` 动作真打开）、研判 👍/👎 反馈、下一条主线投票（百分比条形）、「追一下」写 `queue` 队列。
- 卡片增强：主体 = 核心结论 + 研判 + Top3；4 个 `collapsible_panel` 折叠长内容（9条排名表 / 政策时间轴 / 资金温度计 / Tier 可信度）；末尾数据源带 Tier 标签 + 🔗打开 + 👍点赞。
- 已发「A股热点雷达」群：`message_id om_x100b6460ddee38a0b03087d56bc7443`（00:00:50）。
- **Card 2.0 schema 坑（已回写 SKILL.md §五）**：`div` 无 `elements`；`border_color` 无 `neutral-100`；button `type` 无 `secondary`；panel header `background_color` 不接受 `grey-100`；报错一次只报一个，须批量清理；发送前压缩 JSON。
- ⚠️ 交互生效前提：后端需公网可达 + 飞书应用 Request URL 指向 `/feishu/callback`。

## 2026-10-07 · 热点卡片交互字段回写飞书 Base

- 在 Base「A股热点追踪-原始信号源」新增「点赞数」「点击数」两列(number)，建 url→record_id 映射(7条)；`card_counter.py --ensure-base` 幂等可执行。
- 端到端验证写通道通过(probe 写读回一致→复位0/0)。
- **排错结论**：base 写权限「missing」是误报——真实 scope 名 `base:field:update` 等(无 `:write`)，`auth status` 为权威；`--domain all` 不含 base 写，用 `--domain base`。已回写 `hotspot-tracking` SKILL.md §四/§五。
- 修 card_counter.py 解析 bug：`+record-list` 返回 `{data:{data:[[行],...], record_id_list:[...]}}`、`+field-list` 返回 `{data:{fields:[{name,...}]}}`。
- 待办：后端部署公网 + 飞书应用 Request URL 指向 `/feishu/callback` 后，卡片点赞/点击/投票/下钻才激活并自动回写 Base。
