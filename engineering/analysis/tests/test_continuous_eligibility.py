"""A later exact-revision failure must invalidate selection and descendants."""
from copy import deepcopy
import json
import time

import pytest

from engineering.continuous_design import eligibility, evidence, ledger, planning, research, service, tasks, worker
from engineering.twin_workflow import core
from engineering.analysis.tests.test_continuous_planning import complete, real_children, FRAME


def confirmation(store,child,baseline,state):
    value=tasks.task(child['task']['kind'].replace('-detail','-confirmation'),dict(child=child['key']))
    key=tasks.identity(value,baseline)
    # observe() may already have nominated this exact confirmation recipe.
    with store.db:
        store.db.execute('DELETE FROM promotions WHERE child=?',(child['key'],))
        store.db.execute('DELETE FROM jobs WHERE key=?',(key,))
    result=dict(study_pass=state=='passed',checks=dict(native_exact_child_geometry=True if state=='passed' else False if state=='failed' else None),
        failed_checks=['native_exact_child_geometry'] if state=='failed' else [],
        verification=dict(evaluated_level='numerical_robustness',levels={
            level:dict(state=state if level=='native_geometry' else 'passed') for level in eligibility.MANDATORY}),**core.FLAGS)
    record=complete(store,value,baseline,result)
    with ledger.transaction(store.db):
        research.observe(store,key)
    return record


def test_native_failure_retracts_champion_and_all_descendants_without_editing_results(tmp_path):
    store=service.Store(tmp_path);baseline='a'*64;deps=real_children(store,baseline)
    for child in deps:
        with ledger.transaction(store.db):research.observe(store,child['key'])
    # This heavier alternative was dominated by the original frame.
    alternative=tasks.task('mechanical-detail',dict(context_id='metro-6car-planning',variables=dict(FRAME,side_depth_m=.9)))
    alt_result=deepcopy(store.result(store.db.execute('SELECT * FROM jobs WHERE key=?',(deps[0]['key'],)).fetchone()))
    alt_result['metrics']['mass_kg']+=100
    alt_result['assessment']['objectives']['mass_kg']+=100
    alt=complete(store,alternative,baseline,alt_result)
    with ledger.transaction(store.db):research.observe(store,alt['key'])
    integration=tasks.task('integration-coupling',dict(children=[d['key'] for d in deps]))
    result=worker.integration(dict(baseline_sha256=baseline,dependencies=deps))
    assert result['study_pass']
    old=complete(store,integration,baseline,evidence.label('integration-coupling',result))
    with ledger.transaction(store.db):research.observe(store,old['key'])
    original=(tmp_path/'sealed'/deps[0]['key']/'result.json').read_bytes()
    confirmation(store,deps[0],baseline,'failed')
    status=eligibility.Resolver(store,baseline)
    assert status.state(deps[0]['key'])['state']=='failed'
    assert status.state(old['key'])['state']=='failed'
    assert store.db.execute('SELECT state FROM integration_dispositions WHERE key=?',(old['key'],)).fetchone()[0]=='superseded'
    current=research.summary(store,baseline)
    assert deps[0]['key'] not in {c['key'] for c in current['champions']}
    assert alt['key'] in {c['key'] for c in current['champions']}
    assert current['counts']['integrated']==0 and current['counts']['adopted_for_research']==0
    # Replay a stale worker envelope after the later failure.
    assert not worker.integration(dict(baseline_sha256=baseline,dependencies=deps))['study_pass']
    with pytest.raises(ValueError,match='ineligible'):
        store.validate_children(integration,baseline)
    assert planning.integration_frontier(store,baseline)>0
    new=[json.loads(r['task']) for r in store.db.execute("SELECT task FROM jobs WHERE lane='integration' AND status!='completed'")]
    assert new and all(deps[0]['key'] not in v['parameters']['children'] for v in new)
    assert original==(tmp_path/'sealed'/deps[0]['key']/'result.json').read_bytes()
    assert store.result(store.db.execute('SELECT * FROM jobs WHERE key=?',(old['key'],)).fetchone())['study_pass']


