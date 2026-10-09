"""Independent reconciliation, native six-month funding envelopes and gap debt.

The original support requirement is not a free loan. This module rebuilds debt
from actual draw schedules, charges supplemental funding for its own interest
and fees, sweeps later cash to repayment, and exposes terminal unpaid balances.
"""
from __future__ import annotations

from collections import defaultdict
import math

CORE = ('chinese_export_credit', 'domestic_bonds', 'bank_credit')


def validate_options(options: dict) -> None:
    def finite(value, label, maximum=None):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0 or (maximum is not None and value > maximum):
            raise ValueError(f"invalid {label}")
    for group, keys in {
        'model': ('tranche_months', 'bond_denomination_iqd'),
        'green': ('blended_grace_months', 'blended_repayment_months'),
        'additional_sources': ('climate_grant_first_month', 'rights_first_month', 'rights_tranches'),
    }.items():
        for key in keys:
            value = options[group][key]
            finite(value, key)
            if int(value) != value or (key in ('tranche_months', 'bond_denomination_iqd', 'blended_repayment_months', 'rights_tranches') and value == 0):
                raise ValueError(f"invalid integer/count {key}")
    for key in ('share_of_candidate_bonds', 'blended_rate', 'arrangement_fee', 'annual_guarantee_fee'):
        finite(options['green'][key], key, 1)
    for key in ('commercial_annual_rate', 'commercial_draw_fee', 'concessional_annual_rate', 'concessional_draw_fee'):
        finite(options['liquidity'][key], key, 1)
    finite(options['liquidity']['illustrative_cap_iqd'], 'illustrative_cap_iqd')
    if options['liquidity']['currency'] != 'IQD':
        raise ValueError('supplemental facility must be IQD')
    for key in ('climate_capital_grant_usd', 'net_development_rights_usd', 'incremental_net_local_receipts_annual_usd'):
        finite(options['additional_sources'][key], key)
    for key in ('annual_increase', 'general_price_inflation', 'opex_inflation', 'opex_stress_inflation', 'income_growth', 'income_stress_growth', 'ancillary_indexation', 'peak_trip_share'):
        finite(options['fares'][key], key, 1)
    for key in ('peak_multiplier', 'offpeak_multiplier', 'maximum_demand_multiplier'):
        finite(options['fares'][key], key)
        if options['fares'][key] == 0:
            raise ValueError(f'invalid positive multiplier {key}')
    elasticity = options['fares']['price_elasticity']
    if isinstance(elasticity, bool) or not isinstance(elasticity, (int, float)) or not math.isfinite(elasticity) or elasticity > 0:
        raise ValueError('invalid price elasticity')
    finite(options['prepayments']['operating_buffer_months'], 'operating_buffer_months')
    for name in (*CORE, 'green_bonds'):
        finite(options['prepayments']['premium'][name], name+' prepayment premium', 1)
        age = options['prepayments']['minimum_age_months'][name]
        finite(age, name+' prepayment age')
        if int(age) != age:
            raise ValueError('prepayment age must be an integer')
        if not isinstance(options['prepayments']['eligible'][name], bool):
            raise ValueError('prepayment eligibility must be boolean')
    if options['prepayments']['vintage_order'] != 'oldest draw first':
        raise ValueError('unsupported prepayment vintage order')


