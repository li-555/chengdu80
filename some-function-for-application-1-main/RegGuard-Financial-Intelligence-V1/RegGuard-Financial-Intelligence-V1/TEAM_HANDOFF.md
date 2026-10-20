# Team HKU — 给 Blocks 核心开发者的 RegGuard 对接说明

## 请优先对接的五个文件

1. `catalog/regguard_ai_tools.json`：**18 个受控金融专业 Operation** 的元数据，含参数签名、用途、限制；不是 Blocks 官方 schema。
2. `catalog/regguard_rulebook.csv`：**R1–R12** 每条一行，说明计算方法、阈值、为什么重要、复核优先级和自动化状态。
3. `catalog/competition_tables.json`：比赛 37 表 / 856 字段的**目录元数据**，不含数据本身。
4. `catalog/knowledge_cards.json`：金融方法、合规解释和公式适用边界的知识卡。
5. `regguard/registry.py`：Python 函数白名单，供适配 Blocks Runtime（禁止调用用户提供的任意代码字符串）。

## 平台数据绑定契约

财务：`balance`、`income`、`cashflow` 必须按相同证券、年度报告期、**有效披露日期**对齐；以业务提供方源字段为准，不要用 LLM 猜科目。

公告：比赛原始字段 `announcement_date,ticker,announcement_title,url` → 显式适配器归一化为 `ann_date,ts_code,title,url`。公告标题只能支持标题级初筛；全文分析需要另有授权 PDF / 摘录。

审计：`fina_audit` 的 `audit_result`, `audit_agency`, `ann_date`, `end_date`；无权限或无数据时标 `not_evaluable`，不回退成无保留意见。

质押：`pledge_ratio` 公司整体百分比；实控人质押需额外主体级持股及质押明细，不得用公司百分比冒充。

司法/监管：只消费机构合法获得的授权文档或人工核查结果；采集网页、验证码和访问控制由平台按合规要求处理，金融模块不提供绕过机制。

## Runtime 与 API 的界线

- `regguard.registry.run_named_operation(id, **kwargs)` 只接受白名单中已注册的操作。Blocks 应注册或转译相同能力，不再部署独立的第二套 Runtime。
- `regguard/workflow.py` SQLite 仅本地示例。真正用户身份、权限、访问隔离、任务调度、审计存储和可靠执行应由 Blocks 负责；不要声称 SQLite 的 Hash 链是不可篡改证据。
- LLM 解读只通过批准的模型端点完成。`build_evidence_pack` 只**生成待解释的证据结构**，不会向外发包或暗中调用任何外部 AI。
- 如果 Blocks DSL 不支持 Python，自定义 Operation 优先抽象为 `ratio`, `lag`, `join`, `group`, `compare`, `classify`, `emit_alert`, `request_review` 等已有受控内置节点。

## 返回结构建议

一条研究线索：

`{ rule_id, rule_version, status, observed, threshold, evidence_level, source_url, available_at, reason, review_status, interpretation_limit }`

状态包含 `triggered / not_triggered / not_evaluable / requires_review` 等。`not_evaluable` 必须单独保留。

## 集成验收重点

- 数据在截止日期之后披露时，严格不能出现在旧日期分析里。
- 不允许把法院姓名搜索结果无核查地绑定实控人身份。
- 财报缺数据、年度不一致、公司是金融企业时，需拒绝或降级相关工业企业评分。
- 用户调整阈值后重新运行；保留参数与规则版本。
- 同一类股东质押的“公司百分数”和“控制人个人比例”字段不能混用。
- 验证所有工具不执行任意用户代码，不向应用文件存放 Token。

## 三个演示对话（供 User Guide）

**示例 1**
用户：`扫描我这十家企业近三年的利润和现金流，有没有持续背离？`
AI：`我会读取已披露的年报三表，对齐报告期，运行 R1 等财务质量规则。缺失年度会标为无法计算，输出公式和来源。`

**示例 2**
用户：`近一年哪些公司有非标审计、异常质押或者会计差错更正？`
AI：`我将分别检查审计字段、质押统计和公告标题，按来源和证据强度生成复核清单；不会将标题当作已核实违法事实。`

**示例 3**
用户：`新的监管指引会影响哪些公司？`
AI：`请绑定授权的政策原文和适用主体数据。我可以列出文本变化、可能涉及的议题和合规待办；是否适用及法律效力需人工核查。`
