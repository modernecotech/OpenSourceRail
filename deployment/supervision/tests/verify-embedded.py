"""Installed test: native CBM/points -> history, alarms and ERP cases; restore fixtures."""
import importlib.util
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('supervision', ROOT / 'tools/automation/supervision.py')
s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
controls = ROOT / 'var/supervision/simulator-control.json'
previous = controls.read_text() if controls.exists() else '{}'

def asset(city, equipment_type='vehicle-cbm'):
    snap = s.api('/snapshot', role='viewer', query='?city=' + city + '&environment=simulation')
    return next(a for a in snap['assets'] if a['equipment_type'] == equipment_type)

def wait(predicate, timeout=40):
    end=time.monotonic()+timeout
    while time.monotonic()<end:
        value=predicate()
        if value:return value
        time.sleep(1)
    raise AssertionError('Embedded condition did not reach expected state')

try:
    before=json.loads(previous)
    assert not before.get('cbm_service') and not before.get('points_detection_fault') and not before.get('disconnected'), 'Normal fixture required'
    scoped={**before,'cities':{**before.get('cities',{}),'samawah':{
        **before.get('cities',{}).get('samawah',{}),'cbm_service':True,'points_detection_fault':True}}}
    s.write_private(controls,json.dumps(scoped))
    def delivered():
        a=asset('samawah')
        alarms=[r for r in a['alarms'] if r['active'] and r['case_id']]
        return (a,alarms[0]) if alarms else None
    a,alarm=wait(delivered)
    assert a['readings']['health']['value']==2 and a['readings']['brake_remaining_pct']['value']==10
    assert asset('mosul')['readings']['health']['value']==0
    def points_delivered():
        a=asset('samawah','points')
        alarms=[r for r in a['alarms'] if r['active'] and r['case_id']]
        return (a,alarms[0]) if alarms else None
    point,point_alarm=wait(points_delivered)
    assert point['readings']['detected_position']['value']==0
    assert point['readings']['detection_unknown']['value']==1
    assert asset('mosul','points')['readings']['detection_unknown']['value']==0
    assert point_alarm['case_id'] != alarm['case_id']
    case=alarm['case_id'];occurrences=alarm['occurrences']
    time.sleep(4)
    repeated=next(r for r in asset('samawah')['alarms'] if r['rule']=='component-service')
    assert repeated['case_id']==case and repeated['occurrences']==occurrences
    print('PASS native CBM service flag -> one scoped ERP Issue:',case)
    print('PASS native fail-restrictive point detection -> separate scoped ERP Issue:',point_alarm['case_id'])
    print('PASS repeated telemetry does not duplicate cases; Mosul remains nominal')
finally:
    s.write_private(controls,previous)
wait(lambda:asset('samawah')['readings']['health']['value']==0)
wait(lambda:asset('samawah','points')['readings']['detection_unknown']['value']==0)
a=asset('samawah');alarm=next(r for r in a['alarms'] if r['rule']=='component-service')
assert not alarm['active'] and alarm['erp_status']=='Open'
point=asset('samawah','points');point_alarm=next(r for r in point['alarms'] if r['rule']=='position-unknown')
assert not point_alarm['active'] and point_alarm['erp_status']=='Open'
print('PASS controller conditions cleared; ERP cases remain open for accountable maintenance')
