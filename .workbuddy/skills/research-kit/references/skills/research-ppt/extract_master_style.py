#!/usr/bin/env python3
"""从 .pptx 抽取母版主题（配色 / 字体 / 页尺寸 / 版式 / 母版形状），产出 research-ppt 的「风格锁」常量。

用途：output_target=ppt 且配了 master_template 时，出片前先跑本脚本，
把模板的视觉变量固化下来，再写进 .slide 常量，做到「套公司模板的皮、但产物不依赖模板文件」。

用法：
    python extract_master_style.py <template.pptx> [--out <style-lock.yaml>]

输出：
    1) <stem>-style-lock.yaml  —— 机器可读，供人工核对与版本化
    2) stdout                  —— 可直接粘进 .slide 的 DSL 常量片段

说明：
    - 只读，不改模板文件。
    - 取 theme1（母版通过 rels 指向的主题）；多主题的复杂模板以 master 实际引用为准。
    - 颜色取值优先级：srgbClr@val → sysClr@lastClr（Office 默认主题常用 sysClr）。
"""

import argparse
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

CLR_ORDER = ["dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3",
             "accent4", "accent5", "accent6", "hlink", "folHlink"]

EMU_PER_INCH = 914400
EMU_PER_PX = 9525  # 96 dpi


def read_part(zf, name):
    try:
        return zf.read(name)
    except KeyError:
        return None


def parse_theme(zf, theme_part):
    data = read_part(zf, theme_part)
    if data is None:
        return {}, {}
    root = ET.fromstring(data)

    palette = {}
    cs = root.find(".//a:clrScheme", NS)
    if cs is not None:
        for tag in CLR_ORDER:
            el = cs.find("a:" + tag, NS)
            if el is None:
                continue
            srgb = el.find("a:srgbClr", NS)
            sysc = el.find("a:sysClr", NS)
            val = None
            if srgb is not None:
                val = srgb.get("val")
            elif sysc is not None:
                val = sysc.get("lastClr")
            if val:
                palette[tag] = "#" + val.upper()

    fonts = {}
    for key, tag in (("major", "majorFont"), ("minor", "minorFont")):
        el = root.find(".//a:" + tag, NS)
        if el is None:
            continue
        latin = el.find("a:latin", NS)
        ea = el.find("a:ea", NS)
        fonts[key] = {
            "latin": (latin.get("typeface") if latin is not None else "") or "",
            "ea": (ea.get("typeface") if ea is not None else "") or "",
        }
    return palette, fonts


def master_theme_part(zf):
    """母版 rels 指向的 theme（而非硬编码 theme1）。"""
    rels = read_part(zf, "ppt/slideMasters/_rels/slideMaster1.xml.rels")
    if rels:
        # 母版在 ppt/slideMasters/ 下，rels 的 Target 形如 ../theme/theme1.xml → 还原为 ppt/theme/theme1.xml
        m = re.search(rb'Type="[^"]*/theme"\s+Target="\.\./(theme/theme\d+\.xml)"', rels)
        if m:
            return "ppt/" + m.group(1).decode("ascii")
    return "ppt/theme/theme1.xml"


def parse_page_size(zf):
    data = read_part(zf, "ppt/presentation.xml")
    if data is None:
        return {}
    m = re.search(rb'<p:sldSz[^>]*cx="(\d+)"[^>]*cy="(\d+)"', data)
    if not m:
        return {}
    cx, cy = int(m.group(1)), int(m.group(2))
    ratio = round(cx / cy, 4)
    label = "16:9" if abs(ratio - 16 / 9) < 0.02 else ("4:3" if abs(ratio - 4 / 3) < 0.02 else "custom")
    return {
        "cx_emu": cx,
        "cy_emu": cy,
        "px_96dpi": [round(cx / EMU_PER_PX), round(cy / EMU_PER_PX)],
        "inch": [round(cx / EMU_PER_INCH, 2), round(cy / EMU_PER_INCH, 2)],
        "ratio": label,
    }


def list_layouts(zf, names):
    out = []
    pat = re.compile(r"ppt/slideLayouts/slideLayout(\d+)\.xml$")
    for n in sorted((x for x in names if pat.match(x)), key=lambda s: int(pat.match(s).group(1))):
        data = read_part(zf, n)
        if data is None:
            continue
        root = ET.fromstring(data)
        csld = root.find("p:cSld", NS)
        out.append({
            "index": int(pat.match(n).group(1)) - 1,
            "name": (csld.get("name") if csld is not None else "") or "",
        })
    return out


def list_master_shapes(zf):
    """母版里非占位符形状（Logo / 页眉页脚条等），用于推断安全区。"""
    data = read_part(zf, "ppt/slideMasters/slideMaster1.xml")
    if data is None:
        return []
    root = ET.fromstring(data)
    tree = root.find("p:cSld/p:spTree", NS)
    if tree is None:
        return []
    out = []
    for sp in tree.findall("p:sp", NS):
        nv = sp.find("p:nvSpPr/p:cNvPr", NS)
        name = (nv.get("name") if nv is not None else "") or ""
        if not name:
            continue
        off = sp.find("p:spPr/a:xfrm/a:off", NS)
        ext = sp.find("p:spPr/a:xfrm/a:ext", NS)
        if off is None or ext is None:
            continue
        out.append({
            "name": name,
            "bbox_emu": [int(off.get("x")), int(off.get("y")),
                         int(ext.get("cx")), int(ext.get("cy"))],
        })
    return out


