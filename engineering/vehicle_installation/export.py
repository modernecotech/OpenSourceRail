"""Instanced full-layout GLB and separately checked gross-stock CAD subset."""
from pathlib import Path
from collections import defaultdict
from math import sin,cos,pi,sqrt
import gzip,json,struct,csv,time
from engineering.station_rail.common import identity,digest,encoded
from engineering.design_search.craft_backends import native,solidcraft,freecad_reference
from . import ROOT,FLAGS,model


def _quat(R):
    t=R[0][0]+R[1][1]+R[2][2]
    if t>0:
        s=sqrt(t+1)*2;return [(R[2][1]-R[1][2])/s,(R[0][2]-R[2][0])/s,(R[1][0]-R[0][1])/s,.25*s]
    i=max(range(3),key=lambda j:R[j][j]);j=(i+1)%3;k=(i+2)%3;s=sqrt(1+R[i][i]-R[j][j]-R[k][k])*2
    q=[0.,0.,0.,0.];q[i]=.25*s;q[j]=(R[j][i]+R[i][j])/s;q[k]=(R[k][i]+R[i][k])/s;q[3]=(R[k][j]-R[j][k])/s;return q


def _box(size,at=(0.,0.,0.)):
    a,b,c=[v/2 for v in size];x,y,z=at
    v=[[x+sx*a,y+sy*b,z+sz*c] for sx,sy,sz in ((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1))]
    faces=((0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7))
    return [[v[i] for i in f] for f in faces]


def _mesh(g):
    size=g['size_m'];s=g['source_stock'];kind=g['kind']
    if s and kind=='rhs':
        L,b,h=size;t=s['wall_m'];out=[]
        for side in (-1,1):out+=_box([L,t,h],[0.,side*(b-t)/2,0.]);out+=_box([L,b-2*t,t],[0.,0.,side*(h-t)/2])
        return out
    if s and kind in ('cylinder','annulus'):
        L=size[0];ro=s.get('radius_m',s.get('outer_radius_m'));ri=s.get('inner_radius_m',0.);out=[]
        n=24
        def pt(x,r,i):return [x,r*cos(2*pi*i/n),r*sin(2*pi*i/n)]
        for i in range(n):
            j=(i+1)%n;a,b,c,d=pt(-L/2,ro,i),pt(L/2,ro,i),pt(L/2,ro,j),pt(-L/2,ro,j)
            out.extend(([a,b,c],[a,c,d]))
            if ri:
                ai,bi,ci,di=pt(-L/2,ri,i),pt(L/2,ri,i),pt(L/2,ri,j),pt(-L/2,ri,j)
                out.extend(([ai,ci,bi],[ai,di,ci],[a,d,di],[a,di,ai],[b,bi,ci],[b,ci,c]))
            else:out.extend(([[ -L/2,0,0],d,a],[[L/2,0,0],b,c]))
        return out
    return _box(size)


