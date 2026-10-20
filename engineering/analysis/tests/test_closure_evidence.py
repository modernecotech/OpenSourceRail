"""Reviewed evidence can close digital coverage, but never self-authorise release."""
import base64
from copy import deepcopy
import subprocess
import pytest
from engineering.assembly_design import closure,closure_evidence as e
from engineering.twin_workflow import core


@pytest.fixture
def signed_task(tmp_path):
    task=dict(id='WP03-example',wp='WP03',kind='design',required_evidence='Complete example load path and assembly',title='Example',page=1)
    prepared=dict(prototype=dict(id='example-configuration',revision='p1'),source_sha256={'source.py':'1'*64})
    subjects={'structural-bay':dict(component_id='example-bay',component_revision='c1',interface_revision='i1',full_pilot_scope=False)}
    contract=e.task_contract(task,prepared,subjects);trust={}
    for identity,role in [('author','digital-evidence'),('reviewer','digital-review')]:
        key=tmp_path/(identity+'.pem')
        subprocess.run(['openssl','genpkey','-algorithm','ED25519','-out',str(key)],capture_output=True,check=True)
        public=subprocess.run(['openssl','pkey','-in',str(key),'-pubout'],capture_output=True,text=True,check=True).stdout
        trust[identity]=dict(public_key_pem=public,roles=[role],revoked=False,valid_from='2026-01-01',valid_until='2027-01-01')
    def sign(payload,identity):
        message=tmp_path/'message';message.write_bytes(e.acceptance.canonical(payload))
        signature=subprocess.run(['openssl','pkeyutl','-sign','-inkey',str(tmp_path/(identity+'.pem')),'-rawin','-in',str(message)],check=True,capture_output=True).stdout
        return dict(algorithm='Ed25519',key_id=identity,payload=deepcopy(payload),signature=base64.b64encode(signature).decode())
    artifacts=[]
    for category in contract['required_categories']:
        path=tmp_path/(category+'.txt');path.write_text('SYNTHETIC TEST ONLY; not railway evidence: '+category)
        artifacts.append(dict(path=path.name,sha256=core.sha(path),category=category))
    authored=dict(task_id=task['id'],contract_revision=contract['revision'],artifacts=artifacts,
        coverage={category:'passed' for category in contract['required_categories']})
    reviewed=dict(contract_revision=contract['revision'],authored_sha256=e.acceptance.digest(authored),decision='accepted-record',reasons=['Synthetic test-only review'])
    index=dict(schema='osr-closure-evidence-index/1',submissions=[dict(task_id=task['id'],level='digital',author=sign(authored,'author'),review=sign(reviewed,'reviewer'))])
    return task,prepared,subjects,trust,index,tmp_path,sign


def assess(data):
    task,prepared,subjects,trust,index,root,sign=data
    return e.evaluate([task],prepared,subjects=subjects,trust=trust,index=index,root=root,today='2026-10-20')


def test_valid_reviewed_record_completes_exact_digital_task_only(signed_task):
    task,prepared,subjects,trust,index,root,sign=signed_task
    state=assess(signed_task)['tasks'][task['id']]
    assert state['digital_specification_complete']
    assert not state['physical_validation_records_complete'] and not state['manufacturing_release']
    assert assess(signed_task)['pilot_records']=={}  # An isolated bay cannot cover a complete pilot.
    prepared['closure_plan']=dict(source_pdf='test.pdf',source_sha256='f'*64,packages=[],tasks=[task])
    snapshot=closure.snapshot(prepared,subjects=subjects,evidence_index=index,trust=trust,evidence_root=root,today='2026-10-20')
    assert snapshot['digital_completed_tasks']==1 and snapshot['engineering_closed_tasks']==0
    assert not any(snapshot[flag] for flag in core.FLAGS)


@pytest.mark.parametrize('defect',('component','interface','source','requirement','raw-bytes','signature','revoked','same-reviewer','unknown-trust','missing-category'))
def test_stale_inputs_or_forged_reviews_invalidate_without_erasing_history(signed_task,defect):
    task,prepared,subjects,trust,index,root,sign=signed_task
    record=index['submissions'][0]
    if defect=='component':subjects['structural-bay']['component_revision']='c2'
    elif defect=='interface':subjects['structural-bay']['interface_revision']='i2'
    elif defect=='source':prepared['source_sha256']['source.py']='2'*64
    elif defect=='requirement':task['required_evidence']+=' plus an independent load case'
    elif defect=='raw-bytes':(root/'analysis.txt').write_text('altered')
    elif defect=='signature':record['author']['payload']['coverage']['analysis']='held'
    elif defect=='revoked':trust['reviewer']['revoked']=True
    elif defect=='same-reviewer':record['review']['key_id']='author'
    elif defect=='unknown-trust':trust.clear()
    else:
        record['author']['payload']['artifacts'].pop()
        record['author']=sign(record['author']['payload'],'author')
        payload=record['review']['payload'];payload['authored_sha256']=e.acceptance.digest(record['author']['payload'])
        record['review']=sign(payload,'reviewer')
    result=assess(signed_task)
    assert not result['tasks'][task['id']]['digital_specification_complete']
    assert result['tasks'][task['id']]['digital_state']=='stale-or-invalid'
    assert result['invalid_records'] and len(index['submissions'])==1


