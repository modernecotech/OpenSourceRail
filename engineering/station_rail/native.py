"""Executed FreeCAD material assembly and CalculiX wheel-underframe fixtures.

The CCX case is the actual hollow side-sill section with ideal supports; its
failure is retained. It does not credit the proposed participating body shell.
"""
from hashlib import sha256
from pathlib import Path
import json
import math
import os
import re
import shutil
import subprocess
from . import ROOT,FLAGS
from .common import encoded,identity,source_map
from . import vehicle

PRODUCER='engineering/station_rail/native.py'

FREECAD_SCRIPT=r'''
import FreeCAD as A, Part, Import
import json, pathlib, sys
folder=pathlib.Path(__file__).parent
inputs=json.loads((folder/'input.json').read_text())
doc=A.newDocument('OSR_v06_station_rail')
groups={};mass=0.;volume=0.;mismatch=[]
for p in inputs['parts']:
    origin=A.Vector(*[x*1000 for x in p['at_m']])
    if p['kind']=='box':
        sh=Part.makeBox(*[x*1000 for x in p['size_m']],origin)
        for hole in p.get('holes',[]):
            axis=hole.get('axis','z');index='xyz'.index(axis)
            start=list(p['at_m'])
            for j,key in enumerate(('x_m','y_m','z_m')):
                if j!=index:start[j]+=hole.get(key,0.)
            direction=[0.,0.,0.];direction[index]=1.
            cutter=Part.makeCylinder(hole['diameter_m']*500,hole.get('length_m',p['size_m'][index])*1000,A.Vector(*[x*1000 for x in start]),A.Vector(*direction))
            sh=sh.cut(cutter)
    else:
        axis=A.Vector(*p['axis'])
        sh=Part.makeCylinder(p['radius_m']*1000,p['length_m']*1000,origin,axis)
        if p.get('inner_radius_m',0)>0:
            sh=sh.cut(Part.makeCylinder(p['inner_radius_m']*1000,p['length_m']*1000,origin,axis))
    vm3=sh.Volume/1e9
    if abs(vm3-p['volume_m3'])>max(1e-10,p['volume_m3']*1e-8):mismatch.append(p['id'])
    mass+=vm3*p['density_kg_m3'];volume+=vm3
    groups.setdefault(p.get('system','body-fitout'),[]).append(sh)
objects=[]
for i,(name,shapes) in enumerate(sorted(groups.items())):
    obj=doc.addObject('PartDesign::Feature','Material_'+str(i));obj.Label=name
    obj.Shape=Part.makeCompound(shapes);objects.append(obj)
doc.recompute();doc.saveAs(str(folder/'vehicle.FCStd'))
Import.export(objects,str(folder/'vehicle.step'))
A.closeDocument(doc.Name)
reopened=A.openDocument(str(folder/'vehicle.FCStd'))
reopenedvol=sum(obj.Shape.Volume for obj in reopened.Objects if hasattr(obj,'Shape'))/1e9
step_shape=Part.Shape();step_shape.read(str(folder/'vehicle.step'))
step_volume=step_shape.Volume/1e9
result={'FreeCAD_version':list(A.Version()),'part_count':len(inputs['parts']),'material_groups':len(groups),
        'native_material_kg':mass,'native_volume_m3':volume,'reopened_volume_m3':reopenedvol,
        'part_volume_mismatch_ids':mismatch,'all_part_volumes_match':not mismatch,
        'reopened_volume_matches':abs(reopenedvol-volume)<1e-8,
        'step_reopened_volume_m3':step_volume,'step_reopened_volume_matches':abs(step_volume-volume)<1e-8,
        'complete_installed_geometry':False,'interference_and_removal_qualified':False}
(folder/'cad-result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
A.closeDocument(reopened.Name)
'''


