from copy import deepcopy
from math import ceil
from pathlib import Path
import gzip
import json

import pytest

from engineering.outline import planning_adapter as adapter,planning_geometry as geometry,revision_service
from engineering.development_baseline import planning
from engineering.station_rail.common import digest,identity,encoded


def seal(value,key='evaluation_id'):
    value.pop(key,None);value[key]=identity(value);return value


@pytest.fixture
def fixture(tmp_path,monkeypatch):
    root=tmp_path
    source=root/'fixture-source.json';source.write_bytes(b'{}\n')
    sources={'fixture-source.json':digest(source)}
    for name in {**adapter._LOADED,**revision_service._LOADED}:
        target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((Path(__file__).resolve().parents[1]/name).read_bytes())
    length=planning._distance([0.,0.],[.02,0.]);coordinates=[[0.,0.],[.02,0.]]
    stops=[dict(id='a',chainage_m=0.,lon=0.,lat=0.,dwell_s=35.),
        dict(id='b',chainage_m=20.,lon=.02*20/length,lat=0.,dwell_s=35.),
        dict(id='c',chainage_m=length,lon=.02,lat=0.,dwell_s=35.)]
    original=dict(schema='osr-city-outline-input/1',city=dict(slug='fixture',name='Fixture',country='IQ'),
        reference_candidate_ids=dict(candidate_id='a'*64),selection_id='b'*64,od=[],interchanges=[],
        lines=[dict(line_id='L',shape='radial',route_m=length,coordinates=coordinates,
            coordinate_chainages_m=[0.,length],operational_route_m=length,stops=stops)],
        civil_segments=[dict(line_id='L',**{'class':'elevated'},from_m=0.,to_m=length)],source_sha256=sources)
    seal(original,'input_id')
    ops=[dict(stops[0],id='complex-ab'),deepcopy(stops[2])]
    repair=dict(complexes=[dict(operational_stop_id='complex-ab',original_stop_ids=['a','b'],
        maximum_added_walk_m=20.,summed_added_walk_m=20.,additional_shared_platform_length_m=40.),
        dict(operational_stop_id='c',original_stop_ids=['c'],maximum_added_walk_m=0.,summed_added_walk_m=0.,additional_shared_platform_length_m=0.)])
    duty=dict(line_id='L',operational_stops=ops,station_repair=repair,
        service=dict(stop_dwell_s=[35.,35.]),requirements=dict(headway_s=200.),design=dict(speed_m_s=20.))
    services=seal(dict(city_input_id=original['input_id'],line_services=[duty]))
    seed=dict(schema=adapter.SEED_SCHEMA,city_slug='fixture',rules=dict(peak_demand_pphpd=4000.,
        planning_occupancy=.85,planning_availability_assumption=.99,maximum_headway_s=300.),
        selected_alignment_id='1'*64,selected_alignment_kind='original',selected_city_input_id=original['input_id'],
        selected_service_evaluation_id=services['evaluation_id'],source_outline_evaluation_id='2'*64,
        source_cost_evaluation_id='3'*64,research_configuration_id='4'*64,
        reference_candidate_ids=original['reference_candidate_ids'],source_sha256=sources,source_result_sha256='5'*64,
        **adapter.FLAGS)
    seal(seed,'seed_id')
    detail=dict(city={'slug':'fixture'},planning_seed=seed,selected_alignment_id=seed['selected_alignment_id'],
        evaluation_id=seed['source_outline_evaluation_id'],research_configuration_id=seed['research_configuration_id'],
        full_result_sha256=seed['source_result_sha256'],**adapter.FLAGS)
    folder=root/adapter.PUBLICATION;(folder/'cities').mkdir(parents=True)
    path=folder/'cities/fixture.json.gz';path.write_bytes(planning._gzip_member(encoded(detail)))
    manifest=seal(dict(schema='osr-outline-completion-publication/2',files_sha256={'cities/fixture.json.gz':digest(path)}),'manifest_id')
    (folder/'manifest.json').write_bytes(encoded(manifest))
    monkeypatch.setattr(adapter,'_reconstruct',lambda *a,**kw:(deepcopy(original),deepcopy(services)))
    return root,seed,original,services,adapter.export_plan(seed,root)


def bundle(base,edits):
    seed=base['outline_context']['seed']
    return dict(schema=adapter.EDIT_SCHEMA,city=base['city'],base_revision_sha256=base['revision_sha256'],
        seed_id=seed['seed_id'],source_outline_evaluation_id=base['source_outline_evaluation_id'],actor='Fixture planner',edits=edits)


