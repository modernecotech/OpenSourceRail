"""Offline boundaries; these tests do not claim native services executed."""
from copy import deepcopy
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
spec=spec_from_file_location('v06_native_contracts',ROOT/'tools/automation/native-v06/contracts.py')
c=module_from_spec(spec);spec.loader.exec_module(c)


def reseal(value):
    value['input_id']=c.digest({k:v for k,v in value.items() if k!='input_id'});return value


def test_current_export_input_is_deterministic_source_bound_and_unreleased():
    value=c.load_input(ROOT)
    assert value==c.load_input(ROOT) and c.validate_input(value)==value
    assert value['identities']['candidate_id']=='756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3'
    assert value['source_occurrence']['id']=='retained-comfort/HVAC'
    assert value['conversion']['basis'].startswith('One synthetic software kit')
    assert all(value[k] is False for k in c.FLAGS)


@pytest.mark.parametrize('attack',['source','hash','authority','candidate'])
def test_changed_or_promoted_fixture_refused(attack):
    value=c.load_input(ROOT)
    if attack=='source':value['source_occurrence']['mass_kg']+=1;reseal(value)
    if attack=='hash':value['input_id']='f'*64
    if attack=='authority':value['movement_authority']=True;reseal(value)
    if attack=='candidate':value['identities']['candidate_id']='unknown';reseal(value)
    with pytest.raises(ValueError):c.validate_input(value)


def review():
    expected=dict(identities=c.load_input(ROOT)['identities'],serial='SIM-NEW',latest_test='QI-LATEST',reviewer='reviewer@example.invalid')
    observed=dict(**expected,test_status='Accepted',inspector='inspector@example.invalid',repair_status='Completed',handback_required=True)
    return expected,observed


def test_exact_latest_independent_business_review_retains_physical_hold():
    expected,observed=review();value=c.handback_guard(expected,observed)
    assert value['business_review']=='simulation-business-reviewed'
    assert all(value[k] is False for k in c.FLAGS)


@pytest.mark.parametrize('attack',['serial','latest','failed','self','repair','hold','candidate'])
def test_business_handback_cannot_ignore_native_or_identity_failure(attack):
    expected,observed=review();observed=deepcopy(observed)
    if attack=='serial':observed['serial']='SIM-OLD'
    if attack=='latest':observed['latest_test']='QI-PRIOR'
    if attack=='failed':observed['test_status']='Rejected'
    if attack=='self':observed['reviewer']=observed['inspector']
    if attack=='repair':observed['repair_status']='Pending'
    if attack=='hold':observed['handback_required']=False
    if attack=='candidate':observed['identities']['candidate_id']='e'*64
    with pytest.raises(ValueError):c.handback_guard(expected,observed)


def receipt():
    value=c.load_input(ROOT);source={'fixture.py':'a'*64}
    types=['BOM','Purchase Order','Purchase Receipt','Quality Inspection','Asset','Issue','Asset Repair','Task','Training Program','Stock Entry']
    records=[dict(doctype=dt,name=dt+'-1',docstatus=1,owner='fixture',modified_by='fixture',values={}) for dt in types]
    for row in records:
        if row['doctype']=='Quality Inspection':row['values']=dict(status='Accepted',inspected_by='inspector')
        if row['doctype']=='Task':row.update(modified_by='reviewer',values=dict(status='Completed'))
        if row['doctype']=='Asset Repair':row['values']=dict(repair_status='Completed',custom_osr_handback_required=1)
    records += [dict(doctype='Work Order',name='WO-'+str(i),docstatus=1,values=dict(produced_qty=1)) for i in range(2)]
    records += [dict(doctype='Serial No',name=name,docstatus=0,values={}) for name in ('SIM-OLD','SIM-NEW')]
    context=dict(task='Task-1',quality_inspection='Quality Inspection-1',reviewer='reviewer',inspector='inspector',current_serial='SIM-NEW',
        mapping_identities=value['identities'],native_inspection_order='creation desc, name desc')
    result=dict(schema='osr-v06-native-platform-result/1',execution='executed',input_id=value['input_id'],identities=value['identities'],
        source_sha256=source,native_records=records,checks={k:True for k in c.REQUIRED},uncovered=[],cleanup=dict(verified=True),
        review_context=context,qa_binding=dict(quality_inspection=context['quality_inspection'],measurement=dict(serial='SIM-NEW')),**c.FLAGS)
    return value,source,result


def test_structured_native_readback_boundary_accepts_complete_consistent_fixture_only():
    value,source,result=receipt()
    assert c.verify_result(result,value,source)==result


@pytest.mark.parametrize('attack',['cleanup','mapping','order','reviewer','qa','serial','repair','work'])
def test_native_readback_integrity_checks(attack):
    value,source,result=receipt();result=deepcopy(result)
    if attack=='cleanup':result['cleanup']['verified']=False
    if attack=='mapping':result['review_context']['mapping_identities']['candidate_id']='f'*64
    if attack=='order':result['review_context']['native_inspection_order']='fixture order'
    if attack=='reviewer':next(r for r in result['native_records'] if r['doctype']=='Task')['modified_by']='inspector'
    if attack=='qa':next(r for r in result['native_records'] if r['doctype']=='Quality Inspection')['values']['status']='Rejected'
    if attack=='serial':result['qa_binding']['measurement']['serial']='SIM-OLD'
    if attack=='repair':next(r for r in result['native_records'] if r['doctype']=='Asset Repair')['values']['custom_osr_handback_required']=0
    if attack=='work':next(r for r in result['native_records'] if r['doctype']=='Work Order')['values']['produced_qty']=0
    with pytest.raises(ValueError):c.verify_result(result,value,source)


@pytest.mark.parametrize('attack',['source','identity','partial','uncovered','unexecuted','authority','missing-records'])
def test_receipt_refuses_partial_or_stale_execution(attack):
    value,source,result=receipt();result=deepcopy(result)
    if attack=='source':result['source_sha256']={}
    if attack=='identity':result['identities']['body_candidate_id']='b'*64
    if attack=='partial':result['checks'].pop('outage-replay')
    if attack=='uncovered':result['uncovered']=['native-hr-training']
    if attack=='unexecuted':result['execution']='planned'
    if attack=='authority':result['physical_accepted']=True
    if attack=='missing-records':result['native_records']=[]
    with pytest.raises(ValueError):c.verify_result(result,value,source)
