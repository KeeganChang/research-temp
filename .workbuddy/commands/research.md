---
description: 启动 Research Kit 可控调研全流程（新建 → 按门禁推进 → 回写状态机）。只需单步操作时改用 /research-init（新建立项）或 /research-load（续做中断任务）。
argument-hint: "[项目名 或 驱动问题]"
---

你是 Research Kit。请按以下步骤完成一次可控调研（入口与按需查阅指引见 `.workbuddy/skills/research-kit/SKILL.md`；门禁总纲见 `.workbuddy/skills/research-kit/references/skills/research-core/SKILL.md`）。

> 只需**新建**任务 → 用 `/research-init`；只需**接回中断**任务 → 用 `/research-load`。本命令跑完整条链路。

1. **立项**（等价 `/research-init`）：先运行 `uv run python -m script.load_context --list` 确认是否为续做。新项目则与用户确认「驱动问题 + scope_in/out + 交付物」（门禁 G1），再执行
   `uv run python -m script.new_project --id <PID> --name "..." --track <drill|entry|diagnostic|inductive|scenario>`。
2. **选线**（门禁 G2）：依据**任务描述**套 `references/ROUTING.md` 决策树五选一，不写死；判定结果写回 `project.yaml` 的 `track` 仅作续做记录。同一条链不可混跑，跨 Track 用父子 task 串起。
3. **采集**（G3）：按所选 Track 走 `research-track-<track>` 骨架；**仅路由 `enabled: true` 的 method**（如 `method-topdown` 景气链、`method-ecommerce-ops` 电商诊断，默认关闭，须显式启用）。
4. **成稿/校验/回写**（G4/G5/G6）：反方 ≥5 条含 1 条时间维度 + 关键口径登记 + claim↔证据互指 → 标 `confidence`/`status` → 回写 `research/<PID>/research-state.yaml` 并设 monitor 阈值。
5. **交付**：结构化结论进 research-state；叙述性报告先进 `output/`，确认后移 `archive/raw/<type>/` 并带 frontmatter。

本次用户输入（作为驱动问题或项目主题）： $1
