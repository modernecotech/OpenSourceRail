"""Immutable records shared by a bounded research campaign."""
from hashlib import sha256
import json
from pathlib import Path
from engineering.design_search.storage import atomic_immutable
from . import FLAGS,ROOT


def encoded(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def identity(value):return sha256(encoded(value)).hexdigest()


def write(path,value):return atomic_immutable(Path(path),encoded(value))


def inventory(directory,exclude=()):
    result={}
    for path in sorted(Path(directory).rglob('*')):
        if path.is_symlink():raise ValueError('ordinary immutable research artifacts required')
        if path.is_file():
            name=path.relative_to(directory).as_posix()
            if name not in exclude:result[name]=sha256(path.read_bytes()).hexdigest()
    return result


def source_snapshot(root=ROOT):
    from engineering.vehicle_optimisation import magnets,equipment,hvac,ledger
    from engineering.magnetic_confirmation import formulation
    from engineering.trip_dynamics.fixtures.magnetics import finite_coupon
    root=Path(root).resolve();mapping={}
    paths=set(Path(__file__).parent.rglob('*.py'))|set(magnets.source_paths())|{Path(ledger.__file__)}
    paths.update(Path(formulation.__file__).parent.rglob('*.py'))
    paths.add(Path(finite_coupon.__file__))
    for path in sorted(paths):
        if '__pycache__' in path.parts:continue
        if path.is_symlink():raise ValueError('ordinary source files required')
        parts=path.parts;name='/'.join(parts[parts.index('engineering'):])
        mapping[name]=sha256(path.read_bytes()).hexdigest()
    for records in (equipment.sources(root),hvac.source_inputs(root)['local_sha256']):
        for name,digest in records.items():
            if name in mapping and mapping[name]!=digest:raise ValueError('executing and retained source workspaces disagree: '+name)
            mapping[name]=digest
    return dict(sorted(mapping.items()))


def unaccepted(value):
    if isinstance(value,dict):
        for key,child in value.items():
            if key in FLAGS and child is not False:raise ValueError('research cannot assert acceptance: '+key)
            unaccepted(child)
    elif isinstance(value,list):
        for child in value:unaccepted(child)
