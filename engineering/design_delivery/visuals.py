"""Retained native geometry and receipt-bound sequence illustrations, not dynamics."""
from pathlib import Path
from hashlib import sha256
from html import escape
import gzip
import json
import shutil
import subprocess
import tempfile


def export_mesh(source,destination):
    import FreeCAD as App
    doc=App.openDocument(str(source));parts=[];triangles=0
    try:
        for obj in doc.Objects:
            identity=getattr(obj,'PhysicalPartId',getattr(obj,'DesignId',None))
            if identity is None:continue
            vertices,faces=obj.Shape.tessellate(1.0);triangles+=len(faces)
            if triangles>250000:raise ValueError('presentation triangle budget exceeded')
            parts.append(dict(id=identity,unit_id=getattr(obj,'ManufacturingUnitId',None),
                vertices=[[p.x/1000,p.y/1000,p.z/1000] for p in vertices],faces=[list(f) for f in faces]))
        if not parts:raise ValueError('native model has no identified parts')
        Path(destination).write_text(json.dumps(dict(parts=parts,triangles=triangles)))
    finally:App.closeDocument(doc.Name)


def sequence(choice,model):
    """Take real event order; geometry inspection is used if no assembly DAG exists."""
    from engineering.twin_workflow import core
    from engineering.continuous_design import construction_stage,operation_graph
    folder=Path(choice['row']['folder'])/'output';ids={p['id'] for p in model['parts']}
    if choice['kind']=='civil-kit-study':
        kit=core.read(folder/'civil-kit.json',maximum=30_000_000);schedule=core.read(folder/'delivery-schedule.json',maximum=20_000_000)
        check=construction_stage.verify_schedule(kit,core.read(folder/'delivery-tasks.json'),schedule)
        if not all(check['checks'].values()) or check.get('scenario_holds'):raise ValueError('construction sequence cannot pass its own stage checks')
        units={u['id']:u for u in kit['units']};events=[]
        for row in schedule['tasks']:
            suffix='/place-and-temporary-lock' if row['id'].endswith('/place-and-temporary-lock') else '/site-cast'
            if not row['id'].endswith(suffix):continue
            uid=row['id'].removesuffix(suffix);u=units[uid]
            events.append(dict(event=row['id'],unit=uid,time_h=row['end_h'],parts=u['physical_part_ids']))
        events.sort(key=lambda r:(r['time_h'],r['event']))
        kind='construction-sequence';basis='delivery-schedule.json; placement at scenario completion times'
    elif (folder/'operation-graph.json').exists():
        graph=core.read(folder/'operation-graph.json');replay=operation_graph.evaluate(graph)
        if not all(replay['checks'].values()):raise ValueError('assembly replay fails')
        by={r['id']:r for r in graph['operations']}
        events=[dict(event=r['operation'],parts=by[r['operation']]['parts']) for r in replay['trace'] if r['kind']=='install']
        kind='assembly-sequence';basis='operation-graph.json; dependency-order replay, no measured cycle time'
    else:
        events=[dict(event='geometry-inspection',parts=sorted(ids))]
        kind='geometry-inspection';basis='No evaluated detailed assembly sequence exists for this candidate'
    shown=set()
    for event in events:
        if not set(event['parts'])<=ids:raise ValueError('sequence references unrendered geometry')
        shown.update(event['parts']);event['visible_parts']=sorted(shown)
    if shown!=ids:raise ValueError('sequence omits native parts')
    return dict(kind=kind,basis=basis,events=events,
        motion_path_verified=False,collision_simulation=False,connection_resistance_verified=False,
        scope='Native solids appear at their final positions in evaluated event order. Temporary plant, movement, wet concrete and QA are not visually simulated; milestones compress planning time.')


def frame(mesh,visible,destination,title,caption,angle=24):
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import to_rgb
    # Same projection and bounds for every milestone: no camera rescaling.
    az,el=np.deg2rad([angle,30]);right=np.array([np.cos(az),np.sin(az),0]);forward=np.array([-np.sin(az),np.cos(az),0])
    up=-np.sin(el)*forward+np.array([0,0,np.cos(el)]);camera=np.cos(el)*forward+np.array([0,0,np.sin(el)])
    allpoints=np.concatenate([np.array(p['vertices']) for p in mesh['parts']]);bounds=np.stack([allpoints@right,allpoints@up],axis=1)
    lo,hi=bounds.min(axis=0),bounds.max(axis=0);pad=max(hi-lo)*.05
    polygons=[];colors=[];depth=[]
    for part in mesh['parts']:
        if part['id'] not in visible:continue
        points=np.array(part['vertices']);faces=points[np.array(part['faces'])]
        normals=np.cross(faces[:,1]-faces[:,0],faces[:,2]-faces[:,0]);normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-12)
        shades=.6+.4*np.abs(normals@np.array([-.3,-.4,.866]));color='#567b91' if 'cap' in part['id'].lower() else '#a0b7c5'
        polygons.extend(np.stack([faces@right,faces@up],axis=2));depth.extend(faces@camera);colors.extend(shades[:,None]*np.array(to_rgb(color)))
    fig=plt.figure(figsize=(9.6,5.4),dpi=100,facecolor='#f5f7fa');ax=fig.add_axes([.04,.22,.92,.56]);ax.axis('off')
    if polygons:
        import runpy
        from engineering.twin_workflow import core
        rasterize=runpy.run_path(str(core.ROOT/'tools/automation/design-progress.py'))['rasterize']
        # Degenerate non-rendering anchors keep the full-model camera framing
        # fixed across milestones. Opaque z-buffering hides embedded solids.
        polygons.extend([[lo.tolist()]*3,[hi.tolist()]*3]);depth.extend([[-1e12]*3,[-1e12]*3]);colors.extend([[1.,1.,1.],[1.,1.,1.]])
        ax.imshow(rasterize(polygons,depth,colors,width=960,height=360),interpolation='lanczos')
    fig.text(.04,.92,title[:100],fontsize=14,color='#18384c');fig.text(.04,.84,caption[:120],fontsize=9)
    fig.text(.04,.12,'Provisional native geometry | sequence illustration; no motion, collision or strength proof',fontsize=9)
    fig.text(.04,.06,'Detailed reinforcement, connections, services and physical acceptance remain open.',fontsize=9)
    fig.savefig(destination);plt.close(fig)


