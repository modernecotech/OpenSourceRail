"""Reference module arrangement, physical quantities and conservative DC duty model.

Nominal public module values are kept separate from OSR research assumptions.
The constant-OCV, lumped-temperature model is a screening tool, not PyBaMM or
a supplier electrochemical model. Positive terminal power is discharge.
"""
from __future__ import annotations
import math
from osr_mech.engineering_definition import number
from osr_mech.automated_geometry import aggregate, primitive_volume, validate_spec


def box(identifier, dimensions, centre, kind='box', **extra):
    return dict(id=identifier,kind=kind,dimensions_m=list(dimensions),centre_m=list(centre),**extra)


def compile_pack(choices, basis):
    required={'series_modules','parallel_strings','module_gap_m','edge_margin_m','enclosure_thickness_m',
              'headspace_m','state_of_health','soc_min','soc_max'}
    if set(choices)!=required:raise ValueError('battery choices missing or unknown')
    ns,np=choices['series_modules'],choices['parallel_strings']
    if type(ns) is not int or type(np) is not int or not 1<=ns<=64 or not 1<=np<=8 or ns*np>384:
        raise ValueError('integer module counts outside reference packaging budget')
    for key in required-{'series_modules','parallel_strings'}:number(choices[key],key,minimum=0.)
    gap,margin,t,head=(choices[k] for k in ('module_gap_m','edge_margin_m','enclosure_thickness_m','headspace_m'))
    if gap<.005 or not .025<=margin<=.1 or not .002<=t<=.01 or not .015<=head<=.1:
        raise ValueError('battery gaps, margin, thickness or headspace outside reference domain')
    if margin<=t+.018 or not .5<=choices['state_of_health']<=1 or not 0<=choices['soc_min']<choices['soc_max']<=1:
        raise ValueError('invalid battery state or mounting margin')
    module=next(s['module'] for s in basis['sources'] if s['id']=='toshiba-railway-module');assumptions=basis['assumptions']
    dx,dy,dz=module['dimensions_xyz_m']
    length=ns*dx+(ns-1)*gap+2*margin;width=np*dy+(np-1)*gap+2*margin;height=t+dz+head+t
    holes=[[x,y] for x in (-length*.40,-length*.15,length*.15,length*.40) for y in (-width/2+margin/2,width/2-margin/2)]
    primitives=[box('tray-base',[length,width,t],[0,0,t/2],'plate',holes_xy_m=holes,hole_radius_m=.0065),
                box('lid',[length,width,t],[0,0,height-t/2])]
    for sign in (-1,1):
        primitives.extend([box(f'long-wall-{sign}',[length,t,height-2*t],[0,sign*(width-t)/2,height/2]),
                           box(f'end-wall-{sign}',[t,width-2*t,height-2*t],[sign*(length-t)/2,0,height/2])])
    masses=[primitive_volume(p)*assumptions['enclosure_density_kg_m3'] for p in primitives]
    cutlist=[dict(feature=p['id'],quantity=1,unit='ea',material='assumed aluminium',mass_kg=m,
                  process='cut/drill/formed plate; joining procedure open') for p,m in zip(primitives,masses)]
    for i in range(ns):
        for j in range(np):
            p=box(f'module-S{i+1}-P{j+1}',[dx,dy,dz],[(i-(ns-1)/2)*(dx+gap),(j-(np-1)/2)*(dy+gap),t+dz/2])
            primitives.append(p);masses.append(module['approximate_mass_kg'])
            cutlist.append(dict(feature=p['id'],quantity=1,unit='ea',material='public module envelope',
                                mass_kg=masses[-1],process='buy; supplier rail/fire/vibration release open'))
    # A controlled clearance hole, shank, head, two washers and nut per mounting.
    for i,(x,y) in enumerate(holes):
        for name,radius,bore,depth,z in [('shank',.006,0.,.028,-.006),('head',.010,0.,.008,t+.007),
                                       ('washer-upper',.012,.0065,.003,t+.0015),('washer-lower',.012,.0065,.003,-.0095),
                                       ('nut',.010,.006,.010,-.016)]:
            p=dict(id=f'mount-{i+1}-{name}',kind='tube' if bore else 'cylinder',centre_m=[x,y,z],radius_m=radius,length_m=depth,axis='z')
            if bore:p['inner_radius_m']=bore
            primitives.append(p);mass=primitive_volume(p)*7850.;masses.append(mass)
            cutlist.append(dict(feature=p['id'],quantity=1,unit='ea',material='assumed steel',mass_kg=mass,
                                process='reference cylindrical hardware; certified thread/head/nut geometry open'))
    spec=dict(role='battery-installation',primitives=primitives);validate_spec(spec)
    properties=aggregate(primitives,masses);mass=properties['mass_kg']
    module_mass=ns*np*module['approximate_mass_kg'];enclosure_mass=mass-module_mass
    voltage=ns*module['nominal_voltage_v'];capacity=np*module['capacity_ah']*choices['state_of_health']
    nominal_energy=voltage*capacity/1000
    pack=dict(schema='osr-reference-battery/1',series_modules=ns,parallel_strings=np,module_count=ns*np,
        chemistry='LTO reference alternative; not the existing LFP EBOM release',
        module_source='toshiba-railway-module',dimensions_m=[length,width,height],properties=properties,
        geometry=spec,cutlist=cutlist,hole_pattern_m=[[x,y,t/2] for x,y in holes],
        nominal_voltage_v=voltage,capacity_ah=capacity,nominal_energy_kwh=nominal_energy,
        usable_energy_kwh=nominal_energy*(choices['soc_max']-choices['soc_min']),
        resistance_ohm=ns*assumptions['module_resistance_ohm']/np,
        discharge_current_limit_a=np*assumptions['module_discharge_current_limit_a'],
        charge_current_limit_a=np*assumptions['module_charge_current_limit_a'],
        thermal_capacity_j_k=module_mass*assumptions['module_heat_capacity_j_kg_k']+enclosure_mass*assumptions['enclosure_heat_capacity_j_kg_k'],
        cooling_conductance_w_k=ns*np*assumptions['cooling_conductance_w_k_per_module'],
        temperature_limit_c=assumptions['pack_temperature_limit_c'],soc_min=choices['soc_min'],soc_max=choices['soc_max'],
        model_limits=['constant nominal OCV; no SOC/temperature voltage map','equal parallel current sharing',
                      'lumped temperature; no cell hot spots','current, resistance, cooling and temperature limits are unverified OSR assumptions',
                      'no busbar/contactors/harness/coolant-fluid mass; those remain in the explicit residual carbody allocation'],
        production_released=False,physical_validation=False)
    return pack


