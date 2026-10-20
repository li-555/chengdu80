# AlphaPilot Agent：如何使用金融运算和知识库

1. 读 `catalog/ai_tools.json`：这里列出的 operation 名称是唯一允许使用的运算，AI 不应生成任意 Python、SQL、Shell。
2. 读 `catalog/competition_tables.json`：只看字段名、类型（在工作簿字段描述中）、数据来源、覆盖区间；不把用户私有数据行传入生成模型。
3. 对用户需求先识别 **市场、时间、证券代码、报告期、指标口径、频率、数据权限**，缺少必要信息则提问。
4. 生成声明式 JSON `steps`。`arguments` 中数据通过 `{"$ref":"..."}` 指向已经由平台授权绑定的服务端数据句柄，不内嵌个人资产或 API Token。
5. 校验器 `validate_app` 检查操作名称、引用、步骤顺序和必要参数，执行前必须通过校验。该校验器为教学性原型，不包含 Blocks 官方规范的类型/权限全检。
6. 同一任务优先调用可审计的 Operation；**LLM 只负责解释、摘要和研究假设**，不能凭空计算真实估值、非农公布值、分析师预期、实时成交或交易确定性。
7. 调用 `finance.f10_cards` 时，按 ann_date 限制 as_of；股东质押的旧版数据在缺少新记录时只能返回“资料不充分”，不能当作当前状态。
8. 调用 `finance.compare_fundamentals` 时，解释同业样本、报告期一致性、缺失指标；2–5 支比较和行业全体排名不可混为一谈。
9. `finance.daily_briefing` 输出可审计的事实包；前端或经过批准的模型可继续生成带出处报告，不能把 headline_only 当作公告正文研读。
10. `knowledge.search` 返回的每条资料必须附 source_url；官方 RSS 更新只保存标题和短描述，未经授权的付费新闻不能存全文。
11. 输出结构建议：`facts[]`, `metrics[]`, `interpretations[]`, `uncertainties[]`, `sources[]`, `as_of`, `data_latency`, `investment_advice=false`。
12. 用户请求买卖建议时，改为按其阈值生成**可解释的观察信号与风险提示**，不自动委托下单。

## 例子：工具编排

- “比较这三家同行” → `finance.compare_fundamentals` + `finance.compare_stocks` → 解释有无一致财报期。
- “今日复盘” → `finance.daily_briefing` + `finance.announcement_watch` → 提供证据束给 LLM 写文字。
- “过去一年哪些日期异常” → `ml.anomaly_isolation_forest` → 返回异常分数与训练/测试时间范围（不预测未来涨跌）。
- “非农高于预期了吗” → `finance.macro_release`（只有合法获得的一致预期存在时才计算 surprise）。

## V4 增量：千问金融风险方案及经审计规则

13. 读取 `catalog/regguard_rulebook.json` 获取业务上每条规则的名称、字段、阈值、原因、实现状态。这个业务规则字典不是自动可执行的 Blocks 应用。
14. 对 R1/R2/R4/R7/R11 可调用 `regguard.screen_accounting_v2`，传入已披露且同口径的年度报表；R3 因可比存款利息收益率尚未核实，返回 `not_evaluable`，不得把缺数转成无风险。
15. `finance.compare_peer_scores` 的值是同一行业、同一报告期且已披露的样本内分位（至少八家）；**不是欺诈概率、违约概率或买入概率**。不同比较模型/财报期不可直接拼成统一“风险分”。
16. 正常的风控研究输出必须区分 `triggered`（待核查）、`not_triggered`（给定数据与阈值未触发）、`not_evaluable`（资料不足）。任何严重风险升级和法律定性应由人工复核。
17. 对 R5/R6/R10/R12，未绑定完整可核实字段时不进行数值计算。历史质押表不可用于2026即时监管判断；可使用 `regguard.audit_title_triage` 作仅标题级事件提示。
18. 自然语言询问股票财务状况时，优先调用 AlphaPilot 基本面与财务质量工具；只有用户明确需要异常/监管风险时再使用 RegGuard 的初筛工具。不要把两套产品的用途混为一谈。
