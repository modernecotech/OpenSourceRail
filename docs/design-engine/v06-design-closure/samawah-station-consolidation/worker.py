"""Private deterministic comparison; imports exact90d07 source, never pyc."""
from pathlib import Path
from copy import deepcopy
import gzip,hashlib,importlib.machinery,json,math,subprocess,sys,traceback

RUN=Path(__file__).resolve().parent
REQUEST=json.loads((RUN/'request.json').read_bytes());ROOT=Path(REQUEST['repository']).resolve()
COMMIT=REQUEST['source_commit'];READS={};IMPORTS={};BEFORE={}
encode=lambda v:(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
sha=lambda raw:hashlib.sha256(raw).hexdigest()
ident=lambda v:sha(encode(v))
def save(name,value):
 p=RUN/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(encode(value))
def require(condition,message):
 if not condition:raise ValueError(message)
reader=subprocess.Popen(['/usr/bin/git','-c','core.packedGitWindowSize=16m','-c','core.packedGitLimit=32m','-C',str(ROOT),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
def blob(name):
 if name in READS:return READS[name]
 reader.stdin.write((COMMIT+':'+name+'\n').encode());reader.stdin.flush()
 h=reader.stdout.readline().decode().split();require(len(h)==3 and h[1]=='blob','Missing committed blob: '+name)
 raw=reader.stdout.read(int(h[2]));require(reader.stdout.read(1)==b'\n','Truncated blob')
 record=dict(path=name,commit=COMMIT,git_blob_id=h[0],sha256=sha(raw),bytes=len(raw))
 READS[name]=(raw,record);return raw,record
def checked(name):
 expected,record=blob(name);p=ROOT/name
 require(p.resolve().is_relative_to(ROOT) and not p.is_symlink(),'Ordinary source/data path required: '+name)
 actual=p.read_bytes();require(actual==expected,'Current bytes differ from requested commit: '+name)
 BEFORE.setdefault(name,sha(actual));return actual
original_source_code=importlib.machinery.SourceFileLoader.get_code
original_sourceless_code=importlib.machinery.SourcelessFileLoader.get_code
def project(fullname):return fullname=='engineering' or fullname.startswith('engineering.') or fullname=='services' or fullname.startswith('services.')
def source_code(loader,fullname):
 if not project(fullname):return original_source_code(loader,fullname)
 p=Path(loader.path).resolve();require(p.is_relative_to(ROOT),'Foreign project source: '+fullname)
 name=p.relative_to(ROOT).as_posix();raw=checked(name)
 IMPORTS[fullname]=dict(path=name,sha256=sha(raw),method='compile-authenticated-source-bytes; no project pyc lookup')
 return compile(raw,str(p),'exec',dont_inherit=True)
def no_project_pyc(loader,fullname):
 if project(fullname):raise ImportError('Sourceless project bytecode is not permitted: '+fullname)
 return original_sourceless_code(loader,fullname)
importlib.machinery.SourceFileLoader.get_code=source_code
importlib.machinery.SourcelessFileLoader.get_code=no_project_pyc
require(sys.dont_write_bytecode,'Bytecode writes must be disabled at process startup')
sys.path.insert(0,str(ROOT))

def diff(a,b,path=''):
 rows=[]
 if type(a) is type(b) and isinstance(a,dict):
  for k in sorted(set(a)|set(b)):
   p=path+'/'+k.replace('~','~0').replace('/','~1')
   if k not in a:rows.append(dict(path=p,old_present=False,new_present=True,new=b[k]))
   elif k not in b:rows.append(dict(path=p,old_present=True,old=a[k],new_present=False))
   else:rows.extend(diff(a[k],b[k],p))
 elif type(a) is type(b) and isinstance(a,list):
  for i in range(max(len(a),len(b))):
   p=path+'/'+str(i)
   if i>=len(a):rows.append(dict(path=p,old_present=False,new_present=True,new=b[i]))
   elif i>=len(b):rows.append(dict(path=p,old_present=True,old=a[i],new_present=False))
   else:rows.extend(diff(a[i],b[i],p))
 elif a!=b:rows.append(dict(path=path,old_present=True,old=a,new_present=True,new=b))
 return rows

try:
 from engineering.railway_project import city_recalculation as adapter
 from engineering.outline import city_inputs,planning_geometry
 from engineering.development_baseline import planning
 bodyraw=checked(adapter.BODY_FILE);body=json.loads(gzip.decompress(bodyraw))
 policyraw=checked(adapter.POLICY);policy=json.loads(policyraw)
 require(policy['acceleration_m_s2']==0.4,'Unchanged0.4 policy required')
 context=city_inputs.prepare(root=ROOT);city=city_inputs.load('samawah',root=ROOT,context=context)
 for mapping in (body['source_sha256'],city['source_sha256']):
  for name,want in mapping.items():require(sha(checked(name))==want,'Producer/input source identity mismatch: '+name)
 require(body['candidate_id']==REQUEST['body_candidate_id'] and body['evaluation_id']==REQUEST['body_evaluation_id'],'Wrong body candidate/evaluation')
 line=next(r for r in city['lines'] if r['line_id']=='line-1');chain=planning_geometry.route(line['coordinates'],line['shape'])
 ids=REQUEST['source_marker_ids'];markers=[next(s for s in line['stops'] if s['id']==sid) for sid in ids]
 geometry=[]
 for stop in markers:
  point=planning_geometry.point(line['coordinates'],chain,stop['chainage_m'])
  exact=[stop['lon'],stop['lat']]==point
  geometry.append(dict(source_stop=deepcopy(stop),point_at_declared_chainage=point,exact_coordinate_equality=exact,
   exact_polyline_vertex_indices=[i for i,p in enumerate(line['coordinates']) if p==[stop['lon'],stop['lat']]]))
  require(exact,'Source marker is not exactly on the declared polyline: '+stop['id'])
 require(markers[1]['chainage_m']-markers[0]['chainage_m']==79.97678015644487,'Unexpected marker separation')
 anchor_rows=[deepcopy(row) for row in city['interchanges'] if any(sid in row.get('platforms',[]) for sid in ids)]
 save('geometry-preflight.json',dict(source_commit=COMMIT,city_input_id=city['input_id'],marker_geometry=geometry,
  source_separation_m=markers[1]['chainage_m']-markers[0]['chainage_m'],source_interchange_references=anchor_rows,passed=True,surveyed_accuracy_claimed=False))
 baseline=adapter.evaluate(city,body,policy,trusted_city_input_id=city['input_id'],root=ROOT)
 require(baseline['evaluation_id']==REQUEST['reference_outline_evaluation_id'],'Original0.4 control failed exact reproduction')
 save('baseline.json',baseline);save('inputs/body.json.gz.metadata.json',dict(sha256=sha(bodyraw),bytes=len(bodyraw),candidate_id=body['candidate_id'],evaluation_id=body['evaluation_id']))
 (RUN/'inputs/body.json.gz').write_bytes(bodyraw);save('inputs/city.json',city);(RUN/'inputs/policy.json').write_bytes(policyraw)
 planpath=context['by_slug']['samawah']['plan_path'];planraw=checked(planpath);plan=json.loads(gzip.decompress(planraw));save('inputs/planning.json',plan)
 require(plan['revision_sha256']==city['planning_revision_sha256'],'Planning ancestry differs')
 midpoint=(markers[0]['chainage_m']+markers[1]['chainage_m'])/2
 point=planning_geometry.point(line['coordinates'],chain,midpoint)
 physical_edit=dict(schema='osr-samawah-two-marker-midpoint/1',source_city_input_id=city['input_id'],line_id='line-1',
  source_stop_ids=ids,source_stops=deepcopy(markers),midpoint_chainage_m=midpoint,midpoint_longitude_latitude=point,
  method='Mean source chainage interpolated on the unchanged mapped polyline; not mean coordinates or a surveyed accessible route')
 physical_edit['derivation_id']=ident(physical_edit)
 new_id='complex-'+physical_edit['derivation_id'][:24]
 edits=[dict(kind='add-stop',line='line-1',stop=new_id,chainage_m=midpoint,dwell_s=policy['dwell_s']),
  *[dict(kind='retire-stop',line='line-1',stop=sid) for sid in ids]]
 revised_plan=planning._apply_edits(plan,edits,'deterministic-samawah-station-consolidation-20261109')
 pline=next(r for r in revised_plan['lines'] if r['id']=='line-1')
 new_stop=next(s for s in pline['stops'] if s['id']==new_id)
 require([new_stop['lon'],new_stop['lat']]==point,'Planning midpoint differs from exact source-polyline midpoint')
 new_stop.update(source_stop_ids=ids,source_station_consolidation_derivation_id=physical_edit['derivation_id'],
  physical_access_route_verified=False,passenger_catchment_reassessment_required=True,site_approval=False)
 revised_plan['station_consolidation_derivation_id']=physical_edit['derivation_id']
 revised_plan['revision_sha256']=planning.digest_json({k:v for k,v in revised_plan.items() if k!='revision_sha256'})
 planning._validate_plan(revised_plan,'samawah');save('revised-planning.json',revised_plan)
 derived=deepcopy(city);dline=next(r for r in derived['lines'] if r['line_id']=='line-1')
 dline['stops']=deepcopy(pline['stops']);dline['coordinate_chainages_m']=planning_geometry.route(dline['coordinates'],dline['shape'])
 dline['route_m']=dline['coordinate_chainages_m'][-1]
 dline['legs']=[dict(from_stop=a['id'],to_stop=b['id'],distance_m=b['chainage_m']-a['chainage_m'],closing_leg=False)
  for a,b in zip(dline['stops'],dline['stops'][1:])]
 dline['operational_route_m']=math.fsum(r['distance_m'] for r in dline['legs'])
 dline['unserved_radial_tail_m']=dline['route_m']-dline['operational_route_m']
 derived.update(planning_revision_sha256=revised_plan['revision_sha256'],parent_city_input_id=city['input_id'],
  parent_planning_revision_sha256=city['planning_revision_sha256'],
  station_consolidation_hypothesis=physical_edit,private_calculated_revision_not_published=True)
 derived['input_id']=ident({k:v for k,v in derived.items() if k!='input_id'})
 require(all(a==b for a,b in zip(city['lines'],derived['lines']) if a['line_id']!='line-1'),'Unexpected other-line change')
 require(dline['coordinates']==line['coordinates'] and dline['route_m']==line['route_m'],'Polyline or route changed')
 interchange_rebindings=[]
 for row in derived['interchanges']:
  prior=deepcopy(row);platforms=[]
  for sid in row.get('platforms',[]):
   target=new_id if sid in ids else sid
   if target not in platforms:platforms.append(target)
  if platforms!=row.get('platforms',[]):
   row['platforms']=platforms
   interchange_rebindings.append(dict(interchange_id=row['id'],before=prior,after=deepcopy(row),
    treatment='Only the two retired IDs are rebound and deduplicated. Site coordinates and all other platform IDs remain unchanged.',
    actual_transfer_paths_and_catchment_verified=False,accessible_transfer_distance_m=None))
 require(len(interchange_rebindings)==len(anchor_rows),'Unexpected interchange reference propagation')
 require(derived['od']==city['od'] and derived['civil_segments']==city['civil_segments'],
  'Unexpected OD or civil classification change')
 derived['input_id']=ident({k:v for k,v in derived.items() if k!='input_id'})
 save('derived-city.json',derived)
 result=adapter.evaluate(derived,body,policy,trusted_city_input_id=derived['input_id'],root=ROOT)
 adapter.verify(result);require(result['candidate_id']!=baseline['candidate_id'] and result['evaluation_id']!=baseline['evaluation_id'],'Distinct physical/evaluation identity required')
 require(result['policy']==baseline['policy'] and result['policy_id']==baseline['policy_id'],'Policy changed')
 require(result['body_candidate_id']==baseline['body_candidate_id'] and result['body_evaluation_id']==baseline['body_evaluation_id'],'Body changed')
 require(all(row['cost_usd']==dict.fromkeys(adapter.CASES) and not row['cost_complete'] for row in result['scope_accounts']),'Cost unknowns promoted')
 save('result.json',result)
 save('derivation.json',dict(**physical_edit,new_station_id=new_id,new_station_marker=deepcopy(new_stop),planning_edits=edits,
  interchange_reference_rebindings=interchange_rebindings,parent_planning_revision_id=plan['revision_sha256'],new_planning_revision_id=revised_plan['revision_sha256'],
  caller_authentication_basis='Private deterministic derivation from authenticated90d07 source inputs; not an uploaded or published city revision',
  geometric_along_polyline_offsets_from_original_markers_m=[midpoint-s['chainage_m'] for s in markers],
  actual_accessible_walk_lengths_m=None,physical_accepted=False,engineering_accepted=False,operating_release=False))
 save('changed-fields.json',dict(city_input=diff(city,derived),planning_revision=diff(plan,revised_plan),outline_evaluation=diff(baseline,result)))
 def quantities(r):return dict(route_m=r['quantities']['route_m'],station_markers=r['quantities']['station_markers'],
  boarding_faces=next(x['quantities']['boarding_faces'] for x in r['scope_accounts'] if x['scope']=='stations-power'),
  line1_runtime_s=next(x['assumed_one_way_runtime_s'] for x in r['lines'] if x['line_id']=='line-1'),
  line1_cycle_s=next(x['assumed_cycle_s'] for x in r['lines'] if x['line_id']=='line-1'),
  fleet_request_cases=r['fleet_request_cases'],known_counted_BOM_process_subtotal_usd=r['known_counted_BOM_process_subtotal_usd'],
  definition_failures=r['definition_failures'],scope_totals_usd=r['scope_totals_usd'])
 comparison=dict(schema='osr-private-samawah-station-consolidation-comparison/1',source_commit=COMMIT,
  body_candidate_id=body['candidate_id'],body_evaluation_id=body['evaluation_id'],policy_id=baseline['policy_id'],
  baseline=dict(candidate_id=baseline['candidate_id'],evaluation_id=baseline['evaluation_id'],city_input_id=city['input_id'],**quantities(baseline)),
  midpoint_scenario=dict(candidate_id=result['candidate_id'],evaluation_id=result['evaluation_id'],city_input_id=derived['input_id'],**quantities(result)),
  derivation_id=physical_edit['derivation_id'],new_station_id=new_id,control_reproduced=True,
  source_polyline_unchanged=True,all_other_lines_unchanged=True,body_and_policy_unchanged=True,interchange_reference_rebindings=interchange_rebindings,
  service_complete=False,cost_complete=False,simulation_complete=False,physical_accepted=False,engineering_accepted=False,
  manufacturing_release=False,operating_release=False,movement_authority=False,gate_closed=False,
  limitations=['Only the two identified source markers are consolidated; the physical city candidate is distinct and unselected.',
   'A disappearing120m marker-envelope conflict does not establish a buildable or safe station.',
   'Accessible paths, wheelchair/evacuation interfaces and actual walking links remain unverified.',
   'Passenger catchment, demand, OD and transfer impacts require reassessment; no unchanged-catchment claim.',
   'Station footprint, land, ground, utilities and site conditions remain unknown.',
   'Available drive/braking, grade, thermal, charging and exact-body civil load evidence remain absent.',
   'Runtime/fleet are conditional kinematic requests, not a protected schedule or service evidence.',
   'All14 complete cost scopes and whole-life NPV remain null. Known BOM/process subtotal is not delivered or installed price.',
   'Body mass uncertainty and the18-hour versus two8-hour operating-shift gap are retained.',
   'No safety, passenger protection or accessibility obligation is traded for cost.'])
 comparison['evaluation_id']=ident(comparison);save('comparison.json',comparison)
 # Verify every consumed blob/data source again; record the actual execution method.
 after={name:sha((ROOT/name).read_bytes()) for name in BEFORE}
 require(before_equal:=BEFORE==after,'Consumed source/input bytes changed during execution')
 save('source-integrity.json',dict(source_commit=COMMIT,before_sha256=BEFORE,after_sha256=after,
  unchanged=before_equal,python_runtime=dict(version=sys.version,executable=str(Path(sys.executable).resolve()),executable_sha256=sha(Path(sys.executable).resolve().read_bytes()),cache_tag=sys.implementation.cache_tag,math_extension_path=getattr(math,'__file__',None),math_extension_sha256=sha(Path(math.__file__).read_bytes()) if getattr(math,'__file__',None) else None),git_blobs=[record for raw,record in READS.values()],project_imports=IMPORTS,
  project_pyc_executed=False,bytecode_writes_disabled=sys.dont_write_bytecode,
  isolation='Hash-checked source compilation and before/after integrity observations; source filesystem remains writable; no OS read-only sandbox claimed'))
 print(json.dumps(dict(baseline_evaluation_id=baseline['evaluation_id'],candidate_id=result['candidate_id'],
  evaluation_id=result['evaluation_id'],comparison_evaluation_id=comparison['evaluation_id'],derivation_id=physical_edit['derivation_id'],
  new_station_id=new_id,midpoint_chainage_m=midpoint,midpoint_longitude_latitude=point,
  before=quantities(baseline),after=quantities(result),consumed_source_files=len(BEFORE)),sort_keys=True))
except Exception as exc:
 save('failure.json',dict(stage='private-station-consolidation-worker',error=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),
  source_files_checked=BEFORE,physical_accepted=False,gate_closed=False))
 traceback.print_exc();sys.exit(1)
finally:
 reader.stdin.close();reader.wait()
