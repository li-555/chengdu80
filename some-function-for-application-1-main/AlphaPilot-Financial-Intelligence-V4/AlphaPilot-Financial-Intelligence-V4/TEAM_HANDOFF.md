# 交给 Blocks 核心开发人员的最小接口清单

**不要把这个 Python 包误认为应用文件格式。** 它包含金融领域算法和可移植的业务规则说明。

## 请对接的文件

1. `catalog/competition_tables.json`：字段目录（仅元数据，没有实际数据行）。
2. `catalog/ai_tools.json`：供 AI 选择工具，**这是原型接口描述**。
3. `catalog/regguard_rulebook.json`：12 条业务风险规则，可以转换为 Blocks DSL。
4. `catalog/regguard_rulebook.csv`：给金融团队调整阈值/原因/优先级的表格格式。
5. `alphapilot/research_rules.py`：执行 R1/R2/R3/R4/R7/R11 和同行百分位比较。
6. `alphapilot/financial_forensics.py`：已有 Piotroski、Altman、Beneish、应计质量、公告标题初筛。
7. `AI_AGENT_GUIDE.md`：金融运算使用纪律。

## Blocks 需要提供的能力

- 授权数据绑定：`balance`, `income`, `cashflow`（数据含 ts_code/end_date/ann_date 等）。
- 文件导入/导出：应用只声明表、字段、运算，不包含 Token、客户数据、公司私有数据行。
- 运算注册与校验：两项新增 operation ID 是 `regguard.screen_accounting_v2` 与 `finance.compare_peer_scores`。
- 输出界面：保留 `status`、`observed`、`threshold`、`fields`、`reason`、`review_status` 和报告期。
- 版本：将规则版本、财务数据时间、运行版本写入平台执行记录。

## 输入输出合同（简要）

`regguard.screen_accounting_v2(balance, income, cashflow, as_of, ...) -> list[dict]`

最小有意义输出字段：ts_code、report_period、available_at、trigger_count、rules[]。每条规则有 `triggered` / `not_triggered` / `not_evaluable` 状态；不要把 `not_evaluable` 当作 `not_triggered`。

`finance.compare_peer_scores(records, as_of, min_peers=8) -> list[dict]`

同业、同报告期、已披露、最少 8 家才显示百分位。不提供投资建议、违约概率或舞弊概率。

## 如果平台暂时无法加载 Python

先将 JSON 风险规则表转换为平台已有的比率计算、条件判断、分组和时间筛选。对无法表示的复杂运算（如 Beneish 八因子）可以保留为未来受控内置 Operation；**不要让 AI 用任意 Python 执行替代**。

## 测试

```bash
pip install -r requirements.txt
python -m pytest -q
python demo_v4.py
python export_ai_tools.py
python export_rulebook.py
```

所有 demo 数值均为虚构数据；真实 Tushare 和交易日监控仍需授权环境验证。
