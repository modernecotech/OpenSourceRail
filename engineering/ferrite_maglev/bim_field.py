"""Executed IFC4.3/IDS1/BCF3 exchange and typed, unreleased field evidence.

The exchange covers one dimensioned magnetic module and a25m concrete box.
It does not manufacture, survey or accept these objects, or export a whole city.
"""
from hashlib import sha256
from pathlib import Path
import gzip
import io
import json
import math
import stat
import sys
import tempfile
import uuid
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
from . import model, candidate_magnetics, candidate_structures, candidate_manufacturing as manufacturing, delivery_platform as platform

ROOT=model.ROOT
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/bim-field'
SCHEMA='osr-candidate-bim-field/1'
XSD=Path(__file__).parent/'data/bcf3-schemas'
GUID_NS=uuid.UUID('cb102e43-980b-45ae-a19a-f14c9b01e41d')
FIELD=ROOT/'services/integration'
FILES={'candidate.ifc.gz','candidate.ids.gz','candidate-issues.bcf.gz','study.json.gz','README.md'}
LIMITS={'candidate.ifc.gz':64*1024*1024,'candidate.ids.gz':2*1024*1024,'candidate-issues.bcf.gz':8*1024*1024,'study.json.gz':16*1024*1024}
if str(FIELD) not in sys.path:sys.path.insert(0,str(FIELD))
from osr_integration.operations import field


def source_paths():return sorted({Path(__file__),Path(field.__file__),Path(platform.__file__),Path(model.__file__),FIELD/'osr_integration/config.py',FIELD/'osr_integration/operations/contracts.py',Path(__file__).with_name('requirements.txt'),ROOT/'engineering/analysis/tests/test_ferrite_maglev_bim_field.py',
    *candidate_magnetics.source_paths(),*candidate_structures.source_paths(),*manufacturing.source_paths(),*[p for p in XSD.iterdir() if p.is_file()]})
def sources():return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in source_paths()}
def identity(configuration,part):return str(uuid.uuid5(GUID_NS,configuration+'/'+part))


def _ordinary(path,maximum):
    path=Path(path)
    if any(p.is_symlink() for p in [path,*path.parents]) or not stat.S_ISREG(path.stat().st_mode) or path.stat().st_size>maximum:raise ValueError('bounded ordinary BIM evidence required')
    with path.open('rb') as stream:data=stream.read(maximum+1)
    if len(data)>maximum:raise ValueError('BIM evidence exceeds bound')
    return data


def _inflate(data,maximum):
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:raw=stream.read(maximum+1)
    except (OSError,EOFError) as exc:raise ValueError('invalid compressed BIM evidence') from exc
    if len(raw)>maximum:raise ValueError('BIM decompression exceeds bound')
    return raw


def _xml(data):
    if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():raise ValueError('external/entity XML declarations forbidden')
    try:return ET.fromstring(data)
    except ET.ParseError as exc:raise ValueError('invalid retained BIM XML') from exc


def _signature(element):
    return (element.tag,tuple(sorted(element.attrib.items())),(element.text or '').strip(),tuple(_signature(c) for c in element))


def _specification(configuration):
    from ifctester import ids
    specs=ids.Ids(title='OpenSourceRail controlled unqualified component identities',version='1.0',description='Identity/quantity exchange, not engineering or site acceptance')
    spec=ids.Specification(name='Candidate components retain exact identities',minOccurs=1,ifcVersion=['IFC4X3_ADD2']);spec.applicability.append(ids.Entity(name='IFCBUILDINGELEMENTPROXY'))
    for name,value in [('ConfigurationSHA256',configuration),('PartRevision',configuration),('ManufacturingRelease','false')]:spec.requirements.append(ids.Property(propertySet='OSR_ControlledIdentity',baseName=name,value=value,dataType='IFCLABEL'))
    for name in ('PartID','Serial'):spec.requirements.append(ids.Property(propertySet='OSR_ControlledIdentity',baseName=name,dataType='IFCLABEL'))
    specs.specifications.append(spec);return specs


def _solids(f,part):
    """Real extruded primitives and boolean drilled voids; no envelope mass."""
    def point(v):return f.createIfcCartesianPoint(tuple(float(x) for x in v))
    def direction(v):return f.createIfcDirection(tuple(float(x) for x in v))
    def axis(at=(0,0,0),normal=(0,0,1),ref=(1,0,0)):
        return f.createIfcAxis2Placement3D(point(at),direction(normal),direction(ref))
    def cylinder(d,length,at,ax):
        normal=[0.,0.,0.];normal[ax]=1.;ref=[0.,0.,0.];ref[(ax+1)%3]=1.
        profile=f.createIfcCircleProfileDef('AREA',None,None,float(d)/2)
        return f.createIfcExtrudedAreaSolid(profile,axis(at,normal,ref),direction((0,0,1)),float(length))
    size=part['size_m'];at=np.asarray(part['at_m'],float)
    if part['kind']=='box':
        profile=f.createIfcRectangleProfileDef('AREA',None,None,float(size[0]),float(size[1]))
        pos=at+np.array([size[0]/2,size[1]/2,0.]);solid=f.createIfcExtrudedAreaSolid(profile,axis(pos),direction((0,0,1)),float(size[2]))
    elif part['kind']=='cylinder':
        ax='xyz'.index(part.get('cylinder_axis','z'));pos=at.copy()
        for i in range(3):
            if i!=ax:pos[i]+=size[0]/2
        solid=cylinder(size[0],size[2],pos,ax)
    else:raise ValueError('unsupported native primitive; exchange cannot substitute a box')
    for hole in part.get('holes',[]):
        ax='xyz'.index(hole.get('axis','z'));pos=at.copy()
        for i in range(3):pos[i]+=hole.get('start_m',0.) if i==ax else hole['xyz'[i]+'_m']
        run=hole.get('length_m',size[ax] if part['kind']=='box' else size[2])
        solid=f.createIfcBooleanResult('DIFFERENCE',solid,cylinder(hole['diameter_m'],run,pos,ax))
    return solid


