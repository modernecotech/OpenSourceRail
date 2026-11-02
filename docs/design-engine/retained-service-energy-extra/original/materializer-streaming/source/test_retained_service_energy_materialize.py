import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import tarfile

import pytest

from engineering.design_search import retained_service_energy_materialize as materializer


def _blob(data):
    return hashlib.sha1(('blob '+str(len(data))+'\0').encode()+data).hexdigest()


def sample(monkeypatch):
    prefix='docs/design-engine/sourced-case/'
    chunks=[b'one',b'two',b'three',b'four',b'five']
    files={prefix+'sourced-cell.part-'+f'{i:03d}':data for i,data in enumerate(chunks)}
    files[materializer.OLD_PRODUCER]=b'old-producer'
    files[materializer.OLD_WRAPPER]=b'{}'
    names=sorted(files);tree={name:dict(oid=_blob(files[name]),size=len(files[name])) for name in names}
    expected={name:hashlib.sha256(data).hexdigest() for name,data in files.items()}
    storage={'chunks':[dict(path='sourced-cell.part-'+f'{i:03d}',bytes=len(data),
        sha256=hashlib.sha256(data).hexdigest()) for i,data in enumerate(chunks)]}
    combined=b''.join(chunks)
    monkeypatch.setattr(materializer,'TAR_BYTES',len(combined))
    monkeypatch.setattr(materializer,'TAR_SHA',hashlib.sha256(combined).hexdigest())
    return files,tree,expected,storage,combined


def make_tar(files,*,additional=(),trailing=b''):
    output=io.BytesIO();dirs=set()
    for name in files:
        for parent in PurePosixPath(name).parents:
            if str(parent)!='.':dirs.add(str(parent))
    with tarfile.open(fileobj=output,mode='w',format=tarfile.USTAR_FORMAT) as tar:
        raw=('52 comment='+materializer.COMMIT+'\n').encode()
        header=tarfile.TarInfo('pax_global_header');header.type=tarfile.XGLTYPE;header.size=len(raw)
        tar.addfile(header,io.BytesIO(raw))
        for name in sorted(dirs,key=lambda x:(x.count('/'),x)):
            entry=tarfile.TarInfo(name);entry.type=tarfile.DIRTYPE;tar.addfile(entry)
        for name,data in sorted(files.items()):
            entry=tarfile.TarInfo(name);entry.size=len(data);tar.addfile(entry,io.BytesIO(data))
        for name,kind in additional:
            entry=tarfile.TarInfo(name);entry.type=kind
            if kind==tarfile.REGTYPE:entry.size=1;tar.addfile(entry,io.BytesIO(b'x'))
            else:entry.linkname='target';tar.addfile(entry)
    return output.getvalue()+trailing


def test_exact_external_pins_and_allowed_paths():
    materializer._fixed(materializer.COMMIT,materializer.PINS_ID,materializer.ARCHIVE_ID)
    for values in [('0'*40,materializer.PINS_ID,materializer.ARCHIVE_ID),
                   (materializer.COMMIT,'0'*64,materializer.ARCHIVE_ID),
                   (materializer.COMMIT,materializer.PINS_ID,'0'*64)]:
        with pytest.raises(ValueError,match='pinned'):materializer._fixed(*values)
    for value in ('../escape','/absolute','docs/design-engine/other/file'):
        with pytest.raises(ValueError):materializer._allowed_file(value)


def test_stream_audit_reconstructs_each_blob_and_chunks_without_writes(monkeypatch,tmp_path):
    files,tree,expected,storage,combined=sample(monkeypatch)
    details,old=materializer._stream_tar(io.BytesIO(make_tar(files)),tree,expected,storage)
    assert details['file_count']==7 and details['blob_bytes']==sum(map(len,files.values()))
    assert details['sourced_combined_sha256']==hashlib.sha256(combined).hexdigest()
    assert details['sourced_combined_bytes']==len(combined) and old==b'old-producer'
    assert not list(tmp_path.iterdir())


def test_one_private_tree_reassembles_chunks_without_overwrite(monkeypatch,tmp_path):
    files,tree,expected,storage,combined=sample(monkeypatch);root=tmp_path/'root';root.mkdir()
    materializer._stream_tar(io.BytesIO(make_tar(files)),tree,expected,storage,destination=root)
    materializer._assemble(root,storage)
    target=root/materializer.SOURCED_TAR
    assert target.read_bytes()==combined
    with pytest.raises(FileExistsError):materializer._assemble(root,storage)
    assert target.read_bytes()==combined


