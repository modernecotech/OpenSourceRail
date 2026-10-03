#!/usr/bin/env python3
"""Publish the complete Baghdad proposal and a separate future Iraqi programme."""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tomllib
from urllib.parse import quote
import zipfile

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, Spacer
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[2]
CITY = ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
COUNTRY = CITY.parent
OUT = CITY/'proposal'
MAX_BYTES = 50*1024*1024
SHARED = [
    'docs/rfcs/0033-tacs-runtime-and-resource-control.md',
    'docs/certification/distributed-onboard-control-profile.md',
    'docs/rolling-stock/design-system.md',
    'docs/rfcs/0011-civil-infrastructure-design-standard.md',
    'docs/rfcs/0014-depot-design-standard.md',
    'docs/rfcs/0013-operations-rulebook.md',
    'docs/operating/city-platform.md',
    'docs/deployment-planning-reference.md',
    'docs/civil/slab-trackforms.md',
]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


book = module('baghdad_proposal_book', ROOT/'tools/automation/build-doc-book.py')
national = module('baghdad_proposal_national', ROOT/'tools/automation/generate-national-briefs.py')


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024*1024), b''):
            value.update(block)
    return value.hexdigest()


def receipt(path):
    return {'bytes': path.stat().st_size, 'sha256': digest(path)}


def read_json(path):
    return json.loads(path.read_text())


def table(headers, rows):
    def cell(value):
        return str(value).replace('|', '/').replace('\n', ' ')
    return '\n'.join(['| '+' | '.join(headers)+' |', '| '+' | '.join(['---']*len(headers))+' |',
                       *['| '+' | '.join(cell(v) for v in row)+' |' for row in rows]])


def usd_m(value):
    return f'{value/1e6:,.3f}'


def check_baseline(programme, package):
    detail=read_json(CITY/'engineering/detail/register.json')
    for relative,sha in detail['sources_sha256'].items():
        if digest(ROOT/relative) != sha:
            raise ValueError('Stale Baghdad engineering source: '+relative)
    if detail['engineering_release'] or detail['family'] != 'metro-6car':
        raise ValueError('Unexpected engineering family/release boundary')
    for relative, sha in programme['sources_sha256'].items():
        if digest(ROOT/relative) != sha:
            raise ValueError('Stale Baghdad financing source: '+relative)
    if programme['included_cities'] != ['Baghdad'] or programme['factory']['anchor_city'] != 'Baghdad':
        raise ValueError('Baghdad finance cannot include future national cities')
    if abs(sum(v['usd_equivalent'] for v in programme['capital_sources_native'].values())-programme['total_capex_usd']) > .02:
        raise ValueError('Capital sources and uses disagree')
    if not package['planning_example_complete'] or package['operational_release']:
        raise ValueError('Unexpected Baghdad planning/release status')
    ops = read_json(CITY/'operations/baghdad-operations-manifest.json')
    payload = CITY/'operations'/ops['file']
    if not payload.is_file() or digest(payload) != ops['compressed_sha256']:
        raise ValueError('Materialise the current Baghdad operations payload with ./osr city baghdad')


def national_context(programme):
    cities = [national.load_city(path)[1] for path in sorted(COUNTRY.glob('*/design.toml'))]
    factory = max(c.vehicle_modules for c in cities)*national.NATIONAL_FACTORY_PER_VEHICLE_USD
    aggregate = national.aggregate_breakdowns([c.breakdown for c in cities], national_factory_usd=factory)
    factory_epc = factory*float(tomllib.loads((ROOT/'lib/templates/capex-costs.toml').read_text())['overhead']['epc_fraction'])
    if abs(factory-programme['factory']['cost_usd']) > .02 or abs(factory_epc-programme['factory']['epc_usd']) > .02:
        raise ValueError('National shared factory differs from the single Baghdad plant')
    rows = []
    for c in sorted(cities, key=lambda c: (-c.population, c.name)):
        path = COUNTRY/c.name/'design.toml'
        d = tomllib.loads(path.read_text())
        rows.append({'city': c.name, 'population': c.population, 'lines': len(d['lines']),
                     'stations': len(d['stations']), 'route_km': sum(l['length_m'] for l in d['lines'])/1000,
                     'family': d['lines'][0]['rolling_stock'], 'trainsets': c.fleet_trainsets,
                     'vehicle_modules': c.vehicle_modules, 'city_capex_usd': c.breakdown.total_usd})
    city_total = sum(c.breakdown.total_usd for c in cities)
    if abs(city_total+factory+factory_epc-aggregate.total_usd) > .02:
        raise ValueError('National capital reconciliation failed')
    return {'status': 'future-catalogue-planning-not-funded', 'cities': rows, 'city_count': len(rows),
            'represented_population': sum(c.population for c in cities),
            'trainsets': sum(c.fleet_trainsets for c in cities), 'vehicle_modules': sum(c.vehicle_modules for c in cities),
            'city_capital_usd': city_total, 'shared_factory_usd': factory, 'shared_factory_epc_usd': factory_epc,
            'total_national_capital_usd': aggregate.total_usd,
            'future_incremental_city_capital_after_baghdad_usd': aggregate.total_usd-programme['total_capex_usd'],
            'imported_procurement_usd': aggregate.imported_usd, 'local_procurement_usd': aggregate.local_usd,
            'factory_count': 1, 'baghdad_financing_includes_national_expansion': False,
            'limitations': ['Catalogue budgets, un-escalated and unquoted; no national debt or appropriations agreed.',
                            'The factory and its EPC are included once in both scopes; incremental expansion adds other cities only.',
                            'Expansion capacity, factory renewal/expansion, intercity links and national governance costs remain unpriced.',
                            'Represented population is a sum of planning city populations, not measured rail catchment or unique national beneficiaries.']}