def exchange_parts(candidate,*,beam=None,selection=None,include_rail_and_supports=False,allow_incomplete=False):
    if type(include_rail_and_supports) is not bool:raise ValueError('explicit civil exchange scope required')
    parts=[dict(p,exchange_scope='one magnetic module, module-local frame') for p in candidate['module']['parts']]
    resolved=manufacturing.selected_beam(candidate,beam=beam,selection=selection,allow_incomplete=allow_incomplete)
    geometry=manufacturing._civil_geometry(resolved);density=resolved['assumptions']['concrete']['density_kg_m3']
    sec=resolved['beam']['section'];span=resolved['selection']['span_m']
    # A declared review-layout translation separates a beam coupon from the
    # module coupon. It supplies no installed vehicle/guideway clearance credit.
    offset=[span/2,3.+sec['width_m']/2,sec['depth_m']-resolved['assumptions']['rail_support']['beam_top_z_m']]
    for part in geometry['parts']:
        if part['material']!='concrete' and not include_rail_and_supports:continue
        row=dict(part,id='civil/'+part['id'],at_m=[x+y for x,y in zip(part['at_m'],offset)],
            exchange_scope=f'Selected{span:g}m {sec["id"]} beam coupon; concrete includes endinfills. Review-layout translation only; reinforcement/strand/bearing/foundation installed details remain open.')
        if part['material']=='concrete':row['mass_kg']=part['volume_m3']*density
        if 'cg_m' in part:row['cg_m']=[x+y for x,y in zip(part['cg_m'],offset)]
        parts.append(row)
    for part in candidate.get('additional_stock',[]):
        if part.get('kind') not in {'box','cylinder'} or part.get('equivalent_box'):
            raise ValueError('additional exchange stock needs actual supported primitive geometry')
        row=dict(part,at_m=[part['at_m'][0],part['at_m'][1]+8.,part['at_m'][2]],
            exchange_scope='Known added carrier stock percar, review-layout translated8m laterally. Unresolved bearings/slides/retention are not geometry and remain holds.')
        if 'cg_m' in part:row['cg_m']=[part['cg_m'][0],part['cg_m'][1]+8.,part['cg_m'][2]]
        parts.append(row)
    if len({part['id'] for part in parts})!=len(parts):raise ValueError('unique candidate exchange part IDs required')
    return parts


