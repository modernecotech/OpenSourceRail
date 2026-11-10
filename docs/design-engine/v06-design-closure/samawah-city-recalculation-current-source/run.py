from pathlib import Path
import hashlib,json,resource,shutil,subprocess,sys,time
sys.path.insert(0,str(Path.cwd()))
from engineering.outline import city_inputs
from engineering.railway_project import city_recalculation as adapter
from engineering.station_rail.common import encoded,identity
root=Path.cwd(); run=Path(__file__).resolve().parent
if (run/'manifest.json').exists():raise SystemExit('Immutable run already sealed')
(run/'inputs').mkdir()
body=run/'inputs/body.json.gz';shutil.copyfile(root/adapter.BODY_FILE,body)
city=city_inputs.load('samawah',root=root);(run/'inputs/city.json').write_bytes(encoded(city))
(run/'inputs/policy.json').write_bytes((root/adapter.POLICY).read_bytes())
command=[sys.executable,'-m','engineering.railway_project.city_recalculation','--body',str(body),'--output',str(run/'result.json')]
request=dict(schema='osr-bounded-city-adapter-run-request/1',source_commit=subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),command=command,city_input_id=city['input_id'],body_candidate_id=adapter.BODY,body_evaluation_id=adapter.BODY_EVALUATION,root=str(root),cpu_limit_s=60,address_space_limit_bytes=1024**3,wall_timeout_s=60,scope='Pure Python held planning/quantity requests only; no native solve, cost completion or publication',physical_accepted=False)
request['request_id']=identity(request);(run/'request.json').write_bytes(encoded(request))
def limits():
 resource.setrlimit(resource.RLIMIT_CPU,(60,60));resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
started=time.monotonic();p=subprocess.run(command,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,preexec_fn=limits,timeout=60)
(run/'stdout.log').write_bytes(p.stdout);(run/'stderr.log').write_bytes(p.stderr)
receipt=dict(schema='osr-bounded-city-adapter-run-receipt/1',request_id=request['request_id'],returncode=p.returncode,elapsed_s=time.monotonic()-started,child_maxrss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,isolation='Linux child RLIMIT_CPU and RLIMIT_AS plus parent wall timeout; source tree is writable and no OS read-only sandbox is claimed',native_execution=False,cost_complete=False,service_complete=False,physical_accepted=False)
if p.returncode!=0:print(p.stderr.decode());raise SystemExit(p.returncode)
result=json.loads((run/'result.json').read_bytes());adapter.verify(result)
receipt['candidate_id']=result['candidate_id'];receipt['evaluation_id']=result['evaluation_id'];receipt['receipt_id']=identity(receipt);(run/'receipt.json').write_bytes(encoded(receipt))
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files={p.relative_to(run).as_posix():dict(sha256=hashfile(p),bytes=p.stat().st_size) for p in sorted(run.rglob('*')) if p.is_file()}
manifest=dict(schema='osr-bounded-city-adapter-run/1',source_commit=request['source_commit'],request_id=request['request_id'],receipt_id=receipt['receipt_id'],files=files,physical_accepted=False,cost_complete=False,service_complete=False)
manifest['packet_id']=identity(manifest);(run/'manifest.json').write_bytes(encoded(manifest))
for p in run.rglob('*'):
 if p.is_file():p.chmod(0o444)
for p in sorted((p for p in run.rglob('*') if p.is_dir()),reverse=True):p.chmod(0o555)
run.chmod(0o555)
print(json.dumps(dict(path=str(run),packet_id=manifest['packet_id'],manifest_sha256=hashfile(run/'manifest.json'),result_sha256=hashfile(run/'result.json'),candidate_id=result['candidate_id'],evaluation_id=result['evaluation_id'],policy_id=result['policy_id'],source_city_input_id=result['source_city_input_id'],quantities=result['quantities'],fleet_request_cases=result['fleet_request_cases'],definition_failures=result['definition_failures'],known_BOM_process_subtotal=result['known_counted_BOM_process_subtotal_usd'],receipt=receipt),sort_keys=True))
