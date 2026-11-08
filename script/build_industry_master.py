# -*- coding: utf-8 -*-
import os
import sys
sys.stdout.reconfigure(encoding="utf-8")
"""生成「行业分析母版.pptx」—— 真·幻灯片母版（v3：优化版结构 + 森林绿主色系）。

变更点（相对 v2）：
- 内容页 chrome 采用「优化版」结构：标题栏 / 总结栏 改为整幅宽浅绿占位符
  （去掉原竖条 + 分隔线 + 深色总结块的冗余装饰），并在栏上下加森林绿品牌细线
- 主色系 = 森林绿（标准 #228B22），并同步修改 theme1 主题色
- 四大板块区分色：森林绿 + 3 个协调自然色（松绿 / 赤陶 / 赭金）
- 封面 / 尾页 / 各强调元素（时间轴·流程·大数字·VS）统一森林绿
- 板块内容页标题栏/总结栏统一浅绿主色（不随板块变色，保持主色系一致）

运行：uv run --with python-pptx python script/build_industry_master.py
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.oxml.ns import qn
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.opc.packuri import PackURI
from pptx.parts.slide import SlideLayoutPart
from copy import deepcopy
from lxml import etree

# ---------- 调色板：森林绿主色系 + 3 协调自然色 ----------
FG      = RGBColor(0x22, 0x8B, 0x22)   # 标准森林绿（主色）
FG_DARK = RGBColor(0x14, 0x5A, 0x14)   # 深绿（尾页背景 / 深底）
FG_TINT = RGBColor(0xE9, 0xF3, 0xE9)   # 浅绿 tint（标题栏 / 总结栏底）
# 三大协调自然色（板块区分）
TEALG   = RGBColor(0x2E, 0x7D, 0x6B)   # 松绿（用户画像）
TERRA   = RGBColor(0xB5, 0x53, 0x2F)   # 赤陶（竞品分析）
OCHRE   = RGBColor(0xC0, 0x88, 0x2E)   # 赭金（市场措施）
# 文字 / 中性
INK     = RGBColor(0x2B, 0x2B, 0x28)   # 主文字（深，略暖）
INK2    = RGBColor(0x5A, 0x57, 0x50)   # 次文字
MUTE    = RGBColor(0x7C, 0x79, 0x72)   # 占位提示灰
PANEL   = RGBColor(0xF3, 0xF4, 0xF0)   # 卡片底（微绿灰中性）
LINE    = RGBColor(0xD9, 0xD6, 0xCE)   # 卡片描边
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
# 语义色（问题/对策）—— 保留红/绿语义，绿侧对齐森林绿
PROB_FILL = RGBColor(0xF6, 0xE9, 0xE3); PROB_LINE = RGBColor(0xE0, 0xB4, 0x9E)
SOL_FILL  = RGBColor(0xE8, 0xF3, 0xE8); SOL_LINE  = RGBColor(0x9F, 0xC2, 0xA8)
FONT_CN = "微软雅黑"
EMU = 914400

# ---------- 几何（英寸，16:9） ----------
W, H   = 13.333, 7.5
ML, MR = 0.5, 0.5
CW     = W - ML - MR
T_TITLE, H_TITLE = 0.30, 0.92
C_TOP, C_H      = 1.55, 4.80
S_TOP, S_H      = 6.55, 0.72

# ---------- 低层：直接写 XML 到 shape tree（版式/幻灯片通用） ----------
def _hex(c):
    return str(c).lstrip('#').upper()

def _sp_tree(el):
    st = el.find(qn('p:cSld') + '/' + qn('p:spTree'))
    if st is None:
        st = el.find('.//' + qn('p:spTree'))
    return st

def _st(x):
    if hasattr(x, '_spTree'):
        return x._spTree
    if hasattr(x, 'tag') and x.tag == qn('p:spTree'):
        return x
    el = x._element if hasattr(x, '_element') else x
    return _sp_tree(el)

def _next_cid(spTree):
    ids = [int(e.get('id')) for e in spTree.iter(qn('p:cNvPr')) if e.get('id')]
    return (max(ids) if ids else 1) + 1

def _add_shape(spTree, l, t, w, h, geom='rect', fill=None, line=None, line_w=0.75, ph=None):
    cid = _next_cid(spTree)
    sp = etree.SubElement(spTree, qn('p:sp'))
    nv = etree.SubElement(sp, qn('p:nvSpPr'))
    cnv = etree.SubElement(nv, qn('p:cNvPr')); cnv.set('id', str(cid)); cnv.set('name', 'Shape %d' % cid)
    etree.SubElement(nv, qn('p:cNvSpPr'))
    nvpr = etree.SubElement(nv, qn('p:nvPr'))
    if ph is not None:
        p = etree.SubElement(nvpr, qn('p:ph')); p.set('idx', str(ph[1]))
        if ph[0]: p.set('type', ph[0])
    sppr = etree.SubElement(sp, qn('p:spPr'))
    xfrm = etree.SubElement(sppr, qn('a:xfrm'))
    off = etree.SubElement(xfrm, qn('a:off')); off.set('x', str(int(round(l*EMU)))); off.set('y', str(int(round(t*EMU))))
    ext = etree.SubElement(xfrm, qn('a:ext')); ext.set('cx', str(int(round(w*EMU)))); ext.set('cy', str(int(round(h*EMU))))
    g = etree.SubElement(sppr, qn('a:prstGeom')); g.set('prst', geom); etree.SubElement(g, qn('a:avLst'))
    if fill is not None:
        sf = etree.SubElement(sppr, qn('a:solidFill')); etree.SubElement(sf, qn('a:srgbClr')).set('val', _hex(fill))
    else:
        etree.SubElement(sppr, qn('a:noFill'))
    if line is not None:
        ln = etree.SubElement(sppr, qn('a:ln')); ln.set('w', str(int(round(line_w*12700))))
        sf = etree.SubElement(ln, qn('a:solidFill')); etree.SubElement(sf, qn('a:srgbClr')).set('val', _hex(line))
    else:
        etree.SubElement(sppr, qn('a:ln')).set('w', '0')
    return sp

def _add_text(spTree, l, t, w, h, text='', size=12, color=INK, bold=False, italic=False,
              align='l', anchor='tt', fill=None, line=None, line_w=0.75, rounded=False, ph=None):
    geom = 'roundRect' if rounded else 'rect'
    sp = _add_shape(spTree, l, t, w, h, geom=geom, fill=fill, line=line, line_w=line_w, ph=ph)
    tb = etree.SubElement(sp, qn('p:txBody'))
    bp = etree.SubElement(tb, qn('a:bodyPr')); bp.set('wrap', 'square')
    bp.set('lIns', '72000'); bp.set('tIns', '36000'); bp.set('rIns', '72000'); bp.set('bIns', '36000')
    if anchor: bp.set('anchor', anchor)
    etree.SubElement(bp, qn('a:noAutofit'))
    etree.SubElement(tb, qn('a:lstStyle'))
    for line0 in (text or '').split('\n'):
        p = etree.SubElement(tb, qn('a:p'))
        if align: p.set('algn', align)
        if line0 != '':
            r = etree.SubElement(p, qn('a:r'))
            rpr = etree.SubElement(r, qn('a:rPr')); rpr.set('lang', 'zh-CN'); rpr.set('sz', str(int(size*100)))
            if bold: rpr.set('b', '1')
            if italic: rpr.set('i', '1')
            sf = etree.SubElement(rpr, qn('a:solidFill')); etree.SubElement(sf, qn('a:srgbClr')).set('val', _hex(color))
            etree.SubElement(rpr, qn('a:latin')).set('typeface', FONT_CN)
            etree.SubElement(rpr, qn('a:ea')).set('typeface', FONT_CN)
            etree.SubElement(r, qn('a:t')).text = line0
    return sp

def add_rect(shapes, l, t, w, h, fill=None, line=None, line_w=0.75, rounded=False, geom='rect'):
    st = _st(shapes)
    g = geom if geom != 'rect' else ('roundRect' if rounded else 'rect')
    return _add_shape(st, l, t, w, h, geom=g, fill=fill, line=line, line_w=line_w)

def add_text(shapes, l, t, w, h, text, size=11, color=INK, bold=False, italic=False,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    st = _st(shapes)
    al = {PP_ALIGN.LEFT: 'l', PP_ALIGN.CENTER: 'ctr', PP_ALIGN.RIGHT: 'r'}.get(align, 'l')
    an = {MSO_ANCHOR.TOP: 'tt', MSO_ANCHOR.MIDDLE: 'ctr', MSO_ANCHOR.BOTTOM: 'b'}.get(anchor, 'tt')
    return _add_text(st, l, t, w, h, text, size=size, color=color, bold=bold, italic=italic, align=al, anchor=an)

def add_ph(shapes, idx, ph_type, l, t, w, h, text='', size=12, color=INK, bold=False,
           italic=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, fill=None, line=None,
           line_w=0.75, rounded=True):
    st = _st(shapes)
    al = {PP_ALIGN.LEFT: 'l', PP_ALIGN.CENTER: 'ctr', PP_ALIGN.RIGHT: 'r'}.get(align, 'l')
    an = {MSO_ANCHOR.TOP: 'tt', MSO_ANCHOR.MIDDLE: 'ctr', MSO_ANCHOR.BOTTOM: 'b'}.get(anchor, 'tt')
    return _add_text(st, l, t, w, h, text, size=size, color=color, bold=bold, italic=italic,
                     align=al, anchor=an, fill=fill, line=line, line_w=line_w, rounded=rounded, ph=(ph_type, idx))

# ---------- 统一标题栏 + 总结栏（优化版：整幅宽浅绿占位符 + 森林绿品牌细线） ----------
def chrome(shapes, title_hint="{{页面标题}}"):
    # 标题栏：整幅宽浅绿占位符（背景 + 标题文字合一）
    add_ph(shapes, 1, 'title', 0.0, 0.0, 13.333, 0.78,
           text=title_hint, size=18, bold=True, color=INK, anchor=MSO_ANCHOR.MIDDLE,
           fill=FG_TINT, line=None, rounded=False)
    # 标题栏底部森林绿品牌细线
    add_rect(shapes, 0.0, 0.78, 13.333, 0.03, fill=FG)
    # 总结栏：整幅宽浅绿占位符
    add_ph(shapes, 2, 'body', 0.0, 6.58, 13.333, 0.92,
           text="本页结论：…（一句话总结本页要点，可附数据来源）",
           size=12, color=INK2, anchor=MSO_ANCHOR.MIDDLE,
           fill=FG_TINT, line=None, rounded=False)
    # 总结栏顶部森林绿品牌细线
    add_rect(shapes, 0.0, 6.58, 13.333, 0.03, fill=FG)

# ---------- 内容页：卡片行 / 2x2 ----------
def row_cards(shapes, n, top, height, gap=0.22, hint_prefix="要点",
              fill=PANEL, line=LINE, color=MUTE):
    cw = (CW - (n - 1) * gap) / n
    for i in range(n):
        x = ML + i * (cw + gap)
        txt = f"{hint_prefix}{i+1}\n• 要点描述\n• 要点描述\n• 要点描述"
        add_ph(shapes, 10 + i, 'body', x, top, cw, height, text=txt,
               size=12, color=color, fill=fill, line=line, anchor=MSO_ANCHOR.TOP)

def grid2x2(shapes, top, height, gap=0.22, hints=None, fill=PANEL, line=LINE, color=MUTE):
    cw = (CW - gap) / 2; ch = (height - gap) / 2
    for r in range(2):
        for c in range(2):
            x = ML + c * (cw + gap); y = top + r * (ch + gap)
            idx = 10 + r * 2 + c
            txt = (hints[r*2+c] if hints else f"区块 {r*2+c+1}\n• …")
            add_ph(shapes, idx, 'body', x, y, cw, ch, text=txt,
                   size=12, color=color, fill=fill, line=line, anchor=MSO_ANCHOR.TOP)

# ---------- 各内容页版式 ----------
def build_blank(s):       chrome(s)
def build_2col(s):        chrome(s); row_cards(s, 2, C_TOP, C_H, hint_prefix="要点")
def build_3col(s):        chrome(s); row_cards(s, 3, C_TOP, C_H, hint_prefix="要点")
def build_5col(s):        chrome(s); row_cards(s, 5, C_TOP, C_H, hint_prefix="项")
def build_4col(s):        chrome(s); grid2x2(s, C_TOP, C_H, hints=["区块一","区块二","区块三","区块四"])

def build_listchart(s):
    chrome(s)
    lw = CW * 0.46; cw = CW - lw - 0.22
    add_ph(s, 10, 'body', ML, C_TOP, lw, C_H,
           text="要点清单\n• 事实/数据 1\n• 事实/数据 2\n• 事实/数据 3\n• 事实/数据 4",
           size=13, color=MUTE, fill=PANEL, line=LINE, anchor=MSO_ANCHOR.TOP)
    add_ph(s, 11, 'chart', ML + lw + 0.22, C_TOP, cw, C_H,
           text="（插入图表：菜单 → 插入 → 图表）\n柱状图 / 折线图 / 饼图",
           size=13, color=MUTE, fill=WHITE, line=LINE, line_w=1.0, anchor=MSO_ANCHOR.MIDDLE)

def build_timeline(s):
    chrome(s)
    n = 4; gap = 0.22; cw = (CW - (n-1)*gap) / n
    ly = C_TOP + 0.45
    add_rect(s, ML, ly - 0.01, CW, 0.02, fill=FG)
    for i in range(n):
        x = ML + i * (cw + gap); cx = x + cw/2
        add_rect(s, cx - 0.20, ly - 0.20, 0.40, 0.40, fill=FG, geom='ellipse')
        add_text(s, cx - 0.20, ly - 0.20, 0.40, 0.40, str(i+1), size=14,
                 color=WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        add_ph(s, 10 + i, 'body', x, ly + 0.35, cw, C_H - 0.80,
               text=f"阶段 {i+1}\n• 关键事件\n• 影响", size=12, color=MUTE,
               fill=PANEL, line=LINE, anchor=MSO_ANCHOR.TOP)

def build_comparison(s):
    chrome(s)
    cw = (CW - 0.7) / 2
    add_ph(s, 10, 'body', ML, C_TOP, cw, C_H,
           text="方案 A / 对象 A\n• 维度1：…\n• 维度2：…\n• 维度3：…",
           size=13, color=MUTE, fill=PANEL, line=LINE, anchor=MSO_ANCHOR.TOP)
    add_ph(s, 11, 'body', ML + cw + 0.7, C_TOP, cw, C_H,
           text="方案 B / 对象 B\n• 维度1：…\n• 维度2：…\n• 维度3：…",
           size=13, color=MUTE, fill=PANEL, line=LINE, anchor=MSO_ANCHOR.TOP)
    add_rect(s, ML + cw + 0.12, C_TOP + C_H/2 - 0.25, 0.46, 0.50, fill=FG, geom='roundRect')
    add_text(s, ML + cw + 0.12, C_TOP + C_H/2 - 0.25, 0.46, 0.50, "VS",
             size=16, color=WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

def build_quadrant(s):
    chrome(s)
    grid2x2(s, C_TOP, C_H, gap=0.22,
            hints=["高/高：领先区","高/低：潜力区","低/高：观察区","低/低：退出区"])
    add_text(s, ML, C_TOP + C_H + 0.04, CW, 0.3, "横轴：{{维度X}} →",
             size=11, color=INK2, align=PP_ALIGN.CENTER)
    add_text(s, 0.04, C_TOP + C_H/2 - 0.15, 0.42, 0.3, "↑ 纵轴\n{{维度Y}}",
             size=11, color=INK2, align=PP_ALIGN.CENTER)

def build_kpi(s):
    chrome(s)
    n = 4; gap = 0.22; cw = (CW - (n-1)*gap) / n
    labels = ["市场规模","同比增速","渗透率","集中度CR5"]
    for i in range(n):
        x = ML + i * (cw + gap)
        add_ph(s, 10 + i, 'body', x, C_TOP, cw, C_H,
               text=f"{labels[i]}\n+00.0%", size=13, color=MUTE,
               fill=PANEL, line=LINE, anchor=MSO_ANCHOR.MIDDLE)

def build_process(s):
    chrome(s)
    n = 4; gap = 0.22; aw = 0.35
    cw = (CW - (n-1)*(gap + aw)) / n
    for i in range(n):
        x = ML + i * (cw + gap + aw)
        add_ph(s, 10 + i, 'body', x, C_TOP, cw, C_H,
               text=f"步骤 {i+1}\n• 动作\n• 产出", size=12, color=MUTE,
               fill=PANEL, line=LINE, anchor=MSO_ANCHOR.TOP)
        if i < n - 1:
            add_rect(s, x + cw + gap/2, C_TOP + C_H/2 - 0.18, aw, 0.36, fill=FG, geom='chevron')

def build_bignum(s):
    chrome(s)
    add_ph(s, 10, 'body', ML, C_TOP, CW*0.42, C_H, text="00%", size=54,
           color=FG, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
           fill=WHITE, line=LINE, rounded=True)
    add_ph(s, 11, 'body', ML + CW*0.42 + 0.22, C_TOP, CW*0.58 - 0.22, C_H,
           text="核心结论 / 解读\n• 含义一\n• 含义二\n• 含义三", size=13,
           color=MUTE, fill=PANEL, line=LINE, anchor=MSO_ANCHOR.TOP)

def build_quote(s):
    chrome(s)
    add_ph(s, 10, 'body', ML, C_TOP + 0.2, CW, C_H*0.58,
           text="“在此放置关键洞察或引述，一句话点明行业本质。”", size=22,
           color=INK, italic=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
           fill=WHITE, line=None, rounded=True)
    add_ph(s, 11, 'body', ML + CW*0.55, C_TOP + C_H*0.68, CW*0.45, C_H*0.28,
           text="— {{来源 / 发言人}}", size=13, color=MUTE, align=PP_ALIGN.RIGHT,
           anchor=MSO_ANCHOR.MIDDLE, fill=None, line=None, rounded=False)

def build_probsol(s):
    chrome(s)
    cw = (CW - 0.7) / 2
    add_ph(s, 10, 'body', ML, C_TOP, cw, C_H,
           text="问题 / 痛点\n• 现象\n• 根因\n• 影响", size=13, color=MUTE,
           fill=PROB_FILL, line=PROB_LINE, anchor=MSO_ANCHOR.TOP)
    add_ph(s, 11, 'body', ML + cw + 0.7, C_TOP, cw, C_H,
           text="对策 / 行动\n• 方案\n• 预期效果\n• 时间表", size=13, color=MUTE,
           fill=SOL_FILL, line=SOL_LINE, anchor=MSO_ANCHOR.TOP)
    add_rect(s, ML + cw + 0.12, C_TOP + C_H/2 - 0.20, 0.46, 0.40, fill=FG, geom='chevron')

# ---------- 封面 / 标题页(板块) / 尾页 ----------
def build_cover(s):
    add_ph(s, 4, 'pic', 0.0, 0.0, 6.4, 7.5,
           text="（双击此处插入封面图，或放置行业相关视觉）", size=13, color=MUTE,
           fill=RGBColor(0xED,0xEB,0xE4), line=LINE, anchor=MSO_ANCHOR.MIDDLE)
    add_rect(s, 6.7, 2.3, 0.12, 1.4, fill=FG)
    add_text(s, 7.0, 1.7, 5.8, 0.5, "行业分析", size=16, color=FG, bold=True)
    add_ph(s, 1, 'title', 7.0, 2.2, 5.8, 1.6,
           text="{{行业名称}} 行业分析", size=30, color=INK, bold=True, anchor=MSO_ANCHOR.TOP)
    add_ph(s, 2, 'subTitle', 7.0, 3.9, 5.8, 0.9,
           text="{{副标题：市场·用户·竞品·措施}}", size=15, color=INK2, anchor=MSO_ANCHOR.TOP)
    add_ph(s, 3, 'body', 7.0, 5.6, 5.8, 1.2,
           text="团队：{{团队}}    日期：{{YYYY-MM-DD}}\n版本：v1.0    密级：{{公开/内部}}",
           size=12, color=MUTE, anchor=MSO_ANCHOR.TOP)

def build_section(s, color, num, title, intro):
    add_rect(s, 0, 0, 13.333, 7.5, fill=WHITE)
    add_rect(s, 0, 0, 0.35, 7.5, fill=color)
    add_text(s, 0.9, 1.2, 3.4, 3.2, num, size=120, color=color, bold=True,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)
    add_ph(s, 1, 'title', 4.4, 2.4, 8.6, 1.2, text=title, size=34, color=INK,
           bold=True, anchor=MSO_ANCHOR.MIDDLE)
    add_ph(s, 2, 'body', 4.4, 3.8, 8.6, 2.2,
           text=intro + "\n\n{{本板块要回答的核心问题}}", size=15, color=INK2, anchor=MSO_ANCHOR.TOP)

def build_back(s):
    add_rect(s, 0, 0, 13.333, 7.5, fill=FG_DARK)
    add_ph(s, 1, 'title', 1.0, 2.4, 11.3, 1.4, text="谢谢观看", size=40,
           color=WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_ph(s, 2, 'body', 1.0, 3.9, 11.3, 1.6,
           text="关键结论一句话：{{用一句话复述全报告核心判断}}\n联系：{{团队 / 邮箱}}",
           size=16, color=RGBColor(0xDD,0xDD,0xDD), align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.TOP)

# ---------- 主题色同步（让 PowerPoint 默认强调色也是森林绿家族） ----------
def patch_theme_zip(path):
    import zipfile, os
    with zipfile.ZipFile(path, 'r') as zin:
        names = zin.namelist()
        data = {n: zin.read(n) for n in names}
    theme_names = [n for n in names if n.endswith('theme1.xml')]
    mapping = {
        'dk2': '145A14', 'lt2': 'E9F3E9',
        'accent1': '228B22', 'accent2': '2E7D6B', 'accent3': 'B5532F',
        'accent4': 'C0882E', 'accent5': '6B8E23', 'accent6': '557A46',
    }
    for tn in theme_names:
        root = etree.fromstring(data[tn])
        cs = root.find('.//' + qn('a:clrScheme'))
        if cs is None:
            continue
        for tag, val in mapping.items():
            node = cs.find(qn('a:' + tag))
            if node is None:
                continue
            child = node.find(qn('a:srgbClr'))
            if child is None:
                child = etree.SubElement(node, qn('a:srgbClr'))
            child.set('val', val)
        data[tn] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
    tmp = path + ".tmp"
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for n in names:
            zout.writestr(n, data[n])
    os.replace(tmp, path)

# ---------- 克隆版式进 slide master ----------
CT_SL = 'application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml'
blank = None

def clone_layout(master, name):
    mp = master.part; pkg = mp.package
    el = deepcopy(blank._element)
    el.cSld.set('name', name)
    pn = PackURI("/ppt/slideLayouts/slideLayout_%d.xml" % (len(list(pkg.iter_parts())) + 1))
    part = SlideLayoutPart(pn, CT_SL, pkg, el)
    rId = mp.relate_to(part, RT.SLIDE_LAYOUT)
    part.relate_to(mp, RT.SLIDE_MASTER)
    lst = master._element.sldLayoutIdLst
    existing = [int(e.get('id')) for e in lst.findall(qn('p:sldLayoutId'))]
    nid = (max(existing) if existing else 2147483648) + 1   # PowerPoint 要求 >= 2^31
    sid = etree.SubElement(lst, qn('p:sldLayoutId'))
    sid.set('id', str(nid)); sid.set(qn('r:id'), rId)
    return [l for l in master.slide_layouts if l.name == name][0]

# ---------- 示例文字（普通视图演示用） ----------
SECTION_META = [
    ("标题页-01市场分析", FG,     "01", "市场分析", "市场规模 · 增速 · 结构 · 驱动因素"),
    ("标题页-02用户画像", TEALG,  "02", "用户画像", "人群分层 · 需求 · 决策链路 · 场景"),
    ("标题页-03竞品分析", TERRA,  "03", "竞品分析", "玩家格局 · 份额 · 打法 · 优劣势"),
    ("标题页-04市场措施", OCHRE,  "04", "市场措施", "定位 · 策略 · 行动 · 节奏"),
]
CONTENT_REGISTRY = [
    ("内容-空白",       build_blank,     {}),
    ("内容-左右",       build_2col,      {}),
    ("内容-三分",       build_3col,      {}),
    ("内容-四分(2x2)",  build_4col,      {}),
    ("内容-五分",       build_5col,      {}),
    ("内容-列表+图表",  build_listchart, {}),
    ("内容-时间轴",     build_timeline,  {}),
    ("内容-对比",       build_comparison,{}),
    ("内容-矩阵象限",   build_quadrant,  {}),
    ("内容-KPI指标",    build_kpi,       {}),
    ("内容-流程步骤",   build_process,   {}),
    ("内容-大数字",     build_bignum,    {}),
    ("内容-引述洞察",   build_quote,     {}),
    ("内容-问题对策",   build_probsol,   {}),
]

def gen_content_samples(layout_name):
    base = {1: layout_name.replace("内容-", "") + "：示例标题",
            2: "本页结论：示例——该维度呈结构性改善，建议持续跟踪。"}
    extra = {
        "内容-左右":      {10:"左栏：市场规模与增速\n• 2025 规模 1.2 万亿\n• CAGR 18%\n• 价格结构性上行",
                           11:"右栏：关键结论\n• 量价齐升\n• 龙头集中"},
        "内容-三分":      {10:"用户：三类核心人群\n• 年轻刚需\n• 升级置换\n• 企业采购",
                           11:"渠道：融合趋势\n• 线上占比 45%\n• 线下体验店",
                           12:"场景：高频刚需\n• 日常通勤\n• 商务出行"},
        "内容-四分(2x2)": {10:"区域：华东领跑 42%",11:"价格：高端化加速",12:"供给：产能出清",13:"政策：补贴退坡"},
        "内容-五分":      {10:"玩家A 份额28%",11:"玩家B 21%",12:"玩家C 15%",13:"玩家D 11%",14:"其他 25%"},
        "内容-列表+图表": {10:"驱动因子清单\n• 政策扶持\n• 技术进步\n• 消费升级\n• 资本涌入"},
        "内容-时间轴":    {10:"2018 起步\n• 政策试点",11:"2020 放量\n• 补贴加码",
                           12:"2022 洗牌\n• 价格战",13:"2025 出清\n• 龙头集中"},
        "内容-对比":      {10:"方案 A / 对象 A\n• 份额 35%\n• 优势：渠道\n• 劣势：毛利低",
                           11:"方案 B / 对象 B\n• 份额 28%\n• 优势：品牌\n• 劣势：重资产"},
        "内容-矩阵象限":  {10:"领先区：份额高增速高",11:"潜力区：份额低增速高",
                           12:"观察区：份额高增速低",13:"退出区：份额低增速低"},
        "内容-KPI指标":   {10:"市场规模\n1.2 万亿",11:"同比增速\n+18.0%",
                           12:"渗透率\n23.0%",13:"CR5\n62.0%"},
        "内容-流程步骤":  {10:"步骤1 洞察\n• 扫描需求",11:"步骤2 验证\n• 小步试错",
                           12:"步骤3 放量\n• 渠道铺开",13:"步骤4 复盘\n• 迭代"},
        "内容-大数字":    {10:"23%",11:"核心解读\n• 渗透率仍低\n• 空间广阔\n• 拐点临近"},
        "内容-引述洞察":  {10:"“这个行业的本质，是从产品竞争走向生态竞争。”",11:"— 行业资深从业者"},
        "内容-问题对策":  {10:"问题 / 痛点\n• 同质化严重\n• 毛利承压\n• 获客成本高",
                           11:"对策 / 行动\n• 差异化定位\n• 成本优化\n• 私域运营"},
    }
    base.update(extra.get(layout_name, {}))
    return base

COVER_SAMPLES = {1:"新能源汽车 行业分析", 2:"市场 · 用户 · 竞品 · 措施 全景透视",
                3:"团队：喵星妙妙屋    日期：2026-11-08\n版本：v1.0    密级：内部"}
BACK_SAMPLES  = {1:"谢谢观看",
                2:"关键结论一句话：行业进入结构分化期，龙头集中与细分突围并存。\n联系：喵星妙妙屋 · analyst@miao.com"}

# ---------- 主流程 ----------
def main():
    global blank
    prs = Presentation()
    prs.slide_width  = Inches(W)
    prs.slide_height = Inches(H)
    master = prs.slide_masters[0]
    blank = master.slide_layouts[6]

    sldIdLst = prs.element.find(qn('p:sldIdLst'))
    if sldIdLst is not None:
        for sid in list(sldIdLst):
            rId = sid.get(qn('r:id'))
            prs.part.drop_rel(rId)
            sldIdLst.remove(sid)

    lst = master._element.sldLayoutIdLst
    for sid in list(lst):
        rId = sid.get(qn('r:id'))
        master.part.drop_rel(rId)
        lst.remove(sid)

    layouts = {}
    lc = clone_layout(master, "封面-左图右标题"); build_cover(lc.shapes); layouts["封面-左图右标题"] = lc
    for name, color, num, title, intro in SECTION_META:
        ls = clone_layout(master, name); build_section(ls.shapes, color, num, title, intro); layouts[name] = ls
    for name, fn, _ in CONTENT_REGISTRY:
        lx = clone_layout(master, name); fn(lx.shapes); layouts[name] = lx
    lb = clone_layout(master, "尾页-结语"); build_back(lb.shapes); layouts["尾页-结语"] = lb

    sl = prs.slides.add_slide(layouts["封面-左图右标题"]); _fill(sl, COVER_SAMPLES)
    for name, color, num, title, intro in SECTION_META:
        sl = prs.slides.add_slide(layouts[name])
        _fill(sl, {1: title, 2: intro + "\n\n本板块回答：这个细分领域的关键变量是什么？"})
    for name, fn, _ in CONTENT_REGISTRY:
        sl = prs.slides.add_slide(layouts[name])
        _fill(sl, gen_content_samples(name))
    sl = prs.slides.add_slide(layouts["尾页-结语"]); _fill(sl, BACK_SAMPLES)

    # 规范母版落点：docs/templates（纳入 git 跟踪，作为可复用模板资产）
    out = "docs/templates/行业分析母版.pptx"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    try:
        prs.save(out)
    except PermissionError:
        # 规范文件被打开的预览锁定，落到 output/ 暂存，避免丢产物
        out = "output/行业分析母版.pptx"
        prs.save(out)
        print("[WARN] 规范文件被占用（可能正在预览），已写出到:", out)
    # 保存后同步主题色为森林绿家族（默认强调色也变绿）
    patch_theme_zip(out)

    p2 = Presentation(out)
    m2 = p2.slide_masters[0]
    names = [l.name for l in m2.slide_layouts]
    print(f"OK -> {out}")
    print(f"母版版式数: {len(names)}")
    for n in names:
        print("  -", n)
    print(f"普通视图示例幻灯片数: {len(p2.slides._sldIdLst)}")

def _fill(slide, samples):
    for ph in slide.placeholders:
        idx = ph.placeholder_format.idx
        if idx in samples:
            try:
                ph.text = samples[idx]
            except Exception:
                pass

if __name__ == "__main__":
    main()
