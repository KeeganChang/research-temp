#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
snapshot_url.py — 网页/资讯快照抓取器（Observation 层的落地动作）

为什么存在
----------
一句话：**截图是最差的存证方式。**

不可检索（grep 不到数字）、体积大、没法校验。真正能用于核查的是
「去标签后的正文 + 元信息」：哪天抓的、抓的哪个 URL、原文标题/作者/发布时间、
原始 HTML 的 sha256。有了这些，verify_numbers.py 那种「这个数字在原文里到底
有没有出处」的双向检查才做得到 —— P06 里查出「净流出约 500 亿」凭空捏造，
靠的就是 fund_flow.json 存了完整原文。

存什么
------
    artifacts/raw/web/<YYYYMMDD>_<slug>.txt     去标签正文（人读 / grep 用）
    artifacts/raw/web/<YYYYMMDD>_<slug>.html    原始 HTML（可选，默认存）
    artifacts/raw/web/_index.json               登记表（append，含 sha256）

用法
----
    python -m script.snapshot_url <url> --project P06
    python -m script.snapshot_url <url> --project P06 --name "海上发射国标"
    python -m script.snapshot_url <url> --project P06 --no-html      # 不存原始 HTML
    python -m script.snapshot_url <url> --project P06 --note "行业层+概念层双口径"
    python -m script.snapshot_url --project P06 --list               # 列已有快照

约定
----
- 项目目录靠前缀发现（`research/<PID>-*/`），不建注册表。
- 路径零硬编码：全部相对 workspace 根。
- 文件名 `<日期>_<类别>_<主题>_<版本>.<ext>` 体系（web → 归入 raw）。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESEARCH = ROOT / "research"

TXT_SUBDIR = "artifacts/raw/web"


# ── HTML → 正文（不依赖 bs4，避免环境问题；有 bs4 时用更好的版本）──────────
_TAG_STRIP = re.compile(r"(?is)<(script|style|noscript|svg)\b.*?</\1>")
_TAG_ANY = re.compile(r"(?s)<[^>]+>")
_WS = re.compile(r"[ \t\u00a0]+")
_BLANKS = re.compile(r"\n{3,}")


