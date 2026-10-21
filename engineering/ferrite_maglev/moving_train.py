"""Moving six-car ideal-force twin with actual Rust support controllers.

Repeated linear pinned spans, independent rigid car heave/roll/pitch, and an
integrated longitudinal spring/damper chain. Electromagnetics, flexible bodies,
beam torsion, soil, contacts, shared-field phase authority and hardware timing
remain unqualified. Numerical controls do not confer engineering acceptance.
"""
from dataclasses import asdict
from hashlib import sha256
import gzip
import json
import math
import os
from pathlib import Path
import platform
import selectors
import subprocess
import tempfile
import tomllib

import numpy as np
import scipy
from scipy.linalg import expm

from . import configuration,coupled,geometry,model,station

ROOT=model.ROOT
INPUT=Path(__file__).with_name('moving-train.toml')
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/moving-train'
FILES={'result.json.gz','overview.png','moving-train.mp4','visual-receipt.json','README.md'}
BUILD=['cargo','build','--locked','--release','-p','osr-maglev-control','--example','moving_train_bridge','--message-format=json']
MAX_RAW=128*1024*1024
CARS=6
X=coupled.MODULE_X_M.copy();Y=coupled.MODULE_Y_M.copy()
FIT=np.column_stack((np.ones(24),-Y,X))


def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def digest(value):return sha256(value).hexdigest()


def load():
    a=tomllib.loads(INPUT.read_text());cfg=configuration.selected()
    if a.get('schema')!='osr-moving-train-assumptions/1' or a.get('cars')!=6:raise ValueError('six-car moving study schema required')
    bounds={
        'car_mass_kg':(5000,100000),'body_length_m':(8,30),'coupling_gap_m':(0,2),
        'inertia_roll_kg_m2':(1000,1e8),'inertia_pitch_kg_m2':(10000,1e9),
        'coupler_stiffness_n_m':(1e5,1e8),'coupler_damping_n_s_m':(0,1e7),'coupler_stroke_screen_m':(.001,.5),
        'step_s':(.0005,.01),'runtime_s':(70,150),'acceleration_m_s2':(.1,2),'deceleration_m_s2':(.1,2),'jerk_m_s3':(.1,2),
        'candidate_runtime_s':(70,150),'candidate_acceleration_m_s2':(.1,2),'candidate_coupler_stiffness_n_m':(1e5,1e8),
        'settle_s':(0,10),'gap_target_m':(.001,.03),'gap_minimum_m':(.0001,.02),'gap_maximum_m':(.002,.05),
        'sensor_bias_m':(-.002,.002),
        'sensor_bias_screen_m':(.0001,.001),'beam_modulus_adverse_factor':(.5,.99),
        'trace_interval_s':(.02,1),'beam_elements':(4,100),'beam_modes':(1,12),'beam_damping_ratio':(0,.1),
        'guideway_span_m':(15,40),'beam_modulus_pa':(1e9,1e11),'beam_vertical_inertia_m4':(.01,2),
        'guideway_line_mass_kg_m':(100,10000),'refinement_start_s':(0,88),'refinement_duration_s':(.1,5),
        'refinement_gap_tolerance_m':(.00001,.002),'visual_vertical_amplification':(1,100),'movie_frames':(10,200),'movie_fps':(5,30)}
    for key,(lo,hi) in bounds.items():
        value=a[key]
        if type(value) not in (int,float) or not math.isfinite(value) or not lo<=value<=hi:raise ValueError('finite bounded moving input: '+key)
    if any(type(a[k]) is not int for k in ('cars','beam_elements','beam_modes','movie_frames','movie_fps')):raise ValueError('integer moving counts required')
    if not a['gap_minimum_m']<a['gap_target_m']<a['gap_maximum_m']:raise ValueError('ordered moving gap limits required')
    if a['beam_modes']>=2*a['beam_elements'] or round(a['step_s']*1e9)!=a['step_s']*1e9:raise ValueError('bounded modes/integer nanosecond step required')
    # The selected formation and section, rather than a disconnected copied
    # quantity, define the published reference case.
    cv=cfg.civil;primary=configuration.document(model.INPUT)
    a.update(configuration_revision=cfg.revision,car_mass_kg=cfg.vehicle['baseline_tare_kg_per_car']+cfg.vehicle['payload_aw3_kg_per_car'],
        body_length_m=cfg.formation.body_length_m,coupling_gap_m=cfg.formation.coupling_gap_assumption_m,
        guideway_span_m=cv.span_m,beam_vertical_inertia_m4=model.section(cv.width_m,cv.depth_m,cv.web_m,cv.flange_m)['vertical_i_m4'],
        guideway_line_mass_kg_m=geometry.guideway_quantities(cv.span_m)['total_line_mass_kg_m'],
        beam_modulus_pa=primary['civil']['narrow_box_screen']['gross_uncracked_concrete_e_pa'],
        runtime_s=primary['vehicle']['runtime_reference_seconds'],acceleration_m_s2=primary['vehicle']['maximum_initial_acceleration_m_s2'],
        coupler_stiffness_n_m=primary['vehicle']['coupler_stiffness_assumption_n_m'],
        beam_section_m=dict(width=cv.width_m,depth=cv.depth_m,web=cv.web_m,flange=cv.flange_m))
    return a


def sources():
    paths={Path(__file__),INPUT,ROOT/'engineering/analysis/tests/test_ferrite_maglev_moving_train.py',
        ROOT/'crates/osr-maglev-control/examples/moving_train_bridge.rs',*configuration.source_paths()}
    paths.update(ROOT/name for name in coupled.sources())
    paths.update(ROOT/name for name in station.sources())
    paths.update((ROOT/'crates/osr-maglev-control/src').glob('*.rs'))
    return {p.relative_to(ROOT).as_posix():digest(p.read_bytes()) for p in sorted(paths)}


def trajectory_at(t,time_s):
    """Evaluate exact constant-jerk segments and the same analytic free coast."""
    if not t['study_pass'] or not math.isfinite(time_s) or not 0<=time_s<=t['inputs']['runtime_s']+1e-8:raise ValueError('feasible bounded station trajectory required')
    lt=t['phases']['launch']['duration_s'];ct=t['phases']['coast']['duration_s']
    if time_s<lt:phase='launch';local=time_s;offset=0.;segments=t['segments']['launch']
    elif time_s<lt+ct:
        mass=t['inputs']['train_mass_kg'];cars=t['inputs']['cars'];r=t['resistance'];constant=r['constant_n_per_car']*cars+mass*station.G*t['inputs']['grade']
        speed,distance,_=station._coast(t['launch_speed_kmh']/3.6,time_s-lt,mass,constant,r['quadratic_n_per_car_per_m_s_squared']*cars)
        acceleration=-(constant+r['quadratic_n_per_car_per_m_s_squared']*cars*speed**2)/mass
        return dict(time_s=time_s,position_m=t['phases']['launch']['distance_m']+distance,speed_m_s=speed,acceleration_m_s2=acceleration,phase='coast',motor_force_n=0.)
    else:phase='braking';local=min(time_s-lt-ct,t['phases']['braking']['duration_s']);offset=t['phases']['launch']['distance_m']+t['phases']['coast']['distance_m'];segments=t['segments']['braking']
    segment=next((s for s in segments if local<=s['start_time_s']+s['duration_s']+1e-10),segments[-1])
    tau=max(0.,min(segment['duration_s'],local-segment['start_time_s']))
    speed,acceleration,dx=station._step(segment['start_speed_m_s'],segment['start_acceleration_m_s2'],segment['jerk_m_s3'],tau)
    mass=t['inputs']['train_mass_kg'];cars=t['inputs']['cars'];r=t['resistance']
    force=mass*acceleration+cars*(r['constant_n_per_car']+r['quadratic_n_per_car_per_m_s_squared']*speed**2)+mass*station.G*t['inputs']['grade']
    return dict(time_s=time_s,position_m=offset+segment['start_position_m']+dx,speed_m_s=max(0.,speed),acceleration_m_s2=acceleration,phase=phase,motor_force_n=force)


