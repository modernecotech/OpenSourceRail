"""Two-zone sensible/moisture balance with explicit unqualified HVAC hypotheses."""
import math


def solve(inputs,*,module_count,failed_modules=0,flow_m3_s=.08,duct_area_m2=.02,layout='balanced',step_s=10.,duration_s=None):
    config=inputs['thermal_assumptions'];duration=config['duration_s'] if duration_s is None else duration_s
    if type(module_count) is not int or type(failed_modules) is not int or not 0<=failed_modules<module_count:
        raise ValueError('positive available HVAC module count required')
    if layout not in {'balanced','single-end'} or any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in (flow_m3_s,duct_area_m2,step_s,duration)) or duration/step_s>20000:
        raise ValueError('bounded positive thermal/airflow inputs required')
    # These are declared research boundary conditions, not measured Baghdad weather,
    # passenger ventilation requirements, a supplier map or a refrigerant model.
    rho,cp,latent,air_mass=1.2,1005.,2.45e6,60.
    ambient=config['ambient_c'];initial=config['setpoint_c']
    temperatures=[initial,initial];humidity=[.014,.014];ambient_humidity=.023
    capacity=config['heat_capacity_j_k']/2
    shares=[.5,.5] if layout=='balanced' else [.8,.2]
    sensible_capacity=(module_count-failed_modules)*inputs['module_cooling_w']*.9
    latent_capacity=(module_count-failed_modules)*inputs['module_cooling_w']*.1
    friction=.02;length=8. if layout=='balanced' else 12.;diameter=math.sqrt(4*duct_area_m2/math.pi)
    velocity=flow_m3_s/duct_area_m2
    pressure_drop=friction*length/diameter*rho*velocity**2/2
    fan_power=flow_m3_s*pressure_drop/.5
    energy_residual=0.;water_residual=0.;history=[];peak_temperature=initial;peak_humidity=.014
    elapsed=0.
    while elapsed<duration-1e-9:
        dt=min(step_s,duration-elapsed);old=list(temperatures);water=list(humidity)
        # Two 20-second door pulses per five minutes; inlet is concentrated at
        # the forward zone. Passenger/internal and solar gains remain separated.
        door_flow=.04 if elapsed%300<20 else 0.
        exchange=80.*(old[1]-old[0])
        for zone in range(2):
            mass_flow=rho*(flow_m3_s/2+(door_flow if zone==0 else 0.))
            gain=(config['internal_gain_w']+config['solar_gain_w'])/2
            ventilation=mass_flow*cp*(ambient-old[zone])
            envelope=config['conductance_w_k']/2*(ambient-old[zone])
            transfer=exchange if zone==0 else -exchange
            cooling=min(sensible_capacity*shares[zone],max(0.,capacity*(old[zone]-initial)/dt+gain+ventilation+envelope+transfer))
            power=gain+ventilation+envelope+transfer-cooling+fan_power/2
            temperatures[zone]=old[zone]+power*dt/capacity
            source=.00015+mass_flow*(ambient_humidity-water[zone])
            removed=min(latent_capacity*shares[zone]/latent,max(0.,source+air_mass*(water[zone]-.010)/dt))
            humidity[zone]=water[zone]+(source-removed)*dt/air_mass
            energy_residual+=capacity*(temperatures[zone]-old[zone])-power*dt
            water_residual+=air_mass*(humidity[zone]-water[zone])-(source-removed)*dt
        elapsed+=dt
        peak_temperature=max(peak_temperature,*temperatures);peak_humidity=max(peak_humidity,*humidity)
        if len(history)<400 or elapsed>=duration:
            history.append(dict(time_s=elapsed,temperature_c=list(temperatures),humidity_ratio=list(humidity)))
    return dict(zones=['forward','rear'],history=history,maximum_temperature_c=peak_temperature,
        maximum_humidity_ratio=peak_humidity,electrical_cooling_power_w=(module_count-failed_modules)*inputs['module_cooling_w']/config['cop']+fan_power,
        fan_power_w=fan_power,duct_pressure_drop_pa=pressure_drop,duct_velocity_m_s=velocity,
        sensible_energy_balance_residual_j=energy_residual,moisture_balance_residual_kg=water_residual,
        assumptions=dict(ventilation_minimum_m3_s=.08,ambient_humidity_ratio=ambient_humidity,zone_dry_air_mass_kg=air_mass,
            moisture_source_kg_s_per_zone=.00015,latent_capacity_fraction=.1,door_flow_m3_s=.04,
            module_capacity_status=inputs['rating_status'],duct_friction_factor=friction,fan_efficiency=.5,
            supplier_performance_map=None,humidity_limit_hypothesis=.020),
        scope='Two well-mixed zones and declared duct/fan pressure loss; no CFD, refrigeration cycle, accepted air-quality criterion or railway performance map',
        physical_release=False)
