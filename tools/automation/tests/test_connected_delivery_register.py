import hashlib
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/automation'))
from connected_delivery_register import build_register


def test_all_review_areas_are_traced_without_inventing_appointments():
    report=build_register(ROOT,[])
    assert len(report['requirements'])==20
    assert all(row['appointed_person'] is None and not row['physical_or_commercial_release'] for row in report['requirements'])
    assert not report['engineering_release']


def test_receipt_validity_does_not_authenticate_an_authority(tmp_path):
    path=tmp_path/'evidence.txt';path.write_text('test-only record')
    record=dict(id='record',requirement_id='R07',path='evidence.txt',sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        scope_revision='test-revision',authority='test-only',independent_reviewer='test-only')
    report=build_register(tmp_path,[record])
    assert not report['records'][0]['authority_verified_by_generator']
    assert report['requirements'][6]['acceptance_status']=='evidence-entered-authority-verification-required'
    path.write_text('changed')
    with pytest.raises(ValueError,match='receipt drift'):build_register(tmp_path,[record])
