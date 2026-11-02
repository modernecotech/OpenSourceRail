"""Transport/import guards use tiny fixtures, never physical evidence."""
from pathlib import Path
import hashlib, importlib.util, io, json, subprocess, sys, tarfile
import pytest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('retained_frame_replay',ROOT/'tools/automation/replay-retained-frame.py')
x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x)


def archive(path,entries):
    with tarfile.open(path,'w:gz') as tar:
        for name,raw,kind in entries:
            info=tarfile.TarInfo(name);info.type=kind;info.size=len(raw) if kind==tarfile.REGTYPE else 0
            if kind==tarfile.SYMTYPE:info.linkname='/outside'
            tar.addfile(info,io.BytesIO(raw) if info.isfile() else None)


@pytest.mark.parametrize('names',[['../escape'],['/absolute'],['a/../escape'],['a//b'],['./alias'],['a\\b'],['duplicate','duplicate']])
def test_unsafe_or_aliased_tar_paths_never_extract(tmp_path,names):
    path=tmp_path/'bad.tar.gz';archive(path,[(n,b'x',tarfile.REGTYPE) for n in names]);target=tmp_path/'out'
    with pytest.raises(ValueError,match='Unsafe'):x.unpack(path,target)
    assert not target.exists() and not (tmp_path/'escape').exists()


def test_links_and_size_budgets_rejected_before_writes(tmp_path):
    path=tmp_path/'bad.tar.gz';archive(path,[('link',b'',tarfile.SYMTYPE)])
    with pytest.raises(ValueError,match='Unsafe'):x.unpack(path,tmp_path/'out')
    archive(path,[('large',b'12345',tarfile.REGTYPE)])
    with pytest.raises(ValueError,match='budget'):x.unpack(path,tmp_path/'out',max_raw=4)
    assert not (tmp_path/'out').exists()


def test_producer_hash_inventory_and_duplicate_checks_precede_source_writes(tmp_path):
    path=tmp_path/'sources.tar.gz';raw=b'raise RuntimeError("never import")'
    archive(path,[('producer.py',raw,tarfile.REGTYPE)]);sha=hashlib.sha256(raw).hexdigest()
    with pytest.raises(ValueError,match='hash differs'):x.unpack(path,tmp_path/'bad',expected={'producer.py':'0'*64})
    with pytest.raises(ValueError,match='inventory differs'):x.unpack(path,tmp_path/'missing',expected={'other.py':sha})
    assert not (tmp_path/'bad').exists() and not (tmp_path/'missing').exists()
    x.unpack(path,tmp_path/'good',expected={'producer.py':sha})
    assert (tmp_path/'good/producer.py').read_bytes()==raw


def test_resealed_release_and_untrusted_identity_rejected(tmp_path):
    value=dict(schema='fixture',**{k:False for k in x.FLAGS})
    value['publication_id']=hashlib.sha256(x.encoded(value)).hexdigest();x.seal(value,'publication_id')
    value['physical_accepted']=True;value.pop('publication_id');value['publication_id']=hashlib.sha256(x.encoded(value)).hexdigest()
    with pytest.raises(ValueError,match='acceptance flag'):x.seal(value,'publication_id')
    pub=tmp_path/'publication';pub.mkdir()
    for name in ('summary.json','frame-cell.tar.gz'):(pub/name).write_bytes(b'')
    value=dict(files={},**{k:False for k in x.FLAGS});value['publication_id']=hashlib.sha256(x.encoded(value)).hexdigest()
    (pub/'manifest.json').write_bytes(x.encoded(value))
    with pytest.raises(ValueError,match='Trusted publication identity differs'):x.audit(pub,tmp_path/'output')
    assert not (tmp_path/'output').exists()


def test_parent_symlinks_cannot_redirect_extraction_or_publication(tmp_path):
    real=tmp_path/'real';real.mkdir();alias=tmp_path/'alias';alias.symlink_to(real,target_is_directory=True)
    with pytest.raises(ValueError,match='Unlinked'):x.audit(alias,tmp_path/'out')
    with pytest.raises(ValueError,match='Unlinked'):x.audit(real,alias/'out')


@pytest.mark.parametrize('body,expected',[
    ('import engineering.missing','Retained epoch lacks import engineering.missing'),
    ('import subprocess; subprocess.run(["true"])','Native/process reruns prohibited'),
])
def test_isolated_child_rejects_unpinned_imports_and_process_reruns(tmp_path,body,expected):
    source=tmp_path/'sources';helper=source/x.PRODUCER;helper.parent.mkdir(parents=True)
    (source/'engineering').mkdir()
    helper.write_text('def verify_publication(publication,root):\n '+body+'\n return {}\n')
    snapshot={'source_snapshot':{x.PRODUCER:{'sha256':x.digest(helper),'bytes':helper.stat().st_size}}}
    preflight=tmp_path/'preflight.json';preflight.write_bytes(x.encoded(snapshot))
    r=subprocess.run([sys.executable,'-I','-B','-c',x.BOOTSTRAP,str(source),str(tmp_path),str(preflight)],cwd=tmp_path,capture_output=True,text=True,timeout=15)
    assert r.returncode!=0 and expected in r.stderr


