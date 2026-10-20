"""One controlled instance definition for mass, services and duty sensitivities.

Missing refrigeration, trunk-route, maintenance and commercial data remain null.
Known gross additions never replace a complete vehicle BOM or earn removal credit.
"""
from pathlib import Path
import math

from engineering.twin_workflow import core

DATA=Path(__file__).parent/'data/equipment-layout.json'


def layout():
    value=core.read(DATA)
    if value['schema']!='osr-installed-equipment-layout/1' or value['architecture']!='baghdad-six-car':
        raise ValueError('controlled Baghdad equipment layout required')
    for key in ('cassette_local_positions_m','cooling_module_local_positions_m'):
        points=value[key]
        if not points or len(points)>24 or len({tuple(p) for p in points})!=len(points):raise ValueError('bounded unique equipment positions required')
        if any(len(p)!=3 or any(type(v) not in (int,float) or not math.isfinite(v) for v in p) for p in points):
            raise ValueError('finite equipment positions required')
    if any(value.get(k) is not False for k in core.FLAGS):raise ValueError('equipment layout cannot issue release')
    return value


def counts():
    definition=layout()
    return dict(cassettes_per_car=len(definition['cassette_local_positions_m']),
        cooling_modules_per_car=len(definition['cooling_module_local_positions_m']))


def build(policy,candidate):
    from osr_mech.family_definition import family_definition
    from . import cassette_system,cassette_detail,integration,models
    definition=layout()
    if candidate.get('kind')!='service-cassette-detail' or policy['architecture']!=definition['architecture']:
        raise ValueError('exact detailed cassette and Baghdad architecture required')
    base=models.build(policy,'service-cassette',candidate['metadata']['base_variables'])
    expected=cassette_detail.build(policy,base,**candidate['variables'])
    if core.digest(candidate)!=core.digest(expected):
        raise ValueError('detailed cassette content differs')
    parts=[p for p in candidate['contract']['parts'] if p['id'] in candidate['metadata']['cassette_installed_part_ids']]
    instances=[];allocations=[];boundaries=[]
    lengths=candidate['metadata']['harness_cut_totals_m']
    electrical=cassette_system.electrical_case(female_length_m=lengths['cassette']/8,male_length_m=lengths['vehicle']/8)
    duct=cassette_system.duct_case(candidate['metadata']['duct_clear_area_m2'])
    cars=family_definition('metro-6car')['cars']
    for car_number,car in enumerate(cars,start=1):
        for i,point in enumerate(definition['cassette_local_positions_m']):
            identity=car['id']+'/service-cassette-'+str(i+1).zfill(2)
            position=[point[0]+car['centre_x_m'],point[1],point[2]]
            allocation=dict(id=identity,body_id=car['id'],candidate_revision=candidate['revision'],
                translation_m=position,rotation=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])
            allocations.append(allocation)
            instances.append(dict(**allocation,function='lv-ventilation-cassette',
                electrical_node_id=f'car-{car_number:02d}/lv-cassette',
                local_position_m=point,interfaces=['vehicle-mount','LV-feed','protective-bond','air-in','air-out','locking-indication'],
                cassette_conductor_cut_length_m=lengths['cassette'],
                vehicle_pigtail_cut_length_m=lengths['vehicle'],trunk_route_length_m=None,
                model_lv_source_w=electrical['power_w']['source'],model_fan_input_w=duct['fan_input_w'],
                model_ventilation_conditioning_w=duct['conditioning_demand_w'],
                maintenance_access_verified=False,installed_cost_usd=None))
        for i,point in enumerate(definition['cooling_module_local_positions_m']):
            boundaries.append(dict(id=car['id']+'/cooling-module-'+str(i+1).zfill(2),body_id=car['id'],
                electrical_node_id=f'car-{car_number:02d}/hvac',
                function='refrigeration-boundary',local_position_m=point,
                translation_m=[point[0]+car['centre_x_m'],point[1],point[2]],
                supplier_configuration=None,geometry=None,mass_kg=None,power_map=None,
                installed_cost_usd=None,maintenance_access_verified=False))
    properties=integration.mass_properties(parts,allocations)
    result=dict(schema='osr-installed-equipment-definition/1',architecture=definition['architecture'],
        layout_sha256=core.sha(DATA),candidate_revision=candidate['revision'],car_count=len(cars),
        duct_clear_area_m2=candidate['metadata']['duct_clear_area_m2'],
        counts=counts(),instances=instances,purchased_boundaries=boundaries,allocations=allocations,
        represented_part_ids=[p['id'] for p in parts],represented_gross_properties=properties,
        schedule=dict(cassette_conductor_cut_m=sum(i['cassette_conductor_cut_length_m'] for i in instances),
            vehicle_pigtail_cut_m=sum(i['vehicle_pigtail_cut_length_m'] for i in instances),trunk_route_m=None,
            model_lv_source_w=sum(i['model_lv_source_w'] for i in instances),
            model_fan_input_w=sum(i['model_fan_input_w'] for i in instances),
            model_ventilation_conditioning_w=sum(i['model_ventilation_conditioning_w'] for i in instances),
            complete_installed_mass_kg=None,complete_installed_power_w=None,installed_cost_usd=None),
        no_removal_credit=True,complete_vehicle_equipment_map=False,
        scope=definition['scope'],**core.FLAGS)
    result['revision']=core.digest(result);return result
