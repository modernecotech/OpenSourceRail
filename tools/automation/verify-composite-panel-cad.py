#!/usr/bin/env python3
"""Run inside FreeCADCmd: export and independently verify real panel solids."""
from pathlib import Path
import hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'design/component-catalogue/src'))
from osr_mech.rolling_stock.composite_panels import cad_layers,roof_arc
import FreeCAD
import Part

def run():
 config_path=ROOT/'engineering/composite_panels/config/development.json';config=json.loads(config_path.read_text())
 out=ROOT/'engineering/composite_panels/reference/cad';out.mkdir(parents=True,exist_ok=True);records=[]
 for name,height,crown in [('side',3.45,0),('roof',2.35,.05)]:
  assembly=cad_layers(config,width=.994,height=height,skin=.0015,core=.0246,crown=crown)
  shape=assembly.wrapped
  if shape is None or shape.isNull() or not shape.isValid():raise ValueError('Invalid native panel '+name)
  arc=roof_arc(height,crown);depth=.028;finish=.0003
  # Integrate the complete blank outer/inner surfaces independently of CAD.
  expected=.994*arc['arc_length_m']*(depth+finish)
  if crown:expected+=.994*arc['arc_length_m']*finish*(depth/2+finish/2)/arc['radius_m']
  actual=shape.Volume/1e9
  if not math.isclose(actual,expected,rel_tol=1e-9):raise ValueError((name,actual,expected))
  children=assembly.children
  for i,a in enumerate(children):
   if a.wrapped is None or not a.wrapped.isValid():raise ValueError('Invalid layer '+a.label)
   for b in children[i+1:]:
    if a.wrapped.common(b.wrapped).Volume>1e-5:raise ValueError('Overlapping materials '+a.label+' / '+b.label)
  document=FreeCAD.newDocument('Development_'+name)
  for i,child in enumerate(children):
   obj=document.addObject('PartDesign::Feature','Layer_'+str(i+1));obj.Label=child.label;obj.Shape=child.wrapped
   if 'foam' in child.label:density=config['core']['density_kg_m3'];material='Generic foam assumption'
   elif 'adhesive' in child.label:density=config['bond']['density_kg_m3'];material='Unfrozen bond assumption'
   elif 'potted' in child.label:density=config['hardware']['potting_density_kg_m3'];material='Unfrozen potting assumption'
   elif 'metal insert' in child.label:density=config['hardware']['insert_density_kg_m3'];material='Metal insert assumption'
   elif 'finish' in child.label:density=config['finish']['density_kg_m3'];material='Unfrozen finish assumption'
   else:density=config['glass']['density_kg_m3'];material='Generic GFRP assumption'
   obj.addProperty('App::PropertyString','DevelopmentMaterial');obj.DevelopmentMaterial=material
   obj.addProperty('App::PropertyFloat','AssumedDensityKgM3');obj.AssumedDensityKgM3=density
   obj.addProperty('App::PropertyFloat','CalculatedLayerMassKg');obj.CalculatedLayerMassKg=child.wrapped.Volume/1e9*density
   obj.addProperty('App::PropertyString','QualificationStatus');obj.QualificationStatus='Unqualified development geometry'
   obj.addProperty('App::PropertyString','LoadPath');obj.LoadPath='Weather skin; equipment loads into separate frame supports'
  document.recompute();path=out/(name+'-layered-panel.FCStd');document.saveAs(str(path));FreeCAD.closeDocument(document.Name)
  records.append(dict(panel=name,native_solid_count=len(shape.Solids),native_volume_m3=actual,independent_volume_m3=expected,
   material_regions_nonoverlapping=True,curved_insert_land_qualification=False if crown else None,output=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),passed=True))
 sources=[Path(__file__),config_path,ROOT/'design/component-catalogue/src/osr_mech/rolling_stock/composite_panels.py',ROOT/'design/component-catalogue/src/osr_mech/cad.py']
 receipt=dict(schema='osr-composite-native-cad/1',kernel='FreeCAD Part/OpenCASCADE',freecad_version=FreeCAD.Version(),opencascade_version=Part.OCC_VERSION,
  sources_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},records=records,passed=True,physical_release=False)
 (out/'verification.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print('Native layered CAD: 2 valid, nonoverlapping panels; volumes independently reconciled')
try:run()
except Exception:
 import traceback
 traceback.print_exc();sys.exit(1)
