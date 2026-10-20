"""Dependency recovery, publication holds and primary UI boundaries."""
import http.client
import importlib.util
import json
from pathlib import Path
import subprocess
import threading

import pytest

from engineering.ferrite_maglev import model, workflow


def test_failed_dependency_stops_descendants_and_restart_reuses_verified_outputs(tmp_path):
    stored = {}
    events = []
    failing = {'b': True}

    def stage(name, parent=None):
        def verify():
            events.append(('verify', name))
            if name not in stored or parent and stored[name] != stored[parent]:
                raise ValueError('missing or stale')
        def build():
            events.append(('build', name))
            if failing.get(name):
                raise ValueError('simulated evaluator failure')
            stored[name] = stored[parent] if parent else 'revision-1'
        return name, verify, build

    stages = [stage('a'), stage('b', 'a'), stage('c', 'b')]
    with pytest.raises(ValueError, match='evaluator failure'):
        workflow.run(state=tmp_path, stage_list=stages)
    held = json.loads((tmp_path/'latest.json').read_text())
    assert held['state'] == 'held'
    assert [s['id'] for s in held['stages']] == ['a', 'b']
    assert not any(name == 'c' for _, name in events)
    assert all(held[k] is False for k in model.FLAGS)
    failing['b'] = False
    events.clear()
    resumed = workflow.run(state=tmp_path, stage_list=stages)
    assert ('build', 'a') not in events
    assert resumed['stages'][0]['state'] == 'verified-existing'
    assert all(s['state'] == 'rebuilt-and-verified' for s in resumed['stages'][1:])
    stored['a'] = 'revision-2'
    events.clear()
    workflow.run(state=tmp_path, stage_list=stages)
    assert stored['c'] == 'revision-2'
    assert ('build', 'b') in events and ('build', 'c') in events


def test_successful_execution_with_failed_verification_still_holds(tmp_path):
    def reject():
        raise ValueError('result rejected')
    downstream = []
    with pytest.raises(ValueError, match='result rejected'):
        workflow.run(state=tmp_path, stage_list=[('bad', reject, lambda: None),
            ('descendant', lambda: downstream.append('called'), lambda: None)])
    assert not downstream
    assert json.loads((tmp_path/'latest.json').read_text())['stages'][0]['state'] == 'failed'


def test_manual_and_timer_runs_cannot_build_concurrently(tmp_path):
    with workflow.locked(tmp_path):
        with pytest.raises(ValueError, match='runner lock'):
            with workflow.locked(tmp_path):
                pytest.fail('second writer admitted')
    with workflow.locked(tmp_path):
        pass


def test_source_change_during_build_holds_before_descendant(tmp_path, monkeypatch):
    revision = {'value': 'old'}
    monkeypatch.setattr(model, 'sources', lambda: {'input.toml': revision['value']})
    def missing():
        raise ValueError('stale')
    def edit():
        revision['value'] = 'new'
    reached = []
    with pytest.raises(ValueError, match='sources changed'):
        workflow.run(state=tmp_path, stage_list=[('first', missing, edit),
            ('descendant', lambda: reached.append(True), lambda: None)])
    assert not reached


def test_interrupted_packet_replacement_keeps_old_marker_and_can_recover(tmp_path, monkeypatch):
    output = tmp_path/'published'
    output.mkdir()
    for name in ('a.json', 'b.json', 'manifest.json'):
        (output/name).write_text('old')
    def staged():
        target = tmp_path/'staging'
        target.mkdir(exist_ok=True)
        for name in ('a.json', 'b.json', 'manifest.json'):
            (target/name).write_text('new')
        return target
    original = workflow.os.replace
    def crash(source, destination):
        if Path(destination).name == 'b.json':
            raise OSError('interrupted replacement')
        original(source, destination)
    with monkeypatch.context() as patch:
        patch.setattr(workflow.os, 'replace', crash)
        with pytest.raises(OSError, match='interrupted'):
            workflow.install_packet(staged(), output)
    assert (output/'a.json').read_text() == 'new'
    assert (output/'b.json').read_text() == 'old'
    assert (output/'manifest.json').read_text() == 'old'
    workflow.install_packet(staged(), output)
    assert all(p.read_text() == 'new' for p in output.iterdir())
    assert not any(p.name.startswith('.') for p in output.iterdir())


