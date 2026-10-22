"""Independent physical controls, quantity cost reconciliation and adverse cases."""
from copy import deepcopy
import json
import math
from pathlib import Path
import subprocess
import sys

import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from engineering.ferrite_maglev import model,delivery,station


@pytest.fixture(scope='module')
def context():return model.load()


def test_primary_policy_configuration_and_release_boundary_are_explicit(context):
    policy,c,_=context
    assert (ROOT/'VERSION').read_text().strip()=='0.5'
    assert policy['development']['primary_family']==c['metadata']['family']=='ferrite-pm-maglev-study'
    assert c['vehicle']['cars_per_train']==6
    assert c['metadata']['schema']=='osr-ferrite-maglev-study/2'
    assert c['architecture']['primary_costed_propulsion']=='station-and-located-booster-lsm-shared-vehicle-pm'
    assert c['architecture']['station_zone_powered_stator']
    assert c['architecture']['onboard_support_guidance_windings']
    assert not c['architecture']['onboard_main_traction']
    assert c['architecture']['interstation_powered_propulsion']
    assert c['architecture']['located_booster_powered_stator']
    assert not c['architecture']['interstation_continuous_powered_stator']
    assert c['operating_strategy']['junction_operation']=='passenger-transfer-between-fixed-lines'
    assert c['operating_strategy']['urban_target_stop_spacing_m']==2000
    assert c['mass']['growth_reserve']==1800
    assert c['controls']['preferred_host']=='off-the-shelf-SBC'
    assert policy['objectives']['linear_electromagnetic_propulsion_required']
    assert not policy['objectives']['all_vehicle_moving_parts_eliminated']
    assert all(policy['release'][flag] is False for flag in model.FLAGS)



@pytest.mark.parametrize('ferrite,battery,tare',[(3000,20,14100),(4000,20,15100),(3000,30,14200),(4000,30,15200)])
def test_mass_contains_magnets_once_and_retains_equal_payload(context,ferrite,battery,tare):
    r=model.mass(context[1],ferrite,battery)
    assert r['tare_kg']==tare and r['aw2_kg']==tare+9000 and r['aw3_kg']==tare+12000
    assert r['eol_window_kwh']==pytest.approx(battery*.6*.8)
    assert r['cg_m'] is None and r['inertia_kg_m2'] is None


@pytest.mark.parametrize('scenario',['low','base','high'])
def test_quantity_costs_reconcile_line_items_scenarios_and_reserve(context,scenario):
    _,c,costs=context;r=model.cost_case(c,costs,scenario,3000,30)
    rates=costs['rates'];factor=costs['scenario_multipliers'][scenario];cars=c['vehicle']['cars_per_train']
    expected=(cars*(rates['body_and_passenger_systems_per_car']+3000*rates['ferrite_per_kg']+
        rates['magnetic_equipment_per_car']+30*rates['battery_pack_per_kwh']+
        rates['capture_brake_per_car']+rates['hvac_auxiliary_per_car']+
        rates['assembly_test_hours_per_car']*rates['labour_per_hour'])+
        (cars-1)*rates['coupling_gangway_per_interface']+rates['train_control_per_train'])*factor
    bill=r['vehicle_bill']
    assert bill['priced_scope_subtotal_usd']==pytest.approx(expected)
    assert bill['integration_reserve_usd']==pytest.approx(expected*rates['vehicle_integration_reserve_fraction'])
    assert r['train_usd']==pytest.approx(expected*(1+rates['vehicle_integration_reserve_fraction']))
    assert sum(x['quantity']*x['unit_rate_usd'] for x in bill['rows'])==pytest.approx(expected)
    civil=r['civil_bill'];q=civil['quantities']
    # Independently count native 20 mm reaction faces: two faces per beam,
    # ten 2.49 m cassettes in 25 m, two directional kilometres per route-km.
    reaction_kg=2*10*2.49*.96*.02*7850/25*2000
    # Two 0.4 m solid end infills per beam are additional to the hollow middle.
    box=c['civil']['narrow_box_screen'];w,h,tw,tf=(box[k] for k in ('outer_width_m','outer_depth_m','web_thickness_m','flange_thickness_m'))
    concrete_m3=(w*h-(w-2*tw)*(h-2*tf)+2*.4*(w-2*tw)*(h-2*tf)/25+.12)*2000
    assert q['reaction_steel_kg_dual_km']==pytest.approx(reaction_kg)
    assert q['concrete_m3_dual_km']==pytest.approx(concrete_m3)
    assert q['reinforcement_kg_dual_km']==pytest.approx(concrete_m3*rates['reinforcement_kg_per_m3'])
    assert q['shared_supports_per_route_km']==40 and q['beam_lifts_per_route_km']==80
    assert r['civil_usd_dual_km']==pytest.approx(sum(x['quantity']*x['unit_rate_usd'] for x in civil['rows']))
    assert r['pilot_usd'] is r['city_total_usd'] is bill['complete_factory_gate_price_usd'] is None
    assert not r['epc_included'] and not r['costs_are_quotes']
    reduced=model.cost_case(c,costs,scenario,3000,20)
    reserve=1+rates['vehicle_integration_reserve_fraction']
    assert r['train_usd']-reduced['train_usd']==pytest.approx(cars*10*rates['battery_pack_per_kwh']*factor*reserve)
    more=model.cost_case(c,costs,scenario,4000,30)
    assert more['train_usd']-r['train_usd']==pytest.approx(cars*1000*rates['ferrite_per_kg']*factor*reserve)
    assert more['civil_usd_dual_km']==r['civil_usd_dual_km']


