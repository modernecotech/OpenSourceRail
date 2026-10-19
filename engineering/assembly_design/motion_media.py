"""Kinematic fixture preview from native triangles and declared operation groups."""
from pathlib import Path
import math
import shutil
import subprocess
import tempfile

import numpy as np
from engineering.twin_workflow import core


def cassette(candidate,mesh_path,output):
    binary=shutil.which('ffmpeg');probe=shutil.which('ffprobe')
    if not binary or not probe:return dict(state='hold',reason='ffmpeg/ffprobe unavailable')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    mesh=core.read(mesh_path,maximum=60_000_000);groups=candidate['metadata']['ownership_groups']
    az,el=np.deg2rad([22.,28.]);right=np.array([math.cos(az),math.sin(az),0.])
    forward=np.array([-math.sin(az),math.cos(az),0.]);up=-math.sin(el)*forward+np.array([0.,0.,math.cos(el)])
    camera=math.cos(el)*forward+np.array([0.,0.,math.sin(el)])
    visible=[];limits=[]
    for part in mesh['parts']:
        group=groups[part['id']]
        if group not in {'cassette-moving','host-fixed'}:continue
        vertices=np.asarray(part['vertices']);faces=np.asarray(part['faces'])
        triangles=vertices[faces];moving=group=='cassette-moving';visible.append((part['id'],triangles,moving))
        for offset in ((0.,-1.3) if moving else (0.,)):
            shifted=vertices+np.array([offset,0.,0.]);limits.extend(np.stack([shifted@right,shifted@up],axis=1))
    limits=np.asarray(limits);lo=limits.min(axis=0)-.08;hi=limits.max(axis=0)+.08
    frames=25;output=Path(output)
    with tempfile.TemporaryDirectory(prefix='.motion-',dir=output) as temporary:
        temporary=Path(temporary)
        for frame in range(frames):
            phase=frame/(frames-1);progress=1-abs(2*phase-1);offset=-1.3*(1-progress)
            triangles=[];depth=[];colors=[]
            for identity,points,moving in visible:
                shifted=points+np.array([offset if moving else 0.,0.,0.])
                triangles.extend(np.stack([shifted@right,shifted@up],axis=2));depth.extend(np.mean(shifted@camera,axis=1))
                colors.extend(['#6395ad' if moving else '#d19450']*len(points))
            order=np.argsort(depth);fig,ax=plt.subplots(figsize=(10,4.5),dpi=100)
            ax.add_collection(PolyCollection(np.asarray(triangles)[order],facecolors=np.asarray(colors)[order],edgecolors='none'))
            ax.set(xlim=(lo[0],hi[0]),ylim=(lo[1],hi[1]),aspect='equal');ax.axis('off')
            fig.suptitle('Native cassette / proposed fixture — rigid insertion and withdrawal',fontsize=13)
            fig.text(.04,.08,'Declared detached cover, retention and service groups omitted for this operation state.',fontsize=9)
            fig.text(.04,.035,'Kinematic geometry preview only; no forces, flexible wiring, human access or vehicle qualification.',fontsize=9)
            fig.savefig(temporary/f'{frame:03d}.png');plt.close(fig)
        subprocess.run([binary,'-loglevel','error','-y','-framerate','6','-i',str(temporary/'%03d.png'),
            '-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',str(output/'fixture-motion.mp4')],check=True,timeout=90,capture_output=True)
    call=subprocess.run([probe,'-v','error','-select_streams','v:0','-show_entries','stream=codec_name,nb_frames',
        '-of','json',str(output/'fixture-motion.mp4')],check=True,capture_output=True,text=True,timeout=20)
    import json
    decoded=json.loads(call.stdout)['streams'][0]
    if decoded['codec_name']!='h264' or int(decoded['nb_frames'])!=frames:raise ValueError('motion preview video did not decode')
    return dict(state='executed',candidate_revision=candidate['revision'],native_mesh_sha256=core.sha(mesh_path),
        frames=frames,frames_per_second=6,visible_part_ids=[r[0] for r in visible],travel_m=1.3,
        ffmpeg_sha256=core.sha(Path(binary).resolve()),ffprobe_sha256=core.sha(Path(probe).resolve()),
        decoded_video=decoded,scope='Actual native triangles translated through the declared rigid host fixture path; no dynamic/contact/ergonomic or actual vehicle verification')
