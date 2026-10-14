"""Independent axial/beam/group equations exercise the conditional soil solver."""

from copy import deepcopy
import math

import numpy as np
import pytest

from engineering.design_engine.contracts import fingerprint
from engineering.design_engine.foundation_response import input_template, assess_foundation_response
from engineering.analysis.tests.test_design_engine import scope


SOURCE = dict(reference="synthetic analytical verification fixture; no site data", sha256="a"*64, basis="research-assumption")


def q(value, unit):
    return dict(value=value, unit=unit, source=dict(SOURCE))


def contract(count=1):
    length, radius, density = 10., .4, 2500.
    coordinates = [(0., 0.)] if count == 1 else [(-1., -1.), (-1., 1.), (1., -1.), (1., 1.)]
    mass = math.pi*radius**2*length*density
    parts = [dict(id="foundation-cap-0", properties=dict(cg_m=[0., 0., 0.]),
                  manufacturing=dict(primitives=[dict(kind="box", dimensions_m=[4., 4., .8])]))]
    for i, (x, y) in enumerate(coordinates):
        parts.append(dict(id=f"pile-0-{i}",
                          properties=dict(cg_m=[x, y, -length/2], mass_kg=mass,
                                          inertia_tensor_kg_m2=np.diag([mass*(3*radius**2+length**2)/12]*2+[mass*radius**2/2]).tolist()),
                          manufacturing=dict(primitives=[dict(kind="perforated-cylinder", axis="z", radius_m=radius,
                                                             length_m=length, centre_m=[x, y, -length/2], holes_xy_m=[])])))
    return dict(parts=parts)


def inputs(model, *, force=(0., 0., -1e5), count_cycles=0):
    data = input_template(model, scope())
    data["basis"] = "Synthetic linear beam/Winkler verification; no ground calibration or physical acceptance."
    data["elements_per_pile"] = 8
    radius, young = .4, 30e9
    area, inertia = math.pi*radius**2, math.pi*radius**4/4
    shear = young/(2*1.2)
    for row in data["pile_parameters"]:
        row["section_rigidities"] = dict(EA_n=q(young*area, "N"), EIy_nm2=q(young*inertia, "N m2"),
                                         EIz_nm2=q(young*inertia, "N m2"), GJ_nm2=q(shear*2*inertia, "N m2"),
                                         GAy_n=q(5/6*shear*area, "N"), GAz_n=q(5/6*shear*area, "N"))
        row["soil"] = dict(axial_per_length=q(0., "N/m2"), lateral_x_per_length=q(0., "N/m2"), lateral_y_per_length=q(0., "N/m2"),
                           toe_translation=[q(1e12, "N/m") for _ in range(3)], toe_rotation=[q(1e12, "N m/rad") for _ in range(3)])
        row["group_stiffness_factor"] = q(1., "1")
        row["cyclic"] = dict(degradation_per_cycle=q(0., "1"), minimum_stiffness_fraction=q(.2, "1"))
    data["load_cases"][0].update(force=[q(v, "N") for v in force], moment=[q(0., "N m") for _ in range(3)], cycles=q(count_cycles, "1"))
    return data


def test_missing_values_are_unknown_and_template_maps_actual_physical_ids():
    model = contract(4)
    template = input_template(model, scope())
    assert template["cap_groups"] == [dict(physical_cap_id="foundation-cap-0", pile_ids=[f"pile-0-{i}" for i in range(4)])]
    for data in (None, template):
        result = assess_foundation_response(model, data, context=scope())
        assert result["state"] == "unknown" and result["missing_inputs"]
        assert result["physical_release"] is False and result["foundation_qualified"] is False


def test_single_pile_axial_response_equals_bar_and_toe_compliance():
    model = contract()
    data = inputs(model)
    result = assess_foundation_response(model, data, context=scope())
    case = result["cases"][0]
    ea = data["pile_parameters"][0]["section_rigidities"]["EA_n"]["value"]
    assert case["settlement_m"] == pytest.approx(1e5*(10/ea+1e-12), rel=1e-10)
    assert case["soil_resultant_si"][2] == pytest.approx(1e5, rel=1e-10)
    assert case["numerical_equilibrium"] == "passed"
    assert result["state"] == "conditional"
    assert result["resistance"] == result["consolidation_settlement"] == result["cyclic_capacity"] == "unknown"
    assert not result["foundation_qualified"] and not result["source_files_verified"]


