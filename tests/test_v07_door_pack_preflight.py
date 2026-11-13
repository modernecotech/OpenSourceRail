"""The actual counted door must not inherit a reference or fixture ERP pack."""
from copy import deepcopy
from hashlib import sha256
import gzip
import json

import pytest

from engineering.station_rail.common import encoded, identity
from tools.automation import v07_door_pack_preflight as gate
from tools.automation import v07_door_stage_intake as intake


@pytest.fixture(scope='module')
def handoff():
    return json.loads(gate.HANDOFF.read_bytes())


def synthetic_proposal(handoff):
    """Only a shape fixture; no same-child study or source authentication."""
    ids = {name: 'a' * 64 for name in gate.IDENTITIES}
    ids['body_candidate_id'] = gate.INSTALLED_CHILD
    ids['engineering_revision'] = handoff['installed_evaluation_id']
    parts = [dict(id=p['part_id'], source_component_candidate_id=gate.PHYSICAL_CHILD,
                  component_definition_id=p['component_definition_id'],
                  quantity_per_train=12 * p['quantity_per_opening'], make_buy=p['make_buy'])
             for p in handoff['parts']]
    value = dict(schema='osr-pilot-delivery-proposal/1', status='DRAFT',
                 identities=ids, items=parts, engineering_accepted=False,
                 physical_accepted=False, manufacturing_release=False)
    value['proposal_id'] = identity(value)
    return value


def reseal(value):
    value['proposal_id'] = identity({k: v for k, v in value.items() if k != 'proposal_id'})


def test_current_inventory_is_held_and_source_bound(handoff):
    report = gate.preflight()
    assert gate.OUTPUT.read_bytes() == encoded(report)
    assert report['preflight_id'] == identity({k: v for k, v in report.items() if k != 'preflight_id'})
    assert (report['part_types'], report['pieces_per_opening']) == (74, 694)
    assert (report['purchased_types'], report['purchased_pieces_per_opening']) == (35, 597)
    assert len(report['unnamed_part_document_ids']) == 74
    assert len(report['unnamed_assembly_document_ids']) == 3
    assert len(report['unnamed_conversion_ids']) == 74
    assert report['unverified_stage_inputs']
    assert report['proposal_shape_supplied'] is False
    assert report['pack_ready'] is False
    assert report['native_erp_admitted'] is False


@pytest.mark.parametrize('fault', ['reference-body', 'wrong-revision', 'wrong-component',
                                   'wrong-count', 'wrong-buy-route', 'promoted',
                                   'missing-part', 'broken-seal', 'movement-authority',
                                   'native-ready', 'installed-geometry',
                                   'native-erp', 'pack-ready'])
def test_mixed_or_promoted_shape_refused(handoff, fault):
    value = synthetic_proposal(handoff)
    if fault == 'reference-body':
        value['identities']['body_candidate_id'] = '756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3'
    elif fault == 'wrong-revision':
        value['identities']['engineering_revision'] = '0' * 64
    elif fault == 'wrong-component':
        value['items'][0]['component_definition_id'] = '0' * 64
    elif fault == 'wrong-count':
        value['items'][0]['quantity_per_train'] += 1
    elif fault == 'wrong-buy-route':
        value['items'][0]['make_buy'] = 'local-fabricate' if value['items'][0]['make_buy'] != 'local-fabricate' else 'buy-standard'
    elif fault == 'promoted':
        value['manufacturing_release'] = True
    elif fault == 'missing-part':
        value['items'].pop()
    elif fault == 'movement-authority':
        value['movement_authority'] = True
    elif fault == 'native-ready':
        value['ready_for_native_assembly'] = True
    elif fault == 'installed-geometry':
        value['installed_geometry_verified'] = True
    elif fault == 'native-erp':
        value['native_erp_admitted'] = True
    elif fault == 'pack-ready':
        value['pack_ready'] = True
    else:
        value['proposal_id'] = '0' * 64
    if fault != 'broken-seal':
        reseal(value)
    with pytest.raises(ValueError):
        gate.preflight(proposal=value)


def test_document_and_conversion_coverage_is_only_a_preflight(handoff):
    proposal = synthetic_proposal(handoff)
    first = handoff['parts'][0]['part_id']
    documents = dict(schema='osr-controlled-research-documents/1',
                     identities=deepcopy(proposal['identities']),
                     components=[dict(part_id=first, drawing='drawing.json',
                                      inspection='inspection.json', routing='routing.json')],
                     assemblies=[])
    report = gate.preflight(proposal=proposal, documents=documents,
                            conversions={first: {'source_part_sha256': 'a' * 64}})
    assert len(report['named_part_document_ids']) == 1
    assert len(report['unnamed_part_document_ids']) == 73
    assert len(report['unnamed_conversion_ids']) == 73
    assert report['unverified_stage_inputs']
    assert report['pack_ready'] is False
    assert report['review_compiler_still_required'] is True
    assert report['stage_source_authentication_required'] is True
    assert report['controlled_payloads_verified'] is False
    assert report['native_erp_admitted'] is False
    documents['identities']['body_candidate_id'] = '0' * 64
    with pytest.raises(ValueError, match='identities'):
        gate.preflight(proposal=proposal, documents=documents)


