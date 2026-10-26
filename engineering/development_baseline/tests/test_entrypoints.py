"""Meaningful default/front-door regressions, with synthetic contract fixtures."""
from hashlib import sha256
import gzip
import json
from pathlib import Path
import subprocess
import sys
import threading
import urllib.error
import urllib.request

import pytest

from engineering.development_baseline import FLAGS, INPUT, OUTPUT, WORKBENCH
from engineering.development_baseline import entrypoint as cli
from engineering.development_baseline.server import make_server


def encoded(value):
    return (json.dumps(value, sort_keys=True) + '\n').encode()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded(value))


@pytest.fixture
def packet(tmp_path):
    import tomllib
    # A small synthetic source tests contract plumbing without granting any
    # real engineering acceptance or mutating the retained solver packages.
    template = Path(__file__).resolve().parents[3] / 'development-baseline.toml'
    if not template.is_file():
        template = Path(__file__).resolve().parents[2] / 'development-baseline.toml'
    raw = template.read_text()
    selection = tomllib.loads(raw)
    car = dict(candidate_id=selection['vehicle_candidate_id'],
               body_candidate_id=selection['body_candidate_id'],
               magnet_component_id=selection['magnet_component_id'],
               mass=dict(accounted_tare_kg_per_car=17356.683728076856), **FLAGS)
    source = dict(vehicle=car, whole_system_alternatives=dict(proposals=[dict(
        proposal_id=selection['network_proposal_id'], launch_speed_m_s=20.,
        maximum_station_spacing_m=None)]))
    data = tmp_path / selection['source_design']
    data.parent.mkdir(parents=True)
    data.write_bytes(gzip.compress(encoded(source)))
    source_manifest = tmp_path / selection['source_manifest']
    write_json(source_manifest, dict(files_sha256={data.name:sha256(data.read_bytes()).hexdigest()}))
    selector = tmp_path / INPUT
    selector.parent.mkdir(parents=True, exist_ok=True)
    selector.write_text(raw.replace(selection['source_manifest_sha256'], sha256(source_manifest.read_bytes()).hexdigest()))
    baseline = cli.selected(tmp_path)
    common = dict(selection_id=baseline['selection_id'], development_default=True,
                  **{k:car[k] for k in cli.IDS}, **FLAGS)
    summary = dict(schema='osr-current-design/1', **common,
                   mass=car['mass'], service=selection['service'],
                   gates=[dict(id='capture-energy', engineering_screen='fail', reason='Physical energy rating missing')])
    output = tmp_path / OUTPUT
    write_json(output/'summary.json', summary)
    (tmp_path/'source.txt').write_text('fixture source\n')
    manifest = dict(schema='osr-current-publication/1', **common,
                    files_sha256={'summary.json':sha256((output/'summary.json').read_bytes()).hexdigest()},
                    source_sha256={'source.txt':sha256((tmp_path/'source.txt').read_bytes()).hexdigest()})
    write_json(output/'manifest.json', manifest)
    return tmp_path, summary, manifest


def test_no_argument_status_uses_explicit_selected_default(packet, capsys):
    root, summary, _ = packet
    assert cli.main([], root=root) == 0
    value = json.loads(capsys.readouterr().out)
    assert value['candidate_id'] == summary['candidate_id']
    assert value['development_default'] is True
    assert value['service']['headway_s'] == 120
    assert value['service']['launch_speed_cap_m_s'] == 20
    assert value['service']['normal_capacity_pphpd_arithmetic'] == 8280
    assert value['vehicle']['standing_passengers_per_car'] == 0
    assert value['publication_state'] == 'current'
    assert all(value[key] is False for key in FLAGS)


def test_missing_current_packet_reports_hold_without_legacy(packet, capsys):
    root, _, _ = packet
    (root/OUTPUT/'manifest.json').unlink()
    assert cli.main(['design'], root=root) == 0
    value = json.loads(capsys.readouterr().out)
    assert value['publication_state'] == 'hold'
    assert value['service']['launch_speed_cap_m_s'] == 20
    assert 'run ./osr build' in value['hold_reason']