def duty_cycle(pack, segments, *, initial_soc=.8, initial_temperature_c=25., ambient_temperature_c=25.):
    for value,key in ((initial_soc,'initial SOC'),(initial_temperature_c,'initial temperature'),(ambient_temperature_c,'ambient temperature')):number(value,key)
    if not pack['soc_min']<=initial_soc<=pack['soc_max']:raise ValueError('initial SOC outside pack operating bounds')
    if not segments:raise ValueError('nonempty duty cycle required')
    soc=initial_soc;temperature=initial_temperature_c;rows=[];terminal=chemical=heat=cooling=0.
    V,R,C,H=(pack[k] for k in ('nominal_voltage_v','resistance_ohm','thermal_capacity_j_k','cooling_conductance_w_k'))
    for segment in segments:
        if set(segment)!={'duration_s','terminal_power_w'}:raise ValueError('duration and terminal power required')
        dt=number(segment['duration_s'],'duty duration',minimum=1e-6);P=number(segment['terminal_power_w'],'terminal power')
        discriminant=V*V-4*R*P
        if discriminant<0:raise ValueError('terminal power outside constant-OCV model domain')
        I=2*P/(V+math.sqrt(discriminant));loss=I*I*R;delta_chemical=V*I*dt
        previous=temperature;equilibrium=ambient_temperature_c+loss/H
        temperature=equilibrium+(temperature-equilibrium)*math.exp(-H*dt/C)
        delta_cooling=loss*dt-C*(temperature-previous)
        soc-=I*dt/(3600*pack['capacity_ah']);terminal+=P*dt;chemical+=delta_chemical;heat+=loss*dt;cooling+=delta_cooling
        limit=pack['discharge_current_limit_a'] if I>=0 else pack['charge_current_limit_a']
        constraints=dict(current=abs(I)<=limit,soc=pack['soc_min']<=soc<=pack['soc_max'],
                         temperature=max(previous,temperature)<=pack['temperature_limit_c'])
        rows.append(dict(**segment,pack_current_a=I,string_current_a=I/pack['parallel_strings'],
            terminal_voltage_v=V-I*R,heat_generation_w=loss,soc=soc,temperature_c=temperature,
            constraints=constraints,energy_balance_residual_j=delta_chemical-P*dt-loss*dt))
    return dict(schema='osr-reference-battery-duty/1',history=rows,terminal_energy_j=terminal,
        chemical_energy_change_j=chemical,heat_generated_j=heat,heat_removed_j=cooling,
        stored_thermal_energy_change_j=C*(temperature-initial_temperature_c),
        electrical_balance_residual_j=chemical-terminal-heat,
        thermal_balance_residual_j=heat-cooling-C*(temperature-initial_temperature_c),
        research_constraints_passed=all(all(r['constraints'].values()) for r in rows),
        engineering_constraints_passed=None,physical_validation=False)