def test_formation_bills_price_shared_controls_once_and_interfaces_per_connection(context):
    _,c,costs=context
    three=model.cost_case(c,costs,'base',3000,30,cars=3)['vehicle_bill']
    six=model.cost_case(c,costs,'base',3000,30,cars=6)['vehicle_bill']
    small={r['id']:r for r in three['rows']};large={r['id']:r for r in six['rows']}
    assert small['train-control-and-protection']['quantity']==large['train-control-and-protection']['quantity']==1
    assert small['coupling-and-gangway']['quantity']==2 and large['coupling-and-gangway']['quantity']==5
    for ident in small.keys()-{'train-control-and-protection','coupling-and-gangway'}:
        assert large[ident]['quantity']==pytest.approx(2*small[ident]['quantity'])
    rates=costs['rates']
    assert six['total_allowance_usd']-2*three['total_allowance_usd']==pytest.approx(
        (rates['coupling_gangway_per_interface']-rates['train_control_per_train'])*(1+rates['vehicle_integration_reserve_fraction']))



def test_lower_cost_and_localisation_are_targets_with_imported_inputs_visible(context):
    _,c,costs=context
    base=model.cost_case(c,costs,'base',3000,30)
    target=model.cost_case(c,costs,'base',3000,30,hardware_target=90000)
    before=base['magnetic_bundle_usd_train'];reserve=1+costs['rates']['vehicle_integration_reserve_fraction']
    assert target['magnetic_bundle_usd_train']==90000
    assert base['train_usd']-target['train_usd']==pytest.approx((before-90000)*reserve)
    other=lambda r:{x['id']:x for x in r['vehicle_bill']['rows'] if x['id']!='magnetic-modules'}
    assert other(base)==other(target)
    assert target['costs_are_quotes'] is False
    assert model.localisation([dict(id='coil',cost_usd=10000,imported_input_usd=4000)])['local_fraction']==.6
    assert model.localisation([dict(id='coil',cost_usd=10000,imported_input_usd=None)])['local_fraction'] is None
    with pytest.raises(ValueError):model.localisation([dict(id='coil',cost_usd=100,imported_input_usd=101)])



def test_section_matches_parallel_axis_and_keeps_end_infill_loads(context):
    s=model.section(.8,1.8,.10,.15)
    area=2*.8*.15+2*.10*1.5
    inertia=2*(.8*.15**3/12+(.8*.15)*(.9-.075)**2)+2*(.10*1.5**3/12)
    assert s['area_m2']==pytest.approx(area)
    assert s['vertical_i_m4']==pytest.approx(inertia)
    assert s['lateral_i_m4']==pytest.approx(.0498)
    a=model.civil_case(context[1],.8,1.8,20);b=model.civil_case(context[1],.8,1.8,30)
    # End blocks have fixed volume, so changing span also changes mean line load.
    q=lambda length:(.54+.12)*2500+2*.4*.6*1.5*2500/length+300.23424+26200/17
    assert b['total_elastic_deflection_m']/a['total_elastic_deflection_m']==pytest.approx((30/20)**4*q(30)/q(20))
    assert a['relative_gap_accepted'] is None


