"""Matched senior/mezzanine cashflows for the revised Baghdad scope.

Government import downpayments follow invoices; the remaining appropriation
is allocated to local invoices. The 25% limit applies to total capital, not
each monthly invoice. Deferred junior coupons and PIK are debt, never income.
"""
from copy import deepcopy
import math
from osr_mech.provenance import stable_sum as sum

from baghdad_funding_analysis import add_draw, debt_month, prepay_vintages


def positive(value, name, *, zero=False):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or value < 0 or (not zero and value == 0):
        raise ValueError('Invalid '+name)
    return value


def six_months(rows, denomination=1000000):
    result=[]
    for start in range(0,len(rows),6):
        part=rows[start:start+6]
        values={key:(part[-1][key] if key.startswith('closing_') else sum(r[key] for r in part))
                for key in rows[0] if key not in {'month','senior_dscr'}}
        face=values['domestic_bonds_draw_native']+values['green_bonds_draw_native']
        values.update(tranche_id=f'BGD-R-H{start//6+1:03d}',start_month=part[0]['month'],end_month=part[-1]['month'],
            bond_face_iqd=face,bond_units=math.ceil(face/denomination),
            rounded_bond_face_iqd=math.ceil(face/denomination)*denomination,
            rounding_is_placement_envelope_not_cash=True,
            maximum_cash_residual_usd=max(abs(r['cash_residual_usd']) for r in part))
        result.append(values)
    return result


