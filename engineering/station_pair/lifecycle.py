"""Disjoint fourteen-scope pilot accounts, with explicit unknown energy.

This module extends an immutable station-pair cost record. It neither transfers
pilot performance to a city nor makes an engineering or procurement selection.
Component allocations and lives are bounded outline hypotheses, not installed
equipment inventories or supplier declarations.
"""
from copy import deepcopy
import json
from math import fsum, isclose, isfinite
from pathlib import Path

from engineering.design_search.model_cost import SCOPES, replacement_event_times
from engineering.development_baseline.system_cost import component_renewal_schedule
from engineering.station_rail.common import digest, identity
from . import ROOT, FLAGS

CASES = ('low', 'base', 'high')
PRODUCER = 'engineering/station_pair/lifecycle.py'
POLICY = 'engineering/station_pair/lifecycle-policy.json'
DEPENDENCIES = ('engineering/design_search/model_cost.py',
                'engineering/development_baseline/system_cost.py')
OWNER_SCOPES = {
    'civil-beam-factory': 'guideway',
    'shared-pier-foundation-bearings': 'construction',
    'beam-transport-and-erection': 'construction',
    'running-rails': 'guideway',
    'running-rail-fastenings': 'guideway',
    'station-civil-accessibility': 'construction',
    'station-common-grid-feed': 'stations-power',
    'station-hotel-battery-chargers': 'stations-power',
    'signalling-protection-turnbacks': 'stations-power',
    'depot-tools-utilities': 'land-utilities-depot',
    'wayside-propulsion': 'stations-power',
}


def _number(x, *, positive=False):
    return type(x) in (int, float) and isfinite(x) and (x > 0 if positive else x >= 0)


def _cases(value, name, *, nullable=False, positive=False):
    if not isinstance(value, dict) or set(value) != set(CASES):
        raise ValueError('Explicit three-case mapping required: '+name)
    if any(not (nullable and x is None) and not _number(x, positive=positive)
           for x in value.values()):
        raise ValueError('Finite nonnegative scenario amounts required: '+name)
    return value


def _sealed(value, key='evaluation_id'):
    if not isinstance(value, dict) or value.get(key) != identity({k:v for k,v in value.items() if k != key}):
        raise ValueError('Sealed record identity differs: '+key)


