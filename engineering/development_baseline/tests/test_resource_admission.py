"""Resource admission stops expensive CLI runs before evaluator dispatch."""
import importlib
import json

import pytest

from engineering import performance
from engineering.development_baseline import entrypoint


@pytest.mark.parametrize('arguments,action,module_name,callable_name', [
    (['design','journey-study','run'], 'journey-study-run',
     'engineering.design_search.conditional_journey_study', 'run'),
    (['design','generative','run'], 'generative-campaign',
     'engineering.design_search.generative_campaign', 'run'),
    (['design','adaptive','run'], 'adaptive-campaign',
     'engineering.design_search.adaptive_campaign', 'run'),
    (['design','architecture','run'], 'architecture-campaign',
     'engineering.design_search.railway_architecture', 'evaluate_campaign'),
    (['design','topology','run'], 'civil-topology-run',
     'engineering.design_search.civil_topology', 'run'),
    (['design','campaign','run','fixture'], 'candidate-campaign',
     'engineering.design_search.campaign', 'run'),
])
def test_campaign_cli_holds_before_dispatch_below_shared_reserve(
        tmp_path, monkeypatch, capsys, arguments, action, module_name, callable_name):
    admission = dict(schema='osr-performance-disk-admission/1', root=str(tmp_path),
        filesystem_free_bytes=1, minimum_free_reserve_bytes=20*1024**3,
        minimum_free_reserve_gib=20.0, admitted=False, execution='held',
        reason='below reserve', enforcement='shared reserve only')
    monkeypatch.setattr(performance, 'disk_admission', lambda root: admission)
    module = importlib.import_module(module_name)
    monkeypatch.setattr(module, callable_name,
        lambda *args, **kwargs: pytest.fail('resource-held campaign was dispatched'))

    assert entrypoint.main(arguments, root=tmp_path) == 3
    result = json.loads(capsys.readouterr().out)
    assert result['schema'] == 'osr-performance-disk-admission/1'
    assert result['execution'] == 'held'
    assert result['requested_action'] == action
    assert result['resource_admission']['admitted'] is False
    assert result['physical_accepted'] is False
