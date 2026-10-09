#!/usr/bin/env python3
"""Export the executed C01–C14 audit with compact evidence and open gates."""
from pathlib import Path
import argparse
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'design/component-catalogue/src'))
from engineering.civil_exploration.contracts import load,encoded,sha,dependencies
from engineering.civil_exploration.workflow import verify

EVIDENCE={
 'C01':['requirements-register.json','reference-campaign/manifest.json'],
 'C02':['reference-campaign/manifest.json','search/input.json','search/checkpoint.json'],
 'C03':['option-register.json','family-screening.json'],
 'C04':['assembly/reference25.json'],
 'C05':['components/component-verification.json'],
 'C06':['detailed-confirmation.json','reference-campaign/manifest.json'],
 'C07':['components/nonlinear-pile.json','components/pier-pdelta.json','components/solid-pier-moment-curvature.json'],
 'C08':['construction-continuity-thermal.json','coupled-vehicle.json','coupled-vehicle-convergence.json'],
 'C09':['commercial.json'],
 'C10':['retrieval-verification.json','artifact-store/index.json','search/checkpoint.json'],
 'C11':['search/search.json','uncertainty/robustness.json'],
 'C12':['detailed-confirmation.json','components/orthotropic-coupon/result.json','components/friction-cycle.json','components/prestress.json'],
 'C13':['physical-test-programme/test-programme.json'],
 'C14':['promotion/proposal.json','promotion/seal.json']}
OPEN={
 'C01':['adopted project codes/limits','actual train/ground/material inputs','named acceptance owners'],
 'C02':['independent contract/configuration review'],
 'C03':['supplier sections, material properties and connection qualifications'],
 'C04':['accepted reinforcement/tendon/fabrication drawings'],
 'C05':['measured model applicability and blind physical validation'],
 'C06':['accepted project output specifications and limits'],
 'C07':['site calibration, nonlinear group/scour/liquefaction/seismic selection'],
 'C08':['supplier suspension/axle records and site-specific 3D/erection cases'],
 'C09':['actual charts, routes, productivity, quotations and maintenance/replacement costs'],
 'C10':['project custody/retention and independent environment replay'],
 'C11':['accepted constraints, costs and candidate-specific qualification'],
 'C12':['calibrated interface/anchorage/cyclic/deterioration models and independent checks'],
 'C13':['laboratories, specimens, procurement and actual instrumented tests'],
 'C14':['candidate-specific physical evidence, independent review and authority acceptance']}


def export(bundle):
    programme=load(bundle/'programme.json')
    if not programme['software_executed'] or not programme['numerical_verification_passed']:
        raise ValueError('programme execution/numerical verification incomplete')
    if programme['source_hashes']!=dependencies():raise ValueError('programme source is stale; export cannot assert currency')
    reference=verify(bundle/'reference-campaign')
    cases=[]
    for row in programme['work_packages']:
        evidence={path:sha(bundle/path) for path in EVIDENCE[row['id']]}
        cases.append(dict(id=row['id'],scope=row['scope'],software_delivery=row['software_delivery'],
                          evidence_hashes=evidence,remaining_acceptance=OPEN[row['id']],
                          engineering_acceptance='open',document_acceptance_complete=False))
    components=load(bundle/'components/component-verification.json')
    search=load(bundle/'search/search.json');uncertainty=load(bundle/'uncertainty/robustness.json')
    return dict(schema='osr-civil-programme-review/1',generator='tools/automation/export-civil-programme-review.py',
                generator_sha256=sha(Path(__file__)),consumer='engineering/analysis/tests/test_civil_exploration_programme_review.py',
                programme_sha256=sha(bundle/'programme.json'),source_hashes=programme['source_hashes'],
                work_packages=cases,all_document_items_complete=False,physical_release=False,
                component_verification=components,option_register=load(bundle/'option-register.json'),
                search=search,uncertainty=uncertainty,detailed_confirmation=load(bundle/'detailed-confirmation.json'),
                commercial=load(bundle/'commercial.json'),coupled_vehicle=load(bundle/'coupled-vehicle.json'),
                coupled_vehicle_convergence=load(bundle/'coupled-vehicle-convergence.json'),
                retrieval=load(bundle/'retrieval-verification.json'),physical_test_programme=load(bundle/'physical-test-programme/test-programme.json'),
                promotion=load(bundle/'promotion/proposal.json'),reference_evaluations=len(reference['evaluations']),
                native_environment=reference['environment'],qualified_feasible_pareto_set=[])


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('bundle',type=Path)
    parser.add_argument('--output',type=Path,default=ROOT/'engineering/civil_exploration/examples/programme-review.json')
    parser.add_argument('--check',action='store_true');args=parser.parse_args()
    try:
        result=export(args.bundle);data=encoded(result)
        if args.check:
            if args.output.read_bytes()!=data:raise ValueError('compact programme review stale')
        else:
            args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(data)
            lines=['# C01–C14 executed software and remaining acceptance','','This audit records the executed research software. It does not close physical or engineering acceptance.','',
                   '| ID | Software evidence | Remaining acceptance |','|---|---|---|']
            lines += [f"| {r['id']} — {r['scope']} | {r['software_delivery']} | {'; '.join(r['remaining_acceptance'])} |" for r in result['work_packages']]
            lines += ['',f"Native reference attempts: {result['reference_evaluations']}; component checks: {len(result['component_verification']['checks'])}; unique native search designs: {result['search']['unique_native_evaluations']}.",
                      '', 'Actual physical results received: zero. The sealed promotion proposal remains blocked.',
                      '', 'The companion `programme-review.json` retains exact source and native identities, evidence hashes, constraints, failure/domain states and conditional numerical results.','']
            args.output.with_suffix('.md').write_text('\n'.join(lines))
        print('C01–C14 review current; external acceptance remains open');return 0
    except (ValueError,OSError) as error:print(error,file=sys.stderr);return 1


if __name__=='__main__':raise SystemExit(main())
