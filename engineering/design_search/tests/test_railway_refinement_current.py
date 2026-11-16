"""The supplementary mesh continuation stays bound to the current body/bundle."""
import gzip
import json
from pathlib import Path
import pytest

from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded
from engineering.design_search import railway_mesh_preflight, railway_native, railway_refinement_current as refinement


def test_v2_parent_contract_passes_source_gate_before_candidate_gate(tmp_path,monkeypatch):
    from engineering.design_search import railway_campaign as campaign
    spec={'schema':'v2-fixture'};epoch={'producer':'a'*64}
    monkeypatch.setattr(campaign,'specification',lambda root:spec)
    monkeypatch.setattr(campaign,'source_epoch',lambda root:epoch)
    parent=dict(specification=spec,source_sha256=epoch,contract_id=campaign.contract_identity(spec,epoch),rows=[])
    parent['campaign_id']=campaign.semantic_id(parent)
    parent['run_id']=campaign._aggregate_identity(parent)
    path=tmp_path/'exact-parent.json';path.write_bytes(encoded(parent))
    with pytest.raises(ValueError,match='bounded continuation accepts only'):
        refinement._context(tmp_path,parent_result=path,candidate_id='different-candidate')


def test_current_candidate_mesh_preflight_is_exact_and_bounded():
    current=ROOT/'docs/design-engine/coupled-railway-v07'
    historical=ROOT/'docs/design-engine/coupled-railway'
    folder=current if (current/'manifest.json').is_file() else historical
    bodies = json.loads(gzip.decompress((folder / "bodies.json.gz").read_bytes()))
    bundles = json.loads(gzip.decompress((folder / "bundles.json.gz").read_bytes()))
    preflight_contract = railway_mesh_preflight.specification()
    body = next(b for b in bodies if b["candidate_id"] == refinement.CANDIDATE_ID)
    bundle = next(b for b in bundles if b["candidate_id"] == refinement.P1_BUNDLE_ID)

    if folder==historical:
        assert (historical/'manifest.json').is_file()
        assert body['definition_id']!=preflight_contract['body_definition_id']
        assert bundle['definition_id']!=preflight_contract['bundle_definition_id']
        assert not (current/'manifest.json').exists()
        return

    assert body["definition_id"] == preflight_contract["body_definition_id"]
    assert bundle["body_candidate_id"] == body["candidate_id"]
    assert bundle["body_definition_id"] == body["definition_id"]
    assert bundle["definition_id"] == preflight_contract["bundle_definition_id"]
    assert bundle["normal_sprung_mass_hypothesis_kg"] == 10818.661193648113

    estimate = railway_native.cell_estimate(body, refinement.NEXT_MESH_M)
    assert refinement.NEXT_MESH_M == 0.2125
    assert estimate["solid_cells"] == 82372
    assert estimate["solid_cells"] <= refinement.CELL_BUDGET == 90000
    assert refinement.MEMORY_MB == 5120
    assert refinement.TIMEOUT_S == 150
    assert refinement.ELEMENT_KIND == "C3D8I"


def test_current_refinement_uses_one_named_candidate_and_never_releases_it():
    assert Path(refinement.PRODUCER).as_posix() == "engineering/design_search/railway_refinement_current.py"
    assert refinement.CANDIDATE_ID == "8db92b830fda54c81ec231c541f811b24f938f2471b559448d2ed2683754f78b"
    assert all(value is False for value in refinement.FLAGS.values())
