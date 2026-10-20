# Three Flagship Application Proposals | 三个旗舰应用方案

- Team / 团队：Team HKU
- Platform / 平台：FinWeave（working name / 暂定名称，提交前请确认）

> Milestone 2 — Day 2, 24:00. Submit all three application proposals in this file through the Submission Portal. They will be locked and published to all teams after the deadline.
>
> 第二阶段——第二天 24:00 截止。将三个应用方案填写在本文件中，通过提交系统上传；截止后锁定，并统一向所有团队公开。

All three applications are designed as portable, specification-compliant application documents: they declare data requirements, parameters, computation/AI steps, schedules and interactive views; the platform validates them, binds them to authorised data, executes them, records results and supports single-file export/import. The definitions below commit to the products and user value, not to any one data vendor, AI model or algorithm.

三个应用均按平台统一规范定义为可移植的应用文档：声明数据需求、参数、计算及 AI 步骤、调度和交互界面；平台负责校验、授权数据绑定、执行、记录结果及单文件导入导出。以下锁定产品及用户价值，不锁定特定数据供应商、模型或算法。

## Application 1 | 应用 1

### 1.1 Application Name | 应用名称

**AlphaPilot — AI Investment Research & Market Watch / AlphaPilot——AI 专业投资研究与市场雷达**

### 1.2 Financial Problem | 金融问题

**EN:** Experienced self-directed investors face fragmented information across macroeconomic releases, geopolitical events, company disclosures, financial statements, industry developments and price movements. Generic news feeds explain what happened but rarely connect it consistently to a user's own watchlist, investment thesis and risk limits. Professional research platforms can be expensive and still require substantial manual synthesis. The application addresses the recurring need for evidence-based, personalised investment *research and monitoring* rather than another one-off chatbot answer.

**中文：** 有一定投资经验的个人投资者，需要同时追踪宏观经济数据、地缘政治事件、上市公司公告、财报、行业变化和股价走势，但这些信息分散在不同来源。通用财经新闻通常只解释“发生了什么”，很难持续回答“这对我关注的公司、投资逻辑和风险敞口有什么影响”。专业终端成本较高，研究整合仍依赖大量人工。本应用解决的是**个性化、持续运行且有证据支持的投资研究与监控**需求，而非一次性聊天问答。

### 1.3 Target Users | 目标用户

**EN:** Primary: self-directed retail investors with prior experience in equities/ETFs and an established watchlist who want analyst-grade research workflows without building software. Secondary: independent financial researchers, investment clubs, and licensed advisers using the application as a research-support tool. The initial demonstrable scope is selected A-share equities plus major US macroeconomic events, with other markets supported as authorised data become available.

**中文：** 主要用户是已有股票／ETF 投资经验、具备自选股和基本分析能力、希望得到接近专业研究工作流的自主投资者。次要用户包括独立研究员、投资社群及将本应用作为辅助研究工具的持牌顾问。首个可演示版本聚焦**部分 A 股标的及美国主要宏观事件**；其他市场随获授权的数据源扩展。

### 1.4 Core Features | 核心功能

**EN:**

1. **Macro and geopolitical intelligence:** follow nonfarm payrolls, CPI, FOMC decisions, interest rates and major geopolitical/policy events. Distinguish official data, market commentary and hypotheses; where licensed consensus forecasts exist, compare actual/prior/consensus, otherwise clearly label unavailable comparisons. Summarise plausible transmission channels into rates, currencies, sectors and watched stocks, with source links and timestamps. Sources prioritise official agencies and authorised news feeds; CNN, The Wall Street Journal and other premium publishers are supported only through permitted feeds/licences or outbound article links, not unauthorised paywall scraping.
2. **Fundamentals and F10 company cards:** digest business segments, revenue/profit trends, cash-flow quality, leverage, valuation ratios, shareholder changes, pledges, share-unlock schedules and material filings. Display reporting periods, accounting units and document evidence; flag missing data rather than invent it.
3. **Industry and peer research:** show industry drivers, supply-chain or policy exposure and peer benchmarks. Compare 2–5 stocks on normalised profitability, growth, valuation, leverage, volatility and selected technical indicators, with configurable weighting and transparent metrics.
4. **Technical and portfolio analytics:** calculate MA, RSI, MACD, ATR, returns, drawdowns, volatility and watchlist concentration/correlation from suitably adjusted price data. Explain *what the indicators measure* and conflicting signals; do not present a pattern as a guaranteed price prediction.
5. **Daily research workflow:** scheduled pre-market briefings and post-market reviews covering overnight events, filings, watchlist movers, unusual volume/volatility and changes to a saved investment thesis. Each run is versioned and reproducible against its data timestamp.
6. **Market watch and configurable signals:** track user-selected price thresholds, moving-average crosses, large moves, volume spikes and disclosure triggers. Deliver watchlist alerts and user-defined potential entry/exit *signals* with indicator rationale and delay/freshness labels. Market-data latency depends on the connected provider; the initial product does not execute trades or promise tick-level real-time feeds.
7. **Interactive research workspace:** editable parameters and scenarios, side-by-side comparisons, drill-down charts, citations and a persistent personal watchlist. Export the application definition without transferring the user's holdings or credentials.

