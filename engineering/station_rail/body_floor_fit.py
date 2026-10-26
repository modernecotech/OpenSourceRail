"""Counted floor cutouts and solid collars for the separate post-foot experiment.

This is a fit-up proposal, never the development baseline. No floor/collar shear
stiffness is credited by body_frame. Native Boolean/reopen checks verify stock
volumes; they do not qualify joints, tread finish, sealing, fire or fatigue.
"""
from copy import deepcopy
from math import prod
from pathlib import Path
import json,os,subprocess
from . import ROOT,FLAGS
from . import body_frame
from .common import encoded,identity,digest,source_map
from .vehicle import box
PRODUCER='engineering/station_rail/body_floor_fit.py'


def intersection(a,b):
    lo=[max(a['at_m'][j],b['at_m'][j]) for j in range(3)]
    hi=[min(a['at_m'][j]+a['size_m'][j],b['at_m'][j]+b['size_m'][j]) for j in range(3)]
    if min(y-x for x,y in zip(lo,hi))<=1e-10:return None
    return dict(at_m=lo,size_m=[y-x for x,y in zip(lo,hi)])


def hole_intersects(p,cut):
    # Existing floor holes run through z. Refuse a cut/hole union that this
    # deliberately simple exact volume subtraction cannot account for.
    for h in p.get('holes',[]):
        if h.get('axis','z')!='z':raise ValueError('Only source floor z-holes supported')
        xy=[p['at_m'][j]+h.get(k,0.) for j,k in enumerate(('x_m','y_m'))]
        d2=sum(max(cut['at_m'][j]-xy[j],0.,xy[j]-cut['at_m'][j]-cut['size_m'][j])**2 for j in range(2))
        if d2<(h['diameter_m']/2)**2-1e-14:return True
    return False


