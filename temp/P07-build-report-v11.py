#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
P07 v1.1 组装器：把增补件 A1 作为「附录 A」并入主交付。

设计裁决（见 temp/P07-research-card-v3.md §20）：
- v1 五章正文 / 11 行口径块 / 7 条反方 / 框架件结论 **一律不改**，v1 原文件保留不动。
- 附录定位「T0 冻结期研究储备」，不编为第 6 章（第 5 章已是收口章）。
- 附录口径块与 7 条反方为**独立体系**，不并入报告级 caliber / counter（守 D42 与 H1）。
- 统一 Reference 由五章 + 增补件全文（含其人工分组索引）去重生成，显示端只保留附录正文。

输入：temp/P07-draft-ch1..ch5.md、temp/P07-framework.json、output/2026-11-10_...增补件_v1.md
输出：output/2026-11-10_行业_菲律宾合规CFD市场进入_v1.1.md / .html
      temp/P07-report-data-v11.json
用法：./.venv/Scripts/python.exe temp/P07-build-report-v11.py
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]      # 铁律 #1：零硬编码绝对路径
TMP, OUT = ROOT / "temp", ROOT / "output"

# 复用 v1 组装器的确定性解析链（v1 的 main() 有 __name__ guard，import 不执行）
_spec = importlib.util.spec_from_file_location("p07_v1_builder", TMP / "P07-build-report.py")
b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b)
# 覆盖为当前 checkout 自己的套件路径，保证在 worktree / 任意 clone 位置都能跑
b.SKILL_RENDER = (ROOT / ".workbuddy" / "skills" / "research-kit" / "references"
                  / "skills" / "research-html" / "render_html.py")
b.TPL = (ROOT / ".workbuddy" / "skills" / "research-kit" / "references"
         / "templates" / "html-delivery.html")

DATE = "2026-11-10"
PID = "P07"
THEME = b.THEME
BASENAME = "2026-11-10_行业_菲律宾合规CFD市场进入_v1.1"
MD_PATH = OUT / (BASENAME + ".md")
HTML_PATH = OUT / (BASENAME + ".html")
DATA_PATH = TMP / "P07-report-data-v11.json"

SUPP_PATH = OUT / "2026-11-10_行业_菲律宾合规CFD市场推广前置研究_校企合作交易社群KOL_v1.md"
V1_MD = OUT / "2026-11-09_行业_菲律宾合规CFD市场进入_v1.md"
V1_HTML = OUT / "2026-11-09_行业_菲律宾合规CFD市场进入_v1.html"
V1_MD_BYTES, V1_HTML_BYTES = 236089, 302593

APPENDIX_TITLE = "附录 A｜市场推广前置研究：实习机制（校企合作）、交易社群图谱、KOL 信任"
APPENDIX_SECTION_TITLE = "附录 A｜市场推广前置研究（T0 冻结期研究储备，不参与准入结论）"


def build_appendix(supp_text):
    """返回 (用于显示的附录正文, 用于抽 Reference 的增补件全文)。

    显示端：去掉增补件自己的 # 标题 / 目录 / Reference 分组索引；
            边界声明改写为附录语境；## → ###、### → ####；两个标题改名标明独立体系。
    """
    ls = supp_text.splitlines()
    i_toc = next(i for i, l in enumerate(ls) if l.startswith("## 目录"))
    i_after_toc = next(i for i in range(i_toc + 1, len(ls)) if ls[i].startswith("## "))
    i_ref = next(i for i, l in enumerate(ls) if l.startswith("## Reference"))

    head = [l for l in ls[1:i_toc] if not l.startswith("> ")]   # 去掉旧的「补充件」语境声明
    body = ls[i_after_toc:i_ref]                                  # 保留正文 + 附录独立反方

    def demote(line):
        m = re.match(r"^(#{2,3})\s+(.*)$", line)
        return "#" * (len(m.group(1)) + 1) + " " + m.group(2) if m else line

    merged = [demote(l) for l in head + body]
    merged = [l.replace("### 口径块（Caliber）",
                        "### 附录 A 口径块（独立体系，仅适用本附录）")
              .replace("### 反方论点（≥5 条，含 ≥1 条时间维度）",
                       "### 附录 A 反方论点（独立 7 条，不参与主报告反方计数）")
              for l in merged]

    boundary = [
        "> **附录 A · 版本与边界**：本附录由 2026-11-10 增补件 A1 并入；主交付 v1（2026-11-09 定稿，"
        "G_rubric 11/11、终稿复核 38/38）的五章正文、11 行口径块、7 条反方与结论**均未改写**，"
        "本附录**不参与、不改变准入证伪结论**。",
        "> **定位**：T0 冻结期的获客／传播前置情报，**不是可执行推广方案**；复杂项仅提供可执行调研思路与判据。",
        "> **检索窗口与 caveat**：公开网页索引快照 2026-11-09～10；未接入平台 API、未取得登录态、未做站内抓取，"
        "KOL 指标均为第三方索引页快照，不得当作平台实测数据。",
        "> **独立体系**：本附录口径块（as-of 2026-11-10，与主报告 2026-11-09 并列不合成）与 7 条反方"
        "仅适用本附录，不并入报告级口径块与反方计数；两部分来源统一收口于报告末尾 Reference。",
        "",
    ]
    return "\n".join(boundary + merged).strip() + "\n", supp_text


