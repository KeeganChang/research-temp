#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
research-html 渲染器：把调研主交付数据(JSON) 渲染为自包含单页 HTML 报告。

调用（项目隔离环境）：
  <workspace>/.venv/Scripts/python.exe render_html.py \
      --data <报告数据.json> [--out <output/<PID>-html-主交付.html>]

模板：同套件 references/templates/html-delivery.html
安全策略：caliber 值 / reference 项自动 HTML 转义（纯文本）；
         sections.body 与 counter 条目允许受控内联 HTML（由 agent 提供）。
"""
import argparse
import html
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# 模板路径：本文件在 references/skills/research-html/，模板在 references/templates/
SKILL_DIR = Path(__file__).resolve().parent
TEMPLATE = SKILL_DIR.parent.parent / "templates" / "html-delivery.html"


def build_caliber(rows):
    """rows: list[[label, value]] -> <tr>..</tr>"""
    out = []
    for label, value in rows or []:
        out.append(
            "<tr><th>{}</th><td>{}</td></tr>".format(html.escape(str(label)), html.escape(str(value)))
        )
    return "\n        ".join(out)


def build_sections(sections):
    """sections: list[{title, body}] -> <section>..</section>"""
    out = []
    for sec in sections or []:
        title = html.escape(str(sec.get("title", "")))
        # body 允许受控内联 HTML（agent 提供）
        body = sec.get("body", "")
        out.append("<section><h2>{}</h2>{}</section>".format(title, body))
    return "\n\n    ".join(out)


def build_counter(items):
    """items: list[str] -> <li>..</li> （允许内联 HTML）"""
    return "\n        ".join("<li>{}</li>".format(it) for it in (items or []))


def build_reference(items):
    """items: list[str] -> <li>..</li> （纯文本转义）"""
    return "\n        ".join("<li>{}</li>".format(html.escape(str(it))) for it in (items or []))


def render(data, out_path):
    if not TEMPLATE.exists():
        raise FileNotFoundError("模板缺失: {}".format(TEMPLATE))
    tpl = TEMPLATE.read_text(encoding="utf-8")

    repl = {
        "{{PID}}": html.escape(str(data.get("pid", ""))),
        "{{THEME}}": html.escape(str(data.get("theme", ""))),
        "{{DATE}}": html.escape(str(data.get("date", ""))),
        "{{CALIBER_ROWS}}": build_caliber(data.get("caliber")),
        "{{SECTIONS}}": build_sections(data.get("sections")),
        "{{COUNTER_ITEMS}}": build_counter(data.get("counter")),
        "{{REFERENCE_ITEMS}}": build_reference(data.get("reference")),
    }
    for k, v in repl.items():
        tpl = tpl.replace(k, v)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(tpl, encoding="utf-8")
    return out_path


def main():
    ap = argparse.ArgumentParser(description="research-kit HTML 交付渲染器")
    ap.add_argument("--data", required=True, help="报告数据 JSON 路径")
    ap.add_argument("--out", default=None, help="输出 HTML 路径（默认 output/<pid>-html-主交付.html）")
    args = ap.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        sys.exit("数据文件不存在: {}".format(data_path))
    data = json.loads(data_path.read_text(encoding="utf-8"))

    pid = data.get("pid", "report")
    out = args.out or "output/{}-html-主交付.html".format(pid)
    # 若 out 为相对路径，相对当前工作目录解析（调用方通常在 workspace 根）
    out_path = Path(out)
    if not out_path.is_absolute():
        out_path = Path.cwd() / out_path

    written = render(data, out_path)
    print("OK 已生成 HTML 交付: {}".format(written))
    print("  大小: {} 字节".format(written.stat().st_size))


if __name__ == "__main__":
    main()
