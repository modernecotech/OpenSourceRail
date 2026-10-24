from copy import deepcopy
import math

import pytest

from engineering.design_search import contracts as c, coupling, families, registry, selection


def simple(unknown=False):
    item=dict(id='block',geometry_id='block',quantity=1,scope='vehicle-per-car',frame_id='vehicle',status='unknown' if unknown else 'known',
        unit_mass_kg=None if unknown else 12.,cg_m=[1.,0.,0.],inertia_kg_m2=[[2.,0.,0.],[0.,2.,0.],[0.,0.,2.]],basis='test exact cube')
    return c.make_candidate(requirement_revision='req1',architecture=dict(name='coupon'),
        frames=[dict(id='vehicle',parent_id=None,origin_m=[0.,0.,0.],rotation_matrix=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])],
        materials=[dict(id='test',density_kg_m3=12.,basis='declared test material')],
        geometry=[dict(id='block',kind='box',frame_id='vehicle',material_id='test',size_m=[1.,1.,1.],at_m=[.5,-.5,-.5])],
        interfaces=[],installed_inventory=[item])


def request(candidate,name='field',**kwargs):
    return c.make_evaluation_request(candidate,evaluator_id=name,evaluator_sources={'solver.py':'a'*64},purpose='next-experiment',**kwargs)


def result(candidate,name='field',screen='pass',**kwargs):
    return c.make_result(request(candidate,name,**kwargs),execution_status='executed',numerical_status='converged',screen_status=screen,
        maturity='coupled-numerical',metrics={'mass':12.,'violation':2. if screen=='fail' else 0.})


def test_physical_evaluation_and_context_identities_are_distinct():
    candidate=simple();first=request(candidate,hypothesis={'flux_allocation':'original'});second=request(candidate,hypothesis={'flux_allocation':'sensitivity'})
    assert first['candidate_id']==second['candidate_id']==candidate['candidate_id']
    assert first['evaluation_id']!=second['evaluation_id']
    context=c.bind_context(candidate,requirement_revision='req2',lineage={'parent_candidate_ids':['b'*64]})
    assert context['candidate_id']==candidate['candidate_id']
    assert request(context)['evaluation_id']!=request(candidate)['evaluation_id']


def test_registry_preserves_physical_and_multiple_context_records(tmp_path):
    store=registry.Registry(tmp_path);candidate=simple();other=c.bind_context(candidate,requirement_revision='req2')
    store.store('candidate',candidate);store.store('candidate',other)
    physical=store.read('candidate',candidate['candidate_id'])
    assert 'requirement_revision' not in physical
    assert c.bind_context(physical,requirement_revision='req2')['candidate_id']==candidate['candidate_id']
    assert store.read_context(c.identity(candidate))['requirement_revision']=='req1'
    assert store.read_context(c.identity(other))['requirement_revision']=='req2'
    execution=result(candidate);store.store('evaluation',execution);assert store.cached(execution['request'])==execution
    changed=deepcopy(execution);changed['metrics']['mass']=99.
    with pytest.raises(ValueError,match='payload digest'):c.validate_result(changed)
    changed['result_sha256']=c.identity({key:value for key,value in changed.items() if key!='result_sha256'})
    with pytest.raises(registry.IdentityCollision):store.store('evaluation',changed)


def test_mass_cg_inertia_and_unknown_stock_are_explicit():
    props=c.mass_properties(simple());assert props['total_mass_kg']==12.;assert props['cg_m']==[1.,0.,0.];assert props['inertia_kg_m2'][0][0]==2.
    unknown=c.mass_properties(simple(True));assert unknown['total_mass_kg'] is None;assert unknown['known_mass_subtotal_kg']==0.;assert unknown['unknown_stock_ids']==['block']


@pytest.mark.parametrize('matrix', [[[1.,2.,0.],[2.,1.,0.],[0.,0.,1.]],[[1.,0.,0.],[0.,1.,0.],[0.,0.,3.]]])
def test_impossible_inertias_are_rejected(matrix):
    candidate=simple();candidate['installed_inventory'][0]['inertia_kg_m2']=matrix
    candidate['candidate_id']=c.identity(dict(units=c.UNITS,**{key:candidate[key] for key in c.PHYSICAL_KEYS}))
    with pytest.raises(ValueError,match='PSD'):c.validate_candidate(candidate)


@pytest.mark.parametrize('path',['/etc/passwd','../solver.py','a/../b.py','a\\b.py'])
def test_evaluator_sources_are_repository_relative(path):
    with pytest.raises(ValueError):c.make_evaluation_request(simple(),evaluator_id='x',evaluator_sources={path:'a'*64})


def test_nonconvergence_and_unexecuted_results_cannot_pass():
    for execution,numerical in [('interrupted','unknown'),('running','unknown'),('executed','nonconverged')]:
        with pytest.raises(ValueError):c.make_result(request(simple()),execution_status=execution,numerical_status=numerical,screen_status='pass')


