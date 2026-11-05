"""Portfolio browsing preserves source, parent, evaluation and archive scope."""
from copy import deepcopy
from hashlib import sha256
import gzip
import http.client
import json
import threading

import pytest

from engineering.development_baseline import portfolio_view as view, selection, server
from engineering.station_rail import ROOT, retired_station_reference
from engineering.station_rail.common import encoded, identity


@pytest.fixture(scope='module')
def inputs():
    base = ROOT / 'docs/design-engine'
    body = json.loads((base/'breadth-first-shape-portfolio/result.json').read_bytes())
    civil = json.loads((base/'civil-shape-portfolio/result.json').read_bytes())
    mechanics = json.loads(gzip.decompress((base/'civil-shape-mechanics/result.json.gz').read_bytes()))
    return body, civil, mechanics, selection.load()


@pytest.fixture(scope='module')
def retired_reference():
    # Authenticate exact old bytes; no current evaluator is invoked or admitted.
    return retired_station_reference.verify(ROOT)


def seal(record, key):
    record[key] = identity({k: value for k, value in record.items() if k != key})


def test_all_candidates_and_separate_archive_memberships_remain_visible(inputs, retired_reference):
    result = view.project(*inputs, retired_reference=retired_reference)
    comparison = result['reference_comparison']
    assert comparison['reference_commit'] == retired_station_reference.COMMIT
    assert comparison['retention_id'] == retired_station_reference.EXPECTED_RECEIPT_ID
    assert comparison['reference_selection_id'] == inputs[2]['load_context']['selection_id']
    assert comparison['reference_vehicle_evaluation_id'] == inputs[2]['load_context']['vehicle_evaluation_id']
    assert comparison['active_selection_id'] == inputs[3]['selection_id']
    assert comparison['reference_selection_id'] != comparison['active_selection_id']
    assert comparison['active_installed_propulsion_selected'] is False
    assert all(result[key] is False for key in ('current_evaluator_admission', 'numerical_reexecuted'))
    assert all(p['selection_role'] == 'retired-reference-control-comparison' for p in result['portfolios'])
    body, civil = result['portfolios']
    assert (body['candidate_count'], body['quantity_retained_count'], body['mechanics_retained_count']) == (54, 18, None)
    assert (civil['candidate_count'], civil['quantity_retained_count'], civil['mechanics_retained_count']) == (18, 6, 18)
    assert all(row['model_deflection_upper_m'] is None and row['mechanics_evaluation_id'] is None for row in body['rows'])
    assert all(row['mechanics_retained'] is None for row in body['rows'])
    assert all('stage 1 incomplete' in row['structural_status'] and row['next_tasks'] for row in civil['rows'])
    assert any(not row['quantity_retained'] and row['mechanics_retained'] for row in civil['rows'])
    assert 'per car' in body['cost_scope'] and 'installed span' in civil['cost_scope']
    assert all(row['complete_installed_mass_kg'] is None for p in result['portfolios'] for row in p['rows'])
    assert result['numerical_jobs_dispatched'] == 0 and result['integrated_selection'] is None
    assert all(result[key] is False for key in view.FLAGS)
    assert body['assumptions']['production_basis']['shifts_per_day'] == 2
    assert body['assumptions']['civil_basis']['shifts_per_day'] == 2
    assert body['assumptions']['operations_scenarios']['shifts_per_day'] == [2, 2, 3]


@pytest.mark.parametrize('mutation', ['parent', 'load', 'same-candidate-other-quantity-evaluation', 'cross-candidate-case', 'promotion'])
def test_resealed_mixed_parent_load_and_evaluation_identities_are_rejected(inputs, mutation, retired_reference):
    body, civil, mechanics, baseline = deepcopy(inputs)
    if mutation == 'parent':
        mechanics['parent_portfolio_id'] = '0'*64
    elif mutation == 'load':
        mechanics['load_context']['vehicle_evaluation_id'] = '0'*64
        seal(mechanics['load_context'], 'context_id')
    elif mutation == 'promotion':
        mechanics['stage_1_complete'] = True
    else:
        case = mechanics['cases'][0]
        old_id = case['evaluation_id']
        if mutation == 'same-candidate-other-quantity-evaluation':
            case['quantity_evaluation_id'] = '0'*64
        else:
            case['candidate_id'] = next(row['candidate_id'] for row in civil['evaluations'] if row['candidate_id'] != case['candidate_id'])
        seal(case, 'evaluation_id')
        row = next(row for row in mechanics['evaluations'] if old_id in row['case_evaluation_ids'])
        row['case_evaluation_ids'] = [case['evaluation_id'] if key == old_id else key for key in row['case_evaluation_ids']]
        seal(row, 'evaluation_id')
    seal(mechanics, 'study_id')
    with pytest.raises(view.CurrentUnavailable):
        view.project(body, civil, mechanics, baseline, retired_reference=retired_reference)


def test_body_mass_and_cost_cannot_use_another_physical_candidate(inputs, retired_reference):
    body, civil, mechanics, baseline = deepcopy(inputs)
    body['evaluations'][0]['cost_estimate']['candidate_id'] = body['evaluations'][1]['candidate_id']
    seal(body, 'portfolio_id')
    with pytest.raises(view.CurrentUnavailable, match='Body cost or mass'):
        view.project(body, civil, mechanics, baseline, retired_reference=retired_reference)


