---
name: research-ppt
description: research-kit 的 PPT 交付渲染子技能。把调研主交付（口径块 + 内联引用正文 + 反方≥5 + Reference 的三段式）渲染为自包含、可演示的 PPTX 投研 deck。渲染由 workbuddy-pptx 技能（场景 #49「制作PPT」）完成，沿用其 SlideDSL 与场景体系。
type: delivery
belongs_to_suite: research-kit
derived_from: delivery-standard §0（output_target: ppt）+ workbuddy-pptx 技能（场景 #49 制作PPT）+ investment-analysis 场景
version: 1.2
---

# research-ppt — PPT 交付渲染子技能

## 定位
`delivery-standard.md` 的 `output_target: ppt` 的执行单元。它把 research-kit 的调研主交付渲染成**一份自包含 PPTX 投研 deck**：
- 由 **workbuddy-pptx 技能（场景 #49「制作PPT」）**渲染，沿用其 SlideDSL 与场景体系（默认投研风 `investment-analysis`）；
- 落 `output/<PID>-ppt-主交付.pptx`（文件名默认中文，见 workbuddy-pptx 约定）；
- 与 `local` / `lark` / `html` 同标准：保留三段式（口径块 → 内联引用 → Reference）与反方≥5。

## 何时用
`delivery-standard.md` 的 `output_target` 设为 `ppt` 时，在 G_rubric 门禁通过、主交付内容定稿后调用本子技能渲染：
1. 主交付内容按 `templates/local-delivery.md` 的结构准备好（口径块 / 章节 / 反方 / Reference）；
2. 整理为报告数据 JSON（schema 见下，与 `research-html` 完全兼容复用）；
3. 若 `delivery-standard` 配了 `master_template`，先跑风格锁抽取（见下「母版 / 主题复用」方案 A），拿到 `LOCK` 常量；
4. 调用 workbuddy-pptx 技能（场景 #49「制作PPT」），按下方「幻灯片映射」逐页生成 `.slide` 并 `slidep upsert-dsl` + `lint`，落 `output/`。

## 来源（为什么是它）
- `research-html` 已证明「调研主交付 → 自包含静态载体」的路径可行；PPT 是该路径的**演示态延伸**，受众是投委会 / 路演 / 团队汇报。
- 渲染引擎直接复用 **workbuddy-pptx 技能（场景 #49「制作PPT」）**，而非另起炉灶——它提供成熟的 SlideDSL、场景配色（投研风深蓝冷灰）与布局校验（lint），比自写 python-pptx 渲染器更稳、视觉更专业。
- 2026-11-03 已用测试样例（铝加工行业景气度跟踪 T01）端到端验证：`research/_test/ppt-sample/` 生成 5 页合法 deck，全部页 `lint` 通过（`ok:true`、无 diagnostics）。

## 内容契约（报告数据 JSON schema）
**与 `research-html` 完全兼容**——同一份 JSON 即可渲染 HTML 或 PPTX，不重复造数据：
```json
{
  "pid": "T01",
  "theme": "铝加工行业景气度跟踪（测试）",
  "date": "2026-11-03",
  "caliber": [
    ["数据窗口", "2026-01 ~ 2026-09"],
    ["单位", "亿元人民币 / %"],
    ["分类标准", "申万一级 有色金属-铝"],
    ["代理指标", "铝价月K = 价格景气代理"],
    ["缺月处理", "2026-02 春节错位，标注 N/A"],
    ["色彩惯例", "A股：涨红跌绿"],
    ["known caveat", "数据源 T+1 日频，无周度聚合"]
  ],
  "sections": [
    {"title": "1. 行业景气概览",
     "body": "2026Q3 铝加工板块营收同比 +8.4%（源：analysis_v2.json · 2026-10-30），为 2022 年来首次单季环比回升；加工费中位数 -3.1%（源：sm-fee-2026q3.csv · 2026-10-29），量增价跌特征仍存。"}
  ],
  "counter": [
    "铝价受宏观加息预期压制，若利率上行则估值承压（时间维度）",
    "地产链需求若持续走弱，加工费将再下探",
    "进口铝土矿集中度过高，地缘扰动推升成本",
    "绿电铝产能释放可能压制现货溢价",
    "板块估值已部分反映复苏，安全边际收窄",
    "下游新能源需求增速若见顶，量增逻辑存在证伪风险"
  ],
  "reference": [
    "来源索引：analysis_v2.json（本地）/ NeoData 宏观接口 / sm-fee-2026q3.csv",
    "父项目：P02 美国加密市场进入主交付"
  ]
}
```
> 测试样例完整版见 `research/_test/ppt-delivery-sample.json`（与 `html-delivery-sample.json` 同源同构）。