def simulate(capital, operating, funding, options, assumptions, *, mezzanine=False, commercial_gap=False, extras=True):
    """Prices the same scope with/without a genuinely subordinated IQD tranche."""
    cfg=assumptions['model'];fc=assumptions['financing'];mc=assumptions['mezzanine']
    fx=positive(cfg['iqd_per_usd'],'FX');total=sum(r['capex'] for r in capital.values())
    positive(total,'total capital')
    for section in (cfg,fc,mc):
        for key,value in section.items():
            if isinstance(value,(float,int)) and not isinstance(value,bool):positive(value,key,zero=True)
    for key in ('government_capital_share','government_import_share','chinese_import_share'):
        if not 0<=cfg[key]<=1:raise ValueError('Invalid '+key)
    if not 0<=fc['residual_bond_share']<=1:raise ValueError('Invalid senior bond fraction')
    imports=sum(r['imports'] for r in capital.values());local=total-imports
    for req in capital.values():
        positive(req['capex'],'capital',zero=True);positive(req['imports'],'imports',zero=True)
        if req['imports']>req['capex']+.001:raise ValueError('Imports exceed invoice')
    gov_import=cfg['government_import_share']*imports
    gov_local=cfg['government_capital_share']*total-gov_import
    if gov_local<-.01:raise ValueError('Import downpayments exceed 25% government capital ceiling')
    if abs(cfg['government_import_share']+cfg['chinese_import_share']-1)>1e-9:raise ValueError('Import funding must reconcile')
    local_gov_fraction=max(0,gov_local)/local if local else 0
    if not 0<=local_gov_fraction<=1:raise ValueError('Invalid local government allocation')
    terms={key:deepcopy(funding[key]) for key in ('chinese_export_credit','domestic_bonds','bank_credit')}
    terms['green_bonds']=dict(terms['domestic_bonds'],annual_rate=options['green']['blended_rate'],
        grace_months_from_draw=options['green']['blended_grace_months'],repayment_months=options['green']['blended_repayment_months'],
        arrangement_fee=options['green']['arrangement_fee'])
    for name,t in terms.items():
        positive(t['annual_rate'],name+' coupon',zero=True)
        if t['currency']!=('USD' if name=='chinese_export_credit' else 'IQD'):raise ValueError('Invalid debt currency')
    for key in ('cash_coupon','pik_coupon','overdue_interest_annual_rate','arrangement_fee','minimum_senior_dscr_for_junior_payment'):
        positive(mc[key],key,zero=True)
    if not 0<=mc['share_of_domestic_residual']<=1 or not isinstance(mc['maturity_months_from_draw'],int) or mc['maturity_months_from_draw']<1:
        raise ValueError('Invalid mezzanine allocation/maturity')
    if mc['currency']!='IQD' or mc['automatic_refinancing'] or mc['equity_conversion_assumed'] or not mc['cash_coupon_deferrable_until_maturity']:
        raise ValueError('Unsupported junior terms')
    eligible=sum(max(0,r.get('candidate_capex',0)-r.get('candidate_imports',0)) for m,r in capital.items() if m>=options['additional_sources']['climate_grant_first_month'])
    grant_total=options['additional_sources']['climate_capital_grant_usd'] if extras else 0
    if grant_total>eligible:raise ValueError('Grant exceeds eligible expenditures')
    vintages={name:[] for name in terms};junior=[];cash=gap=reserve=buffer=0.;rows=[]
    gap_rate=fc['commercial_gap_rate'] if commercial_gap else fc['gap_rate']
    cap=fc['gap_cap_iqd']/fx;fee_rate=fc['gap_draw_fee']
    first=min(p['opening_month'] for p in operating[0]['phases']);last=max(p['opening_month'] for p in operating[0]['phases'])
    annual_import_cohorts={year:[(m,r['imports']*cfg['chinese_import_share']) for m,r in sorted(capital.items()) if m//12==year and r['imports']>0] for year in {m//12 for m in capital}}
    for op in operating:
        month=op['month'];req=capital.get(month,{});capex=req.get('capex',0);imp=req.get('imports',0)
        grant=grant_total*max(0,req.get('candidate_capex',0)-req.get('candidate_imports',0))/eligible if eligible and month>=options['additional_sources']['climate_grant_first_month'] else 0
        govt_usd=cfg['government_import_share']*imp;govt_iqd=local_gov_fraction*(capex-imp)*fx
        china=cfg['chinese_import_share']*imp;residual=capex-govt_usd-govt_iqd/fx-china-grant
        if residual<-.02:raise ValueError('Capital sources exceed invoice uses')
        residual=max(0,residual);junior_draw=residual*mc['share_of_domestic_residual'] if mezzanine else 0
        senior_residual=residual-junior_draw;bonds=senior_residual*fc['residual_bond_share'];bank=senior_residual-bonds
        green_candidate=max(0,req.get('candidate_capex',0)-req.get('candidate_imports',0))
        green=min(bonds,green_candidate*fc['residual_bond_share']*options['green']['share_of_candidate_bonds']) if extras else 0
        draws=dict(chinese_export_credit=china,domestic_bonds=bonds-green,green_bonds=green,bank_credit=bank)
        row=dict(month=month,capex_usd=capex,imports_usd=imp,government_usd_cash=govt_usd,government_iqd_cash=govt_iqd,
            climate_grant_iqd=grant*fx,mezzanine_draw_iqd=junior_draw*fx)
        service=fees=0.;opening_cash=cash;opening_gap=gap
        for name,t in terms.items():
            conversion=1 if t['currency']=='USD' else fx
            add_draw(vintages[name],month,draws[name]*conversion,t)
            interest,principal=debt_month(vintages[name],month,t)
            fee=draws[name]*t['arrangement_fee']
            if name=='chinese_export_credit':
                cohort=annual_import_cohorts.get(month//12,[])
                if cohort and month>=cohort[0][0]:fee+=sum(v for m,v in cohort if m>month)*t['undrawn_commitment_fee']/12
            if name=='green_bonds':fee+=(sum(v['balance'] for v in vintages[name])+principal)/fx*options['green']['annual_guarantee_fee']/12
            service+=(interest+principal)/conversion;fees+=fee
            row.update({name+'_draw_native':draws[name]*conversion,name+'_interest_native':interest,
                name+'_principal_native':principal,name+'_fees_native':fee*conversion,name+'_early_principal_native':0.,name+'_early_premium_native':0.})
        junior_fee=junior_draw*mc['arrangement_fee'];fees+=junior_fee
        if junior_draw:junior.append(dict(month=month,balance=junior_draw*fx,overdue_interest=0.,defaulted=False))
        desired=service*fc['debt_service_reserve_months']
        deposit=max(0,desired-reserve);release=max(0,reserve-desired);reserve+=deposit-release
        target=op['opex_usd']*fc['operating_buffer_months']+op.get('restricted_working_capital_usd',0)
        bd=max(0,target-buffer);br=max(0,buffer-target);buffer+=bd-br
        source=options['additional_sources'];rights=0.
        if extras and month>=source['rights_first_month']:
            age=month-source['rights_first_month']
            if age%6==0 and age//6<source['rights_tranches']:rights=source['net_development_rights_usd']/source['rights_tranches']
        opened=sum(p['weight'] for p in op['phases'] if month>=p['opening_month'])
        extra=source['incremental_net_local_receipts_annual_usd']/12*opened if extras and first<=month<last+funding['model']['operating_years']*12 else 0.
        rev=op['revenue_usd'];opex=op['opex_usd'];available=cash+rev+extra+rights-opex-service-fees+release-deposit+br-bd
        gap_interest=opening_gap*gap_rate/12;available-=gap_interest;gap_draw=gap_fee=gap_repayment=support=0.
        if available<0:
            denominator=1-fee_rate-gap_rate/24
            if denominator<=0:raise ValueError('Gap draw costs consume all proceeds')
            gap_draw=min(-available/denominator,max(0,cap-gap));gap_fee=gap_draw*fee_rate
            gap_interest+=gap_draw*gap_rate/24;gap+=gap_draw
            available+=gap_draw-gap_fee-gap_draw*gap_rate/24;support=max(0,-available);available=max(0,available)
        cfads=rev+extra-opex;senior_due=service+gap_interest
        dscr=cfads/senior_due if senior_due>0 else None
        junior_cash=junior_pik=junior_deferred=junior_principal=junior_due=junior_unpaid_due=overdue_accrued=overdue_paid=0.
        # Borrowed or uncovered cash cannot be paid down the junior waterfall.
        allow_junior=gap_draw<1e-9 and support<1e-9 and cfads>0 and (dscr is None or dscr>=mc['minimum_senior_dscr_for_junior_payment'])
        for loan in junior:
            age=month-loan['month']
            opening=loan['balance'];factor=.5 if loan['month']==month else 1
            if age<=mc['maturity_months_from_draw']:
                pik=opening*mc['pik_coupon']/12*factor;coupon=opening*mc['cash_coupon']/12*factor
                paid=min(coupon,max(0,available)*fx) if allow_junior else 0.
                available-=paid/fx;deferred=coupon-paid;loan['balance']+=pik+deferred
                junior_cash+=paid;junior_pik+=pik;junior_deferred+=deferred
            else:
                # No rolling PIK extension after the contractual balloon.
                # Price simple overdue interest separately; no interest-on-arrears.
                accrued=opening*mc['overdue_interest_annual_rate']/12
                loan['overdue_interest']+=accrued;overdue_accrued+=accrued
                paid=min(loan['overdue_interest'],max(0,available)*fx) if allow_junior else 0.
                loan['overdue_interest']-=paid;available-=paid/fx;overdue_paid+=paid
            if age>=mc['maturity_months_from_draw']:
                due=loan['balance'];paid=min(due,available*fx) if allow_junior else 0
                available-=paid/fx;loan['balance']-=paid;junior_principal+=paid
                if age==mc['maturity_months_from_draw']:junior_due+=due;junior_unpaid_due+=due-paid
                if loan['balance']>.01:loan['defaulted']=True
        early_usd=early_fees=0.
        if gap_draw<1e-9 and support<1e-9:
            gap_repayment=min(gap,available);gap-=gap_repayment;available-=gap_repayment
            order=sorted(terms,key=lambda k:-terms[k]['annual_rate'])
            for name in order:
                if not options['prepayments']['eligible'][name]:continue
                conversion=1 if terms[name]['currency']=='USD' else fx
                principal,premium=prepay_vintages(vintages[name],available*conversion,options['prepayments']['premium'][name],month,options['prepayments']['minimum_age_months'][name])
                available-=(principal+premium)/conversion;early_usd+=principal/conversion;early_fees+=premium/conversion
                row[name+'_early_principal_native']=principal;row[name+'_early_premium_native']=premium
        cash=max(0,available)
        for name in terms:row['closing_'+name+'_native']=sum(v['balance'] for v in vintages[name])
        sources=govt_usd+govt_iqd/fx+china+bonds+bank+junior_draw+grant+rev+extra+rights+gap_draw+support+release+br
        uses=capex+opex+service+fees+deposit+bd+gap_interest+gap_fee+gap_repayment+early_usd+early_fees+(junior_cash+junior_principal+overdue_paid)/fx
        row.update(revenue_iqd=rev*fx,opex_iqd=opex*fx,extra_receipts_iqd=extra*fx,rights_receipts_iqd=rights*fx,
            senior_service_iqd_equivalent=service*fx,senior_dscr=dscr,mezzanine_interest_cash_iqd=junior_cash,
            mezzanine_pik_iqd=junior_pik,mezzanine_deferred_coupon_iqd=junior_deferred,mezzanine_principal_iqd=junior_principal,
            mezzanine_fee_iqd=junior_fee*fx,mezzanine_balloon_due_iqd=junior_due,mezzanine_unpaid_balloon_at_maturity_iqd=junior_unpaid_due,
            closing_mezzanine_principal_iqd=sum(v['balance'] for v in junior),
            mezzanine_overdue_interest_accrued_iqd=overdue_accrued,mezzanine_overdue_interest_paid_iqd=overdue_paid,
            closing_mezzanine_overdue_interest_iqd=sum(v['overdue_interest'] for v in junior),
            closing_mezzanine_iqd=sum(v['balance']+v['overdue_interest'] for v in junior),
            closing_overdue_mezzanine_iqd=sum(v['balance']+v['overdue_interest'] for v in junior if month-v['month']>=mc['maturity_months_from_draw']),
            gap_draw_iqd=gap_draw*fx,gap_interest_iqd=gap_interest*fx,gap_fee_iqd=gap_fee*fx,gap_repayment_iqd=gap_repayment*fx,
            closing_gap_iqd=gap*fx,unfunded_support_iqd=support*fx,reserve_deposit_iqd=deposit*fx,reserve_release_iqd=release*fx,
            closing_reserve_iqd=reserve*fx,buffer_deposit_iqd=bd*fx,buffer_release_iqd=br*fx,closing_buffer_iqd=buffer*fx,
            closing_cash_iqd=cash*fx,cash_residual_usd=opening_cash+sources-uses-cash,
            capital_residual_usd=govt_usd+govt_iqd/fx+china+bonds+bank+junior_draw+grant-capex)
        rows.append(row)
    summed=lambda key:sum(r[key] for r in rows)
    maxcash=max(abs(r['cash_residual_usd']) for r in rows);maxcap=max(abs(r['capital_residual_usd']) for r in rows)
    mezz_error=0.;balance=0.
    overdue_balance=0.;senior_error=0.;senior_balances={name:0. for name in terms}
    for row in rows:
        balance+=row['mezzanine_draw_iqd']+row['mezzanine_pik_iqd']+row['mezzanine_deferred_coupon_iqd']-row['mezzanine_principal_iqd']
        mezz_error=max(mezz_error,abs(balance-row['closing_mezzanine_principal_iqd'])/fx)
        overdue_balance+=row['mezzanine_overdue_interest_accrued_iqd']-row['mezzanine_overdue_interest_paid_iqd']
        mezz_error=max(mezz_error,abs(overdue_balance-row['closing_mezzanine_overdue_interest_iqd'])/fx)
        for name,t in terms.items():
            senior_balances[name]+=row[name+'_draw_native']-row[name+'_principal_native']-row[name+'_early_principal_native']
            senior_error=max(senior_error,abs(senior_balances[name]-row['closing_'+name+'_native'])/(1 if t['currency']=='USD' else fx))
    if max(maxcash,maxcap,mezz_error,senior_error)>.02:raise ValueError('Recalculated funding/cash/junior debt does not reconcile')
    balances=[r['closing_gap_iqd']+r['closing_mezzanine_iqd']+sum(r['closing_'+n+'_native']*(fx if t['currency']=='USD' else 1) for n,t in terms.items()) for r in rows]
    active=[r['month'] for r,b in zip(rows,balances) if b>.01]
    metrics=dict(total_capital_usd=total,imported_invoices_usd=imports,usd_capital_intensity=imports/total,
        government_capital_usd_equivalent=summed('government_usd_cash')+summed('government_iqd_cash')/fx,
        government_share=(summed('government_usd_cash')+summed('government_iqd_cash')/fx)/total,
        chinese_usd_draw=summed('chinese_export_credit_draw_native'),mezzanine_draw_iqd=summed('mezzanine_draw_iqd'),
        mezzanine_pik_iqd=summed('mezzanine_pik_iqd'),mezzanine_deferred_coupon_iqd=summed('mezzanine_deferred_coupon_iqd'),
        terminal_mezzanine_iqd=rows[-1]['closing_mezzanine_iqd'],terminal_overdue_mezzanine_iqd=rows[-1]['closing_overdue_mezzanine_iqd'],
        unpaid_junior_balloon_at_maturity_iqd=summed('mezzanine_unpaid_balloon_at_maturity_iqd'),junior_defaulted_vintages=sum(v['defaulted'] for v in junior),
        peak_gap_iqd=max(r['closing_gap_iqd'] for r in rows),terminal_gap_iqd=rows[-1]['closing_gap_iqd'],
        terminal_all_debt_iqd=balances[-1],unfunded_support_iqd=summed('unfunded_support_iqd'),terminal_cash_iqd=rows[-1]['closing_cash_iqd'],
        maximum_cash_residual_usd=maxcash,maximum_capital_residual_usd=maxcap,maximum_mezzanine_balance_residual_usd=mezz_error,
        maximum_senior_balance_residual_usd=senior_error,
        company_npv_before_finance_usd=sum((r['revenue_iqd']/fx+r['extra_receipts_iqd']/fx+r['rights_receipts_iqd']/fx-r['opex_iqd']/fx-r['capex_usd'])/(1+fc['senior_discount_rate'])**(r['month']/12) for r in rows),
        all_debt_cleared_month=active[-1]+1 if active and active[-1]<rows[-1]['month'] else None,
        total_cash_finance_cost_iqd=sum(sum((r[n+'_interest_native']+r[n+'_fees_native']+r[n+'_early_premium_native'])*(fx if t['currency']=='USD' else 1) for n,t in terms.items())+r['gap_interest_iqd']+r['gap_fee_iqd']+r['mezzanine_interest_cash_iqd']+r['mezzanine_overdue_interest_paid_iqd']+r['mezzanine_fee_iqd'] for r in rows),
        total_accrued_junior_interest_iqd=summed('mezzanine_pik_iqd')+summed('mezzanine_deferred_coupon_iqd')+summed('mezzanine_interest_cash_iqd')+summed('mezzanine_overdue_interest_accrued_iqd'),
        financing_committed=False,dividends_iqd=0)
    return dict(metrics=metrics,monthly=rows,semiannual=six_months(rows),
        status='unquoted-matched-scope-senior-junior-sensitivity',government_local_invoice_fraction=local_gov_fraction,
        reserve_policy='Six months of scheduled senior service funded from first draw; three months OPEX plus explicit industrial working capital',
        mezzanine_terms=mc if mezzanine else None,senior_terms=terms,gap_rate=gap_rate,
        automatic_refinancing=False,all_debt_clearance_requires_funding_gaps_and_no_junior_default=metrics['unfunded_support_iqd']<.02 and not metrics['junior_defaulted_vintages'])