**中文：**

1. **宏观与地缘政治智能解读：** 跟踪美国非农就业、CPI、美联储议息、利率变化和重大地缘政治／政策事件。区分官方数据、媒体观点及模型推断；在获得合法预期数据时比较“实际值／前值／预期值”，否则明确标注数据缺口。分析事件可能如何通过利率、汇率、行业传导至自选股，附来源和时间。优先接入官方发布与获授权的财经资讯；CNN、《华尔街日报》等媒体仅通过合规订阅、授权接口或原文链接使用，不绕过付费墙批量抓取。
2. **企业基本面与 F10 深度解读：** 汇总主营业务、营收与利润趋势、经营现金流质量、杠杆、估值、股东变化、股权质押、限售解禁及重大公告。标注报告期、单位和原始证据，缺失数据不得编造。
3. **行业研究与股票横向比较：** 分析行业驱动因素、产业链及政策敞口；支持 2–5 只股票的盈利能力、增长、估值、负债、波动和技术指标并列比较，权重可调、计算可查。
4. **技术与组合风险分析：** 基于适当复权的行情计算均线、RSI、MACD、ATR、收益率、回撤、波动率及自选股相关性／集中度；解释指标含义和相互矛盾的信号，不将技术形态宣传为确定性预测。
5. **早盘分析与每日复盘：** 按交易日自动输出隔夜要闻、重大公告、自选股异动和成交量变化，记录原有投资逻辑是否受到新信息挑战；每次报告保留数据时间戳和版本。
6. **盯盘与自定义买卖观察信号：** 设置目标价、跌破／突破阈值、均线交叉、放量异动及公告提醒；生成有依据的潜在入场／离场观察信号，标明行情延迟及局限。首版不自动下单，也不承诺逐笔实时行情。
7. **交互式研究工作台：** 可调整参数、比较情景、查看图表和原文证据，持久管理自选股；分享应用定义时不携带个人持仓数据或凭据。

### 1.5 Innovation & Value | 创新与价值

**EN:** AlphaPilot connects **event → sector exposure → company fundamentals → market evidence → watchlist-specific action to investigate**, rather than issuing generic AI commentary. Financial calculations are performed by auditable operations; the LLM synthesises evidence and separates facts, interpretation and uncertainty. Repeatable morning/close runs, user-defined signals, comparability checks and cited sources provide a paid-research-style workflow while the reusable application document remains portable across users and data sources. It is decision support, not autonomous investment management or a promise of returns.

**中文：** AlphaPilot 的创新不在“AI 会讲股市”，而在把**事件→行业传导→公司基本面→行情证据→个人自选股待研究事项**串成可复查的工作流。计算由可审计的金融函数完成，LLM 负责证据综合，并区分事实、解释与不确定性。自动晨报／复盘、个人化预警、横向可比性检查和出处追溯，构成接近付费研究服务的体验；应用仍可作为不含用户数据的文档移植复用。它提供决策支持，不承诺投资收益，也不自动管理账户。

### 1.6 User Attraction | 用户吸引力

