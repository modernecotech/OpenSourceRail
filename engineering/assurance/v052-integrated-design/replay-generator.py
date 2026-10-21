"""Execute the existing Baghdad four-circuit normal-duty energy ledger."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import gzip,json,sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from engineering.ferrite_maglev import cities,model

def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
source=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad/engineering/maglev/summary.json'
output=ROOT/'build/v052-final-baghdad-four-circuits.json.gz'
before=digest(source)
report=json.loads(source.read_bytes())
expected=report['source_sha256']
assert expected and all(digest(ROOT/name)==value for name,value in expected.items())
result=cities.replay_city(report,cycles=4,charger_efficiency=.9,regen_available=False,missed_charge_events=())
assert digest(source)==before
assert all(digest(ROOT/name)==value for name,value in expected.items())
assert result['source_sha256']==expected and result['source_current']
assert all(line['cycles']==4 and abs(line['energy_ledger_residual_kwh'])<1e-7 for line in result['lines'])
assert result['physical_release'] is False and result['route_acceptance'] is False and result['force_acceptance'] is False
result.update(model.FLAGS)
result['assurance_receipt']=dict(schema='osr-baghdad-four-circuit-source-receipt/1',
    executed_utc=datetime.now(timezone.utc).isoformat(),generator_path=Path(__file__).relative_to(ROOT).as_posix(),
    generator_sha256=digest(__file__),input_summary_path=source.relative_to(ROOT).as_posix(),input_summary_sha256=before,
    input_source_sha256=expected,input_source_current_before_and_after=True,cycles=4,
    charger_efficiency=.9,regeneration_available=False,missed_charge_events=[],
    scope='One representative train per line, normal-duty repeated energy ledger; fleet traffic, protected emergency reserve, physical route and hardware remain unaccepted')
raw=(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
output.write_bytes(gzip.compress(raw,mtime=0))
retained=json.loads(gzip.decompress(output.read_bytes()))
assert retained==result
print(json.dumps(dict(output=output.relative_to(ROOT).as_posix(),sha256=digest(output),source_current=retained['source_current'],
    normal_window_passed=retained['normal_window_passed'],lines=len(retained['lines']),events=sum(len(line['events']) for line in retained['lines']),
    maximum_energy_ledger_residual_kwh=max(abs(line['energy_ledger_residual_kwh']) for line in retained['lines']),
    failed_lines=[line['line'] for line in retained['lines'] if not line['normal_window_passed']],physical_release=False),indent=2))
