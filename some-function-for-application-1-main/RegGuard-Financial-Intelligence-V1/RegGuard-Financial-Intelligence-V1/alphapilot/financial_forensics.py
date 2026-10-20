"""Reusable *descriptive* accounting metrics, not fraud predictions or investment advice.

All three Tushare statement tables must be point-in-time (published <= as_of),
annual reports, and aligned by stock + period. Missing inputs propagate as UNKNOWN.
Financial companies are rejected for formulas calibrated on industrial firms.
"""
from __future__ import annotations

from typing import Any
import numpy as np
import pandas as pd

ID = ['ts_code', 'end_date']


def _numeric(row: pd.Series, key: str) -> float | None:
    value = pd.to_numeric(row.get(key), errors='coerce')
    if pd.isna(value) or not np.isfinite(value):
        return None
    return float(value)


def _divide(x: float | None, y: float | None) -> float | None:
    if x is None or y is None or abs(y) < 1e-12:
        return None
    return float(x / y)


def _compare(a: float | None, b: float | None, op: str) -> bool | None:
    if a is None or b is None:
        return None
    if op == '>': return a > b
    if op == '>=': return a >= b
    if op == '<=': return a <= b
    if op == '<': return a < b
    raise ValueError('unsupported comparison')


def _pit(frame: pd.DataFrame, as_of: str, prefix: str) -> pd.DataFrame:
    needed = {'ts_code','end_date','ann_date'}
    if not needed.issubset(frame.columns):
        raise ValueError(f'{prefix} requires {sorted(needed - set(frame.columns))}')
    x = frame.copy()
    x['end_date'] = pd.to_datetime(x.end_date.astype(str), errors='coerce')
    x['ann_date'] = pd.to_datetime(x.ann_date.astype(str), errors='coerce')
    actual = pd.to_datetime(x['f_ann_date'].astype(str), errors='coerce') if 'f_ann_date' in x else x.ann_date
    x[f'{prefix}_published'] = pd.concat([x.ann_date, actual], axis=1).max(axis=1)
    cutoff = pd.Timestamp(as_of)
    x = x[x.end_date.notna() & x[f'{prefix}_published'].notna() &
          (x.end_date <= cutoff) & (x[f'{prefix}_published'] <= cutoff)]
    x = x[x.end_date.dt.strftime('%m%d') == '1231']  # Annual reports only
    # Do not accidentally compare consolidated annual reports with a restated/different report type.
    if 'report_type' in x and x['report_type'].notna().any():
        x = x[x['report_type'].astype(str).isin(['1','1.0'])]
    x = x.sort_values(f'{prefix}_published').drop_duplicates(ID, keep='last')
    return x.drop(columns=['ann_date','f_ann_date','report_type','comp_type','end_type','update_flag','id'], errors='ignore')


def _merge(balance: pd.DataFrame, income: pd.DataFrame, as_of: str,
           cashflow: pd.DataFrame | None = None) -> pd.DataFrame:
    b = _pit(balance, as_of, 'balance')
    i = _pit(income, as_of, 'income')
    # prevent duplicate same-named fields silently acquiring _x/_y (semantic ambiguity)
    overlaps = (set(b) & set(i)) - set(ID)
    i = i.rename(columns={x: f'income__{x}' for x in overlaps})
    f = b.merge(i, on=ID, how='inner', validate='one_to_one')
    if cashflow is not None:
        c = _pit(cashflow, as_of, 'cashflow')
        overlap = (set(f) & set(c)) - set(ID)
        c = c.rename(columns={x: f'cashflow__{x}' for x in overlap})
        f = f.merge(c, on=ID, how='inner', validate='one_to_one')
    if f.empty:
        return f
    f = f.sort_values(['ts_code','end_date']).reset_index(drop=True)
    return f


def _nonfinancial(balance: pd.DataFrame, code: str) -> bool:
    row = balance[balance.ts_code == code]
    if 'comp_type' not in row:
        raise ValueError('Missing comp_type; refusing to apply industrial-company models blindly')
    values = set(row.comp_type.dropna().astype(str))
    if not values or values != {'1'}:
        return False
    return True


