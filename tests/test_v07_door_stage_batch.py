"""Small, portable checks for bounded stage intake reuse and drift refusal."""
from hashlib import sha256

import pytest

from tools.automation import v07_door_stage_intake as stage


IDS = ['1' * 64, '2' * 64]


def _fixture(tmp_path, monkeypatch, *, mutate=None):
    root = tmp_path / 'root'
    root.mkdir()
    source = root / 'controlled.txt'
    source.write_text('revision A')
    study_path = tmp_path / 'study.json'
    body_path = tmp_path / 'body.json'
    study_path.write_text('study bytes')
    body_path.write_text('body bytes')
    source_hash = sha256(source.read_bytes()).hexdigest()
    owner = {'source_sha256': {'controlled.txt': source_hash}}
    study = dict(owner, installed=dict(owner), civil=dict(owner))
    body = dict(owner)
    counts = {'study': 0, 'body': 0}

    def checked_study(path, checkout):
        assert path == study_path and checkout == root
        counts['study'] += 1
        stage._sources(study, root)
        return study, stage._sha(path)

    def checked_body(path, checked, checkout):
        assert path == body_path and checked is study and checkout == root
        counts['body'] += 1
        stage._sources(body, root)
        return body, stage._sha(path)

    def checked_intake(**kwargs):
        assert kwargs['_batch_common']['study'] is study
        assert kwargs['_batch_common']['body'] is body
        if mutate and kwargs['service_id'] == IDS[0]:
            mutate(study_path, body_path, source)
        return {'intake_id': kwargs['service_id'],
                'stages': [{'status': 'source-verified'} for _ in stage.STAGES]}

    monkeypatch.setattr(stage, '_study', checked_study)
    monkeypatch.setattr(stage, '_body', checked_body)
    monkeypatch.setattr(stage, '_intake', checked_intake)
    monkeypatch.setattr(stage.model, '_source_map', lambda *args: owner['source_sha256'])
    return root, study_path, body_path, counts


def test_batch_requires_distinct_explicit_bounded_ids():
    for ids in ([], IDS * 7, [IDS[0], IDS[0]], ['bad'], [None]):
        with pytest.raises(ValueError, match='distinct explicit'):
            stage.intake_many(study_path='unused', body_path='unused', service_ids=ids)


def test_batch_reuses_common_check_once_and_retains_distinct_reports(tmp_path, monkeypatch):
    root, study, body, counts = _fixture(tmp_path, monkeypatch)
    result = stage.intake_many(study_path=study, body_path=body,
                               service_ids=IDS, root=root)
    assert counts == {'study': 1, 'body': 1}
    assert [r['service_evaluation_id'] for r in result['reports']] == IDS
    assert len({r['report_id'] for r in result['reports']}) == len(IDS)
    assert [r['intake_report']['intake_id'] for r in result['reports']] == IDS
    assert all(r['report_id'] == stage.identity({k: v for k, v in r.items()
                                                 if k != 'report_id'}) for r in result['reports'])
    assert result['selected_service_id'] is None
    assert result['all_cost_stages_source_verified'] is True
    assert result['pack_ready'] is False
    assert result['physical_accepted'] is False


def test_batch_checks_each_explicit_service_and_cost_record(tmp_path, monkeypatch):
    root = tmp_path / 'root'
    root.mkdir()
    source = root / 'controlled.txt'
    source.write_text('revision A')
    source_map = {'controlled.txt': sha256(source.read_bytes()).hexdigest()}
    study_path = tmp_path / 'study.json'
    body_path = tmp_path / 'body.json'
    study_path.write_text('study bytes')
    body_path.write_text('body bytes')
    candidate = 'a' * 64
    records = []
    for active in (1, 2):
        service = dict(candidate_id=candidate, active_trainsets=active,
                       spare_trainsets=1, total_trainsets=active + 1)
        service['evaluation_id'] = stage.identity(service)
        records.append(dict(experiment='nominal', service=service,
                            request={'candidate_id': candidate},
                            result={'candidate_id': candidate}))
    study = dict(source_sha256=source_map, installed={'source_sha256': source_map},
                 civil={'source_sha256': source_map}, bundle={'candidate_id': candidate},
                 records=records)
    body = {'source_sha256': source_map}
    counts = {'study': 0, 'body': 0, 'cost': []}

    def study_check(path, checkout):
        counts['study'] += 1
        stage._sources(study, checkout)
        return study, stage._sha(path)

    def body_check(path, checked, checkout):
        counts['body'] += 1
        assert checked is study
        stage._sources(body, checkout)
        return body, stage._sha(path)

    def cost_check(checked, installed_body, service_id, checkout):
        counts['cost'].append(service_id)
        return next(r for r in records if r['service']['evaluation_id'] == service_id), source_map

    monkeypatch.setattr(stage, '_study', study_check)
    monkeypatch.setattr(stage, '_body', body_check)
    monkeypatch.setattr(stage.model, '_source_map', lambda *args: source_map)
    monkeypatch.setattr(stage.model, '_input_validation', cost_check)
    monkeypatch.setattr(stage.model, '_binding', lambda *args: {'candidate_id': candidate})
    ids = [r['service']['evaluation_id'] for r in records]
    result = stage.intake_many(study_path=study_path, body_path=body_path,
                               service_ids=ids, root=root)
    assert counts == {'study': 1, 'body': 1, 'cost': ids}
    assert [case['service_evaluation_id'] for case in result['reports']] == ids
    assert len({case['report_id'] for case in result['reports']}) == 2
    assert [case['intake_report']['stages'][3]['status']
            for case in result['reports']] == ['source-verified'] * 2
    assert all(case['intake_report']['stages'][4]['status'] == 'missing'
               for case in result['reports'])


@pytest.mark.parametrize('changed', ['study', 'body', 'source', 'source-symlink'])
def test_batch_refuses_common_input_or_source_drift(tmp_path, monkeypatch, changed):
    def mutate(study, body, source):
        if changed == 'study':
            study.write_text('changed study')
        elif changed == 'body':
            body.write_text('changed body')
        elif changed == 'source':
            source.write_text('revision B')
        else:
            source.rename(source.with_suffix('.saved'))
            source.symlink_to(source.with_suffix('.saved'))

    root, study, body, _ = _fixture(tmp_path, monkeypatch, mutate=mutate)
    with pytest.raises(ValueError, match='Batch input changed|Source bytes differ'):
        stage.intake_many(study_path=study, body_path=body,
                          service_ids=IDS, root=root)
