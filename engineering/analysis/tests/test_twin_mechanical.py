"""Independent physical identities and adverse controls for design-model export."""

import hashlib
import json
import math

import pytest

from engineering.generative_design import mechanical_detail, twin_mechanical as twin


@pytest.fixture(scope="module")
def report():
    return twin.build()


def test_json_source_bindings_and_honest_release_boundary(report):
    json.dumps(report, allow_nan=False)
    assert report["schema"] == "osr-domain-design-twin/1"
    assert not report["physical_twin"] and not report["complete_specification"]
    assert not report["production_release"]
    for path, digest in report["source_files"].items():
        assert hashlib.sha256((twin.ROOT/path).read_bytes()).hexdigest() == digest
    assert {x["configuration_id"] for x in report["systems"]} == {"LM3", "metro-6car-planning"}
    assert any("physical-twin" in x["id"] for x in report["open_requests"])
    assert len([x for x in report["open_requests"] if x.get("coverage")]) == 10


def test_parts_have_valid_ancestry_fasteners_and_open_manufacturing(report):
    for system in report["systems"]:
        for variant in system["variants"]:
            parts = {x["id"]: x for x in variant["parts"]}
            assert len(parts) == len(variant["parts"])
            assert all(x["parent_id"] is None or x["parent_id"] in parts for x in parts.values())
            assert all(x["state"] in {"pass", "fail", "unknown"} for x in variant["checks"])
            assert any(x["state"] == "unknown" for x in variant["checks"])
            assert not variant["accepted"]
            if variant["id"].startswith("connected"):
                bolts = [p for key,p in parts.items() if "-bolt-" in key]
                assert len(bolts) == 2*variant["parameters"]["bolts_per_support"]
                assert all(p["specifications"]["length_m"] is None for p in bolts)
                assert not any(p["manufacturing"].get("origin_confirmed", False) for p in bolts)


def test_independent_concept_volume_and_load_conservation(report):
    for system in report["systems"]:
        context = system["source_context"]
        for variant in system["variants"]:
            if not variant["id"].startswith("concept-"):
                continue
            mass = sum(p["specifications"].get("net_mass_kg", 0) for p in variant["parts"])
            assert mass == pytest.approx(variant["objectives"]["modeled_longitudinal_mass_kg"])
            force = context["source_car_force_n"] + mass*9.80665
            assert variant["parameters"]["load_force_n"] == pytest.approx(force)
            reactions = variant["metrics"]["beam"]["reactions_n"]
            assert sum(reactions) == pytest.approx(force)
            assert reactions[0] == pytest.approx(reactions[1])


def test_closed_form_simply_supported_beam_and_adverse_load_scaling():
    context = dict(mechanical_detail.contexts()[0])
    context.update(body_length_m=10., support_x_m=[0., 10.],
                   side_member_length_m=10., centre_member_length_m=10.,
                   side_depth_envelope_m=1.)
    # Independent analytical fixtures exercise the private pure calculator;
    # exported proposals must instead pass the source-bound public adapter.
    base = twin._architecture_variant(context, "closed-box", .6, .016)
    force = base["parameters"]["load_force_n"]
    ei = base["parameters"]["young_modulus_pa"]*base["parameters"]["total_inertia_m4"]
    assert base["metrics"]["beam"]["maximum_abs_moment_nm"] == pytest.approx(force*10/8)
    assert base["metrics"]["beam"]["maximum_abs_deflection_m"] == pytest.approx(5*force*10**3/(384*ei))
    heavier = dict(context, source_car_force_n=context["source_car_force_n"]*2)
    adverse = twin._architecture_variant(heavier, "closed-box", .6, .016)
    assert adverse["metrics"]["beam"]["maximum_abs_deflection_m"] > base["metrics"]["beam"]["maximum_abs_deflection_m"]
    assert adverse["objectives"] == base["objectives"]


def test_distinct_architectures_are_not_dimension_renaming(report):
    for system in report["systems"]:
        variants = {x["concept"]: x for x in system["variants"] if x["id"].startswith("concept-") and x["parameters"]["side_height_m"] == .6}
        assert variants["closed-box"]["parameters"]["total_inertia_m4"] > variants["open-i"]["parameters"]["total_inertia_m4"]
        assert len(variants["closed-box"]["parts"]) > len(variants["open-i"]["parts"])
        assert any(v["selection_state"] == "rejected-by-research-check" for v in system["variants"])


def test_executed_feedback_retains_ancestry_and_recalculates_self_weight(report):
    for system, experiment in zip(report["systems"], report["experiments"]):
        variants = {v["id"]: v for v in system["variants"]}
        assert len(experiment["feedback_generations"]) == 2
        for edge in experiment["feedback_generations"]:
            parent = variants[edge["parent_variant_id"]]
            child = variants[edge["child_variant_id"]]
            assert parent["parameters"] != child["parameters"]
            before = {c["id"] for c in parent["checks"] if c["state"] == "fail"}
            after = {c["id"] for c in child["checks"] if c["state"] == "fail"}
            assert set(edge["resolved_failed_checks"]) == before-after
            assert set(edge["newly_failed_checks"]) == after-before
            mass = child["objectives"]["modeled_plate_and_RHS_mass_kg"]
            expected_force = system["source_context"]["source_car_force_n"]+mass*9.80665
            assert child["metrics"]["modeled_car_force_n"] == pytest.approx(expected_force)


@pytest.mark.parametrize("height,wall", [(True,.01), (math.nan,.01), (.1,.06), (-.2,.01)])
def test_invalid_dimensions_cannot_be_promoted(height, wall):
    with pytest.raises(ValueError):
        twin.architecture_variant(mechanical_detail.contexts()[0], "open-i", height, wall)


@pytest.mark.parametrize("edit", ["force", "support", "hash"])
def test_architecture_rejects_tampered_controlled_context(edit):
    from copy import deepcopy
    context = deepcopy(mechanical_detail.contexts()[0])
    if edit == "force":
        context["source_car_force_n"] = 0
    elif edit == "support":
        context["support_x_m"][0] += .5
    else:
        name = next(iter(context["source_sha256"]))
        context["source_sha256"][name] = "0"*64
    with pytest.raises(ValueError, match="exact current mechanical context"):
        twin.architecture_variant(context, "closed-box", .6, .016)
