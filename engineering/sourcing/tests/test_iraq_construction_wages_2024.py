from pathlib import Path

from engineering.sourcing.catalogue import load_catalogue


SEED = Path(__file__).resolve().parents[1] / "data/iraq-construction-wages-2024.json"


def test_2024_cso_construction_wages_are_historical_source_bound_statistics():
    rows = load_catalogue([SEED])
    sources = {row["source_key"]: row for row in rows if row["kind"] == "source"}
    benchmarks = {row["benchmark_key"]: row for row in rows if row["kind"] == "benchmark"}
    source = sources["iraq.cso.construction-wages-2024"]

    assert len(rows) == 91
    assert source["source_kind"] == "national_statistic"
    assert source["observation_period"] == "2024 annual construction-worker wage table"
    assert source["table"] == "Table 7: Average worker wages by governorate for 2024"
    assert source["printed_page"] == 9
    assert "Kurdistan Region" in source["geographic_scope"]
    assert "not used in current candidate cost estimates" in source["methodology"]
    assert len(benchmarks) == 90

    expected = {
        "iq-cso-2024:baghdad:wage:skilled:hour-8h-day": (75000, "9375"),
        "iq-cso-2024:baghdad:wage:semi-skilled:hour-8h-day": (35833, "4479.125"),
        "iq-cso-2024:basrah:wage:skilled:hour-8h-day": (50000, "6250"),
    }
    for key, (daily, hourly) in expected.items():
        row = benchmarks[key]
        assert row["source_published_rate_iqd_per_work_day"] == daily
        assert row["unit_price"] == hourly
        assert row["quantity_unit"] == "h"
        assert row["currency"] == "IQD"
        assert row["employer_burden_included"] is False
        assert row["supplier_quote"] is False
        assert row["target_installed_rate"] is False

    assert all(row["source_id"] == source["record_id"] for row in benchmarks.values())
    assert not [row for row in rows if row["kind"] in {"product", "offer"}]
