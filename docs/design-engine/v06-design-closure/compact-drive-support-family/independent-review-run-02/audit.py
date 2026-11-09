"""Read retained JSON/hash/receipt records only; never import or run trial code."""
from pathlib import Path,PurePosixPath
from collections import Counter
import ast,gc,gzip,hashlib,json,math,re,resource,subprocess,time
resource.setrlimit(resource.RLIMIT_CPU,(60,60));resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
OUT=Path(__file__).resolve().parent
REPO=Path('/home/hayder/.local/state/opensourcerail/worktrees/v06-design-closure-20261108')
BASE=Path('/home/hayder/.local/state/opensourcerail/runs/v06-design-closure-20261108')
RUN=BASE/'compact-drive-support-family-run-02';OLD=BASE/'compact-drive-support-family-run-01'
COMMIT='1c41f0b63874f533cb7dbe29133f7672c2fbf31c';CASES=('low','base','high')
enc=lambda v:(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode();sha=lambda b:hashlib.sha256(b).hexdigest();ident=lambda v:sha(enc(v))
read=lambda p:json.loads(p.read_bytes())
errors=[];checks=Counter();source_records={}
def expect(v,label):
 checks[label]+=1
 if not v:errors.append(label)
def snapshot(root):
 rows=[]
 for p in sorted(root.rglob('*')):
  if p.is_symlink():raise ValueError('Unexpected symlink: '+str(p))
  if p.is_file():
   st=p.stat();rows.append(dict(path=p.relative_to(root).as_posix(),sha256=sha(p.read_bytes()),bytes=st.st_size,mtime_ns=st.st_mtime_ns,mode=st.st_mode,inode=st.st_ino))
 return rows
old_before=snapshot(OLD);run_before=snapshot(RUN)
def git(*args):return subprocess.check_output(['/usr/bin/git','-c','core.packedGitWindowSize=16m','-c','core.packedGitLimit=32m','-C',str(REPO),*args])
def source(name):
 if name not in source_records:
  raw=git('show',COMMIT+':'+name);source_records[name]=dict(path=name,commit=COMMIT,git_blob_id=git('rev-parse',COMMIT+':'+name).decode().strip(),sha256=sha(raw),bytes=len(raw))
  (OUT/'sources').mkdir(exist_ok=True)
  if name.endswith('.py') or name.endswith('.json'):
   p=OUT/'sources'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
  return raw
 return git('show',COMMIT+':'+name)
def sealed(value,key='evaluation_id'):
 return value.get(key)==ident({k:v for k,v in value.items() if k!=key})
def validate_manifest(path):
 m=read(path);expect(sealed(m),'canonical seal '+str(path.relative_to(RUN)))
 for n,want in m['files_sha256'].items():
  rel=PurePosixPath(n);expect(not rel.is_absolute() and '..' not in rel.parts,'safe manifest path '+n)
  f=path.parent/n;expect(f.is_file() and sha(f.read_bytes())==want,'payload hash '+str(f.relative_to(RUN)))
 return m
def checksum_file(path):
 rows=[]
 for line in path.read_text().splitlines():
  h,n=line.split('  ',1);rel=PurePosixPath(n)
  expect(bool(re.fullmatch('[0-9a-f]{64}',h)) and not rel.is_absolute() and '..' not in rel.parts,'checksum path '+str(path)+':'+n)
  expect(sha((path.parent/n).read_bytes())==h,'checksum '+str(path)+':'+n);rows.append(n)
 return rows
top=validate_manifest(RUN/'manifest.json');cmp=read(RUN/'comparison.json');checksum_file(RUN/'MANIFEST.sha256')
expect(top['source_commit']==cmp['source_commit']==COMMIT,'top source commit')
expect(top['variants_distinct'] is True,'variants distinct declaration')
for f in ('physical_accepted','engineering_accepted','selected_or_promoted'):expect(top[f] is False,'top no promotion '+f)
policy=json.loads(source('engineering/compact_drive/data/policy.json'))
design=ast.parse(source('engineering/compact_drive/design.py'))
constants={}
for n in design.body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('SUPPORT_FAMILY','SUPPORT_VARIANTS','SUPPORT_LANES') for t in n.targets):
  for t in n.targets:
   if isinstance(t,ast.Name):constants[t.id]=ast.literal_eval(n.value)