def test_seed_requires_current_publication_membership_not_just_a_new_hash(fixture):
    root,seed,_,_,_=fixture
    forged=deepcopy(seed);forged['research_configuration_id']='f'*64;seal(forged,'seed_id')
    with pytest.raises(planning.PlanningError,match='currently published'):adapter.validate_seed(forged,root)
    (root/'fixture-source.json').write_bytes(b'{"changed":true}\n')
    with pytest.raises(planning.PlanningError,match='source changed'):adapter.validate_seed(seed,root)


def test_operational_import_retains_raw_access_and_reexpands_no_edit_once(fixture):
    root,seed,original,_,base=fixture
    assert [x['id'] for x in base['lines'][0]['stops']]==['complex-ab','c']
    assert base['outline_context']['city_input_template']==original
    result=adapter.apply_edits(base,bundle(base,[]),root)
    actual=result['city_input']['lines'][0]
    assert [x['id'] for x in actual['stops']]==['a','b','c']
    assert [x['chainage_m'] for x in actual['stops']]==[0.,20.,original['lines'][0]['route_m']]
    assert 'alignment_hypothesis' not in result['city_input']
    assert result['access_screen']['additional_access_walkway_m']==0
    assert result['source_outline_evaluation_id']==seed['source_outline_evaluation_id']
    assert all(result[k] is False for k in adapter.FLAGS)


def test_cost_verification_does_not_change_canonical_editable_base(fixture):
    root,seed,_,_,_=fixture
    a=adapter.export_plan(seed,root,verify_cost=False);b=adapter.export_plan(seed,root,verify_cost=True)
    assert encoded(a)==encoded(b)
    adapter.apply_edits(b,bundle(b,[]),root)


def test_only_nanometre_endpoint_representation_error_is_normalized(fixture):
    _,seed,city,services,_=fixture
    city=deepcopy(city);services=deepcopy(services);length=city['lines'][0]['route_m']
    services['line_services'][0]['operational_stops'][-1]['chainage_m']=length+1e-8
    plan=adapter._build_plan(seed,city,services)
    assert plan['lines'][0]['stops'][-1]['chainage_m']==length
    assert plan['outline_context']['endpoint_chainage_normalizations'][0]['delta_m']<0
    assert services['line_services'][0]['operational_stops'][-1]['chainage_m']>length
    services['line_services'][0]['operational_stops'][-1]['chainage_m']=length+.001
    with pytest.raises(planning.PlanningError,match='chainage'):adapter._build_plan(seed,city,services)


def test_editable_route_accumulation_epsilon_does_not_rescale_source_geometry(fixture):
    _,seed,city,services,_=fixture
    city=deepcopy(city);services=deepcopy(services);actual=city['lines'][0]['route_m']
    city['lines'][0]['route_m']=actual+1e-8
    services['line_services'][0]['operational_stops'][-1]['chainage_m']=actual+1e-8
    base=adapter._build_plan(seed,city,services)
    assert base['lines'][0]['length_m']==actual
    assert base['lines'][0]['stops'][-1]['chainage_m']==actual
    assert base['outline_context']['city_input_template']['lines'][0]['route_m']==actual+1e-8
    assert base['outline_context']['route_length_normalizations']
    restored,walk,_=adapter._line_input(city['lines'][0],base['lines'][0],services['line_services'][0])
    assert restored['route_m']==actual+1e-8 and restored['stops']==city['lines'][0]['stops'] and walk==0


def test_move_complex_adds_declared_access_cost_and_preserves_original_marker_sources(fixture):
    root,_,original,_,base=fixture
    result=adapter.apply_edits(base,bundle(base,[dict(kind='move-stop',line='L',stop='complex-ab',chainage_m=100.)]),root)
    assert original['lines'][0]['stops'][0]['chainage_m']==0
    assert [x['chainage_m'] for x in result['city_input']['lines'][0]['stops']][:2]==[100.,120.]
    assert result['access_screen']['additional_access_walkway_m']==pytest.approx(250.)
    assert result['city_input']['alignment_hypothesis']['risk_quantities']['additional_access_walkway_m']==pytest.approx(250.)


def test_large_access_failure_stays_priced_research_instead_of_erasing_original_markers(fixture):
    root,_,_,_,base=fixture
    r=adapter.apply_edits(base,bundle(base,[dict(kind='move-stop',line='L',stop='complex-ab',chainage_m=1000.)]),root)
    assert r['access_screen']['status']=='fail'
    assert r['city_input']['alignment_hypothesis']['risk_quantities']['additional_access_walkway_m']>0


