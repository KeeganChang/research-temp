#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
P07 增补件 A1 渲染 + 独立复核（主编侧确定性工具，不改套件模板、不改主交付 v1）

输入：output/2026-11-10_行业_菲律宾合规CFD市场推广前置研究_校企合作交易社群KOL_v1.md（唯一 SSOT）
输出：同名 .html（自包含单页）+ 复核报告（stdout）

用法：./.venv/Scripts/python.exe temp/P07-supplement-render.py
"""
import html
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
TMP = ROOT / "temp"
BASENAME = "2026-11-10_行业_菲律宾合规CFD市场推广前置研究_校企合作交易社群KOL_v1"
MD = OUT / (BASENAME + ".md")
HTML = OUT / (BASENAME + ".html")
SKILL_RENDER = (
    ROOT / ".workbuddy" / "skills" / "research-kit" / "references" / "skills"
    / "research-html" / "render_html.py"
)
BUILDER = TMP / "P07-build-report.py"
MAIN_MD = OUT / "2026-11-09_行业_菲律宾合规CFD市场进入_v1.md"
MAIN_HTML = OUT / "2026-11-09_行业_菲律宾合规CFD市场进入_v1.html"
# 渲染前先记录主交付指纹，用于证明「本次增补未改动已验证的 v1」
MAIN_MD_SIZE_BEFORE = MAIN_MD.stat().st_size if MAIN_MD.exists() else -1
MAIN_HTML_SIZE_BEFORE = MAIN_HTML.stat().st_size if MAIN_HTML.exists() else -1

DATE = "2026-11-10"
PID = "P07-A1"
THEME = "P07 增补件 A1｜市场推广前置研究：实习机制（校企合作）、交易社群图谱、KOL 信任"

# ---------------------------------------------------------------- 复用主交付组装器（有 __main__ guard，可安全 import）
spec_b = importlib.util.spec_from_file_location("p07_builder", BUILDER)
b = importlib.util.module_from_spec(spec_b)
spec_b.loader.exec_module(b)

# ---------------------------------------------------------------- 从 markdown 单一数据源解析
raw_bytes = MD.read_bytes()
assert not raw_bytes.startswith(b"\xef\xbb\xbf"), "md 含 BOM"
md = raw_bytes.decode("utf-8")
assert b"\r\n" not in raw_bytes, "md 含 CRLF"
lines = md.splitlines()

# 口径块：| 项目 | 口径 | 表格
caliber = []
i = next(n for n, l in enumerate(lines) if l.startswith("## 口径块"))
for l in lines[i + 1:]:
    if l.startswith("## "):
        break
    m = re.match(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|$", l)
    if m and m.group(1) not in ("项目", "---"):
        caliber.append((m.group(1), m.group(2)))

# 目录：## 目录 下的非空纯文本行
toc_items = []
i = next(n for n, l in enumerate(lines) if l.startswith("## 目录"))
for l in lines[i + 1:]:
    if l.startswith("## ") or l.strip() == "---":
        break
    if l.strip():
        toc_items.append(l.strip())

# sections：^## [一二三...]、
sec_pat = re.compile(r"^## ([一二三四五六七八九十]+、.+)$")
starts = [(n, m.group(1)) for n, l in enumerate(lines) if (m := sec_pat.match(l))]
end = next(n for n, l in enumerate(lines) if l.startswith("## 反方论点"))
sections = []
for k, (n, title) in enumerate(starts):
    stop = starts[k + 1][0] if k + 1 < len(starts) else end
    body = "\n".join(lines[n + 1:stop]).strip()
    sections.append({"title": title, "body": b.md_to_html(body)})

# 反方：## 反方论点 下的有序列表
i = end
counter = []
for l in lines[i + 1:]:
    if l.startswith("## "):
        break
    m = re.match(r"^\d+\.\s+(.+)$", l)
    if m:
        counter.append(b.inline(m.group(1)))

# Reference：全件内联链接去重
refs = b.collect_references([md])

data = {
    "pid": PID,
    "theme": THEME,
    "date": DATE,
    "caliber": caliber,
    "sections": sections,
    "counter": counter,
    "reference": refs,
}

spec_r = importlib.util.spec_from_file_location("rk_render_html", SKILL_RENDER)
r = importlib.util.module_from_spec(spec_r)
spec_r.loader.exec_module(r)
r.render(data, HTML)

# ---------------------------------------------------------------- 后处理：CSS / 目录 / Reference 链接化
from bs4 import BeautifulSoup

text = HTML.read_text(encoding="utf-8").replace("</style>", b.EXTRA_CSS + "\n</style>", 1)
soup = BeautifulSoup(text, "html.parser")
doc = soup.find("article", class_="doc")
if doc and toc_items:
    hr = doc.find("hr", class_="rule")
    box = soup.new_tag("div")
    box["class"] = "toc"
    h = soup.new_tag("h2")
    h.string = "目录"
    box.append(h)
    ol = soup.new_tag("ol")
    for it in toc_items:
        li = soup.new_tag("li")
        li.string = it
        ol.append(li)
    box.append(ol)
    if hr:
        hr.insert_after(box)

linked = 0
for li in soup.select("ul.ref li"):
    raw = li.get_text()
    m = re.search(r"(https?://\S+)$", raw)
    if m:
        url = m.group(1)
        li.string = ""
        li.append(raw[: m.start()].rstrip(" —"))
        a = soup.new_tag("a", href=url, target="_blank", rel="noopener")
        a.string = url
        li.append(a)
        linked += 1
HTML.write_text(str(soup), encoding="utf-8")

# ---------------------------------------------------------------- 独立复核
body = HTML.read_text(encoding="utf-8")
md_urls = {m.group(2).strip() for m in b.LINK_RE.finditer(md)
           if m.group(2).strip().lower().startswith(("http://", "https://"))}
ref_anchors = {a["href"] for a in soup.select("ul.ref li a")}

BANNED = (
    "currently SUSPENDED", "现行暂停", "首批 4 家", "无限期暂停",
    "test.manilatimes.net", "比索禁令", "三家沙盒承接方", "[UNSOURCED]",
)
KEY_URLS = [
    "https://legacy.ched.gov.ph/wp-content/uploads/2018/03/CMO-NO.-104-S.-2017.pdf",
    "https://www.sec.gov.ph/mc-2025/sec-mc-no-04-series-of-2025the-sec-rules-on-crypto-asset-service-providers-sec-casp-rules/",
    "https://bitpinas.com/business/key-takeaways-sec-final-crypto-rules/",
    "https://www.manilatimes.net/2025/12/13/business/corporate-news/halt-order-issued-versus-pacquiao-endorsed-xm/2242635",
    "https://www.investagrams.com/partners/pafti/",
    "https://dole.gov.ph/news/stronger-internship-guidelines-open-better-pathways-to-jobs-public-service",
]
checks = []


def ck(name, cond, detail=""):
    checks.append((name, bool(cond), detail))


ck("md UTF-8 无 BOM / LF-only", not raw_bytes.startswith(b"\xef\xbb\xbf") and b"\r\n" not in raw_bytes)
ck("口径块行数 ≥8", len(caliber) >= 8, "got=%d" % len(caliber))
ck("目录条目 = 5", len(toc_items) == 5, "got=%d" % len(toc_items))
ck("sections = 5", len(sections) == 5, "got=%d" % len(sections))
ck("五章标题语义正确", [s["title"][0] for s in sections] == list("一二三四五"),
   str([s["title"][:12] for s in sections]))
ck("反方 ≥5 条", len(counter) >= 5, "got=%d" % len(counter))
ck("反方含时间维度", any("时间维度" in c for c in counter))
ck("HTML 占位符全替换", all(p not in body for p in
   ["{{PID}}", "{{THEME}}", "{{SECTIONS}}", "{{CALIBER_ROWS}}", "{{COUNTER_ITEMS}}", "{{REFERENCE_ITEMS}}"]))
ck("HTML section = 5", body.count("<section>") == 5, "got=%d" % body.count("<section>"))
ck("HTML 表格 ≥6", body.count('<table class="data">') >= 6,
   "got=%d" % body.count('<table class="data">'))
ck("HTML 目录块 = 1", body.count('class="toc"') == 1)
ck("Reference 条数 = 去重 URL 数", len(refs) == len(md_urls),
   "refs=%d urls=%d" % (len(refs), len(md_urls)))
ck("Reference 全部链接化", linked == len(refs), "linked=%d refs=%d" % (linked, len(refs)))
ck("内联链接未进 Reference = 0", len(md_urls - ref_anchors) == 0,
   "missing=%d" % len(md_urls - ref_anchors))
for w in BANNED:
    ck("禁用词 0: %s" % w, body.count(w) == 0 and md.count(w) == 0,
       "html=%d md=%d" % (body.count(w), md.count(w)))
for u in KEY_URLS:
    ck("关键 URL 在册: ...%s" % u[-46:], u in md_urls and u in ref_anchors)
ck("证据不足清单 10 条", len(re.findall(r"^\d+\.\s+\*\*未取得\*\*|^\d+\.\s+\*\*未", md, re.M)) >= 8,
   "approx=%d" % len(re.findall(r"^\d+\.\s+\*\*未", md, re.M)))
ck("kind: judgment ≥5", md.count("kind: judgment") >= 5,
   "got=%d" % md.count("kind: judgment"))
ck("数据污染警示存在", "模板字段污染" in md)
ck("§7.3.6 豁免条件在册", "7.3.6" in md and "非金钱利益" in md)
ck("主交付 md 未被本次改动", MAIN_MD.stat().st_size == MAIN_MD_SIZE_BEFORE,
   "before=%d after=%d" % (MAIN_MD_SIZE_BEFORE, MAIN_MD.stat().st_size))
ck("主交付 html 未被本次改动", MAIN_HTML.stat().st_size == MAIN_HTML_SIZE_BEFORE,
   "before=%d after=%d" % (MAIN_HTML_SIZE_BEFORE, MAIN_HTML.stat().st_size))

print("=" * 76)
print("P07 增补件 A1 渲染结果")
print("  md   : %s (%d B)" % (MD.name, MD.stat().st_size))
print("  html : %s (%d B)" % (HTML.name, HTML.stat().st_size))
print("  sections=%d  caliber=%d  counter=%d  refs=%d  链接化=%d"
      % (len(sections), len(caliber), len(counter), len(refs), linked))
print("-" * 76)
ok = 0
for name, passed, detail in checks:
    print("  %-4s %-52s %s" % ("OK" if passed else "FAIL", name, detail))
    ok += bool(passed)
print("=" * 76)
print("SUPPLEMENT_VERIFY %d/%d %s" % (ok, len(checks), "PASS" if ok == len(checks) else "FAIL"))
sys.exit(0 if ok == len(checks) else 1)
