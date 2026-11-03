# file-manager · USER-GUIDE（使用者手册）

> 给**使用者**（人 / 接入的 AI）看的功能说明：你的文件该放哪、叫什么、写什么元数据、怎么安全删除。
> 规则细节在 `references/`；本文件是面向使用者的速查。

---

## 1. 这是什么

`file-manager` 定义了整个本地知识库的**存放规矩**：目录结构、文件命名、必填元数据（frontmatter）、安全删除。
所有归档动作（research 落盘、wiki-skill 产出、outputs 确认后入档）都遵守它。你不需要记住细节，按下面的速查做即可。

核心理念：**`archive/` 是唯一可信源（SSOT），它本身就是 Obsidian vault**；飞书/lark 只是出报告、分享的视图，不反向改它。

---

## 2. 目录速查（你最常碰的几个）

| 你要做的事 | 放哪 |
|-----------|------|
| 随手丢原始素材（网页/PDF/笔记） | `archive/inbox/` |
| 已分类的原始笔记 / 附件 | `archive/raw/<子类>/`（子类见 §4）|
| 整理后的知识库（双链 + MOC） | `archive/wiki/<主题>/`（由 wiki-skill 生成，勿手改）|
| 还没确认的报告 / HTML / PPT 草稿 | `output/<类型>/` |
| 项目经验精华 | `memory/MEMORY.md` |
| 开发用 API 密钥（飞书 / MCP 等） | `secrets/<服务>.env` |
| 项目运行密钥 | 根目录 `.env` |

> `archive/`、`memory/`、`secrets/`、`.env` **不进 git**（本地知识库靠 CHANGELOG + 每日 memory 追溯）。

---

## 3. 文件命名

```
<日期>_<类别>_<主题>_v<版本>.<ext>
```

- 日期：`YYYYMMDD`（如 `20260919`）
- 类别：research 子类（资讯/行业/公司/热点/宏观/个人配置）或产出类型（报告/仪表盘/分析）
- 主题：短横线连接 slug（如 `宁德时代-财报`）
- 版本：`v1` `v2`… 大改递增

例：
- `20260919_公司_宁德时代-财报_v1.md`
- `20260919_宏观_CPI-PPI_v1.csv`
- `20260919_资讯_每日-A股_v1.md`

### 3.1 调研项目目录命名（research/）

调研项目目录命名属于 research-kit 职责，**本手册不重复定义**，规范唯一权威见 `research-kit/references/research-project-naming.md`（格式 `research/<PID>-<slug>[-<YYYYMMDD>]/`、引用键、可改名性、子 task 派生、结论/监控 ID）。

- 一个业务调研 = 一个项目目录，不同调研互不污染。
- 创建：`python -m script.new_project --id Pxx --name "..." --track <drill|entry|diagnostic|inductive|scenario> [--slug xxx]`（统一 `python -m` 模块式，详见 AGENTS.md 铁律 #8）

---

## 4. 必填元数据（frontmatter）

凡是落到 `archive/raw/*.md` 的笔记，**必须在开头写 YAML frontmatter**，否则校验不通过、wiki-skill 不收：

```yaml
---
source: 来源名              # 必填，如 "NeoData / 公司公告 / 网页"
url: https://...            # 必填，http/https 开头
fetched_at: 2026-09-19      # 必填，YYYY-MM-DD
type: 公司                  # 必填，受控 6 类之一（见下）
structure: structured       # 必填，structured | unstructured
confidence: high            # 必填，high | medium | low
tags: [宁德时代, 动力电池]   # 选填，已有标签或 AI 新增（经别名归一）
keywords: [Q3, 毛利率]       # 选填，抽取关键词
reason: 宁德时代 Q3 财报，含动力电池产能数据  # 选填，分类理由（可审计）
---
```

**受控 6 类（`type`，不可自动新建，对应文件夹）**：
`资讯` · `行业` · `公司` · `热点` · `宏观` · `个人配置`

- `structure=structured` 建议带 `data_file:` 指向同目录 csv/json/sqlite（数据源留痕）。
- 校验命令（落盘前跑一遍）：`python -m script.validate_frontmatter <文件或目录>`（运行 script/ 一律 `python -m` 模块式，详见 AGENTS.md 铁律 #8）

---

## 5. 安全删除

- 工作区（`<workspace>`）内可任意增删改（完全访问模式）。
- **删除默认进回收站（可逆）**，不硬删；删完务必确认结果。
- 工作区外的个人目录（Desktop / Downloads 等）只做只读扫描，谨慎操作。
- 详细规则见 `references/safe-delete.md`。

---

## 6. 常见问题

**Q：我该手动建 `archive/raw/公司/` 这样的文件夹吗？**
A：子类文件夹由分类流程/你显式决定后建立，模型不会自动新建 `type`。新主题先丢 `inbox/`，确认分类后再归位。

**Q：文件命名太麻烦，能不能自动？**
A：可以。把原始素材丢 `archive/inbox/`，由分类引擎（wiki-skill / classifier）按 `config/types.yaml` + `config/tags.yaml` 打标、命名、落位。

**Q：飞书上能看到这些吗？**
A：本地 `archive/` 是主。飞书只作为出报告/分享的只读视图，不反向写。

**Q：frontmatter 写错了会怎样？**
A：`script/validate_frontmatter.py` 会报具体错误（缺字段/类型错/格式错），改完再落盘即可。

---

详见：`SKILL.md`（规范总览）· `references/naming-and-frontmatter.md`（命名+frontmatter 细则）· `references/safe-delete.md`（删除规则）
