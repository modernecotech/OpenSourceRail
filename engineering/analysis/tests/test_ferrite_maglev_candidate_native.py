"""Native export definition retains exact material identities and geometric voids."""
import math
from engineering.ferrite_maglev import candidate_native as n


def test_same_exact_module_and_complete_disjoint_visibility_inventory():
    value=n.definition();candidate=n.magnetics.definition();ids=[p['id'] for p in value['parts']]
    assert value['configuration_sha256']==candidate['configuration_sha256']
    assert ids==[p['id'] for p in candidate['module']['parts']]
    assert math.isclose(sum(p['mass_kg'] for p in value['parts']),value['modelled_material_mass_kg'])
    assert set(i for g in value['construction_stages'] for i in g['parts'])==set(ids)
    assert any(p.get('holes') for p in value['parts'])
    assert all(p['source_material'] for p in value['parts'])
    assert not value['physical_release']


import gzip
import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import shutil
import subprocess

import numpy as np
import pytest
from PIL import Image


@pytest.fixture(scope='module')
def retained():
    value=n.definition();receipt=json.loads((n.OUTPUT/'native-cad.json').read_bytes());mesh=json.loads(gzip.decompress((n.OUTPUT/'native-mesh.json.gz').read_bytes()))
    return value,receipt,mesh


def test_retained_triangles_independently_recover_occupied_geometry(retained):
    value,receipt,mesh=retained;actual=n.properties(value,receipt,mesh)
    assert len(actual['parts'])==len(value['parts'])
    assert all(p['mesh']['closed_oriented_manifold'] and p['mesh']['source_surface_verified'] for p in actual['parts'])
    assert max(p['mesh']['volume_relative_error'] for p in actual['parts'])<n.MESH_VOLUME_REL_TOL==.01
    assert any(p['mesh']['volume_relative_error']>.006 for p in actual['parts'])


@pytest.mark.parametrize('fault',['empty','translated','flattened','open','reverse','bad-index','nan','duplicate-face','wrong-material'])
def test_correct_metadata_cannot_hide_empty_or_distorted_native_mesh(retained,fault):
    value,receipt,original=retained;mesh=deepcopy(original);p=mesh['parts'][0]
    if fault=='empty':p['vertices_m']=[];p['triangles']=[]
    elif fault=='translated':p['vertices_m']=[[x+.1,y,z] for x,y,z in p['vertices_m']]
    elif fault=='flattened':p['vertices_m']=[[x,y,0.] for x,y,z in p['vertices_m']]
    elif fault=='open':p['triangles'].pop()
    elif fault=='reverse':p['triangles']=[t[::-1] for t in p['triangles']]
    elif fault=='bad-index':p['triangles'][0][0]=-1
    elif fault=='nan':p['vertices_m'][0][0]=float('nan')
    elif fault=='duplicate-face':p['triangles'].append(p['triangles'][0])
    elif fault=='wrong-material':p['material']='ferrite'
    with pytest.raises(ValueError):n.properties(value,receipt,mesh)


def test_source_void_surface_cannot_be_replaced_by_filled_metadata(retained):
    value,receipt,original=retained;mesh=deepcopy(original)
    i=next(i for i,p in enumerate(value['parts']) if p['kind']=='cylinder' and p.get('holes'))
    p=value['parts'][i];item=mesh['parts'][i];axis='xyz'.index(p['cylinder_axis']);other=[k for k in range(3) if k!=axis];h=p['holes'][0]
    centre=np.array(p['at_m']);centre[other]=[p['at_m'][k]+h['xyz'[k]+'_m'] for k in other]
    vertices=np.array(item['vertices_m']);r=np.linalg.norm(vertices[:,other]-centre[other],axis=1);j=int(np.argmin(abs(r-h['diameter_m']/2)))
    vertices[j,other]=centre[other]+.5*(vertices[j,other]-centre[other]);item['vertices_m']=vertices.tolist()
    with pytest.raises(ValueError,match='source material/void'):n.properties(value,receipt,mesh)


@pytest.fixture(scope='module')
def semantic_packet(retained,tmp_path_factory):
    value,_,mesh=retained;folder=tmp_path_factory.mktemp('semantic-candidate-native')
    (folder/'definition.json').write_bytes(n.platform.encoded(value));(folder/'native-mesh.json.gz').write_bytes(gzip.compress(n.platform.encoded(mesh),mtime=0))
    n.media.native_views(folder);return folder


