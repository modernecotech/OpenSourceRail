"""Bounded, read-only source replay and separate construction-hypothesis arithmetic."""
import hashlib
import json
import math
import copy
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(ROOT))
from engineering.development_baseline import selection
from engineering.design_search import line_benchmark, line_benchmark_civil
from engineering.station_rail import civil
from engineering.station_rail.common import identity

SOURCES = [
    'AGENTS.md',
    'campaigns/line30-affordable-benchmark.toml',
    'campaigns/whole-railway-architecture-search.toml',
    'engineering/design_search/line_benchmark.py',
    'engineering/design_search/line_benchmark_civil.py',
    'engineering/station_rail/civil.py',
    'engineering/development_baseline/selection.py',
    'engineering/pilot_civil/policy.json',
    'engineering/pilot_civil/assembly.py',
    'engineering/pilot_civil/design.py',
    'docs/design-engine/line30-benchmark/result.json',
    'build/v07-ethos/line30-current-20261117-a/result.json',
    'build/v07-ethos/line30-current-20261117-a/manifest.json',
]
source_sha256 = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCES}
commit = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
free_before = __import__('shutil').disk_usage(OUT).free
if free_before < 20 * 1024**3:
    raise RuntimeError('20 GiB disk free reserve unavailable before evaluation')

spec = line_benchmark.specification(ROOT)
fresh_line = json.loads((ROOT/'build/v07-ethos/line30-current-20261117-a/result.json').read_text())
vehicle = selection.load(ROOT)['vehicle']
base = line_benchmark_civil.evaluate(spec['requirements'],spec['design'],vehicle,ROOT)
assert fresh_line['evaluation_id'] == '947dd7cbcac7c260da721150912fba47531c96fd3f7a28365c394249608ee869'
assert fresh_line['civil']['evaluation_id'] == base['evaluation_id']
for epoch in (fresh_line['source_sha256'], base['source_sha256']):
    for name, want in epoch.items():
        if name in source_sha256 and source_sha256[name] != want:
            raise RuntimeError('Conflicting source epoch: '+name)
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != want:
            raise RuntimeError('Source drift: '+name)
        source_sha256[name] = want
load_vehicle = copy.deepcopy(vehicle)
added_kg = spec['design']['added_vehicle_mass_kg_per_car']
for field in ('accounted_tare_kg_per_car','accounted_cap_loaded_kg_per_car','accounted_160_control_kg_per_car'):
    load_vehicle['mass'][field] += added_kg
beam = civil.alternative(load_vehicle,20.0,'box-beam','crowd_control')
assert base['beam']['physical_civil_component_id'] == beam['physical_civil_component_id']
assert base['beam']['maximum_live_moment_Nm'] == beam['maximum_live_moment_Nm']
assert base['quantities']['span_count'] == 3000
assert base['quantities']['independent_supports'] == 3002
assert base['beam']['total_counted_span_mass_kg'] == beam['total_counted_span_mass_kg']

inp = {
    'schema':'osr-v07-civil-construction-input/1',
    'purpose':'next-experiment',
    'source_commit':commit,
    'source_sha256':source_sha256,
    'ancestry':{'fresh_line30_civil_evaluation_id':base['evaluation_id'],
                'fresh_line30_full_evaluation_id':fresh_line['evaluation_id'],
                'whole_beam_component_id':beam['physical_civil_component_id'],
                'vehicle_candidate_id':vehicle['candidate_id'],
                'published_line30_result_sha256':source_sha256['docs/design-engine/line30-benchmark/result.json'],
                'published_line30_status':'historical context; whole packet has stale noncivil dependencies'},
    'requirements':{'route_m':30000,'demonstrator_m':2000,'alternative_demonstrator_m':1500,'tracks':2,'stations':12,
                    'normal_places_per_hour_per_direction':8280,'span_m':20,
                    'mandatory_safety_access_loads_unrelaxed':True,
                    'added_vehicle_mass_kg_per_car_for_load':added_kg,
                    'crowd_control_load_case_retained':True},
    'physical_revision':{'beam_family':'box-beam','beam_section_component_id':beam['physical_civil_component_id'],
                         'pieces_per_span':2,'piece_length_m':10,
                         'joint':'match-cast keyed epoxy closure plus continuous post-tension proposal; 2 mm closure hypothesis',
                         'footing_family':'spread-footing','footing_width_m':3,'footing_length_m':3,
                         'footing_thickness_m':1.2,'pier_area_m2':0.8,'pier_height_m':8,
                         'independent_support_lines':2,'soil_allowable_kPa_hypothesis':200},
    'lifting_hypothesis':{'reference':'engineering/pilot_civil/policy.json',
                         'radius_m':12,'chart_capacity_kg_at_radius':60000,'road_payload_kg':35000,
                         'rigging_kg':1500,'hook_contingency_fraction':0.10},
    'construction_rate_hypotheses':{'source':'fresh line30 civil adapter',
                                   'beam_factory_person_h_per_span_base':64,
                                   'erection_person_h_per_span_base':64,
                                   'support_field_person_h_per_support_base':24,
                                   'baseline_whole_spans_per_crane_shift':2,
                                   'segmented_piece_lifts_per_shift_illustrative':2,
                                   'production_shifts_per_day':2,'hours_per_shift':8,
                                   'productive_utilisation':0.75,
                                   'precast_crew_per_cell':8,
                                   'production_years':3,'production_days_per_year':250,
                                   'mould_cycle_days_base':5},
}
inp['input_id'] = identity({k:v for k,v in inp.items() if k!='input_id'})
physical = dict(inp['physical_revision'])
physical.update(schema='osr-v07-civil-physical-candidate/1',
                track_centres_y_m=[-1.6,1.6],
                running_beams_per_route_span=2,
                bearing_sets_per_beam=4,
                temporary_midspan_tower_per_active_segmented_beam=True)
