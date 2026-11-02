#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a self-contained HTML research note: weekly net-inflow Top list + 12-month industry sentiment."""
import json, os, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
series = json.load(open(os.path.join(BASE, "series.json"), encoding="utf-8"))

SECTOR_ORDER = ["银行","煤炭","石油石化","交通运输","公用事业","食品饮料",
                "电子","通信","计算机","电力设备","有色金属","国防军工"]

# month-end dates in order (Jan omitted by API)
DATES = ["2025-12-31","2026-02-27","2026-03-31","2026-04-30","2026-05-29",
         "2026-06-30","2026-07-31","2026-08-31","2026-09-30","2026-10-29"]
MLABEL = ["25-12","26-02","26-03","26-04","26-05","26-06","26-07","26-08","26-09","26-10"]

# ---- compute MoM returns and YTD ----
mom = {}      # sector -> list aligned to DATES (index0=None baseline; idx1 = Feb vs Dec baseline cumulative)
ytd = {}
norm = {}     # normalized to 100 at 2025-12-31
for s in SECTOR_ORDER:
    closes = [series[s][d] for d in DATES]
    n = [c/closes[0]*100 for c in closes]
    norm[s] = n
    r = [None]
    for i in range(1, len(closes)):
        r.append(closes[i]/closes[i-1]-1)
    mom[s] = r
    ytd[s] = closes[-1]/closes[0]-1

# ---- helpers ----
def pct(x, signed=True):
    if x is None: return "—"
    v = x*100
    return f"{'+' if v>0 else ''}{v:.1f}%"

# ---- colors (categorical line palette) ----
LINE_COLORS = ["#1f77b4","#d62728","#2ca02c","#9467bd","#8c564b","#e377c2",
               "#17becf","#bcbd22","#ff7f0e","#393b79","#7f7f7f","#1a9850"]
SECTOR_COLOR = {s:LINE_COLORS[i] for i,s in enumerate(SECTOR_ORDER)}

# 涨红跌绿 for value coloring
def val_color(v, alpha=0.85):
    if v is None: return "transparent"
    if v>=0:
        inten = min(1.0, abs(v)/0.25)
        return f"rgba(214,40,40,{0.15+0.75*inten})"
    else:
        inten = min(1.0, abs(v)/0.25)
        return f"rgba(39,166,96,{0.15+0.75*inten})"

# =================== HEATMAP (HTML table) ===================
hm_header = "".join(f"<th>{m}</th>" for m in MLABEL[1:])  # skip baseline col for MoM grid
hm_rows = ""
for s in SECTOR_ORDER:
    cells = ""
    for i in range(1, len(DATES)):
        v = mom[s][i]
        cells += f'<td style="background:{val_color(v)};color:#111;text-align:center;font-weight:600">{pct(v)}</td>'
    hm_rows += f"<tr><th style='text-align:right;padding-right:8px'>{s}</th>{cells}</tr>"

# =================== LINE CHART SVG ===================
W, H = 960, 460
ML, MR, MT, MB = 48, 150, 30, 36
plot_w = W-ML-MR
plot_h = H-MT-MB
alln = [v for s in SECTOR_ORDER for v in norm[s]]
ymin, ymax = min(alln), max(alln)
pad = (ymax-ymin)*0.08
ymin, ymax = ymin-pad, ymax+pad
def xpos(i): return ML + plot_w*i/(len(DATES)-1)
def ypos(v): return MT + plot_h*(1-(v-ymin)/(ymax-ymin))

# y gridlines
ygrid = ""
for g in range(0,5):
    val = ymin + (ymax-ymin)*g/4
    y = ypos(val)
    ygrid += f'<line x1="{ML}" y1="{y:.1f}" x2="{ML+plot_w}" y2="{y:.1f}" stroke="#eee"/>'
    ygrid += f'<text x="{ML-6}" y="{y+4:.1f}" font-size="10" fill="#888" text-anchor="end">{val:.0f}</text>'
# x labels
xlab = ""
for i,m in enumerate(MLABEL):
    x = xpos(i)
    xlab += f'<text x="{x:.1f}" y="{MT+plot_h+18}" font-size="10" fill="#666" text-anchor="middle">{m}</text>'
