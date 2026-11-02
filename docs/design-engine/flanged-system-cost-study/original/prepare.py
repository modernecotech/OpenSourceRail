from pathlib import Path
import gzip,json,shutil,hashlib,sys
from engineering.design_search import flanged_system_cost as f
from engineering.station_rail.common import encoded,identity
root=Path.cwd();package=root/'build/flanged-system-evidence/final-three-v2';baseline=json.load(gzip.open(package/'baseline.json.gz','rt'));manifest=json.loads((package/'baseline-manifest.json').read_bytes());producer=hashlib.sha256((package/'producer.py').read_bytes()).hexdigest()
for name in ('baseline','thick-web','thick-flange'):
 case=package/name;case.mkdir(exist_ok=False);source=root/'docs/design-engine/flanged-span-study/original'/name
 for part in ('request.json','result.json'):shutil.copyfile(source/part,case/('original-'+part))
 orig=json.loads((case/'original-request.json').read_bytes());r=json.loads((case/'original-result.json').read_bytes())
 inputs=['baseline.json.gz','baseline-manifest.json','producer.py','worker.py',name+'/original-request.json',name+'/original-result.json']
 request=dict(schema='osr-flanged-system-cost-private-request/1',gauge=name,original_candidate_id=orig['candidate']['candidate_id'],original_geometry_id=orig['candidate']['geometry_id'],original_scoped_evaluation_id=r['cost']['evaluation_id'],expected_baseline_id=baseline['baseline_id'],expected_baseline_manifest_id=manifest['manifest_id'],load_context_id=orig['context']['context_id'],expected_composition_candidate_id=f.composition(orig['candidate'],baseline)['candidate_id'],producer_sha256=producer,input_sha256={part:hashlib.sha256((package/part).read_bytes()).hexdigest() for part in inputs},runtime=f.base._tools(),limits=dict(address_space_bytes=1073741824,cpu_seconds=60,wall_seconds=60,blas_threads=1),scope='Scenario accounting only; no native solve, qualification or selected reference change',physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False)
 request['request_id']=identity(request)
 with (case/'request.json').open('xb') as out:out.write(encoded(request))
print('three request inputs preserved')
