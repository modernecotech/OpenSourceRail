"""Analytical design studies; no supplier ratings or physical qualification."""
from __future__ import annotations
import math
from engineering.industrialisation.common import finite


def precharge(p, voltage_v):
    """Initially empty capacitor, constant source, resistor and closed return path."""
    V = finite(voltage_v, 'voltage', 1e-9)
    vmax = finite(p['maximum_voltage_v'], 'maximum voltage', 1e-9)
    R = finite(p['resistance_ohm'], 'resistance', 1e-9)
    C = finite(p['capacitance_f'], 'capacitance', 1e-12)
    rt = finite(p['resistance_tolerance'], 'resistor tolerance', 0.)
    ct = finite(p['capacitance_tolerance'], 'capacitor tolerance', 0.)
    ratio = finite(p['close_ratio'], 'closure ratio', 0.)
    timeout = finite(p['timeout_s'], 'timeout', 1e-9)
    margin = finite(p['energy_margin'], 'energy margin', 1.)
    if V > vmax or not 0 < ratio < 1 or rt >= 1 or ct >= 1:
        raise ValueError('precharge outside declared study domain')
    tau = R * C
    time = -tau * math.log1p(-ratio)
    worst_time = -R * (1+rt) * C * (1+ct) * math.log1p(-ratio)
    rows = []
    for i in range(21):
        t = time * i/20; fraction = -math.expm1(-t/tau)
        vc = V * fraction; current = V/R * math.exp(-t/tau)
        cap = .5*C*vc*vc; dissipated = .5*C*V*V*(-math.expm1(-2*t/tau))
        supplied = C*V*V*fraction
        rows.append(dict(time_s=t,link_voltage_v=vc,current_a=current,
            capacitor_energy_j=cap,resistor_energy_j=dissipated,
            source_energy_j=supplied,energy_residual_j=supplied-cap-dissipated))
    return dict(schema='osr-precharge-study/1',nominal_ready_time_s=time,
        worst_tolerance_ready_time_s=worst_time,within_declared_timeout=worst_time <= timeout,
        worst_initial_current_a=vmax/(R*(1-rt)),
        worst_initial_resistor_power_w=vmax*vmax/(R*(1-rt)),
        required_resistor_pulse_energy_j=.5*C*(1+ct)*vmax*vmax*margin,
        pulse_rating_verified=False,samples=rows,physical_validation=False,
        assumptions=['constant source; initially discharged bus; no load/ESR/inductance',
                     'closed return contactor; no switching/transient model',
                     'closure threshold and timeout are OSR study policies, not railway acceptance values'])


def closure_decision(p, signals):
    """Offline interlock policy only; this function controls no physical contactor."""
    guards = ('train_stopped','hvil_closed','insulation_ok','main_feedback_open','return_feedback_closed','precharge_feedback_closed')
    if set(signals) != set(guards)|{'elapsed_s','link_voltage_ratio'}:
        raise ValueError('complete interlock observations required')
    if any(type(signals[key]) is not bool for key in guards):
        raise ValueError('interlock observations must be booleans')
    elapsed = finite(signals['elapsed_s'], 'elapsed time', 0.)
    ratio = finite(signals['link_voltage_ratio'], 'link voltage ratio', 0.)
    if ratio > 1.05:
        raise ValueError('link voltage outside observation domain')
    faults = [key for key in guards if not signals[key]]
    if elapsed > p['timeout_s']: faults.append('timeout')
    return dict(can_request_main_close=not faults and ratio >= p['close_ratio'],
        critical_lockout=bool(faults),faults=faults,physical_control_implemented=False)


def thermal_study(p, modules_available, module_cooling_w):
    """One-node saloon with exact integration of constant command over each step."""
    if type(modules_available) is not int or not 0 <= modules_available <= 6:
        raise ValueError('available HVAC modules outside studied configuration')
    for key in p: finite(p[key], 'thermal '+key)
    UA=p['conductance_w_k'];C=p['heat_capacity_j_k'];dt=p['step_s'];duration=p['duration_s']
    if UA <= 0 or C <= 0 or dt <= 0 or duration <= 0 or p['cop'] <= 0 or dt > duration:
        raise ValueError('positive thermal coefficients and supported time grid required')
    count=round(duration/dt)
    if count > 10000 or not math.isclose(count*dt,duration,rel_tol=0,abs_tol=1e-9):
        raise ValueError('thermal duration must contain a bounded integral number of steps')
    cap=modules_available*finite(module_cooling_w,'module capacity',1e-9)
    gain=p['internal_gain_w']+p['solar_gain_w'];T=p['setpoint_c'];ambient=p['ambient_c']
    rows=[];electrical=0.;max_residual=0.
    for i in range(count):
        command=min(cap,max(0.,gain+UA*(ambient-p['setpoint_c'])+UA*(T-p['setpoint_c'])))
        equilibrium=ambient+(gain-command)/UA;decay=math.exp(-UA*dt/C)
        next_T=equilibrium+(T-equilibrium)*decay
        mean_T=equilibrium+(T-equilibrium)*C/(UA*dt)*(1-decay)
        net=(gain+UA*(ambient-mean_T)-command)*dt
        residual=C*(next_T-T)-net;max_residual=max(max_residual,abs(residual))
        electrical+=command*dt/p['cop'];T=next_T
        rows.append(dict(time_s=(i+1)*dt,temperature_c=T,cooling_w=command,energy_residual_j=residual))
    return dict(schema='osr-modular-hvac-study/1',available_modules=modules_available,
        nominal_capacity_w=cap,final_temperature_c=T,maximum_temperature_c=max(r['temperature_c'] for r in rows),
        within_declared_study_limit=all(r['temperature_c'] <= p['study_limit_c'] for r in rows),
        electrical_energy_kwh=electrical/3600000.,maximum_energy_residual_j=max_residual,
        samples=rows,physical_validation=False,
        assumptions=['nominal public cooling capacities; actual ambient/airflow/refrigerant derating unknown',
                     'OSR assumed gains, UA, capacitance, COP and lumped thermostat',
                     'no fresh-air/latent/humidity/duct or certified comfort model'])


def rail_support(p):
    k1=finite(p['rail_pad_stiffness_n_m'],'rail-pad stiffness',1e-9)
    k2=finite(p['base_pad_stiffness_n_m'],'base-pad stiffness',1e-9)
    a=finite(p['anchor_diameter_m'],'anchor diameter',1e-9)
    ratio=finite(p['minimum_edge_distance_ratio'],'study edge ratio',1.)
    x,y,_=p['baseplate_dimensions_m'];holes=p['holes_xy_m'];r=p['hole_radius_m']
    edge=min(min(x/2-abs(h[0]),y/2-abs(h[1])) for h in holes)
    if edge <= r: raise ValueError('anchor clearance hole breaks a plate edge')
    if not math.isclose(p['length_m']/p['seat_spacing_m'],round(p['length_m']/p['seat_spacing_m'])):
        raise ValueError('panel length must contain an integral seat spacing')
    return dict(schema='osr-rail-support-study/1',series_stiffness_n_m=1/(1/k1+1/k2),
        minimum_anchor_edge_distance_m=edge,required_study_edge_distance_m=ratio*a,
        within_declared_edge_policy=edge >= ratio*a,fastening_qualified=False,
        electrical_insulation_verified=False,longitudinal_restraint_n=None,
        limits=['OSR assumed linear pad stiffness, not supplier curves',
                'edge-distance ratio is an internal geometric screen, not bolt/anchor strength acceptance',
                'rail-structure interaction, toe force, fatigue and insulation require actual assembly tests'])
