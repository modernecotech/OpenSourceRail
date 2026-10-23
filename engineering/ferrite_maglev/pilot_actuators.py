"""Executed Rust voltage/current loops inside a six-body moving numerical study.

The retained ideal-force benchmark is untouched. This independent plant closes
the voltage/current/assumed-field/force/motion/sensed-gap chain, with protected
fault holds and visible infeasibility. Magnetic maps and hardware remain open.
"""
from hashlib import sha256
from pathlib import Path
import gzip
import io
import json
import math
import importlib.util
from functools import lru_cache
import subprocess
import tomllib
import numpy as np
from . import body_stiffness, drive_design as drive, launch_optimisation as launch, model, moving_train as moving, pilot_product as product, pilot_limits, station
from concurrent.futures import ProcessPoolExecutor

ROOT=model.ROOT
INPUT=Path(__file__).with_name('pilot-actuators.toml')
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/pilot-actuators'
TEST=ROOT/'engineering/analysis/tests/test_ferrite_maglev_pilot_actuators.py'
RUST=ROOT/'crates/osr-maglev-control/examples/pilot_actuator_bridge.rs'
OBSERVER_ROOT=Path(__file__).parent/'observer-prototype'
OBSERVER_BUILD=['cargo','build','--locked','--release','--manifest-path',str(OBSERVER_ROOT/'Cargo.toml'),'--target-dir',str(ROOT/'build/pilot-observer-rust'),'--message-format=json']
SCHEMA='osr-pilot-actuators/1'
FLAGS=product.FLAGS
BUILD=['cargo','build','--locked','--release','-p','osr-maglev-control','--example','pilot_actuator_bridge','--message-format=json']
FAULTS={1:'Bus',2:'Sensor',3:'Temperature',4:'Authority',5:'Receiver',6:'Phase',7:'Time',8:'Current',9:'Saturation'}
def encoded(v):return product.encoded(v)
def digest(b):return sha256(b).hexdigest()
def observer_source_paths():return [OBSERVER_ROOT/'Cargo.toml',OBSERVER_ROOT/'Cargo.lock',*OBSERVER_ROOT.glob('src/**/*.rs'),*OBSERVER_ROOT.glob('python/*.py'),*OBSERVER_ROOT.glob('include/*.h'),*OBSERVER_ROOT.glob('tests/**/*.py'),*OBSERVER_ROOT.glob('tests/**/*.json'),*OBSERVER_ROOT.glob('tests/*.c')]
def source_paths():return sorted(p for p in {*observer_source_paths(),Path(__file__),Path(pilot_limits.__file__),INPUT,TEST,RUST,ROOT/load()['pilot_city_summary'],*product.source_paths(),*launch.source_paths(),*body_stiffness.source_paths()} if not p.is_relative_to(ROOT/'docs/design-engine'))
def sources():return {p.relative_to(ROOT).as_posix():digest(p.read_bytes()) for p in source_paths()}
def load():
    a=tomllib.loads(INPUT.read_text())
    if a['schema']!='osr-pilot-actuator-input/1' or a['configuration_id']!='baghdad-30kwh-aw3':raise ValueError('explicit controlled actuator profile required')
    for k,v in a.items():
        if type(v) in (int,float) and (not math.isfinite(v) or v<=0):raise ValueError('finite positive actuator assumption '+k)
    if a['outer_step_s']!=.001 or a['current_step_s']!=.00005:raise ValueError('fixed bounded1kHz motion/20kHz virtual current clocks required')
    return a

def variant_configuration(body_variant='gfrp-control',winding_variant='retained-50t16mm2'):
    a=load()
    if body_variant not in a['body_variants'] or winding_variant not in a['support_winding_variants']:raise ValueError('bounded counted actuator variant required')
    cfg=product.configuration_profile(a['configuration_id']);base_hash=cfg.pop('configuration_sha256');d=drive.load()
    row=next(v for v in body_stiffness.derivation()['variants'] if v['name']==body_variant)
    delta=row['incremental_stock_and_spacer_mass_kg'];cfg['body'].update(variant_id=row['id'],longitudinal_stiffness_n_m=row['lumped_stiffness_used_n_m'],incremental_stock_and_spacer_mass_kg=delta,stiffness_role='geometry-derived drilled '+row['stock']['material']+' tubes in series with coupler; rigid-car lumped sensitivity, not flexible-body qualification')
    if winding_variant=='equal-copper-80t10mm2':d['support'].update(turns_per_coil=80,conductor_area_mm2=10.)
    if winding_variant=='equal-copper-100t8mm2':d['support'].update(turns_per_coil=100,conductor_area_mm2=8.)
    extra_mount=extra_cooling=0.;cooling_multiplier=1.
    if winding_variant.startswith('higher-copper-'):
        repair=winding_variant=='higher-copper-140t20mm2';high_turn=winding_variant in {'higher-copper-120t20mm2','higher-copper-140t20mm2'};outer=a['higher_repair_outer_m'] if repair else a['higher_turn_outer_m'] if high_turn else a['higher_copper_outer_m'];mean=sum(d['support']['coil_inner_m'])+sum(outer)
        d['support'].update(turns_per_coil=140 if repair else 120 if high_turn else 100,conductor_area_mm2=20.,coil_outer_m=outer,mean_turn_length_m=mean,coil_height_m=a['higher_repair_height_m'] if repair else a['higher_turn_height_m'] if high_turn else .060)
        extra_mount=24*a['higher_copper_extra_mount_kg_per_module'];extra_cooling=24*a['higher_turn_extra_cooling_kg_per_module'] if high_turn else 24*a['higher_copper_extra_cooling_kg_per_module'];cooling_multiplier=a['higher_turn_cooling_capacity_multiplier'] if high_turn else a['higher_copper_cooling_capacity_multiplier']
    s=drive.support(d);original=drive.support();coil_delta=s['copper_kg_per_car']-original['copper_kg_per_car']
    if winding_variant.startswith('equal-copper') and abs(coil_delta)>1e-8:raise ValueError('declared equal-copper variant must not inherit free mass')
    bay_delta=0.
    if winding_variant.startswith('higher-copper-'):
        service=product.redesigned_bay();bay_delta=service['changed_hardware']['additional_stock_mass_kg_per_car']
        cfg['bay_service_variant']=dict(id=service['id'],changed_hardware=service['changed_hardware'],new_interfaces=service['new_interfaces'],
            basis='Counted detachable collector geometry alternative; splice/global load/fixture acceptance held')
    else:cfg['bay_service_variant']=dict(id='retained-downward-removal-control',changed_hardware=dict(additional_stock_mass_kg_per_car=0.),basis='Retained obstructed path; no redesigned splice hardware credited')
    power_delta=0.
    if winding_variant=='higher-copper-140t20mm2':
        power_delta=24*a['higher_voltage_extra_electronics_kg_per_module']+a['normal_observer_extra_mass_kg_per_car'];d['support']['bus_v']=a['higher_voltage_support_bus_v']
        cfg['support_power_stage']=dict(id='192v-60a-normal-rust-observer-provisional-1',observer_backend='rust-cdylib',rated_bus_v=d['support']['bus_v'],continuous_current_a=60.,peak_current_a=120.,
            additional_mass_kg_per_car=power_delta,additional_unquoted_cost_usd_per_car=24*a['higher_voltage_extra_electronics_usd_per_module']+a['normal_observer_extra_cost_usd_per_car'],
            components=[dict(id='higher-voltage-converter-allocation',count_per_car=24,mass_kg_each=a['higher_voltage_extra_electronics_kg_per_module'],unquoted_cost_usd_each=a['higher_voltage_extra_electronics_usd_per_module']),dict(id='calibrated-phase-current-gap-observer-allocation',count_per_car=24,mass_kg_each=a['normal_observer_extra_mass_kg_per_car']/24,unquoted_cost_usd_each=a['normal_observer_extra_cost_usd_per_car']/24)],
            additional_auxiliary_kw_per_car=a['support_power_stage_extra_auxiliary_kw_per_car'],normal_wrench_feedforward=True,observer_maximum_age_s=a['outer_step_s'],applicable_estimator_scale_cases=a['normal_feedforward_scales'],
            scope='Priced unqualified converter/phase-current-gap observer allocation. One-frame delayed same-map estimate; no physical sensing/timing/field-map qualification or direct force command.')
    else:cfg['support_power_stage']=dict(id='retained-96v-control',rated_bus_v=d['support']['bus_v'],additional_mass_kg_per_car=0.,additional_unquoted_cost_usd_per_car=0.,normal_wrench_feedforward=False)
    cfg.update(id=cfg['id']+'/'+body_variant+'/'+winding_variant,base_configuration_sha256=base_hash,controlled_tare_kg=cfg['controlled_tare_kg']+delta+coil_delta+extra_mount+extra_cooling+bay_delta+power_delta,controlled_aw3_kg=cfg['controlled_aw3_kg']+delta+coil_delta+extra_mount+extra_cooling+bay_delta+power_delta)
    cfg['provisional_dynamic_support_force_n']=cfg['controlled_aw3_kg']*9.81*1.3;cfg['magnetic']['support_winding']=d['support'];cfg['magnetic']['winding_variant']=winding_variant
    original=drive.support();cfg['magnetic'].update(winding_copper_kg_per_car=s['copper_kg_per_car'],incremental_winding_copper_kg=coil_delta,additional_mount_allowance_kg=extra_mount,additional_cooling_allowance_kg=extra_cooling,
        baseline_wire_current_density_a_mm2=a['baseline_wire_current_density_a_mm2'],continuous_copper_heat_budget_w_per_coil=original['coil']['resistance_hot_ohm']*60**2*cooling_multiplier,
        continuous_cooling_budget_is_unqualified=True,cooling_capacity_multiplier=cooling_multiplier,
        additional_unquoted_copper_and_cooling_usd=max(0.,coil_delta)*product.load()['support_copper_usd_per_kg']+(24*(a['higher_turn_extra_cooling_usd_per_module'] if winding_variant in {'higher-copper-120t20mm2','higher-copper-140t20mm2'} else a['higher_copper_extra_cooling_usd_per_module']) if extra_cooling else 0.))
    hp=body_stiffness.assembled_body.hardpoint_screen();ratio=cfg['controlled_aw3_kg']/hp['car_mass_kg']
    cfg['load_reassessment']=dict(reference_prototype_mass_kg=hp['car_mass_kg'],controlled_mass_ratio=ratio,maximum_interface_force_n=hp['maximum_interface_force_n']*ratio,
        reference_ideal_force_car_mass_kg=26200.,reference_guideway_gross_load_ratio=cfg['controlled_aw3_kg']/26200.,new_full_civil_and_hardpoint_acceptance_required=True)
    cfg['support_power_stage']['current_loop_base_kp_v_per_a']=a['support_kp_v_per_a'];cfg['support_power_stage']['current_loop_base_ki_v_per_a_s']=a['support_ki_v_per_a_s']
    cfg['wayside_drive']={k:a[k] for k in ('groups_per_direction','conductor_area_mm2','turns','dc_bus_v')}
    cfg['configuration_sha256']=digest(encoded(cfg));return cfg,d

