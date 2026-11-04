"""The explicit encoder changes execution provenance, never physical results."""
from copy import deepcopy
import json
import os

import pytest

from engineering.design_search import native_campaign as c, native_canonical as n
from engineering.station_rail import common


@pytest.fixture
def small(monkeypatch):
    spec=c.specification();spec.update(proposals_per_generation=4,evaluations_per_generation=2,
        detailed_finalists=0,seed_bracing=[False])
    monkeypatch.setattr(c,"specification",lambda root=c.ROOT:deepcopy(spec))
    registry=c.shape_families.registry();recipes={k:registry[k] for k in ("aluminium_spaceframe","modular_segments")}
    monkeypatch.setattr(c.shape_families,"registry",lambda root=c.ROOT:deepcopy(recipes))


def engine():
    try:return n.NativeCanonical()
    except FileNotFoundError:
        if os.environ.get("OSR_TEST_NATIVE_CANONICAL")=="1":raise
        pytest.skip("Explicit native canonical extension build required")


def read(result):return json.loads(open(result["output"]).read())


def test_default_campaign_does_not_load_or_build_a_native_encoder(tmp_path,small,monkeypatch):
    def forbidden(*args,**kwargs):raise AssertionError("Default campaign requested native encoding")
    monkeypatch.setattr(n,"NativeCanonical",forbidden)
    value=read(c.run(state=tmp_path,generations=0))
    assert "canonical_backend" not in value["contract"]
    assert common.encoded({1:"broader Python domain"})==b'{"1":"broader Python domain"}\n'


def test_rust_and_python_campaigns_preserve_complete_scientific_payloads(tmp_path,small):
    engine()
    original=(common.encoded,common.identity,c.encoded,c.identity)
    python=read(c.run(state=tmp_path/"python",generations=1,maximum_new_evaluations=2))
    rust=read(c.run(state=tmp_path/"rust",generations=1,maximum_new_evaluations=2,canonical_backend="rust"))
    assert (common.encoded,common.identity,c.encoded,c.identity)==original
    assert rust["evaluations"]==python["evaluations"]
    assert rust["archive"]==python["archive"]
    assert rust["refinement"]==python["refinement"]
    keys=("genes","operator","parent_candidate_ids","candidate_id","definition_id","state")
    projection=lambda run:[{k:row.get(k) for k in keys} for row in run["attempts"]]
    assert projection(rust)==projection(python)
    assert rust["contract"]["canonical_backend"]["mode"]=="rust"
    assert rust["contract_id"]!=python["contract_id"]
    assert all(rust[k] is False for k in c.FLAGS)
    resumed=read(c.run(state=tmp_path/"rust",generations=1,maximum_new_evaluations=0,canonical_backend="rust"))
    assert resumed["evaluations"]==rust["evaluations"] and resumed["generations"]==rust["generations"]


def test_encoder_aliases_restore_even_when_strict_domain_rejects_input():
    engine();before=(common.encoded,common.identity,c.encoded,c.identity)
    with pytest.raises(TypeError):
        with n.campaign_backend("rust"):
            assert common.encoded({"negative-zero":-0.0})==b'{"negative-zero":-0.0}\n'
            common.encoded({1:"unsupported native key"})
    assert (common.encoded,common.identity,c.encoded,c.identity)==before
    assert common.encoded({1:"still supported by Python"})==b'{"1":"still supported by Python"}\n'


def test_concurrent_unrelated_context_keeps_python_reference_encoder():
    from concurrent.futures import ThreadPoolExecutor
    engine()
    with n.campaign_backend("rust"):
        with ThreadPoolExecutor(max_workers=1) as pool:
            assert pool.submit(common.encoded,{1:"Python-only key"}).result(timeout=5)==b'{"1":"Python-only key"}\n'
        with pytest.raises(RuntimeError,match="scope is active"):
            with n.campaign_backend("rust"):pass


def test_session_cannot_escape_its_source_epoch():
    value=engine()
    with value.session() as backend:assert backend.encoded([1,2])==b'[1,2]\n'
    with pytest.raises(RuntimeError,match="session has ended"):backend.identity([1,2])