class MovingGuideway:
    """One FE/modal basis reused on distinct dynamically loaded pinned spans."""
    def __init__(self,a,distance_m=1000.,step_s=None):
        self.a=a;self.dt=a['step_s'] if step_s is None else step_s;self.span=a['guideway_span_m']
        self.assumptions=coupled.BeamAssumptions(young_pa=a['beam_modulus_pa'],second_moment_m4=a['beam_vertical_inertia_m4'],
            span_m=self.span,line_mass_kg_m=a['guideway_line_mass_kg_m'],elements=a['beam_elements'],retained_modes=a['beam_modes'],damping_ratio=a['beam_damping_ratio'])
        self.template=coupled.FlexibleGuideway(self.assumptions)
        self.origin=-math.ceil((CARS*(a['body_length_m']+a['coupling_gap_m'])+2*self.span)/self.span)*self.span
        self.count=math.ceil((distance_m+2*self.span-self.origin)/self.span)
        if self.count>800:raise ValueError('bounded repeated-span count required')
        self.omega=self.template.omega_rad_s
        self.phi=np.zeros((2*(a['beam_elements']+1),a['beam_modes']));self.phi[self.template.free]=self.template.phi
        self.q=np.zeros((self.count,a['beam_modes']));self.velocity=self.q.copy()
        matrices=[];drives=[]
        for omega in self.omega:
            matrix=np.array([[0.,1.],[-omega**2,-2*a['beam_damping_ratio']*omega]])
            transition=expm(matrix*self.dt);matrices.append(transition)
            drives.append(np.linalg.solve(matrix,(transition-np.eye(2))@np.array([0.,1.])))
        self.transition=np.array(matrices);self.drive=np.array(drives)

    def sample(self,positions):
        positions=np.asarray(positions,dtype=float)
        if not np.all(np.isfinite(positions)):raise ValueError('finite moving attachment positions required')
        relative=positions-self.origin;indices=np.floor(relative/self.span).astype(int)
        if np.any(indices<0) or np.any(indices>=self.count):raise ValueError('moving attachment outside retained guideway')
        local=relative-indices*self.span;h=self.span/self.a['beam_elements']
        e=np.minimum((local/h).astype(int),self.a['beam_elements']-1);r=(local-e*h)/h
        coeff=np.column_stack((1-3*r*r+2*r**3,h*(r-2*r*r+r**3),3*r*r-2*r**3,h*(-r*r+r**3)))
        dofs=2*e[:,None]+np.arange(4)[None,:]
        shape=np.einsum('ij,ijk->ik',coeff,self.phi[dofs])
        return indices,shape

    def displacement(self,positions):
        indices,shape=self.sample(positions)
        return np.einsum('ij,ij->i',shape,self.q[indices])

    def project(self,positions,forces):
        forces=np.asarray(forces,dtype=float);indices,shape=self.sample(positions)
        if forces.shape!=(len(indices),) or not np.all(np.isfinite(forces)) or np.max(np.abs(forces))>1e6:raise ValueError('bounded matching moving forces required')
        projected=np.zeros_like(self.q);np.add.at(projected,indices,shape*forces[:,None])
        point_power=float(forces@np.einsum('ij,ij->i',shape,self.velocity[indices]))
        modal_power=float(np.sum(projected*self.velocity))
        error=abs(point_power-modal_power)/max(1.,abs(point_power),abs(modal_power))
        return projected,error

    def initialise_static(self,positions,forces):
        projected,_=self.project(positions,forces);self.q=projected/self.omega**2;self.velocity[:]=0.

    def advance(self,positions,forces):
        projected,error=self.project(positions,forces)
        old=np.stack((self.q,self.velocity),axis=2)
        new=np.einsum('mij,smj->smi',self.transition,old)+self.drive[None,:,:]*projected[:,:,None]
        self.q=new[:,:,0];self.velocity=new[:,:,1]
        return error


class CouplerChain:
    """Implicit-midpoint linear chain; its internal forces conserve momentum."""
    def __init__(self,mass,stiffness,damping,step_s,cars=6):
        self.mass=mass;self.k=stiffness;self.c=damping;self.dt=step_s
        self.incidence=np.zeros((cars-1,cars))
        for i in range(cars-1):self.incidence[i,i]=1;self.incidence[i,i+1]=-1
        self.lap=self.incidence.T@self.incidence;self.u=np.zeros(cars);self.velocity=np.zeros(cars)
        d=self.dt
        self.inverse=np.linalg.inv(np.eye(cars)+(d*d*stiffness/(4*mass)+d*damping/(2*mass))*self.lap)
        self.right=np.eye(cars)-(d*d*stiffness/(4*mass)+d*damping/(2*mass))*self.lap

    def energy(self):return float(.5*self.mass*self.velocity@self.velocity+.5*self.k*np.sum((self.incidence@self.u)**2))

    def step(self,external_relative_n):
        external=np.asarray(external_relative_n,dtype=float)
        if external.shape!=self.u.shape or not np.all(np.isfinite(external)):raise ValueError('finite chain force vector required')
        initial=self.energy();old_u=self.u.copy();old_v=self.velocity.copy();d=self.dt
        new_v=self.inverse@(self.right@old_v+d*(external/self.mass-self.k/self.mass*(self.lap@old_u)))
        midpoint_velocity=(old_v+new_v)/2;self.u=old_u+d*midpoint_velocity;self.velocity=new_v
        extension=self.incidence@((old_u+self.u)/2);speed=self.incidence@midpoint_velocity
        pair=-self.k*extension-self.c*speed;forces=self.incidence.T@pair
        damping=float(self.c*(speed@speed)*d);work=float(external@(self.u-old_u))
        residual=self.energy()-initial-work+damping
        return dict(internal_net_force_n=float(forces.sum()),energy_residual_j=residual,
            damping_j=damping,peak_coupler_force_n=float(np.max(np.abs(pair))),extension_m=(self.incidence@self.u).tolist())


