#!/usr/bin/env python3
"""Build a native battery datum-fixture study with a checked six-restraint map."""
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


def native(package,output):
    import FreeCAD as App
    import Part
    from osr_mech.engineering_definition import load_definition,fingerprint
    from osr_mech.automated_geometry import native_shape,primitive_volume
    from osr_mech.freecad_assembly_review import _canonicalise_fcstd
    from engineering.industrialisation.assembly import fixture_constraints
    fixture=load_definition(package);checks=fixture_constraints(fixture['locator_points_m'],fixture['locator_normals'])
    if not checks['independent_rigid_body_restraints']:raise ValueError('fixture underconstrained')
    doc=App.newDocument('OSRBatteryFixtureReference');features=[]
    for primitive in fixture['geometry']['primitives']:
        feature=doc.addObject('Part::Feature',primitive['id'].replace('-','_'))
        feature.Label=primitive['id'];feature.Shape=native_shape(dict(role='fixture-reference',primitives=[primitive]),Part,App)
        expected=primitive_volume(primitive)*1e9
        if not feature.Shape.isValid() or abs(feature.Shape.Volume/expected-1)>1e-8:raise ValueError('native fixture geometry differs')
        if (feature.Shape.Solids[0].CenterOfMass-App.Vector(*(v*1000 for v in primitive['centre_m']))).Length>1e-5:
            raise ValueError('native locator/member position differs')
        feature.addProperty('App::PropertyBool','ProductionReleased','OSR');feature.ProductionReleased=False
        features.append(feature)
    page=doc.addObject('TechDraw::DrawPage','FixtureDrawing');template=doc.addObject('TechDraw::DrawSVGTemplate','FixtureTemplate')
    templates=Path(App.getResourceDir())/'Mod/TechDraw/Templates'
    candidates=list(templates.glob('A4_Landscape*.svg')) or list(templates.glob('*.svg'))
    if not candidates:raise RuntimeError('native TechDraw template resources unavailable')
    template.Template=str(sorted(candidates)[0]);page.Template=template
    edges={}
    for name,direction,y in [('Plan',(0,0,1),140.),('Elevation',(0,-1,0),80.)]:
        view=doc.addObject('TechDraw::DrawViewPart',name);view.Source=features;view.Direction=App.Vector(*direction)
        view.Scale=min(.05,240./(max(p['centre_m'][0] for p in fixture['geometry']['primitives'])-min(p['centre_m'][0] for p in fixture['geometry']['primitives'])+1.)/1000)
        view.X=148.;view.Y=y;page.addView(view)
    page.addProperty('App::PropertyBool','DrawingIssued','OSR');page.DrawingIssued=False
    page.addProperty('App::PropertyString','LocatorMap','OSR');page.LocatorMap=json.dumps(fixture['locator_points_m'])
    doc.recompute()
    for name in ('Plan','Elevation'):
        edges[name]=len(doc.getObject(name).getVisibleEdges())
        if edges[name]==0:raise ValueError('fixture drawing has no geometry')
    doc.saveAs(str(output.resolve()));App.closeDocument(doc.Name);_canonicalise_fcstd(output)
    result=dict(schema='osr-native-industrialisation-fixture/1',fixture_sha256=fingerprint(fixture),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),freecad_version=list(App.Version()),
        constraint_rank=checks['constraint_rank'],reference_solid_count=len(features),drawing_edges=edges,
        fcstd_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),fixture_released=False,drawing_issued=False,physical_validation=False)
    output.with_suffix('.native.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fixture',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--native',action='store_true',help=argparse.SUPPRESS);a=p.parse_args()
    if a.output.exists():raise ValueError('use a fresh native fixture output')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    if a.native:return native(a.fixture,a.output)
    binary=shutil.which('FreeCADCmd') or shutil.which('freecadcmd')
    command=[binary] if binary else ['flatpak','run','--filesystem='+str(ROOT),'--command=FreeCADCmd','org.freecad.FreeCAD']
    (ROOT/'build').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='factory-fixture-',dir=ROOT/'build') as directory:
        wrapper=Path(directory)/'fixture.py';argv=[str(Path(__file__).resolve()),'--fixture',str(a.fixture.resolve()),'--output',str(a.output.resolve()),'--native']
        wrapper.write_text('import runpy,sys,traceback\nsys.argv='+repr(argv)+'\ntry:\n    runpy.run_path(sys.argv[0],run_name="__main__")\nexcept Exception:\n    traceback.print_exc()\n    raise SystemExit(1)\n')
        subprocess.run(command+[str(wrapper)],check=True)
    if not a.output.is_file() or not a.output.with_suffix('.native.json').is_file():raise RuntimeError('native fixture did not complete; inspect FreeCAD exception output')
    print(a.output)


if __name__=='__main__':main()
