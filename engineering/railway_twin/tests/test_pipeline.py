"""Adversarial end-to-end checks; resealed bytes do not establish semantics.

All runs use disposable directories and omit native solver/export execution.
Missing physical evidence must remain an explicit engineering-completion hold.
"""
from copy import deepcopy
from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import json
import shutil

import pytest

from engineering.station_rail.common import encoded, identity
from engineering.railway_twin import pipeline


def read_packet(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def write_packet(path, value):
    raw = encoded(value)
    Path(path).write_bytes(gzip.compress(raw, mtime=0) if str(path).endswith('.gz') else raw)


def copied_package(folder, tmp_path):
    target = tmp_path / 'tampered'
    shutil.copytree(folder, target)
    return target


def reseal_manifest(folder):
    """Refresh every payload hash and the manifest seal, but not engineering."""
    path = folder / 'manifest.json'
    manifest = read_packet(path)
    manifest['files_sha256'] = {
        p.relative_to(folder).as_posix(): sha256(p.read_bytes()).hexdigest()
        for p in sorted(folder.rglob('*')) if p.is_file() and p != path
    }
    manifest['evaluation_id'] = identity({k:v for k,v in manifest.items() if k != 'evaluation_id'})
    write_packet(path, manifest)


@pytest.fixture(scope='module')
def package(tmp_path_factory):
    folder = tmp_path_factory.mktemp('end-to-end') / 'package'
    result = pipeline.generate(family='gfrp_semimonocoque', distance_m=2000.,
                               output=folder, native=False)
    return folder, result


def test_passive_candidate_runs_end_to_end_without_inventing_completion(package):
    folder, result = package
    assert result['verified'] and result['software_consistent']
    assert result['family'] == 'gfrp_semimonocoque' and result['distance_m'] == 2000
    assert result['engineering_complete'] is False and result['physical_design_complete'] is False
    assert result['available_force_maps'] == result['physically_supported_journeys'] == 0
    assert result['integrated_selection'] is None
    assert result['native_execution'] == 'not-run'
    assert result['occurrences'] > 0 and result['unlocated_accounts'] > 0
    for flag in ('physical_accepted', 'engineering_accepted', 'configuration_adopted',
                 'manufacturing_release', 'operating_release', 'physical_journey_completed',
                 'selected_reference_changed'):
        assert result[flag] is False
    model = read_packet(folder / 'candidate.json.gz')
    assert model['bundle']['candidate_id'] == result['candidate_id']
    assert model['bundle']['architecture_case']['physical_definition']['onboard']['drive'] == 'none'
    assert read_packet(folder / 'controls.json')['onboard_traction'] is False
    mass = read_packet(folder / 'mass-properties.json')
    assert abs(mass['account_reconciliation_residual_kg']) < 1e-6
    assert mass['complete_installed_mass_kg'] is None and mass['unknown_mass_occurrences'] > 0
    ledger = read_packet(folder / 'ledger.json.gz')
    assert any(r['accounted_mass_kg'] is None for r in ledger['unlocated_accounts'])
    economics = read_packet(folder / 'economics.json.gz')
    assert economics['whole_life_cost_USD'] is economics['installed_CAPEX_USD'] is None


def test_strict_completion_fails_with_candidate_bound_actionable_blocker_ids(package):
    folder, summary = package
    with pytest.raises(pipeline.IncompleteDesign) as failure:
        pipeline.verify(folder, require_complete=True)
    blockers = failure.value.blockers
    ids = [r['id'] for r in blockers]
    assert len(ids) == len(set(ids))
    assert {'installed-equipment', 'moving-force-map', 'protected-journey',
            'civil-and-site', 'whole-life-economics', 'physical-qualification', 'native-geometry'} <= set(ids)
    assert all(r['candidate_id'] == summary['candidate_id'] and len(r['task_id']) == 64
               and r['completion_evidence_id'] is None for r in blockers)
    assert all(name in str(failure.value) for name in ids)


def test_repeated_and_cached_generation_reproduces_identical_content_identities(package, tmp_path):
    folder, original = package
    cached = pipeline.generate(family='gfrp_semimonocoque', distance_m=2000., output=folder, native=False)
    other = pipeline.generate(family='gfrp_semimonocoque', distance_m=2000., output=tmp_path / 'second', native=False)
    assert cached['cached'] is True and other['cached'] is False
    for key in ('candidate_id', 'body_candidate_id', 'evaluation_id', 'request_id'):
        assert original[key] == cached[key] == other[key]
    assert (folder / 'manifest.json').read_bytes() == (tmp_path / 'second' / 'manifest.json').read_bytes()


def test_equal_volume_scene_movement_rejected_after_payload_reseal(package, tmp_path):
    folder = copied_package(package[0], tmp_path)
    scene = read_packet(folder / 'scene.json.gz')
    original = deepcopy(scene['occurrences'][0])
    scene['occurrences'][0]['translation_m'][0] += 1.
    assert scene['occurrences'][0]['geometry']['volume_m3'] == original['geometry']['volume_m3']
    assert scene['occurrences'][0]['mass_kg'] == original['mass_kg']
    write_packet(folder / 'scene.json.gz', scene)
    reseal_manifest(folder)
    with pytest.raises(ValueError, match='semantic replay'):
        pipeline.verify(folder)


@pytest.mark.parametrize('artifact,mutate', [
    ('candidate.json.gz', lambda x:x['bundle'].update(candidate_id='a' * 64)),
    ('mass-properties.json', lambda x:x.update(complete_installed_mass_kg=0.)),
    ('controls.json', lambda x:x.update(physical_accepted=True)),
    ('physics.json.gz', lambda x:x['map_admission'].update(admitted=True, available_force_map_id='b' * 64)),
    ('economics.json.gz', lambda x:x.update(whole_life_cost_USD=0., economic_winner=x['candidate_id'])),
])
def test_resealed_semantic_forgeries_cannot_promote_or_mix_evidence(package, tmp_path, artifact, mutate):
    folder = copied_package(package[0], tmp_path)
    value = read_packet(folder / artifact)
    mutate(value)
    if 'evaluation_id' in value:
        value['evaluation_id'] = identity({k:v for k,v in value.items() if k != 'evaluation_id'})
    write_packet(folder / artifact, value)
    reseal_manifest(folder)
    with pytest.raises(ValueError, match='semantic replay'):
        pipeline.verify(folder)


def test_self_attested_legacy_map_cannot_enter_candidate_calculation(package):
    materialized = pipeline.model.materialize('gfrp_semimonocoque', 2000.)
    materialized['propulsion']['available_force_map'] = dict(
        schema='osr-station-available-force-map/1', evidence_kind='verified-numerical-operating-map',
        model_family='nonlinear-moving-LIM', execution='completed', numerical_validity='converged',
        model_domain='supported', review_record_id='a' * 64, interface_state_id='b' * 64,
        validation={name:'supported' for name in ('independent_benchmarks', 'mesh_time_convergence',
            'finite_overlap', 'zero_force_outside_windows', 'current_circuit_control',
            'thermal_duty', 'normal_force_interface')})
    materialized['propulsion']['materialization_id'] = identity({
        k:v for k,v in materialized['propulsion'].items() if k != 'materialization_id'})
    with pytest.raises(ValueError, match='materialization differs'):
        pipeline.calculate(materialized)


def test_source_epoch_change_invalidates_verification_and_cached_generation(package, monkeypatch):
    folder, _ = package
    current = deepcopy(read_packet(folder / 'manifest.json')['request']['source_sha256'])
    name = sorted(current)[0]
    current[name] = '0' * 64 if current[name] != '0' * 64 else '1' * 64
    monkeypatch.setattr(pipeline, 'sources', lambda root:deepcopy(current))
    with pytest.raises(ValueError, match='source epoch'):
        pipeline.verify(folder)
    with pytest.raises(ValueError, match='source epoch'):
        pipeline.generate(family='gfrp_semimonocoque', distance_m=2000., output=folder, native=False)


@pytest.mark.parametrize('change', ['missing', 'extra'])
def test_required_artifact_set_cannot_be_changed_by_resealing(package, tmp_path, change):
    folder = copied_package(package[0], tmp_path)
    if change == 'missing':
        (folder / 'controls.json').unlink()
    else:
        write_packet(folder / 'assumed-complete.json', {'physical_accepted':True})
    reseal_manifest(folder)
    with pytest.raises(ValueError, match='semantic replay|Unexpected or missing'):
        pipeline.verify(folder)


@pytest.mark.parametrize('change', ['executed', 'changed-request', 'nested-acceptance'])
def test_unrequested_native_evidence_cannot_be_forged_by_resealing(package, tmp_path, change):
    folder = copied_package(package[0], tmp_path)
    native = read_packet(folder / 'native-status.json')
    if change == 'executed':
        native['execution'] = 'completed'
    elif change == 'changed-request':
        native['requested'] = True
    else:
        native['IFC'] = {'physical_accepted':True, 'native_reopened':True}
    write_packet(folder / 'native-status.json', native)
    reseal_manifest(folder)
    with pytest.raises(ValueError, match='Native|native|acceptance'):
        pipeline.verify(folder)


def test_zero_budget_campaign_preserves_complete_disjoint_pending_matrix(tmp_path):
    state = tmp_path / 'campaign'
    first = pipeline.run(state=state, maximum_new_cases=0, native_jobs=0)
    repeated = pipeline.run(state=state, maximum_new_cases=0, native_jobs=0)
    assert first['new_cases'] == 0 and first['cases'] == first['failed'] == []
    actual = [(r['family'], r['distance_m']) for r in first['pending']]
    expected = {(family, distance) for family in ('gfrp_semimonocoque', 'aluminium_frame',
                                                'aluminium_stressed_skin') for distance in (1500., 2000.)}
    assert len(actual) == len(set(actual)) == 6 and set(actual) == expected
    assert repeated['campaign_id'] == first['campaign_id']
    assert read_packet(state / 'latest.json') == repeated


def test_failed_attempt_retains_inputs_and_pending_coverage_within_case_budget(tmp_path, monkeypatch):
    attempts = []
    def unavailable(root, *, family, distance_m, output, native):
        attempts.append((family, distance_m, native))
        Path(output).mkdir(parents=True)
        write_packet(Path(output) / 'controlled-input.json',
                     {'family':family, 'distance_m':distance_m, 'native':native})
        raise RuntimeError('controlled unavailable evaluator')
    monkeypatch.setattr(pipeline, 'generate', unavailable)
    state = tmp_path / 'campaign'
    result = pipeline.run(state=state, maximum_new_cases=1, native_jobs=0)
    assert len(attempts) == result['new_cases'] == len(result['failed']) == 1
    assert result['cases'] == [] and len(result['pending']) == 6
    requests = [identity(r) for r in result['pending']]
    assert len(set(requests)) == 6
    failure = result['failed'][0]
    assert identity(failure['request']) in requests
    assert failure['reason'] == 'controlled unavailable evaluator'
    assert read_packet(state / ('failure-' + identity(failure['request']) + '.json')) == failure
    retained = read_packet(state / failure['output'] / 'controlled-input.json')
    assert (retained['family'], retained['distance_m'], retained['native']) == attempts[0]


@pytest.mark.parametrize('change', ['native-budget', 'pending-contract', 'campaign-identity'])
def test_all_pending_publication_must_bind_exact_campaign_after_resealing(tmp_path, change):
    state, publication = tmp_path / 'campaign', tmp_path / 'publication'
    pipeline.run(state=state, maximum_new_cases=0, native_jobs=0)
    pipeline.publish(state=state, output=publication)
    valid = pipeline.verify_publication(output=publication)
    assert valid['verified'] and valid['cases'] == 0 and valid['pending'] == 6
    path = publication / 'manifest.json'
    manifest = read_packet(path)
    record = manifest['campaign_record']
    if change == 'native-budget':
        # Forge every dependent hash consistently: the actual budget obligation
        # still prohibits two native jobs in this bounded experiment.
        record['contract']['native_jobs'] = 2
        record['contract_id'] = identity(record['contract'])
        for request in record['pending']:
            request['contract_id'] = record['contract_id']
    elif change == 'pending-contract':
        record['pending'][0]['contract_id'] = 'f' * 64
    if change == 'campaign-identity':
        record['campaign_id'] = 'a' * 64
    else:
        record['campaign_id'] = identity({k:v for k,v in record.items()
                                          if k not in ('campaign_id', 'new_cases')})
    manifest['contract'] = deepcopy(record['contract'])
    manifest['pending'] = deepcopy(record['pending'])
    manifest['campaign_id'] = record['campaign_id']
    manifest['publication_id'] = identity({k:v for k,v in manifest.items() if k != 'publication_id'})
    write_packet(path, manifest)
    with pytest.raises(ValueError):
        pipeline.verify_publication(output=publication)


def test_genuine_package_validation_cannot_satisfy_another_native_request(package):
    folder, result = package
    physical_request = read_packet(folder / 'manifest.json')['request']
    contract = dict(specification=pipeline.specification(),
                    source_sha256=physical_request['source_sha256'], native_jobs=0)
    contract_id = identity(contract)
    requests = [dict(family=f, distance_m=d, native=False, contract_id=contract_id)
                for f in contract['specification']['body_families']
                for d in contract['specification']['distances_m']]
    case = next(r for r in requests if r['family'] == result['family'] and r['distance_m'] == result['distance_m'])
    validation = {k:v for k,v in result.items() if k not in ('cached', 'output')}
    value = dict(schema='osr-end-to-end-twin-campaign/1', contract=contract, contract_id=contract_id,
        cases=[dict(request=case, output='cases/' + identity(case), validation=validation)],
        pending=[r for r in requests if r != case], failed=[], new_cases=1,
        integrated_selection=None, **pipeline.FLAGS)
    value['campaign_id'] = identity({k:v for k,v in value.items() if k not in ('campaign_id', 'new_cases')})
    pipeline._check_campaign(value, pipeline.ROOT)  # Genuine matching native=False control.
    changed = deepcopy(value)
    changed['contract']['native_jobs'] = 1
    changed['contract_id'] = identity(changed['contract'])
    for request in [changed['cases'][0]['request']] + changed['pending']:
        request['contract_id'] = changed['contract_id']
        request['native'] = request['family'] == 'gfrp_semimonocoque' and request['distance_m'] == 2000.
    changed['cases'][0]['output'] = 'cases/' + identity(changed['cases'][0]['request'])
    changed['campaign_id'] = identity({k:v for k,v in changed.items() if k not in ('campaign_id', 'new_cases')})
    with pytest.raises(ValueError):
        pipeline._check_campaign(changed, pipeline.ROOT)


def test_federated_bom_covers_every_train_bank_and_civil_occurrence_once(package):
    folder, summary = package
    scene = read_packet(folder / 'scene.json.gz')
    ledger = read_packet(folder / 'ledger.json.gz')
    bom = read_packet(folder / 'federated-bom.json.gz')
    construction = read_packet(folder / 'construction.json')
    solids = {r['id']:r for r in scene['occurrences']}
    accounts = {r['id']:r for r in ledger['unlocated_accounts']}
    assert len(solids) == len(scene['occurrences'])
    assert len(accounts) == len(ledger['unlocated_accounts']) and not set(solids) & set(accounts)
    ids = [r['id'] for r in bom['engineering_BOM']]
    assert len(ids) == len(set(ids)) and set(ids) == set(solids) | set(accounts)
    assert all(r['candidate_id'] == summary['candidate_id'] for r in bom['engineering_BOM'])
    assert {int(name.split('/')[1]) for name in solids if name.startswith('car/')} == set(range(6))
    assert {int(name.split('/')[1]) for name in solids if name.startswith('bank/')} == set(range(5))
    assert len({name.split('/')[1] for name in solids if name.startswith('span/')}) == construction['spans']
    for row in bom['engineering_BOM']:
        if row['id'] in accounts:
            assert row['quantity'] is None and row['geometry_id'] is None
            assert row['accounted_mass_kg'] == accounts[row['id']]['accounted_mass_kg']
        else:
            assert row['quantity'] == 1
            assert row['accounted_mass_kg'] == solids[row['id']]['mass_kg']
            assert row['nominal_stock_volume_m3'] == solids[row['id']]['geometry']['volume_m3']
    groups = bom['manufacturing_BOM']
    coverage = Counter(name for group in groups for name in group['engineering_occurrence_ids'])
    assert coverage == Counter({name:1 for name in solids})
    for group in groups:
        assert group['known_gross_stock_mass_kg'] == pytest.approx(
            sum(solids[name]['mass_kg'] for name in group['engineering_occurrence_ids']))
        assert group['unit_price_USD'] is group['origin_country'] is None
    assert sum(g['known_gross_stock_mass_kg'] for g in groups) == pytest.approx(sum(r['mass_kg'] for r in solids.values()))
    group_ids = {g['group_id'] for g in groups}
    assert len(group_ids) == len(groups)
    assert Counter(r['manufacturing_group_id'] for r in bom['procurement']) == Counter({name:1 for name in group_ids})
    assert all(r['price_USD'] is r['lead_time_days'] is None and r['ready_for_order'] is False for r in bom['procurement'])
    procurement_ids = {r['id'] for r in bom['procurement']}
    assert all(len(r['predecessors']) == 1 and r['predecessors'][0] in procurement_ids
               for r in bom['manufacturing_operations'])
    assert bom['ERPNext']['posted'] is False and bom['ERPNext']['ready_for_import'] is False
    assert all(r['disabled'] == 1 and r['is_stock_item'] == 0 for r in bom['ERPNext']['items'])
    assert bom['complete_installed_BOM'] is False and bom['complete_installed_price_USD'] is None


@pytest.mark.parametrize('section', ['engineering_BOM', 'manufacturing_BOM'])
def test_federated_bom_removal_cannot_be_hidden_by_resealing(package, tmp_path, section):
    folder = copied_package(package[0], tmp_path)
    path = folder / 'federated-bom.json.gz'
    bom = read_packet(path)
    bom[section].pop()
    bom['evaluation_id'] = identity({k:v for k,v in bom.items() if k != 'evaluation_id'})
    write_packet(path, bom)
    reseal_manifest(folder)
    with pytest.raises(ValueError, match='semantic replay'):
        pipeline.verify(folder)
