"""Completion gates cannot be closed by absent, stale or skipped checks."""
from copy import deepcopy
import pytest
from engineering.assembly_design import baseline, closure, families
from engineering.twin_workflow import core


def test_every_pdf_work_package_has_explicit_tasks_and_open_exit():
    plan=closure.plan()
    assert plan['pages']==19 and len(plan['packages'])==13 and len(plan['tasks'])==88
    assert {t['wp'] for t in plan['tasks']}=={p['id'] for p in plan['packages']}
    assert all(t['engineering_exit']=='open' and t['required_evidence'] for t in plan['tasks'])
    assert all(p['owner'] is None and p['independent_reviewer'] is None for p in plan['packages'])


@pytest.mark.parametrize('pilot',closure.PILOTS)
def test_completion_needs_every_characteristic_at_exact_revision(pilot):
    assert not closure.completion(pilot,'r1')['digital_specification_complete']
    records={g:{k:dict(revision='r1',receipt_verified=True,state='passed') for k in items}
             for g,items in closure.PILOTS[pilot].items()}
    result=closure.completion(pilot,'r1',records)
    assert result['digital_specification_complete'] and result['physical_records_complete']
    assert not any(result[k] for k in core.FLAGS)
    assert not closure.completion(pilot,'r2',records)['digital_specification_complete']
    for group in ('parts','interfaces','operations','analyses'):
        changed=deepcopy(records);first=next(iter(changed[group]))
        for state in ('failed','skipped','held','unknown'):
            changed[group][first]['state']=state
            assert not closure.completion(pilot,'r1',changed)['digital_specification_complete']
    records['analyses'][next(iter(records['analyses']))]['receipt_verified']=False
    assert not closure.completion(pilot,'r1',records)['research_shortlist_eligible']


def test_scope_snapshot_never_converts_implemented_code_to_accepted_design():
    prepared=baseline.build();snapshot=closure.snapshot(prepared)
    assert len(snapshot['tasks'])==88 and snapshot['engineering_closed_tasks']==0
    assert all(t['engineering_exit']=='open' for t in snapshot['tasks'])
    assert any(t['implementation']=='partial-provisional' for t in snapshot['tasks'])
    assert len(snapshot['requests'])==3 and all(not r['issued'] for r in snapshot['requests'])
    assert len(families.registry(prepared['policy']))==10


def test_pareto_never_wins_by_omitted_cost_relaxed_constraint_or_different_context():
    def row(id,**kw):return dict(id=id,context_revision='r1',mandatory_checks={'load':True},installed_mass_kg=10,cost=100,**kw)
    rows=[row('base'),dict(row('failed'),installed_mass_kg=1,cost=1,mandatory_checks={'load':False}),
        dict(row('held'),installed_mass_kg=1,cost=1,mandatory_checks={'load':None}),
        dict(row('empty'),mandatory_checks={}),dict(row('unpriced'),installed_mass_kg=1,cost=None),
        dict(row('other-context'),installed_mass_kg=1,cost=1,context_revision='r2')]
    result=families.pareto(rows)
    assert {r['candidate']['id'] for r in result}=={'base','unpriced','other-context'}
    assert next(r for r in result if r['candidate']['id']=='unpriced')['unpriced_objectives']==['largest_lift_kg','site_hours','cost']
    rows.append(dict(row('improved'),installed_mass_kg=9,cost=90))
    assert 'base' not in {r['candidate']['id'] for r in families.pareto(rows)}
    with pytest.raises(ValueError):families.pareto([dict(row('nan'),installed_mass_kg=float('nan'))])