physical_id = identity(physical)

Q=base['quantities']
rate=base['process_assumptions']
soil=base['soil_gravity_necessary_bounds']
base_soil=next(s for s in soil if s['soil_kPa']==200)
footing_area=9.0
rho=2500.0
g=9.80665
thick=1.2
numerator=base_soil['gravity_closed_area_m2']*(200000-rho*g*thick)
pressure_kPa=(numerator/footing_area+rho*g*thick)/1000
bare_piece=Q['source_max_bare_piece_kg']
whole_hook=(bare_piece+1500)*1.10
piece_hook=(bare_piece/2+1500)*1.10

counts={}
for label,length in [('pilot_1p5km',1500),('demonstrator_2km',2000),('route',30000)]:
    spans_per_track=length//20
    beams=spans_per_track*2
    supports=(spans_per_track+1)*2
    pieces=beams*2
    counts[label]={
        'route_m':length,'track_m':length*2,'spans_per_track':spans_per_track,
        'beam_spans':beams,'independent_supports':supports,
        'spread_footings':supports,'pier_columns':supports,
        'shared_bent_positions_without_shared_crosshead_design':spans_per_track+1,
        'bearings':beams*4,'ten_m_segments':pieces,'required_piece_lifts':pieces,
        'temporary_tower_placements':beams,
        'footing_concrete_m3':supports*footing_area*thick,
        'pier_concrete_m3':supports*0.8*8,
        'beam_concrete_m3':beams*beam['concrete_m3'],
        'rail_stock_m':length*4,
        'direct_fastener_sets':beams*beam['direct_fastener_sets'],
        'continuous_protected_access_track_m_required':length*2,
        'nonstation_walkway_m_priced_in_fresh_line30':Q['protected_walkway_m'] if length==30000 else None,
        'field_butt_welds_for_20m_rail_stock_hypothesis':4*(spans_per_track-1),
        'nominal_10m_segment_bare_stock_tonnes':pieces*bare_piece/2/1000,
        'beam_factory_person_h_whole_beam_proxy_lower_bound':beams*64,
        'site_erection_person_h_whole_beam_proxy_lower_bound':beams*64,
        'support_field_person_h_proxy':supports*24,
        'illustrative_crane_shifts_at_two_piece_lifts_per_shift':math.ceil(pieces/2),
        'illustrative_one_crane_two_shift_workdays':math.ceil(pieces/2/2),
    }

cap_base_iqd=sum(row['costs_iqd']['base'] for row in base['capital_lines'])
base_concrete_m3=Q['foundation_pier_concrete_m3']
new_concrete_m3=counts['route']['footing_concrete_m3']+counts['route']['pier_concrete_m3']
delta_m3=new_concrete_m3-base_concrete_m3
material_delta_iqd=delta_m3*(base['unit_rates']['base']['concrete_ingredient_iqd_m3']+160*base['statistical_rates_iqd']['rebar'])
fx=spec['currency']['iqd_per_usd']

