"""Same-service Class C cost ledger for unqualified flanged-span research.

Reuses the authenticated canonical service/vehicle ledger and the actual
flanged stock/process recipe. Shared input prices are normalized to the
canonical/topology scenarios. No numerical demand is physical qualification.
"""
from copy import deepcopy
from math import ceil, fsum, isclose
from pathlib import Path
import gzip
import json
import re

from engineering.station_rail import civil
from engineering.station_rail.common import digest, identity
from engineering.development_baseline import system_cost
from . import flanged_span as span, model_cost as model, topology_cost, topology_system_cost as base

PRODUCER = 'engineering/design_search/flanged_system_cost.py'
CASES = model.CASES
FLAGS = dict(base.FLAGS)


def reserve_process_spec():
    """Bounded process hypotheses, not measured production or qualified joints."""
    return dict(schema='osr-flanged-reserve-process/1',
        provenance='Class C process, waste and QA assumptions; actual details, machines and inspection remain unqualified',
        steel_material_yield=[.96,.90,.82],
        rebar_cut_bend_tie_person_hours_per_kg=[.01,.04,.12],
        rebar_machine_hours_per_kg=[.002,.008,.025],
        bracing_cut_weld_person_hours_per_kg=[.025,.08,.25],
        bracing_machine_hours_per_kg=[.005,.02,.06],
        fabricated_reserve_qa_person_hours_per_kg=[.002,.006,.02],
        connector_install_person_hours_per_kg=[.005,.02,.06],
        protection_install_person_hours_per_kg=[.005,.02,.06],
        finished_equipment_qa_person_hours_per_kg=[.001,.004,.012])


def _reserve_spec(value):
    spec=deepcopy(reserve_process_spec() if value is None else value);template=reserve_process_spec()
    if (not isinstance(spec,dict) or set(spec)!=set(template) or spec['schema']!=template['schema']
            or not isinstance(spec['provenance'],str) or not spec['provenance']):
        raise ValueError('Complete versioned reserve process assumptions required')
    for key in set(template)-{'schema','provenance'}:
        rows=spec[key]
        if (not isinstance(rows,list) or len(rows)!=3
                or any(not model._finite(x) or x<=0 or x>10 for x in rows)):
            raise ValueError('Positive bounded reserve process case rates required: '+key)
        if key=='steel_material_yield':
            if any(x>1 for x in rows) or rows!=sorted(rows,reverse=True):raise ValueError('Descending physical material yields required')
        elif rows!=sorted(rows):raise ValueError('Ordered reserve process uncertainty required: '+key)
    return spec


def _seal(value, key='evaluation_id'):
    value[key] = identity({k:v for k,v in value.items() if k != key})
    return value


def _sources(root):
    root=Path(root).resolve()
    if digest(root/PRODUCER) != digest(Path(__file__)):
        raise ValueError('Executing flanged system-cost producer differs from root')
    current=base._sources(root)
    for name,source in span._sources().items():
        if digest(root/name)!=source:
            raise ValueError('Flanged producer source differs from root: '+name)
        current[name]=source
    current[PRODUCER]=digest(Path(__file__))
    return dict(sorted(current.items()))


