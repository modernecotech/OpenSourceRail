from decimal import Decimal

from engineering.sourcing.closure_civil_cost import (
    WAGE_CATEGORIES,
    _annual_region_case,
    load_annual_source,
)
from engineering.station_rail import ROOT


def _mid_hour(case):
    return next(
        row for row in case["worker_category_rate_sensitivities"]["skilled"]["scenarios"]
        if row["concrete_labour_hours_per_m3"] == "4"
        and row["reinforcement_cut_bend_hours_per_t"] == "8"
    )


def test_official_annual_wage_and_material_source_is_sealed():
    source = load_annual_source(ROOT)

    assert source["source_record_id"] == "edffd3578155cf7d1cebedc8de7f0cfead2c0c949c17a78a1758e146a80fed86"
    assert source["source"]["document_sha256"] == "02baf7dc75bf1342278206231327c9a998648bf726bc415c6ef0e9c9830f58ef"
    assert set(source["selected_governorates"]) == {"Baghdad", "Al-Muthanna"}
    assert set(source["selected_governorates"]["Baghdad"][
        "worker_daily_wages_iqd_per_person"]) == set(WAGE_CATEGORIES)


def test_annual_local_span_material_labour_and_uplift_are_reproducible():
    source = load_annual_source(ROOT)
    quantities = (Decimal("1"), Decimal("1000"))

    baghdad = _annual_region_case("Baghdad", source, *quantities)
    baghdad_mid = _mid_hour(baghdad)
    assert Decimal(baghdad["direct_material_cost_iqd"]) == Decimal("1119850")
    assert baghdad["worker_category_rate_sensitivities"]["skilled"][
        "assumed_hourly_base_wage_iqd_per_person_hour"] == "9375"
    assert Decimal(baghdad_mid["direct_labour_cost_iqd"]) == Decimal("112500")
    assert Decimal(baghdad_mid["unallocated_uplift_iqd"]) == Decimal("246470")
    assert Decimal(baghdad_mid["partial_material_labour_plus_20pct_iqd"]) == Decimal("1478820")
    assert baghdad_mid["installed_cost_iqd"] is None
    assert all(len(line["source_observation_id"]) == 64
               for line in baghdad["material_takeoff"])
    assert len(baghdad["worker_category_rate_sensitivities"]["skilled"][
        "source_observation_id"]) == 64

    muthanna = _annual_region_case("Al-Muthanna", source, *quantities)
    muthanna_mid = _mid_hour(muthanna)
    assert Decimal(muthanna["direct_material_cost_iqd"]) == Decimal("1063550")
    assert muthanna["worker_category_rate_sensitivities"]["skilled"][
        "assumed_hourly_base_wage_iqd_per_person_hour"] == "6875"
    assert Decimal(muthanna_mid["direct_labour_cost_iqd"]) == Decimal("82500")
    assert Decimal(muthanna_mid["unallocated_uplift_iqd"]) == Decimal("229210")
    assert Decimal(muthanna_mid["partial_material_labour_plus_20pct_iqd"]) == Decimal("1375260")
