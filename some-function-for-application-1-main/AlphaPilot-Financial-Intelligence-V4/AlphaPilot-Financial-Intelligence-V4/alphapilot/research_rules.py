"""Financial-domain review flags, explicitly not evidence of fraud.

This module is independent of the Blocks document schema. The platform may call it
as a reviewed operation or translate catalog/risk_rulebook.json into its native DSL.
All numerical thresholds here are CONFIGURABLE PROTOTYPES, not regulator rules.
"""
from __future__ import annotations

from datetime import date
from typing import Any

import numpy as np
import pandas as pd

from .financial_forensics import _merge, _nonfinancial, _numeric, _divide

RULE_VERSION = "research-2026-10-v1"


def _result(rule_id: str, status: str, observed: Any = None,
            threshold: Any = None, fields: list[str] | None = None,
            reason: str = "", priority: str = "review", **extra) -> dict:
    return {
        "rule_id": rule_id, "rule_version": RULE_VERSION, "status": status,
        "observed": observed, "threshold": threshold,
        "fields": fields or [], "reason": reason,
        "review_priority": priority if status == "triggered" else None,
        "review_status": "unreviewed" if status == "triggered" else "not_applicable",
        "interpretation_limit": "初筛研究线索；不是舞弊认定、监管结论或投资建议。",
        **extra,
    }


def screen_accounting_red_flags(balance: pd.DataFrame, income: pd.DataFrame,
                                cashflow: pd.DataFrame, as_of: str,
                                cfo_ni_threshold: float = 0.5,
                                receivables_gap_threshold: float = 0.15,
                                other_receivables_threshold: float = 0.10,
                                current_ratio_threshold: float = 1.0,
                                consecutive_years: int = 2) -> list[dict]:
    """Evaluate R1, R2, R3, R4, R7, R11, with explicit non-evaluable states.

    Annual figures only, selected using publication <= as_of. R3 is never
    triggered without verified interest-income account mapping. Missing values
    are not imputed and cannot silently become zero.
    """
    if not 0 < cfo_ni_threshold <= 2: raise ValueError("cfo_ni_threshold out of range")
    if not 0 < receivables_gap_threshold <= 2: raise ValueError("receivables_gap_threshold out of range")
    if not 0 < other_receivables_threshold <= 1: raise ValueError("other_receivables_threshold out of range")
    if not 0 < current_ratio_threshold <= 5: raise ValueError("current_ratio_threshold out of range")
    if not 2 <= consecutive_years <= 5: raise ValueError("consecutive_years must be 2..5")
    cutoff = pd.Timestamp(as_of)
    frame = _merge(balance, income, as_of, cashflow)
    out = []
    for code, group in frame.groupby("ts_code"):
        if not _nonfinancial(balance, code):
            out.append({"ts_code": str(code), "status": "unsupported_financial_company", "rules": []})
            continue
        group = group.sort_values("end_date")
        r = group.iloc[-1]
        p = group.iloc[-2] if len(group) >= 2 and r.end_date.year - group.iloc[-2].end_date.year == 1 else None
        rules: list[dict] = []

        # R1: two or more comparable annual positive-NI periods with depressed cash conversion
        trail = group.tail(consecutive_years)
        trail_years = [int(v.year) for v in trail.end_date]
        consecutive = len(trail) == consecutive_years and all(
            trail_years[j] - trail_years[j - 1] == 1 for j in range(1, len(trail_years))
        )
        ratios = []
        if consecutive:
            for _, row in trail.iterrows():
                ni, cfo = _numeric(row, "n_income"), _numeric(row, "n_cashflow_act")
                ratios.append(_divide(cfo, ni) if ni is not None and ni > 0 else None)
        known = bool(consecutive and all(v is not None for v in ratios))
        rules.append(_result("R1_cash_earnings_gap",
                             "triggered" if known and all(v < cfo_ni_threshold for v in ratios) else
                             "not_triggered" if known else "not_evaluable",
                             observed={"cash_conversion_by_year": dict(zip(trail_years, ratios))} if consecutive else None,
                             threshold={"below": cfo_ni_threshold, "consecutive_years": consecutive_years},
                             fields=["n_income", "n_cashflow_act"],
                             reason="连续可比年度经营现金流不足以覆盖正净利润" if known else "缺少连续的正利润年度或现金流数据",
                             priority="medium"))

        # R2: receivables growth versus revenue growth, with absolute AR/sales ratio rising
        gap = None
        increase_ar_sales = None
        if p is not None:
            ar, ar0 = _numeric(r, "accounts_receiv"), _numeric(p, "accounts_receiv")
            rev, rev0 = _numeric(r, "revenue"), _numeric(p, "revenue")
            if all(x is not None for x in [ar, ar0, rev, rev0]) and ar0 > 0 and rev0 > 0 and rev > 0:
                gap = (ar / ar0 - 1) - (rev / rev0 - 1)
                increase_ar_sales = ar / rev > ar0 / rev0
        status = ("not_evaluable" if gap is None else
                  "triggered" if gap > receivables_gap_threshold and increase_ar_sales else "not_triggered")
        rules.append(_result("R2_receivables_vs_sales", status,
                             observed={"growth_gap": gap, "ar_to_sales_increased": increase_ar_sales},
                             threshold={"growth_gap_above": receivables_gap_threshold, "ratio_must_rise": True},
                             fields=["accounts_receiv", "revenue"],
                             reason="应收增长快于营收，且应收/营收占比上升" if status == "triggered" else "需有两年可比应收与营收数据",
                             priority="medium"))

        # R3: do not invent deposit-interest income. Compute context, refuse final rule.
        cash, assets = _numeric(r, "money_cap"), _numeric(r, "total_assets")
        debt_items = [_numeric(r, k) for k in ["st_borr", "lt_borr", "bond_payable"]]
        known_debt = all(x is not None for x in debt_items)
        cash_share = _divide(cash, assets) if assets is not None and assets > 0 else None
        debt_share = _divide(sum(debt_items), assets) if known_debt and assets is not None and assets > 0 else None
        rules.append(_result("R3_high_cash_high_debt", "not_evaluable",
                             observed={"cash_over_assets": cash_share, "debt_over_assets": debt_share},
                             threshold={"cash_over_assets": 0.15, "debt_over_assets": 0.25,
                                        "requires_verified_deposit_interest_yield": True},
                             fields=["money_cap", "st_borr", "lt_borr", "bond_payable", "total_assets"],
                             reason="未获得已核实可比的存款利息收入口径，不可将现金多+债务多等同于风险结论"))

        # R4: only balance-sheet other receivables, not vague related-party allegations
        other = _numeric(r, "oth_receiv")
        oth_assets = _divide(other, assets) if assets is not None and assets > 0 else None
        status = "not_evaluable" if oth_assets is None else "triggered" if oth_assets > other_receivables_threshold else "not_triggered"
        rules.append(_result("R4_other_receivables_concentration", status,
                             observed={"other_receivables_over_assets": oth_assets},
                             threshold={"above": other_receivables_threshold},
                             fields=["oth_receiv", "total_assets"],
                             reason="其他应收款占资产比重偏高，需核查附注和往来方性质" if status == "triggered" else "缺失必要科目或未超过研究阈值",
                             priority="medium"))

        # R7: narrow, reproducible liquidity signal. Interest coverage not assumed.
        ratio = _divide(_numeric(r, "total_cur_assets"), _numeric(r, "total_cur_liab"))
        status = "not_evaluable" if ratio is None else "triggered" if ratio < current_ratio_threshold else "not_triggered"
        rules.append(_result("R7_low_current_ratio", status,
                             observed={"current_ratio": ratio},
                             threshold={"below": current_ratio_threshold},
                             fields=["total_cur_assets", "total_cur_liab"],
                             reason="短期流动性指标偏弱，应结合行业和资产可变现性判断" if status == "triggered" else "缺失必要字段或未超过阈值",
                             priority="medium"))

        # R11 is a compound *research hypothesis*, not evidence of sham trades.
        r2 = next(x for x in rules if x["rule_id"].startswith("R2_"))
        r4 = next(x for x in rules if x["rule_id"].startswith("R4_"))
        compound = "triggered" if r2["status"] == r4["status"] == "triggered" else (
            "not_evaluable" if "not_evaluable" in [r2["status"], r4["status"]] else "not_triggered")
        rules.append(_result("R11_joint_receivables_pattern", compound,
                             observed={"r2_status": r2["status"], "r4_status": r4["status"]},
                             threshold={"both": ["R2_receivables_vs_sales", "R4_other_receivables_concentration"]},
                             fields=["accounts_receiv", "revenue", "oth_receiv", "total_assets"],
                             reason="多个应收类指标同时偏离，仅提示进一步查核经营和关联交易附注",
                             priority="medium"))
        pub = max(r.balance_published, r.income_published, r.cashflow_published)
        if pub > cutoff:
            raise AssertionError("point-in-time safeguard failed")
        out.append({"ts_code": str(code), "report_period": r.end_date.date().isoformat(),
                    "available_at": pub.date().isoformat(), "as_of": cutoff.date().isoformat(),
                    "rule_version": RULE_VERSION,
                    "trigger_count": sum(x["status"] == "triggered" for x in rules),
                    "rules": rules,
                    "caution": "基于有限报表字段的研究预警，不构成财务舞弊/违法事实或风险概率；阈值均需同行业校准。"})
    return out


