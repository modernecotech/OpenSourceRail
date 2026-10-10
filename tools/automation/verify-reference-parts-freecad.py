#!/usr/bin/env python3
"""Reopen generated parts in native FreeCAD and check independent OCC integrals."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]


def native_audit(model_path,cad_path,output):
    import FreeCAD as App
    import Part
    import numpy as np
    from osr_mech.engineering_definition import load_definition,validate,fingerprint
    from osr_mech.automated_geometry import from_source,native_shape,primitive_volume,primitive_inertia
    model=load_definition(model_path);validate(model)
    # Test analytic primitive integrals before opening the larger assembly, so
    # unsupported native APIs cannot hide behind an expensive document restore.
    errors=[];checked=set();rows=[]
    for row in model['instances']:
        spec=from_source(row['geometry'])
        if spec is None:continue
        for primitive in spec['primitives']:
            key=json.dumps(primitive,sort_keys=True)
            if key in checked:continue
            checked.add(key)
            shape=native_shape(dict(role='independent-integral-check',primitives=[primitive]),Part,App).Solids[0]
            volume=shape.Volume;expected=primitive_volume(primitive)*1e9
            native_matrix=shape.MatrixOfInertia
            tensor=np.array([[getattr(native_matrix,f'A{i+1}{j+1}') for j in range(3)] for i in range(3)])/volume/1e6
            analytic=primitive_inertia(primitive,1.)
            relative=float(np.linalg.norm(tensor-analytic)/np.linalg.norm(analytic))
            if abs(volume-expected)/expected>1e-8 or relative>1e-8:
                raise ValueError('OCC volume/inertia disagrees with independent analytic primitive: '+primitive['id'])
            errors.append(relative)
    print('Independent native primitive integrals passed: '+str(len(checked)),flush=True)
    doc=App.openDocument(str(cad_path.resolve()))
    restored_solver=doc.TrainAssembly.solve()
    if type(restored_solver) is not int or restored_solver!=0:raise ValueError('restored native assembly did not solve')
    features={o.InstanceId:o for o in doc.Objects if hasattr(o,'InstanceId')}
    if set(features)!={r['id'] for r in model['instances']}:raise ValueError('native instance coverage differs')
    for row in model['instances']:
        feature=features[row['id']]
        if feature.ConfigurationHash!=fingerprint(model) or feature.ProductionReleased:
            raise ValueError('native identity/release status differs')
        delta=(feature.Placement.Base-App.Vector(*(v*1000 for v in row['transform']['translation_m']))).Length
        matrix=feature.Placement.Rotation.toMatrix()
        rotation=np.array([[getattr(matrix,f'A{i+1}{j+1}') for j in range(3)] for i in range(3)])
        if delta>1e-5 or not np.allclose(rotation,row['transform']['rotation'],rtol=0.,atol=1e-8):
            raise ValueError('native installed placement differs: '+row['id'])
        if not feature.Shape.Solids:raise ValueError('saved native instance has no solids')
        spec=from_source(row['geometry'])
        if spec is None:continue
        if not feature.Shape.isValid():raise ValueError('invalid saved native reference geometry')
        expected_volume=sum(primitive_volume(p) for p in spec['primitives'])*1e9
        if abs(feature.Shape.Volume-expected_volume)/expected_volume>1e-8:
            raise ValueError('saved native reference volume differs: '+row['id'])
        rows.append(dict(instance=row['id'],solid_count=len(feature.Shape.Solids),installed_placement_error_mm=delta))
    if doc.AssemblyDrawing.DrawingIssued:raise ValueError('reference drawing unexpectedly issued')
    result=dict(schema='osr-native-reference-parts-audit/1',configuration_sha256=fingerprint(model),
        fcstd_sha256=hashlib.sha256(cad_path.read_bytes()).hexdigest(),
        audit_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        freecad_version=list(App.Version()),reopened_native_instance_count=len(features),
        restored_native_solver_result=restored_solver,
        analytic_occ_primitive_checks=len(checked),maximum_relative_inertia_error=max(errors),
        native_reference_parts=rows,independent_geometry_integrals_passed=True,drawing_issued=False,
        production_released=False,physical_validation=False)
    App.closeDocument(doc.Name)
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model',type=Path,required=True);parser.add_argument('--cad',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--native-audit',action='store_true',help=argparse.SUPPRESS)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('use a fresh native-audit output')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.native_audit:return native_audit(args.model,args.cad,args.output)
    binary=shutil.which('FreeCADCmd') or shutil.which('freecadcmd')
    if binary:command=[binary]
    elif shutil.which('flatpak'):command=['flatpak','run','--filesystem='+str(ROOT),'--command=FreeCADCmd','org.freecad.FreeCAD']
    else:raise RuntimeError('FreeCADCmd or FreeCAD Flatpak required')
    (ROOT/'build').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='reference-parts-audit-',dir=ROOT/'build') as temporary:
        wrapper=Path(temporary)/'audit.py'
        argv=[str(Path(__file__).resolve()),'--model',str(args.model.resolve()),'--cad',str(args.cad.resolve()),
              '--output',str(args.output.resolve()),'--native-audit']
        wrapper.write_text('import runpy,sys\nsys.argv='+repr(argv)+'\nrunpy.run_path(sys.argv[0],run_name="__main__")\n')
        subprocess.run(command+[str(wrapper)],check=True)
    if not args.output.is_file():raise RuntimeError('native audit did not complete; inspect FreeCAD exception output')
    print(args.output)


if __name__=='__main__':main()
