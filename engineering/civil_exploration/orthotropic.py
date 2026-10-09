"""Positive-definite orthotropic matrices and an independent native coupon."""
from __future__ import annotations
from pathlib import Path
import math
import shutil
import subprocess
import numpy as np
from .contracts import encoded,sha
from .detailed import stress_fields


def validate(record):
    required={'ex_pa','ey_pa','ez_pa','nu_xy','nu_xz','nu_yz','gxy_pa','gxz_pa','gyz_pa'}
    if set(record)!=required or not all(type(v) in (int,float) and math.isfinite(v) for v in record.values()):
        raise ValueError('orthotropic material coverage/finite values invalid')
    if min(record[k] for k in ('ex_pa','ey_pa','ez_pa','gxy_pa','gxz_pa','gyz_pa'))<=0:
        raise ValueError('orthotropic stiffness must be positive')
    S=np.diag([1/record['ex_pa'],1/record['ey_pa'],1/record['ez_pa'],1/record['gyz_pa'],1/record['gxz_pa'],1/record['gxy_pa']])
    S[0,1]=S[1,0]=-record['nu_xy']/record['ex_pa']
    S[0,2]=S[2,0]=-record['nu_xz']/record['ex_pa']
    S[1,2]=S[2,1]=-record['nu_yz']/record['ey_pa']
    if min(np.linalg.eigvalsh(S))<=0:raise ValueError('orthotropic compliance is not positive definite')
    return S


def elastic_lines(record):
    validate(record)
    return ['*ELASTIC,TYPE=ENGINEERING CONSTANTS',','.join(str(record[k]) for k in
             ('ex_pa','ey_pa','ez_pa','nu_xy','nu_xz','nu_yz','gxy_pa','gxz_pa')),str(record['gyz_pa'])]


def coupon(record,output):
    validate(record)
    if output.exists():raise ValueError('orthotropic coupon output must be new')
    output.mkdir(parents=True)
    corners=np.asarray([(0,0,0),(1,0,0),(1,.1,0),(0,.1,0),(0,0,.1),(1,0,.1),(1,.1,.1),(0,.1,.1)])
    edges=[(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
    nodes=list(corners)+[(corners[i]+corners[j])/2 for i,j in edges]
    rows=['*HEADING','Synthetic orthotropic axial verification; no physical qualification','*NODE']
    rows += [f'{i+1},'+','.join(str(v) for v in point) for i,point in enumerate(nodes)]
    rows += ['*ELEMENT,TYPE=C3D20R,ELSET=BODY','1,'+','.join(str(i) for i in range(1,16))+',',','.join(str(i) for i in range(16,21)),
             '*MATERIAL,NAME=FRP',*elastic_lines(record),'*SOLID SECTION,ELSET=BODY,MATERIAL=FRP',
             '*NSET,NSET=TIP','2,3,6,7,10,14,18,19','*BOUNDARY']
    rows += [f'{i},1,1' for i,point in enumerate(nodes,1) if point[0]==0]
    rows += ['1,2,3','4,3,3','*STEP','*STATIC','*CLOAD']
    force=10000.
    rows += [f'{i},1,{-force/12}' for i in (2,3,6,7)]
    rows += [f'{i},1,{force/3}' for i in (10,14,18,19)]
    rows += ['*NODE PRINT,NSET=TIP','U','*EL PRINT,ELSET=BODY','S','*END STEP']
    deck=output/'coupon.inp';deck.write_text('\n'.join(rows)+'\n')
    binary=shutil.which('ccx')
    if not binary:raise RuntimeError('CalculiX required for orthotropic coupon')
    result=subprocess.run([binary,'coupon'],cwd=output,capture_output=True,text=True,timeout=60)
    (output/'stdout.log').write_text(result.stdout);(output/'stderr.log').write_text(result.stderr)
    if result.returncode:raise RuntimeError('native orthotropic coupon failed')
    text=(output/'coupon.dat').read_text()
    import re
    matches=re.findall(r'^\s*2\s+([-+0-9.EeDd]+)\s+[-+0-9.EeDd]+\s+[-+0-9.EeDd]+\s*$',text,re.M)
    if len(matches)!=1:raise ValueError('orthotropic coupon tip displacement missing')
    actual=float(matches[0].replace('D','E'));expected=force/(.01*record['ex_pa'])
    stress=stress_fields(output/'coupon.dat')
    error=abs(actual/expected-1)
    report=dict(schema='osr-civil-orthotropic-coupon/1',material=record,actual_displacement_m=actual,
                analytical_displacement_m=expected,relative_error=error,relative_tolerance=1e-5,passed=error<1e-5,
                peak_native_xx_pa=max(r['stress_pa']['xx'] for r in stress),
                native_input_sha256=sha(deck),native_output_sha256=sha(output/'coupon.dat'),physical_release=False)
    (output/'result.json').write_bytes(encoded(report))
    return report
