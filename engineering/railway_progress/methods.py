"""Publish actual bounded native packages without inventing correlation or replay."""
from pathlib import Path
import io,tarfile,gzip,json,tempfile
from . import ROOT,FLAGS,identity,digest,encoded


def _check(folder,kind,root):
    if kind=='motor':
        from . import propulsion
        return propulsion.verify(folder,root=root,require_current_tool=False)
    if kind=='structure':
        from . import structural_review
        return structural_review.verify(folder,root=root,require_current_tool=False)
    raise ValueError('Owned native method type required')


def publish(packages,output,*,root=ROOT):
    from . import propulsion
    target=Path(output);target.mkdir(parents=True,exist_ok=True);stream=io.BytesIO();rows=[];motors=[]
    if not packages or len(packages)>12 or len({name for name,kind,path in packages})!=len(packages):raise ValueError('Distinct bounded method packages required')
    with tarfile.open(fileobj=stream,mode='w') as archive:
        for name,kind,folder in packages:
            if not name or '/' in name or name in ('.','..'):raise ValueError('Canonical method label required')
            folder=Path(folder);checked=_check(folder,kind,root);files={}
            for p in sorted(folder.rglob('*')):
                if p.is_symlink():raise ValueError('Native payloads must be owned ordinary files')
                if p.is_file():
                    raw=p.read_bytes();relative=p.relative_to(folder).as_posix();info=tarfile.TarInfo(name+'/'+relative);info.size=len(raw);info.mtime=0;info.mode=0o644
                    archive.addfile(info,io.BytesIO(raw));files[relative]=digest(p)
            rows.append(dict(name=name,kind=kind,validation=checked,files_sha256=files))
            if kind=='motor':motors.append(folder)
    comparison=propulsion.compare(motors,root=root) if 2<=len(motors)<=3 else None
    (target/'native-methods.tar.gz').write_bytes(gzip.compress(stream.getvalue(),mtime=0))
    value=dict(schema='osr-continuing-native-methods/1',packages=rows,motor_comparison=comparison,
        files_sha256={'native-methods.tar.gz':digest(target/'native-methods.tar.gz')},
        verification_scope='Recorded tool/source/payload identities and saved-state residuals; no new independent field execution or physical correlation',**FLAGS)
    value['publication_id']=identity(value);(target/'native-methods.json').write_bytes(encoded(value));return value


def verify(output,*,root=ROOT):
    from . import propulsion
    target=Path(output);v=json.loads((target/'native-methods.json').read_bytes())
    if v.get('schema')!='osr-continuing-native-methods/1' or v['publication_id']!=identity({k:x for k,x in v.items() if k!='publication_id'}) or any(v.get(k) is not False for k in FLAGS):raise ValueError('Native method publication identity/disposition differs')
    if v.get('files_sha256')!={'native-methods.tar.gz':digest(target/'native-methods.tar.gz')}:raise ValueError('Native archive hash differs')
    packages=v.get('packages')
    if not isinstance(packages,list) or not 1<=len(packages)<=12 or len({r['name'] for r in packages})!=len(packages) or any(not r['name'] or '/' in r['name'] or r['name'] in ('.','..') or r.get('kind') not in ('motor','structure') for r in packages):raise ValueError('Distinct bounded native package inventory required')
    with tempfile.TemporaryDirectory(prefix='osr-progress-methods-') as temp:
        with tarfile.open(target/'native-methods.tar.gz','r:gz') as a:
            members=a.getmembers();names=[m.name for m in members]
            expected={row['name']+'/'+n for row in v['packages'] for n in row['files_sha256']}
            if len(names)!=len(set(names)) or set(names)!=expected or len(names)>160 or sum(m.size for m in members)>512*1024**2 or any(not m.isfile() or Path(m.name).is_absolute() or '..' in Path(m.name).parts for m in members):raise ValueError('Closed ordinary native archive inventory required')
            a.extractall(temp,filter='data')
        motors=[]
        for row in v['packages']:
            folder=Path(temp)/row['name']
            if any(digest(folder/n)!=h for n,h in row['files_sha256'].items()):raise ValueError('Native recorded payload differs')
            actual=_check(folder,row['kind'],root)
            # Current binary identity can change across hosts. Recorded package
            # validity is compared independently from current-tool reuse status.
            volatile=('current_tool_identity','toolchain_matches_current','native_reuse_eligible')
            if {k:x for k,x in actual.items() if k not in volatile}!={k:x for k,x in row['validation'].items() if k not in volatile}:raise ValueError('Native recorded validation differs')
            if row['kind']=='motor':motors.append(folder)
        comparison=propulsion.compare(motors,root=root) if 2<=len(motors)<=3 else None
        if encoded(comparison)!=encoded(v['motor_comparison']):raise ValueError('Actual motor refinement comparison differs')
    return dict(verified=True,publication_id=v['publication_id'],packages=len(v['packages']),physical_correlation=False,**FLAGS)
