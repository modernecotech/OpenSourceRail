"""Whole-package quantities, coupled mechanics, construction and honest ranking."""
from copy import deepcopy
import gzip
import math
from pathlib import Path

import numpy as np
import pytest

from osr_mech.civil.exploration import geometry,foundation_geometry,assembly_cad
from engineering.civil_exploration.contracts import HERE,ROOT,load,sha
from engineering.civil_exploration.workflow import candidate
from engineering.civil_exploration.model import System,takeoff
from engineering.civil_exploration import systems,foundations,construction,system_economics,space_frame,section_mechanics,bim,system_report


def options():return load(HERE/'config/system-options.json')


def seed(index=1):
    config=options();choice=systems.engineering_seeds(config)[index]
    study,definition=systems.study_for(choice,config)
    return config,choice,study,candidate(definition,study)


@pytest.mark.parametrize('family',['pi','hollow-box','conventional-I','U-girder','ribbed-deck','uhpc-ribbed','hybrid-shell','segmental-box','steel-composite-I','frp-composite-I'])
def test_all_beam_choices_preserve_role_mass_and_canonical_cad(family):
    config=options();i=next(i for i,b in enumerate(config['beams']) if b['id']==family)
    _,_,s,c=seed(i);q=takeoff(c,s);g=geometry(c['definition'])
    volumes=q['deck_material_volumes_m3']
    expected=sum((seg['end_m']-seg['start_m'])*sum(r['width_m']*r['height_m'] for r in seg['regions']) for seg in g['deck'])*q['beam_lifts']
    assert sum(volumes.values())==pytest.approx(expected)
    assert q['deck_concrete_m3']==pytest.approx(volumes.get('concrete',0.)+volumes.get('uhpc',0.))
    all_volumes=expected+sum(q['pier_material_volumes_m3'].values())+q['cap_concrete_m3']+q['foundation_concrete_m3']
    assert assembly_cad(c['definition'],c['foundation'],300.).volume/1e9==pytest.approx(all_volumes)
    if family=='steel-composite-I':assert volumes['steel']>0 and q['prestress_allowance_kg']==0
    assert 'train' not in s


@pytest.mark.parametrize('family',['solid','solid-tapered','hollow-tapered','hollow-prismatic','segmental-hollow','double-skin-hybrid'])
def test_pier_options_have_actual_regions_and_material_masses(family):
    config,choice,_,_=seed();row=next(r for r in config['piers'] if r['id']==family)
    choice['pier']=family;choice['pier_parameters']={k:(lo+hi)/2 for k,(lo,hi) in row['bounds'].items()}
    s,d=systems.study_for(choice,config);c=candidate(d,s);g=geometry(d);q=takeoff(c,s)
    assert len(g['pier'])==8 and all(seg['inertia_y_m4']>0 for seg in g['pier'])
    if family=='double-skin-hybrid':
        assert q['pier_material_volumes_m3']['frp']>0
        assert q['pier_concrete_m3']==pytest.approx(q['pier_material_volumes_m3']['concrete'])
        rows=system_economics.bill(c,s,construction.units(c,s,'precast-full','shell-infill'))
        assert rows['frp_material_and_fabrication']['quantity']==pytest.approx(q['deck_material_volumes_m3'].get('frp',0.)+q['pier_material_volumes_m3']['frp'])


@pytest.mark.parametrize('foundation_id',['reference-four','bored-four','bored-six','single-shaft','CFA-six','displacement-six','hollow-driven-six','square-driven-six','spread-footing'])
def test_foundation_options_match_independent_area_quantities_and_bim(foundation_id,tmp_path):
    config,choice,s,_=seed();choice['foundation']=foundation_id;s,d=systems.study_for(choice,config);c=candidate(d,s)
    p=c['foundation'];g=foundation_geometry(p);D=p['pile_diameter_m'];inner=p.get('pile_inner_diameter_m',0.)
    area=D*D if p.get('pile_shape')=='square' else math.pi*(D*D-inner*inner)/4
    assert g['pile_concrete_m3']==pytest.approx(p['pile_count']*p['pile_length_m']*area)
    assert len(g['piles'])==p['pile_count']
    if foundation_id=='spread-footing':assert g['piles']==[] and p['pile_length_m']==0
    pytest.importorskip('ifcopenshell');r=bim.export(c,s,tmp_path/'assembly.ifc')
    assert r['source_volume_m3']==pytest.approx(assembly_cad(d,p,300.).volume/1e9)
    if foundation_id=='hollow-driven-six':
        import ifcopenshell
        f=ifcopenshell.open(str(tmp_path/'assembly.ifc'))
        assert len(f.by_type('IfcCircleHollowProfileDef'))==takeoff(c,s)['pile_count']


