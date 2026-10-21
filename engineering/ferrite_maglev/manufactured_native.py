"""Reopened native manufacture-detail solids, with numerical dossier provenance."""
from copy import deepcopy
from hashlib import sha256
import gzip
import json
import math
from pathlib import Path
import zipfile

from . import closure,geometry,media,model,station_native
from engineering.factory_examples import models

OUTPUT=model.ROOT/'docs/design-engine/ferrite-maglev/manufactured-native'
FILES={'definition.json','model.FCStd','model.step.gz','native-cad.json','native-mesh.json.gz',
    'overview.png','assembly-visibility.mp4','visual-receipt.json'}
SCHEMA='osr-manufactured-native-publication/1'
MAX=64*1024*1024


def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()


def sources():
    paths={Path(__file__),Path(geometry.__file__),Path(media.__file__),Path(station_native.__file__),
        model.ROOT/'engineering/factory_examples/native.py',Path(models.__file__),
        model.ROOT/'engineering/analysis/tests/test_ferrite_maglev_manufactured_native.py',*closure.source_paths()}
    return {p.relative_to(model.ROOT).as_posix():digest(p) for p in sorted(paths)}


def definition():
    raw=closure.definition();value=geometry.finish(raw['id'],deepcopy(raw['parts']),deepcopy(raw['construction_stages']),
        scope=raw['scope'],holds=raw['holds'])
    value.update(interference_roles=[],interference_scope='Untrimmed member and connection detail stock; no assembled collision acceptance',
        modelled_cg_m=None,cg_scope='Joined assemblies, cut-outs and asymmetric details need an independent centroid/inertia solution',
        complete_body_or_system_modelled=False,**model.FLAGS)
    return value


def publish(output=OUTPUT):
    from engineering.factory_examples.native import generate
    before=sources();output=Path(output);value=definition()
    if output.is_symlink():raise ValueError('ordinary manufacture native directory required')
    output.mkdir(parents=True,exist_ok=True)
    if {p.name for p in output.iterdir()}-FILES-{'manifest.json'}:raise ValueError('unexpected manufacture native output')
    (output/'definition.json').write_bytes(encoded(value));receipt=generate(output/'definition.json',output,model.ROOT)
    raw=(output/'model.step').read_bytes();(output/'model.step.gz').write_bytes(gzip.compress(raw,mtime=0));(output/'model.step').unlink()
    receipt['files_sha256'].pop('model.step');receipt['files_sha256']['model.step.gz']=digest(output/'model.step.gz')
    receipt['step_uncompressed_sha256']=sha256(raw).hexdigest();(output/'native-cad.json').write_bytes(encoded(receipt))
    media.native_views(output)
    if sources()!=before:raise ValueError('manufacture detail sources changed during export')
    manifest=dict(schema=SCHEMA,source_sha256=before,files_sha256={n:digest(output/n) for n in sorted(FILES)},
        part_count=len(value['parts']),modelled_material_mass_kg=value['modelled_material_mass_kg'],
        movie=station_native._probe(output/'assembly-visibility.mp4'),release_authority=False,**model.FLAGS)
    (output/'manifest.json').write_bytes(encoded(manifest));return verify(output)


