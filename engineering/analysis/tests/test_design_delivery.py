"""Offline review membership, download bounds and scoped artifact paths."""
from pathlib import Path
import zipfile
import pytest
from engineering.design_engine.contracts import canonical
from engineering.design_engine.delivery import bundle, controlled_file, CHUNK_BYTES
from engineering.design_engine.publication import digest


def package(root):
    root.mkdir(); (root/'candidate.json').write_bytes(b'{"physical_release":false}\n')
    (root/'manifest.json').write_bytes(canonical(dict(schema='osr-design-export/1', files={'candidate.json':digest(root/'candidate.json')}, physical_release=False)))


def test_offline_download_reassembles_original_verified_bytes(tmp_path):
    source=tmp_path/'source';package(source)
    result=bundle(source,tmp_path/'download')
    target=tmp_path/'restored.zip'
    target.write_bytes(b''.join((tmp_path/'download'/row['name']).read_bytes() for row in result['chunks']))
    assert digest(target)==result['archive_sha256']
    assert all(row['bytes']<=CHUNK_BYTES for row in result['chunks'])
    with zipfile.ZipFile(target) as archive:
        assert archive.read('candidate.json')==(source/'candidate.json').read_bytes()
        assert set(archive.namelist())=={'candidate.json','manifest.json'}
    assert result['physical_release']is False


def test_mutated_package_and_escape_or_symlink_download_reject(tmp_path):
    source=tmp_path/'source';package(source)
    (source/'candidate.json').write_bytes(b'changed')
    with pytest.raises(ValueError):bundle(source,tmp_path/'download')
    outside=tmp_path/'private';outside.write_text('private')
    (source/'link').symlink_to(outside)
    for name in ['../private',str(outside),'link','missing']:
        with pytest.raises(ValueError):controlled_file(source,name)
