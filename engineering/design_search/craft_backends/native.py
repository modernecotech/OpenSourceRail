"""Pinned native tools, bounded private runs and recorded JSON command sessions."""
from hashlib import sha256
from pathlib import Path
from urllib.request import urlopen
import json, math, os, resource, shutil, subprocess, tarfile, time
from . import FLAGS, identity

ROOT = Path(__file__).resolve().parents[3]
LOCK = Path(__file__).with_name('tools.json')
DEFAULT_TOOLS = Path.home()/'.local/share/opensource-rail/toolchains/craft'


def digest(path):
    h=sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024**2),b''):h.update(block)
    return h.hexdigest()


def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():raise ValueError('Immutable output already exists: '+str(path))
    path.write_text(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n')


def pin(name):
    return json.loads(LOCK.read_bytes())['tools'][name]


def executable(name,tool_root=DEFAULT_TOOLS):
    p=pin(name);path=Path(tool_root)/p['directory']/p['binary']
    if not path.is_file() or path.is_symlink() or digest(path)!=p['binary_sha256']:
        raise ValueError('Pinned native executable unavailable or changed: '+name+'; use backends install')
    return path


def install(name,tool_root=DEFAULT_TOOLS):
    p=pin(name);folder=Path(tool_root)/p['directory'];folder.mkdir(parents=True,exist_ok=True)
    archive=folder/p['asset']
    if not archive.exists():
        pending=archive.with_suffix(archive.suffix+'.partial')
        if pending.exists():raise ValueError('Preserve interrupted download; inspect '+str(pending))
        with urlopen(p['url'],timeout=60) as src,pending.open('xb') as out:
            count=0
            while block:=src.read(1024**2):
                count+=len(block)
                if count>p['bytes']:raise ValueError('Release exceeds pinned download size; partial retained')
                out.write(block)
        if count!=p['bytes']:raise ValueError('Release download size differs; partial retained')
        if digest(pending)!=p['asset_sha256']:raise ValueError('Release download digest differs; failed file retained')
        pending.rename(archive)
    if digest(archive)!=p['asset_sha256']:raise ValueError('Pinned release archive changed')
    dist=folder/'dist'
    if not dist.exists():
        with tarfile.open(archive) as tar:
            members=tar.getmembers()
            if (sum(m.size for m in members)>2*1024**3 or len(members)>512
                or any(Path(m.name).is_absolute() or '..' in Path(m.name).parts or not (m.isfile() or m.isdir()) for m in members)):
                raise ValueError('Release requires a reviewed bounded ordinary-file inventory')
            tar.extractall(dist,filter='data')
    return dict(tool=name,executable=str(executable(name,tool_root)),pin=p,**FLAGS)


def _budget(memory_mb,timeout_s):
    if type(memory_mb) is not int or not 256<=memory_mb<=8192 or not 0<timeout_s<=600:
        raise ValueError('Bounded native worker resources required')
    resource.setrlimit(resource.RLIMIT_AS,(memory_mb*1024**2,)*2)
    resource.setrlimit(resource.RLIMIT_CPU,(math.ceil(timeout_s)+1,math.ceil(timeout_s)+2))
    resource.setrlimit(resource.RLIMIT_FSIZE,(64*1024**2,)*2)
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))


