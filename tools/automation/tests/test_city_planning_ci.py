"""CI imports require unchanged sources and every actual native output receipt."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('planning_ci',ROOT/'tools/automation/city-planning-ci.py')
ci=importlib.util.module_from_spec(spec);spec.loader.exec_module(ci)


@pytest.fixture
def evidence(tmp_path,monkeypatch):
    design=tmp_path/'design.toml';design.write_text('[city]\nslug="example"\n')
    scenario=tmp_path/'example.toml';scenario.write_text('[scenario]\nname="Example"\n')
    monkeypatch.setattr(ci,'inputs',lambda _: {'source':'current'})
    report=dict(passed=True,simulator_sha256='actual-build',design_sha256=ci.batch.sha(design),
                scenario_sha256=ci.batch.sha(scenario),generator_sha256=ci.batch.sha(ROOT/'tools/automation/validate-city-simulation.py'),
                trainset_contract={'passed':True},resilience_required=True,resilience_passed=True,runs=[],resilience_cases=[])
    folder=tmp_path/'example';(folder/'native-runs').mkdir(parents=True)
    for index,duration in enumerate([7200,90000]+[90000]*8):
        inputs=dict(simulator_sha256='actual-build',scenario_sha256=ci.batch.sha(scenario) if index<2 else f'variant-{index}',
                    duration_s=duration,compact_json=True,ma_check_every=0)
        key=hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()
        raw=folder/'native-runs'/(key+'.json');raw.write_text(json.dumps({'fixture_case':index}))
        case=dict(label=str(index),duration_s=duration,passed=True,execution_receipt=dict(inputs=inputs,cache_key=key,output_sha256=ci.batch.sha(raw)))
        report['runs' if index<2 else 'resilience_cases'].append(case)
    record=dict(schema=ci.SCHEMA,city='example',commit='recorded-commit',exit_code=0,inputs_unchanged=True,passed=True,inputs={'source':'current'})
    def write():
        (folder/'validation.json').write_text(json.dumps(report));record['report_sha256']=ci.batch.sha(folder/'validation.json')
        (folder/'execution.json').write_text(json.dumps(record))
    write();return folder,design,report,record,write


def test_complete_source_bound_ci_evidence_is_accepted(evidence):
    folder,design,*_=evidence
    record,report=ci.verify(folder,design,'recorded-commit')
    assert record['passed'] and len(report['resilience_cases'])==8


@pytest.mark.parametrize('defect',['source','commit','failed','missing-case','mixed-build','wrong-scenario','duplicate-case'])
def test_stale_incomplete_or_mixed_ci_evidence_is_rejected(evidence,defect):
    folder,design,report,record,write=evidence
    if defect=='source':record['inputs']['source']='old'
    elif defect=='commit':record['commit']='other-commit'
    elif defect=='failed':report['resilience_cases'][0]['passed']=False
    elif defect=='missing-case':report['resilience_cases'].pop()
    elif defect=='mixed-build':report['resilience_cases'][0]['execution_receipt']['inputs']['simulator_sha256']='other-build'
    elif defect=='wrong-scenario':report['runs'][-1]['execution_receipt']['inputs']['scenario_sha256']='other-scenario'
    else:report['resilience_cases'][1]['label']=report['resilience_cases'][0]['label']
    write()
    with pytest.raises(ValueError):ci.verify(folder,design,'recorded-commit')


def test_native_output_cannot_be_changed_after_its_receipt(evidence):
    folder,design,report,*_=evidence
    key=report['resilience_cases'][0]['execution_receipt']['cache_key']
    (folder/'native-runs'/(key+'.json')).write_text('{"tampered":true}')
    with pytest.raises(ValueError,match='Native output'):
        ci.verify(folder,design,'recorded-commit')
