"""Numerical closure fixtures; authenticated IDs are injected test capabilities.

These are arithmetic/adversarial method tests, not authentic physical records.
"""
from copy import deepcopy
from math import exp
import pytest

from engineering.station_rail.common import identity
from engineering.railway_completion import domains as d

SOURCE=identity('source-fixture');CRITERION=identity('criterion-fixture')
RAW1=identity('raw1-fixture');RAW2=identity('raw2-fixture')
I=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]


def context():
    bundle=dict(candidate_id=identity('bundle'),definition_id=identity('bundle-definition'),
        body_candidate_id=identity('body'),requirement_revision=identity('requirements'),cars=6,
        source_sha256={'producer.py':identity('source')},
        mass=dict(accounted_tare_kg_per_car=100.,accounted_cap_loaded_kg_per_car=500.,accounted_160_control_kg_per_car=1000.),
        rotating_equivalent_kg_per_car=50.,brake_definition=dict(brake_definition_id=identity('brakes')),
        architecture_case=dict(physical_definition=dict(route=dict(station_spacing_m=2000.,counted_guideway_start_m=0.,counted_guideway_end_m=20.))),
        physical_definition=dict(vehicle=dict(cars=6,body_length_m=17.,coupling_gap_m=.5),
            support=dict(bogie_centres_x_m=[-6.4,6.4],bogie_wheelbase_m=2.1)))
    body=dict(candidate_id=bundle['body_candidate_id'])
    part=dict(id='stock',kind='box',at_m=[0.,0.,0.],size_m=[1.,1.,1.],volume_m3=1.,mass_kg=10.,density_kg_m3=10.,material='fixture')
    scene=dict(schema='osr-railway-twin-scene/1',candidate_id=bundle['candidate_id'],complete_installed_geometry=False,
        occurrences=[dict(id=f'car/{i}/stock',component_definition_id=identity(part),geometry=deepcopy(part),
            system='vehicle/body',translation_m=[-8.5-17.5*i,0.,0.],mass_kg=10.,scope='nominal-stock') for i in range(6)])
    ledger=dict(candidate_id=bundle['candidate_id'],scene=scene,
        unlocated_accounts=[dict(id=f'car/{i}/joint',accounted_mass_kg=None,component_definition_id=None,system='vehicle/joints') for i in range(6)])
    return bundle,body,ledger


def run(domain,data,ctx=None,extra=()):
    bundle,body,ledger=context() if ctx is None else ctx
    record=d.make_record(bundle,domain,data)
    value=d.evaluate(bundle,body,ledger,records=[record],authenticated={record['record_id'],SOURCE,CRITERION,RAW1,RAW2,*extra})
    return value['domains'][domain]


def installed_data(ctx):
    b,body,ledger=ctx;scene=ledger['scene'];part=scene['occurrences'][0]['geometry']
    rows=[]
    for car in range(6):
        pose=dict(frame_id='vehicle',translation_m=[0.,0.,0.],rotation=I)
        rows.append(dict(id=f'net/{car}',car_index=car,geometry=deepcopy(part),component_definition_id=identity(part),
            density_kg_m3=10.,mass_kg=10.,mass_interval_kg=[9.9,10.1],local_CG_m=[.5,.5,.5],
            local_CG_inertia_kg_m2=[[10/6,0,0],[0,10/6,0],[0,0,10/6]],installed_transform=pose,
            source_evidence_ids=[SOURCE],origin_country='GB',hardware_and_services=[dict(id='wire',kind='wire',quantity=1,
                positions_local_m=[[.5,.5,.5]],included_mass_kg=1.,minimum_bend_radius_m=.1,installed_bend_radius_m=.2,
                provided_slack_m=.2,required_motion_slack_m=.1,duty_evidence_ids=[SOURCE])],
            access=dict(installation_path=[pose],removal_path=[pose],tool_envelopes=[dict(min_m=[0.,0.,0.],max_m=[1.,1.,1.])],
                sequence=['install','inspect'],lifting_capacity_kg=20.,inspection_retention_evidence_ids=[SOURCE])))
    return dict(base_scene_id=identity(scene),remove_occurrence_ids=[r['id'] for r in scene['occurrences']]+[r['id'] for r in ledger['unlocated_accounts']],
        net_occurrences=rows,net_stock_operations=[dict(parent_occurrence_id=r['id'],parent_geometry_id=identity(r['geometry']),
            replacement_occurrence_ids=[f'net/{i}'],removed_volume_m3=0.,cut_joint_clearance_evidence_ids=[SOURCE]) for i,r in enumerate(scene['occurrences'])],
        account_resolution=[dict(parent_account_id=r['id'],replacement_occurrence_ids=[],absence_or_no_residual_evidence_ids=[SOURCE]) for r in ledger['unlocated_accounts']])