class RustTrain:
    def __init__(self,executable,a,step_s):
        command=[str(executable),str(a['car_mass_kg']),str(round(step_s*1e9)),str(a['gap_target_m']),str(a['gap_minimum_m']),str(a['gap_maximum_m'])]
        self.process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1)
        self.selector=selectors.DefaultSelector();self.selector.register(self.process.stdout,selectors.EVENT_READ)

    def tick(self,sequence,gaps):
        values=np.asarray(gaps,dtype=float)
        if values.shape!=(6,24) or not np.all(np.isfinite(values)):raise ValueError('six finite car gap arrays required')
        self.process.stdin.write(str(sequence)+' '+' '.join(format(v,'.15e') for v in values.ravel())+'\n');self.process.stdin.flush()
        if not self.selector.select(15):raise RuntimeError('moving Rust bridge timeout')
        line=self.process.stdout.readline(16385);fields=line.split()
        if len(fields)!=6*28 or len(line)>16384:raise RuntimeError('moving Rust bridge rejected frame: '+line[:160])
        forces=[];stopped=False
        for car in range(6):
            block=fields[car*28:(car+1)*28]
            if block[0]!='true' or block[2]!='false' or abs(float(block[3]))>1e-6:raise RuntimeError('moving Rust force allocation/authority failed')
            stopped|=block[1]=='true';forces.append([float(v) for v in block[4:]])
        result=np.asarray(forces)
        if not np.all(np.isfinite(result)):raise RuntimeError('nonfinite moving Rust force')
        return result,stopped

    def close(self):
        self.selector.close();self.process.stdin.close()
        try:self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:self.process.kill();self.process.wait(timeout=5)
        self.process.stdout.close()

    def __enter__(self):return self
    def __exit__(self,*_):self.close()


def build_bridge():
    built=subprocess.run(BUILD,cwd=ROOT,check=True,capture_output=True,text=True,timeout=180)
    artifacts=[json.loads(line) for line in built.stdout.splitlines()]
    paths=[Path(v['executable']) for v in artifacts if v.get('reason')=='compiler-artifact' and v.get('target',{}).get('name')=='moving_train_bridge' and v.get('executable')]
    if len(paths)!=1 or not paths[0].is_file():raise ValueError('actual moving-train bridge compiler artifact required')
    compiler=subprocess.run(['rustc','--version'],cwd=ROOT,check=True,capture_output=True,text=True,timeout=30).stdout.strip()
    return paths[0],dict(build_command=BUILD,rustc=compiler,binary_sha256=digest(paths[0].read_bytes()))


