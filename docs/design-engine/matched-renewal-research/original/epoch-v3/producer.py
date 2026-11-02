"""Conditional, non-promoting renewal comparison of published span research.

Only declared scenario accounting is compared. Soil, bearing type/capacity,
constructability, physical acceptance, service feasibility and selection stay open.
"""
from copy import deepcopy
from math import fsum, isfinite
from pathlib import Path
import gc

from engineering.station_rail.common import digest, identity
from engineering.station_rail import civil
from engineering.development_baseline import system_cost
from . import flanged_system_cost as cost, flanged_system_cost_publication as publication

PRODUCER = 'engineering/design_search/matched_renewal_research.py'
CASES = cost.CASES


def assumptions():
    """Illustrative Class C hypotheses, not design values or supplier offers."""
    return dict(schema='osr-matched-renewal-assumptions/1',
        provenance='Synthetic bounds for sensitivity; procurement, access, compatibility and life are not verified',
        bearing_count_per_span=4, bearing_mass_kg_per_span=[100., 200., 400.],
        bearing_qa_hours_per_kg=[.001, .004, .012],
        bearing_install_hours_per_span=[4., 8., 16.],
        renewal_access_iqd_per_span=[100000., 500000., 2000000.],
        sealer_material_iqd_per_m2=[3000., 10000., 30000.],
        sealer_application_hours_per_m2=[.01, .04, .12],
        sealer_qa_hours_per_m2=[.002, .01, .03],
        sealer_renewal_years=[15., 10., 7.],
        maintenance_overlap_fraction=[0., .25])


def _assumptions(value):
    a=deepcopy(assumptions() if value is None else value); base=assumptions()
    if not isinstance(a,dict) or set(a)!=set(base) or a['schema']!=base['schema'] or not isinstance(a['provenance'],str) or not a['provenance']:
        raise ValueError('Complete versioned assumptions required')
    if a['bearing_count_per_span']!=4: raise ValueError('Four hypothetical bearings per span required')
    for k in set(base)-{'schema','provenance','bearing_count_per_span','maintenance_overlap_fraction'}:
        v=a[k]
        if not isinstance(v,list) or len(v)!=3 or any(type(x) not in (int,float) or not isfinite(x) or x<=0 or x>1e9 for x in v):
            raise ValueError('Positive finite low/base/high inputs required: '+k)
        if k=='sealer_renewal_years':
            if v!=sorted(v,reverse=True): raise ValueError('Descending sealer lives required')
        elif v!=sorted(v): raise ValueError('Ordered bounds required: '+k)
    v=a['maintenance_overlap_fraction']
    if not isinstance(v,list) or len(v)!=2 or v[0]!=0 or type(v[1]) not in (int,float) or not isfinite(v[1]) or not 0<v[1]<=1:
        raise ValueError('Maintenance overlap sensitivity requires zero and a positive fraction at most one')
    return a


def _line(lines,key):
    found=[x for x in lines if x['line_key']==key]
    if len(found)!=1: raise ValueError('Exactly one required line: '+key)
    return found[0]


def _events(years,life,parent_years,amount,n,rate):
    schedule=system_cost.component_renewal_schedule(years,life,parent_years)
    events=[]
    for e in schedule['events']:
        pv=0. if e['covered_by_parent_replacement'] else n*amount/(1+rate)**e['year']
        events.append(dict(**e,corridor_present_value_iqd=pv,per_span_iqd=amount))
    return dict(schedule_id=schedule['evaluation_id'],age_resets=schedule['age_resets'],events=events,
        present_value_iqd=fsum(e['corridor_present_value_iqd'] for e in events))


def _scope_sums(case):
    totals=case['scope_totals_iqd']
    if set(totals)!=set(cost.model.SCOPES) or any(len(v)!=3 or any(not isfinite(x) or x<0 for x in v) for v in totals.values()):
        raise ValueError('Complete finite fourteen-scope account required')
    return deepcopy(totals)


def _parents(folder,root,topology_id,flanged_id,publication_id):
    manifest,record=publication._check(folder,publication_id)
    cost.base._source_check(manifest['source_sha256'],root)
    raw=publication._snapshot(Path(folder)/'original')
    rows,source,binding=publication._audit(raw,root,topology_id,flanged_id,replay=False)
    if rows!=record['attempts'] or source!=record['source_sha256'] or binding!=record['parent_publications']:
        raise ValueError('Pinned publication attempts, source epoch or parents differ')
    if len(rows)!=3 or any(r['execution']!='completed' for r in rows):
        raise ValueError('All three requested attempts must be complete')
    return raw,record


