"""Dependency recovery, publication holds and primary UI boundaries."""
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
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



def test_first_pass_inventory_and_reader_use_refreshed_overview(tmp_path, monkeypatch):
    """A current inventory must become stale after its overview title changes."""
    monkeypatch.setattr(model, 'ROOT', tmp_path)
    monkeypatch.setattr(model, 'load', lambda: None)
    monkeypatch.setattr(model, 'sources', lambda **_: {'input.toml': 'unchanged'})
    scripts = tmp_path/'tools/automation'
    scripts.mkdir(parents=True)
    overview = tmp_path/'README.md'
    inventory = tmp_path/'docs/INDEX.md'
    reader = tmp_path/'docs/reader.txt'
    inventory.parent.mkdir()
    overview.write_text('# Previous overview\n')
    inventory.write_text('# Document index\n\n- Previous overview\n')
    built = []

    def document(command, *, cwd, check, capture_output, text):
        assert Path(cwd) == tmp_path
        assert check and capture_output and text
        script = Path(command[1])
        assert script.parent == scripts
        assert command[2:] in ([], ['--check'])
        if script.name == 'generate-public-overview.py':
            target, wanted = overview, '# Current overview\n'
        elif script.name == 'generate-doc-index.py':
            title = overview.read_text().splitlines()[0].removeprefix('# ')
            target, wanted = inventory, '# Document index\n\n- '+title+'\n'
        elif script.name == 'build-doc-book.py':
            target, wanted = reader, overview.read_text()+inventory.read_text()
        else:
            pytest.fail('unexpected document generator: '+script.name)
        if command[2:] == ['--check']:
            if not target.exists() or target.read_text() != wanted:
                raise subprocess.CalledProcessError(1, command, stderr='stale document')
        else:
            target.write_text(wanted)
            built.append(script.name)
        return subprocess.CompletedProcess(command, 0, stdout='', stderr='')

    monkeypatch.setattr(workflow.subprocess, 'run', document)
    selected = {'primary-overview', 'markdown-inventory', 'primary-reader-book'}
    stages = [row for row in workflow.stages(workflow.delivery.OUTPUT) if row[0] in selected]
    first = workflow.run(state=tmp_path/'state', stage_list=stages)
    assert first['state'] == 'implemented studies current; engineering closure open'
    assert inventory.read_text() == '# Document index\n\n- Current overview\n'
    assert reader.read_text() == overview.read_text()+inventory.read_text()
    assert 'Previous overview' not in reader.read_text()
    assert built == ['generate-public-overview.py', 'generate-doc-index.py', 'build-doc-book.py']
    built.clear()
    assert workflow.run(state=tmp_path/'state', stage_list=stages)['state'] == 'idle; sources unchanged'
    assert not built


