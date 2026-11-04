"""Project-scale China purchasing and local make/buy, at unchanged service.

Reprices quantities, then recalculates dependent capital and lifecycle records.
It neither discounts an entire project nor changes mass, geometry or acceptance.
"""
from copy import deepcopy
from math import ceil, fsum, sqrt
from pathlib import Path
import json
import tomllib

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from engineering.design_search import line_benchmark as budget, model_cost
from . import vehicle_supply, civil_supply, make_buy

PRODUCER='engineering/outline/supply_economics.py'
POLICY='engineering/outline/supply-policy.toml'
DATA=vehicle_supply.DATA
SCENARIOS=('reference-rates','china-bulk-buy','project-make-buy')
CASES=budget.CASES
FLAGS={**budget.FLAGS,'procurement_approved':False}
_LOADED={name:digest(Path(ROOT)/name) for name in (PRODUCER,DATA,
    vehicle_supply.PRODUCER,civil_supply.PRODUCER,make_buy.PRODUCER)}


def seal(value,key='evaluation_id'):
    value[key]=identity(value);return value


def sources(root=ROOT):
    root=Path(root)
    if any(digest(root/n)!=sha for n,sha in _LOADED.items()):
        raise ValueError('Loaded supply sources changed; restart the calculation worker')
    return {**_LOADED,POLICY:digest(root/POLICY)}


def policy(root=ROOT):
    value=tomllib.loads((Path(root)/POLICY).read_text())
    if (value['schema']!='osr-project-supply-policy/1' or value['default_scenario'] not in SCENARIOS
            or value['physical_reference_changed'] is not False):
        raise ValueError('Versioned non-promoting supply policy required')
    return value


def _electrical(spec,service,mode,root,rates):
    """Calibrate rated module procurement, not a railway available-force map."""
    revised=deepcopy(spec);data,rows=vehicle_supply._dataset(Path(root))
    motor=rows['cn-marathon-sca-250kw-motor'];vfd=rows['cn-canworld-ip54-250-280kw-vfd']
    for row in (motor,vfd):
        if row.get('automatic_rate_use','').startswith(('hold','scope_hold')):
            raise ValueError('A held observation cannot set an equipment rate')
    preliminary,_=budget._drive(spec,service,rates,mode)
    capacity=preliminary[0]['quantity']['capacities']
    motor_rates=[];vfd_rates=[];detail=[]
    for i,c in enumerate(CASES):
        x=capacity[i]
        # Rated output is not a high-ambient or repeated-launch qualification.
        derate=(.95,.85,.70)[i]
        n_motor=ceil(x['budget_shaft_kw_per_site']/(250*derate))
        motor_landed=(motor['advertised_price']['low']+(250.,750.,2000.)[i])*(1+(.005,.01,.02)[i])*(1+(0.,.05,.12)[i])+(150.,400.,1200.)[i]
        motor_rates.append(n_motor*motor_landed/x['budget_shaft_kw_per_site'])
        apparent=sqrt(3)*380*465/1000
        n_vfd=ceil(x['budget_kva_per_site']/(apparent*derate))
        unit=(vfd['advertised_price']['low']+vfd['advertised_price']['high'])/2
        converter_landed=(unit+(100.,250.,700.)[i])*(1+(.005,.01,.02)[i])*(1+(0.,.05,.12)[i])
        integration=(1.3,1.8,3.)[i]*(1. if mode!='compact-launch-LIM' else (1.5,2.5,4.)[i])
        converter_cost=n_vfd*converter_landed*integration+(10000.,30000.,100000.)[i]
        vfd_rates.append(converter_cost/x['budget_kva_per_site'])
        detail.append(dict(case=c,sites=service['departure_sites'],motor_modules_per_site=n_motor,
            motor_module_kw=250.,VFD_modules_per_site=n_vfd,advertised_VFD_output_kva=apparent,
            planning_derate=derate,motor_landed_usd_per_module=motor_landed,
            VFD_landed_usd_per_module=converter_landed,converter_integration_multiplier=integration,
            no_additional_bulk_discount=True,available_force_or_duty_qualified=False))
    revised['rotary']['motor_usd_per_shaft_kw']=motor_rates
    revised['rotary']['converter_usd_per_kva']=vfd_rates
    # Existing mechanical integration, grid/protection and installation budgets
    # remain. A bare cheap motor does not replace its installed launch system.
    copper=rows['cn-nbs-20261021-31-copper-1']['advertised_price']['low']/data['fx_reference']['quote_per_base']/1000
    revised['lim']['copper_iqd_per_kg']=[(copper+premium)*revised['currency']['iqd_per_usd']
        for premium in (.8,2.,5.)]
    return revised,dict(source_observations=[motor['id'],vfd['id'],'cn-nbs-20261021-31-copper-1'],
        module_budget=detail,retained_unpriced_scopes=['mechanical integration','grid/protection','installation','charging'],
        copper_usd_per_kg_before_wire_conversion=copper,
        interpretation='Rated industrial hardware is a costing calibration only; hot ambient, current sharing, harmonic, thermal, insulation and LIM compatibility evidence remain open.')


