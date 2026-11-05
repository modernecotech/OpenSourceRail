"""Local delivery payload integrity; no Frappe installation or site calls."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import json

import pytest

MODULE = Path(__file__).resolve().parents[1]/'services/integration/osr_integration/city_outline.py'
spec = importlib.util.spec_from_file_location('city_outline_delivery', MODULE)
delivery = importlib.util.module_from_spec(spec); spec.loader.exec_module(delivery)


def seal(value, key='plan_id'):
    value.pop(key, None); value[key] = delivery.identity(value); return value


def plan():
    values = dict(schema='osr-city-outline-delivery-plan/1',city=dict(slug='fixture',name='Fixture city'),
        city_record_evaluation_id='evaluation',city_input_id='geography',cost_evaluation_id='cost',
        research_configuration_id='configuration',selection_id='selection',planning_revision_id='revision',
        reference_candidate_ids=dict(candidate_id='vehicle',body_candidate_id='body'),
        items=[dict(item_id='raw',item_code='STEEL',name='Stock steel',quantity=200.,uom='Kg',kind='material',budget_usd=dict(low=100,base=200,high=400)),
            dict(item_id='beam',item_code='BEAM',name='Outline beam',quantity=2.,uom='Nos',kind='assembly')],
        boms=[dict(bom_id='bom',item_code='BEAM',output_quantity=1.,uom='Nos',items=[dict(item_code='STEEL',qty=100.,uom='Kg')])],
        production_groups=[dict(group_id='make-beam',item_code='BEAM',route='make',output_quantity=2.,uom='Nos',
            operations=[dict(operation_id='cut',name='Cut and inspect',sequence=1,resource_id='cell',hours_per_unit=dict(low=1,base=2,high=4),duration_basis='per-beam')])],
        resources=[dict(resource_id='cell',name='Production cell',domain='production',capacity_by_case=dict(low=1,base=1,high=1),capacity_unit='cells',owned=True,priced=True)],
        tasks=[dict(task_id='setup',name='Factory setup',predecessors=[]),dict(task_id='produce',name='Produce beams',predecessors=['setup'])],
        schedule=dict(cases={c:dict(capacity_pass=True,tasks=[dict(task_id='setup',start_workday=0.,finish_workday=2.),dict(task_id='produce',start_workday=2.,finish_workday=5.)]) for c in ('low','base','high')}),
        workforce=dict(shift_patterns=[dict(shift_id='factory',domain='production',shifts_per_day=2,hours_per_shift=8,days_per_year=250,utilisation=.75,positions_by_case=dict(low=2,base=3.1,high=6)),
            dict(shift_id='operation',domain='operations',shifts_per_day=3,hours_per_shift=8,days_per_year=365,utilisation=.75,positions_by_case=dict(low=1,base=2,high=4))]),
        cost_reconciliation=dict(installed_capital_usd=dict(low=1000,base=2000,high=4000)),
        source_sha256={'fixture.json':'0'*64},physical_accepted=False,manufacturing_release=False)
    return seal(values)


def test_actual_doctype_payloads_have_exact_links_and_local_holds():
    p=plan(); result=delivery.delivery_drafts(p)
    delivery.validate(result)
    assert set(result['documents']) == set(delivery.DOCTYPES)
    assert all(result['documents'][k] for k in delivery.DOCTYPES)
    assert all(d['docstatus']==0 for docs in result['documents'].values() for d in docs)
    assert all(m['local_disabled'] and not m['site_insert_permitted'] for m in result['document_metadata'].values())
    assert not result['external_transactions_performed']
    assert not result['target_site_schema_validation_performed']
    wo=result['documents']['Work Order'][0]
    assert wo['qty']==2 and wo['status']=='Draft' and 'planned_start_date' not in wo and 'company' not in wo
    op=result['documents']['Routing'][0]['operations'][0]
    assert op['time_in_mins']==120
    staffing=result['documents']['Staffing Plan']
    assert [x['staffing_details'][0]['vacancies'] for x in staffing]==[8,6]
    assert len(result['documents']['Shift Type'])==5
    assert 'disabled' not in result['documents']['Project'][0]


def test_deterministic_and_immutable_order_revision_preservation():
    old=dict(order_id='released-001',candidate_id='previous-vehicle',released_revision_id='previous-revision',docstatus=1)
    before=deepcopy(old); p=plan()
    value=delivery.delivery_drafts(p,[old])
    assert old==before and value['active_orders_preserved']==[before]
    assert not value['change_reviews'][0]['active_order_mutated']
    assert delivery.delivery_drafts(p,[old])==value
    newer=deepcopy(p); newer['planning_revision_id']='revision-2';seal(newer)
    revised=delivery.delivery_drafts(newer,[old])
    assert revised['draft_id']!=value['draft_id']
    assert revised['documents']['Work Order'][0]['name']!=value['documents']['Work Order'][0]['name']
    assert revised['active_orders_preserved']==value['active_orders_preserved']


@pytest.mark.parametrize('change,reason',[
    (lambda p:p['boms'][0]['items'][0].update(item_code='BEAM',uom='Nos'),'cycle'),
    (lambda p:p['boms'][0]['items'][0].update(uom='m'),'UOM'),
    (lambda p:p['production_groups'][0]['operations'][0].update(resource_id='missing'),'resource'),
    (lambda p:p['schedule']['cases']['base']['tasks'][1].update(start_workday=1.),'precedence'),
    (lambda p:p['workforce']['shift_patterns'][0].update(shifts_per_day=4),'shift'),
    (lambda p:p.update(physical_accepted=True),'release'),
])
def test_rejects_invalid_reference_or_safety_plan_even_after_reseal(change,reason):
    p=plan();change(p);seal(p)
    with pytest.raises(ValueError,match=reason):delivery.delivery_drafts(p)


def test_plan_and_draft_identity_changes_detected():
    p=plan(); p['items'][0]['quantity']+=1
    with pytest.raises(ValueError,match='identity'):delivery.delivery_drafts(p)
    value=delivery.delivery_drafts(plan());value['documents']['Work Order'][0]['qty']=0;seal(value,'draft_id')
    with pytest.raises(ValueError,match='quantity'):delivery.validate(value)
    value=delivery.delivery_drafts(plan());value['documents']['BOM'][0]['is_active']=1;seal(value,'draft_id')
    with pytest.raises(ValueError,match='Inactive'):delivery.validate(value)


def test_receive_fit_does_not_issue_fictitious_manufacturing_order():
    p=plan();p['production_groups'][0]['route']='receive-fit';p['boms']=[];seal(p)
    value=delivery.delivery_drafts(p)
    assert not value['documents']['Work Order'] and value['documents']['Routing']


def test_export_roundtrip_inventory_tampering_and_no_overwrite(tmp_path):
    value=delivery.delivery_drafts(plan()); folder=tmp_path/'run'
    manifest=delivery.export_drafts(value,folder)
    assert delivery.verify_export(folder)==(manifest,value)
    assert len(list(folder.iterdir()))==12
    with pytest.raises(ValueError,match='Fresh'):delivery.export_drafts(value,folder)
    path=folder/'work-order.json'; path.write_text('[]\n')
    with pytest.raises(ValueError,match='Artifact differs'):delivery.verify_export(folder)


def test_refuses_symlink_parent_and_path_escape(tmp_path):
    target=tmp_path/'target';target.mkdir();(tmp_path/'linked').symlink_to(target,target_is_directory=True)
    with pytest.raises(ValueError,match='Ordinary'):delivery.export_drafts(delivery.delivery_drafts(plan()),tmp_path/'linked'/'run')
    p=plan();p['source_sha256']={'../escape':'0'*64};seal(p)
    with pytest.raises(ValueError,match='Relative'):delivery.delivery_drafts(p)


def test_export_resealed_unknown_workstation_rejected(tmp_path):
    value=delivery.delivery_drafts(plan());value['documents']['Operation'][0]['workstation']='missing';seal(value,'draft_id')
    with pytest.raises(ValueError,match='workstation'):delivery.export_drafts(value,tmp_path/'run')


def test_site_flags_and_automatic_attendance_cannot_be_laundered():
    value=delivery.delivery_drafts(plan()); value['documents']['Task'][0]['custom_execute']='arbitrary'
    seal(value,'draft_id')
    with pytest.raises(ValueError,match='Unsupported site field'):delivery.validate(value)
    value=delivery.delivery_drafts(plan()); value['documents']['Shift Type'][0]['enable_auto_attendance']=1
    seal(value,'draft_id')
    with pytest.raises(ValueError,match='attendance'):delivery.validate(value)
    value=delivery.delivery_drafts(plan()); value['documents']['BOM'][0]['items'][0]['docstatus']=1
    seal(value,'draft_id')
    with pytest.raises(ValueError,match='child docstatus'):delivery.validate(value)


def test_wrong_adapter_source_and_unbound_active_order_are_rejected():
    value=delivery.delivery_drafts(plan());value['source_sha256'][delivery.PRODUCER]='0'*64;seal(value,'draft_id')
    with pytest.raises(ValueError,match='source differs'):delivery.validate(value)
    with pytest.raises(ValueError,match='released bindings'):delivery.delivery_drafts(plan(),[dict(order_id='orphan')])
