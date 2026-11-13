"""Explicit body custody at the railway closure research boundary."""
import gzip
import json
from pathlib import Path

import pytest

from engineering.railway_closure import body_input, coordinator
from engineering.station_rail.common import encoded, identity


def _packet(tmp_path, *, candidate=None, changed_source=False, released=False):
    source = tmp_path / 'source.json'
    source.write_bytes(b'physical source')
    physical = {'schema': 'test-installed-physical/1', 'door_count': 12,
                'track_interface': {'schema': 'test-track-interface/1'}}
    cid = identity(physical)
    body = dict(schema='osr-vehicle-installation/1', candidate_id=candidate or cid,
                physical_definition=physical,
                parent_bundle_id='1' * 64,
                parts=[{'assembly_id': 'body/test'}], patterns=[{'id': 'body/test/0'}],
                materials=[{'id': 'test'}],
                mass_scenarios=[dict(name='normal-base', case='base',
                    train_mass_kg=1000., CG_m=[0., 0., 0.],
                    inertia_about_CG_kg_m2=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]],
                    lateral_acceleration_m_s2=.5,
                    axles=[{'x_m':float(i), 'vertical_force_N':100.} for i in range(24)])],
                source_component_types=1, proposed_component_types=1,
                total_occurrences=1,
                nominal_part_mass_kg={'low':1.,'base':1.,'high':1.},
                direct_parts_process_usd={'low':1.,'base':1.,'high':1.},
                interface_screens={},
                policy={'evaluation':{'unlocated_installation_reserve_kg':
                    {'low':1.,'base':1.,'high':1.}}},
                source_sha256={'source.json': body_input.file_sha256(source)},
                engineering_accepted=released, physical_accepted=False,
                manufacturing_release=False, operating_release=False,
                movement_authority=False, selected_reference_changed=False)
    body['evaluation_id'] = identity(body)
    archive = tmp_path / 'body.json.gz'
    archive.write_bytes(gzip.compress(encoded(body), mtime=0))
    if changed_source:
        source.write_bytes(b'changed')
    return archive, cid


def test_explicit_current_body_has_separate_physical_and_file_identities(tmp_path):
    archive, cid = _packet(tmp_path)
    body, receipt = body_input.load(archive, expected_candidate_id=cid, root=tmp_path)
    assert receipt['body_candidate_id'] == cid
    assert receipt['body_evaluation_id'] == body['evaluation_id']
    assert receipt['input_sha256'] == body_input.file_sha256(archive)
    assert receipt['closure_system_architecture'] == 'powered-wheel-research'
    assert receipt['physical_accepted'] is False
    body_input.recheck(archive, receipt)
    archive.write_bytes(archive.read_bytes() + b'changed')
    with pytest.raises(ValueError, match='changed during closure run'):
        body_input.recheck(archive, receipt)


@pytest.mark.parametrize('mutation,reason', [
    ({'candidate': '0' * 64}, 'physical or evaluation identity differs'),
    ({'changed_source': True}, 'source SHA differs'),
    ({'released': True}, 'research-only flags'),
])
def test_mixed_or_stale_or_released_body_is_refused(tmp_path, mutation, reason):
    archive, cid = _packet(tmp_path, **mutation)
    with pytest.raises(ValueError, match=reason):
        body_input.load(archive, expected_candidate_id=cid, root=tmp_path)


def test_symlink_and_implicit_candidate_are_refused_before_run(tmp_path):
    archive, cid = _packet(tmp_path)
    link = tmp_path / 'alias.json.gz'
    link.symlink_to(archive)
    with pytest.raises(ValueError, match='symlink'):
        body_input.load(link, expected_candidate_id=cid, root=tmp_path)
    output = tmp_path / 'not-created'
    with pytest.raises(ValueError, match='supplied together'):
        coordinator.run(output, body_input=archive)
    assert not output.exists()


def test_bogie_detail_cannot_mutate_supplied_body(tmp_path):
    archive, cid = _packet(tmp_path)
    output = tmp_path / 'not-created'
    with pytest.raises(ValueError, match='cannot be silently revised'):
        coordinator.run(output, body_input=archive,
                        expected_body_candidate=cid, bogie_detail=True)
    assert not output.exists()


def test_authenticated_but_incomplete_body_fails_before_output(tmp_path):
    archive, cid = _packet(tmp_path)
    body = json.loads(gzip.decompress(archive.read_bytes()))
    del body['mass_scenarios'][0]['axles']
    body['evaluation_id'] = identity({k:v for k,v in body.items() if k != 'evaluation_id'})
    archive.write_bytes(gzip.compress(encoded(body), mtime=0))
    output = tmp_path / 'not-created'
    with pytest.raises(ValueError, match='24-axle'):
        coordinator.run(output, body_input=archive, expected_body_candidate=cid,
                        root=tmp_path)
    assert not output.exists()
