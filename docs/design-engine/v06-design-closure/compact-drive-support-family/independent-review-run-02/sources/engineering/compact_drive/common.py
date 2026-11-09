"""Sealed inputs and immutable packets for this new producer only."""
from pathlib import Path
import gzip,json
from engineering.station_rail.common import identity,digest,encoded
from . import ROOT,PARENT,PARENT_EVALUATION,FLAGS
INPUT='docs/design-engine/powered-bogie-detail/body.json.gz'

def read(path):
    p=Path(path);data=p.read_bytes()
    return json.loads(gzip.decompress(data) if p.suffix=='.gz' else data)

def policy(root=ROOT):return read(Path(root)/'engineering/compact_drive/data/policy.json')
def vendor(root=ROOT):return read(Path(root)/'engineering/compact_drive/data/vendor.json')
def sources(root=ROOT):
    root=Path(root);names=[INPUT,'engineering/station_rail/common.py','engineering/vehicle_installation/model.py','engineering/vehicle_installation/underframe.py','engineering/powered_bogie/geometry.py']
    names += [p.relative_to(root).as_posix() for p in (root/'engineering/compact_drive').rglob('*') if p.suffix in ('.py','.json')]
    return {n:digest(root/n) for n in sorted(names)}

def parent(root=ROOT):
    b=read(Path(root)/INPUT)
    if b['candidate_id']!=PARENT or b['evaluation_id']!=PARENT_EVALUATION:raise ValueError('Exact sealed9f6 parent required')
    if identity(b['physical_definition'])!=PARENT or identity({k:v for k,v in b.items() if k!='evaluation_id'})!=PARENT_EVALUATION:raise ValueError('Parent seal differs')
    return b

def seal(value):
    value.pop('evaluation_id',None);value['evaluation_id']=identity(value);return value

def validate(value):
    if value['candidate_id']!=identity(value['physical_definition']):raise ValueError('Physical candidate seal differs')
    if value['evaluation_id']!=identity({k:v for k,v in value.items() if k!='evaluation_id'}):raise ValueError('Evaluation seal differs')
    if any(value.get(k) is not False for k in FLAGS):raise ValueError('Research packet cannot grant release')
    return value

def write(path,value):
    p=Path(path)
    if p.exists():raise ValueError('Immutable output exists: '+str(p))
    data=encoded(value);p.write_bytes(gzip.compress(data,mtime=0) if p.suffix=='.gz' else data)
