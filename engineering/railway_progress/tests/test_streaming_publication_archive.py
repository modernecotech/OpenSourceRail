"""The continuing publication archive is deterministic and streamed to disk."""
import hashlib
import fcntl
import gzip
import io
import json
import os
import stat
import tarfile

import pytest

from engineering.railway_progress import archive
from engineering.railway_progress import coordinator


@pytest.fixture(autouse=True)
def isolated_cache_directory(tmp_path,monkeypatch):
    monkeypatch.setenv('XDG_CACHE_HOME',str(tmp_path/'xdg-cache'))


def test_streaming_archive_round_trips_deterministically(tmp_path, monkeypatch):
    state=tmp_path/'state';state.mkdir()
    (state/'latest.json').write_bytes(b'{"schema":"fixture"}\n')
    (state/'cases').mkdir()
    payload=(b'engineering evidence\n'*8192)
    (state/'cases'/'result.json.gz').write_bytes(payload)
    (state/'cases'/'.coordinator.lock').write_bytes(b'nested lock')
    (state/'.coordinator.lock').write_bytes(b'lock')
    first=tmp_path/'first.tar.gz';second=tmp_path/'second.tar.gz'

    # The implementation must stream file handles; loading a complete member
    # or final archive with Path.read_bytes would defeat the memory bound.
    def forbidden_read_bytes(self):
        if self.is_relative_to(state):
            raise AssertionError('publication source was materialized with read_bytes')
        return original_read_bytes(self)
    original_read_bytes=type(state).read_bytes
    monkeypatch.setattr(type(state),'read_bytes',forbidden_read_bytes)

    archive.write_streaming_archive(state,first)
    archive.write_streaming_archive(state,second)
    assert first.read_bytes()==second.read_bytes()
    with tarfile.open(first,'r:gz') as tar:
        members=tar.getmembers()
        assert [member.name for member in members]==['cases/result.json.gz','latest.json']
        assert all(member.mtime==member.uid==member.gid==0 and member.mode==0o644 for member in members)
        assert hashlib.sha256(tar.extractfile('cases/result.json.gz').read()).digest()==hashlib.sha256(payload).digest()
        assert tar.extractfile('latest.json').read()==b'{"schema":"fixture"}\n'


def _consume_tar_and_finish(compressed_bytes):
    with gzip.GzipFile(fileobj=io.BytesIO(compressed_bytes),mode='rb') as stream:
        bounded=archive.BoundedReader(stream,1024**2)
        with tarfile.open(fileobj=bounded,mode='r|') as tar:
            assert list(tar)==[]
        bounded.finish()


def test_bounded_reader_requires_both_tar_end_blocks():
    with pytest.raises(ValueError,match='Second TAR terminator block'):
        _consume_tar_and_finish(gzip.compress(bytes(512),mtime=0))


def test_bounded_reader_rejects_nonzero_bytes_after_tar_end_blocks():
    with pytest.raises(ValueError,match='Nonzero data follows TAR end markers'):
        _consume_tar_and_finish(gzip.compress(bytes(1024)+b'unsigned',mtime=0))


def test_bounded_reader_consumes_and_checks_the_gzip_trailer():
    damaged=bytearray(gzip.compress(bytes(1024),mtime=0));damaged[-8]^=1
    with pytest.raises(gzip.BadGzipFile,match='CRC check failed'):
        _consume_tar_and_finish(bytes(damaged))


@pytest.mark.parametrize('target_kind',['file','directory'])
def test_streaming_archive_refuses_symlinks_and_removes_partial_output(tmp_path,target_kind):
    state=tmp_path/'state';state.mkdir();outside=tmp_path/'outside'
    if target_kind=='file':outside.write_bytes(b'protected')
    else:outside.mkdir()
    (state/'linked').symlink_to(outside,target_is_directory=target_kind=='directory')
    output=tmp_path/'archive.tar.gz'
    with pytest.raises(ValueError,match='Linked continuing artifact'):
        archive.write_streaming_archive(state,output)
    assert not output.exists()
    assert sorted(path.name for path in tmp_path.glob('archive.tar.gz.tmp-*'))==[]


