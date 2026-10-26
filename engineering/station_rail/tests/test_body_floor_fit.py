from pathlib import Path
import os
import pytest
from engineering.station_rail import vehicle,body_floor_fit
ROOT=Path(os.environ.get('OSR_EVIDENCE_ROOT',str(vehicle.ROOT)))

def test_cutouts_change_only_intersected_floor_stock_and_count_sleeves():
    d=body_floor_fit.build(vehicle.build(ROOT),ROOT)
    assert d['collar_count']==20 and 40<=d['collar_stock_parts']<=80
    assert d['changed_parent_parts']>0 and d['removed_material_kg']>0
    assert d['collar_material_mass_kg']>0
    assert d['net_material_mass_delta_kg']==pytest.approx(d['post_connector_mass_kg']+d['collar_material_mass_kg']-d['removed_material_kg'])
    assert all('/floor/' in r['parent_part_id'] or '/floor-' in r['parent_part_id'] for r in d['physical_definition']['removed_stock'])
    assert not d['physical_accepted'] and d['additional_connection_hardware_mass_kg'] is None
    assert d['retained_floor_cap_thickness_m']==pytest.approx(d['retained_floor_top_m']-d['collar_top_m'])
    assert d['tread_recess_m']==0.

def test_rectangular_cutouts_do_not_double_count_retained_holes_or_each_other():
    d=body_floor_fit.build(vehicle.build(ROOT),ROOT)
    for p in d['physical_definition']['geometry_parts']:
        cuts=p.get('rectangular_cutouts',[])
        assert all(not body_floor_fit.hole_intersects(p,c) for c in cuts)
        assert not any(body_floor_fit.intersection(a,b) for i,a in enumerate(cuts) for b in cuts[i+1:])
        assert p['mass_kg']==pytest.approx(p['volume_m3']*p['density_kg_m3'])

def test_unsupported_floor_hole_overlap_is_rejected():
    p=dict(at_m=[0,0,0],holes=[dict(axis='z',diameter_m=.02,x_m=.05,y_m=.05)])
    assert body_floor_fit.hole_intersects(p,dict(at_m=[.04,.04,0],size_m=[.02,.02,.01]))
    assert not body_floor_fit.hole_intersects(p,dict(at_m=[.07,.04,0],size_m=[.02,.02,.01]))