def export_ifc(directory,candidate=None,*,beam=None,selection=None,include_rail_and_supports=False,allow_incomplete=False):
    import ifcopenshell,ifcopenshell.api,ifcopenshell.geom,ifcopenshell.util.shape
    from ifctester import ids
    candidate=candidate or candidate_magnetics.definition();directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    resolved=manufacturing.selected_beam(candidate,beam=beam,selection=selection,allow_incomplete=allow_incomplete)
    cfg=candidate['configuration_sha256'];f=ifcopenshell.api.run('project.create_file',version='IFC4X3')
    project=ifcopenshell.api.run('root.create_entity',f,ifc_class='IfcProject',name='OpenSourceRail candidate exchange')
    ifcopenshell.api.run('unit.assign_unit',f,length={'is_metric':True,'raw':'METERS'})
    context=ifcopenshell.api.run('context.add_context',f,context_type='Model');body=ifcopenshell.api.run('context.add_context',f,context_type='Model',context_identifier='Body',target_view='MODEL_VIEW',parent=context)
    site=ifcopenshell.api.run('root.create_entity',f,ifc_class='IfcSite',name='Provisional Baghdad component exchange; not surveyed')
    ifcopenshell.api.run('aggregate.assign_object',f,products=[site],relating_object=project)
    rows=[];materials={}
    for part in exchange_parts(candidate,beam=resolved,include_rail_and_supports=include_rail_and_supports,allow_incomplete=allow_incomplete):
        uid=identity(cfg,part['id']);obj=ifcopenshell.api.run('root.create_entity',f,ifc_class='IfcBuildingElementProxy',name=part['id']);obj.GlobalId=ifcopenshell.guid.compress(uuid.UUID(uid).hex)
        obj.Tag='SIM-'+uid[:8];solid=_solids(f,part);representation=f.createIfcShapeRepresentation(body,'Body','CSG',[solid])
        ifcopenshell.api.run('geometry.assign_representation',f,product=obj,representation=representation)
        ifcopenshell.api.run('geometry.edit_object_placement',f,product=obj)
        ifcopenshell.api.run('spatial.assign_container',f,products=[obj],relating_structure=site)
        mat=part['material']
        if mat not in materials:materials[mat]=ifcopenshell.api.run('material.add_material',f,name=mat)
        ifcopenshell.api.run('material.assign_material',f,products=[obj],material=materials[mat])
        properties=dict(ConfigurationSHA256=cfg,PartID=part['id'],PartRevision=cfg,Serial=obj.Tag,ManufacturingRelease='false',
            NetVolumeM3=float(part['volume_m3']),AccountedMassKG=float(part['mass_kg']),Scope=part['exchange_scope'])
        pset=ifcopenshell.api.run('pset.add_pset',f,product=obj,name='OSR_ControlledIdentity');ifcopenshell.api.run('pset.edit_pset',f,pset=pset,properties=properties)
        rows.append(dict(part_id=part['id'],ifc_guid=obj.GlobalId,simulated_serial=obj.Tag,expected_volume_m3=part['volume_m3'],accounted_mass_kg=part['mass_kg'],scope=part['exchange_scope']))
    target=directory/'candidate.ifc';f.write(str(target));reopened=ifcopenshell.open(str(target));settings=ifcopenshell.geom.settings()
    settings.set('mesher-linear-deflection',1e-5);settings.set('mesher-angular-deflection',.1)
    for row in rows:
        shape=ifcopenshell.geom.create_shape(settings,reopened.by_guid(row['ifc_guid']));volume=abs(ifcopenshell.util.shape.get_volume(shape.geometry))
        row.update(reopened_volume_m3=volume,volume_relative_error=abs(volume-row['expected_volume_m3'])/row['expected_volume_m3'])
        if not math.isclose(volume,row['expected_volume_m3'],rel_tol=.001,abs_tol=1e-10):raise ValueError('reopened IFC boolean volume differs: '+row['part_id'])
    specs=_specification(cfg)
    if not specs.to_xml(str(directory/'candidate.ids')):raise ValueError('IDS1 schema validation failed')
    restored=ids.open(str(directory/'candidate.ids'),validate=True);restored.validate(reopened)
    if not all(s.status for s in restored.specifications):raise ValueError('independent IfcTester identity validation failed')
    # Negative control: a stale revision must fail the same executed IDS.
    obj=reopened.by_guid(rows[0]['ifc_guid']);rel=obj.IsDefinedBy[0];pset=rel.RelatingPropertyDefinition
    ifcopenshell.api.run('pset.edit_pset',reopened,pset=pset,properties={'ConfigurationSHA256':'f'*64})
    restored.validate(reopened);negative=not all(s.status for s in restored.specifications)
    if not negative:raise ValueError('stale IFC identity negative control escaped IDS')
    return dict(configuration_sha256=cfg,selected_beam=resolved['selection'],
        selected_beam_sha256=platform.digest(dict(configuration_sha256=cfg,selection=resolved['selection'],beam=resolved['beam'])),
        include_rail_and_supports=include_rail_and_supports,
        incomplete_stock_diagnostic=allow_incomplete,
        ifc_schema=f.schema_identifier,ids_schema_valid=True,ids_pass=True,stale_revision_refused=negative,mesh_linear_deflection_m=1e-5,mesh_angular_deflection_rad=.1,mesh_volume_relative_tolerance=.001,
        parts=rows,total_native_volume_m3=math.fsum(r['reopened_volume_m3'] for r in rows),**platform.FLAGS)