@pytest.mark.parametrize('mutation', ['source', 'summary', 'identity', 'acceptance', 'symlink'])
def test_mixed_or_modified_packets_are_rejected(packet, mutation):
    root, summary, manifest = packet
    if mutation == 'source':
        (root/'source.txt').write_text('changed')
    elif mutation == 'summary':
        (root/OUTPUT/'summary.json').write_text('{}')
    elif mutation == 'symlink':
        original = root/'source.txt'
        outside = root/'other.txt'
        outside.write_bytes(original.read_bytes())
        original.unlink(); original.symlink_to(outside)
    else:
        summary['candidate_id' if mutation == 'identity' else 'physical_accepted'] = 'a'*64 if mutation == 'identity' else True
        write_json(root/OUTPUT/'summary.json', summary)
        manifest['files_sha256']['summary.json'] = sha256((root/OUTPUT/'summary.json').read_bytes()).hexdigest()
        write_json(root/OUTPUT/'manifest.json', manifest)
    with pytest.raises((cli.CurrentUnavailable, ValueError)):
        cli.read_packet(root)


def test_unsupported_current_journey_holds_with_selected_ids(packet, capsys):
    root, summary, _ = packet
    assert cli.main(['trip', 'run', '2km'], root=root) == 3
    value = json.loads(capsys.readouterr().out)
    assert value['execution'] == 'held'
    assert value['candidate_id'] == summary['candidate_id']
    assert value['physical_accepted'] is False


def test_server_is_read_only_and_refuses_tampering(packet):
    root, summary, _ = packet
    server = make_server(root=root, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = 'http://127.0.0.1:'+str(server.server_address[1])
    try:
        with urllib.request.urlopen(base+'/api/default-design') as response:
            value = json.load(response)
        assert value['candidate_id'] == summary['candidate_id']
        assert value['publication_state'] == 'current'
        for path, method, status in [('/api/default-design', 'POST', 405), ('/api/hardware', 'GET', 410), ('/.git/config', 'GET', 404), ('/docs/%2e%2e/%2e%2e/etc/passwd', 'GET', 404)]:
            with pytest.raises(urllib.error.HTTPError) as caught:
                urllib.request.urlopen(urllib.request.Request(base+path, method=method))
            assert caught.value.code == status
        (root/'source.txt').write_text('changed after initial API read')
        with pytest.raises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(base+'/api/default-design')
        assert caught.value.code == 503
        assert 'source changed' in json.load(caught.value)['reason']
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)


def test_actual_module_cli_defaults_to_new_design(packet):
    root, summary, _ = packet
    result = subprocess.run([sys.executable, '-m', 'engineering.development_baseline.entrypoint', '--root', str(root)], check=True, capture_output=True, text=True)
    value = json.loads(result.stdout)
    assert value['candidate_id'] == summary['candidate_id']
    assert value['publication_state'] == 'current'
    assert value['service']['normal_capacity_pphpd_arithmetic'] == 8280


def test_twin_entrypoint_exposes_only_verified_selected_exports(packet, capsys, monkeypatch):
    from types import SimpleNamespace
    root, summary, _ = packet
    folder = root / OUTPUT / 'exports'
    folder.mkdir()
    (folder/'civil.json').write_text('{"fixture":true}\n')
    manifest = {key:summary[key] for key in ('selection_id', *cli.IDS)}
    manifest.update(files_sha256={'civil.json':sha256((folder/'civil.json').read_bytes()).hexdigest()}, **FLAGS)
    write_json(folder/'manifest.json', manifest)
    calls=[]
    def verified(**kwargs):
        calls.append(kwargs)
        return {'current':True}
    monkeypatch.setattr(cli, '_module', lambda name: SimpleNamespace(verify=verified) if name=='publication' else None)
    assert cli.main(['twin', 'compile'], root=root)==0
    result=json.loads(capsys.readouterr().out)
    assert result['execution']=='verified-published-export'
    assert result['candidate_id']==summary['candidate_id']
    assert result['artifacts']==[OUTPUT+'/exports/civil.json']
    assert len(calls)==1
    assert cli.main(['twin','compile','a'*64],root=root)==3
    assert json.loads(capsys.readouterr().out)['execution']=='held'
    assert len(calls)==1


