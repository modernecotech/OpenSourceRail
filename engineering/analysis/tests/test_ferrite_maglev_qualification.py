"""Closure coverage and importer negative controls; fixtures are not real tests."""
from copy import deepcopy
from hashlib import sha256
import json

import pytest

from engineering.ferrite_maglev import qualification as q, requirements


def sign(payload, role, identity=None):
    # Test-only trust callback; neither this key nor these records qualify hardware.
    return dict(role=role, identity=identity or role, payload_sha256=q.content_hash(payload), signature='test-only-unaccepted')


def test_authenticator(attestation, role):
    return attestation['signature'] == 'test-only-unaccepted' and attestation['role'] == role


test_authenticator.__test__ = False


def record_fixture(tmp_path, protocol_id='target-io-timing'):
    """Generate schema-shaped in-memory data solely for verifier unit tests."""
    current = q.study(); plan = q.load(); p = next(p for p in plan['protocols'] if p['id'] == protocol_id)
    bundle, raw = q.template(protocol_id)
    bundle['identity']['article_configuration_sha256'] = 'a' * 64
    bundle.update(article_serials=['TEST-ONLY-NOT-A-REAL-ARTICLE'], material_batches=['TEST-ONLY-NOT-A-REAL-BATCH'],
        started_at='2026-10-21T10:00:00Z', ended_at='2026-10-21T10:01:00Z', operator='unit-test-operator')
    raw['identity'] = deepcopy(bundle['identity'])
    raw['provenance'] = dict(kind=p['evidence_class'], operator=bundle['operator'],
        producer='test-only-fixture', synthetic=False, simulated=False)
    raw['samples'] = [dict(case_id=case, **{c['name']: float(i) if c['name'] == 'time_s' else 0. for c in p['channels']})
        for case in p['required_cases'] for i in range(2)]
    bundle['calibrations'] = []
    for c in p['channels']:
        value = dict(channel=c['name'], unit=c['unit'], instrument_serial='TEST-INSTRUMENT', certificate_sha256='b' * 64,
            expanded_uncertainty=0., coverage_factor=2., range_min=-100., range_max=100.,
            calibrated_at='2026-10-20T00:00:00Z', valid_until='2026-10-22T00:00:00Z')
        value['attestation'] = sign(value, 'calibration-authority'); bundle['calibrations'].append(value)
    bundle['limits'] = []
    for criterion in p['criteria']:
        value = dict(protocol_id=protocol_id, criterion_id=criterion['id'], statistic=criterion['statistic'],
            value=1. if criterion['comparison'] == 'le' else -1.,
            unit=criterion['unit'], comparison=criterion['comparison'], case_ids=list(p['required_cases']),
            binding_sha256=current['binding_sha256'], article_configuration_sha256='a' * 64,
            procedure_revision=p['revision'], uncertainty_policy='guard-band', derivation_record_sha256='c' * 64,
            approved_at='2026-10-20T00:00:00Z')
        value['attestation'] = sign(value, 'limit-approver'); bundle['limits'].append(value)
    for pid in ['procedure-and-hazards', 'article-and-material-revisions', 'earlier-gates-and-ncrs', 'safe-restraint-and-rescue']:
        value = dict(id=pid, protocol_id=protocol_id, binding_sha256=current['binding_sha256'], article_configuration_sha256='a' * 64,
            record_sha256='d' * 64, state='passed')
        value['attestation'] = sign(value, 'independent-assessor'); bundle['prerequisite_dispositions'].append(value)
    write_raw(tmp_path, bundle, raw)
    return bundle, raw


def write_raw(root, bundle, raw):
    data = q.encoded(raw); (root / 'measurements.json').write_bytes(data)
    bundle['raw_file'] = dict(name='measurements.json', sha256=sha256(data).hexdigest(), bytes=len(data))
    claim = dict(identity=bundle['identity'], raw_file=bundle['raw_file'],
        article_serials=bundle['article_serials'], material_batches=bundle['material_batches'],
        started_at=bundle['started_at'], ended_at=bundle['ended_at'], operator=bundle['operator'])
    bundle['raw_attestation'] = sign(claim, 'record-producer')
    bundle['witness_attestation'] = sign(claim, 'independent-witness')


