"""Bounded three-train fixed-block capacity research, separate from city defaults.

Exact corridor trajectories feed the actual Rust resource ledger. Synthetic local
occupancy, integer stopping envelopes and repeated stations are hypotheses; this
study does not replace the station-launch protocol or approve moving authority.
"""
from copy import deepcopy
from hashlib import sha256
import gzip
import json
import math
import os
import re
from pathlib import Path
import subprocess
import tomllib

from . import corridor, model, station

ROOT=model.ROOT
INPUT=Path(__file__).with_name('line-capacity.toml')
EXAMPLE=ROOT/'crates/osr-interlocking/examples/line_capacity_replay.rs'
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/line-capacity'
BUILD=['cargo','build','--locked','-p','osr-interlocking','--example','line_capacity_replay','--message-format=json']
API_TEST=['cargo','test','--locked','-p','osr-interlocking','--lib','progressive::tests','--','--test-threads=1']
API_TEST_NAMES={
    'prepare_is_atomic_and_does_not_reserve_a_receiving_berth','readiness_and_clear_body_counterexamples_retain_prepared_locks',
    'snapshots_before_and_after_commit_cannot_resume_after_restart','denied_extension_brakes_inside_previous_owned_authority_without_next_sample_credit',
    'release_needs_geometry_identity_and_no_generic_clear_bypass','raw_proof_and_integrity_faults_hold_without_transfer',
    'duplicate_commit_is_idempotent_but_cannot_extend_a_permission','fabricated_release_pose_and_old_arrived_contract_cannot_clear_current_authority',
    'local_speed_limit_is_enforced_before_general_motion_bounds','invalid_arrival_evidence_holds_and_retains_the_prior_authority',
    'nonuniform_route_speed_limits_are_outside_this_candidate_contract','live_speed_or_missing_body_proof_cannot_authorise_motion'}
FILES={'study.json.gz','execution.json.gz','overview.svg','README.md'}
MAX_FILE=16*1024*1024
MAX_RAW=64*1024*1024
CASES=('pipeline','exclusive-leg','delayed-clearance','stale-position','extended-dwell','coarse-blocks','adverse-brake','emergency-brake-loss','rollback','integrity-loss')
JOINT_CASES=('joint-180','joint-600','joint-replay','joint-restart','joint-prepared-restart','joint-partial-commit','joint-order-commit','joint-conflicting-launch','joint-stale-arrival','joint-receiving-fault')
CONTRACT_CASES=('contract-180','contract-journal','contract-closed-arrival','contract-stale-ready','contract-brake-loss','contract-gap-fault','contract-integrity-loss','contract-rollback','contract-prepared-restart','contract-committed-restart','contract-order-commit','contract-conflicting-prepare','contract-partial-commit')
ALL_CASES=CASES+JOINT_CASES+CONTRACT_CASES
PASS_CASES={'pipeline','coarse-blocks','adverse-brake','joint-600','joint-replay','joint-order-commit','joint-conflicting-launch','contract-180','contract-journal','contract-order-commit','contract-conflicting-prepare'}


def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def digest(value):return sha256(value).hexdigest()


def load():
    a=tomllib.loads(INPUT.read_text())
    if a.get('schema')!='osr-line-capacity-input/1':raise ValueError('line-capacity input schema differs')
    if set(a['validation'])!={'physical_detectors_accepted','independent_brake_accepted','distributed_authority_accepted','whole_line_capacity_accepted','city_default_changed'} or any(v is not False for v in a['validation'].values()):raise ValueError('capacity acceptance must remain open')
    for key,v in a.items():
        if key in {'schema','revision','validation'}:continue
        if type(v) not in (int,float) or not math.isfinite(v) or v<0 or v>100000:raise ValueError('bounded capacity input required: '+key)
    if a['trains']!=3 or a['cars']!=6 or a['headway_s']!=180 or not .01<=a['step_s']<=.1 or a['block_length_m']<400:raise ValueError('bounded three-train/180s reference required')
    if type(a['velocity_error_mmps']) is not int or not 0<=a['velocity_error_mmps']<=1000:raise ValueError('bounded integer velocity error required')
    if any(type(a[k]) is not int for k in ('trains','cars','urban_legs','suburban_legs','downhill_permille')) or not 1<=a['urban_legs']<=5 or not 1<=a['suburban_legs']<=3:raise ValueError('bounded integer counts required')
    if any(not 30<=a[mode+'_dwell_s']<=300 or not 40<=a[mode+'_runtime_s']<=900 for mode in ('urban','suburban')):raise ValueError('bounded runtime/dwell required')
    if a['minimum_deceleration_m_s2']<=9.81*a['downhill_permille']/1000 or a['reaction_s']>2 or a['position_uncertainty_m']>2:raise ValueError('positive net brake and bounded reaction/uncertainty required')
    return a


def source_paths():
    paths={Path(__file__),INPUT,EXAMPLE,ROOT/'engineering/analysis/tests/test_ferrite_maglev_line_capacity.py',ROOT/'Cargo.toml',ROOT/'Cargo.lock',ROOT/'rust-toolchain.toml'}
    # Exact calculation dependencies, never model.sources() or generated packets.
    paths.update(ROOT/p for p in station.sources())
    paths.update({Path(corridor.__file__),corridor.INPUT,model.POLICY,ROOT/'VERSION',
        ROOT/'engineering/ferrite_maglev/optimisation.py',ROOT/'engineering/ferrite_maglev/optimisation.toml',
        ROOT/'engineering/ferrite_maglev/station_structure.py',ROOT/'engineering/ferrite_maglev/station-structure.toml'})
    for name in ('osr-core','osr-interlocking'):
        base=ROOT/'crates'/name;paths.add(base/'Cargo.toml');paths.update(base.rglob('*.rs'))
    return sorted(p for p in paths if p.is_file())