def test_lightweight_deck_does_not_silently_reduce_foundation_or_pier_density():
    config,choice,s,c=seed();old=takeoff(c,s);choice['material']='lightweight'
    light,d=systems.study_for(choice,config);new=takeoff(candidate(d,light),light)
    assert new['installed_study_mass_kg']<old['installed_study_mass_kg']
    assert new['foundation_concrete_m3']==old['foundation_concrete_m3']
    assert new['pier_material_volumes_m3']==old['pier_material_volumes_m3']
    assert light['support_material']['density_kg_m3']==2500.
    assert light['foundation_material']['density_kg_m3']==2500.


def test_cfrp_matrix_changes_stiffness_and_mass_without_a_measured_claim():
    config=options();i=next(i for i,b in enumerate(config['beams']) if b['id']=='frp-composite-I');_,choice,s,c=seed(i)
    baseline=takeoff(c,s);choice['fibre_material']='cfrp';new,d=systems.study_for(choice,config);changed=candidate(d,new)
    from engineering.civil_exploration.model import deck_physics
    section=geometry(d)['deck'][1]
    assert deck_physics(changed,section)['effective_EI_nm2']>deck_physics(c,section)['effective_EI_nm2']
    assert takeoff(changed,new)['installed_study_mass_kg']<baseline['installed_study_mass_kg']
    assert not changed['material_records']['frp']['measured']


@pytest.mark.parametrize('mutation',[
    lambda c:c.update(unregistered=1),
    lambda c:c['spans_m'].append(27.),
    lambda c:c['materials']['normal'].update(measured=True),
    lambda c:c['piers'][1]['bounds'].update(wall_m=[.1,float('nan')]),
    lambda c:c['foundations'][0]['bounds'].update(unsupported_parameter=[1.,2.]),
    lambda c:c['soil_scenarios'][0].update(calibrated=True),
    lambda c:c['soil_scenarios'][0].update(group_efficiency=2.),
    lambda c:c['soil_scenarios'][0].update(toe_n_m3=True),
])
def test_invalid_configuration_is_rejected_before_campaign(mutation):
    c=options();mutation(c)
    with pytest.raises(ValueError):systems.validate_options(c)


def test_foundation_dimensions_are_mutated_and_invalidate_identity():
    config,choice,_,_=seed();choice['foundation']='bored-four'
    first,d=systems.study_for(choice,config);c1=candidate(d,first)
    choice['foundation_parameters']={'pile_diameter_m':1.1,'pile_length_m':24.}
    changed,d=systems.study_for(choice,config);c2=candidate(d,changed)
    assert c1['id']!=c2['id']
    assert changed['foundation']['cap_length_m']==pytest.approx(first['foundation']['cap_length_m']*1.1)
    assert takeoff(c2,changed)['foundation_concrete_m3']>takeoff(c1,first)['foundation_concrete_m3']


def test_native_foundation_reciprocity_refinement_and_coupled_load_path():
    pytest.importorskip('openseespy.opensees')
    config,_,study,c=seed();f=foundations.refinement(c['foundation'],config['materials']['normal'],config['soil_scenarios'][0])
    assert f['passed'] and len(f['levels'])==3
    K=np.asarray(f['selected']['stiffness_matrix'])
    assert np.allclose(K,K.T) and min(np.linalg.eigvalsh(K))>0 and K[0,2]!=0
    r=System(c,study,f['selected'],8).uniform_service(20.,braking_fraction=.15)
    assert sum(p['vertical_n'] for p in r['support_actions'])==pytest.approx(r['expected_total_reaction_n'])
    assert sum(p['horizontal_n'] for p in r['support_actions'])==pytest.approx(-20.*1000*300*2*.15)
    assert r['response']['pier_top_horizontal_m']>0
    assert any(abs(p['moment_nm'])>0 for p in r['support_actions'])


def test_slender_pile_foundation_adapts_beyond_initial_three_meshes():
    pytest.importorskip('openseespy.opensees');config=options()
    parameters=deepcopy(next(f['parameters'] for f in config['foundations'] if f['id']=='CFA-six'))
    parameters.update(cap_depth_m=1.17329718,cap_length_m=4.724398466666667,cap_width_m=3.7795187733333333,
                      pile_diameter_m=.70865977,pile_length_m=29.50187074)
    result=foundations.refinement(parameters,config['materials']['normal'],config['soil_scenarios'][0])
    assert result['passed'] and len(result['levels'])>3
    assert result['selected']['elements_per_pile']>=32
    assert result['relative_stiffness_change']<=result['relative_limit']


