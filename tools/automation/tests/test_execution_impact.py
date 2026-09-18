import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'deployment/erpnext/apps/osr_erpnext'))
from osr_erpnext.execution_impact import revision_review


def fixture():
    mapping = dict(name='M1', component_type_id='panel', engineering_revision='R1',
                   erp_item_code='FG', production_bom='B1')
    boms = {'B1': dict(item='FG', docstatus=1, modified='1', items=[dict(item='SUB', bom='B2')]),
            'B2': dict(item='SUB', docstatus=1, modified='1', items=[dict(item='RAW', bom=None)])}
    orders = [dict(document='PO1', item='RAW'), dict(document='PO2', item='OTHER')]
    work = [dict(name='WO1', item='FG', bom='B1'), dict(name='WO2', item='SUB', bom='B2'),
            dict(name='WRONG-REV', item='FG', bom='B0'), dict(name='WRONG-ITEM', item='OTHER', bom='B1')]
    moves = [dict(name='SE1', work_order='WO1'), dict(name='SE2', work_order='WRONG-REV')]
    return mapping, boms, orders, work, moves


def review(data, visibility=None):
    mapping, boms, orders, work, moves = data
    return revision_review(mapping, boms.get, orders, work, moves, visibility or {},
                           dict(city='samawah', company='OSR', project='P1'))


def test_nested_exact_bom_dependencies_shared_materials_and_movement_provenance():
    data = fixture(); before = copy.deepcopy(data)
    result = review(data)
    assert [r['name'] for r in result['work_orders']] == ['WO1', 'WO2']
    assert [r['document'] for r in result['purchase_orders']] == ['PO1']
    assert result['purchase_orders'][0]['revision_assignment'] == 'unproven'
    assert [r['name'] for r in result['stock_movements']] == ['SE1']
    assert dict(item='RAW', bom=None, path=['B1', 'B2']) in result['dependency_paths']
    assert not result['automatic_disposition'] and not result['railway_release_authorised']
    assert data == before and review(data)['sha256'] == result['sha256']
    data[3][0]['produced_qty'] = 1
    assert review(data)['sha256'] != result['sha256']


def test_unreadable_nested_bom_is_explicit_partial_coverage_without_guessed_materials():
    data = fixture(); del data[1]['B2']
    data[2].append(dict(document='PO-SUB', item='SUB'))
    result = review(data, {'Stock Entry': 'permission-denied'})
    assert result['warnings'] == ['BOM unavailable to this reader: B2', 'Stock Entry: permission-denied']
    assert [r['document'] for r in result['purchase_orders']] == ['PO-SUB']
    assert [r['name'] for r in result['work_orders']] == ['WO1']


def test_cycles_and_item_mismatch_cannot_claim_unrelated_production():
    data = fixture(); data[1]['B2']['items'] = [dict(item='FG', bom='B1')]
    assert 'Cyclic BOM reference: B1' in review(data)['warnings']
    data[1]['B1']['item'] = 'UNRELATED'
    result = review(data)
    assert result['warnings'] == ['BOM/Item mismatch: B1']
    assert not result['work_orders'] and not result['stock_movements']


def test_no_bom_does_not_fall_back_to_all_project_work():
    data = fixture(); data[0]['production_bom'] = None
    result = review(data)
    assert result['warnings'] and not result['work_orders'] and not result['stock_movements']
