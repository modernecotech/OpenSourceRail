"""Adversarial transport checks; original archive/semantic verifier stays intact."""
import importlib.util
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import pytest

SCRIPT=Path(__file__).resolve().parents[1]/'sourced-archive.py'
spec=importlib.util.spec_from_file_location('sourced_archive',SCRIPT);s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)

@pytest.fixture
def packet(tmp_path):
    payload=b'bounded publication payload 0123456789'*3
    (tmp_path/s.ARCHIVE).write_bytes(payload);(tmp_path/'summary.json').write_bytes(b'{}\n')
    m=dict(schema='osr-sourced-cell-publication/1',files_sha256={s.ARCHIVE:sha256(payload).hexdigest(),'summary.json':sha256(b'{}\n').hexdigest()},source_sha256={},**s.FLAGS)
    m['publication_id']=s.identity(m);(tmp_path/s.MANIFEST).write_bytes(s.encoded(m));return tmp_path,payload


def descriptor(folder):return json.loads((folder/s.STORAGE).read_bytes())
def write_descriptor(folder,d):
    d.pop('storage_id',None);d['storage_id']=s.identity(d);(folder/s.STORAGE).write_bytes(s.encoded(d))


def test_fresh_no_storage_is_noop(tmp_path):
    assert s.ensure(tmp_path)['action']=='no-storage'
    assert list(tmp_path.iterdir())==[]


def test_split_roundtrip_and_matching_cache_no_mutation(packet):
    folder,payload=packet;manifest=(folder/s.MANIFEST).read_bytes();x=s.split(folder,chunk_bytes=24)
    assert 1<=x['chunks']<=8 and (folder/s.ARCHIVE).read_bytes()==payload
    d=descriptor(folder);assert all(c['bytes']<=24 for c in d['chunks'])
    before=(folder/s.ARCHIVE).stat().st_mtime_ns
    assert not s.ensure(folder)['reconstructed']
    assert (folder/s.ARCHIVE).stat().st_mtime_ns==before
    (folder/s.ARCHIVE).unlink();assert s.ensure(folder)['reconstructed']
    assert (folder/s.ARCHIVE).read_bytes()==payload
    assert (folder/s.MANIFEST).read_bytes()==manifest
    assert all(d[k] is False for k in s.FLAGS)


def test_wrong_cache_replaced_after_strict_checks(packet):
    f,p=packet;s.split(f,chunk_bytes=24);(f/s.ARCHIVE).write_bytes(b'wrong')
    assert s.ensure(f)['reconstructed'] and (f/s.ARCHIVE).read_bytes()==p


@pytest.mark.parametrize('attack',['tamper','missing','extra','reorder','traversal','absolute','wrongsize','boolean-size','duplicate','selfhash','unknownfield','release'])
def test_chunk_and_descriptor_attacks_rejected_preserve_cache(packet,attack):
    f,p=packet;s.split(f,chunk_bytes=24);d=descriptor(f)
    if attack=='tamper':(f/d['chunks'][0]['path']).write_bytes(b'X'*d['chunks'][0]['bytes'])
    elif attack=='missing':(f/d['chunks'][0]['path']).unlink()
    elif attack=='extra':(f/(s.PREFIX+'099')).write_bytes(b'extra')
    elif attack=='reorder':d['chunks'][0],d['chunks'][1]=d['chunks'][1],d['chunks'][0];write_descriptor(f,d)
    elif attack=='traversal':d['chunks'][0]['path']='../outside';write_descriptor(f,d)
    elif attack=='absolute':d['chunks'][0]['path']='/tmp/outside';write_descriptor(f,d)
    elif attack=='wrongsize':d['chunks'][0]['bytes']+=1;write_descriptor(f,d)
    elif attack=='boolean-size':d['chunks'][0]['bytes']=True;write_descriptor(f,d)
    elif attack=='duplicate':d['chunks'][1]=d['chunks'][0];write_descriptor(f,d)
    elif attack=='selfhash':d['storage_id']='0'*64;(f/s.STORAGE).write_bytes(s.encoded(d))
    elif attack=='unknownfield':d['accepted']=True;write_descriptor(f,d)
    elif attack=='release':d['operating_release']=True;write_descriptor(f,d)
    with pytest.raises(ValueError):s.ensure(f)
    assert (f/s.ARCHIVE).read_bytes()==p


def test_chunk_hash_resealed_still_bound_to_full_archive(packet):
    f,p=packet;s.split(f,chunk_bytes=24);d=descriptor(f);name=d['chunks'][0]['path']
    block=b'Y'*d['chunks'][0]['bytes'];(f/name).write_bytes(block);d['chunks'][0]['sha256']=sha256(block).hexdigest();write_descriptor(f,d)
    with pytest.raises(ValueError,match='Combined'):s.ensure(f)