# polylines
lines = ""
for s in SECTOR_ORDER:
    pts = " ".join(f"{xpos(i):.1f},{ypos(norm[s][i]):.1f}" for i in range(len(DATES)))
    lines += f'<polyline points="{pts}" fill="none" stroke="{SECTOR_COLOR[s]}" stroke-width="1.6" opacity="0.9"/>'
# 100 baseline
base_y = ypos(100)
base_line = f'<line x1="{ML}" y1="{base_y:.1f}" x2="{ML+plot_w}" y2="{base_y:.1f}" stroke="#999" stroke-dasharray="4 3"/>'
base_txt = f'<text x="{ML+plot_w+4}" y="{base_y+3:.1f}" font-size="9" fill="#999">100</text>'
# legend (right column)
legend = '<g font-size="11">'
ly = MT+4
for s in SECTOR_ORDER:
    legend += f'<rect x="{ML+plot_w+12}" y="{ly:.1f}" width="11" height="11" fill="{SECTOR_COLOR[s]}"/>'
    legend += f'<text x="{ML+plot_w+28}" y="{ly+10:.1f}" fill="#333">{s}</text>'
    ly += 18
legend += '</g>'
line_svg = f'''<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg">
<text x="{ML}" y="16" font-size="12" fill="#333" font-weight="600">归一化行业指数（2025-12-31 = 100）</text>
{ygrid}{base_line}{xlab}{lines}{base_txt}{legend}
</svg>'''

# =================== YTD BAR CHART SVG ===================
sorted_ytd = sorted(SECTOR_ORDER, key=lambda s: ytd[s])
BW, BH = 520, 360
bx0, by0, bwid, bht = 90, 26, 360, 24
bars = ""
maxabs = max(abs(ytd[s]) for s in SECTOR_ORDER)
for i,s in enumerate(sorted_ytd):
    v = ytd[s]*100
    w = abs(v)/maxabs*bwid
    y = by0 + i*(bht+4)
    col = "#d62728" if v>=0 else "#27a660"
    if v>=0:
        bars += f'<rect x="{bx0:.1f}" y="{y:.1f}" width="{w:.1f}" height="{bht}" fill="{col}"/>'
        bars += f'<text x="{bx0+w+6:.1f}" y="{y+bht-6:.1f}" font-size="11" fill="#333">{v:+.1f}%</text>'
    else:
        bars += f'<rect x="{bx0-w:.1f}" y="{y:.1f}" width="{w:.1f}" height="{bht}" fill="{col}"/>'
        bars += f'<text x="{bx0-w-6:.1f}" y="{y+bht-6:.1f}" font-size="11" fill="#333" text-anchor="end">{v:+.1f}%</text>'
    bars += f'<text x="{bx0-8:.1f}" y="{y+bht-6:.1f}" font-size="11" fill="#333" text-anchor="end">{s}</text>'
# zero axis
bars += f'<line x1="{bx0:.1f}" y1="{by0-6:.1f}" x2="{bx0:.1f}" y2="{by0+len(sorted_ytd)*(bht+4):.1f}" stroke="#999"/>'
bar_svg = f'''<svg viewBox="0 0 {BW} {BH}" width="100%" xmlns="http://www.w3.org/2000/svg">
<text x="10" y="16" font-size="12" fill="#333" font-weight="600">年初至今收益（2025-12-31 → 2026-10-29）</text>
{bars}</svg>'''

# =================== WEEKLY NET INFLOW TABLE ===================
# Source: 证券时报/Wind 2026-10-29 daily 申万一级 main-force net inflow
inflow = [
    ("国防军工","逾 39","逆市领涨，海上发射国标11/1实施催化"),
    ("银行","逾 26","高股息红利，工行/建行等创历史新高"),
    ("食品饮料","逾 22","防御+消费修复"),
    ("交通运输","逾 12",""),
    ("公用事业","超 1","红利资产"),
    ("煤炭","超 1","高股息，中国神华近19年新高"),
    ("石油石化","超 1","中国石油创18年半新高"),
    ("电力设备","超 1",""),
]
# biggest outflows (balance)
outflow = [
    ("电子","-253","AI硬件链抛压最重"),
    ("通信","-89",""),
    ("计算机","-10+",""),
    ("有色金属","-10+",""),
    ("机械设备","-10+",""),
]
inflow_rows = "".join(f"<tr><td>{i+1}</td><td>{n}</td><td style='color:#d62728;font-weight:700'>{v}</td><td>{note}</td></tr>" for i,(n,v,note) in enumerate(inflow))
outflow_rows = "".join(f"<tr><td>{n}</td><td style='color:#27a660;font-weight:700'>{v}</td><td>{note}</td></tr>" for (n,v,note) in outflow)

