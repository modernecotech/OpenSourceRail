from copy import deepcopy
import json

import pytest

from engineering.design_search import compact_launch as c
from engineering.station_rail.common import identity, digest, encoded


@pytest.fixture(scope="module")
def result():
    return c.evaluate()


def test_reference_zones_keep_full_train_and_catalogue_scopes_separate(result):
    z=result["reference_zone_decomposition"]
    assert z["outgoing_m"]==496.
    assert z["receiving_m"]==pytest.approx(329.004654,abs=1e-5)
    assert z["exact_shared_m"]==z["outgoing_m"]+z["receiving_m"]
    assert z["catalogue_m"]==900.
    assert len(result["cases"])==15
    assert all(result[k] is False for k in c.FLAGS)
    assert result["normal_accounted_mass_kg_per_car"]>22000
    assert result["rotating_stock"]["equivalent_inertial_mass_kg_per_car"]>0


def test_faster_acceleration_reduces_distance_but_increases_force(result):
    rows=[x for x in result["cases"] if x["speed_m_s"]==20]
    assert [x["constant_acceleration_distance_m"] for x in rows]==pytest.approx([500,333.333333,250,200,166.666667])
    assert all(a["profile"]["peak_launch_force_N_per_car"]<b["profile"]["peak_launch_force_N_per_car"] for a,b in zip(rows,rows[1:]))
    for row in rows:
        p=row["profile"]
        assert p["phase_distance_residual_m"]==pytest.approx(0,abs=1e-8)
        assert p["longitudinal_energy_residual_J_per_car"]==pytest.approx(0,abs=1e-7)
        assert p["peak_launch_power_W_per_car"]==p["peak_launch_force_N_per_car"]*20
        compact=row["mechanisms"][1]["quantities"]
        assert compact["full_train_fin_launch_envelope_m"]==pytest.approx(row["constant_acceleration_distance_m"]+96.5)


def test_jerk_trapezoidal_and_triangular_closed_forms():
    bound=c.jerk_bound(20,1,.5)
    assert bound["total_time_s"]==22
    assert bound["distance_m"]==220
    assert not bound["triangular_acceleration"]
    bound=c.jerk_bound(1,2,.5)
    assert bound["triangular_acceleration"]
    assert bound["distance_m"]==pytest.approx(2**.5)
    for args in ((0,1,1),(1,float("nan"),1),(1,1,-1)):
        with pytest.raises(ValueError):c.jerk_bound(*args)


def test_motor_contact_winch_and_driven_weight_bounds_are_quantity_only(result):
    row=next(x for x in result["cases"] if x["speed_m_s"]==20 and x["acceleration_m_s2"]==1)
    mechanisms={x["mechanism"]:x for x in row["mechanisms"]}
    rollers=mechanisms["station-pinch-rollers"];q=rollers["quantities"]
    assert q["minimum_motor_count"]*250000>=q["required_shaft_power_W"]
    assert (q["minimum_motor_count"]-1)*250000<q["required_shaft_power_W"]
    assert all(r["total_N"]*r["mu"]==pytest.approx(rollers["required_train_force_N"]) for r in q["total_contact_normal_force_N"])
    winch=mechanisms["short-stroke-winch-capstan"]["quantities"]
    assert winch["minimum_drum_torque_Nm"]==pytest.approx(rollers["required_train_force_N"]*.5)
    assert [x["constant_acceleration_fits"] for x in winch["stroke_screens"]]==[False,True]
    assert winch["stroke_screens"][1]["jerk_cases_fit"]==[False,False]
    wheel=mechanisms["rotary-wheel-traction-short-feed"]["quantities"]
    assert not any(x["two_bogies_necessary_bound_fits"] for x in wheel["required_driven_weight_fractions"])
    assert all(x["complete_installed_cost"] is None and x["added_installed_mass_kg"] is None for x in mechanisms.values())
    assert row["cost_break_even"]["complete_cost_winner"] is None


def test_fresh_immutable_package_replay_and_tamper_rejection(tmp_path):
    output=tmp_path/"run";written=c.run(output)
    assert c.verify(output)["package_id"]==written["package_id"]
    with pytest.raises(ValueError,match="Fresh"):c.run(output)
    result=json.loads((output/"result.json").read_bytes());result["cases"][0]["constant_acceleration_distance_m"]=0
    result.pop("comparison_id");result["comparison_id"]=identity(result)
    (output/"result.json").write_text(json.dumps(result))
    with pytest.raises(ValueError,match="payload differs"):c.verify(output)
    manifest=json.loads((output/"manifest.json").read_bytes());manifest["files"]["result.json"]=digest(output/"result.json")
    manifest.pop("package_id");manifest["package_id"]=identity(manifest)
    (output/"manifest.json").write_bytes(encoded(manifest))
    with pytest.raises(ValueError,match="does not replay"):c.verify(output)
