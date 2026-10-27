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
def packet(tmp_path, monkeypatch):
    from engineering.development_baseline.selection import identity
    # This fixture exercises fail-closed front-door plumbing only. It grants no
    # engineering validity and supplies no historical magnetic component ID.
    selection = dict(schema='osr-development-baseline-selection/1', revision='V06-FIXTURE',
        family='wheel_rail_station_lim', source_brief='engineering/station_rail/brief.toml',
        network_proposal_id='e'*64,
        vehicle=dict(cars=6,body_length_m=17.,normal_passengers_per_car=46,
                     fixed_seats_per_car=44,wheelchair_places_per_car=2,
                     standing_passengers_per_car=0,passenger_doors_total_per_car=2),
        service=dict(headway_s=120.,dwell_s=35.,launch_speed_cap_m_s=20.,
                     normal_capacity_pphpd_arithmetic=8280.),acceptance=FLAGS)
    (tmp_path/INPUT).parent.mkdir(parents=True)
    (tmp_path/INPUT).write_text('family="wheel_rail_station_lim"\nsource_brief="engineering/station_rail/brief.toml"\n')
    source=tmp_path/selection['source_brief'];source.parent.mkdir(parents=True);source.write_text('version="0.6.0"\n')
    car=dict(candidate_id='a'*64,body_candidate_id='b'*64,support_component_id='c'*64,
             propulsion_component_id='d'*64,mass=dict(accounted_tare_kg_per_car=22000.),**FLAGS)
    baseline=dict(selection_id=identity(selection),selection=selection,vehicle=car,source_sha256={},**FLAGS)
    monkeypatch.setattr(cli.selection,'load',lambda root:baseline)
    write_json(tmp_path/'synthetic-baseline.json',baseline)
    common=dict(selection_id=baseline['selection_id'],development_default=True,
                **{k:car[k] for k in cli.IDS},**FLAGS)
    summary=dict(schema='osr-current-design/1',**common,mass=car['mass'],service=selection['service'],
                 gates=[dict(id='wheelrail-braking',engineering_screen='unknown',reason='Measured brake envelope missing')])
    output=tmp_path/OUTPUT;write_json(output/'summary.json',summary)
    (tmp_path/'source.txt').write_text('fixture source\n')
    manifest=dict(schema='osr-current-publication/1',**common,
        files_sha256={'summary.json':sha256((output/'summary.json').read_bytes()).hexdigest()},
        source_sha256={'source.txt':sha256((tmp_path/'source.txt').read_bytes()).hexdigest()})
    write_json(output/'manifest.json',manifest)
    return tmp_path,summary,manifest


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
        summary['candidate_id' if mutation == 'identity' else 'physical_accepted'] = '0'*64 if mutation == 'identity' else True
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


def test_actual_cli_process_preserves_explicit_selected_contract(packet):
    root,summary,_=packet
    # A fresh process independently checks the same CLI implementation against
    # this synthetic contract; real default selection is covered by browser CI.
    code=("import json; from pathlib import Path; from engineering.development_baseline import entrypoint as c; "
          "r=Path("+repr(str(root))+"); c.selection.load=lambda root:json.loads((r/'synthetic-baseline.json').read_text()); "
          "raise SystemExit(c.main([],root=r))")
    result=subprocess.run([sys.executable,'-c',code],check=True,capture_output=True,text=True)
    value=json.loads(result.stdout)
    assert value['candidate_id']==summary['candidate_id']
    assert value['publication_state']=='current'
    assert value['family']=='wheel_rail_station_lim'
    assert value['service']['normal_capacity_pphpd_arithmetic']==8280


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
    assert cli.main(['twin','compile','0'*64],root=root)==3
    assert json.loads(capsys.readouterr().out)['execution']=='held'
    assert len(calls)==1


