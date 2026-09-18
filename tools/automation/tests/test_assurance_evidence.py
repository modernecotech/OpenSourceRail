import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('controlled_assurance', ROOT/'tools/automation/assurance-evidence.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


@pytest.fixture
def bundle(tmp_path, monkeypatch):
    if not shutil.which('openssl'): pytest.skip('OpenSSL is required for acceptance signature verification')
    monkeypatch.setattr(a, 'ROOT', tmp_path)
    private, public = tmp_path/'private.pem', tmp_path/'public.pem'
    subprocess.run(['openssl','genpkey','-algorithm','ED25519','-out',str(private)],check=True,capture_output=True)
    subprocess.run(['openssl','pkey','-in',str(private),'-pubout','-out',str(public)],check=True,capture_output=True)
    source, log = tmp_path/'proof.rs', tmp_path/'proof.log'
    source.write_text('fn harness() {}');log.write_text('VERIFICATION:- SUCCESSFUL\n')
    row = dict(solution='E1',kind='kani',path='proof.rs',anchor='harness',tool='cargo-kani',tool_version='cargo-kani 0.67.0',bounds='reviewed test bounds',executed_by='runner',status='passed',exit_code=0,report='proof.log',report_sha256=a.sha(log),inputs={'proof.rs':a.sha(source)})
    required_inputs=row['inputs'].copy()
    monkeypatch.setattr(a, 'scope', lambda:required_inputs)
    declared = {k:row[k] for k in ['solution','kind','path','anchor']}
    monkeypatch.setattr(a, 'declared', lambda:[declared])
    results,envelope,signature,policy = [tmp_path/name for name in ['results.toml','acceptance.json','signature.bin','policy.json']]
    results.write_text(a.toml([row]))
    data=dict(schema='osr-independent-acceptance/1',status='accepted',reviewer='reviewer',reference='test-only review',results_sha256=a.sha(results),solutions=['E1'],dependency_scope_reviewed=True)
    policy.write_text(json.dumps(dict(reviewers={'reviewer':dict(enabled=True,public_key='public.pem',public_key_sha256=a.sha(public))})))
    def sign():
        envelope.write_text(json.dumps(data))
        subprocess.run(['openssl','pkeyutl','-sign','-inkey',str(private),'-rawin','-in',str(envelope),'-out',str(signature)],check=True,capture_output=True)
    sign()
    return dict(args=(results,envelope,signature,policy),data=data,row=row,sign=sign,source=source,log=log)


def test_authenticated_signature_is_limited_to_listed_results(bundle):
    result=a.verify_acceptance(*bundle['args'])
    assert result['authenticated'] and result['solutions']==['E1']
    assert result['physical_release'] is False


@pytest.mark.parametrize('change',['result-bytes','source','log','signature','disabled','key','self-review','scope','unreviewed','failed','duplicate','wrong-anchor','escape'])
def test_rejects_stale_forged_or_incomplete_acceptance(bundle, change):
    results,envelope,signature,policy=bundle['args']
    row,data=bundle['row'],bundle['data']
    if change=='result-bytes':results.write_text(results.read_text()+'\n# tamper')
    elif change in {'source','log'}:bundle[change].write_text('changed bytes')
    elif change=='signature':signature.write_bytes(b'not a signature')
    elif change in {'disabled','key'}:
        p=json.loads(policy.read_text());p['reviewers']['reviewer']['enabled' if change=='disabled' else 'public_key_sha256']=False;policy.write_text(json.dumps(p))
    else:
        if change=='self-review':row['executed_by']='reviewer'
        if change=='scope':data['solutions']=[]
        if change=='unreviewed':data['dependency_scope_reviewed']=False
        if change=='failed':row.update(status='failed',exit_code=1)
        if change=='wrong-anchor':row['anchor']='wrong'
        if change=='escape':row['inputs']['../outside']='digest'
        results.write_text(a.toml([row,row] if change=='duplicate' else [row]))
        data['results_sha256']=a.sha(results);bundle['sign']()
    with pytest.raises((ValueError,subprocess.CalledProcessError)):
        a.verify_acceptance(*bundle['args'])