def build_narrative(d, s, p, f, n, ops, deployment):
    comp = p['comparison']; rec = p['independent_recalculation']; indexed = rec['cases']['fare_5pct_opex_5pct']
    prices = rec['fare_pricing']['fare_5pct_opex_5pct']; early = rec['early_repayment']['cases']; fx = 1300.
    energy = national._energy_plan(d, s, national.compute_stats(d, s, d['city']['population']))
    profile = tomllib.loads((ROOT/'lib/templates/rolling-stock.toml').read_text())['profiles']['metro-6car']
    terms = tomllib.loads((ROOT/'lib/templates/iraq-funding.toml').read_text())
    fareopts = tomllib.loads((ROOT/'lib/templates/baghdad-finance-options.toml').read_text())
    line_rows = []
    for line in d['lines']:
        fleet = next(row for row in d['fleets'] if row['line'] == line['name'])
        line_rows.append([line['name'], line['shape'], f"{line['length_m']/1000:.3f}",
                          sum(st['line']==line['name'] for st in d['stations']), fleet['peak_count'],
                          fleet['trainset_count'], next(x['opening_month'] for x in p['phased_opening']['phases'] if x['line']==line['name'])])
    civil = {}
    for segment in d['civil_segments']:
        civil[segment['class']] = civil.get(segment['class'],0.)+segment['to_station_m']-segment['from_station_m']
    cap_rows = [[row['bucket'].replace('_',' '), usd_m(row['total_usd']), usd_m(row['imported_usd']), usd_m(row['local_usd'])]
                for row in f['capex_usd']['procurement_origin_buckets']]
    cap_rows += [['Baghdad plant', usd_m(p['factory']['cost_usd']), usd_m(p['factory']['cost_usd']*national.IMPORTED_SHARE['production_plant']), usd_m(p['factory']['cost_usd']*(1-national.IMPORTED_SHARE['production_plant']))],
                 ['Plant EPC', usd_m(p['factory']['epc_usd']), usd_m(p['factory']['epc_usd']*national.IMPORTED_SHARE['epc_overhead']), usd_m(p['factory']['epc_usd']*(1-national.IMPORTED_SHARE['epc_overhead']))],
                 ['Total Baghdad capital', usd_m(p['total_capex_usd']), usd_m(comp['osr_imported_purchases_usd']), usd_m(comp['osr_local_purchases_usd'])]]
    source_rows = [[name.replace('_',' '), value['currency'], f"{value['amount']:,.0f}", usd_m(value['usd_equivalent'])]
                   for name,value in p['capital_sources_native'].items()]
    selected_capital = early['cost_priority']
    candidate_rows = [[name.replace('_',' '), value['currency'], f"{value['amount']:,.0f}", usd_m(value['usd_equivalent'])]
                      for name,value in p['capital_sources_native'].items() if name.startswith('government_')]
    for label, currency, value in [('Chinese export credit','USD',selected_capital['china_capital_usd']),
                                    ('Ordinary IQD bonds','IQD',selected_capital['ordinary_bonds_iqd']),
                                    ('Green IQD bonds','IQD',selected_capital['green_bonds_iqd']),
                                    ('Bank capital credit','IQD',selected_capital['bank_capital_iqd']),
                                    ('Conditional climate capital grant','IQD',selected_capital['climate_grant_iqd'])]:
        candidate_rows.append([label,currency,f'{value:,.0f}',usd_m(value if currency=='USD' else value/fx)])
    receipts = p['operating_receipts']
    cases = [[name.replace('_',' '), f"{m['peak_supplemental_balance_iqd']/1e12:.3f}",
              f"{m['uncovered_support_iqd']/1e12:.3f}",f"{m['terminal_supplemental_balance_iqd']/1e12:.3f}"]
             for name,m in rec['cases'].items()]
    early_rows = [[name.replace('_',' '), m['all_debt_cleared_month'],
                   usd_m(m['net_finance_cost_saving_vs_buffered_gap_only_usd']), usd_m(m['early_premiums_usd_equivalent'])]
                  for name,m in early.items()]
    national_rows = [[c['city'],f"{c['population']:,}",c['family'],f"{c['route_km']:.1f}",c['trainsets'],usd_m(c['city_capex_usd'])]
                     for c in n['cities']]
    intro = f'''# Baghdad Proposal

OpenSourceRail proposes an owner led feasibility and front end engineering programme for Baghdad, with Iraqi train manufacture and local infrastructure delivery. This proposal brings the Baghdad network, railway systems, operating organisation, delivery evidence and financing together, and sets out a separate path for future national development. It is addressed to the prospective Iraqi public sponsor, Baghdad authorities, operating organisation and financing partners; no appointment or financing commitment is asserted.

The current planning network is **{comp['osr_lines']} lines, {comp['osr_route_km']:.1f} km of double track route, {comp['osr_stations']} stations and {sum(x['trainset_count'] for x in d['fleets']):,} six car trainsets**. Baghdad capital, including one manufacturing plant and its EPC, is **USD {p['total_capex_usd']/1e9:.3f} billion equivalent**. The direct government capital contribution is **25%**. Imports are financed 50% government USD cash and 50% proposed Chinese USD credit; all remaining capital cash, bonds and bank debt are IQD.

The immediate decision proposed is to establish a sponsor, commission survey and demand work, develop the first operable line and plant packages, qualify suppliers and obtain executable financing terms. Construction and operating release require the recorded physical and approval gates. The current resource constrained plan reaches first line revenue in month {prices['first_opening']['month']} and full operation in month {prices['full_opening']['month']} after financial close. That long schedule is a material design and delivery problem to resolve; this proposal does not substitute a five year promise.

## How to read the proposal

The first part states the integrated proposal and the decisions it needs. The next part prints the detailed network registers and six month financing schedules. The technical appendices reproduce every current Baghdad Markdown report, the national brief and selected shared standards. The supporting ZIP preserves the full controlled Baghdad files, every Baghdad financing spreadsheet, the operations payload, national city design inputs and the cited shared references. The source inventory and manifest identify exact file bytes.

Baghdad is the only financed city. National expansion is a future strategic option with its own budgets and approvals. Procurement origin, loan currency and reporting currency are different measures. USD equivalents use the historical model anchor of IQD {fx:,.0f}/USD; this is not a current execution quote. All prices, demand, debt terms and rights proceeds remain planning assumptions. Older generic foreign turnkey examples reproduced in source appendices are separate from the historical 148 km comparison and the scheduled Baghdad financing cases.

## Baghdad network and population access

The design retains a planning population of {comp['planning_population']:,}. The {comp['anchor_weighted_coverage']:.1%} anchor weighted coverage proxy represents {comp['anchor_based_resident_proxy']:,} residents under the model. It is not measured population within an 800 m walking network, nor the number of unique passengers. River crossings, actual entrances, walking barriers and feeders need a surveyed population and access model. A larger network provides a scope to evaluate; it does not prove higher coverage than another proposal.

{table(['Line','Shape','Route km','Stations','Peak fleet','Total fleet','Opening month'],line_rows)}

![Baghdad network](../baghdad-network-map.png)

Line names are controlled design identifiers. Public station names, route brands and final termini require owner approval. Chainages, coordinates, interchange platforms and fleet roles are printed in the network registers and retained without replacing the established layout.

The service concept operates 05:30 to 02:00 with a three minute protected peak headway. The current scheduled journeys and fleet sizing are capacity led; accepted junction/authority capacity, ridership, a timetable, station crowding and degraded recovery need operating review. The 831 trainsets comprise 751 peak, spare and cold reserve roles documented in the annex.

## Trains and imported component strategy

The Baghdad profile is metro 6car: {profile['cars']} cars, {profile['length_m']} m body length, {profile['passenger_capacity']} passengers at nominal planning load including {profile['seat_count']} seats, and {profile['crush_capacity']} at short duration crush load. Each train has {profile['onboard_battery_nameplate_kwh']:,.0f} kWh nameplate / {profile['onboard_battery_kwh']:,.0f} kWh usable LFP battery capacity, {profile['traction_controller_count']} traction controllers, {profile['traction_peak_kw']:,.0f} kW peak traction and a {profile['hvac_design_ambient_c']} C design ambient. These are reference profiles requiring supplier and physical qualification, not delivered fleet performance.

The local industrial scope is train assembly, body modules, fit out, wiring, coatings, inspection, testing and maintenance. Imported scope includes bogies, batteries, windows, doors, solar equipment and manufacturing tooling within existing capital allowances. Chinese supplier origin and export lender eligibility need evidence for every financed item; the entire imported basket is currently an unqualified scenario. Candidate CRRC equipment remains subject to competitive supplier selection, interface and safety qualification. There is no established CRRC partnership, quotation or endorsement.

Shared LM3 fabrication and first article documentation is reference process evidence for a three car platform. It does not qualify Baghdad's six car consist. The national programme should qualify the shared modules and then validate each consist and its interfaces, rather than treating a shared drawing as an accepted Baghdad train.

## Civil infrastructure and stations

The civil screen contains {len(d['civil_segments']):,} segments: '''
    intro += ', '.join(f'{length/1000:.1f} km {name}' for name,length in civil.items())+'. '
    intro += f'''Route kilometres describe double track corridors; they are not track kilometres or a measurement of all sidings. Station products, {len(d['interchanges'])} interchange complexes and {len(d['junctions'])} junction records are bound to the generated layout.

The proposed civil programme starts with survey control, utilities, property and access, geotechnical investigation, flood/drainage levels, alignment and station fit. Desktop soil inputs contain 7,287 sample locations and 65 missing profiles; they do not supply foundation bearing capacity, groundwater or deep stratigraphy. Structural calculations, spans, erection, movements and independent checking must follow route specific evidence. Generated alignment exports have unfitted curves, placeholder vertical profiles and undesigned cant.

Stations require accessible approaches, platforms, passenger information, fire and evacuation design, fare equipment, retail and advertising layouts, security, sanitation and maintenance access. Platform and station access standards must be checked against the final six car envelope and passenger demand. Equipment and architecture references do not establish installed compliance.

The current USD 8m depot allowance remains unreconciled to physical stabling, workshops, power, fire and security. Workshop bays cannot be counted as overnight train parking. The current policy proposes two revenue trains at selected powered stations and line local storage for remaining fleet; usable tracks, charging, protected morning release, evening repositioning and repeated day replay remain open. The depot and stabling appendices retain these failures explicitly.

## Energy and desert operation

The current duty model schedules 3,952 one way journeys and about 217,090 train km per day, with 2,053.8 GWh annual traction demand. It assigns 52.1 MW station/depot PV, 354.0 MWh site storage, 316.0 MW connected charging and {energy.solar_plant_kw/1000:.1f} MW dedicated solar. The design's zero annual residual grid/PPA import is an energy accounting result; it does not establish uninterrupted operation or installed grid independence.

Storage endurance, adverse weather, PV land, heat/dust derating, losses, supplier fire separation, actual charging duty, protection and backup import need a time resolved operating appraisal. Snapshot solver passes and grid only diagnostics do not close these gates. Battery protection and cabin/battery thermal separation must be qualified at the declared ambient and duty. No claimed unlimited battery autonomy or accepted solar islanding is used to close financing.

![Engineering map](../engineering/screenshots/baghdad-qgis-engineering-map.png)

## Train control and operational safety

The current architecture reference is RFC 0033, TACS runtime and committed resource control. RFC 0032's separate authority/protection prototype is superseded. The design retains committed resource ownership in the interlocking, ordered consensus decisions, onboard movement authority, automatic train protection, station departure gates and final brake requests. OCC supplies service intentions and observations; ERP and supervision cannot bypass railway authority or clear protection latches.

The reference uses three static consensus voters and two logical protection channels. Hardware placement, independent power/network domains, sensing, brake outputs and common cause analysis need assessment. Two software channels do not establish independent safety hardware. Lost required permissions, stale/invalid evidence and missing physical proving retain restrictive protection. The runtime is a synthetic process reference and not a deployed Baghdad control system or safety certificate. Existing Baghdad timetable simulations do not constitute RFC 0033 physical acceptance.

## Iraqi manufacture and local economic benefit

The Baghdad plant is sized from {p['factory']['vehicle_modules']:,} vehicle modules. Its base allowance is USD {usd_m(p['factory']['cost_usd'])}m plus USD {usd_m(p['factory']['epc_usd'])}m EPC, counted once outside city CAPEX. The current plant construction assumption is {p['factory']['planning_build_working_days']} working days before train production. Factory siting, freight access, utilities, tooling, staff, production rate, quality capacity and six car qualification require their own approved business and delivery plan.

Baghdad procurement assigns USD {comp['osr_local_purchases_usd']/1e9:.3f}bn equivalent locally. This is potential local expenditure, not payroll, GDP added or a guaranteed Iraqi content ratio. Local train and infrastructure work can retain skills, supplier income, repair capacity and spares knowledge. The plant appraisal covers capital financing only; manufacturing income, factory OPEX and commercial margins need a separate business case. No multiplier, tax recovery, construction job count or future national plant profit is booked as project cash without evidence. Exported components retain foreign exchange and supply chain exposure.

## Operating organisation and digital management

The funded operating allowance is {comp['operating_fte']:,} indicative full time equivalents, including OCC/remote assistance, fleet maintenance, infrastructure/energy, stations, passenger service, administration and training. Annual labour allowance is IQD {comp['operating_labour_annual_iqd']/1e9:.3f}bn. It is a planning FTE and cost model rather than an accepted shift, leave or legal duty roster. Construction and factory headcount await measured work hours, crew mixes, wages and throughput.

{table(['Operating group','Indicative FTE'],[[k.replace('_',' '),v] for k,v in f['workforce']['groups_fte'].items()])}

The Baghdad operating package contains {ops['assets']:,} assets, {ops['manufacturing_tasks']:,} manufacturing/verification tasks, {ops['manufacturing_materials']:,} material/procurement rows, {ops['maintenance_tasks']:,} maintenance tasks and {ops['qa_actions']:,} QA actions. These are generated planning records. Actual purchase orders, execution, measurements and accountable release evidence remain distinct. The project twin, ERPNext/Frappe integration, supervision, QR identities, maintenance and advisory AI support business work; they do not issue movement or safety release authority.

![Baghdad operations dashboard](../offer/screenshots/baghdad-operations-dashboard.png)

## Delivery and commissioning sequence

First obtain survey and demand inputs, freeze a viable first line and plant scope, and reconcile depot and energy duties. Qualify long lead components and the first six car train, then deliver infrastructure, energy, station systems and trained operating staff in accepted phases. Each line needs its own operating and safety acceptance before fare revenue is realised.

The current capital milestones span 347 months, based on 260 working days/year and 30 pre NTP working days. Production is constrained by the current factory/work centres; commissioning adds an explicit three month allowance. Conditional first/full network opening is month 66/346. Opening weighted demand and the 25% fixed / 75% variable OPEX proxy require a surveyed phase specific plan. Expanding production capacity could change those dates, but needs a priced resource and funding revision; no uncosted acceleration is assumed.

![Baghdad project twin](../offer/screenshots/baghdad-project-twin.png)

## Baghdad capital and procurement origin

{table(['Capital scope','USD eq m','Imported USD m','Local USD eq m'],cap_rows)}

The city and plant total includes the plant EPC once. Budgets are unquoted planning estimates; land, utilities, taxes/duties, escalation, contingency and accepted depot/site scope require closure. Loan principal repaid later is a financing cashflow, not additional construction CAPEX. Origin shares do not establish citizenship of vendors, employment or lender eligibility.

## Baghdad financing in USD and Iraqi dinars

{table(['Capital source','Currency','Native amount','USD equivalent m'],source_rows)}

Government cash totals USD {sum(p['capital_sources_native'][k]['usd_equivalent'] for k in ('government_import_cash','government_local_cash'))/1e9:.3f}bn equivalent, exactly 25% of capital. Its USD {p['government_capital_usd_cash']/1e6:.3f}m import cash is inside that limit. The same amount of Chinese USD debt covers the other half of imports. Remaining capital sources are IQD. Combined USD capital funding is USD {p['usd_denominated_capital_usd']/1e9:.3f}bn ({p['usd_denominated_capital_share']:.2%}); IQD is {p['iqd_denominated_capital_share']:.2%}. Only Chinese credit is USD debt, while government also needs USD cash for downpayments.

{table(['Facility','Currency','Rate assumption','Grace months per draw','Amortisation months','Arrangement fee'],[[name.replace('_',' '),terms[name]['currency'],f"{terms[name]['annual_rate']:.0%}",terms[name]['grace_months_from_draw'],terms[name]['repayment_months'],f"{terms[name]['arrangement_fee']:.1%}"] for name in ('chinese_export_credit','domestic_bonds','bank_credit')])}

Bond and bank capital split the residual after government and Chinese credit 75:25. Interest, fees and reserve deposits are funded separately in the cash forecast. A direct 25% capital contribution does not cap sovereign bond liabilities, guarantees or all lifetime public risk. Ministry of Finance issuance powers, sponsor structure, investor mandates, IQD placement capacity, draw availability and creditor consent for city/plant pooling need confirmation. Chinese supplier and lender qualification remains pending. Terms are sensitivities, not loan offers or an approved appropriation.

The capital source table above is the reference allocation. The conditional blended/early repayment case below replaces part of those ordinary bonds with green bonds and adds a climate grant that reduces domestic borrowing. It is a separate capital mix with the same total uses, government cash and Chinese credit; the two tables must not be added together.

{table(['Conditional blended capital source','Currency','Native amount','USD equivalent m'],candidate_rows)}

The conditional capital grant replaces USD 25m equivalent of domestic borrowing. Additional development rights and new local operating receipts enter later project cash and are not counted as construction capital a second time. Supplemental gap draws pay financing/OPEX/reserve cash needs and are separate from both capital tables.

## Early deficits and additional financing

The independent flat price reconstruction requires USD {rec['reconciliation']['gross_additional_liquidity_usd']/1e9:.3f}bn gross early additional cash and retains USD {rec['reconciliation']['later_retained_cash_usd']/1e9:.3f}bn later. Their difference is USD {rec['reconciliation']['net_lifetime_liquidity_gap_usd']/1e6:.3f}m net nominal deficit before pricing gap finance. These figures cannot be added to construction capital as though they were new infrastructure. Later revenue cannot fund an earlier payment without a priced and available facility.

The candidate replaces eligible ordinary capital bonds with IQD green debt at 4% plus arrangement and 0.5% annual guarantee charges; it also tests an uncommitted USD 25m equivalent climate grant, USD 300m equivalent net development rights and USD 25m equivalent annual additional net local receipts. A green label alone changes no coupon. Grants replace eligible domestic capital borrowing; guarantees enhance credit rather than provide cash. Supplemental IQD credit at 2% and a 0.5% draw fee is capped at IQD 13tn outstanding, not treated as proven market capacity. All these conditional sources require legal, donor, investor and valuation evidence.

Additional routes to qualify include climate/renewable energy grants or concessional finance, guaranteed IQD on lending, phased green bonds/sukuk, development rights and station land leases, telecom/fibre leases, naming rights, sponsorship, employer travel contracts and carefully priced concessions. Carbon receipts remain unbooked contingent upside. Upfront lease receipts cannot be added while the same future rents remain in revenue. Keep net proceeds after costs and any transferred liabilities; foreign development finance needs confirmed IQD on lending or a priced hedge to preserve the currency structure.

{table(['Financing and pricing sensitivity','Peak gap IQD tn','Uncovered IQD tn','Terminal gap IQD tn'],cases)}

## Passenger fares and other operating income

Base model average paid trip yield is IQD {comp['fare_iqd']:,.0f}. At full steady operation, existing fares contribute IQD {receipts['farebox_annual_usd']*fx/1e9:.3f}bn/year, shops/kiosks IQD {receipts['station_retail_annual_usd']*fx/1e9:.3f}bn and advertising IQD {receipts['station_advertising_annual_usd']*fx/1e9:.3f}bn. These already reduce the funding gap. Rental occupancy is 88%, advertising 85%; prices, collection and customer demand are not verified Baghdad lease quotations. Commercial figures are gross receipts, with dedicated concession costs requiring appraisal.

Low capacity use assumes {comp['annual_low_case_paid_trips']/365:,.0f} paid trips/day, not unique travellers or a demand survey. The proposed fare design should evaluate concession funding, student and low income access, commuter caps, transfer integration, peak/off peak tiers and collection costs before adopting a tariff. Neither a fare increase nor future kiosk rent places the early financing by itself.

The base full network operating allowance totals USD {usd_m(f['annual_opex_usd']['total'])}m/year equivalent, before the separate inflation sensitivities. Existing maintenance includes a battery renewal reserve on a 12 year reference cycle and fixed asset renewal allowances; it is not an accepted lifecycle replacement plan. Do not add the same battery reserve as new CAPEX. Condition based renewal quantities, inflation, dedicated concession costs, tax and supplier maintenance terms need qualification.

{table(['Base steady annual OPEX','USD equivalent m'],[[k.replace('_',' '),usd_m(v)] for k,v in f['annual_opex_usd']['components'].items()])}

## Annual ticket increases and OPEX inflation

The requested paired sensitivity indexes fares, OPEX and income 5% annually from financial close. No tickets are sold before opening. Nominal average fares are IQD {prices['first_opening']['average_paid_fare_iqd']:,.0f} at first opening and IQD {prices['full_opening']['average_paid_fare_iqd']:,.0f} at full opening. With 5% income growth, 44 trips remain {prices['full_opening']['forty_four_trips_income_share']:.1%} of the income proxy. With only 2% income growth that burden reaches 26.4% at full opening and the assumed real price elasticity reduces paid trips.

Variable pricing tests 40% of baseline trips at 1.25 times the standard fare and 60% at 0.90 times it, with separate demand response and the same capacity limit. If OPEX grows 7% while fares/income grow 5%, the model leaves IQD {rec['cases']['fare_5pct_opex_7pct']['uncovered_support_iqd']/1e12:.3f}tn uncovered cash and IQD 13tn unpaid gap debt. Revenue inflation alone is insufficient. Existing rent is flat unless the rental indexation sensitivity is chosen; new net rights/receipt targets are held nominal.

The paired case's unlevered NPV is USD {indexed['pricing_project_npv_usd_equivalent']/1e9:.3f}bn at {indexed['pricing_nominal_discount_rate']:.1%} nominal discount, excluding new grant/rights/net income targets and with un-escalated capital. Paying debt under a nominal model is not evidence of positive discounted project value. CAPEX escalation, renewal inflation, future FX, floating rates and surveyed demand remain material appraisal work.

![Fare and OPEX sensitivities](../../finance/baghdad-fare-inflation-sensitivities.png)

## Surplus cash and early debt retirement

Surplus first pays OPEX, scheduled principal, interest and fees, then debt service reserves and three months of current OPEX. Voluntary payments cannot be funded by a new gap draw or uncovered cash in the same month. All comparisons below use the same buffers and 5% fare/OPEX/income inputs. Scheduled and voluntary principal are deducted once from native balances.

{table(['Repayment policy','All debt cleared month','Net saving vs buffered gap only USD eq m','Premium USD eq m'],early_rows)}

Cost priority retires bank credit, ordinary bonds, Chinese credit, green bonds, then cheaper gap credit. Under assumed contractual rights it saves USD {usd_m(early['cost_priority']['net_finance_cost_saving_vs_buffered_gap_only_usd'])}m equivalent after premiums and clears debt in month {early['cost_priority']['all_debt_cleared_month']} versus {early['gap_only_buffered']['all_debt_cleared_month']} for buffered gap only. Loans first saves USD {usd_m(early['loans_then_bonds']['net_finance_cost_saving_vs_buffered_gap_only_usd'])}m. All retain IQD {early['cost_priority']['terminal_operating_buffer_iqd']/1e12:.3f}tn operating buffer at the horizon.

Premiums assume 1% bank/Chinese/green and 2% ordinary bonds, with minimum draw ages 6/12/24 months respectively. Eligible vintages are oldest first, retaining instalments and shortening maturity. Calls, notice, compensation, tax and market buyback prices need actual terms. The noncallable case makes no early bond payments; cost ordering is a heuristic rather than a globally best solution. Savings are nominal finance costs, not principal savings or present value wealth. Month numbers run from financial close, with no calendar commencement date assumed.

![Early debt retirement](../../finance/baghdad-early-repayment.png)

## Historical Baghdad metro comparison

{table(['Measure','OpenSourceRail Baghdad plus plant','Historical proposal or requested comparator'],[
 ['Route km',f"{comp['osr_route_km']:.1f}",'148'],['Lines / stations',f"{comp['osr_lines']} / {comp['osr_stations']}",'7 / 64'],
 ['Capital USD equivalent bn',f"{p['total_capex_usd']/1e9:.3f}",'18.000 reported'],
 ['Capital USD equivalent m / route km',f"{p['total_capex_usd']/comp['osr_route_km']/1e6:.2f}",f"{18e9/148/1e6:.2f}"],
 ['USD capital funding bn',f"{p['usd_denominated_capital_usd']/1e9:.3f}",'18.000 requested all USD scenario'],
 ['Chinese USD debt bn',f"{p['usd_denominated_debt_principal_usd']/1e9:.3f}",'Final debt and government split unverified']])}

The July 2024 reported estimate is a historical 148 km, USD 18bn scope. An entirely USD foreign loan/government cash basis is the requested comparator, not a verified financing contract. Under that assumption Baghdad's USD capital requirement is {1-p['usd_denominated_capital_usd']/18e9:.1%} lower. Distinct scope, price date, tunnelling/structures, land, utilities, qualification and schedule prevent a like for like bid saving claim. Third party fares, actual financing and comparable population access are not established. Its Iraqi labour share cannot be assumed zero.

![USD capital comparison](../../finance/baghdad-financing-comparison.png)

## Future national development

Baghdad can establish manufacturing, maintenance, training, procurement and digital delivery capacity that later Iraqi cities can reuse. The existing catalogue contains {n['city_count']} cities representing {n['represented_population']:,} planning residents, {n['trainsets']:,} trainsets and {n['vehicle_modules']:,} vehicle modules across several standard families. These are proposed urban networks; national intercity rail and freight connections are a future feasibility topic, without routes, budgets, revenues or approvals in these totals.

{table(['Future catalogue city','Planning population','Fleet family','Route km','Trainsets','City CAPEX USD eq m'],national_rows)}

All city capital totals sum to USD {n['city_capital_usd']/1e9:.3f}bn. Adding one shared factory at USD {usd_m(n['shared_factory_usd'])}m and its EPC at USD {usd_m(n['shared_factory_epc_usd'])}m produces **USD {n['total_national_capital_usd']/1e9:.3f}bn equivalent** nationally. Baghdad already contains this same plant and EPC. The additional city capital beyond the Baghdad scope is therefore **USD {n['future_incremental_city_capital_after_baghdad_usd']/1e9:.3f}bn**, with no second plant added. Imported/local procurement in the generic national origin model is USD {n['imported_procurement_usd']/1e9:.3f}bn / USD {n['local_procurement_usd']/1e9:.3f}bn; this is procurement composition, not a national loan programme.

No national factory expansion or replacement, intercity connection, research/training institution, shared governance or additional capital acceleration is priced. Sizing by the largest city's module order is not proof of annual production capacity. The 18 city aggregate is not a five year delivery commitment. Future orders require a throughput/renewal study, scheduled allocation and separate appropriations; no national revenue or profit services Baghdad debt in this proposal.

### National industrial and institutional programme

Create common interface standards and supplier quality processes; qualify body, interior and infrastructure suppliers in Iraq; develop local module assembly, battery service, tools, spares and repair capability. A shared apprenticeship and technician programme should cover fabrication, concrete/precast, rail installation, power electronics, charging, software, accessibility and accountable inspection. Set competency outcomes and measured hours before assigning job numbers or training budgets.

Establish a national asset and evidence framework with separate city ownership, budgets, installed configuration and operating approval. Shared procurement and maintenance standards may reduce duplicated development, but each city still needs its own survey, demand, fiscal powers, financial close and safety acceptance. National development should coordinate with existing railways, freight access and universities where feasible; institutional appointments and agreements remain proposed.

### Conditional national sequence

{table(['Stage','Proposed work','Decision before investment'],[
 ['Baghdad foundation','Sponsor, surveyed first line, plant and six car qualification','Accepted scope, executable finance and physical evidence'],
 ['Demonstration and repeatability','Prove operating and industrial outcomes; maintain Mosul and Samawah as planning examples','Evidence of safe service, actual cost, production and affordable demand'],
 ['Next city feasibility','Evaluate regional demand, access, land, energy and local implementation capacity','City specific business case and legal/financial approval'],
 ['Broader urban rollout','Allocate shared factory output by accepted opening dates; qualify family differences','Priced capacity expansion, renewal and approved city finance'],
 ['Intercity and national services','Study railway interfaces, freight/logistics, training and shared standards','New scope, environmental approvals and independently funded appraisal']])}

Mosul and Samawah are useful reference packages; their inclusion here is not a selected construction order. Basra, Erbil, Sulaymaniyah and the other cities require transparent prioritisation from actual need and readiness. Future national borrowing shares and USD/IQD exposure must be recalculated from each qualified import basket. Baghdad's 25% contribution and 50:50 import split are not silently imposed on future city budgets.

## Ownership and decisions requested

The proposed public sponsor should establish the legal project vehicle and accountable budget authority. The city/operator should own demand, fares, service and operating competence. Manufacturing management should own supplier interfaces, tooling, work hours and first article evidence. Independent survey, civil, energy and safety assessors should control their acceptance evidence. Lenders and placement advisers should validate rights, currency, timing, fees and investor capacity. These are proposed functions, not appointments.

Commission a phased Baghdad feasibility package that closes the route, station, depot and energy scope, independently verifies demand and affordable fares, prices capital and lifecycle obligations, and obtains term sheets for the USD import and IQD domestic funding. Review the long production schedule and fund any acceleration explicitly. Present the accepted first phase to the sponsor and competent authorities before construction. Maintain the national chapter as a separately approved development framework.

## Current Baghdad deployment gates

{table(['Gate','Status','Responsible function','Closure action'],[[g['id'],g['status'],g['owner_role'],g['closure_action']] for g in deployment['gates']])}

{deployment['closed_gate_count']} checks are closed and {deployment['open_gate_count']} deployment gates remain open. Manufacturing, system certification and donor/lender decisions have additional distinct gates. The Baghdad package is complete as a planning example and has operational release false. Synthetic simulation, generated registers and documentary completeness are not physical acceptance.

## Detailed schedules and source appendices

The [detailed engineering plan](../DETAILED-ENGINEERING.md) and [component register](../engineering/detail/README.md) expand Baghdad's six-car mechanical interfaces, civil works, Iraqi slab manufacture, missing parts, onboard power/wiring, software host allocation and ERP handover. The register carries 69 reference part rows and all 60 Rust software allocations, with unknown prices and supplier identities left open. It corrects the ST6 seat layout and electronics interface errors; it does not release shop drawings or add unpriced components to the accepted finance totals. Local ERP recovery and planning-contract checks are recorded separately from production readiness.

The following proposal annex prints every station, interchange, fleet role, energy site and the complete cost priority six month draw/repayment schedule. Civil segment chainages and junction details are in the attached registers and design. Full monthly and alternative case ledgers remain in the supporting archive and repository. Technical annexes reproduce the city survey, ground, alignment, depot, stabling, delivery, deployment, finance and acceptance reports, followed by the current shared architecture and engineering references.

[Source inventory](source-inventory.csv) and [publication manifest](manifest.json) identify exact inputs and outputs. [Supporting data archive](Baghdad-Proposal-Supporting-Data.zip) includes the controlled files and complete operations payload. The editable proposal, PDF and appendix source list can be regenerated with the repository's proposal builder.

External instrument and historical sources are retained from the financing baseline. Source retrieval attempts on 3 October 2026 for China Exim, the GCF Iraq page and the NIC notice returned a timeout or access denial; this proposal does not claim a new source verification or a new lending commitment. Detailed financing reports retain the original source URLs and their stated evidence limits.
'''
    return intro