def bcf_exchange(directory,configuration_sha256,parts):
    """BCF3 issue with selected actual IFC component GUIDs, validated upstream XSD."""
    from xmlschema import XMLSchema
    directory=Path(directory);topic_id=identity(configuration_sha256,'field-tolerance-hold');view_id=identity(configuration_sha256,'field-view')
    version=ET.Element('Version',VersionId='3.0');extensions=ET.Element('Extensions')
    for container,item,values in [('TopicTypes','TopicType',['Engineering hold']),('TopicStatuses','TopicStatus',['Open'])]:
        parent=ET.SubElement(extensions,container)
        for value in values:ET.SubElement(parent,item).text=value
    markup=ET.Element('Markup');topic=ET.SubElement(markup,'Topic',Guid=topic_id,TopicType='Engineering hold',TopicStatus='Open')
    for key,value in [('Title','Confirm candidate geometry, material and field survey before release'),('CreationDate','2026-10-23T00:00:00Z'),('CreationAuthor','OpenSourceRail numerical exchange'),('Description','Configuration '+configuration_sha256+'; unexecuted physical dimensional and material acceptance. No automatic handback.')]:ET.SubElement(topic,key).text=value
    viewpoints=ET.SubElement(topic,'Viewpoints');view=ET.SubElement(viewpoints,'ViewPoint',Guid=view_id);ET.SubElement(view,'Viewpoint').text='candidate.bcfv'
    visual=ET.Element('VisualizationInfo',Guid=view_id);components=ET.SubElement(visual,'Components');selection=ET.SubElement(components,'Selection')
    for row in parts[:3]:ET.SubElement(selection,'Component',IfcGuid=row['ifc_guid'])
    ET.SubElement(components,'Visibility',DefaultVisibility='true')
    camera=ET.SubElement(visual,'OrthogonalCamera')
    for name,vec in [('CameraViewPoint',[5,5,5]),('CameraDirection',[-1,-1,-1]),('CameraUpVector',[0,0,1])]:
        node=ET.SubElement(camera,name)
        for axis,value in zip('XYZ',vec):ET.SubElement(node,axis).text=str(value)
    ET.SubElement(camera,'ViewToWorldScale').text='10';ET.SubElement(camera,'AspectRatio').text='1.6'
    members={'bcf.version':(version,'version.xsd'),'extensions.xml':(extensions,'extensions.xsd'),topic_id+'/markup.bcf':(markup,'markup.xsd'),topic_id+'/candidate.bcfv':(visual,'visinfo.xsd')}
    output=directory/'candidate-issues.bcf';valid=[]
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name,(root,schema) in members.items():
            data=ET.tostring(root,encoding='utf-8',xml_declaration=True);validator=XMLSchema(str(XSD/schema));validator.validate(data);z.writestr(name,data);valid.append(name)
    with zipfile.ZipFile(output) as z:
        if set(z.namelist())!=set(members):raise ValueError('BCF inventory differs')
        reopened=ET.fromstring(z.read(topic_id+'/candidate.bcfv'));guids=[e.get('IfcGuid') for e in reopened.findall('./Components/Selection/Component')]
        if guids!=[r['ifc_guid'] for r in parts[:3]]:raise ValueError('BCF selected identities changed')
    return dict(version='3.0',schema_validated_members=valid,selected_ifc_guids=guids,issue_state='Open',independent_acceptance=False)


def field_plan(configuration,part):
    work=dict(id='SIM-BAG-FIELD-BAY',city='baghdad',environment='simulation',asset_id='SIM-BAG-MAGNETIC-BAY',assigned_to='sim-inspector',method_revision='candidate-field-1',erp_task='SIM-CANDIDATE-SURVEY',erp_asset='SIM-BAG-MAGNETIC-BAY',native_modified=configuration,
        instructions='Synthetic dimensional exercise for IFC GUID '+part['ifc_guid']+'; independent site/material acceptance and calibration remain open.',requires_photo=False,
        readings=[dict(id='gap',kind='number',required=True,unit='mm',min=7.5,max=8.5),dict(id='part-revision',kind='text',required=True),dict(id='ifc-guid',kind='text',required=True)])
    return field.validate_work(work)


def assess_field(work,event,*,configuration_sha256,part):
    field.validate_work(work);field.validate_completion(work,event)
    readings=event['readings']
    if work['native_modified']!=configuration_sha256 or readings['part-revision']!=configuration_sha256 or readings['ifc-guid']!=part['ifc_guid']:raise field.Conflict('stale IFC/candidate field identity; refresh and retest')
    return dict(state='performed-awaiting-independent-inspection',configuration_sha256=configuration_sha256,ifc_guid=part['ifc_guid'],serial=part['simulated_serial'],raw_event_sha256=platform.digest(event),simulated=True,**platform.FLAGS)


def study(directory,candidate=None,*,beam=None,selection=None,include_rail_and_supports=False,allow_incomplete=False):
    candidate=candidate or candidate_magnetics.definition();directory=Path(directory);ex=export_ifc(directory,candidate,beam=beam,selection=selection,include_rail_and_supports=include_rail_and_supports,allow_incomplete=allow_incomplete);bcf=bcf_exchange(directory,candidate['configuration_sha256'],ex['parts']);part=ex['parts'][0];work=field_plan(candidate['configuration_sha256'],part)
    event=dict(id='SIM-FIELD-1',device_id='sim-tablet',work_id=work['id'],status='performed-awaiting-inspection',readings={'gap':dict(value=8.,unit='mm'),'part-revision':candidate['configuration_sha256'],'ifc-guid':part['ifc_guid']},photos=[],notes='Synthetic field example, no measured hardware')
    result=assess_field(work,event,configuration_sha256=candidate['configuration_sha256'],part=part);controls=[]
    from copy import deepcopy
    for name,mutate in [('wrong-unit',lambda e:e['readings']['gap'].update(unit='m')),('outside-tolerance',lambda e:e['readings']['gap'].update(value=8.6)),('stale-revision',lambda e:e['readings'].update({'part-revision':'f'*64})),('automatic-handback',lambda e:e.update(status='accepted'))]:
        bad=deepcopy(event);mutate(bad)
        try:assess_field(work,bad,configuration_sha256=candidate['configuration_sha256'],part=part)
        except ValueError:controls.append(dict(id=name,refused=True))
        else:raise ValueError('field negative control escaped: '+name)
    return dict(schema=SCHEMA,configuration_sha256=candidate['configuration_sha256'],exchange=ex,bcf=bcf,work=work,event=event,field_result=result,negative_controls=controls,
        study_pass=ex['ids_pass'] and ex['stale_revision_refused'] and len(controls)==4,
        scope='One magnetic module and explicitly selected beam/span stock exchanged with exact boolean primitive volumes; no whole-train/city IFC, installed reinforcement, accepted tolerance, physical survey, manufacturing or operational release.',**platform.FLAGS)


