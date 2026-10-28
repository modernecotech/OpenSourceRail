"""Necessary launch hardware bounds and source/candidate discipline."""
from copy import deepcopy
import pytest
from engineering.component_registry import make_part,make_registry,make_occurrence,summary
from engineering.component_registry.materials import lookup
from engineering.railway_progress import alternatives as a,identity


@pytest.fixture(scope='module')
def vehicle():
    m=lookup('AL-6082-T651-SHEET')
    body=make_part('DISPOSABLE-TEST-BODY','A',['primary-body'],{'kind':'envelope','dimensions_m':[17.,2.8,3.]},None,
        dict(calculated_kg=None,lower_bound_kg=14000.,upper_bound_kg=18000.,evidence_state='bounded-estimate'),dict(method='unqualified-test-only'))
    fin=make_part('TEST-passive-aluminium-fin','A',['LIM-interface'],{'kind':'box','dimensions_m':[2.98,.012,.3]},m['material_id'],
        dict(calculated_kg=2.98*.012*.3*2700.,lower_bound_kg=2.98*.012*.3*2680.,upper_bound_kg=2.98*.012*.3*2720.,evidence_state='calculated'),dict(method='plate-cut'))
    occ=[]
    for car in range(6):
        occ.append(make_occurrence(f'car-{car+1}/body',body))
        for i,x in enumerate((4.,7.,10.)):
            pose=[[1.,0.,0.,x+17.5*car],[0.,1.,0.,0.],[0.,0.,1.,.5],[0.,0.,0.,1.]]
            occ.append(make_occurrence(f'car-{car+1}/fin-{i}',fin,transform=pose))
    reg=make_registry('TEST NOT FULL VEHICLE',[body,fin],occ,['primary-body','LIM-interface'])
    v=dict(schema='osr-equipped-reference-cell-vehicle/1',candidate_id=reg['candidate_id'],registry=reg,summary=summary(reg),
      requirements=dict(cars=6,car_length_m=17.,fixed_seats_per_car=44,wheelchair_places_per_car=2,passenger_normal_per_car=46))
    v['evaluation_id']=identity(v);return v


def test_sourced_motor_rope_and_speed_domain_are_explicit_not_quotes():
    book=a.catalogue();sources=book['source_facts']['sources'];motor=sources[0]['facts']
    assert motor['shaft_power_W']==250000 and motor['catalogue_mass_kg']==2010 and motor['rated_speed_rpm']==993
    assert sources[1]['facts']['32mm']['minimum_breaking_force_N']==645000
    assert sources[2]['facts']['published_maximum_speed_m_s']==15.<20.
    assert all(s['raw_document_retrieved'] and len(s['document_sha256'])==64 and not s['supplier_quote'] for s in sources)


def test_pinch_geometry_inventory_clamping_torque_and_energy_are_counted(vehicle):
    r=a.evaluate(vehicle);normal=next(x for x in r['load_cases'] if x['load']=='normal')
    assert r['added_counted_onboard_mass_kg']>1500.
    assert r['contact_geometry']['powered_distance_m']==pytest.approx(500.)
    assert r['contact_geometry']['minimum_active_pairs']>=3
    assert normal['required_total_normal_force_N']==pytest.approx(normal['required_force_N']/.2)
    assert normal['required_mechanical_power_W']==pytest.approx(20*normal['required_force_N'])
    assert normal['minimum_launch_distance_at_declared_acceleration_m']==500 and normal['launch_time_s']==50
    assert normal['slip_heat_per_launch_J']>0 and r['unknown_installed_mass_items']
    assert r['installed_CAPEX_usd'] is None and r['whole_life_cost_usd'] is None and r['integrated_winner'] is None
    assert r['published_catalogue_mass_subtotal_kg']==5*8*2010.
    assert all(x['candidate_id']==r['candidate_id'] for x in r['inventory'])


