import pytest
from cities.Baghdad import airport_integration
from cities.Baghdad.engineering.prototype import car, weights


def test_moving_span_exact_interior_extremum_and_overhang():
    r = weights.moving_span([("a", 0, 100)], 9.5, 0.25)
    assert r["max_moment"]["value"] == pytest.approx(100 * 9.5 / 4, abs=1e-6)
    assert r["max_moment"]["pose"]["section_x_m"] == pytest.approx(4.75)
    assert r["min_moment"]["value"] == pytest.approx(-25)
    assert r["min_reaction"]["value"] == pytest.approx(-100 * 0.25 / 9.5, abs=1e-6)


def test_axle_and_group_reconciliation_and_new_load_case(tmp_path):
    parent = airport_integration.build()
    record = car.build(parent)
    f = weights.form(record)
    assert weights.assess(record, f)["opening"] is None
    (tmp_path / "trial.txt").write_bytes(b"Synthetic load regression")
    f["documents"]["trial.txt"] = {
        "sha256": car.sha((tmp_path / "trial.txt").read_bytes()),
        "date": "2026-11-23",
        "issuer": "test",
    }
    kg = [35000, 22000, 25000, 28000, 12000, 9000, 72000]
    for row, amount in zip(f["mass_groups"]["train_mass_groups"].values(), kg, strict=True):
        row.update(kg=amount, evidence="trial.txt")
    gross = sum(kg)
    tare = sum(kg[:-1])
    power = weights.assess(record, f, directory=tmp_path, service=parent["service"])
    assert power["opening"]["power"]["vehicle"]["mass_t"] == pytest.approx(gross / 1000)
    assert power["axle_civil"] is None
    scales = f["axle_weighing"]
    scales.update(
        tare_document="trial.txt",
        loaded_document="trial.txt",
        balance_limit_document="trial.txt",
        permitted_total_discrepancy_kg=1,
    )
    partial = weights.assess(record, f, directory=tmp_path)
    assert partial["opening"] is None and "C1-A1.loaded_kg" in partial["missing"]
    for i, row in enumerate(scales["readings"].values()):
        row.update(tare_kg=tare / 24, loaded_kg=gross / 24 + (1000 if i < 4 else -200))
    full = weights.assess(record, f, directory=tmp_path, service=parent["service"])
    assert full["opening"]["candidate_id"] != power["opening"]["candidate_id"]
    assert (
        full["axle_civil"]["gravity_envelope"]["max_moment"]["value"]
        > record["civil"]["moving_load"]["max_live_moment_knm_sampled"]
    )
    assert (
        full["finance"]["market_scenarios"]["central"]["capital_usd_m"]
        > record["finance"]["market_scenarios"]["central"]["capital_usd_m"]
    )
    scales["readings"]["C1-A1"]["loaded_kg"] += 3
    with pytest.raises(ValueError, match="balance tolerance"):
        weights.assess(record, f, directory=tmp_path)
    (tmp_path / "trial.txt").write_bytes(b"changed")
    with pytest.raises(ValueError, match="attachment"):
        weights.assess(record, f, directory=tmp_path)
