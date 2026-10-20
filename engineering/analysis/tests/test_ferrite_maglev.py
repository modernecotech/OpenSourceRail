"""Independent numerical controls, migration boundaries and adverse-case regressions."""
from copy import deepcopy
import json
import math
from pathlib import Path
import subprocess
import sys

import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from engineering.ferrite_maglev import model,delivery


@pytest.fixture(scope='module')
def context():return model.load()


def test_primary_policy_version_and_comparator_are_explicit(context):
    policy,c,_=context
    assert (ROOT/'VERSION').read_text().strip()=='0.5'
    assert policy['development']['primary_family']==c['metadata']['family']=='ferrite-pm-maglev-study'
    assert policy['development']['automatic_legacy_fallback'] is False
    assert policy['development']['inherit_legacy_acceptance'] is False
    assert c['controls']['preferred_host']=='off-the-shelf-SBC'


@pytest.mark.parametrize('ferrite,battery,tare',[(3000,150,18000),(4000,150,19000),(3000,225,18750),(4000,225,19750)])
def test_mass_contains_magnets_once_and_retains_equal_payload(context,ferrite,battery,tare):
    r=model.mass(context[1],ferrite,battery)
    assert r['tare_kg']==tare and r['aw2_kg']==tare+9000 and r['aw3_kg']==tare+12000
    assert r['eol_window_kwh']==pytest.approx(battery*.6*.8)
    assert r['cg_m'] is None and r['inertia_kg_m2'] is None


@pytest.mark.parametrize('scenario,train,civil,pilot',[
    ('low',764197.416,7047775,9000000),('base',872197.416,8345876,23220000),('high',1130197.416,10528514,55200000)])
def test_costs_reconcile_independent_supplied_totals_and_nonoverlap(context,scenario,train,civil,pilot):
    _,c,costs=context;r=model.cost_case(c,costs,scenario,3000,225)
    assert r['train_usd']==pytest.approx(train)
    assert r['civil_usd_dual_km']==pytest.approx(civil)
    assert r['pilot_usd']==pytest.approx(pilot)
    assert r['removed_direct_usd_train']==206600 and r['battery_credit_usd_train']==0
    reduced=model.cost_case(c,costs,scenario,3000,150)
    assert r['train_usd']-reduced['train_usd']==pytest.approx(30000)
    more=model.cost_case(c,costs,scenario,4000,225)
    assert more['train_usd']-r['train_usd']==pytest.approx(8400)
    assert more['civil_usd_dual_km']==r['civil_usd_dual_km']  # budget sensitivity, not an automatic load-cost conversion
    assert r['city_total_usd'] is None and not r['epc_included']


def test_lower_cost_and_localisation_are_targets_with_imported_inputs_visible(context):
    _,c,costs=context
    r=model.cost_case(c,costs,'base',3000,225,hardware_target=90000)
    assert r['train_usd']==pytest.approx(818197.416)
    assert r['costs_are_quotes'] is False
    assert model.localisation([dict(id='coil',cost_usd=10000,imported_input_usd=4000)])['local_fraction']==.6
    assert model.localisation([dict(id='coil',cost_usd=10000,imported_input_usd=None)])['local_fraction'] is None
    with pytest.raises(ValueError):model.localisation([dict(id='coil',cost_usd=100,imported_input_usd=101)])


def test_section_matches_parallel_axis_and_retains_lateral_issue(context):
    s=model.section(.8,1.6,.15,.18)
    # Independently sum top/bottom flanges and two webs.
    area=2*.8*.18+2*.15*1.24
    inertia=2*(.8*.18**3/12+(.8*.18)*(.8-.09)**2)+2*(.15*1.24**3/12)
    assert s['area_m2']==pytest.approx(area)
    assert s['vertical_i_m4']==pytest.approx(inertia)
    assert s['lateral_i_m4']==pytest.approx(.05535)
    a=model.civil_case(context[1],.8,1.6,20);b=model.civil_case(context[1],.8,1.6,30)
    assert b['total_elastic_deflection_m']/a['total_elastic_deflection_m']==pytest.approx((30/20)**4)
    assert a['relative_gap_accepted'] is None


def test_curve_offset_is_horizontal_and_not_independent_module_sagitta(context):
    r=model.geometry(context[1]);curve=next(x for x in r['curves'] if x['radius_m']==100)
    assert curve['lateral_sagitta_m']==pytest.approx(.18016229225776)
    assert curve['face_width_before_margins_m']==pytest.approx(.8603245845155)
    assert curve['vertical_gap_consumed_by_horizontal_sagitta_m']==0
    assert r['seed_ferrite_mass_kg']==pytest.approx(3000) and r['seed_blocks']==pytest.approx(4800)
    assert r['maxwell_pressure_is_force_prediction'] is False
    assert model.sagitta(1,100)<model.sagitta(12,100)/100


@pytest.mark.parametrize('mass,normal,hot',[(27750,3.661,5.618),(30750,3.842,5.923),(28750,3.721,5.719),(31750,3.902,6.025),
    (27000,3.616,5.542),(30000,3.797,5.847),(28000,3.676,5.643),(31000,3.857,5.948)])