def structure_data(ctx):
    return dict(results=[dict(scope=scope,load='crowd' if scope=='crowd' else 'normal',
        applied_mass_kg_per_car=1000. if scope=='crowd' else 500.,unit='Pa',coarse=100.,fine=101.,uncertainty=1.,limit=200.,
        convergence_limit_fraction=.05,mesh_ids=[RAW1,RAW2],raw_result_ids=[RAW1,RAW2],criterion_record_id=CRITERION,comparison='le') for scope in d.STRUCTURAL_SCOPES])


def brake_data(ctx):
    return dict(cases=[dict(name=name,load='crowd',brake_definition_id=ctx[0]['brake_definition']['brake_definition_id'],
        force_evidence_ids=[SOURCE],criterion_record_id=CRITERION,initial_speed_m_s=0. if name=='parking' else 10.,
        grade_up_fraction=.01,adhesion=.9,dt_s=.05,horizon_s=10.,force_curve=[dict(time_s=0.,force_N_per_car=10000.),dict(time_s=10.,force_N_per_car=10000.)],
        stop_distance_limit_m=100.,disc_heat_capacity_J_K_per_car=1e6,ambient_C=20.,maximum_disc_C=120.,
        heat_rejection_W_K_per_car=1000.,brake_cycle_s=180.,thermal_duty_evidence_ids=[SOURCE]) for name in ('empty','normal','crowd','wet','hot','lost-channel','parking')])


def civil_data(ctx):
    return dict(site_evidence_ids=[SOURCE],supports=[dict(id=f'pier/{i}',chainage_m=float(20*i),
        braking_distribution_fraction=.5,load_and_geometry_evidence_ids=[SOURCE],footing_length_m=10.,footing_width_m=10.,footing_depth_m=1.,
        concrete_density_kg_m3=2500.,pier_headstock_volume_m3=5.,other_vertical_load_N=0.,overturning_Mx_Nm=100.,overturning_My_Nm=100.,
        horizontal_load_N=100.,allowable_bearing_Pa=1e6,base_friction_coefficient=.5,minimum_sliding_factor=1.5,
        soil_elastic_modulus_Pa=1e8,soil_poisson=.3,settlement_shape_factor=1.,settlement_limit_m=.1) for i in range(2)])


def economy_data(ctx):
    b,body,ledger=ctx
    return dict(quotes=[dict(occurrence_id=r['id'],component_definition_id=r['component_definition_id'],currency='USD',unit='occurrence',quantity=1.,
        unit_price_USD=100.,quote_evidence_id=SOURCE,origin_country='GB') for r in ledger['scene']['occurrences']],
        scope_costs=[dict(scope=scope,evidence_ids=[SOURCE],cashflows=[dict(year=1,cost_USD=10. if scope=='energy' else 0.)]) for scope in d.COST_SCOPES],
        design_life_years=20,real_discount_rate=.05,scope_costs_exclude_occurrence_quotes=True,
        service_context=dict(cars=6,normal_people_per_car=46,headway_s=120.,station_spacing_m=2000.))


def test_empty_inputs_hold_each_domain_without_zero_substitutions():
    b,body,ledger=context();r=d.evaluate(b,body,ledger)
    assert r['numerical_domains_supported']==0
    assert all(row['state']=='missing' for row in r['domains'].values())
    assert r['physical_completion'] is False and all(r[k] is False for k in d.FLAGS)


def test_self_authenticated_flags_or_resealed_source_mismatch_do_not_admit():
    b,body,ledger=context();record=d.make_record(b,'body-structure',structure_data((b,body,ledger)))
    assert d.evaluate(b,body,ledger,[record],authenticated=[])['domains']['body-structure']['state']=='missing'
    record['source_sha256']={'different':SOURCE};record['record_id']=identity({k:v for k,v in record.items() if k!='record_id'})
    with pytest.raises(ValueError,match='source_sha256'):d.evaluate(b,body,ledger,[record],authenticated=[record['record_id']])


