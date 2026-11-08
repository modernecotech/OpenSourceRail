"""Studio rendering of source geometry; run only inside the installed Blender.

No solver, geometric resizing or physical acceptance occurs. Display omissions
are enumerated separately from the untouched source model.
"""
from pathlib import Path
from hashlib import sha256
import argparse, gzip, json, math, sys, time
import bpy
from mathutils import Vector

COLORS={'stock':('91a8b4',.55,.31,1.),'steel':('4d6978',.68,.26,1.),
        'seat':('1c8994',.10,.38,.84),'envelope':('d5b273',.05,.42,.22),
        'panel':('dbe6e9',.25,.35,.44),'rubber':('34434b',.02,.66,1.),
        'concrete':('cad3ce',.0,.66,1.),'aluminium':('b1c3ce',.72,.25,1.),
        'electrical':('c29856',.20,.40,.36),'gfrp':('e1e9e4',.03,.52,1.),
        'foam':('d7caae',0.,.78,1.),'polymer':('c5cece',.02,.58,1.),
        'glass':('79a4ad',.02,.21,.48),'copper':('b4774b',.80,.30,1.),'ground':('edf1ee',.0,.75,1.)}
MATERIALS={}


def read(p):
    p=Path(p);raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)


def material(name):
    if name in MATERIALS:return MATERIALS[name]
    color,metal,rough,alpha=COLORS[name]
    rgb=[int(color[i:i+2],16)/255 for i in (0,2,4)];rgb=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*rgb,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
    bs.inputs['Alpha'].default_value=alpha;m.diffuse_color=(*rgb,alpha)
    if name in ('stock','steel','aluminium','concrete','copper'):
        bevel=m.node_tree.nodes.new('ShaderNodeBevel');bevel.inputs['Radius'].default_value=.0025;bevel.samples=2
        m.node_tree.links.new(bevel.outputs['Normal'],bs.inputs['Normal'])
    MATERIALS[name]=m;return m


def mesh_group(name,triangles,mat):
    verts=[];faces=[];lookup={}
    for tri in triangles:
        f=[]
        for v in tri:
            key=tuple(v)
            if key not in lookup:lookup[key]=len(verts);verts.append(v)
            f.append(lookup[key])
        faces.append(f)
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(material(mat));o['presentation_only']=True
    return o


def vehicle(scene):
    sys.path.insert(0,scene['root'])
    from engineering.vehicle_installation.export import _mesh
    body=read(scene['input_path']);objects=[];hidden=[];shown=[];count=0;cached={};grouped={}
    for p in body['patterns']:
        if p['car_allocation']!=[[0,1.]]:continue
        assembly=p['assembly_id'];z=p['centroid_m'][2];y=p['centroid_m'][1]
        omit=((assembly in ('body/roof','services/pv') or (assembly=='services/hvac' and z>2.3))
              or (assembly in ('body/cladding','body/sideframe','body/fixed-window') and y<-.65))
        if omit:hidden.append(p['id']);continue
        shown.append(p['id']);count+=p['count'];g=p['geometry'];key=p['part_id']
        source_material=p['material_id'].split('/')[-1]
        if not g['exact_stock']:
            mat='seat' if assembly in ('body/chair','body/wheelchair') else 'panel' if assembly.startswith('body/') else 'electrical' if assembly.startswith('services/') else 'envelope'
        else:
            mat=('gfrp' if source_material in ('gfrp','fabric','coating') else
                 'foam' if source_material in ('core','foam','thermal-barrier') else
                 'rubber' if source_material in ('rubber','elastomer','rail-elastomer','belt','brake-friction') else
                 'polymer' if source_material in ('polymer','rail-polymer','adhesive') else
                 'glass' if source_material=='glass' else 'copper' if source_material=='copper' else
                 'aluminium' if source_material.startswith('al') else 'stock')
        if key not in grouped:grouped[key]=[mat,[]]
        if key not in cached:cached[key]=_mesh(g)
        R=p['rotation'];tris=cached[key]
        for position in p['positions_m']:
            for tri in tris:
                grouped[key][1].append([[position[i]+sum(R[i][j]*v[j] for j in range(3)) for i in range(3)] for v in tri])
    triangles=sum(len(t[1]) for t in grouped.values())
    if triangles>scene['maximum_triangles'] or len(grouped)>scene['maximum_mesh_groups']:raise ValueError('Bounded presentation geometry exceeded')
    for key,(mat,tris) in grouped.items():objects.append(mesh_group(key,tris,mat))
    return objects,dict(shown_source_pattern_ids=shown,hidden_source_pattern_ids=hidden,
        source_occurrences_shown=count,mesh_groups=len(objects),triangles=triangles,
        display_omissions='Roof/PV, high roof HVAC and near-side wall stock/envelopes only. Physical pattern definitions unchanged.',
        source_frame='X-forward,Y-left,Z-up; metres',geometry_basis='Existing vehicle_installation.export._mesh projection; stock and envelopes distinguished, no new supplier shape.')


