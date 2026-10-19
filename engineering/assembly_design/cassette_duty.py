"""Bounded transient LV/heat/moisture/CO2 controls on the cassette hypotheses.

Finite-capacity performance maps and protective clearing values are explicitly
synthetic benchmark inputs. They establish conservation and adverse propagation,
not selected equipment performance, railway comfort or electrical protection.
"""
import math
import numpy as np

from engineering.twin_workflow import core
from . import cassette_system


def electrothermal(*,voltage_v=24.,ambient_c=50.,duration_s=2.,step_s=.002,fault='none',
                   fault_time_s=.1,clearing_i2t_a2s=20.,thermal_capacity_j_k=20.,thermal_resistance_k_w=20.,
                   female_length_m=.8,male_length_m=1.):
    if fault not in ('none','short','open','reversed'):raise ValueError('registered transient fault required')
    if not all(math.isfinite(v)and v>0 for v in (voltage_v,duration_s,step_s,clearing_i2t_a2s,thermal_capacity_j_k,thermal_resistance_k_w))or duration_s/step_s>20000:
        raise ValueError('bounded positive transient inputs required')
    if not math.isfinite(ambient_c)or not -55<=ambient_c<=125 or not math.isfinite(fault_time_s)or fault_time_s<0:raise ValueError('finite research-domain climate/fault time required')
    ref=cassette_system.electrical_case(ambient_c=20.,female_length_m=female_length_m,male_length_m=male_length_m)
    copper20=ref['external_loop_resistance_ohm']-.016
    temperature=ambient_c;elapsed=0.;tripped=False;i2t=0.;clear_time=None;peak=0.
    ledger=dict(source_j=0.,load_j=0.,source_resistor_j=0.,loop_heat_j=0.,loop_rejected_j=0.)
    history=[]
    while elapsed<duration_s-1e-12:
        dt=min(step_s,duration_s-elapsed)
        if elapsed<fault_time_s<elapsed+dt:dt=fault_time_s-elapsed
        active=fault!='none'and elapsed>=fault_time_s-1e-12
        rwire=copper20*(1+.00393*(temperature-20));rloop=rwire+.016
        load=0. if active and fault=='short' else 4.8
        blocked=tripped or active and fault in ('open','reversed')
        current=0. if blocked else voltage_v/(.05+rloop+load)
        conducting=dt
        if current>8.:
            budget=max(0.,clearing_i2t_a2s-i2t)
            if current*current*dt>=budget:
                conducting=budget/(current*current);tripped=True;clear_time=elapsed+conducting
            i2t+=current*current*conducting
        peak=max(peak,current)
        heat=current*current*rloop;old=temperature
        decay=math.exp(-conducting/(thermal_resistance_k_w*thermal_capacity_j_k))
        temperature=ambient_c+(old-ambient_c)*decay+heat*thermal_resistance_k_w*(1-decay)
        stored=thermal_capacity_j_k*(temperature-old)
        rejected=heat*conducting-stored
        if conducting<dt:
            old=temperature;temperature=ambient_c+(old-ambient_c)*math.exp(-(dt-conducting)/(thermal_resistance_k_w*thermal_capacity_j_k))
            rejected+=thermal_capacity_j_k*(old-temperature)
        ledger['source_j']+=voltage_v*current*conducting
        ledger['load_j']+=current*current*load*conducting
        ledger['source_resistor_j']+=current*current*.05*conducting
        ledger['loop_heat_j']+=heat*conducting;ledger['loop_rejected_j']+=rejected
        elapsed+=dt
        if len(history)<100:history.append(dict(time_s=elapsed,current_a=current,temperature_c=temperature,tripped=tripped))
    ledger['loop_stored_j']=thermal_capacity_j_k*(temperature-ambient_c)
    return dict(fault=fault,voltage_v=voltage_v,ambient_c=ambient_c,female_length_m=female_length_m,male_length_m=male_length_m,final_temperature_c=temperature,peak_current_a=peak,
        tripped=tripped,clearing_time_s=clear_time,accumulated_overcurrent_i2t_a2s=i2t,ledger=ledger,
        electrical_balance_residual_j=ledger['source_j']-ledger['load_j']-ledger['source_resistor_j']-ledger['loop_heat_j'],
        thermal_balance_residual_j=ledger['loop_heat_j']-ledger['loop_stored_j']-ledger['loop_rejected_j'],history=history,
        assumptions=dict(loop_thermal_capacity_j_k=thermal_capacity_j_k,loop_thermal_resistance_k_w=thermal_resistance_k_w,
            overcurrent_pickup_a=8.,clearing_i2t_a2s=clearing_i2t_a2s,reverse_blocking='ideal proposed function, not selected hardware'),
        protection_qualified=False,scope='Lumped copper-temperature resistance and ideal I2t clearing; no arc, contact damage, fuse curves or hardware fault-detection qualification',**core.FLAGS)


