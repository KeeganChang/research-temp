# 第 5 章 合规替代路径与市场措施：钱包支付通道边界、合作方式与分阶段进入动作

> 研究参数卡 v3（主编核定 2026-11-09）｜ Phase 3.1 核定稿 ｜ 监管状态 as-of 2026-11-09 ｜ 简体中文

## 5.1 论点

前四章已证「参与沙盒即可合规做零售 CFD」趋近不成立、需求须重定向至 E3 承接方；本章不重论证条文、不重算份额，只做判定与动作。**核心判断 `kind: judgment`：直做零售 CFD 判否；可行路径是「本地持牌主体承接合规替代业务＋比索法币层与产品层严格分离」。** 分离有据：BlockShoals 法务负责人在 2026 菲律宾区块链周明言「Binance 与 BlockShoals 不移动比索，比索明确属 BSP 管辖」，BSP 书面答复进一步明确「参与沙盒不豁免适用法律，**VASP 活动与法币轨道不在 SEC 沙盒覆盖内**」（[Mintchain, 2026](https://mintchain.ph/?p=3441)；判词经参数卡 v3 §3 核定，第 1 章产出、本章复用）；SEC 委员 Quevedo 2026-08 称入盒「不是通往 SEC 获批的快车道」（[Bitdigest, 引 2026-08-26 表态](https://www.bitdigest.io/posts/sec-chairperson-francis-lim-defends-blockshoals-admission-to-strategic-sandbox)）；另有行业媒体转述其「沙盒不治愈此前 SRC 违规的处罚」表述（[Mintchain, 2026](https://mintchain.ph/?p=3441)），两源分列不合成，本稿仅登记同期官方反驳，不作条文效力判断。故本章只问三事：谁持牌、谁承担法币、谁面向菲律宾公众。**本章不提供任何规避监管的操作路径；下述链路仅为合规要件描述，每一环以监管批准为前提。**

## 5.2 论据：三张可操作清单

### 清单 1｜支付通道合规边界清单（判定 as-of 2026-11-09）

| 接口／场景 | 判定 | 依据（发布方，日期） | 边界条件 |
|---|---|---|---|
| 未注册境外平台接入本地银行／电子钱包作支付伙伴 | **禁区·构成招揽证据** | SEC 对 XM 的 CDO：「XM 已接入并使本地银行与电子钱包成为其支付伙伴，清楚显示菲律宾投资者为其主要目标市场」（[Manila Bulletin, 2025-12-12](https://mb.com.ph/2025/12/12/sec-issues-cease-and-desist-order-against-brokerage-firm-xm)；[Manila Times, 2025-12-13](https://www.manilatimes.net/2025/12/13/business/corporate-news/halt-order-issued-versus-pacquiao-endorsed-xm/2242635) 复核） | 接口本身即成立管辖连接点，无需另证广告投放 |
| 菲律宾零售客户直连离岸 VASP | **禁** | BSP M-2026-003 一手转录：「Direct access of retail customers residing in the Philippines… to offshore VASPs… is not allowed」，除非已向 BSP／SEC 注册（[RegAlert 全文转录, 备忘录 2026-01-30](https://regalert.today/document/reminders-on-sound-risk-management-practices-when-dealing-with-virtual-asset-ser-a45bd605-ffda-4b11-9d18-6aa98ca02018)；[Inquirer, 2026](https://business.inquirer.net/571962/beef-up-defenses-vs-crypto-virtual-asset-risks-financial-firms-told)；[Gorriceta Law/Legal 500, 2026](https://gorricetalaw.com/?p=11390/)） | 母国持牌亦不免；BSFI 须 EDD、AML/AMLC 核验与持续监测（D20） |
| 平台自身比索计价交易／移动比索 | **禁** | Quiogue 原话及「沙盒不允许比索交易」（[Mintchain, 2026](https://mintchain.ph/?p=3441)）；BSP Circ 1153 限于 BSP 监管范围内且明文不得用于规避现行法规（[ASG Law, 2022·历史背景](https://asg.ph/insights/bsp-regulatory-sandbox-framework-1153)） | 与「比索入出金」分属不同层级，不得混同（D15／D23） |
| 比索入出金经 BSP 持牌 VASP 轨道 | **可做（唯一口径）** | 「All PHP onboarding and offboarding operations are processed exclusively through… BSP-licensed VASP partner rails」（[BlockShoals FAQ, 访问 2026-11-09](https://blockshoals.com/faq)）；90 天集成限技术对接、非公开商业发布（[Bitdigest, 2026-08-26](https://www.bitdigest.io/posts/sec-chairperson-francis-lim-defends-blockshoals-admission-to-strategic-sandbox)） | 持牌 VASP 为法币主体；本地 CAI／CASP 承担 KYC、CDD 与适当性 |
| 本地 EMI／OPS／商户受理通道 | **有条件可做** | RA 11127 定义 OPS；EMI 受 Circ 1166(2023)、MPAA 受 Circ 1198(2024) 规范（[Gorriceta Law, 2026](https://gorricetalaw.com/?p=11390/)）；「EMI 发牌通道仍然开放」（[Law.asia/Romulo, 2026](https://law.asia/?p=723541)） | 须 BSP 注册／认证且 AMLC 合规；**拟议 12 个月暂停仅针对新 OPS 注册，属未定案草案、仅作观察哨，与 VASP 暂停令分属不同监管对象，不得混为一谈** |
| InstaPay／PESONet 清算接入 | **可做但须持牌** | 2025 两轨合计 ₱24.74 万亿、同比 +42%（2024 ₱17.42 万亿）、约 GDP 90%（[Manila Bulletin, 2026-03-03](https://mb.com.ph/2026/03/03/philippines-nears-seamless-cross-border-payments-with-project-nexus-link)）；Circ 1238（2026-06-17）改成本定价（[Abanto Law, 2026](https://abantolaw.com/fintech-online-payments-regulatory-developments-philippines-2026/)） | 接入方须为 BSP 注册 OPS；不得为未注册平台导流 |
| 持牌博彩场景加密入金／出金 | **禁** | **一手规章**：PAGCOR《Regulatory Framework for the Accreditation of Gaming Affiliates and Support Service Providers, Rev.1》第 26–27 页 g 条：「PC is not allowed the utilization of credit cards and crypto-currency in account funding and/or withdrawal」（[PAGCOR 官方 PDF, 生效 2025-10-02](https://www.pagcor.ph/regulatory/pdf/GSRM/Regulatory%20Manuals/Regulatory-Framework-for-the-Accreditation-of-Gaming-Affiliates-and-Support-Service-Providers-Rev-No-1.pdf)） | 支付通道仍完全属 BSP 管辖，并须经 PAGCOR 认证；反方⑦判据已由业内观点升级为一手条文（D19） |

**可行链路（要件描述，非操作指引）**：本地用户 → BSP 注册 EMI／钱包（AMLC 合规）→ InstaPay／PESONet 清算 → BSP 持牌 VASP 完成法币↔加密转换 → SEC 注册 CASP／CAI 承担 KYC、客户适当性与产品层；境外平台仅提供技术，不得直接持有本地钱包商户关系。**平台自身不做比索计价交易、不移动比索（产品层）；比索入出金由 BSP 持牌 VASP 承担（法币层）**（D15／D23 层级辨析）。

**玩家地图结论（不重列份额与财务）**：可承接主体稀缺且在收缩——BSP VASP 名录 2026-05-31 版为 11 家（7 活跃非银＋2 银行＋2 inactive，[WorldNgayon, 2026](https://worldngayon.com/crypto-tradfi-2026)），2026-07-15 版为 9 家（6 家活跃非银行＋1 家未运营＋2 家银行 VASP；BloomX、XenRemit 被剔除，WIBS 转活跃、DA5 转未运营）（[DOPAY, 2026](https://dopay.ph/?p=3608)；[TheCryptoNewsFeed, 2026](https://thecryptonewsfeed.com/news/bsp-updated-vasp-registry-drops-bloomx-and-xenremit-reclassifies-two-other-firms-17715)）。**两版按 as-of 并列不合成，均为索引转录／二手，BSP 官方 VASP 名录 PDF 全文本轮未取得**（参数卡亦标注该 PDF 取自索引表格，[BSP List of VASP](https://www.bsp.gov.ph/Lists/Directories/Attachments/19/VASP.pdf)），不作当前持牌数定值；**结论级含义为「可承接的持牌主体在收缩」**（D16／D22）。叠加 BSP M-2025-031 自 2025-09-01 **持续生效＋视 global and local developments 重估（律所解读为无限期，两种表述并列不合成）**；条文自带 reassessment 条款即 2027「VASP 暂停令是否重估」观察哨的**一手依据，不再标为推测**（[BitPinas 全文转录, 2025-08-29 签署](https://bitpinas.com/regulation/bsp-vasp-ban/)；[Law.asia 中文版, 2025-08-29](https://law.asia/zh-hans?p=724913)；[Gorriceta Law, 2026](https://gorricetalaw.com/?p=11390/)），**并购／合作既有持牌方为唯一现实入口**。

### 清单 2｜机会区／禁区／观察哨（接入 2027 日历，复用参数卡 v3 §6）

| 分区 | 条目与判定 | 依据（发布方，日期） | 时点／触发 |
|---|---|---|---|
| 机会区 | ① 借道稀缺既有持牌 VASP／EMI 提供合规法币层服务 | [BitPinas M-2025-031 全文转录, 2025-08-29](https://bitpinas.com/regulation/bsp-vasp-ban/)；[Law.asia/Romulo, 2026](https://law.asia/?p=723541) | 以持牌方合作成立为前提 |
| 机会区 | ② E3 需求重定向承接方：小额 P2P 稳定币与代币化通道；**截至 2025-11 累计 4 家**入盒（2025-06-02 已有 **GCash／GStocks Global**（美股，24 个月／200 万人）与 **Pluang PH**（美股，6 个月／1,000 人），2025-11 **BlockShoals 为第 4 家**），构成为 **2 项美股渠道／1 项代币化房地产／1 家加密资产中介**，**零售 CFD 0 家** | [Manila Times, 2025-06-12](https://www.manilatimes.net/2025/06/12/business/top-business/sec-issues-rules-on-crypto-asset-service-providers/2131711)；[Daily Advent 转引 SEC, 2025-11](https://lite.dailyadvent.com/detail/58930492260620en_ng)；入选者测试期参数经参数卡 v3 D4 核定 | 2025-11 状态 |
| 机会区 | ③ 代币化证券／债券 | [BusinessWorld, 2026-07-29](https://bworldonline.com/corporate/2026/07/29/766484/binance-stratbox-pilot-eyed-within-the-year/) | 探索期，须逐案获批 |
| 禁区 | 沙盒内直做零售 CFD；离岸平台直连本地钱包；未注册即营销／招揽（CASP MC 4/5 将社交帖、活动、广告、空投、直播纳入 marketing，披露文件须提前 ≥30 天）；以「仅提供技术／未落地」抗辩支付接口；任何规避监管安排 | [SEC MC No.9 s.2024](https://www.sec.gov.ph/wp-content/uploads/2024/04/2024MC_SEC-MC-No.-9-S.-of-2024-SEC-Stratbox-Strategic-Sandbox-1.pdf)；[Manila Bulletin XM CDO, 2025-12-12](https://mb.com.ph/2025/12/12/sec-issues-cease-and-desist-order-against-brokerage-firm-xm)；[RegAlert M-2026-003, 2026-01-30](https://regalert.today/document/reminders-on-sound-risk-management-practices-when-dealing-with-virtual-asset-ser-a45bd605-ffda-4b11-9d18-6aa98ca02018)；[Manila Times, 2025-06-12](https://www.manilatimes.net/2025/06/12/business/top-business/sec-issues-rules-on-crypto-asset-service-providers/2131711) | 持续 |
| 观察哨 | HB 4792《Philippine Tokenisation and Crypto Adoption Act of 2025》仍待审 | [ethcred/Law.asia, 2026](https://ethcred.com/?p=32485) | pending |
| 观察哨 | VASP 新牌照暂停令的**重估**（M-2025-031 一手条款自带 subject to reassessment，无确定时点，非推测） | [BitPinas, 2025-08-29](https://bitpinas.com/regulation/bsp-vasp-ban/) | 无固定日期 |
| 观察哨 | Project Nexus 2027 年中接入（BIS Innovation Hub，连 InstaPay 与马／泰／新／印尼／印度） | [Manila Bulletin, 2026-03-03](https://mb.com.ph/2026/03/03/philippines-nears-seamless-cross-border-payments-with-project-nexus-link) | 2027 年中 |
| 观察哨 | GCash（GStocks Global）／Pluang PH 24 个月测试期届满 | 参数卡 v3 §6 观察哨日历（第 1 章产出，本章复用；无外部 URL） | 2027-06 前后 |
| 观察哨 | BlockShoals 自 H2 2026 起 ≥24 个月测试，最早公开上线不早于 2028 | [BlockShoals FAQ](https://blockshoals.com/faq)；[Daily Tribune, 2026-07-28](https://tribune.net.ph/2026/07/28/sec-tests-crypto-oversight-with-blockshoals-2)；参数卡 v3 §6 | 不早于 2028 |
| 观察哨 | BSP Circ.1108 修订征求意见 | 参数卡 v3 §6 观察哨日历（第 1 章产出，本章复用；无外部 URL） | 未定 |
| 观察哨 | **SEC 是否发布允许零售 CFD 登记的 special rules（最直接单点证伪条件）** | [SEC MC No.9 s.2024 §14](https://www.sec.gov.ph/wp-content/uploads/2024/04/2024MC_SEC-MC-No.-9-S.-of-2024-SEC-Stratbox-Strategic-Sandbox-1.pdf)；参数卡 v3 §6 | 未定 |
| 观察哨 | 数字银行剩余席位：主口径「**上限 10／已发 7／剩 3 席**」（MariBank 2026-07-18 为第七家，三源印证）；2026 Q1 另有「4 张新牌照／3 份申请」口径，系**时间差**非口径冲突，**并列不合成** | [Abanto Law, 2026](https://abantolaw.com/fintech-online-payments-regulatory-developments-philippines-2026/)；[BitPinas, 2026 Q1](https://bitpinas.com/?p=74103) | 2026-07 后 |
| 观察哨 | **拟议 12 个月暂停仅针对新 OPS 注册**：草案未定案、仅作观察哨，**不得与 VASP 暂停令混为一谈** | [UseTheBitcoin 引 BitPinas 主编 2026-09-07 澄清](https://usethebitcoin.com/news/philippines-vasp-freeze-proposal/) | 草案 |
| 观察哨 | **2015 IRR Rule 11.2 商品期货规则暂停的现行有效性须回一手条文＋本地律师意见核实（全案单点最大法律不确定性）**；不写「已确认仍有效」或「已被替代」 | 参数卡 v3 D8／§4 已知证据缺口，无一手条文 | T0 门槛 |
| 观察哨 | BSP 沙盒毕业仍须待暂停令解除方可取牌 | [Legal 500/SyCipLaw, 2022·历史背景](https://www.legal500.com/intelligence/philippines/finance-and-banking/come-play-in-the-sandbox-bsp-invites-innovations-through-regulatory-sandbox-framework) | 暂停令解除后 |

### 清单 3｜合作方式与分阶段动作（含被否决备选）

| 阶段 | 动作（均为**建议**） | 前提依赖 |
|---|---|---|
| T0（0–3 月） | 本地律师核验 2015 IRR Rule 11.2 现行有效性、MC 5 衍生品边界；**不启动任何面向公众的招揽** | 前提：取得书面法律意见；未核验前后续动作全部冻结 |
| T1 | 设本地股份公司并备齐下列**准入要件明细**；向 PhiliFINNO 递 CASP Form 1 并持续报送（[SEC MC No.04 s.2025 CASP Rules](https://www.sec.gov.ph/?p=138912)；[RegAlert 转录 SEC MC 5 全文, 2025-06-02 备案](https://regalert.today/document/sec-guidelines-on-the-operations-of-crypto-asset-service-providers-sec-casp-guid-3b1b57f6-978d-4185-aac9-ff489684621e)；[Ocampo & Suralvo, 2025](https://www.ocamposuralvo.com?p=2483/)） | 前提：T0 通过；所有合同／MOU 须报 SEC 批准 |
| T2 | 并购或合作既有 BSP 持牌 VASP／EMI；完成 90 天系统集成（法币轨道＋自动 AML/CTF 报送），不构成公开商业发布（[BlockShoals FAQ](https://blockshoals.com/faq)；[BusinessWorld, 2026-07-29](https://bworldonline.com/corporate/2026/07/29/766484/binance-stratbox-pilot-eyed-within-the-year/)） | 前提：交易经 BSP／SEC 事先认可；**证据不足**：未检索到 VASP 牌照变更控制自动转移的一手条文，须逐案核验 |
| T3 | 24 个月分阶段：先现货、后复杂产品；分层准入配知识／技能／经验测试与客户适当性评估；逐产品向 SEC 报送；比索层始终隔离（[Daily Tribune, 2026-07-28](https://tribune.net.ph/2026/07/28/sec-tests-crypto-oversight-with-blockshoals-2)；[Ablola Law 解读 MC 5, 2025](https://ablola.co?p=16716/)） | 前提：每阶段获 SEC 批准；不得预设毕业 |
| T4 | 依 special rules 毕业并申领正式牌照 | 前提：暂停令解除＋SEC／BSP 双线批准 |

**T1 准入要件明细（参数卡 v3 §8／D8 核定）**：① 本地 SEC 注册股份公司、公司章程主营目的含 CASP；② ≥₱1 亿实缴资本（现金或财产，**不含加密资产**）；③ 菲律宾**实体办公室**（营业时间内有人员）＋**本地数据中心**；④ **CASP Form 1 递 PhiliFINNO**（具体投递邮箱／表单地址本轮未取得 SEC 一手出处，本稿不列明，须实施前向 SEC 核验）并持续月／季／年报、钱包地址与审计财报、记录留档 ≥5 年；⑤ **所有合同／MOU 须报 SEC 批准**；⑥ **披露文件须于营销或发行前 ≥30 天**公布；⑦ **marketing 涵盖社交帖、活动、广告、空投、直播**及非善意「教育内容」；⑧ 客户适当性评估与客户资产隔离（[RegAlert MC5 全文](https://regalert.today/document/sec-guidelines-on-the-operations-of-crypto-asset-service-providers-sec-casp-guid-3b1b57f6-978d-4185-aac9-ff489684621e)；[Ocampo & Suralvo, 2025](https://www.ocamposuralvo.com?p=2483/)；[Manila Times CASP Rules, 2025-06-12](https://www.manilatimes.net/2025/06/12/business/top-business/sec-issues-rules-on-crypto-asset-service-providers/2131711)；[Ablola Law, 2025](https://ablola.co?p=16716/)）。**EMI 发牌通道仍开放**（[Law.asia/Romulo, 2026](https://law.asia/?p=723541)）；**拟议 12 个月暂停新 OPS 注册为草案未定案、仅作观察哨**；**VASP 牌照变更控制是否自动转移＝证据不足**。

**跨章一致性说明（与第 3／4 章统一，参数卡 v3 §12，`kind: judgment`）**：清单 3 的 T2／T3 借鉴的是 BlockShoals×Binance 的**双监管三角结构模板**（本地 CAI 承担合规、BSP 持牌 VASP 承担法币、境外方仅提供技术），**不等于该主体当前可作为承接方、更不等于通道已通**。第 4 章已将其列为「**观察哨而非立即可用承接方**」，依据为：公开 onboarding 尚未开放（官网明示「Public onboarding has not opened yet」）、沙盒参与为受监督测试而非完整牌照（「Sandbox participation is a supervised test and is not a full licence」）、Binance 与 BlockShoals 自身均不持有 VASP 牌照、比索法币层外包予第三方持牌 VASP、测试期 24 个月（[BlockShoals 官网, 访问 2026-11-09](https://blockshoals.com/)；[Mintchain, 2026](https://mintchain.ph/?p=3441)；[Daily Tribune, 2026-07-28](https://tribune.net.ph/2026/07/28/sec-tests-crypto-oversight-with-blockshoals-2)；[BusinessWorld, 2026-07-29](https://bworldonline.com/corporate/2026/07/29/766484/binance-stratbox-pilot-eyed-within-the-year/)）。第 4 章结论为「**结构可复制、许可不可复制**」：第②角受 M-2025-031 暂停令约束、第③角受沙盒名额与 24 个月测试期约束。另据第 3 章，截至 2026-11-09 合规承接方公测未开放，**「合规溢价」目前是预期而非已兑现的观测值**。两者不矛盾：**结构模板可借鉴，该主体当前不可用**。

**被否决备选（记录阈值与结论，`kind: judgment`）**：**A 沙盒内直做零售 CFD**——否决阈值＝无明文全面禁止但 SRC 8.1／28 注册要求（[SEC MC No.9 s.2024 StratBox](https://www.sec.gov.ph/wp-content/uploads/2024/04/2024MC_SEC-MC-No.-9-S.-of-2024-SEC-Stratbox-Strategic-Sandbox-1.pdf)；[Manila Bulletin XM CDO, 2025-12-12](https://mb.com.ph/2025/12/12/sec-issues-cease-and-desist-order-against-brokerage-firm-xm)）、2025–2026 连续 CDO／警示（[SEC Advisory against FX AFFILIATE, 2024-03](https://www.sec.gov.ph/wp-content/uploads/2024/03/2024Advisory-Against-FX-Affiliate.pdf)；[Inquirer, SEC warns Exness/HFM](https://plus.inquirer.net/business/sec-warns-investors-vs-exness-global-hf-markets/)）、沙盒不覆盖且毕业须 special rules；结论＝**不启动**。**B 离岸平台直连本地钱包**——否决阈值＝XM CDO 判词＋M-2026-003 零售直连禁令（母国持牌亦不免）；结论＝**不启动**。**C 自建新 VASP 牌照**——否决阈值＝**新 VASP 牌照持续暂停且重估无确定时点**（M-2025-031 自 2025-09-01 持续生效、视 global and local developments 重估）；结论＝**不可得**。

## 5.3 分析：反方①—⑦逐条回应

① **成立**：Circ 1153 明文不得规避现行法规、SEC MC 9 s.2024 沙盒不自动给牌（[ASG Law, 2022](https://asg.ph/insights/bsp-regulatory-sandbox-framework-1153)；[SEC MC No.9 s.2024](https://www.sec.gov.ph/wp-content/uploads/2024/04/2024MC_SEC-MC-No.-9-S.-of-2024-SEC-Stratbox-Strategic-Sandbox-1.pdf)；[Mintchain, 2026](https://mintchain.ph/?p=3441)）；Quevedo 2026-08 原话如上。需并陈另一面：StratBox 允许 SEC 在法定权限内就个别参与者临时调整或豁免**某些**要求，但明文「不豁免现行法律、不得用于规避」（[Mintchain, 2026](https://mintchain.ph/?p=3441)）——形式窗口存在，实质通道仍无。

② **成立且须精确化**：XM CDO 认定未注册证券「operates as a fraud on investors」（[Manila Bulletin, 2025-12-12](https://mb.com.ph/2025/12/12/sec-issues-cease-and-desist-order-against-brokerage-firm-xm)）；MC 5 另规定「除非 SEC 另行允许，CASP 不得提供加密资产衍生品或杠杆交易」（[Ablola Law, 2025](https://ablola.co?p=16716/)），但该条针对 *crypto-asset derivatives*，**不能据此推定零售 CFD 已被明文全面禁止——参数卡 v3 §4／D18 所载该一手条文缺口仍成立**。

③ **成立**：见清单 1 首行；并陈行业观点：切割方式是由本地持牌 CAI 承担合规、境外方仅提供技术，而非境外主体直连（[BlockShoals FAQ](https://blockshoals.com/faq)）。

④ **成立**：新 VASP 牌照持续暂停下只能并购／合作既有持牌方；变更控制是否自动转移**证据不足**（仅见 CASP 要求合同报批的旁证，非直接条文）。

⑤ **成立**：BSP 2025 CFIS 投资参与率 36%(2021)→23%(2025)、虚拟资产认知 6%(2021)→20%(2025)、实际持有约 1%（[BusinessWorld, 2026](https://www.bworldonline.com?p=743500/)；[Manila Standard, 2026](https://manilastandard.net/business/banking-report/314728090/philippine-financial-literacy-rose-to-74-in-2025-bsp-says.html)；[SiGMA World, 2026](https://sigma.world/news/financial-literacy-reshapes-ph-igaming-behaviour/)）；分母为 15 岁以上成人、样本 8,784 份、调查期 2025-02-16–07-24——**需求侧远弱于「加密热土」叙事**。

⑥ **时间维度，成立且最关键**：**双期并列**——2026 Q2 GDP 2.3% vs **2025 Q2 5.4%**、Q2 家庭消费 2.8% vs **2025 Q2 5.2%**、上半年 GDP 2.6%／通胀 4.8%（2025 全年通胀 1.7%）、Q1 2.8%；固定资本形成 −13.7%（Philstar）／−9.2%（PSA，**两口径并列不合成**）（参数卡 v3 §3 基线，第 1 章产出、本章复用；[PSA／Trading Economics, 2026-10 更新](https://tradingeconomics.com/philippines/gdp-growth-annual) 另载 2025 全年 4.4% vs 2024 5.6%，为年度 GDP 口径，与双期并列分列不合成）。**2027 复苏为预测非事实，且各机构预测跨时点变动，以下全部并列不合成、不得取平均**：IMF Article IV 2026-09「2026 3.4%／2027 5.1%」（[IMF PR 26/304, 2026-09-25](https://www.imf.org/en/news/articles/2026/09/25/pr26304-imf-staff-completes-2026-article-iv-mission-to-the-philippines)）；世行 PEU 2026-08「2026 3.7%／2027 5.2%」（[World Bank PEU Midyear 2026, 2026-08-03](https://worldbank.org/en/news/press-release/2026/08/03/ph-reaches-upper-middle-income-status-bolder-reforms-critical-for-more-inclusive)；[CPBRD BB2026-01, 2026-07](https://docs.congress.hrep.online/download/cso/2027/BB2026-01-PHILIPPINE-ECONOMY-MACROECONOMIC-PERSPECTIVES-2026.pdf) 表中 WB 列同值）；CPBRD BB2026-01（2026-07）另载 2027 增速 WB 5.2／ADB 5.3／AMRO 5.5／IMF 5.5（[CPBRD, 2026](https://docs.congress.hrep.online/download/cso/2027/BB2026-01-PHILIPPINE-ECONOMY-MACROECONOMIC-PERSPECTIVES-2026.pdf)）；2026-10 机构区间 ADB 5.1／AMRO 4.8／S&P 5.4／DBCC 目标 5–6%（[Daily Tribune, 2026-10-15](https://tribune.net.ph/amp/story/2026/10/15/economist-bets-on-2027-rebound)）。**若以 2025 高增长数据做进入测算，将系统性高估可支配收入与风险偏好。**

> 〔口径注〕参数卡 §3 原载「IMF 2026-04 WEO 4.1%/5.8%（4.3%/3.2%）」作为 2027 口径，本轮未在一手 WEO 复核，且 5.8% 在菲律宾众议院 CPBRD 官方文件中对应**世行对 2026 年通胀**的预测，判为口径错位，**已按 D14 整组撤下，不再作为 2027 增速口径**。

⑦ **成立（一手规章，D19）**：判据为 PAGCOR 官方 Rev.1 规章第 26–27 页 g 条（生效 2025-10-02）明文「PC is not allowed the utilization of credit cards and crypto-currency in account funding and/or withdrawal」（[PAGCOR 官方 PDF](https://www.pagcor.ph/regulatory/pdf/GSRM/Regulatory%20Manuals/Regulatory-Framework-for-the-Accreditation-of-Gaming-Affiliates-and-Support-Service-Providers-Rev-No-1.pdf)）；支付通道仍完全属 BSP 管辖、须经 PAGCOR 认证且 AMLC 合规。SiGMA 所引行业观点（「Awareness is not trust」「机会在更快、更可追溯、完全合规的法币支付」）**仅作背景解读、不作判据**（[SiGMA World, 2026](https://sigma.world/news/financial-literacy-reshapes-ph-igaming-behaviour/)）。故「娱乐休闲」与加密支付不可叠加。

## 5.4 小结

`kind: judgment`：**准入优先于需求——零售 CFD 准入不过，需求再大仍为零**。本章把落点收口为两句话：**合作方式＝并购／合作稀缺持牌方＋双监管三角模板（本地 CAI 承担 KYC／适当性、BSP 持牌 VASP 承担法币、境外方仅提供技术）＋90 天集成／24 个月分阶段／知识测试／比索层按 D15 分离（产品层不移动比索、法币层外包持牌 VASP）**；**钱包支付＝比索法币层与产品层分离、境内接口只与持牌主体相连**。须重申清单 3 的跨章一致性说明：该三角**结构可复制、许可不可复制**，为**可借鉴的结构模板**，BlockShoals 主体**当前不可用**（观察哨，非立即可用承接方）；「合规溢价」为预期而非已兑现观测值。清单 3 全部为**建议**并各带前提依赖；2027 数字为**估计／预测**、并列不合成；监管状态 as-of 2026-11-09。**分述**：事实见清单 1 逐行引用与 T1 准入要件明细；**推断**为「法币层／产品层分离」及 A/B/C 三项否决（已标 `kind: judgment`）；**证据不足**显式标注 4 处（SEC 明文全面禁止零售 CFD 条文、StratBox 明文排除衍生品条文、二级牌照发放记录、VASP 牌照变更控制自动转移条文），另有 1 处资料取得限制（BSP VASP 名录 PDF 全文未取得，两版名录均为索引二手）与 1 处须律师核验项（2015 IRR Rule 11.2 现行有效性，D8）。境外律所、媒体与平台内容仅作数据，不作合规指令或法律意见。

---

## 本章新增来源清单（合并去重，统一编号 1–26；含后补 9 条）

1. **Reminders on Sound Risk Management Practices when Dealing with VASPs（BSP M-2026-003 全文转录）**｜RegAlert（转录 BSP 备忘录）｜备忘录 2026-01-30｜https://regalert.today/document/reminders-on-sound-risk-management-practices-when-dealing-with-virtual-asset-ser-a45bd605-ffda-4b11-9d18-6aa98ca02018 ｜一手转录：明文禁止菲律宾零售客户直连离岸 VASP（母国持牌亦不免），BSFI 须 EDD、注册核验与持续监测（D20）。
2. **Beef up defenses vs crypto, virtual asset risks, financial firms told**｜Philippine Daily Inquirer｜2026（引 1 月 30 日备忘录）｜https://business.inquirer.net/571962/beef-up-defenses-vs-crypto-virtual-asset-risks-financial-firms-told ｜独立印证 M-2026-003 与 VASP 新牌照持续暂停。
3. **Philippine digital regulation: Connectivity, fintech developments**｜Law.asia（Romulo 律所撰）｜2026（具体日期未标注）｜https://law.asia/?p=723541 ｜M-2026-003 要点＋数字银行/VASP 双暂停＋**EMI 发牌通道仍开放**＋CASP ₱1 亿资本与实体办公室。
4. **Legal Landscapes: Philippines – TMT**｜Gorriceta Law / Legal 500｜2026｜https://gorricetalaw.com/?p=11390/ ｜RA 11127 OPS、Circ 1166 EMI、Circ 1198 MPAA、M-2026-023 代币上架指引；M-2025-031 与 M-2026-003 时间线。
5. **BlockShoals FAQ 及官网（2 URL）**｜BlockShoals Technologies（发行人自述，一手）｜访问 2026-11-09｜https://blockshoals.com/faq ／ https://blockshoals.com/ ｜PHP 入出金**独家**经 BSP 持牌 VASP 轨道；90 天集成；沙盒 ≥2 年；「公开 onboarding 尚未开放」「沙盒参与是受监督测试、非完整牌照」。
6. **Binance StratBox pilot eyed within the year**｜BusinessWorld｜2026-07-29｜https://bworldonline.com/corporate/2026/07/29/766484/binance-stratbox-pilot-eyed-within-the-year/ ｜90 天集成自 4 月起、正接入 BSP 持牌 VASP；分层产品准入＋知识/技能/经验测试。
7. **SEC tests crypto oversight with BlockShoals**｜Daily Tribune｜2026-07-28｜https://tribune.net.ph/2026/07/28/sec-tests-crypto-oversight-with-blockshoals-2 ｜24 个月分阶段、KYC 与产品适当性评估、逐产品报送、复杂产品需额外知识测试与监管批准。（参数卡补充另载无 `-2` 后缀版本，同文。）
8. **Inside the Philippines' Crypto Sandbox: How StratBox Is Redrawing the Rules for Digital Asset Business Models**｜Mintchain｜2026｜https://mintchain.ph/?p=3441 ｜Quiogue「不移动比索」原话、BSP「沙盒不豁免牌照」、SEC 主席 Lim 与委员 Quevedo「非快车道」原话；StratBox 可个别临时调整但不豁免法律。（本条亦见于参数卡补充来源。）
9. **SEC Chairperson Francis Lim Defends BlockShoals Admission to Strategic Sandbox**｜Bitdigest｜引 2026-08-26 表态｜https://www.bitdigest.io/posts/sec-chairperson-francis-lim-defends-blockshoals-admission-to-strategic-sandbox ｜Quevedo「入盒非获批快车道」表态；90 天仅限技术集成，不含公开 onboarding／交易／全面商营。「不治愈既往 SRC 违法」另见本清单第 8 条 Mintchain，两源分列不合成。
10. **Fintech and Online Payments in the Philippines: What Changed for 2026**｜Abanto Law Firm｜2026｜https://abantolaw.com/fintech-online-payments-regulatory-developments-philippines-2026/ ｜MariBank 2026-07-18 为第七家数字银行、上限 10 下剩 3 席；Circ 1238（2026-06-17）；Project Nexus 2027 年中；AFASA 合规期 2026-06-25 届满。（本条亦见于参数卡补充来源。）
11. **BSP to Release Shortlist for 4 New Digital Bank Licensees in Q1 2026**｜BitPinas｜2026 Q1｜https://bitpinas.com/?p=74103 ｜4 张新牌照、3 份申请、₱10 亿最低资本；与第 10 条构成**时间差**并列口径，不合成（D5／D17）。
12. **Philippines nears seamless cross-border payments with Project Nexus link**｜Manila Bulletin｜2026-03-03｜https://mb.com.ph/2026/03/03/philippines-nears-seamless-cross-border-payments-with-project-nexus-link ｜BIS Nexus 2027 年中上线；2025 两轨 ₱24.74 万亿 +42%、约 GDP 90%；2024 数字支付占零售 57.4%（2023 52.8%）。
13. **Regulatory Framework for the Accreditation of Gaming Affiliates and Support Service Providers, Rev. No. 1**｜PAGCOR（**一手规章**）｜生效 2025-10-02｜https://www.pagcor.ph/regulatory/pdf/GSRM/Regulatory%20Manuals/Regulatory-Framework-for-the-Accreditation-of-Gaming-Affiliates-and-Support-Service-Providers-Rev-No-1.pdf ｜第 26–27 页 g 条明文禁支付通道以信用卡与加密货币作账户入金/出金；PC 须 BSP 注册、AMLC 合规、PAGCOR 认证。**反方⑦判据由业内观点升级为一手规章（D19）**。
14. **SEC Guidelines on the Operations of Crypto-Asset Service Providers（MC 5 全文）**｜RegAlert（转录 SEC）｜2025-06-02 向 UP Law Center 备案｜https://regalert.today/document/sec-guidelines-on-the-operations-of-crypto-asset-service-providers-sec-casp-guid-3b1b57f6-978d-4185-aac9-ff489684621e ｜CASP Form 1 递 PhiliFINNO、₱1 亿实缴资本、实体办公室、所有合同/MOU 须报 SEC 批准、月/季/年报与 5 年留档（T1 准入要件）。
15. **SEC MC No. 5-2025: New Crypto Rules Raise the Bar**｜Ablola Law｜2025（具体日期未标注）｜https://ablola.co?p=16716/ ｜除非 SEC 另行允许，CASP 不得提供加密资产衍生品或杠杆交易；客户适当性评估；本地数据中心；禁涉赌博类及匿名化加密资产（D18）。
16. **PHILIPPINE ECONOMY: MACROECONOMIC PERSPECTIVES 2026（BB2026-01）**｜菲律宾众议院 CPBRD（官方）｜2026（引 2026-07-08 DBCC 声明）｜https://docs.congress.hrep.online/download/cso/2027/BB2026-01-PHILIPPINE-ECONOMY-MACROECONOMIC-PERSPECTIVES-2026.pdf ｜2027 增速 WB 5.2／ADB 5.3／AMRO 5.5／IMF 5.5；2026 增速 WB 3.7、通胀 WB 5.8 等；表中 5.8% 对应通胀而非增速，可作 D14 口径错位核查依据。
17. **BSP VASP 名录时点对照（3 源合并条目）**｜WorldNgayon（引 2026-05-31 名录 11 家）https://worldngayon.com/crypto-tradfi-2026 ／ DOPAY（引 2026-07-15 名录）https://dopay.ph/?p=3608 ／ TheCryptoNewsFeed（名录更新剔除 BloomX、XenRemit）https://thecryptonewsfeed.com/news/bsp-updated-vasp-registry-drops-bloomx-and-xenremit-reclassifies-two-other-firms-17715 ｜2026｜要点：2026-05-31 版 11 家 vs 2026-07-15 版 9 家（6 活跃非银行＋1 未运营＋2 银行），BloomX／XenRemit 被剔除；**两版按 as-of 并列不合成、均为索引二手、BSP PDF 全文未取得**；结论级含义「可承接持牌主体在收缩」（D16／D22）。
18. **Sandbox participants are already testing tokenized products（转引 SEC 2025-11 披露）**｜Daily Advent（聚合转引，仅作数据）｜2025-11 事件／2026 页面｜https://lite.dailyadvent.com/detail/58930492260620en_ng ｜**截至 2025-11 累计 4 家**：2025-06-02 已有 GCash／GStocks Global（美股，24 个月／200 万人）与 Pluang PH（美股，6 个月／1,000 人），2025-11 BlockShoals 为第 4 家；构成 2 美股／1 代币化地产／1 加密中介，**零售 CFD 0 家**（D4）；StratBox 可个别临时调整但不豁免现行法。
19. **Mapping stablecoin regulatory landscape in Philippines（Law.asia/Punolaw 撰）**｜ethcred（转载 Law.asia 内容）｜2026｜https://ethcred.com/?p=32485 ｜HB 4792 仍待审；PHPC 为唯一 BSP 沙盒毕业项目（2025-06）；M-2025-031 持续生效、视发展重估（律所解读为无限期）；PHPX、Cebuana Lhuillier、BPI×Meridian 稳定币结算进展；SEC 2026-01 对 IBKR 警示。
20. **Philippines Tightens Crypto Rules With 12-Month Freeze Proposal**（后补第 3 条）｜UseTheBitcoin（引 BitPinas 主编 Michael Mislos 2026-09-07 澄清）｜2026-09｜https://usethebitcoin.com/news/philippines-vasp-freeze-proposal/ ｜**拟议 12 个月暂停仅针对新 OPS 注册而非 VASP**；**草案未定案、仅作观察哨，与 VASP 暂停令分属不同监管对象，不得混为一谈**（D3）；VASP 新牌照自 2025 起持续暂停、重估无确定时点。
21. **Financial account ownership among Filipinos at 50% — BSP**（后补第 4 条）｜BusinessWorld｜2026（BSP 2025 CFIS 发布后，具体日期未标注）｜https://www.bworldonline.com?p=743500/ ｜投资参与率 36%(2021)→23%(2025)；2025 CFIS 样本 8,784 份、调查期 2025-02-16–07-24；账户拥有率 50%（前值 56%）。
22. **Philippine financial literacy rose to 74% in 2025, BSP says**（后补第 5 条）｜Manila Standard｜2026（具体日期未标注）｜https://manilastandard.net/business/banking-report/314728090/philippine-financial-literacy-rose-to-74-in-2025-bsp-says.html ｜虚拟资产认知升至 20%、投资品认知 53%、64% 会先核实机构是否受监管——反方⑤佐证。
23. **Philippines GDP Annual Growth Rate**（后补第 6 条）｜Trading Economics（数据源 PSA）｜2026-10 更新｜https://tradingeconomics.com/philippines/gdp-growth-annual ｜2026 Q2 GDP 2.3%（Q1 2.8%）、家庭消费 2.8%（Q1 3.0%）、固定投资 −13.7%；2025 全年 4.4% vs 2024 5.6%（年度 GDP 口径，与参数卡 §3 双期并列分列不合成）。
24. **Economist bets on 2027 rebound**（后补第 7 条）｜Daily Tribune｜2026-10-15｜https://tribune.net.ph/amp/story/2026/10/15/economist-bets-on-2027-rebound ｜2027 增速预测多口径 IMF 5.1／WB 5.2／ADB 5.1／AMRO 4.8／S&P 5.4／DBCC 目标 5–6%；均为**预测非事实、跨时点变动、并列不合成**（D14）。
25. **Halt order issued versus Pacquiao-endorsed XM**（后补第 8 条）｜The Manila Times｜2025-12-13｜https://www.manilatimes.net/2025/12/13/business/corporate-news/halt-order-issued-versus-pacquiao-endorsed-xm/2242635 ｜**XM CDO 判词双源复核**：本地银行/e-wallet 作支付伙伴＝以菲投资者为主要目标市场；SRC 8.1/28 与「fraud on investors」。
26. **CASP 规则条文与解读（2 源合并条目；后补第 9 条）**｜Ocampo & Suralvo Law Offices ／ The Manila Times｜2025（MC 05 于 2025-05-30 发布、2025-06-02 备案）｜https://www.ocamposuralvo.com?p=2483/ ／ https://www.manilatimes.net/2025/06/12/business/top-business/sec-issues-rules-on-crypto-asset-service-providers/2131711 ｜CASP 章程主营目的、₱1 亿实缴资本（不含加密资产）、月/季/年报＋5 年留档；marketing 涵盖社交帖／活动／广告／空投／直播，披露文件须提前 ≥30 天；2025-06 已有 **GCash／GStocks Global 与 Pluang PH** 参与 StratBox（D4）。

---

## 复用来源池（本章实际复用的参数卡来源；其余参数卡条目由第 1–4 章引用，本章不重复）

**A 组｜来源池 15 条中本章引用**

1. [SEC MC No.9 s.2024 StratBox（v3 D7 核定路径）](https://www.sec.gov.ph/wp-content/uploads/2024/04/2024MC_SEC-MC-No.-9-S.-of-2024-SEC-Stratbox-Strategic-Sandbox-1.pdf) — 沙盒形式窗口、不自动给牌、毕业须 special rules。**措辞精确**：条文来自搜索引擎索引正文快照（§7、§12–§16、Annex 1），另经 Grant Thornton 镜像＋Ablola＋Lexology 交叉印证；**WebFetch 直连仍返回 Cloudflare「Just a moment」，不得自称直连一手核验成功**（参数卡 v3 D7）。旧路径 `/2024/05/...Strategic-Sandbox.pdf` 为参数卡 v2 所载，本章已按 D7 更新。
2. [SEC MC No.04 s.2025 CASP Rules](https://www.sec.gov.ph/?p=138912) — 本地股份公司、≥₱1 亿实缴资本、PhiliFINNO 备案与持续报送。
3. [SEC Advisory against FX AFFILIATE](https://www.sec.gov.ph/wp-content/uploads/2024/03/2024Advisory-Against-FX-Affiliate.pdf) — 2024-03 对未注册外汇平台警示，被否决备选 A 阈值。
4. [BSP List of VASP（11 家）](https://www.bsp.gov.ph/Lists/Directories/Attachments/19/VASP.pdf) — 参数卡标注「PDF 取自索引表格」；本章据 D16／D22 明确全文未取得、两版名录均为索引二手、按 as-of 并列不合成。
5. [IMF PR 26/304](https://www.imf.org/en/news/articles/2026/09/25/pr26304-imf-staff-completes-2026-article-iv-mission-to-the-philippines) — 2026-09-25：2026 3.4%／2027 5.1%（D14 主口径之一）。
6. [World Bank PEU Midyear 2026](https://worldbank.org/en/news/press-release/2026/08/03/ph-reaches-upper-middle-income-status-bolder-reforms-critical-for-more-inclusive) — 2026-08-03：2026 3.7%／2027 5.2%（经 CPBRD BB2026-01 表 WB 列交叉；D14）。
7. [Manila Bulletin, SEC CDO vs XM（2025-12-12）](https://mb.com.ph/2025/12/12/sec-issues-cease-and-desist-order-against-brokerage-firm-xm) — 「接入本地银行与电子钱包作支付伙伴＝以菲律宾公众为目标市场」关键判词。
8. [Inquirer, SEC warns Exness/HFM](https://plus.inquirer.net/business/sec-warns-investors-vs-exness-global-hf-markets/) — 2025–2026 连续警示，被否决备选 A 阈值。
9. [ASG Law, BSP Circular 1153](https://asg.ph/insights/bsp-regulatory-sandbox-framework-1153) — 沙盒不覆盖证券/衍生品、不得规避现行法规、测试期与毕业规则。
10. [Law.asia 中文版《稳定币的两面》](https://law.asia/zh-hans?p=724913) — M-2025-031 持续生效／律所解读为无限期、PHPC 唯一沙盒毕业、HB 4792 待审。

**B 组｜参数卡「补充（本章高相关）」中本章引用**

11. [BitPinas, BSP M-2025-031 全文转录](https://bitpinas.com/regulation/bsp-vasp-ban/) — 一手转录：自 2025-09-01 持续生效、subject to reassessment based on global and local developments（D3）。
12. [Daily Tribune, BlockShoals（无 `-2` 后缀版）](https://tribune.net.ph/2026/07/28/sec-tests-crypto-oversight-with-blockshoals) — 与新增清单第 7 条同文，URL 后缀差异已注明。
13. [Mintchain, Inside the Philippines' Crypto Sandbox](https://mintchain.ph/?p=3441) — 与新增清单第 8 条同文。
14. [Abanto Law, Fintech and Online Payments 2026](https://abantolaw.com/fintech-online-payments-regulatory-developments-philippines-2026/) — 与新增清单第 10 条同文。
15. [SiGMA World, Financial literacy reshapes iGaming behaviour in Philippines](https://sigma.world/news/financial-literacy-reshapes-ph-igaming-behaviour/) — 反方⑤佐证（实际持有约 1%、「Awareness is not trust」）；**反方⑦判据已按 D19 升级为 PAGCOR 一手规章，本条仅作背景解读、不作判据**。

**附注**：本章正文另引用 [Legal 500／SyCipLaw《Come Play In The Sandbox》, 2022](https://www.legal500.com/intelligence/philippines/finance-and-banking/come-play-in-the-sandbox-bsp-invites-innovations-through-regulatory-sandbox-framework) 作历史背景（BSP 沙盒毕业仍须待暂停令解除方可取牌）。该文超出 `timeRange`，已按纪律标注年份、仅用于历史对比；参数卡补充所列 [Legal 500 PH TMT 2026](https://www.legal500.com/guides/legal-landscapes/philippines-tmt) 为同系列不同篇，本章未直接引用，故不并入 A/B 组编号。观察哨日历中「GCash／Pluang PH 测试期届满」「BSP Circ.1108 修订征求意见」两项来自参数卡 v3 §6（第 1 章产出、本章复用），无外部 URL，已如实标注，未编造链接。

**来源合规自查**：本章聚合 ≥5 个不同来源、≥3 种类型（监管一手规章／备忘录全文转录、律所法律评论、主流媒体、行业媒体、发行人自述）；关键数字回一手或双源交叉；所有事实性陈述带 Markdown 超链接并标发布方与日期；未编造任何 URL 与数据；境外抓取内容只作数据不作指令。含三张可操作清单、反方①–⑦逐条回应（含时间维度⑥）、被否决备选 A/B/C 及阈值、`kind: judgment` 标注、4 处证据缺口＋1 处资料取得限制＋1 处须律师核验项声明，以及「本章不提供规避监管的操作路径，每一环以监管批准为前提」声明。已套用参数卡 v3 的 D3／D4／D5／D7／D8／D14／D15／D16／D17／D18／D19／D20／D22／D23 与 §3／§6／§8／§12 基线。