def test_readme_coverage_follows_publishers_before_reader_and_then_stays_idle(tmp_path, monkeypatch):
    """An early valid audit becomes stale when later packets replace READMEs."""
    from hashlib import sha256
    from engineering.ferrite_maglev import capability_migration, pilot_release

    selected = {'v04-capability-migration', 'connected-pilot-delivery',
                'primary-overview', 'research-readme-context-coverage',
                'markdown-inventory', 'primary-reader-book'}

    def exercise(root, *, old_order):
        base = root/'docs/design-engine/ferrite-maglev'
        coverage = base/'research-closure/readme-coverage.json'
        inventory, reader = root/'docs/INDEX.md', root/'docs/reader.txt'
        readmes = [root/'README.md', base/'capability-migration/README.md',
                   base/'pilot-delivery/README.md']
        built = []
        for path in readmes:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('# Previous '+path.parent.name+'\n')
        coverage.parent.mkdir(parents=True)

        def snapshot():
            return {path.relative_to(root).as_posix(): sha256(path.read_bytes()).hexdigest()
                    for path in readmes}

        coverage.write_text(json.dumps(snapshot(), sort_keys=True))
        initial_coverage = coverage.read_bytes()
        monkeypatch.setattr(model, 'ROOT', root)
        monkeypatch.setattr(model, 'load', lambda: None)
        monkeypatch.setattr(model, 'sources', lambda **_: {'input.toml': 'unchanged'})
        monkeypatch.setattr(workflow, 'BASE', base)
        monkeypatch.setattr(workflow, 'STATE', root/'staging')

        def publisher(module, folder, title):
            wanted = '# Current '+title+'\n'

            def verify():
                if not (base/folder/'README.md').exists() or (base/folder/'README.md').read_text() != wanted:
                    raise ValueError('stale packet README')

            def publish(target):
                target.mkdir(parents=True)
                (target/'README.md').write_text(wanted)
                (target/'manifest.json').write_text('{}\n')
                built.append(folder)

            monkeypatch.setattr(module, 'verify', verify)
            monkeypatch.setattr(module, 'publish', publish)

        publisher(capability_migration, 'capability-migration', 'migration')
        publisher(pilot_release, 'pilot-delivery', 'delivery')

        def document(command, *, cwd, check, capture_output, text):
            assert Path(cwd) == root and check and capture_output and text
            checking = command[-1] == '--check'

            def current_coverage():
                if json.loads(coverage.read_text()) != snapshot():
                    raise subprocess.CalledProcessError(1, command, stderr='stale README coverage')

            if command[1:3] == ['-m', 'engineering.maglev_research.readme_context']:
                assert command[3:] in (['--check'], ['--write'])
                if checking:
                    current_coverage()
                else:
                    coverage.write_text(json.dumps(snapshot(), sort_keys=True))
                    built.append('coverage')
            else:
                script = Path(command[1])
                assert script.parent == root/'tools/automation'
                assert command[2:] in ([], ['--check'])
                if script.name == 'generate-public-overview.py':
                    target, wanted = readmes[0], '# Current overview\n'
                elif script.name == 'generate-doc-index.py':
                    target, wanted = inventory, ''.join(path.read_text() for path in readmes)
                elif script.name == 'build-doc-book.py':
                    # Both reader verification and publication reject an audit
                    # invalidated by a later README publisher.
                    current_coverage()
                    target, wanted = reader, inventory.read_text()+coverage.read_text()
                else:
                    pytest.fail('unexpected document generator: '+script.name)
                if checking:
                    if not target.exists() or target.read_text() != wanted:
                        raise subprocess.CalledProcessError(1, command, stderr='stale document')
                else:
                    target.write_text(wanted)
                    built.append(script.name)
            return subprocess.CompletedProcess(command, 0, stdout='', stderr='')

        monkeypatch.setattr(workflow.subprocess, 'run', document)
        stages = [row for row in workflow.stages(workflow.delivery.OUTPUT) if row[0] in selected]
        assert len(stages) == len(selected)
        if old_order:
            coverage_stage = next(row for row in stages if row[0] == 'research-readme-context-coverage')
            stages = [coverage_stage]+[row for row in stages if row is not coverage_stage]
            with pytest.raises(subprocess.CalledProcessError) as error:
                workflow.run(state=root/'state', stage_list=stages)
            assert error.value.stderr == 'stale README coverage'
            journal = json.loads((root/'state/latest.json').read_text())
            assert journal['state'] == 'held'
            assert journal['stages'][-1]['id'] == 'primary-reader-book'
            assert not reader.exists()
            assert coverage.read_bytes() == initial_coverage
            assert json.loads(coverage.read_text()) != snapshot()
            assert {'capability-migration', 'pilot-delivery'} <= set(built)
        else:
            result = workflow.run(state=root/'state', stage_list=stages)
            assert result['state'] == 'implemented studies current; engineering closure open'
            assert json.loads(coverage.read_text()) == snapshot()
            assert coverage.read_bytes() != initial_coverage
            assert 'Previous' not in reader.read_text()
            assert reader.read_text() == inventory.read_text()+coverage.read_text()
            assert {'capability-migration', 'pilot-delivery', 'coverage', 'build-doc-book.py'} <= set(built)
            built.clear()
            assert workflow.run(state=root/'state', stage_list=stages)['state'] == 'idle; sources unchanged'
            assert not built

    exercise(tmp_path/'early-audit', old_order=True)
    exercise(tmp_path/'current-order', old_order=False)


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
    monkeypatch.setattr(model, 'sources', lambda **_: {'input.toml': revision['value']})
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


