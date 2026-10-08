"""Pack heat/cooling feedback with explicit measured or declared parameters."""
import math
from .industrialisation import nonnegative

PARAMETERS=('heat_capacity_kj_k','loss_fraction','conductance_kw_k','maximum_cooling_thermal_kw','cooling_target_c')


def thermal_step(temperature_c,ambient_c,throughput_kw,seconds,parameters):
    if parameters is None:return dict(temperature_c=None,modelled=False,calibration_accepted=False,missing_parameters=list(PARAMETERS))
    if any(parameters.get(k) is None for k in PARAMETERS) or not parameters.get('source_record'):
        raise ValueError('pack thermal model requires complete sourced parameters')
    for key in PARAMETERS[:-1]:nonnegative(parameters[key],key)
    if parameters['heat_capacity_kj_k']<=0 or parameters['loss_fraction']>1:raise ValueError('positive heat capacity and bounded cell losses required')
    for value in (temperature_c,ambient_c,parameters['cooling_target_c']):
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):raise ValueError('finite pack/ambient temperature required')
    nonnegative(throughput_kw,'electrical throughput');nonnegative(seconds,'thermal time step')
    if seconds<=0 or parameters['conductance_kw_k']*seconds>parameters['heat_capacity_kj_k']:
        raise ValueError('thermal time step exceeds passive stability bound')
    heat=throughput_kw*parameters['loss_fraction']
    passive=parameters['conductance_kw_k']*(temperature_c-ambient_c)
    cooling=min(parameters['maximum_cooling_thermal_kw'],max(0,heat-passive+
        (temperature_c-parameters['cooling_target_c'])*parameters['heat_capacity_kj_k']/seconds))
    temperature=temperature_c+(heat-passive-cooling)*seconds/parameters['heat_capacity_kj_k']
    return dict(temperature_c=temperature,heat_generation_kw=heat,passive_heat_rejection_kw=passive,
        active_cooling_thermal_kw=cooling,modelled=True,source_record=parameters['source_record'],
        calibration_accepted=False,hardware_power_map_released=False)


def thermal_duty(profile,parameters,steps,*,initial_soc,initial_temperature_c,soh=1.):
    from .battery_profiles import charge_limit_kw,discharge_limit_kw
    if not 0<=initial_soc<=1 or not 0<soh<=1:raise ValueError('bounded SOC and aged SOH required')
    capacity=profile['usable_kwh']*soh;energy=capacity*initial_soc;temperature=initial_temperature_c;rows=[]
    for step in steps:
        seconds=step['seconds'];power=step['power_kw'];ambient=step['ambient_c']
        nonnegative(seconds,'thermal time step')
        if seconds<=0:raise ValueError('positive thermal time step required')
        if not math.isfinite(power):raise ValueError('finite requested terminal power required')
        if power>=0:
            actual=min(power,discharge_limit_kw(profile,energy/capacity,temperature,soh),energy*3600/seconds)
            energy-=actual*seconds/3600
        else:
            actual=-min(-power,charge_limit_kw(profile,energy/capacity,temperature,soh),
                max(0,capacity-energy)*3600/seconds/profile['efficiency'])
            energy-=actual*seconds/3600*profile['efficiency']
        heat=thermal_step(temperature,ambient,abs(actual),seconds,parameters)
        if heat['temperature_c'] is None:raise ValueError('thermal duty cannot substitute ambient for missing pack calibration')
        temperature=heat['temperature_c']
        rows.append(dict(requested_power_kw=power,delivered_terminal_power_kw=actual,temperature_c=temperature,
            soc=energy/capacity,soh=soh,**{k:heat[k] for k in ('heat_generation_kw','active_cooling_thermal_kw')}))
    return dict(steps=rows,final_temperature_c=temperature,final_soc=energy/capacity,temperature_feedback_modelled=True,
        calibration_source=parameters['source_record'],supplier_calibration_accepted=False,operational_release=False)
