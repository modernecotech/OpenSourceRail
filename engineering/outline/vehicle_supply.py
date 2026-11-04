"""Pricing-only vehicle make/buy hypotheses at the committed project volume.

Raw benchmarks do not qualify a grade or turn a bogie into mild-steel stock.
Purchased prices below are calculated production proxies, never supplier quotes.
Owned fixed plant is returned separately and excluded from vehicle unit prices.
"""
from copy import deepcopy
from math import fsum, isfinite
from pathlib import Path
import hashlib
import json
import tomllib

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity
from . import make_buy

PRODUCER = 'engineering/outline/vehicle_supply.py'
DATA = 'engineering/outline/data/china-supply-20261104.json'
FX_SPEC = 'campaigns/line30-affordable-benchmark.toml'
CASES = ('low', 'base', 'high')
# Per-car allocations across three long imported groups, not three whole-car
# shipping reserves or a claim about actual load count/container fit.
_LONG_IMPORT_INCREMENT_USD = {
    'located-stock/wheel-underframe/aluminium': (2000.,5000.,12000.),
    'located-stock/retained-comfort/body/generic': (1500.,5000.,18000.),
    'unlocated-account/retained-comfort/body': (1500.,5000.,18000.),
}
_LOADED = {n: digest(Path(ROOT)/n) for n in (PRODUCER, DATA, FX_SPEC,
    make_buy.PRODUCER, 'engineering/station_rail/common.py')}
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    installed_mass_complete=False, manufacturing_release=False, operating_release=False,
    procurement_approved=False, selected_reference_changed=False)


def _canonical(value):
    # The evidence dataset specifies ASCII JSON; do not silently change its identity convention.
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
        ensure_ascii=True, allow_nan=False)+'\n').encode()


def _dataset(root):
    value = json.loads((root/DATA).read_bytes())
    check = {k:v for k,v in value.items() if k != 'dataset_id'}
    if hashlib.sha256(_canonical(check)).hexdigest() != value.get('dataset_id'):
        raise ValueError('China evidence dataset identity differs')
    observations = {}
    for row in value['observations']:
        check = {k:v for k,v in row.items() if k != 'observation_sha256'}
        if hashlib.sha256(_canonical(check)).hexdigest() != row.get('observation_sha256'):
            raise ValueError('China observation identity differs')
        if row['id'] in observations or row.get('supplier_confirmed') is not False or row.get('engineering_qualified') is not False:
            raise ValueError('Unique provisional China observations required')
        observations[row['id']] = row
    return value, observations


def _triple(values):
    return dict(zip(CASES, values))


def _money(values):
    return {c:round(float(values[c]), 2) for c in CASES}


def _rates(data, observations):
    fx = data['fx_reference']['quote_per_base']
    def raw(oid):
        p = observations[oid]['advertised_price']
        return p['low']/1000/(fx if p['currency']=='CNY' else 1)
    al = raw('cn-nbs-20261021-31-aluminium-a00')
    steel = raw('cn-nbs-20261021-31-q235-plate')
    glass = raw('cn-haiding-ewr570-ewr800-woven-glass')
    resin = observations['cn-tianma-tm198-polyester-resin']['advertised_price']
    # No bulk haircut: current ingot floor + declared conversion, not a stale sub-metal offer.
    rates = {
        'aluminium': [al+x for x in (.45,.85,1.5)],
        'steel': [steel+x for x in (.30,.80,2.0)],
        'composite': [.60*glass+.35*(resin['low']+resin['high'])/2000+.05*x+y
            for x,y in zip((4.,8.,16.),(.35,.8,2.))],
        'misc': [3.,6.,12.],
    }
    landed = {}
    for family, prices in rates.items():
        freight = (.2,.4,.8) if family=='composite' else (.15,.30,.55)
        landed[family] = [(prices[i]+freight[i])*(1+(.005,.01,.02)[i])*(1+(0.,.05,.12)[i])
            +(.03,.08,.2)[i] for i in range(3)]
    return rates, landed


