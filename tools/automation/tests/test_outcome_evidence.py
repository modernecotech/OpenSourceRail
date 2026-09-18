"""Adversarial business-evidence tests without a Frappe runtime."""
import copy
import pytest
from test_outcome_contract import signed, fixture
from osr_erpnext.outcome_contract import verify, selected_records, VERIFIERS
from osr_erpnext.disposition_contract import ACTIONS


def base(action, kind='stock-entry', name='SE1'):
    before, _, _, _, time = fixture()
    before['work_orders'] = []; before['stock_movements'] = []
    native = dict(doctype='Stock Entry', name=name, project='P1', company='OSR', docstatus=1,
                  modified='2026-01-01 10:00:00', lines=[])
    return before, dict(action=action, target=dict(kind=kind, document=name)), native, time


def qa(reference='SE1', line='L1', kind='Stock Entry', item='RAW'):
    return dict(name='QI1', company='OSR', docstatus=1, modified='2026-01-01 10:00:00',
        reference_type=kind, reference_name=reference, line=line, item=item, sample_size=1,
        inspected_by='inspector', status='Accepted', readings=[dict(specification='width',status='Accepted',
            numeric=1,reading_1='0')])


def inspect_fixture():
    before, proposal, native, time=base('Request inspection')
    line=dict(line='L1',item='RAW',qty=1,uom='Nos',quality_inspection=None)
    before['stock_movements']=[dict(name='SE1',modified='2026-01-01 08:00:00',lines=[line])]
    after=copy.deepcopy(before);after['stock_movements'][0]['modified']=native['modified']
    after['stock_movements'][0]['lines'][0]['quality_inspection']='QI1'
    native['lines']=copy.deepcopy(after['stock_movements'][0]['lines'])
    return before,after,proposal,native,time,dict(inspections=[qa()])


def run(args):
    before,after,proposal,native,time,evidence=args
    return verify(signed(before),signed(after),proposal,native,time,evidence)


def test_all_catalogue_actions_have_a_typed_verifier():
    assert {a for choices in ACTIONS.values() for a in choices} == set(VERIFIERS)
    assert selected_records('Request amendment',{'purchase_order':'PO1'})=={'purchase_order':'PO1'}
    for records in [{}, {'arbitrary':'PO1'}, {'purchase_order':''}, {'purchase_order':'PO1','approved':True}]:
        with pytest.raises(ValueError):selected_records('Request amendment',records)
    with pytest.raises(ValueError):selected_records('Request inspection',{'quality_inspections':['QI1','QI1']})
    with pytest.raises(ValueError):selected_records('Request cancellation',{'purchase_order':'PO1'})


def test_performed_inspection_preserves_rejection_and_never_mutates_input():
    args=inspect_fixture();old=copy.deepcopy(args)
    assert run(args)=='Inspection recorded: accepted' and args==old
    args[-1]['inspections'][0].update(status='Rejected')
    args[-1]['inspections'][0]['readings'][0]['status']='Rejected'
    assert run(args)=='Inspection recorded: rejected'


@pytest.mark.parametrize('change',[
    dict(docstatus=0),dict(reference_name='OTHER'),dict(company='OTHER'),dict(item='OTHER'),
    dict(line='L2'),dict(readings=[]),dict(sample_size=0),dict(inspected_by=''),
    dict(modified='2026-01-01 08:00:00'),dict(readings=[dict(specification='width',status='Accepted',numeric=1)]),
    dict(readings=[dict(specification='width',status='Rejected',numeric=1,reading_1='0')]),
])
def test_unperformed_wrong_or_unmeasured_inspections_fail(change):
    args=inspect_fixture();args[-1]['inspections'][0].update(change)
    with pytest.raises(ValueError):run(args)


def test_inspection_cannot_hide_material_changes_or_omit_a_line():
    args=inspect_fixture();args[1]['stock_movements'][0]['lines'][0]['qty']=2
    with pytest.raises(ValueError):run(args)
    args=inspect_fixture();args[-1]['inspections']=[]
    with pytest.raises(ValueError,match='every reviewed stock line'):run(args)


def amendment_fixture():
    before,proposal,native,time=base('Request amendment','purchase-line','PO1')
    proposal['target']['line']='L1';native.update(doctype='Purchase Order',docstatus=2)
    line=dict(document='PO1',line='L1',item='RAW',qty=1,received_qty=0,uom='Nos',docstatus=1,modified='2026-01-01 08:00:00')
    before['purchase_orders']=[line]
    replacement={**line,'document':'PO2','line':'L2','qty':3,'modified':native['modified']}
    after=copy.deepcopy(before);after['purchase_orders']=[replacement]
    return before,after,proposal,native,time,dict(
        original=dict(name='PO1',docstatus=2,modified=native['modified'],lines=[dict(line,project='P1')]),
        replacement=dict(name='PO2',company='OSR',docstatus=1,amended_from='PO1',modified=native['modified'],lines=[dict(replacement,project='P1')]))