def simulate(executable,*,assumptions=None,start_time_s=0.,duration_s=None,step_s=None,feedback=True,profile=None):
    """Actual six-car controller reactions on moving, independently loaded spans.

    The aggregate reference is prescribed by station.trajectory; relative car
    positions/velocities and coupler loads are integrated. Independent ideal
    per-car thrust proportional to motor overlap is an unvalidated hypothesis.
    """
    a=dict(load() if assumptions is None else assumptions);dt=a['step_s'] if step_s is None else step_s
    sampler=trajectory_at
    if profile is not None:
        from . import corridor
        if not profile.get('study_pass') or profile['inputs']['cars']!=6:raise ValueError('feasible exact six-car corridor profile required')
        a.update(runtime_s=profile['inputs']['runtime_s'],car_mass_kg=profile['inputs']['car_mass_kg'],
            operational_profile_sha256=digest(encoded(profile)))
        sampler=corridor.trajectory_at
    if (type(feedback) is not bool or not .0005<=dt<=.01 or not math.isfinite(dt)
            or not math.isfinite(a['sensor_bias_m']) or abs(a['sensor_bias_m'])>.002):raise ValueError('bounded explicit moving integration inputs required')
    route=station.load();motion=route['motion'];distance=motion['distance_m'] if profile is None else profile['inputs']['distance_m'];runtime=a['runtime_s']
    duration=runtime-start_time_s if duration_s is None else duration_s
    if not 0<=start_time_s<runtime or not .02<=duration<=runtime-start_time_s+1e-8:raise ValueError('bounded moving trajectory window required')
    t=profile if profile is not None else station.trajectory(distance_m=distance,runtime_s=runtime,car_mass_kg=a['car_mass_kg'],cars=6,
        acceleration=a['acceleration_m_s2'],deceleration=a['deceleration_m_s2'],jerk=a['jerk_m_s3'],record_trace=False)
    if not t['study_pass']:raise ValueError('station trajectory is not feasible under current assumptions')
    beam=MovingGuideway(a,distance,dt);mass=a['car_mass_kg'];weight=mass*station.G
    pitch=a['body_length_m']+a['coupling_gap_m'];offset=-a['body_length_m']/2-np.arange(6)*pitch
    chain=CouplerChain(mass,a['coupler_stiffness_n_m'],a['coupler_damping_n_s_m'],dt)
    initial=sampler(t,start_time_s)
    positions=((initial['position_m']+offset)[:,None]+X).ravel()
    beam.initialise_static(positions,np.full(144,weight/24))
    local=beam.displacement(positions).reshape(6,24)
    body=np.linalg.lstsq(FIT,local.T,rcond=None)[0].T;velocity=np.zeros((6,3))
    inertia=np.array([mass,a['inertia_roll_kg_m2'],a['inertia_pitch_kg_m2']])
    minimum=math.inf;maximum=-math.inf;peakforce=0.;peakbeam=0.;stop=False;failure=None
    peakstroke=0.;peakcoupler=0.;projection_error=0.;chain_balance=0.;net_internal=0.;max_phase_spread=0.
    motor_work=drag_work=damping_work=0.;trace=[];crossings=0;last_indices=None;sequence=0
    nsettle=round(a['settle_s']/dt);nmove=math.ceil(duration/dt)
    if nsettle+nmove>200000:raise ValueError('moving controller frame budget exceeded')
    if abs(nmove*dt-duration)>dt*.001:raise ValueError('duration must contain an integer number of moving steps')
    stride=max(1,round(a['trace_interval_s']/dt));potential0=chain.energy()
    r=t['resistance'];constant=r['constant_n_per_car'];quadratic=r['quadratic_n_per_car_per_m_s_squared']
    wavelength=2*route['vehicle']['pole_pitch_m']
    with RustTrain(executable,a,dt) as controller:
        for tick in range(nsettle+nmove):
            sequence+=1;moving=tick>=nsettle;time=start_time_s+max(0,tick-nsettle)*dt
            ref=sampler(t,min(runtime,time));next_ref=sampler(t,min(runtime,time+dt)) if moving else ref
            mid=sampler(t,min(runtime,time+dt/2)) if moving else ref
            centres=ref['position_m']+offset+chain.u
            positions=(centres[:,None]+X).ravel();indices,_=beam.sample(positions)
            if moving and last_indices is not None:crossings+=int(np.count_nonzero(indices!=last_indices))
            last_indices=indices.copy()
            physical_local=beam.displacement(positions).reshape(6,24)
            local=physical_local if feedback else np.zeros((6,24))
            physical_gaps=a['gap_target_m']+body@FIT.T-physical_local
            gaps=a['gap_target_m']+body@FIT.T-local+a['sensor_bias_m']
            try:forces,stopped=controller.tick(sequence,gaps)
            except RuntimeError as exc:
                if 'rejected frame' not in str(exc) and 'force allocation' not in str(exc):raise
                failure=str(exc);break
            stop|=stopped
            minimum=min(minimum,float(physical_gaps.min()));maximum=max(maximum,float(physical_gaps.max()));peakforce=max(peakforce,float(forces.max()))
            if minimum<a['gap_minimum_m'] or maximum>a['gap_maximum_m']:
                failure='independent physical gap outside envelope';break
            peakbeam=max(peakbeam,float(np.max(np.abs(beam.q@beam.phi.T))))
            generalized=np.column_stack((weight-forces.sum(axis=1),forces@Y,-forces@X))
            acceleration=generalized/inertia
            body+=velocity*dt+.5*acceleration*dt**2;velocity+=acceleration*dt
            midpoint_positions=positions.copy()
            if moving:
                centres_mid=mid['position_m']+offset+chain.u+chain.velocity*dt/2
                midpoint_positions=(centres_mid[:,None]+X).ravel()
                actual_speed=mid['speed_m_s']+chain.velocity
                resist=constant+quadratic*np.maximum(0.,actual_speed)**2
                total_force=0. if mid['phase']=='coast' else 6*mass*mid['acceleration_m_s2']+float(resist.sum())
                bounds=route['station'];start=bounds['winding_start_m'];end=bounds['winding_end_m']
                if profile is not None and mid['phase']!='coast':
                    zone=next(z for z in t['powered_zones'] if z['id']==mid['zone_id']);start=zone['start_m'];end=zone['end_m']
                elif mid['phase']=='braking':start+=distance;end+=distance
                band=route['vehicle']['magnetic_band_m_per_car']
                overlaps=np.maximum(0.,np.minimum(centres_mid+band/2,end)-np.maximum(centres_mid-band/2,start))
                if abs(total_force)>1. and overlaps.sum()<=0:failure='station force demanded without magnetic overlap';break
                applied=np.zeros(6) if mid['phase']=='coast' else total_force*overlaps/max(1e-12,float(overlaps.sum()))
                old_u=chain.u.copy()
                check=chain.step(applied-resist-mass*mid['acceleration_m_s2'])
                displacement=next_ref['position_m']-ref['position_m']+chain.u-old_u
                motor_work+=float(applied@displacement);drag_work+=float(resist@displacement);damping_work+=check['damping_j']
                chain_balance=max(chain_balance,abs(check['energy_residual_j']));net_internal=max(net_internal,abs(check['internal_net_force_n']))
                peakcoupler=max(peakcoupler,check['peak_coupler_force_n']);peakstroke=max(peakstroke,max(abs(v) for v in check['extension_m']))
                max_phase_spread=max(max_phase_spread,float(np.ptp(chain.u))*360/wavelength)
            projection_error=max(projection_error,beam.advance(midpoint_positions,forces.ravel()))
            if moving and (tick-nsettle)%stride==0 or tick==nsettle+nmove-1:
                retained_spans=list(range(beam.count))
                if profile is not None:
                    first=max(0,int((float(positions.min())-2*beam.span-beam.origin)//beam.span))
                    last=min(beam.count,int((float(positions.max())+2*beam.span-beam.origin)//beam.span)+1)
                    retained_spans=list(range(first,last))
                trace.append(dict(time_s=min(runtime,time+dt),phase=mid['phase'],front_reference_m=next_ref['position_m'],
                    car_centres_m=(next_ref['position_m']+offset+chain.u).tolist(),car_relative_longitudinal_m=chain.u.tolist(),
                    car_velocity_m_s=(next_ref['speed_m_s']+chain.velocity).tolist(),body_down_roll_pitch=body.tolist(),
                    minimum_gap_m=float(physical_gaps.min()),maximum_gap_m=float(physical_gaps.max()),
                    minimum_sensed_gap_m=float(gaps.min()),maximum_sensed_gap_m=float(gaps.max()),
                    coupler_extension_m=(chain.incidence@chain.u).tolist(),
                    beam_modal_span_indices=retained_spans,beam_modal_q=beam.q[retained_spans].tolist()))
    if minimum==math.inf:minimum=maximum=0.
    completed=max(0,sequence-nsettle-(1 if failure else 0))
    executed_duration=min(duration,completed*dt)
    final=sampler(t,min(runtime,start_time_s+executed_duration))
    final_kinetic=float(.5*mass*np.sum((final['speed_m_s']+chain.velocity)**2))
    initial_kinetic=.5*6*mass*initial['speed_m_s']**2
    spring=float(.5*chain.k*np.sum((chain.incidence@chain.u)**2))
    energy_residual=final_kinetic-initial_kinetic+spring-potential0-motor_work+drag_work+damping_work
    energy_relative=abs(energy_residual)/max(1.,abs(motor_work),abs(drag_work))
    passed=failure is None and not stop and a['gap_minimum_m']<=minimum<=maximum<=a['gap_maximum_m'] and peakstroke<=a['coupler_stroke_screen_m']
    return dict(schema='osr-moving-six-car-numerical/1',study_pass=bool(passed),failure=failure,
        configuration_revision=a['configuration_revision'],candidate_sha256=digest(encoded(a)),assumptions=a,
        formation=dict(cars=6,body_length_m=a['body_length_m'],coupling_gap_m=a['coupling_gap_m'],car_mass_kg=mass,
            nominal_body_length_m=6*a['body_length_m'],assumed_overall_length_m=6*a['body_length_m']+5*a['coupling_gap_m']),
        trajectory=t,window=dict(start_time_s=start_time_s,duration_s=duration,step_s=dt,settle_s=a['settle_s']),
        completed_moving_steps=completed,planned_moving_steps=nmove,executed_duration_s=executed_duration,
        minimum_gap_m=minimum,maximum_gap_m=maximum,peak_module_force_n=peakforce,stop_seen=bool(stop),
        peak_beam_displacement_m=peakbeam,peak_coupler_extension_m=peakstroke,peak_coupler_force_n=peakcoupler,
        maximum_longitudinal_relative_spread_m=float(max_phase_spread*wavelength/360),maximum_magnetic_phase_spread_degrees=max_phase_spread,
        load_projection_virtual_power_relative_error=projection_error,coupler_internal_net_force_max_n=net_internal,
        coupler_step_energy_residual_max_j=chain_balance,longitudinal_energy=dict(motor_signed_work_j=motor_work,
            drag_work_j=drag_work,coupler_damping_work_j=damping_work,final_spring_energy_j=spring,
            kinetic_change_j=final_kinetic-initial_kinetic,residual_j=energy_residual,relative_residual=energy_relative),
        module_span_boundary_crossings=crossings,guideway=dict(span_m=beam.span,origin_m=beam.origin,spans=beam.count,
            basis=asdict(beam.assumptions)),feedback_enabled=feedback,sensor_bias_m=a['sensor_bias_m'],trace=trace,
        physical_output_authorised=False,structural_acceptance=False,**model.FLAGS,
        scope='Moving repeated linear pinned spans, six rigid bodies and actual Rust vertical support allocation; aggregate prescribed station trajectory with integrated longitudinal spring/damper corrections and independently allocated ideal thrust. No measured magnetic map, shared-field phase feasibility, normal/thrust coupling, torsion/soil/joints/contact, flexible body or physical timing.')


def numerical_controls(a=None):
    a=load() if a is None else a
    baseline=MovingGuideway(a);static=coupled.static_benchmark(baseline.assumptions)
    x=np.linspace(-100.,100.,41);forces=np.linspace(100.,1000.,41)
    baseline.velocity[:]=np.random.default_rng(20261021).normal(0,1e-4,baseline.velocity.shape)
    _,work_error=baseline.project(x,forces)
    baseline.q[:]=1e-3
    boundary=float(abs(np.diff(baseline.displacement(np.array([25.-1e-8,25.+1e-8])))[0]))
    # Continuum simply-supported first-mode moving force, independently solved:
    # q''+w²q=A sin(Omega t), q(0)=q'(0)=0.
    moving=[]
    for dt in (.005,.0025):
        # A finer spatial mesh isolates temporal order from the production
        # 30-element FE interpolation/eigenvector error floor.
        aa=dict(a,beam_elements=60,beam_modes=1,beam_damping_ratio=0.)
        beam=MovingGuideway(aa,step_s=dt);speed=5.;force=100000.;duration=beam.span/speed
        index,_=beam.sample(np.array([beam.span/2]));sign=float(np.sign((beam.template.shape(np.array([beam.span/2]))@beam.template.phi[:,0]).item()))
        massline=aa['guideway_line_mass_kg_m'];omega=math.pi**2*math.sqrt(aa['beam_modulus_pa']*aa['beam_vertical_inertia_m4']/(massline*beam.span**4))
        forcing=force*math.sqrt(2/(massline*beam.span))*sign;frequency=math.pi*speed/beam.span
        errors=[];reference=[]
        for i in range(round(duration/dt)):
            beam.advance(np.array([speed*(i+.5)*dt]),np.array([force]));time=(i+1)*dt
            exact=forcing/(omega**2-frequency**2)*(math.sin(frequency*time)-frequency/omega*math.sin(omega*time))
            reference.append(exact);errors.append(abs(beam.q[int(index[0]),0]-exact))
        moving.append(dict(step_s=dt,mesh_elements=60,retained_modes=1,
            maximum_error=float(max(errors)),relative_error=float(max(errors)/max(abs(v) for v in reference))))
    chain=CouplerChain(a['car_mass_kg'],a['coupler_stiffness_n_m'],0.,a['step_s'])
    chain.u[:2]=[.01,-.01];initial=chain.energy();energy_error=0.;net=0.
    for _ in range(1000):
        r=chain.step(np.zeros(6));net=max(net,abs(r['internal_net_force_n']));energy_error=max(energy_error,abs(chain.energy()-initial)/initial)
    return dict(static_point_load=bool(static['centre_relative_error']<1e-8),static_refinement_relative_error=static['centre_relative_error'],
        force_projection_virtual_power=bool(work_error<1e-12),force_projection_relative_error=work_error,
        support_boundary_continuity=bool(boundary<1e-8),boundary_displacement_jump_m=boundary,
        independent_moving_load_solution=bool(moving[-1]['relative_error']<.001),moving_load_refinement=moving,
        moving_load_refines=bool(moving[-1]['maximum_error']<moving[0]['maximum_error']/3),
        moving_load_temporal_refinement_ratio=moving[0]['maximum_error']/moving[-1]['maximum_error'],
        moving_load_benchmark_scope='60 spatial elements and one mode isolate temporal convergence; production mesh unchanged',
        coupler_energy_conservation=bool(energy_error<1e-10),coupler_energy_relative_error=energy_error,
        coupler_internal_momentum=bool(net<1e-7),coupler_net_force_max_n=net)


def rust_negative_controls(executable,a):
    gaps=np.full((6,24),a['gap_target_m']);replay=bad=False
    with RustTrain(executable,a,a['step_s']) as bridge:
        forces,_=bridge.tick(1,gaps)
        gravity=float(np.max(np.abs(forces.sum(axis=1)-a['car_mass_kg']*station.G)))
        try:bridge.tick(1,gaps)
        except RuntimeError as exc:replay='rejected frame' in str(exc)
    with RustTrain(executable,a,a['step_s']) as bridge:
        try:bridge.tick(1,np.full((6,24),a['gap_minimum_m']/2))
        except RuntimeError as exc:bad='rejected frame' in str(exc)
    return dict(gravity_equilibrium=gravity<1e-6,gravity_residual_n=gravity,replayed_frame_rejected=replay,
        out_of_envelope_gap_rejected=bad,physical_output_authorised=False)


def candidate_assumptions(a):
    """An exact nominal revision plus mandatory adverse variants and a short span."""
    result=[]
    for role,span,depth,stiffness,bias in (
            ('configured-nominal',a['guideway_span_m'],a['beam_section_m']['depth'],1.,0.),
            ('reduced-stiffness',a['guideway_span_m'],a['beam_section_m']['depth'],a['beam_modulus_adverse_factor'],0.),
            ('reduced-stiffness-positive-bias',a['guideway_span_m'],a['beam_section_m']['depth'],a['beam_modulus_adverse_factor'],a['sensor_bias_screen_m']),
            ('reduced-stiffness-negative-bias',a['guideway_span_m'],a['beam_section_m']['depth'],a['beam_modulus_adverse_factor'],-a['sensor_bias_screen_m']),
            ('short-span-comparison',20.,1.8,1.,0.)):
        candidate=dict(a);section=dict(a['beam_section_m'],depth=depth)
        candidate.update(guideway_span_m=span,beam_section_m=section,runtime_s=a['candidate_runtime_s'],acceleration_m_s2=a['candidate_acceleration_m_s2'],
            coupler_stiffness_n_m=a['candidate_coupler_stiffness_n_m'],beam_modulus_pa=a['beam_modulus_pa']*stiffness,
            sensor_bias_m=bias,candidate_role=role)
        candidate['beam_vertical_inertia_m4']=model.section(section['width'],depth,section['web'],section['flange'])['vertical_i_m4']
        candidate['guideway_line_mass_kg_m']=geometry.guideway_quantities(span,**section)['total_line_mass_kg_m']
        result.append(candidate)
    return result


CONFIRMATION_ROLES=('reduced-stiffness','reduced-stiffness-positive-bias','reduced-stiffness-negative-bias')


def confirmation_eligible(run):
    return bool(run['study_pass'] and run['maximum_magnetic_phase_spread_degrees']<=5.
        and run['longitudinal_energy']['relative_residual']<1e-5
        and run['load_projection_virtual_power_relative_error']<1e-10)


def physical_guard_probe_assumptions(a=None):
    """Stable comparison that exposes physical clearance hidden by sensed bias.

    This explicit comparison is independent of the currently selected beam.
    Its initial settling must succeed before the moving gap guard is exercised.
    """
    a=dict(load() if a is None else a);section=dict(a['beam_section_m'],depth=2.2)
    a.update(beam_section_m=section,guideway_span_m=25.,runtime_s=88.,acceleration_m_s2=1.,
        coupler_stiffness_n_m=100_000_000.,sensor_bias_m=.002,beam_modulus_pa=a['beam_modulus_pa']*.85,
        candidate_role='stable-2.2m-positive-bias-physical-guard-negative-control',
        beam_vertical_inertia_m4=model.section(section['width'],section['depth'],section['web'],section['flange'])['vertical_i_m4'],
        guideway_line_mass_kg_m=geometry.guideway_quantities(25.,**section)['total_line_mass_kg_m'])
    return a


def physical_guard_counterexample_passed(run):
    a=run['assumptions']
    return bool(not run['study_pass'] and run['failure']=='independent physical gap outside envelope'
        and run['completed_moving_steps']>0 and run['minimum_gap_m']<a['gap_minimum_m']
        and run['minimum_gap_m']+a['sensor_bias_m']>=a['gap_minimum_m'])


def study():
    a=load();executable,execution=build_bridge()
    negative=dict(a);negative_section=dict(a['beam_section_m'],depth=1.8)
    negative.update(guideway_span_m=25.,beam_section_m=negative_section,runtime_s=90.,acceleration_m_s2=.8,coupler_stiffness_n_m=10_000_000.,candidate_role='rejected-25m-1.8m-90s-soft-coupler-comparison')
    negative['beam_vertical_inertia_m4']=model.section(negative_section['width'],1.8,negative_section['web'],negative_section['flange'])['vertical_i_m4']
    negative['guideway_line_mass_kg_m']=geometry.guideway_quantities(25.,**negative_section)['total_line_mass_kg_m']
    reference=simulate(executable,assumptions=negative)
    candidates=[simulate(executable,assumptions=candidate) for candidate in candidate_assumptions(a)]
    full=candidates[0]
    confirmations={run['assumptions']['candidate_role']:run for run in candidates[1:4]}
    chosen=full['assumptions']
    coarse=simulate(executable,assumptions=chosen,start_time_s=a['refinement_start_s'],duration_s=a['refinement_duration_s'])
    fine=simulate(executable,assumptions=chosen,start_time_s=a['refinement_start_s'],duration_s=a['refinement_duration_s'],step_s=a['step_s']/2)
    refinement=max(abs(coarse[k]-fine[k]) for k in ('minimum_gap_m','maximum_gap_m'))
    disconnected=simulate(executable,assumptions=a,duration_s=.1,feedback=False)
    excessive_bias=simulate(executable,assumptions=physical_guard_probe_assumptions(a),duration_s=20.)
    controls=numerical_controls(a);controls.update(rust_negative_controls(executable,a))
    controls.update(two_way_feedback_negative_control=not disconnected['study_pass'],
        moving_train_time_refinement=bool(coarse['study_pass'] and fine['study_pass'] and refinement<=a['refinement_gap_tolerance_m']),
        full_run_longitudinal_work_balance=full['longitudinal_energy']['relative_residual']<1e-5,
        full_run_projection_work=full['load_projection_virtual_power_relative_error']<1e-10,
        full_run_phase_indexing_screen=full['maximum_magnetic_phase_spread_degrees']<=5.,
        mandatory_adverse_confirmations=all(confirmation_eligible(confirmations[role]) for role in CONFIRMATION_ROLES),
        physical_gap_bias_counterexample_rejected=physical_guard_counterexample_passed(excessive_bias),
        sensed_and_physical_gap_bias_consistent=all(
            abs(row['minimum_sensed_gap_m']-row['minimum_gap_m']-run['sensor_bias_m'])<1e-10
            and abs(row['maximum_sensed_gap_m']-row['maximum_gap_m']-run['sensor_bias_m'])<1e-10
            for run in candidates for row in run['trace']))
    return dict(schema='osr-moving-train-study/1',configuration_revision=a['configuration_revision'],assumptions=a,
        candidate_sha256=full['candidate_sha256'],execution=execution,runtime=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
        formation=full['formation'],moving_run=full,reference_run=reference,candidates=candidates,
        selection_scope='Source-configured common city/station candidate, eligible only with all reduced-stiffness and signed sensor-bias confirmations; short-span alternative and rejected reference retained. Not a complete cost or engineering optimum',
        mandatory_confirmation_roles=list(CONFIRMATION_ROLES),
        automatic_reference_configuration_promotion=False,
        refinement=dict(coarse=coarse,fine=fine,maximum_gap_difference_m=refinement),
        disconnected_feedback_negative_control=disconnected,excessive_sensor_bias_negative_control=excessive_bias,numerical_controls=controls,
        study_pass=bool(full['study_pass'] and all(controls[k] for k in CONTROL_NAMES)),
        shared_field_phase_registration_accepted=False,physical_output_authorised=False,**model.FLAGS)


CONTROL_NAMES={'static_point_load','force_projection_virtual_power','support_boundary_continuity',
    'independent_moving_load_solution','moving_load_refines','coupler_energy_conservation','coupler_internal_momentum',
    'gravity_equilibrium','replayed_frame_rejected','out_of_envelope_gap_rejected','two_way_feedback_negative_control','moving_train_time_refinement',
    'full_run_longitudinal_work_balance','full_run_projection_work','full_run_phase_indexing_screen',
    'mandatory_adverse_confirmations','physical_gap_bias_counterexample_rejected','sensed_and_physical_gap_bias_consistent'}


def render(result,output):
    """Plot exact retained positions/beam states; vertical displacement amplified."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon
    output=Path(output);run=result['moving_run'];a=run['assumptions'];trace=run['trace']
    if not trace:raise ValueError('retained moving geometry trace required')
    beam=MovingGuideway(a,distance_m=run['trajectory']['inputs']['distance_m']);amplification=a['visual_vertical_amplification']
    samples=np.unique(np.linspace(0,len(trace)-1,min(a['movie_frames'],len(trace)),dtype=int)).tolist()
    def frame(index,path):
        item=trace[index];beam.q[:]=0.;beam.q[item.get('beam_modal_span_indices',list(range(beam.count)))]=np.array(item['beam_modal_q']);front=item['front_reference_m']
        fig,axes=plt.subplots(2,1,figsize=(12,6.8),gridspec_kw={'height_ratios':[3,1]},facecolor='#f2f6fa')
        ax=axes[0];xx=np.linspace(front-120,front+35,400)
        ax.plot(xx,-amplification*beam.displacement(xx),color='#47617a',lw=3,label='flexible guideway')
        for car,(centre,body) in enumerate(zip(item['car_centres_m'],item['body_down_roll_pitch'])):
            half=a['body_length_m']/2;corners=[]
            for x,z in ((-half,.25),(half,.25),(half,3.05),(-half,3.05)):
                corners.append([centre+x,z-amplification*(body[0]+x*body[2])])
            ax.add_patch(Polygon(corners,closed=True,facecolor='#0f967f',edgecolor='#063f42',alpha=.85));ax.text(centre,1.4-amplification*body[0],str(car+1),ha='center',color='white')
        ax.set(xlim=(front-120,front+35),ylim=(-1.8,4.2),xlabel='Route position / m',ylabel='Side view / m')
        ax.grid(alpha=.2);ax.set_title(f"Six-car moving ideal-force study — {item['time_s']:.2f}s — {item['phase']}\nDynamic vertical displacements/pitch ×{amplification:g}; car dimensions and longitudinal positions unamplified")
        values=np.array([r['time_s'] for r in trace]);low=np.array([r['minimum_gap_m'] for r in trace])*1000;high=np.array([r['maximum_gap_m'] for r in trace])*1000
        axes[1].fill_between(values,low,high,color='#0f967f',alpha=.3,label='144 physical model gaps')
        axes[1].axvline(item['time_s'],color='#cf6e30');axes[1].axhline(a['gap_minimum_m']*1000,color='red',ls='--');axes[1].axhline(a['gap_maximum_m']*1000,color='red',ls='--')
        axes[1].set(xlabel='Virtual time / s',ylabel='Gap / mm');axes[1].grid(alpha=.2)
        fig.text(.04,.015,'Calculated moving geometry, actual Rust support control; ideal magnetic forces, assumed inertias/couplers. No measured magnetic, motion-clearance or physical acceptance.',fontsize=8)
        fig.tight_layout(rect=(0,.04,1,1));fig.savefig(path,dpi=100,metadata={'Software':'OpenSourceRail moving numerical twin'});plt.close(fig)
    with tempfile.TemporaryDirectory(prefix='osr-moving-frames-') as temporary:
        folder=Path(temporary)
        for i,index in enumerate(samples):frame(index,folder/f'{i:04d}.png')
        overview=folder/f'{len(samples)//2:04d}.png';(output/'overview.png').write_bytes(overview.read_bytes())
        command=['ffmpeg','-y','-loglevel','error','-framerate',str(a['movie_fps']),'-i',str(folder/'%04d.png'),
            '-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',str(output/'moving-train.mp4')]
        subprocess.run(command,check=True,timeout=120)
    receipt=dict(schema='osr-moving-geometry-visual/1',candidate_sha256=run['candidate_sha256'],
        renderer_sha256=digest(Path(__file__).read_bytes()),retained_trace_sha256=digest(encoded(trace)),
        frame_trace_indices=samples,frames_per_second=a['movie_fps'],vertical_displacement_amplification=amplification,
        geometry_scope='Exact retained car positions and linear guideway modal displacement; side view with explicit vertical/pitch amplification, not CAD collision or physical validation',
        files_sha256={name:digest((output/name).read_bytes()) for name in ('overview.png','moving-train.mp4')},**model.FLAGS)
    (output/'visual-receipt.json').write_bytes(encoded(receipt));return receipt


def publish(output=OUTPUT):
    before=sources();result=study();result['source_sha256']=before
    if sources()!=before:raise ValueError('moving-train sources changed during executed study')
    output=Path(output)
    if output.is_symlink():raise ValueError('ordinary moving packet output required')
    output.mkdir(parents=True,exist_ok=True)
    if any(p.is_symlink() for p in output.iterdir()) or {p.name for p in output.iterdir()}-FILES-{'manifest.json'}:raise ValueError('unexpected moving packet file')
    (output/'result.json.gz').write_bytes(gzip.compress(encoded(result),mtime=0));render(result,output)
    run=result['moving_run'];reference=result['reference_run']
    text='\n'.join(['# Moving six-car ideal-force numerical twin','',
        '[Retained numerical results/traces](result.json.gz) · [Moving geometry video](moving-train.mp4) · [Source receipt](manifest.json)','',
        '![Actual calculated moving geometry](overview.png)','',
        f"The selected provisional {run['assumptions']['guideway_span_m']:g}m-span candidate completes {run['executed_duration_s']:g}s with six separate rigid car states and actual Rust 24-module controllers. Gap range: {run['minimum_gap_m']*1000:.3f}–{run['maximum_gap_m']*1000:.3f}mm. The original reference remains recorded with study_pass={reference['study_pass']}; failed evidence is not promoted.",'',
        'Station launch/coast/brake positions come from the exact jerk-limited longitudinal model. Per-car spring/damper corrections are integrated using midpoint dynamics; thrust is allocated by actual band overlap. Coupler energy/internal force, moving point-load closed form/refinement, span-boundary continuity, virtual work, Rust replay/invalid gaps and feedback disconnection are checked.','',
        f"The common configured candidate must also pass {100*(1-result['assumptions']['beam_modulus_adverse_factor']):g}% reduced stiffness and signed ±{result['assumptions']['sensor_bias_screen_m']*1000:g}mm sensor biases. Bias is applied to actual Rust sensed gaps; independent physical model gaps must stay within the original guard. A larger bias counterexample is retained. The short-span family and failed original reference remain available for comparison; no configuration is automatically promoted by this packet. The video uses exact recorded positions and beam states with declared vertical/pitch amplification.",'',
        '**Open:** measured electromagnetic force/loss maps and shared-field phase/current feasibility, flexible bodies, torsion/lateral dynamics, rail joints/contact/soil, full construction and fatigue acceptance, emergency stopping/recovery, guideway alignment and sensor calibration acceptance, and hardware timing. The signed scalar sensor-bias screen is a provisional tolerance-budget calculation, not an accepted route alignment budget. Initial stationary settling, uniform car masses, assumed inertias, pinned linear spans and ideal independently allocated support/thrust remain modelling assumptions. No manufacturing, engineering or physical release is claimed.',''])
    (output/'README.md').write_text(text)
    if sources()!=before:raise ValueError('moving-train sources changed during presentation')
    manifest=dict(schema='osr-moving-train-publication/1',source_sha256=before,execution=result['execution'],candidate_sha256=result['candidate_sha256'],
        files_sha256={name:digest((output/name).read_bytes()) for name in sorted(FILES)},physical_output_authorised=False,**model.FLAGS)
    (output/'manifest.json').write_bytes(encoded(manifest));return verify(output)


def verify(output=OUTPUT):
    output=Path(output)
    if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()}!=FILES|{'manifest.json'}:raise ValueError('exact moving packet inventory required')
    if any(p.is_symlink() or p.stat().st_size>64*1024*1024 for p in output.iterdir()):raise ValueError('bounded ordinary moving packet required')
    manifest=json.loads((output/'manifest.json').read_bytes())
    if manifest.get('schema')!='osr-moving-train-publication/1' or manifest.get('source_sha256')!=sources():raise ValueError('moving source identity differs')
    if set(manifest.get('files_sha256',{}))!=FILES:raise ValueError('complete moving payload receipt required')
    for name,expected in manifest['files_sha256'].items():
        if digest((output/name).read_bytes())!=expected:raise ValueError('moving payload differs: '+name)
    with gzip.open(output/'result.json.gz','rb') as stream:data=stream.read(MAX_RAW+1)
    if len(data)>MAX_RAW:raise ValueError('moving evidence exceeds decompression bound')
    result=json.loads(data);visual=json.loads((output/'visual-receipt.json').read_bytes())
    if (result.get('schema')!='osr-moving-train-study/1' or result.get('source_sha256')!=manifest['source_sha256']
            or result.get('execution')!=manifest.get('execution') or result.get('assumptions')!=load()
            or result['execution']['build_command']!=BUILD or not result['execution']['rustc'].startswith('rustc ')
            or not re_digest(result['execution']['binary_sha256'])):raise ValueError('moving execution/configuration receipt differs')
    run=result['moving_run'];controls=result['numerical_controls']
    if not CONTROL_NAMES<=set(controls):raise ValueError('mandatory moving numerical controls missing')
    for record in (manifest,result,run,visual,*result['candidates'],result['reference_run'],result['refinement']['coarse'],result['refinement']['fine'],
            result['disconnected_feedback_negative_control'],result['excessive_sensor_bias_negative_control']):
        if any(record.get(k) is not False for k in model.FLAGS):raise ValueError('moving numerical study cannot release engineering')
    if (manifest.get('physical_output_authorised') is not False or result.get('physical_output_authorised') is not False
            or result.get('shared_field_phase_registration_accepted') is not False or result.get('automatic_reference_configuration_promotion') is not False):raise ValueError('moving evidence exceeded authority')
    runs=[result['reference_run'],*result['candidates']]
    expected_candidates=candidate_assumptions(result['assumptions'])
    if (len(result['candidates'])!=len(expected_candidates)
            or any(candidate['assumptions']!=expected for candidate,expected in zip(result['candidates'],expected_candidates))
            or result.get('mandatory_confirmation_roles')!=list(CONFIRMATION_ROLES)
            or run!=result['candidates'][0]):raise ValueError('exact configured revision and mandatory adverse candidate inventory required')
    for candidate in runs:
        if candidate['candidate_sha256']!=digest(encoded(candidate['assumptions'])) or candidate['formation']['cars']!=6:raise ValueError('moving candidate identity/formation differs')
        times=[row['time_s'] for row in candidate['trace']]
        if any(b<=a for a,b in zip(times,times[1:])):raise ValueError('moving trace time regressed')
        for row in candidate['trace']:
            if (len(row['car_centres_m'])!=6 or len(row['body_down_roll_pitch'])!=6
                    or any(len(q)!=3 for q in row['body_down_roll_pitch']) or len(row['car_relative_longitudinal_m'])!=6):raise ValueError('complete six-car moving geometry trace required')
            if any(b>=a for a,b in zip(row['car_centres_m'],row['car_centres_m'][1:])):raise ValueError('moving car order/integrity differs')
            if (abs(row['minimum_sensed_gap_m']-row['minimum_gap_m']-candidate['sensor_bias_m'])>1e-10
                    or abs(row['maximum_sensed_gap_m']-row['maximum_gap_m']-candidate['sensor_bias_m'])>1e-10):raise ValueError('sensed and independently observed physical gap bias differ')
        observed_spread=max((max(row['car_relative_longitudinal_m'])-min(row['car_relative_longitudinal_m']) for row in candidate['trace']),default=0.)
        if candidate['maximum_longitudinal_relative_spread_m']+1e-10<observed_spread:raise ValueError('moving phase/indexing envelope omits retained excursions')
        if candidate['study_pass'] and (candidate['failure'] is not None or candidate['stop_seen']
                or candidate['completed_moving_steps']!=candidate['planned_moving_steps']
                or not candidate['trace']
                or candidate['window']['start_time_s']!=0.
                or abs(candidate['window']['duration_s']-candidate['trajectory']['inputs']['runtime_s'])>1e-8
                or abs(candidate['trace'][-1]['time_s']-candidate['trajectory']['inputs']['runtime_s'])>1e-8
                or not candidate['assumptions']['gap_minimum_m']<=candidate['minimum_gap_m']<=candidate['maximum_gap_m']<=candidate['assumptions']['gap_maximum_m']):raise ValueError('passing moving run lacks completed bounded evidence')
    confirmations={candidate['assumptions']['candidate_role']:candidate for candidate in result['candidates'][1:4]}
    mandatory=all(confirmation_eligible(confirmations[role]) for role in CONFIRMATION_ROLES)
    if controls['mandatory_adverse_confirmations'] is not mandatory:raise ValueError('mandatory confirmation selection omitted failed evidence')
    excessive=result['excessive_sensor_bias_negative_control']
    if (excessive['assumptions']!=physical_guard_probe_assumptions(result['assumptions'])
            or excessive['candidate_sha256']!=digest(encoded(excessive['assumptions']))
            or excessive['window']['start_time_s']!=0. or excessive['window']['duration_s']!=20.
            or controls['physical_gap_bias_counterexample_rejected'] is not physical_guard_counterexample_passed(excessive)):
        raise ValueError('independent physical guard counterexample differs')
    expected=bool(run['study_pass'] and all(controls[name] is True for name in CONTROL_NAMES))
    if result['study_pass'] is not expected or manifest['candidate_sha256']!=run['candidate_sha256'] or result['candidate_sha256']!=run['candidate_sha256']:
        raise ValueError('moving study selection differs from applicable evidence')
    if (visual.get('schema')!='osr-moving-geometry-visual/1' or visual.get('candidate_sha256')!=run['candidate_sha256']
            or visual.get('renderer_sha256')!=manifest['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]
            or visual.get('retained_trace_sha256')!=digest(encoded(run['trace']))
            or visual.get('vertical_displacement_amplification')!=run['assumptions']['visual_vertical_amplification']
            or not visual.get('frame_trace_indices') or any(type(i) is not int or not 0<=i<len(run['trace']) for i in visual['frame_trace_indices'])):
        raise ValueError('moving geometry video provenance differs')
    if visual.get('files_sha256')!={name:manifest['files_sha256'][name] for name in ('overview.png','moving-train.mp4')}:raise ValueError('moving visual checksums differ')
    return manifest


def re_digest(value):return isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value)


def read_selected(output=OUTPUT):
    """Verified compact interface for downstream controller/system campaigns."""
    receipt=verify(output)
    with gzip.open(Path(output)/'result.json.gz','rb') as stream:value=json.load(stream)
    run=value['moving_run'];a=run['assumptions'];applicable=[run,*value['candidates'][1:4]]
    return dict(schema='osr-selected-moving-twin/1',candidate_sha256=run['candidate_sha256'],
        configuration_revision=value['configuration_revision'],source_sha256=receipt['source_sha256'],
        study_pass=value['study_pass'],formation=run['formation'],profile=run['trajectory']['inputs'],
        beam_section_m=a['beam_section_m'],guideway_span_m=a['guideway_span_m'],beam_modulus_pa=a['beam_modulus_pa'],
        gross_train_mass_kg=run['trajectory']['inputs']['train_mass_kg'],
        coupler_stiffness_n_m=a['coupler_stiffness_n_m'],coupler_damping_n_s_m=a['coupler_damping_n_s_m'],
        maximum_cumulative_indexing_spread_m=max(candidate['maximum_longitudinal_relative_spread_m'] for candidate in applicable),
        maximum_magnetic_phase_spread_degrees=max(candidate['maximum_magnetic_phase_spread_degrees'] for candidate in applicable),
        maximum_individual_coupler_extension_m=max(candidate['peak_coupler_extension_m'] for candidate in applicable),
        peak_coupler_force_n=max(candidate['peak_coupler_force_n'] for candidate in applicable),
        minimum_gap_m=min(candidate['minimum_gap_m'] for candidate in applicable),
        maximum_gap_m=max(candidate['maximum_gap_m'] for candidate in applicable),
        sensor_bias_screen_m=value['assumptions']['sensor_bias_screen_m'],
        beam_modulus_adverse_factor=value['assumptions']['beam_modulus_adverse_factor'],
        mandatory_confirmation_candidate_sha256=[candidate['candidate_sha256'] for candidate in value['candidates'][1:4]],
        physical_output_authorised=False,shared_field_phase_registration_accepted=False,**model.FLAGS)
