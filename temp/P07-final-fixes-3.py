# -*- coding: utf-8 -*-
"""P07 终稿增量修补 D45：CH3 最终改判 PASS 10/10 附带的引用弱匹配 + kind 标记。
只改正文内联引用挂载与一个标记，不动来源清单（D31 保留全文）、不新增未核验事实。
"""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

T = Path(__file__).resolve().parent
CH3 = T / "P07-draft-ch3.md"
CARD = T / "P07-research-card-v3.md"
ch3 = CH3.read_bytes().decode("utf-8")
card = CARD.read_bytes().decode("utf-8")
orig = (ch3, card)
log = []

# ---- R1: L12 逐平台功能分类，去掉 lbk.pub 弱源，改挂参数卡 §14 已核定两源 ----
R1_OLD = ("其中 Deriv 为零售衍生品／CFD 经纪商，dYdX／Aevo／gTrade／Ostium 为链上永续、期权与杠杆协议"
          "（[lbk.pub 平台功能对照]"
          "(https://www.lbk.pub/es/creator/philippines-sec-flags-dydx-six-crypto-platforms-unauthorized)，2026）。")
R1_NEW = ("其中 Deriv 为零售衍生品／CFD 经纪商，dYdX／Aevo／gTrade／Ostium 为链上永续、期权与杠杆协议"
          "（[Manila Times, 2026-04-22]"
          "(https://www.manilatimes.net/2026/04/22/business/top-business/sec-warns-vs-cryptocurrency-platforms/2325249)；"
          "[Fintech News Philippines](https://fintechnews.ph/?p=71107/)，2026；"
          "**逐平台功能分类口径由参数卡 §14 核定**）。")
assert ch3.count(R1_OLD) == 1, "R1 命中数异常: %d" % ch3.count(R1_OLD)
ch3 = ch3.replace(R1_OLD, R1_NEW)
log.append("OK  CH3 L12 改挂 §14 已核定两源，去掉 lbk.pub 弱匹配（slug 写 6 家 vs 本章 8 家）")

# ---- R2: L8 章首核心判断补显式 kind: judgment ----
R2_OLD = "核心判断：菲律宾被执法压缩、但未被明文消灭的杠杆／衍生品需求"
R2_NEW = "核心判断（`kind: judgment`）：菲律宾被执法压缩、但未被明文消灭的杠杆／衍生品需求"
assert ch3.count(R2_OLD) == 1, "R2 命中数异常: %d" % ch3.count(R2_OLD)
ch3 = ch3.replace(R2_OLD, R2_NEW)
log.append("OK  CH3 L8 补 `kind: judgment` 显式标记")

# ---- 参数卡：§9 状态行改为「最终改判 PASS 10/10」----
cl = card.split("\n")
i9 = next(i for i, l in enumerate(cl) if l.startswith("- ✅ **5 路审稿覆盖完成**"))
old9 = cl[i9]
OLD_SEG = ("CH3 REVISE 9/10 → 3 项必改由 `P07-apply-fixes.py`＋D43 落地"
           "（累计 4 家口径、「四家」量词、反方⑤补 2025-06 节点）")
NEW_SEG = ("CH3 **最终改判 PASS 10/10**（替代上轮基于 31,626 B 版的 REVISE；3 项必改由 "
           "`P07-apply-fixes.py`＋D43 落地，D45 清掉 lbk.pub 弱匹配）")
assert OLD_SEG in old9, "§9 未找到 CH3 旧状态段"
cl[i9] = old9.replace(OLD_SEG, NEW_SEG)
assert cl[i9] != old9
log.append("OK  参数卡 §9 更新为 CH3 最终改判 PASS 10/10")

# ---- 参数卡：§17 追加 D45 终局裁决 ----
d44 = next(i for i, l in enumerate(cl) if l.startswith("| D44 |"))
assert not any(l.startswith("| D45 |") for l in cl), "D45 已存在"
D45 = ("| D45 | CH3 审稿**最终改判 PASS 10/10**（替代上轮基于 31,626 B 版的 REVISE 9/10）；"
       "附带 1 处引用弱匹配 | ① **L12 逐平台功能分类**（Deriv＝零售 CFD 经纪商、"
       "dYdX／Aevo／gTrade／Ostium＝链上永续与杠杆协议）原挂 `lbk.pub`，该页 slug 写 "
       "「six crypto platforms」与本章 8 家口径不一致且属聚合站弱源 → **改挂参数卡 §14 已核定的 "
       "Manila Times 2026-04-22 ＋ Fintech News PH 两源**，来源清单不动（D31 保留全文）。"
       "② L8 章首核心判断补 `kind: judgment` 显式标记（§1⑦ 已有 6 处达下限，此为一致性补强，"
       "不逐句追加）。③ **终局裁决——以下残留不修**：章首重复口径块由 D42 明文豁免；"
       "§1⑧ 双期并列审稿人自判充分；GAI 链接可达性／$273B 回原文／D28「创始人兼 CEO」"
       "属非阻塞核验项；「仅作资金形态对照」等措辞级建议不因追求完美反复退回。"
       "④ 审稿人审的是 31,626 B 版，其列的「三家」量词与「VASP 暂停无限期」"
       "已由 D43 在 31,877 B 版清掉。 |")
cl[d44 + 1:d44 + 1] = [D45]
card = "\n".join(cl)
log.append("OK  参数卡 §17 补录 D45")

# ---- 落盘（守卫只作用于交付正文；参数卡是裁决记录）----
BANNED = ("currently SUSPENDED", "现行暂停", "首批 4 家", "无限期暂停")
bad = {k: ch3.count(k) for k in BANNED if ch3.count(k)}
assert not bad, "CH3 出现禁用词 %s" % bad
assert (ch3, card) != orig, "无变更，拒绝空写"
CH3.write_bytes(ch3.encode("utf-8"))
CARD.write_bytes(card.encode("utf-8"))

print("=" * 72)
for x in log: print("  " + x)
print("=" * 72)
print("  WRITE %-30s %d B" % (CH3.name, CH3.stat().st_size))
print("  WRITE %-30s %d B" % (CARD.name, CARD.stat().st_size))
print("=" * 72)

# ---- 落盘复验 ----
c = CH3.read_bytes().decode("utf-8")
k = CARD.read_bytes().decode("utf-8")
tests = {
    "lbk.pub 弱源残留": (c.count("lbk.pub"), 0),
    "§14 核定两源挂载": (c.count("逐平台功能分类口径由参数卡 §14 核定"), 1),
    "L8 kind 标记": (c.count("核心判断（`kind: judgment`）"), 1),
    # 审稿人下限为 ≥3 处；本章实有 6 处（含 D45 新增的 L8 一处）
    "CH3 kind: judgment 总数": (c.count("kind: judgment"), 6, "ge"),
    "D45 已录": (k.count("| D45 |"), 1),
    "§9 最终改判": (k.count("最终改判 PASS 10/10"), 2, "ge"),
    "来源清单 #7/#8 完好": (int("Manila Times | 2026-04-22" in c and "Fintech News Philippines | 2026" in c), 1),
}
ok = True
for name, val in tests.items():
    if len(val) == 3: got, want, cmp = val
    else: got, want, cmp = val[0], val[1], "eq"
    good = (got >= want) if cmp == "ge" else (got == want)
    if not good: ok = False
    print("  %-4s %-32s got=%-3d want=%s%d" % ("OK " if good else "FAIL", name, got,
          ">=" if cmp == "ge" else "=", want))
print("=" * 72)
print("FINAL_FIXES_3 " + ("PASS" if ok else "FAIL"))
sys.exit(0 if ok else 4)
