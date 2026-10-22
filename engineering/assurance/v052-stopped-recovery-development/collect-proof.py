"""Collect executed local evidence without promoting engineering acceptance."""
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).parent
sys.path.insert(0,str(ROOT))
from engineering.ferrite_maglev import model, stopped_recovery


def read(path):return json.loads(path.read_bytes())
def digest(path):return sha256(path.read_bytes()).hexdigest()
def write(name,value):
    (BASE/name).write_text(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n')


def retained_check(name):
    receipt=read(BASE/(name+'.json'))
    assert receipt['exit_status']==0 and receipt['source_unchanged'] is True
    assert receipt['log_sha256']==digest(BASE/(name+'.txt'))
    assert all(receipt[k] is False for k in model.FLAGS)
    return receipt


def main():
    checks={name:retained_check(name) for name in (
        'rust-current-workspace','rust-current-lint','rust-current-format','python-integration',
        'bundle-selection','python-deferred','readme-check','browser-report','browser-workbench','background-install')}
    rust=sum(map(int,re.findall(r'test result: ok\. (\d+) passed;',
        (BASE/'rust-current-workspace.txt').read_text())))
    assert rust==705
    for name,count in (('python-integration',33),('bundle-selection',25)):
        assert re.search(rf'\b{count} passed\b',(BASE/(name+'.txt')).read_text())
    assert re.search(r'\b2 passed\b',(BASE/'python-deferred.txt').read_text())
    focused=ROOT/'build/recovery-focused-python.log'
    assert '80 passed' in focused.read_text()
    shutil.copyfile(focused,BASE/'python-recovery-capacity.txt')
    # The original focused launch predates this receipt driver. Do not invent
    # a pre-execution source receipt or an execution timestamp for that run.
    write('python-recovery-capacity.json',dict(command=[
        'tools/automation/osr-python','-m','pytest','-q',
        'engineering/analysis/tests/test_ferrite_maglev_stopped_recovery.py',
        'engineering/analysis/tests/test_ferrite_maglev_line_capacity.py'],
        passed=80,log_sha256=digest(BASE/'python-recovery-capacity.txt'),
        binding='Original focused run has no pre-execution envelope receipt. The canonical recovery/capacity packet publishers independently bind before/after sources and retain their actual executed controls.',
        **model.FLAGS))
    for source,name in (
        ('build/recovery-completed-primary.json','primary-refresh.json'),
        ('build/recovery-pre-bundle-fix-refresh.json','source-change-hold.json'),
        ('build/recovery-git-portability.json','git-source-portability.json'),
        ('build/recovery-completed-background.json','background-refresh.json'),
        ('build/recovery-report-browser/browser-check.json','report-browser.json'),
        ('build/recovery-report-browser/primary-study-desktop.png','report-desktop.png'),
        ('build/recovery-report-browser/primary-study-mobile.png','report-mobile.png'),
        ('build/recovery-workbench-browser/checks.json','workbench-browser.json'),
        ('build/recovery-workbench-browser/desktop.png','workbench-desktop.png'),
        ('build/recovery-workbench-browser/mobile.png','workbench-mobile.png')):
        shutil.copyfile(ROOT/source,BASE/name)
    for name in ('primary-refresh.json','background-refresh.json'):
        journal=read(BASE/name)
        assert journal['state'] in {'idle; sources unchanged','implemented studies current; engineering closure open'}
        assert all(s['state'] in {'verified-existing','rebuilt-and-verified'} for s in journal['stages'])
        assert any(s['id']=='stopped-controller-recovery' for s in journal['stages'])
        assert all(journal[k] is False for k in model.FLAGS)
    held=read(BASE/'source-change-hold.json')
    assert held['state']=='held' and 'input sources changed during primary build' in held['error']
    portability=read(BASE/'git-source-portability.json')
    assert portability['git_source_and_packet_identity'] is True
    report=read(BASE/'report-browser.json');workbench=read(BASE/'workbench-browser.json')
    assert len(report['images'])==35 and len(report['videos'])==12
    assert not report['javascript_errors'] and not report['external_requests'] and not report['failed_requests']
    assert report['accepted_item_count']==0 and report['mobile_overflow'] is False
    assert workbench['cities']==266 and workbench['images']==10
    assert workbench['errors']==[] and workbench['external']==[] and workbench['mobile'] is True
    recovery=stopped_recovery.read_summary()
    assert recovery['runs']==44 and recovery['successful_reconciliations']==10 and recovery['adverse_cases_rejected']==34
    manifest=ROOT/'docs/design-engine/ferrite-maglev/stopped-recovery/manifest.json'
    shutil.copyfile(manifest,BASE/'stopped-recovery-manifest.json')
    spec=importlib.util.spec_from_file_location('body_bundle_current',ROOT/'tools/automation/package-maglev-release.py')
    package=importlib.util.module_from_spec(spec);spec.loader.exec_module(package)
    selected=package.body_evidence_paths()
    assert (BASE/'body-axial-receipt.json').relative_to(ROOT).as_posix() in selected
    bundle=ROOT/'build/recovery-multipart-bundle'
    bundle_raw=(bundle/'RELEASE-MANIFEST.json').read_bytes()
    (BASE/'multipart-bundle-manifest.json.gz').write_bytes(gzip.compress(bundle_raw,mtime=0))
    shutil.copyfile(bundle/'SHA256SUMS',BASE/'multipart-bundle-SHA256SUMS.txt')
    timer=subprocess.check_output(['systemctl','--user','is-active','osr-primary-infrastructure.timer'],text=True).strip()
    assert timer=='active'
    service=subprocess.check_output(['systemctl','--user','show','osr-primary-infrastructure.service',
        '--property=ActiveState,Result,ExecMainStatus,ExecMainExitTimestamp'],text=True)
    write('summary.json',dict(schema='osr-stopped-recovery-development-assurance/1',
        rust_tests_passed=rust,focused_python_tests_passed=80,additional_python_tests_passed=60,
        integration_tests_initially_deferred_then_executed=2,
        test_scope='705 workspace Rust tests and 140 targeted Python tests; this is not a rerun of every repository Python test.',
        command_receipts={name:digest(BASE/(name+'.json')) for name in checks},
        recovery=recovery,report_images=35,report_videos=12,report_links=len(report['links']),
        workbench_cities=266,workbench_images=10,mobile_checked=True,
        bundle_manifest_sha256=sha256(bundle_raw).hexdigest(),
        timer_active=True,service_show=service,observed_source_change_hold=True,
        git_source_and_packet_members_checked=portability['checked_files'],
        background_scope='An installed source-change refresh completed successfully; the timer continues checking implemented studies. It cannot manufacture hardware or supply external acceptance.',
        all_points_closed=False,accepted_engineering_releases=0,
        open_gates=list(stopped_recovery.HOLDS)+[
            'Complete equipped vehicle, joined-body strength/fatigue and calibrated coupled magnetic/body behavior remain open.',
            'Site-specific foundations, qualified civil connections/erection, curved stations, rescue and evacuation acceptance remain open.',
            'Complete installed costs, supplier configurations, hardware tests and independent acceptance remain open.'],
        **model.FLAGS))
    write('checksums.json',{p.name:digest(p) for p in sorted(BASE.iterdir()) if p.is_file() and p.name!='checksums.json'})
    print(json.dumps(dict(rust=rust,python=140,replays=44,images=35,videos=12,timer_active=True,all_points_closed=False)))


if __name__=='__main__':main()
