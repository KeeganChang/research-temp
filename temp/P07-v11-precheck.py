"""v1.1 合并前的只读预检：Reference 去重数、禁用词、附录边界、表格数。"""
import sys, re, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]      # 铁律 #1：零硬编码绝对路径
TMP, OUT = ROOT / "temp", ROOT / "output"
SUPP = OUT / "2026-11-10_行业_菲律宾合规CFD市场推广前置研究_校企合作交易社群KOL_v1.md"
LINK = re.compile(r"\[([^\]\n]+)\]\(([^)\n]+)\)")

def urls(t):
    return [m.group(2).strip() for m in LINK.finditer(t)
            if m.group(2).strip().lower().startswith(("http://", "https://"))]

chapters = [(TMP / ("P07-draft-ch%d.md" % k)).read_bytes().decode("utf-8") for k in range(1, 6)]
fw = json.loads((TMP / "P07-framework.json").read_bytes().decode("utf-8"))
supp = SUPP.read_bytes().decode("utf-8")

main_urls = set()
for t in chapters:
    main_urls.update(urls(t))
for k in ("intro", "conclusion"):
    main_urls.update(urls(fw.get(k, "")))
supp_urls = set(urls(supp))
merged = main_urls | supp_urls
print("=" * 76)
print("REFERENCE 去重")
print("=" * 76)
print("  五章+框架 内联 URL = %d" % len(main_urls))
print("  增补件 内联 URL   = %d" % len(supp_urls))
print("  合并去重          = %d  (重叠 %d，新增 %d)" % (
    len(merged), len(main_urls & supp_urls), len(supp_urls - main_urls)))
print("  仅出现在增补件的 URL 前 8 条：")
for u in sorted(supp_urls - main_urls)[:8]:
    print("    " + u)

print("=" * 76)
print("禁用词扫描（增补件全文）")
print("=" * 76)
BANNED = ["currently SUSPENDED", "现行暂停", "首批 4 家", "无限期暂停",
          "test.manilatimes.net", "fintech@sec.gov.ph", "服务费收入 +74%",
          "比索禁令", "三家沙盒承接方", "VASP 暂停无限期", "[UNSOURCED]",
          "另有一条加强证据", "《CASP Rules》规定", "lbk.pub", "无限期"]
for k in BANNED:
    n = supp.count(k)
    if n:
        print("  HIT  %-28s x%d" % (k, n))
        for i, l in enumerate(supp.splitlines(), 1):
            if k in l:
                print("       L%d | %s" % (i, l.strip()[:160]))
print("  (未列出者 = 0 命中)")

print("=" * 76)
print("附录边界与结构")
print("=" * 76)
ls = supp.splitlines()
for i, l in enumerate(ls, 1):
    if l.startswith("## "):
        print("  L%-4d %s" % (i, l[:80]))
print("  TOTAL_LINES=%d  table_rows=%d  table_headers=%d" % (
    len(ls), sum(1 for l in ls if l.lstrip().startswith("|")),
    sum(1 for l in ls if l.lstrip().startswith("|") and "---" not in l)))
idx_ref = next(i for i, l in enumerate(ls) if l.startswith("## Reference"))
idx_counter = next(i for i, l in enumerate(ls) if l.startswith("## 反方论点"))
print("  反方标题 L%d / Reference 标题 L%d → 附录正文保留至 L%d" % (
    idx_counter + 1, idx_ref + 1, idx_ref))
print("  增补件表格数(按分隔行计) = %d" % sum(
    1 for i in range(len(ls) - 1)
    if ls[i].lstrip().startswith("|") and re.match(r"^\s*\|?[\s:\-\|]+\|", ls[i + 1]) and "-" in ls[i + 1]))
print("=" * 76)