def test_new_known_failures_and_native_hold_cannot_be_reviewed_away(signed_task):
    task,prepared,subjects,trust,index,root,sign=signed_task
    for native_state in ('failed','hold'):
        subjects['structural-bay'].update(native_required=True,native_state=native_state)
        # Re-sign against the new exact contract: a review still cannot override native evidence.
        contract=e.task_contract(task,prepared,subjects);record=index['submissions'][0]
        authored=record['author']['payload'];authored['contract_revision']=contract['revision']
        review=record['review']['payload'];review.update(contract_revision=contract['revision'],authored_sha256=e.acceptance.digest(authored))
        record['author']=sign(authored,'author');record['review']=sign(review,'reviewer')
        state=assess(signed_task)['tasks'][task['id']]
        assert not state['digital_specification_complete']
        assert state['digital_state']==('failed' if native_state=='failed' else 'hold')


def test_client_receipt_boolean_is_not_an_authentication_adapter(signed_task):
    task,prepared,subjects,trust,index,root,sign=signed_task
    index['submissions']=[dict(task_id=task['id'],level='digital',receipt_verified=True,state='passed')]
    result=assess(signed_task)
    assert result['invalid_records'] and not result['tasks'][task['id']]['digital_specification_complete']


def test_original_digital_evidence_is_portable_and_byte_tampering_invalidates(signed_task,tmp_path):
    task,prepared,subjects,trust,index,root,sign=signed_task
    prepared.update(completion_evidence=index,completion_trust=trust)
    portable=tmp_path/'portable';e.export_raw(prepared,portable,root=root);e.verify_raw(portable)
    assert e.evaluate([task],prepared,subjects=subjects,root=portable,today='2026-10-20')['tasks'][task['id']]['digital_specification_complete']
    (portable/'analysis.txt').write_text('altered portable bytes')
    with pytest.raises(ValueError):e.verify_raw(portable)
    result=e.evaluate([task],prepared,subjects=subjects,root=portable,today='2026-10-20')
    assert not result['tasks'][task['id']]['digital_specification_complete']


def test_new_component_revision_can_complete_without_erasing_stale_history(signed_task):
    task,prepared,subjects,trust,index,root,sign=signed_task
    old=deepcopy(index['submissions'][0]);subjects['structural-bay']['component_revision']='c2'
    contract=e.task_contract(task,prepared,subjects)
    new=deepcopy(old);authored=new['author']['payload'];authored['contract_revision']=contract['revision']
    reviewed=new['review']['payload'];reviewed.update(contract_revision=contract['revision'],authored_sha256=e.acceptance.digest(authored))
    new['author']=sign(authored,'author');new['review']=sign(reviewed,'reviewer')
    index['submissions'].append(new)
    result=assess(signed_task)
    assert result['tasks'][task['id']]['digital_specification_complete']
    assert result['invalid_records'][0]['state']=='stale' and index['submissions'][0]==old


def test_evidence_index_is_bound_by_epoch_without_self_referential_contract(signed_task):
    task,prepared,subjects,trust,index,root,sign=signed_task
    before=e.task_contract(task,prepared,subjects)
    prepared['source_sha256']['engineering/assembly_design/data/closure-evidence.json']='a'*64
    assert e.task_contract(task,prepared,subjects)==before
    prepared['source_sha256']['engineering/assembly_design/data/closure-trust.json']='b'*64
    assert e.task_contract(task,prepared,subjects)!=before


def test_physical_applicability_comes_from_controlled_task_not_submission(signed_task):
    task,prepared,subjects,trust,index,root,sign=signed_task
    expected=dict(architecture='baghdad-six-car',unit_id='example-bay',unit_revision='c1',interface_revision='i1',
        serial='controlled-serial',method='adopted-method',standard_edition='adopted-edition')
    task['physical_expected']=expected
    contract=e.task_contract(task,prepared,subjects)
    assert contract['physical_expected']==expected
    index['submissions'][0]['physical_expected']={**expected,'serial':'self-appointed'}
    assert e.task_contract(task,prepared,subjects)==contract
