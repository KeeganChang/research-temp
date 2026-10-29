#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
load_context.py — 研究上下文加载器（跨会话记忆的读取端 · v3 支持多项目 + 多层级 task）

用途
----
每次调研开场先跑这个脚本，把上次沉淀的结论 / 监控指标 / 待办 / 已归档数据集
一次性载入，避免"每次调研都从零开始"。

    python -m script.load_context --list                # 列出所有调研项目（含父/子与 rollup）
    python -m script.load_context                       # 加载全部项目（含 _shared 方法论）
    python -m script.load_context --project P02         # 只加载一个项目（自动带上它的子 task）
    python -m script.load_context --project P01,P02     # 多个（逗号分隔）
    python -m script.load_context --project P02 --json  # 机读 json（供模型直接消费）
    python -m script.load_context --files               # 额外列出可加载的结构化数据文件
    python -m script.load_context --only open           # 只看 status=open 的结论
    python -m script.load_context --no-shared           # 不附加跨项目方法论

项目结构（见 research/README.md）
--------------------------------
    research/<ID>-<slug>/project.yaml         # 项目元信息（目标 / 边界 / 交付物）
    research/<ID>-<slug>/research-state.yaml  # 该项目状态机（含 node 关系层）
    research/_shared/research-state.yaml      # 跨项目方法论（默认附加在最后）
    research/_template/                        # 新项目模板（不参与加载）

多层级 task：单方向派生
------------------------
    子节点只写 node.parent；children / depth 不落盘，由本脚本运行时建图。
    新增子 task = 只建节点 + 写 parent，不改父文件（避免双写漂移）。
    父节点总状态（rollup）由子节点派生，词表复用 project.yaml 的 status：
        paused 具粘性（节点自身 paused → rollup 恒 paused，向上传播）；
        叶子 = 自身 status；有子则按子节点 rollup 聚合：
        任一子 paused→paused；否则任一子 active→active；否则全 done/archived→done。
        父节点自身的 active/done 不参与聚合，避免陈旧手填值掩盖真实进度。
    node.depends_on 当前仅作展示，不做硬阻塞。
    无 node 块的老项目一律视为顶层节点（向后兼容）。

设计约束（与项目铁律一致）
--------------------------
1. **零硬编码路径**：workspace 根由「向上找 AGENTS.md」动态定位。
2. **只读**：本脚本不写任何文件，不改任何 research-state.yaml。
3. **不泄密**：只输出路径与字段名，不输出 secrets 内容。
4. **项目发现靠扫描**，不维护 index 注册表（避免两处漂移）：
   扫 `research/*/project.yaml`，`_template` 除外。
5. **向后兼容**：`research/` 不存在而旧的 `config/research-state.yaml` 还在时，
   退化为 v1 单文件模式并给出告警，提示迁移。

依赖：PyYAML（`pip install pyyaml`）。缺失时给出明确提示而非静默失败。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Windows 控制台默认 GBK，输出含中文/符号会 UnicodeEncodeError。
# 统一强制 UTF-8；失败则降级（不阻断运行）。
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001 - 降级不阻断
    pass

try:
    import yaml
except ImportError:
    sys.exit(
        "[ERROR] 缺少依赖 PyYAML。请先安装：\n"
        "  uv run python -m script.load_context\n"
        "  或  pip install pyyaml"
    )

RESEARCH_DIR = "research"
SHARED_ID = "_shared"
TEMPLATE_DIR = "_template"
LEGACY_STATE_REL = os.path.join("config", "research-state.yaml")
ROOT_MARKER = "AGENTS.md"


def find_workspace_root(start: Path | None = None) -> Path:
    """从 start（默认脚本所在目录）向上找含 AGENTS.md 的目录，即 workspace 根。"""
    here = (start or Path(__file__).resolve().parent).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / ROOT_MARKER).is_file():
            return candidate
    sys.exit(f"[ERROR] 未找到 {ROOT_MARKER}，无法确定 workspace 根（从 {here} 向上查找失败）")


