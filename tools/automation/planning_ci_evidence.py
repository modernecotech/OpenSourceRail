"""Check retained metadata after the importer verified actual CI output files.

The tested executable remains the CI executable. A local build can have a
different hash because build paths differ; neither executable is retagged.
This check establishes source currency, rather than physical acceptance.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import tomllib

ROOT=Path(__file__).resolve().parents[2]


def _verifier():
    spec=importlib.util.spec_from_file_location('retained_planning_ci',ROOT/'tools/automation/city-planning-ci.py')
    ci=importlib.util.module_from_spec(spec);spec.loader.exec_module(ci)
    return ci


def current(design: Path, report_path: Path) -> bool:
    record_path=report_path.with_name('ci-execution.json')
    if not record_path.is_file():return False
    try:
        ci=_verifier();slug=tomllib.loads(design.read_text())['city']['slug']
        record=json.loads(record_path.read_text());report=json.loads(report_path.read_text())
        if (record.get('schema')!=ci.SCHEMA or record.get('passed') is not True
                or record.get('exit_code')!=0 or record.get('inputs_unchanged') is not True
                or record.get('physical_release') is not False or record.get('operating_release') is not False
                or len(record.get('commit',''))!=40 or record.get('city')!=slug or record.get('inputs')!=ci.inputs(design)
                or record.get('report_sha256')!=ci.batch.sha(report_path)
                or report.get('design_sha256')!=ci.batch.sha(design)
                or report.get('scenario_sha256')!=ci.batch.sha(design.parent/(slug+'.toml'))
                or report.get('generator_sha256')!=ci.batch.sha(ROOT/'tools/automation/validate-city-simulation.py')
                or report.get('trainset_contract',{}).get('passed') is not True
                or report.get('passed') is not True or report.get('resilience_required') is not True
                or report.get('resilience_passed') is not True):return False
        runs=report.get('runs',[]);cases=report.get('resilience_cases',[])
        if len(runs)!=2 or runs[-1].get('duration_s')!=90000 or len(cases)!=8:return False
        if len({c['label'] for c in cases})!=8:return False
        for case in runs+cases:
            receipt=case['execution_receipt'];inputs=receipt['inputs']
            key=hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()
            if (receipt.get('cache_key')!=key or inputs.get('simulator_sha256')!=report['simulator_sha256']
                    or inputs.get('duration_s')!=case['duration_s'] or inputs.get('compact_json') is not True
                    or inputs.get('ma_check_every')!=0 or len(receipt.get('output_sha256',''))!=64):return False
            if case in cases and (case.get('duration_s')!=90000 or case.get('passed') is not True):return False
            if case in runs and inputs.get('scenario_sha256')!=report['scenario_sha256']:return False
        return True
    except (OSError,ValueError,KeyError,TypeError):
        return False
