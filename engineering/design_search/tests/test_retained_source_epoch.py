"""Authenticated historical source bytes do not imply evaluator admission."""
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import tarfile

import pytest
from engineering.design_search import retained_source_epoch as r


def digest(data): return hashlib.sha256(data).hexdigest()


def make_packet(root, name, *, source=None, promote=False):
    folder=root/'docs/design-engine'/name;folder.mkdir(parents=True)
    payload=b'original packet bytes\n';(folder/'evidence.bin').write_bytes(payload)
    source=source or {'engineering/example.py':digest(b'print(1)\n')}
    m=dict(schema='test/1',source_sha256=source,files_sha256={'evidence.bin':digest(payload)},
        physical_accepted=promote,engineering_accepted=False,manufacturing_release=False,operating_release=False)
    m['manifest_id']=r._id(m);(folder/'manifest.json').write_bytes(r._encoded(m));return m['manifest_id']


@pytest.fixture
def example(tmp_path,monkeypatch):
    monkeypatch.setattr(r,'CATALOG',{k:('test/1','source_sha256','files_sha256','manifest_id',None) for k in ('one','two')})
    root=tmp_path/'repo';(root/'engineering').mkdir(parents=True);(root/'engineering/example.py').write_bytes(b'print(1)\n')
    pins={name:make_packet(root,name) for name in r.CATALOG}
    return root,pins


def archive(members):
    stream=io.BytesIO()
    with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0,compresslevel=6) as g:
        with tarfile.open(fileobj=g,mode='w') as t:
            for name,content in members:
                h=tarfile.TarInfo(name);h.size=len(content);t.addfile(h,io.BytesIO(content))
    return stream.getvalue()


def test_roundtrip_determinism_and_old_source_can_change(example,tmp_path):
    root,pins=example;a=tmp_path/'one';b=tmp_path/'two'
    first=r.capture(root,a,expected_manifests=pins);second=r.capture(root,b,expected_manifests=pins)
    assert first==second and (a/'sources.tar.gz').read_bytes()==(b/'sources.tar.gz').read_bytes()
    assert r.verify(root,a,expected_manifests=pins,expected_archive_id=first['archive_id'])['verified']
    (root/'engineering/example.py').write_text('new current source\n')
    verified=r.verify(root,a,expected_manifests=pins,expected_archive_id=first['archive_id'])
    assert verified['current_evaluator_admission'] is False and verified['physical_accepted'] is False
    with pytest.raises(ValueError,match='Original source bytes differ'):
        r.capture(root,tmp_path/'three',expected_manifests=pins)


def test_source_epochs_cannot_conflict(example,tmp_path):
    root,pins=example;folder=root/'docs/design-engine/two';m=json.loads((folder/'manifest.json').read_bytes())
    m['source_sha256']['engineering/example.py']='f'*64;m.pop('manifest_id');m['manifest_id']=r._id(m)
    (folder/'manifest.json').write_bytes(r._encoded(m));pins['two']=m['manifest_id']
    with pytest.raises(ValueError,match='Conflicting original source epochs'):
        r.capture(root,tmp_path/'out',expected_manifests=pins)


def test_packet_payload_and_caller_pins_checked(example,tmp_path):
    root,pins=example;out=tmp_path/'archive';m=r.capture(root,out,expected_manifests=pins)
    with pytest.raises(ValueError,match='identity'):
        r.verify(root,out,expected_manifests=pins,expected_archive_id='0'*64)
    bad=dict(pins,one='0'*64)
    with pytest.raises(ValueError,match='identity'):
        r.verify(root,out,expected_manifests=bad,expected_archive_id=m['archive_id'])
    (root/'docs/design-engine/one/evidence.bin').write_bytes(b'changed')
    with pytest.raises(ValueError,match='payload'):
        r.verify(root,out,expected_manifests=pins,expected_archive_id=m['archive_id'])


def test_source_archive_rejects_missing_extra_duplicate_and_path_traversal():
    sources={'one':digest(b'hello')}
    assert r._check_archive(archive([('one',b'hello')]),sources) is None
    for rows in ([],[('one',b'hello'),('extra',b'x')],[('one',b'hello'),('one',b'hello')],
                 [('../one',b'hello')],[('/one',b'hello')]):
        with pytest.raises(ValueError):r._check_archive(archive(rows),sources)


def test_manifest_path_traversal_and_false_promotion_rejected(example,tmp_path):
    root,pins=example;path=root/'docs/design-engine/one/manifest.json';m=json.loads(path.read_bytes())
    m['source_sha256']={'../outside':digest(b'x')};m.pop('manifest_id');m['manifest_id']=r._id(m);path.write_bytes(r._encoded(m));pins['one']=m['manifest_id']
    with pytest.raises(ValueError,match='relative POSIX'):r.capture(root,tmp_path/'escape',expected_manifests=pins)
    m['source_sha256']={'engineering/example.py':digest(b'print(1)\n')};m['physical_accepted']=True;m.pop('manifest_id');m['manifest_id']=r._id(m);path.write_bytes(r._encoded(m));pins['one']=m['manifest_id']
    with pytest.raises(ValueError,match='cannot grant'):r.capture(root,tmp_path/'promote',expected_manifests=pins)