def test_native_3d_one_track_loading_preserves_force_and_moment_balance():
    pytest.importorskip('openseespy.opensees')
    config,_,study,c=seed();soil=config['soil_scenarios'][0]
    longitudinal=foundations.stiffness(c['foundation'],config['materials']['normal'],soil,16)
    transverse=foundations.stiffness(c['foundation'],config['materials']['normal'],soil,16,axis='transverse')
    r=space_frame.run(c,study,longitudinal,transverse,20.,1,8,braking_fraction=.15)
    assert r['expected_vertical_n']==pytest.approx(r['actual_vertical_n'])
    assert r['moment_equilibrium'][0]['applied_nm']!=0
    for record in r['moment_equilibrium']:assert record['applied_nm']==pytest.approx(-record['reaction_nm'],abs=1.)
    assert r['peak_cap_bending_nm']>0 and r['peak_deck_roll_rad']>0
    assert r['physical_release'] is False
    assert {e['kind'] for e in r['elements']}=={'foundation','foundation-offset','pier','cap','bearing','deck'}


def test_torsion_uses_saint_venant_and_composite_slip_has_independent_limits():
    J=section_mechanics.rectangle_torsion(1.,1.)
    assert J==pytest.approx(.140577014955,rel=1e-8)
    assert J<1/6  # Polar second moment is not the torsional constant.
    upper=dict(E_pa=30e9,area_m2=.1,inertia_m4=.1**3/12,centroid_z_m=.3)
    lower=dict(E_pa=200e9,area_m2=.02,inertia_m4=.02**3/12,centroid_z_m=0.)
    rows=[section_mechanics.partial_interaction(10.,upper,lower,k,1000.,48) for k in (0.,1e7,1e12)]
    assert rows[0]['peak_deflection_m']==pytest.approx(rows[0]['noncomposite_limit_m'],rel=1e-6)
    assert rows[-1]['peak_deflection_m']==pytest.approx(rows[-1]['perfect_bond_limit_m'],rel=.002)
    assert rows[0]['peak_deflection_m']>rows[1]['peak_deflection_m']>rows[2]['peak_deflection_m']
    with pytest.raises(ValueError):section_mechanics.partial_interaction(10.,{**upper,'E_pa':float('nan')},lower,1e8,1000.)


def test_segmental_and_hybrid_units_preserve_service_mass_and_transport_difference():
    _,_,s,c=seed()
    full=construction.units(c,s,'precast-full','cast-in-place')
    segmented=construction.units(c,s,'segmental','cast-in-place')
    assert sum(p['transport_mass_kg'] for p in segmented['per_beam_units'])==pytest.approx(full['service_beam_mass_kg'])
    assert segmented['beam_units']>full['beam_units'] and segmented['maximum_lift_mass_kg']<full['maximum_lift_mass_kg']
    config=options();i=next(i for i,b in enumerate(config['beams']) if b['id']=='hybrid-shell');_,_,s,c=seed(i)
    shell=construction.units(c,s,'shell-infill','cast-in-place')
    assert sum(p['transport_mass_kg'] for p in shell['per_beam_units'])<shell['service_beam_mass_kg']
    assert not shell['construction_release']


def test_driven_pile_transport_and_splice_scope_is_included():
    config,choice,_,_=seed();choice['foundation']='hollow-driven-six';s,d=systems.study_for(choice,config);c=candidate(d,s)
    u=construction.units(c,s,'precast-full','cast-in-place');q=takeoff(c,s);f=foundation_geometry(c['foundation'])
    assert len(u['per_support_pile_units'])==12 and u['pile_delivery_units']==q['pile_count']*2
    assert sum(p['transport_mass_kg'] for p in u['per_support_pile_units'])==pytest.approx(f['pile_concrete_m3']*(2500+120))
    rows=system_economics.bill(c,s,u)
    assert rows['precast_pile_transport']['quantity']==u['pile_delivery_units']
    assert rows['pile_splice_connections']['quantity']==q['pile_count']


