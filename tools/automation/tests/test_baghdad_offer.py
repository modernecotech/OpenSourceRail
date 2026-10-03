import hashlib
import json
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OFFER = ROOT / "cities/catalogue/west-asia/Iraq/Baghdad/offer"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_baghdad_offer_inputs_and_pdf_are_current():
    manifest = json.loads((OFFER / "manifest.json").read_text())
    assert manifest["document_status"] == "concept-and-feed-offer-not-construction-release"
    assert manifest["failed_city_summaries"] == [
        "engineering/depot-scope/summary.json",
        "engineering/stabling/summary.json",
    ]
    for relative, receipt in manifest["inputs"].items():
        path = ROOT / relative
        assert path.is_file(), relative
        assert path.stat().st_size == receipt["bytes"], relative
        assert digest(path) == receipt["sha256"], relative

    output = ROOT / manifest["output"]["path"]
    assert output.read_bytes().startswith(b"%PDF-")
    assert output.stat().st_size == manifest["output"]["bytes"]
    assert digest(output) == manifest["output"]["sha256"]


def test_baghdad_offer_does_not_overclaim_supplier_or_release_status():
    text = (OFFER / "README.md").read_text()
    assert "candidate CRRC component package" in text
    assert "no CRRC partnership, endorsement, selected supplier" in text
    assert "not" in text.lower() and "construction release" in text.lower()
    assert "physical depot and distributed stabling positions" in text
    assert all(f"**G{gate}" in text for gate in range(5))


def test_baghdad_engineering_evidence_matches_offer_baseline():
    city = OFFER.parent
    with (city / "package-manifest.json").open() as handle:
        package = json.load(handle)
    with (city / "engineering/simulation/validation-summary.json").open() as handle:
        simulation = json.load(handle)
    with (city / "engineering/sumo/summary.json").open() as handle:
        sumo = json.load(handle)
    with (city / "engineering/gis/summary.json").open() as handle:
        gis = json.load(handle)

    assert package["package_status"] == "incomplete"
    assert package["missing_artifacts"] == []
    assert package["stale_analysis_sources"] == []
    assert simulation["passed"] and simulation["resilience_passed"]
    assert len(simulation["resilience_cases"]) == 8
    design = tomllib.loads((city / "design.toml").read_text())
    assert sumo["passed"] and sum(line["arrived_services"] for line in sumo["lines"]) == sum(line["scheduled_services"] for line in sumo["lines"])
    assert gis["passed"] and gis["layers"]["civil_segments"] == len(design["civil_segments"])
    assert package["planning_example_complete"]
    assert not package["operational_release"]


def test_offer_text_uses_current_configuration_and_funding():
    city = OFFER.parent
    design = tomllib.loads((city / "design.toml").read_text())
    fleet = sum(row["trainset_count"] for row in design["fleets"])
    finance = json.loads((city / "engineering/finance/summary.json").read_text())
    text = (OFFER / "README.md").read_text()
    assert f"{fleet} six-car trainsets" in text
    assert f"USD {finance['capex_usd']['reconciled_project_total']/1e9:.2f} billion" in text
    assert "uncommitted appraisal assumptions" in text
    assert "IQD bank credit" in text
