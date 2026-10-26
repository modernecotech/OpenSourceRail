"""Fresh report readback and rejection of a resealed full-car CG claim."""
import json
import os
from pathlib import Path

import pytest

from engineering.equipped_vehicle import ROOT
from engineering.equipped_vehicle.report import run,verify,inventory

EVIDENCE=Path(os.environ.get('OSR_EVIDENCE_ROOT',str(ROOT)))


def test_full_source_bound_report_keeps_equipped_gates_unknown_and_rejects_resealed_cg(tmp_path):
    path=tmp_path/'report';result=run(path,root=EVIDENCE)
    assert len(result['inventories'])==2
    assert all(r['readiness']['mass']=='unknown' and r['cg_m'] is None for r in result['inventories'])
    assert verify(path,root=EVIDENCE)['current']
    summary=json.loads((path/'summary.json').read_bytes());summary['inventories'][0]['cg_m']=[0.,0.,0.]
    (path/'summary.json').write_text(json.dumps(summary))
    manifest=json.loads((path/'manifest.json').read_bytes());manifest['files_sha256']=inventory(path,('manifest.json',))
    (path/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError,match='summary/disposition'):verify(path,root=EVIDENCE)
