---
name: hotspot-tracking
version: 0.1.0
description: A股热点追踪到飞书发布的全流水线 skill：上游用热点猎手/web search 做近一周热点追踪（两段式资金叙事 + Top3 + 活口 + 信号源清单），下游把报告与信号源发布为飞书三件套（多维表格 Base / 文档 Doc / 群 Card 2.0 播报）。覆盖追踪方法论与 lark-cli 发布、im:message.send_as_user 的 OAuth 设备授权、--content 仅接受内联 JSON 的绕过方案、字段删除确认门禁、以及「本地 archive 为 SSOT、飞书为视图」的分层原则。
agent_created: true
---

# hotspot-tracking

把「A股近一周热点追踪」从原始资讯变成一份研究笔记 + 信号源清单，并发布为飞书三件套（多维表格 + 文档 + 群播报卡片）。本 skill 覆盖**完整历程**：上游追踪（§二，详见 `references/hotspot_tracking.md`）+ 下游飞书发布（§三~§五）。底层 lark-cli 命令细节见 `references/lark_commands.md`，发卡片脚本见 `scripts/send_interactive_card.py`，卡片模板见 `assets/card_template.json`，**可交互卡片（点赞/点击计数/投票/下钻）的后端见 `scripts/card_counter.py`**。

## 一、前置与原则

- **SSOT 分层**：本地 `archive/raw/热点/<日期>_热点_<主题>_v1.md` 是唯一可信源；飞书 Base / Doc / 群 都是「分享视图」，不反向写回 archive。
- **lark-cli 路径**：`/c/Users/hello/.workbuddy/binaries/node/cli-connector-packages/lark-cli`（Git Bash）或同目录 `lark-cli.cmd`（PowerShell/Windows）。**不要用 `npx lark-cli`**（npm 无法解析）。
- **身份**：用 `--as user`（以用户本人身份发消息/建群）；bot 身份无 `im:message.send_as_user` 能力。
- **先验证授权**：发卡片前先 `lark-cli auth check --scope "im:message.send_as_user"`；若 `granted` 为空再走设备授权（见 §四）。

## 二、上游：热点追踪处理流程

完整方法论（数据来源、两段式资金叙事、Top3 + 活口、输出契约）见 `references/hotspot_tracking.md`。要点：

1. 用「热点猎手」专家 / `WebSearch` 拉近一周资讯、政策、产业事件 + 板块资金流向。
2. 拆「主升段 → 退潮切换段」两段式资金叙事定调。
3. 排 Top3 主线 + 标活口（持续催化方向）。
4. 与既有研究互证 + 给反方 / 时间维度失效点。
5. 产出：报告 `archive/raw/热点/YYYYMMDD_热点_<主题>_v1.md`（frontmatter `type: 热点`、`project: P01`）+ 信号源清单（标题 / 来源 / URL / 抓取日期 / 关键信号 / 关联项目）。

## 三、下游：飞书发布三件套

### 步骤 1 — 飞书多维表格（Base）存信号源

1. 建表：`lark-cli base +base-create --fields '<schema JSON>'`，首表含字段 `标题(text)/来源(text)/抓取日期(text)/关键信号(text)/关联项目(text)`。
2. 写入：`lark-cli base +record-batch-create --table <table_id> --records '<records JSON>'`。
3. **用户追加调整（常见）**：删独立 URL 列，把链接并入「标题」做成可点击 `[标题](url)`：
   - 更新记录：标题改为 `[原标题](url)`、URL 置空 → `+record-batch-update`。
   - 删字段：`lark-cli base +field-delete --field <field_id>`。**注意 RC=10 确认门禁** → 必须追加 `--yes`。
   - 核验：`+record-list` 确认列数正确、标题均为可点击链接。
4. 记录 `base_token` 与 `table_id`（后续 Doc / 卡片要引用其链接）。

### 步骤 2 — 飞书文档（Doc）导入报告