def operating_budget(pack, car_count, *, train_energy_kwh_km, average_pack_power_w, train_charger_power_w):
    """Conditional range/recharge estimates with the same DC loss/current model.

    Consumption and charger power are explicit scenario inputs. No measured
    range or station dwell capability is inferred from a module catalogue.
    """
    if type(car_count) is not int or car_count<1:raise ValueError('positive car count required')
    for value,key in ((train_energy_kwh_km,'train consumption'),(average_pack_power_w,'pack duty power'),(train_charger_power_w,'charger power')):
        number(value,key,minimum=1e-6)
    discharge=duty_cycle(pack,[dict(duration_s=1.,terminal_power_w=average_pack_power_w)])['history'][0]
    charge=duty_cycle(pack,[dict(duration_s=1.,terminal_power_w=-train_charger_power_w/car_count)])['history'][0]
    V=pack['nominal_voltage_v'];efficiency=average_pack_power_w/(V*discharge['pack_current_a'])
    usable_terminal=car_count*pack['usable_energy_kwh']*efficiency
    charge_chemical_power=-car_count*V*charge['pack_current_a']
    return dict(schema='osr-conditional-battery-operating-budget/1',
        inputs=dict(train_energy_kwh_km=train_energy_kwh_km,average_pack_power_w=average_pack_power_w,train_charger_power_w=train_charger_power_w),
        usable_terminal_energy_kwh=usable_terminal,range_km=usable_terminal/train_energy_kwh_km,
        maximum_recharge_interval_km=usable_terminal/train_energy_kwh_km,
        full_usable_window_recharge_time_s=car_count*pack['usable_energy_kwh']*3.6e6/charge_chemical_power,
        charge_current_a_per_pack=charge['pack_current_a'],discharge_current_a_per_pack=discharge['pack_current_a'],
        current_constraints_passed=charge['constraints']['current'] and discharge['constraints']['current'],
        basis='conditional constant-power screening; consumption/charger assumptions, no route/traction/thermal-duration qualification',
        engineering_constraints_passed=None,physical_validation=False)
