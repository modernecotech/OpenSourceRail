"""The comparison explanation must name its actual mass-specific beams."""
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_reference_geometry_context_matches_published_baseline():
    baseline = json.loads(gzip.decompress(
        (ROOT / 'docs/design-engine/civil-topology/baseline.json.gz').read_bytes()))
    text = (ROOT / 'docs/design-engine/flanged-system-cost-context.md').read_text()
    assert baseline['baseline_id'] in text
    for mass in ('low', 'base', 'high'):
        basis = baseline['cases'][mass]['civil_design_basis']
        expected = f"| {mass.capitalize()} | {basis['prestress_strands']} | `{basis['physical_civil_component_id']}` |"
        assert expected in text
    assert 'not a sensitivity of one fixed reference beam' in text
