"""Native FreeCAD solid export worker; SI recipe -> mm FCStd and STEP."""
import json,math,re,time
from hashlib import sha256
from pathlib import Path
import FreeCAD as App
import Part,Import


def volume(e):
    s=e['shape']
    if s=='box':
        x,y,z=e['size_m']
        return x*y*z-sum(math.pi*(h['diameter_m']/2)**2*h.get('length_m',e['size_m']['xyz'.index(h.get('axis','z'))]) for h in e.get('holes',[]))
    if s in ('cylinder','tube'):return math.pi*(e['radius_m']**2-e.get('inner_radius_m',0.)**2)*e['length_m']
    if s=='sphere':return 4*math.pi*e['radius_m']**3/3
    if s=='profile':
        p=e['points_yz_m'];return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])))/2*e['length_m']
    return None


def vec(p):return App.Vector(*[x*1000 for x in p])


def make(e):
    at=vec(e['at_m']);s=e['shape']
    if s=='box':
        sh=Part.makeBox(*[x*1000 for x in e['size_m']],at)
        for hole in e.get('holes',[]):
            index='xyz'.index(hole.get('axis','z'));start=e['at_m'][:];axis=[0,0,0];axis[index]=1
            for j,k in enumerate(('x_m','y_m','z_m')):
                if j!=index:start[j]+=hole.get(k,0.)
            sh=sh.cut(Part.makeCylinder(hole['diameter_m']*500,hole.get('length_m',e['size_m'][index])*1000,vec(start),App.Vector(*axis)))
        return sh
    if s in ('cylinder','tube'):
        axis=App.Vector(*e['axis']);sh=Part.makeCylinder(e['radius_m']*1000,e['length_m']*1000,at,axis)
        if s=='tube':sh=sh.cut(Part.makeCylinder(e['inner_radius_m']*1000,e['length_m']*1000,at,axis))
        return sh
    if s=='sphere':return Part.makeSphere(e['radius_m']*1000,at)
    if s=='profile':
        p=[at+App.Vector(0,y*1000,z*1000) for y,z in e['points_yz_m']]
        wire=Part.makePolygon(p+[p[0]]);return Part.Face(wire).extrude(App.Vector(e['length_m']*1000,0,0))
    parts=[];points=[at+vec(p) for p in e['path_m']];r=e['radius_m']*1000
    for a,b in zip(points,points[1:]):parts.append(Part.makeCylinder(r,(b-a).Length,a,(b-a)))
    parts.extend(Part.makeSphere(r,p) for p in points[1:-1])
    return Part.makeCompound(parts)


