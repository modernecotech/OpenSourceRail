"""Source-bound, non-promoting publication for an implicit voxel experiment.

The caller supplies trusted original evaluation and publication manifest IDs.
Hashes do not prove provenance if the caller also accepts an attacker-chosen ID.
Verification resamples current source; it does not claim native-evaluator reuse,
physical qualification, or independent attestation of historical runtime.
"""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from . import implicit_geometry as geometry

PRODUCER='engineering/design_search/implicit_geometry_publication.py'
OUTPUT='docs/design-engine/implicit-geometry-study'
FLAGS=dict(geometry.FLAGS)
INPUTS=('candidate.json','evaluation.json','occupancy.vtk')
PAYLOAD=('README.md','candidate.json','evaluation.json','occupancy.vtk','result.json')
MAX_JSON=1024*1024
MAX_VTK=geometry.MAX_VOXELS+4096
SCOPE='Centre-sampled implicit research only; no native reuse, qualification or railway selection'
PROVENANCE='Runtime is recorded by its producer, not independently attested; IDs must be pinned externally'


def _ordinary(path, limit):
    path=Path(path).absolute()
    for component in (path,*path.parents):
        if component.is_symlink():raise ValueError('Symlink file or ancestor rejected')
    before=path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_size>limit:
        raise ValueError('Bounded ordinary file required: '+path.name)
    signature=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
    with os.fdopen(fd,'rb') as f:
        opened=os.fstat(f.fileno())
        if signature(before)!=signature(opened):raise ValueError('Input changed before reading')
        data=f.read(limit+1);after=os.fstat(f.fileno())
    if len(data)>limit or signature(opened)!=signature(after) or signature(after)!=signature(path.lstat()):
        raise ValueError('Input changed during reading')
    return data


def _directory(path):
    path=Path(path).absolute()
    for component in (path,*path.parents):
        if component.is_symlink():raise ValueError('Symlink directory or ancestor rejected')
    if not path.is_dir():raise ValueError('Ordinary existing directory required')
    return path


def _pairs(rows):
    out={}
    for key,value in rows:
        if key in out:raise ValueError('Duplicate JSON key')
        out[key]=value
    return out


