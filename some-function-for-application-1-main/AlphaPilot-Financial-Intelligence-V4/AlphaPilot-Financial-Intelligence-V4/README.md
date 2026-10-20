# AlphaPilot Financial Intelligence V4 + Shared Financial Risk Operations

**基于先前 V2/V3 代码的增量更新，保留原有 AlphaPilot 功能，并吸收千问 RegGuard 方案中能够验证的金融算法与规则。**

## 这版保留了什么？

上一版的全部功能（Tushare 适配、比赛数据目录、F10、基本面比较、技术指标、组合风险、宏观发布数据比较、日报事实包、股票观察信号、机器学习异常检测、官方免费资讯/方法知识卡和应用文件原型）保留。

V3 已引入的 Beneish M-Score、Altman 新兴市场 Z''、Piotroski F-Score、应计质量和 RegGuard 简单初筛也完整保留。

## V4 新增

1. `catalog/regguard_rulebook.json/.csv`：**完整列出千问 R1–R12 的业务定义与落地成熟度**，不强行宣称12条都可计算。
2. `regguard.screen_accounting_v2`：R1（连续2年现金流与利润背离）、R2（应收跑赢收入且比例上升）、R4（其他应收占比）、R7（流动比率）、R11（复合应收异动）；R3输出中间数值但明确不可最终判断。所有规则包含分子/分母相关字段、研究阈值和数据可用性状态。
3. `finance.compare_peer_scores`：同业同报告期有效样本排序，少于8家拒绝输出百分位；截止日期以后披露的财报不参与排名。
4. 加入公告标题的“审计师更换”分类，仍严格保持 `title_only` 标签。
5. 更新金融方法知识卡、AI 使用说明、Blocks 对接清单和千问建议取舍表。

## 测试与运行

Python 3.10+；完全离线可跑，测试数据是虚构数值。

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python demo_v4.py
python export_ai_tools.py
python export_rulebook.py
python update_knowledge.py --db knowledge.sqlite
```

**注意：这不是官方 Blocks App 格式。** `application-v4-example.json` 只演示如何引用经审查的运算；需要核心平台开发者按其正式 Schema 注册。这里提供算法实现，不替代平台运行时的权限、沙箱、调度或审计。

## 金融质量与事实边界

- 千问的普通 Tushare 免费 120 积分前提**不适用于你们的比赛专用 Token**。仍需要对实际接口逐项进行有界探测（参见 `alphapilot/competition_tushare.py`）。
- 你们本次上传的是 37 表/856 字段的字段说明，**不是下载好的实际数据行**；没有 Token 的情况下我们没有验证真实财经行情与财报结果。
- 经典美国模型系数不自动适用于 A 股，不输出“舞弊概率”。Altman 模型常数 3.25 与不同分档阈值不能混淆。
- 风险阈值仅是可校准的研究初始值，非政府监管统一标准。
- R5/R6/R10/R12 和司法数据自动检查在本版中不声称已实现。已标注在 `catalog/regguard_rulebook.json`。
- 仍未实现真实秒级盯盘、自动下单、持牌投资顾问服务、Blocks 官方执行/推送/UI。

## 最重要的文件

- `TEAM_HANDOFF.md`：怎样交给队友集成进真正 Blocks 平台。
- `QWEN_ADOPTION_DECISIONS.md`：千问方案采用/暂缓/拒绝清单。
- `catalog/ai_tools.json`：AI 工具注册信息。
- `catalog/regguard_rulebook.csv`：金融专家可读、可编辑的规则表。
- `alphapilot/research_rules.py`：V4 新实现。
- `tests/test_v4_research_rules.py`：V4 防未来泄漏、缺失值和同行样本测试。
