"""Reopen actual revised occurrence geometry; purchased envelopes stay explicit."""
from pathlib import Path
import io,gzip,tarfile,tempfile,json
from . import ROOT,FLAGS,identity,digest,encoded
from . import coordinator
from engineering.reference_cell import geometry as native


def publish(state,output,root=ROOT):
    target=Path(output);target.mkdir(parents=True,exist_ok=True)
    run=coordinator.read(Path(state)/'latest.json');rows=[];stream=io.BytesIO()
    with tempfile.TemporaryDirectory(prefix='osr-sourced-ifc-') as temp:
        with tarfile.open(fileobj=stream,mode='w') as archive:
            for vid in sorted({r['request']['vehicle_id'] for r in run['cases']}):
                v=coordinator.read(Path(state)/'vehicles'/(vid+'.json.gz'))['vehicle'];path=Path(temp)/(vid+'.ifc')
                receipt=native.export_ifc(v,path);check=native.verify_ifc(v,path)
                files={}
                for p in sorted(Path(temp).glob(vid+'.ifc*')):
                    raw=p.read_bytes();info=tarfile.TarInfo(p.name);info.size=len(raw);info.mtime=0;info.mode=0o644
                    archive.addfile(info,io.BytesIO(raw));files[p.name]=digest(p)
                rows.append(dict(vehicle_id=vid,candidate_id=v['candidate_id'],registry_id=v['registry']['registry_id'],reopened=receipt['reopened'],validation=check,files_sha256=files))
    (target/'revised-vehicles-ifc.tar.gz').write_bytes(gzip.compress(stream.getvalue(),mtime=0))
    value=dict(schema='osr-sourced-vehicle-geometry/1',run_id=run['run_id'],vehicles=rows,source_sha256=coordinator.sources(root),
        files_sha256={'revised-vehicles-ifc.tar.gz':digest(target/'revised-vehicles-ifc.tar.gz')},
        scope='Actual six-car net stock primitives and explicit purchased-component bounding envelopes; not supplier internals, clearance acceptance or production drawings',**FLAGS)
    value['publication_id']=identity(value);(target/'revised-vehicles-ifc.json').write_bytes(encoded(value));return value


def verify(state,output,root=ROOT):
    target=Path(output);v=json.loads((target/'revised-vehicles-ifc.json').read_bytes());run=coordinator.read(Path(state)/'latest.json')
    if v['publication_id']!=identity({k:x for k,x in v.items() if k!='publication_id'}) or v['run_id']!=run['run_id'] or v['source_sha256']!=coordinator.sources(root) or any(v.get(k) is not False for k in FLAGS):raise ValueError('Revised geometry source or run differs')
    if v['files_sha256']!={'revised-vehicles-ifc.tar.gz':digest(target/'revised-vehicles-ifc.tar.gz')}:raise ValueError('Revised IFC archive differs')
    if sorted(r['vehicle_id'] for r in v['vehicles'])!=sorted({r['request']['vehicle_id'] for r in run['cases']}):raise ValueError('Revised IFC candidate coverage differs')
    with tempfile.TemporaryDirectory(prefix='osr-sourced-ifc-reopen-') as temp:
        with tarfile.open(target/'revised-vehicles-ifc.tar.gz','r:gz') as archive:
            entries=archive.getmembers();names=[m.name for m in entries];expected={n for r in v['vehicles'] for n in r['files_sha256']}
            if len(names)!=len(set(names)) or set(names)!=expected or len(names)>10 or sum(m.size for m in entries)>512*1024**2 or any(not m.isfile() or Path(m.name).is_absolute() or '..' in Path(m.name).parts for m in entries):raise ValueError('Closed ordinary IFC archive required')
            archive.extractall(temp,filter='data')
        for row in v['vehicles']:
            vehicle=coordinator.read(Path(state)/'vehicles'/(row['vehicle_id']+'.json.gz'))['vehicle']
            if vehicle['candidate_id']!=row['candidate_id'] or vehicle['registry']['registry_id']!=row['registry_id'] or any(digest(Path(temp)/n)!=h for n,h in row['files_sha256'].items()):raise ValueError('IFC candidate or payload differs')
            actual=native.verify_ifc(vehicle,Path(temp)/(row['vehicle_id']+'.ifc'))
            if actual!=row['validation']:raise ValueError('Reopened IFC verification differs')
    return dict(verified=True,publication_id=v['publication_id'],vehicles=len(v['vehicles']),**FLAGS)


def verify_publication(output,root=ROOT):
    target=Path(output);manifest=coordinator.read(target/'manifest.json')
    if manifest['publication_id']!=identity({k:x for k,x in manifest.items() if k!='publication_id'}) or manifest['source_sha256']!=coordinator.sources(root):raise ValueError('Cell publication identity differs')
    if manifest['files_sha256']!={n:digest(target/n) for n in ('summary.json','sourced-cell.tar.gz')}:raise ValueError('Cell payload differs')
    with tempfile.TemporaryDirectory(prefix='osr-sourced-ifc-input-') as temp:
        with tarfile.open(target/'sourced-cell.tar.gz','r:gz') as archive:
            entries=archive.getmembers();names=[m.name for m in entries]
            if len(names)!=len(set(names)) or len(names)>40 or sum(m.size for m in entries)>1024**3 or any(not m.isfile() or Path(m.name).is_absolute() or '..' in Path(m.name).parts for m in entries):raise ValueError('Ordinary bounded cell payload required')
            archive.extractall(temp,filter='data')
        return verify(temp,output,root)