def assess(root, bundle, protocol='target-io-timing', auth=test_authenticator):
    return q.assess_evidence(protocol, bundle, root, authenticator=auth)


def resign(record, role):
    record['attestation'] = sign({k: v for k, v in record.items() if k != 'attestation'}, role)


def test_every_exact_requirement_system_group_and_gate_has_acyclic_unaccepted_work():
    current = q.study(); register = requirements.register()
    assert current['coverage']['applicable_requirements'] == len(register['requirements']) == 179
    assert current['coverage']['supplied_specification_requirements'] == 100
    assert current['coverage']['obligation_groups'] == 8
    assert current['coverage']['gates'] == 6
    assert current['coverage']['accepted_requirements'] == current['coverage']['accepted_physical_gates'] == 0
    assert {r['requirement_id'] for r in current['requirements']} == {r['id'] for r in register['requirements']}
    lookup = {t['id']: t for t in current['tasks']}; done = set()
    for tid in current['topological_task_order']:
        task = lookup[tid]; assert set(task['prerequisites']) <= done
        assert not task['accepted'] and task['deliverable'] and task['pass_rule'] and task['hold_rule'] and task['fail_rule']
        done.add(tid)
    assert done == set(lookup)
    for r in current['requirements']:
        original = next(x for x in register['requirements'] if x['id'] == r['requirement_id'])
        assert r['requirement_sha256'] == q.content_hash(original)
        assert r['requirement_text'] == original['requirement']
        assert len(r['task_ids']) == 3 and r['protocol_ids'] and r['group_ids']
    assert all(current[k] is False for k in q.FLAGS)
    assert set(current['raw_data_schemas']) == {p['id'] for p in current['protocols']}


@pytest.mark.parametrize('change',['missing-requirement','wrong-sp-group','qualified-limit','missing-gate','duplicate-channel'])
def test_controlled_plan_rejects_missing_or_qualified_coverage(tmp_path, monkeypatch, change):
    plan = q.load()
    if change == 'missing-requirement':del plan['requirement_group_map']['SYS-001']
    if change == 'wrong-sp-group':plan['requirement_group_map']['SP-003'] = ['magnetic-circuit']
    if change == 'qualified-limit':plan['protocols'][0]['criteria'][0]['limit'] = 1.
    if change == 'missing-gate':plan['protocols'] = [p for p in plan['protocols'] if p['gate'] != 'G3']
    if change == 'duplicate-channel':plan['protocols'][0]['channels'].append(plan['protocols'][0]['channels'][0])
    path = tmp_path / 'plan.json'; path.write_text(json.dumps(plan)); monkeypatch.setattr(q, 'INPUT', path)
    with pytest.raises(ValueError):q.load()


def test_test_only_complete_records_never_issue_physical_or_manufacturing_release(tmp_path):
    bundle, raw = record_fixture(tmp_path)
    result = assess(tmp_path, bundle)
    assert result['state'] == 'passed-records' and result['evidence_ready_for_independent_decision']
    assert not result['accepted'] and all(result[k] is False for k in q.FLAGS)
    held = assess(tmp_path, bundle, auth=None)
    assert held['state'] == 'hold' and not held['evidence_ready_for_independent_decision']
    assert any('not authenticated' in hold for hold in held['holds'])


@pytest.mark.parametrize('kind',['executed-study','synthetic','unexecuted-template','supplier-record'])
def test_study_supplier_or_synthetic_data_cannot_impersonate_physical_rig(tmp_path, kind):
    bundle, raw = record_fixture(tmp_path); raw['provenance']['kind'] = kind; write_raw(tmp_path, bundle, raw)
    with pytest.raises(ValueError, match='impersonate'):assess(tmp_path, bundle)