def _row(lines,key):return next(r for r in lines if r['key']==key)


def _replace(lines,key,costs,quantity,basis,life=None):
    old=_row(lines,key);new=[]
    budget._add(new,key,old['scope'],quantity,[costs[c] for c in CASES],basis,life)
    old.clear();old.update(new[0])


def _factory(capital,spec,production,v,c):
    """Replace the old complete factory allocation, rather than adding another."""
    r,d,a=spec['requirements'],spec['design'],spec['capital'];fx=spec['currency']['iqd_per_usd']
    vehicle_floor=[];vehicle_campaign={};civil_campaign={};total={}
    for i,case in enumerate(CASES):
        assembly=production['assembly_bays'][i]
        receiving=max(200.,production['workplaces'][i]*a['workspace_area_m2'])
        floor=(v['cell_floor_m2'][i]+assembly*a['assembly_bay_area_m2']+receiving)*a['factory_storage_area_factor']
        vehicle_floor.append(floor)
        common=a['vehicle_fixture_sets']*a['vehicle_fixture_iqd'][i]+assembly*a['assembly_crew_per_bay']*a['workplace_tooling_iqd'][i]
        vehicle_campaign[case]=v['owned_factory_capital_usd'][case]*fx+floor*a['factory_building_iqd_per_m2'][i]+common
        civil_campaign[case]=c['owned_factory_capital_usd'][case]*fx+c['precast_floor_m2'][i]*a['factory_building_iqd_per_m2'][i]+c['precast_yard_m2'][i]*a['precast_yard_iqd_per_m2'][i]
        total[case]=vehicle_campaign[case]+civil_campaign[case]
    _replace(capital,'project-production-buildings-and-tooling',total,
        dict(vehicle_factory_building_m2=vehicle_floor,vehicle_owned_cell_floor_m2=v['cell_floor_m2'],
            precast_factory_building_m2=c['precast_floor_m2'],precast_yard_m2=c['precast_yard_m2'],
            vehicle_campaign_iqd=vehicle_campaign,civil_campaign_iqd=civil_campaign,
            production_shifts=2,civil_shifts=2,fixed_factory_cost_counted_once=True),
        'One project allocation for selected owned equipment/tooling, common assembly fixtures and shared buildings/yards. Contractor and imported-component factories stay inside purchased prices. Setup is renewed only with the relevant production campaign.')
    owns_fasteners=any(x['item']=='complete-fasteners' and x['selected_route']=='make' for x in c['decisions'])
    fastener_site=c['assumptions']['fastener_floor_m2_charged_in_own_capital'] if owns_fasteners else [0.,0.,0.]
    owns_precast=any(x['item']=='structural-precast-beam' and x['selected_route']=='make' for x in c['decisions'])
    land=_row(capital,'land-and-utility-relocation');q=deepcopy(land['quantity'])
    q.update(vehicle_factory_m2=vehicle_floor,precast_factory_yard_m2=[max(c['precast_floor_m2'][i],c['precast_yard_m2'][i])+fastener_site[i] for i in range(3)])
    costs={case:(r['route_km']*1000*a['row_width_m']*a['new_row_acquisition_fraction'][i]+q['depot_area_m2']+vehicle_floor[i]+q['precast_factory_yard_m2'][i])*a['land_iqd_per_m2'][i]+r['route_km']*a['utilities_iqd_per_route_km'][i] for i,case in enumerate(CASES)}
    _replace(capital,land['key'],costs,q,land['basis'])
    production.update(vehicle_factory_building_m2=vehicle_floor,
        precast_factory_yard_m2=q['precast_factory_yard_m2'],vehicle_campaign_capital_iqd=vehicle_campaign,
        civil_campaign_capital_iqd=civil_campaign,fixed_factory_cost_counted_once=True,
        moulds=c['assumptions']['mould_counts'] if owns_precast else [0.,0.,0.],
        precast_owned=owns_precast,fastener_workshop_owned=owns_fasteners)


