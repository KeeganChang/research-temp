#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
gen_ecommerce_data.py — 生成「多平台直播电商」经营分析样本数据集 → SQLite

背景：
    method-ecommerce-ops（belongs_to_track: diagnostic）的 M1–M5 / R1–R2 需要一套
    「渠道 × 日期 × 账户」粒度的漏斗明细，才能做**账户口径锁定（cohort-locked）**的
    转化分析。外部拿不到真实后台数据，因此用受控的生成脚本造一份内部自洽的样本，
    让「漏斗口径 / 流量结构 / 归因」这套方法可以先跑通、再换真数据。

设计要点（与 method-ecommerce-ops 的口径登记一一对应）：
    1. **一行 = 一个「账户 × 日期 × 场次」的会话**，step_* 单调递增蕴含
       （step_entered=1 ⇒ step_exposed=1；…；step_paid=1 ⇒ step_ordered=1）。
       因此 COUNT(DISTINCT CASE WHEN step_x THEN account_id END) 天然是
       曝光 cohort 的子集 —— 分子分母账户同源，不需额外 JOIN 过滤。
    2. **acq_source** 区分自然(1)/付费(2)进入的人，是流量结构（自然占比）的唯一来源，
       **与广告消耗同源**：spend = 付费曝光/1000 × CPM，故 ROI 可与漏斗自洽互算。
    3. 金额一律 **整数分**，避免浮点累积误差。
    4. 同一 random.Random(seed ^ day_ordinal) 驱动，**完全可复现**。

用法：
    python -m script.gen_ecommerce_data                        # 全量 2025-01-01 ~ 今天
    python -m script.gen_ecommerce_data --limit-days 30        # 冒烟（只生成头 30 天）
    python -m script.gen_ecommerce_data --db <root>/data/ecommerce_ops.db --start 2025-01-01 --end 2026-10-30

产出：
    <root>/data/ecommerce_ops.db   （若已存在则先删除重建，保证幂等）