## 幻灯片映射（主交付 → 页）
| 主交付块 | 页 | 形态要点（投研风） |
|---|---|---|
| 封面 | 第 1 页 | 主标题=theme，副标=视角/范围；信息层（底部小字）放 `PID · date · 本地 SSOT 不反向写`。**封面禁止出现任何数字/数据**（workbuddy-pptx 硬规则）。 |
| 口径块 caliber | 1 页 | 行式 label/value，1px 浅灰细线分隔；底部虚线框放 known caveat 说明。 |
| 章节 sections | 每节 1 页（密度高可合并） | 页题=完整判断句（带数字最佳）；正文内联引用（源 span，斜体灰）；A股 涨红跌绿（`#D8382E` 涨 / `#1F9D55` 跌）；核心结论可用深主色强调卡（一页≤1 个）。 |
| 反方论点 counter | 1 页 | 编号列表 + 细线分隔（≥5 条，含 ≥1 条时间维度）；禁对称卡片堆砌。 |
| Reference | 末页或并入口径 | 来源索引 / 复杂计算 / 父项目链接；投研风可末页单列或做页脚。 |

## 渲染器（workbuddy-pptx 技能 · 场景 #49 制作PPT）
- 触发：调用 workbuddy-pptx 技能（场景 #49「制作PPT」）。
- 场景选择：默认 `investment-analysis`（投研 deck，深蓝冷灰 `#193B5B`/`#7896B2`/`#B07D1F`/`#242D36`/白底）；如需其他调性按场景库另选。
- 工具链：`slidep create <output/<PID>-ppt-主交付.pptx>` → 逐页写 `slides/NN.slide`（SlideDSL，`<Slide>/<Box>/<Text>/<span>/<br/>`）→ `slidep upsert-dsl` 追加 → `slidep lint` 校验（必须 `ok:true`）。
- 已验证样例：`research/_test/ppt-sample/`（`01~05.slide` + `T01-aluminum-ppt.pptx`，5 页全 lint 通过）。

## 母版 / 主题复用（能做什么、不能做什么）

> 2026-11-03 实测（workbuddy-pptx v20261013 + `slide_*` 工具 schema + 解包 T01 deck 验证）。结论按「能力分层」记，别把三层混成一句"支持母版"。

| 层级 | 能否复用 | 依据 / 做法 |
|---|---|---|
| **① 主题级**（主题色、字体主题、母版背景、母版装饰形状/Logo） | ✅ **自动继承** | `slidep create` 产出 = 空白 deck + **1 个 `DEFAULT` 版式** + 标准 Office 主题；解包实测 5 页全部 `own_bg=False`（页级不定义背景）且都挂 `slideLayout1`，母版/版式背景均为 `bgRef idx="1001" → bg1`。继承链完整：换主题或换母版基底，全 deck 配色与母版元素一起生效，无需逐页改。 |
| **② 版式级**（选具体 layout、用标题/正文占位符） | ⚠️ **仅 `slide_*` 工具路径支持，DSL 路径不行** | `slide_add_slides` 有 **`layout_index`**（0-based，指向第一个 master 的版式列表）可指定新页版式；`slide_set_page_properties` 的 `fill_color=""` 可**清除页级背景让 layout/master 透出**；`slide_get_master_info` 读母版、`slide_set_theme` / `slide_list_builtin_themes` 换主题。但 **`slidep upsert-dsl` 没有 layout 参数**，DSL 是「自由绘制 + 固定挂 DEFAULT 版式」，不填占位符。 |
| **③ 模板基底**（拿公司现有 .pptx 当起点） | ⚠️ **可做，但要自己收尾** | `slidep create` 只有 `--base-url / --timeout`，**无 `--template`**。复用模板须：复制模板 → `slide_remove_slide` 清示例页 → `upsert-dsl` 追加内容页（或 `slide_add_slides layout_index=N`）。模板示例页不会被自动清理。 |

