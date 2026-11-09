# -*- coding: utf-8 -*-
"""P07 终稿确定性修补（D42/D43）。原子性：全部替换校验通过后才一次性落盘。
不新增任何未核验事实；只做「减无出处事实 / 增口径说明 / 换已验证域名 / 拆单源合并」。
用 read_bytes/write_bytes 保留各文件原有换行风格（CH3 为 CRLF，其余为 LF）。
"""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
CARD_ONLY = "--card-only" in sys.argv   # 章内修补已落盘时，只补写参数卡

T = Path(__file__).resolve().parent
CH = {i: T / ("P07-draft-ch%d.md" % i) for i in range(1, 6)}
CARD = T / "P07-research-card-v3.md"

# ---------------- 1. 章内确定性替换 ----------------
# (文件, old, new, 期望命中数, 说明)
REPL = [
    # D43-a：staging 域名 → 上一轮已逐条 WebFetch 验证的正式域名
    (1, "https://test.manilatimes.net/", "https://www.manilatimes.net/", 3,
     "CH1 staging 域名 3 处"),
    (5, "https://test.manilatimes.net/", "https://www.manilatimes.net/", 6,
     "CH5 staging 域名 6 处"),

    # D43-b：删无内联出处的 +74%，并把表格已有的 130 万现金网点补进正文论据
    (4,
     "GCash 的 4,150 万月活、210 万 QR 商户与日均 6,240 万笔构成渠道密度与单位经济；"
     "Maya 的商户收单（服务费收入 +74%）与 AI 承保",
     "GCash 的 4,150 万月活、210 万 QR 商户、130 万现金网点与日均 6,240 万笔构成渠道密度与单位经济；"
     "Maya 的商户收单与 AI 承保",
     1, "CH4 删无出处增速 +74%，补 130 万现金网点到正文"),

    # D43-c：无一手出处的邮箱改为显式「不列明 + 须核验」
    (5,
     "④ **CASP Form 1 递 PhiliFINNO**（fintech@sec.gov.ph）并持续月／季／年报",
     "④ **CASP Form 1 递 PhiliFINNO**（具体投递邮箱／表单地址本轮未取得 SEC 一手出处，"
     "本稿不列明，须实施前向 SEC 核验）并持续月／季／年报",
     1, "CH5 删无出处 fintech@sec.gov.ph"),

    # D43-d：小结「比索禁令」与 D15 冲突 → 改法币层/产品层分离
    (5,
     "＋90 天集成／24 个月分阶段／知识测试／比索禁令**",
     "＋90 天集成／24 个月分阶段／知识测试／比索层按 D15 分离"
     "（产品层不移动比索、法币层外包持牌 VASP）**",
     1, "CH5 小结「比索禁令」→ D15 分层表述"),

    # D43-e：Quevedo 双句拆源（WebFetch 核实：Bitdigest 承载「非快车道」，「不治愈」另挂 Mintchain）
    (5,
     "SEC 委员 Quevedo 2026-08 称入盒「不是通往 SEC 获批的快车道」且「不治愈」既往 SRC 违法"
     "（[Bitdigest, 引 2026-08-26 表态]"
     "(https://www.bitdigest.io/posts/sec-chairperson-francis-lim-defends-blockshoals-admission-to-strategic-sandbox)）。",
     "SEC 委员 Quevedo 2026-08 称入盒「不是通往 SEC 获批的快车道」"
     "（[Bitdigest, 引 2026-08-26 表态]"
     "(https://www.bitdigest.io/posts/sec-chairperson-francis-lim-defends-blockshoals-admission-to-strategic-sandbox)）；"
     "另有行业媒体转述其「沙盒不治愈此前 SRC 违规的处罚」表述"
     "（[Mintchain, 2026](https://mintchain.ph/?p=3441)），两源分列不合成，"
     "本稿仅登记同期官方反驳，不作条文效力判断。",
     1, "CH5 正文 Quevedo 双句拆挂 Bitdigest / Mintchain"),

    (5,
     "｜「入盒不治愈既往 SRC 违法」；90 天仅限技术集成，不含公开 onboarding／交易／全面商营。",
     "｜Quevedo「入盒非获批快车道」表态；90 天仅限技术集成，"
     "不含公开 onboarding／交易／全面商营。「不治愈既往 SRC 违法」另见本清单第 8 条 Mintchain，两源分列不合成。",
     1, "CH5 来源清单第 9 条同步拆源"),

    # D43-f：CH1 审稿 PASS 10/10 附带建议——同一条 D18 证据被重复计数，且法规名称
    # 《CASP Rules》与 CH1 L46 的《CASP Guidelines》不一致。删重复句，保留紧随其后的边界声明。
    (1,
     "另有一条加强证据：SEC MC No.5 s.2025《CASP Rules》规定「除非 SEC 另行允许，"
     "CASP 不得提供加密资产衍生品或杠杆交易」"
     "（[Ablola Law](https://ablola.co?p=16716/)；[RegAlert 全文]"
     "(https://regalert.today/document/sec-guidelines-on-the-operations-of-crypto-asset-service-providers-sec-casp-guid-3b1b57f6-978d-4185-aac9-ff489684621e)）。"
     "**但须守住边界**",
     "**但须守住边界**",
     1, "CH1 删 D18 重复证据计数（保留边界声明）"),

    # D43-g：CH3 重审 REVISE 必改 2——「三家」与本章 L20「累计 4 家」自相矛盾
    (3,
     "这解释了为何三家沙盒承接方分别落在",
     "这解释了为何四家沙盒承接方分别落在",
     1, "CH3「三家沙盒承接方」→「四家」"),

    # D43-h：CH3 重审 REVISE 必改 3——反方⑤时间线补 2025-06 节点；
    #        同时把「VASP 暂停无限期」单写改成 D3 的「持续生效＋视情重估（律所解读并列）」
    (3,
     "2024-03 封 Binance → 2025-08 VASP 暂停无限期 → 2025-12 封约 50 家",
     "2024-03 封 Binance → 2025-06 GCash GStocks Global／Pluang PH 获批 StratBox 测试"
     "（美股代币化入口，合规承接侧开放）→ 2025-08 BSP M-2025-031 新 VASP 申请自 2025-09-01 "
     "持续生效、视 global and local developments 重估（律所解读为无限期延长，两口径并列）"
     "→ 2025-12 封约 50 家",
     1, "CH3 反方⑤补 2025-06 节点并同步 D3"),
]

