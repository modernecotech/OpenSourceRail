from pathlib import Path
import os
import pytest
from engineering.station_rail import vehicle,body_frame
ROOT=Path(os.environ.get('OSR_EVIDENCE_ROOT',str(vehicle.ROOT)))

def current():return vehicle.build(ROOT)

def test_stock_sections_reconcile_exact_material_and_local_inertia():
    ms=body_frame.members_from_stock(current()['geometry_parts'])
    assert len(ms)>50
    for m in ms:
        assert m['area_m2']>0 and min(m['I_about_local_1_m4'],m['I_about_local_2_m4'])>0
        assert m['area_m2']*m['length_m']*2710==pytest.approx(m['mass_kg'])
    sill=next(m for m in ms if m['id'].startswith('wheel-underframe/sill/'))
    assert sill['area_m2']==pytest.approx(.18*.35-(.18-.016)*(.35-.016))
    assert sill['I_about_local_1_m4']==pytest.approx((.18*.35**3-(.18-.016)*(.35-.016)**3)/12)

def test_no_rigid_bridge_across_original_missing_post_floor_joint():
    v=current();d=body_frame.build(v,root=body_frame.ROOT)
    base,added=d['variants']
    assert not base['both_roof_chords_connected']
    assert added['both_roof_chords_connected']
    assert added['added_mass_kg']>0
    assert not added['physical_accepted']
    assert all(p['at_m'][2]+p['size_m'][2]<=1.0010001 for p in added['added_material_parts'])

def test_applied_loads_and_actual_bogie_supports_are_explicit():
    d=body_frame.build(current(),root=body_frame.ROOT);alt=d['variants'][1]
    raw,mesh=body_frame.deck(alt,23000,.6,asymmetric=True,braking=True)
    assert mesh['total_vertical_load_N']==pytest.approx(-23000*body_frame.G)
    assert mesh['total_longitudinal_load_N']==pytest.approx(23000*.6)
    assert len(mesh['support_nodes'])==4
    assert '*BEAM SECTION' in raw and 'SECTION=BOX' in raw
    assert 'SECTION=RECT' in raw