def sources():return {p.relative_to(ROOT).as_posix():digest(p.read_bytes()) for p in source_paths()}


def stopping_envelope_mm(velocity_mmps,*,deceleration_mmps2=600,reaction_ms=200,sample_ns=100_000_000,age_ns=0,maximum_acceleration_mmps2=1000,stop_margin_mm=20000,uncertainty_mm=500,downhill_permille=0):
    """Independent integer oracle; ceilings retain every reaction/build-up term."""
    values=(velocity_mmps,deceleration_mmps2,reaction_ms,sample_ns,age_ns,maximum_acceleration_mmps2,stop_margin_mm,uncertainty_mm,downhill_permille)
    if any(type(v) is not int or v<0 for v in values):raise ValueError('nonnegative integer brake inputs required')
    ceil=lambda n,d:(n+d-1)//d
    net=deceleration_mmps2-ceil(9810*downhill_permille,1000)
    if net<=0:raise ValueError('net deceleration must be positive')
    t=reaction_ms*1_000_000+sample_ns+age_ns;v=velocity_mmps+ceil(maximum_acceleration_mmps2*t,10**9)
    return ceil(velocity_mmps*t,10**9)+ceil(maximum_acceleration_mmps2*t*t,2*10**18)+ceil(v*v,2*net)+stop_margin_mm+uncertainty_mm


def _bounds(a,mode,block,*,joint=False):
    d=a[mode+'_distance_m'];legs=a[mode+'_legs'];bounds=[-150.,200.]+([275.] if joint else [])
    for leg in range(legs):
        end=(leg+1)*d-150.
        while bounds[-1]+block<end-1e-9:bounds.append(bounds[-1]+block)
        bounds.extend([end,(leg+1)*d+200.])
        if joint:bounds.append((leg+1)*d+275.)
    if len(bounds)-1>32:raise ValueError('single local resource domain exceeds 32 resources')
    return bounds


def deployment(a,mode,*,block_length_m=None,joint=False):
    """One fixed line, explicit platform intervals, no train-routing points."""
    bounds=_bounds(a,mode,block_length_m or a['block_length_m'],joint=joint);offset=150.
    cfg=list(sha256(encoded([a,mode,bounds])).digest());length=station.load()['vehicle'];length=a['cars']*length['body_length_m']+(a['cars']-1)*length['coupling_gap_m']
    segments=[dict(resource=i,start_mm=round((start+offset)*1000),end_mm=round((end+offset)*1000),speed_limit_mmps=22223,downhill_permille=a['downhill_permille']) for i,(start,end) in enumerate(zip(bounds,bounds[1:]))]
    berths=[i for i,(start,end) in enumerate(zip(bounds,bounds[1:])) if math.isclose(end-start,350.)]
    resources=[dict(id=i,section=100+i,asset_id=f'capacity-resource-{i}'+('-arrival-overlap' if joint and math.isclose(bounds[i+1]-bounds[i],75.) else ''),kind='platform' if i in berths else 'track',controller=900,conflicts=[i],point_asset_id=None,clearance_basis='synthetic independently identified full-consist rear with bounded uncertainty; unqualified detector') for i in range(len(segments))]
    trains=[dict(asset_id=f'capacity-train-{101+i}',config=dict(owner=dict(train=101+i,session=1),configuration=cfg,length_mm=round(length*1000),minimum_deceleration_mmps2=round(a['minimum_deceleration_m_s2']*1000),reaction_time_ms=round(a['reaction_s']*1000),stop_margin_mm=round(a['stop_margin_m']*1000),maximum_position_uncertainty_mm=round(a['position_uncertainty_m']*1000)),integrity_arrangement='synthetic complete six-car integrity, no splitting',braking_evidence='assumed independent on-board emergency brake at every coast location; no measured acceptance',permitted_route=1) for i in range(a['trains'])]
    participants=[dict(entity=i,role='Voter',session=1,public_key=[i]*32,revoked=False,resources=[]) for i in (1,2,3)]+[dict(entity=101+i,role='Train',session=1,public_key=[i+5]*32,revoked=False,resources=[]) for i in range(a['trains'])]
    railway=dict(schema='osr-tacs-railway/2',revision='capacity-pipeline-local-1',approval_state='prototype-unapproved',runtime=dict(voters=[1,2,3],participants=participants,designed_revision='capacity-pipeline-local-1',installed_state='not-installed',approved_operating_profile='prototype-unapproved',clock_error_ns=0),resources=resources,routes=[dict(id=1,asset_id='fixed-capacity-line',direction='Forward',leader_required=False,operating_scope='bounded local-domain progressive-block numerical study; no points, city authority or station launch substitution',segments=segments,stopping_locations=[dict(asset_id=f'station-{j}',at_mm=round((j*a[mode+'_distance_m']+offset)*1000),platform=i,charger_asset_id=f'charger-{j}',minimum_departure_energy_wh=10000) for j,i in enumerate(berths)])],trains=trains,controllers=[dict(id=900,asset_id='capacity-local-controller',startup_epoch=1,restart_reconciliation='retained ownership; positive identified full-tail proof only')],protected_work_resources=[],maintenance_procedure='offline unapproved study')
    return railway,cfg,bounds,berths


def _profile(mode):
    a=load();_,c,_=model.load();mass=model.mass(c,c['mass']['ferrite_base'],50.)['aw3_kg']
    value=corridor.profile(distance_m=a[mode+'_distance_m'],runtime_s=a[mode+'_runtime_s'],cars=a['cars'],car_mass_kg=mass,mode=mode)
    if not value['study_pass']:raise ValueError('current corridor motion profile fails')
    return value


