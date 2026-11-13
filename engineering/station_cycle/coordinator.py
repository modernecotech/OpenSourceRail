"""One identified pilot through motion, stored energy, quantities and costs."""
from copy import deepcopy
from pathlib import Path
import fcntl,gzip,json,time
from engineering.station_pair import coordinator as pair, economics,lifecycle
from engineering.station_pair import native_bridge as journey_bridge
from engineering.station_rail.common import identity,digest,encoded
from engineering.run_cache import cleanup_cargo_targets
from . import ROOT,FLAGS,design,history,native_bridge


def sources(root=ROOT):
    root=Path(root)
    paths=[p for p in (root/'engineering/station_cycle').rglob('*') if p.is_file()
        and p.suffix in ('.py','.json','.html','.css','.js')]
    return {**pair.source_hashes(root),**lifecycle.sources(root),**design.sources(root),
        'engineering/station_pair/native_products.py':digest(root/'engineering/station_pair/native_products.py'),
        'engineering/design_search/requirement_policy.py':digest(root/'engineering/design_search/requirement_policy.py'),
        **{p.relative_to(root).as_posix():digest(p) for p in paths},
        history.OUTPUT+'/manifest.json':digest(root/history.OUTPUT/'manifest.json'),
        history.OUTPUT+'/packet-and-declared-sources.tar.gz':digest(root/history.OUTPUT/'packet-and-declared-sources.tar.gz')}


def stations(d,p):
    present=d['recovery_hardware'];tech=p[d['technology']] if present else None
    stages=[]
    for i in range(p['capture_stages']):
        a=p['station_spacing_m']-p['capture_length_m']+i*p['capture_length_m']/p['capture_stages']
        stages.append(dict(start_m=a,end_m=a+p['capture_length_m']/p['capture_stages'],
            max_force_n=p['stage_force_n'] if present else 0.,max_power_w=p['stage_power_w'] if present else 0.))
    return [dict(id=name,initial_energy_j=0.,
        store=dict(capacity_j=d['capacity_j'],capture_efficiency=tech['capture_efficiency'] if present else 1.,
            release_efficiency=tech['release_efficiency'] if present else 1.,leakage_per_s=tech['leakage_per_s'] if present else 0.),
        capture_stages=deepcopy(stages),release=dict(start_m=p['release_window_m'][0],end_m=p['release_window_m'][1],
            max_force_n=p['release_force_n'] if present else 0.,max_power_w=p['release_power_w'] if present else 0.),
        reset=dict(duration_s=p['reset_duration_s'] if present else 0.,grid_energy_j=p['reset_grid_energy_j'] if present else 0.,
            grid_power_w=p['reset_grid_power_w'] if present else 0.)) for name in ('A','B')]


def make_request(d,template,p,*,count,enabled=True,experiment='nominal'):
    ss=stations(d,p)
    if experiment=='initially-full':
        for s in ss:s['initial_energy_j']=s['store']['capacity_j']
    if experiment=='slow-reset':
        for s in ss:s['reset']['duration_s']=600.
    if experiment=='storage-leakage':
        for s in ss:s['store']['leakage_per_s']=.001
    if experiment=='low-transfer-power':
        for s in ss:
            s['release']['max_power_w']*=.25
            for stage in s['capture_stages']:stage['max_power_w']*=.25
    legs=[]
    for i in range(count):
        q=deepcopy(template)
        if i%2:
            g=q['grade_fraction'];q['grade_fraction']=-g
            q['control']['grade_estimate_fraction']*=-1
            if d['variant']['family']=='cable':q['drive']['external_resistance_n']-=2*2500*9.80665*g
        q.pop('id');q['id']=identity(dict(request=q,leg_index=i))
        legs.append(dict(train_id='point-train-01',journey=q,departure_station_id='A' if i%2==0 else 'B',
            arrival_station_id='B' if i%2==0 else 'A',departure_time_s=i*p['leg_departure_interval_s'],
            departure_authorized=not (experiment=='no-authority' and i==1),
            capture_failed=not enabled or experiment=='capture-failed',
            release_failed=not enabled or experiment=='release-failed',reset_failed=experiment=='reset-failed' and i==0))
    req=dict(candidate_id=d['variant']['candidate_id'],stations=ss,legs=legs)
    req['id']=identity(req);return req


def requests(root=ROOT):
    brief,bundle,mass,designs=design.variants(root);p=design.policy(root);out=[]
    for d in designs:
        v=d['variant'];q=pair.case_for(v,bundle,mass,brief,speed_km_h=d['speed_cap_km_h'],control_mode='feedback',root=root)
        def add(name,template,count,enabled=True):
            out.append(dict(design=d,experiment=name,storage_enabled=enabled and d['recovery_hardware'],
                nominal=name in ('nominal','recovery-disabled'),
                request=make_request(d,template,p,count=count,enabled=enabled,experiment=name)))
        add('nominal',q,p['nominal_legs'])
        if d['recovery_hardware']:add('recovery-disabled',q,p['nominal_legs'],enabled=False)
        refined=deepcopy(q);refined['dt_s']=brief['refined_dt_s'];refined['id']=identity({k:v for k,v in refined.items() if k!='id'})
        add('refined-dt',refined,p['fault_legs'])
        for name,t in pair.followup_requests(v,bundle,mass,brief,q,root=root):add(name,t,p['fault_legs'])
        if d['recovery_hardware']:
            for name in ('capture-failed','release-failed','reset-failed','slow-reset','storage-leakage','low-transfer-power','initially-full','no-authority'):
                add(name,q,p['fault_legs'])
    return brief,bundle,mass,p,out


