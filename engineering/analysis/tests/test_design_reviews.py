"""Appointments and data verification cannot become engineering acceptance."""
from pathlib import Path
import hashlib
import pytest

from engineering.design_engine.store import Store
from engineering.design_engine.review import ReviewStore


def record(tmp_path):
    root=tmp_path/'evidence';root.mkdir();document=root/'appointment.txt';document.write_text('retained appointment record')
    payload=dict(person_name='Test appointment fixture',organization='Test organization',role='test executor',
        appointment_scope='samawah simulation research only',valid_until='2099-01-01',
        identity_reference=dict(path='appointment.txt',sha256=hashlib.sha256(document.read_bytes()).hexdigest()))
    store=ReviewStore(Store(tmp_path/'store'));row=store.submit('samawah','simulation','appointment',payload,'author','unique-key-0001')
    return store,row,root,payload


def actor(name='reviewer',cities=None):return dict(username=name,roles=['approver'],city_scopes=cities or ['samawah'])


def test_verified_record_preserves_separate_author_and_does_not_release_design(tmp_path):
    store,row,root,_=record(tmp_path)
    result=store.verify(row['id'],row['revision'],actor(),city='samawah',environment='simulation',evidence_root=root)
    assert result['reviewer']=='reviewer'
    assert result['physical_release']is False and result['independent_acceptance']is False
    assert result['technical_applicability_accepted']is False
    assert store.list('samawah','simulation')[0]['state']=='verified-record'
    with pytest.raises(ValueError):store.verify(row['id'],row['revision'],actor(),city='samawah',environment='simulation',evidence_root=root)


@pytest.mark.parametrize('fault',['self-review','wrong-city','wrong-environment','stale-revision','changed-file','outside-path','expired','missing'])
def test_incomplete_stale_mis_scoped_or_self_reviewed_records_fail(tmp_path,fault):
    store,row,root,payload=record(tmp_path)
    reviewer=actor();city='samawah';environment='simulation';revision=row['revision']
    if fault=='self-review':reviewer=actor('author')
    elif fault=='wrong-city':city='mosul';reviewer=actor(cities=['mosul'])
    elif fault=='wrong-environment':environment='physical'
    elif fault=='stale-revision':revision='old'
    elif fault=='changed-file':(root/'appointment.txt').write_text('altered')
    elif fault in {'outside-path','expired','missing'}:
        if fault=='outside-path':payload['identity_reference']['path']='../private-key'
        elif fault=='expired':payload['valid_until']='2000-01-01'
        else:payload['person_name']=None
        row=store.submit('samawah','simulation','appointment',payload,'author','unique-key-0002');revision=row['revision']
    with pytest.raises((ValueError,PermissionError)):
        store.verify(row['id'],revision,reviewer,city=city,environment=environment,evidence_root=root)


def test_lost_reply_repeated_submission_is_idempotent_but_changed_content_is_not(tmp_path):
    store,row,root,payload=record(tmp_path)
    assert store.submit('samawah','simulation','appointment',payload,'author','unique-key-0001')['id']==row['id']
    payload['role']='another role'
    with pytest.raises(ValueError,match='idempotency'):store.submit('samawah','simulation','appointment',payload,'author','unique-key-0001')


def test_navigation_role_or_request_approval_flag_cannot_verify_a_record(tmp_path):
    store,row,root,payload=record(tmp_path)
    with pytest.raises(PermissionError):store.verify(row['id'],row['revision'],dict(role='reviewer'),city='samawah',environment='simulation',evidence_root=root)
    payload['physical_release']=True
    with pytest.raises(ValueError):store.submit('samawah','simulation','appointment',payload,'author','unique-key-0003')
