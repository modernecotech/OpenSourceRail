"""Actual native exports of provisional station-powered panel/civil material stock.

The exported one-car panel stock is not a complete sized body. Two illustrative
end supports are not an accepted foundation or a continuous-route support count.
"""
from copy import deepcopy
from hashlib import sha256
import gzip
import json
import math
from pathlib import Path
import subprocess
import zipfile

from . import configuration,geometry,media,model,station_structure

ROOT=model.ROOT
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/station-native'
FILES={'definition.json','model.FCStd','model.step.gz','native-cad.json','native-mesh.json.gz',
    'overview.png','assembly-visibility.mp4','visual-receipt.json'}
MAX_BYTES=64*1024*1024
MAX_RAW=128*1024*1024


def encoded(value):
    return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def digest(data):
    return sha256(data).hexdigest()


def sources():
    paths={Path(__file__),Path(station_structure.__file__),station_structure.INPUT,
        Path(geometry.__file__),Path(model.__file__),Path(media.__file__),*configuration.source_paths(),
        ROOT/'engineering/factory_examples/native.py',ROOT/'engineering/factory_examples/models.py'}
    return {p.relative_to(ROOT).as_posix():digest(p.read_bytes()) for p in sorted(paths)}


def definition():
    """Keep unsized budgets outside the solid ledger; preserve all study holds."""
    raw=station_structure.definition()
    for part in raw['parts']:
        density=raw['material_density_assumptions_kg_m3'][part['material']]
        if not math.isclose(density,geometry.MATERIALS[part['material']],rel_tol=1e-12):
            raise ValueError('native material density needs explicit coordinated identity')
    finished=geometry.finish(raw['id'],deepcopy(raw['parts']),deepcopy(raw['construction_stages']),
        scope=raw['scope'],holds=deepcopy(raw['holds']))
    for name,value in raw.items():
        if name not in finished:finished[name]=deepcopy(value)
    finished.update(**model.FLAGS)
    # Developed panel corners may intersect. No broad collision check or
    # watertight assembled-body acceptance is implied by separate valid solids.
    finished['interference_roles']=[]
    finished['interference_scope']='No assembled-body collision acceptance; developed stock, mitres, joints and interfaces remain unresolved'
    finished['publication_scope']='Partial developed GFRP sandwich stock and civil material regions; no sized complete train body, reinforcement/prestress or accepted foundation'
    return finished


def _read(path,maximum=MAX_BYTES):
    if path.is_symlink() or not path.is_file() or path.stat().st_size>maximum:
        raise ValueError('bounded ordinary station native file required')
    return path.read_bytes()


def _unzip_gzip(path):
    with gzip.open(path,'rb') as stream:data=stream.read(MAX_RAW+1)
    if len(data)>MAX_RAW:raise ValueError('station native decompressed payload exceeds bound')
    return data


def _probe(path):
    result=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries',
        'stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration','-of','json',str(path)],
        check=True,capture_output=True,text=True,timeout=30)
    value=json.loads(result.stdout)
    if len(value.get('streams',[]))!=1:raise ValueError('one station visibility video stream required')
    stream=value['streams'][0]
    return dict(codec=stream['codec_name'],width=stream['width'],height=stream['height'],
        frames_per_second=stream['r_frame_rate'],frames=int(stream['nb_frames']),duration_s=float(value['format']['duration']))


