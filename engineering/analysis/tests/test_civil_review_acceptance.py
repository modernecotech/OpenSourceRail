"""Regression coverage for review holes, including rejected refined cases."""
from copy import deepcopy

import pytest

from engineering.civil_exploration import constraints, contracts, systems, workflow


def config():
    return contracts.load(contracts.HERE/'config/system-options.json')


def demands():
    return dict(relative_deflection=.001,settlement=.001,gross_elastic_stress=1.,
                pier_gross_elastic_stress=1.,pier_drift=.001,planning_axial_resistance=1.,max_lift_mass=1.)


@pytest.mark.parametrize('metric,value',[
    ('relative_deflection',.1),('settlement',.05),('pier_drift',.05),
    ('planning_axial_resistance',101.),('max_lift_mass',76000.),
    ('gross_elastic_stress',101.),('pier_gross_elastic_stress',101.),
])
def test_each_shared_limit_rejects_an_otherwise_converged_case(metric,value):
    c=config();limits={**c['research_constraints'],'gross_elastic_stress_pa':100.}
    d={**demands(),metric:value}
    violations=constraints.evaluate(d,limits,span_m=20.,pier_height_m=8.,axial_resistance_n=100.)
    assert [v['metric'] for v in violations]==[metric]
    assert violations[0]['ratio']>1.


@pytest.mark.parametrize('value',[None,float('nan'),float('inf'),-1.,True])
def test_unknown_or_invalid_demands_cannot_pass(value):
    with pytest.raises(ValueError,match='demand'):
        constraints.evaluate({**demands(),'pier_drift':value},config()['research_constraints'],span_m=20.,pier_height_m=8.,axial_resistance_n=100.)


def test_force_and_stress_nonconvergence_rejects_converged_displacement():
    result=constraints.convergence([dict(d=.1,f=100.,s=10.),dict(d=.101,f=130.,s=20.)],['d','f','s'])
    assert result['checks']['d']['passed']
    assert not result['checks']['f']['passed'] and not result['checks']['s']['passed']
    assert not result['passed']


def test_scheduler_change_invalidates_campaign_resume(tmp_path,monkeypatch):
    source='tools/automation/project_twin.py'
    assert source in contracts.dependencies()
    study=contracts.HERE/'config/reference.json';output=tmp_path/'campaign'
    workflow.prepare(study,output)
    real_sha=contracts.sha
    monkeypatch.setattr(contracts,'sha',lambda p:'0'*64 if p==contracts.ROOT/source else real_sha(p))
    with pytest.raises(ValueError,match='stale model/schema dependencies'):
        workflow.run_campaign(study,output,resume=True)


def row(identifier,span,violation=0.):
    return dict(package_id=identifier,status='completed',violation=violation,
                choice=dict(beam='U-girder',span_m=span),objectives=[1.,1.,1.],
                quantities={'installed_study_mass_kg':span},construction={'maximum_lift_mass_kg':span*10},
                scenarios={'s':dict(installed_cost_usd=span,whole_life_cost_usd=span*2,working_days=span)})


def test_longer_span_diagnostics_are_reserved_without_relaxing_limits():
    rows=[row(str(i),20.) for i in range(20)]+[row('25',25.),row('30-fail',30.,.2)]
    selected=systems.choose_shortlist(rows,['s'],6)
    assert {r['choice']['span_m'] for r in selected}=={20.,25.,30.}
    assert next(r for r in selected if r['package_id']=='30-fail')['violation']==.2
    assert '30-fail' not in systems.leaders(selected,'s')['pareto_ids']


def test_search_objectives_include_every_scenario_whole_life_and_lift():
    r=row('a',20.);r['scenarios']['second']={k:v*3 for k,v in r['scenarios']['s'].items()}
    values=systems.search_objectives(r,['s','second'])
    assert values==[20.,40.,20.,60.,120.,60.,20.,200.]


def test_search_benchmark_counts_cache_hits_and_reports_front_quality():
    a=row('a',20.);b=row('b',25.);a['objectives']=systems.search_objectives(a,['s']);b['objectives']=systems.search_objectives(b,['s'])
    summaries=[dict(seed=11,method='random')]
    events=[dict(seed=11,method='random',package_id='a',status='completed',elapsed_s=2.),
            dict(seed=11,method='random',package_id='a',status='verified-cache-hit',elapsed_s=.1)]
    systems.benchmark_search(summaries,events,{'a':a,'b':b},['s'])
    result=summaries[0]
    assert result['unique_packages']==1 and result['new_native_evaluations']==1
    assert result['evaluation_elapsed_s']==pytest.approx(2.1)
    assert result['normalized_additive_epsilon_to_pooled_front']==0.


def test_retained_native_freecad_receipt_covers_every_family_and_current_sources():
    receipt=contracts.load(contracts.HERE/'examples/native-cad-verification.json')
    c=config()
    expected={(role,r['id']) for role,key in [('beam','beams'),('pier','piers'),('foundation','foundations')] for r in c[key]}
    assert receipt['passed'] and receipt['kernel']=='FreeCAD Part/OpenCASCADE'
    assert {(r['role'],r['family']) for r in receipt['records']}==expected
    for r in receipt['records']:
        assert r['passed'] and r['native_solid_count']>0
        assert r['native_volume_m3']==pytest.approx(r['independent_volume_m3'],rel=1e-9)
    assert all(contracts.sha(contracts.ROOT/p)==h for p,h in receipt['source_sha256'].items())
    review=contracts.load(contracts.HERE/'examples/complete-system-review.json')
    assert receipt['inputs_report_sha256']==review['report_sha256']
    refined={r['package_id']:r for r in review['report']['refinements']}
    assert {r['package_id'] for r in receipt['shortlist']}==set(refined)
    for r in receipt['shortlist']:
        assert r['passed'] and r['native_solid_count']>0
        assert r['candidate_id']==refined[r['package_id']]['candidate_id']
        assert r['native_volume_m3']==pytest.approx(refined[r['package_id']]['cad_ifc_volume_m3'],rel=1e-9)
    assert not receipt['physical_release']


def test_retained_refined_failures_cannot_enter_winners_and_long_spans_are_covered():
    report=contracts.load(contracts.HERE/'examples/complete-system-review.json')['report']
    for span in (25.,30.):
        assert sum(r['span_m']==span for r in report['detailed_coverage'])>=2
    eligible={r['package_id'] for r in report['refinements'] if r['convergence_passed'] and r['refined_research_constraints_passed']}
    for refined in report['refinements']:
        assert refined['refined_research_constraints_passed']==(not refined['refined_research_violations'])
        assert refined['solid_convergence']['passed']
        assert all(case['convergence']['passed'] for case in refined['space_frame_checks'])
    for winners in report['winners'].values():
        assert set(winners['pareto_ids'])<=eligible
        assert all(winners[k] in eligible for k in ('cheapest','lightest','fastest','lowest_whole_life'))
    assert all(r['unique_packages']<=r['completed_evaluations'] and r['evaluation_elapsed_s']>0 for r in report['search_methods'])
