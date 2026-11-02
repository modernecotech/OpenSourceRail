#!/usr/bin/env python3
"""Replay a pinned frame publication in its retained source epoch.

This does not admit old evidence to current evaluators, establish physical
equivalence, or rerun native structural experiments. Archived code is executed
only after the publication, payload and source maps are authenticated. The child
uses an isolated interpreter and cooperative import/process guards, not an OS
sandbox. Missing Python sources are recovered only from the pinned Git tree;
each addition is indexed as newly recovered replay closure, not original evidence.
"""
from pathlib import Path, PurePosixPath
import argparse, gzip, hashlib, io, json, os, shutil, subprocess, sys, tarfile, time, traceback

PUBLICATION_ID='1571005998f338641f2f05ddd3f30a660a0f02a9ec695abd2193f942005b91e2'
GIT_COMMIT='b37988a750690d85939e5cbe7b2223b96c02980e'
PRODUCER='tools/automation/frame-cell.py'
FLAGS=('physical_accepted','engineering_accepted','manufacturing_release','operating_release','selected_reference_changed')
MAX_ARCHIVE=128*1024**2
MAX_RAW=768*1024**2
MAX_SOURCE=64*1024**2
SCOPES=('frame','frame-audit','sourced-methods','bolster-methods','bolster-cell')
ATTACHMENTS={
 'sourced-methods':('docs/design-engine/sourced-case',('structural-methods.json','structural-methods.tar.gz'),'4eaf74191d42cc602dc3190f5d15330fc50188682119782b40f803a6dad2fff6'),
 'bolster-methods':('docs/design-engine/sourced-bolster',('structural-methods.json','structural-methods.tar.gz'),'554a2eec232512b7449254573868e6113e273775a9d3e680116c99691920796b'),
 'bolster-cell':('docs/design-engine/sourced-bolster',('bolster-cell.json','bolster-cell.tar.gz'),'d9782cb747585156c1344e0bab154aa9c99ad12b773aee5dbea2ae8c2013fe56'),
}
SCOPE_TOOLS={'frame-audit':('tools/automation/audit-frame-states.py',),
 'bolster-cell':('tools/automation/sourced-bolster-cell.py','tools/automation/sourced-bolster-package.py')}


def encoded(v):
    return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def safe_name(name):
    p=PurePosixPath(name)
    if not name or any(ord(c)<32 for c in name) or '\\' in name or p.is_absolute() or any(x in ('','.','..') for x in name.split('/')):
        raise ValueError('Unsafe archive/source path')
    return name


def regular(path,limit):
    path=Path(path)
    if any(p.is_symlink() for p in (path,*path.parents)) or not path.is_file() or path.stat().st_size>limit:
        raise ValueError('Bounded regular unlinked input required')
    return path


def read(path):
    regular(path,MAX_SOURCE)
    return json.loads(Path(path).read_bytes())


def seal(value,key):
    actual=hashlib.sha256(encoded({k:v for k,v in value.items() if k!=key})).hexdigest()
    if value.get(key)!=actual:raise ValueError('Recorded identity differs: '+key)
    for flag in FLAGS:
        if value.get(flag) is not False:raise ValueError('Unsupported acceptance flag: '+flag)


def inventory(folder):
    result={}
    for p in sorted(Path(folder).rglob('*')):
        if p.is_symlink() or not(p.is_file() or p.is_dir()):raise ValueError('Ordinary payload required')
        if p.is_file():result[p.relative_to(folder).as_posix()]={'bytes':p.stat().st_size,'sha256':digest(p)}
    return result


def unpack(archive,target,*,expected=None,max_files=64,max_raw=MAX_RAW):
    """Preflight every member before writing; no links, aliases or overwrite."""
    regular(archive,MAX_ARCHIVE);target=Path(target)
    if target.exists():raise ValueError('Fresh extraction directory required')
    with tarfile.open(archive,'r:*') as tar:
        members=[];seen=set();total=0
        for m in tar:
            safe_name(m.name)
            if not m.isfile() or m.name in seen or m.size<0:raise ValueError('Unsafe/duplicate archive member')
            seen.add(m.name);total+=m.size
            if len(seen)>max_files or total>max_raw:raise ValueError('Extraction budget exceeded')
            members.append(m)
            if expected is not None:
                if m.name not in expected:raise ValueError('Source inventory differs')
                with tar.extractfile(m) as f:
                    h=hashlib.sha256()
                    for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
                if h.hexdigest()!=expected[m.name]:raise ValueError('Archived producer hash differs')
        if expected is not None and seen!=set(expected):raise ValueError('Source inventory differs')
        target.mkdir(parents=True)
        for m in members:
            dest=target/m.name;dest.parent.mkdir(parents=True,exist_ok=True)
            with tar.extractfile(m) as src,dest.open('xb') as dst:shutil.copyfileobj(src,dst)