def cooling_map(ambient_c,voltage_v=24.):
    if not math.isfinite(ambient_c)or not 26<=ambient_c<=60 or not math.isfinite(voltage_v)or not 18<=voltage_v<=30:
        raise ValueError('synthetic map envelope26..60C and18..30V required; no extrapolation')
    # Deliberately declared *hypotheses*, not a supplier performance or selection.
    capacity=float(np.interp(ambient_c,[26,40,50,60],[40000,37000,30000,22000]))
    cop=float(np.interp(ambient_c,[26,40,50,60],[3.5,3.,2.4,1.8]))
    supply_factor=min(1.,voltage_v/24.)
    return dict(per_module_capacity_w=capacity*supply_factor,cop=cop*supply_factor,
        capacity_map_hypothesis=True,supplier_source=None)


def car_transient(*,initial_c=26.,ambient_c=50.,passengers=100,module_count=3,failed_modules=0,
                  fault='none',duration_s=1800.,step_s=5.,sensor_bias_c=0.,voltage_v=24.,duct_area_m2=.01):
    if type(passengers)is not int or passengers<0 or type(module_count)is not int or type(failed_modules)is not int or not 0<=failed_modules<=module_count:
        raise ValueError('nonnegative occupancy and module availability required')
    if fault not in ('none','frequent-doors','loaded-filter','blocked-duct','failed-fan','loss-of-cooling'):raise ValueError('registered climate fault required')
    if not all(math.isfinite(v)for v in (initial_c,ambient_c,sensor_bias_c,duration_s,step_s))or duration_s<=0 or not 0<step_s<=10 or duration_s/step_s>20000:raise ValueError('bounded finite zone time inputs and timestep at most10s required')
    performance=cooling_map(ambient_c,voltage_v);base=cassette_system.whole_car_duty()['assumptions']
    ductfault={'loaded-filter':'loaded-filter','blocked-duct':'blockage','failed-fan':'fan-fault'}.get(fault,'none')
    duct=cassette_system.duct_case(duct_area_m2,fault=ductfault)
    fresh=min(base['fresh_air_m3_s'],8*duct['useful_flow_m3_s'])*min(1.,voltage_v/24.)
    volume=18.5*2.65*2.8;dry_mass=1.1*volume;capacity=8e6;latent=2.45e6
    temp=initial_c;water=.010;co2=400e-6;elapsed=0.;history=[]
    ledger=dict(sensible_gains_j=0.,sensible_cooling_j=0.,vapour_in_kg=0.,vapour_out_kg=0.,passenger_water_kg=0.,condensate_kg=0.,cooling_j=0.,compressor_input_j=0.,rejected_heat_j=0.)
    peak_temp=initial_c;peak_co2=400.;max_water=water
    available=(module_count-failed_modules)*performance['per_module_capacity_w']
    if fault=='loss-of-cooling':available=0.
    initial_water=water;initial_temp=temp
    while elapsed<duration_s-1e-9:
        dt=min(step_s,duration_s-elapsed)
        doorperiod=120. if fault=='frequent-doors'else 300.
        infiltration=base['infiltration_door_average_m3_s']+(1. if elapsed%doorperiod<20. else 0.)
        q=fresh+infiltration;mdry=1.1*q
        gain=passengers*75.+base['solar_w']+base['equipment_w']+(mdry*1005.+base['envelope_ua_w_k'])*(ambient_c-temp)
        commanded=min(1.,max(0.,(temp+sensor_bias_c-26.)/2.))
        cooling=available*commanded
        water_in=mdry*base['outdoor_humidity_ratio'];water_out=mdry*water;human=passengers*55./latent
        condensate=min(.25*cooling/latent,max(0.,water_in-water_out+human+dry_mass*(water-.010)/dt))
        sensible=cooling-condensate*latent
        temp+=(gain-sensible)*dt/capacity
        water+=(water_in-water_out+human-condensate)*dt/dry_mass
        co2+=(passengers*5e-6+q*(400e-6-co2))*dt/volume
        electrical=cooling/performance['cop'];reject=cooling+electrical
        for key,value in (('sensible_gains_j',gain),('sensible_cooling_j',sensible),('vapour_in_kg',water_in),('vapour_out_kg',water_out),('passenger_water_kg',human),('condensate_kg',condensate),('cooling_j',cooling),('compressor_input_j',electrical),('rejected_heat_j',reject)):
            ledger[key]+=value*dt
        elapsed+=dt;peak_temp=max(peak_temp,temp);peak_co2=max(peak_co2,co2*1e6);max_water=max(max_water,water)
        if len(history)<400 or elapsed>=duration_s:history.append(dict(time_s=elapsed,air_c=temp,humidity_ratio=water,co2_ppm=co2*1e6,cooling_w=cooling,compressor_w=electrical))
    return dict(case=dict(initial_c=initial_c,ambient_c=ambient_c,passengers=passengers,module_count=module_count,failed_modules=failed_modules,
                    fault=fault,duration_s=duration_s,step_s=step_s,sensor_bias_c=sensor_bias_c,voltage_v=voltage_v),
        final_temperature_c=temp,maximum_temperature_c=peak_temp,final_humidity_ratio=water,maximum_humidity_ratio=max_water,
        maximum_co2_ppm=peak_co2,final_co2_ppm=co2*1e6,fresh_air_m3_s=fresh,synthetic_performance_map=performance,
        available_cooling_w=available,ledger=ledger,history=history,
        sensible_energy_residual_j=capacity*(temp-initial_temp)-ledger['sensible_gains_j']+ledger['sensible_cooling_j'],
        water_residual_kg=dry_mass*(water-initial_water)-ledger['vapour_in_kg']+ledger['vapour_out_kg']-ledger['passenger_water_kg']+ledger['condensate_kg'],
        condenser_balance_residual_j=ledger['rejected_heat_j']-ledger['cooling_j']-ledger['compressor_input_j'],
        hypotheses=dict(zone_volume_m3=volume,dry_air_mass_kg=dry_mass,thermal_capacity_j_k=capacity,
            occupant_co2_source_m3_s_per_person=5e-6,number_of_duct_cassettes=8,latent_fraction_cap=.25),
        comfort_qualified=False,air_quality_criterion_adopted=False,refrigerant_circuit_designed=False,
        fan_failure_scope='Fresh-air cassette fans fail; independent recirculation/cooling assumed, not a complete fan system failure',
        scope='One well-mixed car,8duct hypotheses, synthetic ambient/voltage capacity-COP maps; no refrigerant selection, rail comfort/fire/air-distribution or measured performance',**core.FLAGS)


