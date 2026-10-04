"""An explicit bootstrap restores only the exact hash-bound ignored input."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile
import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/automation'))
from bootstrap_baghdad_tests import restore, restore_proposal_inputs, CITY

def dump(path,value):path.write_text(json.dumps(value))

@pytest.fixture
def checkout(tmp_path):
    city=tmp_path/CITY.relative_to(ROOT);(city/'operations').mkdir(parents=True)
    raw=b'exact ignored fixture';target=city/'operations/baghdad-operations.json.gz';archive=city/'Baghdad-Proposal-Supporting-Data.zip'
    relative=target.relative_to(tmp_path).as_posix()
    receipt=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    dump(city/'operations/baghdad-operations-manifest.json',dict(file=target.name,compressed_bytes=receipt['bytes'],compressed_sha256=receipt['sha256']))
    with zipfile.ZipFile(archive,'w') as z:
        z.writestr(relative,raw);z.writestr('../../unexpected.txt',b'must never be extracted')
    dump(city/'archive-manifest.json',dict(members={relative:receipt}))
    dump(city/'manifest.json',dict(outputs={archive.relative_to(tmp_path).as_posix():dict(bytes=archive.stat().st_size,sha256=hashlib.sha256(archive.read_bytes()).hexdigest())}))
    return tmp_path,city,target,archive,raw

def test_exact_restore_check_idempotency_and_selective_extraction(checkout):
    root,city,target,archive,raw=checkout
    with pytest.raises(ValueError,match='missing'):restore(root,check=True)
    assert restore(root)=='restored-hash-bound-input' and target.read_bytes()==raw
    assert restore(root)=='verified-existing' and restore(root,check=True)=='verified-existing'
    assert not (root.parent/'unexpected.txt').exists()

def test_differing_workspace_input_is_preserved(checkout):
    root,city,target,archive,raw=checkout;target.write_bytes(b'local different data')
    with pytest.raises(ValueError,match='Existing'):restore(root)
    assert target.read_bytes()==b'local different data'

def test_archive_publication_drift_is_rejected(checkout):
    root,city,target,archive,raw=checkout;archive.write_bytes(b'corrupt')
    with pytest.raises(ValueError,match='archive differs'):restore(root)
    assert not target.exists()

def test_receipt_conflict_is_rejected(checkout):
    root,city,target,archive,raw=checkout
    dump(city/'archive-manifest.json',dict(members={target.relative_to(root).as_posix():dict(bytes=len(raw),sha256='0'*64)}))
    with pytest.raises(ValueError,match='receipts disagree'):restore(root)

def test_metadata_cannot_select_another_output_path(checkout):
    root,city,target,archive,raw=checkout
    data=json.loads((city/'operations/baghdad-operations-manifest.json').read_text());data['file']='../../private.json'
    dump(city/'operations/baghdad-operations-manifest.json',data)
    with pytest.raises(ValueError,match='Unexpected'):restore(root)

def test_duplicate_archive_entries_are_rejected_even_with_matching_archive_receipt(checkout):
    root,city,target,archive,raw=checkout
    with zipfile.ZipFile(archive,'a') as z:
        with pytest.warns(UserWarning):z.writestr(target.relative_to(root).as_posix(),raw)
    dump(city/'manifest.json',dict(outputs={archive.relative_to(root).as_posix():dict(bytes=archive.stat().st_size,sha256=hashlib.sha256(archive.read_bytes()).hexdigest())}))
    with pytest.raises(ValueError,match='Duplicate'):restore(root)

@pytest.fixture
def solver_checkout(checkout):
    root,city,target,archive,raw=checkout
    energy=city/'engineering/energy/coordinated-daylight.json';relative=energy.relative_to(root).as_posix()
    solver=b'{"synthetic":true,"fixture":true}'
    with zipfile.ZipFile(archive,'a') as z:z.writestr(relative,solver)
    manifest=json.loads((city/'manifest.json').read_text())
    manifest['outputs'][archive.relative_to(root).as_posix()]=dict(bytes=archive.stat().st_size,sha256=hashlib.sha256(archive.read_bytes()).hexdigest())
    manifest['inputs']={relative:dict(bytes=len(solver),sha256=hashlib.sha256(solver).hexdigest())}
    dump(city/'manifest.json',manifest)
    return root,city,energy,archive,solver

def test_missing_ignored_solver_input_restores_exact_bytes_only(solver_checkout):
    root,city,energy,archive,raw=solver_checkout
    with pytest.raises(ValueError,match='missing'):restore_proposal_inputs(root,check=True)
    assert restore_proposal_inputs(root)=='restored-hash-bound-inputs'
    assert energy.read_bytes()==raw and restore_proposal_inputs(root,check=True)=='verified-existing'
    assert not (root.parent/'unexpected.txt').exists()

def test_solver_drift_is_preserved_and_archive_hash_is_verified(solver_checkout):
    root,city,energy,archive,raw=solver_checkout;energy.parent.mkdir(parents=True);energy.write_bytes(b'local')
    with pytest.raises(ValueError,match='Existing'):restore_proposal_inputs(root)
    assert energy.read_bytes()==b'local'
    energy.unlink();archive.write_bytes(b'corrupt')
    with pytest.raises(ValueError,match='archive differs'):restore_proposal_inputs(root)
    assert not energy.exists()


def test_core_corridor_input_is_restored_from_declared_archive_and_local_drift_is_preserved(solver_checkout):
    root,city,energy,archive,raw=solver_checkout
    corridor=city/'corridors.json';name=corridor.relative_to(root).as_posix();geometry=b'{"lines":[]}'
    with zipfile.ZipFile(archive,'a') as z:z.writestr(name,geometry)
    manifest=json.loads((city/'manifest.json').read_text())
    manifest['inputs'][name]=dict(bytes=len(geometry),sha256=hashlib.sha256(geometry).hexdigest())
    manifest['outputs'][archive.relative_to(root).as_posix()]=dict(bytes=archive.stat().st_size,sha256=hashlib.sha256(archive.read_bytes()).hexdigest())
    dump(city/'manifest.json',manifest)
    assert restore_proposal_inputs(root)=='restored-hash-bound-inputs'
    assert corridor.read_bytes()==geometry
    corridor.write_bytes(b'local alignment')
    with pytest.raises(ValueError,match='Existing'):restore_proposal_inputs(root)
    assert corridor.read_bytes()==b'local alignment'
