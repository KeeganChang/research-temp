# 热点卡片交互激活：部署 + 飞书回调配置

> 目标：让飞书卡片的 👍 点赞 / 🔗 打开点击 真正落库（sqlite），并实时回写飞书 Base 的「点赞数 / 点击数」两列。
> 适用范围：`hotspot-tracking` skill 的 `card_interactive_hotspot.json` + `card_counter.py`。

---

## 已完成（本次已交付，无需你再做）

- 卡片按钮 `source_id` 已对齐后端（`src1/src2/src3`），「🔗 打开」已从 `open_url` 改为 `callback(action=open)`，点击也能计点击。
- **当前生效卡片 = v6（按 HTML 设计稿样式重做）**，已发送到「A股热点雷达」群（`oc_87bcc6fd9094d88ccca05dee9de329c5`，当前账号/租户新建群），message_id `om_x100b6138ceda58a4df2eaa5bf28ba59`（2026-10-27 23:49:21）。
- 群内历史冗余卡片处理（2026-10-27 撤回执行结果）：
  - v5 `om_x100b61382da76ca8ddb1b311f398599`（布局差异）：✅ 已成功撤回（`ok:true`）。
  - 最旧 `om_x100b6348324c3ca8b39cde849afc6ce`（source_id 错误）：❌ API 撤回失败，报 `230002 Bot/User can NOT be out of the chat`——该卡由旧账号/旧租户（`cli_aa3f85d67375dbb5`）发出，当前 `my-buddy` 身份不在其会话上下文，API 无法撤回。**须在飞书 App 内由群主手动删除**（群主可删任意消息，不受租户/窗口限制）。
  - 撤回命令（高风险写操作，需用户显式确认 `--yes`）：`lark-cli im messages delete --message-id <id> --yes --as user`。
- `card_counter.py` 后端逻辑已通过本地端到端验证（`url_verification` 校验、`card.action.trigger` 点赞/打开回调、sqlite 计数落库）。

---

## 你需要执行的 4 步（沙箱无法暴露公网，须在你本机/服务器做）

### 1. 本地起服务

```bash
cd <workspace>/.workbuddy/skills/hotspot-tracking/scripts
python card_counter.py --seed        # 首次：写入 3 条数据源 + 投票键
python card_counter.py --serve --port 8787
# 看到 "serving on http://127.0.0.1:8787" 即就绪
```

> 服务端点：`POST /feishu/callback`（飞书卡片回调）、`GET /stats`（看计数）、`GET /r/<id>`（302 兜底计数）。

### 2. 暴露公网（二选一，都自动给 HTTPS）

飞书事件订阅的 Request URL **必须是 HTTPS**。以下两种都自带证书：

- **cloudflared**（推荐，免登录）：
  ```bash
  cloudflared tunnel --url http://127.0.0.1:8787
  # 输出里找 https://xxxx.trycloudflare.com
  ```
- **ngrok**：
  ```bash
  ngrok http 8787
  # 输出里找 https://xxxx.ngrok-free.app
  ```

记下这个 `https://xxxx` 公网地址，下一步要用。服务器部署同理，用 Nginx/Caddy 反代到 8787 并配证书即可。

### 3. 飞书开放平台 → 后台字段 / 权限清单

完整清单见 **`references/feishu_console_checklist.md`**（后台逐项填法 + 权限表 + 错误码排查）。要点速记：

1. **应用能力** → 添加「机器人」能力，并确认「交互卡片」已开启；把机器人加入「A股热点雷达」群。
2. **开发配置 → 事件与回调 → 回调配置**（⚠️ 是"回调配置"页签，不是"事件配置"）→ 订阅方式选 **Webhook** → **请求地址**填 `<你的公网https>/feishu/callback`。保存时飞书发 `url_verification` 校验，后端已正确返回 `challenge`，状态变「已验证」。
3. **已订阅的回调** → 添加 **`card.action.trigger`（卡片回传交互）**。
   - ⚠️ **卡片点击回调本身不需要任何 API 权限**（官方：权限要求「暂无」）。不要被"权限不足"误导去开 `im:message`——那是发消息用的，与卡片点击无关。
   - 回写 Base 才需要 base 细粒度权限（`base:record:update` 等），上一轮已配通。
4. **应用发布 → 版本管理与发布 → 创建版本 → 发布/申请发布**。**不发布点按钮会报 200340**（应用未配置卡片回调）。企业应用可能需管理员审核。

### 4. 验证激活

1. 在群里打开新卡片，**点 👍 赞** 或 **🔗 打开**。
2. 本地终端看日志：`[sync] base updated ... like=N click=M` 表示计数已回写 Base。
3. 浏览器开 `<公网https>/stats`，看 `sources` 里 `src1/src2/src3` 的 `like/click` 是否 +1。
4. 飞书 Base「A股热点追踪-原始信号源」的「点赞数 / 点击数」两列是否同步更新。

---

## 常见问题

- **点了没反应 / 计数不变**：八成是 Request URL 没配或没加「卡片回传交互」事件；先查 `/stats` 有没有新记录。
- **保存 Request URL 报校验失败**：确认本地 `--serve` 正在跑且公网地址可达；公网地址末尾要带 `/feishu/callback`。
- **Base 不回写但 /stats 在涨**：sync 是 best-effort 后台线程，多半是 base 写权限/`BASE_TOKEN` 问题，单独跑 `python card_counter.py --ensure-base` 看报错。
- **想本地自测不暴露公网**：用 `python card_counter.py --build-card --out /tmp/x.json` 确认卡片渲染；HTTP 链路可用 `http_verify.py`（仓库内回归脚本）在 loopback 自测。

## 停止 / 回滚

- 停服务：`Ctrl+C` 关掉 `--serve` 进程；飞书侧把 Request URL 清空即停止回调。
- 回滚卡片：删除新卡、重新发送旧版（或把 `card_interactive_hotspot.json` 的按钮改回 `open_url` + `source_id: s1/s2/s3` 的旧形态）。
