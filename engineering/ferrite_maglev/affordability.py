"""City service and whole-life affordability sensitivities, never a bankable price.

Resource cost counts construction once. Borrower cash counts equity plus debt
payments, never adds loan principal to the complete capital cost a second time.
All rates and procurement comparators are declared project hypotheses.
"""
from __future__ import annotations

import math
from pathlib import Path
import tomllib

INPUT = Path(__file__).with_suffix('.toml')
SCHEMA = 'osr-maglev-affordability/1'
SOURCES = [
    dict(title='ORR unattended operation safety principles', checked='2026-10-22',
         url='https://www.orr.gov.uk/sites/default/files/2024-07/railway-safety-principles-factors-for-safe-operation-of-goa4-uto.pdf',
         use='GOA4 responsibilities; UK guidance used as a design reference, not Iraqi approval'),
    dict(title='HM Treasury Green Book 2026', checked='2026-10-22',
         url='https://www.gov.uk/government/publications/the-green-book--2/the-green-book-2026',
         use='Whole-life options appraisal reference; no UK discount rate adopted as Iraqi policy'),
    dict(title='UKEF Buyer Credit Facility', checked='2026-10-22',
         url='https://www.gov.uk/guidance/buyer-credit-facility',
         use='Eligible export-contract finance may cover up to 85%; not 85% of a city programme or an offer'),
    dict(title='UKEF foreign content policy', checked='2026-10-22',
         url='https://www.gov.uk/government/publications/ukefs-approach-to-foreign-content/ukefs-approach-to-foreign-content',
         use='UK economic content and transaction assessment; local factory work alone establishes no eligibility'),
]


def source_paths():
    return [Path(__file__), INPUT]


def positive(value, name, *, zero=False):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0 or (not zero and value == 0):
        raise ValueError('finite positive input required: '+name)
    return value


def load():
    a = tomllib.loads(INPUT.read_text())
    if a['schema'] != 'osr-maglev-affordability-input/1' or [r['id'] for r in a['cases']] != ['low', 'base', 'high']:
        raise ValueError('affordability scenarios required')
    for group in (a, *a['cases']):
        for key, value in group.items():
            if key in {'schema', 'price_basis', 'cases', 'id'}:
                continue
            positive(value, key, zero=True)
            if ('fraction' in key or key in {'annual_real_interest', 'discount_rate', 'charger_efficiency'}) and value > 1:
                raise ValueError('fraction exceeds one: '+key)
    for key in ('construction_years', 'operating_years', 'operating_days_per_year'):
        if type(a[key]) is not int or not 1 <= a[key] <= 366:
            raise ValueError('bounded integer duration required')
    if not 0 < a['charger_efficiency'] <= 1:
        raise ValueError('positive charging efficiency required')
    for row in a['cases']:
        for key in ('repayment_years', 'renewal_interval_years'):
            if type(row[key]) is not int or not 1 <= row[key] <= a['operating_years']:
                raise ValueError('bounded integer repayment/renewal duration required')
    return a


def minutes(text):
    hour, minute = (int(v) for v in text.split(':'))
    if not 0 <= hour < 24 or not 0 <= minute < 60:
        raise ValueError('valid service clock required')
    return hour*60+minute


