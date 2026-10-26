from pathlib import Path
import os,pytest
from engineering.station_rail import vehicle,body_frame,body_solid_frame
ROOT=Path(os.environ.get('OSR_EVIDENCE_ROOT',str(vehicle.ROOT)))

def test_explicit_hollow_wall_volume_and_translation_only_constraints():
    d=body_frame.build(vehicle.build(ROOT),ROOT)
    for v in d['variants']:
        raw,m=body_solid_frame.deck(v,16000,.6)
        assert m['meshed_volume_m3']==pytest.approx(m['expected_stock_volume_m3'])
        assert '*ELEMENT,TYPE=C3D20R' in raw and '*BEAM SECTION' not in raw
        lines=iter(raw.splitlines())
        for line in lines:
            if line=='*EQUATION':
                count=int(next(lines));terms=next(lines).split(',');assert len(terms)==3*count
                assert all(int(terms[i]) in (1,2,3) for i in range(1,len(terms),3))


def test_deeper_sill_options_count_new_stock_and_preserve_fixed_upper_interface():
    options=body_solid_frame.sill_stock_options(vehicle.build(ROOT))
    assert len(options)==3 and len({o['alternative_id'] for o in options})==3
    for option in options:
        ps=option['physical_definition']['new_stock']
        assert len(ps)==8
        assert max(p['at_m'][2]+p['size_m'][2] for p in ps)==pytest.approx(.7945)
        assert option['counted_material_mass_delta_kg']>1000
        assert option['structural_screen']=='unknown' and option['clearance_screen']=='unknown'
        assert not option['physical_accepted']
