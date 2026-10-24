"""Counted candidate price and equal-service energy sensitivities, no adoption.

A failed magnetic/dynamic design has no executable commercial duty cycle. Cost
subtotals and kinematic comparisons cannot establish its financial feasibility.
"""
from pathlib import Path
from hashlib import sha256
import math
import numpy as np
from . import candidate_magnetics as magnetics,candidate_manufacturing as manufacturing,candidate_structures as structures,pilot_corridor,delivery_platform as platform

ROOT=magnetics.ROOT
SERVICES=[dict(id='HVAC-hot-weather',rated_kw=38.,duty_fraction=.60,basis='Unmeasured40C summer cooling/compressor study; heat-load/occupancy/solar model and supplier curve required'),
    dict(id='saloon-lighting',rated_kw=1.2,duty_fraction=1.,basis='Provisional lighting layout/input allocation'),
    dict(id='door-drives',rated_kw=2.,duty_fraction=.05,basis='Intermittent station doors; actual motor cycle required'),
    dict(id='passenger-information',rated_kw=.3,duty_fraction=1.,basis='Displays,audio and communications allocation'),
    dict(id='SBC-network-and-safety-supervision',rated_kw=.12,duty_fraction=1.,basis='Counted supervisory electronics hypothesis; target board measurement open'),
    dict(id='support-local-controllers',rated_kw=.012*24,duty_fraction=1.,basis='24two-circuit local controller allocations per car; converter conduction losses separate'),
    dict(id='services-battery-thermal',rated_kw=.7,duty_fraction=.5,basis='Pack thermal-management allocation'),
    dict(id='other-passenger-and-essential-load-reserve',rated_kw=2.,duty_fraction=1.,basis='Explicit unassigned load reserve; complete auxiliary diagram required')]


def source_paths():return sorted({Path(__file__),ROOT/'engineering/analysis/tests/test_ferrite_maglev_candidate_economics.py',*manufacturing.source_paths()})
def sources():return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in source_paths()}


def support_duty(candidate):
    target=candidate['controlled_aw3_kg']*9.80665/24.;current=magnetics.inverse_current([target],[0.],[[.008]*4],40.)
    actual=magnetics.evaluate_batch([[.008]*4],current['current_a'],40.);valid=bool(current['valid'][0]);thermal=magnetics.thermal_study(current['current_a'][0]) if valid else None
    copper=float(np.sum(actual['copper_loss_w'])) if 'copper_loss_w' in actual else float(np.sum(np.asarray(actual['resistance_ohm'])*np.asarray(current['current_a'])**2))
    cooling=candidate['module']['cooling'];pump=cooling['flow_kg_s']/cooling['fluid_density_kg_m3']*cooling['pressure_drop_pa']/cooling['pump_efficiency']
    return dict(static_target_n_per_module=target,current_a=current['current_a'][0].tolist(),map_valid=bool(current['valid'][0]),
        static_copper_kw_per_car=24*copper/1000 if valid else None,pump_kw_per_car=24*pump/1000,
        converter_loss_kw_per_car=24*(12.+.03*copper)/1000 if valid else None,thermal=thermal,
        attempted_copper_kw_per_car=24*copper/1000,energy_duty_usable=valid,failure=None if valid else 'Required static force is outside the current/material/demagnetisation-valid magnetic map; attempted power is not service consumption',
        scope='Uniform AW3 static8mm40C force/current duty only, no guidance transient credit. Electrical conversion model12W+3%winding power/module is unmeasured; actual routed cooling/current/R/temperature duty remains a gate.')


