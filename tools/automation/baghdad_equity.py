#!/usr/bin/env python3
"""Baghdad ordinary equity, funding gates and consolidated pro-forma accounts.

A 100%-owned subsidiary holding case replaces earlier subsidiary private equity.
No new cash is created by relabelling government funding as paid-in equity.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import csv
import hashlib
import html
import json
import math
from pathlib import Path
import tomllib
from baghdad_funding_analysis import CORE, add_draw, debt_month, prepay_vintages
from baghdad_financing_redesign import ROOT, CITY, npv, digest, write_csv

OUT = CITY/'engineering/equity'
GROUPS = ('government', 'iraqi_private', 'foreign_private')


def equity_irr(flows):
    """Annual effective IRR; undefined without both investment and a return."""
    if not any(v<0 for _,v in flows) or not any(v>0 for _,v in flows): return None
    # Report ambiguous sign patterns rather than selecting a favourable root.
    signs=[1 if v>0 else -1 for _,v in flows if abs(v)>.01]
    changes=sum(a!=b for a,b in zip(signs,signs[1:]))
    if changes>1: return None
    lo, hi = -.9999, 20.
    if npv(flows, lo)*npv(flows, hi)>0: return None
    for _ in range(100):
        mid=(lo+hi)/2
        if npv(flows, mid)>0: lo=mid
        else: hi=mid
    return (lo+hi)/2


def validate(config):
    m,a=config['model'],config['accounting']
    for key in ('nominal_share_value_iqd','subscription_price_iqd','later_primary_price_iqd'):
        if not math.isfinite(m[key]) or m[key]<=0: raise ValueError('invalid share price')
    if min(m['subscription_price_iqd'],m['later_primary_price_iqd'])<m['nominal_share_value_iqd']: raise ValueError('below-par issue not supported')
    for key in ('founder_fraction','primary_issue_fee_fraction','private_iraqi_fraction','minimum_state_nominal_ownership','minimum_iraqi_ownership'):
        if isinstance(m[key],bool) or not 0<=m[key]<=1: raise ValueError('invalid ownership/fee fraction')
    for key in ('founder_tranches','founder_interval_months'):
        if isinstance(m[key],bool) or not isinstance(m[key],int) or m[key]<=0: raise ValueError('invalid tranche count')
    if a['terminal_asset_sale_usd']!=0: raise ValueError('unvalued terminal assets cannot be sold in model')
    if not 0<=a['corporate_tax_fraction']<=1: raise ValueError('invalid tax fraction')
    if not 0<=a['profit_retention_fraction']<=1:raise ValueError('invalid profit retention')
    for key in ('rail_asset_life_years','train_asset_life_years','solar_asset_life_years','factory_asset_life_years'):
        if not math.isfinite(a[key]) or a[key]<=0:raise ValueError('invalid asset life')


def consolidated_inputs(case, phases, factory, equity, *, delay_months=0):
    """Cancel every transfer, retain external cash costs and move train resources
    from factory expense to group train PPE at their actual purchase dates.
    Prior subsidiary equity is replaced, never added to the new subscriptions.
    """
    entities=case['entities']; transfers=case['intercompany_monthly']; rows=[]
    for t in transfers:
        month=t['month']; e=[v['monthly'][month] for v in entities.values()]
        original=sum(entities[name]['monthly'][month]['capex_usd'] for name in ('rail','energy','factory'))
        invoice, resource=t['train_rail_capital_invoice_usd'],t['factory_resource_purchase_usd']
        imported=2*sum(v['chinese_export_credit_draw_native'] for v in e)-.35*invoice+.35*resource
        original_external=original-invoice+resource
        revenue=sum(v['revenue_iqd'] for v in e)/1300-t['ppa_energy_receipt_usd']-t['train_factory_receipt_usd']-t['capacity_factory_receipt_usd']-t['rights_rail_receipt_usd']
        opex=sum(v['opex_iqd'] for v in e)/1300-t['ppa_rail_payment_usd']-t['capacity_rail_payment_usd']-resource
        physical=original_external+t['physical_property_build_usd']
        expected=case['consolidated_monthly'][month]['consolidated_unlevered_cash_usd']
        if abs(revenue-opex-physical-expected)>.02: raise ValueError('group resource consolidation fails')
        solar=entities['energy']['monthly'][month]['capex_usd']; plant=entities['factory']['monthly'][month]['capex_usd']
        row=dict(month=month+delay_months,revenue_usd=revenue,opex_usd=opex,
            physical_capital_usd=physical, original_capital_usd=original_external, imported_capital_usd=imported,
            government_capital_usd=.25*original_external, government_usd_cash=.5*imported,
            property_build_usd=t['physical_property_build_usd'], property_sales_usd=t['gross_property_sales_usd'],
            rail_capital_usd=original-invoice-solar-plant, train_capital_usd=resource,
            solar_capital_usd=solar, factory_capital_usd=plant,
            factory_warranty_cash_usd=t['factory_warranty_locked_cash_usd'], consolidation_residual_usd=revenue-opex-physical-expected)
        if delay_months:
            # Existing annual price indices are from close, not restarted at NTP.
            step=(1.05)**((month+delay_months)//12-month//12)
            # Sale contracts remain fixed nominal; fares/maintenance are indexed.
            row['revenue_usd']=t['gross_property_sales_usd']+(revenue-t['gross_property_sales_usd'])*step
            row['opex_usd']=(opex-t['property_transaction_cost_usd'])*step+t['property_transaction_cost_usd']
        row['tax_operating_bases_usd']={name:(entities[name]['monthly'][month]['revenue_iqd']-entities[name]['monthly'][month]['opex_iqd'])/1300 for name in entities}
        row['internal_rights_tax_cost_usd']=t['rights_developer_capital_payment_usd']
        if delay_months:
            # Existing internal invoices and property sales remain fixed nominal.
            # Index rail/energy operations and the factory's capacity/caretaker
            # components only; never index sale proceeds absent a new contract.
            tb=row['tax_operating_bases_usd']
            tb['rail']=(tb['rail']-t['rights_rail_receipt_usd'])*step+t['rights_rail_receipt_usd']
            tb['energy']*=step
            fixed=t['train_factory_receipt_usd']-resource
            tb['factory']=(tb['factory']-fixed)*step+fixed
        rows.append(row)
    if delay_months:
        zero={key:(dict(rail=0.,energy=0.,factory=0.,development=0.) if key=='tax_operating_bases_usd' else 0.) for key in rows[0]}; rows=[dict(zero,month=m) for m in range(delay_months)]+rows
    # Close the final accounting stub and pay its tax in the next month.
    blank={key:(dict(rail=0.,energy=0.,factory=0.,development=0.) if key=='tax_operating_bases_usd' else 0.) for key in rows[0]}
    rows.append(dict(blank,month=rows[-1]['month']+1))
    return dict(rows=rows,phases=[dict(p,opening_month=p['opening_month']+delay_months) for p in phases],
        factory_ready_month=math.ceil((factory['factory_ready_working_day']+30)*12/260)+delay_months,
        factory_close_month=case['factory']['warranty_cash_release_month']+delay_months,
        land_opportunity_usd=case['development']['opportunity_cost_usd'],
        land_opportunity_month=case['development']['opportunity_cost_month']+delay_months,
        replaced_subsidiary_equity_iqd=case['metrics']['total_private_equity_iqd'])


def simulate_equity(inputs, config, funding, options, target_usd, *, success=1., premium=False,
                    government_as_equity=True, secondary=False, debt_caps=None, downside=False, later_success=None, aggregate_tax=False):
    """Native cash, shares and book-equity ledger with annual dividend gates.

    Failed capital subscriptions cannot draw an operating rescue facility or
    unapproved capital credit. A funded prefix ends at the first unmet invoice.
    """
    validate(config); m,a=config['model'],config['accounting']; fx=funding['model']['iqd_per_usd']
    if fx!=1300:raise ValueError('source entity ledgers use 1300 IQD/USD; regenerate them before changing FX')
    if not math.isfinite(target_usd) or target_usd<0 or not 0<=success<=1 or (later_success is not None and not 0<=later_success<=1):
        raise ValueError('invalid primary target or subscription success')
    phases=inputs['phases']; first=min(p['opening_month'] for p in phases); full=max(p['opening_month'] for p in phases)
    terms={name:dict(funding[name]) for name in CORE}
    if downside:
        for t in terms.values(): t['annual_rate']+=.02
    loans={name:[] for name in CORE}; cash=capital_cash=reserve=buffer=gap=0.
    gap_rate=.08 if downside else options['liquidity']['concessional_annual_rate']
    gap_fee=.01 if downside else options['liquidity']['concessional_draw_fee']; gap_cap=4e12/fx if downside else options['liquidity']['illustrative_cap_iqd']/fx
    shares={group:0. for group in GROUPS}; cf={group:[] for group in GROUPS}
    nominal=share_premium=issue_costs=net_income=dividends_paid=0.
    cumulative_gov_cash=primary_gross=primary_net=secondary_receipts=uncovered_total=0.
    assets={key:0. for key in ('rail','train','solar','factory')}; inventory=0.
    property_cost=sum(r['property_build_usd'] for r in inputs['rows']); sales=sum(r['property_sales_usd'] for r in inputs['rows'])
    pending=[]; requests={}; consumed_caps={}; result=[]; stop=None
    if not secondary:
        founder_total=target_usd*m['founder_fraction']
        for i in range(m['founder_tranches']):
            month=m['founder_first_month']+i*m['founder_interval_months']
            requests[month]=(founder_total/m['founder_tranches'],m['subscription_price_iqd'],'founder-primary')
        month=m['later_primary_month'];requests[month]=(target_usd-founder_total,m['later_primary_price_iqd'] if premium else m['subscription_price_iqd'],'conditional-later-primary')
    if target_usd and not government_as_equity: raise ValueError('private ordinary equity case needs contributed government equity')
    factory_impairment=0.; year_profit=0.
    year_tax_bases={name:0. for name in ('rail','energy','factory','development')}
    tax_payable=next_tax=0.
    rights_tax_basis=sum(r['internal_rights_tax_cost_usd'] for r in inputs['rows'])
    for source in inputs['rows']:
        month=source['month']; opening_cash=cash; opening_capital_cash=capital_cash
        govt=source['government_capital_usd']; gov_usd=source['government_usd_cash']; capex=source['physical_capital_usd']; imported=source['imported_capital_usd']
        gov_iqd=(govt-gov_usd)*fx
        gov_new_shares=govt*fx/m['subscription_price_iqd'] if government_as_equity else 0.
        temporary_gov=shares['government']+gov_new_shares
        if month in requests:
            amount,price,label=requests[month];pending.append(dict(amount=amount*(later_success if later_success is not None and label=='conditional-later-primary' else success),price=price,label=label))
        new_private=private_shares=fees_issue=0.; premium_increment=0.
        trial_pending=deepcopy(pending)
        for request in trial_pending:
            allowed=max(0.,temporary_gov*(1/m['minimum_state_nominal_ownership']-1)-shares['iraqi_private']-shares['foreign_private']-private_shares) if m['minimum_state_nominal_ownership'] else math.inf
            issued=min(request['amount']*fx/request['price'],allowed)
            paid=issued*request['price']/fx;request['amount']-=paid
            new_private+=paid;private_shares+=issued
            premium_increment+=issued*(request['price']-m['nominal_share_value_iqd'])
        fees_issue=new_private*m['primary_issue_fee_fraction']; new_net=new_private-fees_issue
        temp_capital_cash=capital_cash+new_net
        residual=max(0.,capex-govt-.5*imported)
        requested_bank=.25*residual;requested_bonds=.75*residual
        equity_bank=min(temp_capital_cash,requested_bank);temp_capital_cash-=equity_bank;requested_bank-=equity_bank
        equity_bonds=min(temp_capital_cash,requested_bonds);temp_capital_cash-=equity_bonds;requested_bonds-=equity_bonds
        draws=dict(chinese_export_credit=.5*imported,domestic_bonds=requested_bonds,bank_credit=requested_bank)
        # Six-month committed placement caps are based on the fully subscribed
        # counterfactual, never enlarged to cover a failed equity offer.
        if debt_caps is not None:
            period=month//6
            refused={name:max(0.,draws[name]-max(0.,debt_caps.get((period,name),0.)-consumed_caps.get((period,name),0.))) for name in CORE}
            if sum(refused.values())>.02:
                stop=dict(month=month,reason='Unplaced equity exceeds agreed six-month capital-credit envelope',
                    refused_capital_credit_usd=refused, withheld_physical_capital_usd=capex,
                    opening_month=None, full_opening_month=None,
                    resume_requirement='Fully place missing capital equity/approved credit, rephase all work, price hold/restart and accept physical evidence',
                    debt_not_forgiven=True, resolution_cashflows_modelled=False)
                break
        pending=trial_pending
        shares['government']=temporary_gov; shares['iraqi_private']+=private_shares*m['private_iraqi_fraction'];shares['foreign_private']+=private_shares*(1-m['private_iraqi_fraction'])
        nominal+=(gov_new_shares+private_shares)*m['nominal_share_value_iqd']
        share_premium+=premium_increment+gov_new_shares*(m['subscription_price_iqd']-m['nominal_share_value_iqd']);issue_costs+=fees_issue*fx
        cumulative_gov_cash+=govt;primary_gross+=new_private;primary_net+=new_net;capital_cash=temp_capital_cash
        shareholder_investment=dict(government=-govt*fx if government_as_equity else 0.,iraqi_private=-new_private*fx*m['private_iraqi_fraction'],foreign_private=-new_private*fx*(1-m['private_iraqi_fraction']))
        secondary_sale=0.
        if secondary and month==m['later_primary_month']:
            price=m['subscription_price_iqd'];transfer=min(target_usd*fx/price,max(0.,shares['government']-m['minimum_state_nominal_ownership']*sum(shares.values())))
            secondary_sale=transfer*price/fx;secondary_receipts+=secondary_sale
            shares['government']-=transfer;shares['iraqi_private']+=transfer*m['private_iraqi_fraction'];shares['foreign_private']+=transfer*(1-m['private_iraqi_fraction'])
            shareholder_investment['government']+=secondary_sale*fx
            shareholder_investment['iraqi_private']-=secondary_sale*fx*m['private_iraqi_fraction'];shareholder_investment['foreign_private']-=secondary_sale*fx*(1-m['private_iraqi_fraction'])
        row=dict(month=month,primary_new_shares=private_shares,
            primary_average_issue_price_iqd=new_private*fx/private_shares if private_shares else None,
            pending_subscription_cash_usd=sum(r['amount'] for r in pending),government_usd_cash=gov_usd,government_iqd_cash=gov_iqd,
            government_equity_iqd=govt*fx if government_as_equity else 0., government_capital_grant_iqd=0. if government_as_equity else govt*fx,
            primary_gross_subscription_iqd=new_private*fx,primary_issue_fee_iqd=fees_issue*fx,primary_net_subscription_iqd=new_net*fx,
            secondary_share_sale_company_receipt_iqd=0.,secondary_share_sale_seller_receipt_iqd=secondary_sale*fx,
            private_equity_capital_use_iqd=(equity_bank+equity_bonds)*fx,physical_capital_iqd=capex*fx,
            revenue_iqd=source['revenue_usd']*fx,opex_iqd=source['opex_usd']*fx)
        interest=principal=core_fees=early=early_fees=0.
        for name in CORE:
            t=dict(terms[name]);conversion=1 if t['currency']=='USD' else fx
            if name!='chinese_export_credit':
                # Long-lived group borrowing: no principal before full network.
                t.update(grace_months_from_draw=max(0,full-month-1),repayment_months=240 if name=='bank_credit' else 216)
            add_draw(loans[name],month,draws[name]*conversion,t)
            paid_interest,paid_principal=debt_month(loans[name],month,t)
            interest+=paid_interest/conversion;principal+=paid_principal/conversion
            fee=draws[name]*t['arrangement_fee']
            if name=='chinese_export_credit':
                cohort=[r for r in inputs['rows'] if r['month']//12==month//12 and r['imported_capital_usd']>0]
                if cohort and month>=cohort[0]['month']:fee+=sum(.5*r['imported_capital_usd'] for r in cohort if r['month']>month)*t['undrawn_commitment_fee']/12
            core_fees+=fee;consumed_caps[(month//6,name)]=consumed_caps.get((month//6,name),0.)+draws[name]
            row.update({name+'_draw_native':draws[name]*conversion,name+'_interest_native':paid_interest,name+'_principal_native':paid_principal,name+'_fees_native':fee*conversion})
        opened=sum(p['weight'] for p in phases if month>=p['opening_month'])
        depreciation=impairment=0.
        asset_depreciation={}
        for key in assets:
            assets[key]+=source[key+'_capital_usd']
            active=(month>=inputs['factory_ready_month']) if key=='factory' else month>=first
            fraction=1 if key=='factory' else opened
            cost=sum(r[key+'_capital_usd'] for r in inputs['rows'] if r['month']<=month)
            dep=min(assets[key],cost/(12*a[key+'_asset_life_years'])*fraction) if active else 0.
            assets[key]-=dep;depreciation+=dep;asset_depreciation[key]=dep
            if key=='factory' and a['factory_impairment_at_backlog_close'] and month==inputs['factory_close_month']:
                impairment+=assets[key];assets[key]=0.
        factory_impairment+=impairment
        inventory+=source['property_build_usd'];cogs=property_cost*source['property_sales_usd']/sales if sales else 0.
        inventory-=cogs
        if inventory<-.02:raise ValueError('property sales exceed modelled completed inventory')
        inventory=max(0.,inventory)
        earnings_before_tax=source['revenue_usd']-source['opex_usd']-cogs-depreciation-impairment-interest-core_fees
        desired_reserve=(interest+principal)*funding['model']['debt_service_reserve_months'] if month>=first else 0.
        deposit=desired_reserve-reserve;reserve=desired_reserve
        desired_buffer=source['opex_usd']*options['prepayments']['operating_buffer_months']+source['factory_warranty_cash_usd']
        buffer_change=desired_buffer-buffer;buffer=desired_buffer
        # Unused primary capital remains restricted until all capital invoices.
        capital_release=capital_cash if month>max(r['month'] for r in inputs['rows'] if r['physical_capital_usd']>.01) else 0.
        capital_cash-=capital_release
        available=cash+source['revenue_usd']-source['opex_usd']-interest-principal-core_fees-deposit-buffer_change+capital_release
        gap_interest=gap*gap_rate/12; available-=gap_interest
        # Pay the prior annual tax accrual: no circular debt/tax calculation.
        tax=next_tax;next_tax=0.;tax_payable-=tax
        available-=tax
        gap_draw=gap_repay=gap_charge=missing=0.
        if available<0:
            draw=min(-available/(1-gap_fee-gap_rate/24),max(0.,gap_cap-gap))
            gap_draw=draw;gap+=draw;gap_charge=draw*gap_fee;gap_interest+=draw*gap_rate/24
            available+=draw-gap_charge-draw*gap_rate/24; missing=max(0.,-available);uncovered_total+=missing;available=max(0.,available)
        if not gap_draw and not missing:
            order=sorted((*CORE,'liquidity'),key=lambda n:-(gap_rate if n=='liquidity' else terms[n]['annual_rate']))
            for name in order:
                if name=='liquidity':
                    gap_repay=min(gap,available);gap-=gap_repay;available-=gap_repay
                elif options['prepayments']['eligible'][name]:
                    conversion=1 if terms[name]['currency']=='USD' else fx
                    paid,charge=prepay_vintages(loans[name],available*conversion,options['prepayments']['premium'][name],month,options['prepayments']['minimum_age_months'][name])
                    row[name+'_early_principal_native']=paid;early+=paid/conversion;early_fees+=charge/conversion;available-=(paid+charge)/conversion
        pretax_period=earnings_before_tax-gap_interest-gap_charge-early_fees
        year_profit+=pretax_period
        tb=source['tax_operating_bases_usd']
        year_tax_bases['rail']+=tb['rail']-asset_depreciation['rail']-asset_depreciation['train']
        year_tax_bases['energy']+=tb['energy']-asset_depreciation['solar']
        year_tax_bases['factory']+=tb['factory']-asset_depreciation['factory']-impairment
        year_tax_bases['development']+=tb['development']-cogs-(rights_tax_basis*source['property_sales_usd']/sales if sales else 0.)
        tax_accrual=0.
        if month%12==11 or month==inputs['rows'][-2]['month']:
            tax_base=max(0.,year_profit) if aggregate_tax else sum(max(0.,value) for value in year_tax_bases.values())
            tax_accrual=a['corporate_tax_fraction']*tax_base
            tax_payable+=tax_accrual;next_tax=tax_accrual
            year_profit=0.;year_tax_bases={name:0. for name in year_tax_bases}
        period_net=pretax_period-tax_accrual;net_income+=period_net
        dividend=0.
        all_debt=gap+sum(v['balance']/(1 if terms[n]['currency']=='USD' else fx) for n,vs in loans.items() for v in vs)
        allowed_profit=max(0.,net_income-dividends_paid-a['profit_retention_fraction']*max(0.,net_income))
        if (month%12==11 or month==inputs['rows'][-1]['month']) and month>=first and all_debt<.01 and uncovered_total<.02 and capital_cash<.01 and sum(shares.values())>0:
            dividend=min(max(0.,available),allowed_profit);available-=dividend;dividends_paid+=dividend
        cash=max(0.,available)
        dividend_groups={group:dividend*fx*shares[group]/sum(shares.values()) if sum(shares.values()) else 0. for group in GROUPS}
        for group in GROUPS:cf[group].append((month,(shareholder_investment[group]+dividend_groups[group])/fx))
        sources=govt+new_net+sum(draws.values())+source['revenue_usd']+gap_draw+missing
        uses=capex+source['opex_usd']+interest+principal+core_fees+gap_interest+gap_charge+gap_repay+early+early_fees+tax+dividend+deposit+buffer_change
        cash_residual=opening_cash+opening_capital_cash+sources-uses-cash-capital_cash
        closing_debt=0.
        for name in CORE:
            balance=sum(v['balance'] for v in loans[name]);conversion=1 if terms[name]['currency']=='USD' else fx
            row[name+'_closing_balance_native']=balance;row.setdefault(name+'_early_principal_native',0.);closing_debt+=balance/conversion
        equity_book=(nominal+share_premium-issue_costs)/fx+net_income-dividends_paid+(cumulative_gov_cash if not government_as_equity else 0.)
        net_assets=cash+capital_cash+reserve+buffer+sum(assets.values())+inventory-closing_debt-gap-tax_payable
        book_residual=net_assets-equity_book
        # Uncovered funding is a separately explicit assumed sponsor support;
        # it is NOT received equity, loan or government cash.
        book_residual-=uncovered_total
        if abs(cash_residual)>.02 or abs(book_residual)>.05:raise ValueError(f'cash/book balance fails month {month}: {cash_residual}, {book_residual}')
        liabilities=closing_debt+gap+tax_payable
        row.update(liabilities_iqd=liabilities*fx,
            indicative_liabilities_to_book_equity=liabilities/equity_book if equity_book>0 else None,
            indicative_article28_threshold_failed=liabilities>3*equity_book+.02,
            tax_iqd=tax*fx,tax_accrual_iqd=tax_accrual*fx,closing_tax_payable_iqd=tax_payable*fx,depreciation_iqd=depreciation*fx,factory_impairment_iqd=impairment*fx,
            property_cost_of_sales_iqd=cogs*fx,net_profit_iqd=period_net*fx,retained_profit_iqd=(net_income-dividends_paid)*fx,
            paid_up_nominal_capital_iqd=nominal,share_premium_iqd=share_premium,issue_cost_equity_deduction_iqd=issue_costs,
            government_shares=shares['government'],iraqi_private_shares=shares['iraqi_private'],foreign_private_shares=shares['foreign_private'],
            government_ownership=shares['government']/sum(shares.values()) if sum(shares.values()) else None,
            iraqi_ownership=(shares['government']+shares['iraqi_private'])/sum(shares.values()) if sum(shares.values()) else None,
            liquidity_draw_iqd=gap_draw*fx,liquidity_interest_iqd=gap_interest*fx,liquidity_fees_iqd=gap_charge*fx,liquidity_repayment_iqd=gap_repay*fx,
            uncovered_support_required_iqd=missing*fx,closing_liquidity_debt_iqd=gap*fx,
            early_premiums_iqd=early_fees*fx,total_dividend_iqd=dividend*fx,government_dividend_iqd=dividend_groups['government'],
            iraqi_private_dividend_iqd=dividend_groups['iraqi_private'],foreign_private_dividend_iqd=dividend_groups['foreign_private'],
            closing_capital_cash_iqd=capital_cash*fx,closing_cash_iqd=cash*fx,closing_dsra_iqd=reserve*fx,closing_operating_and_warranty_buffer_iqd=buffer*fx,
            closing_ppe_iqd=sum(assets.values())*fx,closing_property_inventory_iqd=inventory*fx,
            net_assets_iqd=net_assets*fx,shareholder_book_equity_iqd=equity_book*fx,
            assumed_unfunded_support_cumulative_iqd=uncovered_total*fx,cash_balance_residual_usd=cash_residual,book_balance_residual_usd=book_residual)
        result.append(row)
    shareholder_returns={group:dict(equity_irr=equity_irr(flows),equity_npv_at_hurdle_usd=npv(flows,m['investor_hurdle_rate']),
        cash_investment_usd=-sum(v for _,v in flows if v<0),cash_return_usd=sum(v for _,v in flows if v>0),
        return_basis='Ordinary dividends and explicit secondary purchase/sale; no terminal asset sale or guaranteed equity redemption') for group,flows in cf.items()}
    core_cash_npv=npv([(r['month'],r['revenue_usd']-r['opex_usd']-r['physical_capital_usd']) for r in inputs['rows']],.134)
    last=result[-1] if result else {}
    metrics=dict(target_primary_equity_usd=0. if secondary else target_usd,primary_gross_equity_usd=primary_gross,primary_net_equity_usd=primary_net,
        primary_issue_fees_usd=primary_gross-primary_net,secondary_seller_receipts_usd=secondary_receipts,secondary_company_receipts_usd=0.,
        government_capital_usd=cumulative_gov_cash,government_equity_reclassification_new_cash_usd=0.,
        total_capital_usd=sum(r['physical_capital_iqd'] for r in result)/fx,
        chinese_credit_usd=sum(r['chinese_export_credit_draw_native'] for r in result),
        domestic_bond_face_iqd=sum(r['domestic_bonds_draw_native'] for r in result),bank_capital_iqd=sum(r['bank_credit_draw_native'] for r in result),
        peak_liquidity_debt_iqd=max((r['closing_liquidity_debt_iqd'] for r in result),default=0.),
        terminal_liquidity_debt_iqd=last.get('closing_liquidity_debt_iqd',0.),uncovered_support_iqd=uncovered_total*fx,
        total_dividends_iqd=sum(r['total_dividend_iqd'] for r in result),first_dividend_month=next((r['month'] for r in result if r['total_dividend_iqd']>.01),None),
        government_ownership=last.get('government_ownership'),iraqi_ownership=last.get('iraqi_ownership'),
        corporate_cash_tax_iqd=sum(r['tax_iqd'] for r in result),factory_asset_impairment_usd=factory_impairment,
        core_resource_npv_usd=core_cash_npv,resource_npv_after_land_usd=core_cash_npv-inputs['land_opportunity_usd']/(1.134)**(inputs['land_opportunity_month']/12),
        maximum_cash_residual_usd=max((abs(r['cash_balance_residual_usd']) for r in result),default=0.),
        tax_basis='aggregate-profit-proxy-no-eligibility-established' if aggregate_tax else 'separate-business-positive-profit-floor-no-parent-interest-or-loss-netting-relief',
        maximum_book_residual_usd=max((abs(r['book_balance_residual_usd']) for r in result),default=0.),
        government_cash_share_of_original_scope=.25,
        indicative_article28_threshold_failed_months=sum(r['indicative_article28_threshold_failed'] for r in result),
        first_indicative_article28_threshold_failed_month=next((r['month'] for r in result if r['indicative_article28_threshold_failed']),None),
        all_debt_cleared_without_unfunded_support=bool(not stop and uncovered_total<.02 and last and last['closing_liquidity_debt_iqd']<.02 and all(last[n+'_closing_balance_native']<.02 for n in CORE)))
    return dict(status='funding-blocked-no-opening' if stop else 'conditional-uncommitted-equity-scenario',financing_committed=False,
        company_incorporated=False,listing_approved=False,opening_month=None if stop else first,full_opening_month=None if stop else full,
        funding_stop=stop,metrics=metrics,shareholder_returns=shareholder_returns,monthly=result,
        loan_vintages=[dict(instrument=name,currency=terms[name]['currency'],
            first_contractual_principal_month=v['month']+v['grace_months_from_draw']+1,
            final_contractual_principal_month=v['month']+v['grace_months_from_draw']+v['repayment_months'],**v) for name,vs in loans.items() for v in vs],
        source_equity_replaced_iqd=inputs['replaced_subsidiary_equity_iqd'],final_shares=shares,
        shareholder_cashflows={group:[dict(month=m,cashflow_usd=v,cashflow_iqd=v*fx) for m,v in flows] for group,flows in cf.items()})


def capital_caps(case):
    result={}
    for row in case['monthly']:
        for name in CORE:
            conversion=1 if name=='chinese_export_credit' else 1300
            key=row['month']//6,name
            result[key]=result.get(key,0.)+row[name+'_draw_native']/conversion
    return result


def six_months(rows):
    result=[]
    for start in range(0,len(rows),6):
        period=rows[start:start+6]
        summable=['government_usd_cash','government_iqd_cash','primary_gross_subscription_iqd','primary_issue_fee_iqd','primary_net_subscription_iqd',
            'private_equity_capital_use_iqd','physical_capital_iqd','total_dividend_iqd','liquidity_draw_iqd','uncovered_support_required_iqd']
        summable += ['liquidity_interest_iqd','liquidity_fees_iqd','liquidity_repayment_iqd','tax_iqd','tax_accrual_iqd','net_profit_iqd']
        summable += [n+'_'+key+'_native' for n in CORE for key in ('draw','interest','principal','early_principal','fees')]
        row={key:sum(r[key] for r in period) for key in summable}
        row.update(start_month=period[0]['month'],end_month=period[-1]['month'],government_ownership=period[-1]['government_ownership'],
            closing_capital_cash_iqd=period[-1]['closing_capital_cash_iqd'],closing_liquidity_debt_iqd=period[-1]['closing_liquidity_debt_iqd'],
            capital_reconciliation_usd=(row['government_usd_cash']+(row['government_iqd_cash']+row['private_equity_capital_use_iqd']+row['domestic_bonds_draw_native']+row['bank_credit_draw_native'])/1300+row['chinese_export_credit_draw_native']-row['physical_capital_iqd']/1300))
        result.append(row)
    return result


def build_cases(config, funding, options, baseline, weak, phases, weak_phases, factory):
    normal=consolidated_inputs(baseline,phases,factory,config)
    adverse=consolidated_inputs(weak,weak_phases,factory,config)
    cases={'government_grant_reference':simulate_equity(normal,config,funding,options,0.,government_as_equity=False),
        'government_equity_reference':simulate_equity(normal,config,funding,options,0.)}
    for target in config['model']['private_raise_targets_usd']:
        cases['primary_'+str(int(target/1e6))+'m']=simulate_equity(normal,config,funding,options,target)
    cases['primary_1000m_premium']=simulate_equity(normal,config,funding,options,1e9,premium=True)
    cases['secondary_500m']=simulate_equity(normal,config,funding,options,500e6,secondary=True)
    caps=capital_caps(cases['primary_1000m'])
    cases['undersubscribed_1000m']=simulate_equity(normal,config,funding,options,1e9,success=.5,debt_caps=caps)
    cases['failed_later_primary']=simulate_equity(normal,config,funding,options,1e9,later_success=0.,debt_caps=caps)
    delayed_config=deepcopy(config);delay=config['downside']['subscription_delay_months']
    for key in ('founder_first_month','later_primary_month'):delayed_config['model'][key]+=delay
    delayed=consolidated_inputs(baseline,phases,factory,config,delay_months=delay)
    cases['delayed_1000m']=simulate_equity(delayed,delayed_config,funding,options,1e9)
    cases['joint_downside_1000m']=simulate_equity(adverse,config,funding,options,1e9,downside=True)
    cases['joint_downside_undersubscribed']=simulate_equity(adverse,config,funding,options,1e9,success=.5,
        downside=True,debt_caps=capital_caps(cases['joint_downside_1000m']))
    cases['aggregate_tax_proxy_1000m']=simulate_equity(normal,config,funding,options,1e9,aggregate_tax=True)
    return cases,normal


def report_text(cases,config):
    base=cases['government_equity_reference']['metrics']; one=cases['primary_1000m']; m=one['metrics']
    rows=[]
    for name,c in cases.items():
        v=c['metrics']; ir=c['shareholder_returns']['iraqi_private']['equity_irr']
        dates='Blocked' if c['funding_stop'] else f"{c['opening_month']}/{c['full_opening_month']}"
        rows.append(f"| {name} | {v['primary_gross_equity_usd']/1e6:.1f} | {dates} | {v['peak_liquidity_debt_iqd']/1e12:.3f} | {v['uncovered_support_iqd']/1e12:.3f} | {v['first_dividend_month']} | {'undefined' if ir is None else f'{ir:.2%}'} |")
    caps=[]
    for name in ('primary_500m','primary_1000m','primary_2000m','primary_1000m_premium','secondary_500m'):
        c=cases[name];v=c['metrics']
        caps.append(f"| {name} | {v['primary_gross_equity_usd']/1e6:.1f} | {v['primary_net_equity_usd']/1e6:.1f} | {v['government_ownership']:.2%} | {v['iraqi_ownership']:.2%} | {v['secondary_seller_receipts_usd']/1e6:.1f} |")
    return f'''# Baghdad mixed joint-stock holding and ordinary-equity study

As of {config['model']['as_of']}. This is a proposed Iraqi holding company with **100%-owned rail, station-development, energy and manufacturing subsidiaries**, not an incorporated company, offering, approved listing or committed funding. Baghdad alone supplies the order book. Future national projects remain uncontracted and supply zero revenue, collateral and terminal sale proceeds.

## Ownership, new money and currencies

Government still provides USD {base['government_capital_usd']/1e9:.9f}bn equivalent: 25% of the original USD 7.880493587bn rail/energy/factory capital, rather than 25% of shares or of the enlarged property programme. Reclassifying that existing contribution as ordinary equity generates **zero additional cash**. At the same subscription price, ownership is government cash divided by government plus private subscribed cash. Borrowing earns no ordinary shares.

| Transaction | Gross primary USD m eq | Company net primary USD m eq | Final government shares | Final Iraqi ownership | Government secondary sale USD m eq |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(caps)}

The share unit is an illustrative IQD 1 par and IQD 1 subscription price, not an accepted company valuation or legal share denomination. The premium sensitivity prices the later 25% issue at IQD 1.2, recording the difference in share premium and reducing dilution. Private subscriptions are 70% Iraqi and 30% foreign as an explicit scenario. Every paid-capital month observes the model's 25% state floor and 51% Iraqi floor; actual eligibility and beneficial ownership require counsel. Pending private subscriptions wait for sufficient paid government shares instead of treating promised government capital as paid. No shares or cash are credited for undelivered subscriptions. Land/concession/open designs are not priced into paid-up equity.

The government_grant_reference and government_equity_reference have identical debt, cash and physical costs before distributions. Government grants are a separately identified capital reserve without shares; cash-equity contribution is paid-in ordinary equity. Guarantees and public-service appropriations are uncommitted and never booked as subscription cash. A secondary sale transfers existing government shares: the seller receives the price, the company receives **zero**, and borrowing requirements remain unchanged. The secondary case omits sale fees as an explicit sensitivity; no government sale is authorised.

Original imported parts remain USD 1.793059933bn: government USD cash USD 896.529966m and Chinese USD credit USD 896.529966m. Only Chinese credit is USD debt. Remaining government cash, share subscriptions, bonds, bank/gap credit, fares, property proceeds and dividends are IQD. USD figures for those items are reference conversions at 1,300 IQD/USD, without a dollar-indexed obligation or promised conversion. Original USD capital intensity is 22.75%; local procurement prices still require actual imported-content and FX quotes. The additional USD 2.4bn-equivalent property construction is assumed IQD and makes physical group capital USD 10.280493587bn. It does not add government cash beyond the original 25% rule.

## Conditional results and investor returns

| Case | Actual gross primary USD m eq | Conditional first/full month | Peak IQD gap tn | Missing IQD cash tn | First dividend month | Private annual equity IRR |
| --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(rows)}

The $1bn primary case places IQD 1.300tn gross and IQD 1.274tn net after 2% issue fees. Peak IQD liquidity falls from {base['peak_liquidity_debt_iqd']/1e12:.3f}tn in the matched holding-company equity reference to {m['peak_liquidity_debt_iqd']/1e12:.3f}tn. These references pool four wholly owned businesses and include a conservative tax stress; they are **different from** the existing 4.461tn rail planning baseline and the independently financed 8.450tn SPV alternative. The original SPV private subscriptions of IQD {one['source_equity_replaced_iqd']/1e12:.3f}tn are replaced, not added to holding subscriptions.

Private equity IRR for the $1bn case is {one['shareholder_returns']['iraqi_private']['equity_irr']:.2%} nominal, with a 15% hurdle NPV of USD {one['shareholder_returns']['iraqi_private']['equity_npv_at_hurdle_usd']/1e6:.3f}m for the 70% Iraqi private cohort. Its first dividend is month {m['first_dividend_month']}; ordinary shares have no guaranteed redemption or principal payment. With 5% general inflation, a roughly 3% nominal return does not establish an attractive real return. Actual ordinary dividends, retained profits, reserve balances, shareholder payments and ownership are exported monthly. IRR is undefined without positive shareholder receipts, or for ambiguous multi-sign cash flows; blocked-case NPV covers only funded investment to suspension and omits unresolved recovery/termination, so it is not a complete investor downside valuation.

Planned unlevered group resource NPV remains USD {m['core_resource_npv_usd']/1e9:.3f}bn, or USD {m['resource_npv_after_land_usd']/1e9:.3f}bn after the assumed unverified USD 600m land opportunity cost. It excludes debt/equity transfers, corporation tax and issuance fees and reconciles to the prior consolidated resource case. Debt replacement changes investor cash and finance costs, not this before-financing resource value. Blocked scenarios retain this **planned-scope** diagnostic while reporting only actual funded-prefix capital; no unbuilt assets or future earnings are presented as delivered. Financial resource NPV excludes wider social/economic benefits such as travel time and local employment, which need separate evidence.

## Subscriptions, six-month placements and release gates

Founder/anchor subscriptions request 75% in six equal calls at months 0, 6, 12, 18, 24 and 30. The remaining 25% is a **conditional primary issue at month 60**, which may be private rather than listed; no admission is assumed. Actual settlements may extend beyond the requested dates to preserve the paid state floor. [primary_1000m-six-months.csv](primary_1000m-six-months.csv) reports actual subscriptions, net fees, restricted capital cash, government USD/IQD cash, native capital-credit draws, dividends and gap requirements every six months. Each monthly row reconciles physical invoices against capital sources; unspent subscription cash is restricted until construction invoices complete.

Net equity displaces the residual 25% bank/75% bond capital basket, bank first in each invoice. Domestic bank principal is amortised over 240 months and bond principal over 216 months, starting no earlier than **full-network opening**. This group-wide grace is more conservative than per-line cohorts and needs actual facility documents. Reference coupons stay 9%/8%; China retains 5%, 48-month draw grace and 180-month amortisation. Interest is paid throughout construction; arrangement fees, undrawn Chinese commitment charges, prepayment lock-ins/premiums, six months of debt service reserve, three months of OPEX buffer and factory warranty cash are included. The separate IQD 2% gap sensitivity has a 0.5% draw fee and 13tn cap; downside uses 8%, 1% and 4tn. None is committed.

Undersubscription and failed later issues hold the fully subscribed case's six-month capital-debt envelopes fixed. If the missing shares require capital credit beyond that envelope, the next physical invoice is withheld and the case reports **no opening**. The operating gap facility cannot cover refused capital. Already funded costs and debt remain; there is no forgiveness or assumed rescue. Resumption requires newly executable finance, rephasing, priced hold/restart and physical acceptance; resolution costs are unmodelled. The six-month delay sensitivity instead moves financial-close-to-NTP work and subscriptions together, retains fixed nominal property sales and indexes operations from close; it is a conditional whole-programme deferral, not a priced mid-construction suspension. Joint downside uses the existing 55/106-month physical stress, fare/nonfare shortfall, higher rates/inflation and weaker property sales, without uncontracted extra income.

## Pro-forma accounts and consolidation

The group eliminates PPA, internal train invoices/capacity fees and station-rights charges using [the existing intercompany ledger](../financing-redesign/integrated-intercompany-monthly.csv). Factory input cash moves to group train assets at its actual purchase date; original manufacturing payroll/QA/overhead remains counted once. Subsidiary equity is replaced by parent subscriptions. Central treasury access, subsidiary distributions/guarantees and lender consent are assumptions requiring explicit agreements; 100% ownership alone does not permit unrestricted transfers. Business operating records remain separately attributable in [group-resource-monthly.csv](group-resource-monthly.csv). These are cash-based pro-forma accounts, not audited statutory statements or proof of admission.

Rail, train, solar and factory assets depreciate over 30, 20, 25 and 20 years respectively, phased into operation; depreciation is a **noncash** charge. Factory remaining book assets are conservatively impaired at Baghdad backlog/warranty close; there are no later orders or salvage receipts. Property construction is inventory, released once to cost of sales as sold; sold space generates no extra rental revenue. Existing maintenance/battery renewals remain in cash OPEX, plus the earlier explicit solar/caretaker allowance; reserves are not spent twice. Land opportunity cost remains a separate in-kind appraisal exposure, not a cash injection, paid-up shares or free balance-sheet asset.

The 15% corporate rate is the Iraqi GCT headline non-oil rate, not a tax ruling. Base scenarios tax each positive annual business operating-profit proxy after assigned depreciation/COGS, retaining internal business charges solely for a conservative **tax stress**. They assume no parent-interest deductions, subsidiary loss netting, exemptions, refunds or carryforward relief. This yields IQD {m['corporate_cash_tax_iqd']/1e12:.3f}tn lifetime cash tax in the normal case. The separately labelled aggregate_tax_proxy_1000m sensitivity taxes positive annual consolidated profit including finance costs; group eligibility is unestablished. Neither is statutory taxable income. Customs, property-transfer taxes, transaction withholding, relief and deductible rates require a priced Iraqi tax opinion before these budgets are investment-ready. [GCT corporate declaration guidance](https://tax.mof.gov.iq/دليل-ملىء-تصريح-ضريبة-الشركات/).

Annual tax is accrued at year end and paid next month, including final stub settlement. Net assets reconcile against nominal capital, share premium, issue-fee deductions, net retained profit and dividends; cash and book residuals must stay below USD 0.02/0.05. Missing cash is explicitly separate assumed unfunded support, never new government equity. Dividends require cumulative positive distributable-profit **proxy**, no missing funding, all debt repaid, no unused capital cash and intact OPEX/warranty/DSRA reserves. A further 10% positive-profit retention is contractual sensitivity, not the statutory reserve rule. Audited distributable profit, legal reserves, subsidiary upstreamability and board approval remain additional gates even when the model shows a possible dividend.

## Iraqi legal, governance and admission gates

[Companies Law Articles 7 and 7 bis](https://iraqld.msla.iq/legislations/showlegislation?lawbookid=22025) support a mixed company with initial state capital at least 25%, holding subsidiaries and annual consolidated accounts. Mandate, concession, incorporation, capital approvals and enforceable public-service obligations still require the competent Iraqi bodies. Publish ordinary commercial contracts separately from affordability/service subsidies; optional future availability support requires an appropriation outside the 25% construction rule.

The [official 2019 amendment, Articles 12 and 28](https://csd.gov.iq/uploads/law/%D9%82%D8%A7%D9%86%D9%88%D9%86%20%D8%A7%D9%84%D8%B4%D8%B1%D9%83%D8%A7%D8%AA%2021%20new%20-%20Copy%201.pdf) contains the relevant 51% Iraqi participation condition and a liabilities limit of 300% of capital plus other owners' rights, with adjustment powers. Application, current amendments, foreign-investor exceptions, entity-level calculation and permitted treasury structure require counsel. A **consolidated screening proxy** flags {m['indicative_article28_threshold_failed_months']} months above that limit or with insufficient book equity in the $1bn scenario. It is not a legal compliance certificate; passing a share-floor check does not clear this debt constraint. The model is therefore not an executable capital structure until legal/capitalisation resolution is accepted.

[Regular-market Regulation 6](https://csd.gov.iq/wp-content/uploads/2025/01/%D9%84%D8%A7%D8%A6%D8%AD%D8%A9-6.pdf) normally requires two years/history and audits, at least 100 shareholders, equity at least paid-up capital, actual business and two years' distributable profit; a discretionary shorter history provision does not constitute admission. [Secondary-market Regulation 15](https://isc.gov.iq/upload/2023/01/15/63c3d89620814.pdf) provides a one-year activity/audit route and equity of at least 50% of paid-up capital, alongside approvals and disclosures. Apply the [ISC September 2026 amendments](https://isc.gov.iq/en/news/3437) and seek the regulator's current interpretation before fixing any offering date. Actual shareholder count, audits, eligible profits, applications and approvals are absent. All cases set company_incorporated and listing_approved false; month 60 is a funding assumption, not a listing prediction.

Use an independent board/audit committee, published related-party prices and conflicts policy, minority pre-emption/approval protections, consolidated and subsidiary disclosure, audited capital registers, procurement oversight and an explicit public-service contract. Government control and future retail ownership do not themselves demonstrate these controls. Open licences remain intact: investors own businesses, assets and enforceable contracts, without any valuation premium for exclusive ownership of openly licensed designs. New land/concession contributions require independent valuation, title and separate dilution treatment; none is included here.

ISC's [2025 market report](https://isc.gov.iq/en/news/2934) records IQD 531.5485bn share turnover and IQD 23.673365tn market capitalisation. The old IQD 4.461tn planning gap is approximately 8.4 times annual turnover; turnover is not a ceiling on primary subscriptions. The model therefore requires anchor placement evidence for each tranche rather than assumed retail absorption. The $1bn primary gross IQD 1.3tn is about 2.45 times that turnover, which is a scale comparison, not proof of capacity or incapacity. Sources checked 3 October 2026.

## Evidence programme

[Six new native ERP work packages](90-day-work-programme.json) require Iraqi corporate/tax counsel, public mandate and capital register, anchor/debt placement proof, audit/consolidation and dividend policy, minority/open-licence controls, and actual admission evidence. Owners, quotes, signatures and approvals remain pending. Due days are relative to an approved programme start. The [ERPNext Task import](erpnext-tasks.json) contains draft descriptions and no invented live IDs; local import receipts remain private. Existing ten physical/funding qualification tasks and six financing-redesign tasks continue to apply. Model outputs do not accept any evidence or permit operation. No external investor solicitation, issuance or expenditure is authorised.

Regenerate: `.venv/bin/python tools/automation/baghdad_equity.py`; validate source/output hashes with `--check`. Commitments and accepted physical evidence are required before any construction/opening/dividend decision.
'''


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.check:
        s=json.loads((OUT/'summary.json').read_text())
        for base,key in ((ROOT,'sources_sha256'),(OUT,'outputs_sha256')):
            for rel,sha in s[key].items():
                if digest(base/rel)!=sha:raise ValueError('Stale Baghdad equity '+rel)
        print('Baghdad equity source and output hashes pass');return
    paths=[Path(__file__),ROOT/'tools/automation/baghdad_funding_analysis.py',ROOT/'tools/automation/baghdad_financing_redesign.py',
        ROOT/'lib/templates/baghdad-equity.toml',ROOT/'lib/templates/iraq-funding.toml',ROOT/'lib/templates/baghdad-finance-options.toml',
        ROOT/'design/city-generation/src/osr_scenario/iraq_finance.py',CITY/'engineering/financing-redesign/summary.json',
        CITY/'engineering/financing-redesign/integrated.json',CITY/'engineering/financing-redesign/integrated_joint_downside.json',
        CITY/'engineering/delivery-risk/summary.json',CITY/'engineering/factory/summary.json',CITY/'engineering/qualification/summary.json']
    sources={p.relative_to(ROOT).as_posix():digest(p) for p in paths}
    revision=hashlib.sha256(json.dumps(sources,sort_keys=True).encode()).hexdigest()
    load=lambda p:json.loads(p.read_text())
    config=tomllib.loads(paths[3].read_text());options=tomllib.loads(paths[5].read_text())
    from baghdad_financing_redesign import city_funding_config
    funding=city_funding_config(tomllib.loads(paths[4].read_text()),'baghdad')
    risk,factory=load(paths[10]),load(paths[11])
    cases,normal=build_cases(config,funding,options,load(paths[8]),load(paths[9]),risk['cases']['calendar_baseline']['phases'],risk['cases']['joint_downside']['phases'],factory)
    OUT.mkdir(parents=True,exist_ok=True);outputs=[]
    def save(name,value):
        p=OUT/name;p.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n');outputs.append(p)
    def csvout(name,rows):
        if rows:write_csv(OUT/name,rows);outputs.append(OUT/name)
    for name,case in cases.items():
        case['semiannual']=six_months(case['monthly'])
        save(name+'.json',case);csvout(name+'-monthly.csv',case['monthly']);csvout(name+'-six-months.csv',case['semiannual'])
        csvout(name+'-loan-vintages.csv',case['loan_vintages'])
        csvout(name+'-shareholder-cashflows.csv',[dict(group=group,**row) for group,rows in case['shareholder_cashflows'].items() for row in rows])
    csvout('group-resource-monthly.csv',[{**{k:v for k,v in row.items() if k!='tax_operating_bases_usd'},
        **{name+'_operating_tax_stress_basis_usd':value for name,value in row['tax_operating_bases_usd'].items()}} for row in normal['rows']])
    workstreams=[
        ('LEGAL','Iraqi corporate and tax counsel','Current Articles 7/7bis/12/28, tax assessments and entity liability limits; incorporation/treasury/foreign participation and dividend eligibility opinions',15,60),
        ('MANDATE','Public sponsor and independent capital valuer','Authority and rail public-service/concession mandate; government cash, grants, land, guarantees and paid-in share register separately evidenced',15,60),
        ('PLACEMENT','Sponsor treasury and anchor equity lead','Six-month primary subscriptions and committed native credit; issue fees, under-subscription, state floor, conditional later issuance and bankable downside',15,75),
        ('AUDIT','Independent auditor and accounting lead','Separate statutory accounts and consolidation; tax/renewal/impairment/retained profits, related transfers, upstream restrictions and independent monthly reconciliation',30,90),
        ('GOVERNANCE','Independent board and minority investor counsel','Audit/conflicts committee, related-party prices, minority/pre-emption protection, procurement and retained open licences without exclusive-IP valuation',30,75),
        ('LISTING','Licensed Iraqi securities adviser','Actual holders, beneficial ownership, audited business/profits and equity tests; current ISX/CSD/ISC admission conditions and documented regulator decision',60,90)]
    packages=[dict(id='BAG-EVID-EQ90-'+key,accountable_owner_role=role,named_owner=None,start_day=start,due_day=due,
        day_basis='Days from actual approved equity-study start; no calendar date assigned',output=output,evidence=None,status='not-demonstrated',
        source_revision=revision,acceptance_rule='Independent signed underlying legal/financial evidence; simulation alone is not acceptance') for key,role,output,start,due in workstreams]
    save('90-day-work-programme.json',dict(status='draft-no-evidence',work_packages=packages,external_contacts_made=False))
    tasks=[dict(subject=p['id']+' — '+p['accountable_owner_role'],status='Open',priority='High',description='<pre>'+html.escape(json.dumps(p,indent=2))+'</pre>') for p in packages]
    save('erpnext-tasks.json',dict(doctype='Task',status='draft-import-package-not-live-records',tasks=tasks));csvout('erpnext-task-import.csv',tasks)
    report=OUT/'README.md';report.write_text(report_text(cases,config));outputs.append(report)
    save('listing-gates.json',dict(status='not-incorporated-not-applied',actual_shareholder_count=None,accepted_audits=0,
        accepted_legal_opinion=None,accepted_regulator_decision=None,book_value_checks_are_proxies=True,
        primary_month_60_is_conditional_not_listing_prediction=True,holding_owns_subsidiaries_fraction=1.,
        open_source_design_exclusivity_valuation_iqd=0,unvalued_land_paid_in_equity_iqd=0,
        related_party_prices_approved=False,minority_policy_adopted=False))
    summary=dict(schema='baghdad-ordinary-equity/1',as_of=config['model']['as_of'],status='illustrative-uncommitted-not-investment-ready',
        included_cities=['Baghdad'],financing_committed=False,company_incorporated=False,listing_approved=False,operational_release=False,
        source_revision=revision,sources_sha256=sources,outputs_sha256={p.name:digest(p) for p in outputs},
        cases={name:{key:case[key] for key in ('status','opening_month','full_opening_month','funding_stop','metrics','shareholder_returns','final_shares')} for name,case in cases.items()})
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('Generated 13 holding-equity cases with monthly accounts, ownership/dividends, six-month funding and six draft ERP work packages')


if __name__=='__main__':main()
