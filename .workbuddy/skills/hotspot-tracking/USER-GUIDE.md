# hotspot-tracking 使用手册

把「A股近一周热点追踪」做成一份研究笔记 + 信号源清单，并一键发布为飞书三件套：多维表格 + 文档 + 群播报卡片。本 skill 覆盖**完整历程**（上游追踪 + 下游发布）。

## 什么时候用

- 想跟一下「本周 A股在炒什么 / 近一周热点」。
- 已有或想产出一份 `archive/raw/热点/` 下的热点报告，并推到飞书做分享视图。
- 想建一个飞书群，用交互卡片播报本期热点 Top3。

## 全流程

### 上游：热点追踪

1. 用「热点猎手」专家或 web search 拉近一周资讯、政策、产业事件 + 板块资金流向。
2. 按「主升段 → 退潮切换段」两段式资金叙事定调（避免只列涨跌幅）。
3. 排 Top3 主线 + 标活口（持续催化方向），并与既有研究互证、给反方。
4. 产出：
   - 报告 `archive/raw/热点/YYYYMMDD_热点_<主题>_v1.md`（frontmatter `type: 热点`、`project: P01`）。
   - 信号源清单：每条 `标题 / 来源 / URL / 抓取日期 / 关键信号 / 关联项目`（供飞书 Base 使用）。

> 详细追踪方法论见 `references/hotspot_tracking.md`。

### 下游：飞书发布三件套

#### 第 1 步 · 多维表格存信号源

- 建表（首表字段：`标题/来源/抓取日期/关键信号/关联项目`）。
- 写入记录。
- 常见追加调整：删掉独立 URL 列，把链接合并进「标题」做成 `[标题](url)` 可点击链接。
  - 删字段有确认门禁，必须加 `--yes`。

#### 第 2 步 · 文档导入报告

- 去掉报告顶部 YAML frontmatter。
- 顶部加交叉引用（Base 链接），底部标注本地 SSOT 路径。
- 导入：`lark-cli docs +create --doc-format markdown --content @clean.md --title "..."`
  - 文档导入的 `@file` 是**可用**的（和发卡片不同）。

#### 第 3 步 · 建群 + 发卡片

- 建群：`lark-cli im +chat-create --name "A股热点雷达"`。
- 用 `assets/card_template.json` 填好本期数据。
- **必须用脚本发卡片**（绕开 `--content` 只接受内联 JSON 的坑）：

  ```bash
  .venv/Scripts/python.exe scripts/send_interactive_card.py \
    --chat-id <chat_id> --card card.json --key hotspot-YYYYMMDD-a
  ```

- 返回含 `message_id` 即成功。

## 缺权限怎么补

发卡片报 `missing_scope: im:message.send_as_user` 时：

1. `lark-cli auth login --scope "im:message.send_as_user" --no-wait --json` 取设备码。
2. `lark-cli auth qrcode "<url>" -o qr.png` 生成二维码，扫码授权。
3. 授权后 `lark-cli auth login --device-code <device_code>` 完成登录。
4. `lark-cli auth check --scope "im:message.send_as_user"` 确认已授予，再发。

## 重要原则

- **本地 `archive/` 是唯一可信源（SSOT）**，飞书只是视图，不要反向写回。
- 环境偶发卡顿（bash fork / node 权限报错）是瞬时的，重试通常能过。
- 发完把三个链接记进 `docs/CHANGELOG.md` 和当日 memory。

## 文件导航

| 文件 | 作用 |
|------|------|
| `SKILL.md` | AI 执行流程（追踪 + 发布）与坑位 |
| `references/hotspot_tracking.md` | 上游热点追踪方法论 |
| `references/lark_commands.md` | lark-cli 命令速查 |
| `scripts/send_interactive_card.py` | 发交互卡片（绕开引号坑） |
| `assets/card_template.json` | Card 2.0 卡片模板（带占位符） |