**默认策略（research-ppt）**：DSL 自绘（视觉可控、lint 可校验、跨 deck 稳定）。有强制母版（公司/客户模板）时，按 `delivery-standard` 的 `master_template` 走**风格锁（方案 A，已内置脚本）**：

- **A. 风格锁（默认实现）**
  1. `delivery-standard.md` 的 `master_template` 填模板路径（写 `<path/to/company.pptx>` 占位，**勿硬编码绝对路径**）；留空则用投研风场景配色。
  2. 跑抽取：`python references/skills/research-ppt/extract_master_style.py <template.pptx>` → 生成 `<stem>-style-lock.yaml`（palette / fonts / page / layouts / master_shapes）+ 可直接粘用的 `const LOCK`。
  3. 落地：用 `LOCK` 的 `bg / ink / inkSub / accent / fontTitle / fontBody` 替换场景配色常量；**A股 涨跌色不取模板色**（涨 `#D8382E` / 跌 `#1F9D55`）；`master_shapes` 的 Logo / 页眉页脚条按 bbox 复刻为页脚元素，并校验正文安全区。
  - 收益：产物**不依赖模板文件**，可 lint、可迁移、可离线复现；模板换版重跑脚本刷新 LOCK 即可。
- **B. 模板基底（备选，非默认）**：以模板 pptx 为基底追加页，继承主题/背景/母版元素；**版式仍是自绘**，不等于套用母版占位符，需额外校验安全区是否被母版元素压住。仅在不便重刷配色时用。

**验收注意**：实测 `slidep screenshot` **未反映**母版背景改动（改 theme `lt1` 为深蓝 + 加母版形状后，截图仍为白底）。因此**视觉验收请用 PowerPoint / WPS 打开确认**，不要拿 screenshot 当母版效果的证据；结构验收用解包（`own_bg` / `sldLayout` 引用 / `bgRef`）。

## 与门禁 / 状态机的关系
- 渲染**前置**须过 `references/rules/report-rubric-v1.md` 的 G_rubric 前置清单（内联引用、口径块、反方≥5 等）。
- PPTX 文件为**单向呈现视图**，本地 SSOT（`research/<PID>/research-state.yaml` + `caliber.yaml`）不反向写。
- A股 域色彩：涨红(`#D8382E`) / 跌绿(`#1F9D55`)，与 method-topdown / research-html 交付色规一致。

## 引用
- 交付标准：`references/delivery-standard.md`（output_target 表含 ppt；§0.1 `master_template` 风格锁）
- 风格锁抽取：`references/skills/research-ppt/extract_master_style.py`（模板 pptx → `style-lock.yaml` + `const LOCK`）
- 渲染引擎：`workbuddy-pptx` 技能（场景 #49「制作PPT」）+ `investment-analysis` 场景
- 测试样例：`research/_test/ppt-delivery-sample.json`（数据）+ `research/_test/ppt-sample/`（已生成 deck）
- 门禁：`references/skills/research-core/SKILL.md`（G_rubric）
- 平行子技能：`references/skills/research-html/SKILL.md`（同一份 JSON 亦可直接渲染 HTML）