def _luminance(hex_color):
    """相对亮度（0~1），用于判定浅底/深底模板。"""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return 0.5
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))

    def lin(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def detect_mode(palette):
    """light = 浅底深字（默认）；dark = 深底浅字。以 lt1 与 dk1 的亮度差判定。"""
    lt1 = palette.get("lt1", "#FFFFFF")
    dk1 = palette.get("dk1", "#000000")
    return "dark" if _luminance(lt1) < _luminance(dk1) else "light"


def to_yaml(meta):
    lines = ["# 由 research-ppt/extract_master_style.py 生成，勿手改；重跑覆盖。"]
    lines.append("source: %s" % meta["source"])
    lines.append("generated_at: %s" % meta["generated_at"])
    lines.append("mode: %s   # light=浅底深字 / dark=深底浅字（决定 inkSub 取 dk2 还是 lt2）" % meta["mode"])
    p = meta["page"]
    if p:
        lines.append("page:")
        lines.append("  cx_emu: %d" % p["cx_emu"])
        lines.append("  cy_emu: %d" % p["cy_emu"])
        lines.append("  px_96dpi: [%d, %d]" % tuple(p["px_96dpi"]))
        lines.append("  inch: [%s, %s]" % tuple(p["inch"]))
        lines.append("  ratio: \"%s\"" % p["ratio"])
    if meta["palette"]:
        lines.append("palette:")
        for k in CLR_ORDER:
            if k in meta["palette"]:
                lines.append("  %s: \"%s\"" % (k, meta["palette"][k]))
    if meta["fonts"]:
        lines.append("fonts:")
        for k in ("major", "minor"):
            f = meta["fonts"].get(k, {})
            lines.append("  %s: {latin: \"%s\", ea: \"%s\"}" % (k, f.get("latin", ""), f.get("ea", "")))
    if meta["layouts"]:
        lines.append("layouts:")
        for l in meta["layouts"]:
            lines.append("  - {index: %d, name: \"%s\"}" % (l["index"], l["name"]))
    if meta["master_shapes"]:
        lines.append("master_shapes:")
        for s in meta["master_shapes"]:
            lines.append("  - {name: \"%s\", bbox_emu: [%d, %d, %d, %d]}"
                         % (s["name"], *s["bbox_emu"]))
    return "\n".join(lines) + "\n"


def dsl_const(meta):
    pal = meta["palette"]
    fonts = meta["fonts"]
    major = fonts.get("major", {})
    minor = fonts.get("minor", {})
    title_font = major.get("ea") or major.get("latin") or "Microsoft YaHei"
    body_font = minor.get("ea") or minor.get("latin") or "Microsoft YaHei"
    mode = meta.get("mode", "light")
    # 次级文字：浅底取 dk2（深灰），深底取 lt2（浅灰），否则深色模板上会糊成一片
    ink_sub_key = "lt2" if mode == "dark" else "dk2"
    ink_sub = pal.get(ink_sub_key) or pal.get("dk2") or "#44546A"
    rows = [
        "// ⬇ 风格锁：来自 %s（mode=%s，重跑 extract_master_style.py 可刷新）"
        % (os.path.basename(meta["source"]), mode),
        "const LOCK = {",
        '  bg: "%s",        // lt1 母版背景' % pal.get("lt1", "#FFFFFF"),
        '  ink: "%s",       // dk1 正文' % pal.get("dk1", "#000000"),
        '  inkSub: "%s",    // %s 次级文字（%s 模板）' % (ink_sub, ink_sub_key, mode),
        '  accent: "%s",    // accent1 主色' % pal.get("accent1", "#4472C4"),
        '  accent2: "%s",   // accent2 次色' % pal.get("accent2", "#ED7D31"),
        '  accent3: "%s",   // accent3 辅助' % pal.get("accent3", "#A5A5A5"),
        '  fontTitle: "%s",' % title_font,
        '  fontBody: "%s",' % body_font,
        "};",
        "// A股 色规仍按域覆盖：涨 #D8382E / 跌 #1F9D55（不取模板色）",
    ]
    return "\n".join(rows)


def main():
    ap = argparse.ArgumentParser(description="抽取 pptx 母版主题，生成 research-ppt 风格锁")
    ap.add_argument("pptx", help="模板 .pptx 路径")
    ap.add_argument("--out", help="输出 yaml 路径（默认 <stem>-style-lock.yaml）")
    args = ap.parse_args()

    if not os.path.isfile(args.pptx):
        print("ERROR: 找不到文件 %s" % args.pptx, file=sys.stderr)
        return 2

    with zipfile.ZipFile(args.pptx) as zf:
        names = zf.namelist()
        theme_part = master_theme_part(zf)
        palette, fonts = parse_theme(zf, theme_part)
        meta = {
            "source": os.path.abspath(args.pptx).replace("\\", "/"),
            "generated_at": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M"),
            "theme_part": theme_part,
            "mode": detect_mode(palette),
            "page": parse_page_size(zf),
            "palette": palette,
            "fonts": fonts,
            "layouts": list_layouts(zf, names),
            "master_shapes": list_master_shapes(zf),
        }

    out = args.out or (os.path.splitext(args.pptx)[0] + "-style-lock.yaml")
    with open(out, "w", encoding="utf-8") as f:
        f.write(to_yaml(meta))

    print("== style lock -> %s" % out)
    print("== theme=%s page=%s layouts=%d shapes=%d"
          % (theme_part, meta["page"].get("ratio", "?"), len(meta["layouts"]), len(meta["master_shapes"])))
    print()
    print(dsl_const(meta))
    return 0


if __name__ == "__main__":
    sys.exit(main())