def test_city_endpoint_rejects_manifest_rewritten_outside_bound_catalogue(packet, monkeypatch):
    from functools import partial
    from types import SimpleNamespace
    from http.server import ThreadingHTTPServer
    from engineering.development_baseline import server as web
    from engineering import development_baseline
    root, summary, manifest = packet
    relative='cities/catalogue/region/country/baghdad/engineering/current/summary.json'
    folder=(root/relative).parent
    city={key:summary[key] for key in ('selection_id',*cli.IDS,'development_default',*FLAGS)}
    city['totals']={'total_trainsets':906}
    write_json(root/relative,city)
    city_manifest=dict(city,files_sha256={'summary.json':sha256((root/relative).read_bytes()).hexdigest()},source_sha256={})
    write_json(folder/'manifest.json',city_manifest)
    receipt={key:summary[key] for key in ('selection_id',*cli.IDS,'development_default',*FLAGS)}
    receipt['files_sha256']={(folder/'manifest.json').relative_to(root).as_posix():sha256((folder/'manifest.json').read_bytes()).hexdigest()}
    write_json(root/OUTPUT/'city-catalogue-manifest.json',receipt)
    manifest['files_sha256']['city-catalogue-manifest.json']=sha256((root/OUTPUT/'city-catalogue-manifest.json').read_bytes()).hexdigest()
    write_json(root/OUTPUT/'manifest.json',manifest)
    monkeypatch.setattr(development_baseline,'cities',SimpleNamespace(catalogue=lambda **kwargs:[{'slug':'baghdad','summary_path':relative}]),raising=False)
    class Quiet(web.Handler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,root=root))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    endpoint='http://127.0.0.1:'+str(server.server_address[1])+'/api/city/baghdad'
    try:
        with urllib.request.urlopen(endpoint) as response:
            assert json.load(response)['totals']['total_trainsets']==906
        # Alter both city output and its local receipt. Only the protected
        # catalogue binding distinguishes this from a genuine regeneration.
        city['totals']['total_trainsets']=1
        write_json(root/relative,city)
        city_manifest['files_sha256']['summary.json']=sha256((root/relative).read_bytes()).hexdigest()
        write_json(folder/'manifest.json',city_manifest)
        with pytest.raises(urllib.error.HTTPError) as caught:urllib.request.urlopen(endpoint)
        assert caught.value.code==503
        assert 'bound catalogue' in json.load(caught.value)['reason']
    finally:
        server.shutdown();server.server_close();thread.join(timeout=2)


@pytest.fixture
def reader_cache(packet):
    book=pytest.importorskip('engineering.development_baseline.book')
    root, summary, _=packet
    for name in ('README.md','docs/ROADMAP.md'):
        target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text('# Synthetic reader fixture\n')
    source=root/'engineering/development_baseline/book.py'
    source.parent.mkdir(parents=True,exist_ok=True);source.write_bytes(Path(book.__file__).read_bytes())
    write_json(root/OUTPUT/'cities.json',dict(summary,cities=[]))
    for name in ('vehicle-overview.svg','service-profile.svg','interface-section.svg'):
        (root/OUTPUT/name).write_text('<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"/>')
    pdf=root/'OpenSourceRail-Book.pdf'
    # Cache validation tests inspect an opaque digest, never fabricate a native
    # rendering or a physical acceptance result from these synthetic bytes.
    pdf.write_bytes(b'Synthetic cached-reader bytes, not a rendered PDF\n')
    receipt={key:summary[key] for key in ('selection_id',*cli.IDS,'development_default',*FLAGS)}
    receipt.update(schema='osr-current-reader/1',source_sha256=book._inputs(root),pdf_sha256=sha256(pdf.read_bytes()).hexdigest(),pages=1)
    receipt['receipt_id']=cli.selection.identity(receipt)
    write_json(root/book.RECEIPT,receipt)
    assert book.build(root=root,check=True)['cached'] is True
    return root,book,receipt


@pytest.mark.parametrize('field', ['candidate_id','body_candidate_id','magnet_component_id','development_default','physical_accepted','receipt_id'])
def test_reader_cache_refuses_forged_identity_or_disposition(reader_cache,field):
    root,book,receipt=reader_cache
    receipt[field]='0'*64 if field.endswith('_id') else not receipt[field]
    # A recomputed content hash must not legitimize the wrong physical identity
    # or grant a disposition. The receipt_id case separately tests raw tamper.
    if field!='receipt_id':receipt['receipt_id']=cli.selection.identity({k:v for k,v in receipt.items() if k!='receipt_id'})
    write_json(root/book.RECEIPT,receipt)
    with pytest.raises(ValueError,match='missing/stale'):
        book.build(root=root,check=True)


def test_reader_cannot_rebind_changed_current_payload_as_a_cached_publication(reader_cache):
    root,book,receipt=reader_cache
    summary=json.loads((root/OUTPUT/'summary.json').read_bytes())
    summary['gates'][0]['engineering_screen']='pass'
    write_json(root/OUTPUT/'summary.json',summary)
    # Even a newly self-consistent reader receipt cannot bypass the dossier's
    # authoritative payload binding and invent an improved engineering screen.
    receipt['source_sha256']=book._inputs(root)
    receipt['receipt_id']=cli.selection.identity({k:v for k,v in receipt.items() if k!='receipt_id'})
    write_json(root/book.RECEIPT,receipt)
    with pytest.raises(cli.CurrentUnavailable,match='modified'):
        book.build(root=root,check=True)