def test_explicit_geometry_replacement_has_explicit_stop_positions_and_civil_assumptions(fixture):
    root,_,_,_,base=fixture
    coordinates=[[0.,0.],[.01,.005],[.02,0.]];length=geometry.route(coordinates,'radial')[-1]
    edit=dict(kind='replace-line-geometry',line='L',coordinates=coordinates,shape='radial',design_speed_cap_m_s=12.,
        stops=[dict(id='complex-ab',chainage_m=0.,dwell_s=35.),dict(id='c',chainage_m=length,dwell_s=35.)],reason='Declared detour study')
    result=adapter.apply_edits(base,bundle(base,[edit]),root)
    assert result['city_input']['lines'][0]['coordinates']==coordinates
    assert result['city_input']['lines'][0]['route_m']==pytest.approx(length)
    assert result['city_input']['civil_segments'][0]['to_m']==pytest.approx(length)
    assert result['city_input']['civil_segments'][0]['assumed'] is True
    assert result['city_input']['alignment_hypothesis']['risk_quantities']['additional_row_area_m2']>0
    assert base['lines'][0]['coordinates']!=coordinates


def test_stale_bundle_duplicate_stop_bad_ring_offbounds_or_od_orphan_refused(fixture):
    root,_,_,_,base=fixture
    stale=bundle(base,[]);stale['base_revision_sha256']='0'*64
    with pytest.raises(planning.PlanningError,match='Stale'):adapter.apply_edits(base,stale,root)
    with pytest.raises(planning.PlanningError,match='closed'):
        geometry.route([[0.,0.],[.01,0.]],'ring')
    with pytest.raises(planning.PlanningError,match='longitude'):
        geometry.route([[0.,0.],[200.,0.]],'radial')
    base=deepcopy(base);base['od']=[dict(origin='complex-ab',destination='c',trips_per_day=10,basis='synthetic')]
    base['lines'][0]['stops'].insert(1,dict(id='middle',chainage_m=1000.,lon=.02*1000/base['lines'][0]['length_m'],lat=0.,dwell_s=35.))
    base['revision_sha256']=planning.digest_json({k:v for k,v in base.items() if k!='revision_sha256'})
    with pytest.raises(planning.PlanningError,match='OD'):
        adapter.apply_edits(base,bundle(base,[dict(kind='retire-stop',line='L',stop='complex-ab')]),root,
            trusted_base_sha256=planning.digest_bytes(encoded(base)))


def service(ring=False):
    return seal(dict(requirements=dict(headway_s=200.,stations=3),design=dict(reserve_fraction=.15,terminal_turnback_s=0 if ring else 180),
        round_trip_s=900 if ring else 1800,fleet_direction_multiplier=2 if ring else 1,
        normal_places_per_train=276,train_km_per_day=1000.,departures_per_day=2000.,
        berth_resource_s=250.,baseline_budget_positions_per_end=0 if ring else 2,
        tail_clearance_s_jerk_bound=30.,mechanical_work_kwh_per_departure=9.))


@pytest.mark.parametrize('ring',[False,True])
def test_explicit_headway_changes_fleet_capacity_km_resources_not_physical_models(ring):
    old=service(ring);request=dict(headway_s=140.,legs=[dict(braking_time_s=60.)])
    new=revision_service.project(old,request,dict(planning_occupancy=.85,planning_availability_assumption=.99))
    active=(2 if ring else 1)*ceil(old['round_trip_s']/140)
    assert new['active_trainsets']==active and new['total_trainsets']==active+ceil(active*.15)
    assert new['capacity_pphpd']==pytest.approx(276*3600/140)
    assert new['train_km_per_day']==pytest.approx(1000*200/140)
    assert new['minimum_parallel_berth_resources']==2 and new['additional_berth_edges']==6
    assert new['mechanical_work_kwh_per_departure']==old['mechanical_work_kwh_per_departure']
    assert old['requirements']['headway_s']==200
    assert new['evaluation_id']==identity({k:v for k,v in new.items() if k!='evaluation_id'})


def test_projection_keeps_under_capacity_request_instead_of_silently_optimizing():
    new=revision_service.project(service(),dict(headway_s=300,legs=[dict(braking_time_s=60)]),{})
    assert new['requirements']['headway_s']==300
    assert new['planning_usable_capacity_pphpd']<4000


def test_source_map_collision_is_rejected():
    with pytest.raises(planning.PlanningError,match='Mixed'):
        adapter.merge_sources({'same.py':'a'*64},{'same.py':'b'*64})