def _hex(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def sources(root=ROOT):
    root = Path(root)
    return {n:digest(root/n) for n in (PRODUCER, POLICY, *DEPENDENCIES)}


def policy(root=ROOT):
    p = json.loads((Path(root)/POLICY).read_bytes())
    if (p.get('schema') != 'osr-station-pair-lifecycle-policy/1'
        or p.get('currency') != 'USD' or p.get('supplier_confirmed') is not False
        or p.get('site_surveyed') is not False or p.get('automatic_bulk_discount') is not False):
        raise ValueError('Explicit provisional USD lifecycle policy required')
    def check_tree(node, name):
        if isinstance(node, dict):
            for key,value in node.items(): check_tree(value, name+'/'+key)
        elif isinstance(node, list):
            if len(node) != 3 or any(not _number(x, positive=True) for x in node):
                raise ValueError('Positive finite three-case policy required: '+name)
            if 'fraction' in name and any(x > 1 for x in node):
                raise ValueError('Policy fractions cannot exceed one: '+name)
    check_tree(p, '')
    for i in range(3):
        if fsum(v['fraction_of_delivered_fleet'][i] for v in p['vehicle_components'].values()) > 1:
            raise ValueError('Vehicle component partitions exceed the parent fleet')
    return p


def _route_km(cost):
    # The exact existing pilot record carries route-normalized capital. Require
    # all methods and scenarios to resolve to one positive physical length.
    values = []
    for method in cost['methods']:
        for case in CASES:
            cap = method['installed_capital_usd'][case]
            per_km = method['capital_per_route_km_usd'][case]
            if not _number(cap, positive=True) or not _number(per_km, positive=True):
                raise ValueError('Positive existing capital and route quantities required')
            values.append(cap/per_km)
    if not values or any(not isclose(x, values[0], rel_tol=1e-12) for x in values):
        raise ValueError('Mixed physical route lengths across existing cost methods')
    return values[0]


def _inputs(cost, brief):
    _sealed(cost)
    if cost.get('schema') != 'osr-station-pair-cost/1' or not _hex(cost.get('candidate_id')):
        raise ValueError('Exact sealed station-pair cost/1 required')
    if any(cost.get(k) is not False for k in FLAGS):
        raise ValueError('Research lifecycle accounting cannot grant release')
    for name in ('operation_hours_day', 'operation_days_year', 'design_life_years',
                 'hotel_W_per_car_hypothesis', 'hotel_charge_efficiency_hypothesis'):
        if not _number(brief.get(name), positive=True): raise ValueError('Positive explicit brief: '+name)
    if (brief['operation_hours_day'] > 24 or brief['operation_days_year'] > 366
        or brief['design_life_years'] > 200 or brief['hotel_charge_efficiency_hypothesis'] > 1
        or not _number(brief.get('discount_rate'))):
        raise ValueError('Bounded calendar, horizon, charge efficiency and discount rate required')
    _cases(brief['tariff_usd_kwh'], 'tariffs', positive=True)
    service = cost['service']
    for key in ('active_trainsets', 'spare_trainsets', 'total_trainsets'):
        if type(service.get(key)) is not int or service[key] <= 0:
            raise ValueError('Positive explicit active/reserve fleet required')
    if service['active_trainsets']+service['spare_trainsets'] != service['total_trainsets']:
        raise ValueError('Active and reserve fleet do not reconcile')
    if not _number(service.get('headway_s'), positive=True): raise ValueError('Positive explicit headway required')
    names = [r['owner'] for r in cost['accounts']]
    if len(names) != len(set(names)) or set(names) != set(OWNER_SCOPES)|{'rolling-stock-delivered'}:
        raise ValueError('Every existing owner must be uniquely assigned; unknown or duplicate account')
    for row in cost['accounts']:
        _cases(row['cost_usd'], row['owner'])
        if not _number(row['quantity'], positive=True): raise ValueError('Positive existing account quantity required')
    methods = [r['method'] for r in cost['methods']]
    if not methods or len(methods) != len(set(methods)): raise ValueError('Unique existing purchase/manufacture methods required')


def evaluate(cost, brief, *, extra_accounts=(), energy_context=None, root=ROOT):
    """Extend one sealed economics result without changing it.

    Extra capital rows: candidate_id, unique owner, canonical scope, positive
    quantity, unit, cost_usd={low,base,high}, basis and account_id. Optional
    renewal_class is station-mechanical (default), station-storage,
    station-electrical or site. A site row has no assumed replacement within
    the horizon; maintenance is still provisioned for equipment rows.

    Optional sealed energy_context uses schema
    osr-station-pair-lifecycle-energy/1, candidate_id,
    input_cost_evaluation_id, source_evaluation_id, service_fulfilled,
    annual_energy_usd, basis and evaluation_id. This replaces only the original
    pilot electricity scope. Spare conditioning/depot electricity is added
    separately. A failed/unknown service must retain unknown annual energy.
    """
    _inputs(cost, brief)
    root = Path(root); p = policy(root); pinned = sources(root)
    candidate = cost['candidate_id']; extras = deepcopy(list(extra_accounts))
    owners = {r['owner'] for r in cost['accounts']}
    for row in extras:
        _sealed(row, 'account_id')
        if row.get('candidate_id') != candidate: raise ValueError('Mixed extra-account candidate')
        if (not isinstance(row.get('owner'), str) or not row['owner'] or row['owner'] in owners
            or row.get('scope') not in SCOPES or row['scope'] in ('energy','operations','maintenance','renewals','reliability','disposal')
            or not _number(row.get('quantity'), positive=True)
            or not isinstance(row.get('unit'), str) or not row['unit']
            or not isinstance(row.get('basis'), str) or not row['basis']):
            raise ValueError('Unique explicit extra capital-account scope/quantity/basis required')
        owners.add(row['owner']); _cases(row['cost_usd'], row['owner'], positive=True)
        if row.get('renewal_class', 'station-mechanical') not in ('station-mechanical','station-storage','station-electrical','site'):
            raise ValueError('Explicit supported extra-account renewal class required')
    if energy_context is not None:
        _sealed(energy_context)
        if (energy_context.get('schema') != 'osr-station-pair-lifecycle-energy/1'
            or energy_context.get('candidate_id') != candidate
            or energy_context.get('input_cost_evaluation_id') != cost['evaluation_id']
            or not _hex(energy_context.get('source_evaluation_id'))
            or type(energy_context.get('service_fulfilled')) is not bool
            or not isinstance(energy_context.get('basis'), str) or not energy_context['basis']):
            raise ValueError('Exact candidate/cost-linked lifecycle energy context required')
        _cases(energy_context['annual_energy_usd'], 'energy override', nullable=True)
        if not energy_context['service_fulfilled'] and any(x is not None for x in energy_context['annual_energy_usd'].values()):
            raise ValueError('Unfulfilled service cannot annualize a successful energy cost')
    route_km = _route_km(cost); horizon = brief['design_life_years']; discount = brief['discount_rate']
    annuity = fsum((1+discount)**-y for y in range(1,int(horizon)+1))
    if type(horizon) is not int: raise ValueError('Integer accounting horizon required')
    hours = brief['operation_hours_day']*brief['operation_days_year']
    departures = 2*3600/cost['service']['headway_s']*hours
    train_km = departures*route_km
    spare = cost['service']['spare_trainsets']; total = cost['service']['total_trainsets']
    fraction = spare/total
    original = {r['owner']:r for r in cost['accounts']}
    fleet_amount = original['rolling-stock-delivered']['cost_usd']
    extra_direct = {c:fsum(r['cost_usd'][c] for r in extras) for c in CASES}
    results = []
    for method in cost['methods']:
        capital = []; life = []; renewals = []
        def add(target, key, scope, values, basis, *, quantity=None, **details):
            _cases(values, key, nullable=True)
            row = dict(key=key, scope=scope, costs_usd=dict(values), basis=basis,
                       quantity=quantity, candidate_id=candidate, **details)
            target.append(row)
            return row
        for owner,row in original.items():
            if owner == 'rolling-stock-delivered':
                add(capital, 'original/rolling-stock-active', 'rolling-stock',
                    {c:fleet_amount[c]*(1-fraction) for c in CASES},
                    'Active trainsets partitioned from the existing delivered fleet account; no duplicate train price.',
                    quantity=dict(trainsets=cost['service']['active_trainsets']))
                add(capital, 'original/rolling-stock-reserve', 'fleet',
                    {c:fleet_amount[c]*fraction for c in CASES},
                    'Reserve trainsets partitioned from the same delivered fleet account; no additional spare-vehicle charge.',
                    quantity=dict(trainsets=spare))
            else:
                add(capital, 'original/'+owner, OWNER_SCOPES[owner], row['cost_usd'], row['basis'],
                    quantity=dict(value=row['quantity'],unit=row['unit']))
        direct = {c:fsum(r['cost_usd'][c] for r in cost['accounts']) for c in CASES}
        for c in CASES:
            parts = method['capital_components'][c]
            if (not isclose(parts['direct_accounts'], direct[c], rel_tol=1e-12)
                or not isclose(fsum(parts.values()), method['installed_capital_usd'][c], rel_tol=1e-12)):
                raise ValueError('Original capital components do not reconcile exactly once')
        for key,scope in (('one_campaign_setup','factory-tooling'),('integration_verification','construction'),('contingency','construction')):
            add(capital, 'original/'+key, scope,
                {c:method['capital_components'][c][key] for c in CASES},
                'Original pilot '+key+' retained once; not a new price.',quantity=dict(campaigns=1))
        for row in extras:
            add(capital,'extra/'+row['owner'],row['scope'],row['cost_usd'],row['basis'],
                quantity=dict(value=row['quantity'],unit=row['unit']),account_id=row['account_id'])
        land = {c:route_km*1000*p['land_access_usd_route_m'][i] for i,c in enumerate(CASES)}
        utilities = {c:route_km*1000*p['utility_risk_usd_route_m'][i] for i,c in enumerate(CASES)}
        rescue = dict(zip(CASES,p['protected_rescue_equipment_usd']))
        add(capital,'provision/corridor-land-access','land-utilities-depot',land,
            'Additional corridor access/land reserve, excluding depot/tools/premises already in the original pilot; no surveyed land quantities or titles.',quantity=dict(route_km=route_km))
        add(capital,'provision/utility-diversions','land-utilities-depot',utilities,
            'Additional diversion/interface risk reserve, excluding original grid connection and depot internal utilities.',quantity=dict(route_km=route_km))
        add(capital,'provision/protected-rescue-equipment','recovery',rescue,
            'Dedicated recovery/towing/protection equipment reserve; excludes ordinary depot tools. Hardware, route access and rescue method remain unverified.',quantity=dict(pilot_systems=1))
        supplement_direct = {c:extra_direct[c]+land[c]+utilities[c]+rescue[c] for c in CASES}
        supplement_engineering = {}; supplement_contingency = {}
        for c in CASES:
            b = method['capital_components'][c]
            rate = b['integration_verification']/(b['direct_accounts']+b['one_campaign_setup'])
            risk = b['contingency']/(b['direct_accounts']+b['one_campaign_setup']+b['integration_verification'])
            supplement_engineering[c] = supplement_direct[c]*rate
            supplement_contingency[c] = (supplement_direct[c]+supplement_engineering[c])*risk
        add(capital,'provision/additional-integration','construction',supplement_engineering,
            'Original method integration percentage applied only to the newly added direct scope.')
        add(capital,'provision/additional-contingency','construction',supplement_contingency,
            'Original contingency percentage applied only to the new direct/integration scope.')
        cap = {c:fsum(r['costs_usd'][c] for r in capital) for c in CASES}
        annual = {}; missing_energy = []
        for i,c in enumerate(CASES):
            old = method['annual_operating'][c]
            for key in ('maintenance_usd','staff_usd'):
                if not _number(old[key]): raise ValueError('Nonnegative original annual account required')
            if old['energy_usd'] is not None and not _number(old['energy_usd']): raise ValueError('Valid original energy or unknown required')
            primary = old['energy_usd'] if energy_context is None else energy_context['annual_energy_usd'][c]
            reserve_kwh = spare*6*brief['hotel_W_per_car_hypothesis']/1000*p['reserve_auxiliary_fraction'][i]*hours/brief['hotel_charge_efficiency_hypothesis']
            depot_kwh = p['depot_auxiliary_kw'][i]*hours
            additional_energy = (reserve_kwh+depot_kwh)*brief['tariff_usd_kwh'][c]
            energy = None if primary is None else primary+additional_energy
            if energy is None: missing_energy.append(c)
            extra_maintenance = extra_direct[c]*p['additional_equipment_annual_maintenance_fraction'][i]
            annual[c] = dict(energy_usd=energy,primary_pilot_energy_usd=primary,
                known_reserve_depot_energy_usd=additional_energy,reserve_auxiliary_grid_kwh=reserve_kwh,
                depot_auxiliary_grid_kwh=depot_kwh,operations_usd=old['staff_usd'],
                maintenance_usd=old['maintenance_usd']+extra_maintenance,
                recovery_usd=p['rescue_standby_usd_year'][i],
                reliability_usd=train_km*p['nonrepair_disruption_usd_train_km'][i])
        for key,scope,basis in (
            ('energy_usd','energy','Pilot trip/grid electricity plus explicit spare conditioning and depot loads. Unknown journey electricity remains unknown; no invented regeneration credit.'),
            ('operations_usd','operations','Original pilot paid operations/maintenance staffing retained once. No additional unpriced staffing assumed.'),
            ('maintenance_usd','maintenance','Original routine maintenance retained; added equipment gets a declared routine materials/service reserve. Scheduled renewal excluded.'),
            ('recovery_usd','recovery','Protected rescue standby; excludes routine maintenance or purchase of rescue equipment.'),
            ('reliability_usd','reliability','Nonrepair disruption/replacement-service provision per scheduled train-km. Excludes repair labor/spares and does not establish availability.')):
            values = {c:None if annual[c][key] is None else annual[c][key]*annuity for c in CASES}
            add(life,'annual/'+scope,scope,values,basis,quantity=dict(annual_usd={c:annual[c][key] for c in CASES},annuity=annuity))
        def renewal_events(owner, values, lives, *, parents=None):
            for i,c in enumerate(CASES):
                if parents is None:
                    schedule = [dict(year=y,covered_by_parent_replacement=False) for y in replacement_event_times(horizon,lives[i])]
                else:
                    schedule = component_renewal_schedule(horizon,lives[i],parents[c])['events']
                for event in schedule:
                    covered = event.get('covered_by_parent_replacement',False)
                    amount = 0. if covered else values[c]
                    renewals.append(dict(owner=owner,case=c,year=event['year'],
                        cost_usd=amount,present_value_usd=amount/(1+discount)**event['year'],
                        covered_by_parent_replacement=covered,
                        component_age_origin_year=event.get('component_age_origin_year')))
        parents = {c:replacement_event_times(horizon,p['vehicle_life_years'][i]) for i,c in enumerate(CASES)}
        renewal_events('delivered-whole-fleet',fleet_amount,p['vehicle_life_years'])
        retool = {c:method['capital_components'][c]['one_campaign_setup']*p['vehicle_retool_fraction_of_original_setup'][i] for i,c in enumerate(CASES)}
        renewal_events('vehicle-campaign-retooling-excluding-premises',retool,p['vehicle_life_years'])
        for name,component in p['vehicle_components'].items():
            values = {c:fleet_amount[c]*component['fraction_of_delivered_fleet'][i] for i,c in enumerate(CASES)}
            renewal_events('vehicle/'+name,values,component['life_years'],parents=parents)
        asset_classes = {
            'wayside-propulsion':'station-mechanical','station-common-grid-feed':'station-electrical',
            'station-hotel-battery-chargers':'station-electrical','signalling-protection-turnbacks':'station-electrical',
            'running-rails':'rail','running-rail-fastenings':'rail-fastenings'}
        for owner,kind in asset_classes.items():
            renewal_events(owner,original[owner]['cost_usd'],p['asset_life_years'][kind])
        # Premises and land are retained; only the explicit equipment allocation
        # of the combined depot account is renewed.
        depot = {c:original['depot-tools-utilities']['cost_usd'][c]*p['depot_replaceable_equipment_fraction'][i] for i,c in enumerate(CASES)}
        renewal_events('depot-equipment-excluding-premises',depot,p['asset_life_years']['depot-equipment'])
        bearings = {c:original['shared-pier-foundation-bearings']['cost_usd'][c]*p['support_bearing_equipment_fraction'][i] for i,c in enumerate(CASES)}
        access = {c:original['station-civil-accessibility']['cost_usd'][c]*p['station_access_equipment_fraction'][i] for i,c in enumerate(CASES)}
        renewal_events('bearings-excluding-piers-foundations',bearings,p['asset_life_years']['station-mechanical'])
        renewal_events('station-access-equipment-excluding-civil',access,p['asset_life_years']['station-electrical'])
        renewal_events('protected-rescue-equipment',rescue,p['asset_life_years']['rescue-equipment'])
        for row in extras:
            kind = row.get('renewal_class','station-mechanical')
            if kind != 'site': renewal_events('extra/'+row['owner'],row['cost_usd'],p['asset_life_years'][kind])
        renewal = {c:fsum(r['present_value_usd'] for r in renewals if r['case']==c) for c in CASES}
        add(life,'scheduled/component-renewals','renewals',renewal,
            'Disjoint components renewed between full-parent replacements; parent replacement supplies new components and resets their ages. No renewal exactly at the accounting horizon.',quantity=dict(events=renewals))
        disposal = {c:cap[c]*p['disposal_fraction'][i]/(1+discount)**horizon for i,c in enumerate(CASES)}
        add(life,'final/removal-disposal','disposal',disposal,
            'Final removal, recycling/waste handling and site-restoration reserve at horizon. No speculative salvage credit.',quantity=dict(year=horizon))
        scopes = {s:{c:None if any(r['costs_usd'][c] is None for r in capital+life if r['scope']==s)
            else fsum(r['costs_usd'][c] for r in capital+life if r['scope']==s) for c in CASES} for s in SCOPES}
        known_scopes = {s:{c:fsum(r['costs_usd'][c] for r in capital+life if r['scope']==s and r['costs_usd'][c] is not None)
            + (annual[c]['known_reserve_depot_energy_usd']*annuity if s=='energy' and c in missing_energy else 0.)
            for c in CASES} for s in SCOPES}
        known = {c:fsum(r['costs_usd'][c] for r in capital+life if r['costs_usd'][c] is not None)
            + (annual[c]['known_reserve_depot_energy_usd']*annuity if c in missing_energy else 0.) for c in CASES}
        complete = {c:None if c in missing_energy else known[c] for c in CASES}
        if any(len({r['key'] for r in rows}) != len(rows) for rows in (capital,life)):
            raise ValueError('Duplicate lifecycle ownership key')
        residuals = {c:cap[c] - method['installed_capital_usd'][c]
            - supplement_direct[c]-supplement_engineering[c]-supplement_contingency[c] for c in CASES}
        if any(abs(x)>1e-7*max(1,cap[c]) for c,x in residuals.items()): raise ValueError('Capital conservation failed')
        results.append(dict(method=method['method'],capital_lines=capital,lifecycle_lines=life,
            scope_totals_usd=scopes,known_scope_subtotals_usd=known_scopes,installed_capital_usd=cap,
            capital_per_route_km_usd={c:cap[c]/route_km for c in CASES},
            original_installed_capital_usd=deepcopy(method['installed_capital_usd']),
            additional_capital_usd={c:cap[c]-method['installed_capital_usd'][c] for c in CASES},
            annual_operating=annual,whole_life_NPV_usd=complete,known_whole_life_subtotal_usd=known,
            incomplete_cases=missing_energy,renewal_events=renewals,capital_conservation_residual_usd=residuals,
            accounting_scope_complete=not missing_energy,site_specific_prices_verified=False))
    result = dict(schema='osr-station-pair-lifecycle/1',candidate_id=candidate,
        input_cost_evaluation_id=cost['evaluation_id'],body_candidate_id=cost['body_candidate_id'],
        body_bundle_id=cost['body_bundle_id'],mass_evaluation_id=cost['mass_evaluation_id'],
        journey_evaluation_id=cost['journey_evaluation_id'],brief_id=identity(brief),
        required_cost_scopes=list(SCOPES),methods=results,
        service=deepcopy(cost['service']),route_km=route_km,annual_departures=departures,annual_train_km=train_km,
        horizon_years=horizon,real_discount_rate=discount,
        energy_context=deepcopy(energy_context),extra_accounts=extras,
        price_maturity='Calculated outline with bounded allocations; no supplier or site verification',
        project_finance_layers=deepcopy(p['project_finance_layers']),
        exclusions=['Project financing, taxes, customs and exchange-rate policy are separate excluded project-finance layers.',
            'Physical actuator, storage, battery and brake duty, installed CAD and route-specific ground/utility evidence remain open.',
            'Loss-of-service and component-life allowances are not measured reliability or qualified lifetime predictions.'],
        policy=p,source_sha256=pinned,transactions_performed=False,procurement_ready=False,**FLAGS)
    result['input_cost_source_sha256'] = deepcopy(cost.get('source_sha256',{}))
    if sources(root) != pinned: raise ValueError('Lifecycle sources changed during calculation')
    result['evaluation_id'] = identity(result)
    return result
