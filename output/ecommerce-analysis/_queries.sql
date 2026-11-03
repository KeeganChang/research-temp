-- [Q01] M1 口径基线 / 数据覆盖与规模核对
SELECT MIN(stat_date)                          AS first_day,
       MAX(stat_date)                          AS last_day,
       COUNT(DISTINCT stat_date)               AS days,
       COUNT(*)                                AS impr_rows,
       COUNT(DISTINCT account_id)              AS accounts,
       COUNT(DISTINCT session_id)              AS sessions,
       COUNT(DISTINCT channel_id)              AS channels,
       SUM(paid_cents) / 100.0                 AS total_gmv
FROM fact_account_funnel
WHERE stat_date BETWEEN :start AND :end
  AND (:cid = 0 OR channel_id = :cid);

-- [Q02] M1 口径基线 / 月度 KPI 趋势（账户口径转化率 + 曝光口径 GPM）
SELECT SUBSTR(f.stat_date, 1, 7)                                             AS ym,
       COUNT(*)                                                              AS impr,
       COUNT(DISTINCT f.account_id)                                          AS uv,
       COUNT(DISTINCT CASE WHEN f.step_entered = 1 THEN f.account_id END)     AS enter_uv,
       SUM(f.step_paid)                                                      AS pay_rows,
       ROUND(SUM(f.paid_cents) / 100.0, 0)                                   AS gmv,
       ROUND(1.0 * COUNT(DISTINCT CASE WHEN f.step_paid = 1 THEN f.account_id END)
             / NULLIF(COUNT(DISTINCT f.account_id), 0) * 100, 3)             AS pay_cvr_pct,
       ROUND(1.0 * SUM(f.paid_cents) / NULLIF(SUM(f.step_paid) * 100.0, 0), 0) AS aov,
       ROUND(1.0 * SUM(f.paid_cents) / 100.0
             / NULLIF(COUNT(DISTINCT CASE WHEN f.step_entered = 1 THEN f.account_id END), 0)
             * 1000, 0)                                                      AS gpm_per1k_enter,
       ROUND(1.0 * SUM(CASE WHEN f.acq_source = 1 THEN 1 ELSE 0 END)
             / COUNT(*) * 100, 2)                                            AS organic_impr_pct,
       ROUND(1.0 * SUM(CASE WHEN f.interacted = 1 THEN 1 ELSE 0 END)
             / NULLIF(SUM(f.step_entered), 0) * 100, 2)                      AS interact_pct
FROM fact_account_funnel f
WHERE f.stat_date BETWEEN :start AND :end
  AND (:cid = 0 OR f.channel_id = :cid)
GROUP BY SUBSTR(f.stat_date, 1, 7)
ORDER BY ym;

