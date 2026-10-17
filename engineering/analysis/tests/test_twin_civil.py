"""Independent equilibrium and adverse-case tests of executable civil twins."""

from hashlib import sha256
import json
import math

import pytest

from engineering.generative_design import twin_civil


@pytest.fixture(scope="module")
def packet():
    return twin_civil.build()


def test_contexts_preserve_source_load_identity_without_automatic_acceptance(packet):
    assert len(packet["systems"]) == 4
    assert {s["variants"][0]["parameters"]["span_m"] for s in packet["systems"]} == {
        20.0,
        25.0,
    }
    assert {
        len(s["interfaces"]["vehicle"]["applied_axles"]) for s in packet["systems"]
    } == {12, 24}
    six = next(
        s
        for s in packet["systems"]
        if s["configuration_id"].startswith("planning-six-car")
    )
    interface = six["interfaces"]["vehicle"]
    # Independent total-force balance of the explicit 460.8t sensitivity case;
    # catches dropped axles, renormalisation and double application of1.25.
    assert math.fsum(a["force_n"] for a in interface["applied_axles"]) == pytest.approx(
        460800 * 9.80665 * 1.25
    )
    assert interface["accepted"] is False
    assert packet["physical_twin_correlated"] is False
    assert packet["manufacturing_release"] is False


def test_all_part_parents_resolve_and_unknowns_are_explicit(packet):
    for s in packet["systems"]:
        for v in s["variants"]:
            parts = {p["id"]: p for p in v["parts"]}
            assert len(parts) == len(v["parts"])
            assert [p["id"] for p in v["parts"] if p["parent_id"] is None] == ["bay"]
            assert all(
                p["parent_id"] is None or p["parent_id"] in parts
                for p in parts.values()
            )
            assert (
                len([p for p in parts.values() if p["id"].startswith("strand-")])
                == v["parameters"]["beam_architecture"]["strand_count"]
            )
            for p in parts.values():
                assert p["specifications"]["datum"]
                assert p["specifications"]["tolerance"]["state"] == "unknown"
                assert p["manufacturing"]["accepted"] is False
                assert p["inspection"]["state"] == "not-executed"
            assert (
                parts["support-near-bearing-1"]["specifications"][
                    "rated_vertical_force_n"
                ]
                is None
            )
            assert (
                parts["support-near-footing-reinforcement"]["specifications"][
                    "quantity"
                ]
                is None
            )
            assert parts["lifting-inserts"]["specifications"]["quantity"] is None


def test_recalculated_foundation_diagrams_integrate_to_demand(packet):
    for s in packet["systems"]:
        for v in s["variants"]:
            m = v["metrics"]
            B = v["parameters"]["footing_width_m"]
            f = m["foundation"]
            N, M = m["foundation_vertical_n"], m["foundation_moment_nm"]
            if f["full_contact"]:
                q0, q1 = (
                    f["linear_minimum_pressure_pa"],
                    f["linear_maximum_pressure_pa"],
                )
                assert (q0 + q1) * B**2 / 2 == pytest.approx(N)
                assert (q1 - q0) * B**3 / 12 == pytest.approx(M)
            elif f["equilibrium_possible"]:
                contact = f["compression_contact_length_m"]
                peak = f["compression_maximum_pressure_pa"]
                assert peak * contact * B / 2 == pytest.approx(N)
                assert N * (B / 2 - contact / 3) == pytest.approx(M)


def test_geometry_change_adds_selfweight_and_never_copies_original_reaction(packet):
    for system in packet["systems"]:
        compact, enlarged = system["variants"][:2]
        assert (
            enlarged["metrics"]["support_concrete_mass_kg"]
            > compact["metrics"]["support_concrete_mass_kg"]
        )
        assert (
            enlarged["objectives"]["two_support_known_mass_kg"]
            > compact["objectives"]["two_support_known_mass_kg"]
        )
        assert (
            enlarged["metrics"]["foundation_vertical_n"]
            > compact["metrics"]["foundation_vertical_n"]
        )
        # Full-contact pressure includes this extra gravity, not an area-only
        # division of the lighter candidate's original foundation force.
        B = enlarged["parameters"]["footing_width_m"]
        mean = enlarged["metrics"]["foundation_vertical_n"] / B**2
        assert mean > compact["metrics"]["foundation_vertical_n"] / B**2


def test_failed_candidates_retained_and_feedback_repairs_have_actual_parents(packet):
    for system in packet["systems"]:
        variants = {v["id"]: v for v in system["variants"]}
        assert any(
            v["selection_state"] == "rejected-known-checks" for v in variants.values()
        )
        assert any(v["parent_variant_id"] for v in variants.values())
        for v in variants.values():
            failures = [c["id"] for c in v["checks"] if c["state"] == "fail"]
            assert (v["selection_state"] == "rejected-known-checks") == bool(failures)
            if v["parent_variant_id"]:
                parent = variants[v["parent_variant_id"]]
                assert v["repair_trigger_checks"] == [
                    c["id"] for c in parent["checks"] if c["state"] == "fail"
                ]
                assert v["parameters"] != parent["parameters"]
            # Even a successful finite screen keeps site and resistance gates.
            assert any(
                c["id"] == "site_ground" and c["state"] == "unknown"
                for c in v["checks"]
            )
            assert v["full_specification_complete"] is False


def test_unmodelled_erection_and_station_routes_cannot_inherit_beam_pass(packet):
    for s in packet["systems"]:
        assert "separate evaluators" in s["interfaces"]["station"]
        for v in s["variants"]:
            launcher = next(
                r for r in v["construction_routes"] if r["id"] == "launching-gantry"
            )
            assert launcher["state"] == "unknown"
            assert launcher["supplier_capacity_accepted"] is False
            assert (
                next(
                    c
                    for c in v["checks"]
                    if c["id"] == "handling_attached_rebar_and_equipment"
                )["state"]
                == "unknown"
            )
    assert any("network-civil-coverage" in r["id"] for r in packet["open_requests"])


def test_sources_and_controlled_target_relations_are_bound(packet):
    assert len(packet["source_files"]) > 30
    for path, digest in packet["source_files"].items():
        assert sha256((twin_civil.ROOT / path).read_bytes()).hexdigest() == digest
    span25 = next(
        s for s in packet["systems"] if s["variants"][0]["parameters"]["span_m"] == 25
    )
    beam = next(p for p in span25["variants"][0]["parts"] if p["id"] == "beam")
    assert beam["source_target_ids"] == ["OSR-TYPE-D36A7871D9B7"]
    assert all(
        m["exact_fit_or_adoption"] is False for m in beam["source_target_mappings"]
    )
    json.dumps(packet, allow_nan=False)