def readme(selection=None,include_rail_and_supports=False):
    selection=selection or dict(section_id='narrow-deep-reference',span_m=25.)
    return ('\n'.join(['# Candidate BIM and field exchange','',
        'IFC4.3 ADD2 actual component geometry, materials, configuration/part/serial identities and reopened boolean volumes. The executed IDS1 validator requires these identities; a deliberately stale component fails. BCF3 XML members validate against retained buildingSMART schemas and refer to actual IFC GUIDs.','',
        'The typed field adapter executes synthetic readings and rejects wrong units, out-of-range values, stale revisions and automatic acceptance. Every result awaits independent inspection. The7.5–8.5mm gap band is a provisional exercise limit, not an approved manufacturing tolerance.','',
        f'Scope: one magnetic module and selected {selection["span_m"]:g}m {selection["section_id"]} beam with counted concrete endinfills. '+('Return rails and their support stock are included. ' if include_rail_and_supports else 'Return rails and their support stock remain in the structural packet. ')+'Reinforcement/strand native detailing, station/depot, whole-city federation and physical as-built validation remain further work.','',
        '[IfcTester](https://docs.ifcopenshell.org/ifctester.html), [BCF3 specification](https://github.com/buildingSMART/BCF-XML/tree/release_3_0).',''])).encode()


def publish(output=OUTPUT,candidate=None,*,beam=None,selection=None,include_rail_and_supports=False,allow_incomplete=False):
    before=sources();output=Path(output);output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        folder=Path(temporary);value=study(folder,candidate,beam=beam,selection=selection,include_rail_and_supports=include_rail_and_supports,allow_incomplete=allow_incomplete);files={p.name+'.gz':gzip.compress(p.read_bytes(),mtime=0) for p in folder.iterdir()}
    files['study.json.gz']=gzip.compress(platform.encoded(value),mtime=0);files['README.md']=readme(value['exchange']['selected_beam'],include_rail_and_supports)
    if before!=sources():raise ValueError('BIM exchange sources changed during execution')
    for n,b in files.items():(output/n).write_bytes(b)
    manifest=dict(schema=SCHEMA,source_sha256=before,files_sha256={n:sha256(b).hexdigest() for n,b in files.items()},**platform.FLAGS);(output/'manifest.json').write_bytes(platform.encoded(manifest));return manifest


def _number(actual,expected):
    if type(actual) not in (int,float) or not math.isfinite(actual) or not math.isclose(actual,float(expected),rel_tol=1e-10,abs_tol=1e-10):raise ValueError('retained IFC source dimension/property differs')


def _vector(actual,expected):
    if len(actual)!=len(expected):raise ValueError('retained IFC vector differs')
    for x,y in zip(actual,expected):_number(x,y)


def _extrusion(solid,*,kind,size,at,axis=2):
    """Inspect the actual IFC CSG tree against source dimensions; no re-export."""
    if not solid.is_a('IfcExtrudedAreaSolid'):raise ValueError('retained IFC primitive differs')
    _vector(solid.ExtrudedDirection.DirectionRatios,[0,0,1]);_number(solid.Depth,size[2])
    normal=[0.,0.,0.];normal[axis]=1.
    ref=[0.,0.,0.];ref[(axis+1)%3]=1.
    if kind=='box':normal=[0,0,1];ref=[1,0,0]
    _vector(solid.Position.Location.Coordinates,at);_vector(solid.Position.Axis.DirectionRatios,normal);_vector(solid.Position.RefDirection.DirectionRatios,ref)
    profile=solid.SweptArea
    if profile.ProfileType!='AREA' or profile.Position is not None:raise ValueError('retained IFC profile frame differs')
    if kind=='box':
        if not profile.is_a('IfcRectangleProfileDef'):raise ValueError('retained IFC box profile differs')
        _number(profile.XDim,size[0]);_number(profile.YDim,size[1])
    else:
        if not profile.is_a('IfcCircleProfileDef'):raise ValueError('retained IFC cylinder profile differs')
        _number(profile.Radius,size[0]/2)


