"""Render retained native tessellations; visibility sequences are not motion simulation."""
from hashlib import sha256
from pathlib import Path
import gzip
import json
import subprocess
import tempfile


def native_views(folder):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    import numpy as np
    folder=Path(folder)
    mesh=json.loads(gzip.decompress((folder/'native-mesh.json.gz').read_bytes()))
    definition=json.loads((folder/'definition.json').read_text())
    parts=mesh['parts'];byid={p['id']:p for p in parts}
    colours={'concrete':'#7c8996','steel':'#477e98','aluminium':'#c0cbd3','ferrite':'#dd7558','winding-envelope':'#dab14a','gfrp':'#16998c','core-80':'#e5c76b','core-100':'#c5a249','bond-surface':'#b18895'}
    def image(ids,path,caption,detail=False):
        fig=plt.figure(figsize=(12,6.75),dpi=100,facecolor='#f3f6f9');ax=fig.add_subplot(projection='3d')
        selected=[byid[key] for key in ids];points=[]
        for p in selected:
            vertices=np.array(p['vertices_m']);points.extend(vertices)
            ax.add_collection3d(Poly3DCollection(vertices[np.array(p['triangles'])],facecolors=colours[p['material']],edgecolors='#203b4e',linewidths=.08,alpha=1))
        # Fixed full assembly framing throughout a visibility sequence.
        extent=np.array(points if detail else [v for p in parts for v in p['vertices_m']]);lo=extent.min(axis=0);hi=extent.max(axis=0)
        mid=(lo+hi)/2;span=np.maximum(hi-lo,.1)
        for setter,i in [(ax.set_xlim,0),(ax.set_ylim,1),(ax.set_zlim,2)]:setter(mid[i]-span[i]*.53,mid[i]+span[i]*.53)
        ax.set_box_aspect(span.copy(),zoom=.95);ax.view_init(elev=25,azim=-65 if not detail else -55)
        ax.set_axis_off();fig.text(.04,.08,f'Assembly framing extent: {span[0]:.3f} × {span[1]:.3f} × {span[2]:.3f} m; equal physical scale',fontsize=10)
        fig.suptitle(caption,fontsize=14);fig.text(.04,.03,'Provisional native material regions. Assembly visibility only; no motion, lifting, collision or structural acceptance.',fontsize=10)
        fig.subplots_adjust(left=0,right=1,bottom=.08,top=.92)
        fig.savefig(path,metadata={'Software':'OpenSourceRail native geometry renderer'});plt.close(fig)
    overview=list(byid)
    if definition['id'].endswith('INTERFACE'):
        overview=[p['id'] for p in parts if p['material']!='concrete' and not p['id'].startswith('beam/') and p['id']!='frame/floor-material-region']
    image(overview,folder/'overview.png',definition['id']+' — native cutaway (beam and floor hidden)' if definition['id'].endswith('INTERFACE') else definition['id']+' — actual native tessellation')
    if definition['id'].endswith('INTERFACE'):
        ids=[p['id'] for p in parts if p['id'].startswith('cartridge/1/05/')]
        image(ids,folder/'cartridge-detail.png','Recessed retainer cartridge — supplier/process qualification remains open',detail=True)
    stages=definition['construction_stages'];visible=[];frames=[]
    with tempfile.TemporaryDirectory(prefix='osr-native-sequence-') as temporary:
        for stage in stages:
            chunks=[stage['parts']]
            if stage['id']=='cartridges':
                chunks=[m['part_ids'] for m in definition['modules']]
            for chunk in chunks:
                visible.extend(chunk);frame=Path(temporary)/f'{len(frames):04d}.png'
                image(visible,frame,'Assembly visibility: '+stage['id']);frames.append(frame)
        subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','3','-i',str(Path(temporary)/'%04d.png'),
                        '-c:v','libx264','-pix_fmt','yuv420p','-vf','pad=ceil(iw/2)*2:ceil(ih/2)*2,fps=24','-movflags','+faststart',str(folder/'assembly-visibility.mp4')],check=True,timeout=120)
    names=['overview.png','assembly-visibility.mp4']+(['cartridge-detail.png'] if definition['id'].endswith('INTERFACE') else [])
    receipt=dict(schema='osr-native-visual-evidence/1',mesh_sha256=sha256((folder/'native-mesh.json.gz').read_bytes()).hexdigest(),
        definition_sha256=sha256((folder/'definition.json').read_bytes()).hexdigest(),renderer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        stages=stages,frame_count=len(frames),source_frames_per_second=3,
        scope='Final-position part visibility sequence from native tessellation; no movement trajectory or construction safety verification',
        physical_release=False,files_sha256={name:sha256((folder/name).read_bytes()).hexdigest() for name in names})
    (folder/'visual-receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    return receipt


def field_image(study):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from io import BytesIO
    r=study['mesh_refinement'][1];g=r['grid'];x=np.array(g['x_m']);y=np.array(g['y_m']);bx=np.array(g['b_horizontal_t']);by=np.array(g['b_vertical_t'])
    fig,ax=plt.subplots(figsize=(10,6),dpi=110)
    image=ax.pcolormesh(x,y,np.hypot(bx,by),shading='auto',cmap='magma');ax.contour(x,y,g['potential_wb_m'],levels=24,colors='white',linewidths=.35)
    fig.colorbar(image,ax=ax,label='|B| / T (assumed material law)');ax.set(xlabel='Horizontal coordinate / m',ylabel='Vertical coordinate / m',aspect='equal',title='2D magnetic coupon: equation study, not vehicle force qualification')
    fig.text(.05,.02,'Force mesh is unconverged; supplier B–H / recoil data, 3D losses and measured validation remain open.',fontsize=9)
    buffer=BytesIO();fig.savefig(buffer,metadata={'Software':'OpenSourceRail field study'});plt.close(fig);return buffer.getvalue()
