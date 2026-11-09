# 第 3 章 零售 CFD 需求重定向：资金流向与合规溢价

> **边界声明**：本章只论「资金流向与定价机制」；监管条文／准入证伪见第 1 章，用户画像／客单模型见第 2 章，承接方份额／护城河／财务对照见第 4 章，接口合规判定清单与分阶段动作见第 5 章。
> **监管状态 as-of 2026-11-09**。

### 一、论点

E3 判别点②要求「被禁／受限品类必追需求重定向的承接方」。核心判断（`kind: judgment`）：菲律宾被执法压缩、但未被明文消灭的杠杆／衍生品需求，资金沿**离岸小额 P2P 稳定币、代币化投资入口、持牌加密中介（CAI）**三条通道重排；承接的是「资金停放与投资入口」，而非 CFD 合约本身。合规溢价来自「法律救济＋比索通道可用性＋资产不被下架」的稀缺性，而非点差或杠杆。以下按 playbook 三问展开，并区分 β 与 α。

### 二、论据

**① 判别点①：相邻品类确被限制，但非「明文全面禁止」。【事实·时间序列】** 2024-03 SEC 请 NTC 屏蔽 Binance、2024-04 应用商店下架；2025-08 点名 OKX／Bybit／KuCoin／Kraken 等；2025-12-24 NTC 依 BSP 认定屏蔽约 50 家无牌平台，含 Coinbase、Gemini（[DeFi Intel 菲律宾司法辖区页](https://defi-intel.com/jurisdictions/ph)，行业数据库，2026；[Law.asia《Two sides of the coin》](https://law.asia/stablecoin-regulations-hong-kong-philippines/)，PUNOLAW 律师撰稿，2026-10-22）。更直接的是 2026-03-31 SEC 对 GTRADE、dYdX、Orderly Network、Aevo、Pacifica、Deriv、Ostium、Vest Markets 发警示，指其让菲律宾用户「开户并交易数字资产及衍生品工具」，却无 SEC 注册、无 CASP 授权、无《证券监管法典》第 28 条经纪商／交易商资格，推广者最高 ₱500 万罚款或 21 年监禁（[Manila Times](https://www.manilatimes.net/2026/04/22/business/top-business/sec-warns-vs-cryptocurrency-platforms/2325249)，2026-04-22；[Fintech News Philippines](https://fintechnews.ph/?p=71107/)，2026）；其中 Deriv 为零售衍生品／CFD 经纪商，dYdX／Aevo／gTrade／Ostium 为链上永续、期权与杠杆协议（[Manila Times, 2026-04-22](https://www.manilatimes.net/2026/04/22/business/top-business/sec-warns-vs-cryptocurrency-platforms/2325249)；[Fintech News Philippines](https://fintechnews.ph/?p=71107/)，2026；**逐平台功能分类口径由参数卡 §14 核定**）。2026-01-19 SEC 另对 IBKR 发警示，明确其无权「要约、销售或分销证券，包括衍生品」，亦无经纪／交易商／交易所牌照（[ACCRALAW／BusinessWorld 专栏](https://accralaw.com?p=21235/)，律师评论，2026；[BitPinas](https://bitpinas.com/?p=73905)，2026）；2026-07 IBKR 通知菲客户不再接受稳定币存款（[Law.asia](https://law.asia/stablecoin-regulations-hong-kong-philippines/)，2026-10-22）。供给侧同步收紧：BSP M-2022-035 自 2022-09-01 暂停新 VASP 申请三年，M-2025-031（2025-08-29）使暂停自 2025-09-01 **持续生效并视 global and local developments 重估**（律所解读为无限期延长），新主体「必须考虑通过监管沙盒」进入（[Law.asia 中文版《稳定币的两面》](https://law.asia/zh-hans?p=724913)，2026-10-22）。

**【证据不足·显式】** 截至 as-of 仍未检索到「SEC 明文全面禁止零售 CFD」或「StratBox 明文排除衍生品」的一手条文（SEC MC No.9 PDF 曾被 Cloudflare 拦截，见参数卡已知缺口）。准确口径是「未注册即不得招揽」的执法形成**事实上的准入冻结**，而非立法禁止——这一区分决定需求是「被重定向」而非「被消灭」。

**② 判别点②：三条承接通道。**

（1）**小额 P2P 稳定币（离岸／灰区层）**。【事实】[Chainalysis CSAO 2026 区域报告](https://www.chainalysis.com/blog/central-southeast-asia-oceania-crypto-adoption-2026)（Chainalysis，2026-09-30；报告期 2025-07-01–2026-06-30）：菲／泰／越三国合计 540 万笔 <$10,000 小额 P2P 转账，占全球 14.4%，而三国仅占全球加密经济 2.5%；五分之四以上境内转账 <$1,000，均值 $618，对比全球其余地区 $1,210（低约 49%）。15M 据 14.4%／2.5% 算出约 5.8 倍，但**明确警示这是「笔数份额 vs 经济体量份额」之比，不代表三国处理了 5.8 倍价值**（[15M](https://15m.com/news/philippines-thailand-and-vietnam-take-14-4-of-global-small-p2p-crypto-transfers)，2026-10-03）。**【口径拆解·多口径并列不合成】** 参数卡所引「P2P 中 96% 为稳定币」不出自 CSAO，而出自另一份 [Chainalysis 2026 Global Crypto Adoption Index](https://www.chainalysis.com/?p=30288)（2026-09-23），原文 "peer-to-peer is now 96% stablecoins"，属**全球境内 P2P** 口径；同文另载境内个人钱包转账 $56.8B→$228.7B、<$100 与 $100–1,000 两档分别 +78.4%／+58.6%（合计约 $273B 零售规模流量）、跨境稳定币平均单笔约 $3,000。而「5–10% 入境汇款由稳定币结算」是 PDAX CEO Nichel Gaba 的**【估计】**（原文 "probably around 5-10%"，FAQ 作 "an estimated 5-10%"），非 Chainalysis 测量值，菲为全球第四大汇款市场（CSAO 2026）。三者分母、地域、性质各异，**不得合成为「菲律宾 P2P 96% 稳定币」**。

（2）**代币化投资入口（合规承接层）**。【事实】截至 2025-11，SEC StratBox **累计 4 家**（2025-06-02 已有 GCash GStocks／Pluang PH，2025-11 BlockShoals 为第 4 家，其中**零售 CFD 0 家**）：1 家代币化房地产（分级产权）、2 家提供美股准入（免去开立境外券商账户的摩擦）、1 家 BlockShoals 获 in-principle 批准测试 "crypto-related products and services"（[KayaToday](https://kayatoday.com/news/the-philippines-is-building-a-regulated-path-for-tokenized-assets)，2026-06-22；[Mintchain](https://mintchain.ph/?p=3284)，2026；[cointurbos 转述 Cointelegraph](https://cointurbos.com/philippines-is-ready-for-rwa-tokenization-sec-commissioner-says)，2026）。SEC 委员 Rogelio Quevedo 称 OFW「有资本，却不知把钱放在哪里」，PhiliFINNO 助理主任 Paolo Ong 表述更直白：「下一步是他们把已有的钱放到哪里」（[Daily Tribune](https://tribune.net.ph/2026/07/28/sec-tests-crypto-oversight-with-blockshoals)，2026-07-28）。与 IBKR 被警示、停收稳定币存款并置，构成**美股／衍生品入口被切断 → 两家美股代币化项目作为合规承接方**的闭环。更落地的对照：财政部 2023-11 起经 PDAX×GCash 发行的代币化国债，门槛由 ₱5,000 降至 ₱500（约 $8），bonds.ph 超 40 万用户；Project Bayani 白皮书**【估计】** 2030 年菲代币化资产市场达 $60B，并称约 14% 菲人持加密（约 1,500 万）而参与股／债／基金者不足 5%（[Mintchain](https://mintchain.ph/?p=3284)，2026，行业白皮书估计）。

（3）**持牌 Crypto Asset Intermediary（CAI）**。【事实·一手】[BlockShoals FAQ](https://blockshoals.com/faq)（BlockShoals Technologies，2026）：身份为 CASP Rules 下的 CAI，StratBox 依 SEC MC No.9 s.2024；90 天仅为「系统同步＋集成 BSP 持牌 VASP 法币通道＋验证自动 AML/CTF 报告」的技术窗口，「不构成公开商业上线」；PHP 出入金**仅**经 BSP 持牌 VASP 伙伴通道；沙盒最短两年、H2 2026 起。官网另声明「沙盒参与是受监督测试，不是完整牌照，公测尚未开放」（[BlockShoals 声明页](https://blockshoals.com/?srcf=PR)，一手，2026）。SEC 亦澄清 90 天「不应被解读为公开开户、公开交易运营或更广泛市场重开」，in-principle 批准 2025-11-21、Notice to Proceed 2026-04-14（[Manila Bulletin](https://mb.com.ph/article/10922021/business/the-stock-market/sec-puts-brakes-on-binances-new-philippine-crypto-partner)，2026）。Daily Tribune 现场报道补充：沙盒设计 **24 个月分阶段**，用户须过 KYC、合规检查与**产品适当性评估**，更复杂产品须额外知识测试与监管批准；Binance APAC 主管 SB Seker 称采用逐产品报告（product-by-product reporting）。Quiogue 称「Binance 与 BlockShoals 不移动比索，那明显属 BSP 管辖」，BSP 则指两者均不持 VASP 牌照、「参与沙盒不豁免包括牌照要求在内的适用法律」（[Mintchain](https://mintchain.ph/?p=3441)，2026）。**【口径张力·并列不合成】** Daily Tribune 表述为集成后「允许用户将比索兑换为数字资产」，与「沙盒不自行移动比索」并不等同——精确口径应是：比索法币通道必须外包给持牌 VASP，CAI 自身不构成比索结算许可，且 90 天阶段尚未开放公众交易。

（4）**【口径冲突 → 判证据不足】** 中文二手报道（[399btc URL](https://www.399btc.com/qkl/152360.html)，抓取内容署名「币圈界」《菲律宾SEC官宣代币化框架就绪，沙盒试点四企入局》，2026-06-20，非 399btc 自采）称 BlockShoals「被允许测试加密衍生品相关服务」。但英文多源一致表述为 "crypto-related products and services"／"crypto-related services"／"Crypto Asset Intermediary"，举例范围为**托管与 DeFi**（[KayaToday](https://kayatoday.com/news/the-philippines-is-building-a-regulated-path-for-tokenized-assets)、[Mintchain](https://mintchain.ph/?p=3284)、[Finexus](https://api.finexus.net/api/news/events/28b71ae1-0d8d-4c5b-a17d-fedfdd77749b/html)、[HKTDC Research](https://research.hktdc.com/en/article/MjAyNTMxOTgxNw)，2025-06-02 称申请对象为虚拟资产托管人、加密交易所及其他），且无 SEC 原文佐证「衍生品」；反向证据是 SEC 2026-03-31 恰把 dYdX／Deriv 等衍生品平台列为未授权。按「多口径并列不合成」，此处**判证据不足，不得据此认定沙盒对衍生品／CFD 开放，亦不得把 399btc 表述当作 SEC 原文**；四家构成中亦无零售 CFD 项目（与全案定调一致）。

**③ 判别点③：客单价 × 频次下的资金形态。**【事实】540 万笔／年（三国合计）× $618／笔（>80% 境内转账 <$1,000）＝**高频、低客单、稳定币计价**的周转型资金；对比全球其余 $1,210／笔与跨境稳定币约 $3,000／笔，更接近汇款、储蓄搬运与小额兑换，而非机构级或高杠杆建仓。₱500（约 $8）门槛的代币化国债＋40 万用户说明合规侧同样以「极低客单 × 高笔数」吸储（[Mintchain](https://mintchain.ph/?p=3284)，2026）。**【推断，`kind: judgment`】** 此类资金的定价敏感度落在**通道费率、比索／美元兑换价差、最低门槛**，而非 CFD 点差／隔夜息／杠杆倍数；承接方变现逻辑应为「通道抽成＋兑换价差＋托管准入费＋发行分销费」，而非交易佣金。这解释了为何四家沙盒承接方分别落在「投资入口」（地产／美股代币化）与「资金入口」（CAI＋VASP 法币通道），而非复制离岸 CFD 合约。

### 三、分析：合规溢价、定价权与 β／α

**【推断，`kind: judgment`】溢价来源**：SEC 给出的理由是未注册平台的资金「只有极有限或完全没有政府保护」，欺诈归境外司法管辖、须赴境外求偿，而与境内注册主体交易则受菲法律保护、可在本地法院起诉（[ACCRALAW／BusinessWorld](https://accralaw.com?p=21235/)，律师**观点**，2026）。当离岸通道被屏蔽、推广者面临刑责、IBKR 停止稳定币入金后，「资金可追回＋资产不被下架＋比索通道可用」成为可收费的稀缺属性，表现为承接方能维持更高通道费、更高最低门槛与更严格的适当性准入。ChainReport 亦持**观点**：警示会「把更多流量导向受监管的境内通道，监管确定性正成为执行质量的一部分」（[ChainReport](https://chainreport.co/?p=5750)，行业媒体，2026）——**此为观点，非已观测的定价数据**。

**β**：稳定币与汇款大盘——汇率／利率驱动的美元储蓄需求、跨境支付成本下降、全球稳定币余额维持 $98–109B 且占链上余额 22.5%（[Global Adoption Index](https://www.chainalysis.com/?p=30288)，2026-09-23）、CSAO 跨境稳定币活动为境内的 3.2 倍（[CSAO 2026](https://www.chainalysis.com/blog/central-southeast-asia-oceania-crypto-adoption-2026)，2026-09-30）。任何持牌 VASP 都能随这股潮水同涨同跌，按通用判别「同涨同跌＝假分散」，**这不是 α**。**α**：① CAI 身份稀缺（截至 2025-11 累计 4 家中仅 1 家加密中介；BSP M-2025-031 新 VASP 牌照申请自 2025-09-01 **持续生效、视 global and local developments 重估**）；② 90 天 VASP 集成＋分层适当性／知识测试＋逐产品报告构成与监管共同设计的准入闸门，后来者须重走；③ 代币化证券／债券的**发行与分销侧**通道，赚发行费而非交易佣金；④ 本地 KYC、消费者保护与本地法院救济所对应的定价权。但 α 同时受制：沙盒非全牌照、不治愈既往违规（SEC 委员 Quevedo 2026-08 称「不是通往获批的高速公路」，[Mintchain](https://mintchain.ph/?p=3441)）、比索入口外包第三方 VASP、PHPC 是迄今唯一从 BSP 沙盒毕业者（[Law.asia 中文版](https://law.asia/zh-hans?p=724913)，2026-10-22）。供给稀缺既是溢价来源，也是规模天花板。

**【跨章并列基线 D26·并列不合成】** 第 4 章核定的同报告口径——2025-07~2026-06 全球加密市值缩水约 50%、CSAO 区域加密经济收缩 6.8%、菲律宾以约 445 亿美元活动量列区域第 7、全球草根采纳指数第 19（[CSAO 2026](https://www.chainalysis.com/blog/central-southeast-asia-oceania-crypto-adoption-2026)，Chainalysis，2026-09-30；[Global Adoption Index](https://www.chainalysis.com/?p=30288)，2026-09-23）——与本章「小额档 +78.4%／$100–1,000 档 +58.6%、≥$1M 大额转账 −7.2%」**并列不冲突**：前者是**规模／价值**口径，后者是**笔数结构**口径，规模收缩与小额笔数上升可同时成立；**不得单取其一支撑「需求旺盛」**，亦不得据此反推零售 CFD 需求已被证实。

**反方观点并陈（7 条，含时间维度）**：
1. **归因反方（一手）**：CSAO 原文**未**把 540 万笔与交易所封锁／衍生品／杠杆／CFD 需求迁移关联；Chainalysis 并自我限定「链上转账可包含汇款与供应商付款，也可能只是储蓄转移等不对应购买的行为」（[ncijnetwork 转述 Chainalysis](https://ncijnetwork.com/stablecoins-kept-growing-through-cryptos-2-1-trillion-wipeout)，2026）。故 P2P 增长**不能**直接当作 CFD 需求重定向的证据。
2. **替代解释反方**：15M 明确 540 万笔中「无一被标识」为赌场存款／博彩支付／提款；菲央行曾发现在线赌注借沙龙、面包店商户身份收取，部分低至 ₱50（[15M](https://15m.com/news/philippines-thailand-and-vietnam-take-14-4-of-global-small-p2p-crypto-transfers)，2026-10-03）。小额高频存在多种资金源。
3. **口径反方**：96% 为全球口径、540 万笔为三国合计、5–10% 为个人估计，三者分母不同；5.8 倍为笔数份额比而非价值比。
4. **排位反方**：Global Adoption Index 中菲总体第 19、**P2P economy 分项仅第 22**，落后泰国（第 5）、越南（第 14）——14.4% 不可归给菲律宾单国。
5. **时间维度反方（关键）**：2024-03 封 Binance → 2025-06 GCash GStocks Global／Pluang PH 获批 StratBox 测试（美股代币化入口，合规承接侧开放）→ 2025-08 BSP M-2025-031 新 VASP 申请自 2025-09-01 持续生效、视 global and local developments 重估（律所解读为无限期延长，两口径并列）→ 2025-12 封约 50 家 → 2026-01 IBKR 警示 → 2026-03 衍生品平台警示 → 2026-07 IBKR 停稳定币存款且 BlockShoals 获测试授权，但截至 2026-11-09 公测仍未开放、仅为「受监督测试非全牌照」，合作方称完整功能可能需至 2028（[blockchain.news](https://blockchain.news/PostAMP?id=binance-philippines-partnership-blockshoals)，2026-05-26）。**需求重定向到合规承接方在时间上滞后且尚未闭合，故「合规溢价」目前是预期而非已兑现的观测值**。
6. **承接容量反方**：BSP 明确 Binance／BlockShoals 均无 VASP 牌照、沙盒不豁免牌照要求（[Mintchain](https://mintchain.ph/?p=3441)）；四家沙盒项目能否转为商业化，**证据不足**。
7. **需求侧结构性反方（观点）**：ACCRALAW 专栏指出 PSE 指数由 2018 年 9,058.62 跌至约 5,900、feeder fund 双层费用偏高、股票交易税降至 0.1% 仍未提振参与，质疑沙盒能否提供更便宜选项「尚待观察」（[ACCRALAW／BusinessWorld](https://accralaw.com?p=21235/)，律师观点，2026）。

### 四、小结

三问结论：① **有**——杠杆／衍生品／美股入口在 2024–2026 被系统性压缩，但缺「明文全面禁止零售 CFD」一手条文，**证据不足**；② 重定向至离岸小额 P2P 稳定币、代币化投资入口与 CAI 三条通道，惟 Chainalysis 一手数据不支持把这些流量直接归因于 CFD 需求（**推断，非事实**），口径冲突处判**证据不足**；③ 承接方获得的是「法律救济＋比索通道＋资产不被下架」的定价权与发行侧入口（α），稳定币／汇款大盘仅 β。

- `kind: judgment` **J1**：E3 主线成立，但承接的是「资金停放与投资入口」而非 CFD 合约本身。**被否决备选**：①「需求被消灭」（否决：540 万笔高频小额＋14% 持币率 vs <5% 传统投资参与率）；②「需求全部留在离岸无牌平台」（否决：屏蔽＋推广者刑责＋IBKR 停稳定币入金抬高离岸成本；但**无数据量化留存比例，证据不足**）；③「需求已直接流入沙盒 CAI」（否决：公测未开放、时间滞后）。
- `kind: judgment` **J2**：合规溢价源自稀缺的法律救济与法币入口，而非交易手续费。**被否决备选**：①「溢价来自 Binance 品牌／流动性」（品牌有价值，但牌照在 BlockShoals、比索通道外包，不可独占）；②「溢价来自点差／杠杆」（沙盒未开放衍生品，**证据不足**）。
- `kind: judgment` **J3**：α 在准入闸门与发行侧通道，β 在稳定币与汇款大盘。**被否决备选**：①「所有承接方共享 α」（否决：同涨同跌＝假分散）；②「两家美股／地产代币化项目已具 α」（**证据不足**：未见商业化获批或同口径财务数据，留第 4 章）。

**【主线定位说明】** 大纲将 E3 列为全案「主线」，指的是**分析路径／问题结构**（被禁／受限品类必追需求重定向的承接方）；本章把「需求重定向」降格为**推断**，指的是**证据强度**。两者不矛盾，**主线不等于已证实的因果结论**。须再次明确：[Chainalysis CSAO 2026 一手页面](https://www.chainalysis.com/blog/central-southeast-asia-oceania-crypto-adoption-2026)（Chainalysis，2026-09-30）**完全未**把 540 万笔小额 P2P 流量与交易所封锁、衍生品、杠杆或 CFD 需求迁移关联；本章的三条承接通道是基于执法时间序列、代币化试点构成与 CAI 架构的**结构性推断**，而非一手数据证实的资金流追踪。

---

### 关键发现

- **发现 1（判别点①落锤）**：被限制的相邻品类不是抽象的「加密」，而是具体可指的零售杠杆／衍生品——2026-03-31 SEC 警示的 8 家平台中，Deriv 为零售 CFD 经纪商、dYdX／Aevo／gTrade／Ostium 为链上永续与杠杆协议，SEC 明确指其「交易数字资产及衍生品工具」无授权 ([Manila Times](https://www.manilatimes.net/2026/04/22/business/top-business/sec-warns-vs-cryptocurrency-platforms/2325249), [Fintech News Philippines](https://fintechnews.ph/?p=71107/))。
- **发现 2（判别点②最干净的闭环）**：2026-01 SEC 警示 IBKR 无权分销「包括衍生品」的证券 → 2026-07 IBKR 停止接受菲客户稳定币存款 → 沙盒 4 家中恰有 2 家做美股准入 ([ACCRALAW](https://accralaw.com?p=21235/), [Law.asia](https://law.asia/stablecoin-regulations-hong-kong-philippines/), [KayaToday](https://kayatoday.com/news/the-philippines-is-building-a-regulated-path-for-tokenized-assets))。
- **发现 3（监管自己的问题定义）**：Quevedo「OFW 有资本却不知放哪」与 Paolo Ong「下一步是他们把已有的钱放到哪里」，把 E3 问题由监管方原话确认 ([Daily Tribune](https://tribune.net.ph/2026/07/28/sec-tests-crypto-oversight-with-blockshoals))。
- **发现 4（口径必须拆）**：96% 稳定币属全球口径（Global Adoption Index），540 万笔属三国合计（CSAO），5–10% 属个人估计；三者分母不同，合成即失真 ([Chainalysis GAI](https://www.chainalysis.com/?p=30288), [CSAO](https://www.chainalysis.com/blog/central-southeast-asia-oceania-crypto-adoption-2026), [15M](https://15m.com/news/philippines-thailand-and-vietnam-take-14-4-of-global-small-p2p-crypto-transfers))。
- **发现 5（时间维度反方）**：执法密集期 2024-03→2026-07，但截至 2026-11-09 合规承接方公测未开放、仅为测试非全牌照，完整功能或需 2028；重定向尚未闭合 ([blockchain.news](https://blockchain.news/PostAMP?id=binance-philippines-partnership-blockshoals), [BlockShoals 声明](https://blockshoals.com/?srcf=PR))。

### 数据摘要

| 指标 | 数据 | 口径（务必保留） | 来源 |
|---|---|---|---|
| 小额 P2P 转账 | 540 万笔（<$10,000） | 菲／泰／越**三国合计**，2025-07–2026-06 | [CSAO 2026](https://www.chainalysis.com/blog/central-southeast-asia-oceania-crypto-adoption-2026) |
| 全球笔数份额 / 加密经济体量份额 | 14.4% / 2.5% | 三国合计；比值约 5.8x 是**笔数份额比，非价值比** | [CSAO 2026](https://www.chainalysis.com/blog/central-southeast-asia-oceania-crypto-adoption-2026), [15M](https://15m.com/news/philippines-thailand-and-vietnam-take-14-4-of-global-small-p2p-crypto-transfers) |
| 境内转账 <$1,000 / 均值 | >4/5；$618 vs $1,210（低约 49%） | 三国合计 vs 全球其余 | [CSAO 2026](https://www.chainalysis.com/blog/central-southeast-asia-oceania-crypto-adoption-2026) |
| P2P 中稳定币占比 | 96% | **全球境内 P2P** 口径，非菲律宾、非 CSAO | [Global Adoption Index](https://www.chainalysis.com/?p=30288)（2026-09-23） |
| 境内个人钱包转账 | $56.8B → $228.7B | 全球 | 同上 |
| 零售规模流量 | <$100 +78.4%、$100–1,000 +58.6%，合计约 $273B | 全球 | 同上 |
| 跨境稳定币均笔 / 区域倍数 | 约 $3,000；跨境／境内 3.2x | 全球 / CSAO 区域（菲单国倍数**未给出**） | 同上, [CSAO 2026](https://www.chainalysis.com/blog/central-southeast-asia-oceania-crypto-adoption-2026) |
| 入境汇款稳定币结算 | 5–10% | **PDAX CEO 估计**（"probably around"），菲单国，非测量值 | [CSAO 2026](https://www.chainalysis.com/blog/central-southeast-asia-oceania-crypto-adoption-2026) |
| 菲草根采纳排名 | 总体 19；P2P economy 分项 **22** | 全球 117 国 | [Global Adoption Index](https://www.chainalysis.com/?p=30288) |
| 代币化国债门槛 / 用户 | ₱500（约 $8，原 ₱5,000）/ bonds.ph 超 40 万 | 菲，2023-11 起 | [Mintchain](https://mintchain.ph/?p=3284) |
| 持加密 / 传统投资参与 | 约 14%（约 1,500 万）/ <5% | 菲，**行业白皮书估计** | 同上（Project Bayani） |
| 代币化资产市场 2030 | $60B（股票 26／国债 24／基金 6／其他 4） | 菲，**行业白皮书估计** | 同上 |
| 沙盒周期 / 集成期 | 24 个月分阶段 / 90 天 | BlockShoals×Binance | [Daily Tribune](https://tribune.net.ph/2026/07/28/sec-tests-crypto-oversight-with-blockshoals), [BlockShoals FAQ](https://blockshoals.com/faq) |
| 被屏蔽 / 被警示平台 | 约 50 家（2025-12-24）/ 8 家（2026-03-31） | 菲 | [Law.asia](https://law.asia/stablecoin-regulations-hong-kong-philippines/), [Manila Times](https://www.manilatimes.net/2026/04/22/business/top-business/sec-warns-vs-cryptocurrency-platforms/2325249) |

### 本章「证据不足」显式清单

1. 「SEC 明文全面禁止零售 CFD」一手条文——未找到（参数卡已知缺口，本章复核未补上）。
2. 「StratBox 明文排除衍生品」一手条文——未找到（SEC MC No.9 PDF 被 Cloudflare 拦截）。
3. 399btc／「币圈界」称「加密衍生品相关服务」——与英文多源冲突、无 SEC 原文佐证，**判证据不足**，不得据此认定沙盒对衍生品／CFD 开放。
4. Chainalysis 540 万笔与交易所封锁／衍生品／杠杆／CFD 需求迁移的因果关联——一手页面无此表述，**判证据不足**，本章仅作推断。
5. 5–10% 入境汇款稳定币结算的精确测量值——仅 PDAX CEO 估计，非 Chainalysis 测量。
6. 菲律宾单国 P2P 笔数／均值／稳定币占比——一手仅披露三国合计，**未披露单国拆分**。
7. 「96% 稳定币」对菲律宾 P2P 的适用性——一手仅全球口径，适用性**证据不足**。
8. 屏蔽后需求在离岸无牌平台的留存／迁移比例——**无任何量化数据**。
9. 四家沙盒项目商业化获批与同口径财务数据——未见（按边界留第 4 章）。
10. 二级牌照发放记录——参数卡已知缺口，本章未涉及。

---

## 本章新增来源清单（供主编更新来源池）

| # | 标题 | 发布方 | 日期 | URL | 一句话要点 |
|---|---|---|---|---|---|
| 1 | Singapore Leads Central & Southeast Asia and Oceania's Crypto Industry（CSAO 2026 英文版） | Chainalysis | 2026-09-30 | https://www.chainalysis.com/blog/central-southeast-asia-oceania-crypto-adoption-2026 | 540 万笔／14.4%／2.5%／$618 均为菲泰越三国合计；5–10% 汇款为 PDAX CEO 估计；无 96%、无衍生品迁移表述 |
| 2 | 2026 Global Crypto Adoption Index（来源池第 9 条前半，复核补充） | Chainalysis | 2026-09-23 | https://www.chainalysis.com/?p=30288 | 「P2P is now 96% stablecoins」为全球境内 P2P 口径；菲总体第 19、P2P 分项第 22 |
| 3 | Frequently Asked Questions | BlockShoals Technologies（一手企业） | 2026 | https://blockshoals.com/faq | CAI 身份、90 天仅技术集成、PHP 仅经 BSP 持牌 VASP、最短两年、H2 2026 |
| 4 | Statement / 官网首页声明 | BlockShoals Technologies（一手企业） | 2026 | https://blockshoals.com/?srcf=PR | 「沙盒参与是受监督测试，不是完整牌照；公测尚未开放」 |
| 5 | SEC puts brakes on Binance's new Philippine crypto partner | Manila Bulletin | 2026 | https://mb.com.ph/article/10922021/business/the-stock-market/sec-puts-brakes-on-binances-new-philippine-crypto-partner | SEC 官方澄清 90 天不等于公开开户／市场重开；in-principle 2025-11-21、NTP 2026-04-14 |
| 6 | Philippines RWA Tokenization: SEC Opens StratBox Sandbox as Four Firms Test Tokenized Real Estate and US Equities | Mintchain | 2026 | https://mintchain.ph/?p=3284 | 截至 2025-11 累计 4 家构成；₱500 代币化国债／40 万用户；14% vs <5%；$60B 白皮书估计 |
| 7 | SEC warns vs cryptocurrency platforms | Manila Times | 2026-04-22 | https://www.manilatimes.net/2026/04/22/business/top-business/sec-warns-vs-cryptocurrency-platforms/2325249 | 2026-03-31 SEC 警示 8 家未注册加密交易平台 |
| 8 | Philippines SEC Issues Warnings Against 8 Illegal Crypto Platforms | Fintech News Philippines | 2026 | https://fintechnews.ph/?p=71107/ | 明确 8 家「让投资者开户并交易数字资产及衍生品工具」，无 SRC §28 资格 |
| 9 | SEC: You'll Be Safe Here（原载 BusinessWorld） | ACCRALAW 律师专栏 | 2026 | https://accralaw.com?p=21235/ | IBKR 2026-01-19 警示含「包括衍生品」；未注册平台无本地救济；PSE／feeder fund 质疑 |
| 10 | SEC Issues Advisory Against Interactive Brokers (IBKR) | BitPinas | 2026 | https://bitpinas.com/?p=73905 | IBKR 警示细节、可交易衍生品、与约 50 家屏蔽令的关联 |
| 11 | 3 Asian Markets Take 14.4% of Small P2P Crypto Transfers | 15M | 2026-10-03 | https://15m.com/news/philippines-thailand-and-vietnam-take-14-4-of-global-small-p2p-crypto-transfers | 5.8x 为笔数份额比非价值比；540 万笔无一被标识为赌博；₱50 iGaming 替代解释 |
| 12 | Stablecoins kept growing through crypto's $2.1 trillion wipeout | NCIJ Network（转述 Chainalysis） | 2026 | https://ncijnetwork.com/stablecoins-kept-growing-through-cryptos-2-1-trillion-wipeout | Chainalysis 自我限定：链上转账可含储蓄转移，不对应购买 |
| 13 | Binance Eyes Philippine Return Through BlockShoals Collaboration | blockchain.news | 2026-05-26 | https://blockchain.news/PostAMP?id=binance-philippines-partnership-blockshoals | 合作宣布、屏蔽时间线、完整功能或需至 2028（时间维度反方） |
| 14 | Philippines（司法辖区页） | DeFi Intel（行业数据库） | 2026 | https://defi-intel.com/jurisdictions/ph | 2023-11→2026-04 执法时间线；BSP VASP 名录 11 家；2025-12 约 50 家屏蔽 |
| 15 | Philippine Securities Regulator Signals Openness to RWA Tokenization | Finexus | 2026 | https://api.finexus.net/api/news/events/28b71ae1-0d8d-4c5b-a17d-fedfdd77749b/html | 四家沙盒构成；BlockShoals 范围举例「custodial solutions to DeFi applications」 |
| 16 | Philippines Is Ready for RWA Tokenization, SEC Commissioner Says | cointurbos（转述 Cointelegraph） | 2026 | https://cointurbos.com/philippines-is-ready-for-rwa-tokenization-sec-commissioner-says | Quevedo「OFW 有资本却不知放哪」原话；四家构成 |
| 17 | Philippine SEC's New Crypto Warning Raises the Cost of Using Unlicensed Platforms | ChainReport | 2026 | https://chainreport.co/?p=5750 | **观点**：警示把流量导向境内受监管通道，监管确定性成为执行质量一部分 |
| 18 | Binance StratBox pilot eyed within the year（转 BusinessWorld） | edgeX Exchange | 2026 | https://pro.edgex.exchange/en-US/news/article/binance-operator-blockshoals-targets-launch | 分层准入＋knowledge/skill/experience 测试；探索代币化证券／债券；加入 FinTech Alliance |
| 19 | 菲律宾证券交易委员会警告 dYdX 及其他六个平台无牌经营 | CryptoZen 中文 | 2026 | https://cryptozen.asia/cn?p=18789 | 中文交叉：2025-12-24 Coinbase／Gemini 被封、dYdX 等衍生品平台警示 |
| 20 | Two sides of the coin（英文版另一 URL） | Law.asia / PUNOLAW | 2026-10-22 | https://law.asia/?p=723618 | 与中文版同文；IBKR 2026-01 警示、2026-07 停稳定币存款、2025-12 约 50 家屏蔽 |

**复用来源池**：#8 HKTDC、#9 Chainalysis（两报告）、#11 Manila Bulletin（本篇为新增同报另一篇）、补充 Daily Tribune、Mintchain ?p=3441、KayaToday、Law.asia 中英版、399btc（署名见下方补记）。

**来源标注补记（复用的争议源）**：[399btc](https://www.399btc.com/qkl/152360.html) 该 URL 的实际抓取内容署名「**币圈界**」《菲律宾SEC官宣代币化框架就绪，沙盒试点四企入局》（2026-06-20 21:30），**非 399btc 自采**。正文所引「被允许测试加密衍生品相关服务」出自该中文二手报道，与英文多源「crypto-related products and services／Crypto Asset Intermediary」冲突且无 SEC 原文佐证，判**证据不足**；参数卡与合稿时应按「币圈界（经 399btc URL）」标注发布方，不得标为 SEC 原文或 399btc 自采。