def request(mode='urban',case='pipeline'):
    if case in CONTRACT_CASES:return contract_request(mode,case)
    if case in JOINT_CASES:return joint_request(mode,case)
    if mode not in {'urban','suburban'} or case not in CASES:raise ValueError('declared mode/case required')
    a=load();d=a[mode+'_distance_m'];runtime=a[mode+'_runtime_s'];dwell=a[mode+'_dwell_s'];step=a['step_s'];trains=a['trains'];headway=a['headway_s']
    if case=='adverse-brake':a=deepcopy(a);a['minimum_deceleration_m_s2']=.4;a['reaction_s']=1.;a['downhill_permille']=10
    railway,cfg,bounds,berths=deployment(a,mode,block_length_m=1000. if case=='coarse-blocks' else None)
    first_berth=berths[1];frames=[];t=_profile(mode);horizon=(trains-1)*headway+runtime+10
    # The leaders continue into subsequent legs. No train is deleted at a sink,
    # and no final berth is reused without a positive rear-bound clearance.
    for tick in range(1,math.ceil(horizon/step)+1):
        time=tick*step;now=1_000_000_000+round(time*1e9);positions=[]
        for j in range(trains):
            elapsed=time-j*headway
            if elapsed<0:continue
            position=0.;speed=0.;remaining=elapsed
            for leg in range(a[mode+'_legs']):
                if remaining<runtime:
                    p=corridor.trajectory_at(t,remaining);position=leg*d+p['position_m'];speed=p['speed_m_s'];break
                position=(leg+1)*d;remaining-=runtime
                stop=dwell+(180. if case=='extended-dwell' and j==0 and leg==0 else 0.)
                if remaining<stop:break
                remaining-=stop
            else:raise ValueError('study horizon exceeds final modelled leg')
            observed=now-round(a['stale_age_s']*1e9) if case=='stale-position' and j==0 and time>=a['stale_after_s'] else now
            fault= j==0 and time>=a['stale_after_s']
            front=round((position+150.)*1000)-(5000 if case=='rollback' and fault else 0)
            positions.append(dict(train=101+j,front_mm=front,velocity_mmps=math.ceil(speed*1000),observed_ns=observed,
                integrity_proved=not(case=='integrity-loss' and fault),independent_brake_ready=not(case=='emergency-brake-loss' and fault)))
        frames.append(dict(now_ns=now,positions=positions))
    # Delay full-tail clearance of the first receiving berth until after the
    # follower needs its stopping envelope. The original lock must persist.
    delay_until=round((1.+runtime+dwell+a['delayed_clearance_s'])*1e9)
    return dict(model=railway,configuration=cfg,frames=frames,maximum_acceleration_mmps2=round(a['maximum_acceleration_m_s2']*1000),sample_ns=round(step*1e9),exclusive_leg=case=='exclusive-leg',delayed_clear_resource=first_berth if case=='delayed-clearance' else None,delay_until_ns=delay_until,competing_train=case=='pipeline'),dict(mode=mode,case=case,distance_m=d,runtime_s=runtime,dwell_s=dwell,headway_s=headway,trains=trains,legs=a[mode+'_legs'],horizon_s=horizon,train_length_m=railway['trains'][0]['config']['length_mm']/1000,block_boundaries_m=bounds,receiving_berth_resource=first_berth,**model.FLAGS)


def joint_request(mode='urban',case='joint-180'):
    if mode not in {'urban','suburban'} or case not in JOINT_CASES:raise ValueError('declared joint mode/case required')
    a=load();a[mode+'_legs']=7 if mode=='urban' else 4
    headway=180. if case=='joint-180' else 600.;runtime=a[mode+'_runtime_s'];dwell=a[mode+'_dwell_s'];d=a[mode+'_distance_m'];step=a['step_s']
    railway,cfg,bounds,berths=deployment(a,mode,block_length_m=1000.,joint=True)
    bundles=[dict(leg=j,corridor=berths[j]+2,receiving_berth=berths[j+1],overlap=berths[j+1]+1) for j in range(len(berths)-1)]
    horizon=(a['trains']-1)*headway+runtime+10 if case in {'joint-600','joint-replay','joint-180'} else 70.
    frames=[];t=_profile(mode)
    for tick in range(1,math.ceil(horizon/step)+1):
        time=tick*step;now=1_000_000_000+round(time*1e9);positions=[]
        for j in range(a['trains']):
            elapsed=time-j*headway-step
            if elapsed< -1e-8:continue
            remaining=max(0.,elapsed);position=speed=0.;launch_leg=None
            for leg in range(a[mode+'_legs']):
                if remaining<runtime-1e-8:
                    if remaining<1e-8:position=leg*d;speed=0.;launch_leg=leg;break
                    p=corridor.trajectory_at(t,remaining);position=leg*d+p['position_m'];speed=p['speed_m_s'];launch_leg=leg;break
                position=(leg+1)*d;remaining-=runtime
                if remaining<dwell-1e-8:break
                remaining=max(0.,remaining-dwell)
            else:raise ValueError('joint horizon exceeds bounded railway')
            positions.append(dict(train=101+j,front_mm=round((position+150.)*1000),velocity_mmps=math.ceil(speed*1000),observed_ns=now,integrity_proved=True,independent_brake_ready=True,launch_leg=launch_leg))
        frames.append(dict(now_ns=now,positions=positions))
    value=dict(model=railway,configuration=cfg,frames=frames,maximum_acceleration_mmps2=round(a['maximum_acceleration_m_s2']*1000),sample_ns=round(step*1e9),exclusive_leg=False,delayed_clear_resource=None,delay_until_ns=0,competing_train=False,joint=dict(control=case,fault_at_ns=71_000_000_000,bundles=bundles))
    meta=dict(mode=mode,case=case,distance_m=d,runtime_s=runtime,dwell_s=dwell,headway_s=headway,trains=a['trains'],legs=a[mode+'_legs'],horizon_s=horizon,train_length_m=railway['trains'][0]['config']['length_mm']/1000,block_boundaries_m=bounds,receiving_berth_resource=berths[1],joint_contract='existing-station-launch/1 plus generic fixed blocks',**model.FLAGS)
    return value,meta


