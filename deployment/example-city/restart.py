"""Restart the retained example, verifying data survives every example service stop."""
from datetime import datetime,timezone
import hashlib
import json
import time


def verify(h):
    report=json.loads((h.OUTPUT/'report.json').read_text())
    if report.get('passed') is not True:raise RuntimeError('A completed city scenario is required')
    cfg=json.loads((h.PRIVATE/'integration.json').read_text())
    token=next(p['token'] for p in cfg['principals'] if p['role']=='viewer')
    def snapshot():return h.request_json('http://127.0.0.1:8192/snapshot?city=samawah&environment=simulation',headers={'Authorization':'Bearer '+token})
    def histories():return {a['asset_id']:a['installations'] for a in snapshot()['assets']}
    def work():return h.request_json('http://127.0.0.1:8190/api/ops-core/samawah')['state']['workOrders']
    def project():return {name:hashlib.sha256((h.PRIVATE/'city-project'/name).read_bytes()).hexdigest() for name in ['project.osr.toml','sources.lock.json']}
    before=histories(),work(),project()
    def save():
        report['finished_at']=datetime.now(timezone.utc).isoformat()
        h.write(h.OUTPUT/'report.json',report)
        h.write(h.OUTPUT/'report.html',h.module('example_restart_report','deployment/example-city/report.py').render(report,[p.name for p in sorted(h.OUTPUT.glob('workbench-*.png'))]))
    def check(name,condition):
        report['checks'].append(dict(name=name,passed=bool(condition),before=None,after=None))
        if not condition:raise AssertionError(name)
        print('PASS '+name,flush=True)
    try:
        h.stop();h.start();ready=time.time()
        check('Full stop/start preserves installed and removed serial history',histories()==before[0])
        check('Full stop/start preserves OSR railway work and its baseline/run links',work()==before[1])
        check('Full stop/start preserves the retained City Studio project configuration',project()==before[2])
        end=time.monotonic()+75
        while time.monotonic()<end:
            a=next(a for a in snapshot()['assets'] if a['equipment_type']=='charger')
            reading=a['readings']['temperature_c']
            if reading['quality']=='valid' and reading['received']>=ready:break
            time.sleep(1)
        else:raise AssertionError('No fresh native controller measurement after full restart')
        check('Full stop/start resumes newly received native controller measurements',True)
        save()
    except BaseException as error:
        report.update(passed=False,error=str(error));save();raise
