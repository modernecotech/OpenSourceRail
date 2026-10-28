from pathlib import Path
from copy import deepcopy
import pytest
from engineering.reference_cell import vehicles
from engineering.sourced_case import equipment,power_revision,charging as c
from engineering.sourced_case import identity
ROOT=Path(__file__).resolve().parents[3]
@pytest.fixture(scope='module')
def equip():return power_revision.revise(equipment.substitute(vehicles.evaluate('V1',root=ROOT),root=ROOT),root=ROOT)
@pytest.fixture(scope='module')
def journey(equip):
    r=dict(candidate_id='a'*64,body_candidate_id=equip['candidate_id'],journey_time_s=152.,energy_J=dict(auxiliary=6*14000*152),scenario=dict(auxiliary_W_per_car=14000.))
    r['evaluation_id']=identity(r);return r
@pytest.fixture(scope='module')
def result(equip,journey):return c.design(equip,journey,88.,root=ROOT)


def test_directional_low_voltage_and_converter_inventory(result):
    s=result['sizing'];assert s['source_limited_output_W_per_EPC']==4950.
    assert s['required_total_EPC_per_car']==8
    assert s['additional_EPC_per_car']==5
    assert s['train_peak_HV_supply_W']==pytest.approx(264000)
    assert s['train_peak_supply_current_A']==pytest.approx(440)
    assert len([o for o in result['occurrences'] if 'extra-EPC' in o['occurrence_id']])==30
    assert not result['existing_body_silently_modified']


def test_soc_energy_conservation_and_failed_converter(result):
    assert result['nominal']['restored']
    assert abs(result['nominal']['energy_residual_J'])<1e-4
    assert not result['one_EPC_failure_per_car']['restored']
    assert result['one_EPC_failure_per_car']['restoration_deficit_Wh']>0
    assert max(x.get('LV_current_A',0) for x in result['nominal']['trace'])<=1000
    assert max(x.get('net_battery_charge_current_A',0) for x in result['nominal']['trace'])<=800


def test_source_temperature_and_prices_are_held(result):
    assert result['source_caps']['supply_at_selected_hot_ambient_W'] is None
    assert result['complete_installed_price_USD'] is None
    assert result['partial_public_price']['listed_scope_total_USD'] is None
    assert result['partial_public_price']['candidate_id']==result['candidate_id']
    assert result['sources']['supply']['sha256']
    assert result['sources']['QCC_family_rating']['sha256'] is None
    assert all(result[k] is False for k in c.FLAGS)


def test_sized_assemblies_and_unknown_complete_mass(result):
    for p in result['parts']:assert p['mass']['lower_bound_kg']>0 and p['geometry']['dimensions_m']
    assert all(len(o['transform'])==4 and o['candidate_id']==result['candidate_id'] for o in result['occurrences'])
    assert result['assembly']['ACD_fixation_points_per_unit']==8
    assert not result['assembly']['actual_swept_clearance_proved']
    assert result['complete_installed_mass_kg'] is None


def test_short_layover_and_hypothesis_revision(equip,journey,result):
    r=c.design(equip,journey,35.,root=ROOT)
    assert r['sizing']['required_total_EPC_per_car']>8
    assert not r['nominal']['restored']
    assert r['candidate_id']!=result['candidate_id']
    r=c.design(equip,journey,88.,converter_efficiency=.91,root=ROOT)
    assert r['candidate_id']==result['candidate_id']
    assert r['evaluation_id']!=result['evaluation_id']


def test_mixed_identity_and_energy_forgery_rejected(equip,journey):
    bad=deepcopy(journey);bad['body_candidate_id']='b'*64;bad.pop('evaluation_id');bad['evaluation_id']=identity(bad)
    with pytest.raises(ValueError):c.design(equip,bad,88.,root=ROOT)
    bad=deepcopy(journey);bad['energy_J']['auxiliary']*=2;bad.pop('evaluation_id');bad['evaluation_id']=identity(bad)
    with pytest.raises(ValueError):c.design(equip,bad,88.,root=ROOT)
    with pytest.raises(ValueError):c.design(equip,journey,88.,converter_efficiency=.99,root=ROOT)


def test_unknown_connection_time_does_not_become_zero(result):
    assert result['assumptions']['actual_connection_isolation_disconnect_time_s'] is None
    assert result['actual_terminal_cycle_restored'] is None
    assert result['sizing']['maximum_total_connection_disconnect_overhead_s']==pytest.approx(4.875)