def contract_request(mode='urban',case='contract-180'):
    if mode not in {'urban','suburban'} or case not in CONTRACT_CASES:raise ValueError('declared progressive candidate mode/case required')
    a=load();headway=180.;runtime=a[mode+'_runtime_s'];dwell=a[mode+'_dwell_s'];d=a[mode+'_distance_m'];step=a['step_s']
    railway,cfg,bounds,berths=deployment(a,mode)
    horizon=(a['trains']-1)*headway+runtime+10 if case in {'contract-180','contract-journal','contract-closed-arrival'} else 70.
    frames=[];t=_profile(mode)
    for tick in range(1,math.ceil(horizon/step)+1):
        time=tick*step;now=1_000_000_000+round(time*1e9);positions=[]
        for j in range(a['trains']):
            elapsed=time-j*headway-step
            if elapsed< -1e-8:continue
            remaining=max(0.,elapsed);position=speed=0.;launch_leg=None
            for leg in range(a[mode+'_legs']):
                if remaining<runtime-1e-8:
                    if remaining<1e-8:position=leg*d;speed=0.;launch_leg=leg;break
                    p=corridor.trajectory_at(t,remaining);position=leg*d+p['position_m'];speed=p['speed_m_s'];launch_leg=leg;break
                position=(leg+1)*d;remaining-=runtime
                if remaining<dwell-1e-8:break
                remaining=max(0.,remaining-dwell)
            else:raise ValueError('candidate horizon exceeds bounded railway')
            positions.append(dict(train=101+j,front_mm=round((position+150.)*1000),velocity_mmps=math.ceil(speed*1000),observed_ns=now,integrity_proved=True,independent_brake_ready=True,launch_leg=launch_leg))
        frames.append(dict(now_ns=now,positions=positions))
    policy=dict(maximum_acceleration_mmps2=round(a['maximum_acceleration_m_s2']*1000),maximum_sample_ns=round(step*1e9),velocity_error_mmps=a['velocity_error_mmps'],minimum_gap_um=3000,maximum_gap_um=13000)
    value=dict(model=railway,configuration=cfg,frames=frames,maximum_acceleration_mmps2=policy['maximum_acceleration_mmps2'],sample_ns=policy['maximum_sample_ns'],exclusive_leg=False,delayed_clear_resource=None,delay_until_ns=0,competing_train=False,contract=dict(control=case,fault_at_ns=71_000_000_000,receiving_berth=berths[1],policy=policy))
    meta=dict(mode=mode,case=case,distance_m=d,runtime_s=runtime,dwell_s=dwell,headway_s=headway,trains=a['trains'],legs=a[mode+'_legs'],horizon_s=horizon,train_length_m=railway['trains'][0]['config']['length_mm']/1000,block_boundaries_m=bounds,receiving_berth_resource=berths[1],candidate_contract='osr-progressive-departure/1; remote berth not reserved at departure',**model.FLAGS)
    return value,meta


