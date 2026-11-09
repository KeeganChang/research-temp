# -*- coding: utf-8 -*-
"""P07 主编侧落盘状态自检（只读）。用于上下文压缩后重新对齐 ground truth。"""
import sys, os, re, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / "temp"
OUT = ROOT / "output"

print("=" * 72)
print("[A] temp/P07-* 文件清单")
print("=" * 72)
for p in sorted(TMP.glob("P07-*")):
    st = p.stat()
    print("  %-34s %9d B  %s" % (p.name, st.st_size,
          __import__("datetime").datetime.fromtimestamp(st.st_mtime).strftime("%m-%d %H:%M:%S")))

print()
print("=" * 72)
print("[B] output/ 候选交付物")
print("=" * 72)
for p in sorted(OUT.glob("2026-11-09*")):
    print("  %-58s %9d B" % (p.name, p.stat().st_size))

CH = {i: TMP / ("P07-draft-ch%d.md" % i) for i in range(1, 6)}
FW = TMP / "P07-framework.json"

BANNED = ["currently SUSPENDED", "现行暂停", "首批 4 家", "无限期暂停"]
RESIDUAL = ["WEO", "5.8%", "-13.7%", "−13.7%", "[^fx]", "test.manilatimes.net",
            "fintech@sec.gov.ph", "比索禁令", "服务费收入", "+74%", "130 万",
            "Quevedo", "Mintchain", "non-curative", "不治愈"]
POSITIVE = ["产品层", "法币层", "MC No.5", "kind: judgment", "非明文禁止", "累计 4 家"]

def rd(p):
    return p.read_text(encoding="utf-8") if p.exists() else ""

print()
print("=" * 72)
print("[C] 各章关键词命中（BANNED 必须为 0）")
print("=" * 72)
for i, p in CH.items():
    if not p.exists():
        print("  CH%d : MISSING" % i); continue
    t = rd(p)
    head = ""
    for ln in t.splitlines()[:10]:
        if re.match(r"^#{1,2}\s*第\s*\d+\s*章", ln):
            head = ln.strip(); break
    b = {k: t.count(k) for k in BANNED if t.count(k)}
    r = {k: t.count(k) for k in RESIDUAL if t.count(k)}
    pos = {k: t.count(k) for k in POSITIVE if t.count(k)}
    print("  CH%d : %d B | %s" % (i, len(t.encode("utf-8")), head[:52]))
    print("        BANNED   : %s" % (b if b else "0"))
    print("        RESIDUAL : %s" % (r if r else "—"))
    print("        POSITIVE : %s" % (pos if pos else "—"))

print()
print("=" * 72)
print("[D] 框架件 P07-framework.json")
print("=" * 72)
if FW.exists():
    t = rd(FW)
    print("  bytes=%d  chars=%d" % (len(t.encode("utf-8")), len(t)))
    try:
        d = json.loads(t)
        print("  keys=%s" % list(d.keys()))
        print("  intro=%d  conclusion=%d  toc=%d  toc_html=%d  extra_refs=%d" % (
            len(d.get("intro", "")), len(d.get("conclusion", "")), len(d.get("toc", "")),
            len(d.get("toc_html", "")), len(d.get("extra_references", []))))
    except Exception as e:
        print("  JSON PARSE FAIL: %s" % e)
    for k in BANNED + ["D33", "WEO", "非明文禁止"]:
        print("    %-22s %d" % (k, t.count(k)))
else:
    print("  MISSING")

print()
print("=" * 72)
print("[E] 候选 HTML 关键结构")
print("=" * 72)
h = OUT / "2026-11-09_行业_菲律宾合规CFD市场进入_v1.html"
if h.exists():
    t = rd(h)
    print("  bytes=%d" % len(t.encode("utf-8")))
    print("  sections=%d  h2=%d  h3=%d  table.data=%d  ref_li=%d  toc=%d" % (
        t.count('<section'), t.count("<h2"), t.count("<h3"), t.count('class="data"'),
        t.count('<ul class="ref"'), t.count('class="toc"')))
    hits = {k: t.count(k) for k in BANNED + RESIDUAL + ["{{"] if t.count(k)}
    print("  禁用词/残留 : %s" % (hits if hits else "0"))
else:
    print("  MISSING")

print()
print("=" * 72)
print("[F] 辅助脚本是否齐备")
print("=" * 72)
for n in ["P07-build-report.py", "P07-apply-fixes.py", "P07-rubric-check.py",
          "P07-report-data.json", "P07-research-card-v3.md"]:
    p = TMP / n
    print("  %-30s %s" % (n, ("%d B" % p.stat().st_size) if p.exists() else "MISSING"))
print("=" * 72)