def test_streaming_archive_refuses_destination_inside_source_directory(tmp_path):
    state=tmp_path/'state';state.mkdir();(state/'latest.json').write_bytes(b'{}')
    output=state/'publication.tar.gz'
    with pytest.raises(ValueError,match='outside its source directory'):
        archive.write_streaming_archive(state,output)
    assert not output.exists()
    assert sorted(path.name for path in state.glob('publication.tar.gz.tmp-*'))==[]


def test_streaming_archive_refuses_symlinked_destination_parent(tmp_path):
    state=tmp_path/'state';state.mkdir();external=tmp_path/'external';external.mkdir()
    linked=tmp_path/'linked-parent';linked.symlink_to(external,target_is_directory=True)
    with pytest.raises(ValueError,match='Symlinked or non-directory archive path'):
        archive.write_streaming_archive(state,linked/'archive.tar.gz')
    assert not (external/'archive.tar.gz').exists()


def test_streaming_archive_honors_the_reader_byte_budget(tmp_path,monkeypatch):
    state=tmp_path/'state';state.mkdir();(state/'payload.bin').write_bytes(b'12345')
    monkeypatch.setattr(archive,'MAX_ARCHIVE_UNCOMPRESSED_BYTES',4)
    output=tmp_path/'archive.tar.gz'
    with pytest.raises(ValueError,match='verified member or byte budget'):
        archive.write_streaming_archive(state,output)
    assert not output.exists()
    assert sorted(path.name for path in tmp_path.glob('archive.tar.gz.tmp-*'))==[]


def test_streaming_archive_rejects_windows_separator_member_names(tmp_path):
    state=tmp_path/'state';state.mkdir();(state/'..\\outside').write_bytes(b'protected')
    output=tmp_path/'archive.tar.gz'
    with pytest.raises(ValueError,match='Ordinary relative archive member'):
        archive.write_streaming_archive(state,output)
    assert not output.exists()


@pytest.mark.parametrize('name',['../outside','/absolute','a\\..\\outside','C:/outside','file:stream','a//b','./file','café.txt'])
def test_archive_member_names_are_portable_and_relative(name):
    with pytest.raises(ValueError,match='Ordinary relative archive member'):
        archive.validate_tar_member_name(name)


def test_archive_member_path_length_is_bounded():
    with pytest.raises(ValueError,match='Ordinary relative archive member'):
        archive.validate_tar_member_name('a'*(archive.MAX_ARCHIVE_PATH_CHARS+1))


def test_compressed_archive_writer_enforces_its_output_budget(tmp_path,monkeypatch):
    state=tmp_path/'state';state.mkdir();(state/'payload').write_bytes(b'x'*4096)
    output=tmp_path/'archive.tar.gz'
    monkeypatch.setattr(archive,'MAX_COMPRESSED_ARCHIVE_BYTES',1)
    with pytest.raises(ValueError,match='Compressed continuing archive'):
        archive.write_streaming_archive(state,output)
    assert not output.exists()


def test_streaming_archive_bounds_directory_entries(tmp_path,monkeypatch):
    state=tmp_path/'state';state.mkdir();(state/'one').write_bytes(b'1');(state/'two').write_bytes(b'2')
    output=tmp_path/'archive.tar.gz'
    monkeypatch.setattr(archive,'MAX_ARCHIVE_TREE_ENTRIES',1)
    with pytest.raises(ValueError,match='tree exceeds its entry budget'):
        archive.write_streaming_archive(state,output)
    assert not output.exists()


def test_sha256_file_enforces_compressed_byte_budget(tmp_path):
    state=tmp_path/'state';state.mkdir();(state/'archive.tar.gz').write_bytes(b'012345')
    with pytest.raises(ValueError,match='byte budget'):
        archive.sha256_file(state,'archive.tar.gz',maximum_bytes=5)