def git_blobs(repository,names):
    """Read exact pinned blobs; working-tree bytes and HEAD are never fallbacks."""
    names=list(names)
    if len(names)>4096:raise ValueError('Git closure file budget exceeded')
    for name in names:safe_name(name)
    if not names:return {}
    commit=subprocess.check_output(['git','-C',str(repository),'rev-parse',GIT_COMMIT+'^{commit}'],timeout=15).decode().strip()
    if commit!=GIT_COMMIT:raise ValueError('Pinned Git commit differs')
    queries=('\n'.join(GIT_COMMIT+':'+n for n in names)+'\n').encode()
    raw=subprocess.check_output(['git','-C',str(repository),'cat-file','--batch'],input=queries,timeout=30)
    offset=0;total=0;result={}
    for name in names:
        end=raw.index(b'\n',offset);header=raw[offset:end].decode();offset=end+1
        if header.endswith(' missing'):raise ValueError('Pinned Git tree lacks '+name)
        blob,kind,size=header.split();size=int(size);total+=size
        if kind!='blob' or size<0 or total>MAX_SOURCE:raise ValueError('Git blob type/size budget differs')
        data=raw[offset:offset+size];offset+=size+1
        if len(data)!=size or raw[offset-1:offset]!=b'\n':raise ValueError('Truncated Git object response')
        if hashlib.sha1(('blob '+str(size)+'\0').encode()+data).hexdigest()!=blob:
            raise ValueError('Git blob object identity differs')
        result[name]=(data,blob)
    if offset!=len(raw):raise ValueError('Unexpected Git response')
    return result


def recover_closure(repository,sources,recorded,receipt,publication):
    """Authenticate all133 producer bindings and transport bytes before recovery."""
    expected=dict(recorded)
    for name,sha in receipt.items():
        if name in expected and expected[name]!=sha:raise ValueError('IFC producer epoch differs')
        expected[name]=sha
    transport=['docs/design-engine/frame-refinement/packet/'+n for n in ('manifest.json','summary.json','frame-cell.tar.gz')]
    blobs=git_blobs(repository,[*expected,*transport])
    for name,sha in expected.items():
        if hashlib.sha256(blobs[name][0]).hexdigest()!=sha:raise ValueError('Pinned Git producer binding differs: '+name)
    for name in transport:
        if blobs[name][0]!=Path(publication,name.rsplit('/',1)[1]).read_bytes():raise ValueError('Pinned Git original publication differs')
    listing=subprocess.check_output(['git','-C',str(repository),'ls-tree','-r','-z',GIT_COMMIT,'--','engineering','services/integration/osr_integration'],timeout=15)
    names=[];tree_blobs={}
    for row in listing.split(b'\0'):
        if not row:continue
        meta,raw_name=row.split(b'\t',1);mode,kind,blob=meta.decode().split();name=raw_name.decode();safe_name(name)
        if not name.endswith('.py') or 'tests' in PurePosixPath(name).parts or '__pycache__' in PurePosixPath(name).parts:continue
        if mode not in ('100644','100755') or kind!='blob':raise ValueError('Unlinked Git source blobs required')
        if not (Path(sources)/name).exists():names.append(name);tree_blobs[name]=blob
    additions=git_blobs(repository,names);supplements={}
    for name,(raw,blob) in additions.items():
        if tree_blobs[name]!=blob:raise ValueError('Pinned Git tree/blob differs')
        sha=hashlib.sha256(raw).hexdigest()
        if name in expected and sha!=expected[name]:raise ValueError('Recovered producer binding differs')
        dest=Path(sources)/name;dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('xb') as stream:stream.write(raw)
        supplements[name]=dict(git_commit=GIT_COMMIT,git_blob=blob,sha256=sha,bytes=len(raw),
            provenance='Newly recovered replay closure from immutable Git tree; not original archived source payload',
            original_packet_hash_binding=name in expected)
    for name,sha in expected.items():
        if digest(Path(sources)/name)!=sha:raise ValueError('Recovered source closure differs')
    return supplements,dict(git_commit=GIT_COMMIT,original_source_bindings=len(recorded),IFC_source_bindings=len(receipt),
        distinct_bindings=len(expected),exact_bindings_verified=len(expected),original_transport_files_verified=3)


