"""Portable CI evidence remains tied to the tested build and current sources."""
import importlib.util
import json
from pathlib import Path

import pytest
from test_city_planning_ci import ci, evidence

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('retained_ci',ROOT/'tools/automation/planning_ci_evidence.py')
proof=importlib.util.module_from_spec(spec);spec.loader.exec_module(proof)


@pytest.fixture
def retained(evidence,monkeypatch):
    folder,design,report,record,write=evidence
    record.update(commit='c'*40,physical_release=False,operating_release=False)
    def save():
        write();(folder/'ci-execution.json').write_text(json.dumps(record))
    monkeypatch.setattr(proof,'_verifier',lambda:ci)
    save();return folder,design,report,record,save


def test_current_ci_build_is_not_retagged_as_a_local_executable(retained):
    folder,design,report,*_=retained
    assert proof.current(design,folder/'validation.json')
    assert report['simulator_sha256']=='actual-build'


@pytest.mark.parametrize('defect',['source','report','case','build','city','release','missing-proof'])
def test_retained_ci_metadata_rejects_changes_and_incomplete_evidence(retained,defect):
    folder,design,report,record,save=retained
    if defect=='source':record['inputs']['source']='different'
    elif defect=='report':report['design_sha256']='different'
    elif defect=='case':report['resilience_cases'].pop()
    elif defect=='build':report['simulator_sha256']='different'
    elif defect=='city':record['city']='other-city'
    elif defect=='release':record['operating_release']=True
    save()
    if defect=='missing-proof':(folder/'ci-execution.json').unlink()
    assert not proof.current(design,folder/'validation.json')


def test_report_cannot_change_after_its_import_receipt(retained):
    folder,design,report,record,_=retained
    report['model']='tampered'
    (folder/'validation.json').write_text(json.dumps(report))
    assert not proof.current(design,folder/'validation.json')
