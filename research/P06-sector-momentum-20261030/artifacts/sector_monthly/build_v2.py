# -*- coding: utf-8 -*-
"""生成回跑 v2 报告：M1 流出侧 / M4 四象限 / M5 同涨同跌 + 独立性"""
import json, sys, math, itertools
sys.stdout.reconfigure(encoding="utf-8")

A = json.load(open("analysis_v2.json", encoding="utf-8"))
S, PERIODS = A["sectors"], A["periods"]
inflow, outflow, quad = A["inflow"], A["outflow"], A["quad"]
ytd, mom3, amp, LB = A["ytd"], A["mom3"], A["amp"], set(A.get("lower_bound", []))
mon, norm, ranked = A["mon"], A["norm"], A["ranked"]
BOUND = set(A.get("lower_bound", []))

def flow(s):
    return inflow.get(s, outflow.get(s, 0.0))

# ---------- 独立性：每行业与其最相关对手的相关系数 ----------
def corr(a, b):
    n = len(a); ma, mb = sum(a)/n, sum(b)/n
    num = sum((x-ma)*(y-mb) for x, y in zip(a, b))
    da = sum((x-ma)**2 for x in a) ** .5; db = sum((y-mb)**2 for y in b) ** .5
    return num/(da*db) if da and db else 0.0

vec = {s: [v for _, v in mon[s]] for s in S}
indep = {}
for s in S:
    best = max(((o, corr(vec[s], vec[o])) for o in S if o != s), key=lambda x: x[1])
    indep[s] = (best[0], round(best[1], 3))
maxcorr = {s: v[1] for s, v in indep.items()}

# ---------- 配色（A股：涨红跌绿） ----------
def heat(v):
    if v is None: return "#f5f5f5"
    t = min(abs(v) / 12.0, 1.0)
    if v >= 0:
        return f"rgba(200,30,45,{0.10 + 0.80*t:.2f})"
    return f"rgba(20,130,70,{0.10 + 0.80*t:.2f})"

def txtc(v):
    return "#fff" if v is not None and abs(v) > 6 else "#222"

# ---------- 1) M1 资金流表 ----------
rows_in = sorted([(s, v) for s, v in inflow.items()], key=lambda x: -x[1])
rows_out = sorted([(s, v) for s, v in outflow.items()], key=lambda x: x[1])
def flow_rows(rows):
    out = []
    for s, v in rows:
        star = '<span class="lb">*</span>' if s in BOUND else ''
        cls = "up" if v > 0 else "dn"
        out.append(f'<tr><td>{s}{star}</td><td class="{cls}">{"+" if v>0 else ""}{v:.0f} 亿</td>'
                   f'<td class="num">{mom3[s]:+.1f}%</td><td class="num">{ytd[s]:+.1f}%</td>'
                   f'<td><span class="q {quad[s][:2]}">{quad[s]}</span></td></tr>')
    return "\n".join(out)

# ---------- 2) M3 月度热力图 ----------
mm = {s: dict((p, v) for p, v in mon[s]) for s in S}
heat_rows = []
for s in sorted(S, key=lambda x: -ytd[x]):
    cells = []
    for p in PERIODS:
        v = mm[s].get(p)
        cells.append(f'<td class="hc" style="background:{heat(v)};color:{txtc(v)}">'
                     f'{"" if v is None else f"{v:+.1f}"}</td>')
    heat_rows.append(f'<tr><th>{s}</th>' + "".join(cells) +
                     f'<td class="num ytd">{ytd[s]:+.1f}%</td></tr>')
heat_html = "\n".join(heat_rows)
period_head = "".join(f'<th>{p[2:]}</th>' for p in PERIODS)

