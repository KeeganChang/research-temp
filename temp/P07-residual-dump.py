# -*- coding: utf-8 -*-
"""只读：导出各章残留关键词所在行 + CH2 章首，供主编逐行裁决。"""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

TMP = Path(__file__).resolve().parent
DEST = TMP / "P07-residual-lines.txt"
KEYS = ["test.manilatimes.net", "fintech@sec.gov.ph", "比索禁令", "服务费收入",
        "+74%", "130 万", "Quevedo", "Mintchain", "不治愈", "WEO", "5.8%",
        "−13.7%", "-13.7%", "9.2%", "[^fx]", "63.8520", "61.33"]

lines_out = []
for i in range(1, 6):
    p = TMP / ("P07-draft-ch%d.md" % i)
    if not p.exists():
        continue
    txt = p.read_text(encoding="utf-8")
    lines_out.append("=" * 78)
    lines_out.append("CH%d  (%d chars)" % (i, len(txt)))
    lines_out.append("=" * 78)
    for n, ln in enumerate(txt.splitlines(), 1):
        if any(k in ln for k in KEYS):
            lines_out.append("L%-4d| %s" % (n, ln[:420]))

lines_out.append("")
lines_out.append("=" * 78)
lines_out.append("CH2 章首前 24 行（检查是否被违规新增章首口径块）")
lines_out.append("=" * 78)
ch2 = (TMP / "P07-draft-ch2.md").read_text(encoding="utf-8")
for n, ln in enumerate(ch2.splitlines()[:24], 1):
    lines_out.append("L%-4d| %s" % (n, ln[:420]))

lines_out.append("")
lines_out.append("=" * 78)
lines_out.append("CH4 含 '服务费收入' / '130 万' 的前后各 3 行")
lines_out.append("=" * 78)
ch4 = (TMP / "P07-draft-ch4.md").read_text(encoding="utf-8").splitlines()
for n, ln in enumerate(ch4, 1):
    if "服务费收入" in ln or "130 万" in ln:
        for j in range(max(0, n - 4), min(len(ch4), n + 3)):
            lines_out.append("L%-4d| %s" % (j + 1, ch4[j][:420]))
        lines_out.append("-" * 60)

lines_out.append("")
lines_out.append("=" * 78)
lines_out.append("CH5 含 '比索禁令' / 'fintech@' 的前后各 4 行")
lines_out.append("=" * 78)
ch5 = (TMP / "P07-draft-ch5.md").read_text(encoding="utf-8").splitlines()
for n, ln in enumerate(ch5, 1):
    if "比索禁令" in ln or "fintech@" in ln:
        for j in range(max(0, n - 5), min(len(ch5), n + 4)):
            lines_out.append("L%-4d| %s" % (j + 1, ch5[j][:420]))
        lines_out.append("-" * 60)

DEST.write_text("\n".join(lines_out), encoding="utf-8")
print("WROTE %s  lines=%d  bytes=%d" % (DEST, len(lines_out), DEST.stat().st_size))
