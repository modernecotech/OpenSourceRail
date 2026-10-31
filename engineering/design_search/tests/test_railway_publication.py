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
    summary=json.loads((ROOT/publication.OUTPUT/'summary.json').read_bytes())
    completion=summary['completion_status']
    assert completion['simulation_complete']==112
    assert completion['integrated_force_driven_journey_complete']==0
    assert completion['engineering_validated']==0
    assert completion['approved_for_manufacture_or_operation']==0


def _declared_cost_row():
    candidate_id='c'*64
    scopes=set(publication.engine.model_cost.SCOPES)
    estimate=dict(candidate_id=candidate_id,model_cost_complete_for_declared_case=True,
        model_cost_missing_scopes=[],required_cost_scopes=sorted(scopes),
        scope_totals_iqd={scope:[1,2,3] for scope in scopes},assumption_id='a'*64,
        source_sha256={'rates.json':'b'*64},cost_line_items=[dict(candidate_id=candidate_id,
            scope=scope,source_ids=['a'*64],calculation_basis='explicit Class C assumption',
            scenario_iqd=dict(low=1,base=2,high=3)) for scope in sorted(scopes)])
    return dict(candidate_id=candidate_id,economics=dict(model_cost=estimate),physical_journey_completed=False)


def test_completion_levels_mark_assumption_based_cost_simulation_without_validation_or_release():
    status=publication.completion_summary([_declared_cost_row()])
    assert status['simulation_complete']==1
    assert status['integrated_force_driven_journey_complete']==0
    assert status['engineering_validated']==0
    assert status['approved_for_manufacture_or_operation']==0
    record=status['candidate_states'][0]
    assert record['assumption_id']=='a'*64
    assert 'cost scenario only' in status['simulation_scope']


def test_unattributed_cost_line_cannot_complete_the_simulation():
    row=_declared_cost_row()
    row['economics']['model_cost']['cost_line_items'][0]['source_ids']=[]
    status=publication.completion_summary([row])
    assert status['simulation_complete']==0
    assert status['engineering_validated']==0
    assert status['approved_for_manufacture_or_operation']==0


def test_publication_payload_cannot_promote_an_unqualified_winner(tmp_path):
    out = tmp_path / 'packet'
    shutil.copytree(ROOT / publication.OUTPUT, out)
    path = out / 'summary.json'
    summary = json.loads(path.read_bytes())
    summary['integrated_selection'] = 'invented-winner'
    path.write_text(json.dumps(summary))
    with pytest.raises(ValueError, match='payload changed'):
        publication.verify(output=out)


def test_publishing_current_evidence_does_not_rerun_campaign(monkeypatch):
    def refused(*args, **kwargs):
        raise AssertionError('Publication refresh must not launch a campaign or solver')
    monkeypatch.setattr(publication.engine, 'run', refused)
    assert publication.build()['verified']