@pytest.mark.parametrize('key,value',[('candidate_id','a'*64),('bundle_definition_id','b'*64),('units',{'mass':'lb'}),('physical_accepted',True)])
def test_resealed_record_interface_mismatch_rejects(key,value):
    b,body,ledger=context();r=d.make_record(b,'body-structure',{})
    r[key]=value;r['record_id']=identity({k:v for k,v in r.items() if k!='record_id'})
    with pytest.raises(ValueError):d.evaluate(b,body,ledger,[r],[r['record_id']])


def test_nested_acceptance_or_extra_top_level_attestation_is_not_domain_evidence():
    b,body,ledger=context();r=d.make_record(b,'body-structure',dict(physical_accepted=True))
    with pytest.raises(ValueError,match='Nested'):d.evaluate(b,body,ledger,[r],[r['record_id']])
    r=d.make_record(b,'body-structure',{});r['authenticated']=True
    r['record_id']=identity({k:v for k,v in r.items() if k!='record_id'})
    with pytest.raises(ValueError):d.evaluate(b,body,ledger,[r],[r['record_id']])


def test_equipment_revision_aggregates_six_car_mass_frames_inertia_and_flexibility():
    ctx=context();r=run('installed-equipment',installed_data(ctx),ctx)
    assert r['state']=='supported-for-numerical-scope'
    assert r['proposed_train_mass_properties']['mass_kg']==60.
    assert r['proposed_train_mass_properties']['CG_m']==pytest.approx([-51.75,.5,.5])
    assert r['proposed_per_car_mass_properties']['3']['CG_m']==[.5,.5,.5]
    assert r['proposed_train_mass_properties']['CG_inertia_kg_m2'][2][2]>r['proposed_per_car_mass_properties']['3']['CG_inertia_kg_m2'][2][2]
    assert r['canonical_rematerialization_required'] and r['complete_installed_mass_kg'] is None
    assert r['proposed_installed_mass_kg']==60 and r['physical_accepted'] is False
    assert ctx[0]['mass']['accounted_tare_kg_per_car']==100.


def test_equipment_unknown_joint_is_not_closed_by_asserted_coverage():
    ctx=context();data=installed_data(ctx);data['account_resolution'].pop()
    r=run('installed-equipment',data,ctx)
    assert r['state']=='missing' and r['proposed_installed_mass_kg'] is None
    assert any(o['kind']=='unresolved-parent-accounts' for o in r['open_items'])


@pytest.mark.parametrize('mutation',[
    lambda x:x['net_occurrences'][0].update(mass_kg=0),
    lambda x:x['net_occurrences'][0].update(local_CG_m=[2.,.5,.5]),
    lambda x:x['net_occurrences'][0]['installed_transform'].update(rotation=[[1,1,0],[0,1,0],[0,0,1]]),
    lambda x:x['net_stock_operations'][0].update(removed_volume_m3=.1),
    lambda x:x['net_occurrences'][0].update(local_CG_inertia_kg_m2=[[100.,0,0],[0,100.,0],[0,0,100.]]),
    lambda x:x['net_occurrences'][0].update(local_CG_inertia_kg_m2=[[0.,0,0],[0,0.,0],[0,0,0.]]),
])
def test_invalid_installed_geometry_mass_transform_or_cut_balance_rejects(mutation):
    ctx=context();data=installed_data(ctx);mutation(data)
    with pytest.raises(ValueError):run('installed-equipment',data,ctx)


def test_insufficient_flexibility_and_swept_tool_access_are_failures():
    ctx=context();data=installed_data(ctx)
    data['net_occurrences'][0]['hardware_and_services'][0]['provided_slack_m']=.01
    assert run('installed-equipment',data,ctx)['state']=='fail'
    data=installed_data(ctx);data['net_occurrences'][0]['access']['obstacles_vehicle_m']=[dict(min_m=[.4,.4,.4],max_m=[.6,.6,.6])]
    assert run('installed-equipment',data,ctx)['state']=='fail'


def test_structural_guardband_and_refinement_are_numerical_checks():
    ctx=context();r=run('body-structure',structure_data(ctx),ctx)
    assert r['state']=='supported-for-numerical-scope' and r['checks'][0]['margin']==98.
    assert r['checks'][0]['relative_refinement_change']==pytest.approx(1/101)
    data=structure_data(ctx);data['results'][0]['fine']=250.
    assert run('body-structure',data,ctx)['state']=='fail'
    data=structure_data(ctx);data['results'].pop()
    assert run('body-structure',data,ctx)['state']=='missing'