# The source roster is common.sources(): five pinned parent/method inputs plus the compact producer's py/json tree.
roster=set(['docs/design-engine/powered-bogie-detail/body.json.gz','engineering/station_rail/common.py','engineering/vehicle_installation/model.py','engineering/vehicle_installation/underframe.py','engineering/powered_bogie/geometry.py'])
roster.update(p for p in git('ls-tree','-r','--name-only',COMMIT,'--','engineering/compact_drive').decode().splitlines() if p.endswith(('.py','.json')))
source('engineering/compact_drive/common.py');source('engineering/compact_drive/run.py');source('engineering/compact_drive/evaluate.py');source('engineering/compact_drive/kinematics.py')
variants={};physical_position_hashes={};request_source=None
for variant in ('offset-380mm','offset-420mm'):
 base=RUN/variant;m=validate_manifest(base/'manifest.json');checksum_file(base/'MANIFEST.sha256')
 req=read(base/'execution-request.json');rec=read(base/'execution-receipt.json');inp=read(base/'output/input.json');g=read(base/'output/geometry.json');result=read(base/'output/result.json');contract=read(base/'output/interface-contract.json')
 body=json.loads(gzip.decompress((base/'output/body.json.gz').read_bytes()))
 for label,v in (('request',req),('receipt',rec),('geometry',g),('result',result),('body',body)):
  expect(sealed(v),variant+' '+label+' canonical seal')
 expect(sealed(contract,'contract_id'),variant+' contract canonical seal')
 expect(body['candidate_id']==ident(body['physical_definition']),variant+' physical candidate seal')
 cid=body['candidate_id'];bid=body['evaluation_id'];gid=g['evaluation_id'];rid=result['evaluation_id']
 expect(all(v['candidate_id']==cid for v in (m,rec,g,result,contract)),variant+' candidate links')
 expect(all(v['body_evaluation_id']==bid for v in (rec,g,result)),variant+' body evaluation links')
 expect(rec['geometry_evaluation_id']==result['geometry_evaluation_id']==gid,variant+' geometry links')
 expect(m['result_evaluation_id']==rec['result_evaluation_id']==rid,variant+' result links')
 expect(top['variant_candidate_ids'][variant]==cid,variant+' top physical link')
 expect(contract==body['compact_drive_contract'],variant+' contract payload equality')
 expect(body['physical_definition']['compact_assembly_entities']==contract['assembly_entities'],variant+' physical entity graph equality')
 expect(body['parent_candidate_id']==body['physical_definition']['parent_candidate_id']==inp['parent_candidate_id']==cmp['parent_candidate_id']=='9f6d223074b3438a546d5b3d71cd9b970807387ef0542023bed79bef46dbdeba',variant+' parent binding')
 expect(req['config_id']==result['config_id']==contract['config']['id']==body['physical_definition']['config']['id']==cmp['baseline_config']=='compact-737-h100',variant+' config binding')
 expect(inp['config']==contract['config']==next(c for c in policy['configs'] if c['id']==req['config_id']),variant+' full config payload')
 package=contract['support_package'];expect(package==body['physical_definition']['support_package'],variant+' support physical/contract definition')
 expect(package['family']==constants['SUPPORT_FAMILY'] and package['variant']==variant and package['variables']==constants['SUPPORT_VARIANTS'][variant] and package['lane_definitions']==list(constants['SUPPORT_LANES']),variant+' source family variables and lanes')
 expect(req['variant']==inp['support_family']==variant and req['candidate_family']==package['family'],variant+' request family binding')
 maps=[req['source_sha256'],inp['source_sha256'],body['source_sha256'],result['source_before'],result['source_after'],rec['source_before'],rec['source_after']]
 expect(all(x==maps[0] for x in maps),variant+' exact source epoch union')
 expect(set(maps[0])==roster,variant+' complete producer source roster')
 for name,want in maps[0].items():expect(sha(source(name))==want,variant+' git source hash '+name)
 if request_source is None:request_source=maps[0]
 else:expect(request_source==maps[0],'same source epoch across variants')
 expect(all(v['source_commit']==COMMIT for v in (req,rec,result,m)),variant+' pinned source commits')
 expect(rec['source_unchanged'] is True and result['source_unchanged'] is True,variant+' before after source equality')
 for label,v in (('input',inp),('body',body),('geometry',g),('result',result)):
  for flag in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release','selected_reference_changed'):
   expect(v.get(flag) is False,variant+' '+label+' no promotion '+flag)
 expect(req['native_CAD'] is False and req['native_FEM'] is False and rec['native_jobs']==0,variant+' no native declaration')
 support_ids={r['id'] for r in body['parts'] if r['id'].startswith('compact-drive/pedestal-') or r['id'] in ('compact-drive/emergency-cap','compact-drive/emergency-riser')}
 pats=[r for r in body['patterns'] if r['part_id'] in support_ids]
 entities={r['id']:r for r in contract['assembly_entities'] if r['part_id'] in support_ids and r['role']!='allocation'}
 screen=g['support_package_screen'];nominal=[r for r in g['nominal_findings'] if r.get('part_id') in support_ids or r.get('other_part_id') in support_ids]
 cont=[r for r in g['continuous_and_interface_holds'] if r.get('entity','').split('@')[0] in support_ids]
 ground=[r for r in g['ground_samples'] if r.get('entity','').split('@')[0] in support_ids]
 expect(len(support_ids)==screen['unique_support_part_types']==9,variant+' nine core support types')
 expect(all(r['count']>0 for r in pats) and sum(r['count'] for r in pats)==screen['support_occurrences']==len(entities)==288,variant+' positive support occurrence coverage')
 expect(len(ground)==screen['support_ground_pose_rows']==288 and len({r['entity'] for r in ground})==288 and {r['entity'] for r in ground}==set(entities),variant+' exact nonvacuous ground entity coverage')
 expect(len(g['pose_samples'])==20<=policy['limits']['maximum_pose_samples']==24,variant+' twenty bounded sampled poses')
 bogies=Counter(entities[r['entity']]['bogie'] for r in ground);expect(set(bogies)==set(range(12)) and set(bogies.values())=={24},variant+' ground core supports across all12 bogies')
 for r in ground:
  e=entities[r['entity']]
  expect(r['frame']==e['frame']=='body',variant+' ground frame consistency')
  expect(r['required_ground_m']==policy['ground_allocation_m'] and r['passed_sample']==(r['sample_min_z_m']>=r['required_ground_m']+e['uncertainty_m']),variant+' stored sampled ground predicate')
  expect(r['continuous_ground_verified'] is False,variant+' sampled ground not continuous qualification')
 expect(all(r['passed_sample'] for r in ground) and screen['screens']['sampled_support_ground']=='PASS_WITHIN_SAMPLED_POSES',variant+' nonvacuous sampled ground verdict')
 expect(len(cont)==screen['support_continuous_bound_rows']==312 and len(nominal)==screen['support_nominal_clearance_rows']==2040,variant+' stored support HOLD counts')
 cb=Counter(r['bogie'] for r in cont);expect(set(cb)==set(range(12)) and set(cb.values())=={26},variant+' continuous HOLD coverage acrossall12 bogies')
 expect(all(r['kind']=='continuous-relative-bound-hold' and r['entity'] in entities for r in cont),variant+' typed conservative HOLD records')
 for key in ('nominal_support_clearance','continuous_support_envelope','support_load_path_and_joint_strength','support_stiffness_fatigue_and_retention','supplier_and_finished_geometry','finite_removal_and_service','physical_acceptance'):expect(screen['screens'][key]=='HOLD',variant+' retained HOLD '+key)
 for c in CASES:expect(math.isclose(math.fsum(r['mass_kg'][c] for r in pats),screen['support_mass_kg'][c],rel_tol=1e-12) and screen['support_mass_kg'][c]>0,variant+' positive mass ledger '+c)
 expect(len(g['all12_bogie_records'])==12 and {r['bogie'] for r in g['all12_bogie_records']}==set(range(12)),variant+' all12 repetition records')
 expect(result['nominal_findings']==len(g['nominal_findings'])==5964 and result['continuous_interface_holds']==len(g['continuous_and_interface_holds'])==3942,variant+' result finding totals')
 expect(g['known_geometry_screen_pass'] is False and result['known_geometry_screen_pass'] is False and g['geometry_screen'].startswith('HOLD'),variant+' no geometry acceptance')
 emergency=[e for e in entities.values() if e['part_id'] in ('compact-drive/emergency-cap','compact-drive/emergency-riser')]
 expect(len(emergency)==48,variant+' emergency support physical occurrences')
 xoff=constants['SUPPORT_VARIANTS'][variant]['emergency_x_offset_m']
 for e in emergency:
  bx=8.5+(e['bogie']//2)*17.65+(-6.4 if e['bogie']%2==0 else 6.4)
  expect(math.isclose(abs(e['at_m'][0]-bx),xoff,abs_tol=1e-12),variant+' actual emergency x-offset geometry')
 positions=sorted((e['part_id'],e['bogie'],e['at_m']) for e in entities.values());physical_position_hashes[variant]=ident(positions)
 resource_row=rec['resource'];expect(result['usage']['peak_rss_kib']==resource_row['peak_rss_kib'] and math.isclose(result['wall_s'],resource_row['wall_seconds']),variant+' receipt/result resource agreement')
 expect(result['usage']['user_s']==resource_row['user_seconds'] and result['usage']['system_s']==resource_row['system_seconds'],variant+' receipt/result CPU agreement')
 expect(req['limits']==dict(address_space_bytes=1073741824,cpu_seconds_soft_hard=[60,62],maximum_trials=1,wall_seconds=90),variant+' declared frozen bounds')
 expect(req['wrapper']==['timeout','--signal=TERM','90s','prlimit','--cpu=60:62','--as=1073741824:1073741824','--core=0:0','--','/usr/bin/time','-v'],variant+' recorded timeout/prlimit command')
 expect(resource_row['user_seconds']+resource_row['system_seconds']<60 and resource_row['wall_seconds']<90 and resource_row['peak_rss_kib']<1048576,variant+' observations within declared bounds')
 text=(base/'resource.txt').read_text();outer_user=float(re.search(r'User time \(seconds\): ([\d.]+)',text)[1]);outer_sys=float(re.search(r'System time \(seconds\): ([\d.]+)',text)[1]);outer_rss=int(re.search(r'Maximum resident set size \(kbytes\): (\d+)',text)[1]);outer_clock=re.search(r'Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): (\S+)',text)[1];parts_clock=[float(x) for x in outer_clock.split(':')];outer_wall=sum(v*60**i for i,v in enumerate(reversed(parts_clock)))
 expect(outer_rss==resource_row['peak_rss_kib'] and outer_user+outer_sys<60 and outer_wall<90 and outer_wall>=resource_row['wall_seconds'],'outer time corroboration '+variant)
 expect((base/'exit-code.txt').read_text().strip()=='0' and rec['exit_code']==0 and rec['execution']==result['execution']=='completed' and 'Exit status: 0' in text,variant+' completed calculation status')
 expect(not (base/'stderr.log').read_bytes(),variant+' empty stderr')
 stdout=(base/'stdout.log').read_text().splitlines();expect(len(stdout)==1 and json.loads(stdout[0])=={k:result[k] for k in ('evaluation_id','execution','config_id')},variant+' exact stdout result link')
 cv=cmp['variants'][variant]
 expected=dict(candidate_id=cid,body_evaluation_id=bid,geometry_evaluation_id=gid,result_evaluation_id=rid,package_evaluation_id=m['evaluation_id'],nominal_finding_count=5964,continuous_interface_hold_count=3942,known_geometry_screen_pass=False,support_ground_pose_rows=288,support_ground_failed_rows=0,sampled_ground_screen='PASS_WITHIN_SAMPLED_POSES',support_continuous_rows=312,support_failed_continuous_rows=312,continuous_screen='HOLD',candidate_identity_distinct_from_peer=True,engineering_accepted=False,physical_accepted=False,selected_or_promoted=False)
 expect(cv==expected,variant+' complete comparison row')
 variants[variant]=dict(candidate_id=cid,body_evaluation_id=bid,geometry_evaluation_id=gid,result_evaluation_id=rid,package_evaluation_id=m['evaluation_id'],support_types=9,support_occurrences=288,ground_summary_rows=288,pose_samples=20,support_pose_evaluations_implied_by_source=5760,ground_per_bogie=dict(sorted(bogies.items())),continuous_HOLD_rows=312,continuous_HOLD_per_bogie=dict(sorted(cb.items())),nominal_support_findings=2040,total_nominal_findings=5964,total_continuous_interface_holds=3942,support_mass_kg=screen['support_mass_kg'],resource_receipt=resource_row,outer_time=dict(user_s=outer_user,system_s=outer_sys,wall_s=outer_wall,max_rss_kib=outer_rss),emergency_support_position_digest=physical_position_hashes[variant],screens=screen['screens'])
 del body,g,contract,entities,ground,cont,nominal,pats;gc.collect()
expect(len(set(top['variant_candidate_ids'].values()))==2 and len(set(physical_position_hashes.values()))==2,'genuinely distinct physical geometry variants')
old_after=snapshot(OLD);run_after=snapshot(RUN);expect(old_before==old_after,'run01 content and filemetadata preserved');expect(run_before==run_after,'run02 content and filemetadata preserved')
summary=dict(schema='osr-compact-drive-support-run02-independent-review/1',source_commit=COMMIT,root_manifest_sha256=sha((RUN/'manifest.json').read_bytes()),root_manifest_evaluation_id=top['evaluation_id'],root_checksum_file_sha256=sha((RUN/'MANIFEST.sha256').read_bytes()),run02_files=len(run_before),run01_files=len(old_before),run01_manifest_sha256=sha((OLD/'manifest.json').read_bytes()),run01_file_set_digest=ident([(r['path'],r['sha256'],r['bytes']) for r in old_before]),run01_preserved=old_before==old_after,run02_preserved=run_before==run_after,check_categories=dict(checks),errors=errors,variants=variants,source_roster_records=source_records,verification='Hash/seal/link/count/ledger/receipt checks only; no project module import, trial rerun, CAD or FEM.',limitations=['288ground rows are per-entity minima over20stored poses, not288individual poses. Continuous-ground qualification remains false.','312continuous rows are retained conservative HOLD findings, not the denominator of all checked broadphase pairs; the total checked counter is not serialized.','Wrapper enforcement is asserted by retained requests/receipts; observed/usr/bin/time and getrusage records agree and remain within bounds. This audit did not observe live process limits.','The command uses-B, which disables bytecode writes but does not itself authenticate existing pyc reads. No source-only cache execution attestation or OS read-only sandbox is inferred.','Internal integrity/source bindings support an unselected held analytical archive; they do not qualify support load paths, joints, stiffness, fatigue, supplier geometry, removal or hardware.'])
for name,data in [('audit.json',summary),('run01-before.json',old_before),('run01-after.json',old_after),('run02-before.json',run_before),('run02-after.json',run_after)]: (OUT/name).write_bytes(enc(data))
files={p.relative_to(OUT).as_posix():dict(sha256=sha(p.read_bytes()),bytes=p.stat().st_size) for p in sorted(OUT.rglob('*')) if p.is_file()}
m=dict(schema='osr-compact-drive-support-run02-review-packet/1',source_commit=COMMIT,files=files,trial_rerun=False,source_changed=False);m['packet_id']=ident(m);(OUT/'manifest.json').write_bytes(enc(m))
for p in OUT.rglob('*'):
 if p.is_file():p.chmod(0o444)
for p in sorted((p for p in OUT.rglob('*') if p.is_dir()),reverse=True):p.chmod(0o555)
OUT.chmod(0o555)
print(json.dumps(dict(packet_path=str(OUT),packet_id=m['packet_id'],manifest_sha256=sha((OUT/'manifest.json').read_bytes()),root_manifest_sha256=summary['root_manifest_sha256'],root_manifest_evaluation_id=top['evaluation_id'],checks=sum(checks.values()),errors=errors,variants=variants,run01_manifest_sha256=summary['run01_manifest_sha256'],run01_file_set_digest=summary['run01_file_set_digest'],run01_preserved=summary['run01_preserved']),sort_keys=True))
