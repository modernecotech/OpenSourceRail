"""Historical native caches reject altered bytes, mixed builds and incomplete cases."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('native_seed',ROOT/'tools/automation/seed-native-planning-cache.py')
seed=importlib.util.module_from_spec(spec);spec.loader.exec_module(seed)


def fixture(tmp_path):
    folder=tmp_path/'fixture';(folder/'native-runs').mkdir(parents=True)
    def case(label,duration):
        inputs=dict(simulator_sha256='a'*64,scenario_sha256=seed.sha(label.encode()),
                    duration_s=duration,compact_json=True,ma_check_every=0)
        key=seed.sha(json.dumps(inputs,sort_keys=True).encode())
        raw=json.dumps({'synthetic_test_fixture':True,'label':label}).encode()
        (folder/'native-runs'/(key+'.json')).write_bytes(raw)
        return dict(label=label,duration_s=duration,passed=True,
                    execution_receipt=dict(inputs=inputs,cache_key=key,output_sha256=seed.sha(raw)))
    runs=[case('nominal',1),case('nominal',90000)]
    report=dict(simulator_sha256='a'*64,scenario_sha256=seed.sha(b'nominal'),runs=runs,
                resilience_cases=[case('case-'+str(i),90000) for i in range(8)],
                passed=True,resilience_required=True,resilience_passed=True,trainset_contract={'passed':True})
    (folder/'validation.json').write_text(json.dumps(report))
    record=dict(schema='osr-city-planning-ci/1',passed=True,exit_code=0,inputs_unchanged=True,
                report_sha256=seed.sha((folder/'validation.json').read_bytes()))
    return folder,record,report


def test_complete_receipts_and_altered_native_bytes(tmp_path):
    folder,record,report=fixture(tmp_path)
    assert len(seed.checked_cases(folder,record,report))==10
    key=report['runs'][0]['execution_receipt']['cache_key']
    (folder/'native-runs'/(key+'.json')).write_bytes(b'altered')
    with pytest.raises(ValueError,match='differs from receipt'):seed.checked_cases(folder,record,report)


def test_incomplete_case_set_and_mixed_executable_are_rejected(tmp_path):
    folder,record,report=fixture(tmp_path)
    report['resilience_cases'][0]['label']=report['resilience_cases'][1]['label']
    with pytest.raises(ValueError,match='Incomplete'):seed.checked_cases(folder,record,report)
    report['resilience_cases'][0]['label']='case-0'
    report['simulator_sha256']='b'*64
    with pytest.raises(ValueError,match='differs from receipt'):seed.checked_cases(folder,record,report)
