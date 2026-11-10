import json
from pathlib import Path

import pytest

from engineering import performance
from engineering.outline import __main__ as outline_cli
from engineering.outline import city_workflow, completion


def _denied_admission():
    return dict(schema='osr-performance-disk-admission/1',
        root='/test', filesystem_free_bytes=1,
        minimum_free_reserve_bytes=20*1024**3,
        minimum_free_reserve_gib=20.0, admitted=False, execution='held',
        reason='Free space is below the configured reserve',
        enforcement='Shared-filesystem reserve only')


@pytest.mark.parametrize('action,args,target', [
    ('city', ['city', '--output', 'OUT', '--city', 'samawah'], city_workflow),
    ('complete', ['complete', '--output', 'OUT', '--cities', 'samawah'], completion),
    ('run', ['run', '--output', 'OUT'], outline_cli.coordinator),
])
def test_new_outline_calculations_hold_before_writing_below_reserve(
        tmp_path, monkeypatch, capsys, action, args, target):
    output = tmp_path/'new-state'
    monkeypatch.setattr(performance, 'disk_admission', lambda root: _denied_admission())
    function = {'city': 'run', 'complete': 'run', 'run': 'run'}[action]

    def forbidden(*args, **kwargs):
        pytest.fail('calculation started below the disk reserve')

    monkeypatch.setattr(target, function, forbidden)
    argv = [str(output) if item == 'OUT' else item for item in args]
    assert outline_cli.main(argv, root=tmp_path) == 3
    result = json.loads(capsys.readouterr().out)
    assert result['schema'] == 'osr-performance-disk-admission/1'
    assert result['execution'] == 'held'
    assert result['requested_action'] == 'outline-'+action
    assert result['resource_admission']['admitted'] is False
    assert result['physical_accepted'] is False
    assert not output.exists()


def test_complete_cached_state_can_reuse_results_below_reserve(
        tmp_path, monkeypatch, capsys):
    output = tmp_path/'cached-state'
    (output/'cities'/'samawah').mkdir(parents=True)
    (output/'request.json').write_text(json.dumps({
        'schema': 'osr-outline-completion-request/1', 'cities': ['samawah']}))
    (output/'designs.json').write_text('{}')
    (output/'cities'/'samawah'/'result.json').write_text('{}')
    monkeypatch.setattr(performance, 'disk_admission',
        lambda root: pytest.fail('complete cached state should not dispatch a calculation'))
    called = {}

    def reuse(path, **kwargs):
        called.update(path=Path(path), **kwargs)
        return dict(manifest_id='a'*64)

    monkeypatch.setattr(completion, 'run', reuse)
    assert outline_cli.main(['complete', '--output', str(output), '--cities',
        'samawah', '--workers', '2'], root=tmp_path) is None
    assert called['path'] == output
    assert called['workers'] == 2
    assert json.loads(capsys.readouterr().out)['manifest_id'] == 'a'*64


def test_complete_cached_state_with_a_different_request_still_checks_reserve(
        tmp_path, monkeypatch, capsys):
    output = tmp_path/'cached-state'
    (output/'cities'/'samawah').mkdir(parents=True)
    (output/'request.json').write_text(json.dumps({
        'schema': 'osr-outline-completion-request/1', 'cities': ['samawah']}))
    (output/'designs.json').write_text('{}')
    (output/'cities'/'samawah'/'result.json').write_text('{}')
    monkeypatch.setattr(performance, 'disk_admission', lambda root: _denied_admission())
    monkeypatch.setattr(completion, 'run',
        lambda *args, **kwargs: pytest.fail('a mismatched request is not reusable'))
    assert outline_cli.main(['complete', '--output', str(output), '--cities',
        'baghdad', '--workers', '2'], root=tmp_path) == 3
    assert json.loads(capsys.readouterr().out)['execution'] == 'held'


def test_single_worker_cached_completion_still_checks_reserve(tmp_path, monkeypatch, capsys):
    output = tmp_path/'cached-state'
    (output/'cities'/'samawah').mkdir(parents=True)
    (output/'request.json').write_text(json.dumps({
        'schema': 'osr-outline-completion-request/1', 'cities': ['samawah']}))
    (output/'designs.json').write_text('{}')
    (output/'cities'/'samawah'/'result.json').write_text('{}')
    monkeypatch.setattr(performance, 'disk_admission', lambda root: _denied_admission())
    monkeypatch.setattr(completion, 'run',
        lambda *args, **kwargs: pytest.fail('single worker would initialize evidence cache'))
    assert outline_cli.main(['complete', '--output', str(output), '--cities',
        'samawah', '--workers', '1'], root=tmp_path) == 3
    assert json.loads(capsys.readouterr().out)['execution'] == 'held'