def service(lines):
    """Whole departures per retained window, limited by current protected headway.

    Daily equivalent circuits smear the service over the circuit: finite start/end
    workings and fleet positioning still need a timetable. No ridership forecast.
    """
    rows = []
    for line in lines:
        used = set()
        departures = 0
        service_minutes = 0
        for slot in line['retained_schedule']:
            start, end = minutes(slot['from']), minutes(slot['to'])
            duration = (end-start) % 1440
            if duration == 0:
                raise ValueError('nonzero service window required')
            occupied = {(start+i) % 1440 for i in range(duration)}
            if used & occupied:
                raise ValueError('overlapping daily service windows')
            used |= occupied
            h = max(positive(slot['headway_min'], 'schedule headway')*60,
                    positive(line['selected_peak_headway_seconds'], 'protected headway'))
            departures += math.floor(duration*60/h)
            service_minutes += duration
        ring = line['retained_shape'] == 'ring'
        circuits = departures*(2 if ring else 1)
        duty = line['duty']
        events = duty.get('arrival_events_per_circuit', [])
        traction = duty.get('fixed_station_and_booster_traction_input_kwh_per_train_circuit')
        missing = not events or any(r.get('station_traction_input_kwh') is None for r in events) or traction is None
        rows.append(dict(line=line['line'], service_hours=service_minutes/60,
            directional_departures_per_day=departures, equivalent_train_circuits_per_day=circuits,
            train_km_per_day=circuits*positive(duty['cycle_distance_m'], 'circuit distance')/1000,
            services_hot_kwh_per_day=circuits*positive(duty['hot_aw3_no_regen_cycle_kwh'], 'services duty', zero=True),
            positive_traction_kwh_per_day=None if missing else circuits*traction,
            fixed_zone_events_per_day=circuits*(len(events)+(1 if ring else 2)*len(line.get('operating_plan', {}).get('powered_top_up_zones', []))),
            energy_data_complete=not missing, timetable_qualified=False))
    return dict(lines=rows, train_km_per_day=sum(r['train_km_per_day'] for r in rows),
        timetable_qualified=False, paid_trips_forecast=None,
        method='Window-rounded departures in each direction at max(retained headway,current exclusive resource headway); fractional equivalent circuits, hot services, positive traction without regeneration credit')


def loan(principal, rate, years):
    positive(principal, 'principal', zero=True)
    positive(rate, 'interest rate', zero=True)
    if type(years) is not int or not 1 <= years <= 100:
        raise ValueError('bounded loan tenor required')
    payment = principal/years if rate == 0 else principal*rate/(-math.expm1(-years*math.log1p(rate)))
    balance = principal
    rows = []
    for year in range(1, years+1):
        interest = balance*rate
        repaid = min(balance, payment-interest) if year < years else balance
        closing = max(0., balance-repaid)
        rows.append(dict(year=year, opening_usd=balance, interest_usd=interest,
            principal_usd=repaid, debt_service_usd=repaid+interest, closing_usd=closing))
        balance = closing
    return rows


def cashflow(capex, opex, a, case):
    debt = capex*case['debt_fraction']
    fees = debt*a['finance_fee_fraction']
    amortisation = loan(debt, case['annual_real_interest'], case['repayment_years'])
    rows = []
    balance = 0.
    for year in range(1, a['construction_years']+1):
        spend = capex/a['construction_years']
        draw = debt/a['construction_years']
        # Half-year average draw convention; interest is paid, never capitalised.
        interest = (balance+draw/2)*case['annual_real_interest']
        balance += draw
        fee = fees if year == 1 else 0.
        rows.append(dict(year=year, phase='construction', capex_usd=spend, debt_draw_usd=draw,
            equity_capex_usd=spend-draw, opex_usd=0., renewal_usd=0.,
            interest_usd=interest, principal_usd=0., finance_fee_usd=fee,
            public_cash_out_usd=spend-draw+interest+fee, closing_debt_usd=balance))
    for operating_year in range(1, a['operating_years']+1):
        repayment = amortisation[operating_year-1] if operating_year <= len(amortisation) else None
        # No renewal at horizon end and no residual value credit.
        renewal = capex*case['renewal_fraction'] if operating_year % case['renewal_interval_years'] == 0 and operating_year < a['operating_years'] else 0.
        interest = repayment['interest_usd'] if repayment else 0.
        principal = repayment['principal_usd'] if repayment else 0.
        rows.append(dict(year=a['construction_years']+operating_year, phase='operation', capex_usd=0., debt_draw_usd=0.,
            equity_capex_usd=0., opex_usd=opex, renewal_usd=renewal, interest_usd=interest,
            principal_usd=principal, finance_fee_usd=0., public_cash_out_usd=opex+renewal+interest+principal,
            closing_debt_usd=repayment['closing_usd'] if repayment else 0.))
    resource = sum(r['capex_usd']+r['opex_usd']+r['renewal_usd'] for r in rows)
    return dict(rows=rows, debt_principal_usd=debt, equity_capex_usd=capex-debt,
        foreign_currency_debt_usd=debt*case['foreign_debt_fraction'],
        annual_level_debt_service_usd=amortisation[0]['debt_service_usd'],
        total_interest_usd=sum(r['interest_usd'] for r in rows), finance_fees_usd=fees,
        undiscounted_resource_cost_usd=resource,
        discounted_resource_cost_usd=sum((r['capex_usd']+r['opex_usd']+r['renewal_usd'])/(1+a['discount_rate'])**r['year'] for r in rows),
        undiscounted_public_cash_usd=sum(r['public_cash_out_usd'] for r in rows),
        annual_opex_plus_debt_service_usd=opex+amortisation[0]['debt_service_usd'],
        annual_renewal_reserve_equivalent_usd=sum(r['renewal_usd'] for r in rows)/a['operating_years'],
        accounting='Resource cost = CAPEX + OPEX + renewals. Borrower cash = equity CAPEX + OPEX + renewals + principal + interest + fees. Debt draws are not revenue; no CAPEX/principal double count.')


