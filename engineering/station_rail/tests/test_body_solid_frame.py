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