def _reference(case,baseline,context,spec,sealed,*,sealer):
    a=baseline['assumptions']; x=a['assumptions']; n=case['cost']['corridor_basis']['span_count']; old=case['cost']; lines=old['cost_line_items']
    if case['civil_design_basis']['family']!='box-beam' or case['civil_design_basis']['span_m']!=20.: raise ValueError('Expected concrete 20 m box beam')
    concrete=_line(lines,'precast-beam-concrete-recipe')['quantity']['net_concrete_m3']
    section=civil.section('box-beam')['dimensions'];surface=2*(section['outer_width_m']+section['depth_m'])*20.
    erection=_line(lines,'erection-rail-installation-and-temporary-works')['quantity']['field_hours']
    if any(n*spec['bearing_install_hours_per_span'][i]>erection[i] for i in range(3)):
        raise ValueError('Bearing installation partition exceeds existing erection hours')
    haul=_line(lines,'beam-heavy-haul-to-site')['quantity']; span_mass=haul['counted_span_mass_t']*1000
    plan=old['cost_line_items']; renewal=_line(plan,'bounded-asset-replacements')['quantity']['renewal_plan']
    group=next(g for g in renewal['asset_groups'] if g['asset_group']=='guideway')
    scopes=_scope_sums(old); pack=case['renewal_line']['scenario_iqd']
    for i,k in enumerate(CASES):scopes['renewals'][i]+=pack[k]
    years=a['design_life_years'];rate=a['real_discount_rate'];annuity=fsum((1+rate)**(-y) for y in range(1,years+1));rows=[]
    support={}
    for load in context['cases']:
        live=civil.interior_pier_train_reaction(20.,load['offsets_m'],load['full_axle_force_N'])['maximum_live_reaction_N']
        support.setdefault(load['vehicle_mass_case'],{})[load['name']]=[dict(interior_vertical_N=(span_mass+spec['bearing_mass_kg_per_span'][i])*civil.G+live,ground_capacity_verified=False) for i in range(3)]
    for i,k in enumerate(CASES):
        mass=spec['bearing_mass_kg_per_span'][i]; wage=a['benchmark_rates_iqd']['wage_skilled_iqd_per_h']*x['wage_burden_multipliers'][i]*(1+x['second_shift_wage_premium'][i]/2)
        finished=mass*x['finished_equipment_iqd_per_kg'][i];qa=mass*spec['bearing_qa_hours_per_kg'][i]*wage;over=(finished+qa)*x['factory_overhead_fraction'][i]
        transport=mass/1000*50*cost.topology_cost.default_spec()['transport_iqd_per_tonne_km'][i]
        install=spec['bearing_install_hours_per_span'][i]*wage
        # Installation is a named share of already-costed field hours, never added twice.
        coating_direct=surface*(spec['sealer_material_iqd_per_m2'][i]+(spec['sealer_application_hours_per_m2'][i]+spec['sealer_qa_hours_per_m2'][i])*wage) if sealer else 0.
        coating_factory=coating_direct*(1+x['factory_overhead_fraction'][i]);bearing_factory=finished+qa+over
        initial_guide=n*(bearing_factory+coating_factory);initial_construction=n*transport
        scopes['guideway'][i]+=initial_guide;scopes['construction'][i]+=initial_construction
        duty=a['operating_hours_per_day_cases'][i]/a['maintenance_reference_operating_hours_per_day']
        scopes['maintenance'][i]+=initial_guide*x['maintenance_fraction_per_year'][i]*duty*annuity
        parent=[e['year'] for e in group['cases'][i]['events']]
        # Parent guideway replacement includes the factory portion of the added assets.
        parent_extra=fsum(initial_guide/(1+rate)**y for y in parent)
        replacement_bearing=bearing_factory+transport+install+spec['renewal_access_iqd_per_span'][i]
        bearing_events=_events(years,cost.topology_cost.default_spec()['bearing_renewal_years'][i],parent,replacement_bearing,n,rate)
        coat_events=_events(years,spec['sealer_renewal_years'][i],parent,coating_factory+spec['renewal_access_iqd_per_span'][i],n,rate) if sealer else None
        explicit=bearing_events['present_value_iqd']+(coat_events['present_value_iqd'] if coat_events else 0.)
        scopes['renewals'][i]+=parent_extra+explicit
        capex=old['model_based_installed_CAPEX_iqd'][i]+initial_guide+initial_construction
        scopes['disposal'][i]+=(initial_guide+initial_construction)*x['decommissioning_fraction_of_installed_CAPEX'][i]/(1+rate)**years
        rows.append(dict(case=k,bearing_count=4,mass_kg_per_span=mass,steel_mass_kg_per_span=mass*.7,elastomer_mass_kg_per_span=mass*.3,finished_iqd=finished,qa_iqd=qa,overhead_iqd=over,transport_iqd=transport,
            installation_hours_partitioned=spec['bearing_install_hours_per_span'][i],installation_iqd_in_existing_erection=install,
            incremental_installation_if_not_included_iqd=n*install*(1+x['construction_contingency_fraction'][i]),
            sealer_factory_iqd=coating_factory,bearing_events=bearing_events,sealer_events=coat_events,parent_added_factory_npv_iqd=parent_extra,
            explicit_component_renewal_npv_iqd=explicit,installed_capex_iqd=capex))
    return dict(scope_totals_iqd=scopes,rows=rows,support=support,concrete_m3_per_span=concrete/n,
        coating_outer_longitudinal_area_m2_per_span=surface,coating_scope='Outer longitudinal faces only; ends, interior, access exclusions and interfaces unresolved',
        bearing_material=dict(hypothesis='Steel-reinforced elastomeric pad assembly; type, details and suitability unverified',steel_mass_fraction=.7,elastomer_mass_fraction=.3,pricing='Finished assembly allowance includes constituent materials once; no separate raw-material charge'),
        foundation='Unchanged canonical foundation/site proxy; bearing selfweight shown in support demand but not re-sized, soil capacity and pier selfweight unknown')


