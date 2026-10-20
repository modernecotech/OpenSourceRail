"""Bounded cost/quantity research and elevated route objectives; no engineering release.

Cost coefficients are indexed from the supplied workbook, not invented supplier
quotes. Required equipment, payload, reserve, magnetic mass and storage remain
visible. A smaller mass allocation does not itself earn a procurement saving.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import itertools
import json
import math
from pathlib import Path
import tomllib

from . import model

INPUT=Path(__file__).with_suffix('.toml')
REFERENCES=[
    dict(url='https://www.transit.dot.gov/sites/fta.dot.gov/files/2025-01/Project-and-Construction-Management-Guidelines-January-2025.pdf',
         scope='Aerial guideways: ROW, adjacent buildings, station access, utilities and environmental effects still require assessment; no OSR cost validation'),
    dict(url='https://www.fhwa.dot.gov/bridge/prefab/index.cfm',scope='Offsite components and rapid installation can reduce construction disruption; no railway acceptance or cost validation'),
    dict(url='https://www.fhwa.dot.gov/bridge/prefab/framework.cfm',scope='Connections, component size, erection equipment, local capability and whole-project cost govern prefabrication feasibility'),
]
ROUTE_EVIDENCE=('housing-footprints-height-and-air-rights','road-clearance-and-pier-placement',
                'utilities-and-foundation-investigation','wildlife-habitat-passage-and-water',
                'station-access-egress-and-rescue','construction-access-temporary-works-and-consents')
MASS_KEYS={'structure_ratio':'structural_body_floor_doors_glazing_interior',
           'magnetic_equipment_ratio':'cores_all_windings_carriers_drives_local_sensors_cooling',
           'hvac_ratio':'cabin_hvac_ducting','auxiliary_ratio':'auxiliary_electrical_train_controls_wiring'}


def load():
    a=tomllib.loads(INPUT.read_text())
    if a['schema']!={'version':1,'family':'ferrite-pm-maglev-study'}:raise ValueError('controlled optimisation schema required')
    if any(a['accounting'].get(k) is not False for k in ('costs_are_quotes','design_complete','manufacturing_release')):
        raise ValueError('optimisation targets are unqualified')
    route=a['route']
    fraction=route['target_elevated_mainline_fraction']
    if type(fraction) not in (int,float) or not .95<=fraction<=1:raise ValueError('predominantly elevated target must be in[0.95,1]')
    if route['zero_impact_demonstrated'] is not False:raise ValueError('no zero-impact evidence adapter supplied')
    if route['prefer_all_ordinary_mainline_elevated'] is not True or route['retain_ring_and_terminal_curve_requirements'] is not True:
        raise ValueError('controlled elevated scenario and curved topology exceptions required')
    b=a['civil']
    for name in ('widths_m','depths_m','webs_m','flanges_m','spans_m'):
        if not isinstance(b[name],list) or not 1<=len(b[name])<=8:raise ValueError('bounded search grid required')
        for value in b[name]:model.positive(value,name)
    if math.prod(len(b[k]) for k in ('widths_m','depths_m','webs_m','flanges_m','spans_m'))>512:raise ValueError('civil search budget exceeded')
    for name in ('gross_deflection_span_divisor_screen','maximum_bare_beam_lift_mass_screen_kg','reference_concrete_density_kg_m3','reference_walkway_concrete_area_m2_per_direction'):
        model.positive(b[name],name)
    if not 0<=b['transport_cost_variable_fraction']<=1:raise ValueError('transport variable fraction outside[0,1]')
    if set(b['unchanged_cost_rows'])!={'passive_rail_supply','walkway_brackets','temporary','installation','night','qa','relocation','traffic'}:
        raise ValueError('required unchanged scope rows differ')
    profiles=a['vehicle_profiles']
    if not 1<=len(profiles)<=8 or len({p['id'] for p in profiles})!=len(profiles):raise ValueError('bounded unique vehicle profiles required')
    for p in profiles:
        for key in MASS_KEYS:
            if type(p[key]) not in (int,float) or not .5<=p[key]<=1:raise ValueError('bounded positive mass ratios required')
        if type(p['unqualified_change_count']) is not int or p['unqualified_change_count']<0:raise ValueError('nonnegative change count required')
        if p['hardware_target']!='retain-workbook':model.positive(p['hardware_target'],'hardware target')
    return a


def vehicle(c,costs,p):
    target=deepcopy(c);changes={}
    for ratio,key in MASS_KEYS.items():
        original=c['mass'][key];value=original*p[ratio];target['mass'][key]=value
        changes[key]=dict(reference_kg=original,target_kg=value,qualified=False)
    saved=sum(v['reference_kg']-v['target_kg'] for v in changes.values())
    target['mass']['base_tare_target_150kwh_3t_ferrite']-=saved
    target['mass']['matched_tare_target_225kwh_3t_ferrite']-=saved
    m=model.mass(target,c['mass']['ferrite_base'],c['power']['gross_battery_matched_kwh_per_car'])
    hardware=None if p['hardware_target']=='retain-workbook' else p['hardware_target']
    cost=model.cost_case(c,costs,'base',c['mass']['ferrite_base'],c['power']['gross_battery_matched_kwh_per_car'],hardware_target=hardware)
    duty=model.cycle(target,m['aw3_kg'],hot=True,regen=False)
    return target,dict(id=p['id'],mass=m,mass_allocation_changes=changes,assumed_mass_saving_kg=saved,
        repeat_three_car_train_allowance_usd=cost['train_usd'],hardware_target_usd_train=hardware,
        unqualified_change_count=p['unqualified_change_count'],
        fixed_allocations_kg={k:c['mass'][k] for k in ('ferrite_base','capture_landing_emergency_braking','battery_150kwh_installed','growth_reserve')},
        gross_storage_kwh_per_car=c['power']['gross_battery_matched_kwh_per_car'],
        aw2_passengers_per_car=c['vehicle']['aw2_passengers_per_car'],aw3_passengers_per_car=c['vehicle']['aw3_passengers_per_car'],
        removed_wheel_gear_credit_usd_train=cost['removed_direct_usd_train'],
        required_systems_retained=['passenger doors','HVAC fans/pumps as required','support drives/sensing/cooling',
            'capture/landing/emergency braking','battery protection','independent protection','couplers/gangways','evacuation'],
        normal_running_gear_moving_parts_objective=0,total_moving_parts_count=None,
        matched_duty=dict(hot_aw3_no_regen_cycle_kwh_per_car=duty['cycle_kwh'],
            balanced_charger_kw_per_car=duty['balanced_charger_kw'],
            station_spacing_m=target['power']['station_spacing_study_m'],
            requested_speed_kmh=duty['requested_speed_kmh'],achieved_speed_kmh=duty['achieved_speed_kmh'],
            scope='Same straight/level cycle, payload, storage, hotel load, assumed drag and efficiencies. Actual magnetic force/loss, terrain, wind and charger acceptance remain open.',
            actual_magnetic_loss_map_used=False,route_accepted=False),
        imported_input_usd=None,local_value_added_fraction=None,
        limits='Mass allocations and hardware budgets are targets. No extra body/equipment procurement credit, efficiency gain or import saving inferred.',**model.FLAGS)


def civil(c,costs,v,width,depth,web,flange,span,a,*,guideway_mode='walkway-reference'):
    if guideway_mode not in {'walkway-reference','onboard-evacuation-no-walkway'}:raise ValueError('unknown guideway mode')
    beam_only=guideway_mode=='onboard-evacuation-no-walkway'
    target=deepcopy(c);box=target['civil']['narrow_box_screen'];box['web_thickness_m']=web;box['flange_thickness_m']=flange
    from . import geometry
    native_rail_line_mass=sum(geometry.volume(p)*geometry.MATERIALS[p['material']]
        for p in geometry.beam_parts('quantity-screen',25) if p['role']=='magnetic-rail')/25
    # The exported wide lift faces are heavier than the old 100 kg/m allowance.
    # Never buy a lighter beam by quietly undercounting retained rail material.
    box['magnetic_hardware_line_mass_screen_kg_m_per_direction']=max(
        box['magnetic_hardware_line_mass_screen_kg_m_per_direction'],native_rail_line_mass)
    walkway_area=0 if beam_only else a['civil']['reference_walkway_concrete_area_m2_per_direction']
    r=model.civil_case(target,width,depth,span,walkway_area_m2=walkway_area)
    r['web_m']=web;r['flange_m']=flange
    base=model.cost_case(c,costs,'base',c['mass']['ferrite_base'],c['power']['gross_battery_matched_kwh_per_car'])
    rows=deepcopy(base['civil_rows_usd_dual_km']);b=a['civil']
    volume=(r['area_m2']+walkway_area)*2000
    refvolume=c['civil']['narrow_box_screen']['candidate_listed_concrete_m3_per_dual_route_km']
    reference_lift=c['civil']['narrow_box_screen']['derived_concrete_area_m2']*c['civil']['reference_span_m']*b['reference_concrete_density_kg_m3']
    piers=1000/span;reference_piers=1000/c['civil']['reference_span_m']
    lift_mass=r['area_m2']*span*b['reference_concrete_density_kg_m3']
    ratio=volume/refvolume;lift_ratio=lift_mass/reference_lift;support_ratio=piers/reference_piers
    rows['structural_supply']*=ratio
    # No foundation shrink credit: same assumed support-unit price, varied count.
    rows['supports']*=support_ratio
    variable=b['transport_cost_variable_fraction'];rows['transport']*=1-variable+variable*ratio
    # Longer/heavier spans reduce lift count but increase a transparent handling allowance.
    rows['erection']*=support_ratio*max(1,lift_ratio)
    if beam_only:rows['walkway_brackets']=0
    if set(b['unchanged_cost_rows'])!={'passive_rail_supply','walkway_brackets','temporary','installation','night','qa','relocation','traffic'}:
        raise ValueError('required unchanged scope rows differ')
    reference=base['civil_rows_usd_dual_km']
    for key in b['unchanged_cost_rows']:
        if rows[key]!=reference[key] and not (beam_only and key=='walkway_brackets'):
            raise ValueError('unqualified fixed-scope credit: '+key)
    stiffness=r['total_elastic_deflection_m']<=span/b['gross_deflection_span_divisor_screen']
    lifting=lift_mass<=b['maximum_bare_beam_lift_mass_screen_kg']
    return dict(section=r,concrete_m3_dual_km=volume,counted_concrete_mass_kg_dual_km=volume*b['reference_concrete_density_kg_m3'],
        guideway_mode=guideway_mode,evacuation_state='hold; alternative evacuation unproved' if beam_only else 'reference study; acceptance open',
        eligible_for_reference_research_champion=not beam_only,walkway_removal_approved=False,
        new_onboard_evacuation_mass_kg_per_car=None if beam_only else 0,
        new_onboard_evacuation_lifetime_cost_usd=None if beam_only else 0,
        net_whole_system_saving_usd=None,
        native_passive_rail_line_mass_kg_m_per_direction=native_rail_line_mass,other_attachment_mass_closed=False,
        total_installed_mass_kg_dual_km=None,shared_supports_per_route_km=piers,beam_lifts_per_route_km=2*piers,
        maximum_bare_beam_lift_kg=lift_mass,crane_capacity_at_radius_verified=False,
        indexed_rows_usd_dual_km=rows,indexed_allowance_usd_dual_km=sum(rows.values()),
        stiffness_screen_pass=stiffness,bare_lift_mass_screen_pass=lifting,numerical_screen_pass=stiffness and lifting,
        quantity_ratios=dict(structural_volume=ratio,support_count=support_ratio,maximum_bare_lift=lift_ratio),
        qualifications_open=['strength/prestress/rebar/cracking/thin-wall cover and fabrication','torsion/wind/seismic','local magnetic loads and real rail',
          'dynamic relative gap/settlement/joints/thermal','foundation and ROW','lift rigging/crane radius/ground',
          'erection stages/connections/curing','maintenance/egress/QA','actual unit rates/yield/tooling/origins'],
        scope='Ordinary twin-direction viaduct indexed allowance; support count may vary but support capacity/site feasibility is unproved.',**model.FLAGS)


def scorecard(v,civil):
    """Candidate-specific arithmetic and explicit missing whole-system measures."""
    held=civil['guideway_mode']=='onboard-evacuation-no-walkway'
    return dict(
        installed_cost_usd_dual_route_km=None,
        indexed_ordinary_viaduct_allowance_usd_dual_route_km=civil['indexed_allowance_usd_dual_km'],
        factory_gate_cost_usd_three_car_train=None,
        indexed_repeat_three_car_train_allowance_usd=v['repeat_three_car_train_allowance_usd'],
        tare_kg_per_car=v['mass']['tare_kg'],aw2_kg_per_car=v['mass']['aw2_kg'],aw3_kg_per_car=v['mass']['aw3_kg'],
        hot_aw3_no_regen_cycle_kwh_per_car=None if held else v['matched_duty']['hot_aw3_no_regen_cycle_kwh_per_car'],
        balanced_charger_kw_per_car=None if held else v['matched_duty']['balanced_charger_kw_per_car'],
        maximum_bare_beam_lift_kg=civil['maximum_bare_beam_lift_kg'],maximum_transported_assembly_mass_kg=None,
        counted_concrete_mass_kg_dual_route_km=civil['counted_concrete_mass_kg_dual_km'],total_installed_mass_kg_dual_route_km=None,
        factory_labour_hours_per_route_km=None,onsite_labour_hours_per_route_km=None,
        construction_working_days_per_route_km=None,unique_parts_count=None,moving_assemblies_count=None,
        imported_value_usd=None,specialist_supplier_dependency_count=None,
        module_replacement_time_seconds=None,failed_train_recovery_time_seconds=None,
        additional_onboard_evacuation_mass_required_but_unknown=held,
        evidence_scope='Input-bound analytical screens and indexed allowances; null means unmeasured/unpriced. Tare/load allocations exclude unselected additional chute equipment. No supplier quotation, factory routing, complete installed mass or physical performance verified.',
        accepted=False,**model.FLAGS)


def _vector(r):
    return (r['civil']['indexed_allowance_usd_dual_km'],r['civil']['counted_concrete_mass_kg_dual_km'],
            r['civil']['maximum_bare_beam_lift_kg'],r['vehicle']['mass']['tare_kg'],r['vehicle']['repeat_three_car_train_allowance_usd'],
            r['vehicle']['unqualified_change_count'])


@lru_cache(maxsize=4)
def _study(canonical):
    c,costs,a=json.loads(canonical);rows=[];profiles=[];beam_only_rows=[]
    b=a['civil'];axes=[b[k] for k in ('widths_m','depths_m','webs_m','flanges_m','spans_m')]
    for p in a['vehicle_profiles']:
        target,v=vehicle(c,costs,p);profiles.append(v)
        for width,depth,web,flange,span in itertools.product(*axes):
            try:r=civil(target,costs,v,width,depth,web,flange,span,a)
            except ValueError:continue
            key=f"{p['id']}/{width:g}/{depth:g}/{web:g}/{flange:g}/{span:g}"
            rows.append(dict(id=key,vehicle=v,civil=r,system_scorecard=scorecard(v,r),numerical_screen_pass=r['numerical_screen_pass'],accepted=False))
            bare=civil(target,costs,v,width,depth,web,flange,span,a,guideway_mode='onboard-evacuation-no-walkway')
            beam_only_rows.append(dict(id='onboard-evacuation-no-walkway/'+key,vehicle=v,civil=bare,system_scorecard=scorecard(v,bare),
                numerical_screen_pass=bare['numerical_screen_pass'],accepted=False,
                gross_avoided_scope_usd_dual_km=r['indexed_allowance_usd_dual_km']-bare['indexed_allowance_usd_dual_km'],
                added_vehicle_equipment_mass_and_lifetime_cost_closed=False))
    passing=[r for r in rows if r['numerical_screen_pass']];vectors={r['id']:_vector(r) for r in passing}
    pareto=[]
    for r in passing:
        vector=vectors[r['id']]
        if not any(all(x<=y for x,y in zip(other,vector)) and any(x<y for x,y in zip(other,vector))
                   for identity,other in vectors.items() if identity!=r['id']):pareto.append(r['id'])
    best=min(passing,key=lambda r:(r['civil']['indexed_allowance_usd_dual_km'],r['id'])) if passing else None
    base=model.cost_case(c,costs,'base',c['mass']['ferrite_base'],c['power']['gross_battery_matched_kwh_per_car'])
    lightest=min(passing,key=lambda r:(r['civil']['counted_concrete_mass_kg_dual_km'],r['id'])) if passing else None
    extrema=dict(lowest_indexed_ordinary_allowance_candidate_id=best['id'] if best else None,
        lowest_counted_concrete_mass_candidate_id=lightest['id'] if lightest else None,
        fastest_construction_candidate_id=None,
        scope='Reference configurations passing gross stiffness/bare-lift screens only. Whole installed cost/mass and construction time not established; held no-walkway variants excluded.',
        construction_time_hold='No maglev-specific production/erection resource schedule, productivity or curing/connection evidence; legacy wheel/rail schedule winners cannot transfer.')
    fixed=sum(base['civil_rows_usd_dual_km'][k] for k in b['unchanged_cost_rows'])
    eligible_bare=[r for r in beam_only_rows if r['numerical_screen_pass']]
    bare_best=min(eligible_bare,key=lambda r:(r['civil']['indexed_allowance_usd_dual_km'],r['id'])) if eligible_bare else None
    return dict(schema='osr-maglev-whole-system-optimisation/1',candidate_count=len(rows),numerical_screen_pass_count=len(passing),
        research_extrema=extrema,fully_coupled_optimisation=False,
        coupling_evidence=[
            dict(link='vehicle mass to AW3 UDL/beam deflection',state='implemented analytical screen'),
            dict(link='section/span to support count and indexed transport/erection allowance',state='implemented quantity indexing; capacity unproved'),
            dict(link='vehicle mass to hot no-regen duty/charging',state='implemented fixed-assumption straight/level screen'),
            dict(link='actual magnetic force/loss to structural gap/support and energy',state='open; no qualified force/loss map'),
            dict(link='beam/support changes to actuator spacing/control authority',state='open; no candidate-specific coupled replay'),
            dict(link='manufacturing/erection schedule, local/import MBOM and lifecycle repair',state='open; supplier/process/site evidence required')],
        pareto_candidate_ids=pareto,minimum_indexed_allowance_candidate=best,vehicle_profiles=profiles,candidates=rows,
        beam_only_candidate_count=len(beam_only_rows),beam_only_candidates=beam_only_rows,
        beam_only_minimum_gross_allowance_candidate=bare_best,
        beam_only_reference_champion_eligible=False,beam_only_net_system_saving_usd=None,
        beam_only_selection_hold='No safe landing/accessibility/fire/fault/route/supplier acceptance; additional onboard mass, cost, inspection and replacement unknown. Gross avoidance is not a net saving.',
        reference_ordinary_viaduct_usd_dual_km=base['civil_usd_dual_km'],unchanged_scope_floor_usd_dual_km=fixed,
        acceptance_eligible_candidate_count=0,local_value_added_fraction=None,
        objective_units=['USD/dual-route-km','counted concrete kg/dual-route-km','maximum bare lift kg','tare kg/car','USD/three-car train','unqualified vehicle target changes'],
        coupling='Equal passenger capacity, storage, reserve and ferrite allocation; candidate tare changes AW3 load in civil stiffness screens.',
        cost_method='Workbook-indexed structural volume, support count, transport mass and lift count/weight. Unchanged scope floor retained; no automatic soil, QA, rail, utility, traffic, energy or maintenance savings.',
        claims='Research ordering only. Gross uncracked deflection and bare lifting mass filters do not qualify strength, relative gap, fabrication, installation or route feasibility. Analytical alternatives are not the retained native CAD or coupled replay configuration.',
        exclusions=['stations/access/lifts','special crossings','land/air rights','loop structures','depot','power/charging',
                    'survey and engineering qualification','plant/NRE/EPC','financing/tax/escalation','actual renewal/OPEX'],
        references=REFERENCES,**model.FLAGS)


def study(c=None,costs=None):
    if c is None or costs is None:_,c,costs=model.load()
    from . import evacuation
    a=load();evacuation.load()
    a['evacuation_input_sha256']=sha256(evacuation.INPUT.read_bytes()).hexdigest()
    return _study(json.dumps([c,costs,a],sort_keys=True,allow_nan=False))


def route_strategy(design,corridor,a=None):
    a=a or load();by_class={}
    for segment in design['civil_segments']:
        length=segment['to_station_m']-segment['from_station_m']
        if not math.isfinite(length) or length<0:raise ValueError('invalid retained civil length')
        key=segment['class'];by_class[key]=by_class.get(key,0)+length
    ordinary=by_class.get('elevated',0)+by_class.get('at-grade',0)
    special={k:v for k,v in by_class.items() if k not in {'elevated','at-grade'}}
    route=sum(l['length_m'] for l in design['lines']);discrepancy=sum(by_class.values())-route
    straightness=[];alignment_metrics=[]
    for line in corridor.get('lines',[]):
        cells=line.get('cells',[])
        shape=str(line.get('shape','')).lower()
        if len(cells)<2:
            alignment_metrics.append(dict(line=line.get('name'),shape=shape,path_to_endpoint_chord_ratio=None,reason='fewer than two retained raster points'))
            continue
        length=sum(math.dist(p,q) for p,q in zip(cells,cells[1:]));chord=math.dist(cells[0],cells[-1])
        alignment_metrics.append(dict(line=line['name'],shape=shape,
            raster_cell_path_length=length,raster_cell_endpoint_chord=chord,
            path_to_endpoint_chord_ratio=length/chord if shape=='radial' and chord>0 else None,
            directness_state='raster-observation' if shape=='radial' and chord>0 else 'not-applicable-to-ring-or-zero-chord',
            standard_straight_span_fraction=None,minimum_horizontal_radius_m=None,minimum_vertical_radius_m=None,
            affected_buildings_count=None,affected_utilities_count=None,station_walking_catchment_population=None,
            interchange_access_accepted=False,
            basis='Retained cell-centre polyline and first/last endpoints; no smoothing, vertical profile, standard-span classification or obstacle survey. Other shapes require named corridor endpoints.'))
        if shape!='radial':continue
        straightness.append(dict(line=line['name'],raster_chord_to_path_ratio=chord/length if length else None,
            basis='Retained raster cell-centre geometry; no 3D obstacle/ROW/clearance or rerouting proof'))
    return dict(strategy='predominantly-elevated; maximise feasible straight tangents between demand anchors',
        target_elevated_mainline_fraction=a['route']['target_elevated_mainline_fraction'],
        ordinary_mainline_proposal='all ordinary sections elevated; final fractions subject to route/site validation',
        retained_civil_class_length_m=by_class,ordinary_viaduct_proposal_length_m=ordinary,
        proposed_conversion_from_at_grade_m=by_class.get('at-grade',0),special_crossings_length_m=special,
        civil_coverage_discrepancy_m=discrepancy,civil_quantity_screen_pass=abs(discrepancy)<=1,
        alignment_comparison_metrics=alignment_metrics,
        radial_straightness_observations=straightness,geographic_alignment_recomputed=False,
        elevated_coverage_achieved=None,operating_level_crossings_demonstrated=None,housing_demolition_demonstrated=None,
        wildlife_impact_demonstrated=None,zero_impact_demonstrated=False,
        required_evidence=[dict(id=k,state='unknown',accepted=False) for k in ROUTE_EVIDENCE],
        fixed_topology_exceptions=['rings','terminal loops','station approaches','obstacle/river/airspace avoidance'],
        references=REFERENCES,**model.FLAGS)
