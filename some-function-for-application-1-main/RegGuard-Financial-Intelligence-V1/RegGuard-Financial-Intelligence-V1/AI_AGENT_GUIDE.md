# RegGuard AI 金融工具选择指南 / AI Agent Guide

## 原则

1. **先确定需求、数据与分析日期，再选择操作**。`as_of` 之前不可使用未来财报、重述或新公布的处罚。
2. **信息不足就显示缺失**。每个工具支持 `not_evaluable` / `insufficient_inputs` / `insufficient_comparable_peers` 等状态，不能当作 `not_triggered`。
3. **不得生成或暗示“X 公司舞弊概率 87%”**。Beneish、Isolation Forest 的分数是模式/相对异常值，不能当作事实、舞弊概率或违法判断。
4. **关联主体依赖身份核查**。同名不是同一人、前十大股东不是实际控制人，调查/指控/生效裁判严格区分。
5. **证据必须留出处**。标题级文件不得写成全文级分析。引用具体证据时至少传 `published_at`、`source_url`、`excerpt`，以及可能的 `page`。
6. **数据与模型的权限由 Blocks 管**。不要在应用文件、AI 请求和日志中输出 Tushare Token、内部客户数据或其他敏感数据行。

## 19 个可供 AI 发现的工具

| Tool ID | 场景 | 说明 |
|---|---|---|
| `regguard.screen_financials` | 跨期财报 | R1/R2/R3/R4/R7/R11 财务研究线索 |
| `regguard.altman_em_z` | 偿债 | Altman 新兴市场 Z''，非违约概率 |
| `regguard.piotroski_f` | 财务质量 | 九信号财务健康，非舞弊模型 |
| `regguard.beneish_m` | 财务操纵模式 | 仅研究描述，非舞弊事实 |
| `regguard.accrual_quality` | 盈利含金量 | 利润与经营现金流差异/平均资产 |
| `regguard.compare_peer_scores` | 同行比较 | 同行业、同期、已披露至少 8 家，才出分位数 |
| `regguard.audit_opinion_review` | 审计 | 使用真实 `fina_audit` 结构化意见字段；区分非标与机构变更 |
| `regguard.pledge_risk_review` | 股权质押 | 公司整体质押比例、百分点变化，非实控人个人质押 |
| `regguard.filing_event_triage` | 公告 | 仅公告标题初筛，禁止冒充正文解读 |
| `regguard.controller_legal_checklist` | 司法核查 | 生成官方人工核查待办，不自动判定人员案件 |
| `regguard.disclosed_ownership_graph` | 股东关系 | 时点有效前十大股东边；控制关系需已核实证据 |
| `regguard.regulatory_change_tracker` | 新规追踪 | 对比授权提供的新旧法规版本；缺失≠废止 |
| `regguard.classify_regulatory_topics` | 监管分类 | 关键词主题分类，不得推断法律效力 |
| `regguard.peer_outlier_screen` | 无监督分析 | RobustScaler + IsolationForest，至少30同业样本；需可选 sklearn |
| `regguard.consolidate_alerts` | 预警汇总 | 保留每个风险单独的理由/证据；无合成舞弊概率 |
| `regguard.build_digest` | 日/周摘要 | 形成结构化事实包；不负责运行调度 |
| `regguard.build_evidence_pack` | 大模型解释 | 整理经校验的原文证据包，交给授权 LLM |
| `regguard.dataset_coverage` | 数据盘点 | 37 表/856 字段目录，不是实际数据权限 |
| `regguard.knowledge_search` | 金融与合规知识 | 检索离线知识卡，附出处，非现行法规实时校验 |

所有工具的详细参数由 `catalog/regguard_ai_tools.json` 描述，工具输入不是任意文本，而是 Blocks 已绑定的数据集或结构化结果。

## 关键字段映射

- 公告：比赛 `cd80_anns_d` = `announcement_date`、`ticker`、`announcement_title`、`url`。使用 `regguard.normalize.normalize_source(frame,'cd80_anns_d')` 映射为 `ann_date` / `ts_code` / `title`。
- 财报：利润表 `cd80_stock_fin_income`、资产负债表 `cd80_stock_fin_balancesheet`、现金流 `cd80_stock_fin_cashflow`。须按 `ts_code + end_date + ann_date/f_ann_date` 关联。
- 审计：优先 Tushare `fina_audit`（`audit_result` / `audit_agency` / `ann_date` / `end_date`）。拿不到不能假装有非标类型字段。
- 质押：`pledge_stat` 的 `pledge_ratio` 按 **百分数** 而不是小数处理；比赛的旧 `cd80_stock_refer_pledge_stat` 历史止于 2017 年，不能代表当前企业。

## 典型组合

**财务法证扫描：** `dataset_coverage` → 绑定年报三表 → `screen_financials` + `beneish_m` + `altman_em_z` → `compare_peer_scores`（如足够同行）→ `consolidate_alerts` → `build_digest`。

**公告与治理调查：** `filing_event_triage` + `audit_opinion_review` + `disclosed_ownership_graph` → `controller_legal_checklist` → 平台级人工调查流 → `build_evidence_pack`。

**监管政策：** 由平台导入经许可的官方监管文档新旧版本 → `regulatory_change_tracker` → `classify_regulatory_topics` → 人工合规任务。

## 生成结果必须说明

- 使用的表 / 日期 / 披露时间 / 公式 / 版本号；
- 样本覆盖和缺失字段；
- 指标是研究线索、人工核查项还是有出处的最终监管或司法结论；
- 不能因为数据缺失就写“无风险”。
