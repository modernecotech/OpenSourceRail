"""Read-only final legacy witness/source and coherent raw-negative controls."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from engineering.ferrite_maglev import assembled_body,moving_train,body_stiffness as b

def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())

def expected_sources():
    values={**moving_train.sources(),**assembled_body.sources(),**b.sources()}
    values['build/body-axial-sensitivity/run.py']=digest(ROOT/'build/body-axial-sensitivity/run.py')
    return values

before=expected_sources();p=ROOT/'build/body-axial-sensitivity';receipt=read(p/'receipt.json');summary=read(p/'summary.json')
assert before==receipt['source_sha256']==summary['source_sha256']
assert all(digest(ROOT/name)==value for name,value in before.items())
for name,value in receipt['files_sha256'].items():assert digest(p/name)==value
controls=[];runs=[]
for item in summary['runs']:
    run=json.loads(gzip.decompress((p/item['file']).read_bytes()));a=run['assumptions']
    assert run['candidate_sha256']==sha256(moving_train.encoded(a)).hexdigest()==item['candidate_sha256']
    assert run['formation']['cars']==6 and run['formation']['car_mass_kg']==26200.
    assert item['metrics']=={k:v for k,v in run.items() if k not in b.METRIC_EXCLUDE}
    b.validate_trace_and_energy(run,a)
    runs.append(dict(file=item['file'],candidate_sha256=item['candidate_sha256'],frames=len(run['coupler_step_witness']['midpoint_relative_velocity_m_s']),trace_rows=len(run['trace']),phase_degrees=run['maximum_magnetic_phase_spread_degrees']))
    for control in ('zero-energy','zero-force','truncated-trace','mutated-witness'):
        bad=deepcopy(run)
        if control=='zero-energy':bad['longitudinal_energy']={k:0. for k in bad['longitudinal_energy']}
        elif control=='zero-force':bad['peak_coupler_force_n']=0.
        elif control=='truncated-trace':bad['trace']=bad['trace'][:1];bad['maximum_magnetic_phase_spread_degrees']=.1
        else:bad['coupler_step_witness']['midpoint_relative_velocity_m_s'][100][0]+=.001
        try:b.validate_trace_and_energy(bad,a)
        except ValueError as error:controls.append(dict(file=item['file'],control=control,rejected=True,reason=str(error)))
        else:raise AssertionError('inconsistent legacy raw result accepted: '+control)
assert before==expected_sources()
proof=dict(schema='osr-final-body-witness-controls/1',source_sha256=before,
    audit_driver_sha256=digest(__file__),audit_driver_path=Path(__file__).relative_to(ROOT).as_posix(),
    legacy_receipt_sha256=digest(p/'receipt.json'),legacy_runs=runs,controls=controls,
    sources_current_before_and_after=True,physical_acceptance=False)
(ROOT/'build/body-stiffness-final-controls.json').write_bytes(b.encoded(proof))
print(json.dumps(dict(source_files=len(before),legacy_runs=len(runs),rejected_controls=len(controls),proof='build/body-stiffness-final-controls.json'),sort_keys=True),flush=True)