def test_actual_native_poster_and_decoded_visibility_stages_pass(retained,semantic_packet):
    value,_,mesh=retained;r=n.media.verify_views(semantic_packet,value,mesh)
    assert r['poster_exact_viewport'] and r['stage_count']==4 and r['decoded_frames_checked']==96


def _rehash_media(folder,name):
    receipt=json.loads((folder/'visual-receipt.json').read_bytes());receipt['files_sha256'][name]=sha256((folder/name).read_bytes()).hexdigest()
    if name=='overview.png':
        im=Image.open(folder/name);receipt['poster_viewport_sha256']=sha256(np.asarray(im.crop(n.media.VIEWPORT)).tobytes()).hexdigest()
    (folder/'visual-receipt.json').write_bytes(n.platform.encoded(receipt))


def test_coherently_rehashed_blank_poster_is_rejected(retained,semantic_packet,tmp_path):
    value,_,mesh=retained;folder=tmp_path/'forged';shutil.copytree(semantic_packet,folder)
    Image.new('RGB',(n.media.WIDTH,n.media.HEIGHT),n.media.BACKGROUND).save(folder/'overview.png');_rehash_media(folder,'overview.png')
    with pytest.raises(ValueError,match='poster does not depict'):n.media.verify_views(folder,value,mesh)


def test_coherently_rehashed_static_poster_video_cannot_replace_four_stages(retained,semantic_packet,tmp_path):
    value,_,mesh=retained;folder=tmp_path/'forged';shutil.copytree(semantic_packet,folder)
    subprocess.run(['ffmpeg','-y','-v','error','-loop','1','-i',str(folder/'overview.png'),'-t','4','-r','24','-c:v','libx264','-crf','12','-pix_fmt','yuv420p',str(folder/'assembly-visibility.mp4')],check=True,timeout=60)
    _rehash_media(folder,'assembly-visibility.mp4')
    with pytest.raises(ValueError,match='actual native visibility stage'):n.media.verify_views(folder,value,mesh)


def test_coherently_rehashed_mesh_manifest_cannot_retain_correct_properties(retained,tmp_path):
    _,_,_=retained;folder=tmp_path/'forged';shutil.copytree(n.OUTPUT,folder)
    mesh=json.loads(gzip.decompress((folder/'native-mesh.json.gz').read_bytes()));mesh['parts'][0]['vertices_m']=[];mesh['parts'][0]['triangles']=[]
    (folder/'native-mesh.json.gz').write_bytes(gzip.compress(n.platform.encoded(mesh),mtime=0));digest=sha256((folder/'native-mesh.json.gz').read_bytes()).hexdigest()
    cad=json.loads((folder/'native-cad.json').read_bytes());cad['files_sha256']['native-mesh.json.gz']=digest;(folder/'native-cad.json').write_bytes(n.platform.encoded(cad))
    visual=json.loads((folder/'visual-receipt.json').read_bytes());visual['mesh_sha256']=digest;(folder/'visual-receipt.json').write_bytes(n.platform.encoded(visual))
    manifest=json.loads((folder/'manifest.json').read_bytes());manifest['source_sha256']=n.sources()
    for name in ('native-mesh.json.gz','native-cad.json','visual-receipt.json'):manifest['files_sha256'][name]=sha256((folder/name).read_bytes()).hexdigest()
    (folder/'manifest.json').write_bytes(n.platform.encoded(manifest))
    with pytest.raises(ValueError,match='nonempty finite native vertices'):n.verify(folder)


def test_rehashed_single_middle_frame_substitution_is_rejected(retained,semantic_packet,tmp_path):
    value,_,mesh=retained;folder=tmp_path/'forged';shutil.copytree(semantic_packet,folder);x0,y0,x1,y1=n.media.VIEWPORT
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(folder/'assembly-visibility.mp4'),'-vf',f"drawbox=x={x0}:y={y0}:w={x1-x0}:h={y1-y0}:color=0xf1f5f9:t=1200:enable='eq(n,5)'",'-c:v','libx264','-crf','12','-pix_fmt','yuv420p',str(folder/'altered.mp4')],check=True,timeout=60)
    (folder/'altered.mp4').replace(folder/'assembly-visibility.mp4');_rehash_media(folder,'assembly-visibility.mp4')
    with pytest.raises(ValueError,match='actual native visibility stage'):n.media.verify_views(folder,value,mesh)
