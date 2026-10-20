# AlphaPilot Application 1: Implemented Capabilities and Remaining Development Work | AlphaPilot 应用一功能实现情况与剩余开发工作

**Status as of 2026-10-13, against Application 1 §1.4 Core Features in `M2-Applications-Final-CRM.md`.**
**状态截至 2026-10-13，逐项对照 `M2-Applications-Final-CRM.md` 中 Application 1 的 1.4 节核心功能。**

Every row is checked against what the platform's Operation Registry actually contains — the registered operations, the AI tool manifest, the data catalogue and the declarative run samples built so far.

每一行都以平台操作注册表当前实际包含的内容为准核对——即已注册的运算、AI 工具清单、数据目录，以及至今构建的声明式运行样例。

---

## 1. Coverage by feature | 逐项功能覆盖

Three statuses are used, and they are not interchangeable: **implemented and tested offline**, **prototype or partially implemented**, **not yet implemented**.

使用三种状态，且三者不可互换：**已实现且离线测试**、**原型／部分实现**、**尚未实现**。

> **No provider credentials and no real data rows are connected at present.** Demo code is therefore never reported as a finished product. Where a row reads "algorithm implemented", it means the computation is written, unit-tested against fixtures and registered with a declared contract — not that it has yet run on real market or financial-statement data.
>
> **目前没有接入任何数据提供方凭证，也没有真实数据行。** 因此演示代码一律不报告为已完成的产品。凡标注"算法已实现"，指的是计算已编写、已针对固定样本完成单元测试、并已按声明契约注册——而不是它已经在真实行情或财报数据上运行过。

| M2 feature / M2 功能 | Delivered in this round / 本次落地 | Status / 状态 | Required before go-live / 下一步上线要求 |
|---|---|---|---|
| **1. Macro and geopolitics**<br>**1 宏观与地缘政治** | `macro_release` computing actual-versus-previous-versus-consensus surprise; BLS v1 and FRED adapters; Fed RSS update monitoring; GDELT article discovery.<br>`macro_release` 实际／前值／预期差值，BLS v1 与 FRED 适配，Fed RSS 更新，GDELT 文章发现。 | **Partially implemented**<br>**部分实现** | Real scheduled collection; properly licensed news sources; release revisions; auditable event-to-sector transmission templates. CNN and WSJ retained only through legitimate entry points.<br>实际接入定期采集、授权新闻、修订版本、事件→行业传导的可审核模板；CNN／WSJ 只保留合法入口。 |
| **2. F10 fundamentals in depth**<br>**2 F10 基本面深度解读** | Publication-date-constrained F10 reads; year-on-year indicators; cash-flow-to-profit consistency; shareholder concentration; PE and PB.<br>披露日期约束 F10、同比指标、现金流／利润一致性、股东集中、PE／PB。 | **Algorithm implemented**<br>**算法已实现** | Pull real multi-year statements and business segments; unit and version consistency checks across statements; complete pledge, lock-up expiry and announcement full text.<br>拉取真实多年财报／业务分部，财报单位及版本一致性检查，补全质押／解禁和公告正文。 |
| **3. Sector and cross-company comparison**<br>**3 行业及股票对比** | Point-in-time retrieval of sector and industry membership; breadth of advance; PE and PB comparison across 2–5 companies; like-window risk and performance.<br>同行业／板块成员时点检索、上涨广度、2–5 股财报 PE／PB 对比、同窗风险绩效。 | **Algorithm implemented**<br>**算法已实现** | Supply-chain and supply-demand data; whole-sector percentile ranks; complex accounting bases such as bank versus non-bank; same-report-type validation.<br>产业链、供需数据，行业全样本分位，复杂行业口径（银行／非银行）、同报告类型校验。 |
| **4. Technical and portfolio risk**<br>**4 技术及组合风险** | Inherited MA, RSI, MACD, ATR, drawdown and Sharpe; added portfolio concentration and correlation; third-party adapters for technical and performance computation.<br>继承 MA／RSI／MACD／ATR／回撤／Sharpe，新增组合集中度／相关性，技术／绩效第三方适配。 | **Algorithm implemented**<br>**算法已实现** | Run on real adjusted price series and cross-validate against an established library; introduce a benchmark. A risk model carrying no transaction cost must not be presented as realisable investment return.<br>使用真实复权行情与成熟包交叉校验，引入 benchmark，无交易成本的风险模型不能当真实投资收益。 |
| **5. Morning brief and closing review**<br>**5 晨报和收盘复盘** | `daily_briefing` generating a fact pack of market and announcement data, signals, and source fields.<br>`daily_briefing` 生成行情与公告事实包、信号、来源字段。 | **Partially implemented**<br>**部分实现** | Scheduler; complete news and announcement data; final LLM report generation; report history replay.<br>调度器、完整新闻和公告数据、最终 LLM 报告生成、报告历史回放。 |
| **6. Watch signals and monitoring**<br>**6 观察信号和盯盘** | Inherited price threshold, moving-average cross, RSI and volume-surge signals; added historical SMA rule research.<br>继承价格阈值、均线交叉、RSI、放量信号；新增历史 SMA 规则研究。 | **End-of-day watch implemented**<br>**日终观察已实现** | Licensed real-time quotes; intraday price updates; delivery channels; de-duplication and throttling; retry on failure. This is not tick-level real-time signalling today.<br>实时授权行情、价格分时更新、推送渠道、去重／节流、失败重试；当前不是逐笔实时信号。 |
| **7. Interactive research workbench**<br>**7 交互式研究工作台** | JSON Operation Registry; AI tool manifest; data catalogue; declarative run samples.<br>JSON Operation Registry、AI tools 清单、数据目录、声明式运行样例。 | **Partially implemented**<br>**部分实现** | React workbench; persistent user watchlist binding; backend identity and data permissions; platform-specification validation with export and import.<br>React 工作台、用户自选股持久化绑定、后端身份与数据权限、平台规格校验与导出导入。 |

