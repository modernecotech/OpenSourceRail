"""Current source keeps door cut stock distinct from its display proxy."""
import json
from pathlib import Path

from engineering.vehicle_installation.model import geometry


ROOT = Path(__file__).resolve().parents[1]


def test_door_guide_and_belt_stock_exceed_straight_display_proxy():
    parts = json.loads((ROOT / 'engineering/vehicle_parts/data/body.json').read_text())['parts']
    for part_id, expected_length in (
        ('body/door-guide-rail', 2.9),
        ('body/door-belt', 5.8),
    ):
        part = next(p for p in parts if p['id'] == part_id)
        proxy = geometry(part)
        assert proxy['definition_basis'] == 'proposed-route-zone'
        assert proxy['size_m'][0] == 2.0
        assert proxy['source_stock']['length_m'] == expected_length
        assert proxy['finished_geometry_verified'] is False