def _project_allowances(capital,spec,new_vc,old_vc,service):
    """Do not add duty again on costs already explicitly valued as landed."""
    a=spec['capital'];old={r['line_key']:r for r in old_vc['lines']}; factors=new_vc['mass_reserve_sensitivity']['case_factors']
    held=[r for r in new_vc['lines'] if r['line_key'].startswith('unlocated-account/') and r['cost_iqd']==old[r['line_key']]['cost_iqd']]
    unlanded={'launch-grid-protection-install','launch-contact-and-return-hardware',
        'LIM-primary-installed','auxiliary-charging-and-grid-increment'}
    unknown_import={case:fsum(r['cost_iqd'][case]/factors[case] for r in held)*service['total_trainsets']
        +fsum(r['costs_iqd'][case] for r in capital if r['key'] in unlanded) for case in CASES}
    _replace(capital,'tax-and-import-duty-provision',
        {case:unknown_import[case]*a['tax_duty_provision_fraction'][i] for i,case in enumerate(CASES)},
        dict(unallocated_equipment_base_iqd=unknown_import,fraction=a['tax_duty_provision_fraction'],
            already_landed_materials_modules_and_factory_cells_excluded=True),
        'Planning tax/duty provision on unmatched equipment and unlanded packages only. Explicit landed raw-material, finished-component and drive-module duties are not charged again. These are scenario provisions, not legal rates.')
    excluded={'engineering-prototypes-independent-testing','tax-and-import-duty-provision','project-risk-contingency'}
    direct={case:fsum(r['costs_iqd'][case] for r in capital if r['key'] not in excluded) for case in CASES}
    _replace(capital,'engineering-prototypes-independent-testing',
        {case:direct[case]*a['engineering_testing_fraction'][i] for i,case in enumerate(CASES)},
        dict(direct_budget_iqd=direct,fraction=a['engineering_testing_fraction']),
        'Unchanged prototype, engineering and independent-review percentage applied to the recalculated complete direct scope; no physical requirement waived.')
    subtotal={case:fsum(r['costs_iqd'][case] for r in capital if r['key']!='project-risk-contingency') for case in CASES}
    _replace(capital,'project-risk-contingency',
        {case:subtotal[case]*a['project_contingency_fraction'][i] for i,case in enumerate(CASES)},
        dict(pre_contingency_iqd=subtotal,fraction=a['project_contingency_fraction']),
        'Unchanged risk-contingency percentage applied after explicit scope recalculation; this is not a negotiated discount.')


