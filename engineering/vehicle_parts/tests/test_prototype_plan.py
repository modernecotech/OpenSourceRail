"""Same-candidate and installation refusal controls for the car planning view."""
from copy import deepcopy
from pathlib import Path
import pytest

from engineering.vehicle_parts import ROOT
from engineering.vehicle_parts import prototype_plan as plan


def records():
    return (plan.read(ROOT,'docs/design-engine/current/evaluation.json.gz'),
            plan.read(ROOT,'docs/design-engine/mass-reconciliation/current/summary.json'),
            plan.read(ROOT,'docs/design-engine/current/exports/assembly.json'),
            plan.read(ROOT,'docs/design-engine/v07-execution/door-interface-handoff.json'),
            plan.read(ROOT,'docs/design-engine/vehicle-parts/manufacturing-bundle.json.gz'))


def test_published_plan_is_reproducible_and_keeps_unknown_installation():
    result=plan.build()
    assert result['plan_id']==plan.read(ROOT,'docs/design-engine/v07-representative-car/plan.json')['plan_id']
    assert result['mass_account']['complete_installed_tare_kg_per_car'] is None
    assert result['mass_account']['complete_installed_CG_m'] is None
    assert result['mass_account']['residual_reference_or_unlocated_kg_per_car']==pytest.approx(10090.199590843558)
    assert result['nominal_geometry']['bogie_centre_x_m']==[-6.4,6.4]
    assert [d['ideal_guide_end_stock_m'] for d in result['nominal_geometry']['door_openings']]==pytest.approx([.03,.03])
    assert result['nominal_geometry']['door_openings'][0]['nominal_leaf_x_sweep_m']==pytest.approx([-5.92,-3.08])
    assert all(row['selection_status'].startswith('research child') for row in result['structural_and_running_gear_quote_scopes'])
    assert not result['physical_accepted'] and not result['manufacturing_release']


def test_mixed_candidate_and_mass_closure_are_refused():
    selected,mass,assembly,door,child=records()
    bad=deepcopy(selected);bad['candidate_id']='a'*64
    with pytest.raises(ValueError,match='Mixed selected physical candidate'):
        plan.compose(bad,mass,assembly,door,child)
    bad=deepcopy(mass);bad['residual_reference_or_unlocated_mass_kg']=0
    with pytest.raises(ValueError,match='Residual mass account'):
        plan.compose(selected,bad,assembly,door,child)


def test_changed_running_gear_or_insufficient_door_guide_is_refused():
    selected,mass,assembly,door,child=records()
    bad=deepcopy(selected)
    next(p for p in bad['vehicle']['geometry_parts'] if p['id']=='bogie/0/axle/0')['at_m'][0]+=.1
    with pytest.raises(ValueError,match='reference interfaces differ'):
        plan.compose(bad,mass,assembly,door,child)
    bad=deepcopy(door)
    next(p for p in bad['parts'] if p['part_id']=='body/door-guide-rail')['stock']['length_m']=2.8
    with pytest.raises(ValueError,match='Door guide'):
        plan.compose(selected,mass,assembly,bad,child)


def test_research_door_cannot_be_relabelled_installed():
    selected,mass,assembly,door,child=records()
    bad=deepcopy(door);bad['installed_geometry_verified']=True
    with pytest.raises(ValueError,match='Unverified door'):
        plan.compose(selected,mass,assembly,bad,child)


def test_underframe_erp_draft_is_disabled_and_reconciles_exact_leaves():
    result=plan.build_erp_draft()
    assert result['source_plan_id']==plan.build()['plan_id']
    assert result['assembly_id']=='body/underframe'
    assert len(result['BOM']['items'])==16
    assert sum(row['qty'] for row in result['BOM']['items'])==565
    assert len(result['items'])==17
    assert all(item['disabled']==1 and item['unit_price'] is None and item['supplier'] is None
               for item in result['items'])
    assert all(row['rate'] is None for row in result['BOM']['items'])
    assert all(row['material_cost_usd'] is None and row['process_hours'] is None
               and row['supplier_quote_id'] is None for row in result['make_buy_supplier_rows'])
    assert all(step['time_in_mins'] is None and step['workstation'] is None
               for step in result['Routing']['operations'])
    assert result['BOM']['is_active']==0 and result['BOM']['docstatus']==0
    assert result['selected_installed_mass_added_kg'] is None
    assert result['selected_installed_cost_added_usd'] is None
    assert result['production_orders']==result['purchase_orders']==result['work_orders']==[]
    assert result['posted'] is result['ready_for_import'] is result['external_transactions_performed'] is False


def test_underframe_erp_draft_refuses_mixed_candidate_or_quantity():
    value=plan.build()
    bad=deepcopy(value);bad['research_child_candidate_id']=bad['candidate_id']
    bad['plan_id']=plan.sha256(plan.encoded({k:v for k,v in bad.items() if k!='plan_id'})).hexdigest()
    with pytest.raises(ValueError,match='Research child cannot'):
        plan.compose_erp_draft(bad)
    bad=deepcopy(value);scope=next(s for s in bad['structural_and_running_gear_quote_scopes']
                                  if s['assembly_id']=='body/underframe')
    scope['counted_leaf_pieces_per_car']+=1
    bad['plan_id']=plan.sha256(plan.encoded({k:v for k,v in bad.items() if k!='plan_id'})).hexdigest()
    with pytest.raises(ValueError,match='leaf pieces do not reconcile'):
        plan.compose_erp_draft(bad)
    bad=deepcopy(value);scope=next(s for s in bad['structural_and_running_gear_quote_scopes']
                                  if s['assembly_id']=='body/underframe')
    scope['leaf_quote_rows'][0]['provisional_direct_cost_each_usd']=0
    bad['plan_id']=plan.sha256(plan.encoded({k:v for k,v in bad.items() if k!='plan_id'})).hexdigest()
    with pytest.raises(ValueError,match='zero-priced'):
        plan.compose_erp_draft(bad)


def test_erp_draft_refuses_stale_plan_source(tmp_path,monkeypatch):
    current=plan.build()
    source=tmp_path/'docs/design-engine/v07-representative-car/plan.json'
    source.parent.mkdir(parents=True)
    source.write_bytes(b'{"stale":true}\n')
    monkeypatch.setattr(plan,'build',lambda root: current)
    with pytest.raises(ValueError,match='plan source changed'):
        plan.build_erp_draft(tmp_path)
