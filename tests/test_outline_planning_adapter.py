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
    for name in adapter._LOADED:
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
    services=seal(dict(line_services=[duty]))
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
        seed_id=seed['seed_id'],source_outline_evaluation_id=seed['source_outline_evaluation_id'],actor='Fixture planner',edits=edits)


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
        adapter.apply_edits(base,bundle(base,[dict(kind='retire-stop',line='L',stop='complex-ab')]),root)


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