def civil(scene):
    import importlib.util
    path=Path(scene['root'])/'engineering/visual_models/render_blender.py'
    spec=importlib.util.spec_from_file_location('osr_existing_civil_mesh',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    source=read(scene['input_path']);objects=[];ids=[]
    for e in source['entities']:
        value=dict(e['geometry'],id=e['id'],shape=e['shape'],material='steel')
        o=module.make(value)
        m=e['material'];mat='concrete' if 'concrete' in m else 'rubber' if 'bearing' in m else 'aluminium' if 'aluminium' in m else 'steel'
        o.material_slots[0].link='OBJECT';o.material_slots[0].material=material(mat);objects.append(o);ids.append(e['id'])
    triangles=sum(len(o.data.polygons)*2 for o in objects)
    if triangles>scene['maximum_triangles'] or len(objects)>scene['maximum_mesh_groups']:raise ValueError('Civil presentation budget exceeded')
    return objects,dict(shown_source_entity_ids=ids,hidden_source_entity_ids=[],source_entities=len(objects),
        mesh_groups=len(objects),triangles_upper_bound=triangles,geometry_basis=source['geometric_scope'],
        source_frame='X-along-span,Y-transverse,Z-up at railhead; metres',
        separate_FEM_geometry='This two-track segmented/located assembly is not the bonded continuous gross-solid FEM model.')


def area(name,at,target,power,size,color=(1,1,1)):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color
    o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=at;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()


def main():
    p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    scene=read(a.scene);out=Path(a.output);start=time.monotonic()
    if sha256(Path(scene['input_path']).read_bytes()).hexdigest()!=scene['input_sha256']:raise ValueError('Source model bytes changed')
    bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1.
    objects,geometry=vehicle(scene) if scene['kind']=='vehicle' else civil(scene)
    bpy.context.view_layer.update();points=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
    lo=Vector([min(q[i] for q in points) for i in range(3)]);hi=Vector([max(q[i] for q in points) for i in range(3)]);target=(lo+hi)/2
    direction=Vector(scene['camera']['direction']).normalized();cam=bpy.data.cameras.new('Camera');camera=bpy.data.objects.new('Camera',cam);bpy.context.collection.objects.link(camera);s.camera=camera;cam.type='ORTHO'
    camera.location=target+direction*300;camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
    inverse=camera.matrix_world.inverted();projected=[inverse@q for q in points];xmin,xmax=min(q.x for q in projected),max(q.x for q in projected);ymin,ymax=min(q.y for q in projected),max(q.y for q in projected)
    shift=camera.matrix_world.to_quaternion()@Vector(((xmin+xmax)/2,(ymin+ymax)/2,0));camera.location+=shift;target+=shift
    aspect=scene['width']/scene['height'];fill=scene['camera']['fill'];cam.ortho_scale=max(xmax-xmin,(ymax-ymin)*aspect)/fill;cam.clip_start=.01;cam.clip_end=2000
    extent=max(xmax-xmin,ymax-ymin,2.);floorz=lo.z-.03
    bpy.ops.mesh.primitive_plane_add(size=extent*200,location=(target.x,target.y,floorz));floor=bpy.context.object;floor.name='Display-only studio floor';floor.data.materials.append(material('ground'));floor.is_shadow_catcher=True
    world=bpy.data.worlds.new('Studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.72,.80,.84,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.40;s.world=world
    power=13*extent*extent
    area('Key',target+Vector((-extent*.35,-extent*.6,extent*1.0)),target,power,extent*.75)
    area('Fill',target+Vector((extent*.8,-extent*.1,extent*.6)),target,power*.65,extent*.9,(.85,.92,1))
    area('Rim',target+Vector((-.4*extent,.6*extent,.7*extent)),target,power*.7,extent*.65,(1,.92,.8))
    s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16 if scene['width']<2000 else 64;s.cycles.use_denoising=True;s.cycles.seed=671;s.cycles.max_bounces=5;s.cycles.transparent_max_bounces=12
    s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=scene['width'];s.render.resolution_y=scene['height'];s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.film_transparent=True;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.10
    s.render.filepath=str(out/'raw.png');bpy.ops.render.render(write_still=True)
    geometry.update(recipe_id=scene['recipe_id'],candidate_id=scene['candidate_id'],source_bounds_m=[list(lo),list(hi)],
        actual_blender_version=bpy.app.version_string,display_camera=dict(direction=list(direction),target=list(target),ortho_scale_m=cam.ortho_scale),
        rendering_wall_s=time.monotonic()-start,source_geometry_resized=False,studio_floor_is_physical_component=False,
        physical_accepted=False,engineering_accepted=False,manufacturing_release=False)
    (out/'geometry.json').write_text(json.dumps(geometry,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:geometry[k] for k in ('candidate_id','mesh_groups','actual_blender_version','rendering_wall_s')}))


if __name__=='__main__':main()