def html_to_text(html: str) -> str:
    """去脚本/样式/标签 → 规整空行的纯文本。"""
    try:
        from bs4 import BeautifulSoup  # type: ignore

        soup = BeautifulSoup(html, "html.parser")
        for bad in soup(["script", "style", "noscript", "svg", "header", "footer"]):
            bad.decompose()
        text = soup.get_text("\n")
    except Exception:
        text = _TAG_ANY.sub("\n", _TAG_STRIP.sub("", html))
    lines = [_WS.sub(" ", ln).strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    return _BLANKS.sub("\n\n", "\n".join(lines)).strip()


def slugify(s: str, fallback: str = "page") -> str:
    s = re.sub(r"[^\w\u4e00-\u9fa5]+", "-", s or "").strip("-")
    return (s or fallback)[:40]


def find_project(pid: str) -> Path:
    hits = sorted(p for p in RESEARCH.glob(f"{pid}-*") if p.is_dir())
    if not hits:
        sys.exit(f"[x] 找不到项目目录 research/{pid}-*")
    return hits[0]


def load_index(idx_path: Path) -> list:
    if idx_path.exists():
        try:
            return json.loads(idx_path.read_text(encoding="utf-8"))
        except Exception:
            print(f"[!] _index.json 解析失败，将重建：{idx_path}", file=sys.stderr)
    return []


def cmd_list(project: Path) -> int:
    web = project / TXT_SUBDIR
    if not web.exists():
        print(f"(尚无快照) {web}")
        return 0
    for r in load_index(web / "_index.json"):
        print(f"{r['fetched_at']}  {r['bytes']:>8,}B  {r['title'][:40]:<40}  {r['url'][:60]}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="网页/资讯文本快照抓取器")
    ap.add_argument("url", nargs="?", help="要抓取的 URL")
    ap.add_argument("--project", "-p", required=True, help="项目 ID，如 P06")
    ap.add_argument("--name", help="快照 slug（默认由标题推导）")
    ap.add_argument("--note", default="", help="备注：为什么抓、这页回答什么问题")
    ap.add_argument("--no-html", action="store_true", help="不保存原始 HTML")
    ap.add_argument("--list", action="store_true", help="列出现有快照")
    ap.add_argument("--timeout", type=int, default=20)
    a = ap.parse_args(argv)

    project = find_project(a.project)

    if a.list:
        return cmd_list(project)

    if not a.url:
        sys.exit("[x] 需要 URL（或用 --list 查看已有快照）")

    import requests  # 延迟导入：--list 时不依赖网络库

    print(f"[.] GET {a.url}")
    r = requests.get(
        a.url,
        timeout=a.timeout,
        headers={"User-Agent": "Mozilla/5.0 (compatible; research-snapshot/1.0)"},
    )
    r.raise_for_status()
    if not r.encoding or r.encoding.lower() == "iso-8859-1":
        r.encoding = r.apparent_encoding or "utf-8"
    html = r.text
    sha = hashlib.sha256(html.encode("utf-8", "replace")).hexdigest()

    title = ""
    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", html)
    if m:
        title = _WS.sub(" ", html_to_text(m.group(1))).strip()
    meta_pub = ""
    for pat in (
        r'(?is)<meta[^>]+property=["\']article:published_time["\'][^>]+content=["\']([^"\']+)',
        r'(?is)<meta[^>]+name=["\']publish[-_]?time["\'][^>]+content=["\']([^"\']+)',
        r'(?is)<meta[^>]+name=["\']pubdate["\'][^>]+content=["\']([^"\']+)',
    ):
        mm = re.search(pat, html)
        if mm:
            meta_pub = mm.group(1)
            break

    stamp = datetime.now().strftime("%Y%m%d")
    slug = a.name or slugify(title, fallback=slugify(a.url))
    web = project / TXT_SUBDIR
    web.mkdir(parents=True, exist_ok=True)
    base = web / f"{stamp}_{slug}"

    text = html_to_text(html)
    (base.with_suffix(".txt")).write_text(
        f"# {title}\nURL: {a.url}\nfetched_at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n"
        f"publish_time(meta): {meta_pub or '(未取到)'}\nsha256(html): {sha}\n"
        f"{'-' * 60}\n\n{text}\n",
        encoding="utf-8",
    )
    html_size = 0
    if not a.no_html:
        html_bytes = html.encode("utf-8", "replace")
        (base.with_suffix(".html")).write_bytes(html_bytes)
        html_size = len(html_bytes)

    idx_path = web / "_index.json"
    records = load_index(idx_path)
    records = [x for x in records if x.get("sha256") != sha]
    records.append(
        {
            "date": stamp,
            "slug": slug,
            "title": title,
            "url": a.url,
            "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "publish_time": meta_pub or None,
            "note": a.note or None,
            "text": str((base.with_suffix('.txt')).relative_to(ROOT)).replace("\\", "/"),
            "html": (str((base.with_suffix('.html')).relative_to(ROOT)).replace("\\", "/"))
            if not a.no_html
            else None,
            "bytes": html_size,
            "chars": len(text),
            "sha256": sha,
        }
    )
    records.sort(key=lambda x: x.get("fetched_at", ""))
    idx_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] 正文 {len(text):,} 字符 → {base.with_suffix('.txt').name}")
    if not a.no_html:
        print(f"     原始 HTML {html_size:,}B → {base.with_suffix('.html').name}")
    print(f"     sha256 {sha[:16]}…  标题：{title[:50]}")
    print(f"[i] 登记表 {idx_path.relative_to(ROOT)} 现有 {len(records)} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
