"""Independent mechanics and scope controls for interrupted reachability."""
from copy import deepcopy
from math import log1p,atan,sqrt
from pathlib import Path
import json
import pytest
from engineering.design_search import architecture_reach_closure as c
from engineering.station_rail.common import digest,identity


def inputs(**changes):
    value=dict(distance_m=2000.,mass_kg_per_car=1000.,rotating_mass_kg_per_car=500.,
        rolling_coefficient=0.,constant_resistance_N_per_car=100.,
        aero_coefficient_N_s2_m2=0.,headwind_m_s=0.,grade_fraction_uphill=0.,powered_windows=[])
    value.update(changes);return value


def test_constant_resistance_matches_work_energy_and_rotational_inertia():
    b=c.coast_bound(inputs(),100.,10.)
    assert b['remaining_kinetic_energy_J_per_car']==75000.
    assert b['resistance_floor_N_per_car']==100.
    assert b['additional_coast_distance_upper_m']==750.
    assert b['additional_coast_time_upper_s']==150.
    assert b['stop_position_upper_m']==850.
    assert b['target_infeasibility_proven']
    grade=c.coast_bound(inputs(grade_fraction_uphill=.01),100.,10.)
    assert grade['resistance_floor_N_per_car']==pytest.approx(1000*9.80665*.01+100)


def test_positive_quadratic_drag_has_a_shorter_exact_coast_than_the_bound():
    k=2.;b=c.coast_bound(inputs(aero_coefficient_N_s2_m2=k),100.,10.)
    exact_distance=1500/(2*k)*log1p(k*10**2/100)
    exact_time=1500/sqrt(100*k)*atan(10*sqrt(k/100))
    assert exact_distance<b['additional_coast_distance_upper_m']
    assert exact_time<b['additional_coast_time_upper_s']
    wind=c.coast_bound(inputs(aero_coefficient_N_s2_m2=k,headwind_m_s=3.),100.,10.)
    assert wind['resistance_floor_N_per_car']==118.


def test_reachable_booster_active_power_downhill_and_rounding_cannot_prove_failure():
    future=c.coast_bound(inputs(powered_windows=[[200,300]]),100.,10.)
    assert future['next_target_m']==200 and not future['target_infeasibility_proven']
    distant=c.coast_bound(inputs(powered_windows=[[1000,1100]]),100.,10.)
    assert distant['next_target_m']==1000 and distant['target_infeasibility_proven']
    active=c.coast_bound(inputs(powered_windows=[[0,200]]),100.,10.)
    assert not active['applicable'] and active['additional_coast_distance_upper_m'] is None
    downhill=c.coast_bound(inputs(grade_fraction_uphill=-.02),100.,10.)
    assert not downhill['applicable'] and not downhill['target_infeasibility_proven']
    for distance in (850.,850.+c.TOLERANCE_M/2):
        assert not c.coast_bound(inputs(distance_m=distance),100.,10.)['target_infeasibility_proven']
    assert c.coast_bound(inputs(distance_m=850.+2*c.TOLERANCE_M),100.,10.)['target_infeasibility_proven']
    with pytest.raises(ValueError):c.coast_bound(inputs(headwind_m_s=float('nan')),100.,10.)
    missing=inputs();missing.pop('rolling_coefficient')
    with pytest.raises(ValueError):c.coast_bound(missing,100.,10.)


def test_published_resource_cases_keep_the_original_interruption_and_identities(tmp_path):
    parent=c.ROOT/c.INPUT;before={name:digest(parent/name) for name in ('manifest.json','campaign.json.gz')}
    out=tmp_path/'supplement';r=c.build(output=out)
    assert r['resource_hold_count']==r['analytically_infeasible_cases']==3
    assert r['unresolved_reachability_cases']==0 and r['original_traces_completed'] is False
    data=json.loads((out/'result.json').read_bytes())
    assert {row['cars'] for row in data['rows']}=={4,6,8}
    assert len({row['parent_raw_demand_id'] for row in data['rows']})==3
    for row in data['rows']:
        assert row['source_execution']=='interrupted' and row['source_runtime_s']==row['source_maximum_runtime_s']==600.
        assert row['source_numerical_validity']=='valid' and row['state_error_enclosure_available'] is False
        assert row['evaluation_id']!=row['parent_evaluation_id']
        assert row['bound']['additional_coast_distance_upper_m']==pytest.approx(7.461496581028011)
        assert row['bound']['stop_position_upper_m']==pytest.approx(2554.1783056353465)
        assert row['bound']['shortfall_to_next_target_lower_m']==pytest.approx(445.8216943646533)
        assert all(row[key] is False for key in c.FLAGS)
    assert before=={name:digest(parent/name) for name in before}
    assert c.verify(output=out)['closure_id']==r['closure_id']
    (out/'result.json').write_text('{}')
    with pytest.raises(ValueError,match='payload differs'):c.verify(output=out)
