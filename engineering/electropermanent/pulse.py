"""Independent linear DC/RLC electrical benchmarks, not hysteretic switching FEM."""
import math
from scipy.integrate import quad


def _positive(value, name):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError('finite positive ' + name + ' required')
    return float(value)


def _inputs(R, L, V, duration):
    values = [_positive(v, n) for v, n in zip((R, L, V, duration), ('R_ohm','L_H','V_V','duration_s'))]
    if not 1e-7<=duration<=1 or not 1e-6<=R<=1e5 or not 1e-8<=L<=10 or not 1e-6<=V<=1000:
        raise ValueError('pulse exceeds bounded electrical study domain')
    return values


def rl_pulse(R_ohm, L_H, V_V, duration_s):
    R, L, V, T = _inputs(R_ohm, L_H, V_V, duration_s)
    current = lambda t: V / R * -math.expm1(-R*t/L)
    energy = quad(lambda t: V*current(t), 0, T, epsabs=1e-10, epsrel=1e-10)[0]
    heat = quad(lambda t: R*current(t)**2, 0, T, epsabs=1e-10, epsrel=1e-10)[0]
    stored = .5*L*current(T)**2
    return dict(model='constant-voltage linear RL; zero initial current', R_ohm=R,L_H=L,V_V=V,duration_s=T,
        peak_current_A=current(T), final_current_A=current(T), input_VI_J=energy,
        resistor_I2R_J=heat, final_inductor_J=stored, energy_residual_J=energy-heat-stored,
        turnoff_inductive_energy_J=stored, turnoff_clamp_qualified=False,
        hysteresis_and_eddy_energy_J=None, switching_qualified=False, physical_accepted=False)


def rlc_pulse(R_ohm, L_H, C_F, V0_V, duration_s):
    R,L,V,T = _inputs(R_ohm,L_H,V0_V,duration_s)
    C = _positive(C_F,'C_F')
    if not 1e-9<=C<=1:
        raise ValueError('capacitance exceeds bounded study domain')
    alpha, omega0 = R/(2*L), 1/math.sqrt(L*C)
    if T*omega0>500:
        raise ValueError('oscillation budget exceeds bounded quadrature domain')
    delta = omega0**2-alpha**2
    if abs(delta) <= 1e-10*omega0**2:
        kind='critical'; current=lambda t: V/L*t*math.exp(-alpha*t)
        voltage=lambda t: V*math.exp(-alpha*t)*(1+alpha*t)
        peak_t=min(T,1/alpha);minimum_v=voltage(T)
    elif delta > 0:
        w=math.sqrt(delta);kind='underdamped'
        current=lambda t: V/(L*w)*math.exp(-alpha*t)*math.sin(w*t)
        voltage=lambda t: V*math.exp(-alpha*t)*(math.cos(w*t)+alpha/w*math.sin(w*t))
        peak_t=min(T,math.atan2(w,alpha)/w)
        minimum_v=voltage(min(T,math.pi/w))
    else:
        beta=math.sqrt(-delta);r1=-omega0**2/(alpha+beta);r2=-alpha-beta;kind='overdamped'
        current=lambda t: V/(L*(r1-r2))*(math.exp(r1*t)-math.exp(r2*t))
        voltage=lambda t: V/(r1-r2)*(-r2*math.exp(r1*t)+r1*math.exp(r2*t))
        peak_t=min(T,math.log(r2/r1)/(r1-r2));minimum_v=voltage(T)
    heat=quad(lambda t:R*current(t)**2,0,T,epsabs=1e-9,epsrel=1e-10,limit=200)[0]
    delivered=quad(lambda t:voltage(t)*current(t),0,T,epsabs=1e-9,epsrel=1e-10,limit=200)[0]
    initial=.5*C*V*V;final_cap=.5*C*voltage(T)**2;final_L=.5*L*current(T)**2
    return dict(model='uncontrolled linear series RLC discharge; no hysteresis/back-EMF or switch commutation',
        damping=kind,R_ohm=R,L_H=L,C_F=C,V0_V=V,duration_s=T,
        peak_current_A=current(peak_t),peak_time_s=peak_t,final_current_A=current(T),
        final_capacitor_voltage_V=voltage(T),
        initial_capacitor_J=initial, capacitor_VI_delivered_J=delivered,
        resistor_I2R_J=heat,final_capacitor_J=final_cap,final_inductor_J=final_L,
        minimum_capacitor_voltage_V=minimum_v,capacitor_reversal_present=minimum_v<0,
        energy_residual_J=initial-final_cap-final_L-heat,
        capacitor_port_residual_J=initial-final_cap-delivered,
        sampled_trace=[dict(time_s=T*j/128,current_A=current(T*j/128),capacitor_V=voltage(T*j/128)) for j in range(129)],
        turnoff_inductive_energy_J=final_L, turnoff_clamp_qualified=False,
        hysteresis_and_eddy_energy_J=None,switching_qualified=False,physical_accepted=False)


