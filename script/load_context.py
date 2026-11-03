#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
load_context.py — 研究上下文加载器（跨会话记忆的读取端 · v3 支持多项目 + 多层级 task）

用途
----
每次调研开场先跑这个脚本，把上次沉淀的结论 / 监控指标 / 待办 / 已归档数据集
/ 已发布视图（views）一次性载入，避免"每次调研都从零开始"。

    python -m script.load_context --list                # 列出所有调研项目（含父/子与 rollup）
    python -m script.load_context                       # 加载全部项目（含 _shared 方法论）
    python -m script.load_context --project P02         # 只加载一个项目（自动带上它的子 task）
    python -m script.load_context --project P01,P02     # 多个（逗号分隔）
    python -m script.load_context --project P02 --json  # 机读 json（供模型直接消费）
    python -m script.load_context --files               # 额外列出可加载的结构化数据文件
    python -m script.load_context --only open           # 只看 status=open 的结论
    python -m script.load_context --no-shared           # 不附加跨项目方法论
    python -m script.load_context --lint                # 只读自检状态机（有严重项退出码 1）
    python -m script.load_context --lint --json         # 自检结果机读
    python -m script.load_context --list --all          # 连带显示 archived 项目（默认隐藏）

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

呈现层视图 views（单一 schema）
--------------------------------
    `research-state.yaml` 的 `views` 登记已发布到 lark 的交付物，字段固定：
        kind          lark_doc | lark_sheet | lark_slides（必填）
        title         视图标题（必填）
        url           http(s) 链接（必填，唯一可点入口）
        token         lark 对象裸 token，不带 `docx/` `sheets/` 前缀（类型由 kind 表达）
        role          在交付链里的角色：人读主交付 / 复杂计算附件 …
        sync_direction 只接受 `local_to_lark`（lark 不是 SSOT，反向回写一律改本地再重推）
        generated_by  生成方式（lark-cli / 脚本名）
        pushed_at     最近推送日期，用于判断视图是否过期
        tabs          仅 lark_sheet：页签清单
        note          补充说明（同步步骤 / 降级理由）
    `--lint` 会对旧字段名（type / document_id / spreadsheet_token）直接报 ERROR。

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
ARCHIVE_DIR = "_archive"
LEGACY_STATE_REL = os.path.join("config", "research-state.yaml")
ROOT_MARKER = "AGENTS.md"

# ── --lint 校验用受控词表 ──────────────────────────────────────
# 与 project.yaml 的 track / claim status 词表保持一致（改这里需同步模板与文档）。
VALID_TRACKS = ("drill", "entry", "diagnostic", "inductive", "scenario")
CLAIM_STATUS = ("open", "validated", "falsified")
STATE_SEGMENTS = ("focus", "claims", "monitors", "queue", "datasets")

# ── views（呈现层视图）口径 ───────────────────────────────────
# 2026-11-04 统一：state 里只允许下面这一套字段名，旧写法由 lint 报错推动迁移。
#   kind / title / url / token / role / sync_direction / generated_by / pushed_at / tabs / note
# 铁律：lark 不是 SSOT —— sync_direction 只接受单向 local_to_lark。
VIEW_KINDS = ("lark_doc", "lark_sheet", "lark_slides")
VIEW_SYNC = ("local_to_lark",)
VIEW_REQUIRED = ("kind", "title", "url")
# 旧字段 → 现行字段（出现即报 ERROR，附迁移提示，避免三套写法继续扩散）
VIEW_LEGACY_KEYS = {
    "type": "kind",
    "document_id": "token",
    "spreadsheet_token": "token",
    "doc_id": "token",
}
STALE_DAYS = 90  # E3：命中率成熟期默认 90 天，超此未更新给提示


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
def discover_projects(root: Path, include_archive: bool = False) -> list[dict]:
    """扫 research/*/project.yaml，返回项目清单（_template 除外）。

    没有 index.yaml 注册表是刻意的：注册表会与项目文件两处漂移。
    include_archive=True 时额外扫 `research/_archive/` 下的已归档项目（供 --lint 全量自检）。
    """
    research_dir = root / RESEARCH_DIR
    if not research_dir.is_dir():
        return []
    projects: list[dict] = []
    scan_dirs = [research_dir]
    if include_archive and (research_dir / ARCHIVE_DIR).is_dir():
        scan_dirs.append(research_dir / ARCHIVE_DIR)
    for base in scan_dirs:
        projects.extend(_scan_dir(base, root))
    # 稳定排序：先按目录名，保证输出可复现
    projects.sort(key=lambda p: p["dir"])
    return projects


