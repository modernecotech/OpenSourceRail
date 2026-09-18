import importlib.util
import json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('city_batch',ROOT/'tools/automation/validate-city-batch.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)


def test_partitions_cover_each_city_once_independent_of_input_order():
    cities=[f'city-{i:03d}' for i in range(266)]
    parts=[b.partition(list(reversed(cities)),f'{i}/16') for i in range(16)]
    flattened=[city for part in parts for city in part]
    assert sorted(flattened)==cities
    assert len(flattened)==len(set(flattened))
    assert max(map(len,parts))-min(map(len,parts))<=1


@pytest.mark.parametrize('value',['-1/4','4/4','0/0','0/65','x/2','0/2/3'])
def test_invalid_partition_is_rejected(value):
    with pytest.raises(ValueError):b.partition(['city'],value)


def test_resume_requires_current_successful_bytes_and_same_scope(tmp_path):
    report=tmp_path/'validation.json';report.write_text(json.dumps(dict(passed=True)))
    inputs={'city.toml':'digest'}
    record=dict(inputs=inputs,resilience_required=True,passed=True,report_sha256=b.sha(report))
    (tmp_path/'execution.json').write_text(json.dumps(record))
    assert b.reusable(tmp_path,inputs,True)==record
    assert b.reusable(tmp_path,{'city.toml':'changed'},True) is None
    assert b.reusable(tmp_path,inputs,False) is None
    report.write_text(json.dumps(dict(passed=False)))
    assert b.reusable(tmp_path,inputs,True) is None
    record['report_sha256']=b.sha(report)
    (tmp_path/'execution.json').write_text(json.dumps(record))
    assert b.reusable(tmp_path,inputs,True) is None


def test_resume_rejects_changed_generated_candidate_or_design(tmp_path):
    folder=tmp_path/'sample';folder.mkdir()
    report=folder/'validation.json';report.write_text(json.dumps(dict(passed=True)))
    scenario=folder/'sample.toml';scenario.write_text('scenario')
    design=folder/'design.toml';design.write_text('design')
    inputs={'canonical-design':'digest'}
    record=dict(city='sample',scenario_basis='generator-candidate',inputs=inputs,
                resilience_required=False,passed=True,report_sha256=b.sha(report),
                tested_scenario_sha256=b.sha(scenario),design_sha256=b.sha(design))
    (folder/'execution.json').write_text(json.dumps(record))
    assert b.reusable(folder,inputs,False,'generator-candidate')==record
    scenario.write_text('modified candidate')
    assert b.reusable(folder,inputs,False,'generator-candidate') is None
    scenario.write_text('scenario');design.write_text('modified design')
    assert b.reusable(folder,inputs,False,'generator-candidate') is None
