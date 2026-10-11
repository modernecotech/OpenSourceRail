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
from .variant_compiler import compile_variant, CHOICES_PATH
from engineering.analysis.shared_service import passage_configuration, coverage


def compiled_hardware(model, series_modules):
    """Change real module topology through the same parts/geometry compiler."""
    choices=load(CHOICES_PATH);choices['family']=model['family_definition']['family']
    choices['battery']['series_modules']=series_modules
    if model['revision'].startswith('OSR-TWIN-STUDY-'):
        from engineering.twin_design.compiler import compile_design
        return compile_design(variant_choices=choices)['model']
    return compile_variant(choices)['model']


def complete_run(hardware, cfg, *, dt, mesh, rail, deadline=None):
    cc,plan=passage_configuration(hardware,cfg,speed_m_s=cfg['traffic'][0]['speed_m_s'])
    def budget(sample):
        if deadline is not None and time.monotonic()>deadline:raise TimeoutError('complete-passage search wall budget exhausted')
    result=run_spatial(hardware,cc,dt=dt,duration_s=plan['duration_s'],deck_mesh=mesh,rail_step=rail,sample_callback=budget)
    result['passage_coverage']=coverage(result,plan)
    if not result['passage_coverage']['complete_passage']:raise ValueError('trial did not cover every wheel passage')
    return result


def constraints(result, limits):
    """Unknown adopted limits keep engineering feasibility unresolved."""
    names=('maximum_wheel_contact_n','peak_structure_displacement_m','peak_ride_acceleration_m_s2','maximum_wheel_unloading')
    checks={name:None if limits.get(name) is None else result[name]<=limits[name] for name in names}
    for name,value in limits.items():
        if name not in names or type(value) not in (int,float) or not np.isfinite(value) or value<=0:raise ValueError('invalid adopted search limit: '+name)
    return dict(checks=checks,passed=all(v is True for v in checks.values()),limits_complete=all(v is not None for v in checks.values()))


def confirm(row, deadline=None):
    """Confirm each sampled loading/environment, separating time and mesh changes."""
    metrics=['maximum_wheel_contact_n','peak_structure_displacement_m','peak_ride_acceleration_m_s2','maximum_wheel_unloading']
    scenarios=[]
    for sample in row['scenarios']:
        inputs=sample['inputs'];hardware=deepcopy(row['hardware']);cfg=deepcopy(row['analysis'])
        hardware['bridge']['candidate']['material']['youngs_modulus_pa']*=inputs['modulus_factor']
        cfg['contact']['friction_coefficient']=inputs['friction']
        cfg['traffic'][0]['load_case'].update(id='uneven',passenger_mass_kg=75.*inputs['passenger_mass_factor'])
        if sample['id']!='nominal':cfg['infrastructure_condition']=dict(foundation_stiffness_factor=.5,bearing_stiffness_factor=.8)
        levels=[];dt=.005
        for _ in range(3):
            r=complete_run(hardware,cfg,dt=dt,mesh=2,rail=2.,deadline=deadline)
            levels.append(r)
            if len(levels)>=2 and convergence(levels,metrics)['passed']:break
            if dt/2<.0000625:break
            dt/=2
        spatial=[levels[-1]]
        for mesh,rail in [(4,1.),(8,.5),(16,.25)]:
            spatial.append(complete_run(hardware,cfg,dt=dt,mesh=mesh,rail=rail,deadline=deadline))
            if convergence(spatial,metrics)['passed']:break
        fine=spatial[-1]
        scenarios.append(dict(id=sample['id'],inputs=inputs,hardware_definition_sha256=fingerprint(hardware),configuration_sha256=fingerprint(cfg),
            temporal_levels=levels,spatial_levels=spatial,spatial_level=fine,temporal_refinement=convergence(levels,metrics),
            spatial_refinement=convergence(spatial,metrics),
            within_adapter_domain=all(r['within_adapter_domain'] for r in levels+spatial),
            refined_constraints=constraints(fine,row.get('adopted_limits',{})),capacity_accepted=False))
    return dict(candidate_id=row['candidate_id'],scenarios=scenarios,capacity_accepted=False,
        requires_separate_temporal_and_spatial_refinement=False,
        numerical_confirmation_passed=bool(scenarios) and all(s['within_adapter_domain'] and s['temporal_refinement']['passed'] and s['spatial_refinement']['passed'] for s in scenarios))