def rel(path: str | Path, root: Path) -> str:
    try:
        return os.path.relpath(str(path), str(root)).replace("\\", "/")
    except ValueError:
        return str(path)


def read_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# ── 项目发现 ───────────────────────────────────────────────────
def discover_projects(root: Path) -> list[dict]:
    """扫 research/*/project.yaml，返回项目清单（_template 除外）。

    没有 index.yaml 注册表是刻意的：注册表会与项目文件两处漂移。
    """
    research_dir = root / RESEARCH_DIR
    if not research_dir.is_dir():
        return []
    projects: list[dict] = []
    for entry in sorted(research_dir.iterdir()):
        if not entry.is_dir() or entry.name == TEMPLATE_DIR:
            continue
        meta_path = entry / "project.yaml"
        state_path = entry / "research-state.yaml"
        if not meta_path.is_file():
            continue
        meta = read_yaml(meta_path)
        state = read_yaml(state_path) if state_path.is_file() else {}
        projects.append(
            {
                "id": str(meta.get("id") or entry.name),
                "dir": entry.name,
                "name": meta.get("name") or entry.name,
                "track": meta.get("track"),
                "status": meta.get("status") or "unknown",
                "question": meta.get("question"),
                "meta": meta,
                "state": state,
                "meta_path": rel(meta_path, root),
                "state_path": rel(state_path, root) if state_path.is_file() else None,
            }
        )
    return projects


def split_projects(projects: list[dict]) -> tuple[list[dict], dict | None]:
    """分离普通项目与 _shared 方法论层。"""
    normal = [p for p in projects if p["id"] != SHARED_ID]
    shared = next((p for p in projects if p["id"] == SHARED_ID), None)
    return normal, shared


def select_projects(projects: list[dict], wanted: str | None) -> list[dict]:
    """按 --project 过滤；支持逗号分隔、大小写不敏感、目录名或 id 均可。"""
    if not wanted:
        return projects
    keys = [k.strip().lower() for k in wanted.split(",") if k.strip()]
    picked: list[dict] = []
    for k in keys:
        hit = [p for p in projects if p["id"].lower() == k or p["dir"].lower() == k]
        if not hit:
            sys.exit(
                f"[ERROR] 未找到项目 {k!r}。可用："
                f"{', '.join(p['id'] for p in projects)}（或用 --list 查看）"
            )
        picked.extend(hit)
    return picked


# ── 关系层：多层级 task（单方向派生）────────────────────────────
def node_of(p: dict) -> dict:
    """取节点关系信息。向后兼容：无 node 块 = 顶层（parent=None）。"""
    st = p.get("state") or {}
    nd = st.get("node") or {}
    parent = nd.get("parent")
    if parent is not None:
        parent = str(parent).strip()
        if parent == "" or parent.lower() in ("null", "none", "~"):
            parent = None
    deps = nd.get("depends_on") or []
    return {"parent": parent, "depends_on": [str(d) for d in deps]}


def build_forest(projects: list[dict]) -> dict:
    """按 node.parent 建图。children / depth 运行时派生，不落盘。

    父不在当前集合内或自指 → 降级为根；父链成环 → 环上节点降级为根（保证递归终止）。
    """
    by_id = {p["id"]: p for p in projects}
    parent_of: dict[str, str | None] = {}
    for p in projects:
        par = node_of(p)["parent"]
        parent_of[p["id"]] = par if (par and par in by_id and par != p["id"]) else None

    # 防环：沿父链上溯，若回到已见节点则把起点降级为根
    for pid in list(parent_of):
        seen, cur = set(), pid
        while cur is not None and cur in parent_of:
            if cur in seen:
                parent_of[pid] = None
                break
            seen.add(cur)
            cur = parent_of.get(cur)

    children: dict[str, list[str]] = {pid: [] for pid in parent_of}
    for pid, par in parent_of.items():
        if par is not None:
            children[par].append(pid)
    for k in children:
        children[k].sort()

    depth: dict[str, int] = {}

    def dep(pid: str) -> int:
        if pid in depth:
            return depth[pid]
        par = parent_of.get(pid)
        depth[pid] = 0 if par is None else dep(par) + 1
        return depth[pid]

    for pid in parent_of:
        dep(pid)

    roots = sorted(pid for pid in parent_of if parent_of[pid] is None)
    return {
        "parent_of": parent_of,
        "children": children,
        "depth": depth,
        "roots": roots,
        "by_id": by_id,
    }


