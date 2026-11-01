from copy import deepcopy

import pytest

from engineering.design_search import civil_shape_geometry as g
from engineering.station_rail.common import identity


def test_reference_box_matches_independent_hollow_rectangle_and_surface():
    q = g.quantities(g.generate("reference_box"))
    area = 2*1.4-(2-2*.18)*(1.4-2*.18)
    inertia = (2*1.4**3-(2-2*.18)*(1.4-2*.18)**3)/12
    concrete = q["by_material"]["research_concrete"]
    assert concrete["volume_m3"] == pytest.approx(20*area)
    assert concrete["mass_kg"] == pytest.approx(20*area*2500)
    assert concrete["centroid_m"] == pytest.approx([10,0,-.7])
    assert concrete["I_y_m4"] == pytest.approx(inertia)
    # Open ends retain hollow opening; internal longitudinal faces count.
    surface = 20*(2*(2+1.4)+2*((2-.36)+(1.4-.36)))+2*area
    assert concrete["material_boundary_surface_m2"] == pytest.approx(surface)


def test_real_families_and_profiles_change_physical_geometry_and_preserve_interfaces():
    rows = [g.generate(f,p) for f in g.FAMILIES for p in g.PROFILES]
    assert len(rows)==len({r["candidate_id"] for r in rows})==18
    for r in rows:
        assert r["span_m"]==20 and r["deck_width_m"]==2
        q = g.quantities(r)
        assert q["candidate_id"]==r["candidate_id"]
        assert q["total_nominal_stock_mass_kg"]>0
        assert q["complete_installed_mass_kg"] is None
        assert q["physical_accepted"] is q["engineering_accepted"] is False
    variable = g.generate("variable_depth_box")
    q = g.quantities(variable)
    expected = sum((2*d-(2-.32)*(d-.32)) for d in
        ((.85+.55*4*((i+.5)/20)*(1-(i+.5)/20)) for i in range(20)))
    assert q["by_material"]["research_concrete"]["volume_m3"]==pytest.approx(expected)
    assert len({r["gross_I_y_m4"] for r in q["section_stations"]})>5
    assert q["discretisation_provenance"]["smooth_surface_equivalence_claimed"] is False


def test_subdividing_a_prism_preserves_mass_inertia_and_union_surface():
    r = g.generate("reference_box");q = g.quantities(r)
    a,b = deepcopy(r["cells"][0]),deepcopy(r["cells"][0])
    a["x_end_m"] = 10.;b["id"] = "cell-001";b["x_start_m"] = 10.
    r["cells"] = [a,b]
    r["candidate_id"] = identity({k:v for k,v in r.items() if k!="candidate_id"})
    subdivided = g.quantities(r)
    for key in ("total_nominal_volume_m3","total_nominal_stock_mass_kg",
            "concrete_contact_surface_m2","minimum_gross_bending_I_y_m4"):
        assert subdivided[key] == pytest.approx(q[key],abs=1e-10)


def test_ribs_sloped_webs_and_hybrid_are_substantive_geometry():
    ribs = g.generate("ribbed_u")
    assert {len(c["sections"]) for c in ribs["cells"]}=={3,4}
    folded = g.generate("folded_plate")
    inclined = folded["cells"][0]["sections"][2]["polygon_yz_m"]
    assert any(a[0]!=b[0] and a[1]!=b[1] for a,b in zip(inclined,inclined[1:]+inclined[:1]))
    hybrid = g.quantities(g.generate("hybrid_steel_concrete"))
    assert set(hybrid["by_material"])=={"research_concrete","structural_steel"}
    assert hybrid["by_material"]["research_concrete"]["volume_m3"]==pytest.approx(20*2*.18)
    assert hybrid["by_material"]["structural_steel"]["volume_m3"]==pytest.approx(20*2*(.3*.025+.4*.025+.016*(1.2-.18-.05)))
    assert all(r["composite_stiffness_credit"] is False for r in hybrid["section_stations"])
    following = g.generate("load_following_ribs")
    assert following["cells"][0]["sections"][1]["polygon_yz_m"]!=following["cells"][9]["sections"][1]["polygon_yz_m"]


def test_collision_dimensions_sources_and_acceptance_are_not_silently_ignored():
    original = g.generate("reference_box")
    for mutate,match in (
        (lambda r:r["cells"][0]["sections"].append(dict(r["cells"][0]["sections"][0],id="duplicate")),"Overlapping"),
        (lambda r:r["cells"][0].update(x_end_m=-1),"positive prism"),
        (lambda r:r["materials"]["research_concrete"].update(density_kg_m3=-1),"Finite positive"),
        (lambda r:r.update(physical_accepted=True),"cannot grant")):
        r = deepcopy(original);mutate(r)
        r["candidate_id"] = identity({k:v for k,v in r.items() if k!="candidate_id"})
        with pytest.raises(ValueError,match=match):g.quantities(r)
    changed = deepcopy(original);changed["cells"][0]["sections"][0]["polygon_yz_m"][0][0]+=.01
    with pytest.raises(ValueError,match="Canonical"):g.quantities(changed)
    changed = deepcopy(original);changed["materials"]["research_concrete"]["density_kg_m3"]=float("nan")
    with pytest.raises(ValueError):g.quantities(changed)


def test_multiply_wound_duplicate_and_self_crossing_rings_cannot_inflate_stock():
    original = g.generate("reference_box")
    polygon = original["cells"][0]["sections"][0]["polygon_yz_m"]
    bad_rings = [polygon*2, polygon[:2]+[polygon[0]]+polygon[2:],
        [polygon[0],polygon[2],polygon[1],polygon[3]],
        [[0,0],[1,0],[.5,0],[.5,1],[0,1]]]
    for bad in bad_rings:
        r = deepcopy(original)
        r["cells"][0]["sections"][0]["polygon_yz_m"] = bad
        r["candidate_id"] = identity({k:v for k,v in r.items() if k!="candidate_id"})
        with pytest.raises(ValueError):g.quantities(r)
    # Closing once is a harmless serialization convention, never another pass.
    assert g._properties(polygon+[polygon[0]])==g._properties(polygon)