def test_staging_fsync_failure_leaves_no_partial_publication_bundle(tmp_path,monkeypatch):
    state=tmp_path/'state';state.mkdir();output=tmp_path/'publication'
    output.mkdir()
    archive.ensure_directory(tmp_path/'xdg-cache/opensourcerail/publication-locks')
    coordinator._write(state/'latest.json',{'run_id':'a'*64,'cases':[],'pending':[]})
    monkeypatch.setattr(coordinator,'verify',lambda *args,**kwargs:{'verified':True})
    original_fsync=archive.os.fsync;calls=[]
    def fail_directory_sync(descriptor):
        calls.append(descriptor)
        if len(calls)==2:raise OSError('directory fsync unavailable')
        return original_fsync(descriptor)
    monkeypatch.setattr(archive.os,'fsync',fail_directory_sync)
    with pytest.raises(OSError,match='directory fsync unavailable'):
        coordinator.publish(state,root=tmp_path,output=output)
    assert not (output/'continuing-cell.tar.gz').exists()
    assert not (output/'summary.json').exists()
    assert not (output/'manifest.json').exists()
    assert sorted(path.name for path in output.glob('continuing-cell.tar.gz.tmp-*'))==[]


def test_bundle_commit_restores_previous_files_after_directory_fsync_failure(tmp_path,monkeypatch):
    output=tmp_path/'publication';output.mkdir();staging=output/'.stage';staging.mkdir()
    names=('continuing-cell.tar.gz','summary.json','manifest.json')
    old={name:f'old {name}'.encode() for name in names}
    for name in names:
        (output/name).write_bytes(old[name]);(staging/name).write_bytes(f'new {name}'.encode())
    target_stat=output.stat();original_fsync=archive.os.fsync;target_syncs=[]
    def fail_second_target_sync(descriptor):
        info=os.fstat(descriptor)
        if stat.S_ISDIR(info.st_mode) and (info.st_dev,info.st_ino)==(target_stat.st_dev,target_stat.st_ino):
            target_syncs.append(descriptor)
            if len(target_syncs)==3:raise OSError('publication directory sync failed')
        return original_fsync(descriptor)
    monkeypatch.setattr(archive.os,'fsync',fail_second_target_sync)
    with pytest.raises(OSError,match='publication directory sync failed'):
        archive.replace_file_bundle(staging,output,names)
    assert {name:(output/name).read_bytes() for name in names}==old
    assert list(staging.iterdir())==[]


@pytest.mark.parametrize('interruption',['backup','install'])
def test_bundle_rollback_detects_renames_interrupted_before_bookkeeping(tmp_path,monkeypatch,interruption):
    output=tmp_path/'publication';output.mkdir();staging=output/'.stage';staging.mkdir()
    names=('continuing-cell.tar.gz','summary.json','manifest.json')
    old={name:f'old {name}'.encode() for name in names}
    for name in names:
        (output/name).write_bytes(old[name]);(staging/name).write_bytes(f'new {name}'.encode())
    original_replace=archive.os.replace;interrupted=False
    def interrupt_after_rename(source,destination,*args,**kwargs):
        nonlocal interrupted
        result=original_replace(source,destination,*args,**kwargs)
        is_backup=source in names and isinstance(destination,str) and destination.startswith('.old-')
        is_install=source==destination and source in names
        if not interrupted and ((interruption=='backup' and is_backup) or (interruption=='install' and is_install)):
            interrupted=True
            raise KeyboardInterrupt('simulated signal after successful rename')
        return result
    monkeypatch.setattr(archive.os,'replace',interrupt_after_rename)
    with pytest.raises(KeyboardInterrupt,match='simulated signal'):
        archive.replace_file_bundle(staging,output,names)
    assert interrupted
    assert {name:(output/name).read_bytes() for name in names}==old


