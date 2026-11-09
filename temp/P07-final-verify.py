# -*- coding: utf-8 -*-
"""P07 终稿独立复核（只读）：结构 / 禁用词 / 残留 / Reference 覆盖 / 章标题 / 关键 URL。"""
import sys, re
from pathlib import Path
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding="utf-8")

T = Path(__file__).resolve().parent
O = Path(__file__).resolve().parents[1] / "output"
MD = O / "2026-11-09_行业_菲律宾合规CFD市场进入_v1.md"
HT = O / "2026-11-09_行业_菲律宾合规CFD市场进入_v1.html"
html = HT.read_bytes().decode("utf-8")
md = MD.read_bytes().decode("utf-8")
soup = BeautifulSoup(html, "html.parser")
allc = "\n".join((T / ("P07-draft-ch%d.md" % i)).read_bytes().decode("utf-8") for i in range(1, 6))

results = []
def chk(name, got, want, cmp="eq"):
    ok = (got == want) if cmp == "eq" else (got >= want)
    results.append((ok, name, got, want))
    print("  %-4s %-38s got=%-6s want=%s%s" % (
        "OK " if ok else "FAIL", name, got, ("=" if cmp == "eq" else ">=") + str(want), ""))

print("=" * 78)
print("[1] HTML 结构")
print("=" * 78)
chk("sections", len(soup.find_all("section")), 7)
chk("h2（引言+5章+结论+口径块等）", len(soup.find_all("h2")), 7, "ge")
chk("h3", len(soup.find_all("h3")), 52, "ge")
chk("table.data", len(soup.select("table.data")), 13)
chk("caliber 口径块行数", len(soup.select("table.cal tr")), 11, "ge")
chk("反方清单 li", len(soup.select("ol.cv li")), 7)
chk("目录块 .toc", len(soup.select(".toc")), 1)
chk("占位符残留", html.count("{{"), 0)

print()
print("=" * 78)
print("[2] 禁用词与终稿残留（交付文本必须全 0）")
print("=" * 78)
for k in ["currently SUSPENDED", "现行暂停", "首批 4 家", "无限期暂停",
          "test.manilatimes.net", "fintech@sec.gov.ph", "服务费收入 +74%",
          "比索禁令", "三家沙盒承接方", "VASP 暂停无限期", "[UNSOURCED]",
          "另有一条加强证据", "《CASP Rules》规定", "lbk.pub"]:
    chk(k, html.count(k), 0)
chk("www.manilatimes.net 正式域名", html.count("www.manilatimes.net"), 9, "ge")
chk("kind: judgment", html.count("kind: judgment"), 29, "ge")
chk("非明文禁止（框架结论口径）", html.count("非明文禁止"), 1, "ge")

print()
print("=" * 78)
print("[3] Reference 覆盖（回应 CH1 审稿人「内联链接与 Reference 映射」）")
print("=" * 78)
ref_ul = soup.select_one("ul.ref")
ref_items = ref_ul.find_all("li") if ref_ul else []
ref_urls = set()
for li in ref_items:
    for a in li.find_all("a", href=True):
        ref_urls.add(a["href"].strip())
    # 兜底：纯文本形式
    m = re.search(r"https?://[^\s｜|）)<]+", li.get_text())
    if m: ref_urls.add(m.group(0).rstrip(".,;"))
print("  Reference li = %d，含链接 li = %d，提取到 URL = %d" % (
    len(ref_items), sum(1 for li in ref_items if li.find("a")), len(ref_urls)))

LINK = re.compile(r"\[[^\]\n]+\]\((https?://[^)\n]+)\)")
chap_urls = set()
for i in range(1, 6):
    t = (T / ("P07-draft-ch%d.md" % i)).read_bytes().decode("utf-8")
    for u in LINK.findall(t):
        chap_urls.add(u.split()[0].strip())
missing = sorted(u for u in chap_urls if u not in ref_urls)
print("  五章内联链接去重 = %d；未进 Reference = %d" % (len(chap_urls), len(missing)))
chk("内联链接 Reference 覆盖率缺失数", len(missing), 0)
if missing:
    for u in missing[:15]: print("    MISSING " + u)

print()
print("=" * 78)
print("[4] 五章标题是否按语义抽对（D41）")
print("=" * 78)
for n in range(1, 6):
    h = soup.find_all("h2")
    hit = any(("第 %d 章" % n) in x.get_text() or ("第%d章" % n) in x.get_text() for x in h)
    chk("第 %d 章标题出现在 h2" % n, int(hit), 1)

print()
print("=" * 78)
print("[5] 关键 URL 是否可达性已验证的正式域名 / 一手源")
print("=" * 78)
KEY = [
    "https://www.manilatimes.net/2019/10/09/business/columnists-business/secs-warning-against-online-trading-apps/628580",
    "https://www.manilatimes.net/2025/06/12/business/top-business/sec-issues-rules-on-crypto-asset-service-providers/2131711",
    "https://www.manilatimes.net/2025/12/13/business/corporate-news/halt-order-issued-versus-pacquiao-endorsed-xm/2242635",
    "https://data.worldbank.org/country/philippines",
    "https://psa.gov.ph/content/gdp-grows-23-percent-second-quarter-2026",
    "https://www.sec.gov.ph/?p=138912",
    "https://mintchain.ph/?p=3441",
]
for u in KEY:
    chk("HTML: " + u[:52], int(u in html), 1)

print()
print("=" * 78)
print("[6] 交付物")
print("=" * 78)
print("  MD  %s  %d B" % (MD.name, MD.stat().st_size))
print("  HTML %s  %d B" % (HT.name, HT.stat().st_size))
print("  sections / tables / ref_li = %d / %d / %d" % (
    len(soup.find_all("section")), len(soup.select("table.data")), len(ref_items)))

fails = [r for r in results if not r[0]]
print()
print("=" * 78)
print("FINAL_VERIFY %s  (%d/%d checks passed)" % (
    "PASS" if not fails else "FAIL", len(results) - len(fails), len(results)))
if fails:
    for _, n, g, w in fails: print("  FAIL %s got=%s want=%s" % (n, g, w))
print("=" * 78)
sys.exit(0 if not fails else 1)
