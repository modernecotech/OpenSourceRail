"""Forgery, stale configuration and calibration are rejected before QA ingestion."""
import base64
from copy import deepcopy
from pathlib import Path
import subprocess

import pytest

from engineering.assembly_design import acceptance as a
from engineering.twin_workflow import core


@pytest.fixture
def evidence(tmp_path):
    trust = {}
    for key_id, role in [('lab', 'measurement'), ('cal', 'calibration'), ('reviewer', 'review')]:
        private = tmp_path/(key_id+'.pem')
        subprocess.run(['openssl', 'genpkey', '-algorithm', 'ED25519', '-out', str(private)], check=True, capture_output=True)
        public = subprocess.run(['openssl', 'pkey', '-in', str(private), '-pubout'], check=True, capture_output=True, text=True).stdout
        trust[key_id] = dict(public_key_pem=public, roles=[role], revoked=False, valid_from='2026-01-01', valid_until='2027-01-01')
    def sign(payload, key_id):
        message = tmp_path/'message'
        message.write_bytes(a.canonical(payload))
        sig = subprocess.run(['openssl', 'pkeyutl', '-sign', '-inkey', str(tmp_path/(key_id+'.pem')), '-rawin', '-in', str(message)], check=True, capture_output=True).stdout
        return dict(algorithm='Ed25519', key_id=key_id, payload=deepcopy(payload), signature=base64.b64encode(sig).decode())
    (tmp_path/'raw.csv').write_text('force_N,displacement_mm\n100,0.5\n')
    (tmp_path/'cal.pdf').write_bytes(b'Test-only synthetic certificate; no physical qualification')
    calibration = dict(instrument_id='load-cell', instrument_revision='1', valid_from='2026-01-01', valid_until='2026-12-31',
        certificate=dict(path='cal.pdf', sha256=core.sha(tmp_path/'cal.pdf')),
        ranges=[dict(quantity='force', unit='N', minimum=0, maximum=1000, uncertainty_floor=1)])
    expected = dict(architecture='baghdad-six-car', unit_id='cassette', unit_revision='r1', serial='S1', interface_revision='I1', method='fixture-pull', standard_edition='project-method-1')
    measured = dict(**expected, fixture_id='pull-rig', fixture_revision='A', conditions={'temperature_C':25}, measured_date='2026-10-19',
        instrument_id='load-cell', instrument_revision='1', calibration_sha256=a.digest(calibration),
        raw_files=[dict(path='raw.csv', sha256=core.sha(tmp_path/'raw.csv'))],
        measurements=[dict(quantity='force', unit='N', value=100, uncertainty=2, uncertainty_basis='expanded-k2')])
    def bundle(measure=measured, calibrate=calibration, **changes):
        review = dict(measurement_sha256=a.digest(measure), calibration_sha256=a.digest(calibrate), applicability=expected,
            decision='accepted-record', reasons=['Synthetic test-only authorised review'])
        review.update(changes)
        return sign(measure, 'lab'), sign(calibrate, 'cal'), sign(review, 'reviewer')
    return tmp_path, trust, expected, measured, calibration, sign, bundle


def test_authentication_never_releases_a_design(evidence):
    root, trust, expected, measured, calibration, sign, bundle = evidence
    result = a.ingest(*bundle(), trust, root, expected, today='2026-10-19')
    assert result['authenticated'] and result['state']=='accepted-record'
    assert all(result[k] is False for k in core.FLAGS)
    assert a.ingest(*bundle(decision='retest'), trust, root, expected, today='2026-10-19')['state']=='retest'


@pytest.mark.parametrize('fault', ['altered-payload','unknown-key','revoked','wrong-role','expired-key','different-revision',
    'missing-fixture','no-raw','negative-uncertainty','out-of-range','below-calibration-floor','bad-unit','expired-calibration',
    'wrong-instrument','wrong-instrument-revision','stale-review','raw-changed','path-escape','same-author-review','future-date'])
def test_external_record_mutations_cannot_pass(evidence, fault):
    root, trust, expected, m, c, sign, bundle = evidence
    m, c = deepcopy(m), deepcopy(c)
    if fault=='revoked':trust['lab']['revoked']=True
    if fault=='wrong-role':trust['lab']['roles']=['review']
    if fault=='expired-key':trust['lab']['valid_until']='2026-10-18'
    if fault=='different-revision':m['unit_revision']='old'
    if fault=='missing-fixture':m['fixture_revision']=None
    if fault=='no-raw':m['raw_files']=[]
    if fault=='negative-uncertainty':m['measurements'][0]['uncertainty']=-1
    if fault=='out-of-range':m['measurements'][0]['value']=1001
    if fault=='below-calibration-floor':m['measurements'][0]['uncertainty']=.1
    if fault=='bad-unit':m['measurements'][0]['unit']='kN'
    if fault=='expired-calibration':c['valid_until']='2026-10-18';m['calibration_sha256']=a.digest(c)
    if fault=='wrong-instrument':m['instrument_id']='another'
    if fault=='wrong-instrument-revision':m['instrument_revision']='2'
    if fault=='path-escape':m['raw_files'][0]['path']='../raw.csv'
    if fault=='future-date':m['measured_date']='2026-10-20'
    records=list(bundle(m,c))
    if fault=='altered-payload':records[0]['payload']['measurements'][0]['value']=101
    if fault=='unknown-key':records[0]['key_id']='new-self-appointed-lab'
    if fault=='stale-review':records[2]=sign({**records[2]['payload'],'measurement_sha256':'0'*64}, 'reviewer')
    if fault=='raw-changed':(root/'raw.csv').write_text('tampered')
    if fault=='same-author-review':
        trust['lab']['roles'].append('review');records[2]=sign(records[2]['payload'],'lab')
    with pytest.raises(ValueError):a.ingest(*records,trust,root,expected,today='2026-10-19')


def test_nonfinite_measurements_never_enter_canonical_evidence():
    with pytest.raises(ValueError):a.canonical({'value':float('nan')})
