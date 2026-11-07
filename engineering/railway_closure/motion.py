"""Rebuild plant/controller inputs from the integrated installed load packet."""
from copy import deepcopy
from math import sqrt
from pathlib import Path
import json

from engineering.station_pair import coordinator as pair, profiles, control_policy, native_bridge
from engineering.station_rail.common import identity, digest
from . import ROOT


def case(installed, *, mass_case='base', force_case='base', speed_km_h=60.,
         grade=0., wind=0., dt=.05, fault=None, hotel_W_per_car=None,
         grade_observation=None, sensor_biases=None, drive_fault_observed=False,
         candidate_bundle=None,root=ROOT):
    if installed['evaluation_id'] != identity({k: v for k, v in installed.items() if k != 'evaluation_id'}):
        raise ValueError('Sealed integrated installed mass required')
    if mass_case not in ('low','base','high'):
        raise ValueError('Explicit supported mass scenario required')
    for name,want in installed['source_sha256'].items():
        if digest(Path(root)/name)!=want:raise ValueError('Installed input source changed: '+name)
    cid=installed['candidate_id']
    if candidate_bundle is not None:
        if (candidate_bundle['evaluation_id']!=identity({k:v for k,v in candidate_bundle.items() if k!='evaluation_id'})
            or candidate_bundle['candidate_id']!=identity(candidate_bundle['physical_definition'])
            or candidate_bundle['installed_mass_evaluation_id']!=installed['evaluation_id']
            or candidate_bundle['installed_component_candidate_id']!=cid):
            raise ValueError('Native movement belongs to a different canonical bundle')
        cid=candidate_bundle['candidate_id']
    brief, bundle, old_mass, parents = pair.variants(root)
    parent = next(v for v in parents if v['family']=='powered-wheel'
                  and v['geometry']['driven_axles']==12
                  and v['physical_definition']['station_spacing_m']==1500.)
    q = pair.case_for(parent,bundle,old_mass,brief,speed_km_h=speed_km_h,
                     mass_case=mass_case,force_case=force_case,grade=grade,wind=wind,
                     dt=dt,fault=fault,hotel_W_per_car=hotel_W_per_car,control_mode='feedback',
                     grade_observation=grade_observation,sensor_biases=sensor_biases,
                     drive_fault_observed=drive_fault_observed,root=root)
    loads = {r['name'].removeprefix('normal-'):r for r in installed['load_cases']
             if r['name'].startswith('normal-')}
    row = loads[mass_case]; mass = row['train_mass_kg']; v = installed['variant']
    adhesion = brief['degraded_adhesion_hypothesis'] if fault=='wet' else brief['normal_adhesion_hypothesis']
    q.update(candidate_id=cid,mass_kg=mass,
             rotating_equivalent_mass_kg=mass*brief['rotating_equivalent_fraction_hypothesis'][mass_case],
             brake_adhesion_force_cap_n=mass*9.80665*adhesion/sqrt(1+grade**2))
    q['drive']=profiles.force_profile(v,mass_kg=mass,case=force_case,
                                     adhesion=adhesion,brief=brief,grade=grade)
    grid_limit=v['grid_power_limit_W_per_train']
    q['drive']['grid_power_w']=min(q['drive']['grid_power_w'],grid_limit)
    q['drive']['mechanical_power_w']=min(q['drive']['mechanical_power_w'],grid_limit*q['drive']['electrical_efficiency'])
    q['drive']['contact_force_cap_n']=adhesion*row['driven_static_axle_force_N']/sqrt(1+grade**2)
    p=json.loads((Path(root)/control_policy.POLICY).read_bytes())
    c=q['control']
    low,high=loads['low'],loads['high']
    contact=brief['degraded_adhesion_hypothesis']*low['driven_static_axle_force_N']/sqrt(1+p['numerical_grade_magnitude_limit']**2)
    lower_start=min(v['rated_force_ceiling_N']*brief['force_rating_fraction_hypothesis']['base']
                    *p['start_traction_lower_fraction_of_nominal'],contact)
    c.update(mass_lower_kg=low['train_mass_kg'],mass_upper_kg=high['train_mass_kg'],
             rotating_mass_upper_kg=high['train_mass_kg']*brief['rotating_equivalent_fraction_hypothesis']['high'],
             rolling_resistance_upper_n=high['train_mass_kg']*9.80665*p['rolling_coefficient_upper_hypothesis'],
             start_traction_lower_bound_n=lower_start)
    static={k:v for k,v in c.items() if k not in control_policy.OBSERVATIONS|{'policy_id'}}
    c['policy_id']=identity(dict(candidate_id=cid,parameters=static,
                                 policy_sha256=digest(Path(root)/control_policy.POLICY),
                                 installed_mass_evaluation_id=installed['evaluation_id'],
                                 native_method_sha256=native_bridge.sources(root)))
    q.pop('id',None);q['id']=identity(q)
    return q


def controlled_cycle(installed, *, enabled=True, count=8, dt=.05, root=ROOT, **kwargs):
    from engineering.station_cycle import coordinator as cycle, design
    p=design.policy(root)
    q=case(installed,dt=dt,root=root,**kwargs)
    d=deepcopy(installed['recovery_design']);d['variant']['candidate_id']=q['candidate_id']
    request=cycle.make_request(d,q,p,count=count,enabled=enabled)
    request['release_control']=dict(mode='grid-substitution-slew/1',force_slew_n_s=10000.,
                                    maximum_traction_share=.8,reserve_factor=2.)
    request.pop('id');request['id']=identity(request)
    return request