def audit(publication,output,git_root=None,expected_publication_id=PUBLICATION_ID):
    publication=Path(publication).absolute();output=Path(output).absolute()
    if any(p.is_symlink() for p in (publication,*publication.parents,*output.parents)):
        raise ValueError('Unlinked publication and output parents required')
    publication=publication.resolve()
    if output.exists() or output.is_symlink():raise ValueError('Fresh private output required')
    if publication==output or publication in output.parents:raise ValueError('Output cannot mutate publication')
    if {p.name for p in publication.iterdir()}!={'manifest.json','summary.json','frame-cell.tar.gz'}:raise ValueError('Closed publication inventory required')
    pub=read(publication/'manifest.json');seal(pub,'publication_id')
    if pub['publication_id']!=expected_publication_id:raise ValueError('Trusted publication identity differs')
    if set(pub['files'])!={'summary.json','frame-cell.tar.gz'}:raise ValueError('Publication file set differs')
    for name,item in pub['files'].items():
        p=regular(publication/name,MAX_ARCHIVE)
        if item!={'bytes':p.stat().st_size,'sha256':digest(p)}:raise ValueError('Publication payload differs')
    output.mkdir(parents=True);packet=output/'packet'
    unpack(publication/'frame-cell.tar.gz',packet)
    manifest=read(packet/'manifest.json');seal(manifest,'package_id')
    actual=inventory(packet);actual.pop('manifest.json')
    if manifest['files']!=actual:raise ValueError('Inner payload inventory differs')
    if manifest['source_sha256']!=pub['source_sha256']:raise ValueError('Producer epoch differs')
    sources=output/'sources';unpack(packet/'input-sources.tar.gz',sources,expected=pub['source_sha256'],max_files=512,max_raw=MAX_SOURCE)
    if digest(packet/'helper-source.py')!=pub['source_sha256'][PRODUCER]:raise ValueError('Helper producer identity differs')
    if digest(sources/PRODUCER)!=digest(packet/'helper-source.py'):raise ValueError('Helper bytes differ')
    for name in ('ancestor-native','frame-native'):
        native=read(packet/name/'manifest.json');seal(native,'package_id')
        unpack(packet/name/'sources.tar',output/(name+'-sources'),expected=native['source_sha256'],max_files=512,max_raw=MAX_SOURCE)
        for path,sha in native['source_sha256'].items():
            if pub['source_sha256'].get(path)!=sha:raise ValueError('Native producer is outside retained epoch')
    receipt=read(packet/'ifc/V4.ifc.receipt.json')
    if git_root is None:raise ValueError('Explicit Git repository required for pinned replay closure')
    supplements,git_audit=recover_closure(git_root,sources,pub['source_sha256'],receipt['source_sha256'],publication)
    # Copy exact publication bytes: original strict verify-publication checks all
    # transport identities again, including its own complete 9-journey replay.
    retained=output/'publication';retained.mkdir()
    for name in ('manifest.json','summary.json','frame-cell.tar.gz'):shutil.copyfile(publication/name,retained/name)
    report=dict(schema='osr-retained-frame-replay/1',publication_id=pub['publication_id'],package_id=manifest['package_id'],
        candidate_id=manifest['candidate_id'],body_candidate_id=manifest['body_candidate_id'],evaluation_id=manifest['evaluation_id'],
        retained_source_sha256=pub['source_sha256'],supplemental_sources=supplements,git_epoch_audit=git_audit,source_snapshot=inventory(sources),
        original_publication_inventory=inventory(publication),current_evaluator_admission=False,physical_equivalence_established=False,
        numerical_native_recomputed=False,physical_qualification=None,**{k:False for k in FLAGS})
    (output/'preflight.json').write_bytes(encoded(report));return report