def test_city_endpoint_returns_explicit_hold_without_reading_old_fleet(packet, monkeypatch):
    from types import SimpleNamespace
    from engineering import development_baseline
    root,summary,_=packet
    record=dict(execution='held',reason='v0.6 city performance regeneration is held',
                totals=None,performance_evaluated=False,geography=dict(map_available=True),
                **{key:summary[key] for key in ('selection_id',*cli.IDS,'development_default',*FLAGS)})
    monkeypatch.setattr(development_baseline,'cities',SimpleNamespace(
        catalogue=lambda **kwargs:[dict(slug='baghdad',execution='held',historical_summary_path='must-not-read.json')],
        evaluate_city=lambda *args,**kwargs:record),raising=False)
    server=make_server(root=root,port=0)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    endpoint='http://127.0.0.1:'+str(server.server_address[1])+'/api/city/baghdad'
    try:
        with pytest.raises(urllib.error.HTTPError) as caught:urllib.request.urlopen(endpoint)
        assert caught.value.code==503
        value=json.load(caught.value)
        assert value['execution']=='held'
        assert value['totals'] is None
        assert value['performance_evaluated'] is False
        assert value['candidate_id']==summary['candidate_id']
    finally:
        server.shutdown();server.server_close();thread.join(timeout=2)


def test_selection_cache_invalidates_physical_source_change(packet,monkeypatch):
    root,_,_=packet
    value=cli.selection.load(root);calls=[]
    def load(source):
        calls.append(str(source));return value
    monkeypatch.setattr(cli.selection,'load',load)
    cli.selected(root)
    count=len(calls)
    producer=root/'engineering/station_rail/vehicle.py';producer.write_text('# revised physical generator\n')
    cli.selected(root)
    assert len(calls)==count+1


@pytest.fixture
def reader_cache(packet):
    book=pytest.importorskip('engineering.development_baseline.book')
    reader=pytest.importorskip('engineering.station_rail.reader')
    root, summary, _=packet
    for name in ('README.md','docs/ROADMAP.md','docs/ARCHITECTURE.md','docs/first-adoptable-product.md',
                 'docs/open-source-rail-overview.md','deployment/erpnext/README.md','deployment/supervision/README.md'):
        target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text('# Synthetic reader fixture\n')
    source=root/'engineering/development_baseline/book.py'
    source.parent.mkdir(parents=True,exist_ok=True);source.write_bytes(Path(book.__file__).read_bytes())
    reader_source=root/'engineering/station_rail/reader.py'
    reader_source.parent.mkdir(parents=True,exist_ok=True);reader_source.write_bytes(Path(reader.__file__).read_bytes())
    artwork=json.loads((Path(reader.__file__).resolve().parents[2]/reader.ILLUSTRATIONS).read_bytes())
    write_json(root/reader.ILLUSTRATIONS,artwork)
    for image in artwork['illustrations']:
        (root/image['file']).write_bytes(b'Synthetic image cache fixture, not artwork\n')
    write_json(root/OUTPUT/'cities.json',dict(summary,cities=[]))
    write_json(root/OUTPUT/'comparison.json',dict(alternatives=[]))
    write_json(root/'docs/design-engine/v06-physical-closure/summary.json',dict(scope='Synthetic cache-integrity fixture; no solver evidence'))
    write_json(root/'docs/design-engine/v06-optimisation/summary.json',dict(scope='Synthetic campaign cache fixture; no solver evidence'))
    for name in ('summary.json','native-index.json'):
        write_json(root/'docs/design-engine/v06-architecture'/name,dict(scope='Synthetic architecture cache fixture; no solver evidence'))
    for name in ('summary.json','requirement-policy.json'):
        write_json(root/'docs/design-engine/v06-adaptive-design'/name,dict(scope='Synthetic adaptive cache fixture; no solver evidence'))
    write_json(root/'docs/design-engine/generative-structure/summary.json',dict(scope='Synthetic generative cache fixture; no solver evidence'))
    write_json(root/'docs/design-engine/coupled-railway/summary.json',dict(scope='Synthetic coupled cache fixture; no solver evidence'))
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


@pytest.mark.parametrize('field', ['candidate_id','body_candidate_id','support_component_id','propulsion_component_id','development_default','physical_accepted','receipt_id'])
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


@pytest.mark.parametrize('relative',[
    'docs/design-engine/v06-physical-closure/summary.json',
    'docs/design-engine/v06-architecture/summary.json',
    'docs/design-engine/v06-architecture/native-index.json',
    'docs/design-engine/v06-adaptive-design/summary.json',
    'docs/design-engine/v06-adaptive-design/requirement-policy.json',
    'docs/design-engine/coupled-railway/summary.json'])