def _read(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size>MAX:raise ValueError('bounded ordinary manufacture native file required')
    return path.read_bytes()


def _compressed(path):
    with gzip.open(path,'rb') as stream:raw=stream.read(2*MAX+1)
    if len(raw)>2*MAX:raise ValueError('manufacture native decompression bound exceeded')
    return raw


def _check_archive(path):
    # Bound declared expansion before CRC testing reads compressed members.
    with zipfile.ZipFile(path) as archive:
        entries=archive.infolist();names=[item.filename for item in entries]
        if ('Document.xml' not in names or len(set(names))!=len(names)
                or any(Path(name).is_absolute() or '..' in Path(name).parts for name in names)
                or any(item.file_size>MAX for item in entries)
                or sum(item.file_size for item in entries)>MAX):
            raise ValueError('bounded native document archive required')
        if archive.testzip() is not None:raise ValueError('native document archive differs')


def verify(output=OUTPUT):
    output=Path(output)
    if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()}!=FILES|{'manifest.json'}:raise ValueError('exact manufacture native packet required')
    manifest=json.loads(_read(output/'manifest.json'))
    if manifest.get('schema')!=SCHEMA or manifest.get('source_sha256')!=sources():raise ValueError('manufacture native sources differ')
    if set(manifest.get('files_sha256',{}))!=FILES:raise ValueError('complete manufacture native receipts required')
    for name,expected in manifest['files_sha256'].items():
        if sha256(_read(output/name)).hexdigest()!=expected:raise ValueError('manufacture native payload differs')
    value=json.loads(_read(output/'definition.json'))
    if value!=definition():raise ValueError('manufacture solid definition differs')
    receipt=json.loads(_read(output/'native-cad.json'));visual=json.loads(_read(output/'visual-receipt.json'))
    mesh=json.loads(_compressed(output/'native-mesh.json.gz'))
    ids=[p['id'] for p in value['parts']]
    if (receipt.get('fcstd_reopened') is not True or receipt.get('step_reopened') is not True
            or receipt.get('input_sha256')!=manifest['files_sha256']['definition.json']
            or receipt.get('part_count')!=len(ids) or manifest.get('part_count')!=len(ids)
            or [p['id'] for p in receipt['parts']]!=ids or [p['id'] for p in mesh['parts']]!=ids):
        raise ValueError('actual native reopen/solid evidence differs')
    if (receipt.get('exporter_sha256')!=manifest['source_sha256']['engineering/factory_examples/native.py']
            or receipt.get('geometry_helpers_sha256')!=manifest['source_sha256']['engineering/factory_examples/models.py']):
        raise ValueError('manufacture exporter/helper identity differs')
    for part,actual in zip(value['parts'],receipt['parts']):
        size=models.global_size(part);bounds=part['at_m']+[part['at_m'][i]+size[i] for i in range(3)]
        if (not math.isclose(actual['volume_m3'],models.volume(part),rel_tol=1e-7)
                or len(actual['bounds_m'])!=6 or any(not math.isfinite(a) or abs(a-b)>1e-8 for a,b in zip(actual['bounds_m'],bounds))):
            raise ValueError('native solid bounds or occupied volume differs')
    if (mesh.get('schema')!='osr-native-tessellation/1' or mesh.get('physical_release') is not False
            or visual.get('schema')!='osr-native-visual-evidence/1'
            or visual.get('renderer_sha256')!=manifest['source_sha256']['engineering/ferrite_maglev/media.py']
            or mesh.get('input_sha256')!=manifest['files_sha256']['definition.json']
            or visual.get('definition_sha256')!=manifest['files_sha256']['definition.json']
            or visual.get('mesh_sha256')!=manifest['files_sha256']['native-mesh.json.gz']
            or visual.get('stages')!=value['construction_stages']):raise ValueError('manufacture mesh/visibility provenance differs')
    for part,solid in zip(value['parts'],mesh['parts']):
        vertices=solid.get('vertices_m',[]);triangles=solid.get('triangles',[])
        size=models.global_size(part);lo=part['at_m'];hi=[lo[i]+size[i] for i in range(3)]
        if (solid.get('material')!=part['material'] or not math.isclose(solid.get('volume_m3',0.),models.volume(part),rel_tol=1e-7)
                or not vertices or not triangles or len(vertices)>1000000 or len(triangles)>2000000
                or any(len(v)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) or x<lo[i]-1e-8 or x>hi[i]+1e-8 for i,x in enumerate(v)) for v in vertices)
                or any(len(t)!=3 or any(type(i) is not int or not 0<=i<len(vertices) for i in t) for t in triangles)):
            raise ValueError('native mesh material, volume or bounded topology differs')
    for record,names in ((receipt,{'model.FCStd','model.step.gz','native-mesh.json.gz'}),
            (visual,{'overview.png','assembly-visibility.mp4'})):
        if record.get('physical_release') is not False:raise ValueError('native export has no physical authority')
        if set(record.get('files_sha256',{}))!=names:raise ValueError('exact nested native receipt inventory required')
        if any(digest(output/name)!=expected for name,expected in record['files_sha256'].items()):raise ValueError('nested native receipt differs')
    if sha256(_compressed(output/'model.step.gz')).hexdigest()!=receipt.get('step_uncompressed_sha256'):raise ValueError('STEP receipt differs')
    _check_archive(output/'model.FCStd')
    if station_native._probe(output/'assembly-visibility.mp4')!=manifest.get('movie'):raise ValueError('manufacture visibility movie differs')
    if any(row.get(k) is not False for row in (manifest,value) for k in model.FLAGS) or manifest.get('release_authority') is not False:
        raise ValueError('manufacture geometry has no release authority')
    return manifest