**Summary: three features have their algorithm layer implemented and unit-tested (2, 3, 4); three are partially implemented with the remaining work being data access, scheduling or interface rather than computation (1, 5, 7); one delivers end-of-day observation but explicitly not real-time signalling (6).**

**小结：三项功能的算法层已实现并完成单元测试（2、3、4）；三项属部分实现，剩余工作是数据接入、调度或界面，而非计算本身（1、5、7）；一项已交付日终观察，但明确不是实时信号（6）。**

---

## 2. Executable priorities for the next 72 hours | 未来 72 小时可执行优先级

**1. Tushare data validation — highest priority.** Confirm a real token, interface permissions, and quote and financial-statement coverage. Prepare ten companies across two complete financial years with adjusted daily bars; retain download time and source for each.

**1. Tushare 数据实测（最高优先）。** 确认真实 token、接口权限、行情与财报覆盖。准备 10 家公司过去两个完整财务年度和复权日线；保留下载时间与来源。

**2. F10 and sector, end to end.** Import from the real `cd80_stock_fin_indicator`, `cd80_daily_basic` and `cd80_ci_index_member` tables and render a three-company comparison; verify financial indicators for five companies against their original disclosures.

**2. F10／行业端到端。** 从真实 `cd80_stock_fin_indicator`、`cd80_daily_basic`、`cd80_ci_index_member` 导入，显示 3 股对比；校验 5 家公司的财务指标与原披露一致。

**3. Knowledge and news.** Enable Fed RSS and BLS; take ten to twenty legitimately obtained announcement links through manual review as a test. Full text is indexed only after lawful acquisition, retaining page reference, source and content hash.

**3. 知识与新闻。** 启用 Fed RSS／BLS；将 10–20 条合法公告链接作人工核查测试。完整文本需合法获取后接入索引，保留页码、出处、内容哈希。

**4. Agent path.** Have the AI first read `catalog/ai_tools.json` and `AI_AGENT_GUIDE.md`, generate JSON, pass it through the official platform Validator, then execute under permission binding.

**4. Agent。** 让 AI 先读 `catalog/ai_tools.json` 和 `AI_AGENT_GUIDE.md`，生成 JSON，再过官方平台 Validator，最后通过权限绑定执行。

**5. Demonstration flow.** *"Compare the F10 quality and valuation of three companies → my watchlist's portfolio risk → today's related announcements → an automatic research summary."* Where announcement full text is unavailable, only title-level cues are shown.

**5. 演示流程。** "看三只股票的 F10 质量及估值差异 → 我的自选股组合风险 → 今日相关公告 → 自动研究摘要"。没有公告全文时只显示标题线索。

---

## 3. Explicitly out of scope for these three days | 明确不做的三天功能

