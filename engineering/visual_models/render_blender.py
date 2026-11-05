"""Blender worker: source mesh exports first, explicit display offsets second."""
import argparse,json,math,struct,time
from hashlib import sha256
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from bpy_extras.object_utils import world_to_camera_view

PALETTE={
 'concrete':('A6B5B7',0.,.76),'steel':('8EAAAF',.72,.28),
 'dark_steel':('25424E',.65,.32),'aluminium':('BDCACE',.78,.27),
 'white':('E7ECEA',.14,.35),'teal':('167F82',.36,.31),
 'orange':('EBA448',.28,.35),'red':('B85043',.25,.34),
 'rubber':('273638',.02,.8),'glass':('6CABB8',.3,.2),
 'wood':('BFA988',0.,.65),'copper':('B4774B',.8,.3),
 'ground':('E4E9E7',0.,.85),'gfrp':('E7ECEA',.03,.5),
 'foam':('D9CDB1',0.,.8),'seat':('167F82',.03,.65),
 'safety_yellow':('EBA448',.3,.4),'paint_teal':('167F82',.36,.31),
 'brushed_aluminium':('BDCACE',.78,.27),'steel_dark':('25424E',.65,.32)}
MATERIALS={};MESHES={};HOLED={};SEGMENTS=64


def linear(x):return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4

def material(name):
    if name in MATERIALS:return MATERIALS[name]
    color,metal,rough=PALETTE.get(name,('A2B3B5',.25,.5))
    rgb=[linear(int(color[i:i+2],16)/255) for i in (0,2,4)]
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*rgb,1)
    bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
    # Bevel shading changes normals only, never the source/exported solid.
    if name not in ('glass','rubber','ground'):
        bevel=m.node_tree.nodes.new('ShaderNodeBevel');bevel.inputs['Radius'].default_value=.0015 if name!='concrete' else .008;bevel.samples=2
        m.node_tree.links.new(bevel.outputs['Normal'],bs.inputs['Normal'])
    MATERIALS[name]=m;return m


def mesh_data(e):
    key=json.dumps({k:e[k] for k in ('shape','size_m','radius_m','inner_radius_m','length_m','points_yz_m') if k in e},sort_keys=True)
    if key in MESHES:return MESHES[key]
    s=e['shape'];v=[];f=[];smooth=[]
    if s=='box':
        x,y,z=e['size_m'];v=[(0,0,0),(x,0,0),(x,y,0),(0,y,0),(0,0,z),(x,0,z),(x,y,z),(0,y,z)]
        f=[(3,2,1,0),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
    elif s in ('cylinder','tube'):
        n=SEGMENTS;r=e['radius_m'];h=e['length_m'];inner=e.get('inner_radius_m',0.)
        rings=[(r,0),(r,h)] if not inner else [(r,0),(r,h),(inner,0),(inner,h)]
        v=[(radius*math.cos(2*math.pi*i/n),radius*math.sin(2*math.pi*i/n),z) for radius,z in rings for i in range(n)]
        for i in range(n):j=(i+1)%n;f.append((i,j,n+j,n+i));smooth.append(len(f)-1)
        if not inner:f += [tuple(reversed(range(n))),tuple(range(n,2*n))]
        else:
            for i in range(n):
                j=(i+1)%n
                f += [(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)]
                smooth.append(len(f)-3)
    elif s=='sphere':
        r=e['radius_m'];n=48;lat=24
        v=[(0,0,-r)]
        for j in range(1,lat):
            phi=-math.pi/2+math.pi*j/lat
            v.extend((r*math.cos(phi)*math.cos(2*math.pi*i/n),r*math.cos(phi)*math.sin(2*math.pi*i/n),r*math.sin(phi)) for i in range(n))
        v.append((0,0,r));top=len(v)-1
        for i in range(n):
            k=(i+1)%n;f.append((0,1+k,1+i));f.append((top,1+(lat-2)*n+i,1+(lat-2)*n+k))
        for j in range(lat-2):
            for i in range(n):
                k=(i+1)%n;a=1+j*n;f.append((a+i,a+k,a+n+k,a+n+i))
        smooth=list(range(len(f)))
    elif s=='profile':
        p=e['points_yz_m'][:]
        if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))<0:p.reverse()
        n=len(p);h=e['length_m'];v=[(x,y,z) for x in (0,h) for y,z in p]
        vec=[Vector(x) for x in v[:n]]
        for tri in tessellate_polygon([vec]):
            idx=[x if isinstance(x,int) else vec.index(x) for x in tri];f += [tuple(reversed(idx)),tuple(i+n for i in idx)]
        f.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    mesh=bpy.data.meshes.new(e['shape']);mesh.from_pydata(v,[],f);mesh.update()
    for i in smooth:mesh.polygons[i].use_smooth=True
    MESHES[key]=mesh;return mesh