def preview_glb(result,path):
    """Float32 presentation projection; source double coordinates stay canonical."""
    if result['candidate_id']!=identity(result['physical_definition']):raise ValueError('Same-candidate layout required')
    groups=defaultdict(list)
    for p in result['patterns']:groups[p['part_id']].append(p)
    doc=dict(asset=dict(version='2.0',generator='OpenSourceRail explicit installation projection'),scene=0,
        scenes=[dict(nodes=[0])],nodes=[dict(name='SI installation → glTF Y-up presentation',rotation=[-sqrt(.5),0,0,sqrt(.5)],children=[])],
        meshes=[],materials=[],bufferViews=[],accessors=[],buffers=[{}],extensionsUsed=['EXT_mesh_gpu_instancing'],extensionsRequired=['EXT_mesh_gpu_instancing'])
    # Stock solids are opaque; purchased/proposed envelopes stay translucent.
    colors=([.48,.58,.62,1.],[.10,.50,.61,.18],[.91,.48,.12,.10])
    for i,color in enumerate(colors):doc['materials'].append(dict(name=('Exact gross stock','Catalogue equipment envelope','Proposed unresolved zone')[i],pbrMetallicRoughness=dict(baseColorFactor=color,metallicFactor=.35 if i==0 else 0.,roughnessFactor=.5),doubleSided=True,alphaMode='OPAQUE' if i==0 else 'BLEND'))
    binary=bytearray()
    def accessor(values,width,kind,bounds=False):
        while len(binary)%4:binary.append(0)
        offset=len(binary)
        for v in values:binary.extend(struct.pack('<'+'f'*width,*v))
        view=len(doc['bufferViews']);doc['bufferViews'].append(dict(buffer=0,byteOffset=offset,byteLength=len(binary)-offset))
        a=dict(bufferView=view,componentType=5126,count=len(values),type=kind)
        if bounds:a.update(min=[min(x[i] for x in values) for i in range(width)],max=[max(x[i] for x in values) for i in range(width)])
        idx=len(doc['accessors']);doc['accessors'].append(a);return idx
    for name,patterns in sorted(groups.items()):
        g=patterns[0]['geometry'];tris=_mesh(g);vertices=[];normals=[]
        for tri in tris:
            a,b,c=tri;u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
            n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];length=sqrt(sum(x*x for x in n));n=[x/length for x in n]
            vertices+=tri;normals += [n]*3
        pos=accessor(vertices,3,'VEC3',True);normal=accessor(normals,3,'VEC3')
        material=0 if g['exact_stock'] else 1 if g['kind']=='envelope' else 2
        mesh=len(doc['meshes']);doc['meshes'].append(dict(name=name,primitives=[dict(attributes=dict(POSITION=pos,NORMAL=normal),mode=4,material=material)]))
        translations=[];rotations=[];ids=[]
        for p in patterns:
            translations.extend(p['positions_m']);rotations.extend([_quat(p['rotation'])]*p['count'])
            ids.extend(p['id']+'/'+str(i) for i in range(p['count']))
        node=len(doc['nodes']);doc['nodes'][0]['children'].append(node)
        doc['nodes'].append(dict(name=name,mesh=mesh,extensions=dict(EXT_mesh_gpu_instancing=dict(attributes=dict(TRANSLATION=accessor(translations,3,'VEC3'),ROTATION=accessor(rotations,4,'VEC4')))),
            extras=dict(part_id=name,source_part_id=patterns[0]['source_part_id'],occurrence_count=len(ids),occurrence_id_rule='pattern.id/index; order exactly matches pattern list and positions',
                geometry_basis=g['definition_basis'],exact_finished_geometry=False)))
    doc['nodes'][0]['extras']=dict(candidate_id=result['candidate_id'],mass_evaluation_id=result['evaluation_id'],source_units='m',presentation_frame='x, z, -y',stock_and_envelope_projection=True,**FLAGS)
    doc['buffers'][0]['byteLength']=len(binary);raw=json.dumps(doc,separators=(',',':'),allow_nan=False).encode()
    raw+=b' '*((-len(raw))%4);binary.extend(b'\0'*((-len(binary))%4))
    data=struct.pack('<4sII',b'glTF',2,12+8+len(raw)+8+len(binary))+struct.pack('<I4s',len(raw),b'JSON')+raw+struct.pack('<I4s',len(binary),b'BIN\0')+binary
    Path(path).write_bytes(data)
    return dict(path=str(path),sha256=digest(path),bytes=len(data),mesh_definitions=len(groups),instance_count=result['total_occurrences'],
        coordinate_scope='Presentation only. Float32 and cylinder24segments are not CAD/mass acceptance. Sourcecoordinates stay doubleprecision SI.',**FLAGS)


def representative_case(result):
    """First bogie frame exact gross-stock occurrences, with RHS as four walls."""
    entities=[];measures={};materials={m['id']:m for m in model.load()['materials']}
    for p in result['patterns']:
        if p['assembly_id']!='running/bogie-frame' or p['bogie_index']!=0 or not p['geometry']['exact_stock']:continue
        g=p['geometry'];s=g['source_stock'];R=p['rotation'];L,b,h=g['size_m'];pieces=[([L,b,h],[0,0,0])]
        if s['kind']=='rhs':
            t=s['wall_m'];pieces=[]
            for side in (-1,1):pieces += [([L,t,h],[0,side*(b-t)/2,0]),([L,b-2*t,t],[0,0,side*(h-t)/2])]
        if s['kind'] not in ('rhs','box'):raise ValueError('Representative frame only admits source boxes/RHS')
        for i,center in enumerate(p['positions_m']):
            for j,(size,offset) in enumerate(pieces):
                c=[center[a]+sum(R[a][k]*offset[k] for k in range(3)) for a in range(3)];world=model.transformed_size(size,R);corner=[c[a]-world[a]/2 for a in range(3)]
                name=p['id']+f'/{i}/wall-{j}';entities.append(dict(id=name,shape='box',at_m=corner,size_m=world,material=p['material_id']))
                measures[name]=dict(volume_m3=__import__('math').prod(size),centroid_m=c,bounds_m=[corner,[corner[k]+world[k] for k in range(3)]])
    projection=dict(entities=entities,units='m')
    return dict(schema='osr-installation-stock-cad-case/1',case_id='installed-bogie-frame-stock',candidate_id=result['candidate_id'],component_geometry_id=identity(projection),
        entities=entities,materials=materials,expected=dict(part_count=len(entities),part_measures=measures),
        scope='One bogie frame gross-stock subset in installed coordinates, RHS decomposed into disjoint walls; not finished joints or full installed acceptance',**FLAGS)


