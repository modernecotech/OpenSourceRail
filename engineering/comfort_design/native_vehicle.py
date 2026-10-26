"""Bounded native FreeCAD material proposal and independent reopen receipt.

Supplier equipment references and unlocated allocations are drawn as labelled
contexts, not solids assigned invented density. CAD checks geometry accounting;
they do not establish complete installed mass or an interference-free railway.
"""
from hashlib import sha256
import gzip
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

from . import ROOT, FLAGS

SCHEMA='osr-comfort-native-vehicle/1'
MAX_BYTES=50*1024*1024


def encoded(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()


def _inventory(folder):
    return {p.relative_to(folder).as_posix():digest(p) for p in sorted(Path(folder).rglob('*'))
            if p.is_file() and p.name!='manifest.json'}


def _group(part):
    name=part['id']
    if name.startswith('module/'):family='/'.join(name.split('/')[:2])
    elif name.startswith('retained/'):family='/'.join(name.split('/')[:2])
    elif name.startswith('replacement-frame/'):family='replacement-frame'
    else:family=name.split('/')[0]
    return family+'|rho='+format(part['density_kg_m3'],'.12g')


def _aggregate(parts):
    mass=math.fsum(p['mass_kg'] for p in parts)
    cg=[math.fsum(p['mass_kg']*p['cg_m'][j] for p in parts)/mass for j in range(3)]
    tensor=[[0.]*3 for _ in range(3)]
    for p in parts:
        delta=[p['cg_m'][j]-cg[j] for j in range(3)];rr=math.fsum(x*x for x in delta)
        for i in range(3):
            for j in range(3):tensor[i][j]+=p['inertia_kg_m2'][i][j]+p['mass_kg']*((rr if i==j else 0)-delta[i]*delta[j])
    return dict(mass_kg=mass,cg_m=cg,inertia_kg_m2=tensor,
                volume_m3=math.fsum(p['volume_m3'] for p in parts),part_count=len(parts))


def render_svg(vehicle):
    from html import escape
    scale=65.;left=55.;top=105.;floor=525.
    lines=['<svg xmlns="http://www.w3.org/2000/svg" width="1220" height="660" viewBox="0 0 1220 660">',
           '<rect width="1220" height="660" fill="#f5f7f9"/><g font-family="sans-serif" fill="#18354a">',
           '<text x="35" y="32" font-size="24">Matched comfort-car proposal:44 seats +2 wheelchair users</text>',
           '<text x="35" y="60" font-size="15">Defined material + labelled equipment envelopes. Complete mass, joints, fit and operation remain unqualified.</text>']
    def rect(x,y,w,h,colour):return f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="{colour}" stroke="#355267" stroke-width=".6"/>'
    lines += [rect(left,top,17*scale,2.65*scale,'#edf3f6')]
    for unit in vehicle['physical_definition']['body']['seat_units']:
        x0,y0,x1,y1=unit['bounds_xy_m'];colour='#2a9d8f' if unit['kind']=='wall' else '#558dcc'
        lines.append(rect(left+(x0+8.5)*scale,top+(1.325-y1)*scale,(x1-x0)*scale,(y1-y0)*scale,colour))
    for bay in ((-7.5,-1.2347,-6.2,-.4347),(6.2,-1.2347,7.5,-.4347)):
        x0,y0,x1,y1=bay;lines.append(rect(left+(x0+8.5)*scale,top+(1.325-y1)*scale,(x1-x0)*scale,(y1-y0)*scale,'#9974b6'))
    for x in (-4.5,4.5):lines.append(rect(left+(x+8.5-.7)*scale,top-4,1.4*scale,5,'#e76f51'))
    lines.append('<text x="55" y="310" font-size="15">Plan:20 two-place units +4 singles clear retained posts. Door benches are green; wheelchair bays purple.</text>')
    roof=vehicle['interfaces']['roof_top_z_m']
    lines.append(rect(left,floor-roof*scale,17*scale,roof*scale,'#edf3f6'))
    for x in (-6.5,-1.5,1.5,6.5):lines.append(rect(left+(x+8.5-1)*scale,floor-2.4*scale,2*scale,1.5*scale,'#bfd9eb'))
    for x in (-4.5,4.5):lines.append(rect(left+(x+8.5-.7)*scale,floor-2.1*scale,1.4*scale,2.1*scale,'#d6cbb7'))
    for p in vehicle['interfaces']['HVAC_packages']:
        cx,cy,cz=p['centre_m'];sx,sy,sz=p['size_m']
        lines.append(rect(left+(cx+8.5-sx/2)*scale,floor-(cz+sz/2)*scale,sx*scale,sz*scale,'#c6cdd3'))
    for p in vehicle['interfaces']['magnetic_mounts'][::1]:
        if p['translation_m'][1]>0:continue
        x,y,z=p['translation_m'];lines.append(rect(left+(x+8.5-.5)*scale,floor-(z-.012)*scale,scale,.07*scale,'#c97853'))
    lines += [f'<text x="55" y="620" font-size="14">Roof outer top{roof:.4f}m above floor;24 proposed PM modules below floor;5HVAC boxes are supplier envelopes, not material solids.</text>',
              f'<text x="55" y="645" font-size="11">Candidate {escape(vehicle["candidate_id"])}</text></g></svg>']
    return '\n'.join(lines)+'\n'


def _shape(part,App,Part,cache):
    shape_kind=part.get('kind',part.get('primitive','box'))
    holes=part.get('holes',[])
    spec=dict(kind=shape_kind,size_m=part['size_m'],holes=holes,
              cylinder_axis=part.get('cylinder_axis','z'),axis=part.get('axis'),wall_m=part.get('wall_m'))
    key=encoded(spec)
    if key not in cache:
        size=[x*1000 for x in part['size_m']]
        if shape_kind=='cylinder':
            axis='xyz'.index(spec['cylinder_axis']);origin=[0.,0.,0.]
            for j in range(3):
                if j!=axis:origin[j]=size[0]/2
            direction=[0.,0.,0.];direction[axis]=1.
            shape=Part.makeCylinder(size[0]/2,size[2],App.Vector(*origin),App.Vector(*direction))
        else:
            shape=Part.makeBox(*size)
            if shape_kind=='tube':
                inner=list(size);at=[0.,0.,0.];axis=part['axis'];wall=part['wall_m']*1000
                for j in range(3):
                    if j!=axis:inner[j]-=2*wall;at[j]+=wall
                shape=shape.cut(Part.makeBox(*inner,App.Vector(*at)))
        for h in holes:
            axis='xyz'.index(h.get('axis','z'));at=[0.,0.,0.];direction=[0.,0.,0.];direction[axis]=1.
            for j in range(3):at[j]=(h.get('start_m',0) if j==axis else h['xyz'[j]+'_m'])*1000
            length=h.get('length_m',part['size_m'][axis] if shape_kind!='cylinder' else part['size_m'][2])*1000
            shape=shape.cut(Part.makeCylinder(h['diameter_m']*500,length,App.Vector(*at),App.Vector(*direction)))
        cache[key]=shape
    result=cache[key].copy()
    result.translate(App.Vector(*(x*1000 for x in part['at_m'])))
    return result


def _native_properties(shape,rho):
    cg=[v/1000 for v in tuple(shape.CenterOfMass)];matrix=shape.MatrixOfInertia
    return dict(volume_m3=shape.Volume/1e9,mass_kg=shape.Volume/1e9*rho,cg_m=cg,
        inertia_kg_m2=[[getattr(matrix,'A'+str(i+1)+str(j+1))/1e15*rho for j in range(3)] for i in range(3)])


def _worker(output):
    import FreeCAD as App
    import Part
    from engineering.factory_examples.native import _canonicalise_fcstd
    output=Path(output);request=json.loads((output/'request.json').read_bytes())
    raw=gzip.decompress((output/'geometry.json.gz').read_bytes())
    if sha256(raw).hexdigest()!=request['geometry_sha256']:raise ValueError('native geometry request hash differs')
    geometry=json.loads(raw);parts=geometry['parts'];groups={}
    for p in parts:groups.setdefault(_group(p),[]).append(p)
    doc=App.newDocument('ComfortVehicleResearch');objects=[];checks=[];cache={}
    control=Part.makeBox(1000,1000,1000,App.Vector(3000,4000,5000))
    if not math.isclose(control.MatrixOfInertia.A11/1e15,1/6,rel_tol=1e-9):raise ValueError('native inertia convention control differs')
    for i,(key,regions) in enumerate(sorted(groups.items())):
        shape=Part.makeCompound([_shape(p,App,Part,cache) for p in regions])
        expected=_aggregate(regions);rho=regions[0]['density_kg_m3']
        obj=doc.addObject('PartDesign::Feature','Material'+str(i));obj.Label=key;obj.Shape=shape
        for name,value in (('CandidateId',request['candidate_id']),('BodyCandidateId',request['body_candidate_id']),('DesignGroup',key)):
            obj.addProperty('App::PropertyString',name);setattr(obj,name,value)
        obj.addProperty('App::PropertyFloat','AssumedDensity');obj.AssumedDensity=rho
        objects.append(obj)
        checks.append(dict(group=key,object_name=obj.Name,expected=expected,density_kg_m3=rho))
    for i,context in enumerate(geometry.get('contexts',[])):
        obj=doc.addObject('PartDesign::Feature','EquipmentEnvelope'+str(i));obj.Label='[ENVELOPE ONLY] '+context['id']
        size=context['size_m'];centre=context['centre_m']
        obj.Shape=Part.makeBox(*(x*1000 for x in size),App.Vector(*((centre[j]-size[j]/2)*1000 for j in range(3))))
        obj.addProperty('App::PropertyBool','MaterialGeometry');obj.MaterialGeometry=False
        obj.addProperty('App::PropertyString','CandidateId');obj.CandidateId=request['candidate_id']
    # The integration-critical roof/stringer check uses actual native solids,
    # including the new perimeter bearing. Full-body contact remains separate.
    roof_parts=[p for p in parts if p['id'].startswith('roof/')]
    stringer_parts=[p for p in parts if 'replacement-frame/extrusion/frame/roof-longitudinal' in p['id']]
    if not roof_parts or len(stringer_parts)!=8:raise ValueError('critical roof/longitudinal material identities missing')
    roof_shape=Part.makeCompound([_shape(p,App,Part,cache) for p in roof_parts])
    rail_shape=Part.makeCompound([_shape(p,App,Part,cache) for p in stringer_parts])
    roof_common=roof_shape.common(rail_shape).Volume/1e9
    if roof_common>1e-12:raise ValueError('revised roof still intersects retained primary roof longitudinals')
    critical_fit=dict(actual_native_boolean_executed=True,roof_part_ids=[p['id'] for p in roof_parts],
        longitudinal_part_ids=[p['id'] for p in stringer_parts],positive_common_volume_m3=roof_common,
        nominal_clearance_screen='pass',manufacturing_tolerance_or_dynamic_clearance_qualified=False)
    doc.recompute();doc.saveAs(str(output/'model.FCStd'));App.closeDocument(doc.Name)
    _canonicalise_fcstd(output/'model.FCStd')
    reopened=App.openDocument(str(output/'model.FCStd'))
    for item in checks:
        obj=reopened.getObject(item['object_name']);shape=obj.Shape
        if obj.CandidateId!=request['candidate_id'] or obj.BodyCandidateId!=request['body_candidate_id']:raise ValueError('native object belongs to another design')
        if not shape.isValid() or not shape.Solids:raise ValueError('invalid reopened native material group '+item['group'])
        actual=_native_properties(shape,item['density_kg_m3']);expected=item['expected']
        if not math.isclose(actual['mass_kg'],expected['mass_kg'],rel_tol=1e-7,abs_tol=1e-7):raise ValueError('reopened native mass differs '+item['group']+str((actual['mass_kg'],expected['mass_kg'])))
        if max(abs(a-b) for a,b in zip(actual['cg_m'],expected['cg_m']))>1e-6:raise ValueError('reopened native centroid differs '+item['group'])
        for i in range(3):
            for j in range(3):
                if not math.isclose(actual['inertia_kg_m2'][i][j],expected['inertia_kg_m2'][i][j],rel_tol=2e-6,abs_tol=2e-5):raise ValueError('reopened native inertia differs '+item['group'])
        item['actual']=actual;item['native_valid']=True
    step=output/'model.step'
    Part.export([reopened.getObject(item['object_name']) for item in checks],str(step))
    reread=Part.read(str(step));expected_volume=math.fsum(item['expected']['volume_m3'] for item in checks)
    if not reread.isValid() or not math.isclose(reread.Volume/1e9,expected_volume,rel_tol=1e-7,abs_tol=1e-8):raise ValueError('STEP reopen volume differs')
    step_volume=reread.Volume/1e9
    (output/'model.step.gz').write_bytes(gzip.compress(step.read_bytes(),mtime=0));step.unlink()
    App.closeDocument(reopened.Name)
    actual_total=_aggregate([dict(id=x['group'],**x['actual']) for x in checks])
    result=dict(schema=SCHEMA,candidate_id=request['candidate_id'],body_candidate_id=request['body_candidate_id'],
        execution_status='completed',native_engine='FreeCAD '+'.'.join(App.Version()[:3]),
        material_group_count=len(checks),primitive_count=len(parts),native_checks=checks,
        equipment_context_count=len(geometry.get('contexts',[])),equipment_contexts_excluded_from_mass_and_STEP=True,
        freecad_reopened=True,step_reopened=True,step_total_volume_m3=step_volume,critical_roof_fit=critical_fit,
        defined_material_properties=actual_total,whole_equipped_mass_kg=None,
        complete_installed_mass_known=False,full_global_interference_check_executed=False,
        scope='Native material primitives with proposed placements. Compound overlaps at unresolved joints are not removed; no complete installed mass or collision-free assembly claim.',**FLAGS)
    (output/'native-result.json').write_bytes(encoded(result))
    (output/'completed').write_text('complete\n')


def run_export(vehicle,output,root=ROOT,seconds=600):
    from . import vehicle as model
    model.validate(vehicle,root=root)
    output=Path(output).resolve()
    if output.exists():raise ValueError('fresh native output directory required')
    output.mkdir(parents=True)
    raw=encoded(dict(candidate_id=vehicle['candidate_id'],parts=vehicle['geometry_parts'],contexts=vehicle['interfaces']['HVAC_packages'],
                     material_properties=vehicle['located_material_properties']))
    (output/'geometry.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    request=dict(schema=SCHEMA,candidate_id=vehicle['candidate_id'],body_candidate_id=vehicle['body_candidate_id'],
        magnet_component_id=vehicle['magnet_component_id'],geometry_sha256=sha256(raw).hexdigest(),
        source_sha256=vehicle['source_sha256'],maximum_seconds=seconds,maximum_published_bytes=MAX_BYTES,
        equipment_envelopes_are_material=False,**FLAGS)
    (output/'request.json').write_bytes(encoded(request));(output/'assembly.svg').write_text(render_svg(vehicle))
    binary=shutil.which('FreeCADCmd') or shutil.which('freecadcmd')
    command=[binary] if binary else ['flatpak','run','--filesystem='+str(Path(root).resolve()),'--command=FreeCADCmd','org.freecad.FreeCAD']
    source_root=Path(__file__).resolve().parents[2]
    script=output/'worker.py';script.write_text('import sys\nsys.path[:0]='+repr([str(source_root),str(Path(root).resolve())])+'\nfrom engineering.comfort_design.native_vehicle import _worker\n_worker('+repr(str(output))+')\n')
    start=time.monotonic();status='tool-error';code=None;reason=None
    try:
        with (output/'solver.log').open('w') as log:
            code=subprocess.run([*command,str(script)],cwd=root,stdout=log,stderr=subprocess.STDOUT,timeout=seconds).returncode
        status='completed' if code==0 and (output/'completed').is_file() else 'tool-error'
    except subprocess.TimeoutExpired:status='interrupted';reason='native budget exceeded'
    except OSError as error:reason=str(error)
    result=dict(candidate_id=vehicle['candidate_id'],body_candidate_id=vehicle['body_candidate_id'],
        execution_status=status,returncode=code,elapsed_seconds=time.monotonic()-start,reason=reason,
        source_sha256=vehicle['source_sha256'],scope='Native export/reopen; no physical qualification',**FLAGS)
    (output/'execution.json').write_bytes(encoded(result))
    if sum(p.stat().st_size for p in output.rglob('*') if p.is_file())>MAX_BYTES:
        result['execution_status']='budget-refused';result['reason']='native artifact budget exceeded'
        (output/'execution.json').write_bytes(encoded(result))
    manifest=dict(schema=SCHEMA,candidate_id=vehicle['candidate_id'],body_candidate_id=vehicle['body_candidate_id'],
        source_sha256=vehicle['source_sha256'],files_sha256=_inventory(output),**FLAGS)
    (output/'manifest.json').write_bytes(encoded(manifest))
    if result['execution_status']=='completed':verify_export(output,vehicle,root=root)
    return result


def verify_export(output,vehicle,root=ROOT):
    output=Path(output);manifest=json.loads((output/'manifest.json').read_bytes())
    if manifest['candidate_id']!=vehicle['candidate_id'] or manifest['body_candidate_id']!=vehicle['body_candidate_id']:raise ValueError('native package belongs to another candidate')
    if manifest['source_sha256']!=vehicle['source_sha256']:raise ValueError('native source snapshot differs')
    for name,expected in manifest['source_sha256'].items():
        path=Path(root)/name
        if path.is_symlink() or digest(path)!=expected:raise ValueError('native source changed '+name)
    if manifest['files_sha256']!=_inventory(output):raise ValueError('native artifact digest differs')
    request=json.loads((output/'request.json').read_bytes());raw=gzip.decompress((output/'geometry.json.gz').read_bytes())
    if request['geometry_sha256']!=sha256(raw).hexdigest() or json.loads(raw)['parts']!=vehicle['geometry_parts']:raise ValueError('native input geometry differs')
    execution=json.loads((output/'execution.json').read_bytes())
    if execution['execution_status']!='completed':return dict(current=True,execution_status=execution['execution_status'],native_reopen_established=False,**FLAGS)
    result=json.loads((output/'native-result.json').read_bytes())
    if result['candidate_id']!=vehicle['candidate_id'] or not result['freecad_reopened'] or not result['step_reopened']:raise ValueError('native reopen receipt missing')
    expected=_aggregate(vehicle['geometry_parts']);actual=result['defined_material_properties']
    if not math.isclose(actual['mass_kg'],expected['mass_kg'],rel_tol=1e-7) or not math.isclose(result['step_total_volume_m3'],expected['volume_m3'],rel_tol=1e-7):raise ValueError('native totals differ from geometry inventory')
    if any(result.get(k) is not value for k,value in FLAGS.items()):raise ValueError('native package cannot assert physical release')
    return dict(current=True,candidate_id=vehicle['candidate_id'],execution_status='completed',native_reopen_established=True,
        primitive_count=result['primitive_count'],defined_material_mass_kg=actual['mass_kg'],**FLAGS)