def _authenticated_baseline(baseline,root,expected_manifest_id):
    """Require the caller's externally pinned topology publication identity."""
    if not isinstance(expected_manifest_id,str) or re.fullmatch('[0-9a-f]{64}',expected_manifest_id) is None:
        raise ValueError('Externally pinned baseline manifest identity required')
    root=Path(root).resolve();folder=root/'docs/design-engine/civil-topology';manifest_path=folder/'manifest.json';archive=folder/'baseline.json.gz'
    if any(p.is_symlink() for p in (folder,manifest_path,archive)) or not manifest_path.is_file() or not archive.is_file():
        raise ValueError('Ordinary published baseline manifest and archive required')
    if manifest_path.stat().st_size>4*1024**2 or archive.stat().st_size>16*1024**2:
        raise ValueError('Bounded baseline archive and manifest required')
    manifest=json.loads(manifest_path.read_bytes());base._check(manifest,'manifest_id')
    if (manifest.get('schema')!='osr-civil-topology-publication/1' or manifest['manifest_id']!=expected_manifest_id
            or any(manifest.get(k) is not False for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release'))
            or manifest.get('files_sha256',{}).get('baseline.json.gz')!=digest(archive)):
        raise ValueError('Published baseline manifest or archived bytes differ from externally pinned identity')
    with gzip.open(archive,'rb') as stream: raw=stream.read(128*1024**2+1)
    if len(raw)>128*1024**2 or json.loads(raw)!=baseline:
        raise ValueError('Supplied baseline differs from authenticated published archive')
    base._source_check(manifest['source_sha256'],root)
    return dict(manifest_id=expected_manifest_id,manifest_path='docs/design-engine/civil-topology/manifest.json',
        archive_sha256=digest(archive),baseline_id=baseline['baseline_id'],
        identity_source='Externally trusted caller reference; self-sealing alone does not establish authenticity')


def _contexts(baseline, context, root, *, expected_baseline_manifest_id, require_current_tools=True):
    binding=_authenticated_baseline(baseline,root,expected_baseline_manifest_id)
    base.validate_baseline(baseline,root,require_current_tools=require_current_tools)
    span._context(context,root)
    if context != span.load_context(root):
        raise ValueError('Flanged context does not replay current selected ledger')
    expected=baseline['load_context']; selected=baseline['selected']
    for k in ('vehicle_candidate_id','vehicle_evaluation_id','selection_id','body_candidate_id',
              'support_component_id','propulsion_component_id','selected_context_id','mass_reserve_result_id',
              'dynamic_factor_applied_once'):
        if context[k]!=expected[k]:raise ValueError('Mixed selected load context: '+k)
    keys=('name','vehicle_mass_case','tare_kg_per_car','loaded_kg_per_car','full_axle_force_N','offsets_m')
    if [{k:r[k] for k in keys} for r in context['cases']] != [{k:r[k] for k in keys} for r in expected['cases']]:
        raise ValueError('Vehicle loading and axle cases differ')
    if context['vehicle_candidate_id']!=selected['candidate_id']:
        raise ValueError('Selected physical vehicle differs')
    return binding


def composition(candidate, baseline):
    span._candidate(candidate)
    selected=baseline['selected']
    physical=dict(schema='osr-flanged-railway-research-composition/1',
        vehicle_components={k:selected[k] for k in ('candidate_id','body_candidate_id','support_component_id','propulsion_component_id')},
        civil_candidate_id=candidate['candidate_id'],
        route=deepcopy(baseline['cases']['base']['bundle']['architecture_case']['physical_definition']['route']),
        civil_interfaces=dict(span_m=20.,deck_width_m=2.,rail_interfaces_retained=True))
    return dict(physical_definition=physical,candidate_id=identity(physical))


def _quantity_checks(candidate,quantity,scoped,baseline):
    span._candidate(candidate);span._sealed(quantity,'evaluation_id');span._sealed(scoped,'evaluation_id')
    spec=span._spec(scoped['assumptions'])
    if span.quantities(candidate,spec)!=quantity or span.estimate(candidate,quantity,spec)!=scoped:
        raise ValueError('Flanged quantities or actual process recipe do not replay')
    a=baseline['assumptions']
    for name,value in [('production_shifts_per_day',2),('production_hours_per_shift',8),
                       ('civil_shifts_per_day',2),('civil_hours_per_shift',8)]:
        if a[name]!=value:raise ValueError('Canonical two-shift basis differs')
    if (spec['production_shifts_per_day']!=a['production_shifts_per_day']
            or spec['civil_shifts_per_day']!=a['civil_shifts_per_day']
            or spec['hours_per_shift']!=a['production_hours_per_shift']
            or spec['hours_per_shift']!=a['civil_hours_per_shift']
            or spec['productive_utilisation']!=a['productive_utilisation']):
        raise ValueError('Flanged and canonical shift or utilization assumptions differ')
    corridor=baseline['cases']['base']['cost']['corridor_basis'];n=corridor['span_count']
    indexed=base._lines(baseline['cases']['base']['cost']['cost_line_items'],baseline['cases']['base']['cost']['candidate_id'])
    rails=indexed['precast-rails']['quantity'];sets=indexed['rail-fastener-sets']['quantity']
    if (not isclose(quantity['rail_mass_kg'],rails['mass_kg']/n,rel_tol=1e-12)
            or quantity['fastener_set_count']!=sets['sets']/n
            or not isclose(quantity['fastener_mass_kg'],sets['counted_hardware_mass_kg']/n,rel_tol=1e-12)):
        raise ValueError('Canonical and flanged rail or complete-fastener accounts differ')
    if scoped['whole_system_ranking_allowed'] is not False or scoped['complete_installed_cost_iqd'] is not None:
        raise ValueError('Scoped study must remain unqualified')
    return spec


def _support_demands(candidate,quantity,baseline,context,*,root):
    """Ideal point-bearing gravity scenarios only; not a site or strength bound."""
    span._candidate(candidate);span._sealed(quantity,'evaluation_id');span._sealed(context,'context_id')
    cases={name:dict(load_cases={}) for name in CASES}
    for vehicle in context['cases']:
        live=civil.interior_pier_train_reaction(20.,vehicle['offsets_m'],vehicle['full_axle_force_N'])['maximum_live_reaction_N']
        rows={}
        for name in CASES:
            mass=quantity['accounted_mass_kg_cases'][name];dead=mass*civil.G;reaction=dead+live
            rows[name]=dict(accounted_span_mass_kg=mass,adjacent_span_dead_reaction_N=dead,
                ideal_point_bearing_live_reaction_N=live,interior_support_vertical_reaction_N=reaction,
                minimum_gravity_area_m2_by_assumed_pressure_kpa={str(p):reaction/(p*1000.) for p in (300,200,100)},
                actual_foundation_quantity=None,soil_capacity_verified=False,unknown_pier_and_foundation_selfweight=True,
                finite_bearing_and_actual_sharing_qualified=False)
        cases[vehicle['vehicle_mass_case']]['load_cases'][vehicle['name']]=dict(financial_cases=rows)
    return _seal(dict(schema='osr-flanged-support-scenarios/1',candidate_id=candidate['candidate_id'],
        geometry_id=candidate['geometry_id'],quantity_evaluation_id=quantity['evaluation_id'],
        baseline_id=baseline['baseline_id'],selected_vehicle_candidate_id=context['vehicle_candidate_id'],
        load_context_id=context['context_id'],cases=cases,
        basis='One complete span weight at an interior support and ideal point-bearing live reaction; no finite-bearing amplification, site evidence or physical upper bound',
        source_sha256={**baseline['source_sha256'],**span._sources(),PRODUCER:digest(Path(__file__))},**FLAGS))


def _normalized(candidate,quantity,scoped,baseline,reserve_spec=None):
    """Price actual process hours/stock with shared rates; rails remain separate."""
    assumptions=baseline['assumptions'];a=assumptions['assumptions'];bench=assumptions['benchmark_rates_iqd'];ts=topology_cost.default_spec()
    spec=scoped['assumptions'];reserve_spec=_reserve_spec(reserve_spec);g=quantity['source_quantities'];steel=g['by_material']['structural_steel']['mass_kg'];volume=g['by_material']['research_concrete']['volume_m3']
    surface=scoped['manufacturing_stock']['steel_coating_m2'];rows=[]
    for i,name in enumerate(CASES):
        old=scoped['cases'][name];wage=bench['wage_skilled_iqd_per_h']*a['wage_burden_multipliers'][i]*(1+a['second_shift_wage_premium'][i]/2)
        concrete=(a['concrete_cement_t_per_m3'][i]*bench['cement_iqd_per_t']+a['concrete_aggregate_m3_per_m3'][i]*bench['aggregate_iqd_per_m3']+a['concrete_sand_m3_per_m3'][i]*bench['sand_iqd_per_m3']+a['concrete_admixture_iqd_per_m3'][i])*(1+a['concrete_waste_fraction'][i])
        reserve={}
        for k,v in spec['reserve_mass_kg'].items():
            rate=(bench['rebar_iqd_per_kg']*a['material_rate_sensitivity'][i] if k=='deck_rebar'
                else a['steel_iqd_per_kg'][i] if k in ('bracing','splice_and_weld_metal') else a['finished_equipment_iqd_per_kg'][i])
            yield_factor=reserve_spec['steel_material_yield'][i] if k in ('deck_rebar','bracing','splice_and_weld_metal') else 1.
            reserve[k]=v[i]/yield_factor*rate
        masses={k:v[i] for k,v in spec['reserve_mass_kg'].items()}
        additions=dict(
            rebar_cut_bend_tie=masses['deck_rebar']*reserve_spec['rebar_cut_bend_tie_person_hours_per_kg'][i],
            bracing_cut_weld=masses['bracing']*reserve_spec['bracing_cut_weld_person_hours_per_kg'][i],
            fabricated_reserve_qa=(masses['deck_rebar']+masses['bracing'])*reserve_spec['fabricated_reserve_qa_person_hours_per_kg'][i],
            connector_install=masses['connectors']*reserve_spec['connector_install_person_hours_per_kg'][i],
            protection_install=masses['protection_hardware']*reserve_spec['protection_install_person_hours_per_kg'][i],
            finished_equipment_qa=(masses['connectors']+masses['protection_hardware']+masses['bearings'])*reserve_spec['finished_equipment_qa_person_hours_per_kg'][i])
        added_machine=(masses['deck_rebar']*reserve_spec['rebar_machine_hours_per_kg'][i]+masses['bracing']*reserve_spec['bracing_machine_hours_per_kg'][i])
        coating_hours=surface*ts['coating_hours_per_m2'][i]
        process_hours=fsum(old['factory_labour_hours'].values())+coating_hours+fsum(additions.values())
        machine_hours=old['machine_operating_hours']+added_machine
        if (scoped['manufacturing_stock']['girder_splices']<=0 or scoped['manufacturing_stock']['full_penetration_butt_weld_m']<=0
                or old['factory_labour_hours']['full_moment_splice_weld']<=0 or old['factory_labour_hours']['qa']<=0):
            raise ValueError('Existing positive splice welding and QA process required')
        items=dict(main_steel=steel/ts['steel_purchase_yield'][i]*a['steel_iqd_per_kg'][i],
            concrete_ingredients=volume*concrete,**{'reserve_'+k:v for k,v in reserve.items()},
            process_labour=process_hours*wage,machine_operating=machine_hours*a['machine_rate_iqd_per_h'][i],
            coating_consumables=surface*ts['coating_iqd_per_m2'][i])
        direct=fsum(items.values());overhead=direct*a['factory_overhead_fraction'][i]
        rail_hours=quantity['fastener_set_count']*spec['rates']['rail_install_h_set'][i]
        erection_hours=old['civil_labour_hours']-rail_hours
        if erection_hours<=0:raise ValueError('Positive non-rail erection hours required')
        rows.append(dict(case=name,actual_scoped_record_id=scoped['evaluation_id'],factory_items_iqd=items,
            factory_overhead_iqd=overhead,factory_gate_iqd=direct+overhead,
            actual_process_hours=deepcopy(old['factory_labour_hours']),added_coating_person_hours=coating_hours,
            added_reserve_process_person_hours=additions,added_reserve_machine_hours=added_machine,
            total_factory_person_hours=process_hours,machine_operating_hours=machine_hours,
            reserve_coverage='Rebar cutting/bending/tying and bracing fabrication/QA added; existing brace/bearing assembly retained once; connectors/protection installation and finished-equipment QA added; splice welding/QA already in original route',
            shared_loaded_wage_iqd_per_h=wage,accounted_mass_kg=quantity['accounted_mass_kg_cases'][name],
            erection_person_hours=erection_hours,rail_person_hours_excluded=rail_hours,
            crane_hours=old['crane_hours'],reserve_cost_iqd=reserve,
            rails_and_fastener_cost_excluded=True,transport_iqd_per_tonne_km=ts['transport_iqd_per_tonne_km'][i],
            transport_distance_km=ts['transport_distance_km'],
            crane_iqd_per_shift=a['erection_crane_iqd_per_shift'][i],
            plant_capital_per_cell_iqd=ts['dedicated_plant_capital_iqd'][i],tooling_per_cell_iqd=ts['tooling_iqd'][i],
            coating_renewal_years=ts['coating_renewal_years'][i],bearing_renewal_years=ts['bearing_renewal_years'][i]))
    return _seal(dict(schema='osr-flanged-canonical-rate-normalization/1',candidate_id=candidate['candidate_id'],
        geometry_id=candidate['geometry_id'],quantity_evaluation_id=quantity['evaluation_id'],
        scoped_cost_evaluation_id=scoped['evaluation_id'],canonical_assumption_id=assumptions['assumption_id'],
        reserve_process_spec=reserve_spec,reserve_process_spec_id=identity(reserve_spec),
        normalization_basis='Flanged stock and process hours; common dated benchmark wages, material, machine, overhead, coating, haul and crane scenarios. Original scoped prices are not added.',
        factory_capital_and_coating_basis='Shared topology Class C plant, tooling and coating hypotheses; not equipment quotes or verified cycle capacity',
        cases=rows,source_sha256={**scoped['source_sha256'],**model.sources(Path(__file__).resolve().parents[2]),
            topology_cost.PRODUCER:digest(Path(topology_cost.__file__)),PRODUCER:digest(Path(__file__))},**FLAGS))


def compare(candidate,quantity,scoped,baseline,context,*,root,expected_baseline_manifest_id,require_current_tools=True,reserve_spec=None):
    """Three vehicle mass cases x three coherent cost cases; no safety promotion."""
    reserve_spec=_reserve_spec(reserve_spec)
    input_identity=identity(dict(candidate=candidate,quantity=quantity,scoped=scoped,baseline=baseline,context=context,reserve_spec=reserve_spec,expected_baseline_manifest_id=expected_baseline_manifest_id))
    root=Path(root).resolve();binding=_contexts(baseline,context,root,expected_baseline_manifest_id=expected_baseline_manifest_id,require_current_tools=require_current_tools)
    spec=_quantity_checks(candidate,quantity,scoped,baseline)
    source=_sources(root);physical=composition(candidate,baseline);cid=physical['candidate_id']
    support=_support_demands(candidate,quantity,baseline,context,root=root)
    normalized=_normalized(candidate,quantity,scoped,baseline,reserve_spec);rows=normalized['cases']
    a_record=baseline['assumptions'];a=a_record['assumptions'];n=baseline['cases']['base']['cost']['corridor_basis']['span_count']
    capacity=a_record['production_years']*a_record['production_days_per_year']*a_record['production_shifts_per_day']*a_record['production_hours_per_shift']*a_record['productive_utilisation']
    hours=[n*r['total_factory_person_hours'] for r in rows]
    cells=[max(1,ceil(h/(capacity*spec['production_crew_per_shift']))) for h in hours]
    moulds=[max(1,ceil(n*a['beam_mould_cycle_days'][i]/(a_record['production_years']*a_record['production_days_per_year']))) for i in range(3)]
    outputs={}
    for mass_name,case in baseline['cases'].items():
        cost=case['cost'];corridor=cost['corridor_basis']
        if corridor!=baseline['cases']['base']['cost']['corridor_basis']:raise ValueError('Mixed corridor basis')
        old=base._lines(cost['cost_line_items'],cost['candidate_id'])
        lines=[base._wrap(r,cid,baseline['baseline_id']) for r in cost['cost_line_items'] if r['line_key'] not in base.REPLACE_KEYS and (r['scope']!='guideway' or r['line_key'] in {'precast-rails','rail-fastener-sets'})]
        foundation=next(r for r in lines if r['line_key']=='foundation-footing-pier-proxy')
        foundation['quantity'].update(gravity_support_evaluation_id=support['evaluation_id'],
            gravity_support_cases=deepcopy(support['cases'][mass_name]),price_proxy_mass_coupled=False,
            site_capacity_verified=False,pier_selfweight_unknown=True)
        base._seal(foundation,'line_id');anc=[baseline['baseline_id'],quantity['evaluation_id'],scoped['evaluation_id'],normalized['evaluation_id'],support['evaluation_id']]
        base._add(lines,cid,'flanged-span-factory-gate','guideway',[n*r['factory_gate_iqd'] for r in rows],'factory-gate',anc,
            quantity=dict(spans=n,normalized_per_span=deepcopy(rows)),basis='Actual flanged stock and process hours, shared rate scenarios, no rail or fastener cost, no per-piece plant capital',group='guideway')
        base._add(lines,cid,'flanged-production-cells','factory-tooling',[cells[i]*rows[i]['plant_capital_per_cell_iqd'] for i in range(3)],'capital',anc,
            quantity=dict(cells=cells,crew_per_shift=spec['production_crew_per_shift'],person_hours=hours,productive_hours_per_operator=capacity,verified_machine_throughput=False),
            basis='Common Class C equipped-cell hypothesis; no measured workstation capacity')
        plant=[cells[i]*rows[i]['tooling_per_cell_iqd'] for i in range(3)];mould=[moulds[i]*a['beam_mould_iqd_each'][i] for i in range(3)]
        base._add(lines,cid,'flanged-tooling-and-deck-moulds','factory-tooling',[plant[i]+mould[i] for i in range(3)],'capital',anc,
            quantity=dict(tool_sets=cells,deck_mould_sets=moulds,cycle_days=a['beam_mould_cycle_days']),
            basis='Common tooling and deck mould proxies; special jig, splices and mould process unverified',components=dict(steel_tooling=plant,deck_moulds=mould))
        haul=[n*r['accounted_mass_kg']/1000*r['transport_distance_km']*r['transport_iqd_per_tonne_km'] for r in rows]
        base._add(lines,cid,'flanged-accounted-module-and-rail-haul','construction',haul,'delivered',anc,
            quantity=dict(spans=n,accounted_mass_kg_per_span=[r['accounted_mass_kg'] for r in rows],rails_and_complete_fasteners_counted_once=True),
            basis='All accounted span, rail and fastener masses transported once; route and handling permits unverified')
        labour=[n*r['erection_person_hours']*r['shared_loaded_wage_iqd_per_h'] for r in rows]
        crane_shifts=[ceil(n*r['crane_hours']/(8*a_record['productive_utilisation'])) for r in rows]
        cranes=[crane_shifts[i]*r['crane_iqd_per_shift'] for i,r in enumerate(rows)]
        rail=old['erection-rail-installation-and-temporary-works']['components_iqd']['rail_installation']
        direct=[labour[i]+cranes[i]+rail[i] for i in range(3)];contingency=[direct[i]*a['construction_contingency_fraction'][i] for i in range(3)]
        base._add(lines,cid,'flanged-erection-rail-and-temporary-works','construction',[direct[i]+contingency[i] for i in range(3)],'installed',anc,
            quantity=dict(spans=n,erection_person_hours=[n*r['erection_person_hours'] for r in rows],crane_hours=[n*r['crane_hours'] for r in rows],rail_installation_reused_once=True,
                productive_crane_hours=[n*r['crane_hours'] for r in rows],paid_crane_shifts=crane_shifts,
                productive_utilisation=a_record['productive_utilisation'],actual_lifts_per_span=None,
                crane_radius_m=None,crane_capacity_at_radius_t=None,transport_route_permits_verified=False),
            basis='Declared crane hours are productive duty; paid shifts include utilization. Common rail installation once and temporary-work contingency; lift count and crane capacity unknown',components=dict(labour=labour,crane=cranes,rail_installation=rail,contingency=contingency))
        years=a_record['design_life_years'];rate=a_record['real_discount_rate'];annuity=fsum((1+rate)**(-y) for y in range(1,years+1))
        maintained=[fsum(r['scenario_iqd'][c] for r in lines if r['scope'] in {'rolling-stock','guideway','stations-power'} and r['cost_stage'] in model.INITIAL_COST_STAGES) for c in CASES]
        annual=[maintained[i]*a['maintenance_fraction_per_year'][i]*a_record['operating_hours_per_day_cases'][i]/a_record['maintenance_reference_operating_hours_per_day'] for i in range(3)]
        base._add(lines,cid,'planned-maintenance-and-spares-lifecycle','maintenance',[v*annuity for v in annual],'lifecycle',anc,
            quantity=dict(maintainable_scope_iqd=maintained,annual_cost_iqd=annual,capital_renewal_events_excluded_by_assumption=True),basis='Assumed routine maintenance and spares exclude separately modelled coating, bearing and parent capital renewals; overlap not physically verified')
        plan=model.renewal_plan(lines,a_record)
        base._add(lines,cid,'bounded-asset-replacements','renewals',plan['renewal_NPV_iqd'],'lifecycle',anc+[plan['plan_id']],
            quantity=dict(renewal_plan_id=plan['plan_id'],renewal_plan=plan),basis='Common disjoint parent-asset renewal; each component assigned once')
        group=next(g for g in plan['asset_groups'] if g['asset_group']=='guideway');extra=[];extra_totals=[]
        for i,name in enumerate(CASES):
            parent_years=[e['year'] for e in group['cases'][i]['events']];events=[];reset=[]
            nonrail_mass=rows[i]['accounted_mass_kg']-quantity['rail_mass_kg']-quantity['fastener_mass_kg']
            if nonrail_mass<=0:raise ValueError('Positive non-rail span mass required')
            scoped_no_rails=rows[i]['factory_gate_iqd']+nonrail_mass/1000*rows[i]['transport_distance_km']*rows[i]['transport_iqd_per_tonne_km']+rows[i]['erection_person_hours']*rows[i]['shared_loaded_wage_iqd_per_h']+cranes[i]/n
            coating=scoped_no_rails*topology_cost.default_spec()['coating_renewal_fraction'][i]
            bearings=rows[i]['reserve_cost_iqd']['bearings']+rows[i]['erection_person_hours']*rows[i]['shared_loaded_wage_iqd_per_h']*.25
            for asset,life,basis in [('coating',rows[i]['coating_renewal_years'],coating),('bearings',rows[i]['bearing_renewal_years'],bearings)]:
                schedule=system_cost.component_renewal_schedule(years,life,parent_years);reset.append(dict(asset=asset,schedule_id=schedule['evaluation_id'],age_resets=schedule['age_resets']))
                for event in schedule['events']:
                    pv=0. if event['covered_by_parent_replacement'] else basis/(1+rate)**event['year']
                    events.append(dict(**event,asset=asset,undiscounted_iqd=basis,corridor_present_value_iqd=n*pv))
            events.sort(key=lambda e:(e['year'],e['asset']));extra.append(dict(case=name,events=events,component_age_resets=reset));extra_totals.append(fsum(e['corridor_present_value_iqd'] for e in events))
        base._add(lines,cid,'flanged-coating-and-bearing-renewals','renewals',extra_totals,'lifecycle',anc,
            quantity=dict(event_schedule=extra,coating_basis='Shared topology-style fraction of scoped installed span excluding rail',
                matched_canonical_coating_and_bearing_events=False),basis='Coating and bearing ages reset by complete guideway replacements; no coincident double charge. Canonical baseline has no matching separate component events')
        pack,pack_schedule=system_cost._account_renewal(cid,dict(cost_line_items=lines),a_record);lines.append(pack)
        installed=base._totals(lines,require_complete=False)['model_based_installed_CAPEX_iqd']
        disposal=[installed[i]*a['decommissioning_fraction_of_installed_CAPEX'][i]/(1+rate)**years for i in range(3)]
        base._add(lines,cid,'end-of-life-decommissioning-proxy','disposal',disposal,'lifecycle',anc,
            quantity=dict(base_installed_CAPEX_iqd=installed,year=years),basis='Common discounted end-of-life CAPEX fraction')
        production=deepcopy(cost['production_plan']);schedule=production['construction_schedule_days']
        erection_hours=[n*r['erection_person_hours'] for r in rows];crane_hours=[n*r['crane_hours'] for r in rows]
        crew_days=[ceil(x/(spec['civil_crew_per_shift']*16*a_record['productive_utilisation'])) for x in erection_hours]
        crane_days=[ceil(shifts/2) for shifts in crane_shifts]
        schedule.update(span_erection=[max(crew_days[i],crane_days[i]) for i in range(3)],
            flanged_erection_person_hours=erection_hours,flanged_productive_crane_hours=crane_hours,flanged_paid_crane_shifts=crane_shifts,precedence_and_resource_conflicts_resolved=False)
        critical=[max(schedule[k][i] for k in ('foundations','span_erection','rail_installation','stations')) for i in range(3)]
        schedule['critical_path_duration']=critical
        production.update(guideway_factory_hours=hours,required_guideway_workcells=cells,guideway_mould_sets=moulds,
            guideway_workcell_basis=dict(declared_operators_per_cell=spec['production_crew_per_shift'],productive_person_hours_per_cell=capacity*spec['production_crew_per_shift'],machine_cycle_and_precedence_throughput_resolved=False),
            construction_duration_days=critical,required_parallel_workcells=[production['required_vehicle_workcells'][i]+cells[i]+production['required_station_power_workcells'][i] for i in range(3)],
            factory_gate_vehicle_and_guideway_IQD=[round(fsum(r['scenario_iqd'][c] for r in lines if r['scope'] in {'rolling-stock','guideway'} and r['cost_stage']=='factory-gate'),2) for c in CASES])
        output=dict(candidate_id=cid,vehicle_mass_case=mass_name,cost_line_items=lines,**base._totals(lines),
            production_plan=production,corridor_basis=deepcopy(corridor),annual_maintenance_iqd=[round(x,2) for x in annual],
            renewal_plan=plan,service_pack_renewal_schedule=pack_schedule,flanged_renewal_schedule=extra,
            retained_conditional_model_ids=dict(bundle_definition_id=case['bundle']['definition_id'],architecture_evaluation_id=case['architecture_evaluation_id'],motion_evaluation_id=case['motion_evaluation_id']),
            support_demand_evaluation_id=support['evaluation_id'],**FLAGS)
        for key in ('annual_energy_iqd','annual_operations_iqd','annual_reliability_iqd','annual_electricity_kwh'):
            if key in cost:output[key]=deepcopy(cost[key])
        _seal(output);outputs[mass_name]=output
    delta={}
    for mass,row in outputs.items():
        old=baseline['cases'][mass]
        delta[mass]=dict(installed_CAPEX_delta_iqd=[round(row['model_based_installed_CAPEX_iqd'][i]-old['cost']['model_based_installed_CAPEX_iqd'][i],2) for i in range(3)],
            installed_comparison_scope='Conditional declared cost scenarios; site foundation proxy does not respond to changed load',
            whole_life_NPV_delta_iqd=None,whole_life_rankable=False,
            whole_life_hold='Canonical reference lacks matched separately modelled coating and bearing replacement events; differences cannot be treated as geometry savings')
    value=dict(schema='osr-flanged-system-cost/1',**physical,baseline_id=baseline['baseline_id'],baseline_publication=binding,
        replay_context=dict(current_tools_required=require_current_tools,baseline_tools=deepcopy(baseline['tool_context']),
            ledger_replay_tools=base._tools(),baseline_tool_reuse_check_enforced=require_current_tools,
            native_evaluator_admission=False),
        geometry_id=candidate['geometry_id'],quantity_evaluation_id=quantity['evaluation_id'],span_cost_evaluation_id=scoped['evaluation_id'],
        load_context_id=context['context_id'],support_demands=support,normalized_span_cost=normalized,
        source_sha256={**baseline['source_sha256'],**source},cases=outputs,comparison_to_corrected_canonical_baseline=delta,
        estimate_class='C',currency='IQD',model_cost_complete_for_declared_scope=True,
        whole_life_comparison_ready=False,whole_life_ranking_allowed=False,
        holds=['Actual physical installed mass, moving thrust, braking, protection and energy performance remain unknown',
            'Whole-life comparisons to the canonical baseline are held because its coating and bearing renewal events are not matched',
            'Routine maintenance fractions are assumed to exclude separate component and parent capital renewals; actual overlap is unverified',
            'Point-bearing gravity scenario is not a finite-bearing, foundation or site-capacity verification; unknown pier and footing weights are not zero',
            'Unqualified shear, torsion, deck transfer, local/lateral buckling, fatigue, splices, handling, fire and welds; no prestress is included',
            'Rail and station-LIM deformation and actual magnetic air-gap feedback are unknown; no allowable clearance or gap performance is inferred',
            'Site foundation price is an unchanged proxy, not a mass-coupled estimate or geotechnical design',
            'No certified life, measured process, capacity, crane reach, erection sequence, access or supplier quotation',
            'Same 6 km two-track 120-second nominal service and selected vehicle; no physical service feasibility or integrated selection'],
        integrated_selection=None,**FLAGS)
    if (identity(dict(candidate=candidate,quantity=quantity,scoped=scoped,baseline=baseline,context=context,reserve_spec=reserve_spec,expected_baseline_manifest_id=expected_baseline_manifest_id))!=input_identity
            or _sources(root)!=source):
        raise ValueError('Source epoch changed during system-cost calculation')
    base._source_check(baseline['source_sha256'],root)
    if _authenticated_baseline(baseline,root,expected_baseline_manifest_id)!=binding:
        raise ValueError('Authenticated baseline publication changed during calculation')
    topology_cost._finite_cost(value)
    return _seal(value)