def test_symlinks_and_special_files_rejected(example,tmp_path):
    root,pins=example;file=root/'docs/design-engine/one/evidence.bin';actual=file.read_bytes();file.unlink()
    elsewhere=tmp_path/'elsewhere';elsewhere.write_bytes(actual);file.symlink_to(elsewhere)
    with pytest.raises(ValueError,match='ordinary packet'):r.capture(root,tmp_path/'linked',expected_manifests=pins)
    file.unlink();file.write_bytes(actual);os.mkfifo(file.parent/'unexpected')
    with pytest.raises(ValueError,match='ordinary packet'):r.capture(root,tmp_path/'fifo',expected_manifests=pins)


def test_unlisted_original_packet_file_is_recorded_and_detected(example,tmp_path):
    root,pins=example;folder=root/'docs/design-engine/one';(folder/'extra.txt').write_text('historical unlisted file')
    out=tmp_path/'archive';meta=r.capture(root,out,expected_manifests=pins)
    assert meta['packets']['one']['undeclared_files']==['extra.txt']
    (folder/'extra.txt').write_text('changed')
    with pytest.raises(ValueError,match='packet files'):r.verify(root,out,expected_manifests=pins,expected_archive_id=meta['archive_id'])


def test_archive_membership_with_resealed_attacker_manifest_still_fails(example,tmp_path):
    root,pins=example;out=tmp_path/'archive';r.capture(root,out,expected_manifests=pins)
    m=json.loads((out/'manifest.json').read_bytes());bad=archive([('engineering/example.py',b'print(1)\n'),('extra',b'bad')])
    (out/'sources.tar.gz').write_bytes(bad);m['source_archive_sha256']=digest(bad);m.pop('archive_id');m['archive_id']=r._id(m);(out/'manifest.json').write_bytes(r._encoded(m))
    with pytest.raises(ValueError,match='Archive membership'):r.verify(root,out,expected_manifests=pins,expected_archive_id=m['archive_id'])


def test_private_archive_cannot_be_written_into_original_tree(example):
    root,pins=example
    with pytest.raises(ValueError,match='outside the source tree'):
        r.capture(root,root/'docs/design-engine/one/new-archive',expected_manifests=pins)
    assert not (root/'docs/design-engine/one/new-archive').exists()


def test_public_verify_requires_matching_pins_and_closed_inventory(example,tmp_path):
    root,pins=example;out=tmp_path/'archive';m=r.capture(root,out,expected_manifests=pins)
    with pytest.raises(ValueError,match='entire packet catalog'):
        r.verify(root,out,expected_manifests={'one':pins['one']},expected_archive_id=m['archive_id'])
    (out/'unexpected').write_text('unexpected')
    with pytest.raises(ValueError,match='inventory'):
        r.verify(root,out,expected_manifests=pins,expected_archive_id=m['archive_id'])


def test_source_and_packet_manifest_symlink_ancestors_are_rejected(example,tmp_path):
    root,pins=example;directory=root/'engineering';directory.rename(root/'real-engineering')
    directory.symlink_to(root/'real-engineering',target_is_directory=True)
    with pytest.raises(ValueError,match='Symlink'):
        r.capture(root,tmp_path/'linked-source',expected_manifests=pins)


def test_resealed_archive_cannot_promote_or_change_reference(example,tmp_path):
    root,pins=example;out=tmp_path/'archive';original=r.capture(root,out,expected_manifests=pins)
    for field,value in [('physical_accepted',True),('current_evaluator_admission',True),('selected_reference_changed',True),('reference_candidate_id','0'*64),('unknown_promotion',True)]:
        altered=dict(original);altered[field]=value;altered.pop('archive_id');altered['archive_id']=r._id(altered)
        (out/'manifest.json').write_bytes(r._encoded(altered))
        with pytest.raises(ValueError,match='historical disposition'):
            r.verify(root,out,expected_manifests=pins,expected_archive_id=altered['archive_id'])


def test_capture_does_not_overwrite_existing_or_modify_original(example,tmp_path):
    root,pins=example;folder=root/'docs/design-engine/one';before={x.name:x.read_bytes() for x in folder.iterdir()}
    out=tmp_path/'existing';out.mkdir();(out/'untouched').write_text('keep')
    with pytest.raises(FileExistsError):r.capture(root,out,expected_manifests=pins)
    assert (out/'untouched').read_text()=='keep'
    assert before=={x.name:x.read_bytes() for x in folder.iterdir()}


