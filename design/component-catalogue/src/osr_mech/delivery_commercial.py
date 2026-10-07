"""Dated, scope-matched quotations and partial cashflow sensitivities.

Price evidence never creates factory capacity, purchase authority or complete
financing. Unknown scopes remain separate from the identified cash ledger.
"""
from datetime import date
import math
from osr_mech.provenance import stable_sum as sum

SCOPES=('launcher-purchase','freight-duties','assembly-commissioning','transporters','lifting-frames',
        'temporary-works','spares-maintenance','crews-night-work','relocation','pi20-beams','pi25-beams',
        'civil-supports','special-spans','station-structures','station-access','storage-dispatch')


def quote_register(rows,as_of):
    today=date.fromisoformat(as_of);seen=set();result=[]
    for quote in rows:
        identity=quote['id']
        if not identity or identity in seen:raise ValueError('quotation IDs must be distinct')
        seen.add(identity)
        if quote['scope'] not in SCOPES or quote['status'] not in ('preliminary','firm','contracted'):
            raise ValueError('unknown quotation scope/status')
        if not quote.get('supplier_id') or not quote.get('source_record') or len(quote.get('source_sha256',''))!=64:
            raise ValueError('quotation requires supplier and source receipt')
        start=date.fromisoformat(quote['issued_on']);end=date.fromisoformat(quote['valid_until'])
        if end<start:raise ValueError('quotation validity ends before issue')
        if quote['currency']!='USD':raise ValueError('dated FX reconciliation is required before entering non-USD prices')
        for key in ('quantity','unit_price_usd'):
            value=quote[key]
            if isinstance(value,bool) or not math.isfinite(value) or value<0:raise ValueError('invalid quotation amount')
        if quote['quantity']==0:raise ValueError('quotation quantity must be positive')
        if quote.get('tooling_in_unit_price') and quote.get('project_tooling_usd',0):
            raise ValueError('supplier-amortised tooling cannot also be project CAPEX')
        applicable=start<=today<=end and quote['status'] in ('firm','contracted') and quote.get('review_accepted') is True
        result.append({**quote,'cash_usd':quote['quantity']*quote['unit_price_usd'],
            'price_evidence_applicable_as_of':applicable,'factory_capacity_qualified_by_quote':False,
            'purchase_committed':quote['status']=='contracted' and quote.get('contract_record') is not None})
    return result


def procurement_requirements(quantities,launchers,transporters):
    counts={'launcher-purchase':launchers,'transporters':transporters,'lifting-frames':launchers,
        'pi20-beams':quantities['pi20_beams'],'pi25-beams':quantities['pi25_beams'],
        'special-spans':quantities['special_spans'],'civil-supports':quantities['proposed_supports']}
    return [dict(scope=scope,planning_quantity=counts.get(scope),price_usd=None,
        status='quotation-required',quantity_basis='span-layout.json and identified fleet; proposed supports are not surveyed') for scope in SCOPES]


def partial_cashflow_sensitivity(payments,opening_date,annual_rate,*,borrowed_fraction=1.0):
    """Simple ACT/365 interest until a conditional gate, never a complete loan plan."""
    if not math.isfinite(annual_rate) or not 0<=annual_rate<=1 or not 0<=borrowed_fraction<=1:
        raise ValueError('invalid sensitivity rate/funding share')
    opening=date.fromisoformat(opening_date);ledger=[]
    for payment in sorted(payments,key=lambda p:(p['date'],p['scope'])):
        when=date.fromisoformat(payment['date']);cash=payment['cash_usd']
        if not math.isfinite(cash) or cash<0 or when>opening:raise ValueError('invalid dated payment')
        days=(opening-when).days;principal=cash*borrowed_fraction
        ledger.append({**payment,'days_until_conditional_opening':days,
            'borrowed_cash_sensitivity_usd':principal,'simple_interest_sensitivity_usd':principal*annual_rate*days/365})
    return dict(payments=ledger,identified_cash_usd=sum(p['cash_usd'] for p in ledger),
        interest_on_identified_cash_usd=sum(p['simple_interest_sensitivity_usd'] for p in ledger),
        annual_rate_assumption=annual_rate,borrowed_fraction_assumption=borrowed_fraction,
        conditional_opening_date=opening_date,revenue_start_accepted=False,revenue_usd=None,
        complete_accelerated_capex_usd=None,complete_financing_usd=None,claimed_net_saving_usd=None,
        scope='identified incremental payments only; simple-interest sensitivity excludes unknown costs, complete debt terms and actual revenue',
        financing_committed=False)
