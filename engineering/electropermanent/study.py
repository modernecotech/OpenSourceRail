"""Executed linear pulse cases and coupled EPM necessary circuit diagnostics."""
from copy import deepcopy
from hashlib import sha256
import math
from pathlib import Path
import platform
import sys

import scipy
from engineering.vehicle_optimisation import magnets
from engineering.design_search import storage
from . import FLAGS, ROOT
from . import catalogue, pulse


def sources(root=ROOT):
    root=Path(root).resolve()
    paths=[p for p in Path(__file__).parent.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix in {'.py','.json','.md'}]
    paths+=magnets.source_paths()+[Path(storage.__file__),Path(magnets.passive.__file__).parents[1]/'ferrite_maglev/candidate-magnetics.toml']
    code={p.resolve().relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in paths}
    retained={}
    for name in ('docs/design-engine/vehicle-optimisation/refinements.json',
                 'engineering/ferrite_maglev/candidate-magnetics.toml'):
        path=root/name
        if path.is_file():
            if path.is_symlink():raise ValueError('ordinary retained parent source required')
            retained[name]=sha256(path.read_bytes()).hexdigest()
            if name in code and code[name]!=retained[name]:
                raise ValueError('executing/material source workspaces disagree: '+name)
    return dict(code_sha256=dict(sorted(code.items())),retained_sha256=retained)


def environment():
    import matplotlib
    return dict(python=platform.python_version(),scipy=scipy.__version__,matplotlib=matplotlib.__version__,
                numerical_method='closed-form linear RL/RLC states; independent adaptive-quadrature port accounting')


def _coil_R(value,T):
    c=value['materials']['copper'];w=value['winding']
    return c['resistivity_20c_ohm_m']*(1+c['resistance_temperature_coefficient_per_k']*(T-20))*w['conductor_length_m']/w['wire_area_m2']


def _current_states(value):
    circuit=value['magnetic_circuit'];m=value['materials'];N=value['winding']['turns'];rows=[]
    args={k:circuit[k] for k in ('gaps_m','magnet_length_m','pole_area_m2','nd_area_m2','alnico_area_m2')}
    for H in (m['AlNiCo']['normal_Hc_A_per_m'],m['magnetizing']['Alnico5_recommended_magnetizing_H_A_per_m']):
        for sign in (-1,1):
            for prescribed in (1.25,1.5):
                result=pulse.energized_parallel_circuit(**args,H_m_A_per_m=sign*H,
                    B_alnico_T=sign*prescribed,turns=N,nd_br_T=m['NdFeB']['br_20c_t'],
                    nd_recoil_mu_r=m['NdFeB']['recoil_relative_permeability'])
                result.update(candidate_id=value['candidate_id'],field_purpose='normal-Hc necessary reference' if H==51000 else 'Arnold general magnetizing guidance',
                    prescribed_Alnico_B_basis='Trial values only, not measured B(Hmag), bounds or a fitted saturation law')
                rows.append(result)
    return rows