# ---------- 3) 四象限散点（y 用符号 sqrt 压缩） ----------
W, H = 980, 560
PL, PR, PT, PB = 70, 30, 30, 60
xs = [mom3[s] for s in S]; ys = [flow(s) for s in S]
x0, x1 = -28.0, 12.0
def sy(v): return math.copysign(math.sqrt(abs(v)), v)
y0, y1 = sy(-260), sy(50)
def X(v): return PL + (v - x0) / (x1 - x0) * (W - PL - PR)
def Y(v): return H - PB - (sy(v) - y0) / (y1 - y0) * (H - PT - PB)
QT = {"双高(主推)": "#c81e2d", "脉冲(观察)": "#e08c00", "未兑现(候选)": "#1f7a8c", "双低(规避)": "#16824a"}
pts = []
for s in S:
    px, py = X(mom3[s]), Y(flow(s))
    col = QT[quad[s]]
    off = -12 if mom3[s] > -8 else 16
    anc = "middle"
    pts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="7" fill="{col}" opacity=".85"/>'
               f'<text x="{px:.1f}" y="{py+off:.1f}" class="pl" text-anchor="{anc}">{s}</text>')
yticks = ""
for v in [40, 25, 12, 1, -1, -10, -90, -253]:
    yy = Y(v)
    yticks += (f'<line x1="{PL}" y1="{yy:.1f}" x2="{W-PR}" y2="{yy:.1f}" stroke="#eee"/>'
               f'<text x="{PL-8}" y="{yy+4:.1f}" class="ax" text-anchor="end">{v}</text>')
xticks = ""
for v in [-25, -20, -15, -10, -5, 0, 5, 10]:
    xx = X(v)
    xticks += (f'<line x1="{xx:.1f}" y1="{PT}" x2="{xx:.1f}" y2="{H-PB}" stroke="#eee"/>'
               f'<text x="{xx:.1f}" y="{H-PB+18}" class="ax" text-anchor="middle">{v}</text>')
scatter = f'''<svg viewBox="0 0 {W} {H}" class="chart">
<rect x="{PL}" y="{PT}" width="{W-PL-PR}" height="{H-PT-PB}" fill="#fcfcfc" stroke="#e5e5e5"/>
{yticks}{xticks}
<line x1="{X(0):.1f}" y1="{PT}" x2="{X(0):.1f}" y2="{H-PB}" stroke="#333" stroke-width="1.4"/>
<line x1="{PL}" y1="{Y(0):.1f}" x2="{W-PR}" y2="{Y(0):.1f}" stroke="#333" stroke-width="1.4"/>
<text x="{X(10):.1f}" y="{Y(20):.1f}" class="ql" fill="#c81e2d">双高 · 主推</text>
<text x="{X(-26):.1f}" y="{Y(20):.1f}" class="ql" fill="#e08c00">脉冲 · 观察</text>
<text x="{X(10):.1f}" y="{Y(-200):.1f}" class="ql" fill="#1f7a8c">未兑现 · 候选</text>
<text x="{X(-26):.1f}" y="{Y(-200):.1f}" class="ql" fill="#16824a">双低 · 规避</text>
{''.join(pts)}
<text x="{PL+8}" y="{PT+18}" class="ax">纵轴：主力净流入（亿元，平方根压缩刻度）</text>
<text x="{W-PR-8}" y="{H-14}" class="ax" text-anchor="end">横轴：近 3 个月累计涨跌幅（%）</text>
</svg>'''

# ---------- 4) 相关矩阵热力图 ----------
CM = {}
for a, b in itertools.combinations(S, 2):
    c = corr(vec[a], vec[b]); CM[(a, b)] = c; CM[(b, a)] = c
order_s = sorted(S, key=lambda x: -ytd[x])
cell = 46
MW = 150 + cell * len(S) + 10
MH = 60 + cell * len(S)
cm_body = []
cm_body.append(f'<text x="8" y="16" class="ax">月度涨跌幅相关系数（n=9 期）</text>')
for j, b in enumerate(order_s):
    cm_body.append(f'<text x="{150 + j*cell + cell/2}" y="42" class="ax" text-anchor="middle">'
                   f'{b[:2]}</text>')
