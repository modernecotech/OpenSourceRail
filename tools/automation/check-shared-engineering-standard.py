#!/usr/bin/env python3
"""Apply the OpenSourceRail process standard to a frozen engineering review."""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import tomllib

ROOT=Path(__file__).resolve().parents[2]
STANDARD=ROOT/'engineering/assurance/standards/osr-eng-001.toml'


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def assess(review,standard):
    if review.get('schema')!='osr-shared-spatial-engineering-review/1':raise ValueError('unsupported engineering review schema')
    limits=standard['numerical'];rows=[]
    def add(key,category,passed,evidence):
        rows.append(dict(id='OSR-ENG-001-'+key,category=category,status='open' if passed is None else ('pass' if passed else 'fail'),
                         basis='OpenSourceRail internal rule',evidence=evidence))
    def bounded(value,limit):return type(value) in (int,float) and math.isfinite(value) and 0<=value<=limit
    spatial=review['spatial']
    for key in ('temporal_refinement','spatial_refinement'):
        checks=spatial[key]['checks']
        passed=bool(checks) and all(bounded(c['relative_change'],limits['refinement_relative_limit']) for c in checks.values())
        add(key,'numerical',passed,dict(checks=checks,maximum_relative_change=limits['refinement_relative_limit']))
    add('contact-work','numerical',all(bounded(c['contact_work_residual_w'],limits['contact_work_absolute_limit_w']) for c in spatial['cases']),
        dict(limit_w=limits['contact_work_absolute_limit_w']))
    add('adapter-domain','numerical',bool(spatial['cases']) and all(c['within_adapter_domain'] is True for c in spatial['cases']),
        dict(cases=[c['case'] for c in spatial['cases']]))
    beam=spatial['native_structure'];contact=spatial['contact_benchmark']
    add('independent-benchmarks','numerical',bounded(beam['native_relative_error'],limits['benchmark_relative_limit']) and
        bounded(beam['analytic_relative_error'],limits['benchmark_relative_limit']) and
        bounded(contact['sphere_halfspace_relative_error'],limits['benchmark_relative_limit']) and contact['passed'] is True,
        dict(native_beam=beam,contact=contact))
    joint=review['joint_mesh_refinement']
    add('joint-mesh','numerical',all(bounded(v,limits['refinement_relative_limit']) for v in joint['relative_changes'].values()),joint['relative_changes'])
    add('joint-equilibrium','numerical',all(bounded(r['force_equilibrium_relative_error'],limits['force_equilibrium_relative_limit']) and
        bounded(r['moment_equilibrium_relative_error'],limits['moment_equilibrium_relative_limit']) for r in joint['levels']),
        dict(force_limit=limits['force_equilibrium_relative_limit'],moment_limit=limits['moment_equilibrium_relative_limit']))
    add('native-assembly','numerical',review['native_assembly']['nominal_datums_reconciled'] is True and
        all(n>0 for n in review['native_assembly']['drawing_visible_edges'].values()),review['native_assembly'])
    correlation=review['synthetic_correlation'];climits=standard['correlation']
    add('identifiable-calibration','numerical',correlation['identifiable'] is True and correlation['optimisation_converged'] is True,
        dict(fitted_parameters=correlation['fitted_parameters'],sensitivity_rank=correlation['sensitivity_rank']))
    # RMS is already normalised sample-by-sample by the declared uncertainties.
    add('holdout-residual','numerical',bool(correlation['holdout_tests']) and all(bounded(r['standardised_rmse'],climits['standardised_holdout_rmse_limit']) for r in correlation['holdout_tests']),
        dict(limit=climits['standardised_holdout_rmse_limit'],holdout_tests=[r['test_id'] for r in correlation['holdout_tests']],
             physical_measurements_used=correlation['physical_measurements_used']))
    biases=[]
    for test in correlation['holdout_tests']:
        sigma=[(band[1]-band[0])/3.92 for band in test['measurement_95_percent_band']]
        if len(sigma)!=len(test['residual']) or not sigma or any(not math.isfinite(s) or s<=0 for s in sigma):
            raise ValueError('holdout bias requires aligned positive sample uncertainty')
        biases.append(abs(sum(r/s for r,s in zip(test['residual'],sigma))/len(sigma)))
    add('holdout-bias','numerical',bool(biases) and all(bounded(v,climits['standardised_absolute_holdout_bias_limit']) for v in biases),
        dict(standardised_absolute_biases=biases,limit=climits['standardised_absolute_holdout_bias_limit']))
    add('iso-method-conformity','physical',None,dict(required='controlled applicable full texts, edition/amendment/clauses and recorded conformity review',
        references=[r['id'] for r in standard['iso_references']]))
    add('complete-service-envelope','physical',None,dict(required=standard['service'],
        reason='short synthetic startup campaigns do not cover complete passages, comfort weighting or accepted railway force limits'))
    add('material-and-joint-resistance','physical',None,dict(required='measured material/connection resistance, fatigue/creep and all relevant limit states'))
    add('manufacturing-and-physical-correlation','physical',None,dict(required=standard['manufacturing'],
        reason='synthetic recovery and nominal CAD do not establish production or instrumented prototype acceptance'))
    return dict(schema='osr-internal-standard-assessment/1',standard_id=standard['id'],standard_version=standard['version'],
        requirements=rows,numerical_process_passed=all(r['status']=='pass' for r in rows if r['category']=='numerical'),
        iso_conformity='unassessed',physical_validation=False,engineering_released=False,
        open_gates=[r['id'] for r in rows if r['status']=='open'])


def governed_protocols(protocols,standard):
    result=deepcopy(protocols)
    result['governing_internal_standard']=dict(id=standard['id'],version=standard['version'])
    mapping={'part':['ISO 1101:2017','ISO 1920-4:2020','ISO 14125:1998','ISO 9712:2021'],
        'subassembly':['ISO 898-1:2013','ISO 16047:2005','ISO 5817:2023','ISO 15614-1:2017'],
        'train':['ISO 2631-4:2001','ISO/IEC 17025:2017','ISO 22163:2023'],
        'train-infrastructure':['ISO 2394:2015','ISO 22477-1:2018','ISO 12107:2012','ISO/IEC 17025:2017']}
    for level in result['levels']:
        level['adopted_standard']=standard['id']+'@'+standard['version']
        level['applicable_iso_references']=mapping[level['level']]
        level['iso_clause_review_complete']=False
        level['status']='prepared-under-internal-standard; physical execution and limit-state review open'
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--review',type=Path,required=True)
    p.add_argument('--protocols',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();standard=tomllib.loads(STANDARD.read_text());review=json.loads(a.review.read_text())
    if a.output.exists():raise ValueError('internal-standard assessment output already exists')
    a.output.mkdir(parents=True);report=assess(review,standard)
    report['evidence_sha256']={'standard':digest(STANDARD),'review':digest(a.review),'protocols':digest(a.protocols),'implementation':digest(__file__)}
    (a.output/'assessment.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n')
    (a.output/'protocols.json').write_text(json.dumps(governed_protocols(json.loads(a.protocols.read_text()),standard),indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(numerical_process_passed=report['numerical_process_passed'],iso_conformity='unassessed',engineering_released=False)))
    return 0 if report['numerical_process_passed'] else 2


if __name__=='__main__':raise SystemExit(main())