def compute_rollups(projects: list[dict], forest: dict) -> dict[str, str]:
    """父状态由子节点派生。词表复用 project.yaml 的 active/paused/done/archived。

    规则：
    1. **paused 具粘性**：节点自身 status=paused → 其 rollup 恒为 paused（会向上传播）。
       否则「暂停一个中间节点，祖先感知不到」。
    2. 叶子（无子）→ 自身 status。
    3. 有子 → 取子节点 rollup 聚合：任一 paused→paused；否则任一 active→active；
       否则全 done/archived→done；否则回退自身 status。
    4. 父节点自身 status 为 active/done 时不参与聚合（避免陈旧手填值掩盖真实进度）。
    """
    status_of = {p["id"]: (p.get("status") or "unknown") for p in projects}
    memo: dict[str, str] = {}

    def roll(pid: str) -> str:
        if pid in memo:
            return memo[pid]
        own = status_of.get(pid, "unknown")
        if own == "paused":
            memo[pid] = "paused"
            return "paused"
        kids = forest["children"].get(pid) or []
        if not kids:
            r = own
        else:
            subs = [roll(k) for k in kids]
            if any(s == "paused" for s in subs):
                r = "paused"
            elif any(s == "active" for s in subs):
                r = "active"
            elif subs and all(s in ("done", "archived") for s in subs):
                r = "done"
            else:
                r = own
        memo[pid] = r
        return r

    for p in projects:
        roll(p["id"])
    return memo


def descendants(pid: str, forest: dict) -> list[str]:
    """取某节点的全部后代（--project 时自动带上整棵子树）。"""
    out: list[str] = []
    stack = list(forest["children"].get(pid) or [])
    while stack:
        cur = stack.pop(0)
        out.append(cur)
        stack = list(forest["children"].get(cur) or []) + stack
    return out


def dfs_order(forest: dict) -> list[tuple[str, int]]:
    """按父子树的深度优先顺序返回 (id, depth)，供树形渲染。"""
    out: list[tuple[str, int]] = []

    def walk(pid: str, d: int) -> None:
        out.append((pid, d))
        for c in forest["children"].get(pid) or []:
            walk(c, d + 1)

    for r in forest["roots"]:
        walk(r, 0)
    return out


def fmt_block(label: str, value, indent: int = 0) -> list[str]:
    """把可能多行的字符串整理成缩进文本块。"""
    pad = " " * indent
    if value is None:
        return [f"{pad}- {label}: —"]
    text = " ".join(str(value).split())
    return [f"{pad}- {label}: {text}"]


