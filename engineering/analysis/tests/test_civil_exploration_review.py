"""Compact retained evidence must match quantities and keep acceptance gaps."""
import pytest

from engineering.civil_exploration.contracts import load, sha, ROOT
from engineering.civil_exploration.model import takeoff


def test_retained_review_has_complete_equal_scope_and_no_release_claim():
    report = load(ROOT/'engineering/civil_exploration/examples/first-campaign.json')
    study = report['study']
    assert report['physical_release'] is False and report['operating_release'] is False
    assert report['qualified_feasible_pareto_set'] == []
    assert report['reference_benchmarks']['passed'] is True
    assert report['generator_sha256'] == sha(ROOT/report['generator'])
    expected = {(c['name'], g['name']) for c in study['candidates'] for g in study['ground_scenarios']}
    assert {(r['candidate_name'], r['ground_scenario']) for r in report['cases']} == expected
    for result in report['cases']:
        assert result['execution'] == 'completed'
        case = next(c for c in study['candidates'] if c['name'] == result['candidate_name'])
        candidate = dict(definition={k: case[k] for k in ('deck', 'pier')}, material=study['material'],
                         mass_allowances=study['mass_allowances'], foundation=study['foundation'])
        quantities = takeoff(candidate, study)
        for key in ('concrete_m3', 'installed_study_mass_kg', 'suspended_mass_kg', 'pile_length_m'):
            assert result['quantities'][key] == pytest.approx(quantities[key])
        assert result['quantities']['installed_cost_usd'] is None
        assert result['engineering_feasibility'] == 'unresolved'
        assert result['evidence_gaps']
    pi25 = next(c for c in report['cases'] if c['candidate_name'] == 'pi25-reference')
    assert next(r for r in pi25['research_limits'] if r['metric'] == 'suspended_mass_kg')['status'] == 'failed'