def write_csv(path, rows):
    with path.open('w',newline='') as handle:
        fields = list(dict.fromkeys(key for row in rows for key in row))
        writer = csv.DictWriter(handle,fieldnames=fields,lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)


def write_registers(d, s, early):
    directory=OUT/'registers'; directory.mkdir(exist_ok=True)
    station_rows=[{k: st.get(k,'') for k in ('id','line','s_m','lat','lon','archetype','platform_length_m','anchor_kind','anchor_name')} for st in d['stations']]
    write_csv(directory/'stations.csv',station_rows)
    write_csv(directory/'civil-segments.csv',d['civil_segments'])
    write_csv(directory/'fleets.csv',d['fleets'])
    write_csv(directory/'energy-sites.csv',s['sites'])
    write_csv(directory/'junctions.csv',d['junctions'])
    write_csv(directory/'interchanges.csv',[{**row,'lines':'; '.join(row['lines']),'platforms':'; '.join(row['platforms'])} for row in d['interchanges']])
    parts=['# Baghdad detailed schedules','', '## Station register','',
           'Coordinates and chainages are planning inputs. IDs are controlled; anchor names remain in the UTF-8 CSV rather than being adopted as public station names. Latitude/longitude are WGS84 degrees.','',
           table(['Station ID','Line','Chainage km','Latitude','Longitude','Platform m'],[[r['id'],r['line'],f"{r['s_m']/1000:.3f}",f"{r['lat']:.6f}",f"{r['lon']:.6f}",r['platform_length_m']] for r in station_rows]),'',
           '## Interchange register','',table(['Interchange','Lines','Latitude','Longitude'],[[r['id'],', '.join(r['lines']),f"{r['lat']:.6f}",f"{r['lon']:.6f}"] for r in d['interchanges']]),'',
           '## Fleet roles','',table(['Line','Peak','Rotation','Spare','Cold reserve','Total'],[[r['line'],r['peak_count'],r['service_rotation_count'],r['spare_count'],r['cold_reserve_count'],r['trainset_count']] for r in d['fleets']]),'',
           '## Energy site register','',table(['Site station','Tier','PV kW','Storage kWh','Grid import kW','Charger kW'],[[r['station'],r['tier'],r['pv_nameplate_kw'],r['storage_capacity_kwh'],r['grid_import_kw'],r['charger_max_kw']] for r in s['sites']]),'',
           '## Six month capital and supplemental draw requirements','',
           'Cost priority with identical three month operating buffers. Settlement is monthly; six month rows are envelopes, not advance placements. Unrounded CSV values reconcile; displayed amounts are rounded. Tranches continue through the entire model horizon.','',
           table(['Months','Gov USD m','Gov IQD bn','China USD m','Ordinary bond IQD bn','Green IQD bn','Bank IQD bn','Gap IQD bn'],
                 [[f"{r['start_month']} to {r['end_month']}",f"{r['government_usd_cash']/1e6:.2f}",f"{r['government_iqd_cash']/1e9:.2f}",f"{r['chinese_export_credit_draw_native']/1e6:.2f}",f"{r['domestic_bonds_draw_native']/1e9:.2f}",f"{r['green_bonds_draw_native']/1e9:.2f}",f"{r['bank_credit_draw_native']/1e9:.2f}",f"{r['liquidity_draw_iqd']/1e9:.2f}"] for r in early['semiannual']]),'',
           '## Six month early repayments and closing balances','',
           'Early principal is additional to the scheduled principal separately retained in the full ledger. Outstanding debt uses the final month of each period. USD equivalent aggregates convert Chinese native debt at the historical IQD 1,300 anchor. Premiums and operating buffers are distinct from principal.','',
           table(['Months','Core early principal USD eq m','Premium USD eq m','Gap principal IQD bn','All debt closing IQD tn eq','Cash closing IQD tn','OPEX buffer IQD bn'],
                 [[f"{r['start_month']} to {r['end_month']}",f"{r['early_core_principal_usd_equivalent']/1e6:.2f}",f"{r['early_premiums_usd_equivalent']/1e6:.2f}",f"{r['liquidity_repayment_iqd']/1e9:.2f}",f"{(r['chinese_export_credit_closing_balance_native']*1300+sum(r[n+'_closing_balance_native'] for n in ('bank_credit','domestic_bonds','green_bonds'))+r['closing_liquidity_debt_iqd'])/1e12:.3f}",f"{r['closing_project_cash_iqd']/1e12:.3f}",f"{r['closing_operating_buffer_iqd']/1e9:.3f}"] for r in early['semiannual']]),'',
           '[Complete civil chainages](registers/civil-segments.csv) · [station names and attributes](registers/stations.csv) · [junction records](registers/junctions.csv) · [complete repayment ledger](../../finance/baghdad-early-cost_priority-six-month-tranches.csv)','']
    (OUT/'DETAILED-SCHEDULES.md').write_text('\n'.join(parts))