def test_incomplete_bundle_rollback_retains_recovery_files(tmp_path,monkeypatch):
    state=tmp_path/'state';state.mkdir();output=tmp_path/'publication';output.mkdir()
    coordinator._write(state/'latest.json',{'run_id':'a'*64,'cases':[],'pending':[]})
    names=('continuing-cell.tar.gz','summary.json','manifest.json')
    for name in names:(output/name).write_bytes(f'previous {name}'.encode())
    monkeypatch.setattr(coordinator,'verify',lambda *args,**kwargs:{'verified':True})
    monkeypatch.setattr(coordinator,'sources',lambda root:{})
    target_stat=output.stat();original_fsync=archive.os.fsync;original_replace=archive.os.replace;target_syncs=[]
    def fail_commit_sync(descriptor):
        info=os.fstat(descriptor)
        if stat.S_ISDIR(info.st_mode) and (info.st_dev,info.st_ino)==(target_stat.st_dev,target_stat.st_ino):
            target_syncs.append(descriptor)
            if len(target_syncs)==3:raise OSError('commit fsync fixture')
        return original_fsync(descriptor)
    def fail_backup_restore(source,destination,*args,**kwargs):
        if isinstance(source,str) and source.startswith('.old-'):
            raise OSError('restore fixture')
        return original_replace(source,destination,*args,**kwargs)
    monkeypatch.setattr(archive.os,'fsync',fail_commit_sync)
    monkeypatch.setattr(archive.os,'replace',fail_backup_restore)
    with pytest.raises(archive.BundleRollbackError,match='recovery files retained') as error:
        coordinator.publish(state,root=tmp_path,output=output)
    assert error.value.staging.is_dir()
    backups=list(error.value.staging.glob('.old-*'))
    assert len(backups)==3
    assert not any((output/name).exists() for name in names)


def test_fdopen_failure_closes_descriptor_and_removes_partial_archive(tmp_path,monkeypatch):
    state=tmp_path/'state';state.mkdir();(state/'latest.json').write_bytes(b'{}')
    output=tmp_path/'archive.tar.gz';descriptors=[]
    def fail_fdopen(descriptor,*args,**kwargs):
        descriptors.append(descriptor)
        raise OSError('fdopen fixture failure')
    monkeypatch.setattr(archive.os,'fdopen',fail_fdopen)
    with pytest.raises(OSError,match='fdopen fixture failure'):
        archive.write_streaming_archive(state,output)
    assert len(descriptors)==1
    with pytest.raises(OSError):os.fstat(descriptors[0])
    assert not output.exists()
    assert sorted(path.name for path in tmp_path.glob('archive.tar.gz.tmp-*'))==[]


