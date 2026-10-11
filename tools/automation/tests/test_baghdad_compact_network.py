"""The active compact network restores spacing without reviving withdrawn lines."""
import json,tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
CITY=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'


def test_active_inventory_is_bounded_and_preserves_original_trunks():
    design=tomllib.loads((CITY/'design.toml').read_text());report=json.loads((CITY/'engineering/alignment/residential-line-expansion.json').read_text())
    cfg=json.loads((ROOT/'design/network-planning/baghdad-compact-expansion.json').read_text())
    names={r['name'] for r in design['lines']}
    assert {f'line-{i}' for i in range(1,10)}<=names
    assert 9<len(names)<=9+cfg['maximum_added_lines']
    assert report['final_line_count']==len(names)==report['original_line_count']+report['added_line_count']
    assert report['added_route_m']<=cfg['maximum_added_route_m']
    assert not report['physical_release'] and not report['operating_release']
    assert not (CITY/'station-spacing-policy.toml').exists()


def test_close_stops_are_interchanges_and_ordinary_spacing_has_widened():
    design=tomllib.loads((CITY/'design.toml').read_text());gaps=[]
    for line in design['lines']:
        rows=sorted((s for s in design['stations'] if s['line']==line['name']),key=lambda s:s['s_m'])
        for a,b in zip(rows,rows[1:]):
            gap=b['s_m']-a['s_m'];gaps.append(gap)
            if gap<1000:
                for stop in (a,b):
                    assert stop['archetype'].startswith('interchange') or (stop['archetype']=='terminal' and stop.get('junction_group') is not None)
                if a['archetype']=='terminal' or b['archetype']=='terminal':
                    assert a['junction_group']==b['junction_group']
    assert max(gaps)>6000
    assert sorted(gaps)[len(gaps)//2]>2000