def build(vehicle,root=ROOT):
    frame=body_frame.build(vehicle,root)['variants'][1]
    risers=[p for p in frame['added_material_parts'] if p['id'].endswith('/riser')]
    collars=[];ports=[];omitted=[]
    for riser in risers:
        x,y,z0=riser['at_m'];dx,dy,dz=riser['size_m'];w=.012;z=.9357;h=1.001-z
        prefix=riser['id'].replace('/riser','/floor-collar')
        ports.append(dict(at_m=list(riser['at_m']),size_m=list(riser['size_m']),riser_id=riser['id']))
        for suffix,at,size in [('x-minus',(x-w,y-w,z),(w,dy+2*w,h)),('x-plus',(x+dx,y-w,z),(w,dy+2*w,h)),
                               ('y-minus',(x,y-w,z),(dx,w,h)),('y-plus',(x,y+dy,z),(dx,w,h))]:
            candidate=box(prefix+'/'+suffix,at,size,system='post-floor-collars')
            conflicts=[p['id'] for p in vehicle['geometry_parts'] if p.get('kind')=='box' and '/floor/' not in p['id'] and '/floor-' not in p['id'] and intersection(p,candidate)]
            if conflicts:
                if not suffix.startswith('x-'):raise ValueError('No clear collar transverse flange: '+str(conflicts))
                omitted.append(dict(omitted_collar_part=candidate['id'],reason='Preserve existing door aperture and moving leaf envelope',conflicting_parts=conflicts));continue
            collars.append(candidate);ports.append(dict(at_m=list(at),size_m=list(size),riser_id=riser['id']))
    changed=[];removed=[];unmodified=[]
    for p in vehicle['geometry_parts']:
        if p.get('kind')!='box':unmodified.append(p);continue
        cuts=[c for port in ports if (c:=intersection(p,port))]
        if not cuts:unmodified.append(p);continue
        if '/floor/' not in p['id'] and '/floor-' not in p['id']:raise ValueError('Unexpected non-floor removal: '+p['id'])
        if any(hole_intersects(p,c) for c in cuts):raise ValueError('Floor port overlaps a retained cylindrical hole')
        if any(intersection(a,b) for i,a in enumerate(cuts) for b in cuts[i+1:]):raise ValueError('Cutout ports overlap')
        q=deepcopy(p);q['source_part_id']=p['id'];q['rectangular_cutouts']=cuts;q['kind']='box-with-rectangular-cutouts'
        q['id']='floor-fit/'+identity(dict(parent_part_id=p['id'],cuts=cuts))
        dv=sum(prod(c['size_m']) for c in cuts);q['volume_m3']-=dv;q['mass_kg']=q['volume_m3']*q['density_kg_m3']
        q['cg_m']=[(p['volume_m3']*p['cg_m'][j]-sum(prod(c['size_m'])*(c['at_m'][j]+c['size_m'][j]/2) for c in cuts))/q['volume_m3'] for j in range(3)]
        q.pop('inertia_kg_m2',None);q['inertia_scope']='Changed part inertia not recomputed; parent inertia cannot be reused'
        if q['volume_m3']<=0:raise ValueError('Cutout removes the complete parent part')
        changed.append(q);removed.append(dict(parent_part_id=p['id'],replacement_part_id=q['id'],removed_volume_m3=dv,removed_mass_kg=dv*p['density_kg_m3']))
    # The closed fit-up geometry has positive-area contact at all four collar
    # inner faces and post riser. No physical bolt/weld or adhesive detail yet.
    parts=[*changed,*frame['added_material_parts'],*collars]
    extra=sum(p['mass_kg'] for p in frame['added_material_parts'])+sum(p['mass_kg'] for p in collars)
    saving=sum(r['removed_mass_kg'] for r in removed)
    definition=dict(parent_candidate_id=vehicle['candidate_id'],parent_frame_alternative_id=frame['alternative_id'],
        geometry_parts=parts,removed_stock=removed,ports=ports,unchanged_parent_part_ids=[p['id'] for p in unmodified])
    value=dict(schema='osr-v06-body-floor-fit/1',**{k:vehicle[k] for k in body_frame.IDS},alternative_id=identity(definition),
        physical_definition=definition,collar_count=len(risers),collar_stock_parts=len(collars),omitted_door_adjacent_flanges=omitted,changed_parent_parts=len(changed),
        post_connector_mass_kg=frame['added_mass_kg'],collar_material_mass_kg=sum(p['mass_kg'] for p in collars),
        removed_material_kg=saving,net_material_mass_delta_kg=extra-saving,
        accounted_tare_kg_per_car=vehicle['mass']['accounted_tare_kg_per_car']+extra-saving,
        accounted_normal_kg_per_car=vehicle['mass']['accounted_cap_loaded_kg_per_car']+extra-saving,
        additional_connection_hardware_mass_kg=None,complete_connection_mass_known=False,
        collar_top_m=1.001,retained_floor_top_m=1.0015,retained_floor_cap_thickness_m=.0005,tread_recess_m=0.,
        remaining_gates=['Specific weld/fastener and adhesive load paths','Corner concentrations and floor shear/buckling',
            'Strength and local bond of retained 0.5mm floor-cap layer over collar','Water sealing and corrosion isolation',
            'Al/GFRP differential expansion, fire and fatigue','Whole-car and removal-path clash inspection'],
        source_sha256={**vehicle['source_sha256'],**source_map(root,(body_frame.PRODUCER,)),PRODUCER:digest(__file__)},**FLAGS)
    value['evaluation_id']=identity(value);return value


SCRIPT=r'''
import FreeCAD as A,Part,Import,json,pathlib
folder=pathlib.Path(__file__).parent;data=json.loads((folder/'definition.json').read_text());parts=data['physical_definition']['geometry_parts']
doc=A.newDocument('OSR_floor_ports');objects=[];mass=0.;volume=0.;errors=[];shapes=[]
for i,p in enumerate(parts):
    sh=Part.makeBox(*[s*1000 for s in p['size_m']],A.Vector(*[s*1000 for s in p['at_m']]))
    for hole in p.get('holes',[]):
        start=list(p['at_m']);start[0]+=hole.get('x_m',0.);start[1]+=hole.get('y_m',0.)
        sh=sh.cut(Part.makeCylinder(hole['diameter_m']*500,p['size_m'][2]*1000,A.Vector(*[s*1000 for s in start]),A.Vector(0,0,1)))
    for cut in p.get('rectangular_cutouts',[]):
        sh=sh.cut(Part.makeBox(*[s*1000 for s in cut['size_m']],A.Vector(*[s*1000 for s in cut['at_m']])))
    vm=sh.Volume/1e9
    if not sh.isValid() or abs(vm-p['volume_m3'])>max(1e-11,p['volume_m3']*1e-7):errors.append(p['id'])
    mass+=vm*p['density_kg_m3'];volume+=vm;shapes.append(sh)
    obj=doc.addObject('PartDesign::Feature','Part_'+str(i));obj.Label=p['id'];obj.Shape=sh;objects.append(obj)
clashes=[]
for i,a in enumerate(shapes):
    for j,b in enumerate(shapes[i+1:],i+1):
        if 'source_part_id' in parts[i] and 'source_part_id' in parts[j]:continue
        if not a.BoundBox.isIntersected(b.BoundBox):continue
        overlap=a.common(b).Volume/1e9
        if overlap>1e-11:clashes.append({'a':parts[i]['id'],'b':parts[j]['id'],'overlap_volume_m3':overlap})
doc.recompute();doc.saveAs(str(folder/'floor-fit.FCStd'));Import.export(objects,str(folder/'floor-fit.step'));A.closeDocument(doc.Name)
doc=A.openDocument(str(folder/'floor-fit.FCStd'));reopened=sum(o.Shape.Volume for o in doc.Objects if hasattr(o,'Shape'))/1e9
step=Part.Shape();step.read(str(folder/'floor-fit.step'));stepvol=step.Volume/1e9
(folder/'native-result.json').write_text(json.dumps(dict(part_count=len(parts),native_mass_kg=mass,native_volume_m3=volume,
volume_error_ids=errors,positive_volume_clashes=clashes,reopened_volume_m3=reopened,step_volume_m3=stepvol,FreeCAD_version=list(A.Version())),sort_keys=True,indent=2)+'\n')
A.closeDocument(doc.Name)
'''


