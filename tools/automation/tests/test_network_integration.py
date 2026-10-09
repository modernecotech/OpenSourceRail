import importlib.util
from pathlib import Path
import sys

import pytest
from shapely.geometry import LineString

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/automation'))
from network_integration import complete_link_groups,geometry_interfaces,legs_at_interface,line_at_chainage


def test_transitive_and_same_line_amalgamation_cannot_expand_complex_diameter():
    rows=[dict(id='a',line='one',xy=[0,0]),dict(id='b',line='two',xy=[500,0]),
          dict(id='c',line='three',xy=[1000,0]),dict(id='d',line='one',xy=[1100,0])]
    groups=complete_link_groups(rows,600)
    assert groups
    assert all(g['maximum_platform_separation_m']<=600 for g in groups)
    assert not any({'a','c'}<=set(g['platform_ids']) for g in groups)
    assert all(g['actual_walking_distance_m'] is None and not g['accessible_path_accepted'] for g in groups)


def test_crossing_and_shared_corridor_do_not_create_a_track_switch():
    routes={'one':LineString([(0,0),(50,0)]),'two':LineString([(25,-20),(25,20)]),
            'three':LineString([(10,0),(40,0)])}
    items=geometry_interfaces(routes)
    assert any(i['kind']=='crossing' for i in items)
    assert any(i['kind']=='shared-corridor' and i['shared_length_m']==30 for i in items)
    assert all(i['rail_connection_created'] is False for i in items)


def test_self_crossing_preserves_distinct_chainage_visits():
    route=LineString([(0,0),(10,10),(0,10),(10,0)])
    items=geometry_interfaces({'one':route})
    assert any(i['kind']=='self-crossing' for i in items)
    positions=legs_at_interface(route,[5,5],route.length)
    assert len(positions)==2 and positions[1]>positions[0]


def test_support_interpolation_preserves_declared_chainage_and_rejects_out_of_scope():
    route=LineString([(0,0),(30,0),(30,40)])
    assert line_at_chainage(route,50,100)==[30,5]
    with pytest.raises(ValueError,match='outside'):
        line_at_chainage(route,101,100)


def test_every_catalogue_span_has_unique_directed_front_and_foundation_parents():
    import json
    spec=importlib.util.spec_from_file_location('integrated_plan',ROOT/'tools/automation/integrated-network-plan.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    city=module.CITY;design=module.tomllib.loads((city/'design.toml').read_text())
    routes,_,_,unproject=module.coordinates(design,json.loads((city/'baghdad.corridor.geojson').read_text()),
                                          json.loads((city/'engineering/alignment/planning-grid.json').read_text()))
    foundations,spans,fronts,_=module.foundation_assembly(design,routes,unproject,[])
    ids={f['id'] for f in foundations}
    assert all(s['foundation_a'] in ids and s['foundation_b'] in ids for s in spans)
    assigned=[s['id'] for s in spans if s['front']]
    assert len(assigned)==len(set(assigned))
    byid={s['id']:s for s in spans}
    for front in fronts:
        chainages=[byid[s]['from_m'] for s in front['span_ids']]
        assert chainages==sorted(chainages,reverse=front['direction']<0)
    assert all(f['installed_depth_m'] is None and f['complete_foundation_design_axial_kn'] is None for f in foundations)
    boundary=[f for f in foundations if f['cyclic_boundary_alias_support_id']]
    assert boundary
    for foundation in boundary:
        assert 'FND:'+foundation['cyclic_boundary_alias_support_id'] not in ids
        adjoining=[byid[s] for s in foundation['adjacent_span_ids'].split(';')]
        assert len(adjoining)>=2
        assert all(foundation['id'] in (s['foundation_a'],s['foundation_b']) for s in adjoining)
        assigned_fronts={s['front'] for s in adjoining if s['front']}
        assert foundation['shared_front_stage_coordination_required']==(len(assigned_fronts)>1)