for i, a in enumerate(order_s):
    yy = 60 + i * cell
    cm_body.append(f'<text x="144" y="{yy + cell/2 + 4}" class="ax" text-anchor="end">{a}</text>')
    for j, b in enumerate(order_s):
        c = 1.0 if a == b else CM[(a, b)]
        t = min(abs(c), 1.0)
        fill = f"rgba(200,30,45,{0.15+0.8*t:.2f})" if c >= 0 else f"rgba(20,130,70,{0.15+0.8*t:.2f})"
        col = "#fff" if abs(c) > 0.62 else "#222"
        lab = "—" if a == b else f"{c:.2f}"
        cm_body.append(f'<rect x="{150 + j*cell}" y="{yy}" width="{cell-2}" height="{cell-2}" '
                       f'fill="{fill}"/><text x="{150 + j*cell + (cell-2)/2}" y="{yy + cell/2 + 4}" '
                       f'class="cm" fill="{col}" text-anchor="middle">{lab}</text>')
corr_svg = f'<svg viewBox="0 0 {MW} {MH+10}" class="chart">' + "".join(cm_body) + '</svg>'

# ---------- 5) 独立性排名 ----------
ind_rows = "\n".join(
    f'<tr><td>{s}</td><td class="num">{maxcorr[s]:.2f}</td><td>{indep[s][0]}</td>'
    f'<td>{"低关联 · 独立 α 候选" if maxcorr[s] < 0.75 else "高关联 · 定价同一 β"}</td></tr>'
    for s in sorted(S, key=lambda x: maxcorr[x]))

# ---------- 6) 象限解读 ----------
INTER = {
 "银行": "资金 +26 亿居次、近 3 月 +7.0%、振幅仅 17（全场最低）；最大相关系数 0.76，为<b>双高象限中最独立者</b>（全场最低是公用事业 0.59，但属脉冲象限）→ <b>真 α，唯一确认主推</b>；红利逻辑，工/建行创历史新高",
 "煤炭": "YTD +21.8% 全场最强，近 3 月 +5.9%；但资金仅「超 1 亿」（下限），<b>资金确认偏弱</b>；神华近 19 年新高",
 "石油石化": "近 3 月 +5.5%、YTD +6.0% 稳健；资金同为下限值，<b>待资金确认</b>；中国石油 18 年半新高",
 "交通运输": "资金 +12 亿但近 3 月 -2.9%、YTD -10.7% → <b>避险流入，非趋势</b>",
 "公用事业": "资金下限流入，近 3 月 -3.8%、YTD -0.3% → 防御性承接，趋势中性偏弱",
 "食品饮料": "资金 +22 亿（第 3）但近 3 月 -4.0%、YTD -14.0% → <b>典型防御性流入，基本面仍弱</b>",
 "国防军工": "资金第 1（39 亿）但近 3 月 -4.8%、YTD -24.4%、振幅 36 → <b>事件脉冲典型</b>；海上发射三项国标 11/1 实施催化",
 "电力设备": "资金下限流入但近 3 月 -24.0%、YTD -30.0%（全场最差）→ 流入与趋势严重背离，<b>不参与</b>",
 "计算机": "资金流出 + 近 3 月 -11.1% + YTD -24.4% → 趋势性走弱",
 "有色金属": "近 3 月 -15.7%、振幅 47 → 高位回落未止",
 "电子": "资金 -253 亿（最大流出）、近 3 月 -17.5%、振幅 89（极端）→ <b>泡沫破裂后未企稳</b>",
 "通信": "资金 -89 亿、近 3 月 -20.1% → 与电子高度同向（ρ=0.94），同一 β",
}
lowest = min(S, key=lambda x: maxcorr[x])
low_note = (f"<b>{lowest}</b> 与最相关对手的相关系数仅 {maxcorr[lowest]:.2f}（全场最低），"
            f"说明其月度波动与其他行业<b>不同源</b>，属独立 α；"
            f"而电子-通信 ρ=0.94、煤炭-石油石化 ρ=0.91、计算机-有色金属 ρ=0.94 —— "
            f"这些组合同涨同跌，同时持有属<b>假分散</b>。"
            f"⚠️ 注意：低相关只说明<b>波动不同源</b>，不等于值得配置（公用事业最独立却属脉冲象限）。")