def test_rebound_original_manifest_rejected(packet):
    f,p=packet;s.split(f,chunk_bytes=24);m=json.loads((f/s.MANIFEST).read_bytes());m['source_sha256']={'changed.py':'a'*64};m.pop('publication_id');m['publication_id']=s.identity(m);(f/s.MANIFEST).write_bytes(s.encoded(m))
    with pytest.raises(ValueError,match='rebound'):s.ensure(f)


def test_archive_hash_cannot_be_rebound_by_descriptor(packet):
    f,p=packet;s.split(f,chunk_bytes=24);d=descriptor(f);d['archive_sha256']='0'*64;write_descriptor(f,d)
    with pytest.raises(ValueError,match='rebound'):s.ensure(f)


@pytest.mark.parametrize('target',[s.STORAGE,s.PREFIX+'000',s.ARCHIVE])
def test_symlink_files_refused(packet,target):
    f,p=packet;s.split(f,chunk_bytes=24);original=(f/target).read_bytes();(f/target).unlink();outside=f.parent/(f.name+'-outside');outside.write_bytes(original);(f/target).symlink_to(outside)
    with pytest.raises(ValueError):s.ensure(f)
    assert outside.read_bytes()==original


def test_symlink_folder_and_nonregular_chunk_refused(packet):
    f,p=packet;s.split(f,chunk_bytes=24);alias=f.parent/(f.name+'-alias');alias.symlink_to(f,target_is_directory=True)
    with pytest.raises(ValueError):s.ensure(alias)
    chunk=f/(s.PREFIX+'000');chunk.unlink();chunk.mkdir()
    with pytest.raises(ValueError):s.ensure(f)


def test_budgets_and_nonfinite_duplicate_JSON(packet):
    f,p=packet
    with pytest.raises(ValueError):s.split(f,chunk_bytes=s.CHUNK_BYTES+1)
    with pytest.raises(ValueError):s.split(f,chunk_bytes=1)
    s.split(f,chunk_bytes=24);d=descriptor(f);d['total_bytes']=s.MAX_TOTAL+1;write_descriptor(f,d)
    with pytest.raises(ValueError):s.ensure(f)
    (f/s.STORAGE).write_text('{"schema":"a","schema":"b"}')
    with pytest.raises(ValueError,match='Duplicate'):s.ensure(f)
    (f/s.STORAGE).write_text('{"x":NaN}')
    with pytest.raises(ValueError,match='Nonfinite'):s.ensure(f)


def test_original_bad_hash_prevents_split(packet):
    f,p=packet;(f/s.ARCHIVE).write_bytes(p+b'changed')
    with pytest.raises(ValueError):s.split(f)
    assert not (f/s.STORAGE).exists()


def test_failed_atomic_reconstruction_leaves_previous_cache(packet,monkeypatch):
    f,p=packet;s.split(f,chunk_bytes=24);(f/s.ARCHIVE).write_bytes(b'priorbadcache');original=s._chunks;calls=0
    def fail_during_write(folder,d,output=None):
        if output is not None:output.write(b'partial');raise ValueError('simulated interrupted input')
        return original(folder,d,output)
    monkeypatch.setattr(s,'_chunks',fail_during_write)
    with pytest.raises(ValueError):s.ensure(f)
    assert (f/s.ARCHIVE).read_bytes()==b'priorbadcache'
    assert not list(f.glob('.sourced-archive-*.tmp'))


def test_cli_supports_small_original_and_rejects_invalid_storage(tmp_path):
    r=subprocess.run([sys.executable,str(SCRIPT),'ensure',str(tmp_path)],capture_output=True,text=True)
    assert r.returncode==0 and json.loads(r.stdout)['action']=='no-storage'
    (tmp_path/s.STORAGE).write_text('{}')
    r=subprocess.run([sys.executable,str(SCRIPT),'ensure',str(tmp_path)],capture_output=True,text=True)
    assert r.returncode==2 and 'storage' in r.stderr


def test_real_24MiB_boundary_is_portable(packet):
    f,_=packet
    with (f/s.ARCHIVE).open('wb') as out:
        for _ in range(24):out.write(b'x'*1024**2)
        out.write(b'final-seventeen!!')
    archive_sha,size=s._digest(f/s.ARCHIVE,s.MAX_TOTAL)
    m=json.loads((f/s.MANIFEST).read_bytes());m['files_sha256'][s.ARCHIVE]=archive_sha;m.pop('publication_id');m['publication_id']=s.identity(m);(f/s.MANIFEST).write_bytes(s.encoded(m))
    r=s.split(f);d=descriptor(f)
    assert r['chunks']==2 and d['chunks'][0]['bytes']==24*1024**2
    assert d['chunks'][1]['bytes']==len(b'final-seventeen!!')
    (f/s.ARCHIVE).unlink();s.ensure(f)
    assert s._digest(f/s.ARCHIVE,s.MAX_TOTAL)==(archive_sha,size)