# ── Markdown 渲染 ──────────────────────────────────────────────
def render_project_md(p: dict, root: Path, only: str | None, show_files: bool,
                      depth: int = 0, forest: dict | None = None,
                      roll: dict | None = None) -> list[str]:
    st = p["state"]
    L: list[str] = []
    L.append(f"## 项目 {p['id']} · {p['name']}")
    L.append(
        f"- track: **{p['track'] or '—'}** · status: **{p['status']}** "
        f"· 目录: `research/{p['dir']}/` · state: `{p['state_path'] or '（缺 research-state.yaml）'}`"
    )
    if forest and roll:
        nd = node_of(p)
        kids = forest["children"].get(p["id"]) or []
        par = nd["parent"] or "—（顶层）"
        kid_txt = ", ".join(kids) if kids else "—"
        line = (
            f"- 关系: 层级 {forest['depth'].get(p['id'], 0)} · 父={par} · 子=[{kid_txt}] "
            f"· rollup=**{roll.get(p['id'], '—')}**"
        )
        if nd["depends_on"]:
            line += f" · depends_on={', '.join(nd['depends_on'])}"
        L.append("  " * depth + line)
    if p.get("question"):
        for line in fmt_block("驱动问题", p["question"]):
            L.append(line)
    L.append("")

    focus = st.get("focus") or {}
    if focus:
        L.append("### 焦点")
        L.append(
            f"- topic: **{focus.get('topic') or focus.get('sector') or '—'}** "
            f"(type={focus.get('type', '—')}, status={focus.get('status', '—')})"
        )
        for line in fmt_block("rationale", focus.get("rationale")):
            L.append(line)
        L.append("")

    claims = st.get("claims") or []
    claims = [c for c in claims if not only or c.get("status") == only]
    L.append(f"### 结论台账（{len(claims)} 条）")
    if not claims:
        L.append("- （空）")
    for c in claims:
        L.append(f"- **{c.get('id', '?')}**  [{c.get('status', '?')} / conf={c.get('confidence', '?')}]")
        for line in fmt_block("结论", c.get("statement"), indent=2):
            L.append(line)
        if c.get("tags"):
            L.append(f"  - tags: {', '.join(str(t) for t in c['tags'])}")
        if c.get("derived_from"):
            d = c["derived_from"]
            L.append(f"  - 溯源: 项目 {d.get('project')} / 结论 {d.get('claim')}")
        if c.get("evidence"):
            L.append(f"  - 证据笔记: `{rel(c['evidence'], root)}`")
        if c.get("data"):
            L.append(f"  - 结构化记录: `{rel(c['data'], root)}`")
        if c.get("next_action"):
            L.append(f"  - 触发动作: {c['next_action']}")
    L.append("")

    monitors = st.get("monitors") or []
    L.append(f"### 监控指标（{len(monitors)} 个）")
    if not monitors:
        L.append("- （空）")
    for m in monitors:
        L.append(f"- **{m.get('name', '?')}** = {m.get('last', '?')}  (as_of {m.get('as_of', '?')})")
        L.append(f"  - 阈值: {m.get('threshold', '—')}")
        if m.get("source"):
            L.append(f"  - 来源: `{rel(m['source'], root)}`")
    L.append("")

    queue = st.get("queue") or []
    pending = [q for q in queue if q.get("status") != "done"]
    L.append(f"### 待办队列（{len(pending)} 未完 / 共 {len(queue)}）")
    if not pending:
        L.append("- （空）")
    for q in pending:
        L.append(f"- [{q.get('priority', '?')}] {q.get('id', '?')} · type={q.get('type', '?')}")
        for line in fmt_block("动作", q.get("action"), indent=2):
            L.append(line)
        if q.get("depends_on"):
            L.append(f"  - 依赖: {', '.join(str(d) for d in q['depends_on'])}")
    L.append("")

    datasets = st.get("datasets") or []
    L.append(f"### 已归档结构化记录（{len(datasets)} 份，避免重复抓数）")
    if not datasets:
        L.append("- （空）")
    for d in datasets:
        pth = root / d.get("path", "")
        # 用 ASCII 标记，避免 GBK 控制台下无法编码
        exists = "[OK]" if pth.exists() else "[MISSING]"
        L.append(f"- `{rel(d.get('path', ''), root)}` {exists}")
        L.append(f"  - 覆盖: {d.get('covers', '—')}  (as_of {d.get('as_of', '?')})")
    L.append("")

    if show_files:
        L.append("### 该项目证据文件")
        ev = []
        for c in st.get("claims") or []:
            for key in ("evidence", "data"):
                if c.get(key):
                    ev.append(rel(c[key], root))
        for d in datasets:
            if d.get("path"):
                ev.append(rel(d["path"], root))
        seen, uniq = set(), []
        for e in ev:
            if e not in seen:
                seen.add(e)
                uniq.append(e)
        if uniq:
            L.extend(f"- `{e}`" for e in uniq)
        else:
            L.append("- （无）")
        L.append("")

    return L


