"""References retain provenance, uncertainty, permission and actual execution scope."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

import pytest

from engineering.outline import reference_library as lib, rea_adapter as rea


def record(*, permitted="unknown", authorization="unknown", kind="functional-patterns"):
    raw = b"owned fixture evidence\n"
    return lib.make_record(kind, name="fixture", origin=dict(uri="artifact:fixture",
        artifact_sha256=sha256(raw).hexdigest(), source_kind="authorized-observation", source_class="C", version="fixture/1"),
        rights=dict(spdx="unknown" if permitted == "unknown" else "Apache-2.0", permitted_use=permitted,
            authorization=dict(status=authorization, basis="Explicit fixture permission" if authorization == "authorized" else None,
                scope=["analysis", "implementation"])),
        evidence=[dict(kind="synthetic-fixture", claim="A digital input fixture exists", uncertainty="No physical observation")],
        unresolved_tasks=["Actual target behavior remains unobserved"], artifact_bytes=raw)


def reseal(value, key):
    value = deepcopy(value); value.pop(key); value[key] = lib.identity(value); return value


def test_three_libraries_keep_unknown_permission_and_exact_bytes():
    initial = lib.new_library(); ref = record(); stored = lib.register(initial, ref)
    assert len(initial["records"]["functional-patterns"]) == 0
    assert stored["records"]["functional-patterns"][0]["record_id"] == ref["record_id"]
    assert not ref["implementation_reuse_allowed"]
    assert set(stored["records"]) == set(lib.KINDS)
    changed = deepcopy(stored); changed["records"]["functional-patterns"][0]["name"] = "changed"
    with pytest.raises(ValueError, match="identity"):
        lib.validate(changed)
    with pytest.raises(ValueError, match="Duplicate"):
        lib.register(stored, ref)


@pytest.mark.parametrize("permitted,authorization,expected", [
    ("unknown", "authorized", False), ("reference-only", "authorized", False),
    ("prohibited", "authorized", False), ("implementation", "unknown", False),
    ("implementation", "authorized", True)])
def test_permission_is_separate_from_evidence_and_physical_acceptance(permitted, authorization, expected):
    ref = record(permitted=permitted, authorization=authorization)
    assert ref["implementation_reuse_allowed"] is expected
    assert all(ref[k] is False for k in lib.FLAGS)
    tampered = deepcopy(ref); tampered["physical_accepted"] = True
    with pytest.raises(ValueError, match="physical acceptance"):
        lib.validate_record(reseal(tampered, "record_id"))


def test_unknown_permissions_cannot_be_promoted_by_resealing():
    ref = record(); ref["implementation_reuse_allowed"] = True
    with pytest.raises(ValueError, match="permission"):
        lib.validate_record(reseal(ref, "record_id"))
    ref = record(); ref["evidence"][0]["kind"] = "physical-measurement"
    with pytest.raises(ValueError, match="instrument"):
        lib.validate_record(reseal(ref, "record_id"))


def test_actual_owned_pilot_is_deterministic_and_source_bound():
    first = lib.owned_pilot(); second = lib.owned_pilot()
    assert first == second
    assert not first["rea_executed"] and not first["rust_binary_executed"]
    assert not first["external_transactions_performed"]
    assert first["native_jobs"] == 0
    library = lib.validate(first["library"], root=lib.ROOT)
    assert [len(library["records"][k]) for k in lib.KINDS] == [2, 1, 1]
    pattern = next(r for r in library["records"]["functional-patterns"] if r["behavior_fixtures"])
    fixtures = pattern["behavior_fixtures"]
    assert fixtures[0]["observed"]["drafts"]["external_transactions_performed"] is False
    assert fixtures[0]["observed"]["live_movement_authority"] is False
    assert all(fixtures[0]["observed"][key] == value for key, value in fixtures[0]["expected"].items())
    assert "cannot activate" in fixtures[1]["observed_error"]
    assert "exact integrated cell" in fixtures[2]["observed_error"]
    assert all(sha256((lib.ROOT/name).read_bytes()).hexdigest() == h for name, h in first["source_sha256"].items())


def test_stale_owned_source_is_rejected_before_module_execution(tmp_path):
    target = tmp_path / "services/integration/osr_integration/reference_cell.py"
    target.parent.mkdir(parents=True)
    target.write_text("raise RuntimeError('must not execute changed input')")
    with pytest.raises(ValueError, match="source changed"):
        lib.owned_pilot(tmp_path)


def test_closed_mesh_recovers_only_the_primitive_with_explicit_units():
    raw = lib.box_fixture_bytes(); box = lib.recover_box_ascii_stl(raw, units="mm", uncertainty_m=.0001)
    assert box["dimensions_m"] == pytest.approx([.1, .06, .004])
    assert box["volume_m3"] == pytest.approx(.1*.06*.004)
    assert box["watertight"] and box["consistently_oriented"]
    assert not box["CAD_export_executed"] and not box["arbitrary_organic_reconstruction"]
    assert box["physical_material"] is None
    with pytest.raises(ValueError, match="units"):
        lib.recover_box_ascii_stl(raw, units="unknown", uncertainty_m=0)
    with pytest.raises(ValueError, match="corners"):
        lib.recover_box_ascii_stl(raw.replace(b"vertex 100 60 4", b"vertex 99 60 4", 1), units="mm", uncertainty_m=0)


def test_open_reversed_duplicate_or_nan_mesh_is_rejected():
    raw = lib.box_fixture_bytes()
    first = raw.index(b"facet normal"); end = raw.index(b"endfacet") + len(b"endfacet\n")
    with pytest.raises(ValueError):
        lib.recover_box_ascii_stl(raw[:first]+raw[end:], units="mm", uncertainty_m=0)
    with pytest.raises(ValueError):
        lib.recover_box_ascii_stl(raw.replace(b"vertex 100 60 0\nvertex 100 0 0", b"vertex 100 0 0\nvertex 100 60 0", 1), units="mm", uncertainty_m=0)
    with pytest.raises(ValueError, match="Finite"):
        lib.recover_box_ascii_stl(raw.replace(b"vertex 0 0 0", b"vertex nan 0 0", 1), units="mm", uncertainty_m=0)


def test_library_export_is_fresh_and_hashes_payload(tmp_path):
    pilot = lib.owned_pilot(); output = tmp_path / "library"
    manifest = lib.export_library(pilot["library"], output)
    assert manifest["files"]["library.json"] == sha256((output/"library.json").read_bytes()).hexdigest()
    assert json.loads((output/"library.json").read_bytes()) == pilot["library"]
    with pytest.raises(ValueError, match="Fresh"):
        lib.export_library(pilot["library"], output)


def test_cross_library_links_and_declared_artifact_bytes_are_checked():
    ref = record(); ref["related_record_ids"] = ["f"*64]
    with pytest.raises(ValueError, match="Broken"):
        lib.register(lib.new_library(), reseal(ref, "record_id"))
    with pytest.raises(ValueError, match="Artifact bytes"):
        lib.make_record("physical-solutions", name="bad digest", origin=record()["origin"], rights=record()["rights"],
            evidence=record()["evidence"], artifact_bytes=b"different bytes")


def test_normalized_rea_import_records_claimed_observation_without_faking_execution():
    base = record()
    observation = dict(schema="osr-rea-normalized-observation/1", name="declared captured interface",
        tool=dict(name="REA", version="6.8.0"), origin=base["origin"], rights=base["rights"],
        observations=[dict(kind="software-observation", claim="Declared captured request/response", uncertainty="Imported claim, no local replay")],
        behavior_fixtures=[dict(input={"request": "fixture"}, observed={"response": "fixture"})], upstream_execution_reported=True)
    result = rea.import_rea(observation)
    assert result["origin"]["upstream_execution_reported"] is True
    assert result["behavior_fixtures"][0]["rea_executed"] is False
    assert not result["implementation_reuse_allowed"]
    assert not result["source_bytes_verified_at_import"]
    observation["physical_accepted"] = True
    with pytest.raises(ValueError, match="physical qualification"):
        rea.import_rea(observation)
    observation.pop("physical_accepted"); observation["observations"][0]["kind"] = "physical-measurement"
    with pytest.raises(ValueError, match="not physical"):
        rea.import_rea(observation)


def test_plans_are_data_only_authorization_bounded_and_source_first():
    base = record()
    target = dict(origin=base["origin"], rights=base["rights"], source_available=True)
    blocked = rea.plan_task(target)
    assert blocked["state"] == "authorization-or-permitted-use-required"
    assert blocked["method"] == "source-first"
    assert blocked["commands"] == [] and not blocked["automatic_execution"]
    target["rights"] = record(permitted="implementation", authorization="authorized")["rights"]
    plan = rea.plan_task(target)
    assert plan["state"] == "ready-for-authorized-local-analysis"
    assert plan["tool_requirements"] == []
    for kwargs in ({"cpu_seconds": 61}, {"memory_mb": 1025}, {"purpose": "execute-shell"}):
        with pytest.raises(ValueError): rea.plan_task(target, **kwargs)


def test_upstream_rights_do_not_authorize_themselves_even_with_valid_artifact_bytes():
    base = record(permitted="implementation", authorization="authorized")
    observation = dict(schema="osr-rea-normalized-observation/1", name="untrusted declaration",
        tool=dict(name="REA", version="6.8.0"), origin=base["origin"], rights=base["rights"],
        observations=[dict(kind="software-observation", claim="Reported behavior", uncertainty="No independent replay")])
    imported = rea.import_rea(observation, artifact_bytes=b"owned fixture evidence\n")
    assert imported["source_bytes_verified_at_import"]
    assert imported["origin"]["upstream_rights"] == base["rights"]
    assert imported["origin"]["source_kind"] == "reported-observation"
    assert imported["rights"]["authorization"]["status"] == "unknown"
    assert not imported["implementation_reuse_allowed"]
    authorized = rea.import_rea(observation, artifact_bytes=b"owned fixture evidence\n", rights_declaration=base["rights"])
    assert authorized["implementation_reuse_allowed"]
    assert authorized["physical_accepted"] is False


def test_geometry_tool_names_do_not_conflate_licenses_or_claim_installs():
    physical = lib.owned_pilot()["library"]["records"]["physical-solutions"][0]
    first = rea.geometry_recipe(physical, tool="stl2step_blinkingsun")
    second = rea.geometry_recipe(physical, tool="stl2step_nickpagz")
    assert first["tool"]["spdx"] == "MIT"
    assert second["tool"]["spdx"] == "Apache-2.0"
    assert first["recipe_id"] != second["recipe_id"]
    assert not first["installation_performed"] and not first["execution_performed"]
    with pytest.raises(ValueError, match="identity"):
        rea.geometry_recipe(physical, tool="stl2step")