def test_concatenated_gzip_and_tar_streams_and_trailing_bytes_are_rejected():
    good=archive([('one',b'hello')]);other=archive([('evil',b'unlisted')]);sources={'one':digest(b'hello')}
    for raw in (good+other,good+b'ignored',good+b'\0'):
        with pytest.raises(ValueError,match='bounded gzip'):
            r._check_archive(raw,sources)
    stream=io.BytesIO()
    with gzip.GzipFile(fileobj=stream,mode='wb',filename='',mtime=0,compresslevel=6) as gz:
        gz.write(gzip.decompress(good)+gzip.decompress(other))
    with pytest.raises(ValueError,match='Canonical tar'):
        r._check_archive(stream.getvalue(),sources)


def test_noncanonical_gzip_header_and_tar_metadata_are_rejected():
    good=archive([('one',b'hello')]);sources={'one':digest(b'hello')}
    mutated=bytearray(good);mutated[4]=1
    with pytest.raises(ValueError,match='Canonical gzip header'):
        r._check_archive(bytes(mutated),sources)
    stream=io.BytesIO()
    with gzip.GzipFile(fileobj=stream,mode='wb',filename='',mtime=0,compresslevel=6) as gz:
        with tarfile.open(fileobj=gz,mode='w|',format=tarfile.PAX_FORMAT) as tar:
            entry=tarfile.TarInfo('one');entry.size=5;entry.mode=0o777
            tar.addfile(entry,io.BytesIO(b'hello'))
    with pytest.raises(ValueError,match='Canonical tar'):
        r._check_archive(stream.getvalue(),sources)


def test_tar_decompression_bound_is_checked_before_any_tar_parsing(monkeypatch):
    raw=archive([('one',b'hello')]);monkeypatch.setattr(r,'MAX_TAR_BYTES',64)
    def forbidden(*args,**kwargs):raise AssertionError('Tar parser was called before expansion bound')
    monkeypatch.setattr(r.tarfile,'open',forbidden)
    with pytest.raises(ValueError,match='bounded gzip'):
        r._check_archive(raw,{'one':digest(b'hello')})


def test_packet_inventory_and_total_budgets_are_enforced(example,tmp_path,monkeypatch):
    root,pins=example
    monkeypatch.setattr(r,'MAX_PACKET_ENTRIES',1)
    with pytest.raises(ValueError,match='entry count'):
        r.capture(root,tmp_path/'count',expected_manifests=pins)
    monkeypatch.setattr(r,'MAX_PACKET_ENTRIES',10000)
    monkeypatch.setattr(r,'MAX_PACKET_BYTES',5)
    with pytest.raises(ValueError,match='file bytes'):
        r.capture(root,tmp_path/'bytes',expected_manifests=pins)
    monkeypatch.setattr(r,'MAX_PACKET_BYTES',512*1024*1024)
    monkeypatch.setattr(r,'MAX_TOTAL_PACKET_BYTES',len(b'original packet bytes\n'))
    with pytest.raises(ValueError,match='Total packet inventory'):
        r.capture(root,tmp_path/'total',expected_manifests=pins)


def test_failed_private_stage_is_preserved_and_output_not_created(example,tmp_path,monkeypatch):
    root,pins=example;real=r._records;counter=0
    def changing(*args,**kwargs):
        nonlocal counter
        counter+=1
        if counter==3:raise ValueError('simulated original source mutation')
        return real(*args,**kwargs)
    monkeypatch.setattr(r,'_records',changing);out=tmp_path/'final'
    with pytest.raises(ValueError,match='simulated original source mutation'):
        r.capture(root,out,expected_manifests=pins)
    assert not out.exists()
    stages=list(tmp_path.glob('.retained-source-stage-*'))
    assert len(stages)==1 and (stages[0]/'manifest.json').is_file() and (stages[0]/'sources.tar.gz').is_file()


def test_concurrent_output_is_not_replaced_or_deleted(example,tmp_path,monkeypatch):
    root,pins=example;out=tmp_path/'final'
    def competing(stage,destination):
        destination.mkdir();(destination/'user-data').write_text('keep')
        raise FileExistsError('simulated competing destination')
    monkeypatch.setattr(r,'_rename_noreplace',competing)
    with pytest.raises(FileExistsError):r.capture(root,out,expected_manifests=pins)
    assert (out/'user-data').read_text()=='keep'
    assert len(list(tmp_path.glob('.retained-source-stage-*')))==1


def test_atomic_no_replace_never_overwrites_existing_directory(tmp_path):
    source=tmp_path/'source';source.mkdir();(source/'new').write_text('new')
    target=tmp_path/'existing';target.mkdir();(target/'user-data').write_text('keep')
    with pytest.raises(FileExistsError):r._rename_noreplace(source,target)
    assert (target/'user-data').read_text()=='keep' and (source/'new').read_text()=='new'