def study(report, design, assumptions=None):
    a = assumptions or load()
    operation = service(report['lines'])
    stops, trains = report['totals']['station_records'], report['totals']['trainsets']
    route_km = sum(l.get('operational_route_length_m', l['retained_length_m']) for l in report['lines'])/1000
    sites = stops+report['totals']['added_terminal_service_zones']+report['totals']['powered_top_up_zones']
    cases = []
    for case in a['cases']:
        partial = next(r['priced_scope_subtotal_usd'] for r in report['costs']['scenarios'] if r['scenario'] == case['id'])
        additions = dict(station_building_and_access=stops*case['station_building_access_usd_per_stop'],
            grid_and_connection=sites*case['grid_usd_per_powered_site'],
            depots_and_workshops=trains*case['depot_usd_per_train'],
            land_special_crossing_and_site_premiums=route_km*case['land_special_works_usd_per_route_km'],
            factory_nre_and_initial_spares=case['factory_nre_usd'])
        direct = partial+sum(additions.values())
        additions['design_and_qualification'] = direct*case['design_qualification_fraction']
        additions['epc'] = (partial+sum(additions.values()))*case['epc_fraction']
        additions['contingency'] = (partial+sum(additions.values()))*case['contingency_fraction']
        capex = partial+sum(additions.values())
        complete_energy = all(r['energy_data_complete'] for r in operation['lines'])
        kwh = dict(services=sum(r['services_hot_kwh_per_day'] for r in operation['lines'])/a['charger_efficiency'],
            positive_fixed_zone_traction=None if not complete_energy else sum(r['positive_traction_kwh_per_day'] for r in operation['lines']),
            extra_winding_conversion_loss=sum(r['fixed_zone_events_per_day'] for r in operation['lines'])*case['fixed_zone_loss_kwh_per_event'],
            station_auxiliaries=stops*case['station_auxiliary_kw_per_stop']*24)
        energy_cost = None if not complete_energy else sum(kwh.values())*a['operating_days_per_year']*case['electricity_usd_per_kwh']
        staff = stops*case['staff_per_stop']+trains*case['staff_per_train']+report['totals']['lines']*case['staff_per_line']
        costs = dict(energy=energy_cost, staff_and_supervision=staff*case['loaded_staff_usd_per_year'],
            routine_maintenance_insurance_and_administration=capex*case['routine_maintenance_fraction'])
        opex = None if not complete_energy else sum(costs.values())
        finance = None if opex is None else cashflow(capex, opex, a, case)
        comparator = None if opex is None else cashflow(capex*a['comparison_capex_multiplier'], opex*a['comparison_opex_multiplier'], a,
            {**case, 'foreign_debt_fraction': a['comparison_foreign_debt_fraction']})
        cases.append(dict(id=case['id'], priced_scope_subtotal_usd=partial, scope_additions_usd=additions,
            budget_capex_sensitivity_usd=capex, budget_usd_per_route_km=capex/route_km,
            annual_opex_sensitivity_usd=opex, annual_opex_breakdown_usd=costs,
            daily_energy_breakdown_kwh=kwh, staff_fte_sensitivity=staff,
            energy_data_complete=complete_energy, financing=finance,
            equal_service_procurement_sensitivity=comparator,
            comparative_cash_difference_usd=None if finance is None else comparator['undiscounted_public_cash_usd']-finance['undiscounted_public_cash_usd'],
            comparative_foreign_debt_difference_usd=None if finance is None else comparator['foreign_currency_debt_usd']-finance['foreign_currency_debt_usd']))
    return dict(schema=SCHEMA, currency='USD', price_basis=a['price_basis'], assumptions=a,
        population=design['city'].get('population'), route_km=route_km,
        route_km_per_million_residents=route_km/(design['city']['population']/1e6) if design['city'].get('population', 0)>0 else None,
        service=operation, cases=cases, sources=SOURCES,
        complete_project_estimate_usd=None, financing_offer=False, supplier_quotes=False,
        localisation_fraction=None, ridership_forecast=None, economic_benefit_npv_usd=None,
        limitations=[
            'Scope-covering budget sensitivities are not complete engineered estimates; rates, sites, taxes, customs, inflation and construction risk need local appraisal.',
            'Constant USD with real financing-rate hypotheses; no exchange-rate forecast, tax, revenue, subsidy, grant, fare or guaranteed regeneration assumed.',
            'Loss allowance per fixed-zone event includes a provisional winding/conversion/cooling provision; it is not a measured map. The drive study retains 7.18kWh urban terminal copper heat alone. No free paired-train regeneration.',
            'Missed traction data holds energy OPEX and finance; equivalent circuits are not a complete start/end or disturbed timetable. Reserves and depot movements need their own duty.',
            'Staff counts are paid FTE allowances across shifts; GOA4 removes no station, control-room, rescue or maintenance duty by itself.',
            'Comparator uses identical service quantities and assumed CAPEX/OPEX multipliers with the same debt rate/tenor/fraction; it is not a priced metro alternative or proven saving.',
            'Foreign-currency debt fraction is an independent finance assumption, not imported content or accepted localisation. UKEF eligibility is contract-specific and unconfirmed.',
            'Land-value, access, employment, productivity and travel-time benefits remain unmonetised pending catchments, OD demand, counterfactual and displacement assessment.'
        ], **model_flags())