def altman_em_score(balance: pd.DataFrame, income: pd.DataFrame, as_of: str) -> list[dict]:
    """Altman emerging markets Z'' numeric score ONLY; no universal distress cutoffs.

    3.25 + 6.56 WC/TA + 3.26 RE/TA + 6.72 EBIT/TA + 1.05 equity/liabilities.
    This score is not a default probability or a regulatory solvency judgement.
    """
    f = _merge(balance, income, as_of)
    out = []
    for code, g in f.groupby('ts_code'):
        if not _nonfinancial(balance, code):
            out.append({'ts_code':code,'score':None,'status':'unsupported_financial_company'});continue
        r = g.sort_values('end_date').iloc[-1]
        assets = _numeric(r,'total_assets')
        liab = _numeric(r,'total_liab')
        curr_assets, curr_liab = _numeric(r,'total_cur_assets'),_numeric(r,'total_cur_liab')
        retained, ebit = _numeric(r,'undistr_porfit'), _numeric(r,'ebit')
        equity = _numeric(r,'total_hldr_eqy_inc_min_int')
        wc = None if curr_assets is None or curr_liab is None else curr_assets-curr_liab
        x = {'working_capital_assets':_divide(wc,assets), 'retained_earnings_assets':_divide(retained,assets),
             'ebit_assets':_divide(ebit,assets), 'book_equity_liabilities':_divide(equity,liab)}
        score = None if None in x.values() or assets is None or assets <= 0 or liab is None or liab <= 0 else (
            3.25 + 6.56*x['working_capital_assets'] + 3.26*x['retained_earnings_assets'] +
            6.72*x['ebit_assets'] + 1.05*x['book_equity_liabilities'])
        out.append({'ts_code':str(code),'report_period':r.end_date.date().isoformat(),
                    'available_at':max(r.balance_published,r.income_published).date().isoformat(),
                    'score':float(score) if score is not None else None,'components':x,
                    'status':'ok' if score is not None else 'insufficient_inputs',
                    'model':'Altman Z_double_prime_emerging_market_with_3.25',
                    'limitations':'仅适用于适当非金融企业；非违约概率。不得套用未区分常数项的固定分区阈值。'})
    return out


def accrual_quality(balance: pd.DataFrame, income: pd.DataFrame,
                    cashflow: pd.DataFrame, as_of: str) -> list[dict]:
    """(Net income - operating cashflow)/average assets, NOT a fraud probability.
    Not named unqualified 'Sloan ratio', because competing total/operating accrual variants exist.
    """
    f = _merge(balance,income,as_of,cashflow)
    out=[]
    for code,g in f.groupby('ts_code'):
        if not _nonfinancial(balance,code):continue
        g = g.sort_values('end_date')
        for j in range(1,len(g)):
            r,p=g.iloc[j],g.iloc[j-1]
            if r.end_date.year-p.end_date.year!=1:continue
            ni,cfo = _numeric(r,'n_income'),_numeric(r,'n_cashflow_act')
            assets,prev_assets=_numeric(r,'total_assets'),_numeric(p,'total_assets')
            avg = (assets+prev_assets)/2 if assets is not None and prev_assets is not None and assets>0 and prev_assets>0 else None
            ratio = _divide(None if ni is None or cfo is None else ni-cfo,avg)
            out.append({'ts_code':code,'report_period':r.end_date.date().isoformat(),
                        'available_at':max(r.balance_published,r.income_published,r.cashflow_published).date().isoformat(),
                        'accruals_to_average_assets':ratio,'net_income':ni,'operating_cash_flow':cfo,
                        'formula':'(n_income - n_cashflow_act) / average(total_assets_t, total_assets_t-1)',
                        'status':'ok' if ratio is not None else 'insufficient_inputs',
                        'limitations':'现金流量表法应计代理变量；需对齐累计年报及合并口径；不是舞弊认定。'})
    return out


