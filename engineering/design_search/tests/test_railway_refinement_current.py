"""The supplementary mesh continuation stays bound to the current body/bundle."""
import gzip
import json
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.design_search import railway_native, railway_refinement_current as refinement


def test_current_candidate_mesh_preflight_is_exact_and_bounded():
    folder = ROOT / "docs/design-engine/coupled-railway"
    bodies = json.loads(gzip.decompress((folder / "bodies.json.gz").read_bytes()))
    bundles = json.loads(gzip.decompress((folder / "bundles.json.gz").read_bytes()))
    body = next(b for b in bodies if b["candidate_id"] == refinement.CANDIDATE_ID)
    bundle = next(b for b in bundles if b["candidate_id"] == refinement.P1_BUNDLE_ID)

    assert body["definition_id"] == "8eed09c97b93d3aa1988d8bdc99f11a45d6f64ca470eea10b28ecf664a34a842"
    assert bundle["body_candidate_id"] == body["candidate_id"]
    assert bundle["body_definition_id"] == body["definition_id"]
    assert bundle["definition_id"] == "8b961b89cd2ac4c9f8bb8899e45628a1c41745e8a7d74744e493053e704fbd77"
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
