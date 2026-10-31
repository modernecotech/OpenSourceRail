"""The next mesh is a separately budgeted unchanged-candidate numerical study."""
import gzip
import json
from pathlib import Path
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


def test_prior_context_selects_the_exact_0425_m_packet():
    prior_02125=(0.2125,'eval-02125',Path('/run/02125'),{'mesh_m':0.2125},{'evaluation_id':'eval-02125'})
    prior_0425=(0.425,'eval-0425',Path('/run/0425'),{'mesh_m':0.425},{'evaluation_id':'eval-0425'})
    context=(None,None,None,None,None,None,[prior_02125,prior_0425],None)

    selected=refinement._prior_0425(context)

    assert selected==dict(evaluation_id='eval-0425',raw=Path('/run/0425'),
        request={'mesh_m':0.425},result={'evaluation_id':'eval-0425'})