1. 去 frontmatter：读报告，删除 YAML frontmatter 块。
2. 顶部加交叉引用：贴 Base 链接 +（若有）关联 Doc 链接，便于回跳。
3. 底部标注本地 SSOT 路径（`archive/raw/热点/...`）。
4. 导入：`lark-cli docs +create --doc-format markdown --content @<clean_md> --title "A股近一周热点追踪（YYYY-MM-DD）"`。
   - 注：`docs +create` 的 `--content @file` **可用**（与 im 不同，详见 §五）。
   - 导入前用 `drive +search` 防重复（同一报告只建一份）。
5. 记录 `document_id`。

### 步骤 3 — 新建群 + 发送 Card 2.0 播报卡片

1. 建群：`lark-cli im +chat-create --name "A股热点雷达"`（user 身份自动成为群主+成员）。记录 `chat_id`。
2. 构建卡片：基于 `assets/card_template.json`（schema 2.0，含核心信号 + Top3 + 双按钮跳转 Base/Doc）。填入本期数据。
3. 发送：**必须用 `scripts/send_interactive_card.py`**（见 §五为何）。
   ```
   .venv/Scripts/python.exe scripts/send_interactive_card.py --chat-id <chat_id> --card <card.json> --key hotspot-YYYYMMDD-a
   ```
   脚本用 Python `subprocess` 直接调 node，把 5KB JSON 作为列表参数传入，**规避 `--content` 只接受内联 JSON 的坑**。
   `--idempotency-key` 防止重复发送。
4. 核验返回含 `message_id` 即成功。

### 步骤 3-增强 — 可交互卡片（点赞 / 点击计数 / 投票 / 下钻）

飞书 Card 2.0 **没有原生点赞与点击计数**，要支持必须自建后端 + `callback` 交互。已实现为 `scripts/card_counter.py`（零依赖：stdlib `http.server` + `sqlite3`）。

**卡片布局（增强版）**：主体 = 核心结论 + 研判（所以→行动）+ Top3 主线；中部用 **4 个 `collapsible_panel` 折叠**承载长内容（全量 9 条热点排名表 / 政策事件时间轴 / 资金与个股温度计 / Tier 可信度）；末尾 = **相关数据源链接**区（每条带 Tier 标签 + 🔗打开 + 👍点赞），再接「这份研判对你有用吗」（👍有用/👎存疑）、「下一条主线投票」（机器人/地产/光模块/暂不追，带百分比条形）、「🔍 追一下这条主线」。

**交互机制（四种 callback）**：

| 动作 | value | 后端行为 | 返回 |
|---|---|---|---|
| 点赞 | `{source_id, action:"like"}` | `like_count+1` | `toast` + `card:{type:update}` 原地刷新计数 |
| 打开链接 | `{source_id, action:"open"}` | `click_count+1` | `toast` + `actions:[{type:"open_url"}]` 真打开 |
| 投票/反馈 | `{key, action:"vote"}` | `votes[key]+1` | `toast` + `card:{update}` |
| 追一下 | `{action:"drill", label}` | 写 `queue` 表 | `toast` + `card:{update}` |

后端路由：`POST /feishu/callback`（卡片事件，含 `url_verification` 握手）、`GET /stats`（计数快照）、`GET /queue`、`GET /r/<id>`（302 跳转计数兜底）。

**上线要求**：把服务暴露到公网，并把飞书应用的 **Request URL（事件订阅）** 指向 `<public>/feishu/callback`，卡片交互才会真正生效；否则按钮点了无反应。

**⚠️ 权衡**：`打开链接` 用 callback 才能计数，但**后端未接好时按钮点了打不开**。若要「永远可点」的保守版，把该按钮改回 `behaviors:[{type:"open_url", default_url:<真实URL>}]`（代价：记不到点击数）。

**回写飞书 Base（用户已选）**：每次点赞/打开链接后，后端会**异步（daemon 线程，不阻塞点击响应）**把该数据源的 `点赞数`/`点击数` 写回信号源 Base（即 §三步骤1 那张表），让飞书视图与研究 SaaS 同步。这是 资讯域 SSOT 的一部分（铁律#2：资讯域 lark base 是其 SSOT），不违反「研究域不反向写」。

```bash
# 一次性：给 Base 加「点赞数」「点击数」两列(number) + 建立 url→record_id 映射
.venv/Scripts/python.exe scripts/card_counter.py --ensure-base
# 之后每次点击都会自动 sync；映射缓存到 <skill>/data/base_sync.json
```