def evaluate_cost(meta,result,baseline,brief,bundle,mass,p,*,root=ROOT):
    d=meta['design'];v=d['variant']
    # Financial service remains the same 200 s demand-led scenario. No slower
    # serial shuttle or warm-store leg is silently annualized as that service.
    core=economics.evaluate(v,baseline,bundle,mass,brief,root=root)
    context=dict(schema='osr-station-pair-lifecycle-energy/1',candidate_id=v['candidate_id'],
        input_cost_evaluation_id=core['evaluation_id'],source_evaluation_id=result['evaluation_id'],
        annual_energy_usd={c:None for c in design.CASES},service_fulfilled=False,
        basis='Serial energy-store experiment does not establish concurrent 200 s service. Complete annual energy and NPV remain unknown; no regeneration saving is annualized.')
    context['evaluation_id']=identity(context)
    ledger=lifecycle.evaluate(core,brief,extra_accounts=design.added_accounts(d,core,p),energy_context=context,root=root)
    return dict(base_pilot=core,full_scope=ledger)


def row(meta,result,cost,p,brief):
    d=meta['design'];v=d['variant'];method=cost['full_scope']['methods'][0]
    journeys=[l['journey'] for l in result['legs'] if l['journey'] is not None]
    moving_jerk=max((j['maximum_absolute_jerk_m_s3'] for j in journeys),default=None)
    end=max((l['end_time_s'] for l in result['legs']),default=0.)
    powers={leg['journey']['auxiliary_power_w'] for leg in meta['request']['legs']}
    if len(powers)!=1:raise ValueError('Mixed auxiliary schedules need an explicit piecewise duty adapter')
    power=powers.pop();start=meta['request']['legs'][0]['departure_time_s']
    horizon=max(0.,end-start)
    # Native journey records include a per-leg dwell allowance even for a failed
    # journey. Use the actual cycle clock once, including completed dwell/reset
    # and serial waits, without adding another terminal dwell.
    aux_grid=power*horizon/brief['hotel_charge_efficiency_hypothesis']
    return_allowance=0.
    if v['family']=='cable':
        return_allowance=len(journeys)*(.5*v['external_mass_kg']*5.**2+v['external_resistance_N']*v['geometry']['powered_front_window_m'][1])/v['electrical_efficiency_hypothesis']
    energy=dict(auxiliary_observation_horizon_s=horizon,continuous_auxiliary_power_w=power,
        native_journey_dwell_auxiliary_j=result['ledger']['auxiliary_load_energy_j'],traction_grid_j=result['ledger']['grid_traction_energy_j'],module_reset_grid_j=result['ledger']['reset_grid_energy_j'],
        auxiliary_and_charge_loss_grid_j=aux_grid,ordinary_tug_return_grid_allowance_j=return_allowance,
        known_grid_subtotal_j=result['ledger']['grid_traction_energy_j']+result['ledger']['reset_grid_energy_j']+aux_grid+return_allowance,
        unmodeled_grid_standstill_copper_losses=True,repeated_thermal_and_charger_limits_verified=False,
        basis='Scoped modeled subtotal; declared constant auxiliary load over the explicit cycle observation horizon including serial waits, with declared charging losses. Full-return cable allowance per executed movement, not a validated return trajectory.')
    return dict(candidate_id=v['candidate_id'],name=v['name'],technology=d['technology'],capacity_j=d['capacity_j'],
        sizing=d['sizing'],energy_reconciliation=energy,maximum_moving_jerk_m_s3=moving_jerk,
        advisory_screen=(result['arrived_legs']==result['scheduled_legs'] and moving_jerk is not None and moving_jerk<=brief['comfort_jerk_target_m_s3']*1.01 and all(j['elapsed_s']<=brief['maximum_pair_journey_s'] and j['control']['bounds_valid'] for j in journeys)),
        speed_cap_km_h=d['speed_cap_km_h'],experiment=meta['experiment'],storage_enabled=meta['storage_enabled'],
        scheduled_legs=result['scheduled_legs'],executed_legs=result['executed_legs'],arrived_legs=result['arrived_legs'],state=result['state'],
        ledger=result['ledger'],station_states=result['station_states'],legs=result['legs'],
        cost=dict(installed_capital_usd=method['installed_capital_usd'],whole_life_NPV_usd=method['whole_life_NPV_usd'],
            known_lifecycle_NPV_usd=method['known_whole_life_subtotal_usd'],
            scopes=[dict(scope=k,total_NPV_usd=method['scope_totals_usd'][k],known_NPV_usd=method['known_scope_subtotals_usd'][k])
                for k in cost['full_scope']['required_cost_scopes']]),
        service=dict(requested_headway_s=cost['base_pilot']['service']['headway_s'],
            modeled_direction_headway_s=2*p['leg_departure_interval_s'],
            modeled_shuttle_capacity_pphpd=brief['normal_people']*3600/(2*p['leg_departure_interval_s'])*brief['planning_occupancy'],
            concurrent_service_verified=False,real_train_circulation_verified=False),
        cold_start_zero_energy=all(s['initial_energy_j']==0 for s in meta['request']['stations']),
        evaluation_id=result['evaluation_id'],cost_evaluation_id=cost['full_scope']['evaluation_id'],**FLAGS)