def _json(raw):
    try:value=json.loads(raw,object_pairs_hook=_pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
    except (json.JSONDecodeError,UnicodeDecodeError) as error:raise ValueError('Malformed JSON') from error
    if not isinstance(value,dict) or encoded(value)!=raw:raise ValueError('Canonical JSON object required')
    return value


def _sha(value):return geometry._sha(value)


def _seal(value,key):
    value[key]=identity(value)
    return value


def _sealed(value,key):
    if value.get(key)!=identity({k:v for k,v in value.items() if k!=key}):raise ValueError('Record identity differs: '+key)


def _input(state):
    state=_directory(state)
    return {name:_ordinary(state/name,MAX_VTK if name.endswith('.vtk') else MAX_JSON) for name in INPUTS}


def _sources(root, evaluation):
    root=_directory(root)
    names=(geometry.PRODUCER,'engineering/station_rail/common.py')
    current={name:digest(_ordinary_path(root,name)) for name in names}
    if evaluation.get('source_sha256')!=current:raise ValueError('Original geometry source differs from declared root')
    if digest(Path(geometry.__file__))!=current[geometry.PRODUCER]:raise ValueError('Executing geometry producer differs from root')
    pub=_ordinary_path(root,PRODUCER)
    if digest(Path(__file__))!=digest(pub):raise ValueError('Executing publication producer differs from root')
    return dict(sorted({**current,PRODUCER:digest(pub)}.items()))


def _ordinary_path(root,name):
    path=Path(name)
    if path.is_absolute() or '..' in path.parts:raise ValueError('Relative source path required')
    target=Path(root)/path
    _ordinary(target,MAX_JSON)
    return target


def _readme(record):
    return ('# Three-dimensional implicit cellular geometry study\n\n'
        'This detached gyroid-sheet research sample records exact occupied voxels, their assumed-density mass and the original tool environment. '
        'The voxel surface is not a verified continuous CAD surface or an installed beam. '
        'Skin, interfaces, material strength, manufacturability, loads and physical approval remain unresolved.\n\n'
        f"Original candidate: `{record['candidate_id']}`. Original evaluation: `{record['evaluation_id']}`.\n\n"
        'A verifier resamples the current source and checks every numerical field and VTK byte against the externally pinned original evaluation and manifest identities. '
        'The historical and replay environments are kept separate; this is not native-evaluator reuse or independent runtime attestation. '
        'The implicit-volume enclosure is an ideal-arithmetic bound and does not include guaranteed floating-point roundoff. '
        'No physical or engineering acceptance, manufacturing release, operating release or railway selection is made.\n')


def _result(candidate,evaluation,sources,creation_environment):
    return _seal(dict(schema='osr-implicit-geometry-publication-result/1',candidate_id=candidate['candidate_id'],
        evaluation_id=evaluation['evaluation_id'],source_sha256=sources,
        recorded_environment=deepcopy(evaluation['numerical_environment']),
        publication_environment=deepcopy(creation_environment),
        vtk_sha256=evaluation['geometry']['vtk_sha256'],
        scope=SCOPE,provenance=PROVENANCE,complete_installed_mass_kg=None,complete_installed_cost=None,
        native_evaluator_reuse=False,recorded_environment_independently_attested=False,**FLAGS),'publication_id')


def _payload(folder):
    folder=_directory(folder)
    names={p.name for p in folder.iterdir()}
    if names!=set(PAYLOAD)|{'manifest.json'}:raise ValueError('Exact closed publication inventory required')
    return {n:sha256(_ordinary(folder/n,MAX_VTK if n.endswith('.vtk') else MAX_JSON)).hexdigest() for n in PAYLOAD}


def publish(state, *, expected_evaluation_id, root=ROOT, output=None):
    """Create a previously absent immutable packet from original input bytes."""
    root=_directory(root);state=_directory(state)
    target=Path(output).absolute() if output is not None else root/OUTPUT
    parent=_directory(target.parent)
    if target.exists() or target.is_symlink():raise ValueError('New publication destination required')
    if target==state or target in state.parents or state in target.parents:raise ValueError('Publication and source attempt must be separate')
    raw=_input(state);candidate=_json(raw['candidate.json']);evaluation=_json(raw['evaluation.json'])
    sources=_sources(root,evaluation)
    geometry.verify(candidate,evaluation,raw['occupancy.vtk'],expected_evaluation_id=expected_evaluation_id)
    publication=_result(candidate,evaluation,sources,geometry._environment())
    stage=Path(tempfile.mkdtemp(prefix='.implicit-stage-',dir=parent))
    try:
        for n,data in raw.items():(stage/n).write_bytes(data)
        (stage/'result.json').write_bytes(encoded(publication));(stage/'README.md').write_text(_readme(publication))
        hashes={n:sha256(_ordinary(stage/n,MAX_VTK if n.endswith('.vtk') else MAX_JSON)).hexdigest() for n in PAYLOAD}
        manifest=_seal(dict(schema='osr-implicit-geometry-publication/1',publication_id=publication['publication_id'],
            source_sha256=sources,files_sha256=hashes,**FLAGS),'manifest_id')
        (stage/'manifest.json').write_bytes(encoded(manifest))
        verify(stage,expected_manifest_id=manifest['manifest_id'],root=root)
        if _input(state)!=raw or _sources(root,evaluation)!=sources:
            raise ValueError('Original input or source changed while publishing')
        target.mkdir()
        try:os.rename(stage,target)
        except OSError:
            try:target.rmdir()
            except OSError:pass
            raise
    finally:
        if stage.exists():shutil.rmtree(stage)
    return manifest


def verify(output=None, *, expected_manifest_id, root=ROOT):
    """Check closed payload/source identities and replay with the present runtime."""
    root=_directory(root);output=_directory(output if output is not None else root/OUTPUT)
    manifest=_json(_ordinary(output/'manifest.json',MAX_JSON))
    if not _sha(expected_manifest_id) or manifest.get('manifest_id')!=expected_manifest_id:
        raise ValueError('Externally pinned manifest identity differs')
    _sealed(manifest,'manifest_id')
    if (set(manifest)!={'schema','publication_id','source_sha256','files_sha256','manifest_id',*FLAGS}
            or manifest['schema']!='osr-implicit-geometry-publication/1' or any(manifest[k] is not False for k in FLAGS)
            or manifest['files_sha256']!=_payload(output)):
        raise ValueError('Manifest, flags or payload inventory differs')
    candidate=_json(_ordinary(output/'candidate.json',MAX_JSON))
    evaluation=_json(_ordinary(output/'evaluation.json',MAX_JSON))
    record=_json(_ordinary(output/'result.json',MAX_JSON));_sealed(record,'publication_id')
    geometry._recorded_environment(record.get('publication_environment'))
    sources=_sources(root,evaluation)
    expected=_result(candidate,evaluation,sources,record['publication_environment'])
    if record!=expected or manifest['publication_id']!=record['publication_id'] or manifest['source_sha256']!=sources:
        raise ValueError('Original identity, source, environment or publication disposition differs')
    if _ordinary(output/'README.md',MAX_JSON)!=_readme(record).encode():raise ValueError('Publication interpretation differs')
    replay=geometry.verify(candidate,evaluation,_ordinary(output/'occupancy.vtk',MAX_VTK),expected_evaluation_id=record['evaluation_id'])
    return dict(verified=True,manifest_id=expected_manifest_id,publication_id=record['publication_id'],
        candidate_id=record['candidate_id'],evaluation_id=record['evaluation_id'],
        recorded_environment=deepcopy(record['recorded_environment']),replay_environment=replay['replay_environment'],
        environments_identical=replay['environments_identical'],native_evaluator_reuse=False,
        recorded_environment_independently_attested=False,expected_identity_from_caller=True,**FLAGS)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);commands=p.add_subparsers(dest='action',required=True)
    c=commands.add_parser('publish');c.add_argument('--state',type=Path,required=True);c.add_argument('--expected-evaluation-id',required=True);c.add_argument('--output',type=Path)
    c=commands.add_parser('verify');c.add_argument('--expected-manifest-id',required=True);c.add_argument('--output',type=Path)
    p.add_argument('--root',type=Path,default=ROOT);args=p.parse_args(argv)
    try:
        out=publish(args.state,expected_evaluation_id=args.expected_evaluation_id,root=args.root,output=args.output) if args.action=='publish' else verify(args.output,expected_manifest_id=args.expected_manifest_id,root=args.root)
    except (ValueError,OSError,KeyError,TypeError) as error:p.exit(2,str(error)+'\n')
    print(json.dumps(out,sort_keys=True,indent=2));return 0


if __name__=='__main__':raise SystemExit(main())