@pytest.mark.parametrize('key',['synthetic','simulated'])
def test_explicit_synthetic_marker_rejected_even_with_physical_class_label(tmp_path, key):
    bundle, raw = record_fixture(tmp_path); raw['provenance'][key] = True; write_raw(tmp_path, bundle, raw)
    with pytest.raises(ValueError, match='impersonate'):assess(tmp_path, bundle)


@pytest.mark.parametrize('mutation',['revision','source','configuration','self-accept','raw-self-accept','units','nan','boolean','duplicate-time','outside-run','missing-channel','unknown-case'])
def test_exact_identity_finite_channels_units_and_time_are_enforced(tmp_path, mutation):
    bundle, raw = record_fixture(tmp_path)
    if mutation == 'revision':bundle['identity']['procedure_revision'] = 'old'
    if mutation == 'source':bundle['identity']['binding_sha256'] = '0' * 64
    if mutation == 'configuration':bundle['identity']['configuration_revision'] = 'old'
    if mutation == 'self-accept':bundle['accepted'] = True
    if mutation == 'raw-self-accept':raw['accepted'] = True
    if mutation == 'units':raw['units']['sensor_to_output_s'] = 'ms'
    if mutation == 'nan':raw['samples'][0]['sensor_to_output_s'] = float('nan')
    if mutation == 'boolean':raw['samples'][0]['sensor_to_output_s'] = False
    if mutation == 'duplicate-time':raw['samples'][1]['time_s'] = 0.
    if mutation == 'outside-run':raw['samples'][0]['time_s'] = 100.
    if mutation == 'missing-channel':del raw['samples'][0]['sensor_to_output_s']
    if mutation == 'unknown-case':raw['samples'][0]['case_id'] = 'unrequested'
    if mutation != 'nan':write_raw(tmp_path, bundle, raw)
    else:
        data = json.dumps(raw).encode(); (tmp_path / 'measurements.json').write_bytes(data)
        bundle['raw_file'].update(sha256=sha256(data).hexdigest(), bytes=len(data))
    with pytest.raises(ValueError):assess(tmp_path, bundle)


def test_checksum_path_symlink_and_size_receipts_are_enforced(tmp_path):
    bundle, raw = record_fixture(tmp_path)
    for name in ['../measurements.json','/etc/passwd','./measurements.json']:
        b = deepcopy(bundle); b['raw_file']['name'] = name
        with pytest.raises(ValueError):assess(tmp_path, b)
    b = deepcopy(bundle); b['raw_file']['sha256'] = '0' * 64
    with pytest.raises(ValueError, match='checksum'):assess(tmp_path, b)
    b = deepcopy(bundle); b['raw_file']['bytes'] += 1
    with pytest.raises(ValueError, match='bytes'):assess(tmp_path, b)
    (tmp_path / 'alias.json').symlink_to(tmp_path / 'measurements.json')
    b = deepcopy(bundle); b['raw_file']['name'] = 'alias.json'
    with pytest.raises(ValueError, match='links'):assess(tmp_path, b)


def test_missing_cases_calibration_and_late_or_fake_approval_remain_hold(tmp_path):
    bundle, raw = record_fixture(tmp_path)
    raw['samples'] = raw['samples'][2:]; write_raw(tmp_path, bundle, raw)
    assert assess(tmp_path, bundle)['state'] == 'hold'
    bundle, raw = record_fixture(tmp_path)
    bundle['calibrations'][0]['valid_until'] = '2026-10-21T10:00:01Z'
    resign(bundle['calibrations'][0], 'calibration-authority')
    assert assess(tmp_path, bundle)['state'] == 'hold'
    bundle, raw = record_fixture(tmp_path)
    bundle['limits'][0]['approved_at'] = '2026-10-21T10:00:01Z'; resign(bundle['limits'][0], 'limit-approver')
    assert assess(tmp_path, bundle)['state'] == 'hold'
    bundle, raw = record_fixture(tmp_path)
    bundle['limits'][0]['attestation']['signature'] = 'self-declared'
    assert assess(tmp_path, bundle)['state'] == 'hold'


