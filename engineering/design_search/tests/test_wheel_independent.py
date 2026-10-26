"""Independent selection/cache controls for wheel-rail research integration.

The small stock below is an artificial contract fixture, not a physical train.
Numerical execution, design failure and missing evidence stay distinguishable.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import pytest
from engineering.design_search import contracts as k, selection, registry


def stock(size=1., *, unknown=False):
    mass = 1000. * size
    geometry = [dict(id='stock', kind='box', frame_id='car', material_id='material',
                     at_m=[0., 0., 0.], size_m=[size, 1., 1.])]
    inventory = [dict(id='stock', geometry_id='stock', frame_id='car', scope='vehicle-per-car',
                      quantity=1, status='known', basis='Artificial selection-control stock',
                      unit_mass_kg=mass, cg_m=[size/2, .5, .5],
                      inertia_kg_m2=[[mass/6, 0., 0.],
                                    [0., mass*(size**2+1)/12, 0.],
                                    [0., 0., mass*(size**2+1)/12]])]
    if unknown:
        geometry.append(dict(id='services', kind='unresolved-equipment',
                             frame_id='car', material_id='material'))
        inventory.append(dict(id='services', geometry_id='services', frame_id='car',
                              scope='vehicle-per-car', quantity=1, status='unknown',
                              basis='Actual installed service equipment is not defined', unit_mass_kg=None))
    return k.make_candidate(requirement_revision='wheel-independent-fixture-r1',
        architecture=dict(family='wheel_rail_station_lim', cars=6),
        frames=[dict(id='car', parent_id=None, origin_m=[0., 0., 0.],
                     rotation_matrix=[[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])],
        materials=[dict(id='material', density_kg_m3=1000., basis='Artificial fixture density')],
        geometry=geometry, interfaces=[], installed_inventory=inventory)


def result(candidate, evaluator, *, execution='executed', numerical='converged',
           screen='fail', penalty=None, settings=None):
    source = Path(k.__file__)
    request = k.make_evaluation_request(candidate, evaluator_id=evaluator,
        evaluator_sources={'engineering/design_search/contracts.py': sha256(source.read_bytes()).hexdigest()},
        settings=dict(coupling_context_id=k.identity(candidate), **(settings or {})))
    return k.make_result(request, execution_status=execution, numerical_status=numerical,
        screen_status=screen, maturity='coupled-numerical',
        metrics={} if penalty is None else dict(constraint_violation=penalty))


def policy():
    return dict(policy_id='wheel-independent-r1', objectives=dict(constraint_violation=1.),
                objective_evaluators=['wheel-system'])


@pytest.mark.parametrize('execution,numerical', [('executed', 'invalid'), ('error', 'unknown'),
                                               ('executed', 'nonconverged')])
def test_invalid_or_unfinished_objective_cannot_beat_valid_design_failure(execution, numerical):
    invalid, valid = stock(), stock(1.1)
    rows = [result(invalid, 'definition', screen='pass'),
            result(invalid, 'wheel-system', execution=execution, numerical=numerical,
                   screen='unknown', penalty=0.),
            result(valid, 'wheel-system', penalty=1.)]
    chosen = selection.select([invalid, valid], rows, purpose='next-experiment', policy=policy())
    assert chosen['selected_candidate_id'] == valid['candidate_id']
    assert invalid['candidate_id'] in chosen['rejections']
    assert not chosen['physical_accepted'] and not chosen['configuration_adopted']


def test_valid_design_failure_remains_useful_research_but_unknown_stock_blocks_baseline():
    candidate = stock(unknown=True)
    row = result(candidate, 'wheel-system', penalty=1.)
    research = selection.select([candidate], [row], purpose='next-experiment', policy=policy())
    assert research['selected_candidate_id'] == candidate['candidate_id']
    integrated = selection.select([candidate], [row], purpose='integrated-baseline',
        policy=dict(policy(), critical_evaluators=['wheel-system'], require_confirmation=True))
    assert integrated['selected_candidate_id'] is None
    assert 'incomplete-installed-inventory' in integrated['rejections'][candidate['candidate_id']]
    assert not integrated['physical_accepted'] and not integrated['configuration_adopted']


def test_dependency_payload_and_solver_epoch_are_part_of_exact_cache_identity(tmp_path):
    candidate = stock()
    dependency = result(candidate, 'wheel-motor', penalty=2.)
    revised = k.make_result(dependency['request'], execution_status='executed', numerical_status='converged',
                            screen_status='fail', metrics=dict(constraint_violation=3.))
    assert dependency['evaluation_id'] == revised['evaluation_id']
    assert dependency['result_sha256'] != revised['result_sha256']
    def request_for(dep, tool='a'*64):
        return k.make_evaluation_request(candidate, evaluator_id='wheel-system',
            evaluator_sources=dependency['request']['evaluator_sources'],
            settings=dict(dependency_results={'wheel-motor': dep}),
            environment=dict(solver_binary_sha256=tool))
    a, b, c = request_for(dependency), request_for(revised), request_for(dependency, 'b'*64)
    assert len({a['evaluation_id'], b['evaluation_id'], c['evaluation_id']}) == 3
    store = registry.ImmutableRegistry(tmp_path/'registry')
    cached = k.make_result(a, execution_status='executed', numerical_status='converged',
                           screen_status='unknown', metrics=dict(constraint_violation=2.))
    store.store('evaluation', cached)
    assert store.cached(a) == cached
    assert store.cached(b) is None and store.cached(c) is None


def test_dependency_result_digest_cannot_be_reused_after_payload_change():
    dependency = result(stock(), 'wheel-motor', penalty=1.)
    changed = deepcopy(dependency)
    changed['metrics']['constraint_violation'] = 0.
    with pytest.raises(ValueError, match='payload digest'):
        k.validate_result(changed)


@pytest.mark.parametrize('mutation', ['payload', 'candidate', 'source', 'tool', 'inventory'])
def test_wheel_dependency_adapter_refuses_mixed_or_stale_evidence(monkeypatch, mutation):
    from engineering.design_search import wheel_evaluators as w
    c = stock()
    sources = {'fixture-wheel-method.py': 'a'*64}
    monkeypatch.setattr(w, 'source_snapshot', lambda _: deepcopy(sources))
    tools = {'getdp': {'binary_sha256': 'b'*64}}
    parent = k.make_evaluation_request(c, evaluator_id='wheel-definition', evaluator_sources=sources,
                                      environment=dict(native_tools=tools))
    dep = k.make_result(parent, execution_status='executed', numerical_status='converged',
                        screen_status='unknown')
    deps = {'wheel-definition': dep}
    request = k.make_evaluation_request(c, evaluator_id='wheel-body', evaluator_sources=sources,
        settings=dict(dependency_results=deps), environment=dict(native_tools=tools))
    assert w.validate_dependencies(c, request) == deps
    if mutation == 'payload':
        deps['wheel-definition']['metrics']['fabricated_objective'] = 0.
    elif mutation == 'candidate':
        foreign = stock(1.2)
        req = k.make_evaluation_request(foreign, evaluator_id='wheel-definition', evaluator_sources=sources,
                                        environment=dict(native_tools=tools))
        deps['wheel-definition'] = k.make_result(req, execution_status='executed', numerical_status='converged', screen_status='unknown')
    elif mutation == 'source':
        monkeypatch.setattr(w, 'source_snapshot', lambda _: {'fixture-wheel-method.py': 'c'*64})
    elif mutation == 'tool':
        request = deepcopy(request)
        request['environment']['native_tools'] = {'getdp': {'binary_sha256': 'c'*64}}
    else:
        deps['unrequested-wheel-result'] = dep
    # make_evaluation_request deep-copies settings; install the explicitly
    # changed dependency mapping to exercise the adapter's own evidence guard.
    if mutation != 'tool':
        request = deepcopy(request)
        request['settings']['dependency_results'] = deps
    with pytest.raises(ValueError):
        w.validate_dependencies(c, request)