- 匹配逻辑：读 Base 记录，从「标题」`[标题](url)` 抽 URL，与 sqlite `sources.url` 比对得到 `record_id`；匹配不到的数据源静默跳过（日志提示）。
- 字段名写死 `点赞数`/`点击数`（number 类型），与 `+record-batch-update` 的 field name 一致。
- **前置**：user token 必须含 base 读写 scope。注意 scope 真实命名是**细粒度**的 `base:field:update/create/delete/read`、`base:record:update/create/delete/read`（**没有 `base:field:write` 这种名字**）；`auth check --scope base:field:write` 会报 `missing`，但 token 其实已有写权限——这是**误报**。权威判断用 `auth status`（列出完整 granted 清单）。要拿全 base 权限用 `--domain base`（含写），`--domain all` 反而**不含 base 写**。

命令：

```bash
.venv/Scripts/python.exe scripts/card_counter.py --seed          # 写入数据源 + 投票键
.venv/Scripts/python.exe scripts/card_counter.py --ensure-base  # 加字段 + 建 url→record 映射
.venv/Scripts/python.exe scripts/card_counter.py --build-card --out <card.json>   # 按当前计数渲染卡片
.venv/Scripts/python.exe scripts/card_counter.py --serve --port 8787              # 起服务
.venv/Scripts/python.exe scripts/card_counter.py --stats                          # 看计数
```

DB 落 `<skill>/data/counter.db`（表 `sources`/`votes`/`queue`）。改数据源编辑脚本顶部 `SOURCES`（含 `tier` 可信度标注）。

## 四、OAuth 设备授权（缺 scope 时）

发送/读写被拒 `missing_scope` 或 `token_missing`（refresh_token expired）时：

1. 取设备码：`lark-cli auth login --domain all --no-wait --json` → 得到 `device_code` + `verification_url`（有效期 600s）。**注意 `--domain all` 不含 base 写权限**；若要 base 写，用 `--domain base`（它含 field/record 的 create/read/update/delete）。也可显式 `--scope base:field:update base:record:update im:message.send_as_user`。
2. 出二维码：`lark-cli auth qrcode "<verification_url>" -o qr.png`，把 URL 与图片一并给用户，请其飞书扫码授权。
3. 用户回复「已授权」后：`lark-cli auth login --device-code <device_code>` 完成登录。
4. 用 `auth status`（列出完整 granted scope 清单）做权威判断；单项可用 `auth check --scope "im:message.send_as_user"` 或 `base:field:update`（**用真实细粒度名，别用 `:write`**）确认 `ok:true`。

> ⚠️ **窄 scope 会覆盖旧 token**：曾因只请求 `im:message.send_as_user` 做设备授权，导致原带 base 权限的 token 被替换、随后 base 操作报 `refresh_token expired / token_missing`。故**一次把本次要用的所有 scope 请求齐**（如 `--domain base --scope im:message.send_as_user`）。

> 坑：`auth login --device-code` 会阻塞轮询；若返回「device_code is invalid」，多半是过期/已被消费——以 `auth status` 结论为准，授权成功则 token 已附带 scope。

> 🔑 **scope 名陷阱（实测）**：`auth check --scope base:field:write` 永远报 `missing`，因为**不存在这个 scope 名**。base 真实权限名是 `base:field:create/read/update/delete`、`base:record:create/read/update/delete`（im 同理 `im:message.send_as_user` 是真实名）。判断「有没有写权限」应查 `base:field:update` / `base:record:update` 是否 `granted`，或直接看 `auth status` 的完整清单。别被 `:write` 误报带偏而反复重新授权。

## 五、铁律级坑（本项目反复踩）

