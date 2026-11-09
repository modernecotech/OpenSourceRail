from pathlib import Path
import hashlib,json,resource,subprocess,sys,time
RUN=Path(__file__).resolve().parent;ROOT=Path('/home/hayder/.local/state/opensourcerail/worktrees/v06-design-closure-20261108')
enc=lambda v:(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ident=lambda v:hashlib.sha256(enc(v)).hexdigest()
refs=[Path('/home/hayder/.local/state/opensourcerail/runs/samawah-city-adapter-20261109T220121Z'),
 Path('/home/hayder/.local/state/opensourcerail/runs/samawah-acceleration-sensitivity-20261109T221401Z'),
 Path('/home/hayder/.local/state/opensourcerail/runs/samawah-station-consolidation-20261109T224002Z'),
 Path('/home/hayder/.local/state/opensourcerail/runs/samawah-station-consolidation-20261109T224002Z-attempt02'),
 Path('/home/hayder/.local/state/opensourcerail/runs/samawah-station-consolidation-20261109T224002Z-attempt03')]
def snapshots():
 out={}
 for p in refs:
  m=json.loads((p/'manifest.json').read_bytes());assert m['packet_id']==ident({k:v for k,v in m.items() if k!='packet_id'})
  for n,r in m['files'].items():assert (p/n).stat().st_size==r['bytes'] and sha(p/n)==r['sha256'],str(p/n)
  out[str(p)]={n:sha(p/n) for n in ['manifest.json',*sorted(m['files'])]}
 return out
if (RUN/'manifest.json').exists():raise SystemExit('Immutable attempt already exists')
before=snapshots();commit=subprocess.check_output(['/usr/bin/git','-C',str(ROOT),'rev-parse','90d07f045b^{commit}']).decode().strip()
request=dict(schema='osr-private-samawah-station-consolidation-request/1',repository=str(ROOT),source_commit=commit,
 body_candidate_id='75075df9247dfff7082a78eadc273d3a99f37e5486450621536c43b1bfa2f797',
 body_evaluation_id='fdac4907a6a867f0b4f27e0876a772d1b54d526ec323beb3b6d9a155e0e00b21',
 reference_outline_evaluation_id='0b1715bb59c73645335865a35f317ab51bb24254f1ec2f7711521ef9c32d333c',
 source_marker_ids=['line-1-0485-0464-s009300','line-1-0487-0466-s009380'],
 operation='Only merge the named two line-1 markers at mean chainage on the unchanged polyline',
 worker_sha256=sha(RUN/'worker.py'),prior_attempt_packet_id='b4cac0377dde3d13c3d89617a3acc567692ba60fadc77732aa2978b9bdc57a99',prior_attempt_manifest_sha256='2f5880bff653b562836de0bc29541f6681e49d083e2efd1c2296aa0081a9f0a4',prior_attempt_disposition='Original0.4 control reproduced exactly. Derived input was correctly refused because the worker sealed it before interchange-reference propagation; successor seals only after all declared field changes. No checks or resource bounds changed.',git_read_configuration=dict(packedGitWindowSize='16m',packedGitLimit='32m'),retained_packet_before_hashes=before,cpu_limit_s=60,address_space_limit_bytes=1024**3,
 wall_timeout_s=60,native_GIS_CAD_FEM_allowed=False,repository_edits_allowed=False,physical_accepted=False)
request['request_id']=ident(request);(RUN/'request.json').write_bytes(enc(request))
def limits():
 resource.setrlimit(resource.RLIMIT_CPU,(60,60));resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
command=[sys.executable,'-I','-B',str(RUN/'worker.py')]
started=time.monotonic()
try:
 p=subprocess.run(command,cwd=RUN,stdout=subprocess.PIPE,stderr=subprocess.PIPE,preexec_fn=limits,timeout=60)
 (RUN/'stdout.log').write_bytes(p.stdout);(RUN/'stderr.log').write_bytes(p.stderr);returncode=p.returncode
except subprocess.TimeoutExpired as exc:
 (RUN/'stdout.log').write_bytes(exc.stdout or b'');(RUN/'stderr.log').write_bytes(exc.stderr or b'');returncode=124
usage=resource.getrusage(resource.RUSAGE_CHILDREN);after=snapshots();assert before==after
receipt=dict(schema='osr-private-samawah-station-consolidation-receipt/1',request_id=request['request_id'],command=command,
 returncode=returncode,elapsed_s=time.monotonic()-started,child_user_cpu_s=usage.ru_utime,child_system_cpu_s=usage.ru_stime,
 child_maxrss_kib=usage.ru_maxrss,retained_packets_unchanged=before==after,retained_packet_after_hashes=after,
 isolation='Linux child RLIMIT_CPU and RLIMIT_AS, parent wall timeout, source-byte compilation checks; writable source filesystem, no OS read-only sandbox',
 source_repository_status_after=subprocess.check_output(['/usr/bin/git','-C',str(ROOT),'status','--short','--untracked-files=normal']).decode(),
 native_execution=False,service_complete=False,cost_complete=False,physical_accepted=False,gate_closed=False)
receipt['receipt_id']=ident(receipt);(RUN/'receipt.json').write_bytes(enc(receipt))
files={p.relative_to(RUN).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(RUN.rglob('*')) if p.is_file()}
m=dict(schema='osr-private-samawah-station-consolidation-run/1',source_commit=commit,request_id=request['request_id'],
 receipt_id=receipt['receipt_id'],execution_completed=returncode==0,files=files,physical_accepted=False,gate_closed=False)
m['packet_id']=ident(m);(RUN/'manifest.json').write_bytes(enc(m))
for p in RUN.rglob('*'):
 if p.is_file():p.chmod(0o444)
for p in sorted((p for p in RUN.rglob('*') if p.is_dir()),reverse=True):p.chmod(0o555)
RUN.chmod(0o555)
print(json.dumps(dict(path=str(RUN),packet_id=m['packet_id'],manifest_sha256=sha(RUN/'manifest.json'),receipt=receipt),sort_keys=True))
print((RUN/'stdout.log').read_text())
if returncode:print((RUN/'stderr.log').read_text());sys.exit(returncode)
