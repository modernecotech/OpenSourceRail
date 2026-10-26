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
    assert result['procurement']['total_price_USD'] is None
    assert result['procurement']['first_material_consumption_dates'] is None
    assert result['procurement']['material_availability_blocks_consumption']
    assert result['assembly']['scheduled_start_dates'] is None
    assert result['manufacturing']['production_labour_hours_per_car'] is None
    assert result['civil']['fully_installed_route_quantities'] is None
    assert not result['bom']['complete_installed_BOM']

def test_mixed_city_selection_is_rejected(current):
    index={k:current[k] for k in IDS};index['city_count']=266
    assert exports.compile(current,city_index=index)['procurement']['city_scope']['city_count']==266
    index['support_component_id']='0'*64
    with pytest.raises(ValueError,match='city index belongs'):exports.compile(current,city_index=index)

def test_delivery_hash_and_regeneration_detect_changed_control(tmp_path,current):
    exports.write(tmp_path,current)
    assert exports.verify(tmp_path,current)['current']
    data=json.loads(gzip.decompress((tmp_path/'engineering-bom.json.gz').read_bytes()))
    assert data['stock_inventory_per_car']==current['vehicle']['inventory']
    p=tmp_path/'controls.json';value=json.loads(p.read_bytes());value['target_headway_s']=60.;p.write_text(json.dumps(value))
    with pytest.raises(ValueError,match='payload differs'):exports.verify(tmp_path,current)


def test_same_reference_ifc_is_byte_reproducible_between_directories(tmp_path,current):
    first=tmp_path/'a';second=tmp_path/'b'
    exports.write(first,current);exports.write(second,current)
    assert (first/'selected-interface.ifc').read_bytes()==(second/'selected-interface.ifc').read_bytes()