def attach_scope(scope,publication,output,repository,report):
    """Authenticate only this scope's original attached files before copying."""
    if scope not in ATTACHMENTS:return None
    relative,names,trusted_id=ATTACHMENTS[scope]
    folder=Path(publication).absolute()
    if any(p.is_symlink() for p in (folder,*folder.parents)):
        raise ValueError('Unlinked attached publication required')
    blobs=git_blobs(repository,[relative+'/'+name for name in names])
    for name in names:
        regular(folder/name,MAX_ARCHIVE)
        if (folder/name).read_bytes()!=blobs[relative+'/'+name][0]:
            raise ValueError('Attached publication differs from pinned Git epoch: '+name)
    descriptor=read(folder/names[0]);seal(descriptor,'publication_id')
    if descriptor['publication_id']!=trusted_id:raise ValueError('Trusted attached publication identity differs')
    if scope.endswith('methods'):
        if descriptor.get('schema')!='osr-sourced-structural-methods/1':raise ValueError('Structural methods schema differs')
        rows=descriptor.get('packages',[])
        if not 1<=len(rows)<=8 or len({row['name'] for row in rows})!=len(rows):raise ValueError('Bounded distinct method packages required')
        expected={row['name']+'/'+name:sha for row in rows for name,sha in row['files_sha256'].items()}
        bindings={};occurrences=0
        with tarfile.open(folder/names[1],'r:gz') as archive:
            members=archive.getmembers()
            if len(members)>100 or sum(m.size for m in members)>512*1024**2:raise ValueError('Method archive budget exceeded')
            if len({m.name for m in members})!=len(members) or any(not m.isfile() for m in members):raise ValueError('Ordinary unique method members required')
            actual={}
            for member in members:
                safe_name(member.name);actual[member.name]=hashlib.sha256(archive.extractfile(member).read()).hexdigest()
            if actual!=expected:raise ValueError('Method archive inventory differs')
            for row in rows:
                safe_name(row['name']);manifest=json.load(archive.extractfile(row['name']+'/manifest.json'));seal(manifest,'package_id')
                request=json.load(archive.extractfile(row['name']+'/input.json'));result=json.load(archive.extractfile(row['name']+'/result.json'))
                sources=manifest['source_sha256']
                if request['source_sha256']!=sources or result['source_sha256']!=sources:raise ValueError('Method producer bindings differ')
                with tarfile.open(fileobj=io.BytesIO(archive.extractfile(row['name']+'/sources.tar').read())) as source_tar:
                    source_members=source_tar.getmembers()
                    if len(source_members)>512 or sum(m.size for m in source_members)>MAX_SOURCE:raise ValueError('Method source archive budget exceeded')
                    source_hashes={}
                    for member in source_members:
                        safe_name(member.name)
                        if not member.isfile() or member.name in source_hashes:raise ValueError('Ordinary unique method sources required')
                        source_hashes[member.name]=hashlib.sha256(source_tar.extractfile(member).read()).hexdigest()
                    if source_hashes!=sources:raise ValueError('Method archived producer bytes differ')
                occurrences+=len(sources)
                for name,sha in sources.items():
                    if name in bindings and bindings[name]!=sha:raise ValueError('Mixed method source epochs')
                    bindings[name]=sha
        counts=dict(packages=len(rows),recorded_source_binding_occurrences=occurrences,
            distinct_source_bindings=len(bindings),recorded_contexts=sum(row['validation']['mesh_count']*9 for row in rows))
    else:
        if descriptor.get('schema')!='osr-sourced-bolster-cell-publication/1':raise ValueError('Bolster cell schema differs')
        if descriptor.get('archive_path')!=names[1] or descriptor.get('archive_sha256')!=digest(folder/names[1]):raise ValueError('Bolster archive binding differs')
        bindings=descriptor['source_sha256'];counts=dict(distinct_source_bindings=len(bindings))
    source_blobs=git_blobs(repository,bindings)
    for name,sha in bindings.items():
        if hashlib.sha256(source_blobs[name][0]).hexdigest()!=sha:raise ValueError('Attached producer differs from pinned epoch: '+name)
        if digest(Path(output)/'sources'/name)!=sha:raise ValueError('Attached producer absent from authenticated replay closure: '+name)
    target=Path(output)/'attached-publication';target.mkdir()
    for name in names:shutil.copyfile(folder/name,target/name)
    report['attached_scope']=dict(scope=scope,publication_id=trusted_id,git_commit=GIT_COMMIT,
        original_directory=str(folder),original_files={name:dict(bytes=(folder/name).stat().st_size,sha256=digest(folder/name)) for name in names},
        source_sha256=bindings,counts=counts)
    return folder


