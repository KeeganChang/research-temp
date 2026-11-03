# research/ — 调研项目层

> 一个调研项目 = 一个目录 = 一份独立的状态机。**不同业务调研互不污染**。

## 为什么有这一层

原先所有调研的结论 / 监控 / 待办都堆在 `config/research-state.yaml` 一个文件里。
同时跑「A股半导体景气链」和「美国加密市场进入」两条业务时，问题就暴露了：
焦点是谁的、监控指标属于哪条线、待办优先级跨项目混排——**上下文互相串味**。

## 结构

```
research/
├── README.md                 # 本文件
├── _template/                # 新项目从这里复制（script.new_project 自动做）
│   ├── project.yaml          #   项目元信息：目标 / 边界 / 交付物
│   └── research-state.yaml   #   状态机骨架：focus / claims / monitors / queue / datasets
├── _shared/                  # 跨项目方法论沉淀（不属于任何单个项目）
│   ├── project.yaml
│   └── research-state.yaml
└── P01-hotspot-20260919/        # 一个项目 = 一个目录（P<编号>-<slug>）
    ├── project.yaml
    └── research-state.yaml
```

## 三层职责（别混）

| 层 | 文件 | 存什么 | 谁能改 |
|----|------|--------|--------|
| 全局受控词表 | `config/types.yaml` `config/tags.yaml` | 分类与标签（跨项目共用） | 人工批准 |
| 项目状态机 | `research/<PID>/research-state.yaml` | 该项目的结论 / 监控 / 待办 / 数据集 | 调研收尾回写 |
| 跨项目方法论 | `research/_shared/research-state.yaml` | 可复用的方法论结论（带 `derived_from` 溯源） | 沉淀时提升 |

## 约定

1. **项目 ID**：`P<两位数字>`（P01、P02…），目录名 `P<编号>-<英文slug>`。
2. **结论 ID**：新结论用 `C-<PID>-<序号>`（如 `C-P02-07`）；2026-09-19 迁移前的 `C-20260919-nn` 保留原样，不改号以免断链。
   监控 `M-<PID>-<nn>`、待办 `Q-<PID>-<nn>` 同理。
3. **笔记归属**：`archive/raw/` 仍按 type 分目录（SSOT 不按项目切分），
   用 frontmatter 的 `project: P01` 标记归属，两边靠路径互指。
4. **证伪不删**：`status: falsified` 的结论保留，留作教训。
5. **项目发现靠扫描**：没有 `index.yaml`，`python -m script.load_context` 扫 `research/*/project.yaml` 得到清单，
   避免注册表与项目文件两处漂移。

> **目录命名的唯一权威**：`<PID>-<slug>[-<YYYYMMDD>]` 的完整规范（引用键、可改名性、子 task 派生、结论/监控 ID）见
> `research-kit/references/research-project-naming.md`；本层只保留与上述职责相关的简要约定。

## 常用命令

```bash
python -m script.load_context --list                 # 列出所有项目
python -m script.load_context                        # 加载全部（含 _shared 方法论）
python -m script.load_context --project P02          # 只加载美国加密项目
python -m script.load_context --project P02 --json   # 机读
python -m script.new_project --id P03 --name "日本加密准入" --track entry   # 从模板新建
```
