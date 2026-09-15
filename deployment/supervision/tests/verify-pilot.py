"""Run from repo root; records simulation-only commissioning and maintenance rehearsal."""
import importlib.util,json,time
from pathlib import Path
from datetime import datetime,timezone,timedelta
spec=importlib.util.spec_from_file_location('supervision',Path('tools/automation/supervision.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
now=datetime.now(timezone.utc);rid='pilot-lighting-'+str(time.time_ns())
message=dict(request_id=rid,city='samawah',environment='simulation',asset_id='SAM-ST-001:facilities',command='set_lighting',parameters={'level':75},created_at=now.isoformat(),expires_at=(now+timedelta(seconds=25)).isoformat(),required_conditions=['local_remote_enabled'])
r=s.api('/commands',message,role='operator');assert r['state']=='requested'
for _ in range(10):
 snapshot=s.api('/snapshot',role='viewer',query='?city=samawah&environment=simulation')
 asset=next(a for a in snapshot['assets'] if a['equipment_type']=='facilities')
 if asset['commands_audit'] and asset['commands_audit'][0]['state']=='completed' and asset['readings']['lighting_pct']['value']==75:break
 time.sleep(1)
else:raise AssertionError('Controller did not confirm lighting change')
print('PASS live command requested -> controller accepted -> completed -> measured lighting 75%')
package=json.loads(Path('build/supervision/samawah/simulation/package.json').read_text())
# Explicit simulation rehearsal evidence, not physical acceptance.
base=dict(city='samawah',environment='simulation',asset_id='SAM-ST-001:charger',engineering_revision=package['engineering_revision'],references=['simulation-rehearsal:build/supervision-native-final.log','simulation-rehearsal:build/supervision-fuxa-check.log'])
for kind,role,extra in [('design-review','engineer',{}),('execution-release','reviewer',{}),('installation','engineer',{'serial':'SIM-CHARGER-001','batch':'SIM-PILOT-001'}),('commissioning-test','inspector',{'result':'pass'}),('commissioning-release','reviewer',{'test_id':'pilot-commissioning-test'}),('maintenance','maintainer',{})]:
 s.api('/evidence',dict(base,id='pilot-'+kind,kind=kind,**extra),role=role)
print('PASS simulation lifecycle rehearsal with separate inspector/reviewer credentials')
