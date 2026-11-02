#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse monthly K-line closes for 12 申万一级 sectors from neodata JSON, build time series."""
import json, re, os, glob

BASE = os.path.dirname(os.path.abspath(__file__))

SECTORS = {
    "银行": "bank.json",
    "煤炭": "coal.json",
    "石油石化": "petrochem.json",
    "交通运输": "transport.json",
    "公用事业": "utility.json",
    "食品饮料": "food.json",
    "电子": "electronics.json",
    "通信": "comm.json",
    "计算机": "computer.json",
    "电力设备": "power_equip.json",
    "有色金属": "nonferrous.json",
    "国防军工": "defense.json",
}

def parse_one(path):
    """Return dict {date(str YYYY-MM-DD): close(float)} from the markdown table in apiRecall content."""
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    try:
        data = json.loads(raw)
    except Exception as e:
        return None, f"json-error:{e}"
    content = ""
    for blk in data.get("data", {}).get("apiData", {}).get("apiRecall", []):
        if blk.get("type") in ("统一行情查询",) or "行情" in (blk.get("desc") or ""):
            content += blk.get("content", "") + "\n"
    if not content:
        # fallback: join all content
        for blk in data.get("data", {}).get("apiData", {}).get("apiRecall", []):
            content += blk.get("content", "") + "\n"
    rows = {}
    for line in content.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        d0 = cells[0]
        # date like 2026-10-29 at col0
        m = re.match(r"^(\d{4}-\d{2}-\d{2})(\s|~)", d0 + " ")
        if not m:
            continue
        date = m.group(1)
        # close is col index 4
        close_s = cells[4].replace(",", "")
        try:
            close = float(close_s)
        except ValueError:
            continue
        rows[date] = close
    return rows, ("ok" if rows else "empty")

result = {}
for name, fn in SECTORS.items():
    p = os.path.join(BASE, fn)
    rows, status = parse_one(p)
    if rows is None:
        print(f"[FAIL] {name}: {status}")
        continue
    # keep only month-end-ish: sort dates
    sd = sorted(rows.items())
    print(f"\n=== {name} ({status}) n={len(sd)} ===")
    for d, c in sd:
        print(f"  {d}: {c:.2f}")
    result[name] = dict(sd)

# Save parsed series for downstream
with open(os.path.join(BASE, "series.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("\nSaved series.json")