def capital_projection(contracts: list[dict], config: dict, eligible: set[str]) -> dict[int, dict]:
    """Independent projection of controlled invoice milestones, not ledger support."""
    rows = defaultdict(lambda: {'capex': 0., 'imports': 0., 'candidate_capex': 0., 'candidate_imports': 0.})
    model = config['model']
    for contract in contracts:
        amount, imported = float(contract['budget_usd']), float(contract['imported_share'])
        start, end = int(contract['planned_start_day']), int(contract['planned_finish_day'])
        for day, fraction in ((start-30, .1), ((start+end)//2, .55), (end, .3), (end+90, .05)):
            month = math.floor((day+model['pre_ntp_working_days'])*12/model['working_days_per_year'])
            row = rows[month]
            row['capex'] += amount*fraction
            row['imports'] += amount*fraction*imported
            if contract['bucket'] in eligible:
                row['candidate_capex'] += amount*fraction
                row['candidate_imports'] += amount*fraction*imported
    return dict(rows)


def debt_month(vintages: list[dict], month: int, terms: dict) -> tuple[float, float]:
    """Native interest/principal for independently reconstructed loan vintages."""
    interest = principal = 0.
    rate = float(terms['annual_rate'])/12
    for loan in vintages:
        age = month-loan['month']
        balance = loan['balance']
        interest += balance*rate*(.5 if age == 0 else 1)
        loan['last_interest'] = balance*rate*(.5 if age == 0 else 1)
        loan['last_principal'] = 0.
        if age > loan.get('grace_months_from_draw', terms['grace_months_from_draw']):
            repayment = min(balance, max(0., loan['payment']-balance*rate))
            principal += repayment
            loan['last_principal'] = repayment
            loan['balance'] = max(0., balance-repayment)
    return interest, principal


def add_draw(vintages: list[dict], month: int, amount: float, terms: dict, factory_share: float = 0.) -> None:
    if amount <= 0:
        return
    rate, count = float(terms['annual_rate'])/12, int(terms['repayment_months'])
    payment = amount/count if rate == 0 else amount*rate/(1-(1+rate)**(-count))
    vintages.append({'month': month, 'balance': amount, 'payment': payment, 'principal': amount, 'factory_share': factory_share,
                     'grace_months_from_draw': int(terms['grace_months_from_draw']),
                     'repayment_months': count})


def prepay_vintages(vintages: list[dict], native_budget: float, premium: float,
                    month: int, minimum_age: int) -> tuple[float, float]:
    """Reduce principal once; charge the premium from the same cash budget."""
    principal = 0.
    for loan in vintages:
        if month-loan['month'] < minimum_age:
            continue
        amount = min(loan['balance'], max(0., native_budget/(1+premium)))
        loan['balance'] = max(0., loan['balance']-amount)
        native_budget = max(0., native_budget-amount*(1+premium))
        principal += amount
        if native_budget < 1e-8:
            break
    return principal, principal*premium


def audit_component(ledger: dict, config: dict) -> dict:
    """Rebuild every debt balance/service from draws; independently check fees."""
    vintages = {name: [] for name in CORE}
    rows = ledger['monthly']
    errors = []
    for row in rows:
        month = row['month']
        for name in CORE:
            terms = config[name]
            add_draw(vintages[name], month, row[name+'_draw_native'], terms)
            interest, principal = debt_month(vintages[name], month, terms)
            conversion = 1 if terms['currency'] == 'USD' else row['iqd_per_usd']
            errors.extend((abs(interest-row[name+'_interest_native'])/conversion,
                           abs(principal-row[name+'_principal_native'])/conversion,
                           abs(sum(v['balance'] for v in vintages[name])-row[name+'_closing_balance_native'])/conversion))
            fee = row[name+'_draw_usd']*terms['arrangement_fee']
            if name == 'chinese_export_credit':
                cohort = [r for r in rows if r['month']//12 == month//12 and r[name+'_draw_usd'] > 0]
                if cohort and month >= cohort[0]['month']:
                    fee += sum(r[name+'_draw_usd'] for r in cohort if r['month'] > month)*terms['undrawn_commitment_fee']/12
            errors.append(abs(fee-row[name+'_fees_usd']))
    return {'maximum_difference_usd': max(errors, default=0.), 'passed': max(errors, default=0.) < .02}


def simulate(capital: dict[int, dict], operating: list[dict], config: dict,
             options: dict, *, green: str | None = None, extras: bool = False,
             bridge_rate: float | None = None, bridge_fee: float = 0.,
             repayment_policy: str | None = None, zero_premiums: bool = False,
             noncallable_bonds: bool = False, draw_terms: dict | None = None,
             green_eligible_months: set[int] | None = None) -> dict:
    """Price pooled gap debt; optional borrower shares/equity preserve default 25%."""
    validate_options(options)
    model, green_config = config['model'], options['green']
    funding = config.get('capital_sources', {})
    equity_enabled = bool(funding) or any('private_equity' in row for row in capital.values())
    gov_share = funding.get('government_share', .25)
    china_share = funding.get('chinese_import_share', .5)
    gov_import_share = funding.get('government_import_share', .5)
    bond_share = funding.get('residual_bond_share', .75)
    for value in (gov_share, china_share, gov_import_share, bond_share):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError('invalid capital source share')
    draw_terms = draw_terms or {}
    for overrides in draw_terms.values():
        for name, override in overrides.items():
            if name not in (*CORE, 'green_bonds') or set(override) - {'grace_months_from_draw', 'repayment_months'}:
                raise ValueError('unsupported per-draw terms')
            for key, value in override.items():
                if isinstance(value, bool) or not isinstance(value, int) or value < (1 if key == 'repayment_months' else 0):
                    raise ValueError('invalid per-draw duration')
    fx = float(model['iqd_per_usd'])
    terms = {name: dict(config[name]) for name in CORE}
    green_terms = dict(config['domestic_bonds'])
    if green == 'label':
        green_terms['annual_rate'] = config['domestic_bonds']['annual_rate']
    elif green == 'blended':
        green_terms.update(annual_rate=green_config['blended_rate'],
                           grace_months_from_draw=green_config['blended_grace_months'],
                           repayment_months=green_config['blended_repayment_months'],
                           arrangement_fee=green_config['arrangement_fee'])
    terms['green_bonds'] = green_terms
    if repayment_policy not in (None, 'gap_only', 'gap_first', 'loans_first', 'cost_priority'):
        raise ValueError('unknown repayment policy')
    prepayments = options['prepayments']
    premiums = {name: 0. if zero_premiums else prepayments['premium'][name] for name in terms}
    eligible_prepay = {name: prepayments['eligible'][name] and not (noncallable_bonds and name in ('domestic_bonds', 'green_bonds')) for name in terms}
    if repayment_policy == 'cost_priority':
        costs = {name: loan['annual_rate']+(green_config['annual_guarantee_fee'] if name == 'green_bonds' and green == 'blended' else 0.) for name, loan in terms.items()}
        costs['liquidity'] = bridge_rate or 0.
        order = sorted(costs, key=lambda name: (-costs[name], name))
    elif repayment_policy == 'loans_first':
        order = ['bank_credit', 'chinese_export_credit', 'liquidity', 'domestic_bonds', 'green_bonds']
    elif repayment_policy == 'gap_first':
        order = ['liquidity', 'bank_credit', 'domestic_bonds', 'chinese_export_credit', 'green_bonds']
    else:
        order = ['liquidity']
    vintages = {name: [] for name in terms}
    source = options['additional_sources']
    eligible_after = sum(max(0., row['candidate_capex']-row['candidate_imports'])
                         for month, row in capital.items() if month >= source['climate_grant_first_month'])
    grant_total = source['climate_capital_grant_usd'] if extras else 0.
    if grant_total > eligible_after:
        raise ValueError('climate grant exceeds candidate local project capital')
    phases = operating[0]['phases']
    first_open = min(p['opening_month'] for p in phases)
    full_open = max(p['opening_month'] for p in phases)
    cash = reserve = bridge = operating_buffer = 0.
    bridge_cap = options['liquidity']['illustrative_cap_iqd']/fx
    monthly = []
    for op in operating:
        month = op['month']
        req = capital.get(month, {})
        capex, imported = req.get('capex', 0.), req.get('imports', 0.)
        candidate_capex, candidate_imports = req.get('candidate_capex', 0.), req.get('candidate_imports', 0.)
        grant = (grant_total*max(0., candidate_capex-candidate_imports)/eligible_after
                 if extras and eligible_after and month >= source['climate_grant_first_month'] else 0.)
        equity = req.get('private_equity', 0.)
        if isinstance(equity, bool) or not isinstance(equity, (int, float)) or not math.isfinite(equity) or equity < 0:
            raise ValueError('invalid private equity')
        govt, china = gov_share*capex, china_share*imported
        if govt-gov_import_share*imported < -.02:
            raise ValueError('government import cash exceeds government capital')
        residual = capex-govt-china-grant-equity
        if residual < -.02:
            raise ValueError('alternative capital sources exceed this month capital uses')
        bonds, bank = bond_share*max(0., residual), (1-bond_share)*max(0., residual)
        eligible_bonds = bond_share*max(0., (1-gov_share)*candidate_capex-china_share*candidate_imports-grant-req.get('candidate_private_equity', 0.))
        green_allowed=green is not None and (green_eligible_months is None or month in green_eligible_months)
        green_draw = min(bonds, eligible_bonds*green_config['share_of_candidate_bonds']) if green_allowed else 0.
        draws = {'chinese_export_credit': china, 'domestic_bonds': bonds-green_draw,
                 'green_bonds': green_draw, 'bank_credit': bank}
        factory_capex, factory_imports = req.get('factory_capex', 0.), req.get('factory_imports', 0.)
        factory_residual = .75*factory_capex-.5*factory_imports
        factory_draws = {'chinese_export_credit': .5*factory_imports, 'domestic_bonds': .75*factory_residual,
                         'bank_credit': .25*factory_residual, 'green_bonds': 0.}
        debt_service = fees = principal_usd = interest_usd = factory_service = 0.
        row = {'month': month, 'year': month//12+1, 'capex_usd': capex,
               'government_usd_cash': gov_import_share*imported, 'government_iqd_cash': (govt-gov_import_share*imported)*fx,
               'climate_capital_grant_iqd': grant*fx}
        if equity_enabled:
            row['private_equity_iqd'] = equity*fx
        for name, loan_terms in terms.items():
            vintage_terms = {**loan_terms, **draw_terms.get(month, {}).get(name, {})}
            conversion = 1. if loan_terms['currency'] == 'USD' else fx
            add_draw(vintages[name], month, draws[name]*conversion, vintage_terms,
                     factory_draws[name]/draws[name] if draws[name] else 0.)
            interest, principal = debt_month(vintages[name], month, loan_terms)
            interest_usd += interest/conversion
            principal_usd += principal/conversion
            debt_service += (interest+principal)/conversion
            factory_service += sum((v['last_interest']+v['last_principal'])*v['factory_share'] for v in vintages[name])/conversion
            fee = draws[name]*loan_terms['arrangement_fee']
            if name == 'chinese_export_credit':
                # Separate annual project/plant facility cohorts are signed at
                # their first draw; commitment fees copied from independently
                # audited original ledgers in the operating projection.
                fee += op['chinese_commitment_fee_usd']
            if name == 'green_bonds' and green == 'blended':
                fee += (sum(v['balance'] for v in vintages[name])+principal)*green_config['annual_guarantee_fee']/12/fx
            fees += fee
            row.update({name+'_draw_native': draws[name]*conversion,
                        name+'_interest_native': interest, name+'_principal_native': principal,
                        name+'_fees_native': fee*conversion,
                        name+'_closing_balance_native': sum(v['balance'] for v in vintages[name])})
        rights = 0.
        if extras and month >= source['rights_first_month']:
            age = month-source['rights_first_month']
            if age%options['model']['tranche_months'] == 0 and age//options['model']['tranche_months'] < source['rights_tranches']:
                rights = source['net_development_rights_usd']/source['rights_tranches']
        opened = sum(p['weight'] for p in phases if month >= p['opening_month'])
        extra_income = (source['incremental_net_local_receipts_annual_usd']/12*opened
                        if extras and first_open <= month < full_open+model['operating_years']*12 else 0.)
        income_multiplier=op.get('additional_income_multiplier',1.)
        if isinstance(income_multiplier,bool) or not isinstance(income_multiplier,(float,int)) or not math.isfinite(income_multiplier) or not 0<=income_multiplier<=1:
            raise ValueError('Invalid additional-income service multiplier')
        extra_income*=income_multiplier
        revenue, opex = op['revenue_usd'], op['opex_usd']
        desired = (factory_service*model['debt_service_reserve_months'] if op['factory_reserve_usd'] > 0 else 0.) if repayment_policy else op['factory_reserve_usd']
        if first_open <= month < full_open+model['operating_years']*12:
            desired += max(0., debt_service-(factory_service if repayment_policy else op['factory_debt_service_usd']))*model['debt_service_reserve_months']
        deposit, release = max(0., desired-reserve), max(0., reserve-desired)
        reserve += deposit-release
        buffer_target = opex*prepayments['operating_buffer_months'] if repayment_policy else 0.
        restricted = op.get('restricted_working_capital_usd', 0.)
        if isinstance(restricted, bool) or not isinstance(restricted, (int, float)) or not math.isfinite(restricted) or restricted < 0:
            raise ValueError('invalid restricted working capital')
        buffer_target += restricted
        buffer_deposit, buffer_release = max(0., buffer_target-operating_buffer), max(0., operating_buffer-buffer_target)
        operating_buffer += buffer_deposit-buffer_release
        opening_cash, opening_bridge = cash, bridge
        available = cash+revenue+extra_income+rights-opex-debt_service-fees+release-deposit+buffer_release-buffer_deposit
        gap_draw = gap_fee = gap_interest = gap_repayment = required_support = 0.
        early_principal = early_fees = 0.
        for name in terms:
            row[name+'_early_principal_native'] = 0.
            row[name+'_early_premium_native'] = 0.
        if bridge_rate is None:
            required_support = max(0., -available)
            cash = max(0., available)
        else:
            gap_interest = opening_bridge*bridge_rate/12
            available -= gap_interest
            if available < 0:
                denominator = 1-bridge_fee-bridge_rate/24
                if denominator <= 0:
                    raise ValueError('supplemental draw fees/interest consume all proceeds')
                gap_draw = min(-available/denominator, max(0., bridge_cap-bridge))
                gap_fee = gap_draw*bridge_fee
                gap_interest += gap_draw*bridge_rate/24
                bridge += gap_draw
                available += gap_draw-gap_fee-gap_draw*bridge_rate/24
                required_support = max(0., -available)
                cash = max(0., available)
            else:
                cash = available
        available = max(0., available)
        if gap_draw <= 1e-8 and required_support <= 1e-8:
            for name in order:
                if name == 'liquidity':
                    repayment = min(bridge, available)
                    bridge -= repayment
                    gap_repayment += repayment
                    available = max(0., available-repayment)
                elif eligible_prepay[name]:
                    conversion = 1. if terms[name]['currency'] == 'USD' else fx
                    repayment, premium = prepay_vintages(vintages[name], available*conversion, premiums[name],
                                                        month, prepayments['minimum_age_months'][name])
                    row[name+'_early_principal_native'] = repayment
                    row[name+'_early_premium_native'] = premium
                    early_principal += repayment/conversion
                    early_fees += premium/conversion
                    available = max(0., available-(repayment+premium)/conversion)
        cash = available
        for name in terms:
            row[name+'_closing_balance_native'] = sum(v['balance'] for v in vintages[name])
        sources = govt+equity+sum(draws.values())+grant+revenue+extra_income+rights+gap_draw+required_support+release
        sources += buffer_release
        uses = capex+opex+debt_service+fees+gap_interest+gap_fee+gap_repayment+deposit+buffer_deposit+early_principal+early_fees
        residual_cash = opening_cash+sources-uses-cash
        row.update(revenue_iqd=revenue*fx, opex_iqd=opex*fx,
                   fare_receipts_iqd=op.get('fare_revenue_usd', 0.)*fx,
                   nonfare_receipts_iqd=op.get('nonfare_revenue_usd', revenue)*fx,
                   incremental_net_receipts_iqd=extra_income*fx, net_rights_receipts_iqd=rights*fx,
                   core_interest_usd_equivalent=interest_usd, core_principal_usd_equivalent=principal_usd,
                   core_fees_usd_equivalent=fees, core_debt_service_usd_equivalent=debt_service,
                   early_core_principal_usd_equivalent=early_principal, early_premiums_usd_equivalent=early_fees,
                   liquidity_draw_iqd=gap_draw*fx, liquidity_interest_iqd=gap_interest*fx,
                   liquidity_draw_fee_iqd=gap_fee*fx, liquidity_repayment_iqd=gap_repayment*fx,
                   closing_liquidity_debt_iqd=bridge*fx,
                   uncovered_support_required_iqd=required_support*fx,
                   reserve_deposit_iqd_equivalent=deposit*fx, reserve_release_iqd_equivalent=release*fx,
                   closing_reserve_iqd_equivalent=reserve*fx, closing_project_cash_iqd=cash*fx,
                   operating_buffer_deposit_iqd=buffer_deposit*fx, operating_buffer_release_iqd=buffer_release*fx,
                   closing_operating_buffer_iqd=operating_buffer*fx,
                   cash_balance_residual_usd=residual_cash)
        monthly.append(row)
    summed = lambda key: sum(row[key] for row in monthly)
    metrics = {'total_capital_usd': summed('capex_usd'),
        'green_draw_eligibility_limited': green_eligible_months is not None,
        'green_ineligible_capital_months': sorted(m for m in capital if green_eligible_months is not None and m not in green_eligible_months),
        'government_capital_usd_equivalent': summed('government_usd_cash')+summed('government_iqd_cash')/fx,
        'china_capital_usd': summed('chinese_export_credit_draw_native'),
        'ordinary_bonds_iqd': summed('domestic_bonds_draw_native'), 'green_bonds_iqd': summed('green_bonds_draw_native'),
        'bank_capital_iqd': summed('bank_credit_draw_native'), 'climate_grant_iqd': summed('climate_capital_grant_iqd'),
        'net_rights_receipts_iqd': summed('net_rights_receipts_iqd'), 'incremental_net_receipts_iqd': summed('incremental_net_receipts_iqd'),
        'uncovered_support_iqd': summed('uncovered_support_required_iqd'),
        'total_supplemental_draw_iqd': summed('liquidity_draw_iqd'),
        'peak_supplemental_balance_iqd': max(row['closing_liquidity_debt_iqd'] for row in monthly),
        'supplemental_interest_iqd': summed('liquidity_interest_iqd'), 'supplemental_draw_fees_iqd': summed('liquidity_draw_fee_iqd'),
        'supplemental_repayments_iqd': summed('liquidity_repayment_iqd'),
        'terminal_supplemental_balance_iqd': monthly[-1]['closing_liquidity_debt_iqd'],
        'terminal_cash_iqd': monthly[-1]['closing_project_cash_iqd'],
        'net_lifetime_operating_and_finance_gap_usd': summed('core_debt_service_usd_equivalent')+summed('early_core_principal_usd_equivalent')+summed('core_fees_usd_equivalent')+summed('early_premiums_usd_equivalent')+(summed('opex_iqd')-summed('revenue_iqd'))/fx,
        'core_interest_usd_equivalent': summed('core_interest_usd_equivalent'),
        'core_principal_usd_equivalent': summed('core_principal_usd_equivalent'),
        'early_core_principal_usd_equivalent': summed('early_core_principal_usd_equivalent'),
        'early_premiums_usd_equivalent': summed('early_premiums_usd_equivalent'),
        'terminal_operating_buffer_iqd': monthly[-1]['closing_operating_buffer_iqd'],
        'total_finance_interest_and_fees_usd': summed('core_interest_usd_equivalent')+summed('core_fees_usd_equivalent')+summed('early_premiums_usd_equivalent')+(summed('liquidity_interest_iqd')+summed('liquidity_draw_fee_iqd'))/fx,
        'repayment_policy': repayment_policy or 'original_gap_only_no_operating_buffer', 'repayment_order': order,
        'operating_buffer_months': prepayments['operating_buffer_months'] if repayment_policy else 0.,
        'early_premiums': premiums if repayment_policy else {},
        'prepayment_eligible': eligible_prepay if repayment_policy else {},
        'prepayment_minimum_age_months': prepayments['minimum_age_months'] if repayment_policy else {},
        'maximum_cash_residual_usd': max(abs(row['cash_balance_residual_usd']) for row in monthly),
        'government_capital_share': (summed('government_usd_cash')+summed('government_iqd_cash')/fx)/summed('capex_usd') if summed('capex_usd') else 0.,
        'bridge_annual_rate': bridge_rate, 'bridge_draw_fee': bridge_fee,
        'illustrative_bridge_cap_iqd': options['liquidity']['illustrative_cap_iqd'],
        'core_final_balances_native': {name: sum(v['balance'] for v in loans) for name, loans in vintages.items()},
    }
    if metrics['maximum_cash_residual_usd'] > .02:
        raise ValueError('independent cash ledger does not reconcile')
    balances_error = 0.
    for name in terms:
        balance = 0.
        for row in monthly:
            balance += row[name+'_draw_native']-row[name+'_principal_native']-row[name+'_early_principal_native']
            balances_error = max(balances_error, abs(balance-row[name+'_closing_balance_native'])/(1. if terms[name]['currency'] == 'USD' else fx))
    metrics['maximum_principal_balance_residual_usd'] = balances_error
    if balances_error > .02:
        raise ValueError('scheduled/early principal and remaining balances do not reconcile')
    all_debt = lambda r: r['closing_liquidity_debt_iqd']/fx+sum(r[name+'_closing_balance_native']/(1. if terms[name]['currency'] == 'USD' else fx) for name in terms)
    outstanding = [r['month'] for r in monthly if all_debt(r) > .01]
    metrics['all_debt_cleared_month'] = outstanding[-1]+1 if outstanding and outstanding[-1] < monthly[-1]['month'] else (0 if not outstanding and any(r['capex_usd'] for r in monthly) else None)
    gap_paid = [r['month'] for r in monthly if r['liquidity_repayment_iqd'] > .01]
    metrics['liquidity_final_repayment_month'] = gap_paid[-1] if gap_paid else None
    for name in terms:
        active = [r['month'] for r in monthly if r[name+'_closing_balance_native'] > .01]
        metrics[name+'_last_outstanding_month'] = active[-1] if active else None
        paid = [r['month'] for r in monthly if r[name+'_principal_native']+r[name+'_early_principal_native'] > .01]
        metrics[name+'_final_repayment_month'] = paid[-1] if paid else None
    if equity_enabled:
        metrics['private_equity_iqd'] = summed('private_equity_iqd')
    result = {'metrics': metrics, 'monthly': monthly, 'semiannual': tranches(monthly, options, fx, terms, draw_terms),
            'status': 'illustrative-uncommitted-no-financial-close', 'financing_committed': False}
    if draw_terms:
        result['loan_vintages'] = [dict(instrument=name, currency=terms[name]['currency'], draw_month=v['month'],
            principal_native=v['principal'], annual_rate=terms[name]['annual_rate'], grace_months=v['grace_months_from_draw'],
            amortisation_months=v['repayment_months'], first_principal_month=v['month']+v['grace_months_from_draw']+1,
            contractual_last_principal_month=v['month']+v['grace_months_from_draw']+v['repayment_months'])
            for name, loans in vintages.items() for v in loans]
    return result


def tranches(monthly: list[dict], options: dict, fx: float = 1300., terms: dict | None = None, draw_terms: dict | None = None) -> list[dict]:
    period = int(options['model']['tranche_months'])
    result = []
    for start in range(0, len(monthly), period):
        rows = monthly[start:start+period]
        values = {key: (rows[-1][key] if (key.startswith('closing_') or key.endswith('_closing_balance_native')) else sum(row[key] for row in rows))
                  for key in monthly[0] if key not in ('month', 'year')}
        face = values['domestic_bonds_draw_native']+values['green_bonds_draw_native']
        values.update(tranche_id=f'BGD-H{start//period+1:03d}', start_month=start, end_month=rows[-1]['month'],
                      bond_face_iqd=face,
                      bond_units_at_assumed_denomination=math.ceil(face/options['model']['bond_denomination_iqd']),
                      indicative_rounded_bond_face_iqd=math.ceil(face/options['model']['bond_denomination_iqd'])*options['model']['bond_denomination_iqd'],
                      capital_reconciliation_usd=0.)
        values['capital_reconciliation_usd'] = (values['government_usd_cash']+values['chinese_export_credit_draw_native']
            +(values['government_iqd_cash']+face+values['bank_credit_draw_native']+values['climate_capital_grant_iqd']+values.get('private_equity_iqd', 0.))/fx-values['capex_usd'])
        values['maximum_cash_balance_residual_usd'] = max(abs(row['cash_balance_residual_usd']) for row in rows)
        for name, loan in (terms or {}).items():
            active = [row['month'] for row in rows if row[name+'_draw_native'] > .01]
            values[name+'_contractual_first_repayment_month'] = min(m+(draw_terms or {}).get(m, {}).get(name, {}).get('grace_months_from_draw', loan['grace_months_from_draw'])+1 for m in active) if active else None
            values[name+'_contractual_last_repayment_month'] = max(m+(draw_terms or {}).get(m, {}).get(name, {}).get('grace_months_from_draw', loan['grace_months_from_draw'])+(draw_terms or {}).get(m, {}).get(name, {}).get('repayment_months', loan['repayment_months']) for m in active) if active else None
        result.append(values)
    return result


def price_operating(operating: list[dict], receipts: dict, base_fare_iqd: float,
                    fx: float, options: dict, *, annual_fare: float = 0.,
                    annual_opex: float = 0., annual_income: float = 0.,
                    annual_nonfare: float = 0., elasticity: float = 0.,
                    annual_price_inflation: float = 0.,
                    peak_share: float = 0., peak_multiplier: float = 1.,
                    offpeak_multiplier: float = 1., fare_uplift: float = 1.) -> tuple[list[dict], dict]:
    """Index tariffs/OPEX independently; elastic demand responds to real fares.

    Fare, wage/income and expense assumptions are independent. No extra receipts
    are attributed to demand growth beyond the unchanged practical capacity.
    """
    fare_share = receipts['farebox_annual_usd']/receipts['total_annual_usd']
    result, pricing = [], []
    for source in operating:
        month = source['month']; elapsed_years = month//12
        fare_index = (1+annual_fare)**elapsed_years*fare_uplift
        income_index = (1+annual_income)**elapsed_years
        demand = yield_factor = 0.
        for share, multiplier in ((peak_share, peak_multiplier), (1-peak_share, offpeak_multiplier)):
            quantity = min(options['fares']['maximum_demand_multiplier'], (fare_index*multiplier/income_index)**elasticity)
            demand += share*quantity
            yield_factor += share*quantity*fare_index*multiplier
        fare = source['revenue_usd']*fare_share*yield_factor
        nonfare = source['revenue_usd']*(1-fare_share)*(1+annual_nonfare)**elapsed_years
        row = dict(source)
        row.update(revenue_usd=fare+nonfare, fare_revenue_usd=fare, nonfare_revenue_usd=nonfare,
                   opex_usd=source['opex_usd']*(1+annual_opex)**elapsed_years)
        result.append(row)
        pricing.append({'month': month, 'year_from_close': elapsed_years,
                        'average_paid_fare_iqd': base_fare_iqd*yield_factor/demand,
                        'peak_fare_iqd': base_fare_iqd*fare_index*peak_multiplier,
                        'offpeak_fare_iqd': base_fare_iqd*fare_index*offpeak_multiplier,
                        'paid_trips': source['revenue_usd']*fare_share/(base_fare_iqd/fx)*demand,
                        'demand_multiplier': demand, 'opex_index': (1+annual_opex)**elapsed_years,
                        'income_index': income_index,
                        'forty_four_trips_income_share': 44*base_fare_iqd*yield_factor/demand/(receipts['planning_monthly_income_iqd']*income_index),
                        'fare_receipts_iqd': fare*fx, 'nonfare_receipts_iqd': nonfare*fx,
                        'opex_iqd': row['opex_usd']*fx})
    phases = operating[0]['phases']
    first = min(p['opening_month'] for p in phases); full = max(p['opening_month'] for p in phases)
    active = [row for row in pricing if row['paid_trips'] > 0]
    return result, {'annual_fare_increase': annual_fare, 'annual_opex_inflation': annual_opex,
                    'annual_income_growth': annual_income, 'annual_nonfare_indexation': annual_nonfare,
                    'annual_general_price_inflation': annual_price_inflation,
                    'price_elasticity': elasticity, 'peak_trip_share': peak_share,
                    'peak_multiplier': peak_multiplier, 'offpeak_multiplier': offpeak_multiplier,
                    'initial_real_fare_uplift': fare_uplift,
                    'index_basis': 'annual steps from financial close; price response relative to indexed income; no pre-opening fares',
                    'first_opening': pricing[first], 'full_opening': pricing[full],
                    'last_operating_month': active[-1] if active else None,
                    'monthly_prices': pricing}


def build_analysis(programme: dict, city_funding: dict, factory_funding: dict,
                   city_contracts: list[dict], factory_contracts: list[dict], config: dict, options: dict) -> dict:
    city_case = city_funding['phased_opening']['cases']['low_demand']
    factory_case = factory_funding['base']
    components = (city_case, factory_case)
    audits = [audit_component(case, config) for case in components]
    if not all(row['passed'] for row in audits):
        raise ValueError('independent debt/fee audit failed')
    eligible = set(options['green']['candidate_buckets'])
    capital = capital_projection(city_contracts+factory_contracts, config, eligible)
    for month, amount in capital_projection(factory_contracts, config, eligible).items():
        capital[month]['factory_capex'] = amount['capex']
        capital[month]['factory_imports'] = amount['imports']
    horizon = max(len(case['monthly']) for case in components)
    operational = []
    for month in range(horizon):
        source_rows = [case['monthly'][month] for case in components if month < len(case['monthly'])]
        factory_row = factory_case['monthly'][month] if month < len(factory_case['monthly']) else {}
        operational.append({'month': month, 'revenue_usd': sum(r['revenue_usd'] for r in source_rows),
                            'opex_usd': sum(r['opex_usd'] for r in source_rows),
                            'factory_debt_service_usd': factory_row.get('debt_service_usd', 0.),
                            'factory_reserve_usd': factory_row.get('closing_restricted_reserve_usd', 0.),
                            'chinese_commitment_fee_usd': sum(r['chinese_export_credit_fees_usd']-r['chinese_export_credit_draw_usd']*config['chinese_export_credit']['arrangement_fee'] for r in source_rows)})
    operational[0]['phases'] = city_funding['phased_opening']['phases']
    receipts = programme['operating_receipts']
    for op in operational:
        op['fare_revenue_usd'] = op['revenue_usd']*receipts['farebox_annual_usd']/receipts['total_annual_usd']
        op['nonfare_revenue_usd'] = op['revenue_usd']-op['fare_revenue_usd']
    liquidity = options['liquidity']
    scenarios = {
        'unfunded_reference': {},
        'green_label_only': {'green': 'label'},
        'zero_cost_liquidity_bound': {'bridge_rate': 0.},
        'commercial_gap_credit': {'bridge_rate': liquidity['commercial_annual_rate'], 'bridge_fee': liquidity['commercial_draw_fee']},
        'concessional_gap_credit': {'bridge_rate': liquidity['concessional_annual_rate'], 'bridge_fee': liquidity['concessional_draw_fee']},
        'blended_candidate': {'green': 'blended', 'extras': True, 'bridge_rate': liquidity['concessional_annual_rate'], 'bridge_fee': liquidity['concessional_draw_fee']},
        'green_concessional_only': {'green': 'blended', 'bridge_rate': liquidity['concessional_annual_rate'], 'bridge_fee': liquidity['concessional_draw_fee']},
    }
    cases = {name: simulate(capital, operational, config, options, **settings) for name, settings in scenarios.items()}
    fares = options['fares']
    policies = {
        'fare_5pct_flat_costs_fixed_demand': {'annual_fare': fares['annual_increase']},
        'fare_5pct_flat_costs_elastic': {'annual_fare': fares['annual_increase'], 'elasticity': fares['price_elasticity']},
        'fixed_fare_5pct_opex': {'annual_opex': fares['opex_inflation'], 'annual_income': fares['income_growth']},
        'fare_5pct_opex_5pct': {'annual_fare': fares['annual_increase'], 'annual_opex': fares['opex_inflation'], 'annual_income': fares['income_growth'], 'elasticity': fares['price_elasticity']},
        'fare_5pct_opex_7pct': {'annual_fare': fares['annual_increase'], 'annual_opex': fares['opex_stress_inflation'], 'annual_income': fares['income_growth'], 'elasticity': fares['price_elasticity']},
        'fare_5pct_opex_5pct_income_2pct': {'annual_fare': fares['annual_increase'], 'annual_opex': fares['opex_inflation'], 'annual_income': fares['income_stress_growth'], 'elasticity': fares['price_elasticity']},
        'variable_fare_5pct_opex_5pct': {'annual_fare': fares['annual_increase'], 'annual_opex': fares['opex_inflation'], 'annual_income': fares['income_growth'], 'elasticity': fares['price_elasticity'], 'peak_share': fares['peak_trip_share'], 'peak_multiplier': fares['peak_multiplier'], 'offpeak_multiplier': fares['offpeak_multiplier']},
        'fare_5pct_opex_5pct_rents_indexed': {'annual_fare': fares['annual_increase'], 'annual_opex': fares['opex_inflation'], 'annual_income': fares['income_growth'], 'annual_nonfare': fares['ancillary_indexation'], 'elasticity': fares['price_elasticity']},
    }
    for name, policy in policies.items():
        if policy.get('annual_opex', 0.) > 0:
            policy['annual_price_inflation'] = fares['general_price_inflation']
        projection, pricing = price_operating(operational, receipts, programme['comparison']['fare_iqd'], config['model']['iqd_per_usd'], options, **policy)
        case = simulate(capital, projection, config, options, green='blended', extras=True,
                        bridge_rate=liquidity['concessional_annual_rate'], bridge_fee=liquidity['concessional_draw_fee'])
        case['fare_policy'] = pricing
        nominal_discount = (1+config['model']['discount_rate'])*(1+pricing['annual_general_price_inflation'])-1
        case['metrics']['pricing_nominal_discount_rate'] = nominal_discount
        case['metrics']['pricing_project_npv_usd_equivalent'] = sum((op['revenue_usd']-op['opex_usd']-capital.get(op['month'], {}).get('capex', 0.))/(1+nominal_discount)**(op['month']/12) for op in projection)
        case['metrics']['pricing_npv_basis'] = 'Unlevered capital/fare/existing-nonfare/OPEX cashflows, excluding debt, grants and new rights/net-receipt targets; nominal discount compounds the 8% real assumption with general inflation. Capital budgets remain un-escalated.'
        cases[name] = case
    repayment_cases = {}
    projection, pricing = price_operating(operational, receipts, programme['comparison']['fare_iqd'], config['model']['iqd_per_usd'], options,
                                         **policies['fare_5pct_opex_5pct'])
    strategies = {'gap_only_buffered': {'repayment_policy': 'gap_only'},
                  'gap_then_core': {'repayment_policy': 'gap_first'},
                  'loans_then_bonds': {'repayment_policy': 'loans_first'},
                  'cost_priority': {'repayment_policy': 'cost_priority'},
                  'cost_priority_zero_premium': {'repayment_policy': 'cost_priority', 'zero_premiums': True},
                  'cost_priority_noncallable_bonds': {'repayment_policy': 'cost_priority', 'noncallable_bonds': True}}
    for name, strategy in strategies.items():
        case = simulate(capital, projection, config, options, green='blended', extras=True,
                        bridge_rate=liquidity['concessional_annual_rate'], bridge_fee=liquidity['concessional_draw_fee'], **strategy)
        case['pricing_basis'] = 'Same paired 5% tariff/OPEX/income sensitivity and blended financing; three months of current OPEX retained before discretionary payments.'
        repayment_cases[name] = case
    buffered_cost = repayment_cases['gap_only_buffered']['metrics']['total_finance_interest_and_fees_usd']
    original_cost = cases['fare_5pct_opex_5pct']['metrics']['total_finance_interest_and_fees_usd']
    for case in repayment_cases.values():
        case['metrics']['net_finance_cost_saving_vs_buffered_gap_only_usd'] = buffered_cost-case['metrics']['total_finance_interest_and_fees_usd']
        case['metrics']['net_finance_cost_saving_vs_original_no_buffer_usd'] = original_cost-case['metrics']['total_finance_interest_and_fees_usd']
    reference = cases['unfunded_reference']
    original_flows = programme['phased_opening']['cases']['low_demand']['monthly']
    principal = reference['metrics']['core_principal_usd_equivalent']
    debt_draws = reference['metrics']['china_capital_usd']+(reference['metrics']['ordinary_bonds_iqd']+reference['metrics']['bank_capital_iqd'])/config['model']['iqd_per_usd']
    if abs(principal-debt_draws) > .02:
        raise ValueError('drawn principal does not equal lifetime repayments')
    reference_metrics = reference['metrics']
    reconciliation = {
        'capital_uses_usd': sum(r['capex'] for r in capital.values()),
        'capital_sources_usd': programme['total_capex_usd'],
        'capital_difference_usd': sum(r['capex'] for r in capital.values())-programme['total_capex_usd'],
        'core_capital_principal_usd': principal,
        'core_interest_usd': reference_metrics['core_interest_usd_equivalent'],
        'core_fees_usd': sum(r['core_fees_usd_equivalent'] for r in reference['monthly']),
        'lifetime_revenue_usd': sum(r['revenue_usd'] for r in original_flows),
        'lifetime_opex_usd': sum(r['opex_usd'] for r in original_flows),
        'gross_additional_liquidity_usd': reference_metrics['uncovered_support_iqd']/config['model']['iqd_per_usd'],
        'later_retained_cash_usd': reference_metrics['terminal_cash_iqd']/config['model']['iqd_per_usd'],
        'net_lifetime_liquidity_gap_usd': reference_metrics['net_lifetime_operating_and_finance_gap_usd'],
        'debt_audits': audits,
        'cashflow_identity': 'capital sources + operating revenue + conditional extra liquidity = capital uses + OPEX + principal + interest + fees + net reserve deposits + closing cash',
        'green_candidate_capital_usd': sum(r['candidate_capex'] for r in capital.values()),
        'candidate_local_expenditure_usd': sum(r['candidate_capex']-r['candidate_imports'] for r in capital.values()),
    }
    reconciliation['gross_minus_retained_matches_net_gap'] = abs(reconciliation['gross_additional_liquidity_usd']-reconciliation['later_retained_cash_usd']-reconciliation['net_lifetime_liquidity_gap_usd']) < .02
    if abs(reconciliation['capital_difference_usd']) > .05 or not reconciliation['gross_minus_retained_matches_net_gap']:
        raise ValueError('independent capital/lifetime cash reconciliation failed')
    # Solve the scale of genuinely new NET receipts required, rather than
    # declaring that an arbitrary land or advertising target closes the gap.
    import copy
    lower, upper = 0., 1_000_000_000.
    solved = None
    for _ in range(28):
        middle = (lower+upper)/2
        trial_options = copy.deepcopy(options)
        trial_options['additional_sources']['incremental_net_local_receipts_annual_usd'] = middle
        trial = simulate(capital, operational, config, trial_options, green='blended', extras=True,
                         bridge_rate=liquidity['concessional_annual_rate'], bridge_fee=liquidity['concessional_draw_fee'])
        remainder = trial['metrics']['terminal_supplemental_balance_iqd']+trial['metrics']['uncovered_support_iqd']
        if remainder <= config['model']['iqd_per_usd']:
            upper, solved = middle, trial
        else:
            lower = middle
    threshold = {'incremental_net_receipts_annual_usd': upper if solved else None,
                 'basis': 'Additional annual net IQD receipts at full opening, scaled with open fleet; with the illustrative climate grant, rights receipts, green repricing and 2% IQD facility. No existing fare/rent revenue counted twice.',
                 'metrics': solved['metrics'] if solved else None,
                 'status': 'break-even requirement, not a verified revenue forecast or tariff'}
    lower, upper, fare_solved = 1., 8., None
    for _ in range(24):
        middle = (lower+upper)/2
        projection, pricing = price_operating(operational, receipts, programme['comparison']['fare_iqd'], config['model']['iqd_per_usd'], options,
                                             **policies['fare_5pct_opex_5pct'], fare_uplift=middle)
        trial = simulate(capital, projection, config, options, green='blended', extras=True,
                         bridge_rate=liquidity['concessional_annual_rate'], bridge_fee=liquidity['concessional_draw_fee'])
        if trial['metrics']['terminal_supplemental_balance_iqd']+trial['metrics']['uncovered_support_iqd'] <= config['model']['iqd_per_usd']:
            upper, fare_solved = middle, (trial, pricing)
        else:
            lower = middle
    fare_threshold = {'initial_real_fare_multiplier': upper if fare_solved else None,
                      'basis': 'Constant real fare uplift plus annual 5% tariff/OPEX/income indices, assumed -0.30 real-price elasticity, other blended financing and new net receipts unchanged.',
                      'status': 'required sensitivity, not a tariff recommendation or verified demand forecast',
                      'metrics': fare_solved[0]['metrics'] if fare_solved else None,
                      'pricing': {key: value for key, value in fare_solved[1].items() if key != 'monthly_prices'} if fare_solved else None}
    return {'status': 'planning-independent-recalculation-uncommitted', 'scope': 'Baghdad city and one plant only',
            'assumptions': options, 'iqd_per_usd': config['model']['iqd_per_usd'],
            'reconciliation': reconciliation, 'operating_receipts': programme['operating_receipts'],
            'cases': cases, 'additional_receipts_threshold': threshold, 'fare_uplift_threshold': fare_threshold,
            'selected_pricing_sensitivity': 'fare_5pct_opex_5pct',
            'early_repayment': {'status': 'uncommitted_prepaid_at_par_plus_assumed_premium',
                                'cases': repayment_cases,
                                'selected_comparison': 'cost_priority',
                                'currency_basis': 'Chinese credit USD; every other debt IQD; historical FX unchanged',
                                'repayment_basis': 'Oldest outstanding vintage first; keep instalment and shorten maturity. No core principal is repaid twice; no gap draw or uncovered support funds discretionary repayment. Assumed minimum ages: bank 6, Chinese 12, bonds 24 months.'},
            'limitations': [
                'Six-month bond placement envelopes settle monthly at par; they are not advance-funded bond sales. Advance issuance changes carry, reserve and interest costs and needs a separate cash forecast.',
                'Full unrounded placement values reconcile; illustrative IQD 1 million unit counts round upwards and are not executable orders. No auction price, investor demand or mandate is established.',
                'A green label alone uses unchanged domestic pricing. The lower coupon/longer tenor and 0.5% annual guarantee fee are explicit sensitivities, not donor or lender terms.',
                'Climate capital grants replace domestic capital borrowing only, against candidate local expenditure. They do not pay old debt interest, imported invoices already funded 50:50, or increase government cash above 25%.',
                'Incremental land/rights/local receipts are zero in the reference and must be genuinely additional to existing fare, retail, rent and advertising forecasts. Net proceeds after costs, title, statutory powers and independent valuation require qualification.',
                'The supplemental IQD facility pays its own interest and origination fees. Surplus is swept to repayment; terminal balances are exposed rather than assumed refinanced or forgiven.',
                'The illustrative IQD facility has a 13 trillion maximum outstanding commitment; residual cash requirements beyond that cap remain explicitly uncovered. No committed lender or future market capacity is assumed.',
                'Supplemental facilities have no extra DSRA or undrawn commitment fee and no fixed amortisation before the terminal maturity; term sheets can materially increase costs. Long draw availability and the terminal balloon are uncommitted assumptions.',
                'City/plant cash is pooled subject to legally permitted transfers and creditor consent. Factory income/OPEX remain outside the capital-only plant appraisal; no free factory profit is credited.',
                'All non-Chinese debt is modelled in IQD. Foreign-funded concessional programmes need confirmed IQD on-lending or a priced hedge; an unhedged USD development loan would change the currency strategy.',
                'The reference has constant nominal fares, OPEX and FX. Dedicated pricing cases explicitly index fares, OPEX and income independently from financial close. Capital escalation, FX inflation pass-through and separate lifecycle replacement inflation remain outside this sensitivity; full nominal appraisal must include them.',
                'Pricing cases retain fixed nominal core and gap debt terms; supplier terms, floating rates and imported OPEX exposure need qualification. New net revenue targets are held nominal rather than assumed inflation-protected.',
                'Price elasticity is an uncalibrated response to fare relative to indexed income; no transfer, peak switching or low-income household demand survey is modelled. Off-peak trip increases are bounded by the same practical capacity, not new physical capacity.',
                'Early repayment is a contractual sensitivity, not an exercised call right. Bank/Chinese loan eligibility, bond call or voluntary buyback rights, notice, price and premiums require actual terms. The noncallable case forbids all early bond principal. Illustrative minimum draw ages are 6 months for bank credit, 12 for Chinese credit and 24 for bonds; these are not actual covenants.',
                'Cost priority is a coupon/guarantee-fee heuristic, not a globally optimal treasury strategy. Premiums, tax, remaining maturities, future draws and FX can change the best order; no refinancing or capital-issue cancellation is modelled.',
                'A three-month OPEX buffer is funded before discretionary repayment in every early-policy comparison. It is retained at the terminal horizon and earns no income. Original baseline cases have no such additional buffer; savings are compared with a buffered gap-only case as well as the original.',
            ]}



def debt_clearance_label(month):
    return 'not cleared within the model horizon' if month is None else f'cleared in month {month}'


def repayment_outcome(metrics):
    if metrics['terminal_supplemental_balance_iqd'] > .02 or metrics['uncovered_support_iqd'] > .02:
        return 'The case does not repay the facility and cover all required cash within the model horizon.'
    return 'The case repays the facility within the model horizon under these conditional assumptions.'


def early_repayment_report(analysis: dict, finance_path: str) -> list[str]:
    group = analysis['early_repayment']; cases = group['cases']
    selected = cases['cost_priority']['metrics']; baseline = cases['gap_only_buffered']['metrics']
    lines = ['## Surplus cash and early repayment', '',
        'These cases use identical paired 5% fare/OPEX/income assumptions and the same conditional blended capital sources. Each pays OPEX, scheduled principal, interest and fees, then funds the debt-service reserve and a three-month current-OPEX buffer before voluntary repayment. Borrowed gap proceeds and uncovered external cash cannot fund early payments. The extra buffer remains cash held at the terminal horizon and earns no interest.', '',
        'Compare strategies against **buffered gap-only**, rather than attributing the buffer change to repayment savings. Loans-first pays bank credit, Chinese credit and gap credit before bonds. Cost priority pays bank (9%), ordinary bonds (8%), Chinese credit (5%), green bonds (4% plus 0.5% annual guarantee), then gap credit (2%). It is an interest-rate heuristic, not a proof of the globally best strategy.', '',
        '| Surplus strategy | All debt cleared, month from close | Finance cost saving vs buffered gap-only, USD equivalent m | Early-payment premiums, USD equivalent m | Peak gap debt, IQD tn | Terminal unrestricted cash, IQD tn |',
        '|---|---:|---:|---:|---:|---:|']
    for name, case in cases.items():
        m = case['metrics']; cleared = m['all_debt_cleared_month']
        lines.append(f"| {name.replace('_', ' ')} | {cleared if cleared is not None else 'not cleared'} | {m['net_finance_cost_saving_vs_buffered_gap_only_usd']/1e6:,.3f} | {m['early_premiums_usd_equivalent']/1e6:,.3f} | {m['peak_supplemental_balance_iqd']/1e12:,.3f} | {m['terminal_cash_iqd']/1e12:,.3f} |")
    lines += ['',
        f"Cost-priority debt is **{debt_clearance_label(selected['all_debt_cleared_month'])}**; buffered gap-only debt is **{debt_clearance_label(baseline['all_debt_cleared_month'])}**. Net nominal financing savings are **USD {selected['net_finance_cost_saving_vs_buffered_gap_only_usd']/1e6:,.3f}m equivalent**, after USD {selected['early_premiums_usd_equivalent']/1e6:,.3f}m assumed early-payment premiums. Savings include core interest, annual green guarantee charges and supplemental interest/draw fees; they exclude principal, which is returned once. All cases retain IQD {selected['terminal_operating_buffer_iqd']/1e12:,.3f}tn operating buffer separately from unrestricted cash. There is no additional government contribution above 25% of CAPEX in these cases.", '',
        'Assumed premiums are 1% of bank/Chinese/green principal and 2% of ordinary bond principal. A minimum draw age of 6 months (bank), 12 (Chinese) and 24 (both bonds) prevents immediate issue-and-redemption. Eligible vintages are repaid oldest first; contractual instalments are kept and maturity shortens. Notice, issuer call rights, investor consent, buyback price, remaining-maturity compensation, tax and FX require actual agreements. Noncallable-bond sensitivity makes no voluntary bond payments; zero-premium sensitivity removes only the assumed premium, retaining minimum ages.', '',
        '| Facility | Buffered gap-only final principal payment month | Cost-priority final principal payment month | Early principal, native currency | Premium, native currency |', '|---|---:|---:|---:|---:|']
    for name, currency in (('bank_credit', 'IQD'), ('domestic_bonds', 'IQD'), ('chinese_export_credit', 'USD'), ('green_bonds', 'IQD')):
        rows = cases['cost_priority']['monthly']
        early = sum(r[name+'_early_principal_native'] for r in rows)
        premium = sum(r[name+'_early_premium_native'] for r in rows)
        scale = 1e9 if currency == 'IQD' else 1e6; unit = 'bn' if currency == 'IQD' else 'm'
        lines.append(f"| {name.replace('_', ' ')} | {baseline[name+'_final_repayment_month'] if baseline[name+'_final_repayment_month'] is not None else 'no repayment recorded'} | {selected[name+'_final_repayment_month'] if selected[name+'_final_repayment_month'] is not None else 'no repayment recorded'} | {currency} {early/scale:,.3f}{unit} | {currency} {premium/scale:,.3f}{unit} |")
    lines += ['',
        f"The gap facility's final principal payment is in month {selected['liquidity_final_repayment_month']}. Later surplus remains unrestricted cash after debt retirement. Each month's native debt balance equals prior balance plus draws minus scheduled and early principal. Each six-month closing balance is its final month's balance; payments, premiums, interest and reserve movements are period sums. Contractual repayment windows in tranche files describe the original draw terms; the actual final-payment months above incorporate early repayment.", '',
        f"[Monthly cost-priority repayments]({finance_path}/baghdad-early-cost_priority-monthly.csv) · [six-month repayment tranches]({finance_path}/baghdad-early-cost_priority-six-month-tranches.csv) · [loans-first tranches]({finance_path}/baghdad-early-loans_then_bonds-six-month-tranches.csv) · [all six complete calculations]({finance_path}/baghdad-early-repayment.json)", '',
        f"![Surplus repayment comparison]({finance_path}/baghdad-early-repayment.png)", '',
        'Loan prepayment can carry redeployment/unwind charges: the [World Bank Treasury FAQ](https://treasury.worldbank.org/en/about/unit/treasury/ibrd-financial-products/financial-products-faqs) illustrates the concept, without establishing Chinese or Iraqi loan terms. The [US Treasury buyback FAQ](https://treasurydirect.gov/help-center/faqs/buyback-faqs/) and [published purchase results](https://treasurydirect.gov/auctions/announcements-data-results/buy-backs/) illustrate issuer authority and priced buybacks rather than automatic par redemption; they do not supply an Iraqi legal mandate.', '',
        'This repayment allocation does not change the unlevered project NPV or validate demand. Nominal savings over several decades are not present-value gains. CAPEX escalation, FX, lifecycle replacement, floating-rate risk and the uncommitted early funding still require appraisal.', '']
    return lines


def write_outputs(analysis: dict, programme: dict, directory, country) -> None:
    """Publish native spreadsheets and one full, arithmetic-readable report."""
    import csv
    import json
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fx = analysis['iqd_per_usd']
    public_analysis = dict(analysis)
    public_analysis['early_repayment'] = {**analysis['early_repayment'],
        'cases': {name: case['metrics'] for name, case in analysis['early_repayment']['cases'].items()},
        'full_calculation': 'baghdad-early-repayment.json'}
    (directory/'baghdad-finance-reconciliation.json').write_text(json.dumps(public_analysis, indent=2, sort_keys=True)+'\n')
    (directory/'baghdad-early-repayment.json').write_text(json.dumps(analysis['early_repayment'], indent=2, sort_keys=True)+'\n')
    for name, case in analysis['early_repayment']['cases'].items():
        for period, rows in (('monthly', case['monthly']), ('six-month-tranches', case['semiannual'])):
            with (directory/f'baghdad-early-{name}-{period}.csv').open('w', newline='') as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
                writer.writeheader(); writer.writerows(rows)
    for name, case in analysis['cases'].items():
        rows = case['semiannual']
        with (directory/f'baghdad-{name}-six-month-tranches.csv').open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
            writer.writeheader(); writer.writerows(rows)
        if 'fare_policy' in case:
            prices = case['fare_policy']['monthly_prices']
            with (directory/f'baghdad-{name}-monthly-prices.csv').open('w', newline='') as handle:
                writer = csv.DictWriter(handle, fieldnames=list(prices[0]), lineterminator='\n')
                writer.writeheader(); writer.writerows(prices)
        if name in ('unfunded_reference', 'blended_candidate', 'commercial_gap_credit', 'fare_5pct_opex_5pct', 'variable_fare_5pct_opex_5pct', 'fare_5pct_opex_7pct'):
            rows = case['monthly']
            with (directory/f'baghdad-{name}-monthly-finance.csv').open('w', newline='') as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
                writer.writeheader(); writer.writerows(rows)
    rec = analysis['reconciliation']; reference = analysis['cases']['unfunded_reference']
    envelopes = reference['semiannual']
    capital_rows = [row for row in envelopes if row['capex_usd'] > .01]
    years = [row['start_month']/12 for row in capital_rows]
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), layout='constrained')
    base = [0.]*len(capital_rows)
    for key, label, colour in (('government_iqd_cash', 'Government IQD capital cash', '#759a63'),
                              ('bond_face_iqd', 'IQD capital bond face', '#166d77'),
                              ('bank_credit_draw_native', 'IQD capital bank draws', '#5b78a1')):
        values = [row[key]/1e9 for row in capital_rows]
        axes[0].bar(years, values, width=.45, bottom=base, label=label, color=colour)
        base = [a+b for a, b in zip(base, values)]
    axes[0].set_ylabel('IQD billion / six months')
    base = [0.]*len(capital_rows)
    for key, label, colour in (('government_usd_cash', 'Government USD import cash', '#b86e18'),
                              ('chinese_export_credit_draw_native', 'Chinese USD capital loan', '#a45442')):
        values = [row[key]/1e6 for row in capital_rows]
        axes[1].bar(years, values, width=.45, bottom=base, label=label, color=colour)
        base = [a+b for a, b in zip(base, values)]
    axes[1].set_ylabel('USD million / six months')
    for name, label in (('commercial_gap_credit', '8% gap loan'), ('concessional_gap_credit', '2% gap loan'), ('blended_candidate', 'Illustrative blended + 2% gap loan')):
        rows = analysis['cases'][name]['semiannual']
        axes[2].plot([row['end_month']/12 for row in rows], [row['closing_liquidity_debt_iqd']/1e12 for row in rows], label=label)
    axes[2].axhline(analysis['assumptions']['liquidity']['illustrative_cap_iqd']/1e12, color='#555555', linestyle='--', linewidth=1, label='Illustrative maximum outstanding')
    axes[2].set_ylabel('Unpaid gap loan, IQD trillion')
    for ax in axes:
        ax.set_xlabel('Year from assumed financial close')
        ax.legend(fontsize=8, loc='upper right' if ax is not axes[2] else 'upper left')
        ax.grid(axis='y', alpha=.2)
        ax.set_axisbelow(True)
    fig.suptitle('Baghdad + one plant: native capital funding and unpaid supplemental debt')
    fig.supxlabel('Uncommitted planning scenarios; six-month envelopes settle monthly; no escalation or automatic refinancing', fontsize=9)
    fig.savefig(directory/'baghdad-six-month-funding.png', dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), layout='constrained')
    for name, label in (('blended_candidate', 'Flat fares / flat OPEX'), ('fare_5pct_opex_5pct', 'Fares +5%, OPEX +5%, income +5%'), ('variable_fare_5pct_opex_5pct', 'Peak/off-peak + annual 5% indices'), ('fare_5pct_opex_7pct', 'Fares +5%, OPEX +7%, income +5%')):
        rows = analysis['cases'][name]['semiannual']
        axes[0].plot([row['end_month']/12 for row in rows], [row['closing_liquidity_debt_iqd']/1e12 for row in rows], label=label)
    axes[0].axhline(options_cap := analysis['assumptions']['liquidity']['illustrative_cap_iqd']/1e12, color='#777777', linestyle='--', linewidth=1)
    axes[0].set_ylabel('Unpaid gap loan, IQD trillion')
    for name, label in (('fare_5pct_opex_5pct', 'Fares +5%, income +5%'), ('variable_fare_5pct_opex_5pct', 'Peak/off-peak, income +5%'), ('fare_5pct_opex_5pct_income_2pct', 'Fares +5%, income only +2%')):
        rows = [row for row in analysis['cases'][name]['fare_policy']['monthly_prices'] if row['paid_trips'] > 0]
        axes[1].plot([row['month']/12 for row in rows], [row['forty_four_trips_income_share']*100 for row in rows], label=label)
    axes[1].set_ylabel('44 trips / monthly income proxy, %')
    for ax in axes:
        ax.set_xlabel('Year from assumed financial close')
        ax.legend(fontsize=8, loc='upper left')
        ax.grid(alpha=.2)
    fig.suptitle('Fare policies, OPEX inflation and affordability: illustrative blended funding')
    fig.supxlabel(f'Uncommitted 2% IQD facility capped at {options_cap:.0f}tn; cash beyond cap is uncovered; rates and income growth are sensitivities', fontsize=9)
    fig.savefig(directory/'baghdad-fare-inflation-sensitivities.png', dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), layout='constrained')
    for name, label in (('gap_only_buffered', 'Gap-only with buffer'), ('loans_then_bonds', 'Loans before bonds'), ('cost_priority', 'Interest-rate priority'), ('cost_priority_noncallable_bonds', 'Priority, noncallable bonds')):
        rows = analysis['early_repayment']['cases'][name]['semiannual']
        debt = [(r['chinese_export_credit_closing_balance_native']*fx+sum(r[n+'_closing_balance_native'] for n in ('bank_credit', 'domestic_bonds', 'green_bonds'))+r['closing_liquidity_debt_iqd'])/1e12 for r in rows]
        axes[0].plot([r['end_month']/12 for r in rows], debt, label=label)
    axes[0].set_ylabel('All outstanding debt, IQD tn equivalent'); axes[0].set_xlabel('Year from assumed close')
    axes[0].legend(fontsize=8); axes[0].grid(alpha=.2)
    labels = ['Gap first', 'Loans first', 'Cost priority', 'No premiums', 'Noncallable bonds']
    names = ['gap_then_core', 'loans_then_bonds', 'cost_priority', 'cost_priority_zero_premium', 'cost_priority_noncallable_bonds']
    axes[1].bar(labels, [analysis['early_repayment']['cases'][n]['metrics']['net_finance_cost_saving_vs_buffered_gap_only_usd']/1e6 for n in names], color='#166d77')
    axes[1].set_ylabel('Net financing savings, USD equivalent m'); axes[1].grid(axis='y', alpha=.2); axes[1].set_axisbelow(True)
    fig.suptitle('Surplus cash retires debt: identical three-month OPEX buffers')
    fig.supxlabel('Uncommitted 5% fare/OPEX/income sensitivity; premiums and minimum ages assumed; nominal savings, historical FX', fontsize=9)
    fig.savefig(directory/'baghdad-early-repayment.png', dpi=160); plt.close(fig)
    options = analysis['assumptions']; extra = options['additional_sources']; green = options['green']
    lines = ['# Baghdad financing reconciliation and six-month placement programme', '',
        'Scope: Baghdad city and one Baghdad manufacturing plant. Samawah, Mosul and every other city are excluded. Month zero is an assumed financial close, not an approved date. All financing and additional revenues remain uncommitted.', '',
        '## The numbers that must add up', '',
        'The original capital sources and uses reconcile. The confusion was combining upfront capital, repayment of that same capital debt, gross liquidity injections and later retained cash. The revised schedule also spreads city EPC overhead across direct works instead of paying the entire programme allowance against the initial five-day baseline-freeze task. Capital cost is unchanged. An independent implementation rebuilds every debt vintage, interest charge, principal payment and financing fee from native draws; it does not copy the reported support total.', '',
        '| Capital source | Native currency | Native amount, billion | USD equivalent, million |', '|---|---|---:|---:|']
    lines += [f"| {name.replace('_', ' ')} | {value['currency']} | {value['amount']/1e9:,.6f} | {value['usd_equivalent']/1e6:,.3f} |" for name, value in programme['capital_sources_native'].items()]
    lines += [f"| **Capital uses / sources** | Mixed | — | **{rec['capital_uses_usd']/1e6:,.3f}** |", '',
        'Government cash remains 25% of capital, with government USD import cash inside that contribution. Imports are financed 50% government USD cash / 50% Chinese USD loan. Every other loan and bond is IQD. An international green lender must provide confirmed IQD on-lending or a priced currency hedge to preserve that strategy. A green label does not supply additional money.', '',
        '| Lifetime operating / finance reconciliation | USD equivalent, million |', '|---|---:|',
        f"| Fare and existing nonfare receipts | {rec['lifetime_revenue_usd']/1e6:,.3f} |",
        f"| OPEX | {rec['lifetime_opex_usd']/1e6:,.3f} |",
        f"| Repayment of originally drawn capital principal | {rec['core_capital_principal_usd']/1e6:,.3f} |",
        f"| Interest on original capital financing | {rec['core_interest_usd']/1e6:,.3f} |",
        f"| Original financing fees | {rec['core_fees_usd']/1e6:,.3f} |",
        f"| **Net nominal lifetime liquidity deficit** | **{rec['net_lifetime_liquidity_gap_usd']/1e6:,.3f}** |",
        f"| Gross extra cash required as bills fall due | {rec['gross_additional_liquidity_usd']/1e6:,.3f} |",
        f"| Later unrestricted cash retained if those requirements are met | {rec['later_retained_cash_usd']/1e6:,.3f} |", '',
        f"**USD {rec['gross_additional_liquidity_usd']/1e6:,.3f}m gross injections minus USD {rec['later_retained_cash_usd']/1e6:,.3f}m retained cash equals USD {rec['net_lifetime_liquidity_gap_usd']/1e6:,.3f}m net deficit.** Capital purchases are already financed by their capital sources; principal repayments belong to the lifetime cash ledger and must not be added to the construction budget again. Net reserve deposits are zero at the end. This is a nominal identity, not discounted viability, and assumes city/plant cash can legally be pooled", '',
        'A zero-interest, zero-fee revolving bridge is only a mathematical lower bound. Real gap funding must charge interest and fees on the borrowing needed to carry early deficits, repay itself from later surplus and show any terminal debt. Later surplus cannot be counted both as retained cash and as loan repayment.', '']
    income = analysis['operating_receipts']
    lines += ['## Tickets, kiosk rents and advertising already included', '',
        '| Full-network steady annual receipts | IQD billion | USD equivalent, million |', '|---|---:|---:|']
    for label, key in (('Passenger tickets', 'farebox_annual_usd'), ('Station shops and kiosk leases', 'station_retail_annual_usd'), ('Advertising space', 'station_advertising_annual_usd'), ('Total existing operating receipts', 'total_annual_usd')):
        lines.append(f"| {label} | {income[key]*fx/1e9:,.3f} | {income[key]/1e6:,.3f} |")
    lines += ['',
        f"Tickets use {income['annual_paid_trips']/1e6:,.2f}m annual paid trips at IQD {programme['comparison']['fare_iqd']:,.0f} average yield. This is assumed capacity use, not calibrated demand. Shops/kiosks use {income['rentable_sqm']:,.0f} m² at IQD {income['retail_rent_iqd_m2_month']:,.0f}/m²/month and {income['retail_occupancy']:.0%} occupancy; advertising uses {income['advertising_boards']:,.0f} boards at IQD {income['advertising_board_iqd_month']:,.0f}/month and {income['advertising_occupancy']:.0%} occupancy. Rates derive from the retained income proxy, not Baghdad lease quotes. These are gross rental/advertising receipts; dedicated concession costs, tenant demand and collection losses require appraisal.", '',
        'All three receipts enter the existing operating cashflows and therefore already reduce the financing gap. The phased sensitivity scales the combined receipts by opened-fleet share and the separate 50% / 75% / 100% revenue ramp for each line. Retail and advertising demand may follow different ramps in practice. Proposed naming rights, telecom leases, parking, development proceeds or new commercial receipts must be genuinely additional and net of costs; existing rents cannot be booked again or sold upfront while also retained in future revenue.', '',
        '## What gap finance actually does', '',
        f"The illustrative maximum outstanding facility is IQD {options['liquidity']['illustrative_cap_iqd']/1e12:,.3f} trillion (USD {options['liquidity']['illustrative_cap_iqd']/fx/1e9:.3f}bn equivalent). This is a size assumption, not proof that the Iraqi banking market can place it. All available surplus after core obligations and reserves is swept to its repayment. No refinancing or debt forgiveness is assumed at the final maturity.", '',
        '| Scenario | Gross new liquidity draws, IQD tn | Peak facility balance, IQD tn | Uncovered cash beyond facility, IQD tn | Terminal unpaid facility, IQD tn |', '|---|---:|---:|---:|---:|']
    for name, case in analysis['cases'].items():
        if 'fare_policy' in case:
            continue
        m = case['metrics']
        lines.append(f"| {name.replace('_', ' ')} | {m['total_supplemental_draw_iqd']/1e12:.3f} | {m['peak_supplemental_balance_iqd']/1e12:.3f} | {m['uncovered_support_iqd']/1e12:.3f} | {m['terminal_supplemental_balance_iqd']/1e12:.3f} |")
    lines += ['', 'Reference and label-only cases have no gap facility: their uncovered column is the required external cash contribution, not an approved government top-up. With a facility, uncovered cash excludes the separate terminal loan balance; both need a solution. Gross draws can exceed the maximum outstanding commitment when a revolving facility is repaid and redrawn. Conditional ledgers do not establish that an unfunded payment occurred.', '',
        f"Commercial gap credit assumes {options['liquidity']['commercial_annual_rate']:.0%} interest and {options['liquidity']['commercial_draw_fee']:.1%} draw fees. Concessional gap credit assumes {options['liquidity']['concessional_annual_rate']:.0%} interest and {options['liquidity']['concessional_draw_fee']:.1%} draw fees. Neither is a term sheet or an available GCF line. Funding old debt-service deficits is not automatically eligible green use of proceeds.", '',
        '## Explicit blended sensitivity', '',
        f"Candidate climate expenditure is USD {rec['green_candidate_capital_usd']/1e6:,.2f}m of electric rolling stock, solar and charging provision, including USD {rec['candidate_local_expenditure_usd']/1e6:,.2f}m assigned locally. Climate benefit, supplier qualification and green eligibility require independent review. Candidate green bonds replace only domestic bonds attributable to those expenditures; civil works and unrelated overhead are not automatically relabelled.", '',
        f"The blended sensitivity replaces that eligible bond portion with proposed IQD green bonds/sukuk at {green['blended_rate']:.0%}, {green['blended_grace_months']} months' grace and {green['blended_repayment_months']} months' amortisation, with {green['arrangement_fee']:.2%} arrangement fees and {green['annual_guarantee_fee']:.1%}/year enhancement fees on outstanding principal. The lower rate depends on a concessional or guarantee structure; a green label alone retains the original 8% terms and changes no financial outcome.", '',
        f"Additional targets are a **USD {extra['climate_capital_grant_usd']/1e6:,.0f}m** climate capital grant translated into IQD receipts, replacing domestic borrowing against eligible local capital after month {extra['climate_grant_first_month']}; **USD {extra['net_development_rights_usd']/1e6:,.0f}m** net development-rights proceeds in {extra['rights_tranches']} six-month instalments from month {extra['rights_first_month']}; and **USD {extra['incremental_net_local_receipts_annual_usd']/1e6:,.0f}m/year** genuinely new net local receipts at full opening, scaled with the opened fleet. These are editable targets, not appraisals, GCF approvals, developer contracts or statutory levies. Existing rents, advertising and fares cannot be counted again; transaction/development costs and displaced future rents must be deducted. Public land contribution also needs economic valuation.", '']
    threshold = analysis['additional_receipts_threshold']
    if threshold['incremental_net_receipts_annual_usd'] is not None:
        amount = threshold['incremental_net_receipts_annual_usd']
        lines += [f"Solving the model rather than declaring the targets sufficient requires approximately **USD {amount/1e6:,.2f}m/year additional NET receipts** (IQD {amount*fx/1e9:,.2f}bn/year at full opening) to eliminate both uncovered cash and the terminal facility under the other blended assumptions. This is a break-even funding requirement, not a forecast or a recommended passenger fare increase. Any covenant, inflation, FX or demand change can raise it.", '']
    lines += ['## Variable tickets, annual price changes and OPEX inflation', '',
        'The following cases retain the same conditional blended capital/grant/rights/2% IQD facility assumptions. They change fares, OPEX and income separately. A 5% tariff increase with flat costs is an optimistic sensitivity; the paired 5% OPEX case is the requested inflation comparison. None is an adopted fare, a lender commitment or an Iraqi inflation forecast.', '',
        'Indices compound in annual steps from financial close, including the years before first opening. No tickets are sold before service starts; the nominal launch price reflects elapsed inflation. Existing retail/advertising are held flat unless the case explicitly indexes those rents. New net income and rights targets remain fixed nominal amounts. CAPEX escalation and future FX changes still require a separate full nominal appraisal.', '',
        f"Demand responds to fare relative to the indexed income proxy with an illustrative elasticity of {options['fares']['price_elasticity']:.2f}, except the explicitly fixed-demand cases. Income growth is a separate assumption, not evidence that wages will keep pace. Discount-led demand growth is capped at {options['fares']['maximum_demand_multiplier']:.1f} times the baseline, within the original practical capacity. There is no calibrated Baghdad peak-switching or household demand model.", '',
        f"Variable tickets assume {options['fares']['peak_trip_share']:.0%} of baseline trips in a peak tier at {options['fares']['peak_multiplier']:.2f} times the standard fare, and remaining trips at {options['fares']['offpeak_multiplier']:.2f} times it. Each tier gets its own demand response before revenues are combined. Concessions, commuter caps, integrated transfers and off-peak eligibility require an actual tariff design and funding contract; their costs are not silently waived.", '',
        '| Pricing sensitivity | Fare / OPEX / income growth | Full-opening average fare, IQD | 44 trips / income at full opening | Peak facility, IQD tn | Uncovered cash, IQD tn | Terminal debt, IQD tn |', '|---|---|---:|---:|---:|---:|---:|']
    for name, case in analysis['cases'].items():
        if 'fare_policy' not in case:
            continue
        policy, m = case['fare_policy'], case['metrics']
        opened = policy['full_opening']
        lines.append(f"| {name.replace('_', ' ')} | {policy['annual_fare_increase']:.0%} / {policy['annual_opex_inflation']:.0%} / {policy['annual_income_growth']:.0%} | {opened['average_paid_fare_iqd']:,.0f} | {opened['forty_four_trips_income_share']:.1%} | {m['peak_supplemental_balance_iqd']/1e12:.3f} | {m['uncovered_support_iqd']/1e12:.3f} | {m['terminal_supplemental_balance_iqd']/1e12:.3f} |")
    selected = analysis['cases']['fare_5pct_opex_5pct']; sm = selected['metrics']; sp = selected['fare_policy']
    lines += ['',
        f"In the paired 5% case, the first line's average nominal fare is IQD {sp['first_opening']['average_paid_fare_iqd']:,.0f} in month {sp['first_opening']['month']}; at full opening in month {sp['full_opening']['month']} it is IQD {sp['full_opening']['average_paid_fare_iqd']:,.0f}. Its maximum supplemental facility is IQD {sm['peak_supplemental_balance_iqd']/1e12:,.3f}tn, with IQD {sm['uncovered_support_iqd']/1e12:,.3f}tn uncovered cash and IQD {sm['terminal_supplemental_balance_iqd']/1e12:,.3f}tn unpaid at the end. {repayment_outcome(sm)} Early borrowing still needs placed facilities.", '',
        f"At an {options['fares']['general_price_inflation']:.0%} general-price assumption, the 8% real discount assumption becomes {sm['pricing_nominal_discount_rate']:.1%} nominal. The paired-case unlevered NPV is USD {sm['pricing_project_npv_usd_equivalent']/1e9:,.3f}bn equivalent before grants/new rights/net-income targets and with capital still un-escalated. Large distant nominal balances are not present-value wealth or proof of project viability.", '',
        'If income rises with fares, the modelled commuting share stays broadly constant. With income rising only 2%, the same ticket policy becomes progressively less affordable and reduces paid trips. If OPEX rises 7% against 5% fares, the tested financing again leaves uncovered requirements and terminal debt. Maintaining an affordable real tariff, collecting revenue and placing the required early IQD facility matter as much as the nominal annual increase.', '',
        '![Fare and OPEX inflation sensitivities](../../../finance/baghdad-fare-inflation-sensitivities.png)', '',
        '[Paired 5% six-month funding requirements](../../../finance/baghdad-fare_5pct_opex_5pct-six-month-tranches.csv) · [paired monthly prices and affordability](../../../finance/baghdad-fare_5pct_opex_5pct-monthly-prices.csv) · [variable-ticket funding requirements](../../../finance/baghdad-variable_fare_5pct_opex_5pct-six-month-tranches.csv) · [variable monthly tickets](../../../finance/baghdad-variable_fare_5pct_opex_5pct-monthly-prices.csv)', '']
    fare_threshold = analysis['fare_uplift_threshold']
    if fare_threshold['initial_real_fare_multiplier'] is not None:
        lines += [f"The initial real-fare multiplier required to remove both terminal debt and uncovered cash under paired 5% indices and the other blended assumptions is approximately {fare_threshold['initial_real_fare_multiplier']:.3f} times the existing baseline. This is a conditional break-even sensitivity, not a tariff recommendation; it does not guarantee the facility can be placed or that households' incomes will grow.", '']
    lines += early_repayment_report(analysis, '../../../finance')
    lines += ['## Six-month bond sales and capital loan requirements', '',
        '![Native six-month capital funding and supplemental loan balances](../../../finance/baghdad-six-month-funding.png)', '',
        f"Each half-year is a placement/draw envelope, with monthly settlement against capital milestones. Bonds assume par proceeds and an illustrative IQD {options['model']['bond_denomination_iqd']:,.0f} denomination. Face-value requirements below use unrounded values; unit counts in CSV round upwards and separately disclose the resulting indicative face amount. Sale discounts, issuance fees and investor capacity need actual bookbuilding. Selling every half-year amount upfront changes interest/carry and grace clocks and is not simulated here.", '',
        'The government USD cash and Chinese USD loan are separate; government local cash, bonds, bank draws and uncovered liquidity are native IQD. Chinese facility commitment fees retain the existing annual procurement-cohort assumption; six-month envelopes do not assert a new signing schedule. Grace starts on each actual monthly settlement. First/last repayments for a half-year series therefore differ by draw date.', '',
        '| Tranche | Months from close | Government USD m | Government IQD bn | Chinese loan USD m | Bond face IQD bn | Bank loan IQD bn | Additional cash need IQD bn |', '|---|---|---:|---:|---:|---:|---:|---:|']
    for row in reference['semiannual']:
        if row['capex_usd'] > .01:
            lines.append(f"| {row['tranche_id']} | {row['start_month']}–{row['end_month']} | {row['government_usd_cash']/1e6:.2f} | {row['government_iqd_cash']/1e9:.2f} | {row['chinese_export_credit_draw_native']/1e6:.2f} | {row['bond_face_iqd']/1e9:.2f} | {row['bank_credit_draw_native']/1e9:.2f} | {row['uncovered_support_required_iqd']/1e9:.2f} |")
    totals = reference['metrics']
    lines.append(f"| **Total capital envelopes** | — | {programme['government_capital_usd_cash']/1e6:.2f} | {programme['government_capital_iqd_cash']/1e9:.2f} | {totals['china_capital_usd']/1e6:.2f} | {totals['ordinary_bonds_iqd']/1e9:.2f} | {totals['bank_capital_iqd']/1e9:.2f} | — |")
    lines += ['', 'Displayed two-decimal values can differ from full-precision totals by rounding. The six-month CSVs continue through the entire operating/repayment horizon, including periods with no new capital but interest, principal, liquidity draws, reserve movements and cash sweeps. Every tranche independently reconciles its capital sources and uses.', '',
        '[Reference six-month requirements](../../../finance/baghdad-unfunded_reference-six-month-tranches.csv) · [blended six-month requirements](../../../finance/baghdad-blended_candidate-six-month-tranches.csv) · [commercial gap-credit six-month requirements](../../../finance/baghdad-commercial_gap_credit-six-month-tranches.csv) · [independent machine-readable calculation](../../../finance/baghdad-finance-reconciliation.json)', '',
        '## Financing routes to investigate in Iraq', '',
        '| Route | What it can finance | Cashflow treatment and next requirement |', '|---|---|---|',
        '| IQD green bonds / green sukuk | Qualified electric transport, solar and charging capital | Replace conventional debt. Define eligible use, segregate proceeds, obtain independent review and report allocation/impact. Sukuk requires an approved asset/usufruct, legal and Sharia structure; the model does not assume a qualified sukuk issue. |',
        '| GCF / GEF preparation and climate capital support | Climate studies, proven incremental mitigation/adaptation expenditure and eligible capital | Grants reduce debt only when approved; concessional debt still repays. Seek an accredited entity and Iraq NDA support with an emissions/resilience baseline. No grant is booked in the reference. |',
        '| CBI renewable-energy initiative | Qualifying solar installations under the latest participating-bank rules | Obtain bank confirmation of borrower/project eligibility, current caps and terms. This existing Iraqi route is not assumed available for the whole metro or booked as a new capital source. |',
        '| MDB / IFC credit enhancement and IQD syndication | Mobilising Iraqi banks and institutional bond investors | Guarantees improve placement or terms, supply no standalone cash, cost fees and may create sovereign contingent liabilities. Confirm IQD availability, hedge pricing and lender limits. |',
        '| Station-area joint development and development rights | A contracted contribution towards stations/access or unrestricted net proceeds | Independently value parcels and rights, confirm title and revenue powers, tender transparently, deduct costs and future rent foregone. Early rights proceeds can reduce peak liquidity more than late rents. |',
        '| Parking/congestion proceeds, employer transport subscriptions and business improvement charges | Incremental local recurring cash after authorised net collection costs | Separate each revenue stream from existing fare/nonfare receipts; validate legal powers, demand, affordability, exemptions and enforcement. No unverified tax power is assumed. |',
        '| Solar/BESS project company, energy-service or availability contracts | Private financing of an accepted energy package | Remove transferred CAPEX and related city debt once; add the PPA/lease/service payments and guarantees. Compare their NPV with existing electricity/OPEX to avoid a free-CAPEX saving. No assumed saving is booked here. |',
        '| Manufacturer / tooling leases and supplier finance | Qualified equipment and assembly capacity | Deferred invoices or leases are debt-like obligations with priced future payments. Do not duplicate Chinese invoice credit. Factory customer receipts and actual margins need a consolidated business case. |',
        '| Diaspora and institutional IQD issues | Local capital subscription within the bond programme | These are purchaser channels for existing bond face, not another capital source. Disclose investor FX risk, maturity and redemption; no automatic rollover or compulsory pension purchase. |',
        '| Carbon / results-based climate receipts | Verified additional emission reductions after delivery | Treat as contingent upside until methodology, monitoring, ownership and an offtake are contracted; no carbon revenue in the reference or blended case. |', '',
        'Priority: first align civil spending and production with accepted openings, then seek eligible cheaper/longer capital financing and contractual early rights proceeds. Obtain a funded recurring-revenue plan before borrowing a multi-trillion-dinar gap facility. Green finance and creative structures do not cure an unfunded timing mismatch or unsupported demand on their own.', '',
        '## Primary evidence checked 3 October 2026', '',
        'The [GCF Iraq country profile](https://www.greenclimate.fund/countries/iraq) lists two projects with USD 49.5m total GCF finance and USD 5.2m approved readiness support when checked; these are existing country programmes, not Baghdad rail allocations. The [Iraq country programme](https://www.greenclimate.fund/document/iraq-country-programme) provides national priorities. An additional USD 25m application target is therefore a sensitivity requiring a new proposal, not money already available.', '',
        '[GCF investment framework](https://www.greenclimate.fund/access-funding/project-approval-process/investment-framework) and [financial instruments](https://www.greenclimate.fund/partners/investors) support the grant/concessional/guarantee concepts and require viable revenue-generating activities for loans. [ICMA Green Bond Principles](https://www.icmagroup.org/sustainable-finance/the-principles-guidelines-and-handbooks/green-bond-principles-gbp/) require a transparent use-of-proceeds process, allocation controls and impact reporting; they do not promise a reduced coupon.', '',
        'The [CBI renewable-energy amendment of April 2025](https://cbi.iq/news/view/2845) establishes a local financing route to investigate for eligible energy packages. Its limits and bank eligibility cannot be extrapolated into a multi-trillion-dinar metro facility. [IsDB green/sustainability sukuk guidance](https://www.isdb.org/multimedia/accelerating-climate-finance-through-green-and-sustainability-sukuk-including-launch-of-the-guidance-on-sustainable-sukuk) supplies a structuring reference, not a Baghdad issuance mandate.', '',
        '[World Bank guarantee programme](https://www.worldbank.org/en/programs/guarantees-program.print) supports foreign/local-currency obligations subject to project and sovereign approvals. [IFC local-currency syndications](https://www.ifc.org/en/what-we-do/sector-expertise/syndicated-loans-and-mobilization/local-currency-syndications) explains domestic parallel loans and hedge structures; it does not establish an IQD loan offer for OSR. [IFC Iraq investment activity](https://www.ifc.org/en/pressroom/2025/ifc-marks-20-years-of-partnerships-for-impact-in-iraq-announces-1bn-in-new-investm) establishes an existing country presence, not project eligibility or earmarked money.', '',
        '[World Bank land-value-capture guidance](https://ppp.worldbank.org/library/municipal-public-private-partnership-framework-module-16-harnessing-land-value-capture) and [innovative revenues](https://ppp.worldbank.org/maximizing-revenue-funding-infrastructure) provide structuring examples, not Iraq borrowing/tax authority or a Baghdad parcel valuation.', '',
        '[World Bank integrated-fare guidance](https://blogs.worldbank.org/en/transport/nine-suggestions-designing-and-implementing-integrated-fare-systems) supports examining peak/off-peak, transfer and integrated ticket structures. Its [Bogotá affordability study](https://documents.worldbank.org/en/publication/documents-reports/documentdetail/099422408122455548) illustrates the need for household-specific demand evidence; neither calibrates the -0.30 sensitivity for Baghdad or endorses a 5% annual increase.', '',
        '## Remaining modelling and term-sheet limits', '', *['- '+text for text in analysis['limitations']], '',
        '[Editable options](../../../../../../../lib/templates/baghdad-finance-options.toml) · [existing capital assumptions](../../../../../../../lib/templates/iraq-funding.toml) · [original city appraisal](FUNDING-MODEL.md) · [Baghdad-only programme](../../../IRAQ-FUNDING-PROGRAMME.md)', '']
    (country/'Baghdad/engineering/finance/FUNDING-RECONCILIATION.md').write_text('\n'.join(lines))