# Every fraction is a costing recipe only: it assigns no actual material or mass location.
_RECIPES = {
    'body-reserve': dict(mix={'aluminium':.35,'steel':.15,'composite':.25,'misc':.25},
        labour=(.08,.18,.45), machine=(.02,.05,.12), crew=4, equipment=(60000,120000,280000),
        tooling=(15000,40000,100000), floor=180., process='bounded mixed body/interior stock: cut/form/laminate, join, finish, inspect'),
    'body-generic': dict(mix={'aluminium':.45,'steel':.20,'composite':.25,'misc':.10},
        labour=(.06,.15,.4), machine=(.015,.04,.10), crew=4, equipment=(35000,70000,160000),
        tooling=(10000,25000,60000), floor=130., process='mixed framing/panel stock manufacture and dimensional QA'),
    'composite': dict(mix={'composite':1.},labour=(.12,.30,.75),machine=(.02,.06,.15),
        crew=3,equipment=(30000,70000,180000),tooling=(15000,40000,100000),floor=120.,
        process='mould preparation, lay-up/infusion/cure, trim/bond, inspection'),
    'aluminium': dict(mix={'aluminium':1.},labour=(.04,.10,.25),machine=(.015,.04,.10),
        crew=3,equipment=(25000,60000,150000),tooling=(8000,20000,60000),floor=100.,
        process='receive extrusion/plate, cut/machine, join/finish, dimensional QA'),
    'bogie-frame': dict(mix={'steel':1.},labour=(.06,.16,.40),machine=(.025,.07,.18),
        crew=4,equipment=(50000,120000,300000),tooling=(20000,50000,140000),floor=140.,
        process='frame stock cutting/welding/stress-control/machining and qualified inspection; excludes wheels/axles/bearings'),
}


