---
name: wiki-skill
description: 本地知识整理 skill。扫描 raw/ 下的 markdown，抽取实体并建立 [[双向链接]]，按主题组织进 wiki/，生成/更新知识框架 MOC，保真迁移 wikilink 结构。当用户把 md 丢进 raw/ 或要求「整理知识/建双链/生成知识框架/纳入 Obsidian 笔记」时调用。
read_when:
  - 用户把 md 文件放入 raw/ 并要求整理
  - 用户要求建立双向链接、知识框架、MOC
  - 用户要把 Obsidian 笔记/调研资料纳入本地知识库
---

# wiki-skill — 本地知识整理

_把「散放 md」自动长成「可跳转、有框架的本地知识库」，且 wiki/ 直接兼容 Obsidian。_

## 触发

- 用户在 `archive/raw/` 放入/生成了 markdown（笔记、粘贴调研、scraper/markitdown 转存）
- 用户明确要求「整理知识 / 建双链 / 生成知识框架 / 纳入 Obsidian 笔记」

## 输入

- `archive/raw/*.md`：原始 markdown 投放区（等价旧 inbox）

## 处理流程

1. **扫描**：遍历 `archive/raw/` 下所有 `.md`
2. **抽取实体**：识别人物 / 概念 / 项目 / 数据指标等节点
3. **建双链**：在正文插入 `[[实体名]]`，并在目标页面建立反向链接区
4. **组织**：按主题/类别写入 `archive/wiki/` 对应子目录（如 `wiki/行业/`、`wiki/项目/`）
5. **MOC**：生成/更新知识框架总览页（根 MOC + 分类 MOC）
6. **保真**：保留原有 wikilink / 标签 / 图谱关系（覆盖 S17）

## 输出

- `archive/wiki/` 下结构化知识 + 双链 + MOC
- 一份改动报告（新增/更新了哪些链接与页面）

## 异常处理

- **重名实体**：同名不同义 → 提示用户确认合并或加限定词
- **孤儿笔记**：无任何链接 → 暂存 `archive/wiki/__inbox` 待归类
- **环检测**：双链成环不阻断，但 MOC 标注

## 配置

- `raw/` 下的 research note 需带 frontmatter（source/url/fetched_at/type/confidence），由 `script/validate_frontmatter.py` 校验
- 路径约定集中在 `script/paths.py`（raw/、wiki/ 位置），禁止硬编码
- 命名规则待 `file-manager` 规则落地后对齐

## 待定（设计阶段）

- 本流水线是否足以吸收 S18（历史调研迁移）→ 若够强，migrate-research 引擎可省
