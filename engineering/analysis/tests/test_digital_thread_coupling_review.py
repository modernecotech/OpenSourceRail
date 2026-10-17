"""Independent coupling audit: mass inventory, equilibrium and stale revisions."""

from copy import deepcopy
from hashlib import sha256
import json
import math

import pytest

from engineering.generative_design import civil_detail, digital_thread


@pytest.fixture(scope="module")
def packet():
    return digital_thread.build(concurrency=1)


def test_each_mass_generation_reaches_only_matching_architecture_and_both_spans(packet):
    rows = packet["coupling"]["records"]
    identities = {
        (r["architecture_id"], r["civil_context"]["span_m"], r["mechanical_variant_id"])
        for r in rows
    }
    assert identities == {
        (architecture, span, generation)
        for architecture in ("LM3", "metro-6car-planning")
        for span in (20.0, 25.0)
        for generation in ("connected-seed", "connected-feedback-2")
    }
    assert len(rows) == len(identities) == 8
    systems = {s["id"]: s for s in packet["domains"]["mechanical"]["systems"]}
    for row in rows:
        system = systems[row["mechanical_system_id"]]
        variant = next(
            v for v in system["variants"] if v["id"] == row["mechanical_variant_id"]
        )
        assert system["configuration_id"] == row["civil_context"]["architecture_id"]
        # Sum only actual net plate/RHS item masses; do not count assembly roots,
        # welding reservations, fixture payload or unresolved fasteners as steel.
        inventory_mass = math.fsum(
            p["specifications"].get("net_geometry_mass_kg", 0.0)
            for p in variant["parts"]
        )
        assert row["modeled_member_mass_per_car_kg"] == pytest.approx(inventory_mass)
        expected_cars = 3 if row["architecture_id"] == "LM3" else 6
        assert row["gross_added_train_mass_kg"] == pytest.approx(
            inventory_mass * expected_cars
        )
        assert row["removed_mass_kg"] is None
        assert row["net_mass_change_kg"] is None
        assert row["adopted"] is False


def test_live_force_first_moment_and_sensitivity_applied_once(packet):
    for row in packet["coupling"]["records"]:
        context = row["civil_context"]
        original = context["parent_source_case"]
        changed = context["source_case"]
        assert len(changed["axles"]) == len(original["axles"])
        factor = (
            original["total_mass_kg"] + row["gross_added_train_mass_kg"]
        ) / original["total_mass_kg"]
        original_force = math.fsum(a["force_n"] for a in original["axles"])
        changed_force = math.fsum(a["force_n"] for a in changed["axles"])
        original_first_moment = math.fsum(
            a["force_n"] * a["x_m"] for a in original["axles"]
        )
        changed_first_moment = math.fsum(
            a["force_n"] * a["x_m"] for a in changed["axles"]
        )
        assert changed_force == pytest.approx(original_force * factor)
        assert changed_first_moment == pytest.approx(original_first_moment * factor)
        assert changed["total_mass_kg"] - original["total_mass_kg"] == pytest.approx(
            row["gross_added_train_mass_kg"]
        )
        applied = context["applied_axles"]
        assert math.fsum(a["force_n"] for a in applied) == pytest.approx(
            changed_force * context["force_sensitivity_multiplier"]
        )
        assert [a["id"] for a in applied] == [a["id"] for a in changed["axles"]]
        hash_input = json.dumps(
            changed, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
        assert sha256(hash_input).hexdigest() == context["source_case_sha256"]
        # Already coupled contexts cannot become a fresh base and accumulate
        # the same proposed gross frame mass a second time.
        with pytest.raises(ValueError, match="original uncoupled"):
            civil_detail.coupled_context(context, row["gross_added_train_mass_kg"])


def test_feedback_foundation_force_and_moment_balance_remain_physical(packet):
    for row in packet["coupling"]["records"]:
        assert 1 <= len(row["attempts"]) <= 3
        for attempt in row["attempts"]:
            assessment = attempt["assessment"]
            B = assessment["variables"]["footing_width_m"]
            m = assessment["metrics"]
            f = m["foundation"]
            if f["full_contact"]:
                low = f["linear_minimum_pressure_pa"]
                high = f["linear_maximum_pressure_pa"]
                assert (low + high) * B**2 / 2 == pytest.approx(
                    m["foundation_vertical_n"]
                )
                assert (high - low) * B**3 / 12 == pytest.approx(
                    m["foundation_moment_nm"]
                )
            elif f["equilibrium_possible"]:
                b = f["compression_contact_length_m"]
                assert f[
                    "compression_maximum_pressure_pa"
                ] * b * B / 2 == pytest.approx(m["foundation_vertical_n"])
                assert m["foundation_vertical_n"] * (B / 2 - b / 3) == pytest.approx(
                    m["foundation_moment_nm"]
                )
            assert (
                assessment["source_case_sha256"]
                == row["civil_context"]["source_case_sha256"]
            )
            assert assessment["manufacturing_release"] is False
            assert any(
                c["id"] == "site_ground" and c["state"] == "unknown"
                for c in assessment["checks"]
            )


@pytest.mark.parametrize(
    "field, replacement",
    [
        ("mechanical_configuration_sha256", "0" * 64),
        ("gross_added_train_mass_kg", 1.0),
        ("removed_mass_kg", 100.0),
        ("adopted", True),
    ],
)
def test_public_validation_rejects_inconsistent_parent_coupling(
    packet, field, replacement
):
    altered = deepcopy(packet)
    altered["coupling"]["records"][0][field] = replacement
    with pytest.raises(ValueError):
        digital_thread.validate(altered)


def test_public_validation_rejects_stale_variant_configuration_hash(packet):
    altered = deepcopy(packet)
    variant = altered["domains"]["mechanical"]["systems"][0]["variants"][0]
    variant["parameters"]["plate_thickness_m"] += 0.001
    with pytest.raises(ValueError):
        digital_thread.validate(altered)


@pytest.mark.parametrize(
    "mutation", ["missing-context", "axle-force", "foundation-force", "generation"]
)
def test_public_validation_rejects_incomplete_or_relabelled_civil_evidence(
    packet, mutation
):
    altered = deepcopy(packet)
    rows = altered["coupling"]["records"]
    if mutation == "missing-context":
        rows.pop()
    elif mutation == "axle-force":
        rows[0]["civil_context"]["applied_axles"][0]["force_n"] *= 2
    elif mutation == "foundation-force":
        rows[0]["attempts"][0]["assessment"]["metrics"]["foundation_vertical_n"] += 1000
    else:
        rows[0]["attempts"][0]["generation"] = 99
    with pytest.raises(ValueError):
        digital_thread.validate(altered)


def test_reference_twin_does_not_inherit_experimental_vehicle_or_passage_acceptance(
    packet,
):
    reference = packet["reference_twin"]
    review = reference["review"]
    variant_hashes = {
        v["configuration_sha256"]
        for p in packet["domains"].values()
        for s in p["systems"]
        for v in s["variants"]
    }
    assert review["configuration_sha256"] not in variant_hashes
    assert review["physical_validation"] is False
    assert review["production_released"] is False
    assert review["complete_dynamic_passage_qualified"] is False
    assert review["contact_domain_issue_resolved"] is False
    assert (
        "released profiles and complete six-car coupled passage"
        in review["remaining_gates"]
    )
    assert (
        packet["telemetry_contract"]["configuration_sha256"]
        == review["configuration_sha256"]
    )
    assert packet["physical_validation"] is False
