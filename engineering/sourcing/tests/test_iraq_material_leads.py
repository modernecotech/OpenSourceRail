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
        "iraq.qatral.aluminium-ingot",
        "iraq.sama-kirkuk.eps-listings",
    }
    assert len(rows) == 5
    assert not [row for row in rows if row["kind"] in {"product", "offer", "benchmark"}]
    assert "10 tonnes/day" in sources["iraq.hemn.eps-factory"]["access"]
    assert "12 to 45 kg/m3" in sources["iraq.helal.polyurethane-foam"]["access"]
    assert "not presumed interchangeable" in sources["iraq.hemn.eps-factory"]["access"]
    assert "no offer or candidate match" in sources["iraq.qatral.aluminium-ingot"]["access"]
    assert "6 to 30 kg/m3" in sources["iraq.bafra-shakh.eps"]["access"]
    assert "no product offer" in sources["iraq.sama-kirkuk.eps-listings"]["access"]