def run(output,*,root=ROOT):
    root=Path(root).resolve();output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    with (output/'coordinator.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if (output/'result.json.gz').exists():raise ValueError('Fresh cycle run required; prior evidence cannot be overwritten')
        started=time.monotonic();before=sources(root)
        brief,bundle,mass,p,meta=requests(root)
        kernel=native_bridge.build(output,root)
        native_started=time.monotonic()
        results=native_bridge.execute([m['request'] for m in meta],output,root=root,kernel=kernel)
        native_wall_s=time.monotonic()-native_started
        unique={m['design']['variant']['candidate_id']:m['design'] for m in meta}
        qs=[pair.case_for(d['variant'],bundle,mass,brief,speed_km_h=d['speed_cap_km_h'],control_mode='feedback',root=root) for d in unique.values()]
        base_kernel=journey_bridge.build(output,root)
        baselines=journey_bridge.execute(qs,output,root=root,kernel=base_kernel)
        baseline_by_id={r['candidate_id']:r for r in baselines}
        costs={};records=[];cost_started=time.monotonic()
        for m,r in zip(meta,results):
            cid=m['design']['variant']['candidate_id']
            key=cid
            if key not in costs:costs[key]=evaluate_cost(m,r,baseline_by_id[cid],brief,bundle,mass,p,root=root)
            records.append(dict(design=m['design'],experiment=m['experiment'],nominal=m['nominal'],storage_enabled=m['storage_enabled'],
                request=m['request'],result=r,cost=costs[key],
                cost_basis='Same-hardware nominal capital/accounting scenario; fault service energy remains unknown',row=row(m,r,costs[key],p,brief)))
        if sources(root)!=before:raise ValueError('Cycle sources changed during execution; outputs retained without publication')
        value=dict(schema='osr-station-cycle-study/1',source_sha256=before,parent=history.verify(root),brief=brief,policy=p,
            body_candidate_id=bundle['candidate_id'],body_bundle_id=bundle['bundle_id'],mass_evaluation_id=mass['evaluation_id'],
            records=records,baseline_journeys=baselines,baseline_requests=qs,
            native_build_id=kernel[1]['receipt_id'],native_binary_sha256=kernel[1]['binary_sha256'],
            integrated_selection=None,available_operating_maps_added=0,priced_city_models_replaced=0,
            common_fault_recipes=18,concurrent_service_verified=False,
            limitations=['Serial alternating point-train storage cycle; concurrent 200 s fleet, platform, turnback and resource throughput remain unverified',
                'Ideal retarding-force sharing and immediate friction fallback are assumptions; independent brake capacity is never increased by recovery',
                'Spring force–stroke, hydraulic pressure–flow, clutches, contact jerk, lock integrity and fatigue are not validated by generic force/power envelopes',
                'Module material sizing, installation interfaces and supports are bounded reserves; full CAD, CG, axle loads and civil load paths remain open',
                'Thermal state is not carried through all physical station/vehicle assets; repeated thermal duty and charging remain unverified',
                'Ordinary cable tug return, standby/copper losses and passenger HVAC charging require further integrated duty evidence',
                'No physical acceptance, manufacturing release, operating authority or automatic baseline/city adoption'],
            financial_evaluations=len(costs),phase_wall_s=dict(native=native_wall_s,financial_and_rows=time.monotonic()-cost_started),
            execution_wall_s=time.monotonic()-started,**FLAGS)
        value['study_id']=identity(value)
        (output/'result.json.gz').write_bytes(gzip.compress(encoded(value),mtime=0))
        receipt=dict(schema='osr-station-cycle-run/1',study_id=value['study_id'],source_sha256=before,
            files_sha256={'result.json.gz':digest(output/'result.json.gz')},**FLAGS)
        cleanup_cargo_targets(output,['native-target','native-product-target'],{
            **receipt['files_sha256'],
            'native-build.json':digest(output/'native-build.json'),
            'native-build.log':digest(output/'native-build.log'),
            'cycle-build.json':digest(output/'cycle-build.json')})
        receipt['manifest_id']=identity(receipt);(output/'manifest.json').write_bytes(encoded(receipt))
        return value