def piotroski_f_score(balance: pd.DataFrame, income: pd.DataFrame,
                      cashflow: pd.DataFrame, as_of: str,
                      issuance_flags: dict[str,bool] | None = None) -> list[dict]:
    """Nine Piotroski-inspired financial health checks, preserving unknowns.

    A proper no-new-equity signal requires issuance-event data; total_share alone
    is not sufficient (stock splits and bonus shares can change the count).
    Returns complete 0-9 score ONLY when all nine available. Otherwise partial score.
    """
    f = _merge(balance,income,as_of,cashflow)
    out=[]
    for code,g in f.groupby('ts_code'):
        if not _nonfinancial(balance,code):
            out.append({'ts_code':code,'score':None,'status':'unsupported_financial_company'});continue
        g = g.sort_values('end_date')
        if len(g)<2 or g.iloc[-1].end_date.year-g.iloc[-2].end_date.year!=1:
            out.append({'ts_code':code,'score':None,'status':'insufficient_consecutive_annual_reports'});continue
        r,p=g.iloc[-1],g.iloc[-2]
        def ratio(row,a,b):return _divide(_numeric(row,a),_numeric(row,b))
        def margin(row):
            rev,cost=_numeric(row,'revenue'),_numeric(row,'oper_cost')
            return _divide(None if rev is None or cost is None else rev-cost,rev)
        roa,prev_roa=ratio(r,'n_income','total_assets'),ratio(p,'n_income','total_assets')
        cfo, ni = _numeric(r,'n_cashflow_act'),_numeric(r,'n_income')
        current_ratio,prev_current=ratio(r,'total_cur_assets','total_cur_liab'),ratio(p,'total_cur_assets','total_cur_liab')
        leverage,prev_leverage=ratio(r,'lt_borr','total_assets'),ratio(p,'lt_borr','total_assets')
        gm,prev_gm=margin(r),margin(p)
        turnover,prev_turnover=ratio(r,'revenue','total_assets'),ratio(p,'revenue','total_assets')
        signals={
            'positive_roa': None if roa is None else roa>0,
            'positive_cfo': None if cfo is None else cfo>0,
            'roa_improved':_compare(roa,prev_roa,'>'),
            'cfo_exceeds_net_income':_compare(cfo,ni,'>'),
            'long_term_leverage_not_increased':_compare(leverage,prev_leverage,'<='),
            'current_ratio_improved':_compare(current_ratio,prev_current,'>'),
            'no_new_share_issuance': None if issuance_flags is None or code not in issuance_flags else not issuance_flags[code],
            'gross_margin_improved':_compare(gm,prev_gm,'>'),
            'asset_turnover_improved':_compare(turnover,prev_turnover,'>'),
        }
        complete=all(v is not None for v in signals.values())
        out.append({'ts_code':code,'report_period':r.end_date.date().isoformat(),
                    'available_at':max(r.balance_published,r.income_published,r.cashflow_published).date().isoformat(),
                    'score':sum(v is True for v in signals.values()) if complete else None,
                    'partial_positive_count':sum(v is True for v in signals.values()),
                    'signals':signals,'missing_signals':[k for k,v in signals.items() if v is None],
                    'status':'complete' if complete else 'incomplete',
                    'limitations':'F-Score 原为价值投资财务强弱参考；非财务舞弊模型。当前为年报会计数据口径适配版，债务仅用lt_borr。'})
    return out


