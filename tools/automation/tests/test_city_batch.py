import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('city_batch',ROOT/'tools/automation/validate-city-batch.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)


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
