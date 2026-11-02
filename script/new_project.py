#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
new_project.py — 从模板新建一个调研项目 / 子 task 目录（research/<ID>-<slug>/）

用法：
    python -m script.new_project --id P03 --name "跨境电商选平台" --track drill
    python -m script.new_project --id P03 --name "..." --track drill --slug cbe --question "..."
    python -m script.new_project --id T1 --name "Amazon 平台" --track entry --parent P03
    python -m script.new_project --list                       # 列出已有项目（防止 ID 撞车）

产出：
    research/P03-cbe/project.yaml          # 由 _template/project.yaml 填 id/name/track/日期
    research/P03-cbe/research-state.yaml   # 由 _template/research-state.yaml 填 project_id
                                           # 给了 --parent 时，回填 node.parent

ID 约定：
    P<两位数字>   父项目（如 P03）
    T<n>[.n]      子 task（如 T1 / T1.1），与父项目同为 research/ 下的平铺目录

多 task 单方向派生：
    子 task 只在自己的 research-state.yaml 写 node.parent；children / depth 不落盘，
    由 load_context 运行时建图与汇总。新增子 task 不改父文件（避免双写漂移）。

设计约束：
1. **零硬编码路径**：workspace 根由「向上找 AGENTS.md」动态定位。
2. **只新增不覆盖**：目标目录已存在则报错退出（不会静默覆盖已有项目）。
3. **不依赖模板外的任何东西**：缺 _template 时给出明确提示。
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import date
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

try:
    import yaml
except ImportError:
    sys.exit("[ERROR] 缺少依赖 PyYAML：pip install pyyaml")

RESEARCH_DIR = "research"
TEMPLATE_DIR = "_template"
ROOT_MARKER = "AGENTS.md"
# 父项目 P<两位数字>；子 task T<n>[.n]（多级用点号，如 T1.1）
ID_RE = re.compile(r"^(?:P\d{2}|T\d+(?:\.\d+)*)$")
# 5 种方法级 Track（与 research-assistant/references/ROUTING.md 一致）。
# 旧值 A/B 已随 2026-10 的 5-Track 重构废弃，不再接受。
TRACKS = ["drill", "entry", "diagnostic", "inductive", "scenario"]
TRACK_HELP = (
    "drill=下钻选优(全集里哪个最好) | entry=进入测绘(能不能进/谁在赚) | "
    "diagnostic=诊断归因(为何偏离/根因) | inductive=归纳洞察(什么分群/规律) | "
    "scenario=情景推演(如果…会怎样)"
)


def find_workspace_root(start: Path | None = None) -> Path:
    here = (start or Path(__file__).resolve().parent).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / ROOT_MARKER).is_file():
            return candidate
    sys.exit(f"[ERROR] 未找到 {ROOT_MARKER}，无法确定 workspace 根（从 {here} 向上查找失败）")


def project_ids(root: Path) -> set[str]:
    """已有项目的 ID 集合（用于 --parent 存在性校验）。"""
    rd = root / RESEARCH_DIR
    ids: set[str] = set()
    if not rd.is_dir():
        return ids
    for entry in sorted(rd.iterdir()):
        p = entry / "project.yaml"
        if entry.is_dir() and entry.name != TEMPLATE_DIR and p.is_file():
            with p.open("r", encoding="utf-8") as f:
                meta = yaml.safe_load(f) or {}
            ids.add(str(meta.get("id") or entry.name))
    return ids


def existing_ids(root: Path) -> list[str]:
    rd = root / RESEARCH_DIR
    if not rd.is_dir():
        return []
    ids = []
    for entry in sorted(rd.iterdir()):
        p = entry / "project.yaml"
        if entry.is_dir() and entry.name != TEMPLATE_DIR and p.is_file():
            with p.open("r", encoding="utf-8") as f:
                meta = yaml.safe_load(f) or {}
            ids.append(f"{str(meta.get('id') or entry.name):6s}  {entry.name}")
    return ids


def slugify(name: str) -> str:
    """中文名给不出可用 slug 时，退化成 ascii 剥离 + 截断。"""
    s = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()
    return s[:24] or "project"


