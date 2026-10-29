# lark-cli 命令速查（feishu-hotspot-publish 配套）

本文件记录本项目实测可用的 lark-cli 命令。lark-cli 二进制：

- Git Bash：`/c/Users/hello/.workbuddy/binaries/node/cli-connector-packages/lark-cli`
- PowerShell/Windows：`C:\Users\hello\.workbuddy\binaries\node\cli-connector-packages\lark-cli.cmd`

**不要用 `npx lark-cli`**（npm 无法解析该可执行文件）。

通用约定：输出建议重定向到文件再 Read，因 shell 偶发 stdout 被吞 / 段错误。

---

## 1. 授权（auth）

```bash
# 查看当前身份与已授权 scope
lark-cli auth status
lark-cli auth status --as user        # 注意：status 不带 --as，会报 unknown flag

# 检查某个 scope 是否已授予（发送卡片前必查）
lark-cli auth check --scope "im:message.send_as_user"

# 缺 scope 时走设备授权（返回 device_code + verification_url）
lark-cli auth login --scope "im:message.send_as_user" --no-wait --json > auth_device.json

# 生成二维码 PNG 给用户扫码
lark-cli auth qrcode "<verification_url>" -o qr.png

# 用户扫码授权后，完成登录（会阻塞轮询，可能返回 device_code invalid，以 auth check 为准）
lark-cli auth login --device-code <device_code>
```

注意：`auth login --device-code` 会阻塞直到授权或超时；若返回
`authorization failed: The device_code is invalid`，通常是因为已过期/已被消费，
此时用 `auth check` 复核——若 `granted` 非空说明授权其实已生效。

---

## 2. 多维表格（base）

```bash
# 建表（首表 schema）。字段类型：text / number / single_select / url 等
lark-cli base +base-create --fields '[
  {"name":"标题","type":"text"},
  {"name":"来源","type":"text"},
  {"name":"抓取日期","type":"text"},
  {"name":"关键信号","type":"text"},
  {"name":"关联项目","type":"text"}
]'

# 取 table_id（建表返回或 field-list）
lark-cli base +field-list --base <base_token>

# 批量写记录
lark-cli base +record-batch-create --table <table_id> --records '[ ... ]'

# 批量更新（如把链接并入标题）
lark-cli base +record-batch-update --table <table_id> --records '[ ... ]'

# 删除字段（RC=10 确认门禁，必须 --yes）
lark-cli base +field-delete --base <base_token> --field <field_id> --yes

# 核验
lark-cli base +record-list --table <table_id>
```

Base URL：`https://my.feishu.cn/base/<base_token>`

---

## 3. 文档（docs）

```bash
# 导入 Markdown（--content @file 可用）
lark-cli docs +create --doc-format markdown --content @clean_report.md \
  --title "A股近一周热点追踪（YYYY-MM-DD）"

# 防重复：导入前搜索是否已有同名文档
lark-cli drive +search --query "A股近一周热点追踪"
```

Doc URL：`https://my.feishu.cn/docx/<document_id>`

---

## 4. 群与消息（im）

```bash
# 建群（user 身份自动成为群主 + 成员）
lark-cli im +chat-create --name "A股热点雷达"

# 发送交互卡片 —— 见 §5 的坑
lark-cli im +messages-send --chat-id <chat_id> --msg-type interactive \
  --content '<inline_json>' --idempotency-key hotspot-YYYYMMDD-a --as user
```

Chat URL：`https://my.feishu.cn/client/chat/chatter/chat/...`（入群链接由建群返回）

---

## 5. 发送交互卡片的坑（重点）

`im +messages-send --content` 在本版本 **只接受内联 JSON 字符串**：

- `--content @file.json` → 报 `is not valid JSON: @file.json`
- `--content -`（stdin） → 报 `is not valid JSON: -`
- 必须传内联 JSON；但卡片 5KB、含中文与单引号，shell 引号无法安全传递。

**解决方案 A（🏆 2026-10-11 起首选，pwsh 7）**：pwsh 7.6.6 已安装
（`C:\Users\hello\AppData\Local\Microsoft\WindowsApps\pwsh.exe`，Store 版入口），
`$PSNativeCommandArgumentPassing='Standard'` 后可直接把 JSON 变量传给
`--content`，含 `-68.6` 等陷阱字符也不会被误解析为 flag；且 pwsh 不经
Git Bash fork，零抖动：

```powershell
$PSNativeCommandArgumentPassing = 'Standard'
Set-Location "C:\Users\hello\.workbuddy\binaries\node\cli-connector-packages"
$json = Get-Content -Raw "<card.json 绝对路径>"
& "C:\Users\hello\.workbuddy\binaries\node\versions\22.22.2-6\node.exe" `
  "...\node_modules\@larksuite\cli\scripts\run.js" `
  im +messages-send --chat-id <chat_id> --msg-type interactive `
  --content $json --idempotency-key <key> --as user *> result.txt
```

**解决方案 B**：`--content "@./卡文件"`（JSON 先复制到 cli-connector-packages
cwd），CLI 自己读文件，同样绕开 shell 传参。

**解决方案 C（遗留）**：`scripts/send_interactive_card.py`（Python subprocess
列表参数直传）。注意 Python 包 node 在本机曾触发 0xC0000005 段错误，A/B 优先。

---

## 6. 环境抖动应对

bash fork / node Permission denied 是**瞬时**故障：

- 命令无输出或异常退出 → 直接重试，多数能过。
- 写结果到文件再 Read，避免依赖 stdout。
- 调用 node 直传列表参数比经由 bash 包装更稳。

## 7. pwsh 7（2026-10-11 安装后实测，推翻旧限制）

- `lark-cli im --help` 在 Git Bash **必挂起**（TTY/分页器问题）→ pwsh 7 下**正常输出**。
  完整命令面首次可见：shortcut 远不止报错列表里的 6 个——还有 `+chat-create /
  +chat-list / +chat-messages-list / +chat-search / +feed-* / +flag-* /
  +message-read-users / +messages-resources-download / +threads-messages-list` 等；
  raw API 有 `messages delete/forward/merge_forward/patch/read_status/urgent_*`、
  `images create`、`files create` 等。风险分级 read|write|high-risk-write，
  high-risk 需 `--yes`。
- 注意：`+messages-edit` 是 **bot only**（edit API 不收 user token）；user 身份
  发错的消息用 `im messages delete --message-id <om_...> --yes --as user` 撤回重发。
- pwsh 调 node 不经 fork，`CreateProcessW errno 13` / 段错误不再出现（实测推送 +
  撤回全绿）。
- `--help` 挂起的根因是 Git Bash 交互环境，与 lark-cli 本身无关。
