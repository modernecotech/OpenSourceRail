"""Research delivery records follow wheel support without inventing release/cost."""
from copy import deepcopy
import gzip,json
import pytest
from engineering.development_baseline import evaluate,exports,FLAGS
from engineering.station_rail.evaluation import IDS

@pytest.fixture(scope='module')
def current():return evaluate.build()

def test_shared_physical_identity_and_independent_brake_interfaces(current):
    result=exports.compile(current)
    for value in result.values():
        assert all(value[k]==current[k] for k in IDS)
        assert all(value[k] is v for k,v in FLAGS.items())
    c=result['controls']
    assert c['wheel_suspension_independent_of_station_power']
    assert not c['magnetic_suspension_inputs']
    assert c['qualified_braking_floor_m_s2'] is None
    assert c['actual_physical_headway_s'] is None
    assert c['addressed_sections_per_direction']==72
    assert result['bom']['onboard_traction_battery_kWh']==0
    assert result['bom']['service_battery']['gross_energy_kWh']>0
    assert result['bom']['retained_component_ancestry']

def test_unknown_prices_dates_equipment_and_processes_remain_unknown(current):
    result=exports.compile(current)
    cost=result['selected_vehicle_cost']
    system=result['selected_system_cost']
    assert result['procurement']['total_price_USD'] is None
    assert result['procurement']['first_material_consumption_dates'] is None
    assert result['procurement']['material_availability_blocks_consumption']
    assert result['assembly']['scheduled_start_dates'] is None
    assert result['manufacturing']['production_labour_hours_per_car'] is None
    schedule=result['manufacturing']['line_linked_process_hour_schedule']
    assert schedule==result['assembly']['vehicle_process_hour_schedule']
    assert schedule['schema']=='osr-v06-line-linked-process-hours/1'
    for key in (*IDS,'evaluation_id'):
        assert schedule[key]==current[key]
    assert schedule['cost_estimate_id']==cost['cost_estimate_id']
    assert schedule['hours_unit']=='process-hour'
    assert schedule['production_shift_basis']==cost['shifts']['production_per_day']
    assert schedule['engineering_process_qualified'] is False
    assert schedule['macro_operation_allocation'].startswith('unallocated;')
    assert all(op['labour_hours'] is None for op in result['manufacturing']['operations'])
    assert all(row['line_id'] and row['source_ids'] is not None
        and row['occurrence_ids'] is not None for row in schedule['work_packages'])
    assert all(row['engineering_process_qualified'] is False for row in schedule['work_packages'])
    cases=('low','base','high')
    line_hours={row['line_id']:row for row in schedule['work_packages']}
    expected_lines=[line for line in cost['lines'] if line['stage']!='reference-delivery']
    assert set(line_hours)=={line['line_id'] for line in expected_lines}
    for line in expected_lines:
        row=line_hours[line['line_id']]
        assert row['line_key']==line['line_key']
        assert row['source_ids']==line['source_ids']
        assert row['occurrence_ids']==line['occurrence_ids']
    for case in cases:
        assert schedule['work_package_hours_per_train'][case]==pytest.approx(sum(
            row['process_hours_per_train'][case] for row in schedule['work_packages']))
        assert schedule['factory_process_hours_per_train'][case]==pytest.approx(sum(
            row['process_hours_per_train'][case] for row in schedule['work_packages']
            if row['stage']!='final-assembly'))
        assert schedule['final_assembly_labour_hours_per_train'][case]==pytest.approx(sum(
            row['process_hours_per_train'][case] for row in schedule['work_packages']
            if row['stage']=='final-assembly'))
    assert result['civil']['fully_installed_route_quantities'] is None
    assert not result['bom']['complete_installed_BOM']
    assert cost['candidate_id']==current['candidate_id']
    assert cost['evaluation_id']==current['evaluation_id']
    assert cost['whole_life_cost_iqd'] is None
    assert system['candidate_id']==current['candidate_id']
    assert system['vehicle_evaluation_id']==current['evaluation_id']
    assert system['model_cost_complete_for_declared_case'] is True
    assert system['physical_mass_complete'] is False
    assert system['physical_journey_completed'] is False

def test_mixed_city_selection_is_rejected(current):
    index={k:current[k] for k in IDS};index['city_count']=266
    assert exports.compile(current,city_index=index)['procurement']['city_scope']['city_count']==266
    index['support_component_id']='0'*64
    with pytest.raises(ValueError,match='city index belongs'):exports.compile(current,city_index=index)

def test_delivery_hash_and_regeneration_detect_changed_control(tmp_path,current):
    exports.write(tmp_path,current)
    assert exports.verify(tmp_path,current)['current']
    cost=json.loads((tmp_path/'selected-vehicle-cost.json').read_bytes())
    assert cost['candidate_id']==current['candidate_id']
    assert cost['physical_accepted'] is False
    system=json.loads((tmp_path/'selected-system-cost.json').read_bytes())
    assert system['candidate_id']==current['candidate_id']
    assert system['physical_accepted'] is False
    data=json.loads(gzip.decompress((tmp_path/'engineering-bom.json.gz').read_bytes()))
    assert data['stock_inventory_per_car']==current['vehicle']['inventory']
    p=tmp_path/'controls.json';value=json.loads(p.read_bytes());value['target_headway_s']=60.;p.write_text(json.dumps(value))
    with pytest.raises(ValueError,match='payload differs'):exports.verify(tmp_path,current)


def test_same_reference_ifc_is_byte_reproducible_between_directories(tmp_path,current):
    first=tmp_path/'a';second=tmp_path/'b'
    exports.write(first,current);exports.write(second,current)
    assert (first/'selected-interface.ifc').read_bytes()==(second/'selected-interface.ifc').read_bytes()