def test_real_hardware_revision_changes_inventory_candidate_and_all_downstream_tasks(vehicle):
    first=a.evaluate(vehicle);second=a.revise(vehicle,first,{'roller_pairs_per_bank':5,'motor_count':10})
    assert first['candidate_id']!=second['candidate_id']
    assert second['published_catalogue_mass_subtotal_kg']>first['published_catalogue_mass_subtotal_kg']
    assert second['ancestry']['parent_candidate_id']==first['candidate_id']
    assert {'inventory','thermal','civil-reactions','manufacturing','cost','journey'}<=set(second['ancestry']['invalidated_stages'])
    with pytest.raises(ValueError):a.revise(vehicle,first,{'roller_pairs_per_bank':4})


def test_friction_or_gradient_evaluation_correction_is_not_new_hardware(vehicle):
    a1=a.evaluate(vehicle);a2=a.evaluate(vehicle,hypotheses={'contact_friction_coefficient':.1,'grade_fraction':.02})
    assert a1['candidate_id']==a2['candidate_id'] and a1['evaluation_id']!=a2['evaluation_id']
    assert a2['load_cases'][1]['required_total_normal_force_N']>a1['load_cases'][1]['required_total_normal_force_N']


def test_conditional_force_comes_from_hardware_caps_never_required_acceleration(vehicle):
    r=a.evaluate(vehicle);nom=a.force_bounds(r,100.,20.)
    assert nom['force_N'] is not None and nom['active_motor_count']>0
    assert nom['force_N'][1]<=nom['shaft_power_upper_W']/20.+1e-8
    weak=a.evaluate(vehicle,parameters={'clamp_design_pressure_Pa':1e6})
    assert a.force_bounds(weak,100.,20.)['force_N'][0]<nom['force_N'][0]
    assert a.force_bounds(r,100.,20.,condition='low-friction')['force_N'][0]<nom['force_N'][0]
    assert a.force_bounds(r,100.,20.,power_enabled=False)['force_N']==[0.,0.]
    assert a.force_bounds(r,1200.,20.)['force_N']==[0.,0.]
    assert nom['available_operating_map'] is None and not nom['physical_accepted']


def test_lost_geometric_contact_is_not_filled_with_required_force(vehicle):
    r=a.evaluate(vehicle,parameters={'bank_starts_m':[-12.]})
    assert r['contact_geometry']['powered_distance_m']<500
    assert a.force_bounds(r,400.,10.)['force_N']==[0.,0.]
    assert any('Insufficient geometric' in x for x in r['open_tasks'])


def test_cable_rope_tension_power_return_cycle_and_published_speed_are_separate(vehicle):
    r=a.evaluate(vehicle,kind='cable-launch-tug');normal=r['load_cases'][1];m=r['mechanism']
    assert m['rope_mass_kg']==pytest.approx(m['rope_length_m']*4.18)
    assert normal['minimum_breaking_force_ratio']==pytest.approx(645000/normal['rope_tight_side_tension_N'])
    assert m['minimum_rest_to_rest_reset_time_s']>50.
    assert not m['cycle_fits120s_hypothesis'] and m['reference20m_s_exceeds_published_APM_domain']
    f=a.force_bounds(r,250.,20.)
    assert f['force_N'][1]<=m['conditional_nameplate_shaft_power_W']/20.+1e-8
    assert a.force_bounds(r,501.,10.)['force_N']==[0.,0.]
    assert not m['actual_bend_fatigue_or_grip_verified']


def test_zero_drag_route_energy_bound_rejects_two_percent_uphill_coast(vehicle):
    r=a.evaluate(vehicle,kind='cable-launch-tug',distance_m=2000.)
    route=next(x for x in r['load_cases'][1]['route_energy_bounds'] if x['coast_grade_fraction']==.02)
    assert route['rise_during_unpowered_coast_m']==30.
    assert route['point_mass_zero_loss_maximum_rise_m']==pytest.approx(20.3943242596)
    assert route['fails_even_zero_drag_energy_bound'] and route['failure_class']=='physical-necessary-bound'
    assert route['remaining_energy_before_aerodynamic_and_braking_J']<0