def study(root=ROOT):
    before=sources(root);env=environment();values=catalogue.candidates(root)
    cases=[];loadlines=[];magnetizing=[]
    for value in values:
        catalogue.validate(value,root);w=value['winding'];e=value['electrical'];m=value['materials']
        states=_current_states(value);magnetizing+=states
        full=[q for q in states if q['field_purpose']=='Arnold general magnetizing guidance']
        required=max(abs(q['required_current_A']) for q in full)
        for T in (20.,80.):
            Rcoil=_coil_R(value,T);R=Rcoil+w['series_lead_driver_ESR_ohm']
            for L in w['inductance_sensitivity_H']:
                rl=pulse.rl_pulse(R,L,e['charge_voltage_V'],w['pulse_duration_s'])
                rlc=pulse.rlc_pulse(R,L,e['capacitance_F'],e['charge_voltage_V'],w['pulse_duration_s'])
                coil_heat=rlc['resistor_I2R_J']*Rcoil/R
                deltaT=coil_heat/(w['copper_mass_kg']*m['copper']['specific_heat_j_kg_k'])
                settings=dict(candidate_id=value['candidate_id'],material_id=value['material_id'],
                    coil_initial_temperature_C=T,magnetic_reference='room-reference typical AlNiCo; no hot switching inference',
                    R_coil_ohm=Rcoil,L_H=L,source_snapshot=before,environment=env)
                row=dict(settings=settings,evaluation_id=catalogue.identity(settings),linear_RL=rl,linear_RLC=rlc,
                    execution_status='executed',numerical_status='linear-equations-evaluated',
                    programming_polarities=[-1,1],
                    polarity_basis='Linear electrical magnitudes mirror; magnetic ON/OFF current demands are computed separately and hysteresis is not symmetric by assumption',
                    current_density_peak_A_per_mm2=rlc['peak_current_A']/(w['wire_area_m2']*1e6),
                    DC_3p75_A_per_mm2_comparison_pass=rlc['peak_current_A']/(w['wire_area_m2']*1e6)<=3.75,
                    pulse_current_density_qualified=False,coil_adiabatic_temperature_rise_K=deltaT,
                    coil_I2R_J=coil_heat,other_series_loss_J=rlc['resistor_I2R_J']-coil_heat,
                    core_eddy_hysteresis_J=None,clamp_loss_J=None,cooling_equilibrium_C=None,
                    repeated_pulses_per_minute_sensitivity=[1,10,60],
                    copper_average_W_at_pulses_per_minute=[coil_heat*f/60 for f in (1,10,60)],
                    full_magnetizing_current_conditional_A=required,
                    linear_electrical_demand_screen='pass-conditional' if rlc['peak_current_A']>=required else 'fail-conditional',
                    experiment_budget=dict(peak_current_A=250.,voltage_V=400.,copper_adiabatic_rise_K=5.,
                        scope='Declared protected pulse-coupon budget, not relaxation of continuous current or rail acceptance limits'),
                    conditional_pulse_budget_pass=(rlc['peak_current_A']>=required and rlc['peak_current_A']<=250 and e['charge_voltage_V']<=400 and deltaT<=5
                        and not rlc['capacitor_reversal_present'] and w['slot_fill']<=.55 and value['packing']['longitudinal_margin_m']>0),
                    switching_screen='unknown',bias_retention='unknown',fast_suspension_qualified=False,**FLAGS)
                row['result_sha256']=catalogue.identity(row);cases.append(row)
        circuit=value['magnetic_circuit']
        for gap in (.0002,.001,.012):
            for B in (.2,.5,.8):
                row=pulse.coupled_loadline(B_gap_T=B,gaps_m=[gap,gap],magnet_length_m=circuit['magnet_length_m'],
                    pole_area_m2=circuit['pole_area_m2'],nd_area_m2=circuit['nd_area_m2'],alnico_area_m2=circuit['alnico_area_m2'],
                    nd_br_T=m['NdFeB']['br_20c_t'],nd_recoil_mu_r=m['NdFeB']['recoil_relative_permeability'],
                    alnico_normal_Hc_A_per_m=m['AlNiCo']['normal_Hc_A_per_m'])
                row.update(candidate_id=value['candidate_id'],material_reference='room-reference typical table only')
                loadlines.append(row)
    if sources(root)!=before:raise ValueError('EPM source changed during execution')
    summary=[]
    for value in values:
        selected=[r for r in cases if r['settings']['candidate_id']==value['candidate_id']]
        nominal=next(r for r in selected if r['settings']['coil_initial_temperature_C']==20 and r['settings']['L_H']==.005)
        banks=value['electrical']['banks_per_car']
        remaining=nominal['linear_RLC']['final_capacitor_J']
        deficit=value['electrical']['stored_energy_J']-remaining
        # One shared bank must be reset before each serial pulse. A parallel
        # arrangement can program simultaneously but recharges the same total
        # released energy. Driver turnoff/recovery is explicitly unresolved.
        charger_W=1000.;eta=.9;modules=24
        recharge=modules*deficit/(charger_W*eta)
        slots=modules if banks==1 else 1
        timing=dict(reference_modules=modules,charger_power_W_assumption=charger_W,
            charger_efficiency_assumption=eta,capacitor_reset_required_per_pulse=True,
            nominal_capacitor_voltage_after_pulse_V=nominal['linear_RLC']['final_capacitor_voltage_V'],
            nominal_capacitor_energy_after_pulse_J=remaining,nominal_capacitor_deficit_per_module_J=deficit,
            nominal_inductor_energy_at_turnoff_J=nominal['linear_RLC']['final_inductor_J'],
            post_turnoff_clamp_recovery_heat_J=None,
            one_polarity_reference_car_capacitor_reset_J=modules*deficit,
            two_polarity_reference_car_capacitor_reset_J=2*modules*deficit,
            minimum_program_slots_s=slots*value['winding']['pulse_duration_s'],
            serial_reset_time_s_assuming_no_overlap=recharge,
            serial_program_plus_reset_s_assuming_no_overlap=slots*value['winding']['pulse_duration_s']+recharge,
            timing_basis='Necessary arithmetic at declared charger assumptions, zero recovery credited; switching/settling, energy feedback, cooling and recharge circuit not established',
            actual_dwell_required_s=None,complete_cycle_heat_J=None)
        timing['selector_may_advance_after_20ms']=False
        timing['selector_interlock']='Must establish zero coil current and completed clamp/recovery before changing module; required extra time unknown'
        circuit=value['magnetic_circuit']
        retention=pulse.positive_branch_retention_bound(**{k:circuit[k] for k in ('gaps_m','magnet_length_m','pole_area_m2','nd_area_m2')},
            normal_Hc_A_per_m=value['materials']['AlNiCo']['normal_Hc_A_per_m'],
            nd_br_T=value['materials']['NdFeB']['br_20c_t'],nd_recoil_mu_r=value['materials']['NdFeB']['recoil_relative_permeability'])
        summary.append(dict(name=value['name'],candidate_id=value['candidate_id'],parent_magnet_id=value['parent_magnet_id'],
            turns=value['winding']['turns'],slot_fill=value['winding']['slot_fill'],
            added_counted_stock_kg_per_module=value['mass']['known_added_epm_stock_kg'],
            added_counted_stock_kg_per_reference_car=value['mass']['known_added_epm_stock_kg_per_reference_car'],
            complete_added_installed_mass_kg=None,known_longitudinal_margin_m=value['packing']['longitudinal_margin_m'],
            ideal_zero_external_flux_shunt_B_T=value['magnetic_circuit']['ideal_zero_external_flux_Nd_shunt_B_T'],
            actual_off_state_qualified=False,
            zero_current_positive_branch_bound=retention,
            nominal_RLC_peak_current_A=nominal['linear_RLC']['peak_current_A'],
            conditional_magnetizing_current_A=nominal['full_magnetizing_current_conditional_A'],
            nominal_coil_heat_J=nominal['coil_I2R_J'],nominal_copper_adiabatic_rise_K=nominal['coil_adiabatic_temperature_rise_K'],
            capacitor_energy_J=value['electrical']['stored_energy_J'],
            capacitor_energy_per_car_J=None if banks is None else value['electrical']['stored_energy_J']*banks,
            capacitor_energy_per_six_car_train_J=None if banks is None else value['electrical']['stored_energy_J']*banks*6,
            timing=timing if banks is not None else dict(scope='standalone contact coupon; no installed latch count or dwell claim'),
            conditional_electrical_passes=sum(r['linear_electrical_demand_screen']=='pass-conditional' for r in selected),
            conditional_pulse_budget_passes=sum(r['conditional_pulse_budget_pass'] for r in selected),
            pulse_cases=len(selected),switching_screen='unknown',actual_on_off_force_N=None,**FLAGS))
    optimisation=[]
    for value in values:
        w=value['winding'];required=max(abs(r['required_current_A']) for r in _current_states(value)
            if r['field_purpose']=='Arnold general magnetizing guidance')
        voltages=(24.,48.,96.) if value['name']=='contact-cassette-coupon' else (48.,120.,144.)
        for V in voltages:
            for C in (.02,.05,.1):
                trials=[]
                for T in (20.,80.):
                    rc=_coil_R(value,T)
                    for L in w['inductance_sensitivity_H']:
                        r=pulse.rlc_pulse(rc+.03,L,C,V,.020)
                        dT=r['resistor_I2R_J']*rc/(rc+.03)/(w['copper_mass_kg']*value['materials']['copper']['specific_heat_j_kg_k'])
                        trials.append(dict(coil_temperature_C=T,L_H=L,peak_current_A=r['peak_current_A'],
                            copper_adiabatic_rise_K=dT,capacitor_reversal=r['capacitor_reversal_present'],
                            conditional_budget_pass=required<=r['peak_current_A']<=250 and V<=400 and dT<=5 and not r['capacitor_reversal_present']))
                proposal=dict(parent_geometry_candidate_id=value['candidate_id'],name=value['name'],
                    charge_voltage_V=V,capacitance_F=C,pulse_duration_s=.020,stored_energy_J=.5*C*V*V,
                    conditional_current_demand_A=required,trials=trials,
                    all_sensitivity_points_pass=all(r['conditional_budget_pass'] for r in trials),
                    installed_cap_driver_mass_kg=None,installed_cap_driver_packaging_known=False,
                    hardware_proposal_not_an_adopted_candidate=True,physical_accepted=False)
                proposal['proposal_id']=catalogue.identity(proposal);optimisation.append(proposal)
    if sources(root)!=before:raise ValueError('EPM source changed during optimisation')
    pareto=[]
    for value in values:
        feasible=[r for r in optimisation if r['name']==value['name'] and r['all_sensitivity_points_pass']]
        for row in feasible:
            objectives=(row['stored_energy_J'],row['charge_voltage_V'])
            if not any(all(a<=b for a,b in zip((other['stored_energy_J'],other['charge_voltage_V']),objectives))
                       and any(a<b for a,b in zip((other['stored_energy_J'],other['charge_voltage_V']),objectives))
                       for other in feasible):pareto.append(row['proposal_id'])
    result=dict(schema='osr-electropermanent-study/1',source_snapshot=before,environment=env,candidates=values,
        summary=summary,pulse_cases=cases,loadline_cases=loadlines,magnetizing_state_sensitivities=magnetizing,
        counts=dict(architectures=3,pulse_cases=len(cases),linear_circuit_evaluations=2*len(cases),
                    loadline_cases=len(loadlines),magnetizing_state_cases=len(magnetizing),
                    electrical_bank_proposals=len(optimisation),optimisation_RLC_evaluations=sum(len(r['trials']) for r in optimisation),
                    zero_current_retention_bound_cases=3,spatial_field_solves=0,physical_survivors=0),
        electrical_optimisation=dict(proposals=optimisation,selection_purpose='next electrical bench specification only',
            pareto_proposal_ids=pareto,
            policy='Within each fixed counted winding, minimise stored capacitor energy then voltage among proposals passing all declared L/Cu-temperature points; physical costs/mass unknown',
            selected_proposal_ids=[min((r for r in optimisation if r['name']==v['name'] and r['all_sensitivity_points_pass']),
                key=lambda r:(r['stored_energy_J'],r['charge_voltage_V']))['proposal_id']
                for v in values if any(r['name']==v['name'] and r['all_sensitivity_points_pass'] for r in optimisation)],
            canonical_continuous_current_limits_unchanged=True,installed_packaging_pass=False,physical_accepted=False),
        retired_thin_bridge_counterexample=dict(pole_thickness_m=.01,bar_height_m=.02,Nd_area_m2=.0008,
            reference_Nd_Br_T=1.17,ideal_zero_external_flux_bridge_B_T=1.17*.0008/(.01*.02),
            screen='fail-necessary-thin-bridge',actual_off_force_N=None,
            purpose='Retained discarded parameter point: motivates counted40mm endcaps instead of merely increasing pulse voltage'),
        application_dispositions=[
            dict(application='steady lift / load trim',state='next-experiment',reason='Identify retained bias and gap load lines; keep fast active suspension'),
            dict(application='lateral / yaw bias',state='unknown',reason='Needs signed multidimensional force, moment and stability maps'),
            dict(application='propulsion flux setting',state='exploratory',reason='Independent circuit only; never turn off shared support to regulate thrust'),
            dict(application='cassette / maintenance latch',state='bench-coupon',reason='Positive retention, manual release, wear, EMC and inspection needed'),
            dict(application='parking clamp',state='unknown',reason='Mechanical parking plus state/energy reserve proof; no automatic application on power loss assumed'),
            dict(application='semi-active MR damper',state='exploratory',reason='Separate heat, loss, stability and failed-state evidence required'),
            dict(application='door retention',state='unknown',reason='Magnetic retention is neither actuation nor a qualified door lock'),
            dict(application='HVAC',state='no benefit established',reason='No inherent thermal benefit; winding/driver duty adds unresolved heat')],
        next_experiment=dict(purpose='instrumented bench identification before selecting any train EPM',
            candidate_id=next(v['candidate_id'] for v in values if v['name']=='contact-cassette-coupon'),
            admission='Measure actual geometry/coilR/L, positive/negative current-voltage/flux histories, minor loops, retained flux and hard-PM change',
            gaps_m=[.0002,.001,.012],temperatures_C=[20,50,80],
            pulse_limit='Current-limited protected fixture; supply/driver/clamp limits must be designed before energising',
            measurements=['time-resolved coil voltage/current and capacitor voltage','gap flux and external force at each fixed gap',
                          'AlNiCo minor loops and retention after removing current','NdFeB remanence before/after reverse pulses',
                          'winding/core/driver thermal duty and eddy shielding','independent fast suspension and mechanical safety interfaces'],
            physical_accepted=False),
        conclusions=dict(lift_result_transferable=False,zero_off_force_established=False,
            fixed_state_2D_is_switching_model=False,stationary_EPM_force_stability_established=False,
            fast_active_suspension_still_required=True,mechanical_parking_capture_door_locks_separately_qualified=False),
        limitations=['Linear L sensitivity is not a measured nonlinear inductance envelope',
                     'No measured AlNiCo hysteresis/recoil/knee, switching, retention or EPM force map',
                     'Prescribed circuit states omit steel MMF, leakage, end effects and eddy shielding',
                     'Capacitor stored energy is not measured switching energy; unmodelled magnetic energy/loss ports remain unknown',
                     'All counted PM/coils are onboard; ordinary guideway remains concrete plus passive steel',
                     'Contact-coupon results do not establish12mm support or safety-lock performance'],**FLAGS)
    result['study_id']=catalogue.identity(result)
    return result