def search(model,*,seeds=(11,23),evaluations=8,population=4,wall_seconds=1200,adopted_limits=None):
    if not 1<=len(seeds)<=4 or not 8<=evaluations<=128 or not 4<=population<=evaluations or not 30<=wall_seconds<=3600:
        raise ValueError('shared search budget outside registered bounds')
    config=load(HERE/'config/system-options.json');config['spans_m']=[model['bridge']['candidate']['definition']['deck']['span_m']]
    started=time.monotonic();deadline=started+wall_seconds;cache={};events=[];methods=[];adopted_limits=adopted_limits or {}
    # Reserve finalist time and give each method/seed an independent quota.
    # Cache hits count as trials and their actual cost is reported.
    trial_quota_s=.8*wall_seconds/(2*len(seeds));confirmation_quota_s=.2*wall_seconds
    def evaluate(choice,battery,joint_scale,seed,method,iteration,trial_deadline):
        identity=fingerprint(dict(choice=choice,battery_series_modules=battery,joint_factor=joint_scale,adopted_limits=adopted_limits))
        row=cache.get(identity)
        if row and row.get('status')=='budget-exhausted':row=None
        status='cache-hit' if row else 'evaluated'
        if row is None:
            row=dict(candidate_id=identity,choice=choice,battery_series_modules=battery,joint_factor=joint_scale,
                objectives=[1e30]*3,violation=1e30,status='rejected',engineering_released=False)
            try:
                s,d=study_for(choice,config);s['route_length_m']=model['bridge']['study']['route_length_m']
                c=candidate(d,s);hardware=compiled_hardware(model,battery);hardware['bridge'].update(candidate=c,study=s)
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
                cfg=configuration(hardware)
                for law in cfg['joint_laws'].values():law['stiffness_si']=(np.asarray(law['stiffness_si'])*joint_scale).tolist()
                scenarios=[]
                # Identical adversarial envelopes for both methods, no implicit probabilities.
                for name,Efactor,massfactor,friction in [('nominal',1.,1.,.3),('low-modulus-heavy-low-adhesion',.9,1.05,.1)]:
                    h=deepcopy(hardware);h['bridge']['candidate']['material']['youngs_modulus_pa']*=Efactor
                    cc=deepcopy(cfg);cc['contact']['friction_coefficient']=friction
                    if name!='nominal':cc['infrastructure_condition']=dict(foundation_stiffness_factor=.5,bearing_stiffness_factor=.8)
                    cc['traffic'][0]['load_case'].update(id='uneven',passenger_mass_kg=75.*massfactor)
                    result=complete_run(h,cc,dt=.005,mesh=2,rail=2.,deadline=trial_deadline)
                    scenarios.append(dict(id=name,inputs=dict(modulus_factor=Efactor,passenger_mass_factor=massfactor,friction=friction),
                        hardware_definition_sha256=fingerprint(h),configuration_sha256=fingerprint(cc),
                        result_sha256=fingerprint(result),full_result=result,constraints=constraints(result,adopted_limits)))
                    if not result['within_adapter_domain']:raise ValueError('uncertainty scenario outside spatial model domain')
                logistics=units(c,s,choice['beam_method'],choice['pier_method'],choice['cap_method'])
                feasible=all(r['constraints']['passed'] for r in scenarios)
                row.update(status='completed',violation=0. if feasible else 1e30,scenarios=scenarios,hardware=hardware,analysis=cfg,
                    native_foundation=dict(longitudinal=longitudinal,transverse=transverse,
                        torsion_basis='separate declared research rotational spring, not a planar condensation result'),
                    construction=logistics,civil_bill=bill(c,s),installed_cost_usd=None,
                    objectives=[logistics['service_beam_mass_kg'],max(r['full_result']['maximum_wheel_contact_n'] for r in scenarios),logistics['maximum_lift_mass_kg']],
                    research_constraints_passed=feasible,adopted_limits=deepcopy(adopted_limits),engineering_feasibility='unresolved')
            except (ValueError,RuntimeError,TimeoutError,np.linalg.LinAlgError) as error:
                row['error']=str(error)
                if isinstance(error,TimeoutError):row['status']='budget-exhausted'
            cache[identity]=row
        events.append(dict(seed=seed,method=method,iteration=iteration,candidate_id=identity,status=status))
        return row
    budget_exhausted=False
    for seed in seeds:
        for method in ('random','pareto-evolution'):
            lane_started=time.monotonic();lane_deadline=min(deadline,lane_started+trial_quota_s)
            rng=np.random.default_rng(seed);pool=[];rows=[];lane_exhausted=False
            for i in range(evaluations):
                if time.monotonic()>=lane_deadline:lane_exhausted=True;budget_exhausted=True;break
                parent=None
                if method=='pareto-evolution' and i>=population and pool:
                    parent=pool[int(rng.integers(len(pool)))]
                choice=sample(config,rng,i,parent)
                battery=int(rng.choice([26,28,30]));joint=float(rng.uniform(.7,1.3))
                if parent:
                    battery=int(np.clip(parent['battery_series_modules']+int(rng.choice([-2,0,2])),26,30))
                    joint=float(np.clip(parent['joint_factor']+rng.normal(0,.08),.7,1.3))
                row=evaluate(choice,battery,joint,seed,method,i,lane_deadline);rows.append(row)
                good=[r for r in pool+[row] if r['status']=='completed'];pool=select(good,min(population,len(good))) if good else []
            methods.append(dict(seed=seed,method=method,requested_evaluations=evaluations,completed_trials=len(rows),
                numerically_completed=sum(r['status']=='completed' for r in rows),wall_quota_s=trial_quota_s,
                elapsed_s=time.monotonic()-lane_started,budget_exhausted=lane_exhausted,
                candidate_ids=[r['candidate_id'] for r in rows]))
    good=[r for r in cache.values() if r['status']=='completed']
    selected=select(fronts(good)[0],min(2,len(fronts(good)[0]))) if good else []
    confirmations=[];confirmation_deadline=min(deadline,time.monotonic()+confirmation_quota_s)
    for row in selected:
        try:confirmations.append(confirm(row,confirmation_deadline))
        except (ValueError,RuntimeError,TimeoutError,np.linalg.LinAlgError) as error:
            confirmations.append(dict(candidate_id=row['candidate_id'],status='failed',error=str(error),numerical_confirmation_passed=False,capacity_accepted=False))
    return dict(schema='osr-shared-mixed-search/1',hardware_definition_sha256=fingerprint(model),
        budgets=dict(seeds=list(seeds),evaluations_per_method=evaluations,population=population,wall_seconds=wall_seconds,
            wall_seconds_per_method_seed=trial_quota_s,finalist_reserved_wall_seconds=confirmation_quota_s,
            cache_policy='shared identical-candidate results; hits count as trials; budget failures retried'),
        status='budget-exhausted' if budget_exhausted else 'completed',methods=methods,events=events,candidates=list(cache.values()),
        finalist_confirmations=confirmations,objective_names=['service beam study mass kg','worst sampled wheel force N','maximum construction lift mass kg'],
        uncertainty_basis='two identical deterministic envelopes per design; no probability or reliability claim',
        comparison_scope=dict(route_length_m=model['bridge']['study']['route_length_m'],tracks=2,span_count=model['bridge']['span_count']),
        numerically_confirmed_research_candidates=[c['candidate_id'] for c in confirmations if c.get('numerical_confirmation_passed') and all(s['refined_constraints']['passed'] for s in c['scenarios'])],
        qualified_feasible_pareto_set=[],physical_validation=False,engineering_released=False,
        research_shortlist=[r['candidate_id'] for r in selected],adopted_limits=adopted_limits,
        open_gates=['adopted capacity, ride and unloading limits', 'complete scenario and resonance refinement',
                    'nonlinear capacity/fatigue and calibrated soil', 'complete supplier lifecycle quotations',
                    'continuous construction/joint resistance and calibrated link-slab laws', 'flexible component sensitivity and physical holdout correlation'])
