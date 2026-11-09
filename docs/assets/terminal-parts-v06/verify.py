# Read-only packet/oracle/geometry audit. No native application or solver.
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'code'))
from geometry import read,identity,check,extract_entities
from commands import serialize
from compare import compare

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def verify():
 m=read(ROOT/'manifest.json');check(m,'manifest_id')
 actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and p.name!='manifest.json'}
 assert actual==set(m['files'])
 for n,v in m['files'].items():
  p=ROOT/n;assert not p.is_symlink() and p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],n
 assert all(m[k] is False for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release','selected_reference_changed','movement_authority'))
 registry=read(ROOT/'join-registry.json');check(registry);total=0
 for row in m['cases']:
  s=row['stem'];spec=read(ROOT/(s+'.expected.json'));check(spec)
  src=read(ROOT/(s+'.source-geometry.json'));check(src)
  assert sha(ROOT/(s+'.source-geometry.json'))==spec['source_geometry_sha256']
  assert src['physical_definition_id']==spec['physical_definition_id']==row['physical_definition_id']
  primitives,parts=extract_entities(src,spec['eligible_known_entity_ids'])
  assert primitives==spec['primitives'] and parts==spec['parent_parts']
  script,numerical=serialize(spec,registry)
  assert script==read(ROOT/(s+'.commands.json')) and numerical==read(ROOT/(s+'.serialization.json'))
  assert numerical['finite_vertices_moved']==0 and numerical['engineering_tolerance_relaxed'] is False
  for stage in ('generate','reopen-sc','reopen-step'):
   measurement=read(ROOT/(s+'.'+stage+'-SI.json'))
   assert compare(spec,measurement,'solidcraft')['geometric_bijection']=='passed'
   assert read(ROOT/(s+'.'+stage+'-execution.json'))['execution']=='executed'
  measurement=read(ROOT/(s+'.FreeCAD.json'))
  assert compare(spec,measurement,'freecad')['geometric_bijection']=='passed'
  assert all(b['valid'] and b['closed'] and b['all_solids_closed_valid'] and b['solid_count']==1 for b in measurement['bodies'])
  assert read(ROOT/(s+'.FreeCAD-request.json'))['STEP_sha256']==sha(ROOT/(s+'.step'))
  assert read(ROOT/(s+'.strict-label-failure.json'))['passed'] is False
  assert len(measurement['bodies'])==row['native_primitive_solids'];total+=len(measurement['bodies'])
 failed=read(ROOT/'prior-native-failure.json');assert failed['execution']=='held' and failed['native_calls']==1
 assert read(ROOT/'native-run.json')['native_calls']==8
 return dict(cases=len(m['cases']),independent_closed_solids=total,geometric_correspondence=True,strict_import_identity='failed; retained',source_oracles_and_serialization_reproduced=True,physical_accepted=False)
if __name__=='__main__':print(json.dumps(verify(),sort_keys=True))