def test_scheduler_has_exact_current_units_and_source_change_build_profile(tmp_path):
    spec = importlib.util.spec_from_file_location('primary_cli', model.ROOT/'tools/automation/ferrite-maglev-study.py')
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    output=tmp_path/'report with spaces%'
    units=cli.units(output)
    assert set(units)=={'osr-primary-infrastructure.service','osr-primary-infrastructure.timer'}
    service=units['osr-primary-infrastructure.service']
    assert 'Type=oneshot\n' in service and 'TimeoutStartSec=14400\n' in service
    assert 'WorkingDirectory='+str(model.ROOT) in service
    assert '"'+str(model.ROOT/'tools/automation/ferrite-maglev-study.py')+'" cycle --output' in service
    assert '"'+str(output).replace('%','%%')+'"' in service
    assert 'UMask=0077\n' in service
    timer=units['osr-primary-infrastructure.timer']
    assert 'OnBootSec=2min\n' in timer and 'OnUnitActiveSec=15min\n' in timer
    assert 'Persistent=true\n' in timer and 'Unit=osr-primary-infrastructure.service\n' in timer



def test_primary_reader_and_evidence_sources_bind_current_requirements_and_process_inputs():
    result = subprocess.run([str(model.ROOT/'osr'), 'book', '--list-sources'],
        cwd=model.ROOT, capture_output=True, text=True, check=True, timeout=30)
    rows=[line.split('\t',1) for line in result.stdout.splitlines() if line.strip()]
    assert all(len(row)==2 and row[0]=='primary' for row in rows)
    paths={row[1] for row in rows}
    assert {'engineering/ferrite_maglev/README.md','crates/osr-maglev-control/README.md'}<=paths
    assert all((model.ROOT/path).is_file() for path in paths)
    receipt=model.sources()
    for path in ('engineering/ferrite_maglev/data/requirements.json',
        'engineering/ferrite_maglev/data/systems-inventory.json',
        'engineering/ferrite_maglev/data/cost-rates.json',
        'engineering/ferrite_maglev/manufacturing.py'):
        assert path in receipt
        from hashlib import sha256
        assert receipt[path]==sha256((model.ROOT/path).read_bytes()).hexdigest()



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
    request.origin=f'http://127.0.0.1:{server.server_port}'
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
    assert endpoint('/cities/catalogue/west-asia/Iraq/Baghdad/README.md')[0] == 200
    assert endpoint('/cities/catalogue/west-asia/Iraq/Baghdad/city.json')[0] == 404
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


def test_actual_handler_allows_verified_blob_reads_but_blocks_external_connections(endpoint):
    """Image/media permission does not grant fetch permission for a Blob URL.

    Exercise Chromium with the real Handler's CSP. The independent other-origin
    listener proves a rejected network request never reaches its destination.
    Navigating to source text avoids starting unrelated city/design readers.
    """
    received=[]
    class Foreign(BaseHTTPRequestHandler):
        def do_GET(self):
            received.append(self.path)
            self.send_response(200);self.end_headers();self.wfile.write(b'must not be fetched')
        def log_message(self,*args):
            pass
    foreign=ThreadingHTTPServer(('127.0.0.1',0),Foreign)
    thread=threading.Thread(target=foreign.serve_forever,daemon=True);thread.start()
    script=r"""
import assert from 'node:assert/strict';
import {launchBrowser} from './tools/automation/tests/browser-launch.mjs';
const browser=await launchBrowser({headless:true});
try {
  const page=await browser.newPage();
  const response=await page.goto(process.argv[1]+'/docs/workbench/maglev/pilot.js');
  assert.ok(response.headers()['content-security-policy'].includes("connect-src 'self' blob:"));
  const result=await page.evaluate(async foreign=>{
    const content=new Uint8Array([0,1,2,253,254,255]);
    const url=URL.createObjectURL(new Blob([content],{type:'video/mp4'}));
    const retained=new Uint8Array(await(await fetch(url)).arrayBuffer());
    const sha=bytes=>crypto.subtle.digest('SHA-256',bytes).then(buffer=>
      [...new Uint8Array(buffer)].map(n=>n.toString(16).padStart(2,'0')).join(''));
    const digestMatches=(await sha(retained))===(await sha(content));
    URL.revokeObjectURL(url);
    let revokedRefused=false;
    try {await fetch(url);} catch {revokedRefused=true;}
    let timer;
    const violation=new Promise((resolve,reject)=>{
      timer=setTimeout(()=>reject(Error('External connect-src refusal was not observed')),3000);
      document.addEventListener('securitypolicyviolation',event=>{
        if(event.blockedURI.startsWith(foreign)) {
          clearTimeout(timer);resolve(event.effectiveDirective);
        }
      });
    });
    let externalRefused=false;
    try {await fetch(foreign+'/must-not-arrive');} catch {externalRefused=true;}
    const directive=await violation;
    return {digestMatches,revokedRefused,externalRefused,directive};
  },process.argv[2]);
  assert.deepEqual(result,{digestMatches:true,revokedRefused:true,externalRefused:true,directive:'connect-src'});
  console.log(JSON.stringify({...result,browser_environment:browser.osrRendering}));
} finally {await browser.close();}
"""
    try:
        result=subprocess.run(['node','--input-type=module','-e',script,endpoint.origin,
                               f'http://127.0.0.1:{foreign.server_port}'],cwd=model.ROOT,
                              capture_output=True,text=True,timeout=30)
        assert result.returncode==0,result.stdout+result.stderr
        observed=json.loads(result.stdout)
        assert observed['digestMatches'] is True
        assert observed['browser_environment']['mode'] in {'device-isolated-software','software-requested'}
        assert observed['browser_environment']['browser_version']
        assert received==[]
    finally:
        foreign.shutdown();foreign.server_close();thread.join()