def test_outside_calibrated_range_and_duplicate_json_cannot_hide_measurements(tmp_path):
    bundle, raw = record_fixture(tmp_path)
    cal = next(c for c in bundle['calibrations'] if c['channel'] == 'sensor_to_output_s')
    cal.update(range_min=-.01, range_max=.01); resign(cal, 'calibration-authority')
    raw['samples'][0]['sensor_to_output_s'] = .02; write_raw(tmp_path, bundle, raw)
    result = assess(tmp_path, bundle)
    assert result['state'] == 'hold' and any('outside calibrated' in h for h in result['holds'])
    with pytest.raises(ValueError, match='duplicate JSON'):
        q._json('{"force_n": 100000, "force_n": 0}')


def test_case_failure_cannot_be_hidden_by_later_case_or_by_uncertainty(tmp_path):
    bundle, raw = record_fixture(tmp_path, 'recovery-system')
    # Earlier case final value breaches limit; later case stays at zero.
    raw['samples'][1]['recovery_time_s'] = 1.2; write_raw(tmp_path, bundle, raw)
    result = assess(tmp_path, bundle, 'recovery-system')
    assert result['state'] == 'failed'
    criterion = next(c for c in result['metrics'] if c['criterion_id'] == 'recovery_time')
    assert not criterion['passed'] and not criterion['cases'][0]['passed']
    bundle, raw = record_fixture(tmp_path)
    raw['samples'][0]['sensor_to_output_s'] = .9; write_raw(tmp_path, bundle, raw)
    cal = next(c for c in bundle['calibrations'] if c['channel'] == 'sensor_to_output_s')
    cal['expanded_uncertainty'] = .2; resign(cal, 'calibration-authority')
    result = assess(tmp_path, bundle)
    assert result['state'] == 'failed' and not result['accepted']


def test_revoked_prerequisite_is_failure_and_same_operator_witness_is_hold(tmp_path):
    bundle, raw = record_fixture(tmp_path)
    value = bundle['prerequisite_dispositions'][0]; value['state'] = 'failed'; resign(value, 'independent-assessor')
    assert assess(tmp_path, bundle)['state'] == 'failed'
    bundle, raw = record_fixture(tmp_path)
    bundle['witness_attestation']['identity'] = bundle['operator']
    assert assess(tmp_path, bundle)['state'] == 'hold'


def test_limit_and_prerequisite_approvals_cannot_cross_protocols(tmp_path):
    bundle, raw = record_fixture(tmp_path)
    bundle['limits'][0]['protocol_id'] = 'another-protocol'; resign(bundle['limits'][0], 'limit-approver')
    with pytest.raises(ValueError, match='qualified limit schema'):assess(tmp_path, bundle)
    bundle, raw = record_fixture(tmp_path)
    bundle['prerequisite_dispositions'][0]['protocol_id'] = 'another-protocol'
    resign(bundle['prerequisite_dispositions'][0], 'independent-assessor')
    with pytest.raises(ValueError, match='prerequisite exact revision'):assess(tmp_path, bundle)


def test_packet_round_trip_source_and_presentation_tamper(tmp_path):
    output = tmp_path / 'qualification'; q.publish(output)
    assert q.read_summary(output)['accepted_requirements'] == 0
    assert q.read_summary(output)['protocols'] == 15
    (output / 'README.md').write_text('complete and accepted')
    with pytest.raises(ValueError, match='checksum'):q.verify(output)


def test_cli_has_no_self_approval_and_returns_hold_for_untrusted_import(tmp_path, capsys):
    bundle, raw = record_fixture(tmp_path)
    path = tmp_path / 'bundle.json'; path.write_text(json.dumps(bundle))
    out = tmp_path / 'assessment.json'
    code = q.main(['assess','--protocol','target-io-timing','--bundle',str(path),'--raw-root',str(tmp_path),'--output',str(out)])
    assert code == 2 and json.loads(out.read_text())['state'] == 'hold'
    assert not json.loads(capsys.readouterr().out)['accepted']
