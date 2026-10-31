"""The next mesh is a separately budgeted unchanged-candidate numerical study."""
import gzip
import json
from engineering.station_rail import ROOT
from engineering.design_search import railway_native, railway_refinement_current_fine as refinement


def test_current_fine_preflight_is_explicit_and_stays_within_its_resource_revision():
    folder=ROOT/'docs/design-engine/coupled-railway'
    bodies=json.loads(gzip.decompress((folder/'bodies.json.gz').read_bytes()))
    bundles=json.loads(gzip.decompress((folder/'bundles.json.gz').read_bytes()))
    body=next(x for x in bodies if x['candidate_id']==refinement.CANDIDATE_ID)
    bundle=next(x for x in bundles if x['candidate_id']=='1e8d1d7c394fc0bdbd47e34fb21d413ebc34a49576bad60b31b254bd635dfb68')
    estimate=railway_native.cell_estimate(body,refinement.MESH_M)
    assert bundle['body_candidate_id']==body['candidate_id']
    assert refinement.MESH_M==0.10625
    assert estimate['solid_cells']==128382
    assert estimate['solid_cells']<=refinement.CELL_BUDGET==140000
    assert refinement.MEMORY_MB==8192
    assert refinement.TIMEOUT_S==240
    assert refinement.ELEMENT_KIND=='C3D8I'