def _scan_dir(base: Path, root: Path) -> list[dict]:
    projects: list[dict] = []
    for entry in sorted(base.iterdir()):
        if not entry.is_dir() or entry.name in (TEMPLATE_DIR, ARCHIVE_DIR):
            continue
        meta_path = entry / "project.yaml"
        state_path = entry / "research-state.yaml"
        if not meta_path.is_file():
            continue
        meta = read_yaml(meta_path)
        state = read_yaml(state_path) if state_path.is_file() else {}
        in_archive = base.name == ARCHIVE_DIR
        projects.append(
            {
                "id": str(meta.get("id") or entry.name),
                "dir": f"{ARCHIVE_DIR}/{entry.name}" if in_archive else entry.name,
                "archived": in_archive,
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

    views = st.get("views") or []
    if views or p["id"] != SHARED_ID:  # _shared 是方法论层，无交付视图，空则不渲染
        L.append(f"### 呈现层视图（{len(views)} 个，lark 非 SSOT · 单向同步）")
        if not views:
            L.append("- （空：未发布到 lark，交付物仅在本地）")
        for v in views:
            v = v if isinstance(v, dict) else {}
            kind = v.get("kind") or "?"
            L.append(f"- **[{kind}]** {v.get('title') or '—'}")
            if v.get("url"):
                L.append(f"  - url: {v['url']}")
            if v.get("token"):
                L.append(f"  - token: `{v['token']}`")
            extras = []
            if v.get("role"):
                extras.append(f"角色={v['role']}")
            if v.get("sync_direction"):
                extras.append(f"同步={v['sync_direction']}")
            if v.get("pushed_at"):
                extras.append(f"推送={v['pushed_at']}")
            if v.get("generated_by"):
                extras.append(f"生成={v['generated_by']}")
            if extras:
                L.append(f"  - {' · '.join(extras)}")
            if v.get("tabs"):
                tabs = v["tabs"]
                tab_txt = ", ".join(str(t) for t in tabs) if isinstance(tabs, list) else str(tabs)
                L.append(f"  - tabs: {tab_txt}")
            if v.get("note"):
                for line in fmt_block("备注", v["note"], indent=2):
                    L.append(line)
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
        "views": st.get("views") or [],
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


# ── 状态机自检（--lint，只读）──────────────────────────────────
def _blank(v) -> bool:
    return v is None or (isinstance(v, str) and not v.strip())


def _ref_exists(root: Path, ref: str) -> bool:
    """引用路径是否存在。允许 `path.md#锚点` 形式：锚点只用于定位章节，不参与文件检查。

    历史写法里 claim 的 evidence/data 常带 `#3.2` `#五` 这类锚点，直接用
    `Path.exists()` 会把锚点当成文件名的一部分 → 误报 REF_DANGLING。
    """
    raw = str(ref).strip().split("#", 1)[0].strip()
    if not raw:
        return True
    return (root / raw.replace("\\", "/")).exists()


def _as_date(v):
    """YAML 会把 2026-09-19 解析成 date；这里兼容 date 与字符串。"""
    from datetime import date as _date

    if hasattr(v, "year"):
        return v
    try:
        return _date.fromisoformat(str(v)[:10])
    except Exception:  # noqa: BLE001
        return None


def lint_projects(projects: list[dict], root: Path, forest: dict) -> list[dict]:
    """只读校验状态机与项目元信息。不改任何文件，只报问题。

    级别：ERROR（门禁硬性缺失/悬空引用）> WARN（质量项缺失）> INFO（提示）。
    """
    from datetime import date as _date

    issues: list[dict] = []

    def add(level: str, project: str, code: str, detail: str) -> None:
        issues.append({"level": level, "project": project, "code": code, "detail": detail})

    by_id = {p["id"]: p for p in projects}

    # queue.depends_on 可指向 claim(C-*) / monitor(M-*) / queue(Q-*) 任一对象 ID，
    # 且允许跨项目引用（如子 task 依赖父项目结论）→ 先汇总全局对象 ID。
    def object_ids(st: dict) -> set:
        ids = set()
        for key in ("claims", "monitors", "queue"):
            for it in st.get(key) or []:
                if it.get("id"):
                    ids.add(str(it["id"]))
        return ids

    all_obj_ids: set = set()
    for p in projects:
        all_obj_ids |= object_ids(p.get("state") or {})

    counts: dict[str, int] = {}
    for p in projects:
        counts[p["id"]] = counts.get(p["id"], 0) + 1
    for pid, n in sorted(counts.items()):
        if n > 1:
            add("ERROR", pid, "DUP_ID", f"项目 ID 出现 {n} 次（ID 必须唯一）")

    for p in projects:
        pid = p["id"]
        meta = p.get("meta") or {}
        st = p.get("state") or {}

        # —— project.yaml 必填
        for f in ("id", "name"):
            if _blank(meta.get(f)):
                add("ERROR", pid, "META_MISSING", f"project.yaml 缺 `{f}`")
        if pid != SHARED_ID:
            tr = meta.get("track")
            if _blank(tr):
                add("ERROR", pid, "TRACK_MISSING", "project.yaml 缺 track")
            elif str(tr).strip() not in VALID_TRACKS:
                add("ERROR", pid, "TRACK_INVALID",
                    f"track={tr!r} 不在 5 种内 {list(VALID_TRACKS)}")
        if _blank(meta.get("status")):
            add("WARN", pid, "STATUS_MISSING", "project.yaml 缺 status")

        if not p.get("state_path"):
            add("WARN", pid, "STATE_MISSING", "缺 research-state.yaml")
            continue

        # —— 状态机五段（views 为可选呈现层，单独校验，缺失不告警）
        for seg in STATE_SEGMENTS:
            if seg not in st:
                add("WARN", pid, "SEG_MISSING", f"research-state.yaml 缺 `{seg}` 段")

        # —— claims（G5：confidence + status 必填；证伪留痕不删）
        for c in st.get("claims") or []:
            cid = c.get("id") or "?"
            if _blank(c.get("id")) or _blank(c.get("statement")):
                add("ERROR", pid, "CLAIM_INCOMPLETE", f"claim {cid} 缺 id/statement")
            if _blank(c.get("confidence")) or _blank(c.get("status")):
                add("ERROR", pid, "CLAIM_NO_GRADE",
                    f"claim {cid} 缺 confidence/status（G5 未过）")
            elif str(c.get("status")).strip() not in CLAIM_STATUS:
                add("ERROR", pid, "CLAIM_STATUS",
                    f"claim {cid} status={c.get('status')!r} 不在 {list(CLAIM_STATUS)}")
            for key in ("evidence", "data"):
                v = c.get(key)
                if v and not _ref_exists(root, v):
                    add("ERROR", pid, "REF_DANGLING",
                        f"claim {cid} 的 {key} 指向不存在的文件：{v}")

        # —— monitors（G6：阈值与 as_of）
        for m in st.get("monitors") or []:
            nm = m.get("name") or "?"
            if _blank(m.get("threshold")):
                add("WARN", pid, "MON_NO_THRESHOLD", f"monitor {nm} 缺 threshold")
            if _blank(m.get("as_of")):
                add("WARN", pid, "MON_NO_ASOF", f"monitor {nm} 缺 as_of")

        # —— queue 依赖悬空（可指向 claim / monitor / queue，允许跨项目）
        for q in st.get("queue") or []:
            for d in q.get("depends_on") or []:
                if str(d) not in all_obj_ids:
                    add("WARN", pid, "Q_DEP_DANGLING",
                        f"queue {q.get('id') or '?'} 依赖不存在的 ID：{d}")

        # —— datasets 路径
        for d in st.get("datasets") or []:
            if d.get("path") and not (root / str(d["path"])).exists():
                add("WARN", pid, "DATA_MISSING", f"dataset 路径不存在：{d['path']}")

        # —— views（呈现层视图）：单一 schema + 单向同步，防止三套写法扩散
        raw_views = st.get("views", [])
        if raw_views is not None and not isinstance(raw_views, list):
            add("ERROR", pid, "VIEW_NOT_LIST",
                f"views 必须是列表（当前为 {type(raw_views).__name__}，单个视图也要写成 `- kind: ...`）")
            raw_views = []
        for v in raw_views:
            if not isinstance(v, dict):
                add("ERROR", pid, "VIEW_NOT_MAP", f"views 条目必须是映射（当前：{v!r}）")
                continue
            label = v.get("title") or v.get("url") or "?"
            for old, new in VIEW_LEGACY_KEYS.items():
                if old in v:
                    add("ERROR", pid, "VIEW_LEGACY_KEY",
                        f"view {label} 用了旧字段 `{old}`，已统一为 `{new}`（见 templates/research-state.yaml）")
            for f in VIEW_REQUIRED:
                if _blank(v.get(f)):
                    add("ERROR", pid, "VIEW_INCOMPLETE", f"view {label} 缺 `{f}`（必填 {list(VIEW_REQUIRED)}）")
            kind = str(v.get("kind") or "").strip()
            if kind and kind not in VIEW_KINDS:
                add("ERROR", pid, "VIEW_BAD_KIND",
                    f"view {label} kind={kind!r} 不在受控词表 {list(VIEW_KINDS)}")
            url = str(v.get("url") or "").strip()
            if url and not url.startswith(("http://", "https://")):
                add("ERROR", pid, "VIEW_BAD_URL", f"view {label} url 不是 http(s) 链接：{url!r}")
            tok = str(v.get("token") or "").strip()
            if "/" in tok:
                add("ERROR", pid, "VIEW_TOKEN_PREFIX",
                    f"view {label} token={tok!r} 带了类型前缀；token 只存裸值（{kind or 'kind'} 已表达类型）")
            sd = str(v.get("sync_direction") or "").strip()
            if not sd:
                add("WARN", pid, "VIEW_NO_SYNC",
                    f"view {label} 缺 sync_direction（应为 {VIEW_SYNC[0]}）")
            elif sd not in VIEW_SYNC:
                add("ERROR", pid, "VIEW_SYNC_REVERSE",
                    f"view {label} sync_direction={sd!r}；只允许单向 {list(VIEW_SYNC)}"
                    "（lark 不是 SSOT，回写一律改本地再重推）")
            if _blank(v.get("pushed_at")):
                add("WARN", pid, "VIEW_NO_PUSHED", f"view {label} 缺 pushed_at（无法判断视图是否过期）")

        # —— 关系层
        nd = node_of(p)
        if nd["parent"] and nd["parent"] not in by_id:
            add("ERROR", pid, "PARENT_DANGLING", f"node.parent={nd['parent']} 不存在")

        # —— 陈旧度
        upd = st.get("updated_at") or meta.get("updated_at")
        if _blank(upd):
            add("WARN", pid, "NO_UPDATED", "缺 updated_at")
        else:
            d0 = _as_date(upd)
            if d0 is None:
                add("WARN", pid, "BAD_UPDATED", f"updated_at 无法解析为日期：{upd}")
            elif (_date.today() - d0).days > STALE_DAYS:
                add("INFO", pid, "STALE",
                    f"updated_at={upd} 已超 {STALE_DAYS} 天未更新（E3 命中窗口）")

    # —— 父已收口但子仍有 open 结论
    for p in projects:
        kids = forest["children"].get(p["id"]) or []
        if kids and str(p.get("status")) in ("done", "archived"):
            for k in kids:
                kp = forest["by_id"].get(k) or {}
                kst = kp.get("state") or {}
                n_open = len([c for c in (kst.get("claims") or []) if c.get("status") == "open"])
                if n_open:
                    add("WARN", p["id"], "PARENT_DONE_CHILD_OPEN",
                        f"父已 {p.get('status')}，但子 {k} 仍有 {n_open} 条 open 结论")

    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    issues.sort(key=lambda i: (order.get(i["level"], 9), i["project"], i["code"]))
    return issues


def render_lint(issues: list[dict], n_projects: int, hidden: int = 0) -> str:
    from datetime import date as _date

    n_err = sum(1 for i in issues if i["level"] == "ERROR")
    n_warn = sum(1 for i in issues if i["level"] == "WARN")
    n_info = sum(1 for i in issues if i["level"] == "INFO")

    L: list[str] = [
        "# 状态机自检（--lint · 只读，不改任何文件）",
        "",
        f"- 检查日期：{_date.today().isoformat()} · 项目数：{n_projects}"
        + (f"（含 {hidden} 个已归档）" if hidden else ""),
        f"- 结果：**严重 {n_err} · 警告 {n_warn} · 提示 {n_info}**",
        "",
    ]
    if not issues:
        L.append("✅ 无问题。")
        return "\n".join(L)

    L.append("| 级别 | 项目 | 代码 | 说明 |")
    L.append("|------|------|------|------|")
    for i in issues:
        L.append(f"| **{i['level']}** | {i['project']} | `{i['code']}` | {i['detail']} |")
    L.append("")
    L.append(
        "判定：严重项 = 门禁硬性缺失或悬空引用，须修；"
        "警告 = 质量项缺失；提示 = 仅提醒。有严重项时退出码为 1。"
    )
    return "\n".join(L)


def render_lint_json(issues: list[dict], n_projects: int, hidden: int = 0) -> str:
    from datetime import date as _date

    counts = {
        "ERROR": sum(1 for i in issues if i["level"] == "ERROR"),
        "WARN": sum(1 for i in issues if i["level"] == "WARN"),
        "INFO": sum(1 for i in issues if i["level"] == "INFO"),
    }
    out = {
        "schema": "research-lint/v1",
        "checked_at": _date.today().isoformat(),
        "projects": n_projects,
        "archived_included": hidden,
        "counts": counts,
        "issues": issues,
    }
    return json.dumps(out, ensure_ascii=False, indent=2, default=str)


# ── 清单渲染 ───────────────────────────────────────────────────
def render_list(projects: list[dict], shared: dict | None, root: Path,
                hidden_archived: int = 0) -> str:
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

    if hidden_archived:
        L.append(f"> 已隐藏 {hidden_archived} 个 `archived` 项目（`--all` 才显示；`--lint` 会纳入自检）")
        L.append("")
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
    ap.add_argument("--lint", action="store_true",
                    help="只读自检状态机（不改文件）：受控词表 / 门禁必填 / 悬空引用 / 陈旧度；有严重项退出码 1")
    ap.add_argument("--all", action="store_true",
                    help="连带显示 archived 项目（默认隐藏；--lint 始终纳入归档项目）")
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

    # ── --lint：只读自检（含 _archive 下的归档项目），跑完即退出
    if args.lint:
        scan = discover_projects(root, include_archive=True)
        if not scan:
            sys.exit("[ERROR] 没有可自检的项目（research/*/project.yaml 均未找到）")
        forest_scan = build_forest(scan)
        issues = lint_projects(scan, root, forest_scan)
        hidden = sum(1 for p in scan if p.get("archived"))
        if args.json:
            print(render_lint_json(issues, len(scan), hidden))
        else:
            print(render_lint(issues, len(scan), hidden))
        return 1 if any(i["level"] == "ERROR" for i in issues) else 0

    # ── archived 项目默认隐藏，--all 才显示（D8）；但显式 --project 指定的仍加载
    hidden_archived = sum(1 for p in projects if str(p.get("status")) == "archived")
    if hidden_archived and not args.all:
        wanted = {k.strip().lower() for k in (args.project or "").split(",") if k.strip()}
        kept = [
            p for p in projects
            if str(p.get("status")) != "archived"
            or p["id"].lower() in wanted
            or p["dir"].lower() in wanted
        ]
        actually_hidden = len(projects) - len(kept)
        if actually_hidden:
            projects = kept
            forest_all = build_forest(projects)
        hidden_archived = actually_hidden
    else:
        hidden_archived = 0

    normal, shared = split_projects(projects)
    if args.no_shared:
        shared = None

    if args.list:
        print(render_list(normal, shared, root, hidden_archived))
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
