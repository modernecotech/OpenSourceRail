from pathlib import Path

from engineering.station_rail.publication import _sourcing_section

ROOT = Path(__file__).resolve().parents[3]


def test_current_readme_sourcing_section_checks_and_reports_local_gfrp_screens():
    lines = _sourcing_section(ROOT, {"candidate_id": "reference-candidate"})
    report = "\n".join(lines)

    assert "416 immutable records" in report
    assert "Ministry industrial directory" in report
    assert "cable and busbar production" in report
    assert "transformers" in report
    assert "discovery leads, not quotations" in report
    assert "4,766/4,773 accounts linked" in report
    assert "230 non-additive associations" in report
    assert "GFRP" in report
    assert "IQD 1,565,576.82/1,655,576.82/1,835,576.82" in report
    assert "IQD 827,788.41/917,788.41/1,097,788.41" in report
    assert "IQD 629,235.07/719,235.07/899,235.07" in report
    assert "15 listed governorates" in report
    assert "Kurdistan Region wage data are absent" in report
    assert "IQD 1,523,576.82–1,565,576.82" in report
    assert "July 2026 CSO Baghdad or listed-governorate" in report
    assert "unpriced inputs remain open" in report
    assert "do not price a finished panel or transfer to the selected reference body" in report