def model_flags():
    # Keep this arithmetic module independent of model.load() dependency cycles.
    return dict(design_complete=False, physical_validation=False, manufacturing_release=False, physical_release=False)


def markdown(report, *, prefix=''):
    s = report['affordability']
    rows = ['## CAPEX, OPEX and debt repayment', '',
        '**Affordability is a design objective:** maximise useful coverage and domestic capability per unit of construction capital, annual operating cash and debt repayment.', '',
        'These scope-covering scenarios add explicit allowances to the existing partial quantity bill. They are unquoted budget sensitivities; the complete engineered estimate and funding offer remain open. Values are constant USD.', '',
        '| Scenario | Budget CAPEX | Annual OPEX | Annual debt service | Annual OPEX + debt | 30-year operating life + construction borrower cash |',
        '|---|---:|---:|---:|---:|---:|']
    for c in s['cases']:
        f = c['financing']
        money = lambda value: 'HOLD' if value is None else f'${value/1e6:,.1f}m'
        rows.append('| '+c['id']+' | '+' | '.join(money(v) for v in [c['budget_capex_sensitivity_usd'], c['annual_opex_sensitivity_usd'],
            f['annual_level_debt_service_usd'] if f else None, f['annual_opex_plus_debt_service_usd'] if f else None,
            f['undiscounted_public_cash_usd'] if f else None])+' |')
    rows += ['', 'The combined annual figure excludes irregular renewal payments; those are included in the full cash schedule. Construction interest and fees are paid separately. Resource cost counts CAPEX once; borrower cash counts equity and loan repayments, avoiding a second count of financed principal.', '',
        '| Scenario | Debt / equity CAPEX | Foreign-currency debt | Total construction + repayment interest | Whole-life resource cost | Discounted resource cost |',
        '|---|---:|---:|---:|---:|---:|']
    for c in s['cases']:
        f=c['financing']
        if f:
            rows.append(f"| {c['id']} | ${f['debt_principal_usd']/1e6:,.1f}m / ${f['equity_capex_usd']/1e6:,.1f}m | ${f['foreign_currency_debt_usd']/1e6:,.1f}m | ${f['total_interest_usd']/1e6:,.1f}m | ${f['undiscounted_resource_cost_usd']/1e6:,.1f}m | ${f['discounted_resource_cost_usd']/1e6:,.1f}m |")
        else:
            rows.append(f"| {c['id']} | HOLD | HOLD | HOLD | HOLD | HOLD |")
    rows += ['',
        f"[Every allowance, energy component, finance assumption and yearly cash flow]({prefix}summary.json) → `affordability`. Five construction years and 30 operating years are hypotheses. No fare or subsidy revenue is assumed. Complete financing must address local-currency revenue, foreign-currency debt, lender terms, resilience and renewal funding.", '',
        'The same-service procurement sensitivity assumes 1.5× CAPEX and 1.1× OPEX, without changing coverage, timetable, loan rate or tenor. It illustrates the effect of procurement cost and foreign borrowing; it is not an independently priced alternative. Proven cost advantage and local-content percentages remain open.', '',
        '[Whole-life appraisal reference](https://www.gov.uk/government/publications/the-green-book--2/the-green-book-2026). '
        '[UKEF Buyer Credit](https://www.gov.uk/guidance/buyer-credit-facility) can finance up to85% of an eligible export contract, subject to assessment; that does not establish85% financing of this city programme. '
        '[UK content requirements](https://www.gov.uk/government/publications/ukefs-approach-to-foreign-content/ukefs-approach-to-foreign-content) need a transaction-specific content schedule. No UKEF approval, tariff, lender commitment or economic multiplier is assumed.', '']
    rows += ['## Energy and operating cost detail', '',
        '| Scenario | Annual services supply GWh | Positive traction GWh | Extra fixed-zone losses GWh | Station auxiliaries GWh | Electricity USD/kWh | Annual energy cost | Annual staff cost | Annual maintenance/admin allowance |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    days=s['assumptions']['operating_days_per_year']
    for c, assumptions in zip(s['cases'],s['assumptions']['cases']):
        energy=c['daily_energy_breakdown_kwh'];opex=c['annual_opex_breakdown_usd']
        value=lambda v: 'HOLD' if v is None else f'{v*days/1e6:,.1f}'
        money=lambda v: 'HOLD' if v is None else f'${v/1e6:,.1f}m'
        rows.append(f"| {c['id']} | {value(energy['services'])} | {value(energy['positive_fixed_zone_traction'])} | {value(energy['extra_winding_conversion_loss'])} | {value(energy['station_auxiliaries'])} | {assumptions['electricity_usd_per_kwh']:g} | {money(opex['energy'])} | {money(opex['staff_and_supervision'])} | {money(opex['routine_maintenance_insurance_and_administration'])} |")
    rows += ['', 'Hot services and station auxiliary demand are conservative planning allowances, not measured consumption. Positive traction includes no regeneration credit. Additional winding/conversion losses use explicit8/12/20kWh per fixed-zone event, including separately counted boosters; these are sensitivities rather than measured route-specific loss maps. Reserve/depot movement, missed charging, wind, grade, full field maps, electrical diversity and supply resilience need further duty studies. No automatic solar or grid-independence credit is applied.', '']
    return rows