"""

from __future__ import annotations

import argparse
import random
import bisect
import sqlite3
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

ROOT_MARKER = "AGENTS.md"
DEFAULT_DB = "data/ecommerce_ops.db"
DEFAULT_START = "2025-01-01"
DEFAULT_SEED = 20261030

# ── 漏斗层级（顺序即漏斗方向，勿改）────────────────────────────
FUNNEL_STEPS = ("exposed", "entered", "stayed", "cart", "ordered", "paid")

# 货品角色：1=引流款 2=爆款 3=利润款 4=秒杀款
PRODUCT_CATS = {1: "引流款", 2: "爆款", 3: "利润款", 4: "秒杀款"}
CAT_PRICE_MULT = {1: 0.35, 2: 1.00, 3: 1.85, 4: 0.48}
CAT_ORDER_WEIGHT = {1: 0.28, 2: 0.38, 3: 0.19, 4: 0.15}

# 主播权重：刻意做成头部集中（头部占该渠道曝光 ~42%），
# 用于 M5「单点依赖」识别；mult 是该主播的转化乘数。
HOST_WEIGHTS = (0.42, 0.22, 0.16, 0.12, 0.08)
HOST_MULTS = (1.18, 1.06, 0.96, 0.88, 0.80)


@dataclass(frozen=True)
class ChannelCfg:
    cid: int
    key: str
    name: str
    platform: str
    exp_base: int          # 起始期日均曝光人次（不含大促/增长）
    growth: float          # 21 个月总规模增长倍数
    p_enter: float
    p_stay: float
    p_cart: float
    p_order: float
    p_pay: float
    aov_cents: int         # 客单价（分）
    cv: float              # 客单价离散系数
    org_start: float       # 分析期起点自然流量占比
    org_end: float         # 分析期终点自然流量占比
    cpm_cents: int         # 千次付费曝光的等效投放成本（分，oCPM 等效；按目标 ROI 反推标定）
    cpm_growth: float      # CPM 涨幅（体现「付费越来越贵」）
    pay_penalty: float     # 付费流量相对自然的转化乘数（付费质量更差）
    degrade_at: str | None = None   # 若有：此日之后付费侧额外劣化（ch.pid is the own etimolodz; (see code) 付费 cart 率打折）
    degrade_cart: float = 1.0       # 付费 cart 率折扣
    hostname_prefix: str = ""


CHANNELS: tuple[ChannelCfg, ...] = (
    ChannelCfg(
        cid=1, key="douyin", name="抖音", platform="内容电商",
        exp_base=1380, growth=1.65,
        p_enter=0.110, p_stay=0.52, p_cart=0.17, p_order=0.42, p_pay=0.885,
        aov_cents=48200, cv=0.44,
        org_start=0.63, org_end=0.435, cpm_cents=46500, cpm_growth=1.34,
        pay_penalty=0.80, degrade_at="2026-04-01", degrade_cart=0.86,
        hostname_prefix="抖",
    ),
    ChannelCfg(
        cid=2, key="taobao", name="淘宝直播", platform="货架+直播",
        exp_base=800, growth=1.30,
        p_enter=0.075, p_stay=0.48, p_cart=0.160, p_order=0.405, p_pay=0.905,
        aov_cents=88600, cv=0.50,
        org_start=0.44, org_end=0.355, cpm_cents=73700, cpm_growth=1.22,
        pay_penalty=0.82, hostname_prefix="淘",
    ),
    ChannelCfg(
        cid=3, key="shipinhao", name="视频号", platform="私域+公域",
        exp_base=520, growth=2.10,
        p_enter=0.105, p_stay=0.625, p_cart=0.215, p_order=0.485, p_pay=0.925,
        aov_cents=62400, cv=0.42,
        org_start=0.79, org_end=0.735, cpm_cents=74300, cpm_growth=1.10,
        pay_penalty=0.87, hostname_prefix="微",
    ),
    ChannelCfg(
        cid=4, key="kuaishou", name="快手", platform="信任电商",
        exp_base=950, growth=1.42,
        p_enter=0.115, p_stay=0.55, p_cart=0.190, p_order=0.445, p_pay=0.735,
        aov_cents=31800, cv=0.46,
        org_start=0.68, org_end=0.605, cpm_cents=33200, cpm_growth=1.28,
        pay_penalty=0.84, hostname_prefix="快",
    ),
)

HOST_STEMS = ("小满", "阿哲", "一诺", "Sam", "Q酱")


def find_workspace_root(start: Path | None = None) -> Path:
    here = (start or Path(__file__).resolve().parent).resolve()
    for cand in [here, *here.parents]:
        if (cand / ROOT_MARKER).is_file():
            return cand
    sys.exit(f"[ERROR] 未找到 {ROOT_MARKER}，无法确定 workspace 根（从 {here} 向上查找失败）")


def parse_date(s: str) -> date:
    return date.fromisoformat(s)


def smoothstep(t: float) -> float:
    """0→1 的平滑过渡（用于「缓慢漂移」类参数，避免线性拐点失真）。"""
    t = min(1.0, max(0.0, t))
    return t * t * (3.0 - 2.0 * t)


def weighted_sample_wo(rng: random.Random, items: list, weights: tuple, k: int) -> list:
    """按权重无放回抽 k 个，保持 items 原有顺序（模拟「今天安排哪几位主播上播」）。"""
    pool = list(items)
    wts = list(weights)
    picked: list = []
    for _ in range(min(k, len(pool))):
        tot = sum(wts)
        r = rng.random() * tot
        acc = 0.0
        for i, wt in enumerate(wts):
            acc += wt
            if r <= acc:
                picked.append(pool.pop(i))
                wts.pop(i)
                break
    return sorted(picked)


def promo_weight(d: date) -> tuple[float, str]:
    """大促日历：返回 (曝光放大系数, 标签)。非大促 = (1.0, '日常')。"""
    md = (d.month, d.day)
    if md == (6, 18) or (d.month == 6 and 15 <= d.day <= 20):
        return 3.4, "618"
    if d.month == 11 and (d.day == 11 or 10 <= d.day <= 12):
        return 4.2, "双11"
    if d.month == 12 and 10 <= d.day <= 13:
        return 2.6, "双12"
    if d.month == 1 and 10 <= d.day <= 28:
        return 1.9, "年货节"
    if md == (3, 8) or (d.month == 3 and 6 <= d.day <= 9):
        return 1.8, "38女王节"
    if d.month == 8 and 17 <= d.day <= 19:
        return 1.7, "818"
    if d.month == 9 and 8 <= d.day <= 10:
        return 1.6, "99大促"
    return 1.0, "日常"


def dow_mult(d: date) -> float:
    """周内效应：周末流量更高。"""
    return (0.86, 0.92, 0.95, 0.97, 1.02, 1.18, 1.15)[d.weekday()]


class AccountPool:
    """账户池：按 first_seen 升序排列，支持「只抽已存在账户」。

    这是「不考虑后面的新增账户」的物理保障 —— 某天能抽到的账户，
    只可能是那天之前就已经进池的；后续新注册账户不会回填历史漏斗。
    """

    def __init__(self, size: int, days: int, seed: int, pre_days: int = 540):
        rng = random.Random(seed ^ 0xA11CE)
        self.size = size
        self.pre_days = pre_days
        # first_seen 用「相对起始日的偏移」表示，负值 = 分析窗口之前就已存在的存量账户。
        # 存量账户必须存在，否则「新增 vs 存量」的分群对照（Q15）永远只有一类。
        fs = []
        for _ in range(size):
            if rng.random() < 0.45:
                fs.append(-int(1 + pre_days * (rng.random() ** 1.4)))   # 窗口前老客
            else:
                fs.append(int(days * (rng.random() ** 1.7)))            # 期内新客，偏早期
        self.first_seen = sorted(fs)
        # 忠诚度：影响该账户的转化倾向（beta-ish 分布，取 0.55~1.55）
        self.loyalty = [0.55 + 1.0 * (rng.random() * rng.random() ** 0.6) for _ in range(size)]
        # 累积可用边界：available[i] = 第 i 天时已进池的账户数
        # 用二分替代 O(days×size) 全表：available[i] = first_seen <= i 的账户数（负值天然计入）
        self.available = [bisect.bisect_right(self.first_seen, i) for i in range(days)]

    def n_available(self, day_idx: int) -> int:
        return self.available[min(day_idx, len(self.available) - 1)]


DDL = """
DROP TABLE IF EXISTS dim_channel;
DROP TABLE IF EXISTS dim_account;
DROP TABLE IF EXISTS dim_host;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS fact_session;
DROP TABLE IF EXISTS fact_account_funnel;
DROP TABLE IF EXISTS fact_ad_daily;