def evaluate_case(spec,vehicle,vc,service,civil,assumptions,mode,scenario,*,cache=None,root=ROOT):
    if scenario not in SCENARIOS:raise ValueError('Unknown supply scenario')
    epoch=sources(root);cache={} if cache is None else cache
    reference_capital,reference_production=budget._capital(spec,vehicle,vc,service,civil,assumptions,mode)
    reference_life,reference_operating=budget._lifecycle(spec,service,vc,reference_capital,assumptions,mode)
    if scenario=='reference-rates':
        return dict(capital=reference_capital,lifecycle=reference_life,production=reference_production,
            operating=reference_operating,scenario=scenario,source_sha256=epoch,**FLAGS)
    d=spec['design']
    if tuple(d[k] for k in ('production_years','production_days_per_year','production_shifts','hours_per_production_shift','productive_utilisation'))!=(3,250,2,8.,.75):
        raise ValueError('This supply adapter requires its declared three-year, two-shift production domain')
    contract=identity(dict(specification=spec,source_sha256=epoch,root=str(Path(root).resolve())))
    key=('vehicle',contract,vc['cost_estimate_id'],service['totalcars'],scenario)
    if key not in cache:cache[key]=vehicle_supply.revalue(vc,service,scenario,root=root)
    v=cache[key]
    if v['assumptions']['iqd_per_usd']!=spec['currency']['iqd_per_usd']:
        raise ValueError('Vehicle supply and project currency contexts differ')
    key=('civil',contract,civil['evaluation_id'],scenario)
    if key not in cache:cache[key]=civil_supply.revalue(civil,spec,scenario,root=root)
    c=cache[key];priced,drive=_electrical(spec,service,mode,root,c['civil']['unit_rates'])
    capital,production=budget._capital(priced,vehicle,v['vehicle_cost'],service,c['civil'],assumptions,mode)
    _factory(capital,priced,production,v,c)
    _project_allowances(capital,priced,v['vehicle_cost'],vc,service)
    # Fleet unit prices exclude owned setup. Rebuild it once with each future
    # vehicle production campaign; never amortize initial plant over future orders.
    renewal_inputs=deepcopy(capital);_row(renewal_inputs,'delivered-and-assembled-fleet')['life_years']=None
    life,operating=budget._lifecycle(priced,service,v['vehicle_cost'],renewal_inputs,assumptions,mode)
    renew=_row(life,'scheduled-renewals');events=deepcopy(renew['quantity']['events']);extra={case:0. for case in CASES}
    delivered=_row(capital,'delivered-and-assembled-fleet')
    for i,case in enumerate(CASES):
        exposure=priced['requirements']['operating_hours_per_day']/18
        for year in model_cost.replacement_event_times(priced['requirements']['design_life_years'],priced['lifecycle']['vehicle_life_years'][i]/exposure):
            amount=(delivered['costs_iqd'][case]+production['vehicle_campaign_capital_iqd'][case])/(1+priced['requirements']['real_discount_rate'])**year
            extra[case]+=amount;events.append(dict(line_id=delivered['line_id'],case=case,year=year,present_value_iqd=amount,vehicle_factory_setup_included_once=True))
    renewal_cost={case:renew['costs_iqd'][case]+extra[case] for case in CASES}
    _replace(life,'scheduled-renewals',renewal_cost,{**renew['quantity'],'events':events},
        'Disjoint asset replacements plus complete fleet production campaigns, including their fixed setup once; no renewal of precast plant without civil production.')
    # A cheaper purchasing basis alone does not demonstrate reduced maintenance
    # work or disposal effort for the same physical railway.
    for key in ('routine-maintenance','decommissioning'):
        target=_row(life,key);original=deepcopy(_row(reference_life,key));target.clear();target.update(original)
        target['basis']+=' Held at reference physical-service reserve: lower purchase prices alone do not prove less maintenance/disposal work.'
        target.pop('line_id');target['line_id']=identity(target)
    operating['annual_maintenance_iqd']=reference_operating['annual_maintenance_iqd']
    old={r['key']:r for r in reference_capital}
    delta=[dict(key=r['key'],reference_iqd=old[r['key']]['costs_iqd'],revised_iqd=r['costs_iqd'],
        base_difference_iqd=r['costs_iqd']['base']-old[r['key']]['costs_iqd']['base']) for r in capital]
    merged=dict(epoch)
    for mapping in (v['source_sha256'],c['source_sha256']):
        for name,sha in mapping.items():
            if name in merged and merged[name]!=sha:raise ValueError('Mixed supply source epochs')
            merged[name]=sha
    if any(digest(Path(root)/n)!=sha for n,sha in merged.items()):raise ValueError('Supply sources changed during evaluation')
    return seal(dict(capital=capital,lifecycle=life,production=production,operating=operating,
        scenario=scenario,vehicle=v,civil=c,drive=drive,capital_waterfall=delta,
        physical_quantities_changed=False,reference_cost_estimate_id=vc['cost_estimate_id'],
        source_sha256=merged,**FLAGS))


