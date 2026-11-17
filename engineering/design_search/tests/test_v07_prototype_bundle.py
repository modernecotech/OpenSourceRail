"""Independent integrity checks for the bounded prototype research handoff."""

from __future__ import annotations

import json
from pathlib import Path
import shutil

import pytest

from engineering.design_search.v07_prototype_bundle import ROOT, main
from engineering.station_rail.common import identity


PACKET = ROOT / "docs/design-engine/v07-prototype-bundle/packet"


def test_published_bundle_reproduces_and_keeps_release_holds():
    assert main(["check", "--output", str(PACKET)]) == 0
    result = json.loads((PACKET / "result.json").read_text())
    candidate = result["candidate"]
    evaluation = result["evaluation"]
    assert candidate["candidate_id"] == identity(candidate["physical_definition"])
    assert evaluation["physical_candidate_id"] == candidate["candidate_id"]
    assert result["selection"]["candidate_id"] == candidate["candidate_id"]
    assert len(evaluation["capital_14_scopes"]) == 14
    assert all(row["candidate_installed_USD"] is None for row in evaluation["capital_14_scopes"])
    assert evaluation["independent_brake"]["protected_OLE_loss_brake_energy_J"] is None
    assert evaluation["service_demand"]["minimum_six_group_1C4M_each_kW_hypothesis"] > 460
    assert evaluation["physical_accepted"] is False


def test_mixed_published_candidate_is_rejected(tmp_path: Path):
    altered = tmp_path / "packet"
    shutil.copytree(PACKET, altered)
    path = altered / "result.json"
    result = json.loads(path.read_text())
    result["selection"]["candidate_id"] = "mixed-candidate"
    path.write_text(json.dumps(result))
    with pytest.raises(ValueError, match="differs from current sources"):
        main(["check", "--output", str(altered)])