def test_foreign_document_mapping_refused(handoff):
    proposal = synthetic_proposal(handoff)
    documents = dict(schema='osr-controlled-research-documents/1',
                     identities=proposal['identities'],
                     components=[dict(part_id='fixture/fake', drawing='d',
                                      inspection='i', routing='r')])
    with pytest.raises(ValueError, match='foreign'):
        gate.preflight(proposal=proposal, documents=documents)


def test_all_named_fake_paths_do_not_make_a_pack_ready(handoff):
    proposal = synthetic_proposal(handoff)
    documents = dict(schema='osr-controlled-research-documents/1',
                     identities=proposal['identities'],
                     components=[dict(part_id=p['part_id'], drawing='missing/drawing.svg',
                                      inspection='missing/inspection.json',
                                      routing='missing/routing.json') for p in handoff['parts']],
                     assemblies=[dict(assembly_id=name, drawing='missing/drawing.svg',
                                      inspection='missing/inspection.json',
                                      routing='missing/routing.json') for name in gate.ASSEMBLIES])
    conversions={p['part_id']: {'source_part_sha256': '0' * 64} for p in handoff['parts']}
    report = gate.preflight(proposal=proposal, documents=documents, conversions=conversions)
    assert not report['unnamed_part_document_ids']
    assert not report['unnamed_conversion_ids']
    assert report['unverified_stage_inputs']
    assert report['controlled_payloads_verified'] is False
    assert report['conversion_values_verified'] is False
    assert report['pack_ready'] is False
    assert report['native_erp_admitted'] is False


def _study_packet(tmp_path):
    root=tmp_path/'source';root.mkdir()
    source=root/'controlled.txt';source.write_text('source revision A')
    study=dict(schema='osr-railway-closure-study/1',
               body_candidate_id=gate.INSTALLED_CHILD,
               body_evaluation_id='b'*64,
               source_sha256={'controlled.txt':sha256(source.read_bytes()).hexdigest()},
               engineering_accepted=False,physical_accepted=False)
    study['study_id']=identity(study)
    packet=tmp_path/'study.json.gz'
    packet.write_bytes(gzip.compress(encoded(study),mtime=0))
    return root,source,packet,study


def test_stage_intake_reports_first_missing_stage_without_granting_pack(tmp_path):
    empty=intake.intake(root=tmp_path)
    assert empty['intake_id']==identity({k:v for k,v in empty.items() if k!='intake_id'})
    assert empty['first_unverified_stage']==gate.STAGES[0]
    assert empty['stages'][0]['status']=='missing'
    root,_,packet,_=_study_packet(tmp_path)
    found=intake.intake(study_path=packet,root=root)
    assert found['stages'][0]['status']=='source-verified'
    assert found['first_unverified_stage']==gate.STAGES[1]
    assert found['packet_sha256']['study']==sha256(packet.read_bytes()).hexdigest()
    assert found['pack_ready'] is False and found['native_erp_admitted'] is False


def test_stage_intake_refuses_stale_source_and_resealed_other_child(tmp_path):
    root,source,packet,study=_study_packet(tmp_path)
    source.write_text('source revision B')
    stale=intake.intake(study_path=packet,root=root)
    assert stale['first_unverified_stage']==gate.STAGES[0]
    assert stale['stages'][0]['status']=='held'
    assert 'Source bytes differ' in stale['first_unverified_reason']
    source.write_text('source revision A')
    study['body_candidate_id']='0'*64
    study['study_id']=identity({k:v for k,v in study.items() if k!='study_id'})
    packet.write_bytes(gzip.compress(encoded(study),mtime=0))
    mixed=intake.intake(study_path=packet,root=root)
    assert mixed['first_unverified_stage']==gate.STAGES[0]
    assert 'another installed child' in mixed['first_unverified_reason']


def test_stage_intake_refuses_unsealed_study_and_wrong_body(tmp_path):
    root,_,packet,study=_study_packet(tmp_path)
    study['study_id']='0'*64
    packet.write_bytes(gzip.compress(encoded(study),mtime=0))
    invalid=intake.intake(study_path=packet,root=root)
    assert invalid['stages'][0]['status']=='held'
    assert 'Unsealed study_id' in invalid['first_unverified_reason']
    study['study_id']=identity({k:v for k,v in study.items() if k!='study_id'})
    packet.write_bytes(gzip.compress(encoded(study),mtime=0))
    physical=dict(schema='synthetic-other-child')
    body=dict(schema='osr-vehicle-installation/1',candidate_id=identity(physical),
              physical_definition=physical,
              source_sha256=study['source_sha256'])
    body['evaluation_id']=identity(body)
    body_path=tmp_path/'body.json';body_path.write_bytes(encoded(body))
    wrong=intake.intake(study_path=packet,body_path=body_path,root=root)
    assert wrong['stages'][0]['status']=='source-verified'
    assert wrong['first_unverified_stage']==gate.STAGES[1]
    assert 'Installed body candidate' in wrong['first_unverified_reason']
