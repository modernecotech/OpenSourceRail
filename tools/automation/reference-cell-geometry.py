#!/usr/bin/env python3
"""Publish/reopen actual reference-cell geometry; never issue hardware release."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import argparse,gzip,io,json,tarfile,tempfile,sys,re
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from engineering.station_rail.common import identity,digest,encoded
from engineering.reference_cell import geometry,vehicles

CODE='tools/automation/reference-cell-geometry.py'
FLAGS=dict(geometry.FLAGS,complete_installed_geometry=False)
ARCHIVE='native-geometry.tar.gz';MANIFEST='native-geometry-manifest.json'
MAX_BYTES=512*1024**2


def parse(raw):
    def pairs(rows):
        d={}
        for k,v in rows:
            if k in d:raise ValueError('Duplicate geometry metadata key')
            d[k]=v
        return d
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda value:(_ for _ in ()).throw(ValueError('Finite metadata required')))


def ordinary(path):
    path=Path(path)
    if path.is_symlink() or any(p.is_symlink() for p in path.parents):raise ValueError('Ordinary geometry paths required')
    return path


def scratch():
    path=Path.home()/'.local/state/opensourcerail/geometry-publication';path.mkdir(parents=True,exist_ok=True);return ordinary(path)

def check_flags(value):
    if isinstance(value,dict):
        if any(k in FLAGS and v is not False for k,v in value.items()):raise ValueError('Geometry/history cannot promote release or physical completeness')
        for v in value.values():check_flags(v)
    elif isinstance(value,list):
        for v in value:check_flags(v)

def read(path):
    path=ordinary(path)
    if path.stat().st_size>MAX_BYTES:raise ValueError('Bounded geometry metadata required')
    return parse(path.read_bytes())


def _vehicle(folder,name):
    path=ordinary(Path(folder)/'vehicles'/(name+'.json.gz'))
    with gzip.open(path,'rb') as stream:raw=stream.read(128*1024**2+1)
    if len(raw)>128*1024**2:raise ValueError('Bounded full vehicle record required')
    saved=parse(raw);current=vehicles.evaluate(name,root=ROOT)
    if encoded(saved)!=encoded(current):raise ValueError('Retained equipped vehicle semantic/source replay differs: '+name)
    return current


def _sources(current,include_native):
    result={CODE:digest(ROOT/CODE)}
    for v in current.values():result.update(geometry._source(v))
    if include_native:
        from engineering.reference_cell import native_cad
        result.update(native_cad._source(current['V1'],ROOT))
    for name,expected in result.items():
        if Path(name).is_absolute() or '..' in Path(name).parts or digest(ROOT/name)!=expected:raise ValueError('Geometry publication source epoch differs')
    return dict(sorted(result.items()))


def _native_record(folder,vehicle):
    """Saved-file/producer-result integrity only; no actual file reopening here."""
    from engineering.reference_cell import native_cad as n
    folder=ordinary(folder);r=read(folder/'native-receipt.json')
    files={p.name:digest(p) for p in folder.iterdir() if p.is_file() and p.name!='native-receipt.json'}
    if any(not p.is_file() or p.is_symlink() for p in folder.iterdir()) or set(files)!=n.FILES:
        raise ValueError('Exact native issued-file inventory required')
    if (r.get('schema')!='osr-reference-cell-compound-safe-native/1' or r.get('receipt_id')!=identity({k:v for k,v in r.items() if k!='receipt_id'})
        or r.get('candidate_id')!=vehicle['candidate_id'] or r.get('registry_id')!=vehicle['registry']['registry_id']
        or r.get('source_sha256')!=n._source(vehicle,ROOT) or r.get('files_sha256')!=files
        or r.get('execution')!='completed' or r.get('native_reopened') is not True
        or any(r.get(k) is not False for k in FLAGS)):
        raise ValueError('Recorded native source/input/file/disposition differs')
    data=read(folder/'native-input.json');items=geometry._native_items(vehicle,r['cars'])
    if (identity(data)!=r['input_id'] or data['items']!=items or data['source_sha256']!=r['source_sha256']
        or (folder/'native-worker.py').read_text()!=n.worker_script()):raise ValueError('Recorded native request/worker differs')
    geometry._check_native(items,read(folder/'native-result.json'),vehicle['candidate_id'],r['cars'],data['memory_bytes'])
    return dict(candidate_id=vehicle['candidate_id'],receipt_id=r['receipt_id'],cars=r['cars'],occurrences=len(items),
        recorded_FreeCAD_version=r['FreeCAD_version'],source_sha256=r['source_sha256'],recorded_producer_reopen=True,
        current_native_reopened=False,native_reuse_eligible=False,verification_scope='Recorded source/file/input/producer-result integrity; no fresh native reopening asserted',**FLAGS)


def _replay(folder,include_native,actual_native=False):
    folder=Path(folder);current={};entries=[]
    for name in vehicles.variants():
        v=_vehicle(folder,name);current[name]=v
        receipt=geometry.verify_ifc(v,folder/'IFC'/name)
        recorded=read(folder/'IFC'/name/(name+'.ifc.receipt.json'))
        entries.append(dict(vehicle=name,candidate_id=v['candidate_id'],vehicle_evaluation_id=v['evaluation_id'],
            receipt_id=receipt['receipt_id'],physical_occurrences=receipt['physical_occurrences'],unique_part_shapes=receipt['unique_part_shapes'],
            nominal_net_stock_volume_m3=receipt['nominal_net_stock_volume_m3'],purchased_bounding_volume_m3=receipt['purchased_bounding_volume_m3'],
            maximum_mesh_relative_volume_error=recorded['reopened']['maximum_mesh_relative_volume_error']))
    history=read(folder/'history'/'campaign.json')
    if history.get('record_id')!=identity({k:v for k,v in history.items() if k!='record_id'}):raise ValueError('Exact original geometry campaign required')
    if [r['vehicle'] for r in history.get('ifc',[])]!=vehicles.variants():raise ValueError('Original five-vehicle IFC campaign coverage differs')
    for row in history['ifc']:
        name=row['vehicle'];r=read(folder/'IFC'/name/(name+'.ifc.receipt.json'))
        worker=read(folder/'history'/(name+'-worker.json'))
        if worker!=row:raise ValueError('Original exact worker record differs from campaign')
        for suffix in ('-stdout.log','-stderr.log'):
            if not (folder/'history'/(name+suffix)).is_file():raise ValueError('Original worker logs missing')
        if row.get('execution')!='completed' or row.get('candidate_id')!=current[name]['candidate_id'] or row.get('receipt')!=r:
            raise ValueError('Original campaign differs from actual retained IFC')
    check_flags(history)
    fail=read(folder/'history'/'native-failure-manifest.json');check_flags(fail)
    if fail.get('failure_package_id')!=identity({k:v for k,v in fail.items() if k!='failure_package_id'}) or fail.get('fresh_independent_reopen_executed') is not False:
        raise ValueError('Original failed CAD history differs')
    for name,expected in fail['native_files_sha256'].items():
        if Path(name).is_absolute() or '..' in Path(name).parts or digest(folder/'history/failed-CAD'/name)!=expected:
            raise ValueError('Failed CAD input/output/log history differs')
    if digest(folder/'history'/fail['source_snapshot'])!=fail['source_snapshot_sha256']:raise ValueError('Failed CAD original source snapshot differs')
    native=None;fresh=None
    if include_native:
        native=_native_record(folder/'CAD/current',current['V1'])
        if actual_native:
            from engineering.reference_cell import native_cad
            fresh=native_cad.verify_native(current['V1'],folder/'CAD/current',root=ROOT)
    return dict(entries=entries,native_record=native,native_fresh_verification=fresh,source_sha256=_sources(current,include_native))


def publish(state,output,cad=None):
    start_code=digest(ROOT/CODE)
    state=ordinary(state);output=ordinary(output);output.mkdir(parents=True,exist_ok=True)
    files={}
    def add(source,name):
        source=ordinary(source)
        if not source.is_file() or name in files or Path(name).is_absolute() or '..' in Path(name).parts:raise ValueError('Unique ordinary geometry artifact required')
        files[name]=source.read_bytes()
    for name in vehicles.variants():
        add(state/'vehicles'/(name+'.json.gz'),'vehicles/'+name+'.json.gz')
        for suffix in ('.ifc','.ifc.receipt.json'):add(state/'IFC'/name/(name+suffix),'IFC/'+name+'/'+name+suffix)
    for p in sorted(state.iterdir()):
        if p.is_file():add(p,'history/'+p.name)
    failed=state/'CAD/V1-car1'
    for p in sorted(failed.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:add(p,'history/failed-CAD/'+p.relative_to(failed).as_posix())
    for attempt in sorted((state/'CAD').iterdir()):
        if not attempt.is_dir() or attempt==failed or cad is not None and attempt.resolve()==Path(cad).resolve():continue
        for p in sorted(attempt.rglob('*')):
            if p.is_file():add(p,'history/additional-failed-CAD/'+attempt.name+'/'+p.relative_to(attempt).as_posix())
    if cad is not None:
        for p in sorted(ordinary(cad).iterdir()):add(p,'CAD/current/'+p.name)
    with tempfile.TemporaryDirectory(prefix='osr-geometry-stage-',dir=scratch()) as tmp:
        folder=Path(tmp)
        for name,data in files.items():p=folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        checked=_replay(folder,cad is not None)
    source=checked['source_sha256']
    for name,expected in source.items():
        if digest(ROOT/name)!=expected:raise ValueError('Geometry sources changed before retention')
        add(ROOT/name,'sources/'+name)
    payload=io.BytesIO()
    if len(files)>1024 or sum(len(b) for b in files.values())>MAX_BYTES:raise ValueError('Bounded geometry inventory required')
    with tarfile.open(fileobj=payload,mode='w') as archive:
        for name,data in sorted(files.items()):
            item=tarfile.TarInfo(name);item.size=len(data);item.mtime=0;item.mode=0o644;archive.addfile(item,io.BytesIO(data))
    if digest(ROOT/CODE)!=start_code:raise ValueError('Publication tool source changed during execution')
    target=ordinary(output/ARCHIVE);target.write_bytes(gzip.compress(payload.getvalue(),mtime=0))
    value=dict(schema='osr-reference-cell-geometry-publication/1',archive=ARCHIVE,archive_sha256=digest(target),
        files_sha256={n:sha256(b).hexdigest() for n,b in sorted(files.items())},source_sha256=source,
        entries=checked['entries'],native_record=checked['native_record'],
        retained_history_files_sha256={n:sha256(b).hexdigest() for n,b in sorted(files.items()) if n.startswith('history/')},
        history_scope='Original failed CAD execution, exact inputs/logs/source retained; no failed result is promoted',
        actual_IFC_reopened=True,current_native_reopened=False,native_reuse_eligible=False,**FLAGS)
    value['publication_id']=identity(value);ordinary(output/MANIFEST).write_bytes(encoded(value));return value


def verify(output,actual_native=False):
    output=ordinary(output);ordinary(output/ARCHIVE);m=read(output/MANIFEST)
    if (m.get('schema')!='osr-reference-cell-geometry-publication/1' or m.get('publication_id')!=identity({k:v for k,v in m.items() if k!='publication_id'})
        or m.get('source_sha256',{}).get(CODE)!=digest(ROOT/CODE)
        or m.get('archive')!=ARCHIVE or digest(output/ARCHIVE)!=m.get('archive_sha256') or any(m.get(k) is not False for k in FLAGS)
        or m.get('actual_IFC_reopened') is not True or m.get('current_native_reopened') is not False or m.get('native_reuse_eligible') is not False):
        raise ValueError('Geometry publication source/payload/identity/disposition differs')
    with tempfile.TemporaryDirectory(prefix='osr-geometry-verify-',dir=scratch()) as tmp:
        folder=Path(tmp)
        with tarfile.open(output/ARCHIVE,'r:gz') as archive:
            members=archive.getmembers();names=[p.name for p in members]
            if (len(names)!=len(set(names)) or len(names)>1024 or sum(p.size for p in members)>MAX_BYTES
                or any(not p.isfile() or Path(p.name).is_absolute() or '..' in Path(p.name).parts for p in members)):
                raise ValueError('Bounded ordinary geometry archive required')
            archive.extractall(folder,filter='data')
        actual={p.relative_to(folder).as_posix():digest(p) for p in folder.rglob('*') if p.is_file()}
        if actual!=m['files_sha256']:raise ValueError('Exact geometry artifact inventory/bytes differ')
        if {n:h for n,h in actual.items() if n.startswith('history/')}!=m['retained_history_files_sha256']:raise ValueError('Retained history inventory differs')
        expected={'vehicles/'+n+'.json.gz' for n in vehicles.variants()}
        expected.update('IFC/'+n+'/'+n+suffix for n in vehicles.variants() for suffix in ('.ifc','.ifc.receipt.json'))
        expected.update('sources/'+n for n in m['source_sha256']);expected.update(m['retained_history_files_sha256'])
        if m['native_record'] is not None:
            from engineering.reference_cell import native_cad
            expected.update('CAD/current/'+n for n in native_cad.FILES|{'native-receipt.json'})
        if set(actual)!=expected:raise ValueError('Unexpected geometry artifact outside the owned inventory')
        checked=_replay(folder,m['native_record'] is not None,actual_native)
        for name,expected in checked['source_sha256'].items():
            if digest(folder/'sources'/name)!=expected:raise ValueError('Retained geometry source bytes differ')
        if any(checked[k]!=m[k] for k in ('entries','native_record','source_sha256')):raise ValueError('Geometry semantic/source replay differs')
    return dict(verified=True,publication_id=m['publication_id'],vehicles=5,IFC_reopened=True,
        native_recorded_integrity=m['native_record'] is not None,native_reopened=bool(checked['native_fresh_verification']),
        native_verification=checked['native_fresh_verification'],native_reuse_eligible=False,**FLAGS)


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    p=sub.add_parser('publish');p.add_argument('--state',type=Path,required=True);p.add_argument('--cad',type=Path)
    p.add_argument('--output',type=Path,default=ROOT/'docs/design-engine/reference-cell')
    v=sub.add_parser('verify');v.add_argument('--output',type=Path,default=ROOT/'docs/design-engine/reference-cell');v.add_argument('--native',action='store_true')
    args=parser.parse_args();value=publish(args.state,args.output,args.cad) if args.action=='publish' else verify(args.output,args.native)
    print(json.dumps(value if args.action=='verify' else dict(publication_id=value['publication_id'],vehicles=5,native_recorded=value['native_record'] is not None),indent=2))
if __name__=='__main__':main()
