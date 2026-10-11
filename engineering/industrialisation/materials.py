"""Explicit geometric material screening and first-law duty-cycle accounting."""
from __future__ import annotations
from .common import finite


def panel_screen(material,geometry,demand):
    """Uniform cantilever coupon screen; no supplier-envelope mass inference."""
    L,b,t=(finite(geometry[k],'panel '+k,1e-9) for k in ('length_m','width_m','thickness_m'))
    rho,E=(finite(material[k],'material '+k,1e-9) for k in ('density_kg_m3','longitudinal_modulus_pa'))
    F=finite(demand['tip_force_n'],'tip demand',0.);I=b*t**3/12;mass=rho*L*b*t
    sigma=6*F*L/(b*t*t);deflection=F*L**3/(3*E*I)
    strength=material.get('allowable_stress_pa');limit=demand.get('deflection_limit_m')
    if strength is not None:finite(strength,'conditional stress limit',1e-9)
    if limit is not None:finite(limit,'deflection limit',1e-9)
    return dict(material_id=material['id'],mass_kg=mass,EI_nm2=E*I,tip_deflection_m=deflection,bending_stress_pa=sigma,
        conditional_stress_passed=None if strength is None else sigma<=strength,
        conditional_deflection_passed=None if limit is None else deflection<=limit,
        cost=None if material.get('cost_per_kg') is None else mass*finite(material['cost_per_kg'],'declared material price',0.),
        embodied_carbon_kgco2e=None if material.get('carbon_kgco2e_kg') is None else mass*finite(material['carbon_kgco2e_kg'],'declared carbon factor',0.),
        engineering_accepted=False,limits=['uniform coupon geometry, linear elastic bending; no panel buckling, joints, layup coupling or fatigue',
            'fire/smoke/toxicity, corrosion, ageing, repair, EPD and local supply evidence remain required'])


def thermal_layers(layers,area_m2,temperature_difference_k):
    area=finite(area_m2,'thermal area',1e-9);delta=finite(temperature_difference_k,'temperature difference')
    if not layers:raise ValueError('thermal layer stack required')
    resistance=sum(finite(r['thickness_m'],'layer thickness',1e-9)/finite(r['conductivity_w_m_k'],'conductivity',1e-9)/area for r in layers)
    return dict(resistance_k_w=resistance,heat_flow_w=delta/resistance,thermal_qualification=False,
        limits=['steady one-dimensional conduction; surface films, solar load, bridges, airflow and condensation not resolved'])


def train_energy(duty,mass_kg,traction_efficiency,regeneration_efficiency,auxiliary_power_w,rolling_resistance):
    mass=finite(mass_kg,'train mass',1e-9);traction=finite(traction_efficiency,'traction efficiency',1e-9)
    regen=finite(regeneration_efficiency,'regeneration efficiency',0.);aux=finite(auxiliary_power_w,'auxiliary power',0.)
    resistance=finite(rolling_resistance,'rolling coefficient',0.)
    if traction>1 or regen>1 or not duty:raise ValueError('bounded efficiencies and nonempty duty required')
    battery=mechanical=losses=auxiliary=recovered=0.;rows=[];last_speed=None
    for row in duty:
        if set(row)!={'duration_s','speed_start_m_s','speed_end_m_s','grade_ratio','aerodynamic_force_n'}:raise ValueError('duty segment fields missing or unknown')
        dt=finite(row['duration_s'],'segment duration',1e-9);v0=finite(row['speed_start_m_s'],'speed',0.);v1=finite(row['speed_end_m_s'],'speed',0.)
        if last_speed is not None and abs(v0-last_speed)>1e-10:raise ValueError('duty segment speed discontinuity')
        last_speed=v1;grade=finite(row['grade_ratio'],'grade');aero=finite(row['aerodynamic_force_n'],'aerodynamic resistance',0.)
        if abs(grade)>.1:raise ValueError('screening grade outside declared domain')
        distance=(v0+v1)*dt/2;work=.5*mass*(v1*v1-v0*v0)+(mass*9.81*(resistance+grade)+aero)*distance
        electrical=work/traction if work>=0 else work*regen;loss=electrical-work;aux_energy=aux*dt
        battery+=electrical+aux_energy;mechanical+=work;losses+=loss;auxiliary+=aux_energy;recovered+=max(-electrical,0.)
        rows.append(dict(**row,distance_m=distance,mechanical_work_j=work,electrical_traction_energy_j=electrical,
            conversion_loss_j=loss,auxiliary_energy_j=aux_energy,battery_energy_j=electrical+aux_energy))
    return dict(segments=rows,battery_energy_j=battery,mechanical_work_j=mechanical,conversion_loss_j=losses,
        auxiliary_energy_j=auxiliary,recovered_energy_j=recovered,energy_balance_residual_j=battery-mechanical-losses-auxiliary,
        supplier_maps_used=False,service_delivery_qualified=False,
        limits=['constant efficiencies and supplied aero/auxiliary inputs; no inverter maps, torque limits or battery acceptance limits',
            'screening must be reconciled with detailed pack/thermal models; no CRRC percentage saving inferred'])
