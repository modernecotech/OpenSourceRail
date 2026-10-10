#!/usr/bin/env python3
"""Run with FreeCADCmd: validate native solids for every registered family."""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
import FreeCAD
import Part
from osr_mech.civil.exploration import assembly_cad,geometry,foundation_geometry


def verify(output):
    path=ROOT/'engineering/civil_exploration/config/system-options.json'
    config=json.loads(path.read_text());records=[]
    def parameters(row):return {k:(int(round((a+b)/2)) if k=='rib_count' else (a+b)/2) for k,(a,b) in row['bounds'].items()}
    baseline=dict(deck=dict(family='hollow-box',span_m=20.,parameters=parameters(config['beams'][1])),
                  pier=dict(family='solid',height_m=8.,parameters={}))
    for role,rows in (('beam',config['beams']),('pier',config['piers']),('foundation',config['foundations'])):
        for row in rows:
            definition=deepcopy(baseline);foundation=deepcopy(config['foundations'][0]['parameters'])
            if role=='foundation':foundation=deepcopy(row['parameters'])
            else:definition['deck' if role=='beam' else 'pier'].update(family=row['id'],parameters=parameters(row))
            span=definition['deck']['span_m'];g=geometry(definition);f=foundation_geometry(foundation)
            deck=sum(s['area_m2']*(s['end_m']-s['start_m']) for s in g['deck'])
            pier=sum(s['area_m2']*(s['end_m']-s['start_m']) for s in g['pier'])
            cap=g['cap_concrete_m3']
            expected=4*deck+3*(pier+cap+f['cap_concrete_m3']+f['pile_concrete_m3'])
            shape=assembly_cad(definition,foundation,2*span).wrapped
            if shape is None or shape.isNull() or not shape.isValid():raise ValueError('native shape invalid: '+row['id'])
            actual=shape.Volume/1e9
            if not math.isclose(actual,expected,rel_tol=1e-9):raise ValueError('native volume mismatch: '+row['id'])
            records.append(dict(role=role,family=row['id'],native_solid_count=len(shape.Solids),native_volume_m3=actual,independent_volume_m3=expected,passed=True))
    inputs_path=ROOT/'engineering/civil_exploration/examples/native-cad-inputs.json'
    inputs=json.loads(inputs_path.read_text());shortlist=[]
    for case in inputs['cases']:
        shape=assembly_cad(case['definition'],case['foundation'],case['route_length_m']).wrapped
        if shape is None or shape.isNull() or not shape.isValid():raise ValueError('native shortlist shape invalid: '+case['package_id'])
        actual=shape.Volume/1e9
        if not math.isclose(actual,case['expected_ifc_volume_m3'],rel_tol=1e-9):raise ValueError('native shortlist/IFC volume mismatch: '+case['package_id'])
        shortlist.append(dict(package_id=case['package_id'],candidate_id=case['candidate_id'],native_solid_count=len(shape.Solids),
                              native_volume_m3=actual,expected_ifc_volume_m3=case['expected_ifc_volume_m3'],passed=True))
    sources=[Path(__file__),path,inputs_path,*sorted((ROOT/'design/component-catalogue/src/osr_mech/civil').glob('*.py')),
             *[ROOT/'design/component-catalogue/src/osr_mech'/name for name in ('cad.py','common.py','provenance.py','family_definition.py','schema_validation.py')]]
    receipt=dict(schema='osr-civil-native-cad-verification/1',kernel='FreeCAD Part/OpenCASCADE',freecad_version=FreeCAD.Version(),opencascade_version=Part.OCC_VERSION,
                 native_binary_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
                 source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                 records=records,shortlist=shortlist,inputs_report_sha256=inputs['report_sha256'],
                 passed=all(r['passed'] for r in records+shortlist),physical_release=False)
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print('Native CAD verification:',len(records),'families and',len(shortlist),'complete shortlisted assemblies passed')


# FreeCADCmd executes scripts with a console module name rather than __main__.
try:verify(ROOT/'build/engineering/civil-studies/native-cad-verification.json')
except Exception:
    import traceback
    traceback.print_exc();sys.exit(1)