def test_resealed_untracked_base_is_not_accepted_without_server_manifest_hash(fixture):
    root,_,_,_,base=fixture
    forged=deepcopy(base);forged['lines'][0]['headway_s']=140
    forged['revision_sha256']=planning.digest_json({k:v for k,v in forged.items() if k!='revision_sha256'})
    with pytest.raises(planning.PlanningError,match='server-verified'):
        adapter.apply_edits(forged,bundle(forged,[]),root)
    with pytest.raises(planning.PlanningError,match='artifact hash'):
        adapter.apply_edits(forged,bundle(forged,[]),root,trusted_base_sha256='0'*64)


def test_server_verified_different_study_becomes_exact_editable_base(fixture):
    root,seed,city,services,_=fixture
    services=deepcopy(services);services['line_services'][0]['requirements']['headway_s']=150.;seal(services)
    cost=seal(dict(city_input_id=city['input_id'],source_sha256=city['source_sha256']))
    record=seal(dict(geometry_and_service=city,service_evaluation=services,cost=cost,
        reference_candidate_ids=city['reference_candidate_ids'],research_configuration_id='e'*64,
        selected_alignment_id='f'*64,selected_alignment_kind='server-study',
        policy={**seed['rules'],'peak_demand_pphpd':5000},source_sha256=city['source_sha256'],**adapter.FLAGS))
    h=planning.digest_bytes(encoded(record))
    base=adapter.plan_from_record(seed,record,root,trusted_record_sha256=h,design={'acceleration_m_s2':1.2})
    assert base['lines'][0]['headway_s']==150
    assert base['source_outline_evaluation_id']==record['evaluation_id']
    assert base['source_cost_evaluation_id']==cost['evaluation_id']
    assert base['research_configuration_id']=='e'*64 and base['source_alignment_id']=='f'*64
    result=adapter.apply_edits(base,bundle(base,[]),root,trusted_base_sha256=planning.digest_bytes(encoded(base)))
    assert result['requirements']['peak_demand_pphpd']==5000
    assert result['source_outline_evaluation_id']==record['evaluation_id']
    assert result['requested_design']['acceleration_m_s2']==1.2
    assert result['research_configuration_parent_id']=='e'*64


def test_retired_complex_keeps_access_aliases_and_edited_od_proposals(fixture):
    root,_,_,_,base=fixture
    base=deepcopy(base);base['outline_context']['city_input_template']['interchanges']=[dict(id='transfer',platforms=['a','c'])]
    base['revision_sha256']=planning.digest_json({k:v for k,v in base.items() if k!='revision_sha256'})
    edits=[dict(kind='add-stop',line='L',stop='middle',chainage_m=100.,dwell_s=35.),
        dict(kind='retire-stop',line='L',stop='complex-ab'),
        dict(kind='set-od',rows=[dict(origin='middle',destination='c',trips_per_day=100,basis='synthetic')])]
    result=adapter.apply_edits(base,bundle(base,edits),root,trusted_base_sha256=planning.digest_bytes(encoded(base)))
    assert [s['id'] for s in result['city_input']['lines'][0]['stops']]==['middle','c']
    assert result['city_input']['interchanges'][0]['source_platform_ids']==['a','c']
    assert result['city_input']['interchanges'][0]['platforms']==['middle','c']
    assert result['city_input']['od']==result['plan']['od']
    assert result['access_screen']['additional_access_walkway_m']>0


def test_revision_evaluation_keeps_priced_capacity_failure_and_explicit_dwell_amendment(fixture,monkeypatch):
    root,_,_,_,base=fixture
    revision=adapter.apply_edits(base,bundle(base,[dict(kind='set-service',line='L',headway_s=300.,dwell_s=20.)]),root)
    original=service();original['stop_dwell_s']=[40.,40.,40.];seal(original)
    baseline=seal(dict(city_input_id=revision['city_input']['input_id'],line_services=[seal(dict(line_id='L',
        service=original,requirements=original['requirements'],legs=[dict(braking_time_s=60.)],
        source_sha256=revision['source_sha256']))],summary={},source_sha256=revision['source_sha256']))
    before=deepcopy(baseline)
    monkeypatch.setattr(revision_service.city_service,'evaluate',lambda *a,**kw:deepcopy(baseline))
    result=revision_service.evaluate(revision,{}, {},root)
    assert result['functional_pass'] is False and result['provisional_costing_permitted'] is True
    assert result['line_services'][0]['service']['requirements']['headway_s']==300
    assert result['functional_checks'][0]['capacity_pass'] is False
    assert result['line_services'][0]['dwell_adjustment']['requested_minimum_dwell_s']==20
    assert result['line_services'][0]['dwell_adjustment']['automatic_adjustment_applied'] is True
    assert baseline==before
