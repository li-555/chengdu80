# SuitabilityFlow — CRM Functions & Blocks Integration / CRM 函数与 Blocks 平台对接

**Team HKU · Reference implementation v0.3 / 参考实现版本 v0.3**

## 1. What is included? / 包含什么？

- `suitabilityflow_core.py`: deterministic domain functions, no server, no database, no customer API, no real transaction / 确定性领域计算函数，不含服务器、数据库、客户数据接口或真实交易。
- `suitabilityflow_tests/test_core.py`: 15 reproducible offline tests / 15 项可复现离线测试。
- `SuitabilityFlow_V5_Operation_Contracts.json` (previously delivered): conceptual input/output contracts for agent selection / 之前提供的概念性 AI 工具输入输出契约。
- `FinWeave_Premium_Bilingual_V6.html`: frontend prototype with bilingual rendering, synthetic records, no backend integration / 中英双语单文件交互原型，数据为虚构，尚未接后端。

**No automatic integration / 不会自动接入：** The source code and contracts do not register themselves in the official Blocks Operation Registry. Baseline developers must adapt them to the current version of the platform's machine-readable specification, security model and Data Catalogue / 必须由平台开发者按正式规范完成适配和注册。

## 2. Function inventory / 函数清单

| Python function | Suggested operation / 建议工具 ID | Role / 职责 | Status / 状态 |
|---|---|---|---|
| `evaluate_suitability` | `suitability.evaluate_rules` | S01–S08 hard gates + S09–S10 review checks / 适当性强制门槛和复核条件 | Reference implemented / 已实现参考逻辑 |
| `rank_eligible_products` | `suitability.rank_eligible` | Rank candidates only after mandatory gates / 必要条件通过后排序 | Reference implemented / 已实现 |
| `suitability_matrix` | UI helper / UI 辅助 | Compute N×M statuses and reason codes / 批量矩阵 | Reference implemented / 已实现 |
| `client_360` | `crm.get_client_profile` | Join permitted client, opportunity and activity records / 关联授权客户、商机、时间线 | Reference implemented / 已实现 |
| `pipeline_snapshot` | `crm.dashboard_snapshot` (partial) | Stage counts and pipeline value / 阶段存量和金额 | Partial reference / 部分实现；完整驾驶舱还需任务及合规数据 |
| `advance_opportunity` | `crm.advance_opportunity` | Validate one-step stage transition, evidence and human approval / 阶段门槛 | Reference implemented / 已实现 |
| `prioritise_actions` | `crm.prioritize_actions` | Explainable capacity-constrained action ranking / 容量约束回访排序 | Reference implemented / 已实现 |
| `product_catalog_search` | `product.search_catalog` | Search only institution-approved product metadata / 查询经机构批准的目录 | Reference implemented / 已实现 |
| `cited_product_answer` | `product.answer_cited_question` (reference stub) | Return only pre-reviewed cited facts / 仅返回预审证据片段 | Basic deterministic implementation / 确定性简化实现；非真实 RAG |
| `append_audit_event` | `compliance.record_event` | Emit a typed audit event to an in-memory list / 生成会话审计事件 | Demo only / 仅演示；不具防篡改性 |
| `project_portfolio_concentration` | `portfolio.project_concentration` | Before/after issuer-weight HHI & concentration review / 配置前后 HHI 集中度 | New reference function / 新增数学参考函数；原契约仍属路线图 |
| **Not implemented / 未实现** | `crm.outcome_uplift_estimator` | Causal sales uplift learning / 因果增量销售预测 | Roadmap only / 路线图，不应包装成现成功能 |

**Key boundary / 关键边界：** These functions are pure domain logic. Persistent records, authenticated permissions, alerts, customer messaging, approved-product synchronization, PDF RAG, CRM workflow orchestration and trade execution are *not* included / 真实客户权限、持久化、消息发送、机构审批、PDF RAG 和交易执行均不包含在内。

## 3. Why SuitabilityFlow is not a generic CRM / 与普通 CRM 的不同

A normal CRM primarily tracks contacts, meetings, opportunities and sales stages. SuitabilityFlow makes the workflow **financial-product-specific**: issuer/product disclosures, client risk assessment, investor qualifications, lock-up and liquidity constraints, signed consent, suitability gate before a proposal, human exception review, protected audit history and macro/issuer-risk servicing triggers / 普通 CRM 管线索和客户；SuitabilityFlow 额外把金融产品风险等级、投资者资格、期限流动性、适当性判断、披露与审批证据连入整个销售服务流程。

**Do not promise superior returns, approved recommendations or higher conversion / 不承诺收益、自动认可的投资推荐或提高成交率。**

## 4. Deterministic rule precedence / 规则优先级

