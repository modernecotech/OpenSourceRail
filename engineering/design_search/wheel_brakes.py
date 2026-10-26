"""Realisable-stock brake alternatives; no supplier or WSP qualification inferred."""
from copy import deepcopy
from math import pi
from pathlib import Path
from engineering.station_rail import braking,FLAGS
from engineering.station_rail.vehicle import box
from .contracts import identity


def default_parameters():return dict(piston_diameter_m=.1,maximum_pressure_Pa=.6e6,discs_per_car=8)


def revise(parameters,diagnostics,generation):
    p=deepcopy(parameters)
    if generation>0 and p['piston_diameter_m']<.14:p['piston_diameter_m']=.14
    return p


def materialize(vehicle,parameters):
    v=deepcopy(vehicle);d=parameters['piston_diameter_m']
    if parameters['discs_per_car']!=8 or not .1<=d<=.14 or parameters['maximum_pressure_Pa']!=.6e6:raise ValueError('Brake geometry/pressure outside bounded family')
    extra=[]
    if d>.1:
        # Additional annular housing wall stock, not an invented complete
        # supplier caliper. Existing unlocated brake references stay counted.
        for i in range(8):
            volume=pi*((d/2+.02)**2-(d/2)**2)*.08
            extra.append(dict(id=f'wheel-brake-additional-housing/{i}',kind='annular-cylinder',
                at_m=[-7.45+(i//2)*4.95,-.9 if i%2 else .82,.60],axis=[0,1,0],
                radius_m=d/2+.02,inner_radius_m=d/2,length_m=.08,volume_m3=volume,
                density_kg_m3=2710.,mass_kg=volume*2710.,material='aluminium',system='brake-housing-stock',
                cg_m=None,inertia_kg_m2=None,role='unqualified-additional-housing-stock'))
    v['geometry_parts']+=extra;delta=sum(p['mass_kg'] for p in extra)
    for key in ('accounted_tare_kg_per_car','accounted_cap_loaded_kg_per_car','accounted_160_control_kg_per_car'):v['mass'][key]+=delta
    v['mass']['accounted_tare_kg_six_cars']=v['mass']['accounted_tare_kg_per_car']*6
    v['mass']['located_material_kg']=sum(p['mass_kg'] for p in v['geometry_parts'])
    v['mass']['CG_m']=v['mass']['inertia_kg_m2']=None
    v['brake_parameters']=deepcopy(parameters)
    v['brake_stock_scope']='Added housing material only; installed actuator, pad/fade, hose, mounting and any residual overlap remain unknown.'
    return v


def evaluate(vehicle,parameters,*,stopping_budget_m=1000.):
    spec=braking.definition(vehicle);spec['piston_diameter_m_hypothesis']=parameters['piston_diameter_m'];spec['maximum_pressure_Pa_hypothesis']=parameters['maximum_pressure_Pa']
    cases=[];dt=.01
    for load,key in [('empty','accounted_tare_kg_per_car'),('normal','accounted_cap_loaded_kg_per_car'),('crowd','accounted_160_control_kg_per_car')]:
        m=vehicle['mass'][key];eff=m+spec['rotors']['equivalent_inertial_mass_kg_per_car']
        for name,mu,grade,discs in [('dry',.15,0.,8),('wet-downhill',.05,.02,8),('one-channel-lost',.05,.02,4),('adhesion-incompatible',.03,.04,8)]:
            t=x=heat=gravity=0.;v=20.;state='running'
            while t<500:
                f=braking.force_state(spec,m,v,t+dt/2,rail_adhesion=mu,grade_down_fraction=grade,available_discs=discs)
                if not f['valid']:state='outside-domain';break
                a=f['acceleration_m_s2']
                if t>5 and a>=0:state='cannot-stop';break
                h=min(dt,v/-a) if a<0 else dt;next_v=max(0.,v+a*h);distance=(v+next_v)*h/2
                x+=distance;heat+=f['torque_equivalent_brake_force_N_per_car']*distance;gravity+=f['downhill_gravity_N_per_car']*distance;t+=h;v=next_v
                if v<1e-7:state='stopped';break
            residual=.5*eff*20**2+gravity-heat-.5*eff*v**2
            cases.append(dict(load=load,case=name,state=state,stop_distance_m=x if state=='stopped' else None,
                necessary_stopping_screen='pass' if state=='stopped' and x<=stopping_budget_m else 'fail',
                energy_residual_J=residual,adhesion=mu,downhill_fraction=grade,working_discs=discs,
                disc_temperature_C_hypothesis=50+heat/(spec['counted_disc_stock_kg_per_car']*discs/8*500),
                failure_class='system-incompatibility' if name=='adhesion-incompatible' else 'design-failure' if state!='stopped' or x>stopping_budget_m else 'evidence-gap'))
    return dict(schema='osr-wheel-brake-candidate-screen/1',candidate_id=vehicle['candidate_id'],parameters=parameters,cases=cases,
        numerical_method='Deterministic velocity-trapezoid pure-rolling integration of the previously native-Chrono checked force law; not another Chrono journey',
        dt_s=dt,specification=spec,hardware_qualified=False,stopping_budget_m=stopping_budget_m,
        model_valid=all(abs(c['energy_residual_J'])<.001 for c in cases),**FLAGS)