def run(output,vehicle,root=ROOT):
    output=Path(output).resolve()
    if output.exists():raise ValueError('Fresh floor-fit directory required')
    output.mkdir(parents=True);definition=build(vehicle,root);(output/'definition.json').write_bytes(encoded(definition));(output/'worker.py').write_text(SCRIPT)
    proc=subprocess.run(['flatpak','run','--filesystem='+str(output),'--command=FreeCADCmd','org.freecad.FreeCAD',str(output/'worker.py')],cwd=output,capture_output=True,text=True,timeout=180)
    (output/'stdout.log').write_text(proc.stdout);(output/'stderr.log').write_text(proc.stderr)
    if proc.returncode or not (output/'native-result.json').is_file():raise RuntimeError('FreeCAD floor-fit failed; native logs retained')
    cad=json.loads((output/'native-result.json').read_bytes());expected=sum(p['mass_kg'] for p in definition['physical_definition']['geometry_parts'])
    if cad['volume_error_ids'] or abs(cad['native_mass_kg']-expected)>1e-5:raise ValueError('Floor-fit native stock mass differs')
    if max(abs(cad[k]-cad['native_volume_m3']) for k in ('reopened_volume_m3','step_volume_m3'))>1e-8:raise ValueError('Floor-fit reopened volume differs')
    result=dict(schema='osr-v06-native-floor-fit/1',alternative_id=definition['alternative_id'],parent_candidate_id=vehicle['candidate_id'],
        execution='completed',CAD=cad,fit_subset_clash_screen='fail' if cad['positive_volume_clashes'] else 'pass',
        whole_vehicle_clearance_screen='unknown',net_material_mass_delta_kg=definition['net_material_mass_delta_kg'],
        source_sha256=definition['source_sha256'],scope='Affected floor/lap stock, counted feet/risers and collars only; hardware and whole assembly remain incomplete',**FLAGS)
    if build(vehicle,root)['source_sha256']!=definition['source_sha256']:raise ValueError('Floor-fit source changed during execution')
    result['evaluation_id']=identity(result);(output/'result.json').write_bytes(encoded(result));manifest=dict(source_sha256=definition['source_sha256'],files_sha256={p.relative_to(output).as_posix():digest(p) for p in sorted(output.rglob('*')) if p.is_file()},**FLAGS)
    manifest['manifest_id']=identity(manifest);(output/'manifest.json').write_bytes(encoded(manifest));return result


def verify(output,vehicle,root=ROOT):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes());r=json.loads((output/'result.json').read_bytes())
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Floor-fit manifest differs')
    if build(vehicle,root)['source_sha256']!=m['source_sha256']:raise ValueError('Floor-fit source differs')
    if r['evaluation_id']!=identity({k:v for k,v in r.items() if k!='evaluation_id'}):raise ValueError('Floor-fit result identity differs')
    for name,h in m['files_sha256'].items():
        if digest(output/name)!=h:raise ValueError('Floor-fit output differs')
    if any(r.get(k) is not v for k,v in FLAGS.items()):raise ValueError('Floor fit cannot grant release')
    return dict(verified=True,evaluation_id=r['evaluation_id'],**FLAGS)