def candidate_packaging(winding_variant):
    v=product.redesigned_bay() if winding_variant.startswith('higher-copper-') else product.bay_definition();a=load();extra={}
    if winding_variant.startswith('higher-copper-'):
        repair=winding_variant=='higher-copper-140t20mm2';high_turn=winding_variant in {'higher-copper-120t20mm2','higher-copper-140t20mm2'};outer=a['higher_repair_outer_m'] if repair else a['higher_turn_outer_m'] if high_turn else a['higher_copper_outer_m'];height=a['higher_repair_height_m'] if repair else a['higher_turn_height_m'] if high_turn else .060
        for p,x in zip([p for p in v['equipment'] if p['id'].startswith('bay/coil-')],(.02,.34,.66) if repair else (.04,.36,.68)):
            p['size_m']=[*outer,height];p['at_m']=[x,.925 if high_turn else .94,-.364-height]
        v['equipment'].append(dict(id='bay/extended-coldplate',kind='box',size_m=[.96,.20,.004],at_m=[.02,.925 if high_turn else .9325,-.368-height],role='replaceable',
            defined_aluminium_stock_kg=.96*.20*.004*2700.,included_within_cooling_allocation_not_added_twice=True))
        extra=dict(added_mount_kg=24*a['higher_copper_extra_mount_kg_per_module'],added_cooling_kg=24*(a['higher_turn_extra_cooling_kg_per_module'] if high_turn else a['higher_copper_extra_cooling_kg_per_module']))
    # Recalculate changed collector solid metadata; conservative car mass still
    # retains all original stock, so the tiny joint cuts receive no mass credit.
    for part in [*v['retained_parts'],*v['fixed_parts']]:
        if part['id'].endswith(('/detachable-bay','/fixed-left','/fixed-right')):
            part['volume_m3']=product.models.volume(part);part['volume_rederived_from_changed_shape']=True
    # Check new equipment internally as well as the complete retained body.
    intersections=[];items=[*v['retained_parts'],*[p for p in v['equipment'] if p['role']=='replaceable']]
    equipment=[p for p in v['equipment'] if p['role']=='replaceable']
    for p in equipment:
        aa=product.bounds(p)
        for q in items:
            if p['id']>=q['id'] and q in equipment:continue
            if p['id']==q['id']:continue
            bb=product.bounds(q)
            if min(min(aa[1][i],bb[1][i])-max(aa[0][i],bb[0][i]) for i in range(3))>1e-9:intersections.append([p['id'],q['id']])
    return dict(definition=v,definition_sha256=digest(encoded(v)),path=product.path_check(v),internal_bound_intersections=intersections,
        unqualified_coldplate_thermal_resistance_target_k_w=(120-40)/(drive.support()['coil']['resistance_hot_ohm']*60**2*(a['higher_turn_cooling_capacity_multiplier'] if winding_variant in {'higher-copper-120t20mm2','higher-copper-140t20mm2'} else a['higher_copper_cooling_capacity_multiplier'] if winding_variant.startswith('higher-copper-') else 1.)),
        scope='Geometric stock/pack/extraction screen only. Thermal interfaces/flow, three-coil core topology, electrical insulation and splice/global loads require independent qualification.',**extra)

def motion_profile(cfg):
    """Exact pilot mainleg; runtime rounded UP to the1ms execution clock."""
    a=load();city=json.loads((ROOT/a['pilot_city_summary']).read_bytes());line=next(r for r in city['lines'] if r['line']==a['pilot_line_id'])
    event=next(e for e in line['duty']['arrival_events_per_circuit'] if not e['terminal_loop_allowance'])
    runtime=math.ceil(event['moving_seconds']*1000.)/1000.
    return launch.corridor.profile(distance_m=event['distance_m'],runtime_s=runtime,cars=6,car_mass_kg=cfg['controlled_aw3_kg'])

def magnetic_geometry_hold(d):
    s=d['support'];aperture=math.prod(s['coil_inner_m']);pole=s['pole_area_m2']
    return dict(state='hold',assumed_gap_pole_area_m2=pole,winding_inner_aperture_m2=aperture,pole_to_window_area_ratio=pole/aperture,
        core_neck_area_m2=None,qualified_flux_split=None,
        reason='Gap reluctance area is not a derived magnetic core. Reconcile pole shoe, return/yoke and winding-window geometry with a measured/FE field map; gap B does not establish neck/core saturation acceptance.')

def lift_current(force,gap,s=None):
    s=drive.load()['support'] if s is None else s;mu=4*math.pi*1e-7
    return (np.sqrt(np.maximum(0.,force)*mu/s['pole_area_m2'])*s['series_gaps']*gap-s['bias_flux_t']*s['series_gaps']*s['gap_m'])/(mu*s['turns_per_coil'])

def lift_force(current,gap,s=None):
    s=drive.load()['support'] if s is None else s;mu=4*math.pi*1e-7
    flux=(s['bias_flux_t']*s['series_gaps']*s['gap_m']+mu*s['turns_per_coil']*current)/(s['series_gaps']*gap)
    return s['pole_area_m2']/mu*flux**2,flux

def build_bridge():
    p=subprocess.run(BUILD,cwd=ROOT,capture_output=True,text=True,timeout=240)
    if p.returncode:raise ValueError('pilot Rust build failed: '+p.stderr[-3000:])
    rows=[json.loads(line) for line in p.stdout.splitlines()];paths=[Path(r['executable']) for r in rows if r.get('reason')=='compiler-artifact' and r.get('target',{}).get('name')=='pilot_actuator_bridge' and r.get('executable')]
    if len(paths)!=1:raise ValueError('one actual pilot compiler artifact required')
    return paths[0],dict(command=BUILD,exit_status=p.returncode,binary_sha256=digest(paths[0].read_bytes()),stdout=p.stdout,stderr=p.stderr)

def build_observer():
    result=subprocess.run(OBSERVER_BUILD,cwd=ROOT,capture_output=True,text=True,timeout=240)
    if result.returncode:raise ValueError('standalone Rust observer build failed: '+result.stderr[-3000:])
    rows=[json.loads(line) for line in result.stdout.splitlines()]
    artifacts=[Path(name) for row in rows if row.get('reason')=='compiler-artifact' and row.get('target',{}).get('name')=='osr_normal_wrench_observer_prototype' for name in row.get('filenames',[]) if Path(name).suffix in {'.so','.dylib','.dll'}]
    if len(artifacts)!=1 or not artifacts[0].is_file():raise ValueError('one actual Rust observer dynamic artifact required')
    return artifacts[0],dict(command=OBSERVER_BUILD,exit_status=0,binary_sha256=digest(artifacts[0].read_bytes()),stdout=result.stdout,stderr=result.stderr)

