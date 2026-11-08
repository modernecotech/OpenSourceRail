"""Reproducible presentation recipes over sealed, existing engineering geometry.

Render-only cameras, colours and omissions never change CAD, mass or acceptance.
No geometry generator or numerical solver is executed by this module.
"""
from pathlib import Path
from hashlib import sha256
import argparse, gzip, json, math, os, resource, shutil, signal, subprocess, time

ROOT=Path(__file__).resolve().parents[2]
OWNED=('tools/engineering_gallery/cad.py','tools/engineering_gallery/blender.py')
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
           operating_release=False,selected_reference_changed=False)


def digest(p):
    h=sha256()
    with Path(p).open('rb') as f:
        while block:=f.read(1024*1024):h.update(block)
    return h.hexdigest()


def identity(value):return sha256((json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()

def read(p):
    p=Path(p);raw=p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)


def write(p,value):
    p=Path(p)
    if p.exists():raise ValueError('Immutable output already exists: '+str(p))
    p.write_text(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n')


def _recipe(root,name,kind,source,*,camera,caption,**extra):
    root=Path(root);v=read(root/source);cid=v.get('candidate_id',v.get('civil_candidate_id'))
    if cid is None:raise ValueError('Explicit physical candidate required')
    files={source,*OWNED,'engineering/station_rail/common.py'}
    if kind=='native':
        files|={extra['native_file'],'engineering/design_search/craft_backends/tools.json'}
    elif kind=='vehicle':
        files|={'engineering/vehicle_installation/export.py','engineering/vehicle_installation/model.py'}
    else:files|={'engineering/visual_models/render_blender.py'}
    r=dict(schema='osr-engineering-gallery-cad-recipe/1',id=name,kind=kind,input_file=source,
        candidate_id=cid,input_evaluation_id=v.get('evaluation_id',v.get('assembly_definition_id')),
        source_sha256={n:digest(root/n) for n in sorted(files)},camera=camera,caption=caption,
        units='m',render_size=[3000,1900],presentation_only=True,**extra,**FLAGS)
    r['recipe_id']=identity(r);return r


def recipes(root=ROOT):
    root=Path(root);launch='docs/design-engine/launch-detail/assembly.json'
    body='docs/design-engine/reconciled-pilot-bogie-detail/vehicle/installation.json.gz'
    cad='docs/design-engine/powered-bogie-detail/stock-case.json'
    parts=read(root/launch)['entities'];colours={'frame':'#94aab2','clevis':'#d99a3e','guidance':'#3c6575','fasteners':'#adb6bd','guards':'#aab9bf'}
    styles=[e['id']+':color='+colours[e['subassembly']]+(',opacity=0.12' if e['subassembly']=='guards' else '') for e in parts]
    # Native camera values deliberately use the documented mm/radian interface.
    yield _recipe(root,'launch-assembly','native',launch,native_file='docs/design-engine/launch-detail/assembly.sc',
        camera=dict(view='iso'),body_styles=styles,
        caption='Native SolidCraft launch-shuttle proposal:122 material regions, bores, open RHS, retained pin and guide wheels. Guards ghosted for visibility; no installed capability claim.')
    clevis_styles=[]
    for e in parts:
        group=e['subassembly'];opacity=1. if group=='clevis' else .12 if group=='frame' else .03
        clevis_styles.append(e['id']+':color='+colours[group]+',opacity='+str(opacity))
    yield _recipe(root,'launch-clevis','native',launch,native_file='docs/design-engine/launch-detail/assembly.sc',
        camera=dict(target=[240.,0.,320.],yaw=-.72,pitch=.40,distance=640.,fov=.70),body_styles=clevis_styles,
        caption='Native SolidCraft clevis, bored ears, pin and retainers. Surrounding parts are presentation-only ghosting; not a weld/contact/fatigue qualification.')
    stock=read(root/cad)
    yield _recipe(root,'bogie-cradle','native',cad,native_file='docs/design-engine/powered-bogie-detail/assembly.sc',
        camera=dict(view='iso'),body_styles=[e['id']+':color='+('#d99a3e' if any(k in e['id'] for k in ('motor-','torque-','retention')) else '#4e8298') for e in stock['entities']],
        caption='Native SolidCraft34-solid frame/cradle gross-stock subset. Actual supplier housings, mating interfaces and finished joints remain unknown; complete bogie fit is HOLD.')
    yield _recipe(root,'vehicle-car0','vehicle',body,camera=dict(direction=[1.2,-2.3,1.3],fill=.84),
        hide_roof_above_z_m=2.3,hide_near_wall_y_below_m=-.65,
        caption='One car from the located research body. Roof/near-side cutaway is display-only; exact stock and equipment envelopes have different materials. No physical installation approval.')
    yield _recipe(root,'civil-assembly','civil','docs/design-engine/reconciled-pilot-bogie-detail/civil-assembly.json',
        camera=dict(direction=[1.25,-1.7,1.0],fill=.82),
        caption='Located two-track precast civil proposal:segments, rails, bearings, piers and footing envelopes. Segment joints/reinforcement fit remain unverified; this is not the continuous bonded FEM beam.')


build_recipes=recipes


def validate(recipe,root=ROOT):
    if recipe.get('recipe_id')!=identity({k:v for k,v in recipe.items() if k!='recipe_id'}):raise ValueError('Gallery recipe seal differs')
    for name,want in recipe['source_sha256'].items():
        p=Path(name)
        if p.is_absolute() or '..' in p.parts or digest(Path(root)/p)!=want:raise ValueError('Gallery source changed: '+name)
    v=read(Path(root)/recipe['input_file'])
    if v.get('candidate_id',v.get('civil_candidate_id'))!=recipe['candidate_id']:raise ValueError('Mixed gallery physical candidate')
    if any(recipe.get(k) is not v for k,v in FLAGS.items()):raise ValueError('Presentation cannot grant approval')
    return True


def prepare(recipe,root,output,*,preview=False):
    validate(recipe,root);out=Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    write(out/'recipe.json',recipe);inputs=out/'inputs';inputs.mkdir()
    wanted=recipe['native_file'] if recipe['kind']=='native' else recipe['input_file']
    src=Path(root)/wanted;target=inputs/src.name;shutil.copyfile(src,target)
    if digest(target)!=recipe['source_sha256'][wanted]:raise ValueError('Copied render input differs')
    config=dict(recipe_id=recipe['recipe_id'],id=recipe['id'],kind=recipe['kind'],candidate_id=recipe['candidate_id'],
        input_path=str(target),input_sha256=digest(target),root=str(Path(root).resolve()),camera=recipe['camera'],
        width=1500 if preview else 3000,height=950 if preview else 1900,
        maximum_triangles=1000000,maximum_mesh_groups=668,hide_roof_above_z_m=recipe.get('hide_roof_above_z_m'),
        hide_near_wall_y_below_m=recipe.get('hide_near_wall_y_below_m'),**FLAGS)
    write(out/'scene.json',config);return out


def _limits(cpu_s,memory_mb):
    resource.setrlimit(resource.RLIMIT_CPU,(cpu_s,cpu_s+2));resource.setrlimit(resource.RLIMIT_AS,(memory_mb*1024**2,)*2)
    resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_FSIZE,(128*1024**2,)*2)


def run(recipe,root,output,*,preview=False):
    root=Path(root).resolve();out=prepare(recipe,root,output,preview=preview);scene=read(out/'scene.json')
    if recipe['kind']=='native':
        from engineering.design_search.craft_backends import native
        binary=native.executable('solidcraft');install=binary.parent.parent
        args=[str(binary),'snapshot','--in',scene['input_path'],'--out',str(out/'raw.png'),'--width',str(scene['width']),'--height',str(scene['height']),'--no-grid','--no-axes']
        camera=recipe['camera'];args+=['--view',camera['view']] if 'view' in camera else ['--camera',json.dumps(camera,separators=(',',':'))]
        for style in recipe['body_styles']:args+=['--body',style]
        command=['bwrap','--die-with-parent','--unshare-net','--ro-bind','/','/','--tmpfs','/home','--tmpfs','/root','--dev','/dev',
            '--ro-bind',str(install),str(install),'--ro-bind',str(out/'inputs'),str(out/'inputs'),'--bind',str(out),str(out),'--chdir',str(out),'--',*args]
        timeout,memory=120,2048
        isolation='Bubblewrap read-only host, network unshared, hidden home, private output bind; CPU renderer and per-process POSIX limits.'
    else:
        command=['flatpak','run','--filesystem='+str(root)+':ro','--filesystem='+str(out),'--command=blender','org.blender.Blender',
            '--background','--factory-startup','--threads','4','--python-exit-code','1','--python',str(root/OWNED[1]),'--','--scene',str(out/'scene.json'),'--output',str(out)]
        timeout,memory=600,3072
        isolation='Existing Flatpak Blender sandbox with explicit read-only source and private output filesystem grants; four threads and measured process RSS. No aggregate memory cgroup claimed.'
    env={**os.environ,'SOLIDCRAFT_GPU':'cpu','FIELDCRAFT_GPU':'cpu','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','RAYON_NUM_THREADS':'4'}
    command=['/usr/bin/time','-f','{"peak_rss_kib":%M,"user_s":%U,"system_s":%S,"exit":%x}','-o',str(out/'usage.json'),*command]
    write(out/'request.json',dict(recipe_id=recipe['recipe_id'],command=command,timeout_s=timeout,memory_target_mib=memory,
        source_sha256=recipe['source_sha256'],isolation=isolation,preview=preview,**FLAGS))
    start=time.monotonic();failure=None;code=None
    with (out/'stdout.log').open('wb') as stdout,(out/'stderr.log').open('wb') as stderr:
        try:
            p=subprocess.Popen(command,stdout=stdout,stderr=stderr,env=env,start_new_session=True,
                preexec_fn=(lambda:_limits(122,2048)) if recipe['kind']=='native' else None)
            try:code=p.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid,signal.SIGTERM)
                try:p.wait(timeout=3)
                except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
                failure='wall-time-budget'
        except Exception as e:failure=type(e).__name__+': '+str(e)
    unchanged=True
    try:validate(recipe,root)
    except ValueError:unchanged=False
    png=out/'raw.png';usage=read(out/'usage.json') if (out/'usage.json').exists() else None
    result=dict(schema='osr-engineering-gallery-cad-result/1',id=recipe['id'],candidate_id=recipe['candidate_id'],recipe_id=recipe['recipe_id'],
        execution='completed' if code==0 and png.is_file() and failure is None and unchanged else 'held',exit_code=code,failure=failure,
        source_unchanged=unchanged,wall_s=time.monotonic()-start,usage=usage,
        observed_memory_target_met=bool(usage and usage['peak_rss_kib']<=memory*1024),
        image_sha256=digest(png) if png.exists() else None,width=scene['width'],height=scene['height'],**FLAGS)
    if (out/'geometry.json').exists():result['geometry']=read(out/'geometry.json')
    result['evaluation_id']=identity(result);write(out/'result.json',result)
    if result['execution']!='completed':raise RuntimeError('Retained failed render: '+str(out))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('--output',type=Path,required=True);p.add_argument('--preview',action='store_true');a=p.parse_args()
    recipe=next(r for r in recipes() if r['id']==a.id);print(json.dumps(run(recipe,ROOT,a.output,preview=a.preview)))