@pytest.mark.parametrize('kind',['five-20m-LIM','six-20m-LIM','ten-20m-LIM','long-distributed-LIM','continuous-LIM'])
def test_LIM_geometry_never_promotes_unconverged_force_or_scaled_stock(vehicle,kind):
    r=a.evaluate(vehicle,kind=kind)
    assert r['mechanism']['installed_primary_length_m']>0
    assert r['available_operating_map'] is None and a.force_bounds(r,10.,2.)['force_N'] is None
    assert r['complete_installed_mass_kg'] is None and r['actual_supplier_quotes']==0
    assert any('primary' in x for x in r['unknown_installed_mass_items'])


def test_onboard_rescue_is_explicit_new_research_hardware_not_current_reference(vehicle):
    r=a.evaluate(vehicle,kind='onboard-rescue-research')
    assert r['physical_definition']['normal_traction_onboard']
    assert r['mechanism']['actual_rescue_mass_kg'] is None and not r['selected_reference_changed']
    assert a.force_bounds(r,10.,2.)['force_N'] is None


def test_comparison_is_equal_service_next_experiment_only_and_unknown_price_never_cheapest(vehicle):
    cases=[a.evaluate(vehicle,kind=k) for k in ('five-20m-LIM','station-pinch-rollers','cable-launch-tug')]
    c=a.compare(cases);assert c['integrated_winner'] is None and c['cheapest_candidate'] is None
    assert len(c['ranking'])==3 and 'next-experiment' in c['ranking_purpose']
    with pytest.raises(ValueError):a.compare([cases[0],a.evaluate(vehicle,distance_m=1500.)])


def test_candidate_mixing_bad_geometry_out_of_domain_and_forged_results_rejected(vehicle):
    bad=deepcopy(vehicle);bad['candidate_id']='f'*64;bad['evaluation_id']=identity({k:v for k,v in bad.items() if k!='evaluation_id'})
    with pytest.raises(ValueError):a.evaluate(bad)
    with pytest.raises(ValueError):a.evaluate(vehicle,parameters={'roller_pairs_per_bank':3})
    with pytest.raises(ValueError):a.evaluate(vehicle,hypotheses={'slip_fraction':1.})
    with pytest.raises(ValueError):a.evaluate(vehicle,parameters={'bank_starts_m':[float('nan')]})
    r=a.evaluate(vehicle);r['candidate_id']='f'*64
    with pytest.raises(ValueError):a.force_bounds(r,10.,2.)


def test_failed_bank_is_removed_by_exact_identity_not_global_scaling(vehicle):
    r=a.evaluate(vehicle);normal=a.force_bounds(r,10.,10.);failed=a.force_bounds(r,10.,10.,failed_banks=[0])
    assert normal['active_motor_count']>0 and failed['force_N']==[0.,0.]
    assert a.force_bounds(r,10.,10.,failed_banks=[4])['force_N']==normal['force_N']
    for bad in ([99],[0,0],['0'],[True]):
        with pytest.raises(ValueError):a.force_bounds(r,10.,10.,failed_banks=bad)
    cable=a.evaluate(vehicle,kind='cable-launch-tug')
    assert a.force_bounds(cable,10.,10.,failed_banks=[0])['force_N']==[0.,0.]


def test_validated_model_closure_owns_input_and_does_not_use_later_mutation(vehicle):
    r=a.evaluate(vehicle);model=a.force_model(r);expected=model(10.,10.)
    r['conditional_force_model']['power_per_motor_W']=0.
    assert model(10.,10.)==expected
    with pytest.raises(ValueError):a.force_model(r)


def test_layout_revision_repairs_late_contact_loss_without_erasing_mass_cost_consequences(vehicle):
    old=a.evaluate(vehicle,parameters={'bank_starts_m':[-12.,88.,188.,288.,388.]})
    fixed=a.revise(vehicle,old,{'bank_starts_m':[-12.,91.,194.,297.,400.]})
    assert old['contact_geometry']['minimum_active_pairs']==1 and fixed['contact_geometry']['minimum_active_pairs']==3
    assert old['candidate_id']!=fixed['candidate_id'] and old['published_catalogue_mass_subtotal_kg']==fixed['published_catalogue_mass_subtotal_kg']
    for item in fixed['inventory']:
        if item['installation']=='wayside':assert len(item['longitudinal_instance_centres_m'])==item['count']
