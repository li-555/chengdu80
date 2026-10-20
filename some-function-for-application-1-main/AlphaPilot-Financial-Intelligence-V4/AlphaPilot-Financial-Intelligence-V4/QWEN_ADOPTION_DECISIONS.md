# 千问方案取舍表（团队内部文件，不属于 M2 对外承诺）

原材料：`RegGuard-数据源与算法调用方案.md`；原代码：AlphaPilot V2/V3；这版为 V4。

## 采纳及整合

| 建议 | 决策 | 代码或资料 | 金融口径说明 |
|---|---|---|---|
| Piotroski 九项 F-Score | 保留 V3 | `financial_forensics.piotroski_f_score` | 适用财务健康研究，不是欺诈判断；缺增发事件证据不输出完整分数 |
| Altman 新兴市场 Z'' | 保留 V3 | `financial_forensics.altman_em_score` | 含 3.25 常数，不使用混淆版本的风险区间阈值；不适用银行/保险 |
| Beneish M-Score | 保留 V3 | `financial_forensics.beneish_m_score` | 八项指标贡献需完整；只做研究参考数值，不能当 A 股财务舞弊概率 |
| 应计/利润与现金流质量 | 保留 V3 | `financial_forensics.accrual_quality` | 明确使用 `(NI-CFO)/平均总资产`，**不直接称为不加限定的 Sloan Ratio**，以防混淆定义 |
| 透明风险规则 R1–R12 | **升级 V4** | `catalog/regguard_rulebook.{json,csv}` | 12 条业务规格；其中 R1/R2/R4/R7/R11 代码可计算，R3因利息科目口径待核实，仅展示中间指标不触发最终结论 |
| 标题级审计/重述/减持线索 | 保留并加审计师更换 | `financial_forensics.audit_filing_triage` | 不声称读过公告全文；标题命中只是待复核线索 |
| 同行业异常比较 | **新增 V4** | `research_rules.compare_peer_scores` | 至少 8 家同业、相同报告期、已披露样本；百分位不是风险概率 |
| Tushare 限权探测 | 保留 V3 | `competition_tushare.probe_permissions` | 必须使用比赛 Token 权限探测；普通免费额度并不代表你们实际权限 |
| 知识说明卡 | **增强 V4** | `knowledge.METHODS` | 增加 Piotroski、Beneish、Altman、应收与现金流口径；来源链接，语义检索仍非完全 RAG |

## 暂缓或不采纳

| 建议 | 决策原因 |
|---|---|
| BaoStock 替代 Tushare 做主数据源 | **不采用**。组委会已提供 37 表 / 856 字段与比赛专用 Tushare 授权。现有源优先，其他源仅在合法许可和字段缺口确认后使用。 |
| 原始模型阈值自动贴“舞弊高风险”标签 | **不采用**。美国历史模型未本土化验证；还存在 Z'' 带/不带 3.25 常数分区不可混用的问题。 |
| R3 仅凭资金多和债务多自动指控风险 | **不采用**。存款利息收益率需要经过验证的账户字段和可比平均余额。缺失时显示不可计算。 |
| R5 担保占净资产、R6 最新质押、R10 精确减持比例、R12 交易日事件窗口 | **留作下一步数据工程**。当前文件没有可靠完整的事件账本；不能以标题或过期质押数据冒充2026实时事实。 |
| 自动裁判文书、监管处罚和执行失信站爬虫 | **不采用为基础依赖**。缺稳定许可/开放 API，建议官方链接与人工核查记录，商业/合规使用需另行评估。 |
| Dechow F-Score + 监督式 A 股舞弊模型 | **暂不实现**。系数、字段可得性、训练标签及合法性均需验证。 |
| 断言 `flk.npc.gov.cn/api/` 是稳定开放 API | **暂不采信**。仅在正式公开文档与使用条件明确并经接入测试后接入。 |

## 关于代码与平台文件格式

- Python 在这里是**专业运算实现**。不是要求用户生成/运行自由形式 Python 代码。
- AI 看 `catalog/ai_tools.json`、`catalog/regguard_rulebook.json`、`catalog/competition_tables.json`，生成**平台支持的应用描述**。
- Blocks 团队决定这些操作由已有查询/表达式组合表达，还是作为平台审查过的内置金融操作调用。
- `application-v4-example.json` 是我们自己的原型 DSL，**不要当作最终官方 Blocks 格式**，也不应向其他团队公开源代码或内部阈值。

## 重要数据边界

比赛提供的核心表字段定义不是数据内容。已核实的表包括
`cd80_stock_fin_balancesheet` (`oth_receiv`, `money_cap`, `total_cur_assets`)、
`cd80_stock_fin_income` (`n_income`, `revenue`)、
`cd80_stock_fin_cashflow` (`n_cashflow_act`) 和 `cd80_anns_d`。
实际能够查到多少历史报告、Tushare API 返回什么，需要在团队环境中实测。