result={
    'schema':'osr-v07-civil-construction-result/1','input_id':inp['input_id'],
    'candidate_id':physical_id,'physical_definition':physical,
    'evaluation_type':'deterministic quantity and necessary-bound construction study',
    'execution':'completed_analytic_research','engineering_screen':'hold',
    'selected_reference_changed':False,'physical_accepted':False,
    'independent_approval':False,
    'fresh_civil_evaluation_id':base['evaluation_id'],
    'fresh_line30_full_evaluation_id':fresh_line['evaluation_id'],
    'replayed_whole_beam_analysis_id':beam['alternative_id'],
    'replayed_whole_beam_component_id':beam['physical_civil_component_id'],
    'replay_checks':{'civil_component_identity_matches':True,
                     'span_count_matches':True,'support_count_matches':True,
                     'beam_mass_matches':True},
    'counts':counts,
    'beam_whole_span_model':{
        'scope':'fresh source model of continuous whole 20 m beam; segmented joint and temporary stages excluded',
        'dynamic_factor_applied_once':1.3,
        'moving_load_positions_method':'axle support/section events, 41 section stations',
        'maximum_live_moment_Nm':beam['maximum_live_moment_Nm'],
        'local_envelope':[{'x_m':r['x_m'],'max_live_moment_Nm':r['max_live_moment_Nm'],
                           'max_service_tension_Pa':r['max_service_tension_Pa'],
                           'max_service_compression_Pa':r['max_service_compression_Pa'],
                           'max_transfer_tension_Pa':r['max_release_tension_Pa'],
                           'max_transfer_compression_Pa':r['max_release_compression_Pa']}
                          for r in beam['moving_load_envelope']],
        'maximum_service_tension_Pa':beam['max_service_tension_Pa'],
        'maximum_service_compression_Pa':beam['max_service_compression_Pa'],
        'maximum_transfer_tension_Pa':beam['max_release_tension_Pa'],
        'maximum_transfer_compression_Pa':beam['max_release_compression_Pa'],
        'source_necessary_longitudinal_screen':beam['necessary_longitudinal_screen'],
        'source_deflection_upper_bound_m':beam['deflection_upper_bound_m'],
        'whole_beam_crowd_load':True,'segmented_candidate_structural_pass':None,
    },
    'lifting_transport':{
        'whole_beam_bare_kg':bare_piece,'whole_required_hook_kg_hypothesis':whole_hook,
        'whole_over_60t_at_12m':whole_hook>60000,
        'whole_over_35t_road_payload':bare_piece>35000,
        'half_segment_bare_kg_hypothesis':bare_piece/2,
        'half_required_hook_kg_hypothesis':piece_hook,
        'half_below_provisional_60t_at_12m':piece_hook<=60000,
        'half_below_provisional_35t_road_payload':bare_piece/2<=35000,
        'actual_crane_chart_at_radius_verified':False,
        'actual_transport_permit_and_axle_load_verified':False,
        'handling_attachment_temporary_stress_verified':False,
    },
    'foundation':{
        'family':'spread-footing','width_m':3,'length_m':3,'thickness_m':1.2,
        'gravity_closed_soil_pressure_kPa_hypothesis':pressure_kPa,
        'nominal_soil_case_200kPa_gravity_screen':pressure_kPa<=200,
        'same_footing_100kPa_gravity_screen':pressure_kPa<=100,
        'same_footing_300kPa_gravity_screen':pressure_kPa<=300,
        'necessary_minimum_areas_m2_by_soil_kPa':{str(s['soil_kPa']):s['gravity_closed_area_m2'] for s in soil},
        '100kPa_gravity_only_alternate_square_width_m':4.25,
        'pile_group_quantity':None,
        'settlement_overturning_uplift_lateral_and_seismic_verified':False,
    },
    'cost':{
        'candidate_complete_installed_cost_usd':None,
        'candidate_complete_installed_cost_iqd':None,
        'fresh_unsegmented_line30_civil_class_C_proxy_iqd':cap_base_iqd,
        'fresh_unsegmented_line30_civil_class_C_proxy_usd':cap_base_iqd/fx,
        'unsegmented_proxy_per_route_km_usd':cap_base_iqd/fx/30,
        'selected_3m_footing_additional_concrete_m3_vs_gravity_minimum':delta_m3,
        'selected_3m_footing_additional_concrete_and_rebar_proxy_iqd':material_delta_iqd,
        'segmented_joint_tower_extra_crane_cycles_and_qa_cost_iqd':None,
        'cost_completeness':'unsegmented whole-beam guideway proxy only; 3 m footing material delta separately; revised segment/joint/temporary works/site access unknown',
    },
    'construction_sequence':[
        'Survey alignment, utilities, soil and access; confirm 200 kPa hypothesis and crane standing ground at 12 m radius.',
        'Fabricate match-cast 10 m box segments with bar, duct, anchor and handling details; test concrete and material lots.',
        'Excavate and cast 3 m square footings, independent 8 m piers and bearing seats; cure to measured release strength.',
        'Install surveyed bearings and braced midspan temporary tower with independently designed foundations.',
        'Transport first 10 m segment within route and permit limits; lift with four designed attachments onto end bearing and tower.',
        'Repeat second segment; survey interface and close 2 mm match-cast keyed epoxy joint.',
        'Stress continuous post-tension symmetrically; grout ducts and inspect transfer/end zones.',
        'Unload temporary tower progressively while measuring joint closure, camber, bearing reaction and rail datum.',
        'Install rail, fasteners, drainage and protected access; measure longitudinal/transverse geometry and proof under load.',
        'Independent structural, geotechnical, lifting, accessibility and operations review before any construction or service release.',
    ],
    'holds':[
        'Source whole-beam local moving-load, transfer-stress and deflection screens do not validate the segmented keyed joint, torsion, cracking, shear, fatigue or temporary prop-restrained prestress effects.',
        'Unequal rail loading, walkway eccentricity, braking/centrifugal forces and wind need coupled torsion and transverse bearing reactions.',
        'Four-sling handling attachment strength, segment lifting stress, haul restraint, wind stability and actual crane load chart at radius remain unmeasured.',
        'Soil allowable is a hypothesis; settlement, lateral, seismic, scour, uplift, excavation and temporary tower pad pressure need geotechnical investigation.',
        'Wheel reference has no selected magnetic running gap. Feed measured pier/beam deflection, twist, creep and settlement to any future LIM or magnetic interface clearance model; no unselected gap limit is invented.',
        'Station platforms, terminal/crossover structures, utilities and route-specific crossings are separate accounts. Demonstrator straight-span quantities do not include station work.',
        'Base factory/erection hours and price cover whole beams; segmentation adds positive unresolved work. The illustrative lift cycle is not a verified production schedule.',
        'Complete installed mass, local supplier capacity, road permits, QA and independent approval remain open.',
    ],
    'next_measurements':[
        'Geotechnical boreholes and settlement tests along demonstrator; actual allowable pressure and groundwater.',
        'Match-cast joint mock-up: shear, torsion, fatigue, crack width, tendon anchorage and prop-release strain.',
        'Certified crane chart for 10 m segment plus rigging at measured radius and ground bearing mats.',
        'Factory trial of 10 m form, cage, ducts, cure and handling; timed crew hours and rejection rate.',
        'Road route/permit survey for 10 m, 29.6 t pieces and site turning/laydown.',
        'Proof-load and monitoring survey for beam, pier, bearing, track datum and long-term deformation.',
        'Supplier and local labour quotations for precast, footing, transport, erection and maintenance.',
    ],
    'failure_reasons':{'whole_beam_lift':'required hook exceeds provisional 60 t at 12 m',
                       'whole_beam_transport':'bare beam exceeds provisional 35 t payload',
                       'same_3m_footing_at_100kPa':'gravity pressure exceeds 100 kPa',
                       'segmented_structural_screen':'not evaluated; joint and temporary stages change physical model'},
    'resource_budget':{'maximum_runtime_s':120,'maximum_rss_bytes':536870912,'maximum_disk_bytes':20971520,
                       'disk_free_reserve_bytes':20*1024**3,'native_solver_jobs':0},
}
result['evaluation_id']=identity({k:v for k,v in result.items() if k!='evaluation_id'})
OUT.mkdir(parents=True,exist_ok=True)
for name,value in [('input.json',inp),('result.json',result)]:
    (OUT/name).write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
free_after=__import__('shutil').disk_usage(OUT).free
if free_after < 20 * 1024**3:
    raise RuntimeError('20 GiB disk free reserve breached after evaluation')
print(json.dumps({'input_id':inp['input_id'],'candidate_id':physical_id,'evaluation_id':result['evaluation_id'],
                  'fresh_civil_evaluation_id':base['evaluation_id'],
                  'free_before_bytes':free_before,'free_after_bytes':free_after,
                  'source_commit':commit},sort_keys=True))
