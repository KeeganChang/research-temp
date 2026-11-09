#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
P07 报告组装器（主编侧确定性工具，非 skill 文件，不改套件模板）

输入：
  temp/P07-draft-ch1..ch5.md   五章核定稿（markdown）
  temp/P07-framework.json      可选：程文成产出的 {intro, conclusion, toc, extra_references}
  temp/P07-research-card-v3.md 口径基线（用于抽取反方清单，可选）

输出：
  output/<文件名>.md           markdown 源报告（SSOT 主交付之一）
  temp/P07-report-data.json    research-html 渲染器输入
  output/<文件名>.html         自包含单页 HTML（由套件 render_html.py 生成 + 后处理增强）

用法（工作区根、项目隔离环境）：
  ./.venv/Scripts/python.exe temp/P07-build-report.py
"""
import html
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / "temp"
OUT = ROOT / "output"
SKILL_RENDER = (
    ROOT / ".workbuddy" / "skills" / "research-kit" / "references" / "skills"
    / "research-html" / "render_html.py"
)
TPL = (
    ROOT / ".workbuddy" / "skills" / "research-kit" / "references"
    / "templates" / "html-delivery.html"
)

DATE = "2026-11-09"
PID = "P07"
THEME = "菲律宾合规 CFD 市场进入研究：沙盒准入证伪、钱包支付与需求重定向承接方"
BASENAME = "2026-11-09_行业_菲律宾合规CFD市场进入_v1"
MD_PATH = OUT / (BASENAME + ".md")
HTML_PATH = OUT / (BASENAME + ".html")
DATA_PATH = TMP / "P07-report-data.json"

# ---------------------------------------------------------------- 口径块
CALIBER = [
    ("研究主体", "以参与菲律宾监管沙盒为前提的合规 CFD（零售差价合约）业务；重点＝钱包支付方式与合作方式"),
    ("推理框架", "research-kit Track=entry / method=method-market-entry（E1 准入 → E2 行业 → E3 需求重定向 → E4 画像 → E5 玩家地图）；准入优先于需求"),
    ("时效窗口", "2025–2026 为主，优先采用最新版报告与 2027 展望；监管状态逐条标 as-of，全部数据截至 2026-11-09"),
    ("单位与货币", "金额以菲律宾比索 PHP 原值为主口径；USD 换算仅作量级示意。汇率两口径并列不合成：1 USD≈61.33 PHP（参数卡，as-of 未标注）／63.8520 PHP（BSP 2026-10-30）"),
    ("收入口径", "人均 GNI 以世界银行 Atlas 法一手为主口径 4,850 USD（2025）／4,470 USD（2024）；参数卡 3,967 USD 并列保留，年份与方法未核实，标「证据不足」，不取平均、不合成"),
    ("比率定义", "数字支付占比 52.8%(2023)→57.4%(2024)→64.7%(2025) 分母＝零售支付总笔数、分子＝数字支付笔数；既非金额占比亦非人口渗透率。投资参与率统一用 BSP 2025 CFIS 官方 23%（8,784 样本）"),
    ("缺月／缺期处理", "2026 宏观用季度与上半年值并列（Q1 2.8%／Q2 2.3%，2025 Q2 5.4%）；2027 全部为机构预测，多口径并列不合成，标注「预测非事实」"),
    ("代理指标与已知 caveat", "PSE 33 亿美元／2,100 亿比索为其自述「代理示意」非预测；GTV ≠ 营收；GCash 注册 ≠ MAU ≠ 可投资余额；相对排名（Chainalysis 指数）≠ 绝对规模；Mynt 2026 H1 不可与全年同比"),
    ("证据等级", "一手 > 二手 > 聚合。一手条文缺口（SEC 明文全面禁止零售 CFD／StratBox 明文排除衍生品）显式标注「未检索到」，不作推断填补。SEC MC9 PDF 直连受 Cloudflare 限制，条文取自索引快照＋镜像＋律所解析交叉印证"),
    ("口径冲突纪律", "VASP 名录 11 家(2026-05-31) vs 9 家(2026-07-15)、数字银行 4 张新牌照 vs 已发 7／剩 3 席、GNI、汇率、CFIS 女性账户 25% vs Findex 57.1% 等一律按 as-of／母体不同而并列，不合成、不外推"),
    ("判断标注", "所有推断类结论标 kind: judgment 并保留被否决备选；E3「需求重定向」为分析主线（问题结构），非已证实的因果结论"),
]

# ---------------------------------------------------------------- 反方清单（全案 ≥5，含时间维度）
COUNTER = [
    "<strong>准入不豁免法律、沙盒不自动发牌</strong>：MC 9 s.2024 §15 明文不豁免，参与沙盒不等于取得牌照；BSP 书面答复亦明确 VASP 活动与法币轨道不在 SEC 沙盒覆盖内。",
    "<strong>零售 CFD 无本地持牌主体，且已有直接执法</strong>：2025-12 XM CDO 判「产品未注册即属 fraud on investors」；2026-03-31 SEC 警示 8 家平台（含零售 CFD 经纪商 Deriv）无 SEC 注册／CASP 授权／SRC §28 资格。",
    "<strong>支付通道反成管辖证据</strong>：XM CDO 以「本地银行＋e-wallet 作支付伙伴」认定「清楚显示菲律宾投资者为主要目标市场」——接了比索钱包入金，反而坐实属地管辖。",
    "<strong>持牌承接主体在收缩</strong>：M-2025-031 自 2025-09-01 持续生效（视 global and local developments 重估），VASP 名录由 11 家(2026-05-31) 收缩至 9 家(2026-07-15)；只能并购／合作既有持牌方，而牌照变更控制是否自动转移「证据不足」。",
    "<strong>需求侧远弱于叙事</strong>：BSP 2025 CFIS 投资参与率 36%(2021)→23%(2025)，虚拟资产认知 20% 而投资者实际持有约 1%；64% 交易前核验机构是否受监管。加密被禁于持牌博彩场景（PAGCOR Rev.1 第 26–27 页 g 条，生效 2025-10-02 一手规章），娱乐休闲与加密支付不可简单叠加。",
    "<strong>时间维度（必写）</strong>：2026 宏观急转——Q2 GDP 2.3%（2025 Q2 5.4%）、上半年通胀 4.8%（2025 全年 1.7%）、固定资本形成转负；用 2025 高增长／低通胀数据测算 2026 可支配收入会系统性高估。2027 复苏全部为机构预测而非事实。且截至 2026-11-09 合规承接方仍处受监督测试、公测未开放、完整功能或需 2028，「合规溢价」目前是<strong>预期而非已兑现的观测值</strong>。",
    "<strong>同涨同跌＝假分散</strong>：11→9 家 VASP 同受 M-2025-031 约束、法币入口同收敛至 InstaPay／PESONet、同受一轮全球行情（CSAO 区域加密经济 −6.8%、全球市值缩水约 50%）；牌照数量分散不构成风险分散。",
]

# ---------------------------------------------------------------- markdown 行内解析
LINK_RE = re.compile(r"\[([^\]\n]+)\]\(([^)\n]+)\)")
# 各章标题层级不统一（CH2 用 ## ，其余用 # ），按「第 N 章」语义识别而非按 # 个数
CHAPTER_HEAD_RE = re.compile(r"^#{1,2}\s*第\s*\d+\s*章")


def _plain(s):
    """链接文字：只允许粗体，其余转义。"""
    s = html.escape(s, quote=False)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)


def inline(s):
    """把一行 markdown 转成受控内联 HTML。链接先占位保护，避免 escape 破坏 URL 中的 & 。"""
    stash = []

    def _link(m):
        text, url = m.group(1), m.group(2).strip()
        stash.append(
            '<a href="{}" target="_blank" rel="noopener">{}</a>'.format(
                html.escape(url, quote=True), _plain(text)
            )
        )
        return "\x00L{}\x00".format(len(stash) - 1)

    s = LINK_RE.sub(_link, s)
    # 脚注引用 [^gni] -> 上标
    s = re.sub(r"\[\^([^\]\n]+)\]", lambda m: "<sup>{}</sup>".format(html.escape(m.group(1))), s)
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\x00L(\d+)\x00", lambda m: stash[int(m.group(1))], s)
    return s


def is_table_sep(line):
    return bool(re.match(r"^\s*\|?[\s:\-\|]+\|[\s:\-\|]*$", line)) and "-" in line


def md_to_html(md):
    lines = md.splitlines()
    out, i, n = [], 0, len(lines)
    while i < n:
        raw = lines[i]
        line = raw.rstrip()
        if not line.strip():
            i += 1
            continue

        # 章标题（# / ## 第 N 章）——由调用方抽走，这里降级为 h3 兜底
        if line.startswith("# "):
            out.append("<h3>{}</h3>".format(inline(line[2:].strip())))
            i += 1
            continue
        if line.startswith("## "):
            out.append("<h3>{}</h3>".format(inline(line[3:].strip())))
            i += 1
            continue
        if line.startswith("### "):
            out.append("<h3>{}</h3>".format(inline(line[4:].strip())))
            i += 1
            continue
        if line.startswith("#### "):
            out.append("<h4>{}</h4>".format(inline(line[5:].strip())))
            i += 1
            continue
        if re.match(r"^\s*---+\s*$", line):
            out.append("<hr>")
            i += 1
            continue

        # 表格
        if line.lstrip().startswith("|") and i + 1 < n and is_table_sep(lines[i + 1]):
            def cells(row):
                r = row.strip()
                if r.startswith("|"):
                    r = r[1:]
                if r.endswith("|"):
                    r = r[:-1]
                return [c.strip() for c in r.split("|")]

            head = cells(line)
            i += 2
            body = []
            while i < n and lines[i].lstrip().startswith("|"):
                body.append(cells(lines[i]))
                i += 1
            t = ['<div class="tw"><table class="data"><thead><tr>']
            t += ["<th>{}</th>".format(inline(c)) for c in head]
            t.append("</tr></thead><tbody>")
            for row in body:
                t.append("<tr>")
                t += ["<td>{}</td>".format(inline(c)) for c in row]
                t.append("</tr>")
            t.append("</tbody></table></div>")
            out.append("".join(t))
            continue

        # 脚注定义
        m = re.match(r"^\[\^([^\]]+)\]:?\s*(.*)$", line)
        if m:
            out.append('<p class="fn"><sup>{}</sup> {}</p>'.format(html.escape(m.group(1)), inline(m.group(2))))
            i += 1
            continue

        # 引用
        if line.startswith("> "):
            out.append("<blockquote>{}</blockquote>".format(inline(line[2:].strip())))
            i += 1
            continue

        # 列表（无序 / 有序），连续成组
        if re.match(r"^\s*[-*]\s+", line) or re.match(r"^\s*\d+[.)]\s+", line):
            ordered = bool(re.match(r"^\s*\d+[.)]\s+", line))
            tag = "ol" if ordered else "ul"
            items = []
            pat = r"^\s*\d+[.)]\s+" if ordered else r"^\s*[-*]\s+"
            while i < n and re.match(pat, lines[i]):
                items.append("<li>{}</li>".format(inline(re.sub(pat, "", lines[i]).strip())))
                i += 1
            out.append("<{0}>{1}</{0}>".format(tag, "".join(items)))
            continue

        # 普通段落：连续普通行合并
        para = [line.strip()]
        i += 1
        while i < n:
            nxt = lines[i].rstrip()
            if (not nxt.strip() or nxt.startswith("#") or nxt.lstrip().startswith("|")
                    or nxt.startswith("> ") or re.match(r"^\s*[-*]\s+", nxt)
                    or re.match(r"^\s*\d+[.)]\s+", nxt) or re.match(r"^\s*---+\s*$", nxt)
                    or re.match(r"^\[\^([^\]]+)\]:?", nxt)):
                break
            para.append(nxt.strip())
            i += 1
        out.append("<p>{}</p>".format(inline(" ".join(para))))
    return "\n".join(out)


def chapter_title(md):
    for ln in md.splitlines()[:8]:
        if CHAPTER_HEAD_RE.match(ln):
            return re.sub(r"^#{1,2}\s*", "", ln).strip()
    return "(未命名章节)"


def strip_chapter_heading(md):
    lines = md.splitlines()
    # 容忍标题前有空行；只删章标题行，保留其后的 > as-of / 边界声明引用块
    for idx, ln in enumerate(lines[:4]):
        if CHAPTER_HEAD_RE.match(ln):
            return "\n".join(lines[:idx] + lines[idx + 1:]).lstrip("\n")
    return md


def collect_references(texts):
    """从全部章节抽取 markdown 链接，按 URL 去重，保留首次出现的链接文字。"""
    seen, refs = set(), []
    for md in texts:
        for m in LINK_RE.finditer(md):
            label, url = m.group(1).strip(), m.group(2).strip()
            if url in seen or not url.lower().startswith(("http://", "https://")):
                continue
            seen.add(url)
            refs.append((label, url))
    refs.sort(key=lambda x: x[1])
    return ["{} — {}".format(l, u) for l, u in refs]


EXTRA_CSS = """
  /* P07 报告增强（由组装器注入，不修改套件模板） */
  section h3{font-family:var(--serif);font-size:16.5px;margin:22px 0 10px;color:var(--accent);
    padding-bottom:6px;border-bottom:1px solid var(--line);}
  section h4{font-size:14.5px;margin:16px 0 8px;color:var(--ink);}
  section ul,section ol{margin:0 0 14px;padding-left:24px;}
  section li{margin-bottom:7px;}
  section a{color:var(--accent);text-decoration:underline;text-decoration-color:#b9d5d0;
    text-underline-offset:2px;}
  section a:hover{text-decoration-color:var(--accent);}
  section hr{border:0;border-top:1px dashed var(--line);margin:20px 0;}
  section blockquote{margin:0 0 14px;padding:10px 16px;background:#fcfbf9;
    border-left:3px solid var(--accent);border-radius:0 6px 6px 0;color:var(--muted);font-size:14px;}
  section code{background:#f2f0eb;padding:1px 5px;border-radius:3px;font-size:12.5px;}
  sup{font-size:10.5px;color:var(--accent);}
  p.fn{font-size:12.5px;color:var(--muted);background:#fcfbf9;border:1px solid var(--line);
    border-radius:6px;padding:9px 13px;margin:0 0 12px;}
  .tw{overflow-x:auto;margin:0 0 16px;-webkit-overflow-scrolling:touch;}
  table.data{width:100%;border-collapse:collapse;font-size:12.8px;min-width:560px;}
  table.data th{background:var(--accent-soft);color:var(--accent);font-weight:700;
    text-align:left;padding:9px 11px;border:1px solid #d4e6e2;white-space:nowrap;}
  table.data td{padding:8px 11px;border:1px solid var(--line);vertical-align:top;line-height:1.6;}
  table.data tbody tr:nth-child(even){background:#fcfbf9;}
  table.data td strong{color:var(--ink);}
  ul.ref li{word-break:break-word;}
  .toc{background:#fcfbf9;border:1px solid var(--line);border-radius:8px;padding:16px 22px;margin:0 0 30px;}
  .toc h2{font-family:var(--serif);font-size:17px;margin:0 0 10px;color:var(--accent);}
  .toc ol{margin:0;padding-left:22px;font-size:13.5px;}
  .toc li{margin-bottom:5px;}
  @media print{ .tw{overflow:visible;} table.data{min-width:0;} a{color:var(--ink);} }
"""


def main():
    chapters = []
    for k in range(1, 6):
        p = TMP / "P07-draft-ch{}.md".format(k)
        if not p.exists():
            sys.exit("[ABORT] 缺少章节核定稿: {} —— 五章齐备后再运行".format(p))
        chapters.append(p.read_text(encoding="utf-8"))
    print("[OK] 五章核定稿齐备")

    fw = {}
    fp = TMP / "P07-framework.json"
    if fp.exists():
        fw = json.loads(fp.read_text(encoding="utf-8"))
        print("[OK] 已载入框架件 P07-framework.json")
    else:
        print("[WARN] 未找到框架件，引言/结论留空（可二次运行补入）")

    # 交付前禁用词守卫：D33 已降级（无一手出处 URL）、D3/D4 已统一。
    # 无论哪个写者最后覆盖过文件，都不允许把这些表述带进主交付。
    BANNED = ("currently SUSPENDED", "现行暂停", "首批 4 家", "无限期暂停")
    scan = [("ch{}".format(i + 1), md) for i, md in enumerate(chapters)]
    scan += [("framework." + k, str(fw.get(k, "")))
             for k in ("intro", "conclusion", "toc", "toc_html")]
    violations = [(name, bad) for name, txt in scan for bad in BANNED if bad in txt]
    if violations:
        sys.exit("[ABORT] 交付前禁用词守卫触发（无一手出处或已被裁决废止的表述）: {}".format(violations))
    print("[OK] 禁用词守卫通过（D33 已撤下 / D3 / D4 口径统一）")

    sections = []
    if fw.get("intro"):
        sections.append({"title": "引言", "body": md_to_html(fw["intro"])})
    for idx, md in enumerate(chapters, 1):
        sections.append({
            "title": chapter_title(md),
            "body": md_to_html(strip_chapter_heading(md)),
        })
    if fw.get("conclusion"):
        sections.append({"title": "结论", "body": md_to_html(fw["conclusion"])})

    refs = collect_references(chapters)
    for extra in fw.get("extra_references", []) or []:
        if extra not in refs:
            refs.append(extra)
    print("[OK] Reference 去重后 {} 条".format(len(refs)))

    data = {
        "pid": PID,
        "theme": THEME,
        "date": DATE,
        "caliber": CALIBER,
        "sections": sections,
        "counter": COUNTER,
        "reference": refs,
    }
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[OK] 渲染数据: {}".format(DATA_PATH))

    # markdown 源报告
    md_parts = [
        "# {}".format(THEME), "",
        "> {} · 调研主交付 · 日期 {} ｜ 载体：自包含单页 HTML + markdown 源（本地 SSOT 不反向写）".format(PID, DATE), "",
        "## 口径块（Caliber）", "",
        "| 项目 | 口径 |", "|---|---|",
    ]
    md_parts += ["| {} | {} |".format(a, b) for a, b in CALIBER]
    md_parts += [""]
    if fw.get("toc"):
        md_parts += ["## 目录", "", fw["toc"], ""]
    if fw.get("intro"):
        md_parts += ["## 引言", "", fw["intro"], ""]
    md_parts += [md.strip() for md in chapters]
    if fw.get("conclusion"):
        md_parts += ["", "## 结论", "", fw["conclusion"], ""]
    md_parts += ["", "## 反方论点（≥5 条，含 ≥1 条时间维度）", ""]
    md_parts += ["{}. {}".format(i, re.sub(r"<[^>]+>", "", c)) for i, c in enumerate(COUNTER, 1)]
    md_parts += ["", "## Reference", ""]
    md_parts += ["- {}".format(r) for r in refs]
    md_parts += [""]
    MD_PATH.parent.mkdir(parents=True, exist_ok=True)
    MD_PATH.write_text("\n".join(md_parts), encoding="utf-8")
    print("[OK] markdown 源: {} ({} 字节)".format(MD_PATH, MD_PATH.stat().st_size))

    # 用套件渲染器（import 而不 subprocess，避免 shell 不稳）
    import importlib.util
    spec = importlib.util.spec_from_file_location("rk_render_html", SKILL_RENDER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.render(data, HTML_PATH)

    # 后处理：注入表格/正文 CSS、目录块、Reference 链接化
    from bs4 import BeautifulSoup
    text = HTML_PATH.read_text(encoding="utf-8")
    text = text.replace("</style>", EXTRA_CSS + "\n</style>", 1)
    soup = BeautifulSoup(text, "html.parser")
    doc = soup.find("article", class_="doc")
    if fw.get("toc_html") and doc:
        hr = doc.find("hr", class_="rule")
        box = soup.new_tag("div")
        box["class"] = "toc"
        h = soup.new_tag("h2")
        h.string = "目录"
        box.append(h)
        box.append(BeautifulSoup(fw["toc_html"], "html.parser"))
        if hr:
            hr.insert_after(box)
    for li in soup.select("ul.ref li"):
        raw = li.get_text()
        m = re.search(r"(https?://\S+)$", raw)
        if m:
            url = m.group(1)
            li.string = ""
            li.append(raw[: m.start()].rstrip(" —"))
            a = soup.new_tag("a", href=url, target="_blank", rel="noopener")
            a.string = url
            li.append(a)
    HTML_PATH.write_text(str(soup), encoding="utf-8")
    print("[OK] HTML 主交付: {} ({} 字节)".format(HTML_PATH, HTML_PATH.stat().st_size))

    # 交付自检
    body = HTML_PATH.read_text(encoding="utf-8")
    for ph in ["{{PID}}", "{{THEME}}", "{{SECTIONS}}", "{{CALIBER_ROWS}}",
               "{{COUNTER_ITEMS}}", "{{REFERENCE_ITEMS}}"]:
        assert ph not in body, "占位符未替换: " + ph
    assert "[UNSOURCED]" not in body, "存在未标注来源的数字"
    print("[OK] 自检通过：占位符全替换、无 [UNSOURCED]、sections={}、tables={}".format(
        len(sections), body.count('<table class="data">')))


if __name__ == "__main__":
    main()