def test_publish_and_publication_reader_use_the_streamed_archive(tmp_path,monkeypatch):
    state=tmp_path/'state';state.mkdir();output=tmp_path/'publication'
    case_summary={'case':'fixture',**{key:False for key in coordinator.FLAGS}}
    latest={'run_id':'a'*64,'cases':[{'summary':case_summary}],'pending':[]}
    coordinator._write(state/'latest.json',latest)
    (state/'case.json.gz').write_bytes(b'bounded fixture payload')
    validation={'verified':True,'run_id':latest['run_id'],'cases':1,'pending':0,
        'semantic_replay_executed':False,'conditional_numerical_arrivals':0,
        'qualified_numerical_arrivals':0,**coordinator.FLAGS}
    # This fixture exercises publication packing/inventory; the full engineering
    # campaign verifier needs a source-bound run and is outside this archive test.
    monkeypatch.setattr(coordinator,'verify',lambda *args,**kwargs:validation)
    monkeypatch.setattr(coordinator,'sources',lambda root: {})
    original_read_bytes=type(output).read_bytes
    def forbid_archive_materialization(path):
        if path.name=='continuing-cell.tar.gz':
            raise AssertionError('compressed publication archive was materialized for hashing')
        return original_read_bytes(path)
    monkeypatch.setattr(type(output),'read_bytes',forbid_archive_materialization)

    publication=coordinator.publish(state,root=tmp_path,output=output)
    result=coordinator.verify_publication(root=tmp_path,output=output)

    assert result['verified'] is True
    assert publication['files_sha256']['continuing-cell.tar.gz']

    archive_path=output/'continuing-cell.tar.gz'
    with archive_path.open('rb') as stream:raw=gzip.decompress(stream.read())
    archive_path.write_bytes(gzip.compress(raw+b'unsigned trailing data',mtime=0))
    manifest_path=output/'manifest.json'
    manifest=json.loads(manifest_path.read_bytes())
    with archive_path.open('rb') as stream:
        manifest['files_sha256']['continuing-cell.tar.gz']=hashlib.sha256(stream.read()).hexdigest()
    manifest['publication_id']=coordinator.identity({k:v for k,v in manifest.items() if k!='publication_id'})
    manifest_path.write_bytes(coordinator.encoded(manifest))
    with pytest.raises(ValueError,match='Nonzero data follows TAR end markers'):
        coordinator.verify_publication(root=tmp_path,output=output)


def test_publish_rejects_output_inside_run_before_creating_it(tmp_path,monkeypatch):
    state=tmp_path/'state';state.mkdir()
    monkeypatch.setattr(coordinator,'verify',lambda *args,**kwargs:{})
    with pytest.raises(ValueError,match='outside the run state'):
        coordinator.publish(state,root=tmp_path,output=state/'publication')
    assert not (state/'publication').exists()


def test_publish_rejects_symlinked_parent_before_creating_external_directories(tmp_path,monkeypatch):
    state=tmp_path/'state';state.mkdir();outside=tmp_path/'outside';outside.mkdir()
    linked=tmp_path/'linked-parent';linked.symlink_to(outside,target_is_directory=True)
    monkeypatch.setattr(coordinator,'verify',lambda *args,**kwargs:{})
    with pytest.raises(ValueError,match='Symlinked or non-directory archive path'):
        coordinator.publish(state,root=tmp_path,output=linked/'new'/'publication')
    assert not (outside/'new').exists()


def test_publish_preflights_all_output_files_before_replacing_any(tmp_path,monkeypatch):
    state=tmp_path/'state';state.mkdir();output=tmp_path/'publication';output.mkdir()
    outside=tmp_path/'outside.json';outside.write_bytes(b'protected')
    (output/'summary.json').symlink_to(outside)
    monkeypatch.setattr(coordinator,'verify',lambda *args,**kwargs:{})
    with pytest.raises(ValueError,match='Ordinary publication file'):
        coordinator.publish(state,root=tmp_path,output=output)
    assert outside.read_bytes()==b'protected'
    assert not (output/'continuing-cell.tar.gz').exists()


def test_publish_refuses_a_run_state_owned_by_an_active_coordinator(tmp_path,monkeypatch):
    state=tmp_path/'state';state.mkdir();output=tmp_path/'publication'
    lock_path=state/'.coordinator.lock'
    monkeypatch.setattr(coordinator,'verify',lambda *args,**kwargs:pytest.fail('verification ran while state was locked'))
    with lock_path.open('a') as lock:
        fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        with pytest.raises(ValueError,match='owns this run state'):
            coordinator.publish(state,root=tmp_path,output=output)
    assert not output.exists()


def test_publish_refuses_a_destination_owned_by_another_run(tmp_path,monkeypatch):
    state=tmp_path/'state';state.mkdir();output=tmp_path/'publication';output.mkdir()
    monkeypatch.setattr(coordinator,'verify',lambda *args,**kwargs:{})
    lock=coordinator._open_target_publication_lock(tmp_path,output)
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    try:
        with pytest.raises(ValueError,match='Another continuing publisher'):
            coordinator.publish(state,root=tmp_path,output=output)
    finally:
        fcntl.flock(lock,fcntl.LOCK_UN)
        os.close(lock)
    assert not (output/'continuing-cell.tar.gz').exists()


