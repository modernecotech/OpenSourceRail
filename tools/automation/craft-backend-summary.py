#!/usr/bin/env python3
"""Publish a compact comparison receipt; keep bulky native evidence private."""
from pathlib import Path
import argparse
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from engineering.design_search.craft_backends import native,pilot


def main():
    args=argparse.ArgumentParser()
    args.add_argument('--run',required=True);args.add_argument('--output',required=True)
    a=args.parse_args();folder=Path(a.run).resolve()
    verified=pilot.verify(folder,root=ROOT)
    manifest=json.loads((folder/'manifest.json').read_bytes())
    request=json.loads((folder/'request.json').read_bytes())
    rows=[]
    for c in request['cases']:
        stage=manifest['stages'][c['case_id']];r=stage.get('result',{})
        checks=r.get('checks',{});parts=checks.get('exact_step',{}).get('parts',[])
        rows.append(dict(case_id=c['case_id'],candidate_id=c['candidate_id'],component_geometry_id=c['component_geometry_id'],
            occurrences=c['expected']['part_count'],volume_m3=c['expected']['total_volume_m3'],
            material_mass_kg=c['expected']['total_material_mass_kg'],status=stage['status'],
            geometry_comparison_passed=r.get('geometry_comparison_passed'),
            maximum_exact_volume_relative_error=max([p['relative_volume_error'] for p in parts],default=None),
            maximum_exact_position_error_m=max([p['maximum_position_error_m'] for p in parts],default=None),
            native_step_names_preserved=r.get('native_step_names_preserved'),
            fieldcraft_geometry_names_and_units_verified=r.get('fieldcraft_interchange',{}).get('geometry_names_and_units_verified')))
    numerical=manifest['stages']['linear-controls'].get('result',{})
    rc=manifest['stages'].get('prerelease-interchange',{}).get('result',{})
    result=dict(schema='osr-craft-pilot-summary/1',result_id=manifest['result_id'],evaluation_id=manifest['evaluation_id'],
        producer_sha256=native.digest(__file__),source_sha256=request['source_sha256'],
        toolchain={k:{n:v[n] for n in ('version','commit','asset_sha256','binary_sha256')} for k,v in request['toolchain']['tools'].items()},
        software_pilot_passed=verified['software_pilot_passed'],integrity_verified=verified['integrity_verified'],
        elapsed_s=manifest['elapsed_s'],measurements=manifest['measurements'],cases=rows,
        numerical=dict(coarse_theory_relative_error=numerical.get('coarse',{}).get('relative_theory_error'),
            fine_theory_relative_error=numerical.get('fine',{}).get('relative_theory_error'),
            refinement=numerical.get('refinement'),cross_solver=numerical.get('cross_solver'),
            geometry_face_set_reopen_verified=manifest['stages']['asymmetric-si-control'].get('result',{}).get('fieldcraft_interchange',{}).get('named_face_set_reopen_verified')),
        compatibility=dict(stable_direct_geometry_open='verified on all four cases',
            convenience_sc_open='rejected; direct geometry.open used without renaming',
            prerelease_direct_geometry_open=rc.get('direct_native_interchange',{}).get('direct_geometry_open'),
            tagged_surface_imported=bool(rc.get('tagged_mesh_import')),
            material_definitions_automatically_transferred=False,native_step_import_name_retention='held; generic FreeCAD product labels'),
        raw_evidence=dict(manifest_sha256=native.digest(folder/'manifest.json'),request_sha256=native.digest(folder/'request.json'),
            artifact_inventory_id=pilot.identity(manifest['artifact_sha256']),file_count=len(manifest['artifact_sha256']),
            location='Private immutable run directory supplied to the generator; full evidence not duplicated in Git'),
        limits=request['policy'],default_backends_changed=False,engineering_component_analysis_complete=False,**pilot.FLAGS)
    native.write(a.output,result)
    print(json.dumps(dict(output=a.output,result_id=result['result_id'],software_pilot_passed=result['software_pilot_passed'])))


if __name__=='__main__':main()