CREATE TABLE dim_channel (
    channel_id    INTEGER PRIMARY KEY,
    channel_key   TEXT NOT NULL UNIQUE,
    channel_name  TEXT NOT NULL,
    platform_type TEXT NOT NULL
);

CREATE TABLE dim_account (
    account_id  INTEGER PRIMARY KEY,
    first_seen  TEXT NOT NULL,
    loyalty     REAL NOT NULL
);

CREATE TABLE dim_host (
    host_id    INTEGER PRIMARY KEY,
    channel_id INTEGER NOT NULL,
    host_name  TEXT NOT NULL,
    is_head    INTEGER NOT NULL
);

CREATE TABLE dim_product (
    product_id   INTEGER PRIMARY KEY,
    channel_id   INTEGER NOT NULL,
    category_id  INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    list_price   INTEGER NOT NULL
);

CREATE TABLE dim_date (
    stat_date  TEXT PRIMARY KEY,
    yyyymm     TEXT NOT NULL,
    yyyyq      TEXT NOT NULL,
    dow        INTEGER NOT NULL,
    promo_tag  TEXT NOT NULL,
    is_promo   INTEGER NOT NULL
);

-- 场次：一天 N 场，每场绑定主播与投放预算
CREATE TABLE fact_session (
    session_id   INTEGER PRIMARY KEY,
    channel_id   INTEGER NOT NULL,
    stat_date    TEXT NOT NULL,
    host_id      INTEGER NOT NULL,
    slot         INTEGER NOT NULL,
    duration_min INTEGER NOT NULL,
    spend_cents  INTEGER NOT NULL
);

