from pathlib import Path
import hashlib,json,resource,shutil,subprocess,sys,time
from engineering.outline import city_inputs
from engineering.railway_project import city_acceleration_sensitivity as study
from engineering.station_rail.common import encoded,identity
root=Path.cwd();run=Path(__file__).resolve().parent
retained=Path('/home/hayder/.local/state/opensourcerail/runs/samawah-city-adapter-20261109T220121Z')
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def reference_snapshot():
 m=json.loads((retained/'manifest.json').read_bytes())
 assert hashfile(retained/'manifest.json')==study.REFERENCE_MANIFEST_SHA256
 assert m['packet_id']==study.REFERENCE_PACKET==identity({k:v for k,v in m.items() if k!='packet_id'})
 for name,r in m['files'].items():
  p=retained/name;assert p.stat().st_size==r['bytes'] and hashfile(p)==r['sha256'],name
 return {name:hashfile(retained/name) for name in ['manifest.json',*sorted(m['files'])]}
if (run/'manifest.json').exists():raise SystemExit('Immutable study already exists')
before=reference_snapshot();(run/'inputs').mkdir()
body=run/'inputs/body.json.gz';shutil.copyfile(root/study.outline.BODY_FILE,body)
city=city_inputs.load('samawah',root=root);(run/'inputs/city.json').write_bytes(encoded(city))
(run/'inputs/reference-policy.json').write_bytes((root/study.outline.POLICY).read_bytes())
command=[sys.executable,'-m','engineering.railway_project.city_acceleration_sensitivity','--body',str(body),'--output',str(run/'result.json')]
request=dict(schema='osr-bounded-city-acceleration-run-request/1',source_commit=subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),command=command,source_city_input_id=city['input_id'],body_candidate_id=study.outline.BODY,body_evaluation_id=study.outline.BODY_EVALUATION,acceleration_hypotheses_m_s2=list(study.ACCELERATIONS),retained_packet_path=str(retained),retained_file_sha256=before,cpu_limit_s=60,address_space_limit_bytes=1024**3,wall_timeout_s=60,scope='Three held kinematic requests and inertia-only mass-times-acceleration/speed components; no native solve, cost closure or drive selection',physical_accepted=False)
request['request_id']=identity(request);(run/'request.json').write_bytes(encoded(request))
def limits():
 resource.setrlimit(resource.RLIMIT_CPU,(60,60));resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
started=time.monotonic();p=subprocess.run(command,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,preexec_fn=limits,timeout=60)
(run/'stdout.log').write_bytes(p.stdout);(run/'stderr.log').write_bytes(p.stderr)
if p.returncode:print(p.stderr.decode());raise SystemExit(p.returncode)
result=json.loads((run/'result.json').read_bytes());study.verify(result)
after=reference_snapshot();assert before==after
receipt=dict(schema='osr-bounded-city-acceleration-run-receipt/1',request_id=request['request_id'],returncode=p.returncode,elapsed_s=time.monotonic()-started,child_maxrss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,retained_original_integrity_checked=True,retained_original_unchanged=True,isolation='Linux child RLIMIT_CPU/RLIMIT_AS and parent wall timeout; no OS read-only source sandbox is claimed',native_execution=False,service_complete=False,cost_complete=False,physical_accepted=False,achieved_acceleration=False,drive_selected=False,candidate_id=result['candidate_id'],evaluation_id=result['evaluation_id'])
receipt['receipt_id']=identity(receipt);(run/'receipt.json').write_bytes(encoded(receipt))
files={p.relative_to(run).as_posix():dict(sha256=hashfile(p),bytes=p.stat().st_size) for p in sorted(run.rglob('*')) if p.is_file()}
manifest=dict(schema='osr-bounded-city-acceleration-run/1',source_commit=request['source_commit'],request_id=request['request_id'],receipt_id=receipt['receipt_id'],files=files,retained_original_packet_id=study.REFERENCE_PACKET,physical_accepted=False,service_complete=False,cost_complete=False,drive_selected=False)
manifest['packet_id']=identity(manifest);(run/'manifest.json').write_bytes(encoded(manifest))
for p in run.rglob('*'):
 if p.is_file():p.chmod(0o444)
for p in sorted((p for p in run.rglob('*') if p.is_dir()),reverse=True):p.chmod(0o555)
run.chmod(0o555)
summary=[]
for case in result['cases']:
 inertia=next(r for r in case['inertia_only_lower_bound_components'] if r['mass_scenario']=='normal-base')
 summary.append(dict(acceleration=case['acceleration_hypothesis_m_s2'],source_outline_evaluation_id=case['source_outline_evaluation_id'],case_evaluation_id=case['evaluation_id'],base_fleet=case['fleet_request_cases']['base'],normal_base_inertia_N=inertia['translational_inertia_force_N'],normal_base_inertia_W_at20m_s=inertia['mechanical_power_at_declared_speed_cap_W'],base_oneway_seconds_by_line={r['line_id']:r['assumed_one_way_runtime_s'] for r in case['kinematic_lines']}))
print(json.dumps(dict(path=str(run),packet_id=manifest['packet_id'],manifest_sha256=hashfile(run/'manifest.json'),result_sha256=hashfile(run/'result.json'),candidate_id=result['candidate_id'],evaluation_id=result['evaluation_id'],summary=summary,receipt=receipt),sort_keys=True))