**EN:** A user can start by uploading an existing watchlist and immediately receive a structured comparison and evidence-linked daily briefing. Clear differentiation from generic financial chatbots comes from persistent monitoring, consistent calculations, source transparency and alerts tied to personal criteria. The freemium-to-premium potential lies in more watchlists, scheduled intelligence, deeper peer analysis and legitimately licensed data—not unsubstantiated “profitable signals.” Sharing a ready-to-run watchlist-research application encourages adoption while the recipient binds their own data.

**中文：** 用户导入已有自选股即可获得结构化比较和附出处的每日简报，无需重新建立研究流程。相较普通财经聊天机器人，持续盯盘、口径一致的计算、可核查证据和个性化提醒更容易形成日常使用习惯。可持续的付费价值来自更多自选股、定时研究、更深的同业比较及合法授权的数据服务，而非无法验证的“稳赚信号”。应用可分享给其他投资者，并由接收者绑定自己的数据。

## Application 2 | 应用 2

### 2.1 Application Name | 应用名称

**RegGuard — AI Corporate Risk & Regulatory Intelligence / RegGuard——AI 企业风险与监管情报雷达**

### 2.2 Financial Problem | 金融问题

**EN:** Analysts, risk and compliance officers, auditors and corporate due-diligence teams must examine large volumes of financial statements, announcements, ownership disclosures, enforcement notices and regulatory changes. Important red flags may be scattered across documents and time periods. Manual checks are slow, inconsistent and difficult to audit; a simple summarisation chatbot cannot reliably distinguish documented findings from suspicions. The application addresses continuous, evidence-based corporate risk surveillance and regulatory change assessment, with human review of serious alerts.

**中文：** 金融机构的研究、风控、合规、审计及企业尽调团队必须持续阅读大量财报、公告、股权披露、监管处罚与法规更新。重要风险信号可能分散在不同文件和年度中，人工核查耗时、标准不一且难以审计；单纯摘要型聊天机器人又难以区分已证实事实和未经证实的怀疑。本应用解决的是**证据驱动、持续运行、可复核的企业风险监控与监管变化评估**，重大预警由专业人员复核。

### 2.3 Target Users | 目标用户

**EN:** Primary: credit/equity research teams, bank and asset-manager risk/compliance staff, investment due-diligence teams and internal auditors. Secondary: corporate legal/governance teams and professional advisers. Users work with authorised public disclosures and their organisation's access-controlled internal datasets; the initial demonstrable scope is listed-company disclosures and official regulatory sources in selected jurisdictions.

**中文：** 主要面向银行及资管机构风控／合规人员、股票与信用研究员、投前尽调团队和内部审计人员；次要面向企业法务、公司治理与专业咨询团队。数据来自授权使用的公开披露和机构内部受控数据；首个可演示版本聚焦选定市场的上市公司公告及官方监管来源。

### 2.4 Core Features | 核心功能

**EN:**

1. **Financial statement and audit interpretation:** extract and compare key items across annual/quarterly reports and notes: revenue, net income, operating cash flow, receivables, inventory, debt, guarantees, related-party transactions and auditor opinions. Explain significant movements and reconcile the evidence to original filings and reporting periods.
2. **Accounting anomalies and potential misconduct indicators:** apply transparent rules to cash-flow/earnings divergence, abnormal receivables growth, related-party dependence, auditor changes, restatements and unusual guarantees/pledges. Optionally add unsupervised anomaly scores; labelled supervised fraud models only when suitable, legally usable training data and validation exist. Results are **review flags, not allegations or proof of fraud**.
3. **Controller and management legal-risk due diligence:** build authorised entity/beneficial-owner relationships and search official public court judgments, enforcement decisions, disciplinary notices and sanctions lists where available. Reconcile names using additional identifiers, show case status and jurisdiction, distinguish allegations/investigations from final decisions, and allow manual confirmation before escalation.
4. **Regulatory horizon scanning:** monitor updates from securities regulators, exchanges and relevant authorities. Categorise policy changes by topic, affected entities, effective date and potential compliance tasks; link back to official text. A tracked change in policy is not automatically a legal conclusion.
5. **Event-driven early-warning dashboard:** configure thresholds for cash-flow quality, leverage, share pledges, enforcement events, material related-party transactions and disclosures; produce severity-ranked alerts, watchlists, daily/weekly digests and cross-period comparisons.
6. **Evidence-based investigation workflow:** for every alert show a structured risk description, relevant calculations, primary-source excerpts, dates, confidence/coverage limitations and a human-review status. Save decisions, model/rule versions and run histories for reproducibility.
7. **Enterprise-safe operation:** internal datasets remain inside the organisation's authorised environment; generation uses field metadata without exposing sensitive rows. Optional LLM analysis uses only approved model endpoints and access policies. Apps are portable without embedding internal files or credentials.