class ProposalDoc(book.BookDocTemplate):
    def afterFlowable(self, flowable):
        super().afterFlowable(flowable)
        if getattr(flowable,'book_bookmark',None) is not None:
            self.notify('TOCEntry',(flowable.book_level,flowable.book_title,self.page,flowable.book_bookmark))


def build_pdf(sources, as_of):
    book.IMAGE_ERRORS.clear(); book._register_fonts(); styles=book._styles()
    width,height=A4; content_width=width-2.9*cm-12; content_height=height-3.1*cm-12
    styles['title'].alignment=0; styles['title'].textColor=colors.HexColor('#102936')
    story=[Spacer(1,3*cm),Paragraph('Baghdad Proposal',styles['title']),
           Paragraph('Urban railway and Iraqi manufacturing<br/>Future national development',styles['subtitle']),
           Spacer(1,.8*cm),Paragraph(f'OpenSourceRail · Planning baseline {as_of}',styles['subtitle']),
           Paragraph('Complete proposal, detailed schedules and technical evidence annexes',styles['subtitle']),
           Paragraph('Prepared for the prospective Iraqi sponsor, Baghdad authorities, operating organisation and financing partners.',styles['body']),
           Paragraph('Baghdad finance only. National expansion is a separate future development programme. Construction and operating approval remain pending.',styles['body']),Spacer(1,.5*cm)]
    story.extend(book._image_flowables({'attrs':{'url':'../baghdad-network-map.png'},'children':[{'type':'text','raw':'Baghdad planning network'}]},OUT/'BAGHDAD-PROPOSAL.md',styles,max_width=content_width,max_height=9.5*cm,max_px=1600,quality=85))
    story.extend([PageBreak(),Paragraph('Contents',styles['h1'])])
    toc=TableOfContents(); toc.levelStyles=[ParagraphStyle('TOC',fontName=styles['body'].fontName,fontSize=9,leading=13,leftIndent=0,firstLineIndent=0,spaceBefore=4)]
    story += [toc,PageBreak()]
    for index,path in enumerate(sources):
        if index: story.append(PageBreak())
        title=book._markdown_title(path)
        story.append(book._outline_heading(title,styles['h1'],f'chapter-{index}',0))
        relative=path.relative_to(ROOT).as_posix()
        source_url=book.REPOSITORY_BLOB_URL+'/'+quote(relative,safe='/')
        story.append(Paragraph('Source: <link href="'+html.escape(source_url,quote=True)+'" color="#2563eb">'+html.escape(relative)+'</link>',styles['source']))
        story.extend(book._render_markdown(path,styles,content_width,content_height,1600,85,True))
    if book.IMAGE_ERRORS: raise ValueError('Missing proposal images: '+str(book.IMAGE_ERRORS))
    def footer(canv,doc):
        canv.saveState();canv.setFont(styles['small'].fontName,7)
        canv.setFillColor(colors.HexColor('#52616A'));canv.drawString(1.45*cm,.75*cm,'OpenSourceRail Baghdad Proposal · '+as_of+' · planning only')
        canv.drawRightString(width-1.45*cm,.75*cm,str(doc.page));canv.restoreState()
    doc=ProposalDoc(str(OUT/'Baghdad-Proposal.pdf'),pagesize=A4,leftMargin=1.45*cm,rightMargin=1.45*cm,topMargin=1.55*cm,bottomMargin=1.55*cm,
                    title='Baghdad Proposal',author='OpenSourceRail',invariant=1)
    doc.multiBuild(story,onFirstPage=footer,onLaterPages=footer)