def compare_peer_scores(records: list[dict], as_of: str, min_peers: int = 8) -> list[dict]:
    """Rank already-computed accounting scores within same industry & same fiscal year.

    Missing/late disclosure, different periods and tiny groups are never ranked.
    No default inference that 'high score is fraud' or other interpretation.
    """
    if not 8 <= min_peers <= 500:
        raise ValueError("min_peers must be in [8,500]")
    cutoff = pd.Timestamp(as_of)
    data = pd.DataFrame(records)
    needed = {"ts_code", "industry", "report_period", "available_at", "score", "status"}
    if not needed.issubset(data.columns):
        raise ValueError(f"Missing keys: {sorted(needed - set(data.columns))}")
    if data.duplicated(["ts_code", "industry", "report_period"]).any():
        raise ValueError("Duplicate company/industry/report_period; version selection required")
    data["available_at"] = pd.to_datetime(data.available_at, errors="coerce")
    data["score"] = pd.to_numeric(data.score, errors="coerce")
    good = data[(data.available_at.notna()) & (data.available_at <= cutoff) &
                (data.status == "ok") & data.score.notna() &
                np.isfinite(data.score) & data.industry.notna() & data.report_period.notna()].copy()
    output = []
    for (industry, period), group in good.groupby(["industry", "report_period"]):
        n = len(group)
        if n < min_peers:
            output.append({"industry": str(industry), "report_period": str(period),
                           "status": "insufficient_peers", "peer_count": n, "minimum": min_peers})
            continue
        ranks = group.score.rank(pct=True, method="average")
        for (_, row), percentile in zip(group.iterrows(), ranks):
            output.append({"ts_code": str(row.ts_code), "industry": str(industry),
                           "report_period": str(period), "available_at": row.available_at.date().isoformat(),
                           "score": float(row.score), "sample_percentile": round(float(percentile), 6),
                           "peer_count": n, "status": "ok",
                           "caution": "仅同业已披露样本中的数值排名，非舞弊概率、违约概率或投资建议。"})
    return output
