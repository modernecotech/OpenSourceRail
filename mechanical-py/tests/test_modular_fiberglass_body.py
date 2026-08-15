from __future__ import annotations

from osr_mech.rolling_stock.modular_fiberglass_body import (
    CLIPS_PER_MODULE,
    END_RING_TRANSITION_MM,
    MODULES_PER_CAR,
    MODULE_WIDTH_MM,
    cladding_bays,
    design_manifest,
    fiberglass_cladding_system,
    one_day_trainset_assembly_plan,
    write_design_pack,
)


def _labels(part) -> list[str]:
    labels = [getattr(part, "label", "")]
    for child in getattr(part, "children", []):
        labels.extend(_labels(child))
    return labels


def test_light_metro_car_uses_sixteen_exact_one_metre_bays() -> None:
    bays = cladding_bays(16_500.0)
    assert len(bays) == 16
    assert all(bay.width_mm == MODULE_WIDTH_MM for bay in bays)
    assert bays[0].x_center_mm == -7_500.0
    assert bays[-1].x_center_mm == 7_500.0
    assert END_RING_TRANSITION_MM == 250.0


def test_cladding_cad_contains_side_roof_clips_and_dry_seals() -> None:
    cladding = fiberglass_cladding_system(
        body_length_mm=16_500.0,
        body_width_mm=2_850.0,
        body_height_mm=3_450.0,
        door_centres_mm=(-2_750.0, 2_750.0),
        door_width_mm=1_400.0,
        door_sill_mm=350.0,
        door_height_mm=2_000.0,
        window_zones=((-5_850.0, 3_600.0), (0.0, 2_900.0), (5_850.0, 3_600.0)),
        window_sill_mm=1_500.0,
        window_height_mm=900.0,
    )
    labels = _labels(cladding)
    assert sum("clip-on fiberglass side module" in label for label in labels) == 32
    assert sum("clip-on fiberglass roof module" in label for label in labels) == 16
    assert sum("Captive keyed" in label for label in labels) == MODULES_PER_CAR * CLIPS_PER_MODULE
    assert "Dry EPDM compression seals and drain joints" in labels


def test_three_car_exterior_body_is_installable_in_one_shift() -> None:
    plan = one_day_trainset_assembly_plan()
    manifest = design_manifest()
    assert sum(phase.elapsed_hours for phase in plan) == 8.0
    assert manifest["assembly_elapsed_hours"] == 8.0
    assert manifest["modules_per_three_car_trainset"] == 144
    assert "no production adhesive cure" in manifest["seal"]
    assert manifest["structural_role"].startswith("non-structural")


def test_design_pack_writes_machine_and_human_readable_artifacts(tmp_path) -> None:
    json_path, markdown_path = write_design_pack(tmp_path)
    assert json_path.exists()
    assert markdown_path.exists()
    assert '"design_id": "LM3-BDY-160"' in json_path.read_text()
    assert "One-shift route" in markdown_path.read_text()
