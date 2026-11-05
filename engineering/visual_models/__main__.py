"""Generate, export and render explicit engineering communication assemblies."""
import argparse,gzip,json,os,shutil,subprocess,sys,time
from pathlib import Path
from . import core

ROOT=Path(__file__).resolve().parents[2]
BASE='engineering/visual_models'


def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(core.encoded(value))


def definitions(output):
    output=Path(output)
    if output.exists():raise ValueError('Fresh definition output required')
    values,sources=core.collect(ROOT);output.mkdir(parents=True)
    for name,h in sources.items():
        path=output/'source-snapshot'/name;path.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,path)
        if core.digest(path)!=h:raise ValueError('Source changed during visual definition: '+name)
    for value in values:write(output/(value['id']+'.json'),value)
    m=dict(schema='osr-visual-definitions/1',source_sha256=sources,
        assemblies=[dict(id=v['id'],visual_study_id=v['visual_study_id'],parts=len(v['entities'])) for v in values],**core.FLAGS)
    m['definition_id']=core.identity(m);write(output/'manifest.json',m);return m


def selected(folder,assembly):
    folder=Path(folder);m=json.loads((folder/'manifest.json').read_bytes())
    if m['definition_id']!=core.identity({k:v for k,v in m.items() if k!='definition_id'}):raise ValueError('Definition identity differs')
    for name,h in m['source_sha256'].items():
        if core.digest(ROOT/name)!=h:raise ValueError('Visual model producer/data changed: '+name)
    if assembly not in [r['id'] for r in m['assemblies']]:raise ValueError('Unknown defined assembly')
    value=json.loads((folder/(assembly+'.json')).read_bytes());before=value['visual_study_id']
    if core.validate(value)['visual_study_id']!=before:raise ValueError('Visual definition changed')
    return value


def run(command,log,timeout):
    log=Path(log);log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('wb') as output:
        result=subprocess.run(command,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,timeout=timeout,
            env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','QT_QPA_PLATFORM':'offscreen'})
    if result.returncode:raise RuntimeError('Native worker failed; inspect '+str(log))


def render(folder,assembly,output,preview=False):
    value=selected(folder,assembly);output=Path(output).resolve()
    if output.exists():raise ValueError('Fresh rendering output required')
    worker=ROOT/BASE/'render_blender.py';before=core.digest(worker)
    args=['flatpak','run','--filesystem='+str(ROOT),'--command=blender','org.blender.Blender','--background','--factory-startup','--threads','4','--python-exit-code','1','--python',str(worker),'--','--scene',str(Path(folder).resolve()/(assembly+'.json')),'--output',str(output)]
    if preview:args.append('--preview')
    run(args,output.with_suffix('.log'),600)
    if core.digest(worker)!=before:raise ValueError('Renderer changed during execution; preserve draft output')
    receipt=json.loads((output/'render.json').read_bytes())
    if receipt['worker_source_sha256']!=before:raise ValueError('Renderer receipt source differs')
    from .compose import plate
    result=plate(value,output,output/(assembly+'.webp'));result['assembly']=assembly
    return result


def cad(folder,assembly,output):
    selected(folder,assembly);output=Path(output).resolve()
    if output.exists():raise ValueError('Fresh native CAD output required')
    script=output.with_suffix('.launch.py');script.parent.mkdir(parents=True,exist_ok=True)
    text='SCENE_PATH='+repr(str(Path(folder).resolve()/(assembly+'.json')))+'\nOUTPUT_PATH='+repr(str(output))+'\n'
    worker=ROOT/BASE/'cad_freecad.py'
    text+='scope={"SCENE_PATH":SCENE_PATH,"OUTPUT_PATH":OUTPUT_PATH,"__name__":"osr_cad_worker","__file__":'+repr(str(worker))+'}\n'
    text+='exec(compile(open('+repr(str(worker))+').read(),'+repr(str(worker))+',"exec"),scope)\nscope["main"]()\n'
    script.write_text(text)
    args=['flatpak','run','--filesystem='+str(ROOT),'--env=QT_QPA_PLATFORM=offscreen','--env=OMP_NUM_THREADS=1','--command=FreeCADCmd','org.freecad.FreeCAD',str(script)]
    before=core.digest(worker)
    run(args,output.with_suffix('.log'),600)
    if core.digest(worker)!=before:raise ValueError('CAD worker changed during execution; preserve draft output')
    if not (output/'cad.json').is_file():raise RuntimeError('No verified native CAD receipt; inspect '+str(output.with_suffix('.log')))
    receipt=json.loads((output/'cad.json').read_bytes())
    if receipt['worker_source_sha256']!=before:raise ValueError('Native CAD receipt source differs')
    return receipt


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('definitions','render','cad','compose'))
    p.add_argument('--definitions',type=Path);p.add_argument('--assembly');p.add_argument('--output',type=Path,required=True);p.add_argument('--render-dir',type=Path);p.add_argument('--preview',action='store_true');a=p.parse_args()
    if a.action=='definitions':v=definitions(a.output)
    else:
        if not a.definitions or not a.assembly:p.error('--definitions and --assembly required')
        if a.action=='render':v=render(a.definitions,a.assembly,a.output,a.preview)
        elif a.action=='cad':v=cad(a.definitions,a.assembly,a.output)
        else:
            from .compose import plate
            v=plate(selected(a.definitions,a.assembly),a.render_dir,a.output)
    print(json.dumps(v,sort_keys=True))

if __name__=='__main__':main()
