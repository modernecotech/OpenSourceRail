"""Same-input demonstrator demand and refusal controls."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from engineering.design_search.demonstrator_propulsion import evaluate, encoded, SELECTED

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'docs/design-engine/v07-demonstrator-propulsion'


@pytest.fixture(scope='module')
def packet():
    config = json.loads((BASE / 'input.json').read_bytes())
    result = evaluate(config, ROOT)
    assert encoded(result) == (BASE / 'comparison.json').read_bytes()
    return config, result


def test_common_service_and_distinct_research_configurations(packet):
    _, result = packet
    assert result['parent_selected_vehicle_candidate_id'] == SELECTED
    assert result['railway_selection_id'] is None
    assert len(result['rows']) == 18
    assert len({r['railway_research_configuration_id'] for r in result['rows']}) == 6
    assert all(r['physical_accepted'] is False and r['installed_capital_usd'] is None for r in result['rows'])
    assert all(r['numerical_validity'] == 'valid' and r['energy_residual_relative'] < 1e-6 for r in result['rows'])
    assert result['physical_accepted'] is False


def test_two_percent_grade_requires_more_than_station_only_under_model(packet):
    _, result = packet
    rows = {r['architecture']: r for r in result['rows'] if r['spacing_m'] == 2000 and r['grade_up_fraction'] == .02}
    assert rows['station-only']['analytical_target_reached'] is False
    assert rows['station-only']['final_position_m'] < 1500
    assert rows['station-plus-midroute-booster']['analytical_target_reached'] is True
    assert rows['powered-wheel-sustained']['analytical_target_reached'] is True
    assert rows['station-plus-midroute-booster']['declared_powered_window_m'] == 750
    assert rows['station-plus-midroute-booster']['installed_stator_or_conductor_length_m'] is None
    assert result['independent_brake']['pass_inherited_mu_hypothesis'] is False


def test_mixed_candidate_is_refused_and_missing_booster_changes_result(packet):
    config, _ = packet
    mixed=deepcopy(config);mixed['parent_selected_vehicle_candidate_id']='f'*64
    with pytest.raises(ValueError, match='Mixed selected vehicle'):
        evaluate(mixed, ROOT)
    hidden=deepcopy(config);hidden['architectures'][1]['powered_windows_m']['2000']=[]
    result=evaluate(hidden, ROOT)
    row=next(r for r in result['rows'] if r['architecture']=='station-plus-midroute-booster' and r['spacing_m']==2000 and r['grade_up_fraction']==.02)
    assert row['analytical_target_reached'] is False