def test_curve_offset_is_horizontal_and_not_independent_module_sagitta(context):
    r=model.geometry(context[1]);curve=next(x for x in r['curves'] if x['radius_m']==100)
    assert curve['lateral_sagitta_m']==pytest.approx(.18016229225776)
    assert curve['face_width_before_margins_m']==pytest.approx(.8603245845155)
    assert curve['vertical_gap_consumed_by_horizontal_sagitta_m']==0
    assert r['seed_ferrite_mass_kg']==pytest.approx(3000) and r['seed_blocks']==pytest.approx(4800)
    assert r['maxwell_pressure_is_force_prediction'] is False
    assert model.sagitta(1,100)<model.sagitta(12,100)/100


@pytest.mark.parametrize('mass',[23200,26200,24200,27200])
def test_level_duty_separates_station_traction_from_services_battery(context,mass):
    for hot,hotel in [(False,40),(True,60)]:
        r=model.cycle(context[1],mass,hot=hot)
        assert r['kinematic_screen_pass']
        assert r['moving_seconds']==pytest.approx(context[1]['vehicle']['runtime_reference_seconds'])
        assert r['cycle_kwh']==r['services_kwh']==pytest.approx(hotel*(context[1]['vehicle']['runtime_reference_seconds']+60)/3600)
        assert r['propulsion_dc_kwh']==r['recovered_dc_kwh']==0
        assert r['station_traction_input_kwh']>0
        assert r['battery_replacement_kwh']==pytest.approx(hotel*(context[1]['vehicle']['runtime_reference_seconds']+15)/3600)
        assert r['balanced_charger_kw']==pytest.approx((hotel+hotel*(context[1]['vehicle']['runtime_reference_seconds']+15)/45)/context[1]['power']['station_charger_efficiency_assumption'])


def test_station_braking_and_higher_speed_limit_never_create_pack_charge(context):
    c=context[1];a=model.cycle(c,26200,hot=True,regen=False);b=model.cycle(c,26200,hot=True,speed_kmh=90,regen=True)
    required=(60+60*(c['vehicle']['runtime_reference_seconds']+15)/45)/c['power']['station_charger_efficiency_assumption']
    assert a['balanced_charger_kw']==b['balanced_charger_kw']==pytest.approx(required)
    assert a['charger_balance_kwh']['200']<0 and a['charger_balance_kwh']['240']>0
    assert a['recovered_dc_kwh']==b['recovered_dc_kwh']==0
    assert a['station_brake_dc_kwh']>0 and b['station_brake_dc_kwh']>0
    assert 'no vehicle-pack credit' in a['regeneration_destination']
    assert a['achieved_speed_kmh']<80  # speed input is a limit, not powered cruising.


def test_station_energy_and_services_duty_close_independently(context):
    c=context[1];r=model.cycle(c,26200,hot=True)
    t=station.trajectory(cars=1,car_mass_kg=26200,runtime_s=c['vehicle']['runtime_reference_seconds'],acceleration=c['vehicle']['maximum_initial_acceleration_m_s2'],record_trace=True)
    launch=[row for row in t['trace'] if row['phase']=='launch']
    # Independent midpoint integration of the prescribed force demand.
    work=0.
    for left,right in zip(launch,launch[1:]):
        dt=right['time_s']-left['time_s']
        work+=dt*(left['motor_force_n']*left['speed_m_s']+right['motor_force_n']*right['speed_m_s'])/2
    assert work/(.85*3.6e6)==pytest.approx(r['station_traction_input_kwh'],abs=.001)
    assert r['services_kwh']==pytest.approx(60*(c['vehicle']['runtime_reference_seconds']+60)/3600)
    assert r['battery_replacement_kwh']==pytest.approx(60*(c['vehicle']['runtime_reference_seconds']+60-45)/3600)
    heavier=model.cycle(c,27200,hot=True)
    assert heavier['cycle_kwh']==r['cycle_kwh']
    assert heavier['station_traction_input_kwh']>r['station_traction_input_kwh']