def test_git_reads_explicit_pinned_commit_blobs_not_worktree_or_head(tmp_path,monkeypatch):
    raw=b'immutable old code\n';blob=hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest();calls=[]
    def checked(command,**kwargs):
        calls.append((command,kwargs))
        if command[-2]=='rev-parse':return (x.GIT_COMMIT+'\n').encode()
        assert command[-2:]==['cat-file','--batch']
        assert kwargs['input']==(x.GIT_COMMIT+':engineering/missing.py\n').encode()
        return (blob+' blob '+str(len(raw))+'\n').encode()+raw+b'\n'
    monkeypatch.setattr(x.subprocess,'check_output',checked)
    (tmp_path/'engineering').mkdir();(tmp_path/'engineering/missing.py').write_bytes(b'WRONG CURRENT CODE')
    result=x.git_blobs(tmp_path,['engineering/missing.py'])
    assert result=={'engineering/missing.py':(raw,blob)}
    assert len(calls)==2 and all('HEAD' not in c for c,_ in calls)


def recovery_fixture(tmp_path,monkeypatch,*,wrong_binding=False,wrong_transport=False,link=False):
    source=tmp_path/'source';source.mkdir();publication=tmp_path/'publication';publication.mkdir()
    original='engineering/original.py';missing='engineering/missing.py'
    raw={original:b'original source\n',missing:b'recovered source\n'}
    (source/'engineering').mkdir();(source/original).write_bytes(raw[original])
    transport={}
    for name in ('manifest.json','summary.json','frame-cell.tar.gz'):
        data=('original '+name).encode();(publication/name).write_bytes(data)
        transport['docs/design-engine/frame-refinement/packet/'+name]=b'tampered' if wrong_transport else data
    calls=[]
    def blobs(repository,names):
        calls.append(list(names));return {n:((raw|transport)[n],('1' if n==original else '2')*40) for n in names}
    monkeypatch.setattr(x,'git_blobs',blobs)
    mode='120000' if link else '100644'
    listing=(mode+' blob '+'2'*40+'\t'+missing+'\0'+'100644 blob '+'3'*40+'\tengineering/tests/test_ignored.py\0').encode()
    monkeypatch.setattr(x.subprocess,'check_output',lambda *a,**kw:listing)
    expected={original:hashlib.sha256(raw[original]).hexdigest()}
    if wrong_binding:expected[original]='0'*64
    return source,publication,expected,calls,missing,raw[missing]


def test_git_recovery_records_each_new_source_and_excludes_tests(tmp_path,monkeypatch):
    source,pub,expected,calls,missing,raw=recovery_fixture(tmp_path,monkeypatch)
    supplements,audit=x.recover_closure(tmp_path,source,expected,{},pub)
    assert (source/missing).read_bytes()==raw and not (source/'engineering/tests').exists()
    assert set(supplements)=={missing} and audit['exact_bindings_verified']==1
    record=supplements[missing]
    assert record['git_commit']==x.GIT_COMMIT and record['git_blob']=='2'*40
    assert record['sha256']==hashlib.sha256(raw).hexdigest() and record['original_packet_hash_binding'] is False
    assert 'not original archived source' in record['provenance']


@pytest.mark.parametrize('failure',['binding','transport','link'])
def test_git_recovery_rejects_epoch_transport_or_link_mismatch_before_writing(tmp_path,monkeypatch,failure):
    source,pub,expected,calls,missing,raw=recovery_fixture(tmp_path,monkeypatch,wrong_binding=failure=='binding',wrong_transport=failure=='transport',link=failure=='link')
    with pytest.raises(ValueError,match='binding differs|publication differs|Unlinked'):
        x.recover_closure(tmp_path,source,expected,{},pub)
    assert not (source/missing).exists()


def test_git_other_revision_and_forged_object_identity_rejected(tmp_path,monkeypatch):
    monkeypatch.setattr(x.subprocess,'check_output',lambda *a,**kw:b'0'*40+b'\n')
    with pytest.raises(ValueError,match='commit differs'):x.git_blobs(tmp_path,['engineering/missing.py'])
    def forged(command,**kwargs):
        if command[-2]=='rev-parse':return (x.GIT_COMMIT+'\n').encode()
        return b'0000000000000000000000000000000000000000 blob 1\nx\n'
    monkeypatch.setattr(x.subprocess,'check_output',forged)
    with pytest.raises(ValueError,match='object identity differs'):x.git_blobs(tmp_path,['engineering/missing.py'])


def test_invalid_scope_is_rejected_before_publication_or_source_recovery(tmp_path,monkeypatch):
    monkeypatch.setattr(x,'audit',lambda *a,**k:pytest.fail('No preflight for an unsupported scope'))
    with pytest.raises(ValueError,match='scope required'):
        x.replay(tmp_path,tmp_path/'out',scope='arbitrary-code')
    with pytest.raises(ValueError,match='no attached publication'):
        x.replay(tmp_path,tmp_path/'out',scope='frame',attached_publication=tmp_path)


