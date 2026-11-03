from copy import deepcopy

import pytest

from engineering.design_search.invocation_cache import InvocationCache


def test_reuse_is_fresh_bounded_and_returns_independent_json_records():
    context = dict(source="one",runtime="same")
    made = dict(candidate_id="body",nested=[dict(mass=None)])
    calls = []
    def compute():
        calls.append(1)
        return made
    cache = InvocationCache(lambda:context)
    first = cache.evaluate("axial-assessment",dict(load=1),compute)
    first["nested"][0]["mass"] = 999
    made["nested"][0]["mass"] = 123
    assert cache.evaluate("axial-assessment",dict(load=1),compute)["nested"][0]["mass"] is None
    assert len(calls)==1
    # A new invocation never accepts the preceding invocation's recorded result.
    other = InvocationCache(lambda:context)
    assert other.evaluate("axial-assessment",dict(load=1),compute)["nested"][0]["mass"]==123
    assert len(calls)==2
    stats=cache.statistics()
    assert stats["counts"]["axial-assessment"]["reused"]==1
    assert stats["persisted_evidence_loaded"] is False
    stats["counts"]["axial-assessment"]["reused"]=100
    assert cache.statistics()["counts"]["axial-assessment"]["reused"]==1


@pytest.mark.parametrize("change",["candidate","definition","graph","loads","requirements","runtime","sources"])
def test_every_declared_semantic_input_participates_in_reuse_key(change):
    cache=InvocationCache(lambda:dict(epoch="same"))
    inputs={k:"original" for k in ("candidate","definition","graph","loads","requirements","runtime","sources")}
    assert cache.evaluate("axial-assessment",inputs,lambda:dict(result=1))==dict(result=1)
    revised=deepcopy(inputs);revised[change]="revised"
    assert cache.evaluate("axial-assessment",revised,lambda:dict(result=2))==dict(result=2)
    assert cache.statistics()["counts"]["axial-assessment"]["computations"]==2


@pytest.mark.parametrize("field",["source","runtime"])
def test_changed_epoch_rejects_a_hit_and_during_compute(field):
    context=dict(source="one",runtime="one")
    cache=InvocationCache(lambda:context)
    cache.evaluate("axial-assessment",{},lambda:dict(result=1))
    context[field]="two"
    with pytest.raises(RuntimeError,match="context changed"):
        cache.evaluate("axial-assessment",{},lambda:dict(result=2))
    fresh=InvocationCache(lambda:context)
    def altered():
        context[field]="three"
        return dict(result=3)
    with pytest.raises(RuntimeError,match="context changed"):
        fresh.evaluate("axial-assessment",{},altered)
    assert fresh.statistics()["entries"]==0


def test_lru_limits_and_oversize_records_do_not_change_results():
    cache=InvocationCache(lambda:{},maximum_entries=2,maximum_bytes=30)
    for i in (1,2,1,3):
        assert cache.evaluate("axial-assessment",i,lambda:dict(n=i))==dict(n=i)
    stats=cache.statistics()
    assert stats["entries"]==2 and stats["retained_bytes"]<=30
    assert stats["counts"]["axial-assessment"]==dict(computations=3,reused=1,failed=0,oversize=0,evicted=1)
    result=cache.evaluate("axial-assessment","big",lambda:dict(large="x"*100))
    assert result==dict(large="x"*100)
    assert cache.statistics()["counts"]["axial-assessment"]["oversize"]==1


def test_failures_are_not_cached_and_disable_mode_has_identical_outputs():
    cache=InvocationCache(lambda:{})
    def failed():raise ValueError("bounded model failed")
    with pytest.raises(ValueError,match="model failed"):
        cache.evaluate("axial-assessment",{},failed)
    expected=dict(state="model-held",unknown=None,engineering_accepted=False)
    assert cache.evaluate("axial-assessment",{},lambda:expected)==expected
    disabled=InvocationCache(lambda:{},enabled=False)
    assert disabled.evaluate("axial-assessment",{},lambda:expected)==expected
    assert disabled.evaluate("axial-assessment",{},lambda:expected)==expected
    assert disabled.statistics()["entries"]==0
    assert disabled.statistics()["counts"]["axial-assessment"]["computations"]==2


@pytest.mark.parametrize("kwargs",[dict(enabled=1),dict(maximum_entries=0),dict(maximum_entries=65),dict(maximum_bytes=0),dict(maximum_bytes=17*1024**2)])
def test_invalid_resource_or_policy_limits_are_rejected(kwargs):
    with pytest.raises(ValueError):InvocationCache(lambda:{},**kwargs)


def test_unknown_namespace_and_nonfinite_inputs_cannot_enter_cache():
    cache=InvocationCache(lambda:{})
    with pytest.raises(ValueError):cache.evaluate("native-solver",{},lambda:{})
    with pytest.raises(ValueError):cache.evaluate("axial-assessment",dict(x=float("nan")),lambda:{})
    assert cache.statistics()["entries"]==0
