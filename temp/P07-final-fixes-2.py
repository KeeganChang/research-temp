# -*- coding: utf-8 -*-
"""P07 终稿增量修补（D44）：CH2 复核 PASS 8/10 附带的两处引用语义残留 + 参数卡状态更新。
只读不改套件文件；用 read_bytes/write_bytes 保留换行风格。
"""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

T = Path(__file__).resolve().parent
CH2 = T / "P07-draft-ch2.md"
CARD = T / "P07-research-card-v3.md"

ch2 = CH2.read_bytes().decode("utf-8")
card = CARD.read_bytes().decode("utf-8")
orig_ch2, orig_card = ch2, card
log = []

# ---- 1. 反方①：2025 全年 GDP/通胀补世界银行 WDI 内联链接 ----
R1_OLD = "2025 全年 GDP +4.4%、通胀 1.7%（世界银行 WDI）"
R1_NEW = ("2025 全年 GDP +4.4%、通胀 1.7%"
          "（[世界银行 WDI 菲律宾国别页](https://data.worldbank.org/country/philippines)，"
          "世界银行，2025 年值）")
assert ch2.count(R1_OLD) == 1, "R1 命中数异常: %d" % ch2.count(R1_OLD)
ch2 = ch2.replace(R1_OLD, R1_NEW)
log.append("OK  CH2 反方① 补世界银行 WDI 内联链接")

# ---- 2. 反方①：Q1 2.8% 显式挂 BusinessWorld/PSA，避免与紧邻的 Philstar 链接语义错配 ----
R2_OLD = "（2025 Q2 为 5.4%、2026 Q1 为 2.8%）"
R2_NEW = ("（2025 Q2 为 5.4%、2026 Q1 为 2.8%，"
          "[BusinessWorld 转引 PSA, 2026-08-07]"
          "(https://bworldonline.com/top-stories/2026/08/07/768829/"
          "philippine-q2-growth-slumps-to-new-post-pandemic-low-amid-oil-shock)）")
assert ch2.count(R2_OLD) == 1, "R2 命中数异常: %d" % ch2.count(R2_OLD)
ch2 = ch2.replace(R2_OLD, R2_NEW)
log.append("OK  CH2 反方① Q1 2.8% 显式挂 BusinessWorld/PSA")

# ---- 3. 参数卡：§9 的 CH2 状态补上「复核 PASS 8/10」----
clines = card.split("\n")
i9 = next(i for i, l in enumerate(clines) if l.startswith("- ✅ **5 路审稿覆盖完成**"))
old9 = clines[i9]
assert "CH2 REVISE 8/10" in old9 and "复核 PASS" not in old9, "§9 状态行不符合预期"
clines[i9] = old9.replace(
    "、`[^fx]` 汇率两时点脚注）、CH3 REVISE",
    "、`[^fx]` 汇率两时点脚注）→ **复核 PASS 8/10**"
    "（3 项非阻塞残留：2 项由 D44 修补、1 项由 D42 明文豁免）、CH3 REVISE")
assert clines[i9] != old9, "§9 替换未生效"
log.append("OK  参数卡 §9 补 CH2 复核 PASS 8/10")

# ---- 4. 参数卡：§17 追加 D44 ----
d43 = next(i for i, l in enumerate(clines) if l.startswith("| D43 |"))
assert not any(l.startswith("| D44 |") for l in clines), "D44 已存在"
D44 = ("| D44 | CH2 复核 PASS 8/10 附带的 2 处引用语义残留 | "
       "① 反方①「2025 全年 GDP +4.4%、通胀 1.7%（世界银行 WDI）」为纯文字括注 → "
       "补 WDI 国别页内联链接；②「2026 Q1 为 2.8%」与紧邻的 Philstar／The Freeman 链接"
       "（该源承载 −13.7%）易被误读为同源 → 显式改挂 BusinessWorld 转引 PSA（该源登记 Q1 2.8%）。"
       "**与 D14 的 −13.7% 错配同源，按 `data-integrity.md` A1/A5 处理**。"
       "第 3 项残留（章内缺口径块）由 D42 明文豁免，报告级顶部口径块已满足 rubric §1②。 |")
clines[d43 + 1:d43 + 1] = [D44]
card = "\n".join(clines)
log.append("OK  参数卡 §17 补录 D44")

# ---- 5. 落盘（参数卡是裁决记录，禁用词守卫不适用）----
BANNED = ("currently SUSPENDED", "现行暂停", "首批 4 家", "无限期暂停")
bad = {k: ch2.count(k) for k in BANNED if ch2.count(k)}
assert not bad, "CH2 出现禁用词 %s" % bad
assert ch2 != orig_ch2 and card != orig_card, "无变更，拒绝空写"
CH2.write_bytes(ch2.encode("utf-8"))
CARD.write_bytes(card.encode("utf-8"))

print("=" * 72)
for x in log: print("  " + x)
print("=" * 72)
print("  WRITE %-30s %d B" % (CH2.name, CH2.stat().st_size))
print("  WRITE %-30s %d B" % (CARD.name, CARD.stat().st_size))
print("=" * 72)

# ---- 6. 落盘复验 ----
chk = CH2.read_bytes().decode("utf-8")
tests = {
    "R1 纯文字括注残留": (chk.count(R1_OLD), 0),
    "WDI 内联链接": (chk.count("世界银行 WDI 菲律宾国别页"), 2),
    "Q1 2.8% 未挂源残留": (chk.count(R2_OLD), 0),
    "Q1 2.8% 已挂 PSA": (chk.count("2026 Q1 为 2.8%，[BusinessWorld"), 1),
    "[^fx] 成对": (chk.count("[^fx]"), 2),
    "D42 明文豁免": (CARD.read_bytes().decode("utf-8").count("| D42 |"), 1),
    "D44 已录": (CARD.read_bytes().decode("utf-8").count("| D44 |"), 1),
    # 两处均正当：§9 状态行 + D44 裁决标题
    "§9 复核 PASS": (CARD.read_bytes().decode("utf-8").count("复核 PASS 8/10"), 2),
}
ok = True
for k, (got, want) in tests.items():
    flag = "OK " if got == want else "FAIL"
    if got != want: ok = False
    print("  %-4s %-28s got=%-3d want=%d" % (flag, k, got, want))
print("=" * 72)
print("FINAL_FIXES_2 " + ("PASS" if ok else "FAIL"))
sys.exit(0 if ok else 4)