def main() -> int:
    ap = argparse.ArgumentParser(description="新建调研项目 / 子 task 目录")
    ap.add_argument("--id", help="项目 ID：P<两位数字>（父项目）或 T<n>[.n]（子 task）")
    ap.add_argument("--name", help="项目名（一句话）")
    ap.add_argument("--track", choices=TRACKS, help=TRACK_HELP)
    ap.add_argument("--slug", help="目录名后缀（英文短横线），默认由 --name 生成")
    ap.add_argument("--question", help="驱动问题（可选）")
    ap.add_argument("--parent", help="父节点 ID（建子 task）；只写子节点 node.parent，不改父文件")
    ap.add_argument("--list", action="store_true", help="列出已有项目后退出")
    args = ap.parse_args()

    root = find_workspace_root()

    if args.list:
        ids = existing_ids(root)
        print("\n".join(ids) if ids else "（暂无项目）")
        return 0

    if not (args.id and args.name and args.track):
        ap.error("新建项目需要 --id / --name / --track（或用 --list 查看已有项目）")
    if not ID_RE.match(args.id):
        ap.error(
            "--id 必须是 P 加两位数字（父项目，如 P03）或 T 加数字（子 task，如 T1 / T1.1），"
            f"实际: {args.id!r}"
        )

    # --parent 校验：必须真实存在，且不能自指
    parent = args.parent
    if parent:
        if parent == args.id:
            ap.error("--parent 不能指向自己")
        known = project_ids(root)
        if parent not in known:
            sys.exit(
                f"[ERROR] 父项目 {parent!r} 不存在。已有：{', '.join(sorted(known)) or '（无）'}"
            )

    research_dir = root / RESEARCH_DIR
    template_dir = research_dir / TEMPLATE_DIR
    if not template_dir.is_dir():
        sys.exit(f"[ERROR] 缺少模板目录: {template_dir}")

    slug = args.slug or slugify(args.name)
    target = research_dir / f"{args.id}-{slug}"
    if target.exists():
        sys.exit(f"[ERROR] 目标已存在，不会覆盖: {target}")

    today = date.today().isoformat()
    target.mkdir(parents=True)

    # 用「文本替换」而不是 yaml round-trip：模板里的注释是给填写者看的指引，
    # safe_load + safe_dump 会把注释全部丢掉，生成的项目就少了填写说明。
    def fill(template_name: str, subs: list[tuple[str, str]]) -> None:
        src = (template_dir / template_name).read_text(encoding="utf-8")
        for pattern, repl in subs:
            src = re.sub(pattern, repl, src, flags=re.M)
        (target / template_name).write_text(src, encoding="utf-8")

    fill(
        "project.yaml",
        [
            (r"^id:.*$", f"id: {args.id}"),
            (r'^name:.*$', f'name: "{args.name}"'),
            (r"^track:.*$", f"track: {args.track}"),
            (r"^(created_at|updated_at):.*$", rf"\1: {today}"),
            (r"^status:.*$", "status: active"),
        ]
        + ([("^question: >\\n  .*$", "question: >\n  " + args.question)] if args.question else []),
    )
    fill(
        "research-state.yaml",
        [
            (r"^project_id:.*$", f"project_id: {args.id}"),
            (r"^updated_at:.*$", f"updated_at: {today}"),
            (r"^  started_at:.*$", f"  started_at: {today}"),
            # 单方向派生：只写子节点的 parent；children / depth 不落盘
            (r"^  parent:.*$", f"  parent: {parent if parent else 'null'}"),
        ],
    )

    print(f"[OK] 已创建项目 {args.id}: {target.relative_to(root).as_posix()}")
    print(f"     - {args.id}-{slug}/project.yaml")
    print(f"     - {args.id}-{slug}/research-state.yaml")
    if parent:
        print(f"     - 已挂到父节点 {parent}（node.parent）；父文件未改动")
    print("\n下一步：填写 project.yaml 的 question / scope_in / scope_out / deliverables，")
    print(f"然后跑：python -m script.load_context --project {args.id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
