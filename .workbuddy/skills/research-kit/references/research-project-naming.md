# 调研项目命名与目录结构

> **唯一权威（canonical）**：本文件定义「调研项目目录命名」。通用文件/命名规范见 `file-manager`，
> 但**调研项目目录命名属于 research-kit 职责**，file-manager 不重复定义，只指向本文件。

## 目录格式

```
research/<PID>-<slug>[-<YYYYMMDD>]/
```

- **`<PID>`**：项目 ID。
  - 父项目 = `P` + 两位数字（`P01`、`P02`…）。
  - 子 task = `T<n>[.n]`（`T1` / `T1.1`），与父项目同为 `research/` 下的**平铺目录**。
- **`<slug>`**：英文短横线人读后缀，由 `--name` 的拉丁字符自动派生（`slugify`：去非字母数字、转小写、截断 24 位），或 `--slug` 显式覆盖。
  - 例：`P04-pest`（名含 "PEST" 被保留）、`P02-us-crypto`、`P03-cn-chip`（手动指定）。
- **`[-<YYYYMMDD>]`**：可选日期后缀，**仅观察类 / 快照型项目**带（如 `P01-hotspot-20260919`）；常青主题不加（如 `P02-us-crypto`）。

## 引用键与可改名性

- `<PID>` 是**跨文件稳定引用键**：笔记 frontmatter 写 `project: P03`、状态机 `research-state.yaml` 互相引用都靠它。
- 目录名是「人读标签」，**可改名不影响 PID 引用**（如 `P03-project` → `P03-cn-chip-20260904` 零断链，内部只用 ID 互指）。

## 子 task 单方向派生

- 子 task 只在自己的 `research-state.yaml` 写 `node.parent`；`children` / `depth` 不落盘，由 `load_context` 运行时建图与汇总。
- 新增子 task **不改父文件**（避免双写漂移）。

## 结论 / 监控 / 待办 ID

- 结论 `C-<PID>-<序号>`（如 `C-P02-07`）；监控 `M-<PID>-<nn>`；待办 `Q-<PID>-<nn>`。
- 2026-09-19 迁移前的 `C-20260919-nn` 保留原样，不改号以免断链。

## 创建命令

```bash
# 父项目
python -m script.new_project --id P03 --name "芯片行业深度" --track drill [--slug cn-chip-20260904]
# 子 task（单方向派生，只写子节点的 parent）
python -m script.new_project --id T1 --name "Amazon 平台" --track entry --parent P03
```

- 统一 `python -m` 模块式调用，详见根 `AGENTS.md` **铁律 #8**。
- `--track` 取值（5 选 1，不可混跑）：`drill` / `entry` / `diagnostic` / `inductive` / `scenario`。
- Track 旧值 `A`/`B` 已于 2026-10 的 5-Track 重构废弃，不再接受。