def main():
    if not SUPP_PATH.exists():
        sys.exit("[ABORT] 缺少增补件 A1: %s" % SUPP_PATH)
    # 用「运行前字节数」做锚点，而非硬编码常量：任意 checkout / CRLF 环境都能跑，
    # 且能证明本次运行确实没动 v1。另把已登记指纹作为信息报告。
    v1_before = (V1_MD.stat().st_size, V1_HTML.stat().st_size)
    print("[OK] v1 运行前指纹 %d / %d B（参数卡 §18 登记 %d / %d B，差异仅可能来自换行归一化）"
          % (v1_before[0], v1_before[1], V1_MD_BYTES, V1_HTML_BYTES))

    chapters = []
    for k in range(1, 6):
        p = TMP / ("P07-draft-ch%d.md" % k)
        if not p.exists():
            sys.exit("[ABORT] 缺少章节核定稿: %s" % p)
        chapters.append(p.read_text(encoding="utf-8"))
    fw = json.loads((TMP / "P07-framework.json").read_text(encoding="utf-8"))
    supp_text = SUPP_PATH.read_text(encoding="utf-8")
    appendix_display, appendix_refs_src = build_appendix(supp_text)
    print("[OK] 五章 + 框架件 + 增补件 A1 齐备；附录正文 %d 行" % len(appendix_display.splitlines()))

    # 交付前禁用词守卫：v1 的 D33/D3/D4 口径 + D43–D45 残留，附录同样受约束
    BANNED = ("currently SUSPENDED", "现行暂停", "首批 4 家", "无限期暂停",
              "test.manilatimes.net", "fintech@sec.gov.ph", "服务费收入 +74%",
              "比索禁令", "三家沙盒承接方", "VASP 暂停无限期", "[UNSOURCED]",
              "另有一条加强证据", "《CASP Rules》规定", "lbk.pub")
    scan = [("ch%d" % i, md) for i, md in enumerate(chapters, 1)]
    scan += [("framework." + k, str(fw.get(k, "")))
             for k in ("intro", "conclusion", "toc", "toc_html")]
    scan += [("appendix.display", appendix_display), ("supp.full", supp_text)]
    violations = [(name, bad) for name, txt in scan for bad in BANNED if bad in txt]
    if violations:
        sys.exit("[ABORT] 禁用词守卫触发: %s" % violations)
    print("[OK] 14 类禁用词守卫通过（含附录全文）")

    sections = [{"title": "引言", "body": b.md_to_html(fw["intro"])}]
    for md in chapters:
        sections.append({"title": b.chapter_title(md),
                         "body": b.md_to_html(b.strip_chapter_heading(md))})
    sections.append({"title": "结论", "body": b.md_to_html(fw["conclusion"])})
    sections.append({"title": APPENDIX_SECTION_TITLE, "body": b.md_to_html(appendix_display)})

    refs = b.collect_references(chapters + [appendix_refs_src])
    for extra in fw.get("extra_references", []) or []:
        if extra not in refs:
            refs.append(extra)
    print("[OK] Reference 去重后 %d 条（v1 = 167，新增 %d）" % (len(refs), len(refs) - 167))

    # 目录追加附录 A（标「非章节」，避免被读成第 6 章）
    toc_line = ("6. 附录 A（非章节）｜市场推广前置研究：实习机制（校企合作）、交易社群图谱、KOL 信任 "
                "—— T0 冻结期前置情报，不参与准入结论。")
    toc_md = fw["toc"].rstrip() + "\n" + toc_line
    toc_html = fw["toc_html"].replace(
        "</ol>", "<li>附录 A（非章节）｜市场推广前置研究：实习机制（校企合作）、交易社群图谱、KOL 信任"
                 " —— T0 冻结期前置情报，不参与准入结论。</li></ol>")

    data = {
        "pid": PID, "theme": THEME, "date": DATE,
        "caliber": b.CALIBER,          # 11 行，沿用 v1
        "sections": sections,          # 8 段 = 引言 + 5 章 + 结论 + 附录 A
        "counter": b.COUNTER,          # 7 条，沿用 v1
        "reference": refs,             # 216 条
    }
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---------- markdown 源（结构与 HTML sections 顺序一致） ----------
    md_parts = [
        "# %s" % THEME, "",
        "> %s · 调研主交付 **v1.1** · 日期 %s ｜ 载体：自包含单页 HTML + markdown 源（本地 SSOT 不反向写）" % (PID, DATE),
        "> **版本说明**：v1.1 = v1 五章正文与结论 + **附录 A**（2026-11-10 增补件 A1 并入）；"
        "v1 原文件保留不改，附录不参与准入结论。", "",
        "## 口径块（Caliber）", "", "| 项目 | 口径 |", "|---|---|",
    ]
    md_parts += ["| %s | %s |" % (a, c) for a, c in b.CALIBER]
    md_parts += ["", "## 目录", "", toc_md, ""]
    md_parts += ["## 引言", "", fw["intro"], ""]
    md_parts += [md.strip() for md in chapters]
    md_parts += ["", "## 结论", "", fw["conclusion"], ""]
    md_parts += ["# %s" % APPENDIX_SECTION_TITLE, "", appendix_display.strip(), ""]
    md_parts += ["## 反方论点（主报告 7 条，不含附录 A；≥5 条且含 ≥1 条时间维度）", ""]
    md_parts += ["%d. %s" % (i, re.sub(r"<[^>]+>", "", c)) for i, c in enumerate(b.COUNTER, 1)]
    md_parts += ["", "## Reference（主报告 + 附录 A 统一去重，%d 条）" % len(refs), ""]
    md_parts += ["- %s" % r for r in refs]
    md_parts += [""]
    MD_PATH.write_text("\n".join(md_parts), encoding="utf-8")
    print("[OK] markdown 源: %s (%d B)" % (MD_PATH.name, MD_PATH.stat().st_size))

    # ---------- HTML：复用套件渲染器 + 后处理 ----------
    spec = importlib.util.spec_from_file_location("rk_render_html_v11", b.SKILL_RENDER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.render(data, HTML_PATH)

    from bs4 import BeautifulSoup
    text = HTML_PATH.read_text(encoding="utf-8")
    text = text.replace("</style>", b.EXTRA_CSS + "\n</style>", 1)
    soup = BeautifulSoup(text, "html.parser")
    doc = soup.find("article", class_="doc")
    if doc:
        hr = doc.find("hr", class_="rule")
        box = soup.new_tag("div")
        box["class"] = "toc"
        h = soup.new_tag("h2")
        h.string = "目录"
        box.append(h)
        box.append(BeautifulSoup(toc_html, "html.parser"))
        if hr:
            hr.insert_after(box)
        # 版本说明（模板只有 DATE，v1.1 需显式标注）
        sub = doc.select_one(".sub")
        if sub:
            meta = soup.new_tag("div")
            meta["class"] = "meta"
            meta.string = "v1.1｜2026-11-10｜v1 五章正文与结论未改写，新增附录 A（增补件 A1 并入，不参与准入结论）"
            sub.insert_after(meta)
    for li in soup.select("ul.ref li"):
        raw = li.get_text()
        m = re.search(r"(https?://\S+)$", raw)
        if m:
            url = m.group(1)
            li.string = ""
            li.append(raw[:m.start()].rstrip(" —"))
            a = soup.new_tag("a", href=url, target="_blank", rel="noopener")
            a.string = url
            li.append(a)
    HTML_PATH.write_text(str(soup), encoding="utf-8")
    print("[OK] HTML 主交付: %s (%d B)" % (HTML_PATH.name, HTML_PATH.stat().st_size))

    # ---------- 交付自检 ----------
    body = HTML_PATH.read_text(encoding="utf-8")
    for ph in ["{{PID}}", "{{THEME}}", "{{SECTIONS}}", "{{CALIBER_ROWS}}",
               "{{COUNTER_ITEMS}}", "{{REFERENCE_ITEMS}}"]:
        assert ph not in body, "占位符未替换: " + ph
    assert "[UNSOURCED]" not in body
    assert "附录 A" in body
    assert (V1_MD.stat().st_size, V1_HTML.stat().st_size) == v1_before
    print("[OK] 自检通过：占位符 0 / [UNSOURCED] 0 / 附录 A 在册 / v1 原文件未被改动")
    print("[OK] sections=%d  tables=%d  reference=%d" % (
        len(sections), body.count('<table class="data">'), len(refs)))


if __name__ == "__main__":
    main()
