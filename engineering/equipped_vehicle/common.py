"""Source-bound immutable records for equipped-vehicle research."""
from hashlib import sha256
import json
from pathlib import Path
from engineering.design_search.storage import atomic_immutable
from . import ROOT


def encoded(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def identity(value):return sha256(encoded(value)).hexdigest()


def write(path,value):atomic_immutable(Path(path),encoded(value))


def sources(root=ROOT):
    from engineering.halbach_scaling import vehicles,candidates
    from engineering.ferrite_maglev import candidate_magnetics,assembled_body,closure,configuration,geometry,station_structure
    from engineering.factory_examples import models
    root=Path(root).resolve();records=vehicles.sources(root)
    paths=set(candidates.source_paths())|set(candidate_magnetics.source_paths())|{Path(assembled_body.__file__)}
    paths.update((assembled_body.INPUT,assembled_body.LEGACY,assembled_body.REJECTED,assembled_body.REJECTED_FLANGE,
                  Path(closure.__file__),closure.INPUT,Path(geometry.__file__),Path(station_structure.__file__),station_structure.INPUT,
                  Path(models.__file__),*configuration.source_paths()))
    paths.update(Path(__file__).parent.rglob('*.py'))
    for path in paths:
        if '__pycache__' in path.parts:continue
        try:name=path.relative_to(ROOT).as_posix()
        except ValueError:name=path.relative_to(root).as_posix()
        digest=sha256(path.read_bytes()).hexdigest()
        if name in records and records[name]!=digest:raise ValueError('executing and retained sources differ: '+name)
        records[name]=digest
    return dict(sorted(records.items()))