def _source_solid(obj,part):
    import ifcopenshell.util.placement
    if not np.allclose(ifcopenshell.util.placement.get_local_placement(obj.ObjectPlacement),np.eye(4),rtol=0,atol=1e-10):raise ValueError('retained IFC object placement differs')
    reps=obj.Representation.Representations if obj.Representation else []
    if len(reps)!=1 or reps[0].RepresentationIdentifier!='Body' or reps[0].RepresentationType!='CSG' or len(reps[0].Items)!=1:raise ValueError('retained IFC representation differs')
    solid=reps[0].Items[0];at=np.asarray(part['at_m'],float);size=part['size_m']
    for hole in reversed(part.get('holes',[])):
        if not solid.is_a('IfcBooleanResult') or solid.Operator!='DIFFERENCE':raise ValueError('retained IFC drilled void differs')
        ax='xyz'.index(hole.get('axis','z'));pos=at.copy()
        for i in range(3):pos[i]+=hole.get('start_m',0.) if i==ax else hole['xyz'[i]+'_m']
        run=hole.get('length_m',size[ax] if part['kind']=='box' else size[2])
        _extrusion(solid.SecondOperand,kind='cylinder',size=[hole['diameter_m']]*2+[run],at=pos,axis=ax);solid=solid.FirstOperand
    pos=at.copy();bounds=np.asarray(size,float).copy()
    if part['kind']=='box':pos+=np.array([size[0]/2,size[1]/2,0.]);axis=2
    else:
        axis='xyz'.index(part.get('cylinder_axis','z'));bounds[:]=size[0];bounds[axis]=size[2]
        for i in range(3):
            if i!=axis:pos[i]+=size[0]/2
    _extrusion(solid,kind=part['kind'],size=size,at=pos,axis=axis)
    return at,at+bounds