def regguard_red_flags(balance: pd.DataFrame, income: pd.DataFrame,
                       cashflow: pd.DataFrame, as_of: str,
                       cfo_ni_threshold: float = 0.5,
                       receivable_growth_gap: float = 0.15,
                       current_ratio_threshold: float = 1.0) -> list[dict]:
    """Transparent REVIEW clues (R1/R2/R7), not fraud claims.
    Thresholds are engineering prototypes, NOT regulatory-prescribed cutoffs.
    """
    if not (0 < cfo_ni_threshold <= 2 and 0 < receivable_growth_gap <= 2 and 0 < current_ratio_threshold <= 5):
        raise ValueError('Threshold out of allowed prototype range')
    f = _merge(balance,income,as_of,cashflow)
    out=[]
    for code,g in f.groupby('ts_code'):
        if not _nonfinancial(balance,code):continue
        g=g.sort_values('end_date')
        if len(g)<2 or g.iloc[-1].end_date.year-g.iloc[-2].end_date.year!=1:continue
        r,p=g.iloc[-1],g.iloc[-2]
        ni,cfo=_numeric(r,'n_income'),_numeric(r,'n_cashflow_act')
        ocf_ratio=_divide(cfo,ni) if ni is not None and ni>0 else None
        flags=[]
        def flag(id, value, threshold, triggered, data_fields):
            if triggered is True:
                flags.append({'rule_id':id,'rule_version':'MVP-1','observed':value,'threshold':threshold,
                              'source_fields':data_fields,'report_period':r.end_date.date().isoformat(),
                              'evidence_level':'financial_statement_fields_only',
                              'review_status':'unreviewed',
                              'caution':'初筛线索不是舞弊事实或监管定性；请核查财报原文及行业差异。'})
        flag('R1_cash_earnings_gap',ocf_ratio,cfo_ni_threshold,
             (ocf_ratio<cfo_ni_threshold) if ocf_ratio is not None else None,['n_income','n_cashflow_act'])
        def growth(field):
            a,b=_numeric(r,field),_numeric(p,field)
            return a/b-1 if a is not None and b is not None and b>0 else None
        g_ar,g_rev=growth('accounts_receiv'),growth('revenue')
        gap=(g_ar-g_rev) if g_ar is not None and g_rev is not None else None
        flag('R2_receivables_outgrow_revenue',gap,receivable_growth_gap,
             gap>receivable_growth_gap if gap is not None else None,['accounts_receiv','revenue'])
        cur_ratio=_divide(_numeric(r,'total_cur_assets'),_numeric(r,'total_cur_liab'))
        flag('R7_low_current_ratio',cur_ratio,current_ratio_threshold,
             cur_ratio<current_ratio_threshold if cur_ratio is not None else None,['total_cur_assets','total_cur_liab'])
        out.append({'ts_code':code,'report_period':r.end_date.date().isoformat(),
                    'available_at':max(r.balance_published,r.income_published,r.cashflow_published).date().isoformat(),
                    'review_flags':flags,'rule_count':len(flags),
                    'limitations':'阈值是待行业校准的示例；不输出舞弊概率或综合定罪评分。'})
    return out


def audit_filing_triage(filings: pd.DataFrame, as_of: str) -> list[dict]:
    """Title-only risk triage; does not claim to read disclosure PDF bodies."""
    required={'announcement_date','ticker','announcement_title','url'}
    if not required.issubset(filings.columns):raise ValueError(f'Missing {sorted(required-set(filings.columns))}')
    patterns={
        'audit_opinion':['保留意见','否定意见','无法表示意见','非标准审计意见','非标审计意见'],
        'auditor_change':['变更会计师事务所','改聘会计师事务所','更换审计机构','变更审计机构'],
        'restatement':['会计差错更正','追溯调整','财务报表更正'],
        'legal_disclosure':['诉讼','仲裁','立案调查','行政处罚'],
        'pledge_or_freeze':['股权质押','股份冻结','司法冻结'],
        'guarantees':['对外担保','违规担保'],
        'shareholder_sale':['减持计划','减持股份']
    }
    f=filings.copy();f['date']=pd.to_datetime(f.announcement_date.astype(str),errors='coerce')
    f=f[f.date.notna() & (f.date<=pd.Timestamp(as_of))]
    out=[]
    for _,r in f.iterrows():
        typ=[k for k,tokens in patterns.items() if any(token in str(r.announcement_title) for token in tokens)]
        if typ:
            out.append({'ts_code':str(r.ticker),'published_at':r.date.date().isoformat(),
                        'title':str(r.announcement_title),'categories':typ,'source_url':str(r.url),
                        'evidence_level':'title_only','review_status':'unreviewed',
                        'caution':'标题命中不代表正文结论或已确认的违法/舞弊事实。'})
    return sorted(out,key=lambda r:r['published_at'],reverse=True)