def campaign(duct_area_m2=.01,*,candidate=None):
    female=.8;male=1.;revision=None
    if candidate is not None:
        if candidate.get('kind')!='service-cassette-detail':raise ValueError('detailed cassette context required')
        revision=candidate['revision'];duct_area_m2=candidate['metadata']['duct_clear_area_m2']
        female=candidate['metadata']['harness_cut_totals_m']['cassette']/8
        male=candidate['metadata']['harness_cut_totals_m']['vehicle']/8
    cases=[('normal',{}),('full-occupancy',dict(passengers=200)),('hot-start',dict(initial_c=50.)),
        ('frequent-doors',dict(fault='frequent-doors')),('loaded-filter',dict(fault='loaded-filter')),
        ('blocked-duct',dict(fault='blocked-duct')),('failed-fan',dict(fault='failed-fan')),
        ('one-cooling-module-failed',dict(failed_modules=1)),('loss-of-cooling',dict(fault='loss-of-cooling')),
        ('sensor-low-bias',dict(sensor_bias_c=-3.)),('supply-low',dict(voltage_v=18.))]
    thermal=[dict(id=name,result=car_transient(duct_area_m2=duct_area_m2,**kwargs))for name,kwargs in cases]
    electrical=[electrothermal(fault=f,female_length_m=female,male_length_m=male)for f in ('none','short','open','reversed')]
    refined=car_transient(duct_area_m2=duct_area_m2,step_s=2.5)
    nominal=thermal[0]['result']
    checks=dict(electrical_conservation=all(abs(r['electrical_balance_residual_j'])<1e-8 and abs(r['thermal_balance_residual_j'])<1e-8 for r in electrical),
        heat_water_conservation=all(abs(r['result']['sensible_energy_residual_j'])<1e-4 and abs(r['result']['water_residual_kg'])<1e-8 and abs(r['result']['condenser_balance_residual_j'])<1e-4 for r in thermal),
        zone_time_refinement=abs(refined['final_temperature_c']-nominal['final_temperature_c'])<.1,
        actual_supplier_map=None,physical_climate_and_fault_correlation=None)
    return dict(schema='osr-cassette-transient-duty/1',candidate_revision=revision,electrical=electrical,thermal=thermal,refined_nominal=refined,checks=checks,
        failed_checks=[k for k,v in checks.items()if v is False],held_checks=[k for k,v in checks.items()if v is None],
        digital_specification_complete=False,scope='Conservation/adverse transient implementation; all synthetic equipment properties remain unqualified',**core.FLAGS)
