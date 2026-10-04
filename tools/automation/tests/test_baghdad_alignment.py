"""Core alignment changes actual routes without concealing property/release gaps."""
import gzip
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tomllib

import pytest
ROOT=Path(__file__).resolve().parents[3]
CITY=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
spec=importlib.util.spec_from_file_location('baghdad_alignment',ROOT/'tools/automation/rework-baghdad-alignment.py')
alignment=importlib.util.module_from_spec(spec);spec.loader.exec_module(alignment)

def test_committed_alignment_controls_are_reproducible_and_change_the_main_routes():
    subprocess.run([sys.executable,str(ROOT/'tools/automation/rework-baghdad-alignment.py'),'--check'],check=True)
    seed=json.loads(gzip.decompress(alignment.SEED.read_bytes()));grid=json.loads(alignment.GRID.read_text())
    config=tomllib.loads(alignment.CONFIG.read_text());routes,report=alignment.rework(seed,grid,config)
    assert len(routes['lines'])==len(seed['lines'])==9
    assert report['core_analytical_length_m']<.85*report['core_original_length_m']
    for old,new,record in zip(seed['lines'],routes['lines'],report['lines']):
        assert new['cells'][0]==old['cells'][0] and new['cells'][-1]==old['cells'][-1]
        assert new['anchor_ids']==old['anchor_ids']
        for run in record['core_runs']:
            if new['shape']=='Radial':
                assert len(run['control_points'])==2
                assert all(control['kind']=='tangent' for control in run['controls'])
            else:
                assert all(c['radius_m']>=300 for c in run['controls'] if c['kind']=='arc')
    d=tomllib.loads((CITY/'design.toml').read_text())
    assert sum(line['length_m'] for line in d['lines'])<500_000
    elevated=sum(s['to_station_m']-s['from_station_m'] for s in d['civil_segments'] if s['class']=='elevated')
    assert elevated/sum(line['length_m'] for line in d['lines'])>.5
    assert sum(s['to_station_m']-s['from_station_m'] for s in d['civil_segments'])==pytest.approx(sum(line['length_m'] for line in d['lines']),abs=2)
    assert any(s['class']=='bridge' for s in d['civil_segments'])
    assert 'Property' in report['limitations'][1] or any('property' in line.lower() for line in report['limitations'])

def test_circular_controls_meet_geometry_and_do_not_hide_an_impossible_reversal():
    samples,controls=alignment.fillet([(0,0),(3000,0),(3000,3000)],1000,20)
    arc=next(c for c in controls if c['kind']=='arc')
    assert arc['radius_m']==pytest.approx(1000)
    assert alignment.distance(arc['start'],arc['center'])==pytest.approx(1000)
    assert alignment.distance(arc['end'],arc['center'])==pytest.approx(1000)
    assert arc['angle_rad']==pytest.approx(math.pi/2)
    assert samples[0]==(0,0) and samples[-1]==(3000,3000)
    with pytest.raises(ValueError,match='reverses direction'):
        alignment.fillet([(0,0),(3000,0),(0,0)],1000,20)