def benchmark(root=ROOT):
    """Revalue the exact 30 km / 12-station / 52-train comparison."""
    from . import coordinator
    context=coordinator.prepare(root);spec=context['spec'];vc=context['vehicle_cost'];vehicle=context['vehicle']
    from engineering.design_search import line_benchmark_service,line_benchmark_civil
    service=line_benchmark_service.evaluate(spec['requirements'],spec['design'],vehicle)
    civil=line_benchmark_civil.evaluate(spec['requirements'],spec['design'],vehicle,root=root)
    rows=[];cache={};fx=spec['currency']['iqd_per_usd'];epoch={}
    for scenario in SCENARIOS:
        for mode in budget.MODES:
            value=evaluate_case(spec,vehicle,vc,service,civil,context['assumptions'],mode,scenario,cache=cache,root=root)
            cap={c:fsum(r['costs_iqd'][c] for r in value['capital'])/fx for c in CASES}
            npv={c:cap[c]+fsum(r['costs_iqd'][c] for r in value['lifecycle'])/fx for c in CASES}
            rows.append(dict(scenario=scenario,mechanism=mode,installed_capital_usd=cap,
                price_per_route_km_usd={c:cap[c]/spec['requirements']['route_km'] for c in CASES},
                whole_life_npv_usd=npv,details=value))
            epoch.update(value['source_sha256'])
    return seal(dict(schema='osr-supply-benchmark/1',service=service,
        functional_requirements=budget.functional_requirements(spec),requirements_id=identity(budget.functional_requirements(spec)),
        policy=policy(root),variants=rows,source_sha256={**context['sources'],**epoch},**FLAGS))


def publish(output,root=ROOT):
    output=Path(output)
    if output.exists():raise ValueError('Fresh immutable supply publication required')
    value=benchmark(root);output.mkdir(parents=True)
    (output/'result.json').write_bytes(encoded(value))
    compact=[{k:v for k,v in row.items() if k!='details'} for row in value['variants']]
    (output/'summary.json').write_bytes(encoded(dict(evaluation_id=value['evaluation_id'],variants=compact,
        requirements_id=value['requirements_id'],**FLAGS)))
    m=seal(dict(schema='osr-supply-publication/1',evaluation_id=value['evaluation_id'],
        source_sha256=value['source_sha256'],files_sha256={n:digest(output/n) for n in ('result.json','summary.json')},**FLAGS),'manifest_id')
    (output/'manifest.json').write_bytes(encoded(m));return m


def verify(output,root=ROOT):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes())
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Supply manifest identity differs')
    if set(m['files_sha256'])!={'result.json','summary.json'}:raise ValueError('Unexpected supply artifact paths')
    if any(digest(output/n)!=sha for n,sha in m['files_sha256'].items()):raise ValueError('Supply payload differs')
    if any(digest(Path(root)/n)!=sha for n,sha in m['source_sha256'].items()):raise ValueError('Supply source epoch differs')
    actual=benchmark(root)
    if encoded(actual)!=(output/'result.json').read_bytes():raise ValueError('Supply benchmark replay differs')
    return m


def compact_summary(value):
    return dict(schema='osr-supply-summary/1',evaluation_id=value['evaluation_id'],
        requirements_id=value['requirements_id'],policy=value['policy'],
        variants=[{k:v for k,v in row.items() if k!='details'} for row in value['variants']],**FLAGS)


def publish_compact(state,output,root=ROOT):
    state=Path(state);output=Path(output);verified=verify(state,root)
    value=json.loads((state/'result.json').read_bytes())
    if output.exists():raise ValueError('Fresh compact supply output required')
    output.mkdir(parents=True)
    (output/'summary.json').write_bytes(encoded(compact_summary(value)))
    m=seal(dict(schema='osr-supply-compact-publication/1',evaluation_id=value['evaluation_id'],
        source_sha256=value['source_sha256'],canonical_result_sha256=verified['files_sha256']['result.json'],
        files_sha256={'summary.json':digest(output/'summary.json')},
        full_run_storage='Private immutable execution artifacts; regenerate through engineering.outline supply',**FLAGS),'manifest_id')
    (output/'manifest.json').write_bytes(encoded(m));return m


def verify_compact(output,root=ROOT):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes())
    if (m.get('schema')!='osr-supply-compact-publication/1'
            or m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'})):
        raise ValueError('Compact supply manifest differs')
    if set(m['files_sha256'])!={'summary.json'} or digest(output/'summary.json')!=m['files_sha256']['summary.json']:
        raise ValueError('Compact supply payload differs')
    if any(digest(Path(root)/n)!=sha for n,sha in m['source_sha256'].items()):raise ValueError('Compact supply sources differ')
    if any(m.get(k) is not False for k in FLAGS):raise ValueError('Supply pricing cannot authorize procurement or physical release')
    actual=benchmark(root)
    if identity(actual)!=m['canonical_result_sha256'] or actual['evaluation_id']!=m['evaluation_id'] or encoded(compact_summary(actual))!=(output/'summary.json').read_bytes():
        raise ValueError('Compact supply calculation replay differs')
    return m