def _command(command,stdin=None):
    r=subprocess.run(command,input=stdin,cwd=ROOT,env=dict(os.environ,CARGO_TERM_COLOR='never'),capture_output=True,text=True,timeout=240,check=False)
    if r.returncode:raise RuntimeError('line-capacity execution failed: '+r.stderr[-4000:])
    value=dict(command=list(map(str,command)),returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
    if len(encoded(value))>MAX_RAW:raise ValueError('line-capacity execution transcript exceeds bound')
    return value


def compile_replay():
    compiler=_command(['rustc','--version']);build=_command(BUILD);artifacts=[v['executable'] for line in build['stdout'].splitlines() if (v:=json.loads(line)).get('reason')=='compiler-artifact' and v.get('target',{}).get('name')=='line_capacity_replay' and v.get('executable')]
    if len(artifacts)!=1:raise ValueError('actual Rust replay artifact missing')
    binary=Path(artifacts[0])
    if not binary.is_file() or binary.is_symlink():raise ValueError('ordinary compiler artifact required')
    return binary,dict(compiler=compiler,build=build,binary_sha256=digest(binary.read_bytes()))


def replay(binary,mode='urban',case='pipeline'):
    value,meta=request(mode,case);raw=encoded(value);entry=_command([str(binary)],raw.decode());result=json.loads(entry['stdout'])
    control=_check_replay(result,value,case)
    return dict(**meta,request_sha256=digest(raw),request_frames=len(value['frames']),replay=result,expected_schedule_pass=case in PASS_CASES,control_pass=control),entry


def _check_replay(result,value,case):
    if case in CONTRACT_CASES:return _check_contract_replay(result,value,case)
    if case in JOINT_CASES:return _check_joint_replay(result,value,case)
    if result.get('schema')!='osr-line-capacity-replay/1' or result.get('physical_output_authorised') is not False or result.get('whole_line_capacity_accepted') is not False:raise ValueError('line-capacity Rust scope differs')
    expected=case in {'pipeline','coarse-blocks','adverse-brake'}
    control=result['study_pass'] is expected
    control&=type(result.get('frames_executed')) is int and 0<result['frames_executed']<=len(value['frames'])
    for key in ('release_count','stopped_forward_withdrawals','fault_fenced_resources','reservation_count','renewal_count','maximum_owned_resources','maximum_active_trains','maximum_stopping_envelope_mm'):
        control&=type(result.get(key)) is int and result[key]>=0
    control&=result['maximum_owned_resources']<=len(value['model']['resources']) and result['maximum_active_trains']<=3
    if expected:
        control&=result.get('failure') is None and result['frames_executed']==len(value['frames']) and result['minimum_train_separation_mm']>0 and result['minimum_stopping_authority_margin_mm']>=0
        # Independent Python integer arithmetic recovers the largest envelope
        # from exact requested velocities; no leader stopping credit is used.
        configs={t['config']['owner']['train']:t['config'] for t in value['model']['trains']};grade=max(s['downhill_permille'] for s in value['model']['routes'][0]['segments'])
        maximum=max(stopping_envelope_mm(p['velocity_mmps'],deceleration_mmps2=cfg['minimum_deceleration_mmps2'],reaction_ms=cfg['reaction_time_ms'],sample_ns=value['sample_ns'],age_ns=f['now_ns']-p['observed_ns'],maximum_acceleration_mmps2=value['maximum_acceleration_mmps2'],stop_margin_mm=cfg['stop_margin_mm'],uncertainty_mm=cfg['maximum_position_uncertainty_mm'],downhill_permille=grade) for f in value['frames'] for p in f['positions'] for cfg in (configs[p['train']],))
        control&=result['maximum_stopping_envelope_mm']==maximum
    if case=='pipeline':control&=result['maximum_active_trains']==3 and result['release_count']>0 and result['competing_owner_rejected'] and result['unidentified_tail_clear_rejected']
    if case=='stale-position':control&=result.get('failure',{}).get('kind')=='stale-position' and bool(result['retained_owners'])
    if case in {'emergency-brake-loss','rollback','integrity-loss'}:
        control&=result.get('failure',{}).get('kind')=={'emergency-brake-loss':'independent-brake-unavailable','rollback':'rollback-observed','integrity-loss':'consist-integrity-lost'}[case] and bool(result['retained_owners'])
    if case in {'emergency-brake-loss','rollback','integrity-loss','stale-position'}:control&=result['fault_fenced_resources']>0
    if case in {'delayed-clearance','extended-dwell','exclusive-leg'}:control&=result.get('failure',{}).get('kind')=='reservation-rejected' and bool(result['retained_owners'])
    return bool(control)


def _check_joint_replay(result,value,case):
    if result.get('schema')!='osr-line-capacity-joint-replay/1' or result.get('physical_output_authorised') is not False or result.get('whole_line_capacity_accepted') is not False:raise ValueError('joint station scope differs')
    expected=case in {'joint-600','joint-replay','joint-order-commit','joint-conflicting-launch'}
    control=result.get('study_pass') is expected and type(result.get('frames_executed')) is int and 0<result['frames_executed']<=len(value['frames'])
    control&=result.get('durable_event_replay_equal') is True and result.get('journal_records',0)>0 and len(result.get('journal_sha256',[]))==32
    if case not in {'joint-partial-commit','joint-prepared-restart'}:control&=result.get('committed_launches',0)>0 and result.get('individual_clear_bypass_rejected') is True and result.get('partial_tail_clear_rejected') is True
    if expected:
        control&=result.get('failure') is None and result['frames_executed']==len(value['frames']) and result.get('station_protection_checks',0)>0
    if case in {'joint-600','joint-replay'}:control&=result['maximum_active_trains']==3 and result['cleared_launches']>=3 and result['minimum_train_separation_mm']>0
    failure=result.get('failure') or {}
    if case=='joint-180':control&=failure.get('kind')=='station-prepare-rejected' and failure.get('atomic_no_partial_allocation') is True and failure.get('stopped_before_departure') is True
    if case=='joint-partial-commit':control&=failure.get('kind')=='station-commit-rejected' and failure.get('prepared_locks_retained') is True and failure.get('arrival_not_committed') is True
    if case=='joint-prepared-restart':control&=failure.get('kind')=='station-prepared-restart-held' and failure.get('prepared_locks_retained') is True and failure.get('commit_rejected_after_restart') is True and result.get('checkpoint_verified') is True
    if case=='joint-order-commit':control&=result.get('commit_before_prepare_rejected') is True
    if case=='joint-conflicting-launch':control&=result.get('conflicting_launch_rejected') is True
    if case=='joint-replay':control&=result.get('checkpoint_verified') is True and len(result.get('checkpoint_sha256',[]))==32
    if case=='joint-restart':control&=failure.get('kind')=='station-restart-held' and result.get('checkpoint_verified') is True and result.get('restart_arrival_protected') is True
    if case=='joint-stale-arrival':control&=failure.get('kind')=='station-stale-arrival-held' and result.get('stale_arrival_held') is True
    if case=='joint-receiving-fault':control&=failure.get('kind')=='station-receiver-held' and failure.get('arrival_protected') is True and failure.get('phase')=='Held'
    return bool(control)


def _check_contract_replay(result,value,case):
    if result.get('schema')!='osr-progressive-departure-replay/1' or result.get('protocol')!='osr-progressive-departure/1' or result.get('physical_output_authorised') is not False or result.get('whole_line_capacity_accepted') is not False:raise ValueError('progressive candidate scope differs')
    control=result.get('study_pass') is (case in PASS_CASES) and type(result.get('frames_executed')) is int and 0<result['frames_executed']<=len(value['frames'])
    control&=result.get('durable_event_replay_equal') is True and result.get('journal_records',0)>0 and len(result.get('journal_sha256',[]))==32
    if case in PASS_CASES:control&=result.get('failure') is None and result['frames_executed']==len(value['frames']) and result['committed_departures']>0
    if case in {'contract-180','contract-journal'}:control&=result['maximum_active_trains']==3 and result['committed_departures']>=3 and result['stopped_arrivals']>=3 and result['full_tail_releases']>0 and result['minimum_train_separation_mm']>0 and result['minimum_stopping_authority_margin_mm']>=0
    if case=='contract-closed-arrival':
        control&=(result.get('failure') or {}).get('kind')=='progressive-arrival-authority-held' and result.get('braking_plant_pass') is True and len(result.get('braking_plants',[]))>0
        configs={t['config']['owner']['train']:t['config'] for t in value['model']['trains']}
        for plant in result.get('braking_plants',[]):control&=plant['initial_hold_margin_mm']>=0 and plant['final_speed_m_s']==0 and plant['final_front_m']*1000+configs[plant['train']]['stop_margin_mm']<=plant['owned_authority_end_mm'] and len(plant['trace'])>1
    if case in {'contract-stale-ready','contract-brake-loss','contract-gap-fault','contract-integrity-loss','contract-rollback'}:control&=(result.get('failure') or {}).get('kind')=='progressive-evidence-held' and any(d['phase']=='Held' and d['stop_required'] for d in result['retained_contracts']) and bool(result['retained_owners'])
    if case=='contract-journal':control&=result.get('snapshot_restore_fenced') is True and len(result.get('snapshot_sha256',[]))==32
    if case in {'contract-prepared-restart','contract-committed-restart'}:control&=result.get('snapshot_restore_fenced') is True and result.get('restart_owners_retained') is True and any(d['phase']=='Held' for d in result['retained_contracts'])
    if case=='contract-order-commit':control&=result.get('commit_order_rejected') is True
    if case=='contract-conflicting-prepare':control&=result.get('conflicting_prepare_rejected') is True
    if case=='contract-partial-commit':control&=result.get('partial_commit_fenced') is True and result['committed_departures']==0 and bool(result['retained_owners'])
    return bool(control)


def _contract_scope():return dict(protocol='osr-progressive-departure/1',implementation='crates/osr-interlocking/src/progressive.rs',remote_arrival_reserved_at_departure=False,legacy_station_launch_changed=False,restored_snapshot_can_authorise_motion=False,snapshot_reconciliation_implemented=False,station_motor_receiver_contract_integrated=False)

def _open_gates():return ['measured/degraded independent brake curves and stopping-time distributions','qualified detector and train-integrity coverage, latency and clock error','candidate finite-authority protocol composed with station motor/receiver and onboard brake/support command interfaces','durable multi-controller handover, authenticated installed event persistence and restart/reconciliation; restored snapshots cannot resume','perturbed dwell, failed mid-coast recovery, junction/passenger demand, turnbacks and repeated full-line cycles','real-time timing, fail-safe output and physical system acceptance']


def study():
    before=sources();binary,execution=compile_replay();binary_sha=execution['binary_sha256'];runs=[];transcripts=[]
    execution['progressive_api_tests']=_command(API_TEST);_api_tests(execution['progressive_api_tests'])
    for mode in ('urban','suburban'):
        for case in ALL_CASES:
            run,entry=replay(binary,mode,case);runs.append(run);transcripts.append(dict(mode=mode,case=case,**entry))
    if sources()!=before or digest(binary.read_bytes())!=binary_sha:raise ValueError('capacity sources or executable changed during study')
    result=dict(schema='osr-line-capacity-study/1',source_sha256=before,runs=runs,executed_controls_pass=all(r['control_pass'] for r in runs),study_pass=False,
        capacity_candidate_only=True,whole_line_capacity_accepted=False,city_default_changed=False,
        assumptions=['one persistent local controller domain and at most32 exclusive resources','three ideal-profile trains; only the declared finite horizon is simulated','synthetic independent detector, whole-consist integrity and full-tail clearance assertions','constant independent emergency brake available throughout unpowered coasting; no measured curve','maximum acceleration continues during reaction, observation age and next sample; constant deceleration then','flat/adverse scalar grade hypotheses; no gradient transition or brake jerk build-up beyond reaction allowance','explicit closed-arrival plant accelerates over reaction then brakes at the assumed minimum, inside previously owned authority; other active trains continue until the finite stopping endpoint','ordinary demand/energy screens remain in corridor and operating_plan; no city-cost or headway promotion'],
        progressive_contract=_contract_scope(),
        open_gates=_open_gates(),
        references=[dict(title='ERA Introduction to ETCS braking curves',url='https://www.era.europa.eu/system/files/2022-11/Introduction%20to%20ETCS%20braking%20curves.pdf',use='Braking envelopes depend on train/track data and reaction; this simple hypothesis is not an ETCS implementation or compliance claim')],**model.FLAGS)
    return result,dict(**execution,runs=transcripts)


def _api_tests(entry):
    names=set(re.findall(r'^test progressive::tests::([A-Za-z0-9_]+) \.\.\. ok$',entry.get('stdout',''),re.M))
    summaries=re.findall(r'^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',entry.get('stdout',''),re.M)
    if entry.get('command')!=API_TEST or entry.get('returncode')!=0 or names!=API_TEST_NAMES or len(summaries)!=1 or summaries[0][:4]!=(str(len(API_TEST_NAMES)),'0','0','0'):raise ValueError('actual progressive API controls incomplete')


def _overview(result):
    rows=[];height=140+28*len(result['runs'])
    for j,r in enumerate(result['runs']):
        p=r['replay'];status='PASS expected' if r['control_pass'] else 'CONTROL FAILED';schedule='schedule continues' if p['study_pass'] else 'schedule held: '+p['failure']['kind'];rows.append(f'<text x="20" y="{70+j*28}" font-size="15">{r["mode"]} / {r["case"]}: {status}; {schedule}; {p["frames_executed"]} frames</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="{height}" viewBox="0 0 1120 {height}"><rect width="1120" height="{height}" fill="#f4f8fb"/><g font-family="sans-serif" fill="#152f43"><text x="20" y="32" font-size="23">Three-train fixed-block numerical capacity study — unapproved</text>'+''.join(rows)+f'<text x="20" y="{height-30}" font-size="15">Synthetic full-tail detectors, assumed brake, one local domain; no city default or safety acceptance.</text></g></svg>\n').encode()


def readme(result):
    return '\n'.join(['# Three-train fixed-block capacity study','', '[Raw study](study.json.gz) · [Actual compiler, API-test and replay transcript](execution.json.gz) · [Overview](overview.svg) · [Source/payload receipt](manifest.json)','',
        f'{2*len(ALL_CASES)} actual Rust mode/case replays and {len(API_TEST_NAMES)} named API regressions are retained. Three six-car trains follow exact current urban2km/140s and suburban5km/375s profiles through repeated fixed-line stations. Every train remains within the finite model; none disappears at an ideal sink.','',
        'The generic fixed-block study compares180s departures, exclusive one-leg retention, delayed tail clearance, stale sensing, occupied arrivals after extended dwell, coarser blocks and adverse brake/reaction/grade assumptions. Adverse braking holds the longitudinal trace fixed and changes only its braking-envelope hypothesis. These generic fault runs stop at the first rejected continuation.','',
        'The legacy joint study executes the actual StationLaunch prepare/commit/hold/complete-consist-clear API alongside progressive ordinary blocks. The true receiving berth and75m overlap stay committed from departure. Three-train600s profiles pass;180s follower launches are rejected while stopped, without partial allocation. Prepared/committed snapshots, event-order, conflicting launch, partial clearance, stale receiving evidence and receiver loss are executed. The legacy protocol is unchanged.','',
        '`osr-progressive-departure/1` is a separate Rust candidate contract. It atomically prepares initial stopping authority at a declared stop and commits while stopped. The remote arrival berth is acquired later, before the stopping envelope reaches it. Fresh brake, support, gap, integrity, identified position, sequence, occupied-body detector and local speed-limit checks gate extensions. This candidate accepts only uniform speed limits on each fixed route; nonuniform routes and live speed restrictions are rejected or held because transition curves are unimplemented. Traversed releases require the exact latest validated pose and complete-tail geometry; unused forward withdrawals require an explicitly proved stopped state. An old contract cannot release its successor’s resources.','',
        'The new candidate executes three-train180s profiles. In the closed-arrival controls, extension is denied and the previous authority is retained. An explicit longitudinal plant applies worst assumed acceleration over reaction time, then the minimum independent brake until stopped. It gives no additional next-sample credit after denial. Other active trains continue to the finite fault-study endpoint. Raw stop traces and owned authority bounds are retained. This assumes that an independent brake works anywhere along an unpowered coast; measured brake evidence and failed-stop rescue remain open.','',
        '**Restoration stays fenced.** A deserialised progressive domain cannot authorise movement, commit or prepare a new departure. Restart retains owners and the fence. Snapshot reconciliation and resumption are unimplemented; a fresh constructor must not bypass a retained journal or an unresolved restart. Positive journal replays are offline deterministic-fold checks, and retained source/request data can reproduce their event streams. Serde consistency does not authenticate a snapshot or prove an installed controller flushed events durably. Authenticated persistence, consensus, protection-adapter qualification and safe recovery are caller/system responsibilities still open.','',
        'The scalar stopping horizon includes reaction, observation age, next sample, clock error, acceleration, velocity/position error, grade and a stop margin; it gives no credit for a leader moving or braking. [ERA braking-curve background](https://www.era.europa.eu/system/files/2022-11/Introduction%20to%20ETCS%20braking%20curves.pdf) informs the distinction between a hypothesis and a measured train/track braking curve. This is not an ETCS implementation or compliance claim.','',
        '**Scope:** bounded local software/plant research. The candidate is not composed with live station motor/receiver, support or brake outputs. Measured maps, degraded brakes, detectors, physical integrity, distributed authority, authenticated storage, recovery, complete-line disturbed cycles and hardware acceptance remain open. City headways and costs are unchanged. No manufacturing or physical release is claimed.',''])


def publish(output=OUTPUT):
    result,execution=study()
    if not result['executed_controls_pass']:raise ValueError('capacity controls failed; no publication')
    note=readme(result)
    payload={'study.json.gz':gzip.compress(encoded(result),mtime=0),'execution.json.gz':gzip.compress(encoded(execution),mtime=0),'overview.svg':_overview(result),'README.md':note.encode()}
    output=Path(output)
    if output.is_symlink():raise ValueError('ordinary capacity output required')
    output.mkdir(parents=True,exist_ok=True)
    if {p.name for p in output.iterdir()}-FILES-{'manifest.json'} or any(p.is_symlink() for p in output.iterdir()):raise ValueError('capacity output inventory differs')
    for name,data in payload.items():
        if len(data)>MAX_FILE:raise ValueError('bounded capacity publication required')
        pending=output/(name+'.pending');pending.write_bytes(data);pending.replace(output/name)
    manifest=dict(schema='osr-line-capacity-publication/1',source_sha256=result['source_sha256'],files_sha256={n:digest(v) for n,v in payload.items()},study_pass=False,executed_controls_pass=True,whole_line_capacity_accepted=False,city_default_changed=False,**model.FLAGS)
    pending=output/'manifest.json.pending';pending.write_bytes(encoded(manifest));pending.replace(output/'manifest.json')
    return verify(output)


def _read(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size>MAX_FILE:raise ValueError('bounded ordinary capacity payload required')
    return path.read_bytes()


def _inflate(raw):
    import io
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as f:value=f.read(MAX_RAW+1)
    if len(value)>MAX_RAW:raise ValueError('bounded capacity raw evidence required')
    return json.loads(value)


def verify(output=OUTPUT):
    output=Path(output)
    if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()}!=FILES|{'manifest.json'}:raise ValueError('exact capacity packet inventory required')
    manifest=json.loads(_read(output/'manifest.json'))
    if manifest.get('schema')!='osr-line-capacity-publication/1' or manifest.get('source_sha256')!=sources() or set(manifest.get('files_sha256',{}))!=FILES:raise ValueError('capacity source/payload inventory differs')
    payload={name:_read(output/name) for name in FILES}
    if any(digest(data)!=manifest['files_sha256'][name] for name,data in payload.items()):raise ValueError('capacity payload checksum differs')
    result=_inflate(payload['study.json.gz']);execution=_inflate(payload['execution.json.gz'])
    for value in (manifest,result):
        if any(value.get(flag) is not False for flag in model.FLAGS) or value.get('whole_line_capacity_accepted') is not False or value.get('city_default_changed') is not False or value.get('study_pass') is not False:raise ValueError('capacity authority exceeds provisional scope')
    if result.get('progressive_contract')!=_contract_scope() or result.get('open_gates')!=_open_gates():raise ValueError('capacity contract scope or open gates differ')
    if payload['README.md']!=readme(result).encode():raise ValueError('capacity presentation differs from retained results')
    if result.get('source_sha256')!=manifest['source_sha256'] or result.get('executed_controls_pass') is not True or len(result.get('runs',[]))!=2*len(ALL_CASES):raise ValueError('capacity study evidence incomplete')
    if {(r['mode'],r['case']) for r in result['runs']}!={(m,c) for m in ('urban','suburban') for c in ALL_CASES}:raise ValueError('capacity mode/case coverage differs')
    if execution.get('build',{}).get('command')!=BUILD or execution['build']['returncode']!=0 or execution.get('compiler',{}).get('command')!=['rustc','--version'] or execution['compiler']['returncode']!=0:raise ValueError('actual capacity build transcript required')
    _api_tests(execution.get('progressive_api_tests',{}))
    artifacts=[v['executable'] for line in execution['build']['stdout'].splitlines() if (v:=json.loads(line)).get('reason')=='compiler-artifact' and v.get('target',{}).get('name')=='line_capacity_replay' and v.get('executable')]
    if len(artifacts)!=1 or not execution['compiler']['stdout'].startswith('rustc ') or not isinstance(execution.get('binary_sha256'),str) or len(execution['binary_sha256'])!=64 or any(v not in '0123456789abcdef' for v in execution['binary_sha256']):raise ValueError('capacity compiler/artifact identity differs')
    entries={(r['mode'],r['case']):r for r in execution.get('runs',[])}
    if len(entries)!=2*len(ALL_CASES):raise ValueError('complete actual capacity replay transcript required')
    for run in result['runs']:
        entry=entries[run['mode'],run['case']]
        if entry.get('command')!=[artifacts[0]] or entry.get('returncode')!=0 or json.loads(entry['stdout'])!=run['replay'] or run.get('control_pass') is not True:raise ValueError('capacity replay/transcript differs')
        # Source-bound requests are regenerated, not trusted from result claims.
        value,meta=request(run['mode'],run['case'])
        if digest(encoded(value))!=run['request_sha256'] or len(value['frames'])!=run['request_frames'] or any(run.get(k)!=v for k,v in meta.items()):raise ValueError('capacity input identity differs')
        if not _check_replay(run['replay'],value,run['case']) or run.get('expected_schedule_pass') is not (run['case'] in PASS_CASES):raise ValueError('capacity claimed control outcome differs')
    if payload['overview.svg']!=_overview(result) or payload['README.md']!=readme(result).encode():raise ValueError('capacity presentation differs from retained results')
    return dict(schema='osr-line-capacity-verification/1',executed_controls_pass=True,runs=2*len(ALL_CASES),whole_line_capacity_accepted=False,city_default_changed=False,study_pass=False,source_files=len(manifest['source_sha256']),**model.FLAGS)


def read_summary(output=OUTPUT):
    verification=verify(output);value=_inflate(_read(Path(output)/'study.json.gz'))
    by={(r['mode'],r['case']):r['replay'] for r in value['runs']}
    return dict(**verification,scope='Executed legacy StationLaunch composition and separate finite-authority departure candidate; live motor/brake interfaces and physical acceptance open',
        profiles=[dict(mode=mode,headway_s=180.,nominal=next(dict(frames=r['replay']['frames_executed'],full_tail_releases=r['replay']['release_count'],
            stopped_forward_withdrawals=r['replay']['stopped_forward_withdrawals'],minimum_stopping_margin_m=r['replay']['minimum_stopping_authority_margin_mm']/1000,
            maximum_active_trains=r['replay']['maximum_active_trains']) for r in value['runs'] if r['mode']==mode and r['case']=='pipeline')) for mode in ('urban','suburban')],
        protection_controls=sum(not r['expected_schedule_pass'] for r in value['runs']),
        legacy_station_launch=dict(runs=2*len(JOINT_CASES),headway_180s_rejected_while_stopped=all(by[m,'joint-180']['failure']['stopped_before_departure'] for m in ('urban','suburban')),headway_600s_executed_pass=all(by[m,'joint-600']['study_pass'] for m in ('urban','suburban')),legacy_contract_changed=False),
        progressive_departure=dict(protocol='osr-progressive-departure/1',runs=2*len(CONTRACT_CASES),executed_api_tests=len(API_TEST_NAMES),restored_snapshot_can_authorise_motion=False,reconciliation_resumption_implemented=False,
            profiles=[dict(mode=m,headway_s=180.,committed_departures=by[m,'contract-180']['committed_departures'],stopped_arrivals=by[m,'contract-180']['stopped_arrivals'],full_tail_releases=by[m,'contract-180']['full_tail_releases'],minimum_stopping_margin_m=by[m,'contract-180']['minimum_stopping_authority_margin_mm']/1000,
                closed_arrival_brake_plant_pass=by[m,'contract-closed-arrival']['braking_plant_pass'],hold_stopping_margin_m=by[m,'contract-closed-arrival']['failure']['immediate_stopping_margin_mm']/1000) for m in ('urban','suburban')]),open_gates=value['open_gates'])