1. Load permissioned client and approved product snapshots with timestamps / 加载获授权且有时间戳的客户及已批准产品资料。
2. Run S01–S08 hard gates: missing inputs become `unknown`; explicit failures become `block` / 执行硬性门槛；资料缺失时为 unknown，明确不通过为 block。
3. If any hard gate fails or is unknown, no product recommendation ranking may be presented / 硬性条件未通过时不得排名推荐。
4. Run S09–S10 review-only checks; `review` means a human decision remains outstanding / 审查项不等于已经批准。
5. Rank only eligible candidates with explainable, versioned weights (30/25/20/15/10 demo; **not legal thresholds**) / 合格集合内可解释打分，权重只是产品假设。
6. Record inputs, rule version, reasons, cited product document, actor and decision / 留存输入、规则版本、原因、出处、人员和结果。

**Potential confusion / 易混点：** An eligible `review` result may be shown in a comparison with a review badge; it must NOT be sent to customers as an approved recommendation before the appropriate sign-off / 待复核产品可供内部比较，不得自动对外推介。

## 5. Data required / 数据绑定需求

**Client / 客户**: ID; profile/consent validity; risk grade; qualified-investor status; investment horizon; liquidity need; investable capital; objective; proposed allocation; last-updated fields.

**Product / 产品**: ID; institution approval; risk grade; investor eligibility; lock-up; liquidity supply; minimum ticket; costs; objective; issuer; original fact sheet document ID/version/citation.

**Opportunity / 商机**: ID; client/product; current stage; assigned advisor; amount; next contact; linked suitability result; disclosure; approval record.

**Audit / 审计**: actor and role; event time; rule version; decision and reason codes; input snapshot; original document references; review state.

Neither competition Tushare market data nor the 37 financial tables contains the institution's own permissioned CRM client records. Use **synthetic data for demo**, or separately bind customer spreadsheets supplied by an authorized operator / Tushare 与比赛市场数据库不包含真实 CRM 客户资料；演示需使用虚构数据，正式使用应由机构授权导入。

## 6. Blocks integration / 开发同事接入步骤

1. Unpack AlphaPilot V4 and RegGuard V1 *once* and deduplicate shared financial functions; do not copy the prototype runtimes into Blocks / 两个金融包只提取算法，避免重造平台 Runtime。
2. Register CRM functions through the **official** Platform Operation Registry; use names above as mappings, not claims of official identifiers / 通过正式注册表绑定，本文 ID 是建议名。
3. Adapt `client_id` and `product_id` to actual catalog bindings. `evaluate_suitability` itself accepts `Client` and `Product` objects; the service adapter must fetch typed, permission-checked snapshots / 标识符需先经授权取数，再转换为对象。
4. Attach rule-version, as-of timestamp, required/optional fields, result status, source references and human-review controls to each operation schema / 每个操作应声明规则版本、时点、数据字段、结果码、证据和人工审批条件。
5. Validator must reject unsupported operations and unauthorized cross-user access; AI chooses from listed operations but NEVER edits mandatory suitability outcomes / 校验器拒绝越权操作；LLM 不能改写合规结果。
6. Use Blocks persistent workflow/audit services for official evidence; in-memory examples here are *not* immutable proof / 正式审计留痕使用平台服务，不使用内存列表冒充防篡改证据。
7. Bind UI views to operation outputs only after successful integration; retain demo/real/unknown labels / 接入完成后再替换界面模拟值。

## 7. Acceptance tests / 验收建议

- All 10 rule IDs are returned with bilingual descriptions and reason codes / 10 条规则均给出中英解释和原因码。
- Hard-block and unknown cases are never ranked as recommended / 阻断及资料缺失不可自动推荐。
- Review cases cannot silently become approved sales / 待复核不可自动成交。
- Opportunity approval requires durable suitability/disclosure/sign-off records / 审批前必须有适当性、披露、人工签审记录。
- 10×10 demo matrix returns 100 independently evaluable pairs and is scrollable on a 1366px screen / 100 格矩阵结果和分辨率可验。
- Product facts are source-linked and never fabricated / 产品说明必须有出处。
- Action rankings identify input weights and advisor capacity; no asserted sales propensity / 回访排序显示权重和容量，不冒充成交概率。
- No customer PII in exported application documents / 导出应用不包含客户隐私数据。

## 8. Operation Contracts explained / 什么是 Operation Contracts？

The prior `SuitabilityFlow_V5_Operation_Contracts.json` is a **proposed tool manifest**, not a Python program, not an app file, and not the official Blocks schema / 它是建议的工具描述清单，不是函数代码、不是应用文件，也不是 Blocks 官方规范。

Each contract says **tool ID, input, output, prerequisites and availability** so an AI generator and validator can discover what is allowed. It is useful if Blocks needs an external tool catalog. If the platform already generates machine-readable operation specifications from Python definitions, **do not maintain a redundant competing manifest**—convert the content into the platform's authoritative registry / 若 Blocks 已从已注册代码自动导出 Schema，应将契约内容融入统一注册表，而非维护第二套标准。

The original contract contains **11 operations**: nine prototype/demonstration entries and two roadmap entries (`portfolio.project_concentration`, `crm.outcome_uplift_estimator`). This reference package implements concentration math, but no official operation is registered; uplift remains unsupported / 原契约共有 11 项，其中 9 项演示级接口，2 项路线图。此包新增集中度纯函数，但未注册平台；提升度模型仍未实现。