# ---------- 7) 反方 ----------
counter = [
 ("价格景气 ≠ 基本面景气", "月度环比只反映定价边际，未含盈利/订单/产能；可能只是估值扩张。"),
 ("【时间维度】单日资金流是快照不是趋势", "且 2026-10-29 全市场超 4700 只个股下跌，当日资金流入被<b>避险属性</b>主导，而非景气趋势。"),
 ("幸存者偏差", "只列流入 Top 会忽略流出侧同量级信号（电子 -253 亿），单边叙事必然偏乐观。"),
 ("YTD 掩盖路径", "电子 YTD -1.8% 但年内振幅 89 个百分点（归一化曾冲高后回落）；银行振幅仅 17。"),
 ("指数编制失真", "板块指数多为市值加权，龙头单票可绑架行业读数（银行被四大行绑架）。"),
 ("事件脉冲不可外推", "国防军工 39 亿流入由海上发射三项国标（11/1 实施）催化，属一次性重定价。"),
 ("相关系数样本仅 9 期", "同涨同跌结论为指示性；n=9 时 ρ>0.7 才勉强可信，边缘值须存疑。"),
 ("缺失月误读", "接口省略 2026-01 月末 → 「02」列实为上年末至 2 月底的跨 2 月累计。"),
]
counter_html = "".join(f'<li><b>{t}</b> — {d}</li>' for t, d in counter)

quad_count = {}
for s in S: quad_count[quad[s]] = quad_count.get(quad[s], 0) + 1
main_push = [s for s in S if quad[s] == "双高(主推)"]

html = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>行业景气度横截面 · 回跑 v2（method-sector-momentum）</title>
<style>
:root{{--bd:#e5e5e5;--mut:#666;}}
body{{font:14px/1.65 -apple-system,"Segoe UI","Microsoft YaHei",sans-serif;color:#1a1a1a;background:#fff;margin:0;padding:32px 28px;max-width:1180px;margin:0 auto;}}
h1{{font-size:22px;margin:0 0 4px;}} h2{{font-size:17px;margin:34px 0 10px;padding-left:9px;border-left:4px solid #c81e2d;}}
h3{{font-size:14px;margin:20px 0 8px;color:#333;}}
.sub{{color:var(--mut);font-size:12.5px;margin-bottom:18px;}}
table{{border-collapse:collapse;width:100%;font-size:13px;margin:8px 0;}}
th,td{{border:1px solid var(--bd);padding:6px 9px;text-align:left;}}
th{{background:#fafafa;font-weight:600;}}
td.num,th.num{{text-align:right;font-variant-numeric:tabular-nums;}}
.hc{{text-align:center;font-size:12px;font-variant-numeric:tabular-nums;}}
.ytd{{font-weight:600;background:#fafafa;}}
.up{{color:#c81e2d;font-weight:600;}} .dn{{color:#16824a;font-weight:600;}}
.lb{{color:#c90;font-size:11px;}}
.q{{padding:2px 7px;border-radius:3px;font-size:12px;color:#fff;}}
.q.双高{{background:#c81e2d;}} .q.脉冲{{background:#e08c00;}} .q.未兑现{{background:#1f7a8c;}} .q.双低{{background:#16824a;}}
.chart{{width:100%;height:auto;border:1px solid var(--bd);background:#fff;}}
.pl{{font-size:11px;fill:#1a1a1a;}} .ax{{font-size:11px;fill:#666;}}
.cm{{font-size:11px;font-variant-numeric:tabular-nums;}}
.ql{{font-size:13px;font-weight:700;opacity:.55;}}
.note{{background:#fbfbfb;border:1px solid var(--bd);border-left:3px solid #999;padding:10px 14px;font-size:12.5px;color:#444;margin:10px 0;}}
.cards{{display:flex;gap:12px;flex-wrap:wrap;margin:14px 0;}}
.card{{border:1px solid var(--bd);border-radius:6px;padding:12px 16px;min-width:150px;}}
.card .k{{font-size:11.5px;color:var(--mut);}} .card .v{{font-size:20px;font-weight:700;}}
ol li{{margin:6px 0;}} .foot{{margin-top:34px;padding-top:12px;border-top:1px solid var(--bd);font-size:11.5px;color:#888;}}
</style></head><body>
<h1>行业景气度横截面跟踪 · 回跑 v2</h1>
<div class="sub">method-sector-momentum（→ drill）｜数据窗口 2025-12-31 → 2026-10-29｜资金流快照 2026-10-29（日频 T+1）｜12 个申万一级行业<br>
v2 补齐：M1 流出侧对照 · <b>M4 双维交叉四象限</b> · M5 同涨同跌与 β/α 剥离（v1 缺失项）</div>

<div class="cards">
<div class="card"><div class="k">覆盖行业</div><div class="v">12</div></div>
<div class="card"><div class="k">双高 · 主推</div><div class="v" style="color:#c81e2d">{quad_count.get("双高(主推)",0)}</div></div>
<div class="card"><div class="k">脉冲 · 观察</div><div class="v" style="color:#e08c00">{quad_count.get("脉冲(观察)",0)}</div></div>
<div class="card"><div class="k">双低 · 规避</div><div class="v" style="color:#16824a">{quad_count.get("双低(规避)",0)}</div></div>
<div class="card"><div class="k">主推名单</div><div class="v" style="font-size:15px">{"、".join(main_push)}</div></div>
</div>

<h2>M1 资金面横截面：流入 Top 与流出侧对照</h2>
<div class="note"><b>v2 新增：流出侧平衡视角。</b>当日全市场普跌（超 4700 只个股下跌，成交 1.57 万亿元）—— 只看流入 Top 会严重高估市场强度。<br>
⚠️ <b>已删除一处「全市场主力净流出总量」数字</b>：该数字在原始返回中<b>查无出处</b>（v1 为凭印象写入，非接口数据），经 `verify_numbers.py` 溯源校验后移除。<span class="lb">*</span> = 原文为「超 X 亿」，登记为<b>下限值</b>。</div>
<table><tr><th>行业</th><th>主力净流入</th><th class="num">近 3 月</th><th class="num">YTD</th><th>象限</th></tr>
{flow_rows(rows_in)}
</table>
<h3>流出侧（对照）</h3>
<table><tr><th>行业</th><th>主力净流入</th><th class="num">近 3 月</th><th class="num">YTD</th><th>象限</th></tr>
{flow_rows(rows_out)}
</table>
<div class="note"><b>⚠️ 概念层不是独立证据（2026-10-30 溯源校验后修正）：</b>行业层与概念层数字出自<b>同一篇资讯</b>（证券时报，返回中 3 篇为同源转载，均引 Wind），<b>不构成「≥2 路独立证据」，M1 门禁实际未满足</b>，须补独立数据源后方可宣称通过。数据本身如下：净流入 —— 军民融合 +40 亿、低空经济/商业航天/大飞机 各 +30 亿+、央企/卫星导航/中字头 各 +20 亿+；净流出 —— 华为概念/人工智能/消费电子 各 -100 亿+、光通信/半导体/5G 应用 各 -90 亿+。概念层与行业层同向。</div>

<h2>M3 月度景气度矩阵</h2>
<table><tr><th>行业</th>{period_head}<th class="num">YTD</th></tr>{heat_html}</table>
<div class="note">读数：横向看单行业全年起伏，纵向看某月哪些行业同步走强/走弱。<b>涨红跌绿</b>。
⚠️ 接口省略 2026-01 月末 → 「02」列为 <b>2025-12-31 → 2026-02-27 跨 2 月累计</b>，其余为真实月度环比；最后一列「10」为当月截至 10-29，非完整月。</div>

<h2>M4 双维交叉四象限（v2 核心新增）</h2>
<div class="note">纵轴 = 当期主力资金流向；横轴 = 近 3 个月累计涨跌幅（中期景气动量）。<b>v1 只给了两张并列图、未做交叉 = 未产出结论。</b></div>
{scatter}
<h3>象限归类表</h3>
<table><tr><th>象限</th><th>行业</th><th>资金</th><th class="num">近 3 月</th><th class="num">YTD</th><th class="num">振幅</th><th>解读</th></tr>
{''.join(f'<tr><td><span class="q {quad[s][:2]}">{quad[s]}</span></td><td><b>{s}</b></td>'
         f'<td class="{"up" if flow(s)>0 else "dn"}">{flow(s):+.0f} 亿</td>'
         f'<td class="num">{mom3[s]:+.1f}%</td><td class="num">{ytd[s]:+.1f}%</td>'
         f'<td class="num">{amp[s]:.0f}</td><td>{interpret}</td></tr>'
         for s, interpret in [(s, INTER[s]) for s in ranked])}
</table>
<div class="note"><b>⚠️ v2 关键修正：</b>「脉冲」象限多达 {quad_count.get("脉冲(观察)",0)} 个，且集中在当日流入但近 3 月下跌的行业（国防军工 39 亿 / 近 3 月 -4.8% / YTD -24.4%）。
原因是 <b>2026-10-29 全市场大跌（超 4700 只个股下跌），当日资金流被「避险属性」主导而非景气趋势</b>。
→ 结论：单日资金流方向<b>必须与当日大盘状态交叉解读</b>，否则会把避险流入误读为趋势买入。</div>

<h2>M5 同涨同跌与 β/α 剥离</h2>
<h3>月度涨跌幅相关系数矩阵</h3>
{corr_svg}
<div class="note">高相关（红深）说明两行业定价<b>同一个 β</b>，同时持有 = 假分散。</div>
<h3>独立性排名（与最相关对手的相关系数）</h3>
<table><tr><th>行业</th><th class="num">最大相关系数</th><th>最相关对手</th><th>判定</th></tr>{ind_rows}</table>
<div class="note"><b>读数：</b>{low_note}</div>

<h2>R1 反方论点（G4 · 8 条）</h2>
<ol>{counter_html}</ol>

<h2>口径登记</h2>
<table><tr><th>项</th><th>口径</th></tr>
<tr><td>资金流</td><td>主力净流入（大单+特大单），单位 ¥ 亿元；<b>日频 T+1，无原生周度聚合</b>，本表为 2026-10-29 单日快照</td></tr>
<tr><td>近一周口径</td><td>严格 N 日累计须逐日拉取求和；本次沿用 v1 的同交易日快照口径，未变更数据窗口</td></tr>
<tr><td>月度景气</td><td>板块指数月底收盘环比（%）；基准 2025-12-31 = 100</td></tr>
<tr><td>近 3 月动量</td><td>2026-07-31 → 2026-10-29 累计涨跌幅</td></tr>
<tr><td>行业分类</td><td>申万一级（12 个代表行业，非全部 31 个）</td></tr>
<tr><td>数据来源</td><td>NeoData 统一行情（月 K）+ 证券时报/Wind 资金流资讯（3 篇同源互证）</td></tr>
</table>

<div class="foot">回跑约定：数据窗口不变、不新增抓取（月度序列复用 v1；资金流重拉同一交易日 2026-10-29 以补登结构化字段）。<br>
⚠️ 由 AI 基于公开数据整理，仅供参考，不构成投资建议。</div>
</body></html>'''
open("industry_sentiment_2026_v2.html", "w", encoding="utf-8").write(html)
print("v2 written, size", len(html))
print("quad:", quad_count)
print("main push:", main_push)
print("indep low:", sorted([(s, maxcorr[s]) for s in S], key=lambda x: x[1])[:4])
