from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from hashlib import sha256
import json,os,resource,subprocess,sys,time
from engineering.station_rail.common import encoded,identity
root=Path.cwd();package=root/'build/flanged-system-evidence/final-three-v2';worker=package/'worker.py';python=Path(sys.executable);env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONHASHSEED='0',PYTHONPATH=str(root))
def limits():
 resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824));resource.setrlimit(resource.RLIMIT_CPU,(60,60))
def execute(name):
 folder=package/name;request=json.loads((folder/'request.json').read_bytes());start=time.monotonic();status='started';code=None
 with (folder/'stdout.log').open('xb') as stdout,(folder/'stderr.log').open('xb') as stderr:
  process=subprocess.Popen([str(python),str(worker),name],cwd=root,env=env,stdout=stdout,stderr=stderr,preexec_fn=limits)
  try:
   code=process.wait(timeout=60);status='completed' if code==0 else 'failed'
  except subprocess.TimeoutExpired:
   process.kill();process.wait();status='wall-timeout'
 value=dict(schema='osr-flanged-private-execution/1',request_id=request['request_id'],execution=status,returncode=code,wall_seconds=time.monotonic()-start,limits=request['limits'],actual_files={p.name:sha256(p.read_bytes()).hexdigest() for p in folder.iterdir() if p.is_file()},isolation='ordinary subprocess with resource limits; no filesystem or network sandbox',physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False)
 value['execution_id']=identity(value)
 with (folder/'execution.json').open('xb') as out:out.write(encoded(value))
 return (name,status)
with ThreadPoolExecutor(max_workers=3) as pool:out=list(pool.map(execute,('baseline','thick-web','thick-flange')))
print(out,flush=True)
if any(status!='completed' for _,status in out):raise SystemExit(1)