def test_finite_resource_time_is_conditional_and_no_overlapping_resource_lane():
    _,_,s,c=seed();u=construction.units(c,s,'precast-full','cast-in-place')
    p=load(HERE/'config/system-scenarios.json')['scenarios'][0]['productivity']
    schedule=construction.schedule(c,s,u,p)
    assert schedule['unresolved_external_gates']
    for pool in p['capacities']:
        for lane in range(1,p['capacities'][pool]+1):
            tasks=sorted([t for t in schedule['tasks'] if t['resource_pool']==pool and t['resource_lane']==lane],key=lambda t:t['planned_start_hour'])
            assert all(a['planned_finish_hour']<b['planned_start_hour'] for a,b in zip(tasks,tasks[1:]))
    by_uid={t['manufacturing_uid']:t for t in schedule['tasks']}
    for task in schedule['tasks']:
        for predecessor in task['schedule_predecessor_uids'].split('; '):
            if predecessor:assert by_uid[predecessor]['planned_finish_hour']<task['planned_start_hour']
    scarce=deepcopy(p);scarce['capacities'].update({'foundation-rig':1,'precast-bed':1,'erection':1})
    assert construction.schedule(c,s,u,scarce)['programme_working_days']>=schedule['programme_working_days']


def test_complete_scenario_costs_have_traceable_scope_but_actual_prices_unknown():
    _,choice,s,c=seed();u=construction.units(c,s,'precast-full','cast-in-place');source=HERE/'config/system-scenarios.json';scenario=load(source)['scenarios'][0]
    schedule=construction.schedule(c,s,u,scenario['productivity'])
    priced=system_economics.scenario_price(c,s,choice,u,schedule,scenario,source)
    assert priced['installed_cost_usd']==pytest.approx(sum(r['cost_usd'] for r in priced['rows']))
    assert priced['whole_life_cost_usd']>priced['installed_cost_usd']
    assert not priced['actual_baghdad_price'] and priced['hypothetical_tier_is_not_a_crane_chart']
    assert all(r['rate_record']['classification']=='assumption' for r in priced['rows'])
    actual=system_economics.actual_price(c,s,u,load(HERE/'config/commercial.json'))
    assert actual['installed_cost_usd'] is None and not actual['actual_baghdad_price']
    assert {'site_overhead','crane_mobilisation'}<=set(actual['unpriced_scope'])


def test_pareto_and_objective_leaders_keep_different_choices():
    def row(id,cost,mass,days):return dict(package_id=id,status='completed',violation=0.,objectives=[cost,mass,days],quantities={'installed_study_mass_kg':mass},scenarios={'s':{'installed_cost_usd':cost,'whole_life_cost_usd':cost*2,'working_days':days}})
    rows=[row('cheap',1.,5.,5.),row('light',5.,1.,5.),row('fast',5.,5.,1.),row('dominated',6.,6.,6.)]
    report=systems.leaders(rows,'s')
    assert report['cheapest']=='cheap' and report['lightest']=='light' and report['fastest']=='fast'
    assert set(report['pareto_ids'])=={'cheap','light','fast'}


def test_retained_full_system_review_preserves_source_proof_and_external_gates():
    review=load(HERE/'examples/complete-system-review.json');report=review['report'];config=review['option_register']
    assert review['generator_sha256']==sha(ROOT/review['generator'])
    assert len(config['beams'])==10 and len(config['piers'])==6 and len(config['foundations'])==9
    assert report['distinct_packages']>=500 and len(report['shortlist'])>=20
    assert report['component_benchmarks']['passed'] and report['numerical_refinement_passed']
    assert report['artifact_retrieval']['integrity_verified']
    assert not report['actual_supplier_costs_known'] and report['cheapest_qualified_design'] is None
    assert not report['all_document_acceptance_complete'] and not report['physical_release']
    assert report['qualified_feasible_pareto_set']==[] and not report['global_optimum_proven']
    assert report['load_case']['actual_axle_positions_m'] is None
    assert all(r['actual_installed_cost_usd'] is None for r in review['rows'] if r['status']=='completed')
    assert all(p['observed_results'] is None for p in review['physical_tests']['tests'])
    assert review['promotion']['status'].startswith('blocked')
    assert all(r['convergence_passed'] and len(r['solid_meshes'])==3 and len(r['space_frame_checks'])==6 for r in report['refinements'])
    assert all(r['pier_pdelta_diagnostic']['analytical_relative_error']<=.002 for r in report['refinements'])
    assert {w['id'] for w in report['work_packages']}=={f'C{i:02d}' for i in range(1,15)}
    assert all(not w['complete'] and w['remaining_acceptance'] for w in report['work_packages'])
    for name in ('system-choices.svg','pareto.svg'):assert sha(HERE/'examples'/name)==review['artifacts'][name]
    by_id={r['package_id']:r for r in review['rows']}
    assert len(review['history'])==report['evaluated_attempts']
    for event in review['history']:
        assert event['reason_from_recorded_method'] and event['package_id'] in by_id
        assert all(parent in by_id for parent in event['parents'])
    for sid,winners in report['winners'].items():
        for objective in ('cheapest','lightest','fastest'):
            r=by_id[winners[objective]];assert r['violation']==0 and r['status']=='completed'