def source_inputs():
    tracked=subprocess.check_output(['git','ls-files',str(CITY.relative_to(ROOT)),str((COUNTRY/'finance').relative_to(ROOT))],cwd=ROOT,text=True).splitlines()
    paths={ROOT/p for p in tracked if not p.startswith(OUT.relative_to(ROOT).as_posix()+'/')}
    paths.update(COUNTRY.glob('*/design.toml')); paths.update(p.parent/(tomllib.loads(p.read_text())['city']['slug']+'.toml') for p in COUNTRY.glob('*/design.toml'))
    paths.update(COUNTRY.glob('*/README.md'))
    paths.update(ROOT/p for p in SHARED)
    paths.update([COUNTRY/'NATIONAL-BRIEF.md',COUNTRY/'IRAQ-FUNDING-PROGRAMME.md',ROOT/'tools/automation/build-baghdad-proposal.py',
                  ROOT/'tools/automation/build-doc-book.py',ROOT/'tools/automation/generate-national-briefs.py',ROOT/'tools/automation/baghdad_funding_analysis.py',
                  ROOT/'tools/automation/generate-iraq-funding-programme.py',ROOT/'design/city-generation/src/osr_scenario/capital.py',
                  ROOT/'design/city-generation/src/osr_scenario/network_readme.py',ROOT/'lib/templates/capex-costs.toml',
                  ROOT/'lib/templates/rolling-stock.toml',ROOT/'lib/templates/iraq-funding.toml',ROOT/'lib/templates/baghdad-finance-options.toml'])
    paths.update(ROOT/relative for relative in read_json(COUNTRY/'finance/baghdad-programme.json')['sources_sha256'])
    paths.update((ROOT/'lib/templates').glob('*.toml'))
    paths.update((ROOT/'design/city-generation/src/osr_scenario').glob('*.py'))
    paths.add(ROOT/'design/city-generation/pyproject.toml')
    # Public hardware/ERP design inputs; never private site data.
    detail=read_json(CITY/'engineering/detail/register.json')
    paths.update(ROOT/relative for relative in detail['sources_sha256'])
    paths.update(CITY.glob('DETAILED-ENGINEERING.md'))
    paths.update(p for p in (CITY/'engineering/detail').glob('*') if p.is_file())
    # Exact full task payload is deliberately excluded from Git outside this archive.
    ops=read_json(CITY/'operations/baghdad-operations-manifest.json');paths.add(CITY/'operations'/ops['file'])
    # Retained solver/geospatial outputs complete the evidence where materialised.
    for subpath in ('engineering/gis','engineering/sumo','engineering/energy'):
        paths.update(path for path in (CITY/subpath).glob('*') if path.is_file() and path.suffix in ('.gpkg','.xml','.json'))
    return sorted(paths)


