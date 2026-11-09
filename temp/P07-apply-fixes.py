#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
P07 交付前确定性修订（主编侧，不经过 shell 内联，避免特殊字符被吞）：
  1. framework.json 结论① 清除被撤回的 D33（无一手出处 URL）
  2. 第 3 章清理 D3 / D4 残留（单写「首批 4 家」「无限期延长／无限期暂停」）
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
D = Path(__file__).resolve().parent

# ---------------------------------------------------------------- 1. 框架件
fp = D / "P07-framework.json"
data = json.loads(fp.read_text(encoding="utf-8"))
c = data["conclusion"]
start = c.find("**① 法定地位")
end = c.find("[MC 9 s.2024]", start)
assert start >= 0 and end > start, "结论① 锚点未找到"

new_para = (
    "**① 法定地位与沙盒／牌照准入（条件、时点、主体资格）→ 判否。** "
    "全案对零售 CFD 只能表述「**非明文禁止**」——本研究**未检索到** SEC 全面禁止零售 CFD 的一手条文；"
    "实际障碍是缺可注册的牌照通道：2015 IRR Rule 11.2 的现行有效性仍须**回一手条文并取本地律师意见核实**"
    "（含暂停的法律后果、能否经 special rules 恢复），本研究不作「已被替代／仍有效／已彻底核实闭环」的定论。"
)
data["conclusion"] = c[:start] + new_para + c[end:]
fp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("[OK] framework.json 结论① 已清除 D33")

# ---------------------------------------------------------------- 2. 第 3 章
cp = D / "P07-draft-ch3.md"
t = cp.read_text(encoding="utf-8")
fixes = [
    (
        "SEC 于 2025-11 披露 StratBox 首批 4 家：",
        "截至 2025-11，SEC StratBox **累计 4 家**"
        "（2025-06-02 已有 GCash GStocks／Pluang PH，2025-11 BlockShoals 为第 4 家，其中**零售 CFD 0 家**）：",
    ),
    (
        "① CAI 身份稀缺（首批 4 家中仅 1 家加密中介，VASP 新牌照无限期暂停）",
        "① CAI 身份稀缺（截至 2025-11 累计 4 家中仅 1 家加密中介；"
        "BSP M-2025-031 新 VASP 牌照申请自 2025-09-01 **持续生效、视 global and local developments 重估**）",
    ),
    (
        "M-2025-031（2025-08-29）无限期延长，新主体",
        "M-2025-031（2025-08-29）使暂停自 2025-09-01 **持续生效并视 global and local developments 重估**"
        "（律所解读为无限期延长），新主体",
    ),
    (
        "| 首批 4 家构成；",
        "| 截至 2025-11 累计 4 家构成；",
    ),
]
for old, new in fixes:
    n = t.count(old)
    assert n >= 1, "CH3 未找到锚点: " + old[:34]
    t = t.replace(old, new)
    print("[OK] CH3 替换 x{}: {}".format(n, old[:34]))

cp.write_text(t, encoding="utf-8")
print("[OK] CH3 已落盘, 字节", cp.stat().st_size)

# ---------------------------------------------------------------- 3. 复验
j = fp.read_text(encoding="utf-8")
c3 = cp.read_text(encoding="utf-8")
print()
print("[CHECK] framework currently SUSPENDED =", j.count("currently SUSPENDED"))
print("[CHECK] framework 非明文禁止 =", j.count("非明文禁止"))
print("[CHECK] CH3 首批 4 家 =", c3.count("首批 4 家"))
print("[CHECK] CH3 无限期暂停 =", c3.count("无限期暂停"))
print("[CHECK] CH3 菲律宾 P2P 96%（禁令说明，应保留）= 1 ->", c3.count("菲律宾 P2P 96%"))