def test_resealed_archive_cannot_omit_candidates(inputs, retired_reference):
    body, civil, mechanics, baseline = deepcopy(inputs)
    body['archive']['cells'][0]['candidate_ids'].pop()
    seal(body['archive'], 'archive_id')
    seal(body, 'portfolio_id')
    with pytest.raises(view.CurrentUnavailable, match='archive candidate coverage'):
        view.project(body, civil, mechanics, baseline, retired_reference=retired_reference)


def test_current_http_endpoint_refuses_changed_bound_payload(tmp_path, monkeypatch, inputs, retired_reference):
    # Load the sibling fixture explicitly: this also supports isolated tests
    # against an integration checkout's production package with importlib mode.
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location('osr_topology_view_fixture',
        Path(__file__).with_name('test_topology_portfolio_view.py'))
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    revision_spec = importlib.util.spec_from_file_location('osr_revision_view_fixture',
        Path(__file__).with_name('test_topology_revision_portfolio_view.py'))
    revision_fixture = importlib.util.module_from_spec(revision_spec)
    revision_spec.loader.exec_module(revision_fixture)
    baseline = inputs[3]
    historical, _ = view._retired_comparison_context(baseline, inputs[2]['load_context'], retired_reference)
    revision_record, topology_record, _, parent_manifest = revision_fixture.records(historical)
    # Synthetic HTTP payload fixture isolates transport/source checks from the
    # separately exercised real pinned-history verifier.
    monkeypatch.setattr(retired_station_reference, 'verify', lambda root: retired_reference)
    publication = dict(source_sha256={})
    payloads = dict(zip(['breadth-first-shape-portfolio/result.json', 'civil-shape-portfolio/result.json',
        'civil-shape-mechanics/result.json.gz', 'civil-topology/result.json', 'civil-topology/manifest.json', 'civil-topology-revisions/result.json'],
        [encoded(inputs[0]), encoded(inputs[1]), gzip.compress(encoded(inputs[2]),mtime=0), encoded(topology_record), encoded(parent_manifest), encoded(revision_record)]))
    for name, raw in payloads.items():
        relative = 'docs/design-engine/' + name
        target = tmp_path/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        publication['source_sha256'][relative] = sha256(raw).hexdigest()
    reads = []
    def checked_packet(root):
        reads.append(root)
        return {}, publication
    monkeypatch.setattr(server, 'read_packet', checked_packet)
    monkeypatch.setattr(server, 'selected', lambda root: baseline)
    httpd = server.make_server(root=tmp_path, port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    def request():
        client = http.client.HTTPConnection('127.0.0.1', httpd.server_port)
        client.request('GET', '/api/portfolios/current')
        response = client.getresponse()
        status, value = response.status, json.loads(response.read())
        client.close()
        return status, value
    try:
        status, value = request()
        assert status == 200 and len(value['portfolios']) == 4
        assert value['numerical_jobs_dispatched'] == 0
        assert value['portfolios'][2]['key'] == 'topology'
        assert value['portfolios'][3]['key'] == 'topology-revisions'
        (tmp_path/'docs/design-engine/civil-shape-mechanics/result.json.gz').write_bytes(b'changed')
        status, value = request()
        assert status == 503 and 'current source binding' in value['reason']
        assert len(reads) == 2
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)


def test_retired_evaluation_cannot_implicitly_replace_current_context(inputs):
    with pytest.raises(view.CurrentUnavailable, match='selected load identity'):
        view.project(*inputs)


@pytest.mark.parametrize('mutation', ['body', 'component', 'commit', 'receipt', 'admission', 'execution'])
def test_retired_comparison_rejects_mixed_reference_or_promoted_evidence(inputs, retired_reference, mutation):
    body, civil, mechanics, baseline = deepcopy(inputs)
    proof = deepcopy(retired_reference)
    if mutation == 'body':
        baseline['vehicle']['body_candidate_id'] = '0' * 64
    elif mutation == 'component':
        baseline['vehicle']['propulsion_component_id'] = '0' * 64
    elif mutation == 'commit':
        proof['reference_commit'] = '0' * 40
    elif mutation == 'receipt':
        proof['retention_id'] = '0' * 64
    else:
        proof['current_evaluator_admission' if mutation == 'admission' else 'numerical_reexecuted'] = True
    with pytest.raises(view.CurrentUnavailable, match='Retired portfolio reference'):
        view.project(body, civil, mechanics, baseline, retired_reference=proof)


def test_reader_refuses_retired_integrity_failure_before_payload_access(tmp_path, monkeypatch):
    def refused(root):
        raise retired_station_reference.RetiredReferenceHold('fixture corrupt source')
    monkeypatch.setattr(retired_station_reference, 'verify', refused)
    with pytest.raises(view.CurrentUnavailable, match='Retired portfolio source integrity hold'):
        view.read(tmp_path, {}, {})
    assert not list(tmp_path.iterdir())