def test_reader_cache_refuses_changed_native_followup(reader_cache,relative):
    root,book,_=reader_cache
    write_json(root/relative,dict(scope='Changed synthetic evidence'))
    with pytest.raises(ValueError,match='stale'):
        book.build(root=root,check=True)


@pytest.mark.parametrize('relative',[
    'docs/assets/v0.6/illustrations.json',
    'docs/assets/v0.6/elevated-station.png',
    'docs/assets/v0.6/accessible-interior.png',
    'docs/assets/v0.6/vehicle-assembly.png',
    'docs/assets/v0.6/precast-construction.png',
    'docs/assets/v0.6/station-lim-interface.png'])
def test_reader_cache_refuses_changed_illustrations(reader_cache,relative):
    root,book,_=reader_cache
    with (root/relative).open('ab') as handle:handle.write(b'\n')
    with pytest.raises(ValueError,match='stale'):
        book.build(root=root,check=True)


@pytest.mark.parametrize('endpoint,relative,schema',[
    ('campaigns','docs/design-engine/v06-optimisation/summary.json','osr-wheel-iterative-campaign-publication/1'),
    ('design-space','docs/design-engine/v06-design-space/summary.json','osr-expanded-design-space-summary/1'),
    ('architectures','docs/design-engine/v06-architecture/summary.json','osr-railway-architecture-summary/1'),
    ('adaptive','docs/design-engine/v06-adaptive-design/summary.json','osr-adaptive-design-summary/1'),
    ('generative','docs/design-engine/generative-structure/summary.json','osr-generative-structure-summary/1'),
    ('railway','docs/design-engine/coupled-railway/summary.json','osr-coupled-railway-summary/1')])
def test_campaign_api_requires_bound_research_bytes(packet,endpoint,relative,schema):
    root,_,manifest=packet
    value=dict(schema=schema,physical_accepted=False,engineering_accepted=False,configuration_adopted=False,manufacturing_release=False,operating_release=False)
    if endpoint in ('generative','railway'):value.update(integrated_selection=None,selected_reference_changed=False)
    write_json(root/relative,value)
    server=make_server(root=root,port=0);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    url='http://127.0.0.1:'+str(server.server_address[1])+'/api/'+endpoint+'/current'
    try:
        with pytest.raises(urllib.error.HTTPError) as caught:urllib.request.urlopen(url)
        assert caught.value.code==503
        manifest['source_sha256'][relative]=sha256((root/relative).read_bytes()).hexdigest();write_json(root/OUTPUT/'manifest.json',manifest)
        with urllib.request.urlopen(url) as response:assert json.load(response)['configuration_adopted'] is False
        value['physical_accepted']=True;write_json(root/relative,value)
        manifest['source_sha256'][relative]=sha256((root/relative).read_bytes()).hexdigest();write_json(root/OUTPUT/'manifest.json',manifest)
        with pytest.raises(urllib.error.HTTPError) as caught:urllib.request.urlopen(url)
        assert caught.value.code==503
    finally:server.shutdown();server.server_close();thread.join(timeout=2)


@pytest.mark.parametrize('action',['plan','run','publish','verify'])
def test_generative_cli_dispatches_explicit_research_contract_without_legacy(packet,monkeypatch,capsys,action):
    from types import ModuleType
    root,_,_=packet;calls=[]
    campaign=ModuleType('engineering.design_search.generative_campaign')
    publication=ModuleType('engineering.design_search.generative_publication')
    def spec():calls.append(('plan',None));return dict(schema='synthetic-plan',scope='Contract test only',physical_accepted=False)
    def run(*,root):
        calls.append(('run',root));return dict(campaign_id='7'*64,candidates=[dict(candidate_id='8'*64)],executed_rewrites=[dict(kind='synthetic-layout')],
            integrated_selection=None,selected_reference_changed=False,configuration_adopted=False,**FLAGS)
    def publish(*,root):calls.append(('publish',root));return dict(published=True,physical_accepted=False)
    def verify(*,root):calls.append(('verify',root));return dict(verified=True,physical_accepted=False)
    campaign.specification=spec;campaign.run=run;publication.build=publish;publication.verify=verify
    monkeypatch.setitem(sys.modules,campaign.__name__,campaign);monkeypatch.setitem(sys.modules,publication.__name__,publication)
    import engineering.design_search as package
    monkeypatch.setattr(package,'generative_campaign',campaign,raising=False);monkeypatch.setattr(package,'generative_publication',publication,raising=False)
    assert cli.main(['design','generative',action],root=root)==0
    result=json.loads(capsys.readouterr().out)
    assert calls==[(action,None if action=='plan' else root)] and result['physical_accepted'] is False
    if action=='run':
        assert result['candidate_count']==1 and result['rewrite_count']==1
        assert result['integrated_selection'] is None and result['selected_reference_changed'] is False


