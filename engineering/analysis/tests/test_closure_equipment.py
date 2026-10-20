"""One instance definition must drive gross mass, conductors and thermal counts."""
from copy import deepcopy
import pytest
from engineering.assembly_design import baseline,models,cassette_detail,cassette_duty,installed_equipment as equipment,system_design
from engineering.twin_workflow import core


@pytest.fixture
def definition():
    p=core.read(baseline.DATA)
    base=models.build(p,'service-cassette',next(models.candidates(p,'service-cassette')))
    candidate=cassette_detail.build(p,base,guide_clearance_m=.009,connector_float_m=.006,seal_compression=.25)
    return p,candidate,equipment.build(p,candidate)


def test_all_instances_mass_inertia_harness_and_counts_are_coherent(definition):
    p,c,value=definition
    assert value['car_count']==6 and value['counts']==dict(cassettes_per_car=8,cooling_modules_per_car=3)
    assert len(value['instances'])==48 and len(value['purchased_boundaries'])==18
    assert len({i['id'] for i in value['instances']})==48
    mass=sum(part['properties']['mass_kg'] for part in c['contract']['parts'] if part['id'] in c['metadata']['cassette_installed_part_ids'])
    assert value['represented_gross_properties']['mass_kg']==pytest.approx(48*mass)
    assert value['schedule']['cassette_conductor_cut_m']==pytest.approx(48*c['metadata']['harness_cut_totals_m']['cassette'])
    assert value['schedule']['vehicle_pigtail_cut_m']==pytest.approx(48*c['metadata']['harness_cut_totals_m']['vehicle'])
    assert value['schedule']['complete_installed_mass_kg'] is None and value['schedule']['installed_cost_usd'] is None
    assert value['schedule']['trunk_route_m'] is None
    assert all(not i['maintenance_access_verified'] for i in value['instances'])
    assert all(value[k] is False for k in core.FLAGS)


def test_thermal_and_system_models_bind_exact_same_definition(definition):
    p,c,value=definition
    transient=cassette_duty.campaign(candidate=c,equipment=value)
    assert transient['equipment_definition_revision']==value['revision']
    assert all(case['result']['hypotheses']['number_of_duct_cassettes']==value['counts']['cassettes_per_car'] for case in transient['thermal'])
    assert all(case['result']['case']['module_count']==value['counts']['cooling_modules_per_car'] for case in transient['thermal'])
    config=system_design.defaults(value)
    assert config['equipment_definition_revision']==value['revision']
    assert config['fan_power_w']*6==pytest.approx(value['schedule']['model_fan_input_w'])
    changed=deepcopy(value);changed['counts']['cassettes_per_car']=1
    with pytest.raises(ValueError):cassette_duty.campaign(candidate=c,equipment=changed)


def test_mutated_part_geometry_cannot_keep_original_equipment_identity(definition):
    p,c,value=definition;c['metadata']['cassette_installed_part_ids'].pop()
    with pytest.raises(ValueError):equipment.build(p,c)