def publish(output=OUTPUT):
    from engineering.factory_examples.native import generate
    before=sources();value=definition();output=Path(output)
    if output.is_symlink():raise ValueError('ordinary station native packet directory required')
    output.mkdir(parents=True,exist_ok=True)
    if any(p.is_symlink() for p in output.iterdir()) or {p.name for p in output.iterdir()}-FILES-{'manifest.json'}:
        raise ValueError('unexpected station native packet files')
    (output/'definition.json').write_bytes(encoded(value))
    receipt=generate(output/'definition.json',output,ROOT)
    raw=_read(output/'model.step',MAX_RAW)
    (output/'model.step.gz').write_bytes(gzip.compress(raw,mtime=0));(output/'model.step').unlink()
    receipt['files_sha256'].pop('model.step')
    receipt['files_sha256']['model.step.gz']=digest((output/'model.step.gz').read_bytes())
    receipt['step_uncompressed_sha256']=digest(raw)
    (output/'native-cad.json').write_bytes(encoded(receipt))
    media.native_views(output)
    movie=_probe(output/'assembly-visibility.mp4')
    if sources()!=before:raise ValueError('station native sources changed during export/render')
    manifest=dict(schema='osr-station-native-publication/1',source_sha256=before,
        files_sha256={name:digest(_read(output/name)) for name in sorted(FILES)},
        part_count=len(value['parts']),movie=movie,scope=value['publication_scope'],holds=value['holds'],
        modelled_material_mass_kg=value['modelled_material_mass_kg'],complete_body_mass_modelled=False,
        release_authority=False,**model.FLAGS)
    path=output/'manifest.json';pending=path.with_suffix('.pending');pending.write_bytes(encoded(manifest));pending.replace(path)
    return verify(output)