def _flanged(record, original_detail, baseline, spec, mass_case):
    c=record['cases'][mass_case];scopes=_scope_sums(c); a=baseline['assumptions'];x=a['assumptions'];n=c['corridor_basis']['span_count']
    old_extra=_line(c['cost_line_items'],'flanged-coating-and-bearing-renewals')
    normalized=record['normalized_span_cost']['cases'];parent_group=next(g for g in c['renewal_plan']['asset_groups'] if g['asset_group']=='guideway')
    masses=original_detail['cost']['assumptions']['reserve_mass_kg']['bearings']
    years=a['design_life_years'];rate=a['real_discount_rate']; rows=[]
    for i,k in enumerate(CASES):
        row=normalized[i];wage=row['shared_loaded_wage_iqd_per_h'];mass=masses[i]
        if mass<=0:raise ValueError('Positive candidate-specific bearing mass required')
        # Coating consumables and productive hours are the actual candidate route
        # at normalized benchmark prices. Access and QA are explicit new bounds.
        coating_material=row['factory_items_iqd']['coating_consumables'];coating_labour=row['added_coating_person_hours']*wage
        surface=original_detail['cost']['manufacturing_stock']['steel_coating_m2']
        coating_qa=surface*spec['sealer_qa_hours_per_m2'][i]*wage
        coating_factory=(coating_material+coating_labour+coating_qa)*(1+x['factory_overhead_fraction'][i])
        bearing_qa=mass*cost.reserve_process_spec()['finished_equipment_qa_person_hours_per_kg'][i]*wage
        bearing_factory=(row['reserve_cost_iqd']['bearings']+bearing_qa)*(1+x['factory_overhead_fraction'][i])
        transport=mass/1000*row['transport_distance_km']*row['transport_iqd_per_tonne_km']
        bearing_install=spec['bearing_install_hours_per_span'][i]*wage
        parent=[e['year'] for e in parent_group['cases'][i]['events']]
        coating_events=_events(years,row['coating_renewal_years'],parent,coating_factory+spec['renewal_access_iqd_per_span'][i],n,rate)
        bearing_events=_events(years,row['bearing_renewal_years'],parent,bearing_factory+transport+bearing_install+spec['renewal_access_iqd_per_span'][i],n,rate)
        new=coating_events['present_value_iqd']+bearing_events['present_value_iqd']
        scopes['renewals'][i]+=new-old_extra['scenario_iqd'][k]
        rows.append(dict(case=k,installed_capex_iqd=c['model_based_installed_CAPEX_iqd'][i],
            bearing_mass_kg_per_span=mass,bearing_factory_iqd=bearing_factory,bearing_transport_iqd=transport,
            bearing_installation_iqd=bearing_install,coating_material_iqd=coating_material,
            coating_actual_route_labour_iqd=coating_labour,coating_added_qa_iqd=coating_qa,
            coating_factory_iqd=coating_factory,coating_events=coating_events,bearing_events=bearing_events,
            removed_legacy_component_npv_iqd=old_extra['scenario_iqd'][k],explicit_component_renewal_npv_iqd=new))
    return dict(scope_totals_iqd=scopes,rows=rows,support=deepcopy(record['support_demands']['cases'][mass_case]),
        initial_steel_coating='Retains candidate-specific normalized factory route and initial price from the published cost record',
        foundation='Unchanged candidate foundation/site proxy; loads are not repriced and soil capacity is unknown')