def test_direct_amendment_is_bounded_to_its_replacement():
    args=amendment_fixture();assert run(args)=='Native amendment verified'
    args[1]['purchase_orders'].append(dict(args[1]['purchase_orders'][0],document='PO3'))
    with pytest.raises(ValueError,match='Other revision'):run(args)


@pytest.mark.parametrize('change',[dict(docstatus=0),dict(company='OTHER'),dict(amended_from='OTHER')])
def test_wrong_amendment_evidence_fails(change):
    args=amendment_fixture();args[-1]['replacement'].update(change)
    with pytest.raises(ValueError):run(args)


@pytest.mark.parametrize('change',[dict(item='SUBSTITUTE'),dict(project='P2'),dict(received_qty=1),dict(qty=0)])
def test_amendment_cannot_hide_substitution_scope_or_receiving(change):
    args=amendment_fixture();args[-1]['replacement']['lines'][0].update(change)
    with pytest.raises(ValueError):run(args)


def rework_fixture():
    before,after,proposal,native,time=fixture()
    proposal['action']='Request rework';native['status']='In Process'
    after=copy.deepcopy(before);after['work_orders'][0]['modified']=native['modified']
    card=dict(name='JC2',company='OSR',project='P1',work_order='WO1',bom='BOM1',item='ITEM',
        corrective=True,for_job_card='JC1',for_operation='Weld',operation='Repair',docstatus=1,status='Completed',
        qty=1,completed_qty=1,process_loss_qty=0,modified=native['modified'],quality_inspection='QI1',
        time_logs=[dict(minutes=10,from_time='2026-01-01 09:30:00',to_time='2026-01-01 09:40:00')])
    source={**card,'name':'JC1','corrective':False,'operation':'Weld'}
    return before,after,proposal,native,time,dict(job_card=card,original_job=source,inspections=[qa('JC2','JC2','Job Card','ITEM')])


def test_native_corrective_card_requires_accepted_inspection():
    args=rework_fixture();assert run(args)=='Corrective work and inspection verified'
    args[-1]['inspections'][0]['status']='Rejected'
    with pytest.raises(ValueError,match='accepted native inspection'):run(args)


@pytest.mark.parametrize('change', [dict(corrective=False),dict(work_order='OTHER'),dict(bom='OTHER'),dict(project='OTHER'),
    dict(for_operation='OTHER'),dict(docstatus=0),dict(completed_qty=0),dict(process_loss_qty=1),dict(time_logs=[]),dict(qty=100)])
def test_unperformed_unlinked_or_incomplete_corrective_work_fails(change):
    args=rework_fixture();args[-1]['job_card'].update(change)
    with pytest.raises(ValueError):run(args)


def trace_fixture():
    before,proposal,native,time=base('Request material trace')
    line=dict(line='L1',item='RAW',qty=2,uom='Nos',source_warehouse='Stores',target_warehouse=None,serial_and_batch_bundle='B1')
    before['stock_movements']=[dict(name='SE1',modified=native['modified'],lines=[line])];native['lines']=[line]
    evidence=dict(items=[dict(name='RAW',stock_uom='Nos',has_serial_no=False,has_batch_no=True)],
        ledger=[dict(company='OSR',line='L1',item='RAW',warehouse='Stores',qty=-2)],
        bundles=[dict(name='B1',company='OSR',docstatus=1,cancelled=False,item='RAW',voucher_type='Stock Entry',voucher_no='SE1',line='L1',
            entries=[dict(batch_no='BATCH1',serial_no=None,qty=-2)])])
    return before,copy.deepcopy(before),proposal,native,time,evidence


def test_material_trace_reconciles_ledger_and_batch_identity():
    assert run(trace_fixture())=='Native movement trace verified'


@pytest.mark.parametrize('change', ['ledger-missing','ledger-qty','ledger-company','bundle-missing','bundle-cancelled','bundle-other','batch-missing','bundle-qty'])
def test_incomplete_or_wrong_native_trace_fails(change):
    args=trace_fixture();data=args[-1]
    if change=='ledger-missing':data['ledger']=[]
    if change=='ledger-qty':data['ledger'][0]['qty']=-1
    if change=='ledger-company':data['ledger'][0]['company']='OTHER'
    if change=='bundle-missing':data['bundles']=[]
    if change=='bundle-cancelled':data['bundles'][0]['cancelled']=True
    if change=='bundle-other':data['bundles'][0]['voucher_no']='OTHER'
    if change=='batch-missing':data['bundles'][0]['entries'][0]['batch_no']=None
    if change=='bundle-qty':data['bundles'][0]['entries'][0]['qty']=-1
    with pytest.raises(ValueError):run(args)
