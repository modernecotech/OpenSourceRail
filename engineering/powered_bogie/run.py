"""Frozen-source private runs, retaining failed space/native executions."""
from copy import deepcopy
from pathlib import Path
import argparse
import gzip
import json
import platform
import subprocess
import time

from engineering.station_rail.common import identity, encoded, digest
from engineering.vehicle_installation import export, model
from . import FLAGS, ROOT
from . import design, geometry


def _write(path,value):
    path.write_bytes(encoded(value))


def bogie_preview(result):
    """Presentation subset, with positive external mass ownership retained."""
    view=deepcopy(result)
    view['patterns']=[r for r in view['patterns'] if r['bogie_index']==0]
    for e in result['external_drive_placements'][:2]:
        r=dict(id=e['id'],part_id='external/'+e['hardware'],source_part_id=None,
            assembly_id='external-installed-drive-inventory',assembly_occurrence_id='bogie0',
            car_allocation=[[0,1.]],bogie_index=0,count=1,positions_m=[e['centroid_m']],
            rotation=model.I,geometry=dict(kind='envelope',size_m=e['size_m'],
                source_stock=dict(kind='envelope',size_m=e['size_m']),
                exact_stock=False,definition_basis='OSR necessary-space envelope; actual supplier dimensions unknown'),
            material_id='external-drive',mass_kg=e['mass_kg'],
            mass_owner='external-installed-drive-inventory',not_added_to_body_BOM=True)
        view['patterns'].append(r)
    view['total_occurrences']=sum(r['count'] for r in view['patterns'])
    return view


def run(output,*,cad=False,root=ROOT):
    root=Path(root);folder=Path(output).resolve();folder.mkdir(parents=True,exist_ok=False)
    before=design.sources(root);start=time.monotonic()
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    tracked=subprocess.check_output(['git','diff','--name-only','HEAD','--',
        'engineering/powered_bogie','tests/test_powered_bogie.py'],cwd=root,text=True).strip()
    if tracked:raise ValueError('Freeze and commit producer source before running')
    _write(folder/'request.json',dict(schema='osr-powered-bogie-run-request/1',
        source_commit=commit,source_before=before,limits=design.policy(root)['limits'],cad=cad,
        command=f'python -m engineering.powered_bogie.run {folder}'+(' --cad' if cad else ''),
        actual_isolation='Separate Git worktree and private run directory; native wrapper resource/process controls only. No claim of source filesystem read-only enforcement.',**FLAGS))
    parent=design.parent(root)
    (folder/'input-body.json.gz').write_bytes(gzip.compress(encoded(parent),mtime=0))
    variants=[]
    for variant in design.policy(root)['variant_ids']:
        body=design.build(parent,variant_id=variant,root=root)
        report=geometry.evaluate(body)
        own=folder/variant;own.mkdir()
        (own/'body.json.gz').write_bytes(gzip.compress(encoded(body),mtime=0))
        _write(own/'geometry.json',report)
        _write(own/'change-set.json',dict(candidate_id=body['candidate_id'],
            body_evaluation_id=body['evaluation_id'],parent_candidate_id=parent['candidate_id'],
            stock_change=body['change_set'],BOP_partition=body['BOP_partition'],
            external_drive_placements=body['external_drive_placements'],**FLAGS))
        if variant=='extended-cradle-3240':
            _write(own/'stock-case.json',geometry.stock_case(body))
            _write(own/'preview.json',export.preview_glb(bogie_preview(body),own/'bogie.glb'))
            if cad:
                try:
                    native=export.native_cad(body,own/'native-cad',case=geometry.stock_case(body))
                    # Do not rewrite the legacy native receipt. This enclosing
                    # immutable record supplies the full new producer context.
                    native_result=dict(status='completed',native_receipt=native,
                        exact_source_sha256=before,source_commit=commit,
                        candidate_id=body['candidate_id'],geometry_evaluation_id=report['evaluation_id'],**FLAGS)
                except Exception as exc:
                    native_result=dict(status='failed',failure_type=type(exc).__name__,
                        failure_reason=str(exc),candidate_id=body['candidate_id'],
                        exact_source_sha256=before,**FLAGS)
                native_result['evaluation_id']=identity(native_result)
                _write(own/'native-result.json',native_result)
        variants.append(dict(variant_id=variant,candidate_id=body['candidate_id'],
            body_evaluation_id=body['evaluation_id'],geometry_evaluation_id=report['evaluation_id'],
            mass_delta_kg=body['change_set']['mass_delta_kg'],cost_delta_usd=body['change_set']['cost_delta_usd'],
            BOP_partition=body['BOP_partition'],
            conflicts={d['hardware']:len(d['required_space_conflicts']) for d in report['drives']},
            body_sweep_holds={d['hardware']:len(d['continuous_body_or_battery_holds']) for d in report['drives']},
            geometry_status=report['geometry_screen_status']))
    after=design.sources(root)
    summary=dict(schema='osr-powered-bogie-run/1',source_commit=commit,
        source_before=before,source_after=after,source_integrity_passed=before==after,
        input_candidate_id=parent['candidate_id'],input_evaluation_id=parent['evaluation_id'],
        variants=variants,wall_s=time.monotonic()-start,python=platform.python_version(),
        execution='completed' if before==after else 'source-drift',numerical_validity='bounded analytic geometry and counted stock only',
        geometry_screen='HOLD; failed allocation trials retained, no supplier fit, frame strength or installed acceptance',
        selection_purpose='Next supplier drawing and structural/detailing experiment only',**FLAGS)
    _write(folder/'summary.json',summary)
    manifest=dict(schema='osr-powered-bogie-artifacts/1',summary=summary,
        files_sha256={p.relative_to(folder).as_posix():digest(p) for p in sorted(folder.rglob('*')) if p.is_file()},**FLAGS)
    manifest['evaluation_id']=identity(manifest);_write(folder/'manifest.json',manifest)
    if before!=after:raise ValueError('Source drift; retain failed execution without publishing')
    return manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path);parser.add_argument('--cad',action='store_true')
    args=parser.parse_args();r=run(args.output,cad=args.cad)
    print(json.dumps(dict(manifest_id=r['evaluation_id'],summary=r['summary']),sort_keys=True))


if __name__=='__main__':main()
