"""Equal-budget mixed civil/vehicle exploration using the shared spatial solver.

Sampled inputs are declared research ranges, not measured distributions. Every
trial is retained, including unsupported arrangements and nonconvergence.
"""
from __future__ import annotations
from copy import deepcopy
import time
import numpy as np
from osr_mech.engineering_definition import fingerprint
from .contracts import load,HERE
from .systems import sample,study_for
from .workflow import candidate
from .construction import units
from .commercial import bill
from .search import select,fronts
from .spatial_demo import configuration
from .spatial_vehicle import run_spatial
from .foundations import stiffness as foundation_stiffness
from .constraints import convergence


def confirm(row):
    """Confirm each sampled loading/environment, separating time and mesh changes."""
    metrics=['maximum_wheel_contact_n','peak_structure_displacement_m','peak_ride_acceleration_m_s2','maximum_wheel_unloading']
    scenarios=[]
    for sample in row['scenarios']:
        inputs=sample['inputs'];hardware=deepcopy(row['hardware']);cfg=deepcopy(row['analysis'])
        hardware['bridge']['candidate']['material']['youngs_modulus_pa']*=inputs['modulus_factor']
        cfg['contact']['friction_coefficient']=inputs['friction']
        cfg['traffic'][0]['load_case'].update(id='uneven',passenger_mass_kg=75.*inputs['passenger_mass_factor'])
        if sample['id']!='nominal':cfg['infrastructure_condition']=dict(foundation_stiffness_factor=.5,bearing_stiffness_factor=.8)
        levels=[];dt=.001
        for _ in range(5):
            r=run_spatial(hardware,cfg,dt=dt,duration_s=.1,deck_mesh=4,rail_step=1.)
            levels.append(r)
            if len(levels)>=2 and convergence(levels,metrics)['passed']:break
            if dt/2<.0000625:break
            dt/=2
        fine=run_spatial(hardware,cfg,dt=dt,duration_s=.1,deck_mesh=8,rail_step=.5)
        scenarios.append(dict(id=sample['id'],inputs=inputs,hardware_definition_sha256=fingerprint(hardware),configuration_sha256=fingerprint(cfg),
            temporal_levels=levels,spatial_level=fine,temporal_refinement=convergence(levels,metrics),
            spatial_refinement=convergence([levels[-1],fine],metrics),
            within_adapter_domain=all(r['within_adapter_domain'] for r in levels+[fine]),capacity_accepted=False))
    return dict(candidate_id=row['candidate_id'],scenarios=scenarios,capacity_accepted=False,
        requires_separate_temporal_and_spatial_refinement=False,
        numerical_confirmation_passed=bool(scenarios) and all(s['within_adapter_domain'] and s['temporal_refinement']['passed'] and s['spatial_refinement']['passed'] for s in scenarios))


