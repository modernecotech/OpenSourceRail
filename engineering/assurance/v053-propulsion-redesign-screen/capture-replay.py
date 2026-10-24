"""One-time archive construction: retain selected replay, never production writes."""
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json,os,subprocess,sys,tempfile
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
 original=json.loads((BASE/'executed/manifest.json').read_bytes())
 with tempfile.TemporaryDirectory(prefix='osr-propulsion-archive-replay-') as temporary:
  root=Path(temporary)
  for name,h in original['source_sha256'].items():
   assert not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts
   source=BASE/'inputs'/name;data=source.read_bytes();assert sha256(data).hexdigest()==h
   target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
  work=root/'build/propulsion-redesign-screen';work.mkdir(parents=True)
  for source,target in [('executed/run.py','run.py'),('replay-selected.py','replay-selected.py')]:
   data=(BASE/source).read_bytes()
   if source=='executed/run.py':assert sha256(data).hexdigest()==original['files_sha256']['run.py']
   (work/target).write_bytes(data)
  env=dict(os.environ,PYTHONPATH=str(root),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
  with (BASE/'selected-replay.log').open('wb') as log:
   subprocess.run([sys.executable,str(work/'replay-selected.py'),str(BASE)],cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
  (BASE/'selected-replay-receipt.json').write_bytes((work/'replay-selected-results.json').read_bytes())
 print('Selected archived cold/warm coupons reproduced exactly; elapsed_host_s excluded only.')
