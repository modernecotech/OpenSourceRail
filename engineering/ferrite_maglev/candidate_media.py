"""Candidate-only deterministic native-triangle views and semantic media oracle.

The viewport contains only native triangles at fixed orthographic scale. Text,
font rasterization and encoder bytes are outside the semantic comparison.
Visibility stages show parts at final coordinates, not an assembly trajectory.
"""
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, binary_erosion

WIDTH,HEIGHT=1200,720
VIEWPORT=(36,92,1164,636)
BACKGROUND=(241,245,249)
FPS=24
STAGE_SECONDS=1
PALETTE={'steel':(71,126,152),'aluminium':(192,203,211),'ferrite':(221,117,88),
         'winding-envelope':(218,177,74),'gfrp':(22,153,140)}
SCHEMA='osr-candidate-native-semantic-views/1'


def sha(path):return sha256(Path(path).read_bytes()).hexdigest()


def _projection(mesh):
    az=np.deg2rad(-58.);el=np.deg2rad(25.)
    normal=np.array([np.cos(el)*np.cos(az),np.cos(el)*np.sin(az),np.sin(el)])
    right=np.array([-np.sin(az),np.cos(az),0.])
    up=np.cross(normal,right)
    basis=np.array([right,up,normal])
    points=np.concatenate([np.asarray(p['vertices_m'],float) for p in mesh['parts']])@basis.T
    low=points[:,:2].min(0);high=points[:,:2].max(0);span=high-low
    if np.any(span<=0):raise ValueError('nonempty three-dimensional native view required')
    x0,y0,x1,y1=VIEWPORT;scale=.90*min((x1-x0)/span[0],(y1-y0)/span[1])
    centre=(low+high)/2
    return basis,centre,scale


def render_viewport(definition,mesh,visible_ids):
    """Opaque, depth-tested triangles; no matplotlib/viewer-dependent framing."""
    by={p['id']:p for p in mesh['parts']};visible=list(visible_ids)
    if len(set(visible))!=len(visible) or not visible or not set(visible)<=set(by):raise ValueError('exact nonempty visible native part set required')
    basis,centre,scale=_projection(mesh);x0,y0,x1,y1=VIEWPORT;w=x1-x0;h=y1-y0
    pixels=np.full((h,w,3),BACKGROUND,np.uint8);depth=np.full((h,w),-np.inf)
    light=np.array([.3,-.4,.8660254038]);light/=np.linalg.norm(light)
    for identity in visible:
        part=by[identity];vertices=np.asarray(part['vertices_m'],float);triangles=np.asarray(part['triangles'],int);projected=vertices@basis.T
        projected[:,:2]=(projected[:,:2]-centre)*scale
        projected[:,0]+=w/2;projected[:,1]=h/2-projected[:,1]
        base=np.array(PALETTE[part['material']],float)
        for indices in triangles:
            tri=projected[indices];xmin=max(0,int(np.floor(tri[:,0].min())));xmax=min(w-1,int(np.ceil(tri[:,0].max())));ymin=max(0,int(np.floor(tri[:,1].min())));ymax=min(h-1,int(np.ceil(tri[:,1].max())))
            if xmax<xmin or ymax<ymin:continue
            a,b,c=tri;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(den)<1e-12:continue
            yy,xx=np.mgrid[ymin:ymax+1,xmin:xmax+1];xx=xx+.5;yy=yy+.5
            wa=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
            wb=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;wc=1-wa-wb
            z=wa*a[2]+wb*b[2]+wc*c[2];target=depth[ymin:ymax+1,xmin:xmax+1]
            mask=(wa>=-1e-10)&(wb>=-1e-10)&(wc>=-1e-10)&(z>target+1e-12)
            if not mask.any():continue
            world=vertices[indices];n=np.cross(world[1]-world[0],world[2]-world[0]);length=np.linalg.norm(n)
            if length<=1e-15:raise ValueError('nondegenerate native triangles required for view')
            intensity=.62+.38*abs(float(np.dot(n/length,light)));colour=np.rint(base*intensity).astype(np.uint8)
            pixels[ymin:ymax+1,xmin:xmax+1][mask]=colour;target[mask]=z[mask]
    if np.count_nonzero(np.isfinite(depth))<100:raise ValueError('native view has no meaningful geometry footprint')
    return pixels


