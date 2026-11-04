"""Retained benchmark cohorts exclude later cache users without hiding gaps."""
import gzip
import hashlib
import importlib.util
from pathlib import Path

import pytest


path=Path(__file__).resolve().parents[3]/"tools/automation/benchmark-campaign-serialization.py"
spec=importlib.util.spec_from_file_location("campaign_serialization_benchmark",path)
benchmark=importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)


def record(folder,*,runtime="measured",definition="definition",source="original",extra=None):
    request=dict(runtime=dict(numpy=runtime),source_sha256={"producer":source},retained_equipment_sources={})
    if extra is not None:
        request["extra"]=extra
    value=dict(request=request,candidate=dict(candidate_id="candidate",definition_id=definition))
    value["record_id"]=hashlib.sha256(benchmark.encoded(value)).hexdigest()
    path=folder/(hashlib.sha256(benchmark.encoded(request)).hexdigest()+".json.gz")
    path.write_bytes(gzip.compress(benchmark.encoded(value),mtime=0))
    return path


def run():
    return dict(contract=dict(runtime=dict(numpy="measured")),sources={"producer":"original"},
        evaluations=[dict(candidate_id="candidate",definition_id="definition")],attempts=[])


def test_later_runtime_and_source_contexts_do_not_contaminate_retained_measurement(tmp_path):
    expected=record(tmp_path)
    record(tmp_path,runtime="later-python-numpy")
    record(tmp_path,source="later-producer")
    records,metadata=benchmark.geometry_cohort(tmp_path,[run(),run()])
    assert list(records)==[expected.name]
    assert metadata["expected_definition_runtime_pairs"]==metadata["selected_records"]==1
    assert metadata["ignored_other_context_records"]==2
    assert metadata["compressed_bytes"]==expected.stat().st_size


def test_complete_expected_definition_coverage_is_required(tmp_path):
    record(tmp_path,runtime="later-python-numpy")
    with pytest.raises(ValueError,match="coverage incomplete"):
        benchmark.geometry_cohort(tmp_path,[run()])


def test_ambiguous_same_definition_runtime_records_are_rejected(tmp_path):
    record(tmp_path)
    record(tmp_path,extra="different-request")
    with pytest.raises(ValueError,match="Ambiguous"):
        benchmark.geometry_cohort(tmp_path,[run()])


def test_selected_record_identity_is_verified(tmp_path):
    path=record(tmp_path)
    path.write_bytes(gzip.compress(gzip.decompress(path.read_bytes()).replace(b'"record_id":"',b'"record_id":"f')))
    with pytest.raises(ValueError,match="identity differs"):
        benchmark.geometry_cohort(tmp_path,[run()])