def render_md(projects: list[dict], shared: dict | None, root: Path,
              only: str | None, show_files: bool, legacy: bool) -> str:
    shown = projects + ([shared] if shared else [])
    forest = build_forest(shown)
    roll = compute_rollups(shown, forest)

    L: list[str] = []
    title_mode = "（v1 单文件兼容模式）" if legacy else ""
    L.append(f"# 研究上下文快照 {title_mode}")
    L.append("")
    if legacy:
        L.append("> [WARN] 检测到旧的 `config/research-state.yaml`，已进入兼容模式。")
        L.append("> 建议拆到 `research/<PID>/research-state.yaml`（见 research/README.md）。")
        L.append("")

    L.append("## 项目清单")
    L.append(f"- 共 {len(projects)} 个项目" + (f" + 跨项目方法论层（{SHARED_ID}）" if shared else ""))
    for pid, d in dfs_order(forest):
        p = forest["by_id"][pid]
        st = p["state"]
        n_claim = len(st.get("claims") or [])
        n_open = len([c for c in (st.get("claims") or []) if c.get("status") == "open"])
        n_pend = len([q for q in (st.get("queue") or []) if q.get("status") != "done"])
        L.append(
            "  " * d +
            f"- **{p['id']}** {p['name']} — track={p['track'] or '—'}, "
            f"status={p['status']}, rollup={roll.get(pid, '—')}, "
            f"结论 {n_claim}(open {n_open}), 待办 {n_pend}"
        )
    L.append("")

    for pid, d in dfs_order(forest):
        L.extend(render_project_md(forest["by_id"][pid], root, only, show_files, d, forest, roll))

    if shared:
        L.append(f"## 跨项目方法论（{SHARED_ID}）")
        L.append("")
        L.extend(render_project_md(shared, root, only, show_files))

    return "\n".join(L)


# ── JSON 渲染 ──────────────────────────────────────────────────
def project_json(p: dict, only: str | None,
                 forest: dict | None = None, roll: dict | None = None) -> dict:
    st = p["state"]
    out = {
        "id": p["id"],
        "dir": p["dir"],
        "name": p["name"],
        "track": p["track"],
        "status": p["status"],
        "question": p.get("question"),
        "state_path": p["state_path"],
        "focus": st.get("focus"),
        "claims": [c for c in (st.get("claims") or []) if not only or c.get("status") == only],
        "monitors": st.get("monitors") or [],
        "queue": [q for q in (st.get("queue") or []) if q.get("status") != "done"],
        "datasets": st.get("datasets") or [],
    }
    if forest and roll:
        nd = node_of(p)
        out["node"] = {
            "parent": nd["parent"],
            "depends_on": nd["depends_on"],
            "children": forest["children"].get(p["id"]) or [],
            "depth": forest["depth"].get(p["id"], 0),
            "rollup": roll.get(p["id"]),
        }
    return out


def render_json(projects: list[dict], shared: dict | None, only: str | None, legacy: bool) -> str:
    shown = projects + ([shared] if shared else [])
    forest = build_forest(shown)
    roll = compute_rollups(shown, forest)
    out = {
        "schema": "research-context/v3" if not legacy else "research-context/v1-legacy",
        "projects": [project_json(p, only, forest, roll) for p in projects],
    }
    if shared:
        out["shared"] = project_json(shared, only)
    # 注意: YAML 会把 `2026-09-19` 自动解析为 datetime.date 对象，
    # json.dumps 默认无法序列化，必须给 default=str，否则 --json 模式抛 TypeError。
    return json.dumps(out, ensure_ascii=False, indent=2, default=str)


