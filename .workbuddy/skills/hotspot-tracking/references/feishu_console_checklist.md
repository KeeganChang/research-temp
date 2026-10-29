# 飞书开放平台后台配置清单（热点卡片交互激活）

> 目的：让飞书卡片的 👍 点赞 / 🔗 打开点击 真正回传到你的 `card_counter.py` 后端并落库。
> 适用范围：`hotspot-tracking` skill 的 `card_interactive_hotspot.json` + `card_counter.py`（Webhook 模式）。
> 配合阅读：`references/deploy_callback.md`（本地起服务 + 暴露公网）。

## 一句话结论

卡片点击要落库，**必须在飞书开放平台给你的应用配「卡片回传交互」回调地址 + 发布新版本**。
⚠️ **卡片回传交互 `card.action.trigger` 本身不需要任何额外 API 权限**（飞书官方：权限要求「开启任一权限即可 / 暂无」）。不要被"权限不足"误导去乱开 `im:message`——那是发消息用的，与卡片点击回调无关。

---

## 后台 4 步填法

### ① 应用能力
- 位置：应用详情 → **添加应用能力** → **机器人**
- 动作：添加「机器人」能力（必须，否则无法收发卡片）
- 进入机器人设置 → 确认「**交互卡片**」开关已开启（Interactive Card）
- 把机器人加入「A股热点雷达」群（oc_87bcc6fd9094d88ccca05dee9de329c5，当前账号/租户新建群），否则它在群里收不到交互

### ② 回调配置（核心，Webhook 模式）
- 位置：**开发配置 → 事件与回调 → 回调配置**（注意是"**回调配置**"页签，**不是**"事件配置"页签）
- 订阅方式：选 **Webhook**
- **请求地址(Request URL)**：`https://<你的公网地址>/feishu/callback`
  - 保存时飞书会发 `url_verification` 挑战；后端已正确返回 `challenge` → 状态变「已验证」
- **已订阅的回调** → 添加回调 → 勾选 **`card.action.trigger`（卡片回传交互）**
- ⚠️ 这是「回调」不是「事件」：在"事件配置"里加 `card.action.trigger` **收不到按钮点击**。两者是分开的页签。

### ③ 权限（scope）清单
| 用途 | 所需权限 | 是否必须 |
|---|---|---|
| 卡片回传交互 `card.action.trigger` | 无（官方：权限要求「暂无」） | **不需要 API 权限** |
| 机器人收发卡片 | 由"机器人"应用能力内含 | 添加能力即得 |
| 回写飞书 Base「点赞数/点击数」 | 细粒度 `base:record:read` / `base:record:update` / `base:field:read` / `base:field:create`（上一轮已配通） | 仅回写 Base 时需要 |
| `lark-cli event consume` 长连接消费 | `im:message:readonly` | **仅走长连接模式才需，本方案不需要** |

- 若发布版本时管理员要求声明权限，按需勾选即可，**不影响卡片回调本身生效**。
- 卡片**发送**只需发送权限（`lark-cli im +messages-send --as user` 用的是用户身份，不依赖应用级发消息 scope）。卡片**点击**才需要上面的回调配置。

### ④ 发布（最易漏、致命）
- 位置：**应用发布 → 版本管理与发布 → 创建版本**
- 填版本号 / 说明 → **发布** 或 **申请发布**
- **不发布，点按钮会报 `200340`（应用未配置卡片回调地址）**
- 企业自建应用可能需管理员审核，审核通过才生效

---

## 验证是否激活

1. 群里打开新卡片，点 👍 赞 或 🔗 打开
2. 本地终端看 `/stats`：`sources` 里 `src1/src2/src3` 的 `like/click` 是否 +1
3. 看飞书是否弹错：
   - **200340** → 回调地址未配 / 未发布新版本（最常见）
   - **200342 / 200343** → 飞书无法访问你填的 Request URL（公网不可达 / 证书问题；用 cloudflared/ngrok 自带 HTTPS）
4. 看 `[sync] base updated ... like=N click=M` 日志 + Base「点赞数/点击数」两列是否同步

---

## 常见坑（来自飞书官方）

- **卡片发出去正常、但点了没反应** = 回调没配 / 没发布。卡片发送只需要发送权限；点击才需要回调 + 发布版本。
- **200340**：应用未配置卡片回调地址或地址无效 → 必须创建并发布最新版本。
- **200342/200343**：飞书连不上 Request URL → 公网地址要 HTTPS 且可达。
- 回调响应必须在 **3 秒内**返回（`card_counter.py` 已满足），且**不能用 3xx 重定向**应答卡片回调（我们用即时 JSON 响应，符合）。

---

## 替代方案（不想暴露公网时）

若你不想把本机服务暴露公网，可改用 **`lark-cli` 长连接**消费卡片事件（无需公网 URL）：
```
lark-cli event consume card.action.trigger --as bot --max-events 1
```
但这需要改写 `card_counter.py` 的消费逻辑（从"收 HTTP 回调"改为"读 lark-cli 事件流"），且需 `im:message:readonly` 权限自动拉取 `card_content`。当前 `card_counter.py` 已按 Webhook 模式实现，走上面的 ①–④ 即可，**无需改用长连接**。