def run(name,args,folder,*,stdin=None,tool_root=DEFAULT_TOOLS,timeout_s=120,memory_mb=2048,read_roots=()):
    """No network, hidden home, read-only host; only this private run can be written."""
    folder=Path(folder).resolve();folder.mkdir(parents=True,exist_ok=False)
    binary=executable(name,tool_root);install_root=binary.parent.parent
    for part in ('config','cache','data','tmp'):(folder/part).mkdir()
    if not shutil.which('bwrap'):raise ValueError('Linux bubblewrap required for native pilot; no unconfined fallback')
    # Preserve the exact invocation, declared OS limits and stdin before execution.
    roots=[]
    for value in read_roots:
        p=Path(value).resolve()
        if not p.is_dir() or p==Path.home() or p in Path.home().parents or not folder.is_relative_to(p):
            raise ValueError('Read root must be this private run parent, never HOME or a system root')
        roots.append(p)
    invocation=dict(tool=name,pin=pin(name),arguments=list(map(str,args)),stdin=stdin,read_roots=list(map(str,roots)),
        resources=dict(memory_mb=memory_mb,timeout_s=timeout_s,file_limit_bytes=64*1024**2),**FLAGS)
    write(folder/'invocation.json',invocation)
    source=folder/'stdin.jsonl';source.write_text(stdin or '')
    env={k:os.environ[k] for k in ('PATH','HOME','LANG') if k in os.environ}
    env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',RAYON_NUM_THREADS='1',
        XDG_CONFIG_HOME=str(folder/'config'),XDG_CACHE_HOME=str(folder/'cache'),XDG_DATA_HOME=str(folder/'data'),
        TMPDIR=str(folder/'tmp'),FIELDCRAFT_GPU='cpu')
    cmd=['/usr/bin/time','-f','{"peak_rss_kib":%M,"user_s":%U,"system_s":%S,"exit":%x}',
         '-o',str(folder/'usage.json'),'bwrap','--die-with-parent','--unshare-net','--ro-bind','/','/',
         '--tmpfs','/home','--tmpfs','/root','--dev','/dev','--ro-bind',str(install_root),str(install_root)]
    for value in roots:cmd+=['--ro-bind',str(value),str(value)]
    cmd+=['--bind',str(folder),str(folder),'--chdir',str(folder),'--',str(binary),*map(str,args)]
    started=time.monotonic();timed_out=False
    with source.open('rb') as inp,(folder/'stdout.jsonl').open('wb') as out,(folder/'stderr.log').open('wb') as err:
        proc=subprocess.Popen(cmd,stdin=inp,stdout=out,stderr=err,env=env,start_new_session=True,
                              preexec_fn=lambda:_budget(memory_mb,timeout_s))
        try:code=proc.wait(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            from engineering.design_search.resource_limits import stop_group
            stop_group(proc.pid);code=proc.wait();timed_out=True
    usage=None
    if (folder/'usage.json').is_file():
        try:usage=json.loads((folder/'usage.json').read_text().splitlines()[-1])
        except (ValueError,IndexError):pass
    result=dict(execution='timed-out' if timed_out else 'executed' if code==0 else 'failed',
        returncode=code,elapsed_s=time.monotonic()-started,usage=usage,tool=name,
        invocation_id=identity(invocation),filesystem_write_scope=str(folder),
        isolation_requested=dict(network_unshared=True,home_hidden=True,graphics_devices_hidden=True),
        isolation_established_for_successful_execution=(code==0),
        scope_mechanism='Linux bubblewrap and POSIX resource limits; per-process address space, not aggregate cgroup memory',**FLAGS)
    write(folder/'execution.json',result)
    return result


def mcp(name,calls,folder,*,tool_root=DEFAULT_TOOLS,timeout_s=120,memory_mb=2048,read_root=None):
    folder=Path(folder).resolve();read=Path(read_root or folder.parent).resolve()
    args=['mcp','--headless']
    if name=='fieldcraft':args+=['--automation-read-root',str(read),'--automation-write-root',str(folder)]
    else:args+=['--allow-path',str(read),'--allow-path',str(folder)]
    messages=[dict(jsonrpc='2.0',id=1,method='initialize',params=dict(protocolVersion='2024-11-05',capabilities={},clientInfo=dict(name='OpenSourceRail',version='0.6')))]
    for i,(tool,arguments) in enumerate(calls,2):messages.append(dict(jsonrpc='2.0',id=i,method='tools/call',params=dict(name=tool,arguments=arguments)))
    text=''.join(json.dumps(x,allow_nan=False)+'\n' for x in messages)
    execution=run(name,args,folder,stdin=text,tool_root=tool_root,timeout_s=timeout_s,memory_mb=memory_mb,read_roots=(read,))
    replies=[]
    for line in (folder/'stdout.jsonl').read_text().splitlines():
        if line.strip():replies.append(json.loads(line))
    if execution['execution']=='executed':
        initial=next((r for r in replies if r.get('id')==1),{})
        if initial.get('result',{}).get('serverInfo',{}).get('version')!=pin(name)['version'].removeprefix('v'):
            raise ValueError('Native MCP self-reported version differs from pinned provider')
    return execution,replies


def payload(reply):
    if 'error' in reply:raise ValueError('Native JSON-RPC error: '+str(reply['error']))
    result=reply.get('result',{})
    if result.get('isError'):raise ValueError('Native tool error: '+str(result.get('content')))
    if 'structuredContent' in result:return result['structuredContent']
    texts=[c['text'] for c in result.get('content',[]) if c.get('type')=='text']
    if len(texts)!=1:raise ValueError('One structured native tool reply required')
    return json.loads(texts[0])