-- 核心事实表：账户 × 日期 × 场次
-- 一行 = 一次「曝光会话」，step_* 单调递增蕴含，保证漏斗分子必为分母子集。
CREATE TABLE fact_account_funnel (
    stat_date    TEXT NOT NULL,
    channel_id   INTEGER NOT NULL,
    session_id   INTEGER NOT NULL,
    account_id   INTEGER NOT NULL,
    acq_source   INTEGER NOT NULL,     -- 1=自然流量 2=付费流量
    step_exposed INTEGER NOT NULL,     -- 恒为 1（存在即被曝光）
    step_entered INTEGER NOT NULL,     -- 进入直播间
    step_stayed  INTEGER NOT NULL,     -- 停留 > 30s
    step_cart    INTEGER NOT NULL,     -- 点击购物车
    step_ordered INTEGER NOT NULL,     -- 下单
    step_paid    INTEGER NOT NULL,     -- 支付成功
    stay_seconds INTEGER NOT NULL,
    interacted   INTEGER NOT NULL,     -- 评论/点赞/分享任一
    order_cents  INTEGER NOT NULL,     -- 下单金额（分）
    paid_cents   INTEGER NOT NULL,     -- 支付金额（分）= GMV 口径
    product_cat  INTEGER               -- 1引流 2爆款 3利润 4秒杀；仅下单时有值
);