def generate(choice,output):
    from engineering.twin_workflow import core
    confirmation=Path(choice['confirmation']['folder'])/'output';common=choice['kind']!='mechanical-detail'
    model_path=confirmation/('physical-contract.json' if common else 'model-definition.json')
    cad=confirmation/'cad'/('candidate.FCStd' if common else 'model.FCStd');native=core.read(confirmation/'cad/native-cad.json')
    if native['input_sha256']!=core.sha(model_path):raise ValueError('native geometry belongs to another definition')
    model=core.read(model_path,maximum=30_000_000);plan=sequence(choice,model);core.write(output/'sequence.json',plan)
    before=core.sha(cad);shutil.copyfile(cad,output/'model.FCStd')
    # Neutral interchange remains compact and tracked despite raw STEP ignore rules.
    step=next((p for p in sorted((confirmation/'cad').glob('*.step'))),None)
    if step is None:raise ValueError('native STEP interchange is absent')
    (output/'model.step.gz').write_bytes(gzip.compress(step.read_bytes(),mtime=0))
    with tempfile.TemporaryDirectory(prefix='.visual-',dir=output) as temp:
        temp=Path(temp);script=temp/'export.py';mesh_path=temp/'mesh.json'
        script.write_text('import runpy\nrunpy.run_path('+repr(str(Path(__file__).resolve()))+')["export_mesh"]('+repr(str(cad))+','+repr(str(mesh_path))+')\n')
        binary=shutil.which('FreeCADCmd') or shutil.which('freecadcmd')
        command=[binary] if binary else ['flatpak','run','--filesystem='+str(cad.parent),'--filesystem='+str(temp),'--filesystem='+str(Path(__file__).parent),'--command=FreeCADCmd','org.freecad.FreeCAD']
        call=subprocess.run([*command,str(script)],capture_output=True,text=True,timeout=120)
        if call.returncode:raise ValueError('native mesh export failed: '+call.stderr[-500:])
        mesh=core.read(mesh_path,maximum=60_000_000)
        if {p['id'] for p in mesh['parts']}!={p['id'] for p in model['parts']}:raise ValueError('native presentation identity differs')
        if any(p.get('unit_id')!=next(q.get('manufacturing_unit_id') for q in model['parts'] if q['id']==p['id']) for p in mesh['parts']):raise ValueError('native unit identity differs')
        events=plan['events'];indices=sorted({round(i*(len(events)-1)/9) for i in range(10)})
        if plan['kind']=='geometry-inspection':indices=[0]*10
        frames=[]
        for i,index in enumerate(indices):
            event=events[index];name=f'{i:03d}.png';path=temp/name
            frame(mesh,event['visible_parts'],path,choice['group'],event['event']+(' | scenario %.2f h'%event['time_h'] if 'time_h' in event else ''),angle=24+i*24 if plan['kind']=='geometry-inspection' else 24)
            frames.append(name)
        shutil.copyfile(temp/frames[-1],output/'overview.png')
        # Concatenation repeats retained milestone frames into a short H.264 review.
        concat=temp/'frames.txt';duration=8/len(frames)
        concat.write_text(''.join("file '"+name+"'\nduration "+str(duration)+'\n' for name in frames)+"file '"+frames[-1]+"'\n")
        video=output/('inspection.mp4' if plan['kind']=='geometry-inspection' else 'assembly.mp4');command=['ffmpeg','-nostdin','-loglevel','error','-y','-f','concat','-safe','1','-i',str(concat),'-t','8','-r','12','-c:v','libx264','-crf','25','-pix_fmt','yuv420p','-movflags','+faststart',str(video)]
        subprocess.run(command,check=True,capture_output=True,timeout=120)
        probe=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,width,height','-of','json',str(video)],check=True,capture_output=True,text=True,timeout=20)
        info=json.loads(probe.stdout)
        if not 7.5<=float(info['format']['duration'])<=8.5:raise ValueError('short video duration differs')
    if before!=core.sha(cad):raise ValueError('retained CAD was changed while rendering')
    return dict(kind=plan['kind'],cad_sha256=before,native_definition_sha256=core.sha(model_path),
        sequence_sha256=core.sha(output/'sequence.json'),image='overview.png',video=video.name,video_probe=info,
        physical_release=False,motion_path_verified=False)