cache = {}          # path -> str（原文）
pending = {}        # path -> str（改后文）
log = []

def get(p):
    if p not in cache:
        cache[p] = p.read_bytes().decode("utf-8")
    return cache[p]

if not CARD_ONLY:
    for idx, old, new, expect, desc in REPL:
        p = CH[idx]
        cur = pending.get(p, get(p))
        n = cur.count(old)
        if n != expect:
            print("[ABORT] %s : 命中 %d，期望 %d  → %s" % (desc, n, expect, p.name))
            sys.exit(2)
        pending[p] = cur.replace(old, new)
        log.append("OK  %-46s x%d" % (desc, n))
else:
    log.append("SKIP 章内替换（--card-only：4 章正文修补已于上一次运行落盘）")

# ---------------- 2. 参数卡：补录 D42 / D43 ----------------
card = get(CARD)
lines = card.split("\n")

# 2.1 在 §17 表格 D41 行后插入 D42 / D43
d41 = next(i for i, l in enumerate(lines) if l.startswith("| D41 |"))
assert not any(l.startswith("| D42 |") for l in lines), "D42 已存在，避免重复插入"
D42 = ("| D42 | 第 2 章 REVISE 要求「章首新增口径块」 | **驳回章内新增**：报告级顶部口径块已由组装器统一渲染"
       "（11 行），满足 rubric §1②；再在各章首复制一份违反 H1 单一数据源，且会造成多份口径块漂移。"
       "改为章内表格注用 `[^fx]` 指向脚注。**D14／D2／D9／D37 与本条共同构成第 2 章修订基线**。 |")
D43 = ("| D43 | 终稿残留 5 类（staging 域名、无出处邮箱、无出处增速数字、D15 口径词、引语单源合并） | "
       "由 `temp/P07-final-fixes.py` 一次性确定性修补：`test.manilatimes.net` → `www.manilatimes.net`"
       "（9 处，上一轮已逐条 WebFetch 验证正式域名可加载）；`fintech@sec.gov.ph` 改为"
       "「未取得一手出处、不列明、须实施前向 SEC 核验」；CH4「服务费收入 +74%」删具体数值并把表格已有的"
       "「130 万现金网点」补进正文论据；CH5 小结「比索禁令」改 D15 分层表述；Quevedo「非快车道」与"
       "「不治愈」拆挂 Bitdigest／Mintchain 两源。**均为减事实或增口径，不新增未核验事实**。 |")
lines[d41 + 1:d41 + 1] = [D42, D43]
log.append("OK  参数卡 §17 补录 D42 / D43")

# 2.2 参数卡 §3：消除「−13.7% / −9.2% 并列登记」与 CH1 只写 PSA 一手 −9.2% 的表面张力
#     （CH1 审稿已判定此处无错，但补上跨章用法规则，防止后续审稿再次误判）
i3 = next(i for i, l in enumerate(lines) if l.startswith("- 2026 宏观双期并列："))
lines[i3] = lines[i3] + (
    " **跨章用法说明（D43）**：参数卡登记全部并列口径；单章可择一手主值"
    "（CH1 采用 PSA 一手 −9.2%、CH2／CH5 按时间维度反方需要并列两值），择一不等于否认另一口径；"
    "但不得把 −13.7%（Philstar／The Freeman）挂到只记 −9.2% 的 BusinessWorld／PSA 来源上，"
    "也不得取平均或合成。"
)
log.append("OK  参数卡 §3 补跨章用法说明")

