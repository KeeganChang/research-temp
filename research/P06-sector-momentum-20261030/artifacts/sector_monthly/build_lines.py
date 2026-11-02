# -*- coding: utf-8 -*-
"""景气度走势折线图：横轴 = 相对月份，纵轴 = 景气度，每个行业一条线。
双模式：① 归一化景气度（基准 2025-12-31=100）② 月度环比景气度（%）
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

A = json.load(open("analysis_v2.json", encoding="utf-8"))
S, PERIODS = A["sectors"], A["periods"]
norm = {s: [v for _, v in A["norm"][s]] for s in S}   # 10 点
mon = {s: [v for _, v in A["mon"][s]] for s in S}      # 9 区间
dates = [d for d, _ in A["norm"][S[0]]]

# 横轴标签：相对月份 T0..T9 + 实际月份
rel_norm = [f"T{i}" for i in range(len(dates))]
month_norm = [d[:7].replace("-", "/") for d in dates]
month_mon = [p.replace("-", "/") for p in PERIODS]
rel_mon = [f"T{i+1}" for i in range(len(PERIODS))]

COLORS = ["#c81e2d", "#16824a", "#1f6fb4", "#e08c00", "#7a4fbf", "#0f8b8d",
          "#b5651d", "#5a6b7d", "#d14d8a", "#3f8f2f", "#8a6d1f", "#2f4f8f"]
order = sorted(S, key=lambda x: -A["ytd"][x])
cmap = {s: COLORS[i % len(COLORS)] for i, s in enumerate(order)}

payload = {
    "sectors": order, "colors": cmap,
    "relNorm": rel_norm, "monthNorm": month_norm, "norm": norm,
    "relMom": rel_mon, "monthMom": month_mon, "mom": mon,
    "ytd": A["ytd"], "quad": A["quad"],
}

legend = "".join(
    f'<button class="lg" data-s="{s}" style="border-color:{cmap[s]}">'
    f'<i style="background:{cmap[s]}"></i>{s} <b>{A["ytd"][s]:+.1f}%</b></button>' for s in order)

html = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>行业景气度走势 · 相对月份 × 景气度</title>
<style>
body{{font:14px/1.6 -apple-system,"Segoe UI","Microsoft YaHei",sans-serif;color:#1a1a1a;background:#fff;margin:0;padding:28px 26px;max-width:1120px;margin:0 auto;}}
h1{{font-size:21px;margin:0 0 4px;}} .sub{{color:#666;font-size:12.5px;margin-bottom:16px;}}
.bar{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:10px 0 6px;}}
.tab{{padding:6px 14px;border:1px solid #ccc;background:#fff;border-radius:5px;cursor:pointer;font-size:13px;}}
.tab.on{{background:#c81e2d;color:#fff;border-color:#c81e2d;font-weight:600;}}
.lgs{{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 14px;}}
.lg{{display:inline-flex;align-items:center;gap:5px;padding:3px 9px;border:1.5px solid;border-radius:14px;
background:#fff;cursor:pointer;font-size:12px;}}
.lg i{{width:11px;height:11px;border-radius:50%;display:inline-block;}}
.lg.off{{opacity:.32;}}
.lg b{{font-weight:600;font-variant-numeric:tabular-nums;}}
#wrap{{border:1px solid #e5e5e5;border-radius:6px;background:#fff;}}
.note{{background:#fbfbfb;border:1px solid #e5e5e5;border-left:3px solid #999;padding:10px 14px;font-size:12.5px;color:#444;margin:12px 0;}}
.tip{{font-size:11px;fill:#1a1a1a;}}
.ax{{font-size:11px;fill:#666;}} .gl{{stroke:#eee;}}
.gl0{{stroke:#333;stroke-width:1.3;}}
.foot{{margin-top:22px;padding-top:10px;border-top:1px solid #e5e5e5;font-size:11.5px;color:#888;}}
</style></head><body>
<h1>行业景气度走势（相对月份 × 景气度）</h1>
<div class="sub">method-sector-momentum · P06 ｜ 12 个申万一级行业 ｜ 数据窗口 2025-12-31 → 2026-10-29</div>

<div class="bar">
<button class="tab on" id="t-norm">① 归一化景气度（基准 100）</button>
<button class="tab" id="t-mom">② 月度环比景气度（%）</button>
<span style="color:#888;font-size:12px">点击图例可隐藏/显示某行业 · 悬停圆点看数值</span>
</div>
<div class="lgs">{legend}</div>
<div id="wrap"></div>

<div class="note"><b>横轴</b>为相对月份：T0 = 2025-12-31（基准月），T1 = 2026-02，… T9 = 2026-10（截至 10-29）。
<b>纵轴</b>可切换两种景气度口径 —— ① 水平值（归一化指数，看全年轨迹与分化）② 变化率（月度环比，看边际景气）。
⚠️ 接口省略 2026-01 月末 → <b>T1 为「2025-12-31 → 2026-02-27」跨 2 月累计</b>，故环比模式下 T1 一段不代表单月景气；T9 为当月截至 10-29，非完整月。</div>
<div class="foot">由 AI 基于 NeoData 公开数据整理，仅供参考，不构成投资建议。</div>

<script>
const D = {json.dumps(payload, ensure_ascii=False)};
let mode = "norm", hidden = new Set();
const W=1060, H=560, PL=62, PR=24, PT=26, PB=72;

function scale(vals){{
  let lo=Math.min(...vals), hi=Math.max(...vals);
  const pad=(hi-lo)*0.08||1; lo-=pad; hi+=pad;
  if(mode==="norm" && lo>95) lo=95; if(mode==="norm" && hi<105) hi=105;
  return {{lo,hi, y:v=>H-PB-(v-lo)/(hi-lo)*(H-PT-PB)}};
}}
function render(){{
  const isNorm = mode==="norm";
  const labels = isNorm? D.relNorm : D.relMom;
  const months = isNorm? D.monthNorm : D.monthMom;
  const data = isNorm? D.norm : D.mom;
  const all = [].concat(...D.sectors.map(s=>data[s]));
  const sc = scale(all);
  const n = labels.length;
  const X = i => PL + (n===1?0:i/(n-1))*(W-PL-PR);

  let g="";
  // 横向网格 + 纵轴刻度
  for(let k=0;k<=6;k++){{
    const v = sc.lo + (sc.hi-sc.lo)*k/6, y = sc.y(v);
    g += `<line class="gl${{Math.abs(v)<0.001&&!isNorm?' gl0':''}}" x1="${{PL}}" y1="${{y.toFixed(1)}}" x2="${{W-PR}}" y2="${{y.toFixed(1)}}"/>`;
    g += `<text class="ax" x="${{PL-8}}" y="${{(y+4).toFixed(1)}}" text-anchor="end">${{v.toFixed(isNorm?0:1)}}</text>`;
  }}
  if(isNorm){{ const y0=sc.y(100); g+=`<line class="gl0" stroke-dasharray="5 4" x1="${{PL}}" y1="${{y0.toFixed(1)}}" x2="${{W-PR}}" y2="${{y0.toFixed(1)}}"/>`;
    g+=`<text class="ax" x="${{W-PR}}" y="${{(y0-6).toFixed(1)}}" text-anchor="end">基准 100</text>`; }}
  // 横轴
  for(let i=0;i<n;i++){{
    g += `<text class="ax" x="${{X(i).toFixed(1)}}" y="${{H-PB+18}}" text-anchor="middle">${{labels[i]}}</text>`;
    g += `<text class="ax" x="${{X(i).toFixed(1)}}" y="${{H-PB+34}}" text-anchor="middle" style="font-size:10px">${{months[i]}}</text>`;
  }}
  g += `<text class="ax" x="${{PL}}" y="${{H-14}}">纵轴：${'{'}isNorm?"归一化景气度指数（2025-12-31 = 100）":"月度环比景气度（%）"{'}'}</text>`;
  // 折线
  D.sectors.forEach(s=>{{
    if(hidden.has(s)) return;
    const pts = data[s].map((v,i)=>`${{X(i).toFixed(1)}},${{sc.y(v).toFixed(1)}}`).join(" ");
    g += `<polyline points="${{pts}}" fill="none" stroke="${{D.colors[s]}}" stroke-width="2" opacity=".9"/>`;
    data[s].forEach((v,i)=>{{
      g += `<circle cx="${{X(i).toFixed(1)}}" cy="${{sc.y(v).toFixed(1)}}" r="3.2" fill="${{D.colors[s]}}">`
        + `<title>${{s}} · ${{labels[i]}}（${{months[i]}}）：${{isNorm? v.toFixed(1) : (v>=0?"+":"")+v.toFixed(1)+"%"}}</title></circle>`;
    }});
    const lastV = data[s][n-1];
    g += `<text class="tip" x="${{(X(n-1)+7).toFixed(1)}}" y="${{(sc.y(lastV)+4).toFixed(1)}}" fill="${{D.colors[s]}}">${{s}}</text>`;
  }});
  document.getElementById("wrap").innerHTML =
    `<svg viewBox="0 0 ${{W}} ${{H}}" style="width:100%;height:auto">${{g}}</svg>`;
}}
document.getElementById("t-norm").onclick = e=>{{mode="norm";e.target.classList.add("on");
  document.getElementById("t-mom").classList.remove("on");render();}};
document.getElementById("t-mom").onclick = e=>{{mode="mom";e.target.classList.add("on");
  document.getElementById("t-norm").classList.remove("on");render();}};
document.querySelectorAll(".lg").forEach(b=>b.onclick=()=>{{
  const s=b.dataset.s; hidden.has(s)?hidden.delete(s):hidden.add(s);
  b.classList.toggle("off"); render();}});
render();
</script></body></html>'''

open("industry_momentum_lines.html", "w", encoding="utf-8").write(html)
print("lines written, size", len(html), "| sectors", len(order))
