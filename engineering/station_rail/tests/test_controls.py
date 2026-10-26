"""Reject corrupted outputs even when their self-contained hashes are recomputed."""
from copy import deepcopy
import json
import pytest
from engineering.station_rail import controls
from engineering.station_rail.common import encoded,identity,digest
from engineering.station_rail import FLAGS


def record():
    return {key:str(i+1)*64 for i,key in enumerate((*controls.IDS,'evaluation_id'))}


def make_package(path,monkeypatch):
    monkeypatch.setattr(controls,'sources',lambda root:{'fixture':'source'})
    for row in controls.requests(record()):
        (path/(row['case']+'.request.json')).write_bytes(encoded(row['request']))
        (path/(row['case']+'.stdout.json')).write_bytes(encoded(controls.expected_response(row)))
        (path/(row['case']+'.stderr')).write_bytes(b'')
    for name in ('regressions.stdout','regressions.stderr','build.stdout','build.stderr'):
        (path/name).write_bytes(b'synthetic verification test log')
    (path/'result.json').write_bytes(encoded(controls.result_definition(record())))
    reseal(path)


def reseal(path):
    value=dict(source_sha256={'fixture':'source'},files_sha256={p.name:digest(p)
        for p in path.iterdir() if p.is_file() and p.name!='manifest.json'},**FLAGS)
    value['manifest_id']=identity(value)
    (path/'manifest.json').write_bytes(encoded(value))


def test_complete_contract_inventory_and_powered_vs_coast_semantics():
    rows={row['case']:row for row in controls.requests(record())}
    failed=controls.expected_response(rows['launch_power_lost'])
    coast=controls.expected_response(rows['coasting_without_departure_power'])
    assert failed['outcome']['mechanical_brake']=='Emergency'
    assert coast['outcome']['mechanical_brake']=='Release'
    assert coast['outcome']['station_thrust_inhibit'] is True
    assert len(rows)==20


@pytest.mark.parametrize('field,value',[
    ('support_power_required',True),('station_thrust_inhibit',True),
    ('recovery_required_if_off_zone',False),('launch_permissive',1),
])
def test_hash_repaired_wrong_predicate_is_rejected(tmp_path,monkeypatch,field,value):
    make_package(tmp_path,monkeypatch)
    path=tmp_path/'nominal_predicates.stdout.json'
    actual=json.loads(path.read_bytes());actual['outcome'][field]=value
    path.write_bytes(encoded(actual));reseal(tmp_path)
    with pytest.raises(ValueError,match='complete wheel disposition'):
        controls.verify(tmp_path,record())


@pytest.mark.parametrize('change',[{'controls':999},{'rows':[]},
    {'candidate_id':'0'*64},{'all_controls_pass':False},
    {'physical_train_simulated':True},{'operating_release':True}])
def test_hash_repaired_summary_cannot_forge_execution_or_acceptance(tmp_path,monkeypatch,change):
    make_package(tmp_path,monkeypatch)
    path=tmp_path/'result.json';actual=json.loads(path.read_bytes());actual.update(change)
    path.write_bytes(encoded(actual));reseal(tmp_path)
    with pytest.raises(ValueError):controls.verify(tmp_path,record())


def test_well_formed_packet_verifies_and_missing_or_extra_case_cannot_hide(tmp_path,monkeypatch):
    make_package(tmp_path,monkeypatch)
    assert controls.verify(tmp_path,record())['controls']==20
    (tmp_path/'invented-case.stdout.json').write_bytes(b'{}\n');reseal(tmp_path)
    with pytest.raises(ValueError,match='file inventory'):
        controls.verify(tmp_path,record())
