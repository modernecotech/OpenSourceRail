from pathlib import Path

from engineering.station_rail.publication import _sourcing_section

ROOT = Path(__file__).resolve().parents[3]


def test_current_readme_sourcing_section_checks_current_regional_cost_evidence():
    lines = _sourcing_section(ROOT, {"candidate_id": "reference-candidate"})
    report = "\n".join(lines)

    assert "533 immutable records" in report
    assert "Ministry industrial directory" in report
    assert "rolled steel profile suppliers" in report
    assert "ordinary and sulphate-resistant cement producers" in report
    assert "cable and busbar production" in report
    assert "transformers" in report
    assert "discovery leads, not quotations" in report
    assert "31,989 physical scopes across 7,042 review requirements" in report
    assert "137 evaluated, 6,905 pending" in report
    assert "nine RFQ drafts remain unsent" in report
    assert "191 draft packages and 8 purchasing/material lines" in report
    assert "52 domestic-source lead associations across seven families" in report
    assert "Hadeed Iraq also provides a rebar marketplace/RFQ directory" in report
    assert "displayed figures are indicative seller listings, not a binding Hadeed offer" in report
    assert "materials + labour + 20%" in report
    assert "Baghdad IQD 205.0–326.8m; Al-Muthanna IQD 196.9–294.3m" in report
    assert "4,766/4,773 accounts linked" in report
    assert "230 non-additive associations" in report
    assert "GFRP" in report
    assert "IQD 1,565,576.82/1,655,576.82/1,835,576.82" in report
    assert "IQD 827,788.41/917,788.41/1,097,788.41" in report
    assert "IQD 629,235.07/719,235.07/899,235.07" in report
    assert "15 listed governorates" in report
    assert "Kurdistan Region wage data are absent" in report
    assert "IQD 1,523,576.82–1,565,576.82" in report
    assert "September 2026 CSO Baghdad or listed-governorate" in report
    assert "2025 local material/labour scenarios" not in report
    assert "530 scopes" not in report
    assert "unpriced inputs remain open" in report
    assert "do not price a finished panel or transfer to the selected reference body" in report
    assert "validation-current.json" in report
    assert "9.354 t across five bank groups and ten retained occurrences" in report
    assert "IQD 90.19/91.03/92.72 million" in report
    assert "do not establish winding-conductor compatibility" in report
    assert "approximately 900 m winding allocation" in report
    assert "Five source-bound unsent bank scopes" in report
    assert "station-drive RFQ draft" in report
    assert "validation-current.json" in report
    assert "CSO 2024 construction-wage archive" in report
    assert "not used in current 2025/2026 estimates" in report
