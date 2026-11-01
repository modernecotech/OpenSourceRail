from copy import deepcopy
from math import fsum

import pytest

from engineering.design_search import civil_section_model as model
from engineering.design_search import civil_shape_geometry as geometry
from engineering.station_rail.common import identity


MODULI = {"research_concrete": 35e9, "structural_steel": 200e9}


def test_reference_box_matches_independent_hollow_rectangle():
    candidate = geometry.generate("reference_box")
    value, = model.models(candidate, MODULI)
    cell, = value["cells"]
    assert value["name"] == "full-section-uncracked"
    assert cell["EI_Nm2"] == pytest.approx(35e9*.30360192)
    assert cell["mass_per_length_kg_m"] == pytest.approx(54720/20)
    assert all(f["neutral_axis_z_m"] == pytest.approx(-.7) for f in cell["section_fibers"])
    assert value["evaluation_id"] == identity({k:v for k,v in value.items() if k!="evaluation_id"})
    assert value["candidate_id"] == candidate["candidate_id"]
    assert value["complete_installed_mass_kg"] is None
    assert all(value[key] is False for key in model.FLAGS)


def _manual_hybrid(steel_only=False):
    # Independent rectangle dimensions: (width, height, centroid_z, E, count).
    rectangles = [(.3,.025,-.1925,200e9,2), (.4,.025,-1.1875,200e9,2),
        (.016,.97,-.69,200e9,2)]
    if not steel_only:
        rectangles.append((2.,.18,-.09,35e9,1))
    ea = fsum(b*h*e*n for b,h,z,e,n in rectangles)
    neutral = fsum(b*h*z*e*n for b,h,z,e,n in rectangles)/ea
    ei = fsum(e*n*(b*h**3/12+b*h*(z-neutral)**2) for b,h,z,e,n in rectangles)
    return neutral, ei


def test_hybrid_matches_independent_rectangles_and_retains_concrete_gravity():
    candidate = geometry.generate("hybrid_steel_concrete")
    steel, full = model.models(candidate, MODULI)
    assert [steel["name"], full["name"]] == ["steel-only-longitudinal", "perfect-bond-uncracked"]
    for value, steel_only in ((steel,True),(full,False)):
        neutral, ei = _manual_hybrid(steel_only)
        cell, = value["cells"]
        assert cell["EI_Nm2"] == pytest.approx(ei)
        assert all(f["neutral_axis_z_m"] == pytest.approx(neutral) for f in cell["section_fibers"])
        assert cell["mass_per_length_kg_m"] == pytest.approx(28368.28/20)
    assert steel["cells"][0]["EI_Nm2"] < full["cells"][0]["EI_Nm2"]
    assert {f["material"] for f in steel["cells"][0]["section_fibers"]} == {"structural_steel"}
    assert {f["material"] for f in full["cells"][0]["section_fibers"]} == set(MODULI)


@pytest.mark.parametrize("moduli", [
    {"research_concrete":35e9},
    dict(MODULI, unknown_material=1e9),
    dict(MODULI, research_concrete=0),
    dict(MODULI, research_concrete=-1),
    dict(MODULI, structural_steel=float("nan")),
    dict(MODULI, structural_steel=float("inf")),
    dict(MODULI, structural_steel=True),
    dict(MODULI, structural_steel=10**500),
])
def test_missing_extra_or_invalid_moduli_are_not_zero_stiffness(moduli):
    with pytest.raises(ValueError, match="exact declared material coverage"):
        model.models(geometry.generate("reference_box"), moduli)


def test_modulus_revision_changes_evaluation_only_and_does_not_mutate_inputs():
    candidate = geometry.generate("hybrid_steel_concrete")
    original = deepcopy(candidate)
    before = model.models(candidate, MODULI)
    after = model.models(candidate, {key:2*value for key,value in MODULI.items()})
    assert candidate == original
    for a,b in zip(before,after):
        assert a["candidate_id"] == b["candidate_id"] == candidate["candidate_id"]
        assert a["evaluation_id"] != b["evaluation_id"]
        assert a["cells"][0]["mass_per_length_kg_m"] == b["cells"][0]["mass_per_length_kg_m"]
        assert b["cells"][0]["EI_Nm2"] == pytest.approx(2*a["cells"][0]["EI_Nm2"])


@pytest.mark.parametrize("family", geometry.FAMILIES)
@pytest.mark.parametrize("profile", geometry.PROFILES)
def test_models_preserve_exact_cells_and_all_nominal_weight(family, profile):
    candidate = geometry.generate(family, profile)
    quantity = geometry.quantities(candidate)
    for value in model.models(candidate, MODULI):
        assert [(c["x_start_m"],c["x_end_m"]) for c in value["cells"]] == [
            (c["x_start_m"],c["x_end_m"]) for c in candidate["cells"]]
        mass = fsum(c["mass_per_length_kg_m"]*(c["x_end_m"]-c["x_start_m"]) for c in value["cells"])
        assert mass == pytest.approx(quantity["total_nominal_stock_mass_kg"])
        assert value["source_quantity_evaluation_id"] == quantity["evaluation_id"]


def test_modified_unsealed_geometry_is_rejected():
    candidate = geometry.generate("reference_box")
    candidate["cells"][0]["x_end_m"] = 19.
    with pytest.raises(ValueError, match="Canonical"):
        model.models(candidate, MODULI)
