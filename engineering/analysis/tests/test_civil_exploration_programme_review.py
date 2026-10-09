"""Retained programme proof must preserve budgets, failures and external gates."""
from engineering.civil_exploration.contracts import ROOT,load,sha


def test_retained_programme_keeps_document_acceptance_open():
    r=load(ROOT/'engineering/civil_exploration/examples/programme-review.json')
    assert {x['id'] for x in r['work_packages']}=={f'C{i:02d}' for i in range(1,15)}
    assert r['all_document_items_complete'] is False and r['physical_release'] is False
    assert r['generator_sha256']==sha(ROOT/r['generator'])
    assert all(x['evidence_hashes'] and x['remaining_acceptance'] for x in r['work_packages'])
    assert r['component_verification']['passed'] is True
    assert len(r['option_register']['families'])==8
    methods=r['search']['methods']
    for seed in {m['seed'] for m in methods}:
        pair=[m for m in methods if m['seed']==seed]
        assert {p['method'] for p in pair}=={'random','pareto-evolution'}
        assert len({p['completed_evaluations'] for p in pair})==1
    assert r['search']['qualified_feasible_pareto_set']==[]
    assert all(x['convergence_passed'] for x in r['detailed_confirmation'])
    assert r['retrieval']['integrity_verified'] is True
    assert r['promotion']['physical_release'] is False and r['promotion']['status'].startswith('blocked')
    assert all(p['observed_results'] is None for p in r['physical_test_programme']['tests'])
    assert all(p['installed_cost_usd'] is None for p in r['commercial'])