-- 投放日汇总：与 fact_account_funnel 的付费侧同源
CREATE TABLE fact_ad_daily (
    stat_date     TEXT NOT NULL,
    channel_id    INTEGER NOT NULL,
    paid_impr     INTEGER NOT NULL,    -- 付费曝光人次
    organic_impr  INTEGER NOT NULL,    -- 自然曝光人次
    spend_cents   INTEGER NOT NULL,
    PRIMARY KEY (stat_date, channel_id)
);
"""


def build_dims(con: sqlite3.Connection, channels, start: date, dates: list[date]) -> tuple[list[int], dict]:
    days = len(dates)
    con.executescript(DDL)

    con.executemany(
        "INSERT INTO dim_channel VALUES (?,?,?,?)",
        [(c.cid, c.key, c.name, c.platform) for c in channels],
    )

    # ── 账户池 ──
    pool = AccountPool(size=360_000, days=days, seed=DEFAULT_SEED)
    con.executemany(
        "INSERT INTO dim_account VALUES (?,?,?)",
        [
            (i + 1, (start + timedelta(days=pool.first_seen[i])).isoformat(), round(pool.loyalty[i], 4))
            for i in range(pool.size)
        ],
    )

    # ── 主播：每渠道 5 人，权重与 dim 表一致 ──
    host_names: dict[tuple[int, int], str] = {}
    rows = []
    hid = 0
    for c in channels:
        for k, stem in enumerate(HOST_STEMS):
            hid += 1
            rows.append((hid, c.cid, f"{c.hostname_prefix}·{stem}", 1 if k == 0 else 0))
            host_names[(c.cid, k)] = hid
    con.executemany("INSERT INTO dim_host VALUES (?,?,?,?)", rows)

    # ── 商品：每渠道每个角色 4 款 ──
    prows = []
    pid = 0
    for c in channels:
        for cat in sorted(PRODUCT_CATS):
            for n in range(1, 5):
                pid += 1
                price = int(c.aov_cents * CAT_PRICE_MULT[cat] * (0.82 + 0.11 * n))
                prows.append((pid, c.cid, cat, f"{c.name}-{PRODUCT_CATS[cat]}-{n:02d}", price))
    con.executemany("INSERT INTO dim_product VALUES (?,?,?,?,?)", prows)

    # ── 日期维 ──
    drows = []
    for d in dates:
        _w, tag = promo_weight(d)
        drows.append(
            (d.isoformat(), f"{d.year}{d.month:02d}", f"{d.year}Q{(d.month - 1) // 3 + 1}",
             d.weekday(), tag, 1 if tag != "日常" else 0)
        )
    con.executemany("INSERT INTO dim_date VALUES (?,?,?,?,?,?)", drows)

    con.commit()
    return [], {"pool": pool, "host_names": host_names, "product_rows": prows}


def gen_channel_day(
    rng: random.Random, c: ChannelCfg, d: date, day_idx: int, days: int,
    pool: AccountPool, host_names, t: float, ds: str, session_seq: list[int],
) -> tuple[list[tuple], list[tuple], dict]:
    """生成「某渠道某天」的全部会话行 + 场次行。

    返回 (funnel_rows, session_rows, day_metrics)
    """
    promo_mult, promo_tag = promo_weight(d)
    growth = c.growth ** (day_idx / max(1, days - 1))
    base = c.exp_base * growth * promo_mult * dow_mult(d)
    # 周度级别的随机波动（±12%），不用日噪声以免漏斗日序列过抖
    base *= 0.94 + 0.12 * rng.random()
    n_exposed = max(60, int(base * (0.97 + 0.06 * rng.random())))

    organic_share = c.org_start + (c.org_end - c.org_start) * smoothstep(t)
    # 大促期间自然占比会被压制（付费买量集中投放）
    if promo_tag != "日常":
        organic_share *= 0.80
    organic_share = min(0.92, max(0.22, organic_share * (0.96 + 0.08 * rng.random())))

    n_org = int(n_exposed * organic_share)
    n_paid = n_exposed - n_org

    cpm = c.cpm_cents * (c.cpm_growth ** t)
    spend = int(n_paid / 1000.0 * cpm * (0.95 + 0.10 * rng.random()))

    # ── 拆场次：当天出场的 n 名主播按权重「无放回」抽签 ──
    # （按 k=0..n 固定取前几名会让排在后面的主播永远不出场，集中度分析就失真了）
    n_sessions = 2 + (1 if rng.random() < 0.45 else 0)
    idx = weighted_sample_wo(rng, list(range(len(HOST_WEIGHTS))), HOST_WEIGHTS, n_sessions)
    w = [HOST_WEIGHTS[i] for i in idx]
    wsum = sum(w)
    quotas = [int(n_exposed * wi / wsum) for wi in w]
    quotas[-1] += n_exposed - sum(quotas)

    # 付费侧的额外劣化：degrade_at 之后付费流量购物车点击率打折
    degrade = c.degrade_at is not None and ds >= c.degrade_at
    degrade_cart = c.degrade_cart if degrade else 1.0

    avail = max(1, pool.n_available(day_idx))

    funnel_rows: list[tuple] = []
    session_rows: list[tuple] = []
    # 付费人次在各场次间的分配（按配额比例，带轻微差异）
    paid_left = n_paid
    for k in range(n_sessions):
        q = quotas[k]
        if q <= 0:
            continue
        sid = session_seq[0]
        session_seq[0] += 1
        hid = host_names[(c.cid, idx[k])]
        hm = HOST_MULTS[idx[k]]

        # 该场次的付费配额（最后一场兜底）
        if k == n_sessions - 1:
            this_paid = paid_left
        else:
            this_paid = int(n_paid * q / max(1, n_exposed))
            paid_left -= this_paid
        session_spend = int(spend * q / max(1, n_exposed))
        session_rows.append(
            (sid, c.cid, ds, hid, k, 120 + int(90 * rng.random()), session_spend)
        )

        # 场次级转化基准（含主播乘数与日噪声）
        p_enter = min(0.95, c.p_enter * hm * (0.94 + 0.12 * rng.random()))
        p_stay = min(0.98, c.p_stay * (0.97 + 0.06 * rng.random()))
        p_cart = min(0.9, c.p_cart * (0.94 + 0.12 * rng.random()))
        p_order = min(0.95, c.p_order * (0.95 + 0.10 * rng.random()))
        p_pay = min(0.99, c.p_pay * (0.97 + 0.06 * rng.random()))

        # 该场次付费人次计数
        paid_quota = [1] * this_paid + [0] * (q - this_paid)
        if this_paid > q:
            paid_quota = [1] * q
        rng.shuffle(paid_quota)
        # 商品角色的轮盘
        cat_keys = sorted(PRODUCT_CATS)
        cat_w = [CAT_ORDER_WEIGHT[k_] for k_ in cat_keys]

        for pos in range(q):
            aid = rng.randrange(avail) + 1
            loy = pool.loyalty[aid - 1]
            is_paid_flow = paid_quota[pos]
            acq = 2 if is_paid_flow else 1
            pn = c.pay_penalty if is_paid_flow else 1.0
            # 自然转化的逐步概率（every step conditioned on previous）
            step_entered = 1 if rng.random() < p_enter * pn * (0.75 + 0.35 * loy) else 0
            if not step_entered:
                stay_sec = 0
                interact = 1 if rng.random() < 0.012 else 0
                funnel_rows.append(
                    (ds, c.cid, sid, aid, acq, 1, 0, 0, 0, 0, 0, stay_sec, interact, 0, 0, None)
                )
                continue
            stay_sec = int(max(1, rng.expovariate(1 / 95.0)))
            step_stayed = 1 if stay_sec > 30 else 0
            interact = 1 if rng.random() < (0.30 if step_stayed else 0.06) else 0
            pc = p_cart * pn * degrade_cart if is_paid_flow else p_cart
            pc = pc * (0.8 + 0.4 * loy if step_stayed else 0.0)   # 未过停留层 ⇒ 必不过加购层（保证漏斗严格嵌套）
            step_cart = 1 if rng.random() < min(0.92, pc) else 0
            step_ordered = 0
            order_cents = 0
            paid_cents = 0
            prod_cat = None
            if step_cart and rng.random() < p_order * (0.7 + 0.5 * loy):
                step_ordered = 1
                cat = rng.choices(cat_keys, weights=cat_w, k=1)[0]
                prod_cat = cat
                unit = int(max(900, rng.gauss(c.aov_cents, c.aov_cents * c.cv) * CAT_PRICE_MULT[cat]))
                order_cents = unit
                step_paid = 1 if rng.random() < p_pay else 0
                if step_paid:
                    paid_cents = unit
                funnel_rows.append(
                    (ds, c.cid, sid, aid, acq, 1, 1, step_stayed, step_cart, step_ordered,
                     step_paid, stay_sec, interact, order_cents, paid_cents, prod_cat)
                )
                continue
            funnel_rows.append(
                (ds, c.cid, sid, aid, acq, 1, 1, step_stayed, step_cart, 0, 0,
                 stay_sec, interact, 0, 0, None)
            )

    return funnel_rows, session_rows, {}


def main() -> int:
    ap = argparse.ArgumentParser(description="生成多平台直播电商经营分析样本数据集 → SQLite")
    ap.add_argument("--root", help="workspace 根（默认向上查找 AGENTS.md）")
    ap.add_argument("--db", help=f"sqlite 路径（默认 <root>/{DEFAULT_DB}）")
    ap.add_argument("--start", default=DEFAULT_START, help=f"起始日期（默认 {DEFAULT_START}）")
    ap.add_argument("--end", help="结束日期（默认今天）")
    ap.add_argument("--limit-days", type=int, help="只生成前 N 天（冒烟测试用）")
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED, help="随机种子（保证可复现）")
    args = ap.parse_args()

    root = Path(args.root).resolve() if args.root else find_workspace_root()
    db_path = Path(args.db) if args.db else (root / DEFAULT_DB)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    start = parse_date(args.start)
    end = parse_date(args.end) if args.end else date.today()
    if end < start:
        ap.error(f"--end ({end}) 早于 --start ({start})")

    all_days = (end - start).days + 1
    days = min(all_days, args.limit_days) if args.limit_days else all_days
    dates = [start + timedelta(days=i) for i in range(days)]

    print(f"[INFO] workspace root : {root}")
    print(f"[INFO] db             : {db_path}")
    print(f"[INFO] 日期范围       : {dates[0]} ~ {dates[-1]}（{days} 天 / 全期 {all_days} 天）")
    print(f"[INFO] seed           : {args.seed}")

    if db_path.exists():
        db_path.unlink()
        print(f"[INFO] 已删除旧库，重建（保证幂等）")

    con = sqlite3.connect(db_path)
    con.execute("PRAGMA journal_mode=OFF")
    con.execute("PRAGMA synchronous=OFF")
    con.execute("PRAGMA temp_store=MEMORY")
    con.execute("PRAGMA cache_size=-262144")

    print("[1/4] 建表 + 维表 ...")
    _, meta = build_dims(con, CHANNELS, start, dates)
    pool: AccountPool = meta["pool"]
    host_names = meta["host_names"]
    print(f"      账户池 {pool.size:,} · 主播 {len(HOST_STEMS) * len(CHANNELS)} · 商品 {len(meta['product_rows'])}")

    ins_funnel = (
        "INSERT INTO fact_account_funnel VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    )
    ins_session = "INSERT INTO fact_session VALUES (?,?,?,?,?,?,?)"
    ins_ad = "INSERT INTO fact_ad_daily VALUES (?,?,?,?,?)"

    print("[2/4] 生成事实表 ...")
    session_seq = [1]
    total_rows = 0
    ad_rows: list[tuple] = []
    for day_idx, d in enumerate(dates):
        ds = d.isoformat()
        t = day_idx / max(1, days - 1)
        day_funnel: list[tuple] = []
        day_session: list[tuple] = []
        for c in CHANNELS:
            rng = random.Random(args.seed ^ (c.cid * 1000003) ^ d.toordinal())
            fr, sr, _ = gen_channel_day(
                rng, c, d, day_idx, days, pool, host_names, t, ds, session_seq
            )
            day_funnel.extend(fr)
            day_session.extend(sr)
            n_org = sum(1 for r in fr if r[4] == 1)
            n_paid = len(fr) - n_org
            # 投放消耗：按付费曝光 × CPM（与渠道参数同源，日维度重新算以保证与 rows 一致）
            cpm = c.cpm_cents * (c.cpm_growth ** t)
            spend = int(n_paid / 1000.0 * cpm)
            ad_rows.append((ds, c.cid, n_paid, n_org, spend))
        con.executemany(ins_session, day_session)
        con.executemany(ins_funnel, day_funnel)
        if len(ad_rows) >= 32 * len(CHANNELS):
            con.executemany(ins_ad, ad_rows)
            ad_rows = []
        total_rows += len(day_funnel)
        if (day_idx + 1) % 50 == 0 or day_idx == days - 1:
            print(f"      {ds} 累计 {total_rows:,} 行", flush=True)
    if ad_rows:
        con.executemany(ins_ad, ad_rows)
    con.commit()
    print(f"      共 {total_rows:,} 行漏斗明细")

    print("[3/4] 建索引 ...")
    con.executescript(
        """
        CREATE INDEX ix_funnel_date    ON fact_account_funnel(stat_date);
        CREATE INDEX ix_funnel_ch_date ON fact_account_funnel(channel_id, stat_date);
        CREATE INDEX ix_funnel_acct    ON fact_account_funnel(account_id);
        CREATE INDEX ix_funnel_sess    ON fact_account_funnel(session_id);
        CREATE INDEX ix_session_date   ON fact_session(channel_id, stat_date);
        """
    )
    con.commit()

    print("[4/4] ANALYZE + 校验 ...")
    con.execute("ANALYZE")
    con.commit()

    n = con.execute("SELECT COUNT(*) FROM fact_account_funnel").fetchone()[0]
    mono = con.execute(
        """
        SELECT COUNT(*) FROM fact_account_funnel
        WHERE step_entered > step_exposed
           OR step_stayed  > step_entered
           OR step_cart    > step_stayed
           OR step_ordered > step_cart
           OR step_paid    > step_ordered
        """
    ).fetchone()[0]
    sz = db_path.stat().st_size / (1024 * 1024)
    print(f"      行数 {n:,} · 单调性违规 {mono}（须为 0）· 文件大小 {sz:.1f} MB")

    con.close()
    if mono:
        print("[ERROR] 漏斗层级单调性被破坏，请检查生成器")
        return 1
    print(f"[OK] 数据集已生成：{db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
