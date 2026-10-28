"""Closed publication of corrected and rejected structural experiments."""
from pathlib import Path
import io,tarfile,gzip,json,tempfile
from . import ROOT,FLAGS,identity,digest,encoded


def check(folder,kind,root=ROOT):
    if kind=='rejected-whole':
        from .whole_structure import verify
    elif kind=='corrected-whole':
        from .whole_refinement import verify
    elif kind=='distributed-contact-whole':
        from .whole_contact import verify
    else:raise ValueError('Explicit structural producer required')
    checked=verify(folder,root=root)
    value=json.loads((Path(folder)/'result.json').read_bytes())
    return dict(verification=checked,execution=value['execution'],numerical_cases_valid=value.get('numerical_cases_valid'),
        kinematic_cases_in_domain=value.get('kinematic_cases_in_domain'),mesh_count=len(value.get('results',[])),
        model_defect='Layered panel published width was shadowed by a segment coordinate; invalid model geometry, retained for audit' if kind=='rejected-whole' else 'Contact integrated at only four points across long piecewise elements; unsuitable stiffness prediction' if kind=='corrected-whole' else None,
        result_evaluation_id=value.get('evaluation_id'),qualification=False)


def publish(packages,output,root=ROOT):
    if not 1<=len(packages)<=8 or len({x[0] for x in packages})!=len(packages):raise ValueError('Distinct bounded packages required')
    target=Path(output);target.mkdir(parents=True,exist_ok=True);stream=io.BytesIO();rows=[]
    with tarfile.open(fileobj=stream,mode='w') as archive:
        for name,kind,folder in packages:
            if not name or '/' in name or name in ('.','..'):raise ValueError('Canonical label required')
            folder=Path(folder);verified=check(folder,kind,root);files={}
            for p in sorted(folder.rglob('*')):
                if p.is_symlink():raise ValueError('Ordinary immutable payload required')
                if p.is_file():
                    raw=p.read_bytes();relative=p.relative_to(folder).as_posix();info=tarfile.TarInfo(name+'/'+relative)
                    info.size=len(raw);info.mtime=0;info.mode=0o644;archive.addfile(info,io.BytesIO(raw));files[relative]=digest(p)
            rows.append(dict(name=name,kind=kind,validation=verified,files_sha256=files))
    (target/'structural-methods.tar.gz').write_bytes(gzip.compress(stream.getvalue(),mtime=0))
    value=dict(schema='osr-sourced-structural-methods/1',packages=rows,
        files_sha256={'structural-methods.tar.gz':digest(target/'structural-methods.tar.gz')},
        verification_scope='Recorded source, request and result integrity; no new independent numerical execution or physical correlation',**FLAGS)
    value['publication_id']=identity(value);(target/'structural-methods.json').write_bytes(encoded(value));return value


def verify(output,root=ROOT):
    target=Path(output);v=json.loads((target/'structural-methods.json').read_bytes())
    if v['publication_id']!=identity({k:x for k,x in v.items() if k!='publication_id'}) or any(v.get(k) is not False for k in FLAGS):raise ValueError('Structural publication differs')
    if v['files_sha256']!={'structural-methods.tar.gz':digest(target/'structural-methods.tar.gz')}:raise ValueError('Structural archive differs')
    rows=v['packages']
    if not 1<=len(rows)<=8 or len({r['name'] for r in rows})!=len(rows) or any(not r['name'] or '/' in r['name'] or r['name'] in ('.','..') for r in rows):raise ValueError('Structural inventory differs')
    with tempfile.TemporaryDirectory(prefix='osr-sourced-structure-') as temp:
        with tarfile.open(target/'structural-methods.tar.gz','r:gz') as archive:
            entries=archive.getmembers();names=[m.name for m in entries];expected={r['name']+'/'+n for r in rows for n in r['files_sha256']}
            if len(names)!=len(set(names)) or set(names)!=expected or len(names)>100 or sum(m.size for m in entries)>512*1024**2 or any(not m.isfile() or Path(m.name).is_absolute() or '..' in Path(m.name).parts for m in entries):raise ValueError('Ordinary bounded structural archive required')
            archive.extractall(temp,filter='data')
        for row in rows:
            folder=Path(temp)/row['name']
            if any(digest(folder/n)!=h for n,h in row['files_sha256'].items()) or check(folder,row['kind'],root)!=row['validation']:raise ValueError('Structural method replay differs')
    return dict(verified=True,publication_id=v['publication_id'],packages=len(rows),physical_correlation=False,**FLAGS)