def _compare(case,measured,associate=False):
    expected=case['expected']['part_measures'];unused=set(expected);matches=[]
    for body in measured['bodies']:
        actual=[*body['center_of_mass_m'],*body['bbox_m']['min'],*body['bbox_m']['max']];found=[]
        for name in unused:
            e=expected[name];wanted=[*e['centroid_m'],*e['bounds_m'][0],*e['bounds_m'][1]]
            if abs(body['volume_m3']-e['volume_m3'])<=max(1e-12,e['volume_m3']*1e-7) and max(abs(a-b) for a,b in zip(actual,wanted))<1e-6:found.append(name)
        if len(found)!=1:raise ValueError('No unique volume/centroid/bounds correspondence')
        name=found[0]
        if not associate and name!=body['id']:raise ValueError('Source occurrence names changed')
        if body.get('closed') is not True:raise ValueError('Native solid is not closed')
        unused.remove(name);matches.append(dict(source_occurrence=name,imported_name=body['id'],volume_m3=body['volume_m3']))
    if unused:raise ValueError('Native source occurrence coverage differs')
    return dict(comparison_passed=True,exact_brep=associate,occurrences=matches,native_names_preserved=all(r['source_occurrence']==r['imported_name'] for r in matches),**FLAGS)


def native_cad(result,output):
    folder=Path(output);folder.mkdir(parents=True,exist_ok=False);case=representative_case(result)
    (folder/'case.json').write_bytes(encoded(case));script=folder/'commands.json';script.write_bytes(encoded(solidcraft.script_for(case)))
    generated=folder/'solidcraft'
    execution=native.run('solidcraft',['run',script,'--save',generated/'assembly.sc','--out',generated/'assembly.step','--results','--json-out',generated/'results.json'],generated,timeout_s=120,memory_mb=2048,read_roots=(folder,))
    if execution['execution']!='executed':raise ValueError('CAD worker failed; immutable execution retained')
    measured=solidcraft.parse_measurements(json.loads((generated/'results.json').read_bytes()));comparison=_compare(case,measured)
    reference=freecad_reference.run(generated/'assembly.step',folder/'independent-freecad',timeout_s=120,memory_mb=2048)
    if reference['execution']!='completed':raise ValueError('Independent STEP import failed; native execution and error retained')
    exact=_compare(case,reference,associate=True)
    report=dict(candidate_id=result['candidate_id'],installation_evaluation_id=result['evaluation_id'],component_geometry_id=case['component_geometry_id'],
        diagnostic=comparison,independent_exact=exact,source_stock_occurrences=len(case['entities']),
        step_sha256=digest(generated/'assembly.step'),native_sha256=digest(generated/'assembly.sc'),source_sha256=model.sources(),**FLAGS)
    report['evaluation_id']=identity(report);(folder/'verification.json').write_bytes(encoded(report));return report


def write(result,output,*,cad=False):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    (output/'installation.json.gz').write_bytes(gzip.compress(encoded(result),mtime=0))
    (output/'axle-loads.json').write_bytes(encoded(model.axle_loads(result)))
    with (output/'bom.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['part_id','source_part_id','assembly_id','quantity_per_train','material_id','mass_low_kg','mass_base_kg','mass_high_kg','direct_base_usd','stock_kind','manufacturing','joining','maintenance_removal'])
        for p in result['parts']:writer.writerow([p['id'],p['source_part_id'],p['assembly_id'],p['quantity_per_train'],p['material_id'],*[p['mass_each_kg'][c]*p['quantity_per_train'] for c in model.CASES],p['direct_cost_each_usd']['base']*p['quantity_per_train'],(p['stock'] or {}).get('kind'),'; '.join(p['manufacturing']),p['joining'],p['maintenance_removal']])
    preview=preview_glb(result,output/'assembly.glb')
    meta=dict(schema='osr-vehicle-installation-run/1',candidate_id=result['candidate_id'],evaluation_id=result['evaluation_id'],source_sha256=result['source_sha256'],preview=preview,files_sha256={p.name:digest(p) for p in output.iterdir() if p.is_file()},**FLAGS)
    if cad:
        try:meta['native_cad']=dict(status='completed',result=native_cad(result,output/'native-cad'))
        except (ValueError,OSError,KeyError,TypeError) as exc:
            failure=dict(status='failed',type=type(exc).__name__,reason=str(exc),candidate_id=result['candidate_id'],**FLAGS)
            (output/'native-failure.json').write_bytes(encoded(failure));meta['native_cad']=failure
    if model.sources()!=result['source_sha256']:raise ValueError('Source drift during export; retain failed run, regenerate')
    meta['files_sha256']={p.relative_to(output).as_posix():digest(p) for p in output.rglob('*') if p.is_file()}
    meta['manifest_id']=identity(meta);(output/'manifest.json').write_bytes(encoded(meta));return meta