def search(model,*,seeds=(11,23),evaluations=8,population=4,wall_seconds=1200):
    if not 1<=len(seeds)<=4 or not 8<=evaluations<=128 or not 4<=population<=evaluations or not 30<=wall_seconds<=3600:
        raise ValueError('shared search budget outside registered bounds')
    config=load(HERE/'config/system-options.json');config['spans_m']=[model['bridge']['candidate']['definition']['deck']['span_m']]
    started=time.monotonic();cache={};events=[];methods=[]
    def evaluate(choice,battery,joint_scale,seed,method,iteration):
        identity=fingerprint(dict(choice=choice,battery_factor=battery,joint_factor=joint_scale))
        row=cache.get(identity);status='cache-hit' if row else 'evaluated'
        if row is None:
            row=dict(candidate_id=identity,choice=choice,battery_factor=battery,joint_factor=joint_scale,
                objectives=[1e30]*3,violation=1e30,status='rejected',engineering_released=False)
            try:
                s,d=study_for(choice,config);s['route_length_m']=model['bridge']['study']['route_length_m']
                c=candidate(d,s);hardware=deepcopy(model);hardware['bridge'].update(candidate=c,study=s)
                if choice['connection_scheme']=='link-slab':
                    hardware['bridge']['span_connection']=dict(stiffness_si=np.diag([1e8,1e8,2e8,1e6,1e6,1e6]).tolist(),
                        basis='synthetic finite six-direction link slab; geometry, cracking, thermal and strength calibration open')
                soil=config['soil_scenarios'][0];support=c.get('foundation_material',c.get('support_material',c['material']))
                longitudinal=foundation_stiffness(c['foundation'],support,soil,8,axis='longitudinal')
                transverse=foundation_stiffness(c['foundation'],support,soil,8,axis='transverse')
                Kf=np.zeros((6,6));Kl=np.asarray(longitudinal['stiffness_matrix']);Kt=np.asarray(transverse['stiffness_matrix'])
                D=np.diag([1.,1.,-1.]);Kf[np.ix_([0,2,4],[0,2,4])]=D@Kl@D
                Kf[np.ix_([1,2,3],[1,2,3])]+=Kt
                Kf[2,2]=(Kl[1,1]+Kt[1,1])/2
                Kf[5,5]=s['ground_scenarios'][0]['rotational_stiffness_nm_rad']
                hardware['bridge']['foundation_stiffness_si']=Kf.tolist()
                for part in hardware['instances']:
                    if part['part_id']=='LM3-TRC-P040':
                        p=part['properties']['design'];p['mass_kg']*=battery
                        p['inertia_tensor_kg_m2']=(np.asarray(p['inertia_tensor_kg_m2'])*battery).tolist()
                        p['uncertainty_kg']*=battery;p['inertia_uncertainty_kg_m2']*=battery
                cfg=configuration(hardware)
                for law in cfg['joint_laws'].values():law['stiffness_si']=(np.asarray(law['stiffness_si'])*joint_scale).tolist()
                scenarios=[]
                # Identical adversarial envelopes for both methods, no implicit probabilities.
                for name,Efactor,massfactor,friction in [('nominal',1.,1.,.3),('low-modulus-heavy-low-adhesion',.9,1.05,.1)]:
                    h=deepcopy(hardware);h['bridge']['candidate']['material']['youngs_modulus_pa']*=Efactor
                    cc=deepcopy(cfg);cc['contact']['friction_coefficient']=friction
                    if name!='nominal':cc['infrastructure_condition']=dict(foundation_stiffness_factor=.5,bearing_stiffness_factor=.8)
                    cc['traffic'][0]['load_case'].update(id='uneven',passenger_mass_kg=75.*massfactor)
                    result=run_spatial(h,cc,dt=.002,duration_s=.02,deck_mesh=2,rail_step=2.)
                    scenarios.append(dict(id=name,inputs=dict(modulus_factor=Efactor,passenger_mass_factor=massfactor,friction=friction),
                        hardware_definition_sha256=fingerprint(h),configuration_sha256=fingerprint(cc),
                        result_sha256=fingerprint(result),full_result=result))
                    if not result['within_adapter_domain']:raise ValueError('uncertainty scenario outside spatial model domain')
                logistics=units(c,s,choice['beam_method'],choice['pier_method'],choice['cap_method'])
                row.update(status='completed',violation=0.,scenarios=scenarios,hardware=hardware,analysis=cfg,
                    native_foundation=dict(longitudinal=longitudinal,transverse=transverse,
                        torsion_basis='separate declared research rotational spring, not a planar condensation result'),
                    construction=logistics,civil_bill=bill(c,s),installed_cost_usd=None,
                    objectives=[logistics['service_beam_mass_kg'],max(r['full_result']['maximum_wheel_contact_n'] for r in scenarios),logistics['maximum_lift_mass_kg']],
                    engineering_feasibility='unresolved')
            except (ValueError,RuntimeError,np.linalg.LinAlgError) as error:row['error']=str(error)
            cache[identity]=row
        events.append(dict(seed=seed,method=method,iteration=iteration,candidate_id=identity,status=status))
        return row
    budget_exhausted=False
    for seed in seeds:
        for method in ('random','pareto-evolution'):
            rng=np.random.default_rng(seed);pool=[];rows=[]
            for i in range(evaluations):
                if time.monotonic()-started>wall_seconds:budget_exhausted=True;break
                parent=None
                if method=='pareto-evolution' and i>=population and pool:
                    parent=pool[int(rng.integers(len(pool)))]
                choice=sample(config,rng,i,parent)
                battery=float(rng.uniform(.9,1.1));joint=float(rng.uniform(.7,1.3))
                if parent:
                    battery=float(np.clip(parent['battery_factor']+rng.normal(0,.03),.9,1.1))
                    joint=float(np.clip(parent['joint_factor']+rng.normal(0,.08),.7,1.3))
                row=evaluate(choice,battery,joint,seed,method,i);rows.append(row)
                good=[r for r in pool+[row] if r['status']=='completed'];pool=select(good,min(population,len(good))) if good else []
            methods.append(dict(seed=seed,method=method,requested_evaluations=evaluations,completed_trials=len(rows),
                numerically_completed=sum(r['status']=='completed' for r in rows),
                candidate_ids=[r['candidate_id'] for r in rows]))
            if budget_exhausted:break
        if budget_exhausted:break
    good=[r for r in cache.values() if r['status']=='completed']
    selected=select(fronts(good)[0],min(2,len(fronts(good)[0]))) if good else []
    confirmations=[]
    for row in selected:
        try:confirmations.append(confirm(row))
        except (ValueError,RuntimeError,np.linalg.LinAlgError) as error:
            confirmations.append(dict(candidate_id=row['candidate_id'],status='failed',error=str(error),numerical_confirmation_passed=False,capacity_accepted=False))
    return dict(schema='osr-shared-mixed-search/1',hardware_definition_sha256=fingerprint(model),
        budgets=dict(seeds=list(seeds),evaluations_per_method=evaluations,population=population,wall_seconds=wall_seconds),
        status='budget-exhausted' if budget_exhausted else 'completed',methods=methods,events=events,candidates=list(cache.values()),
        finalist_confirmations=confirmations,objective_names=['service beam study mass kg','worst sampled wheel force N','maximum construction lift mass kg'],
        uncertainty_basis='two identical deterministic envelopes per design; no probability or reliability claim',
        comparison_scope=dict(route_length_m=model['bridge']['study']['route_length_m'],tracks=2,span_count=model['bridge']['span_count']),
        qualified_feasible_pareto_set=[],physical_validation=False,engineering_released=False,
        open_gates=['short startup screening is not an operating envelope', 'complete passage and resonance refinement',
                    'nonlinear capacity/fatigue and calibrated soil', 'complete supplier lifecycle quotations',
                    'continuous construction/joint resistance and calibrated link-slab laws', 'flexible component sensitivity and physical holdout correlation'])