These are not deferrals for lack of time. Each is a claim the platform is not willing to make, because making it would produce output that looks authoritative and is not.

以下各项并非因时间不足而推迟。每一项都是平台不愿意作出的声明，因为一旦作出，就会产出看起来权威、实则不然的结果。

| Not done / 不做 | Why / 原因 |
|---|---|
| **No claim of predicting price direction, an optimal entry point, or automated trading without adequate evaluation.**<br>**无充分评估就声称预测股票涨跌、最优买点、自动交易。** | A technical indicator describes past price behaviour; it is not a forecast. Presenting one as a directional call is the claim-boundary error the platform's validation exists to reject.<br>技术指标描述的是过去的价格行为，不是预测。把它当作方向判断呈现，正是平台校验机制要拒绝的结论边界错误。 |
| **No fabricated institutional consensus, and no asserted certainty about the impact of geopolitical news events.**<br>**伪造机构一致预期、地缘新闻事件的确定性影响。** | Consensus data has a source or it does not exist. Event-to-sector transmission is a hypothesis requiring an auditable template, not a number to be generated on request.<br>一致预期数据要么有来源，要么不存在。事件对行业的传导是需要可审核模板的假设，而不是一个可按需生成的数字。 |
| **No direct comparison of the same debt-to-assets threshold across banks and manufacturers.**<br>**对银行和制造业直接比较相同资产负债率阈值。** | A bank's balance sheet is not a manufacturer's balance sheet. Leverage means different things in the two, and a shared threshold produces a ranking that is arithmetically valid and financially meaningless.<br>银行的资产负债表与制造业的资产负债表不是同一回事。杠杆在两者中含义不同，共用一个阈值会产出算术上成立、金融上无意义的排序。 |
| **No bulk downloading of paywalled news full text without permission.**<br>**未经许可批量下载付费新闻全文。** | A licensing boundary, not a technical one. Titles and links with publication timestamps are held; full text enters the index only through lawful acquisition.<br>这是授权边界，而非技术边界。平台持有的是标题、链接与发布时间戳；正文只在合法获取后进入索引。 |
| **No backfilling historical periods with modern revised financial or economic data and then claiming a strategy backtest is valid.**<br>**用现代改写后的财务／经济数据回填过去并宣传策略回测有效。** | This is look-ahead bias introduced deliberately rather than by accident. A restated figure becomes available from its own publication date, not retroactively; a backtest built the other way measures the past with knowledge of the future.<br>这是有意引入的前视偏差，而非无意造成。重述后的数字自其自身披露日起可用，不追溯生效；反向构建的回测是在用对未来的知识衡量过去。 |

---

## 4. What "implemented" means in this document | 本文档中"已实现"的含义

Because this status table will be read alongside the platform specification and the final report, the distinction is stated once and held throughout:

由于本状态表将与平台规范及最终报告一同被阅读，此处一次性说明区别，并全文保持一致：

**Algorithm implemented** — the computation is written in real code, declared as a registered operation with its parameter schema, required data basis, preconditions, emitted basis labels and failure modes, and tested against fixtures offline. What has not happened is execution on real provider data at scale.

**算法已实现** —— 计算以真实代码编写，作为已注册运算声明其参数规范、所需数据口径、前提条件、输出口径标签与失效情形，并已针对固定样本完成离线测试。尚未发生的是在真实提供方数据上的规模化执行。

**Partially implemented** — the computational or data-model layer exists; what is missing is one of scheduled collection, licensed data access, interface, or identity and permission handling. In every row above, the missing part is named explicitly.

**部分实现** —— 计算层或数据模型层已存在；缺失的是定期采集、授权数据接入、界面，或身份与权限处理之一。上表每一行都已明确指出缺失的是哪一部分。

**End-of-day watch implemented** — signals evaluate correctly against settled daily data. Intraday and tick-level evaluation is a different requirement and is not claimed.

**日终观察已实现** —— 信号能够在已收市的日频数据上正确求值。盘中与逐笔求值是另一项要求，本平台不作此声明。

The honest reading of this table is that the algorithm layer of Application 1 is substantially built and the binding constraint on the remaining work is data access, not computation. That is why Tushare validation is the first priority rather than the last.

对本表的诚实解读是：应用一的算法层已基本构建完成，剩余工作的约束在数据接入，而不在计算。这正是 Tushare 数据实测被列为第一优先而非最后一项的原因。
