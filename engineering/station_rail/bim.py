"""Native IFC of selected concrete and equivalent-area running rails, not full BIM."""
from pathlib import Path
import hashlib,json,uuid
from .common import encoded,identity
from .evaluation import IDS
from . import FLAGS

def parts(record):
    r=record['civil']['selected_reference'];d=r['section']['dimensions'];L=r['span_m'];B=d['outer_width_m'];H=d['depth_m'];tw=d['wall_m'];tf=d['flange_m'];top=-.172
    rows=[]
    def box(name,at,size,material):rows.append(dict(id=name,at_m=list(at),size_m=list(size),material=material,volume_m3=size[0]*size[1]*size[2]))
    box('box-bottom',(0,-B/2,top-H),(L,B,tf),'concrete')
    box('box-top',(0,-B/2,top-tf),(L,B,tf),'concrete')
    for side in (-1,1):box('box-web-'+str(side),(0,-B/2 if side<0 else B/2-tw,top-H+tf),(L,tw,H-2*tf),'concrete')
    diaphragm=r['diaphragm_definition']
    for end in (0,1):box('end-diaphragm-'+str(end),(0 if end==0 else L-diaphragm['thickness_m'],-diaphragm['clear_width_m']/2,top-H+tf),
        (diaphragm['thickness_m'],diaphragm['clear_width_m'],diaphragm['height_m']),'concrete')
    # Equivalent-area straight blocks retain mass and outer width/height only;
    # actual60E1 fillets, cant, worn profile and contact are not represented.
    area=60.21/7850.;foot=.15;head=.072;tfrail=.016;th=.040;hw=.172-tfrail-th;web=(area-foot*tfrail-head*th)/hw
    for side in (-1,1):
        centre=side*.7535
        box('rail-foot-'+str(side),(0,centre-foot/2,-.172),(L,foot,tfrail),'steel')
        box('rail-web-'+str(side),(0,centre-web/2,-.172+tfrail),(L,web,hw),'steel')
        box('rail-head-'+str(side),(0,centre-head/2,-th),(L,head,th),'steel')
    return rows

def write(output,record):
    output=Path(output)
    try:
        import ifcopenshell,ifcopenshell.api
        from ifcopenshell.util.unit import calculate_unit_scale
    except ImportError:
        return dict(execution='not-run',reason='IfcOpenShell unavailable',complete_vehicle_IFC=False,**FLAGS)
    api=ifcopenshell.api.run;f=api('project.create_file',version='IFC4')
    project=api('root.create_entity',f,ifc_class='IfcProject',name='OpenSourceRail v0.6 research interface')
    length=api('unit.add_si_unit',f,unit_type='LENGTHUNIT');api('unit.assign_unit',f,units=[length])
    model=api('context.add_context',f,context_type='Model');body=api('context.add_context',f,context_type='Model',context_identifier='Body',target_view='MODEL_VIEW',parent=model)
    site=api('root.create_entity',f,ifc_class='IfcSite',name='Reference track');api('aggregate.assign_object',f,products=[site],relating_object=project)
    rows=parts(record)
    for row in rows:
        obj=api('root.create_entity',f,ifc_class='IfcBeam',name=row['id']);obj.GlobalId=ifcopenshell.guid.compress(hashlib.sha256((record['candidate_id']+row['id']).encode()).hexdigest()[:32])
        api('spatial.assign_container',f,products=[obj],relating_structure=site)
        x,y,z=row['at_m'];a,b,c=row['size_m'];vertices=[(x+dx*a,y+dy*b,z+dz*c) for dz in (0,1) for dy in (0,1) for dx in (0,1)]
        faces=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
        rep=api('geometry.add_mesh_representation',f,context=body,vertices=[vertices],faces=[faces],unit_scale=1.)
        api('geometry.assign_representation',f,product=obj,representation=rep)
        pset=api('pset.add_pset',f,product=obj,name='OSR_Development_Identity')
        api('pset.edit_pset',f,pset=pset,properties={**{k:record[k] for k in IDS},'physical_accepted':False,
            'scope':'Concrete selected dimensions; rail equivalent-area blocks only, contact profile omitted','volume_m3':row['volume_m3']})
    # Stable design identities and release-epoch header make repeated exports
    # byte reproducible. These are research design records, not as-built dates.
    for entity in f.by_type('IfcRoot'):
        key=record['candidate_id']+record['civil']['civil_component_id']+entity.is_a()+str(entity.id())
        entity.GlobalId=ifcopenshell.guid.compress(hashlib.sha256(key.encode()).hexdigest()[:32])
    for relation in f.by_type('IfcRelContainedInSpatialStructure'):
        relation.RelatedElements=sorted(relation.RelatedElements,key=lambda entity:entity.GlobalId)
    f.header.file_name.name='selected-interface.ifc'
    f.header.file_name.time_stamp='2026-10-26T00:00:00'
    path=output/'selected-interface.ifc';f.write(str(path))
    value=dict(schema='osr-v06-IFC/1',**{k:record[k] for k in IDS},execution='completed',
        parts=rows,ifcopenshell_version=ifcopenshell.version,units='m',native_reopened=True,
        complete_vehicle_IFC=False,complete_civil_IFC=False,rail_profile_qualification=False,
        scope='Selected reference concrete and equivalent-area60E1 blocks; fasteners, reinforcement, prestress, bearings, piers, foundations and vehicle not modelled',**FLAGS)
    value['definition_id']=identity(value);verify(path,record,value);return value

def verify(path,record,receipt):
    import ifcopenshell,ifcopenshell.geom
    from ifcopenshell.util.element import get_pset
    from ifcopenshell.util.shape import get_volume
    f=ifcopenshell.open(str(path));elements=f.by_type('IfcBeam');expected={r['id']:r for r in parts(record)}
    if len(elements)!=len(expected):raise ValueError('IFC part count differs')
    for obj in elements:
        row=expected[obj.Name];props=get_pset(obj,'OSR_Development_Identity')
        if any(props.get(k)!=record[k] for k in IDS) or props.get('physical_accepted') is not False:raise ValueError('IFC identity or release differs')
        shape=ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(),obj)
        if abs(get_volume(shape.geometry)-row['volume_m3'])>1e-7:raise ValueError('Native IFC volume differs')
    if receipt['parts']!=list(expected.values()):raise ValueError('IFC definition differs')
    return dict(verified=True,native_reopened=True,part_count=len(elements),geometry_and_identity_checks=True,physical_accepted=False)
