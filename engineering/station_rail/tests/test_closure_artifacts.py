from pathlib import Path
import json
import pytest
from engineering.station_rail import FLAGS
from engineering.station_rail.common import encoded,identity,digest
from engineering.station_rail import closure_artifacts as a


def packet(tmp_path):
    root=tmp_path/'source';root.mkdir();(root/'worker.py').write_text('print(1)\n')
    raw=tmp_path/'raw';raw.mkdir();(raw/'input.json').write_text('{}\n');(raw/'result.json').write_text('{}\n');(raw/'motor.pro').write_text('GetDP source\n');(raw/'stdout.log').write_text('executed\n');(raw/'force.txt').write_text('1.0\n');(raw/'motor.res').write_bytes(b'large-binary')
    m=dict(files_sha256={p.name:digest(p) for p in raw.iterdir()},source_sha256={'worker.py':digest(root/'worker.py')},**FLAGS);m['manifest_id']=identity(m);(raw/'manifest.json').write_bytes(encoded(m))
    return root,raw


def test_compact_archives_are_deterministic_and_explicitly_partial(tmp_path):
    root,raw=packet(tmp_path);one=tmp_path/'one.tar.gz';two=tmp_path/'two.tar.gz'
    m=a.export(raw,one,root);a.export(raw,two,root)
    assert one.read_bytes()==two.read_bytes()
    assert m['omitted_raw_files_sha256']=={'motor.res':digest(raw/'motor.res')}
    assert m['remote_raw_storage'] is None
    assert a.verify(one)['full_native_verifier_available_from_compact_alone'] is False
    assert not a.verify(one)['retained_raw_payload_complete']
    assert (raw/'motor.res').exists()


def test_include_all_preserves_small_complete_raw_packet(tmp_path):
    root,raw=packet(tmp_path);path=tmp_path/'all.tar.gz';m=a.export(raw,path,root,include_all=True)
    assert not m['omitted_raw_files_sha256']
    assert a.verify(path,root)['retained_raw_payload_complete']


def test_archive_rejects_modified_raw_or_method_before_export(tmp_path):
    root,raw=packet(tmp_path);(raw/'motor.res').write_bytes(b'corrupted')
    with pytest.raises(ValueError,match='raw package'):a.export(raw,tmp_path/'bad.tar.gz',root)
    assert not (tmp_path/'bad.tar.gz').exists()


def test_budget_and_source_integrity_are_enforced(tmp_path):
    root,raw=packet(tmp_path)
    with pytest.raises(ValueError,match='budget'):a.export(raw,tmp_path/'small.tar.gz',root,max_bytes=10)
    path=tmp_path/'good.tar.gz';a.export(raw,path,root);(root/'worker.py').write_text('changed')
    with pytest.raises(ValueError,match='source'):a.verify(path,root)
    assert a.verify(path)['verified']
