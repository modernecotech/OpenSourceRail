"""Known-stock wheel-rail research twin; no complete assembly or release implied."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json, subprocess, time
from . import contracts as k
ROOT=Path(__file__).resolve().parents[2]
FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
           complete_installed_twin=False,manufacturing_release=False,operating_release=False,
           complete_cost_known=False)
PRODUCER='engineering/design_search/wheel_twin.py'
SUPPORTED={'box','box-with-rectangular-cutouts','cylinder','annular-cylinder'}


def _materialize(candidate):
    from .wheel_families import materialize
    return materialize(candidate)


def _project(part):
    from .wheel_families import native_part
    return native_part(part)


def _sources(candidate):
    names={PRODUCER,'engineering/design_search/contracts.py','engineering/design_search/wheel_families.py'}
    return {name:sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(names) if (ROOT/name).is_file()}


def _parts(candidate, materialized):
    if materialized.get('candidate_id')!=candidate['candidate_id']:
        raise ValueError('Materialized wheel candidate identity differs')
    parts=[dict(deepcopy(p),twin_frame='vehicle') for p in materialized['geometry_parts']]
    parts += [dict(deepcopy(p),twin_frame='station') for p in materialized.get('wayside_parts',[])]
    parts += [dict(deepcopy(p),twin_frame='guidebeam') for p in materialized.get('civil_parts',[])]
    if len({p['id'] for p in parts})!=len(parts):raise ValueError('Unique wheel occurrence IDs required')
    expected={g['native_part']['id']:g['native_part'] for g in candidate['geometry'] if g.get('native_part') is not None}
    if set(expected)!={p['id'] for p in parts}:raise ValueError('Candidate and materialized native stock inventory differ')
    exported=[]
    for p in parts:
        q=deepcopy(p);frame=q.pop('twin_frame')
        if _project(q)!=expected[p['id']]:raise ValueError('Materialized native stock differs from physical candidate')
        p=dict(deepcopy(expected[p['id']]),twin_frame=frame);exported.append(p)
        if p['kind'] not in SUPPORTED:raise ValueError('Unsupported native primitive; no placeholder allowed: '+p['kind'])
        for field in ('volume_m3','mass_kg'):k.finite(p[field],field,True)
    return exported


SCRIPT=r'''
import FreeCAD as A,Part,Import,json,pathlib
out=pathlib.Path(__file__).parent;data=json.loads((out/'native-input.json').read_text());doc=A.newDocument('OSR_wheel_research');objects=[];rows=[]
for i,p in enumerate(data['parts']):
    at=A.Vector(*[x*1000 for x in p['at_m']])
    if p['kind'] in ('box','box-with-rectangular-cutouts'):
        shape=Part.makeBox(*[x*1000 for x in p['size_m']],at)
        for hole in p.get('holes',[]):
            index='xyz'.index(hole.get('axis','z'));start=list(p['at_m']);direction=[0.,0.,0.];direction[index]=1.
            for j,key in enumerate(('x_m','y_m','z_m')):
                if j!=index:start[j]+=hole.get(key,0.)
            shape=shape.cut(Part.makeCylinder(hole['diameter_m']*500,hole.get('length_m',p['size_m'][index])*1000,A.Vector(*[x*1000 for x in start]),A.Vector(*direction)))
        for cut in p.get('rectangular_cutouts',[]):
            shape=shape.cut(Part.makeBox(*[x*1000 for x in cut['size_m']],A.Vector(*[x*1000 for x in cut['at_m']])))
    elif p['kind'] in ('cylinder','annular-cylinder'):
        axis=A.Vector(*p['axis']);shape=Part.makeCylinder(p['radius_m']*1000,p['length_m']*1000,at,axis)
        if p.get('inner_radius_m',0):shape=shape.cut(Part.makeCylinder(p['inner_radius_m']*1000,p['length_m']*1000,at,axis))
    else:raise ValueError('Unsupported stock primitive')
    volume=shape.Volume/1e9
    if not shape.isValid() or abs(volume-p['volume_m3'])>max(1e-10,1e-6*p['volume_m3']):raise ValueError('Native stock volume differs: '+p['id'])
    obj=doc.addObject('PartDesign::Feature','Occurrence_'+str(i));obj.Label=p['id'];obj.Shape=shape
    for key,value in [('CandidateID',data['candidate_id']),('OccurrenceID',p['id']),('Frame',p['twin_frame'])]:
        obj.addProperty('App::PropertyString',key);setattr(obj,key,value)
    objects.append(obj);vertices,triangles=shape.tessellate(.15)
    rows.append(dict(id=p['id'],vertices_m=[[v.x/1000,v.y/1000,v.z/1000] for v in vertices],triangles=[list(t) for t in triangles],native_volume_m3=volume))
doc.recompute();doc.saveAs(str(out/'wheel-stock.FCStd'));Import.export(objects,str(out/'wheel-stock.step'));A.closeDocument(doc.Name)
doc=A.openDocument(str(out/'wheel-stock.FCStd'));reopened=sum(o.Shape.Volume for o in doc.Objects if hasattr(o,'Shape'))/1e9
if len([o for o in doc.Objects if hasattr(o,'Shape')])!=len(rows):raise ValueError('Reopened occurrence count differs')
A.closeDocument(doc.Name);step=Part.Shape();step.read(str(out/'wheel-stock.step'));total=sum(r['native_volume_m3'] for r in rows)
if max(abs(reopened-total),abs(step.Volume/1e9-total))>max(1e-8,1e-7*total):raise ValueError('Reopened CAD/STEP volume differs')
(out/'native-result.json').write_text(json.dumps(dict(candidate_id=data['candidate_id'],part_count=len(rows),rows=rows,native_volume_m3=total,reopened_volume_m3=reopened,step_volume_m3=step.Volume/1e9,FreeCAD_version=list(A.Version())),sort_keys=True)+'\n')
'''


def _ifc(output,candidate,parts,native):
    started=time.monotonic()
    import ifcopenshell,ifcopenshell.api,ifcopenshell.geom
    from ifcopenshell.util.element import get_pset
    from ifcopenshell.util.shape import get_volume
    api=ifcopenshell.api.run;f=api('project.create_file',version='IFC4')
    project=api('root.create_entity',f,ifc_class='IfcProject',name='OpenSourceRail known wheel-rail stock')
    unit=api('unit.add_si_unit',f,unit_type='LENGTHUNIT');api('unit.assign_unit',f,units=[unit])
    context=api('context.add_context',f,context_type='Model');body=api('context.add_context',f,context_type='Model',context_identifier='Body',target_view='MODEL_VIEW',parent=context)
    site=api('root.create_entity',f,ifc_class='IfcSite',name='Vehicle and separate station coordinate frames')
    api('aggregate.assign_object',f,products=[site],relating_object=project)
    meshes={r['id']:r for r in native['rows']}
    for p in parts:
        if time.monotonic()-started>60:raise TimeoutError('Bounded60s IFC export/verification budget exhausted')
        obj=api('root.create_entity',f,ifc_class='IfcBuildingElementProxy',name=p['id'])
        api('spatial.assign_container',f,products=[obj],relating_structure=site)
        row=meshes[p['id']]
        rep=api('geometry.add_mesh_representation',f,context=body,vertices=[row['vertices_m']],faces=[row['triangles']],unit_scale=1.)
        api('geometry.assign_representation',f,product=obj,representation=rep)
        ps=api('pset.add_pset',f,product=obj,name='OSR_Research_Identity')
        api('pset.edit_pset',f,pset=ps,properties=dict(candidate_id=candidate['candidate_id'],occurrence_id=p['id'],frame=p['twin_frame'],physical_accepted=False,complete_installed_twin=False))
    for entity in f.by_type('IfcRoot'):
        entity.GlobalId=ifcopenshell.guid.compress(sha256((candidate['candidate_id']+entity.is_a()+str(entity.id())).encode()).hexdigest()[:32])
    f.header.file_name.name='wheel-stock.ifc';f.header.file_name.time_stamp='2026-10-26T00:00:00';path=output/'wheel-stock.ifc';f.write(str(path));reopened=ifcopenshell.open(str(path));errors=[]
    actual=reopened.by_type('IfcBuildingElementProxy')
    if len(actual)!=len(parts):raise ValueError('IFC occurrence inventory differs')
    for obj in actual:
        if time.monotonic()-started>60:raise TimeoutError('Bounded60s IFC export/verification budget exhausted')
        ps=get_pset(obj,'OSR_Research_Identity');row=meshes[obj.Name]
        if ps.get('candidate_id')!=candidate['candidate_id'] or ps.get('physical_accepted') is not False:raise ValueError('IFC candidate identity differs')
        shape=ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(),obj)
        volume=abs(get_volume(shape.geometry))
        error=abs(volume-row['native_volume_m3'])/row['native_volume_m3'];errors.append(error)
        if error>.005:raise ValueError('IFC tessellation volume differs beyond declared0.5% tolerance: '+obj.Name)
    return dict(execution='completed',native_reopened=True,part_count=len(actual),ifcopenshell_version=ifcopenshell.version,
        maximum_relative_volume_error=max(errors,default=0.),representation='Faceted native BRep tessellation; curved surfaces approximated at0.15mm chord setting',**FLAGS)


def _drafts(candidate,parts,identity):
    groups={}
    for p in parts:
        key=(p['twin_frame'],p.get('system','known-stock'))
        groups.setdefault(key,[]).append(p['id'])
    grouping=[dict(frame=frame,system=system,occurrence_ids=ids) for (frame,system),ids in sorted(groups.items())]
    def ids(predicate):return [p['id'] for p in parts if predicate(p)]
    steps=[('stock','Check and prepare enumerated stock against native dimensions and cutout definitions',[],ids(lambda p:True)),
      ('frame','Fixture and join chassis, posts and body members; hold until joining procedures and joint limits are approved',['stock'],ids(lambda p:any(t in p['id'] for t in ('frame','sill','bolster','post-connection')))),
      ('panels','Fit floor, roof, glazing, doors and interior stock; qualify attachments and seals',['frame'],ids(lambda p:any(t in p['id'] for t in ('comfort-shell','floor-fit','collar')))),
      ('running-gear','Mount and align bogies, brakes and passive secondary; qualify load paths and removal access',['frame'],ids(lambda p:p['id'].startswith(('bogie/','station-secondary/','secondary-')))),
      ('wayside','Prepare guidebeam and station module interfaces; qualify rail and stator fastening/alignment',['stock'],ids(lambda p:p['twin_frame'] in ('station','guidebeam'))),
      ('services','Install services only after unknown equipment, mounts, wiring and protection are designed',['panels','running-gear'],ids(lambda p:p.get('system') in ('services','electrical','hvac','battery'))),
      ('qa','Execute approved continuity, insulation, pressure, brake and clearance checks; tests are not yet specified or executed',['services','wayside'],ids(lambda p:True)),
      ('weigh','Measure complete mass, CG and inertia after all equipment and hardware is installed',['qa'],ids(lambda p:True))]
    operations=[dict(operation_id=name,operation=text,prerequisite_operation_ids=prior,affected_occurrence_ids=affected,
       performed=False,procedure_approved=False,estimated_labour_hours=None,approved_tools=None,installation_tolerances=None) for name,text,prior,affected in steps]
    quantities={}
    for p in parts:
        key=(p['twin_frame'],p.get('material','unspecified material'))
        row=quantities.setdefault(key,dict(frame=key[0],material=key[1],occurrence_ids=[],mass_kg=0.,volume_m3=0.))
        row['occurrence_ids'].append(p['id']);row['mass_kg']+=p['mass_kg'];row['volume_m3']+=p['volume_m3']
    procurement=[dict(row,quantity_basis='Known geometric occurrences only; yield and complete installed quantities unknown',unit_price=None,
        estimated_total_cost=None,supplier=None,origin_evidence=None,lead_time_days=None) for row in quantities.values()]
    quality=[dict(occurrence_id=p['id'],nominal_geometry_reference='engineering-bom.json',native_volume_m3=p['volume_m3'],
        material=p.get('material'),inspection_method=None,tolerance_limits=None,measurement=None,accepted=False) for p in parts]
    maintenance=[dict(frame=g['frame'],system=g['system'],occurrence_ids=g['occurrence_ids'],operation='Inspect, isolate and replace by an approved system-specific procedure',
        procedure_approved=False,interval=None,replacement_life=None,tools=None,labour_hours=None,performed=False) for g in grouping]
    base=dict(**identity,status='draft-research-plan',unknown_inventory_ids=[r['id'] for r in candidate['installed_inventory'] if r['status']=='unknown'],**FLAGS)
    return dict(assembly=dict(base,groups=grouping,operations=operations),qa=dict(base,inspections=quality,
        final_tests=['Dimensional and material inspection','Qualified joint tests','Electrical continuity and insulation','Brake pressure and response','Swept clearance','Final weighing and mass properties'],test_procedures_approved=False),
        procurement=dict(base,material_quantities=procurement,estimated_total_cost=None,unknown_stock_priced=False),
        maintenance=dict(base,system_plans=maintenance,scope='Draft known-stock systems; actual wear, service limits and qualification remain unknown'))


def compile(candidate,results,*,output,export_native=True,allow_incomplete=True):
    k.validate_candidate(candidate)
    if candidate['architecture'].get('family')!='wheel_rail_station_lim':raise ValueError('Wheel-rail station LIM candidate required')
    if type(export_native) is not bool or type(allow_incomplete) is not bool:raise ValueError('Explicit research export choices required')
    for r in results:
        k.validate_result(r)
        if r['candidate_id']!=candidate['candidate_id'] or r['requirement_revision']!=candidate['requirement_revision']:raise ValueError('Mixed candidate evaluation cannot enter wheel twin')
    if len({r['evaluation_id'] for r in results})!=len(results):raise ValueError('Unique wheel evaluations required')
    inventory=k.inventory_summary(candidate)
    if not allow_incomplete and not inventory['complete_installed_distribution']:raise k.UnknownInstalledStock('Complete installed distribution unavailable')
    materialized=_materialize(candidate);parts=_parts(candidate,materialized);output=Path(output)
    if output.is_symlink() or any(p.is_symlink() for p in output.parents):raise ValueError('Ordinary owned output path required')
    output=output.resolve()
    if output.exists():raise ValueError('Fresh wheel twin output required')
    output.mkdir(parents=True);sources=_sources(candidate)
    def write(name,data):(output/name).write_bytes(k.encoded(data))
    write('candidate.json',candidate);write('evaluations.json',results)
    unknown=[r['id'] for r in candidate['installed_inventory'] if r['status']=='unknown']
    unlocated=[r['id'] for r in candidate['installed_inventory'] if r['status']=='known' and r.get('cg_m') is None]
    identity=dict(candidate_id=candidate['candidate_id'],requirement_revision=candidate['requirement_revision'],
        component_ids={key:materialized[key] for key in ('body_candidate_id','support_component_id','propulsion_component_id') if key in materialized})
    write('engineering-bom.json',dict(**identity,known_geometric_occurrences=parts,installed_inventory=candidate['installed_inventory'],unknown_stock_ids=unknown,unlocated_stock_ids=unlocated,**FLAGS))
    write('manufacturing-bom.json',dict(**identity,material_takeoff=[dict(occurrence_id=p['id'],material=p.get('material'),mass_kg=p['mass_kg'],volume_m3=p['volume_m3'],frame=p['twin_frame'],geometry_id=p['id'],primitive=p['kind']) for p in parts],
        scope='Counted material only; stock yield, tooling, labour, joints and complete installed prices unknown',**FLAGS))
    for name,data in _drafts(candidate,parts,identity).items():write(name+'.json',data)
    write('native-input.json',dict(**identity,parts=parts,frames_separate=True,scope='Known occurrence stock in parent coordinate frames; no assembly clearance claim',**FLAGS))
    native_status=dict(execution='not-run',reason='Native export explicitly disabled',**FLAGS);ifc_status=dict(execution='not-run',reason='No native tessellation was generated',**FLAGS)
    if export_native:
        (output/'worker.py').write_text(SCRIPT)
        proc=subprocess.run(['flatpak','run','--filesystem='+str(output),'--command=FreeCADCmd','org.freecad.FreeCAD',str(output/'worker.py')],cwd=output,capture_output=True,text=True,timeout=180)
        (output/'stdout.log').write_text(proc.stdout);(output/'stderr.log').write_text(proc.stderr)
        if proc.returncode or not (output/'native-result.json').is_file():raise RuntimeError('Native wheel twin failed; logs retained')
        raw=json.loads((output/'native-result.json').read_bytes())
        if raw['candidate_id']!=candidate['candidate_id'] or raw['part_count']!=len(parts):raise ValueError('Native wheel twin candidate differs')
        native_status={key:value for key,value in raw.items() if key!='rows'};native_status.update(execution='completed',native_reopened=True,**FLAGS)
        ifc_status=_ifc(output,candidate,parts,raw)
    summary=dict(schema='osr-wheel-research-twin/1',**identity,known_geometric_occurrences=len(parts),omitted_unknown_inventory_ids=unknown,
        omitted_unlocated_inventory_ids=unlocated,inventory=inventory,native=native_status,IFC=ifc_status,evaluation_ids=[r['evaluation_id'] for r in results],
        frames=dict(vehicle='Car reference',station='Separate wayside module reference; not an installed co-located assembly',guidebeam='Separate selected concrete/rail span reference'),
        vehicle_scope='One car known stock plus separate station module and selected guidebeam span',scope='Known-stock research twin only; complete installed mass/CG/inertia, priced costs, manufacturing and physical acceptance remain open',**FLAGS)
    write('twin.json',summary)
    links='[Native FreeCAD](wheel-stock.FCStd) · [STEP](wheel-stock.step) · [IFC](wheel-stock.ifc)' if export_native else 'Native CAD and IFC were not executed.'
    (output/'README.md').write_text('# Wheel-rail known-stock research twin\n\nOpenSourceRail pursues simple, locally repairable station-powered transport. This package connects one wheel-rail candidate to known-stock geometry and draft delivery records.\n\nCandidate `'+candidate['candidate_id']+'`; requirements `'+candidate['requirement_revision']+'`. '+str(len(parts))+' known geometric occurrences, representing one car, a separate station module and selected guidebeam stock. Vehicle and station coordinates are separate frames, not an installed assembly clearance demonstration.\n\n'+links+'\n\n[Engineering BOM](engineering-bom.json) · [Manufacturing takeoff](manufacturing-bom.json) · [Assembly](assembly.json) · [QA](qa.json) · [Procurement](procurement.json) · [Maintenance](maintenance.json) · [Evidence summary](twin.json)\n\nUnknown and unlocated equipment is listed without placeholder solids. Complete installed mass, CG, inertia, cost, joining procedures and physical qualification remain open. All production and operating releases remain held.\n')
    if _sources(candidate)!=sources:raise ValueError('Wheel twin sources changed during generation')
    manifest=dict(schema='osr-wheel-research-twin-manifest/1',**identity,source_sha256=sources,
        files_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in output.iterdir() if p.is_file()},**FLAGS)
    manifest['manifest_id']=k.identity(manifest);write('manifest.json',manifest);return verify(output)


def verify(output):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes());c=json.loads((output/'candidate.json').read_bytes());k.validate_candidate(c)
    if m['manifest_id']!=k.identity({key:v for key,v in m.items() if key!='manifest_id'}):raise ValueError('Wheel twin manifest differs')
    if m['candidate_id']!=c['candidate_id'] or m['source_sha256']!=_sources(c):raise ValueError('Wheel twin source/candidate differs')
    if {p.name:sha256(p.read_bytes()).hexdigest() for p in output.iterdir() if p.is_file() and p.name!='manifest.json'}!=m['files_sha256']:raise ValueError('Wheel twin payload differs')
    for name in ('twin','engineering-bom','manufacturing-bom','assembly','qa','procurement','maintenance','native-input'):
        row=json.loads((output/(name+'.json')).read_bytes())
        if row['candidate_id']!=c['candidate_id'] or any(row.get(key) is not val for key,val in FLAGS.items()):raise ValueError('Wheel twin identity/disposition differs')
    return dict(verified=True,candidate_id=c['candidate_id'],manifest_id=m['manifest_id'],summary=json.loads((output/'twin.json').read_bytes()),**FLAGS)