@pytest.mark.parametrize('claim',['selection','reference'])
def test_generative_api_refuses_source_bound_selection_claim(packet,claim):
    root,_,manifest=packet;relative='docs/design-engine/generative-structure/summary.json'
    value=dict(schema='osr-generative-structure-summary/1',physical_accepted=False,engineering_accepted=False,
        configuration_adopted=False,manufacturing_release=False,operating_release=False,
        integrated_selection='invented-winner' if claim=='selection' else None,selected_reference_changed=claim=='reference')
    write_json(root/relative,value);manifest['source_sha256'][relative]=sha256((root/relative).read_bytes()).hexdigest();write_json(root/OUTPUT/'manifest.json',manifest)
    server=make_server(root=root,port=0);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        with pytest.raises(urllib.error.HTTPError) as caught:urllib.request.urlopen('http://127.0.0.1:'+str(server.server_address[1])+'/api/generative/current')
        assert caught.value.code==503
    finally:server.shutdown();server.server_close();thread.join(timeout=2)


def test_generative_cli_does_not_mask_an_accepted_result_as_research(packet,monkeypatch,capsys):
    from types import ModuleType
    root,_,_=packet;campaign=ModuleType('engineering.design_search.generative_campaign');publication=ModuleType('engineering.design_search.generative_publication')
    campaign.run=lambda **kwargs:dict(campaign_id='7'*64,candidates=[],executed_rewrites=[],integrated_selection=None,
        selected_reference_changed=False,configuration_adopted=False,**{**FLAGS,'physical_accepted':True})
    monkeypatch.setitem(sys.modules,campaign.__name__,campaign);monkeypatch.setitem(sys.modules,publication.__name__,publication)
    import engineering.design_search as package
    monkeypatch.setattr(package,'generative_campaign',campaign,raising=False);monkeypatch.setattr(package,'generative_publication',publication,raising=False)
    assert cli.main(['design','generative','run'],root=root)==3
    result=json.loads(capsys.readouterr().out)
    assert result['execution']=='held' and 'cannot select or release' in result['reason']


@pytest.mark.parametrize('action',['plan','run','publish','verify'])
def test_coordinated_cli_routes_to_shared_research_engine_without_running_native_fixtures(packet,monkeypatch,capsys,action):
    from types import ModuleType
    import engineering.design_search as package
    root,_,_=packet;campaign=ModuleType('engineering.design_search.railway_campaign');publication=ModuleType('engineering.design_search.railway_publication');calls=[]
    campaign.EDGES=[['body','inventory']]
    campaign.specification=lambda root:dict(schema='synthetic-contract-plan',physical_accepted=False)
    def run(root,**kwargs):
        calls.append(kwargs);return dict(campaign_id='7'*64,contract_id='8'*64,bodies=[{}],rows=[{}],frontier=[],new_bundles=1,reused_bundles=0,
            integrated_selection=None,selected_reference_changed=False,configuration_adopted=False,**FLAGS)
    campaign.run=run;publication.build=lambda root:dict(published=True,physical_accepted=False);publication.verify=lambda root:dict(verified=True,physical_accepted=False)
    monkeypatch.setitem(sys.modules,campaign.__name__,campaign);monkeypatch.setitem(sys.modules,publication.__name__,publication)
    monkeypatch.setattr(package,'railway_campaign',campaign,raising=False);monkeypatch.setattr(package,'railway_publication',publication,raising=False)
    assert cli.main(['design','railway',action],root=root)==0
    value=json.loads(capsys.readouterr().out);assert value['physical_accepted'] is False
    if action=='run':assert calls==[dict(maximum_new_bundles=None,native_jobs=0)]
