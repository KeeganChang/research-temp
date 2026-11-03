---
name: delivery-standard
title: 交付标准（Delivery Standard）
type: config
derived_from: 证据链精简方案 v1.1 §4.5 + §8 Q1/Q2
applies_to: 所有 research-kit 产出（一次性 / 月频 / 跨会话）
output_target: lark   # 可选：local（本地 md）/ lark（飞书 Doc+Sheet）/ html（自包含单页报告）/ workbuddy_library（资料库，未测试）
---

# 交付标准（Delivery Standard）

> 本文件把「Lark Doc 为主、三层内联、Sheet 退 reference、文件级粒度、一次性也推 Doc、新闻存快照」从审阅报告与示例项目**提升为 skill 级一等指令**。换一个 agent 读 skills 即可复现交付形态，无需反推 P06/T1 示例。

---

## 0. 输出目标（output_target）

交付落到哪个载体，由参数 `output_target` 决定（当前默认 `lark`）：

| 值 | 载体 | 模板 | 说明 |
|---|---|---|---|
| `local` | 本地 markdown 文件（落 `output/` 或项目目录） | `templates/local-delivery.md` | 纯本地，无外部依赖 |
| `lark` | 飞书 **Doc + Sheet**（lark-cli 推送） | `templates/lark-doc-delivery.md` | 人读 + 复杂计算视图；单向呈现，本地 SSOT 不反向写 |
| `html` | **自包含单页 HTML 报告**（落 `output/`） | `templates/html-delivery.html` + `references/skills/research-html/` | 内嵌 CSS、离线可读、可打印/导出 PDF；渲染能力由 research-html 子技能（合并自 frontend-design）提供 |
| `workbuddy_library` | WorkBuddy **资料库**上传（未测试） | `templates/local-delivery.md` | 复用 local 模板生成的 md，再上传资料库；链路尚未实测 |

- 切换输出目标 = 改本文件 frontmatter 的 `output_target` 一行，**不动**模板与门禁。
- 无论哪个目标，**三段式（口径块 → 内联引用 → Reference）与 rubric 门禁不变**（准确性保障与载体解耦）。
- `html` 目标**不引入外部依赖**（字体走系统栈、无 CDN）；交付文件须满足 `references/report-rubric-v1.md` 的 G_rubric 前置清单，与 lark/local 同标准。

## 1. 载体分层（§4.5）

> 以下以 `output_target: lark` 为例；`local` / `workbuddy_library` 仅把「主交付」改为本地 md，其余层级（原始返回 / SSOT / 口径块 / 反方）不变。

| 层 | 载体 | 说明 |

| 层 | 载体 | 说明 |
|---|---|---|
| 主交付 | **Lark Doc** | 人读，内联引用，可读性优先 |
| 复杂计算 | 额外 **Lark Sheet** | 四象限/相关矩阵/复算视图；**挂在 Doc 末尾 reference 段链接**，不独立成主交付 |
| 原始返回 | 本地 `artifacts/` | 接口原文/抓取 payload，**不进正文**，仅服务复算 |
| SSOT | 本地 `research/<PID>/research-state.yaml` + `caliber.yaml` | 飞书文档/表格仅为**单向呈现视图**，永不反向写 |

## 2. Doc 内部三段式（§4.5 内联）

1. **顶部口径块**：单位 / 基准日 / 缺月处理 / 代理指标定义 / known caveat。
2. **正文内联引用**：每个关键数字旁标 `源：<文件> · 抓取/检索日期`（如 `源：analysis_v2.json · 2026-10-30`）。**无 `[UNSOURCED]`**。
3. **末尾 Reference**：来源 URL/文件索引 + 复杂计算 Sheet 链接 + 父项目链接（若有）。

> 模板见 `references/templates/lark-doc-delivery.md`，新任务直接套用。

## 3. 粒度（§8 Q2）

- 证据链粒度锚在**文件级**（不可再拆的可重取单元）。**不建 DAG / hash / stage 台账**。
- 新闻/资讯类来源：存**可检索文本快照**（`script/snapshot_url.py`），不存截图；快照含 URL / fetched_at / meta / sha256 + `_index.json`。

## 4. 一次性任务也推 Lark Doc（§8 Q1）

- 即使是一次性问题，也产出**轻量 Lark Doc**（finding + 内联引用 + 口径块），**不建 7-tab Sheet**。
- 目的：让未来报告能写「详见 Pxx Lark Doc §X」做轻引用，而非重新推导——**没有 Doc 才无法轻引用**。
- 仅存在复杂计算时才额外生成 Sheet，挂 reference。

## 5. 与状态机 / rubric 的关系

- 准确性保障 = **内联引用 + 口径块 + 反方≥5**（状态机自 2026-11-02 降级为可选复用层，见 `research-core`）。
- 交付前须过 `references/report-rubric-v1.md` 前置清单（见 `research-core` G_rubric 门禁）。