def recover_scope_tools(scope,repository,output,report):
    """Additional trusted tools are new replay closure, not original evidence."""
    names=SCOPE_TOOLS.get(scope,())
    for name,(raw,blob) in git_blobs(repository,names).items():
        target=Path(output)/'sources'/name
        if target.exists():
            if target.read_bytes()!=raw:raise ValueError('Retained tool source differs')
        else:
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
            report['supplemental_sources'][name]=dict(git_commit=GIT_COMMIT,git_blob=blob,
                sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),original_packet_hash_binding=False,
                provenance='Newly recovered scope tool from immutable Git tree; not original archived source payload')


def private_git_index(repository,output):
    """Build an isolated index from the authenticated complete retained tree."""
    git=Path(shutil.which('git')).resolve();output=Path(output)
    env={k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,GIT_CONFIG_SYSTEM=os.devnull,GIT_OPTIONAL_LOCKS='0')
    listing=subprocess.check_output([str(git),'-C',str(repository),'ls-tree','-r','-z',GIT_COMMIT],env=env,timeout=30)
    rows=listing.split(b'\0');entries=0
    for row in rows:
        if not row:continue
        meta,name=row.split(b'\t',1);mode,kind,blob=meta.decode().split();safe_name(name.decode())
        if mode not in ('100644','100755','120000') or kind!='blob':raise ValueError('Unexpected retained Git index entry')
        entries+=1
    directory=output/'private-git';subprocess.run([str(git),'init','--bare','--quiet','--template=',str(directory)],env=env,check=True,timeout=15)
    index=directory/'index';env.update(GIT_DIR=str(directory),GIT_INDEX_FILE=str(index),GIT_WORK_TREE=str(output/'sources'))
    subprocess.run([str(git),'update-index','-z','--index-info'],input=listing,env=env,check=True,timeout=30)
    names=list(SCOPE_TOOLS['bolster-cell']);commands=[]
    for name in names:
        command=['git','ls-files','--error-unmatch','--',name]
        actual=subprocess.check_output([str(git),*command[1:]],cwd=output/'sources',env=env,timeout=15)
        if actual.decode().strip()!=name:raise ValueError('Private retained Git index lacks required tool')
        commands.append(command)
    return dict(git_executable=str(git),git_executable_sha256=digest(git),git_commit=GIT_COMMIT,
        private_git_directory=str(directory),private_index=str(index),index_sha256=digest(index),
        retained_tree_listing_sha256=hashlib.sha256(listing).hexdigest(),index_entries=entries,
        allowed_commands=commands,cwd=str(output/'sources'),
        scope='Only two unchanged helper tracked-file probes; no current checkout index or general process permission')


