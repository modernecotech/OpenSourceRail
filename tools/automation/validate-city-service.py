#!/usr/bin/env python3
"""Run the existing simulation suite with additional per-line promotion gates.

The legacy validator retains its aggregate software contract. This adapter
captures its native per-line observations and applies stricter acceptance to a
separate report. Batch/catalogue qualification uses this entry point.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import tomllib

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('simulation_suite',ROOT/'tools/automation/validate-city-simulation.py')
suite=importlib.util.module_from_spec(spec);spec.loader.exec_module(suite)
from osr_scenario.service_acceptance import line_service_screen, configured_passenger_capacity


def qualify(report,design,scenario):
    report['aggregate_software_passed']=report['passed']
    full=report['runs'][-1]
    minimum=report['model']['minimum_service_completion_ratio']
    tolerance=report['model']['service_completion_numerical_tolerance']
    full['line_service']=line_service_screen(design,scenario,full.get('per_line_km',[]),minimum,tolerance)
    for case in report['resilience_cases']:
        case['aggregate_software_passed']=case['passed']
        case['line_service']=line_service_screen(design,scenario,case.get('per_line_km',[]),case['minimum_service_completion_ratio'],tolerance)
        case['passed']=case['aggregate_software_passed'] and case['line_service']['passed']
    if report['resilience_required']:
        report['resilience_passed']=bool(report['resilience_cases']) and all(c['passed'] for c in report['resilience_cases'])
    report['full_window_passed']=full['duration_s']>=90000
    report['passed']=(report['aggregate_software_passed'] and report['full_window_passed'] and full['line_service']['passed']
        and (not report['resilience_required'] or report['resilience_passed']))
    report['passenger_capacity']=configured_passenger_capacity(scenario)
    report['operating_release']=False
    report['service_acceptance_schema']='osr-city-service-qualification/1'
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__,add_help=False)
    parser.add_argument('--scenario',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args,_=parser.parse_known_args()
    scenario=args.scenario.resolve();output=args.output.resolve()
    if output==scenario.parent/'engineering/simulation/validation-summary.json':
        raise ValueError('Keep line qualification separate from the legacy aggregate report')
    paths=[Path(__file__).resolve(),ROOT/'tools/automation/validate-city-simulation.py',
        ROOT/'design/city-generation/src/osr_scenario/service_acceptance.py',
        ROOT/'design/city-generation/src/osr_scenario/network_readme.py',scenario,scenario.parent/'design.toml']
    before={str(p.relative_to(ROOT)):suite.sha256(p) for p in paths}
    # Preserve the existing suite, variant generation and physics checks. The
    # decorator retains native observations its legacy summary does not use.
    original=suite.summarize_result
    def with_line_observations(label,duration,result,*expected):
        summary=original(label,duration,result,*expected)
        summary['per_line_km']=result.get('per_line_km',[])
        return summary
    suite.summarize_result=with_line_observations
    try:
        suite.main()
    finally:
        suite.summarize_result=original
    report=json.loads(output.read_text())
    qualify(report,tomllib.loads((scenario.parent/'design.toml').read_text()),tomllib.loads(scenario.read_text()))
    report['qualification_source_sha256']=before
    report['qualification_inputs_unchanged']=all(suite.sha256(ROOT/p)==value for p,value in before.items())
    report['passed']=report['passed'] and report['qualification_inputs_unchanged']
    output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(f"Per-line qualification: {output} (passed={report['passed']}; operating_release=False)")
    return 0 if report['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
