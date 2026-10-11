#!/usr/bin/env python3
"""Compare archived timestep probes with the current guarded contact-domain run."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from osr_mech.engineering_definition import load_definition


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--coarse',type=Path,required=True);p.add_argument('--fine',type=Path,required=True)
    p.add_argument('--guarded-audit',type=Path,required=True);p.add_argument('--guarded-evidence',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('comparison output exists; retain previous evidence')
    paths=[path.resolve() for path in (a.coarse,a.fine,a.guarded_audit,a.guarded_evidence)]
    if any(not path.is_relative_to(ROOT) for path in paths):raise ValueError('comparison inputs must be inside the controlled repository')
    coarse,fine,guard,evidence=[load_definition(path) for path in paths]
    identity=coarse['hardware_definition_sha256'];configuration=coarse['configuration_sha256']
    if any(r['hardware_definition_sha256']!=identity or r['configuration_sha256']!=configuration for r in (fine,guard)) or evidence['configuration_sha256']!=identity:
        raise ValueError('contact comparisons need identical hardware and operating inputs')
    for audit in (coarse,fine,guard):
        if not audit['producer_sources_verified']:raise ValueError('contact audit producer sources were not verified')
        for relative,digest in audit['audit_sources_sha256'].items():
            if sha(ROOT/relative)!=digest:raise ValueError('contact audit source changed: '+relative)
    c=coarse['first_footprint_exceedance'];f=fine['first_footprint_exceedance']
    cb,fb,gb=(r['campaign_budgets'] for r in (coarse,fine,guard))
    if fb['time_step_s']!=cb['time_step_s']/2 or gb['time_step_s']!=cb['time_step_s'] or any(fb[k]!=cb[k] or gb[k]!=cb[k] for k in ('deck_mesh','rail_step_m')):
        raise ValueError('independent timestep comparison needs identical meshes and a halved timestep')
    if c is None or f is None or guard['first_footprint_exceedance'] is not None or not guard['all_retained_footprints_inside_supplied_profiles']:
        raise ValueError('comparison does not establish a supported guarded prefix')
    cases=evidence['service']['cases']
    if len(cases)!=1 or cases[0]['status']!='outside-model-domain' or cases[0]['time_s']!=c['time_s']:
        raise ValueError('guarded case must reject at the independently replayed boundary')
    detail=next(d for d in cases[0]['domain_details'] if d['kind']=='contact-footprint')
    if (detail['train'],detail['wheelset'],detail['side'])!=(c['train'],c['wheelset'],c['side']) or detail['minimum_clearance_m']!=c['minimum_clearance_m']:
        raise ValueError('guarded physical diagnostic differs from the retained coarse contact')
    result=dict(schema='osr-contact-domain-comparison/1',hardware_definition_sha256=identity,configuration_sha256=configuration,
        input_sha256={str(path.relative_to(ROOT)):sha(path) for path in paths},
        publisher_sha256=sha(Path(__file__)),archived_probe_first_exceedances=dict(coarse=c,time_refined=f),
        probe_time_steps_s=dict(coarse=cb['time_step_s'],time_refined=fb['time_step_s'],guarded=gb['time_step_s']),
        boundary_time_difference_s=abs(c['time_s']-f['time_s']),
        boundary_normal_force_relative_difference=abs(c['normal_n']-f['normal_n'])/c['normal_n'],
        guarded_case_status=cases[0]['status'],guarded_stop_time_s=cases[0]['time_s'],
        last_committed_supported_time_s=guard['last_retained_time_s'],supported_sample_count=guard['sample_count'],
        supported_contact_check_count=guard['contact_check_count'],unsupported_contact_states_committed=0,
        completed_full_family_passages=0,numerical_time_and_mesh_confirmation_performed=False,
        physical_validation=False,engineering_released=False,
        conclusion='The same profile-boundary exceedance occurs in both archived timestep probes; the current guard rejects it before commitment. Full service qualification remains open.')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(boundary_time_difference_s=result['boundary_time_difference_s'],unsupported_contact_states_committed=0,physical_validation=False)))


if __name__=='__main__':main()