@pytest.mark.parametrize('field,value', [('electromagnetic_force_map_validated',True),('fabrication_release_allowed',True),('vehicle_mass_measured',True)])
def test_claimed_release_is_rejected(context,field,value):
    c=deepcopy(context[1]);c['metadata'][field]=value
    with pytest.raises(ValueError):model.validate(c)


@pytest.mark.parametrize('mutate',[
    lambda c:c['power'].update(station_drive_efficiency=0),
    lambda c:c['power'].update(normal_soc_high=1.1),
    lambda c:c['power'].update(charger_effective_seconds=61),
    lambda c:c['power'].update(normal_soc_high=True),
    lambda c:c['power'].update(charger_candidates_kw_per_car=[float('nan')]),
    lambda c:c['vehicle'].update(nominal_car_length_m='TBD'),
    lambda c:c['mass'].update(ferrite_base=float('nan')),
    lambda c:c['vehicle'].update(nominal_car_length_m=True),
    lambda c:c['mass'].update(growth_reserve=1),
    lambda c:c['architecture'].update(route_powered_stator=False),
    lambda c:c['architecture'].update(onboard_main_traction=True),
    lambda c:c['architecture'].update(interstation_powered_propulsion=False),
    lambda c:c['architecture'].update(interstation_continuous_powered_stator=True),
    lambda c:c['architecture'].update(located_booster_powered_stator=False),
    lambda c:c['operating_strategy'].update(junction_operation='route-trains-between-guideways'),
    lambda c:c['operating_strategy'].update(urban_target_stop_spacing_m=1200)])
def test_invalid_physical_inputs_fail_closed(context,mutate):
    c=deepcopy(context[1]);mutate(c)
    with pytest.raises(ValueError):model.validate(c)


def test_requirements_have_unique_source_locations_and_no_acceptance():
    rows=model.requirement_register();ids=[r['id'] for r in rows]
    assert len(ids)==len(set(ids)) and len(ids)>=60
    assert {'SYS-001','MAG-055','CIV-007','CTL-007','MFG-005'}<=set(ids)
    assert all(r['state']=='open' and r['accepted'] is False for r in rows)


def test_primary_publication_tamper_stale_and_source_binding(tmp_path):
    out=tmp_path/'packet';m=delivery.publish(out);delivery.publish(out,check=True)
    r=json.loads((out/'result.json').read_text())
    assert len(r['civil_section_candidates'])==45 and len(r['cost_cases'])==12 and len(r['energy_cases'])==16
    assert all(r[k] is False for k in model.FLAGS)
    assert all(g['accepted'] is False for g in r['gates'])
    assert len(r['work_packages'])==11 and not any(p['accepted'] for p in r['work_packages'])
    assert r['localisation']['local_fraction'] is None
    (out/'duty-energy.svg').write_bytes(b'bad')
    with pytest.raises(ValueError,match='differs'):delivery.verify(out)


def test_cli_primary_and_unsupported_commands_fail_closed():
    for command in [['./osr'],['./osr','design','status']]:
        r=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=180)
        assert r.returncode==0 and json.loads(r.stdout)['family']=='ferrite-pm-maglev-study'
    for command in [['./osr','city','unknown-maglev-city'],['./osr','sim','unknown-maglev-city'],['./osr','design','release-check'],['./osr','design','unsupported-family']]:
        r=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=180)
        assert r.returncode in (2,3)



def test_scheduled_cycle_idles_without_rewriting_unchanged_results(tmp_path):
    command=[str(ROOT/'tools/automation/osr-python'),str(ROOT/'tools/automation/ferrite-maglev-study.py'),'cycle','--output',str(tmp_path/'primary')]
    # A complete cold cycle verifies native bodies, fitted hubs, report mirrors
    # and the reader PDF. Its combined verification exceeds the former10min
    # budget; retain every stage and assertion with a bounded one-hour allowance.
    first=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=3600)
    assert first.returncode==0,first.stderr
    path=tmp_path/'primary/result.json';before=(path.stat().st_mtime_ns,path.read_bytes())
    second=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=3600)
    assert second.returncode==0 and json.loads(second.stdout)['state']=='idle; sources unchanged'
    assert (path.stat().st_mtime_ns,path.read_bytes())==before
