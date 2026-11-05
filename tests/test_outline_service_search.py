from copy import deepcopy

import pytest

from engineering.development_baseline import selection
from engineering.design_search import line_benchmark as budget
from engineering.design_search import line_benchmark_service as helper
from engineering.outline import service_search as search
from engineering.station_rail.common import encoded,identity


@pytest.fixture(scope="module")
def inputs():
    brief=dict(route_km=30,stations=12,peak_demand_pphpd=4000,planning_occupancy=.85,
        maximum_headway_s=300,maximum_one_way_minutes=45,operating_hours_per_day=18,
        availability_target=.99,planning_availability_assumption=.99,demand_source="declared-planning-example")
    variables=dict(headways_s=[120,150,180,210,240,300],speeds_kmh=[50,60,72],
        accelerations_m_s2=[.6,.8,1,1.2],dwell_s=[35],headway_quantum_s=10,maximum_screened=128)
    return brief,variables,budget.specification(),selection.load()["vehicle"]


@pytest.fixture(scope="module")
def result(inputs):
    return search.screen(*inputs)


def chosen(result,headway=200,acceleration=1):
    return next(c for c in result["cases"] if c["request"]["requirements"]["headway_s"]==headway
        and c["request"]["design"]["speed_m_s"]==20
        and c["request"]["design"]["acceleration_m_s2"]==acceleration)


def test_demand_derives_new_headway_instead_of_universal_two_minutes(result):
    assert result["generation"]["demand_derived_headway_s"]==200
    assert 200 not in result["generation"]["seed_headways_s"]
    assert len(result["cases"])==84 and result["pending"]==[]
    c=chosen(result)
    assert c["eligible_for_costing"] and c["screen_status"]=="pass"
    assert c["checks"]["capacity"]["planning_offered_pphpd"]==pytest.approx(276*3600/200*.85*.99)
    assert chosen(result,210)["screen_status"]=="fail"
    assert chosen(result,210)["fail_reasons"]==["capacity"]
    assert c["request"]["requirements"]["minimum_capacity_pphpd"]==4000
    assert result["requirements_id"]==result["requirements_contract"]["requirements_id"]
    assert result["requirements_contract"]["maximum_headway_s"]==300
    assert result["requirements_contract"]["planning_availability_assumption"]==.99
    assert result["assumptions"]["reference_120s_is_universal_obligation"] is False
    assert all(result[k] is False for k in search.FLAGS)


def test_headway_reuse_is_exact_and_all_cost_eligible_cases_are_replayed(inputs,result):
    _b,_v,_spec,vehicle=inputs
    assert result["counters"]["physical_profiles_prepared"]==12
    assert result["counters"]["headway_projections_reused"]==72
    assert result["counters"]["independent_helper_replays"]==len(result["eligible_for_costingIDs"])
    for h in (120,150,180,200,210,240,300):
        case=chosen(result,h)
        direct=helper.evaluate(case["request"]["requirements"],case["request"]["design"],vehicle)
        assert encoded(case["service"])==encoded(direct)
    assert result["evaluation_id"]==identity({k:x for k,x in result.items() if k!="evaluation_id"})
    assert budget.PRODUCER in result["source_sha256"]
    assert helper.PRODUCER in result["source_sha256"]


def test_terminal_positions_include_approach_and_departure_without_protection_claim(result):
    case=chosen(result)
    terminal=case["terminal_resource_planning"]
    assert terminal["turnback_only_positions_per_end"]==1
    assert terminal["conservative_serial_resource_s"]>200
    assert terminal["planning_positions_per_end"]==2
    assert terminal["cost_additional_positions"]==0
    assert terminal["actual_turnback_or_headway_qualified"] is False
    assert terminal["shared_throat_conflict_free"] is None
    assert case["known_model_failures"]
    assert all(x["reason"]=="coast_stops_before_receiving_zone" for x in case["known_model_failures"])
    assert case["physical_screen"]=="unknown"
    assert case["service"]["actual_available_force_map"] is None


def test_budget_preserves_cursor_and_same_case_identity_on_continuation(inputs,result):
    b,v,spec,vehicle=inputs
    first=search.screen(b,{**v,"maximum_screened":3},spec,vehicle)
    second=search.screen(b,{**v,"maximum_screened":3,"start_index":3},spec,vehicle)
    assert len(first["cases"])==3 and first["pending"][0]["remaining"]==81
    assert first["pending"][0]["next_index"]==3
    assert second["pending"][0]["next_index"]==6
    assert [c["case_id"] for c in second["cases"]]==[c["case_id"] for c in result["cases"][3:6]]


def test_cable_reset_failure_does_not_discard_other_mechanisms(inputs):
    b,v,spec,vehicle=inputs
    result=search.screen({**b,"peak_demand_pphpd":10000},{**v,"headways_s":[80]},spec,vehicle)
    case=chosen(result,80)
    assert case["screen_status"]=="pass"
    assert case["mechanism_screens"]["cable-capstan"]["status"]=="fail"
    assert case["mechanism_screens"]["cable-capstan"]["minimum_parallel_launch_resources"]==2
    assert case["eligible_mechanisms"]==["common-drive-rollers","compact-launch-LIM"]
    assert case["terminal_resource_planning"]["cost_additional_positions"]>0


