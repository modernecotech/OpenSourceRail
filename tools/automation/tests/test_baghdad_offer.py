"""The retired short offer shares the complete root publication command."""
import json
import tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
CITY=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'

def test_one_baghdad_publication_and_preserved_screenshots():
    assert not (CITY/'offer').exists()
    assert not (CITY/'proposal').exists()
    assert (CITY/'Baghdad-Proposal.pdf').read_bytes().startswith(b'%PDF-')
    for name in ('baghdad-operations-dashboard.png','baghdad-project-twin.png','baghdad-qa-gates.png'):
        assert (CITY/'engineering/screenshots'/name).is_file()
    text=(ROOT/'tools/automation/build-baghdad-offer.py').read_text()
    assert 'build-baghdad-proposal.py' in text
    assert 'reportlab' not in text

def test_baghdad_engineering_evidence_matches_offer_baseline():
    city = CITY
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