def verify():
    manifest=read_json(OUT/'manifest.json')
    for group in ('inputs','outputs'):
        for relative,value in manifest[group].items():
            if receipt(ROOT/relative) != value: raise ValueError('Proposal '+group+' changed: '+relative)
    with zipfile.ZipFile(OUT/'Baghdad-Proposal-Supporting-Data.zip') as archive:
        if archive.testzip() is not None: raise ValueError('Corrupt proposal archive')
        if set(archive.namelist()) != set(manifest['archive_members']): raise ValueError('Archive inventory mismatch')
        members=read_json(OUT/'archive-manifest.json')['members']
        for relative,value in members.items():
            raw=archive.read(relative)
            if len(raw)!=value['bytes'] or hashlib.sha256(raw).hexdigest()!=value['sha256']:
                raise ValueError('Archive member checksum mismatch: '+relative)
    print('Baghdad proposal: source/output hashes and archive CRCs pass')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.check: verify();return 0
    OUT.mkdir(parents=True,exist_ok=True)
    d=tomllib.loads((CITY/'design.toml').read_text());s=tomllib.loads((CITY/'baghdad.toml').read_text())
    p=read_json(COUNTRY/'finance/baghdad-programme.json');f=read_json(CITY/'engineering/finance/summary.json')
    check_baseline(p,read_json(CITY/'package-manifest.json'))
    n=national_context(p);ops=read_json(CITY/'operations/baghdad-operations-manifest.json')['totals']
    deployment=read_json(CITY/'engineering/deployment/summary.json')
    (OUT/'BAGHDAD-PROPOSAL.md').write_text(build_narrative(d,s,p,f,n,ops,deployment))
    (OUT/'national-context.json').write_text(json.dumps(n,indent=2,sort_keys=True)+'\n')
    early=read_json(COUNTRY/'finance/baghdad-early-repayment.json')['cases']['cost_priority']
    write_registers(d,s,early)
    city_docs=sorted(path for path in CITY.rglob('*.md') if OUT not in path.parents)
    sources=[OUT/'BAGHDAD-PROPOSAL.md',OUT/'DETAILED-SCHEDULES.md',*city_docs,COUNTRY/'IRAQ-FUNDING-PROGRAMME.md',COUNTRY/'NATIONAL-BRIEF.md',*[ROOT/p for p in SHARED]]
    (OUT/'appendix-sources.json').write_text(json.dumps([p.relative_to(ROOT).as_posix() for p in sources],indent=2)+'\n')
    as_of=tomllib.loads((ROOT/'lib/templates/iraq-funding.toml').read_text())['model']['as_of']
    build_pdf(sources,as_of)
    inputs=source_inputs()
    inventory=[{'path':path.relative_to(ROOT).as_posix(),**receipt(path)} for path in inputs]
    write_csv(OUT/'source-inventory.csv',inventory)
    readme='''# Baghdad proposal publication

The complete proposal integrates Baghdad network, trains, civil and energy systems, Iraqi manufacturing, operations, delivery, financing and early repayment. Future national development has its own chapter and reconciled catalogue budget; no additional city is included in Baghdad finance.

- [Complete proposal PDF](Baghdad-Proposal.pdf)
- [Editable proposal](BAGHDAD-PROPOSAL.md)
- [Detailed schedules](DETAILED-SCHEDULES.md)
- [Supporting data archive](Baghdad-Proposal-Supporting-Data.zip)
- [Source inventory](source-inventory.csv)
- [National context and capital reconciliation](national-context.json)
- [Appendix source list](appendix-sources.json)
- [Publication manifest](manifest.json)
- [Archive member checksums](archive-manifest.json)

The PDF includes every current Baghdad Markdown report and selected shared standards. The archive preserves repository paths for all controlled Baghdad files, full operations tasks, every Baghdad financing case, national city design/scenario inputs and cited shared documents. References to other repository material remain links to the wider repository; the archive is an evidence publication rather than a standalone build environment. The archive member manifest checks all packaged files; the publication manifest is delivered alongside the archive and additionally checks the archive itself. No private credentials, operational databases or user identities are collected.

The urban railway is a planning proposal, with physical and operating gates open. The national chapter is a future option, without national loan commitments or revenue added to Baghdad. The shared plant and its EPC are counted once. Source values and all monthly/six-month calculations retain their evidence limits.

Regenerate with `.venv/bin/python tools/automation/build-baghdad-proposal.py`; validate with the same command plus `--check`. If the complete Baghdad operations payload is missing, first materialise it with `./osr city baghdad`. Solver/geospatial files retained in the workspace are included and identified in the inventory.
'''
    (OUT/'README.md').write_text(readme)
    generated=[path for path in OUT.rglob('*') if path.is_file() and path.name not in ('Baghdad-Proposal-Supporting-Data.zip','manifest.json','archive-manifest.json')]
    archive_members={path.relative_to(ROOT).as_posix():path for path in inputs+generated}
    archive_receipts={relative:receipt(path) for relative,path in sorted(archive_members.items())}
    (OUT/'archive-manifest.json').write_text(json.dumps({'schema_version':'1.0','members':archive_receipts,'self_hash_excluded':True},indent=2,sort_keys=True)+'\n')
    archive_members[(OUT/'archive-manifest.json').relative_to(ROOT).as_posix()]=OUT/'archive-manifest.json'
    if OUT/'archive-manifest.json' not in generated: generated.append(OUT/'archive-manifest.json')
    archive_path=OUT/'Baghdad-Proposal-Supporting-Data.zip'
    with zipfile.ZipFile(archive_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for relative,path in sorted(archive_members.items()):
            entry=zipfile.ZipInfo(relative,date_time=tuple(int(v) for v in as_of.split('-'))+(0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED;entry.external_attr=0o100644<<16
            archive.writestr(entry,path.read_bytes())
    outputs=generated+[archive_path]
    for path in outputs:
        if path.stat().st_size>MAX_BYTES: raise ValueError('Proposal artifact exceeds repository 50 MiB limit: '+str(path))
    manifest={'schema_version':'1.0','title':'Baghdad Proposal','as_of':as_of,'document_status':'planning-proposal-not-construction-or-operating-release',
              'baghdad_financing_scope':['Baghdad'],'national_development_status':'future-separate-not-funded','factory_count':1,
              'baseline_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'inputs':{path.relative_to(ROOT).as_posix():receipt(path) for path in inputs},
              'outputs':{path.relative_to(ROOT).as_posix():receipt(path) for path in outputs},
              'archive_members':sorted(archive_members),'appendix_document_count':len(sources),
              'facts':{'baghdad_total_capex_usd':p['total_capex_usd'],'baghdad_route_km':p['comparison']['osr_route_km'],
                       'baghdad_station_count':len(d['stations']),'baghdad_government_share':p['government_share_of_total_capital'],
                       'national_total_capital_usd':n['total_national_capital_usd'],'national_incremental_after_baghdad_usd':n['future_incremental_city_capital_after_baghdad_usd']}}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    verify(); print(f'Published proposal with {len(sources)} document chapters and {len(inputs)} source files')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