BOOTSTRAP=r'''
import hashlib,importlib.abc,importlib.machinery,importlib.util,json,os,pathlib,sys
root=pathlib.Path(sys.argv[1]).resolve();publication=pathlib.Path(sys.argv[2]).resolve();report=json.loads(pathlib.Path(sys.argv[3]).read_text());snapshot=report['source_snapshot'];scope=report.get('replay_scope','frame')
def authenticate(p):
 p=pathlib.Path(p).resolve()
 try:name=p.relative_to(root).as_posix()
 except ValueError:raise ImportError('Import escaped retained root')
 if name not in snapshot or hashlib.sha256(p.read_bytes()).hexdigest()!=snapshot[name]['sha256']:raise ImportError('Unaudited retained import: '+name)
class Guard(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if fullname.split('.')[0] not in ('engineering','services','tools'):return None
  spec=importlib.machinery.PathFinder.find_spec(fullname,path)
  if spec is None:raise ImportError('Retained epoch lacks import '+fullname)
  if spec.origin and spec.origin not in ('built-in','frozen'):
   p=pathlib.Path(spec.origin).resolve()
   try:name=p.relative_to(root).as_posix()
   except ValueError:raise ImportError('Import escaped retained root: '+fullname)
   authenticate(p)
  for directory in spec.submodule_search_locations or []:
   if not pathlib.Path(directory).resolve().is_relative_to(root):raise ImportError('Namespace escaped retained root')
  return spec
sys.path.insert(0,str(root));sys.meta_path.insert(0,Guard())
git_queries=[]
def no_process(event,args):
 if event=='subprocess.Popen' and scope=='bolster-cell':
  executable,command,cwd,environment=args;allowed=report['private_git_index']
  if executable=='git' and command in allowed['allowed_commands'] and pathlib.Path(cwd).resolve()==root and environment is None and command not in git_queries:
   git_queries.append(command);return
 if event in ('subprocess.Popen','os.system','os.posix_spawn','os.posix_spawnp','os.fork','os.forkpty') or event.startswith('os.exec') or event.startswith('os.spawn'):raise RuntimeError('Native/process reruns prohibited in retained verification')
sys.addaudithook(no_process)
def tool(name,label):
 p=root/name;authenticate(p);spec=importlib.util.spec_from_file_location(label,p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
if scope=='frame':
 m=tool('tools/automation/frame-cell.py','retained_frame_producer');value=m.verify_publication(publication,root=root)
elif scope=='frame-audit':
 m=tool('tools/automation/audit-frame-states.py','retained_frame_auditor');packet=publication.parent/'packet'
 value=m.audit(packet/'frame-native',parent_native=packet/'ancestor-native',root=root)
elif scope in ('sourced-methods','bolster-methods'):
 from engineering.sourced_case import methods
 value=methods.verify(publication.parent/'attached-publication',root=root)
elif scope=='bolster-cell':
 m=tool('tools/automation/sourced-bolster-package.py','retained_bolster_producer');value=m.verify_publication(publication.parent/'attached-publication',root=root)
 if git_queries!=report['private_git_index']['allowed_commands']:raise RuntimeError('Exact retained Git probe inventory differs')
else:raise ValueError('Unsupported retained replay scope')
print(json.dumps(value,sort_keys=True),flush=True)
'''


