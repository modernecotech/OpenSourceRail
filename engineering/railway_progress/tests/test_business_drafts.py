"""Actual disabled production drafts, count explosion and immutable revisions."""
from copy import deepcopy
from collections import Counter
import pytest
from engineering.railway_progress import production as p,alternatives as a,identity
from engineering.railway_progress.tests.test_alternatives import vehicle as base_vehicle


@pytest.fixture(scope='module')
def inputs(base_vehicle):
    alt=a.evaluate(base_vehicle);cid=identity({'body':base_vehicle['candidate_id'],'alternative':alt['candidate_id']})
    civil=dict(candidate_id=cid,body_candidate_id=base_vehicle['candidate_id'],alternative_candidate_id=alt['candidate_id'],construction_sequence=[])
    civil['evaluation_id']=identity(civil)
    return base_vehicle,civil,alt,cid


def test_disabled_records_reconcile_vehicle_and_added_launch_hardware(inputs):
    v,c,a,cid=inputs;result=p.compile(v,c,a,cid);d=result['ERPNext_drafts']
    assert not d['submission_allowed'] and not d['active_BOMs'] and d['items_disabled'] and d['docstatus']==0
    assert d['quantity_reconciliation']['all_counts_reconciled']
    assert d['quantity_reconciliation']['vehicle_occurrences']==24
    assert d['quantity_reconciliation']['added_onboard_launch_occurrences']>0
    assert d['quantity_reconciliation']['wayside_launch_occurrences']>0
    assert d['quantity_reconciliation']['exploded_onboard_occurrences']==24+d['quantity_reconciliation']['added_onboard_launch_occurrences']
    assert d['quantity_reconciliation']['identical_six_car_BOM']
    assert len(d['item_drafts'])==len(d['rfq_drafts'])==len(d['routing_drafts'])
    assert len({r['item_code'] for r in d['item_drafts']})==len(d['item_drafts'])
    assert {r['item_name'] for r in d['assembly_item_drafts']}=={'CAR','TRAIN','WAYSIDE-PLANT'}
    assert not d['production_orders'] and not d['active_assets'] and not d['external_transactions_performed']
    assert result['complete_installed_cost_usd'] is None and result['whole_life_cost_usd'] is None


def test_every_export_is_candidate_revision_linked_inactive_and_no_vendor_price_is_invented(inputs):
    result=p.compile(*inputs[:3],inputs[3]);d=result['ERPNext_drafts'];cid=inputs[3]
    for name in ('item_drafts','assembly_item_drafts','operation_drafts','routing_drafts','workstation_drafts','rfq_drafts'):
        for r in d[name]:
            assert r['candidate_id']==cid and r['disabled']==1 and r['docstatus']==0
            assert not r['submission_allowed'] and r['import_validation_required']
            assert r['draft_id']==identity({k:v for k,v in r.items() if k!='draft_id'})
    for r in d['BOM_drafts']:
        assert r['candidate_id']==cid and r['docstatus']==0 and r['is_active']==r['is_default']==0
        assert not r['submission_allowed'] and not r['approved']
    for r in d['rfq_drafts']:
        assert not r['suppliers'] and not r['send_supplier_emails'] and r['company'] is None
        assert r['items'][0]['rate'] is None and r['items'][0]['amount'] is None
    for r in d['item_drafts']:assert r['valuation_rate'] is None and r['standard_rate'] is None


def test_multilevel_car_bom_explodes_exact_part_multiplicity_and_operations_resolve(inputs):
    d=p.compile(*inputs[:3],inputs[3])['ERPNext_drafts'];boms={b['source_assembly_scope']:b for b in d['BOM_drafts']}
    car=boms['one-proposed-car-with-counted-launch-interface'];train=boms['six-repeated-cars']
    assert len(train['items'])==1 and train['items'][0]['qty']==6 and train['items'][0]['bom_no']==car['name']
    items={i['item_code']:i for i in d['item_drafts']};ops={o['name'] for o in d['operation_drafts']}
    source=Counter(o['part_definition_id'] for o in inputs[0]['registry']['occurrences'])
    for line in car['items']:
        item=items[line['item_code']]
        if item['source_scope']=='vehicle':assert line['qty']*6==source[item['part_definition_id']]
    assert all(step['operation'] in ops for r in d['routing_drafts'] for step in r['operations'])
    assert all(step['time_in_mins'] is None and step['approved_work_instruction'] is None for r in d['routing_drafts'] for step in r['operations'])


