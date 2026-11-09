from copy import deepcopy

import pytest

from engineering.railway_project import compact_drive_corridor as probe
from engineering.station_rail.common import identity


def body():
    p={'candidate_family':'compact-drive-test','drive':'in-body'}
    v=dict(schema='osr-vehicle-installation/1',physical_definition=p,
        candidate_id=identity(p),parent_candidate_id=probe.PARENT,
        layout_definition_complete=True,installed_mass_complete=False,
        evaluation_id='pending')
    v['evaluation_id']=identity({k:x for k,x in v.items() if k!='evaluation_id'})
    return v


def test_source_candidate_remains_distinct_and_all_unknowns_stay_open():
    v=probe.packet(body(),route_records=[],stage_records=[],holds=['drive duty inputs absent'],
        source_sha256={'design.py':'a'*64})
    assert probe.verify(v)
    assert v['candidate_identity']['body_candidate_id'] not in (probe.SEED,probe.RECOVERY)
    assert v['body_definition_complete'] is True and v['installed_mass_complete'] is False
    assert v['service']['normal_passenger_capacity_per_train'] is None
    assert v['service']['grade_profile'] is None
    assert v['service']['charging_duty'] is None
    assert v['infrastructure']['platforms'] is None
    assert v['costs']['scope_count']==14 and v['costs']['scope_costs_USD'] is None
    assert v['costs']['scalar_cost_per_km_used'] is False
    assert all(v[k] is False for k in probe.FLAGS)


def test_cross_candidate_bundle_is_rejected():
    b=body()
    fake=dict(schema='osr-mapped-railway-project-bundle/1',candidate_id='b'*64,
        evaluation_id='c'*64,physical_definition=dict(body_candidate_id='d'*64),body_evaluation_id='e'*64)
    with pytest.raises(ValueError,match='mixed with another body'):
        probe.packet(b,route_records=[],stage_records=[dict(kind='project-bundle',packet=fake)],
            holds=[],source_sha256={})


def test_source_manifest_rejects_non_sha_values():
    with pytest.raises(ValueError,match='lowercase SHA-256'):
        probe.packet(body(),route_records=[],stage_records=[],holds=[],source_sha256={'commit':'abc'})


def test_false_acceptance_or_completion_cannot_be_resealed():
    v=probe.packet(body(),route_records=[],stage_records=[],holds=['held'],source_sha256={})
    v['physical_accepted']=True
    v['evaluation_id']=identity({k:x for k,x in v.items() if k!='evaluation_id'})
    with pytest.raises(ValueError,match='cannot grant acceptance'):
        probe.verify(v)