def replay(publication,output,*,python=sys.executable,git_root=None,timeout_s=600,memory_bytes=4*1024**3,scope='frame',attached_publication=None):
    if not 0<timeout_s<=600:raise ValueError('Replay timeout must be at most600s')
    if memory_bytes<=0:raise ValueError('Positive memory limit required')
    if scope not in SCOPES:raise ValueError('Explicit bounded retained replay scope required')
    if attached_publication is not None and scope not in ATTACHMENTS:raise ValueError('This scope has no attached publication')
    output=Path(output).absolute();start=time.monotonic()
    report=audit(publication,output,git_root)
    report['replay_scope']=scope
    recover_scope_tools(scope,git_root,output,report)
    attached=None
    if scope in ATTACHMENTS:
        attached=attach_scope(scope,attached_publication or Path(git_root)/ATTACHMENTS[scope][0],output,git_root,report)
    if scope=='bolster-cell':report['private_git_index']=private_git_index(git_root,output)
    report['source_snapshot']=inventory(output/'sources');(output/'preflight.json').write_bytes(encoded(report))
    env={k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','OPENBLAS','OMP_','MKL_','NUMEXPR','GIT_'))}
    env.update(OPENBLAS_CORETYPE='NEHALEM',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
    env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,GIT_CONFIG_SYSTEM=os.devnull)
    if scope=='bolster-cell':
        index=report['private_git_index'];env.update(GIT_DIR=index['private_git_directory'],GIT_INDEX_FILE=index['private_index'],GIT_WORK_TREE=str(output/'sources'),GIT_OPTIONAL_LOCKS='0',PATH=str(Path(index['git_executable']).parent)+os.pathsep+'/bin')
    command=[str(python),'-I','-B','-c',BOOTSTRAP,str(output/'sources'),str(output/'publication'),str(output/'preflight.json')]
    report.update(command=command,timeout_s=timeout_s,memory_limit_bytes=memory_bytes,execution='failed',
        requested_runtime_environment={k:env[k] for k in ('OPENBLAS_CORETYPE','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')},
        isolation='Isolated Python import roots, archive/source integrity checks, Python process-spawn audit guard, RLIMIT_AS; no OS filesystem/network sandbox',
        permitted_child_processes=report.get('private_git_index',{}).get('allowed_commands',[]))
    def limit():
        import resource
        resource.setrlimit(resource.RLIMIT_AS,(memory_bytes,memory_bytes))
    try:
        with (output/'stdout.log').open('wb') as stdout,(output/'stderr.log').open('wb') as stderr:
            child=subprocess.run(command,cwd=output,env=env,stdout=stdout,stderr=stderr,timeout=timeout_s,preexec_fn=limit)
        report['exit_code']=child.returncode
        if child.returncode!=0:report['reason']='Strict retained verifier exited with code '+str(child.returncode)+'; see stderr.log'
        if child.returncode==0:
            check=json.loads((output/'stdout.log').read_text());report['retained_verification']=check
            if scope=='frame':
                if check.get('verified') is not True or check.get('semantic_replay_executed') is not True or check.get('actual_IFC_reopened') is not True or check.get('journeys')!=9:raise ValueError('Incomplete strict retained replay')
                if check.get('publication_id')!=report['publication_id']:raise ValueError('Replay publication differs')
            elif scope=='frame-audit':
                seal(check,'audit_id')
                if check.get('independent_saved_state_cases_checked')!=18 or check.get('equilibrium_and_energy_checks_passed') is not True or check.get('independent_fresh_solver_validation') is not False:raise ValueError('Incomplete retained saved-state audit')
            else:
                if check.get('verified') is not True or check.get('publication_id')!=report['attached_scope']['publication_id']:raise ValueError('Attached retained verification differs')
                if scope.endswith('methods') and (check.get('packages')!=report['attached_scope']['counts']['packages'] or check.get('physical_correlation') is not False):raise ValueError('Incomplete retained method verification')
                if scope=='bolster-cell' and (check.get('semantic_replay_executed') is not True or check.get('journeys')!=9 or check.get('native_fresh_solve_executed') is not False):raise ValueError('Incomplete retained bolster replay')
            report['execution']='completed'
    except BaseException as err:
        report['reason']=type(err).__name__+': '+str(err);(output/'failure.log').write_text(traceback.format_exc())
    report['elapsed_s']=time.monotonic()-start
    report['logs']={name:dict(bytes=(output/name).stat().st_size,sha256=digest(output/name)) for name in ('stdout.log','stderr.log') if (output/name).is_file()}
    if inventory(output/'sources')!=report['source_snapshot']:raise ValueError('Retained source bytes changed during replay')
    if inventory(publication)!=report['original_publication_inventory']:raise ValueError('Original publication changed during replay')
    if attached is not None:
        for name,expected in report['attached_scope']['original_files'].items():
            if {'bytes':(attached/name).stat().st_size,'sha256':digest(attached/name)}!=expected:raise ValueError('Original attached publication changed during replay')
    if scope=='bolster-cell':
        index=report['private_git_index']
        if digest(index['private_index'])!=index['index_sha256'] or digest(index['git_executable'])!=index['git_executable_sha256']:raise ValueError('Retained Git index or executable changed during replay')
    report['report_id']=hashlib.sha256(encoded(report)).hexdigest();(output/'report.json').write_bytes(encoded(report));return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('publication',type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--python',default=sys.executable);p.add_argument('--git-root',type=Path,required=True);p.add_argument('--timeout-s',type=int,default=600)
    p.add_argument('--scope',choices=SCOPES,default='frame');p.add_argument('--attached-publication',type=Path)
    a=p.parse_args();r=replay(a.publication,a.output,python=a.python,git_root=a.git_root,timeout_s=a.timeout_s,scope=a.scope,attached_publication=a.attached_publication);print(json.dumps(r,sort_keys=True,indent=2));return 0 if r['execution']=='completed' else 1
if __name__=='__main__':raise SystemExit(main())
