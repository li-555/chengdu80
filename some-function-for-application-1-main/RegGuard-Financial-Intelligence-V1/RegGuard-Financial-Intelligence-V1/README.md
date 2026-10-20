# RegGuard Financial Intelligence V1（应用 2 专业能力包）

**定位：** 参赛平台 Blocks 的企业风险与监管情报金融能力模块，重用 AlphaPilot V4 的经过测试的财务运算。它不是独立产品平台、不是发布格式、也不是法院/监管执法系统。

## 包含什么

- 19 项注册操作：6 项重用的财务算法/规则 + 13 项新领域操作。见 `catalog/regguard_ai_tools.json` 和 `AI_AGENT_GUIDE.md`。
- 与团队协作的 Excel 工作簿 `RegGuard_Rules_Tools_M2.xlsx`（规则、工具、M2 覆盖、数据源四张表）。
- 12 条财务红旗的标准化规则表：`catalog/regguard_rulebook.csv`、`.json`；完整规则**不代表全部可自动计算**。
- 37 张比赛数据表 / 856 个字段的元数据目录：`catalog/competition_tables.json`（**无真实数据行**）。
- Tushare 白名单连接器（来自 AlphaPilot V4），Token 只从环境变量 `TUSHARE_TOKEN` 读取。
- 案例 SQLite 审查记录（本地演示），人工核查清单、法规快照差异、公告标题风险事件、可审计证据包。
- 本地官方方法参考知识卡 `catalog/knowledge_cards.json`，不声称已经实时更新监管资料。
- 虚构公告、审计意见、质押表和 demo 结果（全部虚构；`example.org` URL 不是真实披露文件）。

## 运行

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python demo_regguard.py
python export_tools.py
```

可选：

```bash
python -m pip install -r requirements-optional.txt
# 在私有环境设置 TUSHARE_TOKEN，不要粘贴或上传 Token
python verify_tushare.py 000001.SZ
```

`scikit-learn` 用于可选的同行业 Isolation Forest；`tushare` 仅用于已授权数据请求。测试没有使用真实交易数据或联网服务。

## 七大能力映射 M2

| M2 2.4 | 实现方式 | 当前状态 |
|---|---|---|
| 1 财报与审计 | 现金流/应计/模型 + `audit_opinion_review` | 财务运算已实现，审计接口需真实 Token/数据验证，附注全文解析尚未完成 |
| 2 财务异常和潜在舞弊线索 | R1/R2/R3/R4/R7/R11、Beneish、Altman、F-Score、同行异常模型 | 部分规则可算；缺失字段显示 `not_evaluable`，不宣称模型有效预测舞弊 |
| 3 实控人及法律风险 | `disclosed_ownership_graph` + `controller_legal_checklist` | 显示历史持股关系、官方人工核查待办；不自动抓法院/确认身份 |
| 4 监管风向 | `regulatory_change_tracker` + 主题分类 | 已支持授权输入的监管文档快照比对；未上线官方持续采集 |
| 5 事件驱动预警 | 质押/审计/标题事件 + `consolidate_alerts` / `build_digest` | 离线生成与合并可用，定时触发和通知交由 Blocks 平台 |
| 6 可审计工作流 | `regguard/workflow.py` 审核事件与证据引用 | 本地 SQLite 示范可用；权限、审计防篡改与部署需平台实现 |
| 7 安全与隔离 | 数据提供方 Token 隔离、命名工具白名单、只传元信息 | 金融模块已避免任意执行；租户、运行容器、安全部署需 Blocks 统一实现 |

**重要：** 审计和法律模块只能得出待复核线索；`not_evaluable` 不等于未触发、无风险。研究阈值不是监管官方标准，不作为定性法律结论。

## 三个典型使用案例

- “筛选现金流与利润持续背离的企业” → `regguard.screen_financials` → 显示规则、公式、披露日与未计算项目。
- “哪些公司发生非标审计、股权质押上升或公告差错更正？” → `audit_opinion_review` + `pledge_risk_review` + `filing_event_triage` → 独立事实线索和按复核优先级排列的待办。
- “新规有哪些变化，谁需要核查？” → 导入合法来源的旧/新法规文本 → `regulatory_change_tracker` → 主题分组和人工判断任务。

## 对接 Blocks

开发者应直接看 `TEAM_HANDOFF.md` 和 `catalog/regguard_capability_map.json`；`catalog/example_workflow_prototype.json` **只是概念流程示例**；**不要将** `regguard.registry` **本身误当做 Blocks 官方 Registry**。无 Blocks 正式接口时，保留 `catalog/regguard_ai_tools.json` 作为中立的元数据契约，由 Blocks 开发者进行适配。

## 原始与后续范围

金融报表和学术模型代码复用自先前的 `AlphaPilot-Financial-Intelligence-V4`；Qwen 提案的 12 条风险规则是业务参考，并不证明所有公式在当前比赛数据中可计算。算法系数、行业适用范围与监管口径要在真实财报上进一步验证；M2 是产品承诺，而这个包只承担金融专业层。