def make(e):
    if e['shape']=='pipe':
        curve=bpy.data.curves.new(e['id'],'CURVE');curve.dimensions='3D';curve.resolution_u=1;curve.bevel_depth=e['radius_m'];curve.bevel_resolution=3;curve.use_fill_caps=True
        line=curve.splines.new('POLY');line.points.add(len(e['path_m'])-1)
        for p,co in zip(line.points,e['path_m']):p.co=(*co,1)
        obj=bpy.data.objects.new(e['id'],curve)
    else:obj=bpy.data.objects.new(e['id'],mesh_data(e))
    bpy.context.collection.objects.link(obj);obj.location=e['at_m']
    if e['shape'] in ('cylinder','tube'):obj.rotation_mode='QUATERNION';obj.rotation_quaternion=Vector(e['axis']).to_track_quat('Z','Y')
    if e.get('holes'):
        key=json.dumps({'size':e['size_m'],'holes':e['holes']},sort_keys=True)
        if key in HOLED:obj.data=HOLED[key]
        else:
            obj.data=obj.data.copy();bpy.context.view_layer.objects.active=obj
            for hole in e['holes']:
                index='xyz'.index(hole.get('axis','z'));axis=[0,0,0];axis[index]=1;start=e['at_m'][:]
                for j,k in enumerate(('x_m','y_m','z_m')):
                    if j!=index:start[j]+=hole.get(k,0.)
                length=hole.get('length_m',e['size_m'][index]);eps=.00001 if length==e['size_m'][index] else 0.
                start[index]-=eps
                cutter=bpy.data.objects.new('Hole cutter',mesh_data({'shape':'cylinder','radius_m':hole['diameter_m']/2,'length_m':length+2*eps}))
                bpy.context.collection.objects.link(cutter);cutter.location=start;cutter.rotation_mode='QUATERNION';cutter.rotation_quaternion=Vector(axis).to_track_quat('Z','Y')
                modifier=obj.modifiers.new('Source through-hole','BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
                bpy.ops.object.modifier_apply(modifier=modifier.name);bpy.data.objects.remove(cutter,do_unlink=True)
            if not len(obj.data.vertices):raise ValueError('Empty drilled source mesh: '+e['id'])
            HOLED[key]=obj.data
    obj.data.materials.append(material(e.get('material','steel'))) if not obj.data.materials else None
    # Linked mesh instances need per-object material slots, not shared mutation.
    if len(obj.material_slots)==0:obj.data.materials.append(material(e.get('material','steel')))
    obj.material_slots[0].link='OBJECT';obj.material_slots[0].material=material(e.get('material','steel'))
    for k in ('id','basis','source','group','source_part_id'):
        if k in e:obj[k]=str(e[k])
    obj['units']='metres';obj['physical_accepted']=False
    return obj


def world_bounds(objects):
    bpy.context.view_layer.update();points=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
    return [[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]


def stl_export(objects,path):
    count=0
    with path.open('wb') as out:
        out.write(b'OpenSourceRail source mesh; millimetres; not production release'.ljust(80,b' '));out.write(struct.pack('<I',0))
        deps=bpy.context.evaluated_depsgraph_get()
        for obj in objects:
            evaluated=obj.evaluated_get(deps);mesh=evaluated.to_mesh();mesh.calc_loop_triangles();matrix=obj.matrix_world
            for tri in mesh.loop_triangles:
                a,b,c=[matrix@mesh.vertices[i].co for i in tri.vertices]
                normal=(b-a).cross(c-a)
                if normal.length_squared<1e-24:continue
                normal.normalize();out.write(struct.pack('<12fH',*normal,*(x*1000 for p in (a,b,c) for x in p),0));count+=1
            evaluated.to_mesh_clear()
        out.seek(80);out.write(struct.pack('<I',count))
    return count


def check_mesh_exports(objects,out,name,source_bounds):
    """Reopen the GLB and binary STL; preserve IDs, source pose and SI scale."""
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(out/(name+'.glb')))
    imported=[o for o in bpy.data.objects if o not in before]
    meshes=[o for o in imported if o.type=='MESH']
    expected={o['id'] for o in objects}
    if {o.get('id') for o in meshes}!=expected or len(meshes)!=len(objects):
        raise ValueError('GLB reopened part identities differ')
    reopened_bounds=world_bounds(meshes)
    if max(abs(a-b) for x,y in zip(reopened_bounds,source_bounds) for a,b in zip(x,y))>1e-4:
        raise ValueError('GLB reopened units or source pose differ')
    for obj in imported:bpy.data.objects.remove(obj,do_unlink=True)
    lo=[float('inf')]*3;hi=[-float('inf')]*3
    with (out/(name+'.stl')).open('rb') as inp:
        inp.read(80);count=struct.unpack('<I',inp.read(4))[0]
        for _ in range(count):
            row=struct.unpack('<12fH',inp.read(50))
            for j in (3,6,9):
                for i in range(3):lo[i]=min(lo[i],row[j+i]/1000);hi[i]=max(hi[i],row[j+i]/1000)
        if inp.read(1):raise ValueError('Unexpected STL data')
    if not count or max(abs(a-b) for x,y in zip((lo,hi),source_bounds) for a,b in zip(x,y))>1e-4:
        raise ValueError('STL reopened units or source pose differ')
    return dict(glb_reopened=True,glb_reopened_parts=len(meshes),glb_source_bounds_m=reopened_bounds,
                stl_reopened=True,stl_source_bounds_m=[lo,hi])


def area(name,location,target,power,size,color=(1,1,1)):
    light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='DISK';light.size=size;light.color=color
    o=bpy.data.objects.new(name,light);bpy.context.collection.objects.link(o);o.location=location;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()


def main():
    import sys
    p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--output',required=True);p.add_argument('--preview',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    started=time.monotonic();data=json.loads(Path(a.scene).read_bytes());out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    objects=[make(e) for e in data['entities']];source_bounds=world_bounds(objects)
    for obj in objects:obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.export_scene.gltf(filepath=str(out/(data['id']+'.glb')),export_format='GLB',use_selection=True,export_extras=True,export_animations=False,export_lights=False,export_cameras=False,export_apply=False)
    triangles=stl_export(objects,out/(data['id']+'.stl'))
    mesh_check=check_mesh_exports(objects,out,data['id'],source_bounds)
    for obj,e in zip(objects,data['entities']):obj.location+=Vector(e.get('render_offset_m',[0,0,0]));obj.select_set(False)
    bounds=world_bounds(objects)
    target=Vector(data.get('camera',{}).get('target_m',[(x+y)/2 for x,y in zip(*bounds)]));direction=Vector(data.get('camera',{}).get('direction',[1,-1,.8])).normalized()
    cam=bpy.data.cameras.new('Presentation camera');camera=bpy.data.objects.new('Presentation camera',cam);bpy.context.collection.objects.link(camera);scene.camera=camera;cam.type='ORTHO';camera.location=target+direction*1000;camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
    bpy.context.view_layer.update();inverse=camera.matrix_world.inverted();points=[inverse@(o.matrix_world@Vector(c)) for o in objects for c in o.bound_box]
    xmin,xmax=min(p.x for p in points),max(p.x for p in points);ymin,ymax=min(p.y for p in points),max(p.y for p in points)
    # Recenter any proposed camera on its actual geometry projection.
    shift=camera.matrix_world.to_quaternion()@Vector(((xmin+xmax)/2,(ymin+ymax)/2,0));camera.location+=shift;target+=shift
    width,height=(1500,950) if a.preview else (3000,1900)
    scene.render.resolution_x=width;scene.render.resolution_y=height;scene.render.resolution_percentage=100
    cam.ortho_scale=max((xmax-xmin)/.68,(ymax-ymin)*(width/height)/.68,.5)
    cam.lens=50;cam.clip_end=10000;cam.clip_start=.001
    extent=max(xmax-xmin,ymax-ymin,2.)
    plane_mesh=bpy.data.meshes.new('Studio floor');z=bounds[0][2]-.025
    plane_mesh.from_pydata([(-10000,-10000,z),(10000,-10000,z),(10000,10000,z),(-10000,10000,z)],[],[(0,1,2,3)]);plane_mesh.update()
    floor=bpy.data.objects.new('Studio floor',plane_mesh);bpy.context.collection.objects.link(floor);floor.data.materials.append(material('ground'));floor.is_shadow_catcher=True
    world=bpy.data.worlds.new('Neutral studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.75,.82,.85,1);world.node_tree.nodes['Background'].inputs[1].default_value=.22;scene.world=world
    # Lighting scales with model dimensions; no HDRI or external texture assets.
    power=10*extent*extent
    area('Key',target+Vector((-extent*.4,-extent*.5,extent*.95)),target,power,extent*.65)
    area('Fill',target+Vector((extent*.7,extent*.2,extent*.65)),target,power*.5,extent*.7,(.82,.9,1))
    area('Rim',target+Vector((-extent*.5,extent*.6,extent*.6)),target,power*.65,extent*.5,(1,.91,.78))
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12 if a.preview else 48;scene.cycles.use_denoising=True;scene.cycles.seed=41;scene.cycles.max_bounces=5;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=3
    scene.render.threads_mode='FIXED';scene.render.threads=4;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
    scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-.35
    scene.render.filepath=str(out/'raw.png');bpy.context.view_layer.update()
    labels=[]
    for label in data.get('labels',[]):
        q=world_to_camera_view(scene,camera,Vector(label['anchor_m']));labels.append({**label,'pixel':[q.x*width,(1-q.y)*height]})
    bpy.ops.render.render(write_still=True)
    receipt={'schema':'osr-blender-visual-execution/1','assembly_id':data['id'],'visual_study_id':data['visual_study_id'],'blender_version':bpy.app.version_string,'source_bounds_m':source_bounds,'rendered_bounds_m':bounds,'mesh_objects':len(objects),'stl_triangles':triangles,'stl_units':'millimetres','gltf_units':'metres','display_offsets_in_mesh_exports':False,'labels':labels,'render_width':width,'render_height':height,'wall_seconds':time.monotonic()-started,'unmapped_materials':sorted(set(e.get('material','steel') for e in data['entities'])-set(PALETTE)),'physical_accepted':False,'engineering_accepted':False,'manufacturing_release':False}
    receipt.update(worker_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),input_sha256=sha256(Path(a.scene).read_bytes()).hexdigest())
    receipt.update(mesh_check)
    receipt['files_sha256']={p.name:sha256(p.read_bytes()).hexdigest() for p in
        (out/(data['id']+'.glb'),out/(data['id']+'.stl'),out/'raw.png')}
    (out/'render.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    # The compact recipe is the editable source; bulky .blend caches stay private.
    print(json.dumps({k:receipt[k] for k in ('assembly_id','mesh_objects','stl_triangles','wall_seconds')}))

if __name__=='__main__':main()
