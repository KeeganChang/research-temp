# 命名与 frontmatter 细则

## 目录落位

| 内容 | 落位 |
|------|------|
| 研究原始笔记 / 附件 | `archive/raw/<子类>/` |
| 整理后知识（双链 + MOC） | `archive/wiki/<主题>/` |
| 待分类暂存 | `archive/inbox/` |
| 产出草稿（HTML/PPT/报告） | `output/<类型>/` |
| 产出确认后 | 移入 `archive/raw/<子类>/` |
| 经验沉淀 | `memory/MEMORY.md` + `memory/*.jsonl` |
| 按日工作记录 | `.workbuddy/memory/YYYY-MM-DD.md` |
| 开发 API 密钥 | `secrets/<服务>.env` 或 `secrets/` |
| 项目运行密钥 | 根 `.env` |
| 脚本 | `script/` |

## 研究子类（archive/raw/ 下）

- **资讯**：每日资讯
- **行业**：行业调研（如铝加工）
- **公司**：公司研究（如 CATL / 宁德时代）
- **热点**：热点追踪
- **宏观**：宏观分析（GDP/CPI/PPI/PMI/LPR/货币）
- **个人配置**：组合前几种（如投资组合监控）

## 命名模板

```
<日期>_<类别>_<主题>_v<版本>.<ext>
```

- 日期 `YYYYMMDD`
- 类别用上面子类名
- 主题用短横线 slug
- 版本 `v1` 起，大改 +1

例：
- `20260919_公司_宁德时代-财报_v1.md`
- `20260919_宏观_CPI-PPI_v1.csv`
- `20260919_资讯_每日-A股_v1.md`

## 调研项目目录命名（research/）

调研项目目录命名属于 research-kit 职责，**本文件不重复定义**。规范（`<PID>-<slug>[-<YYYYMMDD>]`、引用键、可改名性、子 task 派生、结论/监控 ID）的唯一权威见 `research-kit/references/research-project-naming.md`。

- 创建：`python -m script.new_project --id Pxx --name "..." --track <drill|entry|diagnostic|inductive|scenario> [--slug xxx]`（统一 `python -m` 模块式，详见 AGENTS.md 铁律 #8）。

## frontmatter 字段

| 字段 | 必填 | 类型 | 取值 / 说明 |
|------|------|------|------|
| source | 是 | str | 来源名（文本），如 "NeoData / 公司公告 / 网页" |
| url | 是 | str | http/https 开头 |
| fetched_at | 是 | date | YYYY-MM-DD |
| type | 是 | enum | **受控**：资讯 / 行业 / 公司 / 热点 / 宏观 / 个人配置（= `archive/raw/<子类>/`）|
| structure | 是 | enum | structured / unstructured（数据源形态）|
| confidence | 是 | enum | high / medium / low（本次打标/抽取置信度）|
| tags | 否 | list | 已有标签 或 AI 新增类型（经别名归一后写入）|
| keywords | 否 | list | 提取关键词 |
| reason | 否 | str | tags 分类理由汇总（可审计）|

- `type` 受控（用户设定范围），对应 `archive/raw/<子类>/` 文件夹，模型不自动新建。
- `tags` 允许 AI 新增类型，但须经 `config/tags.yaml` 别名归一后写入并留痕，避免标签爆炸。
- `structure=structured` 建议带 `data_file:` 指向同目录 csv/json/sqlite。
- 校验：`script/validate_frontmatter.py <path>`，支持单文件或目录递归。

## 数据源留痕

- **非结构化**（网页 / PDF / 文章）：抽取为 md 存 `archive/raw/`，原件保真另存（同目录或 `assets/`）。
- **结构化**（API JSON / 行情 / RUtable）：存 csv/json（单次）或 sqlite（cron 定时），本地为 SSOT；飞书 bitable 仅查询视图。
- **线上版本**：存 URL + 缓存 md + provenance（source/url/fetched_at）。