def _comparison(key, mass, recipe, cars, raw, landed, wages, dataset_id, root):
    r = _RECIPES[recipe]
    long_load_increment = _LONG_IMPORT_INCREMENT_USD.get(key,(0.,0.,0.))
    price = [fsum(raw[f][i]*fraction for f,fraction in r['mix'].items()) for i in range(3)]
    local_price = [fsum(landed[f][i]*fraction for f,fraction in r['mix'].items()) for i in range(3)]
    labour = [mass*x for x in r['labour']]
    machine = [mass*x for x in r['machine']]
    # A comparable finished purchase includes foreign productive labour, process
    # machines, consumables, QA and one supplier overhead/profit allowance.
    # Explicit engineering assumptions; neither labour rates nor finished prices are quotes.
    purchase = []
    for i in range(3):
        material = mass/(.96,.90,.82)[i]*price[i]
        direct = material+labour[i]*(5.,8.,13.)[i]+machine[i]*(3.,6.,12.)[i]+mass*(.12,.30,.75)[i]
        purchase.append((direct+material*(.04,.08,.16)[i])*(1+(.12,.20,.35)[i]))
    spec = dict(item_id=key, unit='car-subassembly',currency='USD',quantity=cars,
        committed_volume=cars,project_years=3,
        purchase=dict(unit='car-subassembly',currency='USD',tiers=[dict(minimum_quantity=1,
            unit_price=_triple(purchase),already_bulk=True,source_class='calculated-Class-C-finished-proxy',
            source=dataset_id+'; explicit material/process/QA/overhead route, not a supplier offer')],
            landed=dict(freight_per_unit=_triple([mass*x+long_load_increment[i]
                    for i,x in enumerate((.18,.35,.65))]),
                insurance_fraction=_triple([.005,.01,.02]),duty_fraction=_triple([0.,.05,.12]),
                qa_per_unit=_triple([mass*x+mass*h*wages[i]
                    for i,(x,h) in enumerate(zip((.05,.15,.40),(.003,.008,.02)))]),
                local_delivery_per_unit=_triple([mass*x for x in (.02,.05,.12)]))),
        make=dict(unit='car-subassembly',currency='USD',
            material=dict(unit='kg',net_quantity_per_unit=mass,unit_price=_triple(local_price),
                yield_fraction=_triple([.96,.90,.82]),scrap_credit_per_unit=None),
            operations=dict(cell_hours_per_unit=_triple([x/r['crew'] for x in labour]),
                labour_hours_per_unit=_triple(labour),machine_hours_per_unit=_triple(machine),
                setup_cell_hours_per_batch=_triple([2.,4.,8.]),
                setup_labour_hours_per_batch=_triple([4.,8.,16.]),
                setup_machine_hours_per_batch=_triple([2.,4.,8.]),batch_quantity=6,
                labour_rate_per_hour=_triple(wages),machine_rate_per_hour=_triple([3.,6.,12.]),
                energy_kwh_per_unit=_triple([mass*x for x in (.15,.35,.8)]),
                setup_energy_kwh_per_batch=_triple([5.,10.,20.]),energy_rate_per_kwh=_triple([.08,.12,.20]),
                consumables_per_unit=_triple([mass*x for x in (.12,.30,.75)]),
                qa_per_unit=_triple([mass*x for x in (.20,.55,1.5)]),
                labour_rate_basis='productive-hour-loaded',
                machine_rate_basis='cash-operating-excluding-capital-recovery'),
            fixed=dict(equipment_per_cell=_triple(r['equipment']),tooling_per_cell=_triple(r['tooling']),
                building_shared=0.,building_priced_elsewhere=True,
                building_cost_reference='project-production-buildings-and-tooling; coordinator must include owned cell floor once',
                commissioning_shared=_triple([5000.,15000.,40000.])),
            capacity=dict(shifts_per_day=2,hours_per_shift=8.,days_per_year=250.,utilisation=.75),learning=None))
    spec['purchase']['weight_freight_usd_per_unit']=_triple([mass*x for x in (.18,.35,.65)])
    spec['purchase']['long_load_packing_volumetric_increment_usd_per_unit']=_triple(long_load_increment)
    spec['purchase']['freight_basis']='Weight freight plus declared Class C long-load/OOG/packing allocation for the same car subassembly; no shipping quote, container-fit or flat-pack claim. Other groups retain weight-only freight with actual route and dimensional transport unresolved.'
    spec['purchase']['local_receiving_fit_hours_per_unit']=_triple([mass*h for h in (.003,.008,.02)])
    spec['purchase']['incoming_qa_testing_usd_per_unit']=_triple([mass*x for x in (.05,.15,.40)])
    spec['purchase']['qa_charge_basis']='Incoming QA/testing allowance plus separately calculated local receiving/fit productive hours times paid-idle-adjusted local wage; both charged once in landed QA.'
    return make_buy.evaluate(spec,root=root)