**中文：**

1. **财报与审计意见解读：** 提取并跨期对比营收、净利润、经营现金流、应收账款、存货、有息负债、担保、关联交易以及审计意见，解释重大变化，并追溯至原始报表、附注和报告期。
2. **财务异常与潜在舞弊线索：** 针对“利润与现金流背离”“应收异常增长”“关联方依赖”“审计师变更”“会计差错更正”“异常担保／质押”等运行透明规则；可叠加无监督异常评分。只有存在适当的合法标签数据且经过验证时，才增加监督式舞弊模型。输出的是**需要复核的风险线索，而非舞弊事实认定**。
3. **实控人、董监高与关联主体法律风险：** 在合法授权范围内构建实际控制、股权及关联关系，核查官方公开裁判文书、行政处罚、交易所纪律处分和制裁名单等。结合身份标识避免同名误匹配，标注司法管辖区及案件状态，严格区分调查、指控和生效裁决；重大线索先人工确认再升级。
4. **监管风向与合规变化追踪：** 自动跟踪证券监管机构、交易所等权威来源，按议题、适用主体、生效时间和潜在合规任务分类，附原文链接。政策更新的自动解读不直接替代律师或合规人员判断。
5. **事件驱动预警：** 用户自定义现金流质量、负债、股权质押、处罚事件、重大关联交易和信息披露阈值，输出分级预警、自选公司监控、每日／每周摘要及跨期趋势。
6. **可审计调查工作流：** 每条风险信号包含分析结论、计算过程、原文证据、日期、置信局限和人工复核状态，保留审查意见、模型／规则版本及运行历史。
7. **机构数据安全：** 内部数据留在机构授权环境，生成阶段只暴露数据字段元信息，LLM 分析遵守获批准的接口和数据权限。应用可分享，但不包含机构内部文件或凭据。

### 2.5 Innovation & Value | 创新与价值

**EN:** RegGuard combines three traditionally separate workflows—**quantitative forensic screening, document-grounded investigation and regulatory change monitoring**—in one repeatable application. Instead of a black-box “fraud probability,” it delivers explainable indicators and a traceable evidence chain: rule/model → affected company → filing section or official decision → reviewer outcome. Cross-company templates can be reused without exposing sensitive organisational data, and every run is logged. This reduces repetitive first-pass due-diligence effort while preserving professional accountability.

**中文：** RegGuard 把传统上分散的**财务法证筛查、基于文档证据的尽调、监管规则变化监控**整合为可持续运行的一套应用。其核心不是一个无法解释的“欺诈概率”，而是清晰的证据链：规则／模型→受影响公司→财报段落或官方处罚→复核意见。相同尽调模板可以跨团队复用且不泄漏机构数据，每次运行可留痕，从而减少重复初筛工作，同时保留专业人员的审查责任。

### 2.6 User Attraction | 用户吸引力

**EN:** Teams can import a company list or a filing dataset, receive an initial evidence-linked red-flag report and keep monitoring new disclosures and official actions without rebuilding the process. Inspectable calculations, original-source references, review status and exportable audit trails make it materially more useful to institutional users than a generic LLM summary. Reusable cross-company risk templates create a growing library of internal controls and encourage wider platform adoption.

**中文：** 团队导入公司名单或公告／财务数据集，就能获得附证据的首轮风险扫描，并在后续披露及监管事件发生时持续跟踪。可检查的计算、官方来源、人工复核状态和可导出的审计轨迹，使其比普通 LLM 摘要更适用于金融机构。跨公司复用的风险模板逐步沉淀为机构内部的监控工具库，促进平台在不同部门扩展。

## Application 3 | 应用 3

### 3.1 Application Name | 应用名称

**SuitabilityFlow — AI Financial Product Sales & Client Relationship CRM / SuitabilityFlow——AI 金融产品销售与客户关系管理系统**