def _retained_ifc(ifc_bytes,ids_bytes,candidate,record,*,beam=None,selection=None,include_rail_and_supports=False,allow_incomplete=False):
    import ifcopenshell,ifcopenshell.api,ifcopenshell.geom,ifcopenshell.util.shape,ifcopenshell.util.element,ifcopenshell.util.unit,ifcopenshell.util.placement
    from ifctester import ids
    resolved=manufacturing.selected_beam(candidate,beam=beam,selection=selection,allow_incomplete=allow_incomplete)
    cfg=candidate['configuration_sha256'];parts=exchange_parts(candidate,beam=resolved,include_rail_and_supports=include_rail_and_supports,allow_incomplete=allow_incomplete)
    if (record.get('selected_beam')!=resolved['selection'] or
            record.get('selected_beam_sha256')!=platform.digest(dict(configuration_sha256=cfg,selection=resolved['selection'],beam=resolved['beam'])) or
            record.get('include_rail_and_supports') is not include_rail_and_supports or
            record.get('incomplete_stock_diagnostic') is not allow_incomplete):raise ValueError('retained selected beam/span or civil scope differs')
    if not ifc_bytes.lstrip().startswith(b'ISO-10303-21;') or not ifc_bytes.rstrip().endswith(b'END-ISO-10303-21;'):raise ValueError('retained IFC STEP framing invalid')
    settings=ifcopenshell.geom.settings();settings.set('mesher-linear-deflection',1e-5);settings.set('mesher-angular-deflection',.1)
    if any(record.get(k) is not True for k in ('ids_schema_valid','ids_pass','stale_revision_refused')) or record.get('ifc_schema')!='IFC4X3_ADD2' or record.get('configuration_sha256')!=cfg or any(record.get(k) is not False for k in platform.FLAGS):raise ValueError('retained IFC execution metadata differs')
    for name,value in [('mesh_linear_deflection_m',1e-5),('mesh_angular_deflection_rad',.1),('mesh_volume_relative_tolerance',.001)]:_number(record[name],value)
    if len(record['parts'])!=len(parts):raise ValueError('retained source part coverage differs')
    with tempfile.TemporaryDirectory() as temporary:
        folder=Path(temporary);actual_ifc=folder/'retained.ifc';actual_ids=folder/'retained.ids';actual_ifc.write_bytes(ifc_bytes);actual_ids.write_bytes(ids_bytes)
        try:reopened=ifcopenshell.open(str(actual_ifc))
        except Exception as exc:raise ValueError('retained IFC cannot be reopened') from exc
        if reopened.schema_identifier!='IFC4X3_ADD2' or not math.isclose(ifcopenshell.util.unit.calculate_unit_scale(reopened),1.,rel_tol=0,abs_tol=1e-12):raise ValueError('retained IFC schema/units differ')
        contexts=reopened.by_type('IfcGeometricRepresentationContext',include_subtypes=False)
        if len(contexts)!=1 or not np.allclose(ifcopenshell.util.placement.get_axis2placement(contexts[0].WorldCoordinateSystem),np.eye(4),rtol=0,atol=1e-10):raise ValueError('retained IFC source world frame differs')
        expected_ids=folder/'source.ids';_specification(cfg).to_xml(str(expected_ids))
        if _signature(_xml(ids_bytes))!=_signature(_xml(expected_ids.read_bytes())):raise ValueError('retained IDS requirements differ')
        try:restored=ids.open(str(actual_ids),validate=True);restored.validate(reopened)
        except Exception as exc:raise ValueError('retained IDS schema/application failed') from exc
        if not restored.specifications or not all(s.status for s in restored.specifications):raise ValueError('retained IFC fails actual IDS requirements')
        objects=reopened.by_type('IfcBuildingElementProxy');expected_guids=[ifcopenshell.guid.compress(uuid.UUID(identity(cfg,p['id'])).hex) for p in parts]
        if len(objects)!=len(parts) or len({o.GlobalId for o in objects})!=len(parts) or {o.GlobalId for o in objects}!=set(expected_guids):raise ValueError('retained IFC exact GUID inventory differs')
        if {o.id() for o in reopened.by_type('IfcElement')}!={o.id() for o in objects}:raise ValueError('retained IFC extra component hidden outside IDS')
        sites=reopened.by_type('IfcSite')
        if len(sites)!=1 or sites[0].Representation is not None or {o.id() for o in reopened.by_type('IfcProduct')}!={o.id() for o in [*objects,*sites]}:raise ValueError('retained IFC product/site coverage differs')
        volumes=[]
        for part,row,guid in zip(parts,record['parts'],expected_guids):
            obj=reopened.by_guid(guid);serial='SIM-'+identity(cfg,part['id'])[:8]
            expected=dict(ConfigurationSHA256=cfg,PartID=part['id'],PartRevision=cfg,Serial=serial,ManufacturingRelease='false',NetVolumeM3=float(part['volume_m3']),AccountedMassKG=float(part['mass_kg']),Scope=part['exchange_scope'])
            psets=ifcopenshell.util.element.get_psets(obj,psets_only=True)
            if obj.Name!=part['id'] or obj.Tag!=serial or set(psets)!={'OSR_ControlledIdentity'}:raise ValueError('retained IFC part/serial identity differs')
            relations=list(obj.IsDefinedBy)
            if len(relations)!=1 or not relations[0].is_a('IfcRelDefinesByProperties') or not relations[0].RelatingPropertyDefinition.is_a('IfcPropertySet'):raise ValueError('unique retained IFC property set required')
            properties=relations[0].RelatingPropertyDefinition.HasProperties
            if len(properties)!=len(expected) or {p.Name for p in properties}!=set(expected):raise ValueError('duplicate or incomplete retained IFC properties')
            for prop in properties:
                if not prop.is_a('IfcPropertySingleValue') or prop.Unit is not None or prop.NominalValue is None or prop.NominalValue.is_a()!=('IfcReal' if isinstance(expected[prop.Name],float) else 'IfcLabel'):raise ValueError('retained IFC property type/unit differs')
            props=dict(psets['OSR_ControlledIdentity']);props.pop('id',None)
            if props!=expected:raise ValueError('retained IFC controlled properties differ')
            mat=ifcopenshell.util.element.get_material(obj)
            if mat is None or not mat.is_a('IfcMaterial') or mat.Name!=part['material']:raise ValueError('retained IFC material identity differs')
            low,high=_source_solid(obj,part)
            shape=ifcopenshell.geom.create_shape(settings,obj);volume=abs(ifcopenshell.util.shape.get_volume(shape.geometry));vertices=ifcopenshell.util.shape.get_vertices(shape.geometry)
            if not len(vertices) or not np.isfinite(vertices).all() or not np.allclose(vertices.min(axis=0),low,rtol=0,atol=2e-5) or not np.allclose(vertices.max(axis=0),high,rtol=0,atol=2e-5):raise ValueError('retained IFC reopened geometric bounds differ')
            if not math.isclose(volume,part['volume_m3'],rel_tol=.001,abs_tol=1e-10):raise ValueError('retained IFC actual boolean volume differs')
            expected_row=dict(part_id=part['id'],ifc_guid=guid,simulated_serial=serial,expected_volume_m3=part['volume_m3'],accounted_mass_kg=part['mass_kg'],scope=part['exchange_scope'])
            if set(row)!=set(expected_row)|{'reopened_volume_m3','volume_relative_error'} or {k:row.get(k) for k in expected_row}!=expected_row:raise ValueError('retained IFC row/source identity differs')
            _number(row['reopened_volume_m3'],volume);_number(row['volume_relative_error'],abs(volume-part['volume_m3'])/part['volume_m3']);volumes.append(volume)
        _number(record['total_native_volume_m3'],math.fsum(volumes))
        # The SAME retained IFC and IDS must reject a deliberately stale identity.
        first=reopened.by_guid(expected_guids[0]);pset=next(r.RelatingPropertyDefinition for r in first.IsDefinedBy if r.is_a('IfcRelDefinesByProperties') and r.RelatingPropertyDefinition.Name=='OSR_ControlledIdentity')
        ifcopenshell.api.run('pset.edit_pset',reopened,pset=pset,properties={'ConfigurationSHA256':'f'*64});restored.validate(reopened)
        if all(s.status for s in restored.specifications):raise ValueError('retained IDS stale-revision control escaped')
    return record['parts']