def test_packet_recovery_preserves_unowned_files(tmp_path):
    output, target = tmp_path/'published', tmp_path/'staged'
    output.mkdir(); target.mkdir()
    (output/'personal-notes.txt').write_text('preserve')
    (target/'manifest.json').write_text('new')
    with pytest.raises(ValueError, match='unexpected files'):
        workflow.install_packet(target, output)
    assert (output/'personal-notes.txt').read_text() == 'preserve'


def test_install_retires_only_this_checkouts_design_units(monkeypatch):
    from types import SimpleNamespace
    spec = importlib.util.spec_from_file_location('primary_cli', model.ROOT/'tools/automation/ferrite-maglev-study.py')
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    mutations = []
    def run(args, **kwargs):
        if args[2] == 'cat':
            # A second checkout's unit must never be stopped.
            source = '/other/checkout' if args[-1] == 'osr-design-progress.service' else str(model.ROOT)
            return SimpleNamespace(returncode=0, stdout=source)
        if args[2] == 'show':
            return SimpleNamespace(returncode=0, stdout='loaded\n')
        if args[2] == 'is-enabled':
            return SimpleNamespace(returncode=0, stdout='enabled\n')
        mutations.append(args)
        return SimpleNamespace(returncode=0, stdout='')
    monkeypatch.setattr(cli.subprocess, 'run', run)
    retired = cli.retire_legacy_units()
    assert 'osr-assembly-verification.timer' in retired
    assert 'osr-design-coverage.timer' in retired
    assert not any('design-progress' in name for name in retired)
    assert all(not any(word in ' '.join(args) for word in ('erp','supervision','primary-infrastructure')) for args in mutations)


def test_primary_reader_source_manifest_excludes_legacy_product_model():
    result = subprocess.run([str(model.ROOT/'osr'), 'book', '--list-sources'],
        cwd=model.ROOT, capture_output=True, text=True, check=True, timeout=30)
    assert 'engineering/ferrite_maglev/README.md' in result.stdout
    assert 'crates/osr-maglev-control/README.md' in result.stdout
    assert 'rolling-stock/light-metro-3car' not in result.stdout


@pytest.fixture
def endpoint():
    spec = importlib.util.spec_from_file_location('primary_workbench', model.ROOT/'tools/automation/maglev-workbench.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    class Handler(module.Handler):
        def log_message(self, *args):
            pass
    server = module.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    def request(path, method='GET'):
        client = http.client.HTTPConnection('127.0.0.1', server.server_port)
        client.request(method, path)
        response = client.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        client.close()
        return result
    yield request
    server.shutdown()
    server.server_close()
    thread.join()


def test_default_ui_routes_to_maglev_and_has_no_private_or_mutable_routes(endpoint):
    status, headers, _ = endpoint('/')
    assert status == 303 and headers['Location'] == '/docs/workbench/maglev/'
    assert endpoint('/docs/workbench/maglev/')[0] == 200
    assert endpoint('/docs/design-engine/ferrite-maglev/beam-only/overview.png')[0] == 200
    assert endpoint('/engineering/ferrite_maglev/city-index.json')[0] == 200
    for path in ['/.git/config', '/var/ops-core.sqlite3', '/build/maglev-workflow/latest.json',
                 '/docs/workbench/maglev/%2e%2e/%2e%2e/README.md', '/docs/design-engine/ferrite-maglev/',
                 '/api/design/jobs', '/crates/osr-maglev-control/src/lib.rs']:
        assert endpoint(path)[0] == 404, path
    assert endpoint('/api/design/jobs', 'POST')[0] == 501


def test_ui_serves_every_primary_city_summary(endpoint):
    index = json.loads((model.ROOT/'engineering/ferrite_maglev/city-index.json').read_text())
    from urllib.parse import quote
    for row in index['cities']:
        status, _, data = endpoint(quote('/'+row['package_path']+'/summary.json'))
        assert status == 200
        summary = json.loads(data)
        assert summary['architecture'] == 'ferrite-pm-maglev-study'
        assert summary['city'] == row['city']
        assert all(summary[k] is False for k in model.FLAGS)