def test_standalone_observer_change_holds_the_dependency_runner(tmp_path,monkeypatch):
    monkeypatch.setattr(model,'ROOT',tmp_path)
    monkeypatch.setattr(model,'load',lambda:None)
    monkeypatch.setattr(model,'sources',lambda **_: {})
    source=tmp_path/'engineering/ferrite_maglev/observer-prototype/src/lib.rs'
    source.parent.mkdir(parents=True);source.write_text('initial observer')
    def missing():raise ValueError('missing result')
    def edit():source.write_text('changed observer')
    reached=[]
    with pytest.raises(ValueError,match='sources changed'):
        workflow.run(state=tmp_path/'state',stage_list=[('observer',missing,edit),
            ('descendant',lambda:reached.append(True),lambda:None)])
    assert not reached


def test_migration_browser_dependency_change_stops_the_runner(tmp_path,monkeypatch):
    from engineering.ferrite_maglev import capability_migration
    monkeypatch.setattr(model,'ROOT',tmp_path)
    monkeypatch.setattr(model,'load',lambda:None)
    monkeypatch.setattr(model,'sources',lambda **_: {})
    marker=tmp_path/'engineering/ferrite_maglev/data/pilot-capability-migration.json'
    marker.parent.mkdir(parents=True);marker.write_text('{}')
    revision={'sha':'before'}
    monkeypatch.setattr(capability_migration,'sources',lambda:{'browser.mjs':revision['sha']})
    def missing():raise ValueError('missing result')
    def edit():revision['sha']='after'
    reached=[]
    with pytest.raises(ValueError,match='sources changed'):
        workflow.run(state=tmp_path/'state',stage_list=[('browser',missing,edit),
            ('dependent',lambda:reached.append(True),lambda:None)])
    assert not reached


def test_stale_book_is_rejected_before_expensive_report_checks(tmp_path,monkeypatch):
    from hashlib import sha256
    from engineering.ferrite_maglev import delivery
    spec=importlib.util.spec_from_file_location('primary_book_gate',model.ROOT/'tools/automation/build-doc-book.py')
    book=importlib.util.module_from_spec(spec);spec.loader.exec_module(book)
    monkeypatch.setattr(book,'primary_book_sources',lambda:{'input.md':'a'*64})
    calls=[]
    def qualified():
        calls.append(True)
        raise ValueError('report qualification still required')
    monkeypatch.setattr(delivery,'verify',qualified)
    pdf=tmp_path/'book.pdf';pdf.write_bytes(b'%PDF-test')
    options=dict(include_images=True,max_image_px=1600,image_quality=82,source_ref='main')
    receipt=dict(schema='osr-primary-reader-book/1',source_sha256={'input.md':'b'*64},
        options=options,pdf_sha256=sha256(pdf.read_bytes()).hexdigest(),**model.FLAGS)
    pdf.with_suffix('.receipt.json').write_text(json.dumps(receipt))
    with pytest.raises(ValueError,match='book sources'):
        book.primary_book(pdf,check=True,**options)
    assert not calls
    receipt['source_sha256']={'input.md':'a'*64}
    pdf.with_suffix('.receipt.json').write_text(json.dumps(receipt))
    with pytest.raises(ValueError,match='qualification still required'):
        book.primary_book(pdf,check=True,**options)
    assert calls==[True]
