"""Actual browser disposition journey; credentials never enter public artifacts."""
import json
import secrets
import subprocess
import time


def verify(h):
    if json.loads((h.OUTPUT/'report.json').read_text()).get('passed') is not True:raise RuntimeError('Complete the base example first')
    passwords={role:secrets.token_urlsafe(24) for role in ['proposer','reviewer','executor']}
    data=dict(site=h.SITE,source=json.loads((h.OUTPUT/'native-records.json').read_text()),run=str(time.time_ns()),passwords=passwords)
    script='INPUT = '+repr(data)+'\n'+(h.ROOT/'deployment/example-city/disposition-fixture.py').read_text()
    result=subprocess.run(h.compose('erp','exec','-T','backend','env/bin/python'),input=script,text=True,capture_output=True,cwd=h.ROOT)
    # Frappe errors can include request details; fixture diagnostics are private.
    h.write(h.PRIVATE/'disposition-fixture.log',result.stdout+result.stderr,True)
    if result.returncode:raise RuntimeError('Disposition fixture failed; inspect private diagnostic log')
    fixture=next(json.loads(line.removeprefix('OSR_FIXTURE:')) for line in result.stdout.splitlines() if line.startswith('OSR_FIXTURE:'))
    h.write(h.PRIVATE/'disposition-browser.json',dict(**fixture,passwords=passwords),True)
    h.command(['node','deployment/example-city/verify-disposition-live.mjs'],'disposition-browser')
    report=json.loads((h.OUTPUT/'disposition-report.json').read_text())
    if not report['passed']:raise RuntimeError('Native browser disposition scenario failed')
    print('PASS actual browser proposal, independent endorsement, native action, verification and stale evidence')