def main():
    # FreeCADCmd treats remaining argv as filenames; launcher defines these.
    started=time.monotonic();data=json.loads(Path(SCENE_PATH).read_bytes());out=Path(OUTPUT_PATH);out.mkdir(parents=True,exist_ok=False)
    doc=App.newDocument('OpenSourceRail_Study');objects=[];exact=0.;native=0.;source_mass=0.;source_parts=0;source_mass_unknowns=0;errors=[]
    assembly=doc.addObject('App::DocumentObjectGroup','Assembly');assembly.Label=data['title']+' (outline)'
    groups={}
    for i,e in enumerate(data['entities']):
        sh=make(e)
        if sh.isNull() or not sh.isValid() or sh.Volume<=0:raise ValueError('Invalid native solid: '+e['id'])
        obj=doc.addObject('PartDesign::Feature','P'+str(i));obj.Label=e['id'];obj.Shape=sh
        key=e.get('group','other')
        if key not in groups:
            group=doc.addObject('App::DocumentObjectGroup','Subsystem'+str(len(groups)))
            group.Label=key;assembly.addObject(group);groups[key]=group
        groups[key].addObject(obj)
        for key,val in [('DimensionBasis',e['basis']),('DimensionSource',str(e['source'])),('Subsystem',e.get('group','')),('VisualStudyID',data['visual_study_id'])]:
            obj.addProperty('App::PropertyString',key);setattr(obj,key,val)
        obj.addProperty('App::PropertyString','DisplayFamily');obj.DisplayFamily=e['material']
        if e.get('source_material'):
            obj.addProperty('App::PropertyString','SourceMaterial');obj.SourceMaterial=str(e['source_material'])
        obj.addProperty('App::PropertyString','SIRecipe');obj.SIRecipe=json.dumps({k:e[k] for k in
            ('shape','at_m','size_m','axis','radius_m','inner_radius_m','length_m','holes','points_yz_m','path_m') if k in e},sort_keys=True)
        if e.get('source_part_id'):
            obj.addProperty('App::PropertyString','SourcePartID');obj.SourcePartID=e['source_part_id']
        if e.get('source_mass_kg') is not None:
            obj.addProperty('App::PropertyFloat','SourceStockMassKg');obj.SourceStockMassKg=e['source_mass_kg']
        obj.addProperty('App::PropertyBool','PhysicalAccepted');obj.PhysicalAccepted=False
        expected=volume(e)
        if expected is not None:
            actual=sh.Volume/1e9;exact+=expected;native+=actual
            if abs(expected-actual)>max(1e-9,expected*1e-7):errors.append(e['id'])
        if e['basis']=='source-geometry':
            source_parts+=1
            if e.get('source_mass_kg') is None:source_mass_unknowns+=1
            else:source_mass+=e['source_mass_kg']
        objects.append(obj)
    if errors:raise ValueError('Native volume mismatch: '+str(errors[:10]))
    doc.recompute();doc.saveAs(str(out/(data['id']+'.FCStd')));Import.export(objects,str(out/(data['id']+'.step')))
    total=sum(o.Shape.Volume for o in objects)/1e9
    App.closeDocument(doc.Name)
    reopened=App.openDocument(str(out/(data['id']+'.FCStd')))
    # FreeCAD groups expose an aggregate Shape too; count only actual features.
    reopened_parts=[o for o in reopened.Objects if o.isDerivedFrom('Part::Feature')]
    if len(reopened_parts)!=len(objects) or len(reopened.Objects)!=len(objects)+len(groups)+1:
        raise ValueError('Reopened native assembly tree differs')
    reopened_volume=sum(o.Shape.Volume for o in reopened_parts)/1e9
    if abs(reopened_volume-total)>max(1e-8,total*1e-8):raise ValueError('Native document reopened volume differs')
    App.closeDocument(reopened.Name)
    step=Part.Shape();step.read(str(out/(data['id']+'.step')));step_volume=step.Volume/1e9
    if not step.isValid() or abs(step_volume-total)>max(1e-7,total*1e-7):raise ValueError('STEP reopened shape/volume differs')
    result=dict(schema='osr-native-visual-model/1',assembly_id=data['id'],visual_study_id=data['visual_study_id'],
        worker_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),input_sha256=sha256(Path(SCENE_PATH).read_bytes()).hexdigest(),
        FreeCAD_version=list(App.Version()),parts=len(objects),assembly_groups=len(groups),source_geometry_parts=source_parts,
        declared_source_stock_mass_kg=None if source_mass_unknowns or not source_parts else source_mass,
        source_parts_without_mass=source_mass_unknowns,source_stock_mass_is_installed_mass=False,
        exact_primitive_volume_m3=exact,checked_native_primitive_volume_m3=native,
        native_compound_volume_m3=total,reopened_document_volume_m3=reopened_volume,
        reopened_step_volume_m3=step_volume,all_native_shapes_valid=True,
        routed_envelopes_are_material_quantities=False,display_offsets_applied=False,
        wall_seconds=time.monotonic()-started,complete_installed_mass=False,
        physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False)
    result['files_sha256']={p.name:sha256(p.read_bytes()).hexdigest() for p in
        (out/(data['id']+'.FCStd'),out/(data['id']+'.step'))}
    (out/'cad.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')

if __name__=='__main__':main()
