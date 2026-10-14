"""Independent exact fronts and adversarial objective/constraint regressions."""
from copy import deepcopy
import pytest
from engineering.design_engine.registry import get
from engineering.design_engine.optimization import dominates,frontier,paired


def charter():
    p=get('clipped-side-bay');p['variables']={'x':dict(kind='choice',unit='1',choices=[1,2,3,4])};return p


def evaluator(values,seed,arm,cached):
    if cached:return None
    x=values['x']
    return dict(id='candidate-'+str(x),variables=values,definition={},metrics=dict(defined_mass_kg=x,attachment_count=5-x),
        checks=dict(geometry=dict(state='passed')),evidence_state='unknown',installed_cost=None,physical_release=False)


def test_exact_known_front_and_equal_budget_random_controls_reproduce():
    result=paired(charter(),evaluator,seeds=[11,29],evaluations=4)
    assert result==paired(charter(),evaluator,seeds=[11,29],evaluations=4)
    assert result['oracle_calls']==4 and result['cache_hits']==12
    assert result['proposals']==16 and result['verified_frontier']==[]
    for trial in result['trials']:
        assert trial['equal_budget']and len(trial['optimiser'])==len(trial['random_control'])==4
        assert set(trial['conditional_screen_frontier'])=={'candidate-1','candidate-2','candidate-3','candidate-4'}
    assert all(c['installed_cost']is None for c in result['candidates'])


def test_low_mass_cannot_buy_away_a_failed_mandatory_constraint():
    def constrained(values,*args):
        row=evaluator(values,*args)
        if row and values['x']==1:row['checks']['geometry']['state']='failed'
        return row
    result=paired(charter(),constrained,seeds=[11,29],evaluations=4)
    assert all('candidate-1'not in t['conditional_screen_frontier']for t in result['trials'])
    assert any(c['id']=='candidate-1'for c in result['candidates'])


def test_absent_prices_and_nonfinite_objectives_are_not_rankable_zeros():
    for left,right in [([None],[0]),([float('nan')],[1]),([1],[1,2])]:
        with pytest.raises(ValueError):dominates(left,right)
    assert dominates([1,2],[2,3])


def test_single_selected_seed_is_not_an_improvement_campaign():
    with pytest.raises(ValueError):paired(charter(),evaluator,seeds=[11],evaluations=4)