def _scenario_totals(item,spec):
    scopes=item['scope_totals_iqd']; totals=[]
    for i in range(3):
        total=fsum(v[i] for v in scopes.values());explicit=item['rows'][i]['explicit_component_renewal_npv_iqd']
        overlap=min(scopes['maintenance'][i],spec['maintenance_overlap_fraction'][1]*explicit)
        totals.append(dict(base_npv_iqd=total,overlap_sensitivity_npv_iqd=total-overlap,
            overlap_removed_iqd=overlap,overlap_basis='Illustrative fraction of explicit component renewal PV potentially already embedded in routine-maintenance proxy; not measured'))
    return totals


def compare(publication_folder, *, root, expected_publication_manifest_id,
            expected_topology_manifest_id, expected_flanged_manifest_id, scenario_assumptions=None):
    """Compare all 3 spans with unsealed and externally sealed concrete scenarios.

    Each parent ID must be supplied from an independent trust source. Reads the
    authenticated original cost ledger; does not run native structural solvers.
    """
    root=Path(root).resolve();folder=Path(publication_folder).resolve();producer=digest(Path(__file__))
    if not (root/PRODUCER).is_file() or digest(root/PRODUCER)!=producer:raise ValueError('Executing comparator source epoch differs from declared root')
    spec=_assumptions(scenario_assumptions)
    raw,publication_record=_parents(folder,root,expected_topology_manifest_id,expected_flanged_manifest_id,expected_publication_manifest_id)
    baseline=publication._gzip_json(raw['baseline.json.gz']);a=baseline['assumptions'];context=baseline['load_context']
    if (a['production_shifts_per_day'],a['production_hours_per_shift'],a['civil_shifts_per_day'],a['civil_hours_per_shift'])!=(2,8,2,8):
        raise ValueError('Two 8-hour production and civil shifts required')
    if a['operations_shifts_per_day_cases']!=[2,2,3] or a['operating_hours_per_day_cases']!=[16,18,24]:
        raise ValueError('Recorded 2–3 shift operating assumptions required')
    if any(baseline['cases'][k]['cost']['corridor_basis']!=baseline['cases']['base']['cost']['corridor_basis'] for k in CASES):
        raise ValueError('Mixed corridor')
    original_context=publication._json(raw[publication.NAMES[0]+'/original-request.json'])['context']
    fields=('vehicle_candidate_id','vehicle_evaluation_id','selection_id','body_candidate_id',
            'support_component_id','propulsion_component_id','selected_context_id','mass_reserve_result_id','dynamic_factor_applied_once')
    load_fields=('name','vehicle_mass_case','tare_kg_per_car','loaded_kg_per_car','full_axle_force_N','offsets_m')
    if (original_context['context_id']!=publication_record['load_context_id']
            or any(original_context[k]!=context[k] for k in fields)
            or [{k:r[k] for k in load_fields} for r in original_context['cases']]!=[{k:r[k] for k in load_fields} for r in context['cases']]):
        raise ValueError('Published and baseline selected vehicle, identity or load cases differ')
    civil_id=baseline['cases']['base']['civil_design_basis']['physical_civil_component_id']
    references={}
    for seal_name,sealed in [('unsealed',False),('outer_sealer',True)]:
        physical=dict(schema='osr-concrete-bearing-reference-composition/1',baseline_id=baseline['baseline_id'],
            civil_candidate_id=civil_id,vehicle_candidate_id=context['vehicle_candidate_id'],
            bearing_reserve=dict(count_per_span=4,mass_kg_per_span=spec['bearing_mass_kg_per_span'],steel_mass_fraction=.7,elastomer_mass_fraction=.3),surface_treatment=seal_name)
        references[seal_name]=dict(candidate_id=identity(physical),physical_definition=physical,
            mass_cases={m:_reference(baseline['cases'][m],baseline,context,spec,sealed,sealer=sealed) for m in CASES})
    comparisons={}
    for name in publication.NAMES:
        record=publication._gzip_json(raw[name+'/result.json.gz']);detail=publication._json(raw[name+'/original-result.json'])
        if record['baseline_id']!=baseline['baseline_id'] or record['load_context_id']!=publication_record['load_context_id']:
            raise ValueError('Candidate ancestry mismatch')
        output=dict(candidate_id=record['candidate_id'],physical_civil_candidate_id=publication._json(raw[name+'/original-request.json'])['candidate']['candidate_id'],
            source_evaluation_id=record['evaluation_id'],mass_cases={})
        for mass in CASES:
            f=_flanged(record,detail,baseline,spec,mass);f['totals']=_scenario_totals(f,spec);compare_ref={}
            for name_ref in references:
                ref=references[name_ref]['mass_cases'][mass];totals=_scenario_totals(ref,spec)
                compare_ref[name_ref]=dict(reference_candidate_id=references[name_ref]['candidate_id'],
                    capex_delta_iqd=[f['rows'][i]['installed_capex_iqd']-ref['rows'][i]['installed_capex_iqd'] for i in range(3)],
                    npv_delta_iqd=[f['totals'][i]['base_npv_iqd']-totals[i]['base_npv_iqd'] for i in range(3)],
                    overlap_sensitivity_delta_iqd=[f['totals'][i]['overlap_sensitivity_npv_iqd']-totals[i]['overlap_sensitivity_npv_iqd'] for i in range(3)],
                    reference_bearing_installation_if_additive_iqd=[r['incremental_installation_if_not_included_iqd'] for r in ref['rows']])
            output['mass_cases'][mass]=dict(flanged=f,reference_deltas=compare_ref)
        comparisons[name]=output;del record;gc.collect()
    value=dict(schema='osr-matched-renewal-research/1',baseline_id=baseline['baseline_id'],
        parent_publication_manifest_id=expected_publication_manifest_id,topology_manifest_id=expected_topology_manifest_id,
        flanged_span_manifest_id=expected_flanged_manifest_id,baseline_load_context_id=context['context_id'],load_context_id=publication_record['load_context_id'],
        selected_vehicle_candidate_id=context['vehicle_candidate_id'],corridor=deepcopy(baseline['cases']['base']['cost']['corridor_basis']),
        cost_assumption_id=a['assumption_id'],assumptions=spec,reference_compositions=references,comparisons=comparisons,
        source_sha256={**publication_record['source_sha256'],PRODUCER:producer},
        estimate_class='C',currency='IQD',conditional_scenario_deltas_only=True,whole_life_ranking_allowed=False,
        integrated_selection=None,installed_mass_complete=False,physical_accepted=False,engineering_accepted=False,
        manufacturing_release=False,operating_release=False,physical_journey_completed=False,service_qualified=False,selected_reference_changed=False,
        holds=['No geotechnical investigation, bearing type/material suitability, finite-bearing demand or independent approval',
            'The four-bearing reserve is a cost/mass scenario; support layout and bearing reactions are unverified',
            'No resolved structural stress, prestress transfer, torsion, fatigue, temporary stability, crane radius or magnetic-gap deformation',
            'Unchanged foundation proxy is not load-dependent; support selfweights and soil capacity remain unknown',
            'Routine maintenance excludes capital component renewals by assumption; overlap sensitivity is illustrative',
            'Parent-asset replacement prices cover factory assets only; replacement logistics and access during parent renewal remain uncertain',
            'Sealer applies only to outer longitudinal concrete faces; actual treatment needs, ends, interior and access remain unknown',
            'Steel coating maintenance uses candidate route with hypothetical access and QA, not measured costs or service life'])
    if digest(Path(__file__))!=producer or digest(root/PRODUCER)!=producer:raise ValueError('Comparator source changed during calculation')
    cost.base._source_check(publication_record['source_sha256'],root)
    publication._check(folder,expected_publication_manifest_id)
    value['evaluation_id']=identity(value)
    return value