def report(output,selected,ledger):
    from engineering.twin_workflow import core
    h=lambda value:escape(str(value),quote=True)
    rows=['<!doctype html><html lang="en"><meta charset="utf-8"><title>OpenSourceRail design delivery</title>',
        '<style>body{font:17px system-ui;max-width:1100px;margin:2rem auto;padding:1rem;color:#18384c}img,video{width:100%}article{border-bottom:1px solid #ccc;padding:1rem}pre{white-space:pre-wrap}</style>',
        '<h1>OpenSourceRail — provisional design and simulation delivery</h1>',
        '<p>Publication integrity can pass while engineering completion remains open. No manufacturing or physical release is claimed.</p>',
        '<p>'+str(ledger['required_components'])+' authoritative items and '+str(ledger['required_packages'])+' work packages are tracked; '+str(ledger['accepted_components'])+' items have accepted completion evidence in this ledger.</p>',
        '<p><a href="completion.json">Full completion gates</a> | <a href="tests.log">Executed tests</a> | <a href="qualification.json">Test/source receipt</a> | <a href="evidence.tar.gz">Portable raw evidence</a> | <a href="manifest.json">Checksums</a></p>']
    for c in selected:
        base='models/'+c['id']+'/'
        rows+=['<article><h2>'+h(c['group'])+'</h2><p>Exact candidate '+h(c['key'])+'</p><p>'+h(c['scope'])+'</p>',
            '<p><a href="'+base+'summary.json">Metrics and verification</a></p>']
        if 'visualisation' in c:
            rows+=['<p>'+h(c['visualisation']['kind'])+'; final-position sequence illustration, not a motion or collision simulation.</p>',
                '<img alt="Retained candidate geometry" src="'+base+'overview.png">',
                '<video controls preload="metadata" poster="'+base+'overview.png" src="'+base+c['visualisation']['video']+'"></video>',
                '<p><a href="'+base+'model.FCStd">Native FreeCAD</a> | <a href="'+base+'model.step.gz">Compressed STEP</a> | <a href="'+base+'sequence.json">Sequence events</a></p>']
        elif c['kind'].startswith('software-'):
            rows+=['<img alt="Retained executable test checks" src="'+base+'tests.png">']
        rows+=['<p><a href="'+base+'result.json">Full retained result</a></p>']
        rows+=['<details><summary>Outstanding evidence</summary><pre>'+h(json.dumps(c['outstanding'][:12],indent=2))+'</pre></details></article>']
    rows+=['</html>'];(output/'index.html').write_text('\n'.join(rows))
    text='# Provisional continuous design delivery\n\nOpen [the illustrated review](index.html) for CAD pictures and short videos.\n\nThis package preserves selected source-bound research results, tests, native CAD, manufacturing/QA data and sequence visualisations. Full component and system completion remains open in [completion.json](completion.json); no physical or manufacturing release is claimed.\n\nVerify offline from the repository root:\n\n```bash\ntools/automation/osr-python tools/automation/design-publish.py verify --package docs/design-engine/continuous-delivery --media\n```\n\nThe portable evidence archive contains original receipts and all their retained files. Archive integrity is checked without rerunning physics. Publication-time eligibility is a snapshot, not a continuing acceptance claim. Assembly videos reveal retained solids at their final positions following evaluated operation/schedule events; they do not prove insertion paths, collision freedom or connection resistance. The underframe uses a camera inspection tour when no detailed assembly graph is present.\n'
    for c in selected:
        if 'visualisation' not in c:continue
        base='models/'+c['id']+'/'
        text+='\n## '+c['group']+'\n\n![Retained native geometry]('+base+'overview.png)\n\n[Eight-second '+c['visualisation']['kind']+' video]('+base+c['visualisation']['video']+') · [Native CAD]('+base+'model.FCStd) · [Metrics and open evidence]('+base+'summary.json)\n'
    (output/'README.md').write_text(text)


def software(choice,output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    result=choice['result'];replay=result.get('replay',[])[:24]
    labels=[r['id'] for r in replay] if replay else list(result['checks'])[:24]
    values=[int(r['passed']) for r in replay] if replay else [int(result['checks'][key] is True) for key in labels]
    fig,ax=plt.subplots(figsize=(10,6));ax.barh(labels,values,color=['#24798c' if x else '#c15243' for x in values]);ax.invert_yaxis();ax.set_xlim(0,1.1)
    ax.set_xlabel('Retained offline check passed (1) / failed (0)');ax.set_title(choice['kind']+' — executed research checks')
    fig.text(.1,.015,'Exact generated source and raw results are included; physical network, target timing and SIL/HIL remain open.',fontsize=9)
    fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(output/'tests.png',dpi=110);plt.close(fig)