def revalue(vehicle_cost, service, scenario, root=ROOT):
    """Reprice one immutable six-car account at the actual committed fleet size.

    china-bulk-buy purchases all repriced manufactured stock. project-make-buy
    chooses each subassembly's cheaper base total including its fixed plant,
    then retains that same route for low/high cases. Fixed plant is returned once.
    """
    if scenario not in ('china-bulk-buy','project-make-buy'):
        raise ValueError('Unknown vehicle supply scenario')
    root=Path(root)
    if any(digest(root/n)!=sha for n,sha in _LOADED.items()):
        raise ValueError('Loaded vehicle supply source epoch changed')
    if vehicle_cost.get('cost_estimate_id') != identity({k:v for k,v in vehicle_cost.items() if k!='cost_estimate_id'}):
        raise ValueError('Exact sealed source vehicle cost required')
    if vehicle_cost.get('currency') != 'IQD' or any(digest(root/n)!=sha for n,sha in vehicle_cost.get('source_sha256',{}).items()):
        raise ValueError('Current IQD source vehicle cost epoch required')
    if any(vehicle_cost.get(k) is not False for k in ('physical_accepted','engineering_accepted','installed_mass_complete','manufacturing_release','operating_release')):
        raise ValueError('Pricing hypotheses cannot admit or grant vehicle qualification')
    cars, fleet = service.get('totalcars'), service.get('total_trainsets')
    if type(cars) is not int or type(fleet) is not int or cars<=0 or fleet<=0 or cars!=6*fleet:
        raise ValueError('Committed positive integer six-car fleet required')
    if vehicle_cost['vehicle_account']['cars_per_train']!=6:
        raise ValueError('Only the source six-car formation is supported')
    keys=[r['line_key'] for r in vehicle_cost['lines']]
    if len(keys)!=len(set(keys)) or any(r['candidate_id']!=vehicle_cost['candidate_id'] for r in vehicle_cost['lines']):
        raise ValueError('Duplicate or mixed-candidate cost account')
    for row in vehicle_cost['lines']:
        if row['line_id']!=identity({k:v for k,v in row.items() if k!='line_id'}):
            raise ValueError('Source vehicle cost line identity differs')
    data, observations = _dataset(root)
    raw,landed=_rates(data,observations)
    project_spec=tomllib.loads((root/FX_SPEC).read_text())
    iqd_per_usd=project_spec['currency']['iqd_per_usd']
    capital_rates=project_spec['capital']
    utilisation=.75
    # Upstream includes burden and shift premiums per PAID hour only. Local
    # operations are productive hours, so recover paid idle time exactly once
    # in this rate. The generic kernel receives productive-hour-loaded rates
    # and therefore applies no second utilisation multiplier.
    paid_wages=[x/iqd_per_usd for x in vehicle_cost['assumption_values']['loaded_two_shift_skilled_wage_iqd_per_h']]
    wages=[x/utilisation for x in paid_wages]
    factors=vehicle_cost['mass_reserve_sensitivity']['case_factors']
    if factors!={'low':.8,'base':1.,'high':1.2}:
        raise ValueError('Preserve source reserve factors 0.8/1.0/1.2')
    value=deepcopy(vehicle_cost); decisions=[]; fixed={c:0. for c in CASES}; floor=[0.,0.,0.]
    for row in value['lines']:
        key=row['line_key']; original_id=row.pop('line_id'); q=row['quantity']
        recipe=None; frame_fraction=1.
        if key=='unlocated-account/retained-comfort/body':
            recipe='body-reserve'; mass=q['residual_account_mass_kg_per_car']
        elif key=='located-stock/passive-bogie-pair/steel':
            recipe='bogie-frame'; frame_fraction=.4; mass=q['net_mass_kg_per_car']*.4
        elif key.startswith('located-stock/'):
            family=key.rsplit('/',1)[-1];mass=q['net_mass_kg_per_car']
            if '/retained-comfort/body/' in key and family=='generic':recipe='body-generic'
            elif family in ('aluminium','composite'):recipe=family
        if recipe:
            evaluation=_comparison(key,mass,recipe,cars,raw,landed,wages,data['dataset_id'],root)
            # The generic kernel has no overhead field: add an explicit, source-bound
            # production-indirect allowance outside it, before selecting a route.
            # Its original result remains immutable and independently replayable.
            incremental_building_land={c:evaluation['cases'][c]['make']['cell_count']
                *_RECIPES[recipe]['floor']*capital_rates['factory_storage_area_factor']
                *(capital_rates['factory_building_iqd_per_m2'][i]+capital_rates['land_iqd_per_m2'][i])
                /iqd_per_usd for i,c in enumerate(CASES)}
            adjusted_make={c:evaluation['cases'][c]['make']['variable_total']*(1+(.10,.15,.25)[i])
                +evaluation['cases'][c]['make']['fixed_total']+incremental_building_land[c]
                for i,c in enumerate(CASES)}
            selected='buy' if scenario=='china-bulk-buy' or evaluation['cases']['base']['purchase']['total']<=adjusted_make['base'] else 'make'
            branch='make' if selected=='make' else 'purchase'
            costs={}; hours=[]; components={}
            for i,c in enumerate(CASES):
                result=evaluation['cases'][c][branch]
                if result is None:raise ValueError('Complete comparable make/buy inputs required')
                factor=factors[c] if key.startswith('unlocated-account/') else 1.
                direct_variable=result['variable_total'] if selected=='make' else result['total']
                overhead=direct_variable*(.10,.15,.25)[i] if selected=='make' else 0.
                variable=direct_variable+overhead
                per_car=variable/cars
                # Explicit purchased precision rolling components are never valued as raw mild steel.
                rolling=0.
                if recipe=='bogie-frame':
                    rolling=q['net_mass_kg_per_car']*(1-frame_fraction)*(4.,8.,18.)[i]
                    per_car+=rolling
                    rolling_fit_h=q['net_mass_kg_per_car']*(1-frame_fraction)*(.005,.02,.06)[i]
                    per_car+=rolling_fit_h*wages[i]
                else:
                    rolling_fit_h=0.
                costs[c]=per_car*6*iqd_per_usd*factor
                if selected=='make':
                    fixed[c]+=result['fixed_total'];floor[i]+=result['cell_count']*_RECIPES[recipe]['floor']
                    local_h=result['labour_hours']/cars
                    components.setdefault('make_direct_variable_excluding_fixed',{})[c]=direct_variable/cars*6*iqd_per_usd*factor
                    components.setdefault('make_production_indirects',{})[c]=overhead/cars*6*iqd_per_usd*factor
                else:
                    local_h=mass*(.003,.008,.02)[i]
                    components.setdefault('landed_finished_purchase',{})[c]=variable/cars*6*iqd_per_usd*factor
                if rolling:
                    components.setdefault('purchased_precision_running_components',{})[c]=rolling*6*iqd_per_usd
                    components.setdefault('precision_component_local_fit_labour',{})[c]=rolling_fit_h*wages[i]*6*iqd_per_usd
                hours.append((local_h+rolling_fit_h)*factor)
            row['cost_iqd']=_money(costs)
            if key.startswith('unlocated-account/'):
                q['upstream_process_hours_per_train']=q.get('process_hours_per_train')
                q['process_hours_per_train']=[h*6 for h in hours]
            else:
                q['upstream_process_hours_per_car']=q.get('process_hours_per_car')
                q['process_hours_per_car']=hours
                q['machine_hours_per_car']=[evaluation['cases'][c]['make']['machine_hours']/cars if selected=='make' else 0. for c in CASES]
            row['components_iqd']={name:_money(v) for name,v in components.items()}
            row['process_template']=_RECIPES[recipe]['process'] if selected=='make' else 'purchase calculated finished subassembly; receive and inspect locally'
            row['calculation_basis']='Pricing-only material/process recipe; same net and residual mass, no overlap credit. Owned fixed plant excluded from this unit cost and returned separately. Residual cost/hours retain source factors.'
            row['supply_scenario']=dict(scenario=scenario,selected_route=selected,comparison_id=evaluation['evaluation_id'],
                recipe=recipe,pricing_mixture_only=_RECIPES[recipe]['mix'],source_line_id=original_id,
                physical_material_definition_changed=False,bogie_frame_mass_fraction_pricing_proxy=frame_fraction if recipe=='bogie-frame' else None)
            decisions.append(dict(line_key=key,source_line_id=original_id,disposition='revalued',selected_route=selected,
                comparison=evaluation,make_total_including_production_indirects_usd=adjusted_make,
                make_route_incremental_building_land_usd=incremental_building_land,
                route_selection_basis='Base variable production, own equipment/tooling, production indirects and incremental owned-cell building plus land. Shared assembly/receiving areas remain in parent project comparison; per-group heuristic, not a global optimum.',
                production_indirect_fraction=_triple([.10,.15,.25]),
                production_indirect_basis='Declared own-factory administration/support allowance on variable production; excludes capital and shared building',
                purchased_remaining_bogie_mass_fraction=.6 if recipe=='bogie-frame' else None,
                purchased_rolling_component_usd_per_kg=_triple([4.,8.,18.]) if recipe=='bogie-frame' else None,
                precision_component_scope='Landed bounded precision rolling components before separately counted local fit labour; not a supplier quote or proven rail qualification' if recipe=='bogie-frame' else None))
        else:
            # Retain bounded equipment prices; only state local receiving/fit time.
            # Supplier manufacturing hours must not size the local project factory.
            if key=='six-car-final-vehicle-assembly':
                local_assembly={c:q['labour_hours_per_car'][i]*6*wages[i]*iqd_per_usd for i,c in enumerate(CASES)}
                equipment=row['components_iqd']['equipment']
                row['components_iqd']['labour']=_money(local_assembly)
                row['cost_iqd']=_money({c:local_assembly[c]+equipment[c] for c in CASES})
                row['calculation_basis']='Same declared final-assembly productive hours and equipment; upstream burden/shift-loaded paid-hour wage divided by0.75 utilisation exactly once.'
            elif key.startswith('unlocated-account/'):
                mass=q['residual_account_mass_kg_per_car']
                q['upstream_process_hours_per_train']=q.get('process_hours_per_train')
                q['process_hours_per_train']=[mass*x*6*factors[c] for x,c in zip((.005,.02,.06),CASES)]
            elif key.startswith('located-stock/'):
                mass=q['net_mass_kg_per_car']
                q['upstream_process_hours_per_car']=q.get('process_hours_per_car')
                q['process_hours_per_car']=[mass*x for x in (.005,.02,.06)]
                q['machine_hours_per_car']=[0.,0.,0.]
            decisions.append(dict(line_key=key,source_line_id=original_id,disposition='paid-idle-corrected-local-assembly' if key=='six-car-final-vehicle-assembly' else 'retained-bounded-cost',
                reason='Final local productive assembly labour corrected to paid-hour wage /0.75 once; equipment allowance unchanged.' if key=='six-car-final-vehicle-assembly' else 'No matched equivalent quotation/assembly scope; original all-in cost retained once. Purchased equipment local hours cover receiving/fit/check within that bounded allowance, not supplier factory work.'))
        row['upstream_line_id']=original_id
        row['source_ids']=sorted(set(row['source_ids']+[data['dataset_id'],vehicle_cost['cost_estimate_id']]))
        row['line_id']=identity(row)
    factory=[r for r in value['lines'] if r['line_key'].startswith(('located-stock/','unlocated-account/'))]
    value['final_vehicle_assembly_cost_iqd_per_train']=deepcopy(next(r for r in value['lines'] if r['line_key']=='six-car-final-vehicle-assembly')['cost_iqd'])
    value['factory_gate_cost_iqd_per_train']=_money({c:fsum(r['cost_iqd'][c] for r in factory) for c in CASES})
    value['total_vehicle_factory_delivery_assembly_iqd_per_train']=_money({c:fsum(r['cost_iqd'][c] for r in value['lines']) for c in CASES})
    value['unit_iqd_per_car']=_money({c:value['total_vehicle_factory_delivery_assembly_iqd_per_train'][c]/6 for c in CASES})
    value['separate_unamortized_factory_tooling_capital_iqd']=_money({c:fixed[c]*iqd_per_usd for c in CASES})
    value['upstream_cost_estimate_id']=value.pop('cost_estimate_id')
    value['source_sha256']={**value['source_sha256'],**_LOADED}
    value['supply_revaluation']=dict(scenario=scenario,dataset_id=data['dataset_id'],committed_cars=cars,
        committed_trainsets=fleet,owned_fixed_capital_excluded_from_unit_price=True,
        unchanged_physical_candidate=True,unchanged_mass_accounts=True,
        every_upstream_line_covered_once=len(decisions)==len(vehicle_cost['lines']))
    value['limitations']+=['China supply scenario is calculated Class C pricing, not a received quote or engineering acceptance.',
        'Mixed unresolved body and40% bogie-frame fractions are costing recipes only, not resolved geometry/materials or installed mass.',
        'Owned machines/tooling are charged only in returned fixed project capital; shared building floor must be charged once by coordinator.',
        'Purchased nonstructural equipment retains original allowance; conflicting HVAC advertisement is not used.',
        'Long imported underframe/body groups include explicit nonzero packing/OOG/volumetric allowances before route choice; these are engineering sensitivities, not shipping quotes or evidence of container fit/modularity.']
    value['cost_estimate_id']=identity(value)
    assumptions=dict(iqd_per_usd=iqd_per_usd,cny_per_usd=data['fx_reference']['quote_per_base'],
        raw_material_usd_per_kg={k:_triple(v) for k,v in raw.items()},
        landed_material_usd_per_kg={k:_triple(v) for k,v in landed.items()},
        labour_usd_per_productive_hour=_triple(wages),
        local_loaded_wage_usd_per_paid_hour=_triple(paid_wages),
        local_paid_hours_per_productive_hour=1/utilisation,
        local_wage_derivation='Upstream burden-and-shift-loaded paid-hour wage / 0.75 productive utilisation exactly once; kernel productive-hour-loaded basis applies no further paid-idle factor.',
        project_years=3,
        shifts_per_day=2,hours_per_shift=8,days_per_year=250,utilisation=.75,
        learning_discount=False,additional_bulk_discount=False,
        supplier_factory_labour_usd_per_h=_triple([5.,8.,13.]),
        supplier_factory_labour_rate_basis='Declared final productive-hour rate; local paid-idle factor is not applied to foreign supplier prices.',
        long_import_increment_usd_per_car={key:_triple(values) for key,values in _LONG_IMPORT_INCREMENT_USD.items()},
        long_import_allocation_basis='Three scoped per-car allocations sum to USD5000/15000/48000 low/base/high, not three duplicate whole-car shipping reserves or a verified load count. Existing physical17m structures and joints are unchanged.',
        other_import_freight_caveat='Nine-metre secondary, bogie-frame and panel groups retain weight-based freight hypotheses; route, packing, transport envelope and load consolidation remain unresolved.',
        purchase_local_receiving_fit_basis='Productive local receiving/fit hours at adjusted local wage, plus a distinct incoming QA/testing allowance, counted once inside landed purchase QA.',
        own_factory_production_indirect_fraction=_triple([.10,.15,.25]),
        material_import_freight_usd_per_kg=dict(composite=_triple([.2,.4,.8]),other=_triple([.15,.30,.55])),
        material_import_insurance_fraction=_triple([.005,.01,.02]),
        material_import_duty_fraction=_triple([0.,.05,.12]),
        material_import_receiving_qa_usd_per_kg=_triple([.03,.08,.2]),
        recipes=deepcopy(_RECIPES),residual_mass_factors_preserved=factors,
        complete_installed_mass=False,physical_materials_redefined=False,
        factory_building='Incremental cell building and land included in route selection; returned as cell floor for parent to charge once in project-production-buildings-and-tooling/land. Excluded from owned equipment capital and vehicle unit cost.',
        factory_storage_area_factor=capital_rates['factory_storage_area_factor'],
        factory_building_iqd_per_m2=_triple(capital_rates['factory_building_iqd_per_m2']),
        factory_land_iqd_per_m2=_triple(capital_rates['land_iqd_per_m2']),
        route_selection='Per-group base-cost heuristic including incremental cell premises; common assembly/receiving allocated by parent and global optimum not established.',
        local_hours_policy='Owned productive process hours, or bounded receiving/fit/check hours for purchased equipment. Vendor factory work is excluded from local capacity.',
        fixed_capital_policy='Selected base route retained for all cases; whole fixed machines/tooling/commissioning at committed volume, no speculative future orders or resale credit.')
    value['upstream_assumptions_id']=value['assumptions_id']
    value['assumption_values']['supply_revaluation']=deepcopy(assumptions)
    value['assumption_values']['upstream_rate_table_role']='Retained source context only; revalued line prices/processes use supply_revaluation and per-line comparison IDs. Unrevalued equipment retains its original allowance.'
    value['assumptions_id']=identity(value['assumption_values'])
    value.pop('cost_estimate_id')
    value['cost_estimate_id']=identity(value)
    if any(digest(root/n)!=sha for n,sha in _LOADED.items()):raise ValueError('Vehicle supply source changed during calculation')
    result=dict(vehicle_cost=value,decisions=decisions,owned_factory_capital_usd=_money(fixed),
        cell_floor_m2=floor,source_sha256=dict(_LOADED),assumptions=assumptions,**FLAGS)
    result['evaluation_id']=identity(result)
    return result