def test_level_duty_matches_independent_review_cases(context,mass,normal,hot):
    for is_hot,expected in [(False,normal),(True,hot)]:
        r=model.cycle(context[1],mass,hot=is_hot)
        assert abs(r['cycle_kwh']-expected)<.00051
        assert r['cycle_kwh']==pytest.approx(r['propulsion_dc_kwh']-r['recovered_dc_kwh']+r['services_kwh'])
        assert r['balanced_charger_kw']==pytest.approx(r['cycle_kwh']*80)


def test_no_regen_and_90kmh_expose_600kw_charger_deficit(context):
    c=context[1];a=model.cycle(c,31750,hot=True,regen=False);b=model.cycle(c,31750,hot=True,speed_kmh=90,regen=False)
    assert a['balanced_charger_kw']==pytest.approx(540.16996,abs=.001)
    assert b['balanced_charger_kw']==pytest.approx(619.45459,abs=.001)
    assert a['charger_balance_kwh']['600']>0 and b['charger_balance_kwh']['600']<0
    assert a['recovered_dc_kwh']==b['recovered_dc_kwh']==0


def test_cycle_has_independent_time_domain_energy_control(context):
    # Independent 1 ms integration of acceleration; compare with quadrature's
    # peak speed and DC energy for an unambiguously acceleration-only interval.
    c=context[1];p=c['power'];m=31750;dt=.001;t=0;speed=0;energy=0;distance=0
    while speed<80/3.6:
        drag=1000+1.8*speed**2
        accel=min(1.,((600000-60000)*.55/max(speed,1e-12)-drag)/m)
        step=min(dt,(80/3.6-speed)/accel)
        midpoint=speed+accel*step/2
        energy+=((m*accel+1000+1.8*midpoint**2)*midpoint/.55)*step
        distance+=midpoint*step;t+=step;speed+=accel*step
    r=model.cycle(c,m,hot=True)
    braking_distance=(80/3.6)**2/2
    cruise=max(0,1000-distance-braking_distance)
    assert t+cruise/(80/3.6)+(80/3.6)==pytest.approx(r['moving_seconds'],abs=.002)
    cruise_energy=(1000+1.8*(80/3.6)**2)*cruise/.55
    assert (energy+cruise_energy)/3.6e6==pytest.approx(r['propulsion_dc_kwh'],abs=.001)


@pytest.mark.parametrize('field,value', [('electromagnetic_force_map_validated',True),('fabrication_release_allowed',True),('vehicle_mass_measured',True)])
def test_claimed_release_is_rejected(context,field,value):
    c=deepcopy(context[1]);c['metadata'][field]=value
    with pytest.raises(ValueError):model.validate(c)


@pytest.mark.parametrize('mutate',[
    lambda c:c['power'].update(normal_drive_efficiency=0),
    lambda c:c['power'].update(normal_soc_high=1.1),
    lambda c:c['power'].update(charger_effective_seconds=61),
    lambda c:c['power'].update(normal_soc_high=True),
    lambda c:c['power'].update(charger_candidates_kw_per_car=[float('nan')]),
    lambda c:c['vehicle'].update(nominal_car_length_m='TBD'),
    lambda c:c['mass'].update(ferrite_base=float('nan')),
    lambda c:c['vehicle'].update(nominal_car_length_m=True),
    lambda c:c['mass'].update(growth_reserve=1),
    lambda c:c['architecture'].update(route_powered_stator=True)])
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
    assert len(r['civil_section_candidates'])==27 and len(r['cost_cases'])==12 and len(r['energy_cases'])==16
    assert all(r[k] is False for k in model.FLAGS)
    assert all(g['accepted'] is False for g in r['gates'])
    assert len(r['work_packages'])==11 and not any(p['accepted'] for p in r['work_packages'])
    assert r['localisation']['local_fraction'] is None
    (out/'duty-energy.svg').write_bytes(b'bad')
    with pytest.raises(ValueError,match='differs'):delivery.verify(out)


def test_cli_primary_and_legacy_boundaries():
    for command in [['./osr'],['./osr','design','status']]:
        r=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=30)
        assert r.returncode==0 and json.loads(r.stdout)['family']=='ferrite-pm-maglev-study'
    for command in [['./osr','city','baghdad'],['./osr','sim'],['./osr','design','release-check']]:
        r=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=30)
        assert r.returncode in (2,3)
    assert subprocess.run(['./osr','design','legacy','twin','--help'],cwd=ROOT,capture_output=True,timeout=90).returncode==0


def test_scheduled_cycle_idles_without_rewriting_unchanged_results(tmp_path):
    command=[str(ROOT/'tools/automation/osr-python'),str(ROOT/'tools/automation/ferrite-maglev-study.py'),'cycle','--output',str(tmp_path/'primary')]
    first=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=30)
    assert first.returncode==0,first.stderr
    path=tmp_path/'primary/result.json';before=(path.stat().st_mtime_ns,path.read_bytes())
    second=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=30)
    assert second.returncode==0 and json.loads(second.stdout)['state']=='idle; sources unchanged'
    assert (path.stat().st_mtime_ns,path.read_bytes())==before
