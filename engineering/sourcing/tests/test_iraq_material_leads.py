from pathlib import Path

from engineering.sourcing.catalogue import load_catalogue

SEED = Path(__file__).resolve().parents[1] / "data/iraq-domestic-material-leads-2026-10.json"


def test_additional_domestic_material_leads_remain_source_only():
    rows = load_catalogue([SEED])
    sources = {row["source_key"]: row for row in rows if row["kind"] == "source"}
    assert set(sources) == {
        "iraq.bafra-shakh.eps",
        "iraq.hemn.eps-factory",
        "iraq.helal.polyurethane-foam",
        "iraq.lafarge-iraq.cement-products",
        "iraq.alpha-steel.rebar-range-2026",
        "iraq.al-kanz.precast-piling",
        "iraq.qatral.aluminium-ingot",
        "iraq.sama-kirkuk.eps-listings",
        "iraq.regaasphalt.aggregate",
        "iraq.hewa.construction-materials",
    }
    assert len(rows) == 10
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
