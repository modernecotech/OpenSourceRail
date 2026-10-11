"""Sector selection retains real counts and one total compact route budget."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/automation'))


def test_sector_reservations_and_full_union_accounting():
    city=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
    report=json.loads((city/'engineering/alignment/residential-line-expansion.json').read_text())
    cfg=json.loads((ROOT/'design/network-planning/baghdad-compact-expansion.json').read_text())
    mapping=json.loads((ROOT/'design/network-planning/baghdad-mapping-sources.json').read_text())
    for sector in mapping['sectors']:
        rows=[row for row in report['added_lines'] if row['selection_sector']==sector['id']]
        assert len(rows)==sector['reserved_added_lines']
        assert all(row['incremental_sector_residents']>0 and row['incremental_residents']>=row['incremental_sector_residents'] for row in rows)
    assert report['added_route_m']<=min(cfg['maximum_added_route_m'],report['original_route_m']*cfg['maximum_added_route_fraction'])+.01
    before=report['sector_baseline']['sectors'][0];after=report['sector_proposed_stop_screen']['sectors'][0]
    # Overlapping phase/sector circles cannot inflate the full-city population gain.
    gain=sum(row['incremental_residents'] for row in report['added_lines'])
    assert abs(gain-(after['radial_covered_population']-before['radial_covered_population']))<.02
    assert report['population_year']==2026 and report['baseline_population_year']==2020
    assert all('incremental_residents_2020' not in row for row in report['added_lines'])
    assert not report['accessible_walking_coverage_accepted']