def test_single_pile_lateral_response_equals_independent_timoshenko_cantilever():
    model = contract()
    data = inputs(model, force=(1e4, 0., 0.))
    case = assess_foundation_response(model, data, context=scope())["cases"][0]
    section = data["pile_parameters"][0]["section_rigidities"]
    ei, ga, length, force = section["EIy_nm2"]["value"], section["GAz_n"]["value"], 10., 1e4
    displacement = force*(length**3/(3*ei)+length/ga+1e-12+length**2/1e12)
    rotation = force*(length**2/(2*ei)+length/1e12)
    assert case["cap_displacement_m"][0] == pytest.approx(displacement, rel=1e-9)
    assert case["cap_rotation_rad"][1] == pytest.approx(rotation, rel=1e-9)
    assert case["force_balance_relative_error"] < 1e-9
    assert case["moment_balance_relative_error"] < 1e-6


def test_symmetric_four_pile_group_shares_load_and_settlement():
    model = contract(4)
    data = inputs(model)
    case = assess_foundation_response(model, data, context=scope())["cases"][0]
    ea = data["pile_parameters"][0]["section_rigidities"]["EA_n"]["value"]
    assert case["settlement_m"] == pytest.approx(1e5/4*(10/ea+1e-12), rel=1e-9)
    assert [r["head_force_moment_si"][2] for r in case["piles"]] == pytest.approx([-25000.]*4, rel=1e-9)
    assert np.linalg.norm(case["cap_rotation_rad"]) < 1e-12
    assert {r["physical_part_id"] for r in case["piles"]} == {f"pile-0-{i}" for i in range(4)}


def test_group_overturning_couples_cap_rotation_to_opposed_axial_pile_forces():
    model = contract(4)
    data = inputs(model, force=(0., 0., 0.))
    data["load_cases"][0]["moment"][1] = q(1e5, "N m")
    case = assess_foundation_response(model, data, context=scope())["cases"][0]
    section = data["pile_parameters"][0]["section_rigidities"]
    ea, ei = section["EA_n"]["value"], section["EIy_nm2"]["value"]
    axial_stiffness = 1/(10/ea+1e-12)
    pile_moment_stiffness = 1/(10/ei+1e-12)
    # Four pile bending moments plus the axial-force couple at x=+/-1 m.
    rotation = 1e5/(4*(pile_moment_stiffness+axial_stiffness))
    assert case["cap_rotation_rad"][1] == pytest.approx(rotation, rel=1e-9)
    axial = [p["head_force_moment_si"][2] for p in case["piles"]]
    assert axial == pytest.approx([axial_stiffness*rotation]*2+[-axial_stiffness*rotation]*2, rel=1e-9)
    assert case["soil_resultant_si"][4] == pytest.approx(-1e5, rel=1e-9)


def test_entered_cyclic_degradation_changes_soil_response_without_inventing_capacity():
    model = contract()
    data = inputs(model, count_cycles=100)
    pile = data["pile_parameters"][0]
    pile["soil"]["toe_translation"][2] = q(1e6, "N/m")
    pile["cyclic"]["degradation_per_cycle"] = q(.01, "1")
    result = assess_foundation_response(model, data, context=scope())
    retained = .2+.8*math.exp(-1)
    ea = pile["section_rigidities"]["EA_n"]["value"]
    assert result["cases"][0]["settlement_m"] == pytest.approx(1e5*(10/ea+1/(1e6*retained)), rel=1e-8)
    assert result["cases"][0]["piles"][0]["cyclic_stiffness_fraction"] == pytest.approx(retained)
    assert result["cyclic_capacity"] == "unknown"


def test_scope_units_source_hash_and_physical_correspondence_are_enforced():
    model = contract()
    original = inputs(model)
    mutations = [
        lambda d: d["identity"].update(project="another-project"),
        lambda d: d.update(contract_sha256="b"*64),
        lambda d: d["pile_parameters"][0]["section_rigidities"]["EA_n"].update(unit="kN"),
        lambda d: d["pile_parameters"][0]["section_rigidities"]["EA_n"]["source"].update(sha256="wrong"),
        lambda d: d["cap_groups"][0]["pile_ids"].append("pile-not-in-contract"),
        lambda d: d["pile_parameters"].append(deepcopy(d["pile_parameters"][0])),
    ]
    for mutate in mutations:
        data = deepcopy(original)
        mutate(data)
        with pytest.raises(ValueError):
            assess_foundation_response(model, data, context=scope())


def test_actual_viaduct_geometry_has_two_complete_groups_and_blank_inputs():
    from engineering.design_consistency.demonstrators import viaduct
    model = viaduct()
    template = input_template(model, scope())
    assert len(template["cap_groups"]) == 2
    assert all(len(group["pile_ids"]) == 4 for group in template["cap_groups"])
    assert template["unmapped_physical_pile_ids"] == []
    assert assess_foundation_response(model, template, context=scope())["state"] == "unknown"