1. **`im +messages-send --content` 只接受内联 JSON 字符串**——`@file` 与 `-`(stdin) 在本版本均不支持，会报 `is not valid JSON`。5KB 卡片含中文与单引号，shell 引号无法安全传递。**一律用 `scripts/send_interactive_card.py`**（Python subprocess 列表传参，绕开引号）。
2. **node 二进制路径**：脚本直调 `C:\Users\hello\.workbuddy\binaries\node\versions\22.22.2-6\node.exe` + `...\node_modules\@larksuite\cli\scripts\run.js`，**绕过 lark-cli 那层 bash 包装的 `exec node`（该包装偶发 Permission denied / fork 失败）**。`22.22.2-x` 是托管运行时版本号，重装后会变——若脚本报 `node.exe 不存在`，到 `binaries/node/versions/` 下确认当前版本号再改。
3. **环境抖动（bash fork / node Permission denied）是瞬时的**：命令无输出/异常退出时直接重试，多数能过。
4. **`+field-delete` 有 RC=10 确认门禁**：必须加 `--yes`，否则 hint「add --yes to confirm」。
5. **Doc 用 `@file`，im 不能用 `@file`**——两者不一致，别套用。
6. **SSOT 不反向写**：飞书视图里不要出现「再回写 archive」的流程。
7. **卡片 schema 一次只报一个错**：失败形如 `Failed to create card content, ErrPath: ROOT -> body -> elements -> [8](tag: interactive_container); ErrMsg: invalid border color: neutral-100`。修完再发会暴露下一个 → **修的时候把所有可疑枚举一次性清掉**，别逐个试。
8. **Card 2.0 枚举踩雷清单（实测）**：
   - `div` **不支持 `elements` 嵌套**（那是容器 / 1.0 写法）→ 小标题直接用 `{"tag":"markdown"}` 元素。
   - `border_color` 无 `neutral-100` → 删掉该键走默认边框。
   - button `type` 无 `secondary` → 用 `default`。
   - `collapsible_panel.header.background_color` 不接受 `grey-100` → 删掉该键。
   - **已验证可用**：`border_color: blue-100`、`background_style: blue-50`、button `type: default` / `primary_filled`、`interactive_container` 的 `has_border/corner_radius/padding/vertical_spacing/margin`、`collapsible_panel` 的 `expanded/header.title/header.icon`。
9. **卡片体积**：pretty-print 约 25KB，发送前压成紧凑 JSON（`separators=(',',':')`，约 12KB）更稳。
10. **`base +record-list --format json` 的真实结构**：返回 `{data:{data:[[...行数组...]], record_id_list:[...], fields:{...}}}`。**行是数组（列序：标题 / 抓取日期 / 关联项目 / 来源 / 点赞数 / 点击数 / 关键信号），`record_id` 在平行的 `record_id_list` 里（按索引对齐），不在行内**。别用 `data.items[].fields` 解析（那是另一种格式，本连接器不返回）。从「标题」`[标题](url)` 抽 URL 用正则 `\]\(([^)]+)\)`。
11. **`base +field-list --format json` 的真实结构**：返回 `{data:{fields:[{id,name,type,...}]}}`，字段名用 `name`（**不是 `field_name`**）。判断字段是否已存在要匹配 `name`。
12. **`+field-create` / `+record-batch-update` JSON 格式**（实测）：
    - 建字段：`--json '{"name":"点赞数","type":"number"}'`（number/text/select 等；select 要带 `options`）。
    - 批量更新：`--json '{"update_records":{"recA":{"点赞数":1,"点击数":2}}}'`，数值字段直接写数字（number→`12.5`，text→`"x"`）。
13. **scope 名与「误报」**：见 §四「scope 名陷阱」——`base:field:write` 不存在，写权限查 `base:field:update`；`auth status` 才是完整清单。

## 六、自检清单

- [ ] 报告 frontmatter 已剥离、顶部有 Base 链接、底部有本地路径
- [ ] Base 列数正确、标题可点击、URL 列已删（如用户要求）
- [ ] `auth check` 显示 `im:message.send_as_user` 已 granted
- [ ] 卡片用脚本发送、返回含 `message_id`
- [ ] 可交互卡片：`card_counter.py` 后端已部署 + 应用 Request URL 指向 `/feishu/callback`（否则按钮点了无反应）
- [ ] Base 回写：已跑 `--ensure-base`（加「点赞数/点击数」列 + 建 url→record 映射）；`auth status` 确认 token 含 `base:field:update`/`base:record:update`/`im:message.send_as_user`（注意别用 `:write` 误报）
- [ ] 三件套链接已记录到 `docs/CHANGELOG.md` 与当日 memory