def beneish_m_score(balance: pd.DataFrame, income: pd.DataFrame,
                    cashflow: pd.DataFrame, as_of: str) -> list[dict]:
    """Eight-variable Beneish M-score; A-share use ONLY as exploratory peer ranking.

    Conservative: if even one denominator/necessary account is absent, refuse
    to calculate rather than silently substitute zero. Coefficients from the
    commonly published Beneish (1999) variant, which was US-calibrated.
    This never emits a fraud label or an estimated fraud probability.
    """
    f = _merge(balance,income,as_of,cashflow)
    out=[]
    for code,g in f.groupby('ts_code'):
        if not _nonfinancial(balance,code):
            out.append({'ts_code':code,'score':None,'status':'unsupported_financial_company'});continue
        g=g.sort_values('end_date')
        if len(g)<2 or g.iloc[-1].end_date.year-g.iloc[-2].end_date.year!=1:
            out.append({'ts_code':code,'score':None,'status':'insufficient_consecutive_annual_reports'});continue
        r,p=g.iloc[-1],g.iloc[-2]
        reasons=[]
        def amount(row,key):
            v=_numeric(row,key)
            if v is None:reasons.append(f'missing {key}')
            return v
        def div(a,b,label):
            if a is None or b is None or b<=0:
                reasons.append(f'undefined {label} denominator / account')
                return None
            return a/b
        def any_sum(row,cols):
            items=[amount(row,c) for c in cols]
            return sum(items) if all(v is not None for v in items) else None
        def gm(row):
            rev,cogs=amount(row,'revenue'),amount(row,'oper_cost')
            return div(rev-cogs if rev is not None and cogs is not None else None,rev,'gross margin')
        def ar_sales(row):return div(amount(row,'accounts_receiv'),amount(row,'revenue'),'receivables/sales')
        def asset_quality(row):
            ta=amount(row,'total_assets');cur=amount(row,'total_cur_assets');ppe=amount(row,'fix_assets')
            share=div(cur+ppe if cur is not None and ppe is not None else None,ta,'AQI')
            return None if share is None else 1-share
        def dep_rate(row):
            dep=amount(row,'depr_fa_coga_dpba');ppe=amount(row,'fix_assets')
            return div(dep,dep+ppe if dep is not None and ppe is not None else None,'depreciation rate')
        def sga_sales(row):
            sga=any_sum(row,['sell_exp','admin_exp'])
            return div(sga,amount(row,'revenue'),'SG&A ratio')
        def leverage(row):
            debt=any_sum(row,['total_cur_liab','lt_borr','bond_payable'])
            return div(debt,amount(row,'total_assets'),'leverage')
        def profit_accrual(row):
            ni,cfo=amount(row,'n_income'),amount(row,'n_cashflow_act')
            return div(ni-cfo if ni is not None and cfo is not None else None,
                       amount(row,'total_assets'),'TATA')
        dsri=div(ar_sales(r),ar_sales(p),'DSRI')
        gmi=div(gm(p),gm(r),'GMI')
        aqi=div(asset_quality(r),asset_quality(p),'AQI')
        sgi=div(amount(r,'revenue'),amount(p,'revenue'),'SGI')
        depi=div(dep_rate(p),dep_rate(r),'DEPI')
        sgai=div(sga_sales(r),sga_sales(p),'SGAI')
        lvgi=div(leverage(r),leverage(p),'LVGI')
        tata=profit_accrual(r)
        values={'DSRI':dsri,'GMI':gmi,'AQI':aqi,'SGI':sgi,'DEPI':depi,'SGAI':sgai,'LVGI':lvgi,'TATA':tata}
        coef={'DSRI':0.920,'GMI':0.528,'AQI':0.404,'SGI':0.892,
              'DEPI':0.115,'SGAI':-0.172,'LVGI':-0.327,'TATA':4.679}
        contributions={k:coef[k]*values[k] for k in values} if all(v is not None and np.isfinite(v) for v in values.values()) else None
        score=-4.840+sum(contributions.values()) if contributions is not None else None
        out.append({'ts_code':code,'report_period':r.end_date.date().isoformat(),
                    'available_at':max(r.balance_published,r.income_published,r.cashflow_published).date().isoformat(),
                    'score':float(score) if score is not None else None,
                    'variables':values,'contributions':contributions,'missing_or_undefined':sorted(set(reasons)),
                    'status':'ok' if score is not None else 'insufficient_inputs',
                    'limitations':'Beneish 1999 美国样本系数未经本项目A股校准；不使用固定阈值断言舞弊，不能当成概率。依赖年度同口径且公开时点有效的财报字段。'})
    return out
