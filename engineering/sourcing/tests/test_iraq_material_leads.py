from pathlib import Path

from engineering.sourcing.catalogue import load_catalogue

SEED = Path(__file__).resolve().parents[1] / "data/iraq-domestic-material-leads-2026-10.json"


def test_additional_domestic_material_leads_remain_source_only():
    rows = load_catalogue([SEED])
    sources = {row["source_key"]: row for row in rows if row["kind"] == "source"}
    assert set(sources) == {
        "iraq.hemn.eps-factory",
        "iraq.helal.polyurethane-foam",
        "iraq.qatral.aluminium-ingot",
        "iraq.bafra-shakh.eps",
        "iraq.sama-kirkuk.eps-listings",
        "iraq.regaasphalt.aggregate",
        "iraq.hewa.construction-materials",
        "iraq.lafarge-iraq.cement-products",
        "iraq.alpha-steel.rebar-range-2026",
        "iraq.al-kanz.precast-piling",
        "iraq.hadeediraq.rebar-marketplace",
        "iraq.briskey-roj.composite-materials",
        "iraq.diwan-electrical-industries",
        "iraq.rs-alnajaf-electrical-factory",
        "iraq.ibn-majid-heavy-engineering",
        "iraq.haidar-ahmed-mousa.pur-pir-panels",
        "iraq.kanza-iq.sandwich-panel-lines",
        "iraq.erbil-copper-cable",
    }
    assert len(rows) == 18
    assert not [row for row in rows if row["kind"] in {"product", "offer", "benchmark"}]
    assert "10 tonnes/day" in sources["iraq.hemn.eps-factory"]["access"]
    assert "12 to 45 kg/m3" in sources["iraq.helal.polyurethane-foam"]["access"]
    assert "not presumed interchangeable" in sources["iraq.hemn.eps-factory"]["access"]
    assert "no offer or candidate match" in sources["iraq.qatral.aluminium-ingot"]["access"]
    assert "6 to 30 kg/m3" in sources["iraq.bafra-shakh.eps"]["access"]
    assert "no product offer" in sources["iraq.sama-kirkuk.eps-listings"]["access"]
    assert "three crushing plants" in sources["iraq.regaasphalt.aggregate"]["access"]
    assert "does not establish Iraqi extraction/origin" in sources["iraq.hewa.construction-materials"]["access"]
    assert "sulfate-resistant cement" in sources["iraq.lafarge-iraq.cement-products"]["access"]
    assert "10–32 mm" in sources["iraq.alpha-steel.rebar-range-2026"]["access"]
    assert "supplier lead only" in sources["iraq.alpha-steel.rebar-range-2026"]["access"]
    assert "precast concrete pile manufacture" in sources["iraq.al-kanz.precast-piling"]["access"]
    assert "indicative supplier prices, not a Hadeed offer" in sources["iraq.hadeediraq.rebar-marketplace"]["access"]
    assert "no offer or product match is created" in sources["iraq.hadeediraq.rebar-marketplace"]["access"]
    assert "not a qualified passenger-body core" in sources["iraq.haidar-ahmed-mousa.pur-pir-panels"]["access"]
    assert "dated company-profile document" in sources["iraq.kanza-iq.sandwich-panel-lines"]["access"]


def test_erbil_copper_source_is_only_a_candidate_for_future_conductor_inquiry():
    rows = load_catalogue([SEED])
    source = next(row for row in rows if row.get("source_key") == "iraq.erbil-copper-cable")
    assert source["kind"] == "source"
    assert "copper rod, wire and cable" in source["access"]
    assert "LIM winding-conductor product" in source["access"]
    assert "no product, offer, benchmark or candidate match" in source["access"]