@pytest.mark.parametrize('kind',[tarfile.SYMTYPE,tarfile.LNKTYPE,tarfile.FIFOTYPE,tarfile.CHRTYPE,tarfile.BLKTYPE])
def test_stream_rejects_links_and_special_files(monkeypatch,kind):
    files,tree,expected,storage,_=sample(monkeypatch)
    raw=make_tar(files,additional=[('docs/design-engine/sourced-case/extra',kind)])
    with pytest.raises(ValueError,match='links, special'):
        materializer._stream_tar(io.BytesIO(raw),tree,expected,storage)


@pytest.mark.parametrize('name',['../escape','/absolute','docs/design-engine/sourced-case/extra'])
def test_stream_rejects_unlisted_or_escaping_files(monkeypatch,name):
    files,tree,expected,storage,_=sample(monkeypatch)
    with pytest.raises(ValueError):
        materializer._stream_tar(io.BytesIO(make_tar(files,additional=[(name,tarfile.REGTYPE)])),tree,expected,storage)


def test_stream_rejects_duplicate_and_appended_tar(monkeypatch):
    files,tree,expected,storage,_=sample(monkeypatch);name=next(iter(files))
    with pytest.raises(ValueError,match='duplicate'):
        materializer._stream_tar(io.BytesIO(make_tar(files,additional=[(name,tarfile.REGTYPE)])),tree,expected,storage)
    raw=make_tar(files)
    with pytest.raises(ValueError,match='trailing'):
        materializer._stream_tar(io.BytesIO(raw+raw),tree,expected,storage)


def test_stream_detects_blob_hash_and_chunk_mismatch(monkeypatch):
    files,tree,expected,storage,_=sample(monkeypatch);wrong=dict(expected);wrong[next(iter(files))]='0'*64
    with pytest.raises(ValueError,match='SHA differs'):
        materializer._stream_tar(io.BytesIO(make_tar(files)),tree,wrong,storage)
    monkeypatch.setattr(materializer,'TAR_SHA','0'*64)
    with pytest.raises(ValueError,match='Combined sourced chunks'):
        materializer._stream_tar(io.BytesIO(make_tar(files)),tree,expected,storage)


def test_assembly_rejects_changed_or_linked_chunk(monkeypatch,tmp_path):
    files,tree,expected,storage,_=sample(monkeypatch);root=tmp_path/'root';root.mkdir()
    materializer._stream_tar(io.BytesIO(make_tar(files)),tree,expected,storage,destination=root)
    chunk=root/'docs/design-engine/sourced-case/sourced-cell.part-000';os.link(chunk,tmp_path/'hardlink')
    with pytest.raises(ValueError,match='Unsafe sourced chunk'):
        materializer._assemble(root,storage)
    assert (root/materializer.SOURCED_TAR).exists()  # failed private stage is retained


def test_final_root_inventory_rejects_extra_and_symlink(monkeypatch,tmp_path):
    files,tree,expected,storage,combined=sample(monkeypatch);root=tmp_path/'root';root.mkdir()
    materializer._stream_tar(io.BytesIO(make_tar(files)),tree,expected,storage,destination=root)
    materializer._assemble(root,storage);expected=dict(expected,**{materializer.SOURCED_TAR:hashlib.sha256(combined).hexdigest()})
    dirs={str(parent) for name in expected for parent in PurePosixPath(name).parents if str(parent)!='.'}
    monkeypatch.setattr(materializer,'FINAL_BYTES',sum(map(len,files.values()))+len(combined))
    materializer._check_root(root,expected,dirs)
    (root/'unexpected').write_text('x')
    with pytest.raises(ValueError,match='Unlisted'):materializer._check_root(root,expected,dirs)
    (root/'unexpected').unlink();(root/'link').symlink_to(root/materializer.SOURCED_TAR)
    with pytest.raises(ValueError,match='link or special'):materializer._check_root(root,expected,dirs)


