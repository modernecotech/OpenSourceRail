from pathlib import Path
import gzip,json,sys,hashlib
from engineering.design_search import flanged_system_cost as f
from engineering.station_rail.common import encoded,identity
root=Path.cwd();package=root/'build/flanged-system-evidence/final-three-v2';name=sys.argv[1];case=package/name
request=json.loads((case/'request.json').read_bytes())
if request['request_id']!=identity({k:v for k,v in request.items() if k!='request_id'}):raise ValueError('Request identity differs')
for file,expected in request['input_sha256'].items():
 path=package/file
 if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('Input bytes differ: '+file)
source=root/'engineering/design_search/flanged_system_cost.py'
if hashlib.sha256(source.read_bytes()).hexdigest()!=request['producer_sha256']:raise ValueError('Source epoch differs')
baseline=json.load(gzip.open(package/'baseline.json.gz','rt'));original=json.loads((case/'original-request.json').read_bytes());result=json.loads((case/'original-result.json').read_bytes())
out=f.compare(original['candidate'],result['quantities'],result['cost'],baseline,original['context'],root=root,expected_baseline_manifest_id=request['expected_baseline_manifest_id'])
if out['candidate_id']!=request['expected_composition_candidate_id'] or out['baseline_id']!=request['expected_baseline_id']:raise ValueError('Result ancestry differs')
if any(out[k] is not False for k in f.FLAGS) or out['integrated_selection'] is not None:raise ValueError('Unexpected promotion')
with (case/'result.json.gz').open('xb') as raw:
 with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as stream:stream.write(encoded(out))
print('completed',name,out['evaluation_id'],out['candidate_id'],flush=True)
