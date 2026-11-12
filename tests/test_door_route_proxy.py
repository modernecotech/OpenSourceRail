"""A short layout proxy cannot qualify the full door guide or belt route."""
import json
from pathlib import Path

from engineering.vehicle_installation.model import geometry, cut_length_proxy_audit


ROOT = Path(__file__).resolve().parents[1]


def test_door_guide_and_belt_keep_full_stock_length_separate_from_route_proxy():
    parts = json.loads((ROOT / 'engineering/vehicle_parts/data/body.json').read_text())
    if isinstance(parts, dict):
        parts = parts['parts']
    for part_id, expected_length in (
        ('body/door-guide-rail', 2.9),
        ('body/door-belt', 5.8),
    ):
        part = next(p for p in parts if p['id'] == part_id)
        shape = geometry(part)
        assert shape['definition_basis'] == 'proposed-route-zone'
        assert shape['size_m'][0] == 2.0
        assert shape['source_stock'] == part['stock']
        audit = cut_length_proxy_audit([dict(id=part_id+'@opening',part_id=part_id,geometry=shape)])
        assert audit == [dict(pattern_id=part_id+'@opening',part_id=part_id,
            declared_cut_length_m=expected_length,straight_proxy_length_m=2.0,
            length_not_represented_by_proxy_m=expected_length-2.0,
            full_route_fit_verified=False)]

    backplate = next(p for p in parts if p['id'] == 'body/door-header-backplate')
    assert cut_length_proxy_audit([dict(id='backplate@opening',part_id=backplate['id'],
        geometry=geometry(backplate))]) == []