def equal_service_energy(candidate,services_kw_per_car,*,rail_gross_mass_kg=30000.,length_m=2000.,speed_m_s=20.):
    """Same triangular/trapezoidal trajectory and hotel loads on both systems."""
    a=.7;cruise=length_m-speed_m_s**2/a
    if cruise<0:raise ValueError('bounded trapezoidal service required')
    acceleration_s=speed_m_s/a;duration=2*acceleration_s+cruise/speed_m_s;times=np.linspace(0,duration,4001);speed=np.minimum(np.minimum(a*times,speed_m_s),a*(duration-times));acc=np.where(times<acceleration_s,a,np.where(times>duration-acceleration_s,-a,0.))
    aux=services_kw_per_car*6*(duration+60.)/3600;rows=[];support=support_duty(candidate)
    support_kw=None if not support['map_valid'] else (support['static_copper_kw_per_car']+support['pump_kw_per_car']+support['converter_loss_kw_per_car'])*6
    for name,mass,rolling,eff,suspension in [('candidate-maglev',candidate['controlled_aw3_kg']*6,0.,.92,support_kw),('independent-steel-wheel',rail_gross_mass_kg*6,.002,.90,0.)]:
        force=mass*acc+mass*9.80665*rolling+3.*speed**2;mechanical=float(np.trapezoid(np.maximum(force*speed,0.),times))/3.6e6
        traction=mechanical/eff;susp=None if suspension is None else suspension*(duration+60.)/3600
        rows.append(dict(architecture=name,mass_kg=mass,same_services_kw_per_car=services_kw_per_car,positive_mechanical_work_kwh=mechanical,assumed_traction_efficiency=eff,traction_kwh=traction,hotel_kwh=aux,support_kwh=susp,total_kwh=None if susp is None else traction+aux+susp,regeneration_credit_kwh=0.))
    return dict(distance_m=length_m,runtime_s=duration,dwell_s=60.,cars=6,max_speed_m_s=speed_m_s,acceleration_m_s2=a,rows=rows,
        scope='Independent equal-service kinematic sensitivity only. Maglev efficiency is an unqualified hypothesis, NOT integrated fixed-zone force/current/phase/thermal evidence. Rail contact/brake/curves and whole-line service also require design. Both use identical hotel load; no proven savings or annual service viability.')


def study():
    candidate=magnetics.definition();products=manufacturing.product_definition(candidate);support=support_duty(candidate);nominal=sum(r['rated_kw']*r['duty_fraction'] for r in SERVICES)
    per_car=24*products['products'][0]['estimated_material_process_cost_usd']+sum(r['extended_cost_usd'] for r in candidate['manufacturing_bom'] if r['component_scope'].startswith('new-passive-propulsion'))
    structures_value=structures.study(candidate);beam=products['beam'];sub=structures_value['civil']['substructure_variants'][beam['id']];foundations=[]
    for pier in sub:
        for scenario in pier['foundations']:
            option=scenario['least_cost_screen_option']
            foundations.append(dict(pier=pier['id'],soil=scenario['soil']['id'],foundation=option['id'] if option else None,column_cap_usd=pier['material_formwork_cost_usd'],foundation_usd=option['material_excavation_formwork_cost_usd'] if option else None,qualified=False))
    return dict(schema='osr-candidate-economics/1',configuration_sha256=candidate['configuration_sha256'],services=SERVICES,named_services_average_kw_per_car=nominal,
        support_duty=support,equal_service_energy=[equal_service_energy(candidate,nominal),equal_service_energy(candidate,60.)],
        priced_stock=dict(magnetic_module_usd=products['products'][0]['estimated_material_process_cost_usd'],new_magnetic_and_passive_propulsion_per_car_usd=per_car,
            guidebeam_25m_materials_process_and_bearings_usd=products['products'][1]['estimated_material_process_cost_usd'],wayside_5m_group_usd=products['products'][2]['estimated_material_process_cost_usd'],foundation_scenarios=foundations,
            old_column_cap_allowance_usd=structures.load()['rates']['column_cap_old_allowance_usd'],old_foundation_allowance_usd=structures.load()['rates']['foundation_old_allowance_usd'],unquoted=True,complete_installed_cost=False),
        whole_pilot_finance=dict(capex_usd=None,annual_opex_usd=None,dscr=None,financial_close=False,reason='New propulsion geometry has unresolved mandatory field/demagnetisation evidence and full service duty. Do not transplant the old94ad finance or use kinematic sensitivities to claim revenue/service feasibility.'),
        optimisation='Magnetic alternatives compare full counted AW3, material/process cost, current/packing/demag/thermal screens. Structural alternatives compare actual girder, rail/support, prestress,rebar,lift and unmeasuredsoil scenarios. Reject mandatory failure before cost ranking.',
        allocation_accounting='Named auxiliary study is an alternative to the retained60kW opaque budget, not approved removal credit. Support winding, pump and converter losses are exposed separately. No source allocation silently disappears.',**platform.FLAGS)
