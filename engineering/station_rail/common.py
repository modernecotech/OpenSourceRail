"""Small shared SI definition/identity helpers for the v0.6 physical candidate."""
from hashlib import sha256
from pathlib import Path
import json
import tomllib
from . import ROOT,BRIEF,FLAGS

def encoded(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def identity(value):return sha256(encoded(value)).hexdigest()
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def brief(root=ROOT):
    value=tomllib.loads((Path(root)/BRIEF).read_text())
    if value['schema']!='osr-station-rail-brief/1' or value['version']!='0.6.0':raise ValueError('Explicit v0.6 brief required')
    if value['vehicle']['cars']!=6 or value['vehicle']['normal_people_per_car']!=46:raise ValueError('Six-car comfort basis required')
    if any(value['acceptance'].get(k) is not v for k,v in FLAGS.items()):raise ValueError('Development brief cannot grant release')
    return value

def source_map(root,names):
    root=Path(root)
    return {name:digest(root/name) for name in sorted(set((BRIEF,'engineering/station_rail/__init__.py','engineering/station_rail/common.py',*names)))}
