"""A local Git reconstruction never grants current evaluator admission."""
import hashlib
import io
from pathlib import Path
import subprocess
import tarfile

import pytest
from engineering.design_search import retained_packet_materialize as m


def oid(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def header(name,kind,size=0,link=''):
    t=tarfile.TarInfo(name);t.type=kind;t.size=size;t.linkname=link
    return t.tobuf(format=tarfile.USTAR_FORMAT)


def block(data):return data+b'\0'*((-len(data))%512)


def make_tar(entries,*,global_commit=m.ORIGINAL_COMMIT):
    comment=('52 comment='+global_commit+'\n').encode()
    parts=[header('pax_global_header',tarfile.XGLTYPE,len(comment)),block(comment)]
    for name,kind,data in entries:
        parts.append(header(name,kind,len(data) if kind in (tarfile.REGTYPE,tarfile.AREGTYPE) else 0))
        if kind in (tarfile.REGTYPE,tarfile.AREGTYPE):parts.append(block(data))
    parts.append(b'\0'*1024)
    return b''.join(parts)


def sample():
    prefix=m.ALLOWED_PREFIXES[0];name=prefix+'/sample.bin';data=b'historical source bytes'
    dirs=['docs','docs/design-engine',prefix]
    entries=[(x,tarfile.DIRTYPE,b'') for x in dirs]+[(name,tarfile.REGTYPE,data)]
    tree={name:dict(oid=oid(data),size=len(data))}
    return name,data,entries,tree


def test_bounded_git_tar_reconstructs_exact_blob_and_inventory(tmp_path):
    name,data,entries,tree=sample();root=tmp_path/'root';root.mkdir()
    result=m._extract_tar(io.BytesIO(make_tar(entries)),root,tree,m.ORIGINAL_COMMIT)
    assert (root/name).read_bytes()==data
    assert result==dict(file_count=1,directory_count=3,blob_bytes=len(data))


def test_traversal_symlink_duplicate_and_unlisted_members_are_rejected(tmp_path):
    name,data,entries,tree=sample()
    attacks=[entries[:-1]+[('../escaped',tarfile.REGTYPE,data)],
             entries[:-1]+[(name,tarfile.SYMTYPE,b'')],
             entries+[(name,tarfile.REGTYPE,data)],
             entries+[(m.ALLOWED_PREFIXES[0]+'/unlisted',tarfile.REGTYPE,b'')]]
    for n,attack in enumerate(attacks):
        root=tmp_path/str(n);root.mkdir()
        with pytest.raises(ValueError):m._extract_tar(io.BytesIO(make_tar(attack)),root,tree,m.ORIGINAL_COMMIT)
    assert not (tmp_path/'escaped').exists()


def test_git_blob_tamper_truncation_extensions_and_extra_tar_are_rejected(tmp_path):
    name,data,entries,tree=sample();root=tmp_path/'root';root.mkdir()
    bad=entries[:-1]+[(name,tarfile.REGTYPE,b'x'*len(data))]
    with pytest.raises(ValueError,match='Git blob'):m._extract_tar(io.BytesIO(make_tar(bad)),root,tree,m.ORIGINAL_COMMIT)
    root=tmp_path/'root2';root.mkdir()
    with pytest.raises(ValueError):m._extract_tar(io.BytesIO(make_tar(entries)[:-1000]),root,tree,m.ORIGINAL_COMMIT)
    root=tmp_path/'root3';root.mkdir()
    ext=entries[:-1]+[('unexpected-pax',tarfile.XHDTYPE,b'')]+entries[-1:]
    with pytest.raises(ValueError,match='extensions'):m._extract_tar(io.BytesIO(make_tar(ext)),root,tree,m.ORIGINAL_COMMIT)
    root=tmp_path/'root4';root.mkdir()
    with pytest.raises(ValueError,match='trailing'):
        m._extract_tar(io.BytesIO(make_tar(entries)+make_tar(entries)),root,tree,m.ORIGINAL_COMMIT)


def test_commit_pin_absent_git_and_conflicting_manifest_pins_fail_closed(tmp_path):
    with pytest.raises(ValueError,match='exact|Exact'):
        m._pin_commit('0'*40)
    with pytest.raises(ValueError,match='absent'):
        m._git_tree(tmp_path,m.ORIGINAL_COMMIT)
    archive=tmp_path/'archive';archive.mkdir()
    with pytest.raises(ValueError,match='entire packet catalog'):
        m.materialize(tmp_path,tmp_path/'out',archive,expected_commit=m.ORIGINAL_COMMIT,
            expected_manifests={'wrong':'0'*64},expected_archive_id='0'*64)


def test_existing_destination_and_internal_source_tree_are_untouched(tmp_path):
    repo=tmp_path/'repo';repo.mkdir();archive=tmp_path/'archive';archive.mkdir()
    pins={name:'0'*64 for name in m.retained.CATALOG};out=tmp_path/'out';out.mkdir();(out/'user-data').write_text('keep')
    with pytest.raises(FileExistsError):m.materialize(repo,out,archive,expected_commit=m.ORIGINAL_COMMIT,expected_manifests=pins,expected_archive_id='1'*64)
    assert (out/'user-data').read_text()=='keep'
    with pytest.raises(ValueError,match='separate'):
        m.materialize(repo,repo/'within',archive,expected_commit=m.ORIGINAL_COMMIT,expected_manifests=pins,expected_archive_id='1'*64)
    assert not (repo/'within').exists()


class FakeProcess:
    def __init__(self,raw): self.stdout=io.BytesIO(raw)
    def wait(self,timeout=None):return 0
    def poll(self):return 0
    def kill(self):pass


def test_changed_git_tree_or_failed_archive_verification_never_hands_off(tmp_path,monkeypatch):
    repo=tmp_path/'repo';repo.mkdir();archive=tmp_path/'archive';archive.mkdir();name,data,entries,tree=sample()
    pins={name:'0'*64 for name in m.retained.CATALOG};calls=[]
    def tree_changed(*args):
        calls.append(1)
        return tree if len(calls)==1 else dict(tree,**{'x':dict(oid='1'*40,size=1)})
    monkeypatch.setattr(m,'_git_tree',tree_changed)
    monkeypatch.setattr(m,'_check_manifest_pins',lambda *args:None)
    monkeypatch.setattr(m,'_preflight_archive',lambda *args:('a','b'))
    monkeypatch.setattr(subprocess,'Popen',lambda *args,**kw:FakeProcess(make_tar(entries)))
    out=tmp_path/'out'
    with pytest.raises(ValueError,match='inventory changed'):
        m.materialize(repo,out,archive,expected_commit=m.ORIGINAL_COMMIT,expected_manifests=pins,expected_archive_id='1'*64)
    assert not out.exists() and len(list(tmp_path.glob('.retained-packets-stage-*')))==1
    monkeypatch.setattr(m,'_git_tree',lambda *args:tree)
    def fail_verify(*args,**kw):raise ValueError('injected archival verification failure')
    monkeypatch.setattr(m.retained,'verify',fail_verify)
    with pytest.raises(ValueError,match='injected archival'):
        m.materialize(repo,out,archive,expected_commit=m.ORIGINAL_COMMIT,expected_manifests=pins,expected_archive_id='1'*64)
    assert not out.exists() and len(list(tmp_path.glob('.retained-packets-stage-*')))==2


def test_absent_commit_in_real_local_git_repo_never_fetches(tmp_path):
    repo=tmp_path/'empty-repo'
    subprocess.run(['git','init','--quiet',str(repo)],check=True)
    with pytest.raises(ValueError,match='absent or not a commit'):
        m._git_tree(repo,m.ORIGINAL_COMMIT)
    assert m._environment()['GIT_NO_LAZY_FETCH']=='1'


def test_conflicting_original_manifest_pin_is_rejected_before_extraction(tmp_path,monkeypatch):
    contract=('test/1','source_sha256','files_sha256','manifest_id',None)
    monkeypatch.setattr(m.retained,'CATALOG',{'one':contract})
    manifest=dict(schema='test/1',source_sha256={},files_sha256={});manifest['manifest_id']=m.retained._id(manifest)
    raw=m.retained._encoded(manifest);name='docs/design-engine/one/manifest.json';tree={name:dict(oid=oid(raw),size=len(raw))}
    monkeypatch.setattr(subprocess,'run',lambda *args,**kwargs:subprocess.CompletedProcess(args,0,stdout=raw,stderr=b''))
    with pytest.raises(ValueError,match='pinned original Git packet manifest differs'):
        m._check_manifest_pins(tmp_path,m.ORIGINAL_COMMIT,{'one':'0'*64},tree)


def test_competing_output_or_changed_source_archive_cannot_be_handed_off(tmp_path,monkeypatch):
    repo=tmp_path/'repo';repo.mkdir();archive=tmp_path/'archive';archive.mkdir();name,data,entries,tree=sample()
    pins={name:'0'*64 for name in m.retained.CATALOG};out=tmp_path/'out'
    monkeypatch.setattr(m,'_git_tree',lambda *args:tree)
    monkeypatch.setattr(m,'_check_manifest_pins',lambda *args:None)
    monkeypatch.setattr(subprocess,'Popen',lambda *args,**kw:FakeProcess(make_tar(entries)))
    monkeypatch.setattr(m.retained,'verify',lambda *args,**kw:{'verified':True})
    seen=[]
    def changed_archive(*args):
        seen.append(1);return ('one','two') if len(seen)==1 else ('changed','two')
    monkeypatch.setattr(m,'_preflight_archive',changed_archive)
    with pytest.raises(ValueError,match='source archive changed'):
        m.materialize(repo,out,archive,expected_commit=m.ORIGINAL_COMMIT,expected_manifests=pins,expected_archive_id='1'*64)
    assert not out.exists()
    monkeypatch.setattr(m,'_preflight_archive',lambda *args:('one','two'))
    def competing(stage,destination):
        destination.mkdir();(destination/'user-data').write_text('keep');raise FileExistsError('competing output')
    monkeypatch.setattr(m.retained,'_rename_noreplace',competing)
    with pytest.raises(FileExistsError):
        m.materialize(repo,out,archive,expected_commit=m.ORIGINAL_COMMIT,expected_manifests=pins,expected_archive_id='1'*64)
    assert (out/'user-data').read_text()=='keep'
    assert len(list(tmp_path.glob('.retained-packets-stage-*')))==2


def test_unlisted_materialized_file_injected_during_verification_is_rejected(tmp_path,monkeypatch):
    repo=tmp_path/'repo';repo.mkdir();archive=tmp_path/'archive';archive.mkdir();name,data,entries,tree=sample()
    pins={name:'0'*64 for name in m.retained.CATALOG};out=tmp_path/'out'
    monkeypatch.setattr(m,'_git_tree',lambda *args:tree)
    monkeypatch.setattr(m,'_check_manifest_pins',lambda *args:None)
    monkeypatch.setattr(m,'_preflight_archive',lambda *args:('one','two'))
    monkeypatch.setattr(subprocess,'Popen',lambda *args,**kw:FakeProcess(make_tar(entries)))
    def inject(root,*args,**kw):
        (root/'unlisted').write_text('unexpected');return {'verified':True}
    monkeypatch.setattr(m.retained,'verify',inject)
    with pytest.raises(ValueError,match='unlisted or resized'):
        m.materialize(repo,out,archive,expected_commit=m.ORIGINAL_COMMIT,expected_manifests=pins,expected_archive_id='1'*64)
    assert not out.exists() and len(list(tmp_path.glob('.retained-packets-stage-*')))==1