### 3.2 Financial Problem | 金融问题

**EN:** Financial product distributors and wealth-management teams manage clients, leads, product enquiries, opportunities, follow-ups, investment suitability checks and compliance records across disconnected spreadsheets and systems. Conventional CRMs can track sales activity but rarely connect it to client risk tolerance, product eligibility, approved product information and auditable disclosures. This fragmentation causes missed follow-ups, inefficient client servicing and risks of unsuitable product recommendations. SuitabilityFlow provides an integrated, permission-controlled **sales-and-service CRM with built-in financial suitability and compliance workflows**, helping professionals serve clients consistently without replacing licensed judgement.

**中文：** 金融产品销售及财富管理团队通常把客户档案、潜在客户线索、产品咨询、销售商机、回访任务、投资者适当性检查和合规材料分散保存在表格与多个系统中。传统 CRM 虽能记录销售进展，却往往无法把客户风险承受能力、产品适销条件、合规产品资料和风险揭示记录贯通起来，容易造成客户跟进遗漏、服务效率低和产品不适配风险。本应用提供一套具有权限控制的**金融产品销售与客户服务 CRM，并内置投资者适当性及合规工作流**，辅助专业人员高效服务客户，不替代持牌人员的专业判断。

### 3.3 Target Users | 目标用户

**EN:** Primary users are authorised relationship managers, wealth-management advisers, licensed financial-product sales staff and sales-team leaders at banks, brokerages, asset managers and other financial institutions. Compliance supervisors and client-service staff are secondary users. The application operates on an organisation's authorised customer records and approved product catalogue; it does not scrape personal contacts or perform unsolicited mass marketing.

**中文：** 主要面向银行、证券公司、资管机构等合规金融机构的客户经理、财富管理顾问、持牌金融产品销售人员及销售主管；合规审查人员与客户服务团队是次要用户。应用仅使用机构**已授权的客户资料及经过批准的金融产品目录**，不抓取未经同意的个人联系方式，也不执行未经授权的批量营销。

### 3.4 Core Features | 核心功能

**EN:**

1. **Permissioned client 360 and segmentation:** import or bind authorised CSV/XLSX client records covering contact/service status, investment experience, documented risk profile, goals, investment horizon, liquidity needs, holdings where permitted and consent metadata. Flag incomplete or stale fields; group clients by institution-defined service criteria, with role-based access.
2. **Lead, opportunity and sales pipeline management:** record consented enquiries, lead sources, assigned relationship managers, product interests, opportunity stages, expected follow-up dates and outcomes. Show a stage-based pipeline, overdue tasks, conversion metrics and reasons for lost opportunities; create reminders without requiring automatic outbound messaging.
3. **Financial-product suitability and eligibility checks:** compare a client's recorded risk tolerance, objectives, time horizon, liquidity requirements and regulatory restrictions with the product's approved risk rating, investor-qualification requirements, lock-up period and concentration limits. Explain each pass/fail condition and send exceptions for human review; approved rules, not an unconstrained LLM, determine checks.
4. **AI-assisted product knowledge and client service:** search the institution's approved product brochures, fact sheets and risk disclosures. Generate source-linked explanations of fees, returns scenarios, redemption terms and material risks; assist staff in drafting meeting summaries and follow-up messages for review, while refusing to fabricate product terms or present drafts as approved advice.
5. **Lifecycle follow-ups and retention:** schedule suitability reassessments, maturity/renewal reviews, client meetings, periodic service calls and document-update reminders; relate tasks to product events and client status. Keep human control of actual client communications and any product transaction.
6. **Compliance records and auditability:** log customer consent, disclosure delivery, suitability assessments, recommendation rationale, conflicts of interest, supervisory approval and relevant service interactions. Surface missing documentation and overdue compliance actions; preserve actor, timestamp, rule version and review outcome.
7. **Sales and supervision dashboard:** display pipeline conversion, active opportunities, client coverage, overdue follow-ups, product-interest patterns and outstanding suitability exceptions. Support configurable filters, side-by-side service scenarios and reusable CRM templates that can be exported without customer data or credentials.

**中文：**