# 2.3 重写 §9 章节状态（旧版停留在「落盘指令刚发出」时点）
s9 = next(i for i, l in enumerate(lines) if l.startswith("## 9. 章节状态"))
s13 = next(i for i, l in enumerate(lines) if l.startswith("## 13."))
NEW9 = [
    "## 9. 章节状态（终稿对齐 · 2026-11-09）",
    "- ✅ **5 章核定稿全部落盘**：`temp/P07-draft-ch1.md` 50,201 B／`ch2` 32,651 B／`ch3` 31,626 B／"
    "`ch4` 45,811 B／`ch5` 41,706 B（终稿修补后字节数见 §18）。",
    "- ✅ **5 路审稿覆盖完成**：CH1 PASS 10/10（按 50,201 B 版重读，8 条裁决全落地、44 条来源清单为正确终态）、"
    "CH2 REVISE 8/10 → 3 项必改由 `draft-reviser-ch2` 落地（D14 撤下组删除、`−13.7%`／`−9.2%` 双源并列、"
    "`[^fx]` 汇率两时点脚注）、CH3 REVISE 9/10 → 3 项必改由 `P07-apply-fixes.py`＋D43 落地"
    "（累计 4 家口径、「四家」量词、反方⑤补 2025-06 节点）、CH4 PASS 9/10、CH5 PASS 9/10。"
    "**五章五维均 ≥8/10 且任一维 ≠0，G_rubric 后置通过线满足**。",
    "- ✅ 框架件 `temp/P07-framework.json` 已定稿：intro／conclusion／toc／toc_html／extra_references 五键；"
    "禁用词 0、`D33` 0、`非明文禁止` 1。框架撰写人已 shutdown，不再写入。",
    "- ✅ 渲染链：`P07-build-report.py`（含交付前禁用词守卫）＋`P07-apply-fixes.py`＋`P07-final-fixes.py`＋"
    "`P07-report-data.json`＋套件 `render_html.py`／`html-delivery.html`（**套件文件未改动**，"
    "只在输出 HTML 注入表格 CSS 与 Reference 链接化）。",
    "- ✅ G_rubric 前置机械自检：`P07-rubric-check.py` 11/11 PASS；客单价恒等式数值复算闭合"
    "（金额 +42.0249% vs 频次×客单 +42.0112%，差 −0.0137pp）。",
    "- 🔄 待办：重跑组装器覆盖 md/html → 终稿禁用词与结构复核 → 更新 §18 交付物 → 最终呈现 → 团队收尾。",
    "",
]
lines[s9:s13] = NEW9
log.append("OK  参数卡 §9 重写为终稿状态")
pending[CARD] = "\n".join(lines)

# ---------------- 3. 原子性落盘 ----------------
print("=" * 72)
for x in log:
    print("  " + x)
print("=" * 72)
BANNED = ("currently SUSPENDED", "现行暂停", "首批 4 家", "无限期暂停")
for p, txt in pending.items():
    # 参数卡是裁决记录，「引用被禁表述本身」属正当；禁用词守卫只作用于交付正文（五章）
    if p in CH.values():
        bad = {k: txt.count(k) for k in BANNED if txt.count(k)}
        if bad:
            print("[ABORT] %s 出现禁用词 %s" % (p.name, bad)); sys.exit(3)
    p.write_bytes(txt.encode("utf-8"))
    print("  WRITE %-30s %d B" % (p.name, p.stat().st_size))

# ---------------- 4. 落盘后复验 ----------------
print("=" * 72)
allc = "\n".join((T / ("P07-draft-ch%d.md" % i)).read_bytes().decode("utf-8") for i in range(1, 6))
checks = {
    "test.manilatimes.net": 0, "fintech@sec.gov.ph": 0,
    "服务费收入 +74%": 0, "比索禁令": 0, "130 万现金网点": 2,
    "currently SUSPENDED": 0, "首批 4 家": 0, "三家沙盒承接方": 0,
    "四家沙盒承接方": 1, "另有一条加强证据": 0, "VASP 暂停无限期": 0,
    "2025-06 GCash GStocks Global": 1,
}
ok = True
for k, want in checks.items():
    got = allc.count(k)
    flag = "OK " if got == want else "FAIL"
    if got != want: ok = False
    print("  %-4s %-30s got=%-3d want=%d" % (flag, k, got, want))
# www 正式域名：原有若干 + 新替换 9 处，只设下限
got = allc.count("www.manilatimes.net")
flag = "OK " if got >= 9 else "FAIL"
if got < 9: ok = False
print("  %-4s %-30s got=%-3d want=>=9" % (flag, "www.manilatimes.net", got))
print("=" * 72)
print("FINAL_FIXES " + ("PASS" if ok else "FAIL"))
sys.exit(0 if ok else 4)