@pytest.mark.parametrize('state',['hold','failed'])
def test_holds_are_distinct_from_deterministic_failure_and_revision_specific(tmp_path,state):
    store=service.Store(tmp_path);baseline='a'*64;deps=real_children(store,baseline)
    for dep in deps:
        with ledger.transaction(store.db):research.observe(store,dep['key'])
    confirmation(store,deps[0],baseline,state)
    status=eligibility.Resolver(store,baseline)
    assert status.state(deps[0]['key'])['state']==state
    assert status.state(deps[1]['key'])['eligible']
    assert not status.dependencies([d['key'] for d in deps])['eligible']
    assert eligibility.Resolver(store,'b'*64).state(deps[0]['key'])['state']=='hold'


def test_interrupted_confirmation_holds_and_successful_retry_releases_only_research_hold(tmp_path):
    store=service.Store(tmp_path);baseline='a'*64;deps=real_children(store,baseline)
    with ledger.transaction(store.db):research.observe(store,deps[0]['key'])
    key=store.db.execute('SELECT task_key FROM promotions WHERE child=?',(deps[0]['key'],)).fetchone()[0]
    assert eligibility.Resolver(store,baseline).state(deps[0]['key'])['eligible']  # first pending nomination
    with store.db:store.db.execute("UPDATE jobs SET error='interrupted',status='queued' WHERE key=?",(key,))
    assert eligibility.Resolver(store,baseline).state(deps[0]['key'])['state']=='hold'
    confirmation(store,deps[0],baseline,'passed')
    status=eligibility.Resolver(store,baseline).state(deps[0]['key'])
    assert status['eligible'] and not status['analytical_only']


@pytest.mark.parametrize('busy',[False,True])
def test_final_best_candidate_bypasses_five_percent_threshold_when_context_is_idle(tmp_path,busy):
    store=service.Store(tmp_path);baseline='a'*64;deps=real_children(store,baseline)
    with ledger.transaction(store.db):research.observe(store,deps[0]['key'])
    # Four already-nominated recipes trigger the normal expenditure threshold.
    with store.db:
        store.db.execute("UPDATE jobs SET status='error' WHERE key IN (SELECT task_key FROM promotions)")
        for i in range(3):
            store.db.execute('INSERT INTO promotions VALUES(?,?,?,?,?,?)',(f'historical-{i}',baseline,'metro-6car-planning',f'finished-{i}','test',1))
    value=tasks.task('mechanical-detail',dict(context_id='metro-6car-planning',variables=dict(FRAME,crossbearer_pitch_m=1.2)))
    result=deepcopy(store.result(store.db.execute('SELECT * FROM jobs WHERE key=?',(deps[0]['key'],)).fetchone()))
    result['metrics']['mass_kg']*=.99;result['assessment']['objectives']['mass_kg']*=.99
    child=complete(store,value,baseline,result)
    with ledger.transaction(store.db):research.observe(store,child['key'])
    assert store.db.execute('SELECT 1 FROM promotions WHERE child=?',(child['key'],)).fetchone() is None
    if busy:
        store.enqueue(tasks.task('mechanical-detail',dict(context_id='metro-6car-planning',variables=dict(FRAME,side_depth_m=.9))),baseline)
        with store.db:assert research.confirm_final_candidates(store,baseline)==0
    with store.db:assert research.confirm_final_candidates(store,baseline,now=time.time()+(901 if busy else 0))==1
    assert store.db.execute('SELECT reason FROM promotions WHERE child=?',(child['key'],)).fetchone()[0].startswith('Final best')
    with store.db:assert research.confirm_final_candidates(store,baseline)==0


def test_changed_evidence_generates_fresh_integration_revision_instead_of_reusing_stale_job(tmp_path):
    store=service.Store(tmp_path);baseline='a'*64;deps=real_children(store,baseline)
    assert planning.integration_frontier(store,baseline)==1
    original=store.db.execute("SELECT * FROM jobs WHERE lane='integration'").fetchone()
    confirmation(store,deps[0],baseline,'passed')
    assert store.db.execute('SELECT state FROM integration_dispositions WHERE key=?',(original['key'],)).fetchone()[0]=='superseded'
    assert planning.integration_frontier(store,baseline)==1
    fresh=store.db.execute("SELECT * FROM jobs WHERE lane='integration' AND key!=?",(original['key'],)).fetchone()
    old_result=worker.integration(dict(task=json.loads(original['task']),baseline_sha256=baseline,dependencies=deps))
    assert not old_result['study_pass'] and old_result['evaluation_disposition']=='superseded'
    new_result=worker.integration(dict(task=json.loads(fresh['task']),baseline_sha256=baseline,dependencies=deps))
    assert new_result['study_pass'] and new_result['evaluation_disposition']=='current'