def verify(output=OUTPUT):
    output=Path(output)
    if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()}!=FILES|{'manifest.json'}:
        raise ValueError('exact station native packet inventory required')
    manifest=json.loads(_read(output/'manifest.json'))
    if manifest.get('schema')!='osr-station-native-publication/1' or manifest.get('source_sha256')!=sources():
        raise ValueError('station native source identity differs')
    if set(manifest.get('files_sha256',{}))!=FILES:raise ValueError('complete station native payload receipts required')
    for name,expected in manifest['files_sha256'].items():
        if digest(_read(output/name))!=expected:raise ValueError('station native payload differs: '+name)
    expected=definition();value=json.loads(_read(output/'definition.json'))
    if value!=expected:raise ValueError('station native definition or evidence holds differ')
    if (manifest.get('part_count')!=len(value['parts']) or manifest.get('scope')!=value['publication_scope']
            or manifest.get('holds')!=value['holds'] or manifest.get('modelled_material_mass_kg')!=value['modelled_material_mass_kg']
            or manifest.get('complete_body_mass_modelled') is not False):
        raise ValueError('station native scope, mass or part ledger differs')
    if any(record.get(key) is not False for record in (manifest,value) for key in model.FLAGS):
        raise ValueError('station native study cannot release engineering or hardware')
    if manifest.get('release_authority') is not False:raise ValueError('station native packet has no release authority')
    receipt=json.loads(_read(output/'native-cad.json'));visual=json.loads(_read(output/'visual-receipt.json'))
    if (receipt.get('schema')!='osr-factory-native-cad/1' or receipt.get('fcstd_reopened') is not True
            or receipt.get('step_reopened') is not True or receipt.get('part_count')!=len(value['parts'])
            or receipt.get('input_sha256')!=manifest['files_sha256']['definition.json']
            or receipt.get('exporter_sha256')!=manifest['source_sha256']['engineering/factory_examples/native.py']
            or receipt.get('geometry_helpers_sha256')!=manifest['source_sha256']['engineering/factory_examples/models.py']
            or not receipt.get('freecad_version') or not receipt.get('opencascade_version')):
        raise ValueError('actual native reopen/export identity required')
    if receipt.get('checked_interference_roles')!=[] or receipt.get('interference_checked_ids')!=[]:
        raise ValueError('no assembled-body collision acceptance is available')
    ids=[part['id'] for part in value['parts']]
    if [part['id'] for part in receipt.get('parts',[])]!=ids:raise ValueError('native solid inventory differs')
    volume_sum=0.
    for part,native in zip(value['parts'],receipt['parts']):
        bounds=part['at_m']+[part['at_m'][i]+part['size_m'][i] for i in range(3)]
        if (not math.isclose(native['volume_m3'],part['volume_m3'],rel_tol=1e-7)
                or len(native['bounds_m'])!=6 or any(abs(x-y)>1e-8 for x,y in zip(native['bounds_m'],bounds))):
            raise ValueError('native solid volume/bounds differs from dimensioned definition')
        volume_sum+=native['volume_m3']
    if not math.isclose(receipt.get('volume_sum_m3',-1),volume_sum,rel_tol=1e-9):raise ValueError('native occupied-volume receipt differs')
    expected_native={'model.FCStd','model.step.gz','native-mesh.json.gz'}
    expected_visual={'overview.png','assembly-visibility.mp4'}
    for record,names in ((receipt,expected_native),(visual,expected_visual)):
        if record.get('physical_release') is not False or set(record.get('files_sha256',{}))!=names:
            raise ValueError('complete non-release native/visual receipts required')
        if any(digest!=manifest['files_sha256'][name] for name,digest in record['files_sha256'].items()):
            raise ValueError('nested station native receipt differs')
    step=_unzip_gzip(output/'model.step.gz')
    if digest(step)!=receipt.get('step_uncompressed_sha256') or not step.startswith(b'ISO-10303-21;'):
        raise ValueError('compressed STEP identity differs from reopened export')
    with zipfile.ZipFile(output/'model.FCStd') as archive:
        if ('Document.xml' not in archive.namelist() or sum(v.file_size for v in archive.infolist())>MAX_RAW
                or archive.testzip() is not None):raise ValueError('bounded valid native document archive required')
    mesh=json.loads(_unzip_gzip(output/'native-mesh.json.gz'))
    if (mesh.get('schema')!='osr-native-tessellation/1' or mesh.get('input_sha256')!=manifest['files_sha256']['definition.json']
            or mesh.get('physical_release') is not False or [p['id'] for p in mesh.get('parts',[])]!=ids):
        raise ValueError('native tessellation provenance or part inventory differs')
    for part,solid in zip(value['parts'],mesh['parts']):
        if solid.get('material')!=part['material'] or not math.isclose(solid['volume_m3'],part['volume_m3'],rel_tol=1e-7):
            raise ValueError('native mesh material/quantity differs')
        vertices=solid.get('vertices_m',[]);triangles=solid.get('triangles',[])
        if not vertices or not triangles or len(vertices)>100000 or len(triangles)>200000:
            raise ValueError('bounded native mesh geometry required')
        if any(len(v)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in v) for v in vertices):
            raise ValueError('finite native mesh coordinates required')
        if any(len(t)!=3 or any(type(i) is not int or not 0<=i<len(vertices) for i in t) for t in triangles):
            raise ValueError('native mesh triangle identity differs')
    if (visual.get('schema')!='osr-native-visual-evidence/1'
            or visual.get('renderer_sha256')!=manifest['source_sha256']['engineering/ferrite_maglev/media.py']
            or visual.get('definition_sha256')!=manifest['files_sha256']['definition.json']
            or visual.get('mesh_sha256')!=manifest['files_sha256']['native-mesh.json.gz']
            or visual.get('stages')!=value['construction_stages']
            or visual.get('frame_count')!=len(value['construction_stages'])
            or visual.get('source_frames_per_second')!=3):
        raise ValueError('native visibility sequence provenance differs')
    png=_read(output/'overview.png')
    if not png.startswith(b'\x89PNG\r\n\x1a\n') or [int.from_bytes(png[i:i+4],'big') for i in (16,20)]!=[1200,675]:
        raise ValueError('native overview image dimensions differ')
    movie=_probe(output/'assembly-visibility.mp4')
    if (movie!=manifest.get('movie') or movie['codec']!='h264' or (movie['width'],movie['height'])!=(1200,676)
            or movie['frames_per_second']!='24/1' or movie['frames']<=0
            or abs(movie['duration_s']-visual['frame_count']/3)>1/24+.001):
        raise ValueError('native visibility movie differs from declared sequence')
    return manifest