-- [Q03] M2 渠道对比 / 渠道经营总览（窗口期）
WITH w AS (
    SELECT * FROM fact_account_funnel
    WHERE stat_date BETWEEN :start AND :end AND (:cid = 0 OR channel_id = :cid)
),
ad AS (
    SELECT channel_id, SUM(spend_cents) AS spend
    FROM fact_ad_daily
    WHERE stat_date BETWEEN :start AND :end
    GROUP BY channel_id
)
SELECT c.channel_name                                                        AS channel,
       COUNT(*)                                                              AS impr,
       COUNT(DISTINCT w.account_id)                                          AS uv,
       ROUND(SUM(w.paid_cents) / 100.0, 0)                                   AS gmv,
       ROUND(1.0 * SUM(w.paid_cents) / (SELECT SUM(paid_cents) FROM w) * 100, 1) AS gmv_share_pct,
       SUM(w.step_paid)                                                      AS orders,
       ROUND(1.0 * SUM(w.paid_cents) / NULLIF(SUM(w.step_paid) * 100.0, 0), 0)   AS aov,
       ROUND(1.0 * COUNT(DISTINCT CASE WHEN w.step_paid = 1 THEN w.account_id END)
             / NULLIF(COUNT(DISTINCT w.account_id), 0) * 100, 3)             AS pay_cvr_pct,
       ROUND(1.0 * SUM(w.paid_cents) / 100.0
             / NULLIF(COUNT(DISTINCT CASE WHEN w.step_entered = 1 THEN w.account_id END), 0)
             * 1000, 0)                                                      AS gpm_per1k_enter,
       ROUND(1.0 * SUM(CASE WHEN w.acq_source = 1 THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS organic_pct,
       ROUND(1.0 * SUM(CASE WHEN w.acq_source = 2 THEN w.paid_cents ELSE 0 END)
             / NULLIF(ad.spend, 0), 2)                                       AS paid_roi,
       ROUND(ad.spend / 100.0, 0)                                            AS ad_spend
FROM w
JOIN dim_channel c ON c.channel_id = w.channel_id
LEFT JOIN ad ON ad.channel_id = w.channel_id
GROUP BY c.channel_name
ORDER BY gmv DESC;

-- [Q04] M2 渠道对比 / 渠道 × 季度：GMV 与自然流量占比漂移
SELECT c.channel_name                                                    AS channel,
       (SUBSTR(f.stat_date, 1, 4) || 'Q' ||
        ((CAST(SUBSTR(f.stat_date, 6, 2) AS INTEGER) - 1) / 3 + 1))       AS quarter,
       ROUND(SUM(f.paid_cents) / 100.0, 0)                               AS gmv,
       COUNT(*)                                                          AS impr,
       ROUND(1.0 * SUM(CASE WHEN f.acq_source = 1 THEN 1 ELSE 0 END)
             / COUNT(*) * 100, 2)                                        AS organic_pct,
       SUM(CASE WHEN f.acq_source = 1 THEN 1 ELSE 0 END)                 AS organic_impr,
       SUM(CASE WHEN f.acq_source = 2 THEN 1 ELSE 0 END)                 AS paid_impr
FROM fact_account_funnel f
JOIN dim_channel c ON c.channel_id = f.channel_id
WHERE f.stat_date BETWEEN :start AND :end AND (:cid = 0 OR f.channel_id = :cid)
GROUP BY c.channel_name, quarter
ORDER BY c.channel_id, quarter;

-- [Q05] M3 流量结构 / 自然 vs 付费：分层表现与投放效率
WITH w AS (
    SELECT * FROM fact_account_funnel
    WHERE stat_date BETWEEN :start AND :end AND (:cid = 0 OR channel_id = :cid)
),
ad AS (
    SELECT channel_id, SUM(spend_cents) AS spend, SUM(paid_impr) AS paid_impr
    FROM fact_ad_daily
    WHERE stat_date BETWEEN :start AND :end
    GROUP BY channel_id
)
SELECT c.channel_name                                                    AS channel,
       CASE w.acq_source WHEN 1 THEN '自然' ELSE '付费' END                AS source,
       COUNT(*)                                                          AS impr,
       ROUND(1.0 * SUM(w.step_entered) / COUNT(*) * 100, 2)              AS enter_pct,
       ROUND(1.0 * SUM(w.step_cart) / NULLIF(SUM(w.step_entered), 0) * 100, 2)   AS cart_pct,
       ROUND(1.0 * SUM(w.step_paid) / NULLIF(SUM(w.step_cart), 0) * 100, 2)      AS pay_of_cart_pct,
       ROUND(1.0 * SUM(w.step_paid) / COUNT(*) * 100, 3)                 AS pay_per_impr_pct,
       ROUND(SUM(w.paid_cents) / 100.0, 0)                               AS gmv,
       ROUND(1.0 * SUM(w.paid_cents) / NULLIF(SUM(w.step_paid) * 100.0, 0), 0)   AS aov,
       -- ROI / CPM 只在付费行有意义；自然行强制置 NULL，避免显示成 0 被误读
       CASE WHEN w.acq_source = 2 THEN
            ROUND(1.0 * SUM(w.paid_cents) / NULLIF(ad.spend, 0), 2) END      AS roi,
       CASE WHEN w.acq_source = 2 THEN
            ROUND(1.0 * ad.spend / NULLIF(ad.paid_impr, 0) * 1000, 0) END    AS cost_per1k_impr
FROM w
JOIN dim_channel c ON c.channel_id = w.channel_id
LEFT JOIN ad ON ad.channel_id = w.channel_id
GROUP BY c.channel_name, w.acq_source
ORDER BY c.channel_id, w.acq_source;

-- [Q06] M3 流量结构 / 自然流量占比月度漂移（驱动指标）
SELECT SUBSTR(f.stat_date, 1, 7)                                          AS ym,
       COUNT(*)                                                           AS impr,
       SUM(CASE WHEN f.acq_source = 1 THEN 1 ELSE 0 END)                  AS organic_impr,
       SUM(CASE WHEN f.acq_source = 2 THEN 1 ELSE 0 END)                  AS paid_impr,
       ROUND(1.0 * SUM(CASE WHEN f.acq_source = 1 THEN 1 ELSE 0 END)
             / COUNT(*) * 100, 2)                                         AS organic_pct,
       ROUND(SUM(CASE WHEN f.acq_source = 1 THEN f.paid_cents ELSE 0 END) / 100.0, 0) AS organic_gmv,
       ROUND(SUM(CASE WHEN f.acq_source = 2 THEN f.paid_cents ELSE 0 END) / 100.0, 0) AS paid_gmv
FROM fact_account_funnel f
WHERE f.stat_date BETWEEN :start AND :end AND (:cid = 0 OR f.channel_id = :cid)
GROUP BY ym
ORDER BY ym;

-- [Q07] M3 流量结构 / 付费侧效率季度趋势（CPM / ROI / 付费转化）
WITH q AS (
    SELECT f.stat_date, f.channel_id,
           (SUBSTR(f.stat_date, 1, 4) || 'Q' ||
            ((CAST(SUBSTR(f.stat_date, 6, 2) AS INTEGER) - 1) / 3 + 1)) AS quarter,
           f.acq_source, f.step_paid, f.paid_cents
    FROM fact_account_funnel f
    WHERE f.stat_date BETWEEN :start AND :end AND (:cid = 0 OR f.channel_id = :cid)
),
ad AS (
    SELECT channel_id,
           (SUBSTR(stat_date, 1, 4) || 'Q' ||
            ((CAST(SUBSTR(stat_date, 6, 2) AS INTEGER) - 1) / 3 + 1)) AS quarter,
           SUM(spend_cents) AS spend, SUM(paid_impr) AS paid_impr
    FROM fact_ad_daily
    WHERE stat_date BETWEEN :start AND :end
    GROUP BY channel_id, quarter
)
SELECT c.channel_name                                                   AS channel,
       q.quarter                                                        AS quarter,
       ROUND(1.0 * SUM(CASE WHEN q.acq_source = 2 THEN q.paid_cents ELSE 0 END)
             / NULLIF(ad.spend, 0), 2)                                  AS paid_roi,
       ROUND(1.0 * ad.spend / NULLIF(ad.paid_impr, 0) * 1000, 0)        AS cpm_per1k,
       ROUND(1.0 * SUM(CASE WHEN q.acq_source = 2 THEN q.step_paid ELSE 0 END)
             / NULLIF(SUM(CASE WHEN q.acq_source = 2 THEN 1 ELSE 0 END), 0) * 100, 3) AS paid_pay_per_impr_pct,
       ROUND(1.0 * SUM(CASE WHEN q.acq_source = 1 THEN q.step_paid ELSE 0 END)
             / NULLIF(SUM(CASE WHEN q.acq_source = 1 THEN 1 ELSE 0 END), 0) * 100, 3) AS organic_pay_per_impr_pct,
       ROUND(ad.spend / 100.0, 0)                                       AS spend
FROM q
JOIN dim_channel c ON c.channel_id = q.channel_id
LEFT JOIN ad ON ad.channel_id = q.channel_id AND ad.quarter = q.quarter
GROUP BY c.channel_name, q.quarter
ORDER BY c.channel_id, q.quarter;

-- [Q08] M4 转化漏斗 / 六层漏斗 · 账户口径 cohort-locked（分子必为分母子集）
WITH w AS (
    SELECT * FROM fact_account_funnel
    WHERE stat_date BETWEEN :start AND :end AND (:cid = 0 OR channel_id = :cid)
),
lv AS (
    SELECT CASE WHEN :cid = 0 THEN '全渠道' ELSE (SELECT channel_name FROM dim_channel WHERE channel_id = :cid) END AS channel,
           COUNT(DISTINCT account_id)                                              AS n_exposed,
           COUNT(DISTINCT CASE WHEN step_entered = 1 THEN account_id END)          AS n_entered,
           COUNT(DISTINCT CASE WHEN step_stayed  = 1 THEN account_id END)          AS n_stayed,
           COUNT(DISTINCT CASE WHEN step_cart    = 1 THEN account_id END)          AS n_cart,
           COUNT(DISTINCT CASE WHEN step_ordered = 1 THEN account_id END)          AS n_ordered,
           COUNT(DISTINCT CASE WHEN step_paid    = 1 THEN account_id END)          AS n_paid
    FROM w
)
SELECT channel,
       n_exposed,
       n_entered, ROUND(1.0 * n_entered / NULLIF(n_exposed, 0) * 100, 2)  AS r_enter_pct,
       n_stayed,  ROUND(1.0 * n_stayed  / NULLIF(n_entered, 0) * 100, 2)   AS r_stay_pct,
       n_cart,    ROUND(1.0 * n_cart    / NULLIF(n_stayed, 0) * 100, 2)    AS r_cart_pct,
       n_ordered, ROUND(1.0 * n_ordered / NULLIF(n_cart, 0) * 100, 2)      AS r_order_pct,
       n_paid,    ROUND(1.0 * n_paid    / NULLIF(n_ordered, 0) * 100, 2)   AS r_pay_pct,
       ROUND(1.0 * n_paid / NULLIF(n_exposed, 0) * 100, 4)                 AS e2e_pct
FROM lv;

-- [Q09] M4 转化漏斗 / 口径对照：账户去重口径 vs 曝光累加口径（量化重复计数偏差）
WITH w AS (
    SELECT * FROM fact_account_funnel
    WHERE stat_date BETWEEN :start AND :end AND (:cid = 0 OR channel_id = :cid)
),
acct AS (
    SELECT channel_id,
           COUNT(DISTINCT account_id)                                     AS a_exposed,
           COUNT(DISTINCT CASE WHEN step_entered = 1 THEN account_id END) AS a_entered,
           COUNT(DISTINCT CASE WHEN step_cart    = 1 THEN account_id END) AS a_cart,
           COUNT(DISTINCT CASE WHEN step_paid    = 1 THEN account_id END) AS a_paid
    FROM w GROUP BY channel_id
),
impr AS (
    SELECT channel_id,
           COUNT(*)              AS i_exposed,
           SUM(step_entered)     AS i_entered,
           SUM(step_cart)        AS i_cart,
           SUM(step_paid)        AS i_paid
    FROM w GROUP BY channel_id
)
SELECT c.channel_name                                                       AS channel,
       ROUND(1.0 * a.a_entered / a.a_exposed * 100, 2)                      AS acct_enter_pct,
       ROUND(1.0 * i.i_entered / i.i_exposed * 100, 2)                      AS impr_enter_pct,
       ROUND((1.0 * i.i_entered / i.i_exposed) - (1.0 * a.a_entered / a.a_exposed), 4) * 100 AS enter_gap_pp,
       ROUND(1.0 * a.a_paid / a.a_exposed * 100, 4)                         AS acct_pay_pct,
       ROUND(1.0 * i.i_paid / i.i_exposed * 100, 4)                         AS impr_pay_pct,
       ROUND((1.0 * i.i_paid / i.i_exposed) - (1.0 * a.a_paid / a.a_exposed), 5) * 100 AS pay_gap_pp,
       a.a_exposed                                                          AS acct_uv,
       i.i_exposed                                                          AS impr_rows,
       ROUND(1.0 * i.i_exposed / a.a_exposed, 2)                            AS impr_per_acct
FROM acct a
JOIN impr i ON i.channel_id = a.channel_id
JOIN dim_channel c ON c.channel_id = a.channel_id
ORDER BY c.channel_id;

-- [Q10] M4 转化漏斗 / 漏斗关键层转化率季度趋势（找漏点漂移）
WITH t AS (
    SELECT (SUBSTR(stat_date, 1, 4) || 'Q' ||
            ((CAST(SUBSTR(stat_date, 6, 2) AS INTEGER) - 1) / 3 + 1)) AS quarter,
           channel_id, step_entered, step_stayed, step_cart, step_ordered, step_paid
    FROM fact_account_funnel
    WHERE stat_date BETWEEN :start AND :end AND (:cid = 0 OR channel_id = :cid)
)
SELECT c.channel_name                                                       AS channel,
       t.quarter                                                            AS quarter,
       ROUND(1.0 * SUM(t.step_entered) / COUNT(*) * 100, 2)                 AS enter_pct,
       ROUND(1.0 * SUM(t.step_stayed)  / NULLIF(SUM(t.step_entered), 0) * 100, 2) AS stay_pct,
       ROUND(1.0 * SUM(t.step_cart)    / NULLIF(SUM(t.step_stayed), 0) * 100, 2)  AS cart_pct,
       ROUND(1.0 * SUM(t.step_ordered) / NULLIF(SUM(t.step_cart), 0) * 100, 2)    AS order_pct,
       ROUND(1.0 * SUM(t.step_paid)    / NULLIF(SUM(t.step_ordered), 0) * 100, 2) AS pay_pct
FROM t
JOIN dim_channel c ON c.channel_id = t.channel_id
GROUP BY c.channel_name, t.quarter
ORDER BY c.channel_id, t.quarter;

-- [Q11] M5 货品与主播 / 货品角色结构（GMV 占比 / 客单 / 漏斗贡献）
SELECT c.channel_name                                                    AS channel,
       CASE f.product_cat WHEN 1 THEN '引流款' WHEN 2 THEN '爆款'
                          WHEN 3 THEN '利润款' WHEN 4 THEN '秒杀款' END   AS cat,
       SUM(f.step_paid)                                                  AS orders,
       ROUND(SUM(f.paid_cents) / 100.0, 0)                               AS gmv,
       ROUND(1.0 * SUM(f.paid_cents) / 100.0
             / (SELECT SUM(paid_cents) / 100.0 FROM fact_account_funnel
                WHERE stat_date BETWEEN :start AND :end AND (:cid = 0 OR channel_id = :cid))
             * 100, 1)                                                   AS gmv_share_pct,
       ROUND(1.0 * SUM(f.paid_cents) / NULLIF(SUM(f.step_paid) * 100.0, 0), 0) AS aov,
       ROUND(1.0 * SUM(f.order_cents - f.paid_cents)
             / NULLIF(SUM(f.order_cents), 0) * 100, 2)                   AS unpaid_loss_pct
FROM fact_account_funnel f
JOIN dim_channel c ON c.channel_id = f.channel_id
WHERE f.stat_date BETWEEN :start AND :end
  AND f.step_ordered = 1
  AND (:cid = 0 OR f.channel_id = :cid)
GROUP BY c.channel_name, f.product_cat
ORDER BY c.channel_id, gmv DESC;

-- [Q12] M5 货品与主播 / 主播 GMV 集中度（单点依赖识别）
WITH f AS (
    SELECT * FROM fact_account_funnel
    WHERE stat_date BETWEEN :start AND :end AND (:cid = 0 OR channel_id = :cid)
),
by_host AS (
    SELECT f.channel_id, s.host_id,
           COUNT(*) AS impr, SUM(f.step_paid) AS orders, SUM(f.paid_cents) AS gmv_cents
    FROM f JOIN fact_session s ON s.session_id = f.session_id
    GROUP BY f.channel_id, s.host_id
),
ranked AS (
    SELECT bh.*, RANK() OVER (PARTITION BY bh.channel_id ORDER BY bh.gmv_cents DESC) AS rk
    FROM by_host bh
)
SELECT c.channel_name                                                    AS channel,
       COUNT(DISTINCT rh.host_id)                                        AS hosts,
       ROUND(1.0 * MAX(CASE WHEN rh.rk = 1 THEN rh.gmv_cents END)
             / SUM(rh.gmv_cents) * 100, 1)                               AS top1_share_pct,
       ROUND(1.0 * SUM(CASE WHEN rh.rk <= 2 THEN rh.gmv_cents ELSE 0 END)
             / SUM(rh.gmv_cents) * 100, 1)                               AS top2_share_pct,
       ROUND(1.0 * SUM(CASE WHEN rh.rk = 1 THEN rh.impr END)
             / SUM(rh.impr) * 100, 1)                                    AS top1_exposure_pct,
       ROUND(1.0 * MAX(CASE WHEN rh.rk = 1 THEN rh.gmv_cents END) / 100.0
             / NULLIF(MAX(CASE WHEN rh.rk = 1 THEN rh.orders END), 0), 0) AS top1_aov,
       ROUND(1.0 * SUM(rh.gmv_cents) / 100.0
             / NULLIF(SUM(rh.impr), 0) * 1000, 0)                        AS gpm_per1k_impr
FROM ranked rh
JOIN dim_channel c ON c.channel_id = rh.channel_id
GROUP BY c.channel_name
ORDER BY top1_share_pct DESC;

-- [Q13] R1 根因归因 / GMV 变动四因素分解（规模 / 结构 / 效率 / 客单）
-- 曝光口径（行级可加）。分解连等式：
--   ΔGMV = E_size + E_mix + E_eff + E_aov (+ residual≈0)
--   其中 E_mix = UV1 × Δ自然占比 × (自然转化 − 付费转化) × AOV0
--   即「把曝光从高转化的自然搬向低转化的付费」造成的 GMV 损失，这是本分析的归因核心。
WITH per AS (
    SELECT 'P0' AS period, channel_id,
           COUNT(*)                                                          AS uv,
           1.0 * SUM(CASE WHEN acq_source = 1 THEN 1 ELSE 0 END) / COUNT(*)  AS s_org,
           1.0 * SUM(CASE WHEN acq_source = 1 THEN step_paid ELSE 0 END)
               / NULLIF(SUM(CASE WHEN acq_source = 1 THEN 1 ELSE 0 END), 0)  AS c_org,
           1.0 * SUM(CASE WHEN acq_source = 2 THEN step_paid ELSE 0 END)
               / NULLIF(SUM(CASE WHEN acq_source = 2 THEN 1 ELSE 0 END), 0)  AS c_paid,
           1.0 * SUM(paid_cents) / 100.0                                     AS gmv,
           1.0 * SUM(paid_cents) / 100.0 / NULLIF(SUM(step_paid), 0)         AS aov
    FROM fact_account_funnel
    WHERE stat_date BETWEEN :p0s AND :p0e AND (:cid = 0 OR channel_id = :cid)
    GROUP BY channel_id
    UNION ALL
    SELECT 'P1', channel_id,
           COUNT(*),
           1.0 * SUM(CASE WHEN acq_source = 1 THEN 1 ELSE 0 END) / COUNT(*),
           1.0 * SUM(CASE WHEN acq_source = 1 THEN step_paid ELSE 0 END)
               / NULLIF(SUM(CASE WHEN acq_source = 1 THEN 1 ELSE 0 END), 0),
           1.0 * SUM(CASE WHEN acq_source = 2 THEN step_paid ELSE 0 END)
               / NULLIF(SUM(CASE WHEN acq_source = 2 THEN 1 ELSE 0 END), 0),
           1.0 * SUM(paid_cents) / 100.0,
           1.0 * SUM(paid_cents) / 100.0 / NULLIF(SUM(step_paid), 0)
    FROM fact_account_funnel
    WHERE stat_date BETWEEN :p1s AND :p1e AND (:cid = 0 OR channel_id = :cid)
    GROUP BY channel_id
),
k AS (
    SELECT a.channel_id,
           a.uv AS uv0, b.uv AS uv1,
           a.s_org AS s0, b.s_org AS s1,
           a.c_org AS c0o, b.c_org AS c1o,
           a.c_paid AS c0p, b.c_paid AS c1p,
           a.aov AS a0, b.aov AS a1,
           a.gmv AS g0, b.gmv AS g1
    FROM per a JOIN per b ON a.channel_id = b.channel_id
    WHERE a.period = 'P0' AND b.period = 'P1'
),
d AS (
    SELECT *,
           ((s0 * c0o) + ((1 - s0) * c0p))          AS k0,
           ((s1 * c1o) + ((1 - s1) * c1p))          AS k1
    FROM k
),
e AS (
    SELECT *,
           (uv1 - uv0) * k0 * a0                                     AS e_size,
           uv1 * ((s1 - s0) * (c0o - c0p)) * a0                      AS e_mix,
           uv1 * (s1 * (c1o - c0o) + (1 - s1) * (c1p - c0p)) * a0    AS e_eff,
           uv1 * k1 * (a1 - a0)                                      AS e_aov
    FROM d
)
SELECT c.channel_name                                      AS channel,
       ROUND(g0, 0)                                        AS gmv_baseline,
       ROUND(g1, 0)                                        AS gmv_current,
       ROUND(g1 - g0, 0)                                   AS delta_gmv,
       ROUND(e_size, 0)                                    AS e_size,
       ROUND(e_mix, 0)                                     AS e_mix_flowmix,
       ROUND(e_eff, 0)                                     AS e_eff_cvr,
       ROUND(e_aov, 0)                                     AS e_aov,
       ROUND((g1 - g0) - (e_size + e_mix + e_eff + e_aov), 0) AS residual,
       ROUND((s1 - s0) * 100, 2)                           AS organic_share_pp,
       ROUND(c1o / c0o, 3)                                 AS organic_cvr_ratio,
       ROUND(c1p / c0p, 3)                                 AS paid_cvr_ratio
FROM e JOIN dim_channel c ON c.channel_id = e.channel_id
ORDER BY delta_gmv DESC;

-- [Q14] R1 根因归因 / 自然流量绝对量 vs 占比：是「自然萎缩」还是「付费扩张」
WITH per AS (
    SELECT 'P0' AS period, channel_id,
           COUNT(*) AS impr,
           SUM(CASE WHEN acq_source = 1 THEN 1 ELSE 0 END) AS org_impr,
           SUM(CASE WHEN acq_source = 2 THEN 1 ELSE 0 END) AS paid_impr,
           SUM(CASE WHEN acq_source = 1 THEN paid_cents ELSE 0 END) AS org_gmv,
           SUM(CASE WHEN acq_source = 2 THEN paid_cents ELSE 0 END) AS paid_gmv
    FROM fact_account_funnel
    WHERE stat_date BETWEEN :p0s AND :p0e AND (:cid = 0 OR channel_id = :cid)
    GROUP BY channel_id
    UNION ALL
    SELECT 'P1', channel_id, COUNT(*),
           SUM(CASE WHEN acq_source = 1 THEN 1 ELSE 0 END),
           SUM(CASE WHEN acq_source = 2 THEN 1 ELSE 0 END),
           SUM(CASE WHEN acq_source = 1 THEN paid_cents ELSE 0 END),
           SUM(CASE WHEN acq_source = 2 THEN paid_cents ELSE 0 END)
    FROM fact_account_funnel
    WHERE stat_date BETWEEN :p1s AND :p1e AND (:cid = 0 OR channel_id = :cid)
    GROUP BY channel_id
)
SELECT c.channel_name                                       AS channel,
       ROUND(1.0 * a.org_impr / a.impr * 100, 2)            AS baseline_organic_pct,
       ROUND(1.0 * b.org_impr / b.impr * 100, 2)            AS current_organic_pct,
       ROUND((1.0 * b.org_impr / b.impr - 1.0 * a.org_impr / a.impr) * 100, 2) AS organic_pct_pp,
       a.org_impr                                           AS baseline_organic_impr,
       b.org_impr                                           AS current_organic_impr,
       ROUND(1.0 * b.org_impr / NULLIF(a.org_impr, 0), 3)   AS organic_impr_x,
       ROUND(1.0 * b.paid_impr / NULLIF(a.paid_impr, 0), 3) AS paid_impr_x,
       ROUND(1.0 * b.impr / NULLIF(a.impr, 0), 3)           AS total_impr_x
FROM per a JOIN per b ON a.channel_id = b.channel_id
JOIN dim_channel c ON c.channel_id = a.channel_id
WHERE a.period = 'P0' AND b.period = 'P1'
ORDER BY organic_pct_pp;

-- [Q15] R1 根因归因 / 新增账户 vs 存量账户漏斗差异（窗口内 cohort 切分）
-- 「新增账户」= 首次曝光日期落在分析窗口内的账户（由 dim_account.first_seen 判定）。
-- 这是「不考虑后面的新增账户」的对照实验：若窗口内新账户占比高，
-- 会把漏斗整体拉低 —— 必须先量化它，才能判断「现有账户变差」还是「人群换了」。
WITH w AS (
    SELECT f.*, a.first_seen
    FROM fact_account_funnel f
    JOIN dim_account a ON a.account_id = f.account_id
    WHERE f.stat_date BETWEEN :start AND :end AND (:cid = 0 OR f.channel_id = :cid)
)
SELECT CASE WHEN first_seen >= :start THEN '窗口内新增' ELSE '存量' END      AS cohort,
       COUNT(DISTINCT account_id)                                          AS uv,
       ROUND(1.0 * COUNT(DISTINCT CASE WHEN step_entered = 1 THEN account_id END)
             / COUNT(DISTINCT account_id) * 100, 2)                        AS enter_pct,
       ROUND(1.0 * COUNT(DISTINCT CASE WHEN step_cart = 1 THEN account_id END)
             / NULLIF(COUNT(DISTINCT CASE WHEN step_stayed = 1 THEN account_id END), 0) * 100, 2) AS cart_pct,
       ROUND(1.0 * COUNT(DISTINCT CASE WHEN step_paid = 1 THEN account_id END)
             / COUNT(DISTINCT account_id) * 100, 3)                        AS pay_pct,
       ROUND(1.0 * SUM(paid_cents) / 100.0, 0)                             AS gmv,
       ROUND(1.0 * SUM(paid_cents) / NULLIF(SUM(step_paid) * 100.0, 0), 0) AS aov
FROM w
GROUP BY cohort
ORDER BY uv DESC;

-- [Q16] R2 修复估算 / 反事实推演：自然占比若维持基线水平，当期 GMV 差多少
-- 保持当期「曝光总量 / 付费转化 / 自然转化 / 客单」不变，仅把自然-付费结构
-- 复原到基线期，看 GMV 的差值 —— 即「结构效应」可被修复的上界（修复收益天花板）。
WITH cur AS (
    SELECT f.channel_id,
           COUNT(*) AS uv,
           1.0 * SUM(CASE WHEN f.acq_source = 1 THEN 1 ELSE 0 END) / COUNT(*) AS s1,
           1.0 * SUM(CASE WHEN f.acq_source = 1 THEN f.step_paid ELSE 0 END)
               / NULLIF(SUM(CASE WHEN f.acq_source = 1 THEN 1 ELSE 0 END), 0) AS c_org,
           1.0 * SUM(CASE WHEN f.acq_source = 2 THEN f.step_paid ELSE 0 END)
               / NULLIF(SUM(CASE WHEN f.acq_source = 2 THEN 1 ELSE 0 END), 0) AS c_paid,
           1.0 * SUM(f.paid_cents) / 100.0 / NULLIF(SUM(f.step_paid), 0)      AS aov
    FROM fact_account_funnel f
    WHERE f.stat_date BETWEEN :p1s AND :p1e AND (:cid = 0 OR f.channel_id = :cid)
    GROUP BY f.channel_id
),
base AS (
    SELECT f.channel_id,
           1.0 * SUM(CASE WHEN f.acq_source = 1 THEN 1 ELSE 0 END) / COUNT(*) AS s0
    FROM fact_account_funnel f
    WHERE f.stat_date BETWEEN :p0s AND :p0e AND (:cid = 0 OR f.channel_id = :cid)
    GROUP BY f.channel_id
)
SELECT c.channel_name                                                    AS channel,
       ROUND(cur.s1 * 100, 2)                                            AS current_organic_pct,
       ROUND(base.s0 * 100, 2)                                           AS baseline_organic_pct,
       ROUND((cur.s1 - base.s0) * 100, 2)                                AS gap_pp,
       ROUND(cur.uv * ((cur.s1 * cur.c_org) + ((1 - cur.s1) * cur.c_paid)) * cur.aov, 0) AS gmv_actual,
       ROUND(cur.uv * ((base.s0 * cur.c_org) + ((1 - base.s0) * cur.c_paid)) * cur.aov, 0) AS gmv_if_baseline_mix,
       ROUND(cur.uv * (base.s0 - cur.s1) * (cur.c_org - cur.c_paid) * cur.aov, 0) AS recoverable_gmv
FROM cur
JOIN base ON base.channel_id = cur.channel_id
JOIN dim_channel c ON c.channel_id = cur.channel_id
ORDER BY recoverable_gmv DESC;