def test_audit_mode_hands_off_only_small_record(monkeypatch,tmp_path):
    files,tree,expected,storage,_=sample(monkeypatch);raw=make_tar(files)
    repo=tmp_path/'repo';repo.mkdir();archive=tmp_path/'archive';archive.mkdir();out=tmp_path/'audit'
    monkeypatch.setattr(materializer.extra,'_pins',lambda pins,expected:pins)
    monkeypatch.setattr(materializer,'_preflight',lambda *args:({'test':True},expected,set(),('a','b')))
    monkeypatch.setattr(materializer,'_tree',lambda repo,expected,log:(log.touch(),tree)[1])
    monkeypatch.setattr(materializer,'_git_metadata',lambda *args:storage)
    monkeypatch.setattr(materializer,'_git_blob',lambda *args:b'{}')
    monkeypatch.setattr(materializer,'_old_archive',lambda *args:None)
    monkeypatch.setattr(materializer.shutil,'which',lambda _: '/usr/bin/timeout')
    class FakeProcess:
        def __init__(self,*args,**kwargs):self.stdout=io.BytesIO(raw)
        def wait(self,timeout=None):return 0
        def poll(self):return 0
    monkeypatch.setattr(materializer.subprocess,'Popen',FakeProcess)
    result=materializer.run(repo,out,archive,pins={},mode='audit',expected_commit=materializer.COMMIT,
        expected_pins_id=materializer.PINS_ID,expected_archive_id=materializer.ARCHIVE_ID)
    assert result['root_written'] is False and result['full_packet_verifier_executed'] is False
    assert result['physical_accepted'] is False and result['current_evaluator_admission'] is False
    assert not (out/'root').exists() and (out/'result.json').is_file()
    assert json.loads((out/'result.json').read_bytes())==result


def test_synthetic_materialization_verifies_twice_before_handoff(monkeypatch,tmp_path):
    files,tree,expected,storage,combined=sample(monkeypatch);raw=make_tar(files)
    expected=dict(expected,**{materializer.SOURCED_TAR:hashlib.sha256(combined).hexdigest()})
    dirs={str(parent) for name in expected for parent in PurePosixPath(name).parents if str(parent)!='.'}
    repo=tmp_path/'repo';repo.mkdir();archive=tmp_path/'archive';archive.mkdir();out=tmp_path/'packet'
    monkeypatch.setattr(materializer,'FINAL_BYTES',sum(map(len,files.values()))+len(combined))
    monkeypatch.setattr(materializer,'FINAL_FILES',len(expected))
    monkeypatch.setattr(materializer.extra,'_pins',lambda pins,expected:pins)
    monkeypatch.setattr(materializer,'_preflight',lambda *args:({'test':True},expected,dirs,('a','b')))
    monkeypatch.setattr(materializer,'_tree',lambda repo,expected,log:(log.touch(),tree)[1])
    monkeypatch.setattr(materializer,'_git_metadata',lambda *args:storage)
    monkeypatch.setattr(materializer,'_git_blob',lambda *args:b'{}')
    monkeypatch.setattr(materializer,'_old_archive',lambda *args:None)
    monkeypatch.setattr(materializer.shutil,'which',lambda _: '/usr/bin/timeout')
    calls=[]
    def verify(root,*args,**kwargs):
        assert not out.exists()
        assert (root/materializer.SOURCED_TAR).read_bytes()==combined
        calls.append(root)
        return {'historical_integrity':True}
    monkeypatch.setattr(materializer.extra,'verify',verify)
    class FakeProcess:
        def __init__(self,*args,**kwargs):self.stdout=io.BytesIO(raw)
        def wait(self,timeout=None):return 0
        def poll(self):return 0
    monkeypatch.setattr(materializer.subprocess,'Popen',FakeProcess)
    result=materializer.run(repo,out,archive,pins={},mode='materialize',expected_commit=materializer.COMMIT,
        expected_pins_id=materializer.PINS_ID,expected_archive_id=materializer.ARCHIVE_ID)
    assert len(calls)==2 and calls[0]==calls[1]
    assert (out/'root'/materializer.SOURCED_TAR).read_bytes()==combined
    assert result['root_written'] and result['full_packet_verifier_executed']
    assert not result['physical_accepted'] and not result['current_evaluator_admission']
    with pytest.raises(ValueError,match='Fresh ordinary destination'):
        materializer.run(repo,out,archive,pins={},mode='materialize',expected_commit=materializer.COMMIT,
            expected_pins_id=materializer.PINS_ID,expected_archive_id=materializer.ARCHIVE_ID)
