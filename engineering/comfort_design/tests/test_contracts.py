from io import BytesIO
import gzip
import tarfile
import pytest
from engineering.comfort_design import common as c


def test_cannot_mix_service_or_body_identities():
    vehicle=dict(candidate_id='car-a',body_candidate_id='body-a',magnet_component_id='pm-a')
    assert c.require_candidate(dict(vehicle),vehicle)
    for key in vehicle:
        wrong=dict(vehicle);wrong[key]='another'
        with pytest.raises(ValueError,match='mixed or missing'):c.require_candidate(wrong,vehicle)


def test_archive_retains_files_and_rejects_outside_members(tmp_path):
    source=tmp_path/'source';source.mkdir();(source/'result.json').write_text('{"physical_accepted":false}\n')
    blob=c.package(source,'native')
    target=c.unpack(blob,tmp_path/'readback','native')
    assert c.inventory(source)==c.inventory(target)
    data=BytesIO()
    with tarfile.open(fileobj=data,mode='w') as archive:
        entry=tarfile.TarInfo('native/../../escape');entry.size=1;archive.addfile(entry,BytesIO(b'x'))
    with pytest.raises(ValueError,match='ordinary'):c.unpack(gzip.compress(data.getvalue()),tmp_path/'bad','native')


def test_gate_pass_cannot_grant_physical_or_operating_release():
    gate=c.gate('event-model','pass','120second resource screen under declared stopping hypotheses')
    assert gate['state']=='pass'
    assert gate['physical_accepted'] is False and gate['operating_release'] is False
    with pytest.raises(ValueError):c.gate('actual-safe-headway','possible','')