def _ccx_deck(v,dx):
    # Single physical sill: 180x350x8 mm, 17 m long, supported at +/-6.4m.
    # Four hollow walls share nodes. Full uniform half-car force is applied.
    xs=sorted(set(round(-8.5+i*dx,9) for i in range(round(17/dx)+1))|{-6.4,6.4,0.})
    ys=[-.09,-.082,.082,.09];zs=[.50,.508,.842,.85]
    nodes={};coordinates=[];n=0
    for i,x in enumerate(xs):
        for j,y in enumerate(ys):
            for k,z in enumerate(zs):
                n+=1;nodes[(i,j,k)]=n;coordinates.append((n,x,y,z))
    elements=[];eid=0
    for i in range(len(xs)-1):
        for j in range(3):
            for k in range(3):
                if j==1 and k==1:continue
                eid+=1
                elements.append((eid,*[nodes[q] for q in ((i,j,k),(i+1,j,k),(i+1,j+1,k),(i,j+1,k),(i,j,k+1),(i+1,j,k+1),(i+1,j+1,k+1),(i,j+1,k+1))]))
    lines=['*HEADING','V06 hollow side sill; whole loaded car half-load; ideal two-bogie supports','*NODE']
    lines += [','.join(map(str,row)) for row in coordinates]
    lines += ['*ELEMENT,TYPE=C3D8,ELSET=SILL']+[','.join(map(str,row)) for row in elements]
    lines += ['*MATERIAL,NAME=AL','*ELASTIC','69000000000,0.33','*SOLID SECTION,ELSET=SILL,MATERIAL=AL','*BOUNDARY']
    for i,x in enumerate(xs):
        if x in (-6.4,6.4):
            for j in range(4):
                for k in range(4):lines.append(f'{nodes[(i,j,k)]},3,3')
        if x==-6.4:
            # A single datum prevents axial drift; lateral translation restrained
            # at both bearings rather than across the whole beam.
            lines.append(f'{nodes[(i,0,0)]},1,1')
        if x in (-6.4,6.4):lines.append(f'{nodes[(i,0,0)]},2,2')
    mid=[nodes[(xs.index(0.),j,k)] for j in range(4) for k in range(4)]
    lines+=['*NSET,NSET=MID',','.join(map(str,mid)),'*STEP','*STATIC','*CLOAD']
    total=v['mass']['accounted_cap_loaded_kg_per_car']*9.80665/2
    for i,x in enumerate(xs):
        width=(xs[min(i+1,len(xs)-1)]-xs[max(i-1,0)])/2
        load=-total*width/17/16
        for j in range(4):
            for k in range(4):lines.append(f'{nodes[(i,j,k)]},3,{load:.12g}')
    lines+=['*NODE PRINT,NSET=MID','U','*NODE FILE','U','*END STEP','']
    return '\n'.join(lines),len(coordinates),len(elements)


def _run_ccx(folder,v,dx):
    folder.mkdir();deck,nodes,elements=_ccx_deck(v,dx);(folder/'sill.inp').write_text(deck)
    proc=subprocess.run(['/usr/bin/ccx','sill'],cwd=folder,capture_output=True,text=True,timeout=180,env={**os.environ,'OMP_NUM_THREADS':'1'})
    (folder/'stdout.log').write_text(proc.stdout);(folder/'stderr.log').write_text(proc.stderr)
    if proc.returncode or not (folder/'sill.dat').is_file():raise RuntimeError('CalculiX sill fixture failed: '+str(proc.returncode))
    values=[]
    for line in (folder/'sill.dat').read_text().splitlines():
        fields=line.split()
        if len(fields)==4 and fields[0].isdigit():
            try:values.append([float(x) for x in fields[1:]])
            except ValueError:pass
    if not values:raise ValueError('No actual CalculiX displacement records')
    maxdisp=max(abs(row[2]) for row in values)
    analytical=v['underframe_screens']['normal']['midspan_deflection_m']
    return dict(execution='completed',solver='CalculiX',mesh_axial_m=dx,node_count=nodes,element_count=elements,
        maximum_midspan_vertical_displacement_m=maxdisp,analytical_Euler_deflection_m=analytical,
        discrepancy_fraction=(maxdisp-analytical)/analytical,engineering_screen='pass' if maxdisp<=12.8/500 else 'fail',
        scope='Single physical hollow side sill at half whole-car normal load, ideal bearings; no body-shell/post/joint stiffness credited')


