# -*- coding: utf-8 -*-
"""只读：精确输出待替换行的完整原文，供确定性修补比对。"""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
T = Path(__file__).resolve().parent

targets = {
    "ch2": ("P07-draft-ch2.md", ["WEO"]),
    "ch4": ("P07-draft-ch4.md", ["服务费收入"]),
    "ch5": ("P07-draft-ch5.md", ["fintech@sec", "比索禁令", "不治愈"]),
}
out = []
for tag, (fn, keys) in targets.items():
    lines = (T / fn).read_text(encoding="utf-8").splitlines()
    out.append("### " + fn)
    for n, ln in enumerate(lines, 1):
        if any(k in ln for k in keys):
            out.append("L%d [%d chars]" % (n, len(ln)))
            out.append(ln)
            out.append("")
out.append("### test.manilatimes.net 全案分布")
for i in range(1, 6):
    p = T / ("P07-draft-ch%d.md" % i)
    t = p.read_text(encoding="utf-8")
    for n, ln in enumerate(t.splitlines(), 1):
        if "test.manilatimes.net" in ln:
            for m in __import__("re").finditer(r"https://test\.manilatimes\.net/[^\s｜|）)]+", ln):
                out.append("CH%d L%d  %s" % (i, n, m.group(0)))
dest = T / "P07-exact-lines.txt"
dest.write_text("\n".join(out), encoding="utf-8")
print("WROTE", dest, dest.stat().st_size)