def test_coupling_converges_with_real_inventory_and_explicit_residuals():
    def update(candidate,state):return {'state':dict(mass_kg=12.,heat_w=10.,temperature_c=45.,deformation_m=.0001,gap_m=.0079)}
    value=coupling.iterate(simple(),update,max_iterations=40)
    assert value['coupling_status']=='converged';assert value['residual_history'];assert not value['physical_accepted']
    assert coupling.iterate(simple(),update,max_iterations=1)['coupling_status']=='nonconverged'
    assert coupling.iterate(simple(True),update)['coupling_status']=='unknown'
    def invented(candidate,state):return {'state':dict(mass_kg=13.,heat_w=0.,temperature_c=40.,deformation_m=0.,gap_m=.008)}
    assert coupling.iterate(simple(),invented)['coupling_status']=='failed'


def test_next_experiment_can_rank_failure_but_integrated_policy_refuses_it():
    candidate=simple();failure=result(candidate,screen='fail');policy=dict(policy_id='declared',objectives={'mass':1.},critical_evaluators=['field'],minimum_maturity='coupled-numerical')
    assert selection.select([candidate],[failure],purpose='next-experiment',policy=policy)['selected_candidate_id']==candidate['candidate_id']
    assert selection.select([candidate],[failure],purpose='integrated-baseline',policy=policy)['selected_candidate_id'] is None


def test_confirmation_metrics_do_not_replace_primary_or_fake_domain_validation():
    candidate=simple();primary=result(candidate,settings={'coupling_context_id':'same'})
    req=c.make_evaluation_request(candidate,evaluator_id='field',evaluator_sources={'independent.py':'b'*64},purpose='confirmation',
        settings={'confirmation_of':primary['evaluation_id'],'verification_scope':'arithmetic-source-only'},scenario={'independent_case':True})
    confirm=c.make_result(req,execution_status='executed',numerical_status='converged',screen_status='pass',maturity='coupled-numerical',metrics={'mass':12.0001})
    policy=dict(policy_id='domain',objectives={'mass':1.},critical_evaluators=['field'],minimum_maturity='coupled-numerical',required_confirmation_scope='independent-domain',
        confirmation_links={primary['evaluation_id']:[confirm['evaluation_id']]})
    chosen=selection.select([candidate],[primary,confirm],purpose='integrated-baseline',policy=policy)
    assert chosen['selected_candidate_id'] is None
    assert 'missing-independent-confirmation:field' in chosen['rejections'][candidate['candidate_id']]


def test_incompatible_primary_flux_hypotheses_are_not_mixed():
    candidate=simple();rows=[result(candidate,hypothesis={'flux':'original'}),result(candidate,hypothesis={'flux':'sensitivity'})]
    chosen=selection.select([candidate],rows,purpose='next-experiment',policy={'policy_id':'original','objectives':{'mass':1.}})
    assert chosen['selected_candidate_id'] is None


@pytest.fixture(scope='module')
def real_families():return families.initial_families()


def test_three_real_families_have_counted_stock_and_selected_spans(real_families):
    assert len({candidate['candidate_id'] for candidate in real_families})==3
    assert [candidate['architecture']['guidebeam']['span_m'] for candidate in real_families]==[25.,25.,20.]
    masses=[c.mass_properties(candidate)['known_mass_subtotal_kg'] for candidate in real_families]
    assert masses[0]==pytest.approx(37618.5915003343)
    assert masses[1]>masses[0] and masses[2]>masses[0]
    for candidate in real_families:
        with pytest.raises(c.UnknownInstalledStock):families.materialize(candidate)
        native=families.materialize(candidate,allow_incomplete=True)
        assert native['candidate_id']==candidate['candidate_id'];assert native['unknown_installed_stock_ids']
        assert not native['complete_installed_distribution']


def test_worker_environment_roundtrip_preserves_exact_request(real_families):
    from engineering.design_search import evaluators
    candidate=real_families[0];planned=evaluators.request_for(candidate,'definition')
    actual=evaluators.evaluate(candidate,'definition',environment=planned['environment'])
    assert actual['request']==planned
    assert actual['execution_status']=='executed'


def test_span_revision_rebuilds_geometry_and_identity(real_families):
    original=real_families[0];changed=families.with_beam_selection(original,span_m=20.)
    assert changed['candidate_id']!=original['candidate_id']
    assert changed['lineage']['parent_candidate_ids']==[original['candidate_id']]
    native=families.materialize(changed,allow_incomplete=True)
    assert native['guideway_definition']['span_m']==20.
    assert c.mass_properties(changed,'guideway-per-span')['known_mass_subtotal_kg']<c.mass_properties(original,'guideway-per-span')['known_mass_subtotal_kg']


def test_result_driven_beam_revision_is_counted_and_keeps_unknowns(real_families):
    source=real_families[1];failed=result(source,name='civil',screen='fail')
    child=families.propose_revision(source,[failed])
    assert child['architecture']['guidebeam']['section_id']=='narrow-deep-reference'
    assert child['lineage']['parent_candidate_ids']==[source['candidate_id']]
    assert c.inventory_summary(child)['unknown_stock_ids']
    assert families.propose_revision(source,[result(source,name='magnetic',screen='fail')]) is None