def test_structural_parent_mass_and_unapproved_limit_cannot_be_inherited():
    ctx=context();data=structure_data(ctx);data['results'][0]['applied_mass_kg_per_car']=0.
    with pytest.raises(ValueError,match='mass scope'):run('body-structure',data,ctx)
    data=structure_data(ctx);data['results'][0]['criterion_record_id']='e'*64
    assert run('body-structure',data,ctx)['state']=='missing'


def test_brake_force_integration_conserves_energy_and_resolves_periodic_heat():
    ctx=context();r=run('independent-brakes',brake_data(ctx),ctx)
    assert r['state']=='supported-for-numerical-scope'
    for row in r['cases']:
        assert row['stopped'] and abs(row['energy_residual_J_per_car'])<1e-6
    case=r['cases'][0]
    expected=20.+(case['heat_J_per_car']/1e6)/(1-exp(-1000*180/1e6))
    assert case['periodic_impulse_temperature_bound_C']==pytest.approx(expected)
    assert r['cases'][-1]['distance_m']==0


def test_weak_brakes_or_uncovered_force_domain_cannot_pass():
    ctx=context();data=brake_data(ctx)
    data['cases'][0]['force_curve']=[dict(time_s=0.,force_N_per_car=0.),dict(time_s=10.,force_N_per_car=0.)]
    assert run('independent-brakes',data,ctx)['state']=='fail'
    data=brake_data(ctx);data['cases'][0]['force_curve'][-1]['time_s']=1.
    with pytest.raises(ValueError,match='whole case'):run('independent-brakes',data,ctx)


def test_site_support_influence_bearing_sliding_and_settlement_are_recomputed():
    ctx=context();r=run('civil-and-site',civil_data(ctx),ctx)
    assert r['state']=='supported-for-numerical-scope'
    assert r['supports'][0]['maximum_train_reaction_N']>0
    assert r['supports'][0]['counted_superstructure_dead_reaction_N']>0
    assert r['supports'][0]['elastic_settlement_m']>0
    data=civil_data(ctx);data['supports'][0]['allowable_bearing_Pa']=1.
    assert run('civil-and-site',data,ctx)['state']=='fail'


def test_civil_wrong_span_or_incomplete_braking_distribution_rejects():
    ctx=context();data=civil_data(ctx);data['supports'][1]['chainage_m']=21.
    with pytest.raises(ValueError,match='stationing'):run('civil-and-site',data,ctx)
    data=civil_data(ctx);data['supports'][0]['braking_distribution_fraction']=0.
    with pytest.raises(ValueError,match='braking-force'):run('civil-and-site',data,ctx)


def test_whole_life_cost_is_disjoint_and_discounted_at_equal_service():
    ctx=context();ctx[2]['unlocated_accounts']=[]
    r=run('whole-life-economics',economy_data(ctx),ctx)
    assert r['state']=='supported-for-numerical-scope'
    assert r['conditional_whole_life_cost_USD']==pytest.approx(600+10/1.05)
    assert r['whole_life_cost_USD'] is None and r['economic_winner'] is None


def test_unpriced_or_unresolved_scope_does_not_become_zero_cost():
    ctx=context();data=economy_data(ctx);data['quotes'][0]['unit_price_USD']=None
    r=run('whole-life-economics',data,ctx)
    assert r['state']=='missing' and r['conditional_whole_life_cost_USD'] is None
    assert r['known_quoted_stock_subtotal_USD']==500.


def test_economics_wrong_unit_quantity_definition_or_double_count_rejects():
    ctx=context();ctx[2]['unlocated_accounts']=[]
    data=economy_data(ctx);data['quotes'][0].update(unit='kg',quantity=1.)
    with pytest.raises(ValueError,match='quantity'):run('whole-life-economics',data,ctx)
    data=economy_data(ctx);data['scope_costs_exclude_occurrence_quotes']=False
    with pytest.raises(ValueError,match='Disjoint'):run('whole-life-economics',data,ctx)
    data=economy_data(ctx);data['service_context']['headway_s']=60.
    with pytest.raises(ValueError,match='service'):run('whole-life-economics',data,ctx)