1. **客户 360 画像与分层管理：** 导入或绑定机构获授权的 CSV／Excel 客户资料，整合联系及服务状态、投资经验、已记录的风险测评、投资目标、投资期限、流动性需求、授权范围内的持仓及客户同意记录；识别缺失或过期资料，按照机构批准的规则进行客户分层，并设置角色权限。
2. **销售线索与商机漏斗：** 管理经客户同意取得的咨询线索、线索来源、客户经理分配、感兴趣的金融产品、商机阶段、下一次跟进时间和成交／流失结果；展示销售漏斗、逾期任务、转化率和流失原因，支持提醒但不依赖自动对外群发。
3. **金融产品适当性及资格核查：** 将客户记录中的风险承受能力、投资目标、期限、流动性需求及监管限制，与机构批准的产品风险等级、合格投资者要求、封闭期和集中度限制进行匹配；清晰说明符合或不符合的条件，并将例外提交人工复核。匹配规则由机构批准，而不是由大模型自由决定。
4. **AI 产品知识库与客户服务辅助：** 检索经过批准的产品说明书、产品要素表和风险揭示文件，附来源解释费用、收益情景、赎回条款与重要风险；辅助生成面谈纪要及待审核的回访话术，不编造产品条款，也不将 AI 草稿直接视为已批准投资建议。
5. **客户生命周期与持续跟进：** 围绕风险测评复核、产品到期／续约、客户会面、定期回访与资料更新创建定时任务，并将任务关联到客户状态及产品事件；客户联系与实际交易仍由人工或机构授权系统完成。
6. **销售合规和审计留痕：** 记录客户授权、风险揭示、适当性核查、推荐理由、利益冲突披露、主管批准及重要服务互动；提示资料缺失和超期事项，保留操作人员、时间戳、规则版本及复核结果。
7. **销售与主管驾驶舱：** 展示线索转化率、活跃商机、客户覆盖情况、待办及逾期回访、产品关注分布与未处理的适当性例外；支持筛选、服务情景对比及模板复用，导出的应用文件不包含客户个人信息或机构凭据。

### 3.5 Innovation & Value | 创新与价值

**EN:** SuitabilityFlow is more than a generic contact database: it links **client intelligence → opportunity management → product suitability → evidence-grounded AI assistance → compliant follow-up → auditable outcomes** in one repeatable financial workflow. Deterministic eligibility rules keep decisions explainable, while AI reduces the time spent reading product documents and preparing service notes. The same specification-compliant application can be imported into different institutions and bound to their own permissioned customer data, product catalogues and local compliance rules. Its value lies in more consistent client servicing, reduced manual administration and better supervision—not autonomous sales or promises of conversion gains.

**中文：** SuitabilityFlow 不只是普通联系人数据库，而是将**客户画像→销售商机管理→金融产品适当性核查→基于证据的 AI 服务辅助→合规回访→全过程审计**整合为可重复运行的金融服务工作流。确定性规则保障产品适配判断透明可查，AI 则减少阅读产品文件与整理服务记录的人工工作量。应用可以通过统一规范在不同机构之间复用，并由接收方绑定自身获授权的客户资料、产品目录及当地合规规则。其价值是提升客户服务一致性、降低重复行政工作并加强合规监督，而非自动化推销或承诺提高成交率。

### 3.6 User Attraction | 用户吸引力

**EN:** A relationship manager can upload an approved customer list and product catalogue, obtain a client-service dashboard, organise active opportunities, identify follow-ups due this week, check whether a proposed product satisfies recorded client constraints, and prepare a cited product explanation for supervisor review. Team leaders gain a clear view of pipeline bottlenecks and compliance exceptions without a separate custom software project. An immediately useful sales workflow, configurable to each institution, makes the platform attractive to financial teams that want both efficiency and governance.

**中文：** 客户经理导入已授权的客户名单和产品目录后，即可查看客户服务看板、管理活跃商机、识别本周应完成的回访、核查目标产品是否满足客户既定条件，并生成附产品条款依据、待主管审核的客户说明。销售主管可以同时看到漏斗瓶颈和合规异常，而无需额外定制一整套软件。**可立即使用、按机构规则配置、兼顾销售效率与合规治理**的 CRM 工作流，将成为该应用吸引金融机构采用平台的核心理由。
