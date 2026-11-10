"""Other output-producing engineering front doors honor disk admission."""
import json

import pytest

from engineering import performance


def _denied(root):
    return dict(schema='osr-performance-disk-admission/1', root=str(root),
        filesystem_free_bytes=1, minimum_free_reserve_bytes=20*1024**3,
        minimum_free_reserve_gib=20.0, admitted=False, execution='held',
        reason='below reserve', enforcement='shared reserve only')


@pytest.mark.parametrize('kind', ['parts', 'progress', 'backend', 'viaduct'])
def test_auxiliary_cli_holds_without_dispatch_or_output(tmp_path, monkeypatch, capsys, kind):
    monkeypatch.setattr(performance, 'disk_admission', lambda root: _denied(root))
    output = tmp_path/'result'

    if kind == 'parts':
        from engineering.vehicle_parts import __main__ as cli, catalogue
        monkeypatch.setattr(catalogue, 'build',
            lambda *args, **kwargs: pytest.fail('parts package was built below the reserve'))
        status = cli.main(['build', '--output', str(output)], root=tmp_path)
        action = 'vehicle-parts-build'
    elif kind == 'progress':
        from engineering.railway_progress import cli
        monkeypatch.setattr(cli.coordinator, 'run',
            lambda *args, **kwargs: pytest.fail('progress run dispatched below reserve'))
        status = cli.main(['run'], root=tmp_path)
        action = 'railway-progress-run'
    else:
        from engineering.design_search.craft_backends import __main__ as cli, pilot
        if kind == 'backend':
            monkeypatch.setattr(pilot, 'run',
                lambda *args, **kwargs: pytest.fail('backend run dispatched below reserve'))
            arguments = ['run', '--output', str(output)]
            action = 'backend-run'
        else:
            from engineering.design_search.craft_backends import viaduct_workflow
            monkeypatch.setattr(viaduct_workflow, 'run',
                lambda *args, **kwargs: pytest.fail('viaduct run dispatched below reserve'))
            arguments = ['viaduct', 'run', '--output', str(output)]
            action = 'backend-viaduct-run'
        status = cli.main(arguments, root=tmp_path)

    assert status == 3
    result = json.loads(capsys.readouterr().out)
    assert result['schema'] == 'osr-performance-disk-admission/1'
    assert result['execution'] == 'held'
    assert result['requested_action'] == action
    assert result['resource_admission']['admitted'] is False
    assert not output.exists()
