"""Audit retained chair CAD evidence; no CAD application or solver is started."""
from pathlib import Path
import sys,json,gzip,hashlib,importlib.util,math
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent

def read(n):
 b=(P/n).read_bytes();return json.loads(gzip.decompress(b) if str(n).endswith('.gz') else b)
def ident(v):return hashlib.sha256((json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sealed(v,key='evaluation_id'):assert v[key]==ident({k:x for k,x in v.items() if k!=key})
def code(n):
 spec=importlib.util.spec_from_file_location('retained_chair_'+n,P/'code'/str(n+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def verify():
 m=read('manifest.json');sealed(m,'manifest_id')
 actual={p.relative_to(P).as_posix() for p in P.rglob('*') if p.is_file() and p.name!='manifest.json'}
 assert actual==set(m['files'])
 for n,f in m['files'].items():
  p=P/n;assert not p.is_symlink() and p.stat().st_size==f['bytes'] and sha(p)==f['sha256'],n
 assert m['source_physical_definition_id']=='05ac85c9287da76fbc2e5e2f0c0c4bcd934380bc4e8cf37907e090026a3ecaa3'
 assert m['component_geometry_id']=='6be0297c507f473ed3c9b8f812e0ec205d62ac2a24f27d91954e2480a89167a2'
 assert all(m[k] is False for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release','selected_reference_changed','movement_authority','installed_mass_complete'))
 g=code('geometry');p=code('probes');case=read('case.json');expected=read('expected.json');coupon=read('source/coupon.json');recipe=read('source/recipe.json');export=read('export.json');sealed(export)
 assert g.identity(g.source_physical_projection(coupon))==m['source_physical_definition_id']
 assert sha(P/'source/coupon.json')==export['source_binding']['coupon_sha256'] and sha(P/'source/recipe.json')==export['source_binding']['recipe_sha256']
 assert sha(P/'code/geometry.py')==export['implementation_sha256'] and export['case']==case and export['expected']==expected
 fresh={};solids=[]
 for e in coupon['entities']:
  s,o=g.solid_oracle(e);rho=recipe['materials'][s['material']]['density_kg_m3'];o['nominal_material_mass_kg']=None if rho is None else o['volume_m3']*rho;solids.append(s);fresh[s['id']]=o
 assert fresh==expected and sorted(solids,key=lambda e:e['id'])==case['entities'] and g.script_for(case)==read('commands.json')
 assert len(solids)==275 and case['component_geometry_id']==m['component_geometry_id']
 n=read('native-run.json');sealed(n);assert n['evaluation_id']=='ef49f1b2c28f761c895373a73a9a6536f4cd581d53ac2e676246733b70491b62'
 ref=read('FreeCAD-run.json');sealed(ref);assert ref['evaluation_id']=='aead4bdfbb650f8fc95cf4058f5d1841a9b5cbe46c0c219338ce453c39ee0484' and ref['actual_FreeCAD_reference_launches']==1 and ref['source_and_input_integrity_unchanged']
 review=read('geometry-review.json');sealed(review)
 assert review['evaluation_id']=='4c378d3d1d2d87f773230de5893182cf42e4a39e73eebde5e7ff96f9445619a8'
 pins=review['files_sha256']
 for suffix,public in (('/chair-r4-freecad-reference-01/result.json','FreeCAD-run.json'),('/reference/measurement.json','FreeCAD.json.gz'),('/reference/worker.py','code/executed-worker.py'),('/reference/input.step','chair.step'),('/plan/probe-plan.json','probe-plan.json.gz'),('/definition/case.json','case.json'),('/definition/expected.json','expected.json')):
  matches=[h for n,h in pins.items() if n.endswith(suffix)];assert len(matches)==1
  raw=(P/public).read_bytes();raw=gzip.decompress(raw) if public.endswith('.gz') else raw
  assert hashlib.sha256(raw).hexdigest()==matches[0],public
 for stage in n['stages']:
  folder={'native-build':'generate','reopen-SC':'reopen-sc','reopen-STEP':'reopen-step'}[stage['stage']]
  raw=gzip.decompress((P/('native/'+folder+'.json.gz')).read_bytes())
  assert hashlib.sha256(raw).hexdigest()==stage['measurement_sha256']
  assert read('native/'+folder+'-execution.json')=={k:v for k,v in stage.items() if k not in ('measurement_bodies','measurement_sha256')} and stage['returncode']==0 and stage['measurement_bodies']==275
 measurement=read('FreeCAD.json.gz');plan=read('probe-plan.json.gz');sealed(plan,'plan_id')
 assert plan['case']==case and plan['oracle']==expected and plan['plan_id']==ref['probe_plan_id']
 assert len(measurement['bodies'])==275 and all(b['valid'] and b['closed'] and b['solid_count']==1 and b['all_solids_closed_valid'] and b['volume_m3']>0 for b in measurement['bodies'])
 actual_points=measurement['point_probes']['results'];recorded={(x['native_name'],tuple(x['point_m'])):x['actual_inside'] for x in actual_points}
 regenerated=p.evaluate_probes(plan,measurement['bodies'],lambda n,point:recorded[(n,tuple(point))])
 assert regenerated==measurement['point_probes'] and regenerated['geometry_verification']=='passed'
 assert regenerated['executed_probe_count']==regenerated['planned_probe_count']==2427 and regenerated['mismatches']==regenerated['mapping_issues']==[]
 assert regenerated['strict_native_name_identity']=='failed' and regenerated['strict_name_failure']
 worker=p.instrument_freecad_worker((P/'code/base-worker.txt').read_text(),plan)
 assert worker['worker_sha256']==sha(P/'code/executed-worker.py')==ref['instrumented_worker_sha256']
 assert worker['worker'].encode()==(P/'code/executed-worker.py').read_bytes()
 for row in m['images']:
  result=read(row['result']);recipe_record=read(row['recipe']);sealed(result);sealed(recipe_record,'recipe_id')
  assert result['execution']=='completed' and result['recipe_id']==recipe_record['recipe_id'] and result['image_sha256']==sha(P/row['native_png'])
  assert recipe_record['candidate_id']==m['source_physical_definition_id'] and row['compositor']['image_fit']=='contain; no crop or stretch'
 return dict(positive_closed_valid_solids=275,material_and_void_point_checks=2427,strict_import_identity='failed; retained separately',native_geometry_and_image_bytes_verified=True,physical_accepted=False,installed_mass_complete=False)
if __name__=='__main__':print(json.dumps(verify(),sort_keys=True))