def _retained_bcf(data,configuration,parts,record):
    from xmlschema import XMLSchema
    topic=identity(configuration,'field-tolerance-hold');view=identity(configuration,'field-view')
    schemas={'bcf.version':'version.xsd','extensions.xml':'extensions.xsd',topic+'/markup.bcf':'markup.xsd',topic+'/candidate.bcfv':'visinfo.xsd'}
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            entries=archive.infolist()
            if len(entries)!=4 or {i.filename for i in entries}!=set(schemas) or sum(i.file_size for i in entries)>8*1024*1024:raise ValueError('retained BCF exact zip inventory differs')
            members={}
            for item in entries:
                if item.flag_bits&1 or item.is_dir() or stat.S_IFMT(item.external_attr>>16)==stat.S_IFLNK or not 0<item.file_size<=2*1024*1024:raise ValueError('bounded ordinary BCF XML member required')
                with archive.open(item) as stream:raw=stream.read(2*1024*1024+1)
                if len(raw)!=item.file_size:raise ValueError('retained BCF size differs')
                members[item.filename]=_xml(raw)
                try:XMLSchema(str(XSD/schemas[item.filename]),allow='local',defuse='always').validate(raw)
                except Exception as exc:raise ValueError('retained BCF XSD validation failed') from exc
    except (zipfile.BadZipFile,RuntimeError) as exc:raise ValueError('invalid retained BCF archive') from exc
    if members['bcf.version'].get('VersionId')!='3.0':raise ValueError('retained BCF version differs')
    markup=members[topic+'/markup.bcf'];t=markup.find('Topic');vp=t.find('Viewpoints/ViewPoint') if t is not None else None
    if t is None or t.get('Guid')!=topic or t.get('TopicType')!='Engineering hold' or t.get('TopicStatus')!='Open' or configuration not in (t.findtext('Description') or '') or vp is None or vp.get('Guid')!=view or vp.findtext('Viewpoint')!='candidate.bcfv':raise ValueError('retained BCF issue/configuration/viewpoint differs')
    visual=members[topic+'/candidate.bcfv'];guids=[e.get('IfcGuid') for e in visual.findall('./Components/Selection/Component')];expected=[p['ifc_guid'] for p in parts[:3]]
    if visual.get('Guid')!=view or guids!=expected or len(set(guids))!=len(expected) or not set(guids)<={p['ifc_guid'] for p in parts}:raise ValueError('retained BCF IFC GUID linkage differs')
    result=dict(version='3.0',schema_validated_members=list(schemas),selected_ifc_guids=guids,issue_state='Open',independent_acceptance=False)
    if result!=record:raise ValueError('retained BCF reported evidence differs')


def verify(output=OUTPUT,candidate=None,*,beam=None,selection=None,include_rail_and_supports=False,allow_incomplete=False):
    output=Path(output);before=sources();m=json.loads(_ordinary(output/'manifest.json',1024*1024))
    if m.get('schema')!=SCHEMA or m.get('source_sha256')!=before or any(m.get(k) is not False for k in platform.FLAGS):raise ValueError('BIM field inputs/release stale')
    if set(m['files_sha256'])!=FILES or {p.name for p in output.iterdir()}!=FILES|{'manifest.json'}:raise ValueError('BIM exchange inventory differs')
    files={n:_ordinary(output/n,LIMITS.get(n,1024*1024)) for n in FILES}
    if any(sha256(files[n]).hexdigest()!=h for n,h in m['files_sha256'].items()):raise ValueError('BIM exchange bytes altered')
    candidate=candidate_magnetics.definition() if candidate is None else candidate
    resolved=manufacturing.selected_beam(candidate,beam=beam,selection=selection,allow_incomplete=allow_incomplete)
    if files['README.md']!=readme(resolved['selection'],include_rail_and_supports):raise ValueError('BIM evidence description differs')
    raw={n:_inflate(data,LIMITS[n]) for n,data in files.items() if n in LIMITS};value=json.loads(raw['study.json.gz']);cfg=candidate['configuration_sha256']
    if value.get('schema')!=SCHEMA or value['configuration_sha256']!=cfg or any(value.get(k) is not False for k in platform.FLAGS):raise ValueError('BIM candidate/release differs')
    parts=_retained_ifc(raw['candidate.ifc.gz'],raw['candidate.ids.gz'],candidate,value['exchange'],beam=resolved,include_rail_and_supports=include_rail_and_supports,allow_incomplete=allow_incomplete);_retained_bcf(raw['candidate-issues.bcf.gz'],cfg,parts,value['bcf'])
    part=parts[0];work=field_plan(cfg,part)
    if value['work']!=work or value['field_result']!=assess_field(work,value['event'],configuration_sha256=cfg,part=part):raise ValueError('retained typed field/work/evidence differs')
    from copy import deepcopy
    controls=[]
    for name,mutate in [('wrong-unit',lambda e:e['readings']['gap'].update(unit='m')),('outside-tolerance',lambda e:e['readings']['gap'].update(value=8.6)),('stale-revision',lambda e:e['readings'].update({'part-revision':'f'*64})),('automatic-handback',lambda e:e.update(status='accepted'))]:
        bad=deepcopy(value['event']);mutate(bad)
        try:assess_field(work,bad,configuration_sha256=cfg,part=part)
        except ValueError:controls.append(dict(id=name,refused=True))
        else:raise ValueError('retained typed field negative escaped: '+name)
    if value['negative_controls']!=controls or value['study_pass'] is not True or before!=sources():raise ValueError('retained field controls/source/evidence differ')
    return dict(verified=True,study_pass=value['study_pass'],parts=len(value['exchange']['parts']),**platform.FLAGS)
