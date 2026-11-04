---
name: research-html
description: research-kit 的 HTML 交付渲染子技能。把调研主交付（口径块 + 内联引用正文 + 反方≥5 + Reference 的三段式）渲染为自包含、可离线打开、可打印/导出 PDF 的单页 HTML 报告。HTML 渲染能力合并自内置 frontend-design 技能（md/数据 → HTML 的"frontend"位），按研究报告语境收敛为克制编辑型排版。
type: delivery
belongs_to_suite: research-kit
derived_from: 内置 frontend-design 技能（HTML/CSS 美学原则）+ delivery-standard §2 三段式
version: 1.0
---

# research-html — HTML 交付渲染子技能

## 定位
`delivery-standard.md` 的 `output_target: html` 的执行单元。它把 research-kit 的调研主交付渲染成**一份自包含单页 HTML 报告**：
- 内嵌 CSS，**零外部依赖**（字体走系统栈、无 CDN），离线可读；
- 可直接浏览器打开，也可打印或"导出为 PDF"存档；
- 与 `local` / `lark` 同标准：保留三段式（口径块 → 内联引用 → Reference）与反方≥5。

## 来源（为什么是它）
AGENTS.md 预留的 `frontend`（md/数据 → HTML / PPT，经 lark-cli 发飞书）长期为"待办"。本子技能**合并内置 `frontend-design` 技能的 HTML 渲染能力**进 research-kit 套件，并按"研究报告"语境做收敛：
- 继承 frontend-design 的**设计原则**：CSS 变量统一配色、克制而有辨识度的排版（衬线标题 + 无衬线正文）、内聚的强调色、对细节与间距的精修；
- **不继承**其"张扬视觉/炫技动效"取向——研究报告要的是可读、可信、可打印，故去掉重动画，保留编辑型(editorial)的稳重感。

## 何时用
`delivery-standard.md` 的 `output_target` 设为 `html` 时，在 G_rubric 门禁通过、主交付内容定稿后调用本子技能渲染：
1. 主交付内容按 `templates/local-delivery.md` 的结构准备好（口径块 / 章节 / 反方 / Reference）；
2. 整理为报告数据 JSON（schema 见下）；
3. 运行 `render_html.py` 生成 HTML 落 `output/`。

## 渲染器
`render_html.py`（与本文件同目录）：
```
<workspace>/.venv/Scripts/python.exe <research-kit>/references/skills/research-html/render_html.py \
  --data <报告数据.json> --out <output/<PID>-html-主交付.html>
```
- 模板：`references/templates/html-delivery.html`（占位符由渲染器拼装）。
- 占位符：`{{PID}} {{THEME}} {{DATE}} {{CALIBER_ROWS}} {{SECTIONS}} {{COUNTER_ITEMS}} {{REFERENCE_ITEMS}}`。
- 安全策略：`caliber` 值、`reference` 项为纯文本（自动 HTML 转义）；`sections.body` 与 `counter` 条目允许受控内联 HTML（如 `<span class="up">` / `<span class="down">` 标 A股 涨红跌绿、`<span class="src">` 标来源、`<strong>` 强调），由 agent 在数据中提供。

## 报告数据 JSON schema
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
     "body": "<p>2026Q3 铝加工板块营收同比 <span class=\"up\">+8.4%</span><span class=\"src\">analysis_v2.json · 2026-10-30</span>，为 2022 年来首次单季环比回升。</p>"},
    {"title": "2. 现金流质量",
     "body": "<p>净现比 1.12<span class=\"src\">catl_cashflow_q3.json · 2026-10-31</span>，经营现金流覆盖资本开支。</p>"}
  ],
  "counter": [
    "铝价受宏观加息预期压制，若利率上行则估值承压（时间维度）",
    "地产链需求若持续走弱，加工费将再下探",
    "进口铝土矿集中度过高，地缘扰动推升成本",
    "绿电铝产能释放可能压制现货溢价",
    "板块估值已部分反映复苏，安全边际收窄"
  ],
  "reference": [
    "来源索引：analysis_v2.json（本地）/ NeoData 宏观接口",
    "复杂计算：output/T01_quadrant.csv",
    "父项目：P02 美国加密市场进入主交付"
  ]
}
```

## 与门禁 / 状态机的关系
- 渲染**前置**须过 `references/rules/report-rubric-v1.md` 的 G_rubric 前置清单（内联引用、口径块、反方≥5 等）。
- HTML 文件为**单向呈现视图**，本地 SSOT（`research/<PID>/research-state.yaml` + `caliber.yaml`）不反向写。
- A股 域色彩：`.up`=红(涨) / `.down`=绿(跌)，与 method-topdown 交付色规一致。

## 引用
- 模板：`references/templates/html-delivery.html`
- 交付标准：`references/delivery-standard.md`（output_target 表含 html）
- 门禁：`references/skills/research-core/SKILL.md`（G_rubric）
- 美学来源：内置 `frontend-design` 技能（CSS 变量 / 排版 / 配色原则）