def test_scope_tool_recovery_records_exact_new_blob_and_refuses_existing_mismatch(tmp_path,monkeypatch):
    name=x.SCOPE_TOOLS['frame-audit'][0];raw=b'# pinned audit tool\n'
    monkeypatch.setattr(x,'git_blobs',lambda repository,names:{name:(raw,'a'*40)})
    report={'supplemental_sources':{}}
    x.recover_scope_tools('frame-audit',tmp_path,tmp_path,report)
    p=tmp_path/'sources'/name
    assert p.read_bytes()==raw
    record=report['supplemental_sources'][name]
    assert record['git_commit']==x.GIT_COMMIT and record['git_blob']=='a'*40
    assert record['sha256']==hashlib.sha256(raw).hexdigest() and record['original_packet_hash_binding'] is False
    p.write_bytes(b'wrong code')
    with pytest.raises(ValueError,match='tool source differs'):
        x.recover_scope_tools('frame-audit',tmp_path,tmp_path,report)


def test_attached_transport_must_match_exact_git_bytes_before_copy_or_import(tmp_path,monkeypatch):
    folder=tmp_path/'original';folder.mkdir();names=x.ATTACHMENTS['sourced-methods'][1]
    for name in names:(folder/name).write_bytes(b'tampered')
    monkeypatch.setattr(x,'git_blobs',lambda repository,paths:{n:(b'original','a'*40) for n in paths})
    with pytest.raises(ValueError,match='publication differs from pinned Git'):
        x.attach_scope('sourced-methods',folder,tmp_path,tmp_path,{})
    assert not (tmp_path/'attached-publication').exists()


def test_import_guard_checks_actual_blob_bytes_before_execution(tmp_path):
    source=tmp_path/'sources';helper=source/x.PRODUCER;helper.parent.mkdir(parents=True)
    helper.write_text('raise RuntimeError("tampered source executed")\n')
    preflight=tmp_path/'preflight.json';preflight.write_bytes(x.encoded({'source_snapshot':{x.PRODUCER:{'sha256':'0'*64,'bytes':helper.stat().st_size}}}))
    r=subprocess.run([sys.executable,'-I','-B','-c',x.BOOTSTRAP,str(source),str(tmp_path),str(preflight)],cwd=tmp_path,capture_output=True,text=True,timeout=15)
    assert r.returncode!=0 and 'Unaudited retained import' in r.stderr
    assert 'tampered source executed' not in r.stderr


def test_private_git_index_is_exact_retained_tree_and_never_uses_checkout_index(tmp_path):
    (tmp_path/'sources').mkdir()
    actual_index=Path(subprocess.check_output(['git','rev-parse','--git-path','index'],cwd=ROOT,text=True).strip())
    if not actual_index.is_absolute():actual_index=ROOT/actual_index
    before=x.digest(actual_index)
    report=x.private_git_index(ROOT,tmp_path)
    assert report['git_commit']==x.GIT_COMMIT
    assert Path(report['private_index']).is_relative_to(tmp_path)
    assert x.digest(report['private_index'])==report['index_sha256']
    assert report['index_entries']>0 and x.digest(actual_index)==before
    assert report['allowed_commands']==[['git','ls-files','--error-unmatch','--',name] for name in x.SCOPE_TOOLS['bolster-cell']]


@pytest.mark.parametrize('forbidden',[None,['git','status'],['git','ls-files','--error-unmatch','--','README.md']])
def test_bolster_child_allows_only_two_real_read_only_git_probes(tmp_path,forbidden):
    import os
    source=tmp_path/'sources';source.mkdir();index=x.private_git_index(ROOT,tmp_path)
    producer='tools/automation/sourced-bolster-package.py';helper=source/producer;helper.parent.mkdir(parents=True)
    commands=index['allowed_commands'] if forbidden is None else [forbidden]
    helper.write_text('import subprocess\ndef verify_publication(publication,root):\n'
        +' for command in '+repr(commands)+':\n'
        +'  subprocess.run(command,cwd=root,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)\n'
        +' return {"verified":True}\n')
    record={'replay_scope':'bolster-cell','private_git_index':index,
        'source_snapshot':{producer:{'sha256':x.digest(helper),'bytes':helper.stat().st_size}}}
    preflight=tmp_path/'preflight.json';preflight.write_bytes(x.encoded(record))
    env={k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_DIR=index['private_git_directory'],GIT_INDEX_FILE=index['private_index'],GIT_WORK_TREE=str(source),GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,GIT_CONFIG_SYSTEM=os.devnull,GIT_OPTIONAL_LOCKS='0',PATH=str(Path(index['git_executable']).parent)+os.pathsep+'/bin')
    result=subprocess.run([sys.executable,'-I','-B','-c',x.BOOTSTRAP,str(source),str(tmp_path/'publication'),str(preflight)],cwd=tmp_path,env=env,capture_output=True,text=True,timeout=15)
    if forbidden is None:assert result.returncode==0 and json.loads(result.stdout)=={'verified':True}
    else:assert result.returncode!=0 and 'Native/process reruns prohibited' in result.stderr
    assert x.digest(index['private_index'])==index['index_sha256']
