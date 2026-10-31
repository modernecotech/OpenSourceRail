"""Declared LIM assumptions exercise journeys without becoming physical evidence."""
import gzip
import json
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.design_search import conditional_journey_study as study


def _bundle():
    bundles=json.loads(gzip.decompress((ROOT/'docs/design-engine/coupled-railway/bundles.json.gz').read_bytes()))
    return next(b for b in bundles
        if b['candidate_id']=='1e8d1d7c394fc0bdbd47e34fb21d413ebc34a49576bad60b31b254bd635dfb68')


def test_current_p1_study_runs_declared_low_base_high_maps_without_promoting_them():
    result=study.evaluate_bundle(_bundle(),study.specification())

    assert [case['case'] for case in result['cases']]==['low','base','high']
    low,base,high=result['cases']
    assert low['trajectory_summary']['maximum_positive_acceleration_m_s2']<0.4
    assert low['trajectory_summary']['elapsed_s']>base['trajectory_summary']['elapsed_s']
    assert base['trajectory_summary']['berth_stop'] is True
    assert high['trajectory_summary']['state']=='controller-speed-limit'
    assert result['service_capacity_arithmetic']['arithmetic_places_per_hour_direction']==8280
    assert result['service_capacity_arithmetic']['headway_and_capacity_physically_demonstrated'] is False
    for case in result['cases']:
        assert case['force_map']['evidence_kind']=='synthetic-method-test'
        assert case['forward']['test_only'] is True
        assert case['forward']['available_motor_map_id'] is None
        assert case['forward']['physical_journey_completed'] is False
        assert abs(case['trajectory_summary']['energy_residual_J'])<1e-5
        assert abs(case['trajectory_summary']['electrical_work_residual_J'])<1e-5
    assert result['physical_journey_completed'] is False
    assert result['engineering_validated'] is False
    assert result['approved_for_manufacture_or_operation'] is False


def test_study_keeps_both_p1_motor_definitions_per_body():
    _,_,bundles=study._campaign(ROOT)
    assert len(bundles)==28
    assert len({b['body_candidate_id'] for b in bundles})==14
    for body_id in {b['body_candidate_id'] for b in bundles}:
        variants=[b for b in bundles if b['body_candidate_id']==body_id]
        assert len(variants)==2
        assert len({b['propulsion_component_id'] for b in variants})==2