def _canvas(view,caption):
    canvas=Image.new('RGB',(WIDTH,HEIGHT),BACKGROUND);canvas.paste(Image.fromarray(view),(VIEWPORT[0],VIEWPORT[1]));draw=ImageDraw.Draw(canvas)
    draw.text((36,22),caption,fill=(21,37,54));draw.text((36,48),'Actual native triangles; fixed orthographic framing and equal physical scale.',fill=(21,37,54))
    draw.text((36,662),'Final-position visibility only. No motion, collision, lifting, manufacture or physical acceptance.',fill=(21,37,54))
    return canvas


def _stages(definition):
    seen=[];out=[]
    stages=definition['construction_stages']
    if not 1<=len(stages)<=8:raise ValueError('bounded nonempty native visibility stages required')
    for stage in stages:
        if not stage['parts'] or set(stage['parts'])&set(seen):raise ValueError('disjoint nonempty visibility stage required')
        seen.extend(stage['parts']);out.append((stage['id'],list(seen)))
    if set(seen)!={p['id'] for p in definition['parts']}:raise ValueError('visibility sequence must cover exact native inventory')
    return out


def native_views(folder):
    import gzip
    folder=Path(folder);definition=json.loads((folder/'definition.json').read_bytes());mesh=json.loads(gzip.decompress((folder/'native-mesh.json.gz').read_bytes()))
    stages=_stages(definition);allids=[p['id'] for p in definition['parts']];poster=render_viewport(definition,mesh,allids)
    _canvas(poster,definition['id']+' / actual native module').save(folder/'overview.png')
    with tempfile.TemporaryDirectory(prefix='osr-candidate-native-views-') as temporary:
        for i,(identity,visible) in enumerate(stages):
            view=render_viewport(definition,mesh,visible);_canvas(view,'Final-position part visibility / '+identity).save(Path(temporary)/f'{i:03d}.png')
        subprocess.run(['ffmpeg','-y','-v','error','-framerate','1','-i',str(Path(temporary)/'%03d.png'),'-vf',f'fps={FPS}','-c:v','libx264','-crf','12','-pix_fmt','yuv420p','-movflags','+faststart',str(folder/'assembly-visibility.mp4')],check=True,timeout=120)
    receipt=dict(schema=SCHEMA,definition_sha256=sha(folder/'definition.json'),mesh_sha256=sha(folder/'native-mesh.json.gz'),renderer_sha256=sha(Path(__file__)),stages=definition['construction_stages'],frame_count=len(stages),source_frames_per_second=1,
        viewport=list(VIEWPORT),image_dimensions=[WIDTH,HEIGHT],poster_viewport_sha256=sha256(poster.tobytes()).hexdigest(),
        scope='Depth-tested actual native triangles. Semantic checks cover geometry viewport/masks, not text/font/encoder bytes. Final-position visibility, not motion/collision verification.',physical_release=False,
        files_sha256={name:sha(folder/name) for name in ('overview.png','assembly-visibility.mp4')})
    (folder/'visual-receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    return receipt


def _frame_oracle(expected):
    bg=np.array(BACKGROUND,np.int16);image=expected.astype(np.int16);mask=np.max(abs(image-bg),axis=2)>30
    inside=binary_erosion(mask,iterations=2);outside=~binary_dilation(mask,iterations=2)
    return bg,image,mask,inside,outside


def _semantic_frame(actual,expected,oracle=None):
    if actual.shape!=expected.shape:raise ValueError('candidate video viewport dimensions differ')
    bg,image,mask,inside,outside=_frame_oracle(expected) if oracle is None else oracle
    observed=np.max(abs(actual.astype(np.int16)-bg),axis=2)>30
    if np.count_nonzero(inside)<100:raise ValueError('meaningful candidate video footprint required')
    missing=np.count_nonzero(inside&~observed)/np.count_nonzero(inside)
    excess=np.count_nonzero(outside&observed)/max(1,np.count_nonzero(mask))
    # Lossy420 compression perturbs edges; object interiors must retain actual
    # material/shading colour, so same-silhouette wrong-stage substitution fails.
    difference=np.max(abs(actual.astype(np.int16)-image),axis=2)
    bad_colour=np.count_nonzero(inside&(difference>24))/np.count_nonzero(inside)
    if missing>.002 or excess>.002 or bad_colour>.02:raise ValueError('candidate video does not depict its actual native visibility stage')
    return dict(missing_fraction=missing,excess_fraction=excess,interior_colour_error_fraction=bad_colour)


def verify_views(folder,definition,mesh):
    """Re-render source geometry and inspect actual bounded decoded video frames."""
    from . import station_native
    folder=Path(folder);receipt=json.loads((folder/'visual-receipt.json').read_bytes());stages=_stages(definition)
    if receipt.get('schema')!=SCHEMA or receipt.get('viewport')!=list(VIEWPORT) or receipt.get('image_dimensions')!=[WIDTH,HEIGHT] or receipt.get('frame_count')!=len(stages) or receipt.get('source_frames_per_second')!=1:raise ValueError('candidate semantic view contract differs')
    if receipt.get('definition_sha256')!=sha(folder/'definition.json') or receipt.get('mesh_sha256')!=sha(folder/'native-mesh.json.gz') or receipt.get('renderer_sha256')!=sha(Path(__file__)) or receipt.get('stages')!=definition['construction_stages'] or receipt.get('physical_release')is not False:raise ValueError('candidate semantic media provenance differs')
    if set(receipt.get('files_sha256',{}))!={'overview.png','assembly-visibility.mp4'} or any(sha(folder/name)!=digest for name,digest in receipt['files_sha256'].items()):raise ValueError('candidate semantic media files differ')
    expected=render_viewport(definition,mesh,[p['id'] for p in definition['parts']]);poster=Image.open(folder/'overview.png');poster.load()
    if poster.size!=(WIDTH,HEIGHT) or poster.mode!='RGB' or not np.array_equal(np.asarray(poster.crop(VIEWPORT)),expected) or receipt.get('poster_viewport_sha256')!=sha256(expected.tobytes()).hexdigest():raise ValueError('candidate poster does not depict actual native triangles')
    probe=station_native._probe(folder/'assembly-visibility.mp4');frames=len(stages)*FPS
    if probe['width']!=WIDTH or probe['height']!=HEIGHT or probe['frames']!=frames or abs(probe['duration_s']-len(stages))>.01 or probe['frames_per_second']!='24/1':raise ValueError('candidate visibility video timing/dimensions differ')
    indices=list(range(frames))
    if frames*WIDTH*HEIGHT*3>256*1024*1024:raise ValueError('bounded candidate video decode required')
    # One surplus frame detects a lying container frame count while bounding
    # decoder output even when its remaining stream is arbitrarily long.
    result=subprocess.run(['ffmpeg','-v','error','-i',str(folder/'assembly-visibility.mp4'),'-vsync','0','-frames:v',str(frames+1),'-f','rawvideo','-pix_fmt','rgb24','-'],check=True,capture_output=True,timeout=90)
    required=len(indices)*WIDTH*HEIGHT*3
    if len(result.stdout)!=required or required>256*1024*1024:raise ValueError('bounded decoded candidate frames differ')
    decoded=np.frombuffer(result.stdout,np.uint8).reshape(len(indices),HEIGHT,WIDTH,3);checks=[]
    x0,y0,x1,y1=VIEWPORT
    for stage,(_,visible) in enumerate(stages):
        target=render_viewport(definition,mesh,visible);oracle=_frame_oracle(target)
        for slot in range(stage*FPS,(stage+1)*FPS):checks.append(_semantic_frame(decoded[slot,y0:y1,x0:x1],target,oracle))
    return dict(poster_exact_viewport=True,decoded_frames_checked=len(indices),stage_count=len(stages),frame_checks=checks,
        scope='Actual native-triangle viewport and visibility semantics only; no motion/collision/engineering acceptance')