def test_publication_verification_refuses_a_destination_owned_by_writer(tmp_path):
    output=tmp_path/'publication';output.mkdir()
    lock=coordinator._open_target_publication_lock(tmp_path,output)
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    try:
        with pytest.raises(ValueError,match='Another continuing publisher'):
            coordinator.verify_publication(root=tmp_path,output=output)
    finally:
        fcntl.flock(lock,fcntl.LOCK_UN);os.close(lock)


def test_publication_target_locks_are_shared_across_worktree_roots(tmp_path):
    target=tmp_path/'shared-publication'
    first=coordinator._open_target_publication_lock(tmp_path/'worktree-one',target)
    second=coordinator._open_target_publication_lock(tmp_path/'worktree-two',target)
    try:
        assert os.fstat(first).st_ino==os.fstat(second).st_ino
        assert os.fstat(first).st_dev==os.fstat(second).st_dev
    finally:
        os.close(first);os.close(second)


def test_publication_reader_rejects_too_many_tar_members_while_streaming(tmp_path,monkeypatch):
    output=tmp_path/'publication';output.mkdir();archive_path=output/'continuing-cell.tar.gz'
    with tarfile.open(archive_path,'w:gz') as tar:
        for index in range(archive.MAX_ARCHIVE_MEMBERS+1):
            payload=f'{index}'.encode();info=tarfile.TarInfo(f'{index}.txt');info.size=len(payload)
            tar.addfile(info,io.BytesIO(payload))
    summary=coordinator.encoded({'fixture':True})
    (output/'summary.json').write_bytes(summary)
    validation={'verified':True}
    manifest={'schema':'osr-continuing-cell-publication/1','source_sha256':{},'run_id':'fixture',
        'validation':validation,'files_sha256':{'continuing-cell.tar.gz':hashlib.sha256(archive_path.read_bytes()).hexdigest(),
        'summary.json':hashlib.sha256(summary).hexdigest()},**coordinator.FLAGS}
    manifest['publication_id']=coordinator.identity(manifest)
    (output/'manifest.json').write_bytes(coordinator.encoded(manifest))
    monkeypatch.setattr(coordinator,'sources',lambda root:{})
    with pytest.raises(ValueError,match='Bounded ordinary continuing archive'):
        coordinator.verify_publication(root=tmp_path,output=output)


@pytest.mark.parametrize('archive_format',[tarfile.PAX_FORMAT,tarfile.GNU_FORMAT])
def test_publication_reader_rejects_gnu_or_pax_control_headers(tmp_path,monkeypatch,archive_format):
    output=tmp_path/'publication';output.mkdir();archive_path=output/'continuing-cell.tar.gz'
    with tarfile.open(archive_path,'w:gz',format=archive_format) as tar:
        payload=b'x';info=tarfile.TarInfo('a'*2_000_000);info.size=len(payload);tar.addfile(info,io.BytesIO(payload))
    summary=coordinator.encoded({'fixture':True});(output/'summary.json').write_bytes(summary)
    manifest={'schema':'osr-continuing-cell-publication/1','source_sha256':{},'run_id':'fixture',
        'validation':{'verified':True},'files_sha256':{'continuing-cell.tar.gz':hashlib.sha256(archive_path.read_bytes()).hexdigest(),
        'summary.json':hashlib.sha256(summary).hexdigest()},**coordinator.FLAGS}
    manifest['publication_id']=coordinator.identity(manifest);(output/'manifest.json').write_bytes(coordinator.encoded(manifest))
    monkeypatch.setattr(coordinator,'sources',lambda root:{})
    with pytest.raises(ValueError,match='control or special member headers'):
        coordinator.verify_publication(root=tmp_path,output=output)