def test_availability_is_a_declared_assumption_with_an_independent_target(inputs):
    b,v,spec,vehicle=inputs
    result=search.screen({**b,"planning_availability_assumption":.95},v,spec,vehicle)
    case=chosen(result,200)
    assert "reliability_assumption" in case["fail_reasons"]
    assert result["eligible_for_costingIDs"]==[]
    assert result["assumptions"]["achieved_availability"] is None


def test_expanded_headway_seeds_are_not_required_for_lower_demand(inputs):
    b,v,spec,vehicle=inputs
    result=search.screen({**b,"peak_demand_pphpd":2000},{**v,"headways_s":[120]},spec,vehicle)
    assert result["generation"]["domains"]["headways_s"]==[120,300]
    assert chosen(result,300)["eligible_for_costing"]


def test_search_keeps_input_snapshots_and_does_not_reduce_physical_mass(inputs):
    b,v,spec,vehicle=deepcopy(inputs)
    before=deepcopy((b,v,spec,vehicle))
    result=search.screen(b,{**v,"maximum_screened":2},spec,vehicle)
    assert (b,v,spec,vehicle)==before
    for case in result["cases"]:
        assert case["service"]["accounted_reference_mass_kg_per_car"]==vehicle["mass"]["accounted_cap_loaded_kg_per_car"]
        assert case["service"]["provisional_normal_mass_kg_per_car"]>vehicle["mass"]["accounted_cap_loaded_kg_per_car"]


def test_conflicting_vehicle_source_cannot_be_hidden_by_a_loaded_module_hash(inputs):
    b,v,spec,vehicle=deepcopy(inputs)
    path="engineering/station_rail/electrical.py"
    assert path in vehicle["source_sha256"]
    vehicle["source_sha256"][path]="0"*64
    vehicle.pop("evaluation_id")
    vehicle["evaluation_id"]=identity(vehicle)
    with pytest.raises(ValueError,match="Vehicle and loaded source epochs conflict"):
        search.screen(b,{**v,"maximum_screened":1},spec,vehicle)


@pytest.mark.parametrize("section,key,value",[("b","planning_occupancy",0),("b","availability_target",1.1),
    ("b","peak_demand_pphpd",float("nan")),("b","stations",1),("v","headway_quantum_s",0),
    ("v","maximum_screened",129),("v","headways_s",[float("inf")])])
def test_invalid_briefs_and_unbounded_budgets_are_rejected(inputs,section,key,value):
    b,v,spec,vehicle=deepcopy(inputs);(b if section=="b" else v)[key]=value
    with pytest.raises(ValueError):search.screen(b,v,spec,vehicle)


def test_braking_and_jerk_are_distinct_profile_variables_without_force_admission(inputs):
    b,v,spec,vehicle=inputs
    variables={**v,'headways_s':[180,200],'speeds_kmh':[72.],'accelerations_m_s2':[.8],
        'service_decelerations_m_s2':[.6,.9],'jerks_m_s3':[.25,.5]}
    result=search.screen(b,variables,spec,vehicle)
    assert result['counters']['physical_profiles_prepared']==4
    assert result['counters']['headway_projections_reused']==4
    assert len(result['cases'])==8
    by={(c['request']['design']['service_deceleration_m_s2'],c['request']['design']['jerk_m_s3'],
         c['request']['requirements']['headway_s']):c for c in result['cases']}
    a=by[.6,.5,200];braked=by[.9,.5,200];jerked=by[.6,.25,200];headway=by[.6,.5,180]
    assert a['service']['jerk_launch_distance_m']==braked['service']['jerk_launch_distance_m']
    assert a['service']['one_way_s']!=braked['service']['one_way_s']
    assert a['service']['jerk_launch_distance_m']!=jerked['service']['jerk_launch_distance_m']
    assert a['service']['jerk_launch_distance_m']==headway['service']['jerk_launch_distance_m']
    assert len({c['case_id'] for c in (a,braked,jerked,headway)})==4
    assert all(c['service']['actual_available_force_map'] is None for c in result['cases'])
    for c in result['cases']:
        direct=helper.evaluate(c['request']['requirements'],c['request']['design'],vehicle)
        assert encoded(c['service'])==encoded(direct)


def test_demand_changes_requirement_identity_and_derived_headway_not_vehicle_mass(inputs):
    b,v,spec,vehicle=inputs
    variables={**v,'speeds_kmh':[72.],'accelerations_m_s2':[.8],'headways_s':[200]}
    a=search.screen(b,variables,spec,vehicle)
    other=search.screen({**b,'peak_demand_pphpd':2000},variables,spec,vehicle)
    assert a['requirements_id']!=other['requirements_id']
    assert other['generation']['demand_derived_headway_s']==300
    first=next(c for c in a['cases'] if c['request']['requirements']['headway_s']==200)
    second=next(c for c in other['cases'] if c['request']['requirements']['headway_s']==200)
    assert first['case_id']!=second['case_id']
    assert first['service']['provisional_normal_mass_kg_per_car']==second['service']['provisional_normal_mass_kg_per_car']
    assert first['service']['jerk_launch_distance_m']==second['service']['jerk_launch_distance_m']


def test_unknown_design_variables_are_rejected_instead_of_silently_ignored(inputs):
    b,v,spec,vehicle=inputs
    with pytest.raises(ValueError,match='Unknown or untyped'):
        search.screen(b,{**v,'jerk_m_s3':[.25]},spec,vehicle)
    with pytest.raises(ValueError):search.screen(b,{**v,'jerks_m_s3':[0.]},spec,vehicle)