def run(output,root=ROOT):
    root=Path(root);output=Path(output).resolve()
    if output.exists() and any(output.iterdir()):raise ValueError('Fresh native run directory required')
    output.mkdir(parents=True,exist_ok=True);v=vehicle.build(root)
    ids={k:v[k] for k in ('candidate_id','body_candidate_id','support_component_id','propulsion_component_id')}
    inputs=dict(schema='osr-station-rail-native-input/1',**ids,parts=v['geometry_parts'])
    (output/'input.json').write_bytes(encoded(inputs));(output/'worker.py').write_text(FREECAD_SCRIPT)
    proc=subprocess.run(['flatpak','run','--filesystem='+str(output),'--command=FreeCADCmd','org.freecad.FreeCAD',str(output/'worker.py')],cwd=output,capture_output=True,text=True,timeout=300)
    (output/'freecad.stdout.log').write_text(proc.stdout);(output/'freecad.stderr.log').write_text(proc.stderr)
    if proc.returncode or not (output/'cad-result.json').is_file():raise RuntimeError('Native FreeCAD execution failed; inspect logs')
    cad=json.loads((output/'cad-result.json').read_bytes())
    expected=v['mass']['located_material_kg']
    if not cad['all_part_volumes_match'] or not cad['reopened_volume_matches'] or not cad['step_reopened_volume_matches'] or abs(cad['native_material_kg']-expected)>1e-5:raise ValueError('Native material geometry does not reconcile with candidate stock')
    fixtures=[_run_ccx(output/name,v,dx) for name,dx in (('sill-coarse',.2),('sill-fine',.1))]
    result=dict(schema='osr-station-rail-native/1',**ids,execution='completed',CAD=cad,underframe_fixtures=fixtures,
        deflection_refinement_change_fraction=abs(fixtures[-1]['maximum_midspan_vertical_displacement_m']-fixtures[0]['maximum_midspan_vertical_displacement_m'])/fixtures[-1]['maximum_midspan_vertical_displacement_m'],
        scope='Actual material CAD export/reopen and limited underframe FEA. Neither complete equipped structural proof nor a moving train simulation.',
        source_sha256={**v['source_sha256'],**source_map(ROOT,(PRODUCER,))},**FLAGS)
    result['evaluation_id']=identity(result);(output/'result.json').write_bytes(encoded(result))
    files={p.relative_to(output).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(output.rglob('*')) if p.is_file()}
    manifest=dict(schema='osr-station-rail-native-manifest/1',**ids,evaluation_id=result['evaluation_id'],source_sha256=result['source_sha256'],files_sha256=files,**FLAGS)
    manifest['manifest_id']=identity(manifest);(output/'manifest.json').write_bytes(encoded(manifest))
    return result


def verify(output,root=ROOT):
    output=Path(output);v=vehicle.build(root);m=json.loads((output/'manifest.json').read_bytes());r=json.loads((output/'result.json').read_bytes())
    if m['manifest_id']!=identity({k:x for k,x in m.items() if k!='manifest_id'}):raise ValueError('Native manifest identity differs')
    for k in ('candidate_id','body_candidate_id','support_component_id','propulsion_component_id'):
        if m[k]!=v[k] or r[k]!=v[k]:raise ValueError('Native physical candidate differs')
    for name,h in m['source_sha256'].items():
        p=Path(root)/name
        if not p.is_file() or sha256(p.read_bytes()).hexdigest()!=h:raise ValueError('Native source changed: '+name)
    for name,h in m['files_sha256'].items():
        if sha256((output/name).read_bytes()).hexdigest()!=h:raise ValueError('Native output changed: '+name)
    if r['evaluation_id']!=identity({k:x for k,x in r.items() if k!='evaluation_id'}):raise ValueError('Native result identity differs')
    if any(m.get(k) is not val or r.get(k) is not val for k,val in FLAGS.items()):raise ValueError('Native evidence cannot release a train')
    return dict(verified=True,evaluation_id=r['evaluation_id'],candidate_id=v['candidate_id'],native_material_kg=r['CAD']['native_material_kg'],**FLAGS)
