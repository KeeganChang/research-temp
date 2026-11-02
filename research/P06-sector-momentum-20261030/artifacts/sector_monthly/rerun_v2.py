# -*- coding: utf-8 -*-
"""method-sector-momentum 回跑 v2 —— 补齐 M1 流出侧 / M4 四象限 / M5 β-α 剥离
数据窗口不变：复用 series.json（2025-12-31 → 2026-10-29），资金流重拉同交易日(2026-10-29)。
"""
import json, sys, re, statistics, itertools
sys.stdout.reconfigure(encoding="utf-8")

BASE = "2025-12-31"

# ---------- 加载月度序列 ----------
series = json.load(open("series.json", encoding="utf-8"))
SECTORS = list(series.keys())

# ---------- M1 资金流：从资讯正文正则提取 + 手工补登记 ----------
docs = json.load(open("fund_flow.json", encoding="utf-8"))["data"]["docData"]["docRecall"][0]["docList"]
text = max((d.get("content", "") for d in docs), key=len)

inflow, outflow = {}, {}
BOUND = {}   # True = 该值为下限（原文用「超 X 亿」而非「逾 X 亿」）
for s in SECTORS:
    m = re.search(s + r"[^，。]*?获得逾?([\d.]+)亿元", text)
    if m:
        inflow[s] = float(m.group(1)); BOUND[s] = False
    m2 = re.search(s + r"[^，。]*?净流出(?:逾|超)([\d.]+)亿元", text)
    if m2:
        outflow[s] = -float(m2.group(1)); BOUND[s] = True if "超" in m2.group(0) else False

# 原文只说「超亿元净流入」、无精确值 → 登记为下限 1.0 亿
for s in ["公用事业", "煤炭", "石油石化", "电力设备"]:
    if s not in inflow and s not in outflow:
        inflow[s] = 1.0; BOUND[s] = True
LOWER_BOUND = {k: v for k, v in BOUND.items() if v}

# ---------- M2/M3 景气度计算 ----------
def pct(a, b):
    return (b / a - 1.0) * 100.0 if a else float("nan")

mon = {}      # 行业 -> [(period_label, mom_pct)]
norm = {}     # 行业 -> [(date, 归一化值)]
for s in SECTORS:
    d = series[s]
    dates = sorted(d.keys())
    closes = [d[x] for x in dates]
    base = d.get(BASE, closes[0])
    norm[s] = [(x, d[x] / base * 100.0) for x in dates]
    mon[s] = [(dates[i][:7], pct(closes[i - 1], closes[i])) for i in range(1, len(dates))]

PERIODS = [p for p, _ in mon[SECTORS[0]]]
ytd = {s: pct(series[s][BASE], series[s][sorted(series[s])[-1]]) for s in SECTORS}
mom3 = {s: sum(v for _, v in mon[s][-3:]) for s in SECTORS}          # 近 3 个月累计（07-31→10-29）
amp = {s: (max(v for _, v in norm[s]) - min(v for _, v in norm[s])) for s in SECTORS}

# ---------- M5 同涨同跌：月度环比相关矩阵 ----------
def corr(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = sum((x - ma) ** 2 for x in a) ** 0.5
    db = sum((y - mb) ** 2 for y in b) ** 0.5
    return num / (da * db) if da and db else 0.0

vec = {s: [v for _, v in mon[s]] for s in SECTORS}
corr_pairs = []
for a, b in itertools.combinations(SECTORS, 2):
    corr_pairs.append((a, b, round(corr(vec[a], vec[b]), 3)))
corr_pairs.sort(key=lambda x: -x[2])

# ---------- M4 四象限 ----------
def quadrant(s):
    f = inflow.get(s) or outflow.get(s) or 0.0
    m = mom3[s]
    if f > 0 and m > 0: return "双高(主推)"
    if f > 0 and m <= 0: return "脉冲(观察)"
    if f <= 0 and m > 0: return "未兑现(候选)"
    return "双低(规避)"

quad = {s: quadrant(s) for s in SECTORS}
order = {"双高(主推)": 0, "未兑现(候选)": 1, "脉冲(观察)": 2, "双低(规避)": 3}
ranked = sorted(SECTORS, key=lambda s: (order[quad[s]], -mom3[s]))

# ---------- 输出 ----------
print("流入(亿):", json.dumps(inflow, ensure_ascii=False))
print("流出(亿):", json.dumps(outflow, ensure_ascii=False))
print("\n行业      流入   近3月%   YTD%    振幅    象限")
for s in ranked:
    f = inflow.get(s) or outflow.get(s) or 0.0
    flag = "*" if BOUND.get(s) else " "
    print(f"{s:<8}{f:>7.1f}{flag}{mom3[s]:>8.1f}{ytd[s]:>8.1f}{amp[s]:>8.0f}   {quad[s]}")
print("\n同涨同跌 Top8 (相关系数):")
for a, b, c in corr_pairs[:8]:
    print(f"  {a}-{b}: {c}")

out = dict(periods=PERIODS, sectors=SECTORS, inflow=inflow, outflow=outflow,
           lower_bound=LOWER_BOUND, ytd=ytd, mom3=mom3, amp=amp, quad=quad,
           mon={s: [[p, round(v, 2)] for p, v in mon[s]] for s in SECTORS},
           norm={s: [[d, round(v, 1)] for d, v in norm[s]] for s in SECTORS},
           corr_top=corr_pairs[:15], ranked=ranked)
json.dump(out, open("analysis_v2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n[OK] analysis_v2.json written")
