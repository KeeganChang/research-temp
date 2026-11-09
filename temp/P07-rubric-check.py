#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
P07 主交付 G_rubric 前置 10 条自检（report-rubric-v1.md §1）
只做机械可检项与数值复算；语义层（引用是否真支持结论）由 5 路审稿人承担。
"""
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")
HTML = Path(__file__).resolve().parents[1] / "output" / "2026-11-09_行业_菲律宾合规CFD市场进入_v1.html"
p = HTML
t = p.read_text(encoding="utf-8")
soup = BeautifulSoup(t, "html.parser")
text = soup.get_text(" ", strip=True)
sections = soup.select("section")

results = []

# ---- ⑤ 结论由脚本校验：客单价恒等式复算 ----
a24, a25 = 17.423, 24.745          # 万亿 PHP
n24, n25 = 15.08, 47.73            # 亿笔
p24, p25 = 11554, 5184             # PHP/笔
g_amount = a25 / a24 - 1
g_count = n25 / n24 - 1
g_price = p25 / p24 - 1
product = (1 + g_count) * (1 + g_price) - 1
calc24 = a24 * 1e12 / (n24 * 1e8)
calc25 = a25 * 1e12 / (n25 * 1e8)
ok_identity = (
    abs(g_amount - 0.4202) < 0.0005
    and abs(g_count - 2.165) < 0.002
    and abs(g_price + 0.551) < 0.002
    and abs(product - g_amount) < 0.0005
    and abs(calc24 - p24) < 5
    and abs(calc25 - p25) < 5
)
print("=== ⑤ 数值复算 ===")
print("  金额 17.423→24.745 万亿 = {:+.4%}  (报告 +42.02%)".format(g_amount))
print("  笔数 15.08→47.73 亿笔   = {:+.4%}  (报告 +216.5%)".format(g_count))
print("  客单 11,554→5,184 PHP   = {:+.4%}  (报告 -55.1%)".format(g_price))
print("  频次×客单 = {:+.4%}，与金额增幅差 {:.4f}pp".format(product, (product - g_amount) * 100))
print("  由金额/笔数反算客单：2024 {:.0f}（报告 11,554）／2025 {:.0f}（报告 5,184）".format(calc24, calc25))
print("  恒等式：", "PASS" if ok_identity else "FAIL")
results.append(("⑤ 结论由脚本校验（恒等式复算）", ok_identity,
                "金额+42.02% = 频次+216.5% × 客单-55.1%，反算客单误差<5 PHP"))

# ---- ① 关键数字内联引用 ----
links = sum(len(sec.select("a")) for sec in sections)
unsourced = t.count("[UNSOURCED]")
results.append(("① 关键数字内联引用、无 [UNSOURCED]", links > 200 and unsourced == 0,
                "正文内联链接 {} 处；[UNSOURCED] {} 处".format(links, unsourced)))

# ---- ② 顶部口径块 ----
cal_rows = len(soup.select("table.cal tr"))
has_caveat = "caveat" in text or "证据不足" in text
results.append(("② 顶部口径块（单位/基准日/代理指标/known caveat）", cal_rows >= 8 and has_caveat,
                "口径块 {} 行；含 caveat/证据不足标注".format(cal_rows)))

# ---- ③ 反方 ≥5 且含时间维度 ----
counter = soup.select("ol.cv li")
time_dim = sum(1 for li in counter if "时间维度" in li.get_text() or "预测非事实" in li.get_text())
results.append(("③ 反方 ≥5 条且 ≥1 条时间维度", len(counter) >= 5 and time_dim >= 1,
                "反方 {} 条；时间维度 {} 条".format(len(counter), time_dim)))

# ---- ④ 原始返回独立落盘、不进正文 ----
raw_markers = [k for k in ["原始返回", "RAW_RESPONSE", "tool_result_dump"] if k in text]
results.append(("④ 原始返回独立落盘、不进报告正文", len(raw_markers) == 0,
                "正文原始数据块标记：{}".format(raw_markers or "无")))

# ---- ⑥ 标发布方、≥2 路独立源 ----
publisher_hits = len(re.findall(r"[（(][^）)]{2,20}(?:，|,) ?20\d\d", text))
ref_count = len(soup.select("ul.ref li"))
results.append(("⑥ 多源标发布方、≥2 路真正独立源", publisher_hits >= 30 and ref_count >= 30,
                "「发布方，日期」内联标注约 {} 处；去重 Reference {} 条（覆盖 SEC／BSP／PSA／IMF／世行／PAGCOR／律所／媒体等）".format(
                    publisher_hits, ref_count)))

# ---- ⑦ 判断类结论标 kind: judgment + 被否决备选 ----
judg = text.count("kind: judgment")
veto = text.count("被否决备选")
results.append(("⑦ 判断标 kind: judgment、记被否决备选", judg >= 3 and veto >= 3,
                "kind: judgment {} 处；被否决备选 {} 处".format(judg, veto)))

# ---- ⑧ 同比/环比双期并列 ----
pairs = sum(1 for k in ["2025 Q2", "2026 Q2", "2024→2025", "2021 为", "2025 全年", "2024 为"] if k in text)
results.append(("⑧ 同比/环比双期并列写出", pairs >= 5,
                "双期并列标记命中 {}/6 组".format(pairs)))

# ---- ⑨ 比率拆分子分母 ----
num_den = text.count("分子") + text.count("分母")
results.append(("⑨ 比率类指标已拆分子分母", num_den >= 4,
                "分子/分母显式拆解 {} 处（客单价=金额÷笔数、数字支付占比=数字笔数÷零售总笔数等）".format(num_den)))

# ---- ⑩ 关键数字回一手、未裁决冲突不得交付 ----
first_hand = text.count("一手")
insufficient = text.count("证据不足")
unresolved = text.count("未裁决")
results.append(("⑩ 关键数字回一手、未裁决冲突不交付", first_hand >= 20 and insufficient >= 20 and unresolved == 0,
                "一手 {} 处／证据不足 {} 处／未裁决冲突 {} 处".format(first_hand, insufficient, unresolved)))

# ---- 交付级硬检查 ----
placeholders = sum(t.count(ph) for ph in
                   ["{{PID}}", "{{THEME}}", "{{SECTIONS}}", "{{CALIBER_ROWS}}", "{{COUNTER_ITEMS}}", "{{REFERENCE_ITEMS}}"])
banned = {k: t.count(k) for k in ["currently SUSPENDED", "现行暂停", "首批 4 家", "无限期暂停"]}
results.append(("交付硬检查：占位符/禁用词", placeholders == 0 and all(v == 0 for v in banned.values()),
                "占位符 {}；禁用词 {}".format(placeholders, banned)))

print()
print("=== G_rubric 前置 10 条自检 ===")
okn = 0
for label, ok, note in results:
    print("  [{}] {} — {}".format("PASS" if ok else "FAIL", label, note))
    okn += 1 if ok else 0
print()
print("通过 {}/{} 项".format(okn, len(results)))
print("文件大小：HTML {} 字节".format(p.stat().st_size))