# 近一周价格动量 (5日涨跌幅, 申万二级/概念, 2026-10-29 板块涨跌排行)
momentum = [
    ("航天装备Ⅱ","+8.52%"),("保险Ⅱ","+4.60%"),("城商行Ⅱ","+3.67%"),
    ("煤炭开采","+2.54%"),("国有大型银行Ⅱ","+2.27%"),("风电设备","+0.73%"),
]
mom_rows = "".join(f"<tr><td>{n}</td><td style='color:#d62728;font-weight:700'>{v}</td></tr>" for n,v in momentum)

# =================== ASSEMBLE HTML ===================
html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>近一周行业资金净流入 Top & 近一年月度行业景气度</title>
<style>
 body{{font-family:-apple-system,'Segoe UI','Microsoft YaHei',sans-serif;margin:0;background:#f6f7f9;color:#222}}
 .wrap{{max-width:1080px;margin:0 auto;padding:28px 22px 60px}}
 h1{{font-size:22px;margin:0 0 4px}}
 .sub{{color:#888;font-size:13px;margin-bottom:18px}}
 .card{{background:#fff;border:1px solid #ececec;border-radius:10px;padding:18px 20px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,.04)}}
 h2{{font-size:16px;margin:0 0 12px;border-left:4px solid #d62728;padding-left:10px}}
 table{{border-collapse:collapse;width:100%;font-size:13px}}
 th,td{{border:1px solid #e6e6e6;padding:6px 8px}}
 th{{background:#fafafa;font-weight:600}}
 .note{{font-size:12px;color:#777;line-height:1.6;background:#fbfbfb;border:1px dashed #e0e0e0;border-radius:8px;padding:10px 12px;margin-top:10px}}
 .grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
 @media(max-width:760px){{.grid2{{grid-template-columns:1fr}}}}
 .legend-note{{font-size:12px;color:#666;margin-top:8px}}
 .pos{{color:#d62728;font-weight:700}} .neg{{color:#27a660;font-weight:700}}
</style></head>
<body><div class="wrap">
<h1>近一周行业资金净流入 Top &amp; 近一年月度行业景气度</h1>
<div class="sub">数据源：NeoData 金融数据（板块资金主力统计 / 板块历史行情）· 截至 2026-10-29 · 研究员：严研行（market-researcher）</div>

<div class="card">
<h2>一、近一周行业主力资金净流入（申万一级，最新交易日 2026-10-29）</h2>
<p style="font-size:13px;color:#555;margin:0 0 10px">说明：NeoData「板块资金主力统计」为<b>日频（T+1）</b>口径，未暴露原生“周度聚合”。下表为最新交易日（2026-10-29，周四）申万一级行业主力资金净流入，是“近一周”最权威的可用资金流快照；当日全市场主力净流出约 500 亿元，资金高度集中于防御/红利与事件驱动板块。</p>
<table>
<tr><th>排名</th><th>行业</th><th>主力净流入（亿元）</th><th>备注</th></tr>
{inflow_rows}
</table>
<div class="note">当日净流出居前的行业（平衡视角）：{ "；".join(f"{n} {v}" for n,v,_ in outflow) }。概念层面净流入更强：军民融合 +40亿、低空经济/商业航天/大飞机 各 +30亿、央企/卫星导航/中字头 各 +20亿、跨境支付/白酒/太空算力 各 +10亿。</div>

<h3 style="font-size:14px;margin:18px 0 8px">附：近一周价格动量（5日涨跌幅，申万二级/概念，2026-10-29）</h3>
<table><tr><th>板块</th><th>5日涨跌幅</th></tr>{mom_rows}</table>
<div class="note">⚠️ 口径提示：上方“净流入”为<b>资金流</b>（日频快照），此表为<b>价格动量</b>（5日），二者维度不同，请勿混用。如需严格“近5个交易日累计净流入”，需逐日拉取板块资金主力统计后求和——可另行补做。</div>
</div>

<div class="card">
<h2>二、近一年月度行业景气度（2025-12 → 2026-10，价格景气代理）</h2>
<p style="font-size:13px;color:#555;margin:0 0 10px">方法：以申万一级行业指数<b>月底收盘</b>的<b>月度环比涨跌幅</b>作为“行业景气度”的代理指标（市场定价对景气的边际投票）。红色=景气上行（涨），绿色=景气下行（跌），色深表强度。数据来自 NeoData 板块历史行情（前复权）。<b>注：接口省略 2026-01 月末数据，故“26-02”列为 2025-12-31→2026-02-27 的累计收益，其余月份为真实月度环比。</b></p>
<table>
<tr><th>行业 \\ 月份</th>{hm_header}</tr>
{hm_rows}
</table>
<div class="legend-note">读数：横向看单行业全年起伏，纵向（列）看某月哪些行业同步走强/走弱。2026 年主线为“红利防御（银行/煤炭/石油石化）持续占优、公用事业基本持平，TMT（电子/通信/计算机）在 6 月见顶后剧烈回撤，国防军工 10 月事件驱动反弹”。</div>
</div>

<div class="card">
<h2>三、归一化行业指数走势（全年轨迹）</h2>
{line_svg}
<div class="legend-note">以 2025-12-31 = 100 归一。可见：电子/通信在 2026 上半年泡沫式冲高（6 月电子归一化达 ~186），下半年崩塌；银行稳步抬升至 10 月新高、煤炭 8 月见阶段高点后回落仍为全年最强；国防军工 10 月单月脉冲。</div>
</div>

<div class="card">
<h2>四、年初至今收益（2025-12-31 → 2026-10-29）</h2>
<div class="grid2">
<div>{bar_svg}</div>
<div style="font-size:13px;color:#555;align-self:center">
<p><b>赢家（红利三杰）：</b>煤炭 +21.8%、石油石化 +6.0%、银行 +4.8%，公用事业基本持平（-0.3%）。高股息+低估值在 2026 年“资产荒+风格再平衡”中持续占优。</p>
<p><b>输家：</b>电力设备 -30.0%、国防军工 -24.4%、计算机 -24.4%、有色金属 -22.0%、食品饮料 -14.0%、交通运输 -10.7%、通信 -7.7%、电子 -1.7%（振幅极大，6 月归一化曾达 ~186）。</p>
<p>全年呈极端 <b>K 型分化</b>：红利价值抗跌，前期 TMT/制造高位回撤惨烈。</p>
</div>
</div>
</div>

<div class="card">
<h2>五、结论与反方论点</h2>
<p style="font-size:13px;line-height:1.7">
<b>结论：</b>① 近一周资金明显“弃高估值成长、抱红利防御+事件驱动”——国防军工（海上发射国标催化）、银行、食品饮料获主力净流入居前，电子/通信遭巨额净流出。② 近一年行业景气度呈现“红利防御持续占优、TMT 6 月见顶后崩塌、军工 10 月脉冲”的结构，年初至今红利板块正收益、成长/制造大幅负收益。
</p>
<p style="font-size:13px;line-height:1.7"><b>反方 / 风险：</b>① 红利板块（银行/煤炭/石油石化）已创多年新高，估值与拥挤度风险上升，若利率上行或经济超预期复苏，防御逻辑弱化。② TMT 的剧烈回撤包含“超跌反弹”机会，但需外部科技股企稳与量能回升确认，否则仍是下行趋势。③ 国防军工的净流入高度依赖 11-01 国标落地等事件催化，事件兑现后易回吐。④ 月度景气度以“价格”为代理，未纳入盈利/订单等基本面景气，且 1 月数据缺失，存在刻画偏差。</p>
</div>

<div class="note">
<b>数据来源与免责：</b>行业资金流与指数月线均来自 NeoData 金融数据服务（板块资金主力统计 / 板块历史行情，前复权），引用自 Wind/证券时报等公开披露。部分“净流入”为公开报道披露的“逾/超”区间值，精确逐日数据未完全暴露，已标注。本页由 AI 基于公开信息整理，<b>仅供参考，不构成任何投资建议</b>。投资有风险，决策需谨慎。
</div>
</div></body></html>"""

out = os.path.join(BASE, "industry_sentiment_2026.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print("WROTE", out, "bytes=", len(html))
# also dump computed metrics for the note
metrics = {s:{"ytd":ytd[s],"mom_last":mom[s][-1]} for s in SECTOR_ORDER}
print(json.dumps(metrics, ensure_ascii=False, indent=2))
