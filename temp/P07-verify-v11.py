#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
P07 v1.1 独立复核（只读）：结构 / 禁用词 / 合并专项 / Reference 覆盖 / 标题 / 关键 URL / v1 未改写。

与 v1 的 P07-final-verify.py 并列，互不覆盖；验证对象是实际交付的 md + html，
附录正文直接从 v1.1 markdown 源截取，不重建生成逻辑。
"""
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
T, O = ROOT / "temp", ROOT / "output"
MD = O / "2026-11-10_行业_菲律宾合规CFD市场进入_v1.1.md"
HT = O / "2026-11-10_行业_菲律宾合规CFD市场进入_v1.1.html"
V1_MD = O / "2026-11-09_行业_菲律宾合规CFD市场进入_v1.md"
V1_HT = O / "2026-11-09_行业_菲律宾合规CFD市场进入_v1.html"
SUPP_HT = O / "2026-11-10_行业_菲律宾合规CFD市场推广前置研究_校企合作交易社群KOL_v1.html"

html = HT.read_bytes().decode("utf-8")
md = MD.read_bytes().decode("utf-8")
soup = BeautifulSoup(html, "html.parser")
v1_soup = BeautifulSoup(V1_HT.read_bytes().decode("utf-8"), "html.parser")
supp_soup = BeautifulSoup(SUPP_HT.read_bytes().decode("utf-8"), "html.parser")
chapters = [(T / ("P07-draft-ch%d.md" % i)).read_bytes().decode("utf-8") for i in range(1, 6)]
h2_all = soup.find_all("h2")

results = []


def chk(name, got, want, cmp="eq"):
    ok = (got == want) if cmp == "eq" else (got >= want)
    results.append((ok, name, got, want))
    print("  %-4s %-48s got=%-6s want=%s" % (
        "OK " if ok else "FAIL", name, got, ("=" if cmp == "eq" else ">=") + str(want)))


print("=" * 80)
print("[1] HTML 结构")
print("=" * 80)
chk("sections（引言+5章+结论+附录A）", len(soup.find_all("section")), 8)
chk("h2", len(h2_all), 8, "ge")
chk("h3", len(soup.find_all("h3")), 52, "ge")
chk("h4（附录小节）", len(soup.find_all("h4")), 20, "ge")
chk("table.data（v1 13 + 附录 11）", len(soup.select("table.data")), 24)
chk("caliber 口径块行数", len(soup.select("table.cal tr")), 11, "ge")
chk("主报告反方清单 li", len(soup.select("ol.cv li")), 7)
chk("目录块 .toc", len(soup.select(".toc")), 1)
chk("目录条目数（5 章 + 附录 A）", len(soup.select(".toc ol li")), 6)
chk("占位符残留", html.count("{{"), 0)
chk("目录含「附录 A（非章节）」", int("附录 A（非章节）" in html), 1)

print()
print("=" * 80)
print("[2] 禁用词与终稿残留（交付文本必须全 0）")
print("=" * 80)
BANNED = ["currently SUSPENDED", "现行暂停", "首批 4 家", "无限期暂停",
          "test.manilatimes.net", "fintech@sec.gov.ph", "服务费收入 +74%",
          "比索禁令", "三家沙盒承接方", "VASP 暂停无限期", "[UNSOURCED]",
          "另有一条加强证据", "《CASP Rules》规定", "lbk.pub"]
for k in BANNED:
    chk(k, html.count(k), 0)
chk("www.manilatimes.net 正式域名", html.count("www.manilatimes.net"), 9, "ge")
chk("kind: judgment", html.count("kind: judgment"), 29, "ge")
chk("非明文禁止（框架结论口径）", html.count("非明文禁止"), 1, "ge")

print()
print("=" * 80)
print("[3] v1.1 合并专项（附录独立性）")
print("=" * 80)
chk("附录 A 出现次数", html.count("附录 A"), 5, "ge")
chk("附录 A 标题出现在 h2", int(any("附录 A" in x.get_text() for x in h2_all)), 1)
chk("未误编为「第 6 章」", int(any("第 6 章" in x.get_text() for x in h2_all)), 0)
for s in ["不参与、不改变准入证伪结论", "不是可执行推广方案", "独立体系", "仅适用本附录"]:
    chk("边界声明: " + s[:14], int(s in html), 1)
chk("附录 A 口径块标题", int("附录 A 口径块" in html), 1)
chk("附录 A 反方标题标明独立", int("不参与主报告反方计数" in html), 1)
chk("版本说明 v1.1 在册", int("v1.1｜2026-11-10" in html), 1)
cal = soup.select_one("table.cal")
chk("报告级 caliber 未混入附录口径", int("附录 A 口径块" in (cal.get_text() if cal else "")), 0)
chk("附录口径表在正文（非 cal）", int("附录 A 口径块" in soup.get_text()), 1)

print()
print("=" * 80)
print("[4] Reference 覆盖与来源不丢失")
print("=" * 80)
ref_items = soup.select("ul.ref li")
ref_urls = set()
for li in ref_items:
    for a in li.find_all("a", href=True):
        ref_urls.add(a["href"].strip())
    m = re.search(r"https?://[^\s｜|）)<]+", li.get_text())
    if m:
        ref_urls.add(m.group(0).rstrip(".,;"))
v1_urls = {a["href"].strip() for a in v1_soup.select("ul.ref li a[href]")}
supp_urls = {a["href"].strip() for a in supp_soup.select("ul.ref li a[href]")}
print("  Reference li=%d  含链接 li=%d  提取 URL=%d" % (
    len(ref_items), sum(1 for li in ref_items if li.find("a")), len(ref_urls)))
print("  v1=%d 条 / 增补件=%d 条 / 合并=%d 条" % (len(v1_urls), len(supp_urls), len(ref_urls)))
chk("Reference li", len(ref_items), 216)
chk("Reference 全部链接化", sum(1 for li in ref_items if li.find("a")), 216)
chk("v1 来源全部保留", sum(1 for u in v1_urls if u in ref_urls), len(v1_urls))
chk("增补件来源全部保留", sum(1 for u in supp_urls if u in ref_urls), len(supp_urls))

LINK = re.compile(r"\[[^\]\n]+\]\((https?://[^)\n]+)\)")
i_app = md.index("# 附录 A｜")
j_app = md.index("## 反方论点（主报告")
app_md = md[i_app:j_app]
inline = set()
for t in chapters + [app_md]:
    for u in LINK.findall(t):
        inline.add(u.split()[0].strip())
missing = sorted(u for u in inline if u not in ref_urls)
print("  五章 + 附录内联链接去重 = %d；未进 Reference = %d" % (len(inline), len(missing)))
chk("内联链接 Reference 覆盖缺失数", len(missing), 0)
if missing:
    for u in missing[:12]:
        print("    MISSING " + u)

print()
print("=" * 80)
print("[5] 章节标题语义抽取")
print("=" * 80)
for n in range(1, 6):
    hit = any(("第 %d 章" % n) in x.get_text() or ("第%d章" % n) in x.get_text() for x in h2_all)
    chk("第 %d 章标题出现在 h2" % n, int(hit), 1)

print()
print("=" * 80)
print("[6] 关键一手 URL（主报告 7 + 附录 6）")
print("=" * 80)
KEY = [
    "https://www.manilatimes.net/2019/10/09/business/columnists-business/secs-warning-against-online-trading-apps/628580",
    "https://www.manilatimes.net/2025/06/12/business/top-business/sec-issues-rules-on-crypto-asset-service-providers/2131711",
    "https://www.manilatimes.net/2025/12/13/business/corporate-news/halt-order-issued-versus-pacquiao-endorsed-xm/2242635",
    "https://data.worldbank.org/country/philippines",
    "https://psa.gov.ph/content/gdp-grows-23-percent-second-quarter-2026",
    "https://www.sec.gov.ph/?p=138912",
    "https://mintchain.ph/?p=3441",
    "https://legacy.ched.gov.ph/wp-content/uploads/2018/03/CMO-NO.-104-S.-2017.pdf",
    "https://www.sec.gov.ph/mc-2025/sec-mc-no-04-series-of-2025the-sec-rules-on-crypto-asset-service-providers-sec-casp-rules/",
    "https://bitdigest.io/posts/sec-ph-says-crypto-kols-and-content-creators-need-a-license--heres-what-that-means",
    "https://www.investagrams.com/partners/pafti/",
    "https://dole.gov.ph/news/stronger-internship-guidelines-open-better-pathways-to-jobs-public-service",
    "https://www.sec.gov.ph/wp-content/uploads/2023/11/2023Advisory_ARCANE-DIGITAL-MARKETING-Final_11-16-2023-Draft.pdf",
]
for u in KEY:
    chk("HTML: " + u[:46], int(u in html), 1)

print()
print("=" * 80)
print("[7] 交付物与 v1 未被改写")
print("=" * 80)
print("  MD   %-62s %d B" % (MD.name, MD.stat().st_size))
print("  HTML %-62s %d B" % (HT.name, HT.stat().st_size))
chk("v1.1 md 规模", int(MD.stat().st_size > 250000), 1)
chk("v1.1 html 规模", int(HT.stat().st_size > 350000), 1)
chk("v1 md 仍完整（准入证伪在册）",
    int(V1_MD.stat().st_size >= 200000 and "准入证伪" in V1_MD.read_bytes().decode("utf-8")), 1)
chk("v1 html 仍完整（非明文禁止在册）",
    int(V1_HT.stat().st_size >= 300000 and "非明文禁止" in V1_HT.read_bytes().decode("utf-8")), 1)
print("  v1 md/html = %d / %d B（参数卡 §18 登记 236089 / 302593；精确指纹由 v1.1 组装器运行前后断言保证）"
      % (V1_MD.stat().st_size, V1_HT.stat().st_size))

fails = [r for r in results if not r[0]]
print()
print("=" * 80)
print("VERIFY_V11 %s  (%d/%d checks passed)" % (
    "PASS" if not fails else "FAIL", len(results) - len(fails), len(results)))
if fails:
    for _, n, g, w in fails:
        print("  FAIL %s got=%s want=%s" % (n, g, w))
print("=" * 80)
sys.exit(0 if not fails else 1)
