"""Published native evidence is usable without dispatching local solvers."""
import json
import shutil
import pytest
from engineering.station_rail import ROOT
from engineering.design_search import railway_publication as publication


def test_coordinated_publication_retains_execution_and_unknowns():
    result = publication.verify()
    assert result['body_count'] == 14
    assert result['evaluated_bundle_count'] == 112
    assert result['native_body_case_count'] == 7
    assert result['physical_journeys'] == result['complete_installed_masses'] == 0
    assert result['physical_accepted'] is False


def test_publication_payload_cannot_promote_an_unqualified_winner(tmp_path):
    out = tmp_path / 'packet'
    shutil.copytree(ROOT / publication.OUTPUT, out)
    path = out / 'summary.json'
    summary = json.loads(path.read_bytes())
    summary['integrated_selection'] = 'invented-winner'
    path.write_text(json.dumps(summary))
    with pytest.raises(ValueError, match='payload changed'):
        publication.verify(output=out)


def test_publishing_current_evidence_needs_no_local_solver_folders(monkeypatch):
    def refused(*args, **kwargs):
        raise AssertionError('Current publication must reuse its sealed evidence')
    monkeypatch.setattr(publication, 'current', refused)
    assert publication.build()['verified']