@lru_cache(maxsize=1)
def observer_binding():
    spec=importlib.util.spec_from_file_location('osr_research_observer_binding',OBSERVER_ROOT/'python/observer.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

class RustNormalObserver:
    """Bounded by-value real Rust observer used on every compensated frame."""
    def __init__(self,library,cfg,groups,k,scale):
        api=observer_binding();self.api=api;self.count=len(groups);self.scale=scale
        self.library=api.C.CDLL(str(library));self.function=self.library.osr_research_normal_wrench_v1;self.function.argtypes=[api.Input];self.function.restype=api.Output
        self.input=api.Input(api.Config(1,self.count,api.digest(cfg['configuration_sha256']),k,scale,1_000_000),api.State(),api.Frame())
        dtype=np.dtype({'names':['psi','theta','position','alpha','beta'],'formats':[(np.float64,6),(np.float64,6),(np.float64,6),np.float64,np.float64],'offsets':[0,48,96,144,152],'itemsize':160})
        if api.C.sizeof(api.Group)!=160 or api.C.sizeof(api.Input)!=33472:raise ValueError('observer ABI layout differs')
        self.groups=np.frombuffer(self.input.frame.groups,dtype=dtype,count=api.MAX_GROUPS);self.desired=np.ctypeslib.as_array(self.input.frame.desired_support_n)
        self.speed=np.ctypeslib.as_array(self.input.frame.speed_m_s);self.centres=np.ctypeslib.as_array(self.input.frame.centres_m)
        self.calls=0;self.hash=digest(Path(library).read_bytes());self.error=np.zeros(3)
    def step(self,sequence,desired,sample,k,dt):
        f=self.input.frame;f.sequence=sequence;f.timestamp_ns=sequence*1_000_000;self.desired[:]=desired
        if sample is not None:
            fields,speed,currents,centres=sample
            f.sample_present=1;f.sample_groups=self.count;f.sample_sequence=sequence-1;f.sample_timestamp_ns=(sequence-1)*1_000_000;f.sample_configuration_sha256=self.input.config.configuration_sha256
            self.groups['psi'][:self.count]=fields['psi'];self.groups['theta'][:self.count]=fields['theta'];self.groups['position'][:self.count]=fields['normal_positions_m']
            self.groups['alpha'][:self.count]=currents[:,0];self.groups['beta'][:self.count]=currents[:,1];self.speed[:]=speed;self.centres[:]=centres
        out=self.function(self.input)
        if out.status or out.physical_output_authorised:raise RuntimeError('Rust observer hold '+str(out.status))
        estimate=np.ctypeslib.as_array(out.scaled_wrench_up_roll_pitch).copy();correction=np.ctypeslib.as_array(out.correction_n).copy();command=np.ctypeslib.as_array(out.requested_support_n).copy()
        reference=normal_wrench_observer(sample,k,dt)*self.scale;expected=normal_force_correction(reference)
        errors=np.array([np.abs(estimate[:,0]-reference[:,0]).max(),np.abs(estimate[:,1:]-reference[:,1:]).max(),np.abs(correction-expected).max()])
        if np.any(errors>1e-7):raise RuntimeError('Rust observer/Python independent numerical difference')
        self.error=np.maximum(self.error,errors);self.calls+=1;self.input.state=out.next_state
        return estimate,correction,command,errors
    def receipt(self):return dict(backend='rust-cdylib',successful_calls=self.calls,library_sha256=self.hash,maximum_force_difference_n=float(self.error[0]),maximum_moment_difference_nm=float(self.error[1]),maximum_correction_difference_n=float(self.error[2]),physical_output_authorised=False)

class RustActuators:
    def __init__(self,binary,cfg,a,groups,initial_currents,d=None):
        self.a=a;self.groups=groups;self.n=144+len(groups);d=drive.load() if d is None else d;s=d['support'];coil=drive.support(d);self.sequence=0;self.support_bus=s['bus_v']
        self.process=subprocess.Popen([str(binary),'144',str(len(groups)),str(round(a['outer_step_s']*1e9)),str(round(a['current_step_s']*1e9)),cfg['configuration_sha256']],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
        for current in initial_currents:
            scale=(s['turns_per_coil']/50.)**2
            values=[coil['coil']['resistance_hot_ohm'],coil['lift_inductance_hypothesis_h'],a['support_kp_v_per_a']*scale,a['support_ki_v_per_a_s']*scale,s['peak_current_a'],current,coil['coil']['copper_kg'],a['initial_copper_temperature_c']]
            self.process.stdin.write(' '.join(format(float(v),'.17g') for v in values)+'\n')
        wire=drive.copper(d,a['turns'],1.5,a['conductor_area_mm2'],s['hot_copper_temperature_c'])
        for g in groups:
            count=g['cassettes_per_face'];R=wire['resistance_hot_ohm']*count*2*5;L=launch.load()['inductance_one_turn_175m_h']*a['turns']**2*g['length_m']/175.;mass=wire['copper_kg']*count*2*15
            values=[R,L,a['wayside_kp_v_per_a'],a['wayside_ki_v_per_a_s'],launch.load()['maximum_phase_current_a'],0.,mass,a['initial_copper_temperature_c']]
            self.process.stdin.write(' '.join(format(float(v),'.17g') for v in values)+'\n')
        self.process.stdin.flush()
    def tick(self,currents,emf,gaps,wayside,*,fault=0):
        self.sequence+=1;values=[self.sequence,fault,self.support_bus,self.a['dc_bus_v']]
        values.extend(np.column_stack((currents,emf,gaps)).ravel());values.extend(np.asarray(wayside).ravel())
        self.process.stdin.write(' '.join(format(float(v),'.13g') for v in values)+'\n');self.process.stdin.flush();line=self.process.stdout.readline()
        if not line.startswith('OK '):raise RuntimeError(line.strip() or 'pilot current process ended')
        words=line.split();numbers=np.array([float(x) for x in words[1:]])
        if len(numbers)!=9+2*self.n or not np.all(np.isfinite(numbers)):raise RuntimeError('invalid pilot current response')
        return dict(voltage_limited_frames=int(numbers[0]),copper_heat_j=numbers[1],dc_signed_j=numbers[2],maximum_temperature_c=numbers[3],peak_current_a=numbers[4],peak_voltage_v=numbers[5],emf_work_j=numbers[6],field_change_j=numbers[7],rl_residual_j=numbers[8],currents_ab=numbers[9:].reshape(self.n,2))
    def close(self):
        if self.process.stdin and not self.process.stdin.closed:self.process.stdin.close()
        try:self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:self.process.kill();self.process.wait()
        if self.process.stdout:self.process.stdout.close()
        if self.process.stderr:self.process.stderr.close()
    def __enter__(self):return self
    def __exit__(self,*_):self.close()

class GroupPlant:
    """Vectorized finite-band overlap, full local phase budget and field slopes."""
    def __init__(self,groups,a,d=None):
        self.d=drive.load() if d is None else d;self.l=self.d['launch'];self.v=station.load()['vehicle'];self.a=a
        self.k=math.pi/self.l['pole_pitch_m'];self.start=np.array([g['start_m'] for g in groups])[:,None];self.end=np.array([g['end_m'] for g in groups])[:,None]
        self.zones=np.array([g['zone_id'] for g in groups],dtype=object)
        wire=drive.copper(self.d,a['turns'],1.5,a['conductor_area_mm2'],self.l['hot_copper_temperature_c'])
        self.R=np.array([wire['resistance_hot_ohm']*g['cassettes_per_face']*2*5 for g in groups])
        self.coefficient=self.l['faces']/self.l['cassette_m']*5*a['turns']*self.l['useful_fundamental_flux_t']*2*self.l['pole_pitch_m']/math.pi*self.l['face_width_m']
    def state(self,centres,velocity,gaps,vertical_velocity,force_request,profile_phase):
        k=self.k;l=self.l;v=self.v;front=centres+v['body_length_m']/2+np.arange(6)*(v['body_length_m']+v['coupling_gap_m'])
        fixed=(l['position_uncertainty_um']+l['registration_uncertainty_um']+l['thermal_index_uncertainty_um'])*1e-6+max(0.,float(np.max(velocity)))*l['time_uncertainty_ns']*1e-9
        fixed+=l['mechanical_phase_allowance_mdeg']/360000.*(2*l['pole_pitch_m'])
        lower=centres-v['magnetic_band_m_per_car']/2;upper=centres+v['magnetic_band_m_per_car']/2
        overlap=np.maximum(0.,np.minimum(upper,self.end)-np.maximum(lower,self.start))
        derivative=((upper<self.end).astype(float)-(lower>self.start).astype(float))*(overlap>0)
        decay=np.exp(-k*(gaps.mean(axis=1)-self.d['support']['gap_m']));psi=self.coefficient*overlap*decay;dx=self.coefficient*derivative*decay
        total=psi.sum(axis=1);active=psi>1e-9;reference=np.divide((psi*front).sum(axis=1),total,out=np.full(len(total),front[0]),where=total>1e-12)
        measured=reference+fixed;theta=k*(front-self.start);phase=(k*(measured-self.start[:,0]))%(2*math.pi);relative=k*(front-measured[:,None])
        dynamic=np.max(np.where(active,np.abs(k*(front-reference[:,None])),0.),axis=1)
        guard=np.where(total>1e-12,dynamic+k*abs(fixed),0.)*180000/math.pi
        exp=np.exp(1j*theta);linkage=(psi*exp).sum(axis=1);change=(((dx+1j*k*psi)*velocity-k*psi*vertical_velocity)*exp).sum(axis=1)
        K=1.5*k*(psi*np.cos(relative)).sum(axis=1);enabled=self.zones==profile_phase;den=np.where(enabled,K*K/self.R,0.).sum()
        q=np.where(enabled,force_request*K/self.R/max(1e-12,den),0.);omega=k*np.divide((psi*velocity).sum(axis=1),total,out=np.zeros(len(total)),where=total>1e-12)
        demands=np.column_stack((q,(phase*180000/math.pi)%360000,guard,omega,np.abs(linkage),change.real,change.imag,np.zeros(len(q))))
        return dict(psi=psi,dx=dx,theta=theta,phase=phase,phase_error_mdeg=guard,emf=change,K=K,enabled=enabled,linkage=linkage,relative=relative,
            normal_positions_m=(np.minimum(upper,self.end)+np.maximum(lower,self.start))/2),demands

def powered_group_state(groups,centres,velocity,gaps,vertical_velocity,force_request,profile_phase,a,_context=None):
    d=drive.load() if _context is None else _context[0]
    fields,demands=GroupPlant(groups,a,d).state(centres,velocity,gaps,vertical_velocity,force_request,profile_phase)
    return [{k:v[i] for k,v in fields.items()} for i in range(len(groups))],demands.tolist()

def selected_configuration():return variant_configuration(load()['preferred_body_variant'],load()['preferred_winding_variant'])[0]

def normal_wrench_observer(sample,k,dt):
    # Virtual phase/current/gap observations from the previous accepted frame.
    # Identical-map calibration is unqualified; full ±10% scale cases are mandatory.
    if sample is None:return np.zeros((6,3))
    fields,speed,currents,centres=sample
    local=(currents[:,0]+1j*currents[:,1])[:,None]*np.exp(-1j*(fields['theta']+k*speed*dt))
    term=1.5*k*fields['psi']*local.real
    return np.column_stack((term.sum(axis=0),np.zeros(6),-(term*(fields['normal_positions_m']-centres)).sum(axis=0)))

NORMAL_MAP=np.stack((np.ones(24),moving.Y,-moving.X))
NORMAL_ALLOCATION=NORMAL_MAP.T@np.linalg.inv(NORMAL_MAP@NORMAL_MAP.T)

def normal_force_correction(wrench):return -np.asarray(wrench)@NORMAL_ALLOCATION.T

def simulate(binary,*,duration_s=None,fault=0,fault_time_s=1.,assumptions=None,body_variant='gfrp-control',winding_variant='retained-50t16mm2',start_time_s=0.,estimator_scale=1.,observer_library=None):
    a=load() if assumptions is None else dict(assumptions);cfg,d=variant_configuration(body_variant,winding_variant)
    p=motion_profile(cfg);dt=a['outer_step_s'];runtime=p['inputs']['runtime_s'];duration=runtime-start_time_s if duration_s is None else duration_s
    if not 0<=start_time_s<runtime or estimator_scale not in a['normal_feedforward_scales'] or not .02<=duration<=runtime-start_time_s+1e-8 or abs(duration/dt-round(duration/dt))>1e-7:raise ValueError('bounded integer current-coupled duration required')
    m=moving.load();mass=cfg['controlled_aw3_kg'];m.update(car_mass_kg=mass,coupler_stiffness_n_m=cfg['body']['longitudinal_stiffness_n_m'])
    beam=moving.MovingGuideway(m,p['inputs']['distance_m'],dt);chain=moving.CouplerChain(mass,m['coupler_stiffness_n_m'],m['coupler_damping_n_s_m'],dt)
    pitch=m['body_length_m']+m['coupling_gap_m'];offset=-m['body_length_m']/2-np.arange(6)*pitch;initial_ref=launch.corridor.trajectory_at(p,start_time_s);positions=((initial_ref['position_m']+offset)[:,None]+moving.X).ravel();weight=mass*station.G
    beam.initialise_static(positions,np.full(144,weight/24));local=beam.displacement(positions).reshape(6,24);body=np.linalg.lstsq(moving.FIT,local.T,rcond=None)[0].T;velocity=np.zeros((6,3))
    support_sample=d['support'];k=math.pi/d['launch']['pole_pitch_m'];context=(d,station.load()['vehicle'])
    gaps=m['gap_target_m']+body@moving.FIT.T-local;initial=lift_current(np.full(144,weight/24),gaps.ravel(),support_sample);previous_gap=gaps.copy();previous_current=initial.copy()
    groups=launch.group_geometry(p,a['groups_per_direction']);group_plant=GroupPlant(groups,a,d);inertia=np.array([mass,m['inertia_roll_kg_m2'],m['inertia_pitch_kg_m2']]);nsettle=round(a['settle_s']/dt);nmove=round(duration/dt);trace=[];failure=None;stop=False
    extrema=dict(minimum_gap_m=math.inf,maximum_gap_m=-math.inf,peak_flux_t=0.,peak_lift_current_a=0.,peak_wayside_current_a=0.,peak_group_phase_error_mdeg=0.,maximum_intercar_phase_spread_degrees=0.,maximum_temperature_c=0.,peak_phase_voltage_v=0.,peak_module_force_n=0.,peak_unwanted_normal_force_n=0.,rl_energy_residual_max_j=0.)
    heat=dc=emfwork=field=0.;limited=0;completed=0;requested=0.;actual=0.;stride=round(a['trace_interval_s']/dt);injected_at=None;fault_observed=None
    witness=[];window=[];last_success_tick=0;maximum_position_error=0.;end_state=None;observer_sample=None;ff_enabled=cfg['support_power_stage']['normal_wrench_feedforward'];rust_observer=RustNormalObserver(observer_library or build_observer()[0],cfg,groups,k,estimator_scale) if ff_enabled else None
    allocator_binary,_=moving.build_bridge()
    with moving.RustTrain(allocator_binary,m,dt) as allocator,RustActuators(binary,cfg,a,groups,initial,d) as actuators:
        for tick in range(nsettle+nmove):
            moving_now=tick>=nsettle;time=start_time_s+max(0,tick-nsettle)*dt;ref=launch.corridor.trajectory_at(p,time);mid=launch.corridor.trajectory_at(p,min(runtime,time+dt/2)) if moving_now else ref
            centres=ref['position_m']+offset+chain.u;positions=(centres[:,None]+moving.X).ravel();local=beam.displacement(positions).reshape(6,24)
            gaps=m['gap_target_m']+body@moving.FIT.T-local
            if float(gaps.min())<m['gap_minimum_m'] or float(gaps.max())>m['gap_maximum_m']:failure='independent physical gap outside envelope';break
            try:desired,stopped=allocator.tick(tick+1,gaps)
            except RuntimeError as exc:failure=str(exc);break
            stop|=stopped
            try:
                if rust_observer is not None:estimate,correction,command,observer_error=rust_observer.step(tick+1,desired,observer_sample,k,dt)
                else:estimate=np.zeros((6,3));correction=np.zeros((6,24));command=desired;observer_error=np.zeros(3)
            except RuntimeError as exc:failure=str(exc);break
            if np.any(command<0) or np.any(command>20000):failure='feedforward support allocation outside declared bounds';break
            desired_current=lift_current(command.ravel(),gaps.ravel(),support_sample);gap_speed=(gaps-previous_gap)/dt
            mu=4*math.pi*1e-7;s=support_sample;B=(s['bias_flux_t']*s['series_gaps']*s['gap_m']+mu*s['turns_per_coil']*previous_current)/(s['series_gaps']*gaps.ravel())
            linkage=s['turns_per_coil']*s['pole_area_m2']*B;back=-linkage/gaps.ravel()*gap_speed.ravel()
            speed=mid['speed_m_s']+chain.velocity if moving_now else np.zeros(6);r=p['resistance'];resist=r['constant_n_per_car']+r['quadratic_n_per_car_per_m_s_squared']*np.maximum(0.,speed)**2
            force_request=0. if mid['phase']=='coast' or not moving_now else 6*mass*mid['acceleration_m_s2']+float(resist.sum())
            fields,demands=group_plant.state(centres,speed,gaps,gap_speed.mean(axis=1),force_request,mid['zone_id'] if moving_now else None)
            triggered=fault if moving_now and time-start_time_s>=fault_time_s else 0
            if triggered and injected_at is None:injected_at=time-start_time_s
            try:out=actuators.tick(desired_current,back,gaps.ravel(),demands,fault=triggered)
            except RuntimeError as exc:
                failure=str(exc)
                if triggered:fault_observed=failure
                break
            current=out['currents_ab'][:144,0];forces,flux=lift_force(current,gaps.ravel(),support_sample);forces=forces.reshape(6,24);normal=np.zeros(6);normal_moment=np.zeros(6);applied=np.zeros(6);normal_positions=[];normal_loads=[]
            currents=out['currents_ab'][144:]
            local_i=(currents[:,0]+1j*currents[:,1])[:,None]*np.exp(-1j*(fields['theta']+k*speed*dt))
            applied=1.5*(fields['dx']*local_i.real+k*fields['psi']*local_i.imag).sum(axis=0)
            term=1.5*k*fields['psi']*local_i.real;normal=term.sum(axis=0);normal_moment=(term*(fields['normal_positions_m']-centres)).sum(axis=0)
            observer_sample=(fields,speed.copy(),currents.copy(),centres.copy())
            mask=np.abs(term)>1e-10;normal_positions=fields['normal_positions_m'][mask];normal_loads=term[mask]
            force_sum=forces.sum(axis=1)+normal
            generalized=np.column_stack((weight-force_sum,forces@moving.Y,-forces@moving.X-normal_moment));acc=generalized/inertia
            body+=velocity*dt+.5*acc*dt**2;velocity+=acc*dt
            if moving_now:
                chain.step(applied-resist-mass*mid['acceleration_m_s2']);completed+=1;requested+=force_request*mid['speed_m_s']*dt;actual+=float(applied@speed)*dt
            maximum_position_error=max(maximum_position_error,float(np.max(np.abs(chain.u))))
            beam.advance(np.concatenate((positions,np.array(normal_positions))),np.concatenate((forces.ravel(),np.array(normal_loads))));previous_gap=gaps.copy();previous_current=current.copy()
            next_ref=launch.corridor.trajectory_at(p,min(runtime,start_time_s+completed*dt))
            next_centres=next_ref['position_m']+offset+chain.u;next_local=beam.displacement((next_centres[:,None]+moving.X).ravel()).reshape(6,24)
            next_gaps=m['gap_target_m']+body@moving.FIT.T-next_local
            observed_min=min(float(gaps.min()),float(next_gaps.min()));observed_max=max(float(gaps.max()),float(next_gaps.max()))
            # Every updated mechanical pose, including the final frame, is checked.
            end_state=dict(last_outer_tick=tick+1,car_centres_m=next_centres.tolist(),body_down_roll_pitch=body.tolist(),guideway_displacement_m=next_local.tolist(),physical_gap_m=next_gaps.tolist())
            if observed_min<m['gap_minimum_m'] or observed_max>m['gap_maximum_m']:failure='independent post-step physical gap outside envelope'
            _,next_flux=lift_force(current,next_gaps.ravel(),support_sample)
            observed_flux=max(float(np.abs(flux).max()),float(np.abs(next_flux).max()))
            heat+=out['copper_heat_j'];dc+=out['dc_signed_j'];emfwork+=out['emf_work_j'];field+=out['field_change_j'];limited+=out['voltage_limited_frames']
            extrema['minimum_gap_m']=min(extrema['minimum_gap_m'],observed_min);extrema['maximum_gap_m']=max(extrema['maximum_gap_m'],observed_max);extrema['peak_flux_t']=max(extrema['peak_flux_t'],observed_flux);extrema['peak_lift_current_a']=max(extrema['peak_lift_current_a'],float(np.abs(current).max()))
            extrema['peak_wayside_current_a']=max(extrema['peak_wayside_current_a'],float(np.linalg.norm(out['currents_ab'][144:],axis=1).max()));extrema['peak_group_phase_error_mdeg']=max(extrema['peak_group_phase_error_mdeg'],float(fields['phase_error_mdeg'].max()));extrema['maximum_intercar_phase_spread_degrees']=max(extrema['maximum_intercar_phase_spread_degrees'],float(np.ptp(chain.u))*360/.5)
            for key,target in [('maximum_temperature_c','maximum_temperature_c'),('peak_phase_voltage_v','peak_voltage_v'),('rl_energy_residual_max_j','rl_residual_j')]:extrema[key]=max(extrema[key],out[target])
            extrema['peak_module_force_n']=max(extrema['peak_module_force_n'],float(forces.max()));extrema['peak_unwanted_normal_force_n']=max(extrema['peak_unwanted_normal_force_n'],float(np.abs(normal).max()))
            next_speed=launch.corridor.trajectory_at(p,min(runtime,start_time_s+completed*dt))['speed_m_s']+chain.velocity
            window.append([observed_min,observed_max,float(np.abs(current).max()),float(np.linalg.norm(out['currents_ab'][144:],axis=1).max()),float(out['peak_voltage_v']),observed_flux,float(out['maximum_temperature_c']),float(fields['phase_error_mdeg'].max()),float(np.abs(normal).max()),float(forces.max()),out['voltage_limited_frames'],float(out['copper_heat_j']),float(out['dc_signed_j']),float(out['emf_work_j']),float(out['field_change_j']),float(out['rl_residual_j']),float(np.ptp(chain.u))*720,float(np.max(np.abs(chain.u))),float(np.max(np.abs(next_speed))),float(np.abs(estimate[:,0]).max()),float(np.abs(estimate[:,2]).max()),float(np.abs(correction).max()),*observer_error.tolist()])
            last_success_tick=tick+1
            if len(window)==10 or tick==nsettle+nmove-1:
                arr=np.array(window);row=[tick+1,len(window),float(arr[:,0].min())]+[float(arr[:,j].max()) for j in range(1,10)]+[float(arr[:,j].sum()) for j in range(10,15)]+[float(arr[:,15].max()),float(arr[:,16].max()),float(arr[:,17].max()),float(arr[-1,18]),float(arr[:,19].max()),float(arr[:,20].max()),float(arr[:,21].max()),*[float(arr[:,j].max()) for j in range(22,25)]];witness.append(row);window=[]
            if moving_now and (completed%stride==0 or completed==nmove):trace.append(dict(time_s=(completed)*dt,car_relative_x_m=chain.u.tolist(),car_actual_speed_m_s=(mid['speed_m_s']+chain.velocity).tolist(),minimum_gap_m=observed_min,maximum_gap_m=observed_max,peak_lift_current_a=float(np.abs(current).max()),phase_reference_mdeg=demands[:,1].tolist(),group_phase_error_mdeg=fields['phase_error_mdeg'].tolist(),body_down_roll_pitch=body.tolist()))
            if failure is not None:break
            if extrema['peak_flux_t']>a['maximum_flux_screen_t']:failure='assumed gap-field screen exceeded';break
            if triggered==9 and out['voltage_limited_frames']:
                failure='current-loop voltage saturation (Saturation)';fault_observed=failure;break
    end=launch.corridor.trajectory_at(p,min(runtime,start_time_s+completed*dt));position_error=maximum_position_error;arrival_speed=float(np.max(np.abs(end['speed_m_s']+chain.velocity)))
    if not math.isfinite(extrema['minimum_gap_m']):extrema['minimum_gap_m']=extrema['maximum_gap_m']=0.
    if window:
        arr=np.array(window);witness.append([last_success_tick,len(window),float(arr[:,0].min())]+[float(arr[:,j].max()) for j in range(1,10)]+[float(arr[:,j].sum()) for j in range(10,15)]+[float(arr[:,15].max()),float(arr[:,16].max()),float(arr[:,17].max()),float(arr[-1,18]),float(arr[:,19].max()),float(arr[:,20].max()),float(arr[:,21].max()),*[float(arr[:,j].max()) for j in range(22,25)]])
    screens=dict(completed=failure is None and completed==nmove and not stop,gap=m['gap_minimum_m']<=extrema['minimum_gap_m']<=extrema['maximum_gap_m']<=m['gap_maximum_m'],
        no_voltage_saturation=limited==0,continuous_lift_current=extrema['peak_lift_current_a']<=support_sample['continuous_current_a'],flux=extrema['peak_flux_t']<=a['maximum_flux_screen_t'],
        temperature=extrema['maximum_temperature_c']<=support_sample['insulation_temperature_screen_c'],local_group_phase=extrema['peak_group_phase_error_mdeg']<=a['maximum_phase_error_mdeg'],
        rl_energy_balance=extrema['rl_energy_residual_max_j']<1e-5,arrival_position=position_error<=a['maximum_position_error_m'],arrival_speed=start_time_s+duration<runtime-1e-9 or arrival_speed<=a['maximum_arrival_speed_m_s'])
    coil=drive.support(d);packaging=candidate_packaging(winding_variant)
    thermal=dict(wire_current_density_a_mm2=extrema['peak_lift_current_a']/support_sample['conductor_area_mm2'],baseline_limit_a_mm2=a['baseline_wire_current_density_a_mm2'],
        peak_continuous_copper_w_per_coil=extrema['peak_lift_current_a']**2*coil['coil']['resistance_hot_ohm'],allocated_continuous_copper_heat_w_per_coil=cfg['magnetic']['continuous_copper_heat_budget_w_per_coil'],
        copper_kg_per_car=coil['copper_kg_per_car'],mean_turn_length_m=support_sample['mean_turn_length_m'],packing_fraction=coil['packing_fraction'],cooling_qualified=False)
    screens.update(wire_current_density=thermal['wire_current_density_a_mm2']<=a['baseline_wire_current_density_a_mm2'],continuous_cooling=thermal['peak_continuous_copper_w_per_coil']<=thermal['allocated_continuous_copper_heat_w_per_coil'],
        winding_pack=coil['packing_screen'],packaging_path=packaging['path']['clear_under_declared_box_bounds'] and not packaging['internal_bound_intersections'])
    observer_receipt=rust_observer.receipt() if rust_observer is not None else dict(backend='disabled',successful_calls=0,physical_output_authorised=False)
    screens['rust_normal_observer']=rust_observer is None or (rust_observer.calls>0 and bool(np.all(rust_observer.error<=1e-7)))
    screens={k:bool(v) for k,v in screens.items()}
    return dict(schema='osr-pilot-actuator-run/1',configuration=cfg,configuration_sha256=cfg['configuration_sha256'],profile=p,profile_sha256=digest(encoded(p)),assumptions=a,body_variant=body_variant,winding_variant=winding_variant,requested_duration_s=duration,start_time_s=start_time_s,estimator_scale=estimator_scale,case_id=f'estimator-{estimator_scale:.1f}',observer_execution=observer_receipt,feedforward=dict(enabled=ff_enabled,maximum_observation_age_s=dt,applied_through_current_command=True,calibrated_phase_and_field_map_qualified=False),fault=fault,fault_time_s=fault_time_s,fault_injected_at_s=injected_at,fault_observed=fault_observed,
        actual_rust_current_kernel=True,ideal_force_benchmark_retained_separately=True,planned_moving_steps=nmove,completed_moving_steps=completed,executed_duration_s=completed*dt,failure=failure,controlled_stop_seen=bool(stop),
        extrema=extrema,voltage_limited_microsteps=limited,copper_heat_j=heat,dc_signed_input_j=dc,emf_transfer_j=emfwork,current_field_energy_change_j=field,
        rl_energy_residual_j=dc-heat-emfwork-field,requested_trajectory_motor_work_j=requested,actual_motor_work_j=actual,maximum_position_error_m=position_error,arrival_maximum_speed_m_s=arrival_speed,
        screens=screens,study_pass=all(screens.values()),thermal=thermal,end_state=end_state,magnetic_geometry=magnetic_geometry_hold(d),packaging={k:v for k,v in packaging.items() if k!='definition'},trace=trace,groups=groups,window_witness=dict(schema='osr-actuator-window-witness/1',window_max_steps=10,columns=['last_outer_tick','count','gap_min','gap_max','lift_current_max','wayside_current_max','phase_voltage_max','flux_max','temperature_max','local_phase_max','normal_force_max','module_force_max','limited_microsteps_sum','copper_heat_sum','dc_signed_sum','emf_transfer_sum','field_change_sum','rl_residual_max','intercar_spread_max','position_error_max','last_speed','estimated_normal_force_max','estimated_pitch_moment_max','feedforward_module_correction_max','observer_force_difference_max','observer_moment_difference_max','observer_correction_difference_max'],rows=witness),
        scope='Six rigid bodies, moving pinned guideway and lumped drilled-body/coupler chain;20kHz actual Rust PI current kernels, independent exact stationary RL plant, assumed gap-reluctance support and harmonic LSM coenergy derivatives.1kHz mechanical coupling and virtual phase observations. Lateral/guide circuits, measured saturation/shared fields/magnetic loss map, converter switching/cooling and hardware timing remain open.',**FLAGS)

def full_case(binary,scale):
    return simulate(binary,body_variant=load()['preferred_body_variant'],winding_variant=load()['preferred_winding_variant'],estimator_scale=scale)

def full_eligible(r):
    cases=r.get('full_estimator_cases',[]);scales=load()['normal_feedforward_scales'];cfg=selected_configuration()['configuration_sha256']
    return (len(cases)==len(scales) and [x['estimator_scale'] for x in cases]==scales and all(
        x['configuration_sha256']==cfg and x['start_time_s']==0 and x['requested_duration_s']==x['profile']['inputs']['runtime_s'] and x['completed_moving_steps']==x['planned_moving_steps'] and x['study_pass'] and pilot_limits.actual_module_force(x)['passed'] for x in cases)
        and len(r['controls'])==len(FAULTS) and [c['fault'] for c in r['controls']]==list(FAULTS)
        and all(c['expected_hold'] and c['run']['configuration_sha256']==cfg for c in r['controls']))

def study():
    binary,receipt=build_bridge();_,observer_receipt=build_observer();receipt['normal_wrench_observer']=observer_receipt;before=sources();nominal=simulate(binary,duration_s=2.);controls=[]
    intermediate=simulate(binary,duration_s=2.,body_variant='steel-wall-004',winding_variant='equal-copper-80t10mm2')
    rewound=simulate(binary,duration_s=2.,body_variant='steel-wall-004',winding_variant='equal-copper-100t8mm2')
    with ProcessPoolExecutor(max_workers=3) as pool:full=list(pool.map(full_case,[binary]*3,load()['normal_feedforward_scales']))
    repair=next(x for x in full if x['estimator_scale']==1.)
    for fault in FAULTS:
        r=simulate(binary,duration_s=1.1,fault=fault,fault_time_s=1.,body_variant=load()['preferred_body_variant'],winding_variant=load()['preferred_winding_variant'])
        reason=FAULTS[fault]
        controls.append(dict(fault=fault,expected_fault=reason,expected_hold=r['fault_injected_at_s'] is not None and r['fault_observed'] is not None and '('+reason+')' in r['fault_observed'] and not r['study_pass'],run=r))
    if before!=sources():raise ValueError('actuator sources changed during run')
    result=dict(schema=SCHEMA,revision=load()['revision'],full_estimator_cases=full,nominal=nominal,repair_candidates=[intermediate,rewound,repair],controls=controls,execution=receipt,
        digital_execution_complete=True,model_feasibility=False,all_negative_controls_held=all(r['expected_hold'] for r in controls),
        qualified_configuration_sha256=repair['configuration_sha256'],control_configuration_sha256=controls[0]['run']['configuration_sha256'],
        qualification_scope='Executed offline winding and control cases for this exact candidate; no physical or hardware qualification',
        holds=['Assumed25,000mm² gap pole area versus9,600mm² winding aperture: pole shoe/core neck/yoke flux geometry and saturation remain unreconciled; gap-field pass does not close this hold','Support/LSM maps, shared PM flux, saturation/core/eddy losses and temperature qualification','Lateral/guidance dynamics and all omitted current circuits','Complete converter/DC/brake/cooling/electrical fault energy and physical timing','Whole equipped-body mass/CG/inertia and joined load paths remain unaccepted','One-frame normal-wrench observer uses unqualified calibrated phase/current/gap maps; full0.9/1.0/1.1scale cases are required, not a physical robustness proof'],**FLAGS)
    result['model_feasibility']=bool(full_eligible(result));return result

def validate_run(r):
    cfg,d=variant_configuration(r['body_variant'],r['winding_variant'])
    if r.get('configuration')!=cfg or r.get('configuration_sha256')!=cfg['configuration_sha256'] or r.get('profile_sha256')!=digest(encoded(r['profile'])):raise ValueError('actuator exact configuration/profile mismatch')
    if r.get('case_id')!=f"estimator-{r['estimator_scale']:.1f}":raise ValueError('estimator case identity differs')
    if r.get('start_time_s',-1)<0 or r.get('estimator_scale') not in load()['normal_feedforward_scales']:raise ValueError('exact bounded diagnostic/estimator case required')
    if r.get('assumptions')!=load() or r['planned_moving_steps']!=round(r['requested_duration_s']/load()['outer_step_s']):raise ValueError('actuator exact assumptions/window mismatch')
    expected_profile=motion_profile(cfg)
    if r['profile']!=expected_profile or r['groups']!=launch.group_geometry(expected_profile,load()['groups_per_direction']):raise ValueError('actuator exact motion/group definition differs')
    if not 0<=r['completed_moving_steps']<=r['planned_moving_steps'] or r['executed_duration_s']!=r['completed_moving_steps']*load()['outer_step_s']:raise ValueError('actuator completion counts differ')
    if abs(r['rl_energy_residual_j']-(r['dc_signed_input_j']-r['copper_heat_j']-r['emf_transfer_j']-r['current_field_energy_change_j']))>1e-8:raise ValueError('actuator RL arithmetic differs')
    if r['study_pass']!=all(r['screens'].values()) or any(r.get(k) is not False for k in FLAGS):raise ValueError('actuator screens/release differ')
    if r['copper_heat_j']<=0 or not r['actual_rust_current_kernel'] or not r['ideal_force_benchmark_retained_separately']:raise ValueError('executed current/heat evidence required')
    if any(not math.isfinite(float(x)) for x in r['extrema'].values()):raise ValueError('finite actuator extrema required')
    w=r.get('window_witness',{});rows=np.asarray(w.get('rows',[]),dtype=float)
    if w.get('schema')!='osr-actuator-window-witness/1' or w.get('window_max_steps')!=10 or rows.ndim!=2 or rows.shape[1]!=27 or not len(rows) or not np.all(np.isfinite(rows)):raise ValueError('bounded complete actuator window witness required')
    if len(rows)>math.ceil((load()['settle_s']+r['requested_duration_s'])/load()['outer_step_s']/10)+1 or np.any(rows[:,1]<1) or np.any(rows[:,1]>10) or np.any(np.diff(np.r_[0.,rows[:,0]])!=rows[:,1]):raise ValueError('actuator witness cadence/count differs')
    ff=dict(enabled=cfg['support_power_stage']['normal_wrench_feedforward'],maximum_observation_age_s=load()['outer_step_s'],applied_through_current_command=True,calibrated_phase_and_field_map_qualified=False)
    if r.get('feedforward')!=ff or (not ff['enabled'] and np.any(rows[:,21:]!=0)):raise ValueError('declared one-frame observer/current-only application differs')
    expected_steps=round(load()['settle_s']/load()['outer_step_s'])+r['completed_moving_steps']
    observer=r.get('observer_execution',{})
    if ff['enabled']:
        if observer.get('backend')!='rust-cdylib' or observer.get('physical_output_authorised') is not False or observer.get('successful_calls') not in {expected_steps,expected_steps+1}:raise ValueError('actual complete offline Rust observer execution required')
        if observer['successful_calls']!=expected_steps and r['failure'] is None:raise ValueError('extra Rust observer call requires recorded held mechanical frame')
        h=observer.get('library_sha256','')
        if len(h)!=64 or any(c not in '0123456789abcdef' for c in h):raise ValueError('exact executed Rust observer artifact hash required')
        for key,col in [('maximum_force_difference_n',24),('maximum_moment_difference_nm',25),('maximum_correction_difference_n',26)]:
            if not math.isclose(observer.get(key,float('inf')),float(rows[:,col].max()),abs_tol=1e-7):raise ValueError('observer differential witness differs')
    elif observer!={'backend':'disabled','successful_calls':0,'physical_output_authorised':False} or np.any(rows[:,24:]!=0):raise ValueError('disabled observer execution differs')
    if int(rows[-1,0])!=expected_steps:raise ValueError('actuator witness executed coverage differs')
    if np.any(rows[:,13]<=0) or np.any(rows[:,2]<=0) or np.any(rows[:,2]>rows[:,3]):raise ValueError('actuator witness must retain physical gap and positive copper heat')
    extrema={'minimum_gap_m':float(rows[:,2].min()),'maximum_gap_m':float(rows[:,3].max()),'peak_lift_current_a':float(rows[:,4].max()),'peak_wayside_current_a':float(rows[:,5].max()),'peak_phase_voltage_v':float(rows[:,6].max()),'peak_flux_t':float(rows[:,7].max()),'maximum_temperature_c':float(rows[:,8].max()),'peak_group_phase_error_mdeg':float(rows[:,9].max()),'peak_unwanted_normal_force_n':float(rows[:,10].max()),'peak_module_force_n':float(rows[:,11].max()),'rl_energy_residual_max_j':float(rows[:,17].max()),'maximum_intercar_phase_spread_degrees':float(rows[:,18].max())}
    if any(not math.isclose(r['extrema'][k],v,rel_tol=1e-12,abs_tol=1e-10) for k,v in extrema.items()):raise ValueError('actuator extrema differ from all executed windows')
    for key,col in [('voltage_limited_microsteps',12),('copper_heat_j',13),('dc_signed_input_j',14),('emf_transfer_j',15),('current_field_energy_change_j',16)]:
        if not math.isclose(r[key],float(rows[:,col].sum()),rel_tol=1e-11,abs_tol=1e-6):raise ValueError('actuator energy/current witness differs: '+key)
    if not math.isclose(r['maximum_position_error_m'],float(rows[:,19].max()),abs_tol=1e-10) or not math.isclose(r['arrival_maximum_speed_m_s'],float(rows[-1,20]),abs_tol=1e-10):raise ValueError('actuator motion witness differs')
    aa=load();s=cfg['magnetic']['support_winding'];m=moving.load()
    end=r.get('end_state')
    if not isinstance(end,dict) or end.get('last_outer_tick')!=int(rows[-1,0]):raise ValueError('final post-step gap checkpoint required')
    body=np.asarray(end.get('body_down_roll_pitch'),dtype=float);local=np.asarray(end.get('guideway_displacement_m'),dtype=float);gap=np.asarray(end.get('physical_gap_m'),dtype=float);centres=np.asarray(end.get('car_centres_m'),dtype=float)
    if body.shape!=(6,3) or local.shape!=(6,24) or gap.shape!=(6,24) or centres.shape!=(6,) or not all(np.all(np.isfinite(x)) for x in (body,local,gap,centres)):raise ValueError('finite final six-car body/guideway/gap checkpoint required')
    if not np.allclose(gap,m['gap_target_m']+body@moving.FIT.T-local,rtol=0.,atol=1e-12):raise ValueError('post-step physical gap arithmetic differs')
    if not extrema['minimum_gap_m']-1e-12<=float(gap.min())<=float(gap.max())<=extrema['maximum_gap_m']+1e-12:raise ValueError('post-step physical gap outside retained extrema')
    if r.get('magnetic_geometry')!=magnetic_geometry_hold(d):raise ValueError('magnetic core/window reconciliation hold differs')
    expected_screens=dict(completed=r['failure'] is None and r['completed_moving_steps']==r['planned_moving_steps'] and not r['controlled_stop_seen'],gap=m['gap_minimum_m']<=extrema['minimum_gap_m']<=extrema['maximum_gap_m']<=m['gap_maximum_m'],no_voltage_saturation=r['voltage_limited_microsteps']==0,continuous_lift_current=extrema['peak_lift_current_a']<=s['continuous_current_a'],flux=extrema['peak_flux_t']<=aa['maximum_flux_screen_t'],temperature=extrema['maximum_temperature_c']<=s['insulation_temperature_screen_c'],local_group_phase=extrema['peak_group_phase_error_mdeg']<=aa['maximum_phase_error_mdeg'],rl_energy_balance=extrema['rl_energy_residual_max_j']<1e-5,arrival_position=r['maximum_position_error_m']<=aa['maximum_position_error_m'],arrival_speed=r['start_time_s']+r['requested_duration_s']<r['profile']['inputs']['runtime_s']-1e-9 or r['arrival_maximum_speed_m_s']<=aa['maximum_arrival_speed_m_s'])
    coil=drive.support(d);packaging=candidate_packaging(r['winding_variant'])
    thermal=dict(wire_current_density_a_mm2=extrema['peak_lift_current_a']/s['conductor_area_mm2'],baseline_limit_a_mm2=aa['baseline_wire_current_density_a_mm2'],peak_continuous_copper_w_per_coil=extrema['peak_lift_current_a']**2*coil['coil']['resistance_hot_ohm'],allocated_continuous_copper_heat_w_per_coil=cfg['magnetic']['continuous_copper_heat_budget_w_per_coil'],copper_kg_per_car=coil['copper_kg_per_car'],mean_turn_length_m=s['mean_turn_length_m'],packing_fraction=coil['packing_fraction'],cooling_qualified=False)
    if r.get('thermal')!=thermal or r.get('packaging')!={k:v for k,v in packaging.items() if k!='definition'}:raise ValueError('actuator exact wire/pack/cooling allocation differs')
    expected_screens['rust_normal_observer']=not ff['enabled'] or (observer['successful_calls']>0 and all(observer[key]<=1e-7 for key in ('maximum_force_difference_n','maximum_moment_difference_nm','maximum_correction_difference_n')))
    expected_screens.update(wire_current_density=thermal['wire_current_density_a_mm2']<=aa['baseline_wire_current_density_a_mm2'],continuous_cooling=thermal['peak_continuous_copper_w_per_coil']<=thermal['allocated_continuous_copper_heat_w_per_coil'],winding_pack=coil['packing_screen'],packaging_path=packaging['path']['clear_under_declared_box_bounds'] and not packaging['internal_bound_intersections'])
    if r['screens']!={k:bool(v) for k,v in expected_screens.items()}:raise ValueError('actuator independently derived screens differ')
    stride=round(load()['trace_interval_s']/load()['outer_step_s']);expected_times=[i*stride*load()['outer_step_s'] for i in range(1,r['completed_moving_steps']//stride+1)]
    if r['completed_moving_steps']==r['planned_moving_steps'] and r['completed_moving_steps']%stride:expected_times.append(r['executed_duration_s'])
    if len(r['trace'])!=len(expected_times):raise ValueError('complete actuator sampled motion trace required')
    for row,t in zip(r['trace'],expected_times):
        if not math.isclose(row['time_s'],t,abs_tol=1e-10) or len(row['car_relative_x_m'])!=6 or len(row['car_actual_speed_m_s'])!=6 or len(row['group_phase_error_mdeg'])!=len(r['groups']):raise ValueError('actuator trace cadence/formation differs')
        if not extrema['minimum_gap_m']-1e-10<=row['minimum_gap_m']<=row['maximum_gap_m']<=extrema['maximum_gap_m']+1e-10:raise ValueError('actuator trace gap/summary differs')
    return True

def overview(r):
    n=r['repair_candidates'][-1];return f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="350"><rect width="1100" height="350" fill="#101c2b"/><g fill="white" font-family="sans-serif"><text x="30" y="50" font-size="25">Voltage → actual Rust current → assumed field → moving vehicle</text><text x="30" y="110" font-size="20">Counted steel/higher-copper repair: {n["completed_moving_steps"]} / {n["planned_moving_steps"]} frames</text><text x="30" y="165" font-size="18">Gap {n["extrema"]["minimum_gap_m"]*1000:.3f}–{n["extrema"]["maximum_gap_m"]*1000:.3f} mm; copper heat {n["copper_heat_j"]/3600000.:.3f} kWh</text><text x="30" y="225" font-size="18">Model feasibility: {r["model_feasibility"]}; all fault controls held: {r["all_negative_controls_held"]}</text><text x="30" y="295" font-size="16">Assumed magnetic plant, unqualified materials/timing/guide control. Physical output disabled.</text></g></svg>'

def readme(r):
    return '\n'.join(['# Provisional electrical/magnetic/moving actuator composition','',
        'The retained ideal-force benchmark remains separate. This new execution integrates actual public Rust current controllers with independently solved RL windings, gap-dependent support flux and forces, moving-body/guideway states and local powered-group phase references. Copper heat, DC energy, current/voltage/temperature/phase screens and rejected cases are retained.','',
        f'Nominal executed {r["nominal"]["completed_moving_steps"]}/{r["nominal"]["planned_moving_steps"]} moving frames; numerical feasibility {r["nominal"]["study_pass"]}; failure {r["nominal"]["failure"]}.','',
        *[f'Counted repair {x["body_variant"]}/{x["winding_variant"]}: {x["configuration"]["controlled_aw3_kg"]:,.3f}kg/car AW3; {x["completed_moving_steps"]}/{x["planned_moving_steps"]} frames; numerical pass {x["study_pass"]}; failure {x["failure"]}; current screen {x["screens"]["continuous_lift_current"]}.' for x in r['repair_candidates']],'',
        'Equal-copper rewinds preserve I²R and current density at equal ampere-turns; they cannot cure the thermal failure by relabelling a60A rating. The counted higher-copper candidate derives its700mm mean turn from300×200mm outer and120×80mm inner dimensions,140turns×20mm² in a75mm-deep pack; actual copper, resistance, pack fill and vehicle mass are recalculated. The detachable collector adds its separately derived106.01368kg/car of splice plates and bolts, with no cut-stock removal credit. Additional mount36kg/car and cooling120kg/car with an explicit3× continuous winding heat-rejection allocation are included. The3.75A/mm² baseline wire screen and separate60A drive screen remain unchanged. Coldplate flow/thermal resistance is an unqualified design requirement, and full-trip adiabatic temperature does not qualify continuous duty.','',
        '[Counted higher-copper packaging](candidate-bay.svg) · [Exact candidate bay definition](candidate-bay.json.gz). Existing26.4t hardpoint/civil acceptance is not inherited: the new gross load requires re-evaluation.','',
        'Each group uses a flux-weighted virtual phase reference. The full3degree mechanical/index allowance remains ADDITIONAL to actual car-relative phase and position, timestamp, stator-registration and thermal uncertainties. Worst-case magnitudes are summed against the unchanged5degree local limit. Seventy independently controlled5m groups per direction count140converters at a two-direction station; the actual12m band/17.5m pitch leaves5.5m between bands. Whole-train5degree spread is a distinct historical observation. The adverse index error also enters the physical field and its unwanted normal force.','',
        'The192V/60A support power-stage alternative adds48kg/car of converter allocation plus6kg/car of observer electronics and explicit unquoted prices. An actual standalone Rust observer (bounded by-value ABI) uses the one1ms-frame delayed calibrated phase/current/gap model and computes normal force and pitch/roll wrench compensation; this changes current commands before the same actual Rust PI/RL plant, never applies an ideal mechanical force. Nominal and both0.9/1.1observer-scale full journeys must pass all unchanged screens, alongside nine exact-candidate faults. The1mm nominal coldplate/carrier stock clearance has no approved tolerance or physical fit acceptance.','',
        'Gap-field screens use an assumed25,000mm² pole area, while the winding inner aperture is9,600mm². No core neck/yoke area or validated flux split has been derived. A low gap B cannot establish core saturation acceptance; the magnetic geometry remains an explicit manufacturing/field-map hold. Updated body/beam gap poses are checked after every mechanical frame, including the final frame.','',
        'The nominal motion profile uses actual Baghdad line14 mainleg geometry, with runtime rounded upward to the1ms model clock; finance must use that exact profile hash. Rust current input power and heat are aggregate support/wayside values; they must not be added to a separate LSM loss budget as support-only energy. The RL energy identity covers frozen-geometry incremental current energy, not a complete measured PM/structure energy balance.','',*r['holds'],'','No digital pass authorizes hardware, manufacturing or operation.',''])

def publish(output=OUTPUT):
    src=sources();r=study();text=readme(r)
    if src!=sources():raise ValueError('actuator publication source epoch changed')
    bay=candidate_packaging(load()['preferred_winding_variant'])['definition']
    raw=json.dumps(r,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()
    if len(raw)>product.MAX_RAW:raise ValueError('bounded complete sensitivity packet required')
    return product.publish_packet(output,SCHEMA,r,src,{'study.json.gz':gzip.compress(raw,mtime=0),'overview.svg':overview(r).encode(),'README.md':text.encode(),'candidate-bay.svg':candidate_views(bay).encode(),'candidate-bay.json.gz':gzip.compress(encoded(bay),mtime=0)})

def candidate_views(bay):return product.bay_views(bay).replace('Three174×134×60mm winding candidates','Three300×200×75mm winding candidates')

def verify(output=OUTPUT):
    m,r=product.verify_packet(output,SCHEMA,sources())
    if set(m['files_sha256'])!={'study.json.gz','overview.svg','README.md','candidate-bay.svg','candidate-bay.json.gz'} or (Path(output)/'README.md').read_text()!=readme(r):raise ValueError('actuator payload set/scope text differs')
    if r.get('schema')!=SCHEMA or len(r.get('controls',[]))!=len(FAULTS) or [x['fault'] for x in r['controls']]!=list(FAULTS):raise ValueError('complete actuator controls required')
    validate_run(r['nominal'])
    if len(r.get('repair_candidates',[]))!=3:raise ValueError('all counted actuator repair iterations required')
    for repair in r['repair_candidates']:validate_run(repair)
    if len(r.get('full_estimator_cases',[]))!=3 or [x['estimator_scale'] for x in r['full_estimator_cases']]!=load()['normal_feedforward_scales']:raise ValueError('complete full-trip estimator sensitivity required')
    for case in r['full_estimator_cases']:validate_run(case)
    if r['repair_candidates'][-1]!=r['full_estimator_cases'][1]:raise ValueError('nominal repair differs from full exact estimator case')
    for c in r['controls']:
        validate_run(c['run'])
        if c['expected_fault']!=FAULTS[c['fault']] or c['run']['fault']!=c['fault']:raise ValueError('actuator fault identity differs')
        run=c['run'];expected=run['fault_injected_at_s'] is not None and run['fault_observed'] is not None and '('+c['expected_fault']+')' in run['fault_observed'] and not run['study_pass']
        if c['expected_hold'] is not expected:raise ValueError('actual actuator fault hold differs')
    repair=r['repair_candidates'][-1]
    observer_hash=r['execution']['normal_wrench_observer']['binary_sha256']
    if any(x['observer_execution']['library_sha256']!=observer_hash for x in [*r['full_estimator_cases'],*[c['run'] for c in r['controls']]]):raise ValueError('exact built observer artifact differs across campaign')
    if any(c['run']['configuration_sha256']!=repair['configuration_sha256'] or c['run']['profile_sha256']!=repair['profile_sha256'] for c in r['controls']):raise ValueError('fault campaign must test the exact full candidate/profile')
    if r.get('qualified_configuration_sha256')!=repair['configuration_sha256'] or r.get('control_configuration_sha256')!=repair['configuration_sha256']:raise ValueError('actuator qualification/control identity differs')
    if r['model_feasibility'] is not bool(full_eligible(r)) or r['all_negative_controls_held']!=all(c['expected_hold'] for c in r['controls']):raise ValueError('actuator summary differs')
    if (Path(output)/'overview.svg').read_text()!=overview(r):raise ValueError('actuator figure differs')
    bay=candidate_packaging(load()['preferred_winding_variant'])['definition']
    with gzip.GzipFile(fileobj=io.BytesIO((Path(output)/'candidate-bay.json.gz').read_bytes())) as f:raw=f.read(product.MAX_RAW+1)
    if len(raw)>product.MAX_RAW or json.loads(raw)!=bay or (Path(output)/'candidate-bay.svg').read_text()!=candidate_views(bay):raise ValueError('actuator counted candidate packaging differs')
    full=full_eligible(r)
    return dict(schema='osr-pilot-actuator-verification/1',verified=True,digital_execution_complete=True,model_feasibility=r['model_feasibility'],any_full_candidate_feasible=bool(full),applicable_full_cases=[{k:x[k] for k in ('case_id','configuration_sha256','profile_sha256','estimator_scale','start_time_s','study_pass','completed_moving_steps','planned_moving_steps','failure','screens','extrema','observer_execution')} for x in r['full_estimator_cases']],negative_controls=len(r['controls']),holds=r['holds'],all_negative_controls_held=r['all_negative_controls_held'],configuration_sha256=r['nominal']['configuration_sha256'],base_configuration_sha256=r['nominal']['configuration']['base_configuration_sha256'],qualified_configuration_sha256=r['qualified_configuration_sha256'],control_configuration_sha256=r['control_configuration_sha256'],nominal_completed_steps=r['nominal']['completed_moving_steps'],nominal_planned_steps=r['nominal']['planned_moving_steps'],nominal_failure=r['nominal']['failure'],nominal_screens=r['nominal']['screens'],extrema=r['nominal']['extrema'],repair_candidates=[{k:x[k] for k in ('configuration_sha256','body_variant','winding_variant','study_pass','completed_moving_steps','planned_moving_steps','failure','screens','extrema','thermal','packaging','magnetic_geometry')} for x in r['repair_candidates']],**FLAGS)

def read_summary(output=OUTPUT):return dict(**verify(output),manifest_sha256=digest((Path(output)/'manifest.json').read_bytes()))