def coupled_loadline(*, B_gap_T, gaps_m, magnet_length_m, pole_area_m2,
                     nd_area_m2, alnico_area_m2, nd_br_T=1.17, nd_recoil_mu_r=1.05,
                     alnico_normal_Hc_A_per_m=51000.):
    """Zero-current, no-leakage parallel hard/soft branch necessary diagnostic.

    The two branches share H*l and their fluxes add. Prescribed Bgap does NOT
    solve the unknown AlNiCo hysteresis/load line. Steel MMF is neglected.
    """
    if type(B_gap_T) not in (int,float) or not math.isfinite(B_gap_T) or B_gap_T < 0:
        raise ValueError('nonnegative prescribed gap field required')
    if not isinstance(gaps_m,(list,tuple)) or len(gaps_m)!=2:
        raise ValueError('explicit two-gap topology required')
    for value,name in [(x,'gap_m') for x in gaps_m]+[(magnet_length_m,'length'),(pole_area_m2,'pole_area'),
            (nd_area_m2,'nd_area'),(alnico_area_m2,'alnico_area'),(nd_br_T,'Br'),
            (nd_recoil_mu_r,'recoil'),(alnico_normal_Hc_A_per_m,'normal_Hc')]:
        _positive(value,name)
    mu0=4e-7*math.pi
    H=-B_gap_T*sum(gaps_m)/(mu0*magnet_length_m)
    Bnd=nd_br_T+mu0*nd_recoil_mu_r*H
    Bal=(pole_area_m2*B_gap_T-nd_area_m2*Bnd)/alnico_area_m2
    exceeds=abs(H)>alnico_normal_Hc_A_per_m
    return dict(B_gap_T=B_gap_T,gaps_m=list(gaps_m),common_H_A_per_m=H,
        nd_branch_B_T=Bnd,alnico_required_B_T=Bal,
        normal_Hc_ratio=abs(H)/alnico_normal_Hc_A_per_m,
        prescribed_positive_Alnico_branch_exceeds_normal_Hc=exceeds,
        retention_screen='fail-necessary-positive-state' if exceeds else 'unknown',
        actual_gap_field_T=None,actual_force_N=None,remanent_state_known=False,
        reason='Prescribed gap field and optimistic zero-steel-drop/no-leakage circuit; Hc is not a measured irreversible knee',
        physical_accepted=False)


def energized_parallel_circuit(*, H_m_A_per_m, B_alnico_T, gaps_m,
        magnet_length_m, pole_area_m2, nd_area_m2, alnico_area_m2,
        turns, nd_br_T=1.17, nd_recoil_mu_r=1.05):
    """Conditional common-winding Ampere/flux balance, not a hysteresis curve.

    B_alnico is a prescribed sensitivity value at H_m, never inferred from Br.
    Both pulse directions are needed: the hard magnet biases their demands.
    """
    if any(type(v) not in (int,float) or not math.isfinite(v) for v in (H_m_A_per_m,B_alnico_T)):
        raise ValueError('finite prescribed magnetic state required')
    if type(turns) is not int or turns<=0 or len(gaps_m)!=2:
        raise ValueError('positive turns and two explicit gaps required')
    for v in [*gaps_m,magnet_length_m,pole_area_m2,nd_area_m2,alnico_area_m2,nd_br_T,nd_recoil_mu_r]:
        _positive(v,'magnetic geometry/material')
    mu0=4e-7*math.pi
    Bnd=nd_br_T+mu0*nd_recoil_mu_r*H_m_A_per_m
    gap_B=(nd_area_m2*Bnd+alnico_area_m2*B_alnico_T)/pole_area_m2
    mmf_m=H_m_A_per_m*magnet_length_m
    mmf_gap=gap_B*sum(gaps_m)/mu0
    return dict(prescribed_H_m_A_per_m=H_m_A_per_m,prescribed_B_alnico_T=B_alnico_T,
        nd_branch_B_T=Bnd,prescribed_circuit_B_gap_T=gap_B,
        magnet_MMF_At=mmf_m,gap_MMF_At=mmf_gap,required_NI_At=mmf_m+mmf_gap,
        required_current_A=(mmf_m+mmf_gap)/turns,
        state_is_measured=False,steel_drop_and_leakage_omitted=True,
        actual_switching_current_A=None,actual_force_N=None,physical_accepted=False)


def positive_branch_retention_bound(*, gaps_m, magnet_length_m, pole_area_m2,
        nd_area_m2, normal_Hc_A_per_m=51000., nd_br_T=1.17, nd_recoil_mu_r=1.05):
    """Necessary positive-AlNiCo-B interval in the stated no-leakage circuit.

    H>=-Hc plus B_Al>=0 imposes a minimum gap flux from the Nd branch; Ampere's
    law imposes a maximum. No overlap rejects that modelled state. An overlap
    still does not identify a knee, retained minor loop or spatial field.
    """
    if not isinstance(gaps_m,(list,tuple)) or len(gaps_m)!=2:
        raise ValueError('two explicit gaps required')
    for v in [*gaps_m,magnet_length_m,pole_area_m2,nd_area_m2,normal_Hc_A_per_m,nd_br_T,nd_recoil_mu_r]:
        _positive(v,'retention geometry/material')
    mu0=4e-7*math.pi;ndB=nd_br_T-mu0*nd_recoil_mu_r*normal_Hc_A_per_m
    if ndB<=0:raise ValueError('positive hard-Nd branch required for this necessary bound')
    maximum=mu0*magnet_length_m*normal_Hc_A_per_m/sum(gaps_m)
    minimum=nd_area_m2*ndB/pole_area_m2
    return dict(minimum_gap_B_from_positive_branches_T=minimum,
        maximum_gap_B_before_normal_Hc_T=maximum,interval_overlap_T=maximum-minimum,
        status='fail-within-declared-no-leakage-circuit' if minimum>maximum else 'unknown',
        minimum_pole_area_m2=nd_area_m2*ndB/maximum,
        minimum_magnet_length_m=nd_area_m2*ndB*sum(gaps_m)/(pole_area_m2*mu0*normal_Hc_A_per_m),
        actual_retention_qualified=False,irreversible_knee_identified=False,
        limitation='Typical room-reference normal Hc and declared Nd recoil; leakage/3D paths can change this model and external force remains unknown',
        physical_accepted=False)