def test_nonrepeated_car_layout_is_not_falsely_divided_into_six_identical_boms(inputs):
    v,c,a,cid=inputs;v=deepcopy(v);reg=v['registry'];reg['occurrences'][0]['occurrence_id']='special-package/body'
    from engineering.component_registry.registry import _physical
    reg['candidate_id']=identity(_physical(reg))
    for o in reg['occurrences']:o['candidate_id']=reg['candidate_id']
    reg['registry_id']=identity({k:x for k,x in reg.items() if k!='registry_id'})
    v['candidate_id']=reg['candidate_id'];v['evaluation_id']=identity({k:x for k,x in v.items() if k!='evaluation_id'})
    alt=a_module().evaluate(v);cid=identity({'body':v['candidate_id'],'alternative':alt['candidate_id']})
    civil=dict(c,candidate_id=cid,body_candidate_id=v['candidate_id'],alternative_candidate_id=alt['candidate_id']);civil['evaluation_id']=identity({k:x for k,x in civil.items() if k!='evaluation_id'})
    d=p.compile(v,civil,alt,cid)['ERPNext_drafts']
    assert not d['quantity_reconciliation']['identical_six_car_BOM']
    assert {b['source_assembly_scope'] for b in d['BOM_drafts']}=={'actual-nonrepeated-owned-occurrences','counted-launch-plant-only-civil-separate'}


def a_module():
    from engineering.railway_progress import alternatives
    return alternatives


def test_physical_quantity_duplicates_and_mixed_candidate_rejected(inputs):
    v,c,a,cid=inputs
    with pytest.raises(ValueError):p.compile(v,c,a,'f'*64)
    bad=deepcopy(a);bad['inventory'].append(deepcopy(bad['inventory'][0]));bad['evaluation_id']=identity({k:x for k,x in bad.items() if k!='evaluation_id'})
    newc=dict(c,alternative_candidate_id=bad['candidate_id']);newc['evaluation_id']=identity({k:x for k,x in newc.items() if k!='evaluation_id'})
    with pytest.raises(ValueError,match='Unique|routing|Duplicate'):p.compile(v,newc,bad,cid)
    with pytest.raises(ValueError):p.compile(v,c,a,'g'*64)


def test_changed_launch_hardware_produces_new_disabled_records_not_active_order_mutation(inputs):
    v,c,old,cid=inputs;new=a.revise(v,old,{'roller_pairs_per_bank':5,'motor_count':10})
    newcid=identity({'body':v['candidate_id'],'alternative':new['candidate_id']});newc=dict(c,candidate_id=newcid,alternative_candidate_id=new['candidate_id'])
    newc['evaluation_id']=identity({k:x for k,x in newc.items() if k!='evaluation_id'})
    one=p.compile(v,c,old,cid)['ERPNext_drafts'];two=p.compile(v,newc,new,newcid)['ERPNext_drafts']
    assert one['export_id']!=two['export_id']
    assert {x['item_code'] for x in one['item_drafts']}.isdisjoint({x['item_code'] for x in two['item_drafts']})
    assert not one['production_orders'] and not two['production_orders'] and not two['active_BOMs']


def test_actual_V1_part_master_exports_real_multilevel_drafts_and_occurrence_counts():
    from engineering.reference_cell import vehicles
    v=vehicles.evaluate('V1');alt=a.evaluate(v);cid=identity({'body':v['candidate_id'],'alternative':alt['candidate_id']})
    civil=dict(candidate_id=cid,body_candidate_id=v['candidate_id'],alternative_candidate_id=alt['candidate_id'],construction_sequence=[])
    civil['evaluation_id']=identity(civil)
    r=p.compile(v,civil,alt,cid);d=r['ERPNext_drafts']
    actual_defs=len(v['registry']['parts']);assert actual_defs>100
    assert len([item for item in d['item_drafts'] if item['source_scope']=='vehicle'])==actual_defs
    assert d['quantity_reconciliation']['vehicle_occurrences']==len(v['registry']['occurrences'])
    assert len([bom for bom in d['BOM_drafts'] if bom['source_assembly_scope']=='six-repeated-cars'])==1
    assert d['quantity_reconciliation']['identical_six_car_BOM'] and d['quantity_reconciliation']['all_counts_reconciled']
    assert r['purchased_occurrences']>0 and r['unpriced_part_ids']
    assert r['complete_installed_cost_usd'] is None and not d['submission_allowed']