# ── 清单渲染 ───────────────────────────────────────────────────
def render_list(projects: list[dict], shared: dict | None, root: Path) -> str:
    L: list[str] = [f"# 调研项目清单（{root.name}/research）", ""]
    if not projects and not shared:
        L.append(
            "- （无项目）可用 `python -m script.new_project --id P01 --name \"...\" "
            "--track <drill|entry|diagnostic|inductive|scenario>` 新建"
        )
        return "\n".join(L)

    shown = projects + ([shared] if shared else [])
    forest = build_forest(shown)
    roll = compute_rollups(shown, forest)

    L.append("| ID | 名称 | Track | 状态 | Rollup | 父 | 层级 | 结论 | 待办未完 | 更新 |")
    L.append("|----|------|-------|------|--------|----|------|------|----------|------|")
    for pid, d in dfs_order(forest):
        p = forest["by_id"][pid]
        st = p["state"]
        updated = st.get("updated_at") or (p["meta"].get("updated_at") if p["meta"] else "—")
        L.append(
            f"| {'  ' * d}{p['id']} | {p['name']} | {p['track'] or '—'} | {p['status']} "
            f"| {roll.get(pid, '—')} | {node_of(p)['parent'] or '—'} | {d} "
            f"| {len(st.get('claims') or [])} "
            f"| {len([q for q in (st.get('queue') or []) if q.get('status') != 'done'])} "
            f"| {updated} |"
        )
    L.append("")
    L.append("用法：`python -m script.load_context --project <ID>`（自动带上其子 task；默认加载全部）")
    L.append("建子 task：`python -m script.new_project --id T1 --name \"...\" --track <track> --parent <PID>`")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description="加载 research 项目的研究上下文")
    ap.add_argument("--project", metavar="ID", help="只加载指定项目（逗号分隔多个；默认全部；自动含子 task）")
    ap.add_argument("--list", action="store_true", help="只列出项目清单")
    ap.add_argument("--json", action="store_true", help="输出 JSON（供模型消费）")
    ap.add_argument("--files", action="store_true", help="额外列出项目相关的证据/数据文件")
    ap.add_argument("--only", metavar="STATUS", help="只输出指定 status 的结论，如 open / validated")
    ap.add_argument("--no-shared", action="store_true", help="不附加跨项目方法论层（_shared）")
    ap.add_argument("--root", help="手动指定 workspace 根（默认自动上溯查找 AGENTS.md）")
    args = ap.parse_args()

    root = Path(args.root).resolve() if args.root else find_workspace_root()
    projects = discover_projects(root)

    # 兼容：research/ 尚未建立时退回 v1 单文件
    legacy = False
    if not projects:
        legacy_path = root / LEGACY_STATE_REL
        if legacy_path.is_file():
            legacy = True
            projects = [
                {
                    "id": "LEGACY",
                    "dir": "config",
                    "name": "（v1 单文件状态机，待迁移）",
                    "track": None,
                    "status": "unknown",
                    "question": None,
                    "meta": {},
                    "state": read_yaml(legacy_path),
                    "meta_path": rel(legacy_path, root),
                    "state_path": rel(legacy_path, root),
                }
            ]
        else:
            sys.exit(
                f"[ERROR] 既没有 {RESEARCH_DIR}/*/project.yaml，也没有 {LEGACY_STATE_REL}。\n"
                "  新建一个项目：python -m script.new_project --id P01 --name \"...\" "
                "--track <drill|entry|diagnostic|inductive|scenario>"
            )

    # 全量建图一次，用于 --project 时展开子树
    forest_all = build_forest(projects)

    normal, shared = split_projects(projects)
    if args.no_shared:
        shared = None

    if args.list:
        print(render_list(normal, shared, root))
        return 0

    # 显式 --project 时按选择过滤；并自动带上所选节点的全部后代
    if args.project:
        picked = select_projects(projects, args.project)
        ids = {p["id"] for p in picked}
        for pid in list(ids):
            ids.update(descendants(pid, forest_all))
        normal = [p for p in normal if p["id"] in ids]
        shared = next((p for p in picked if p["id"] == SHARED_ID), None)

    if args.json:
        print(render_json(normal, shared, args.only, legacy))
    else:
        print(render_md(normal, shared, root, args.only, args.files, legacy))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
