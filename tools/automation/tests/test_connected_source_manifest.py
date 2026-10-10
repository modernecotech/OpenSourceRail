"""Detect a changed source inventory before the expensive connected replay."""
import hashlib
import json
from pathlib import Path


ROOT=Path(__file__).resolve().parents[3]


def test_connected_baghdad_binds_current_civil_sources_and_retained_outputs():
    folder=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad/engineering/connected-build'
    manifest=json.loads((folder/'manifest.json').read_text())
    expected={p.relative_to(ROOT).as_posix() for p in (ROOT/'design/component-catalogue/src/osr_mech/civil').glob('*.py')}
    assert expected<=manifest['source_sha256'].keys()
    for path,digest in manifest['source_sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    for path,digest in manifest['output_sha256'].items():
        assert hashlib.sha256((folder/path).read_bytes()).hexdigest()==digest,path
