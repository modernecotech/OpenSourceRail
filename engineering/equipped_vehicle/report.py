"""Immutable inventories plus executed composite method output."""
import gzip
import json
from hashlib import sha256
from pathlib import Path

from engineering.design_search.storage import atomic_immutable
from . import ROOT,FLAGS
from .common import encoded,identity,sources,write
from .inventory import study
from .structures import run_structural_fixture,verify_structural_fixture


def inventory(directory,exclude=()):
    result={}
    for path in sorted(Path(directory).rglob('*')):
        if path.is_symlink():raise ValueError('ordinary equipped-vehicle files required')
        if path.is_file() and path.relative_to(directory).as_posix() not in exclude:
            result[path.relative_to(directory).as_posix()]=sha256(path.read_bytes()).hexdigest()
    return result


def summary(value,structural):
    rows=[]
    for r in value['inventories']:
        rows.append({k:r[k] for k in ('composition_id','body_candidate_id','magnet_component_id','body_name','magnetic_recipe_id',
            'assembly_definition_id','evaluation_id','comparison_empty_kg_per_car','comparison_aw3_kg_per_car',
            'located_material_properties','accounted_mass_by_evidence_class_kg','located_share_of_accounted_comparison',
            'installed_empty_kg_per_car','installed_aw3_kg_per_car','cg_m','inertia_kg_m2','modal_model','system_coverage','readiness')})
    return dict(schema='osr-equipped-vehicle-report/1',inventory_study_id=value['study_id'],inventories=rows,
        structural_method=dict(evaluation_id=structural['evaluation_id'],execution_status=structural['execution_status'],
            method_screen=structural['method_screen'],scope=structural['scope']),
        gfrp_seed_geometry_id=value['gfrp_design_space']['seed_geometry_id'],
        source_sha256=value['source_sha256'],**FLAGS)


def run(output,*,root=ROOT,ccx=None):
    before=sources(root);output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False)
    value=study(root);atomic_immutable(output/'inventories.json.gz',gzip.compress(encoded(value),mtime=0))
    structural=run_structural_fixture(output/'structural-fixture',ccx=ccx,root=root)
    result=summary(value,structural);result['report_id']=identity(result);write(output/'summary.json',result)
    if sources(root)!=before:raise ValueError('equipped-car report sources changed')
    write(output/'manifest.json',dict(schema='osr-equipped-vehicle-publication/1',source_sha256=before,
        report_id=result['report_id'],files_sha256=inventory(output,('manifest.json',)),**FLAGS))
    return result


def verify(output,*,root=ROOT):
    output=Path(output).resolve();manifest=json.loads((output/'manifest.json').read_bytes())
    if manifest['source_sha256']!=sources(root):raise ValueError('equipped-car source snapshot differs')
    if manifest['files_sha256']!=inventory(output,('manifest.json',)):raise ValueError('equipped-car payload differs')
    expected=study(root)
    if (output/'inventories.json.gz').read_bytes()!=gzip.compress(encoded(expected),mtime=0):raise ValueError('equipped-car inventory does not reproduce exact geometry/accounting')
    native=verify_structural_fixture(output/'structural-fixture',root=root)
    structural=json.loads((output/'structural-fixture/result.json').read_bytes());expected_summary=summary(expected,structural)
    expected_summary['report_id']=identity(expected_summary)
    if json.loads((output/'summary.json').read_bytes())!=expected_summary or manifest['report_id']!=expected_summary['report_id']:
        raise ValueError('equipped-car summary/disposition differs')
    if any(manifest.get(k) is not v for k,v in FLAGS.items()):raise ValueError('equipped-car research cannot assert qualification')
    return dict(current=True,report_id=manifest['report_id'],structural_method=native['method_screen'],physical_accepted=False)