def test_completion_marks_descendants_before_outbox_projection(tmp_path):
    store=service.Store(tmp_path);baseline='a'*64;deps=real_children(store,baseline)
    assert store.integration_jobs(baseline)==1
    integration=store.db.execute("SELECT key FROM jobs WHERE lane='integration'").fetchone()[0]
    value=tasks.task('mechanical-confirmation',dict(child=deps[0]['key']))
    result=dict(study_pass=False,verification=dict(levels={level:dict(state='failed' if level=='native_geometry' else 'passed') for level in eligibility.MANDATORY}),**core.FLAGS)
    record=complete(store,value,baseline,result)
    ledger.complete_job(store,record['key'],record['receipt_sha256'],result)
    assert store.db.execute('SELECT state FROM integration_dispositions WHERE key=?',(integration,)).fetchone()[0]=='superseded'
    assert store.db.execute('SELECT 1 FROM observations WHERE key=?',(record['key'],)).fetchone() is None
    assert store.db.execute('SELECT state FROM outbox WHERE origin=?',('job:'+record['key'],)).fetchone()[0]=='pending'


@pytest.mark.parametrize('failure',[FileNotFoundError('FreeCAD absent'),TimeoutError('native execution interrupted')])
def test_unavailable_native_tool_holds_instead_of_rejecting_geometry(tmp_path,monkeypatch,failure):
    from engineering.continuous_design import confirmation as native_confirmation
    store=service.Store(tmp_path);baseline='a'*64;deps=real_children(store,baseline)
    child=worker.child_records(dict(baseline_sha256=baseline,dependencies=[deps[0]]))[0]
    def unavailable(*_):raise failure
    monkeypatch.setattr(native_confirmation,'native',unavailable)
    output=tmp_path/'held';output.mkdir()
    result=native_confirmation.evaluate({},output,[child])
    assert not result['study_pass'] and result['verification']['levels']['native_geometry']['state']=='hold'
    assert 'native_available' in result['held_checks']
    assert 'native_available' not in result['failed_checks']


def test_native_section_disagreement_and_geometry_derived_stiffness_have_negative_controls(tmp_path):
    from engineering.continuous_design import native_properties,beam_confirmation
    measured=dict(controls=dict(box_volume_m3=24.,box_centroid_z_m=1.5,box_inertia_yy_m5=50.),
        samples=[dict(group='test',station_m=1.,area_m2=2.,centroid_z_m=1.,inertia_vertical_bending_m4=3.)],
        parts_volume_m3=dict(steel=5.))
    spec=dict(kind='mechanical-detail',groups=[dict(name='test',expected=dict(area_m2=2.,centroid_z_m=1.,inertia_vertical_bending_m4=3.))],
        density_kg_m3=7850.,expected_mass_kg=39250.,modulus_pa=2e11)
    assert all(native_properties.compare(measured,spec)['checks'].values())
    changed=deepcopy(measured);changed['samples'][0]['inertia_vertical_bending_m4']*=1.1
    assert not all(native_properties.compare(changed,spec)['checks'].values())
    store=service.Store(tmp_path);deps=real_children(store,'a'*64)
    assessment=store.result(store.db.execute('SELECT * FROM jobs WHERE key=?',(deps[0]['key'],)).fetchone())['assessment']
    out=tmp_path/'wrong-ei';out.mkdir()
    result=beam_confirmation.confirm('mechanical-detail',assessment,out,native_ei=2*assessment['metrics']['load_case_responses'][0]['beam']['ei_n_m2'])
    assert any(not passed for key,passed in result['checks'].items() if key.endswith('/analytical-agreement'))
