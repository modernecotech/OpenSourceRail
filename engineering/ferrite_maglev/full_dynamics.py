"""Continued post-fault electromechanical research, never physical acceptance.

The shared candidate owns equipment identity/mass. This module adds no free
reserve/brake/capture hardware and does not inherit the earlier ideal-force pass.
"""
from __future__ import annotations

from collections import deque
from concurrent.futures import ProcessPoolExecutor
import base64
import ctypes as C
from hashlib import sha256
import importlib
import json
import math
import re
from pathlib import Path
import subprocess
import time
import tomllib
import gzip

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
INPUT=Path(__file__).with_name('full-dynamics.toml')
PROTECTION=Path(__file__).parent/'data/candidate-protection-equipment.json'
KERNEL=Path(__file__).parent/'full-dynamics-kernel'
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/full-dynamics'
TEST=ROOT/'engineering/analysis/tests/test_ferrite_maglev_full_dynamics.py'
SCHEMA='osr-continued-full-dynamics/1'
FLAGS=dict(design_complete=False,physical_validation=False,manufacturing_release=False,physical_release=False)
MAX_RAW=128*1024*1024
FAULTS={'none','main-power-loss','reserve-depletion','no-capture','inverter-loss','sensing-dropout','sensing-disagreement','watchdog-delay','map-errors','receiver-loss'}
SOURCES=[
 dict(id='stm32h753',url='https://www.st.com/resource/en/datasheet/stm32h753xi.pdf',scope='Selected candidate MCU: Cortex-M7, ADC/PWM/watchdog resources; no measured railway execution claim'),
 dict(id='stm32-independent-watchdog',url='https://www.st.com/content/ccc/resource/training/technical/product_training/group0/98/3f/88/10/52/e1/46/9d/STM32H7-WDG_TIMERS-Independent_Watchdog_IWDG/files/STM32H7-WDG_TIMERS-Independent_Watchdog_IWDG.pdf/_jcr_content/translations/en.STM32H7-WDG_TIMERS-Independent_Watchdog_IWDG.pdf',scope='Independent watchdog uses separate low-speed clock; actual timeout tolerance and reset paths need target tests'),
 dict(id='cm5',url='https://datasheets.raspberrypi.com/cm5/cm5-datasheet.pdf',scope='Selected supervisory SBC: CM5, thermal throttling and published operating range; no fast-loop guarantee'),
]


def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def digest(value):return sha256(value).hexdigest()
def magnetics():return importlib.import_module('.candidate_magnetics',__package__)
def structures():return importlib.import_module('.candidate_structures',__package__)


def source_paths():
    own=[Path(__file__),INPUT,PROTECTION,TEST,KERNEL/'Cargo.toml',KERNEL/'Cargo.lock',
         *KERNEL.glob('src/*.rs'),ROOT/'Cargo.toml',ROOT/'Cargo.lock',ROOT/'rust-toolchain.toml',
         ROOT/'crates/osr-maglev-control/Cargo.toml',*list((ROOT/'crates/osr-maglev-control/src').glob('*.rs'))]
    try:own+=magnetics().source_paths()
    except ModuleNotFoundError:pass
    try:own+=structures().source_paths()
    except ModuleNotFoundError:pass
    try:own += [ROOT/p for p in importlib.import_module('.candidate_authority',__package__).sources()]
    except ModuleNotFoundError:pass
    return sorted(set(own))


def sources():return {p.relative_to(ROOT).as_posix():digest(p.read_bytes()) for p in source_paths()}


def validate_case(case):
    if not isinstance(case,dict) or not re.fullmatch('[a-z0-9][a-z0-9-]{0,79}',case.get('id','')) or case.get('fault') not in FAULTS:raise ValueError('implemented bounded named fault/load case required')
    if not all(type(case.get(k)) in (int,float) and math.isfinite(case[k]) and case[k]>=0 for k in ('speed_m_s','curve_radius_m')):raise ValueError('finite nonnegative speed/radius required')
    for key,lo,hi in [('reserve_fraction',0.,1.),('current_scale',.001,2.),('sensor_delay_s',0.,.03),('map_error_fraction',0.,.5),('duration_s',.001,3600.),('fault_time_s',0.,3600.)]:
        if key in case and (type(case[key]) not in (int,float) or not math.isfinite(case[key]) or not lo<=case[key]<=hi):raise ValueError('bounded case parameter required: '+key)
    if 'fault_module' in case and (type(case['fault_module']) is not int or not 0<=case['fault_module']<144):raise ValueError('actual module index required')
    return case


def load():
    a=tomllib.loads(INPUT.read_text())
    if a['schema']!='osr-full-dynamics-input/1':raise ValueError('continued dynamics input schema required')
    if a['mechanical_step_s']!=.001 or a['current_step_s']!=.00005:raise ValueError('declared1kHz/20kHz virtual clocks required')
    for k,v in a.items():
        if isinstance(v,(int,float)) and (isinstance(v,bool) or not math.isfinite(v) or v<=0):raise ValueError('finite positive dynamics assumption required: '+k)
    if len({c['id'] for c in a['cases']})!=len(a['cases']) or not 1<=len(a['cases'])<=32:raise ValueError('bounded unique dynamics cases required')
    if not a['minimum_gap_m']<a['nominal_gap_m']<a['maximum_gap_m']:raise ValueError('physical gap envelope required')
    if not 0<a['preferred_current_fraction']<=1 or not 0<a['preferred_negative_current_fraction']<=1:raise ValueError('bounded current fractions required')
    if not math.isfinite(a['coupler']['attachment_z_m']) or abs(a['coupler']['attachment_z_m'])>2:raise ValueError('bounded provisional drawgear height required')
    for case in a['cases']:validate_case(case)
    return a


def protection():
    value=json.loads(PROTECTION.read_bytes())
    if value['schema']!='osr-candidate-protection-equipment/1' or any(value[k] is not False for k in FLAGS):raise ValueError('provisional protection equipment required')
    rows={r['id']:r for r in value['rows']}
    for r in rows.values():
        if len(r['positions_m'])!=r['quantity_per_car'] or r['unit_mass_kg']<=0:raise ValueError('counted protection placement required')
    return value,rows


def mass_properties(regions):
    """Exact parallel-axis aggregation of declared boxes/regions, never a budget inertia."""
    mass=sum(float(r['mass_kg']) for r in regions)
    if not math.isfinite(mass) or mass<=0:raise ValueError('positive region mass required')
    cg=sum(float(r['mass_kg'])*np.asarray(r['position_m'],float) for r in regions)/mass
    tensor=np.zeros((3,3))
    for r in regions:
        m=float(r['mass_kg']);p=np.asarray(r['position_m'],float)-cg
        if 'local_inertia_kg_m2' in r:local=np.asarray(r['local_inertia_kg_m2'],float)
        else:
            x,y,z=r['bounds_m'];local=np.diag([m*(y*y+z*z)/12,m*(x*x+z*z)/12,m*(x*x+y*y)/12])
        if local.shape!=(3,3) or not np.isfinite(local).all() or np.linalg.eigvalsh(local).min()<-1e-9:raise ValueError('valid local inertia required')
        tensor+=local+m*(p@p*np.eye(3)-np.outer(p,p))
    return dict(mass_kg=mass,cg_m=cg.tolist(),inertia_kg_m2=tensor.tolist(),regions=len(regions),measured=False)


def contact_force(penetration,velocity,stiffness,damping):
    """Unilateral elastic force + compression-only damping; no tensile force."""
    d=np.maximum(0.,np.asarray(penetration,float));v=np.asarray(velocity,float)
    force=stiffness*d+damping*np.maximum(0.,v)*(d>0)
    return force,.5*stiffness*d*d,damping*np.maximum(0.,v)**2*(d>0)


def curve_offsets(x,radius):
    """Rigid straight body versus circular guideway; no free articulated mounts."""
    x=np.asarray(x,float)
    if radius==0:return np.zeros_like(x)
    if radius<=0 or np.max(np.abs(x))>=radius:raise ValueError('bounded positive curve radius required')
    return radius-np.sqrt(radius*radius-x*x)


def io_design():
    return dict(sbc=dict(model='Raspberry Pi Compute Module5, industrial carrier TBD',role='1kHz supervisory allocation, configuration and event logging; no direct gates',target_timing_measured=False),
        local_mcu=dict(model='STM32H753XI',role='Prototype target for2currentcircuits/module at20kHz, independent gap/current acquisition and reserve fallback',rust_target='thumbv7em-none-eabihf',target_build_and_timing_measured=False),
        topology=dict(cars=6,modules_per_car=24,physical_coils_per_module=3,current_circuits_per_module=2,primary_local_nodes=144,reserve_independence_qualified=False),
        input_packet=dict(fields=['configuration_sha256','unit_serial','sequence','captured_ns','valid_until_ns','dual_gap_m','dual_lateral_m','dual_current_a','bus_v','coil_temperature_c','reserve_energy_j','brake_and_capture_state'],units='SI;2currentaxes;4physicalgaps',stale_response='remove propulsion demand; independent local reserve/capture state continues; never interpret no duties as safe'),
        output_packet=dict(fields=['configuration_sha256','sequence','current_demands_a','kernel_status','reserve_active','brake_request','capture_load_n'],hardware_addresses=[],physical_outputs_enabled=False),
        watchdog=dict(independent_clock=True,study_timeout_s=.002,reset_does_not_remove_support_power=True,external_gate_interlock='unimplemented target circuit; must preserve independent reserve path'),
        timing=dict(current_period_s=.00005,allocation_period_s=.001,virtual_clock_only=True,host_wall_time_is_not_target_latency=True,required_target_evidence=['ADC aperture/skew','interrupt/DMA worst-case latency','PWM/update delay','watchdogmin/max overtemperature','brownout/EMI','reserve switchover under load']),sources=SOURCES,**FLAGS)


F2=C.c_double*2;F3=C.c_double*3;F4=C.c_double*4;F5=C.c_double*5;F6=C.c_double*6
class CurrentState(C.Structure):
    _fields_=[('sequence',C.c_uint64),('now_ns',C.c_uint64),('observed_ns',C.c_uint64),('integral_v',F2),('fault',C.c_uint32),('initialized',C.c_uint32)]
class Module(C.Structure):
    _fields_=[(n,t) for n,t in [('resistance_ohm',F2),('inductance_h',F4),('motional_emf_v',F2),('primary_target_a',F2),('reserve_target_a',F2),('current_a',F2),('temperature_c',F2),('copper_mass_kg',F2),('cooling_w_k',F2),('primary',CurrentState*2),('reserve',CurrentState*2),('faults',C.c_uint32),('car',C.c_uint32)]]
class ElectricalInput(C.Structure):
    _fields_=[('configuration',C.c_uint8*32),('first_sequence',C.c_uint64),('step_ns',C.c_uint64),('substeps',C.c_uint32),('count',C.c_uint32)]+[(n,C.c_double) for n in ('primary_bus_v','reserve_bus_v','maximum_current_a','kp_v_per_a','ki_v_per_a_s','maximum_temperature_c','ambient_c','copper_cp_j_kg_k','reserve_efficiency')]+[('reserve_remaining_j',F6),('reserve_auxiliary_w',F6),('modules',Module*144)]
class ElectricalOutput(C.Structure):
    _fields_=[('status',C.c_uint32),('physical_output_authorised',C.c_uint32),('modules',Module*144),('reserve_remaining_j',F6),('last_voltage_v',F2*144)]+[(n,C.c_uint32) for n in ('primary_fault_channels','reserve_used_channels','reserve_depleted_cars','voltage_limited_microsteps')]+[(n,C.c_double) for n in ('primary_dc_j','reserve_dc_j','reserve_draw_j','copper_heat_j','rejected_cooling_j','emf_work_j','field_change_j','maximum_rl_residual_j','peak_current_a','peak_voltage_v')]
class AllocationInput(C.Structure):
    _fields_=[('positions_m',F3*24)]+[(n,F5) for n in ('modes','velocities','gains','damping')]+[(n,C.c_double) for n in ('mass_kg','gravity','curve_acceleration_m_s2','maximum_upward_n','maximum_lateral_n','maximum_slew_n_s','step_s')]+[('previous',F2*24),('preferred_upward_n',C.c_double*24),('preferred_enabled',C.c_uint32),('physical_upward_limits_n',F2*24),('physical_limits_enabled',C.c_uint32)]
class AllocationOutput(C.Structure):
    _fields_=[('status',C.c_uint32),('at_limit',C.c_uint32),('forces',F2*24),('residual',F6),('physical_output_authorised',C.c_uint32)]


def build_kernel():
    before=sources();target=ROOT/'build/full-dynamics-kernel'
    command=['cargo','build','--locked','--release','--manifest-path',str(KERNEL/'Cargo.toml'),'--target-dir',str(target)]
    result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=300)
    if result.returncode:raise ValueError('full dynamics kernel build failed: '+result.stderr[-4000:])
    path=target/'release/libosr_full_dynamics_kernel.so'
    if before!=sources():raise ValueError('kernel sources changed during build')
    return path,dict(command=command,binary_sha256=digest(path.read_bytes()),source_sha256=before,hardware_output=False)


class RustPlant:
    def __init__(self,path,a,configuration_sha256):
        self.lib=C.CDLL(str(path));self.electrical=self.lib.osr_full_dynamics_electrical_v1
        self.electrical.argtypes=[ElectricalInput];self.electrical.restype=ElectricalOutput
        self.allocate=self.lib.osr_full_dynamics_allocation_v1;self.allocate.argtypes=[AllocationInput];self.allocate.restype=AllocationOutput
        self.input=ElectricalInput();i=self.input
        if not isinstance(configuration_sha256,str) or len(configuration_sha256)!=64:raise ValueError('exact configuration digest required')
        i.configuration=(C.c_uint8*32)(*bytes.fromhex(configuration_sha256));i.step_ns=round(a['current_step_s']*1e9)
        i.substeps=round(a['mechanical_step_s']/a['current_step_s']);i.count=144
        i.primary_bus_v=a['support_bus_v'];i.reserve_bus_v=a['support_bus_v'];i.maximum_current_a=a['current_limit_a']
        i.kp_v_per_a=a['current_kp_v_per_a'];i.ki_v_per_a_s=a['current_ki_v_per_a_s'];i.maximum_temperature_c=a['temperature_screen_c']
        i.ambient_c=a['ambient_c'];i.copper_cp_j_kg_k=385.;i.reserve_efficiency=.9
        self.step=0;self.previous_forces=np.zeros((6,24,2));self.preferred=None;self.physical_limits=None
        names=['resistance_ohm','inductance_h','motional_emf_v','primary_target_a','reserve_target_a','current_a','temperature_c','copper_mass_kg','cooling_w_k','faults','car']
        dtype=np.dtype(dict(names=names,formats=[('f8',4) if n=='inductance_h' else 'u4' if n in {'faults','car'} else ('f8',2) for n in names],offsets=[getattr(Module,n).offset for n in names],itemsize=C.sizeof(Module)))
        self.view=np.ndarray((144,),dtype=dtype,buffer=i.modules);self.view['car']=np.repeat(np.arange(6),24)

    def current_step(self,*,resistance,inductance,emf,targets,reserve_targets,current,temperature,copper_mass,cooling,faults,reserve_energy,reserve_aux):
        i=self.input;i.first_sequence=self.step*i.substeps+1
        for name,value in [('resistance_ohm',resistance),('inductance_h',np.asarray(inductance).reshape(144,4)),
            ('motional_emf_v',emf),('primary_target_a',targets),('reserve_target_a',reserve_targets),('current_a',current),
            ('temperature_c',temperature),('copper_mass_kg',copper_mass),('cooling_w_k',cooling),('faults',faults)]:self.view[name]=value
        i.reserve_remaining_j=F6(*reserve_energy);i.reserve_auxiliary_w=F6(*reserve_aux)
        out=self.electrical(i)
        if out.status or out.physical_output_authorised:raise ValueError('actual current kernel refused bounded inputs: '+str(out.status))
        i.modules=out.modules;self.step+=1
        currents=np.ndarray((144,2),dtype='f8',buffer=out.modules,offset=Module.current_a.offset,strides=(C.sizeof(Module),8)).copy()
        temps=np.ndarray((144,2),dtype='f8',buffer=out.modules,offset=Module.temperature_c.offset,strides=(C.sizeof(Module),8)).copy()
        return out,currents,temps

    def allocation(self,a,positions,mass,modes,velocities,curve_acceleration):
        commands=np.zeros((6,24,2));statuses=[]
        for car in range(6):
            i=AllocationInput();i.positions_m=(F3*24)(*(F3(*p) for p in positions));i.modes=F5(*modes[car]);i.velocities=F5(*velocities[car]);i.gains=F5(*a['body_mode_gains']);i.damping=F5(*a['body_mode_damping'])
            i.mass_kg=mass;i.gravity=a['gravity_m_s2'];i.curve_acceleration_m_s2=curve_acceleration[car]
            i.maximum_upward_n=a['maximum_module_force_n'];i.maximum_lateral_n=a['maximum_guidance_force_n'];i.maximum_slew_n_s=a['force_slew_n_s'];i.step_s=a['mechanical_step_s']
            i.previous=(F2*24)(*(F2(*p) for p in self.previous_forces[car]))
            if self.preferred is not None:
                i.preferred_upward_n=(C.c_double*24)(*self.preferred);i.preferred_enabled=1
            if self.physical_limits is not None:
                i.physical_upward_limits_n=(F2*24)(*(F2(*p) for p in self.physical_limits[car]));i.physical_limits_enabled=1
            r=self.allocate(i)
            if r.physical_output_authorised:raise ValueError('allocator cannot authorise physical output')
            commands[car]=np.ctypeslib.as_array(r.forces);statuses.append(r.status)
        self.previous_forces=commands.copy();return commands,statuses


class Receiver(C.Structure):
    _fields_=[('state',CurrentState),('current_dq_a',F2),('speed_m_s',C.c_double),('requested_brake_n',C.c_double),('temperature_c',C.c_double),('unavailable',C.c_uint32),('reserved',C.c_uint32)]
class ReceiverInput(C.Structure):
    _fields_=[('configuration',C.c_uint8*32),('first_sequence',C.c_uint64),('step_ns',C.c_uint64),('substeps',C.c_uint32),('reserved',C.c_uint32)]+[(n,C.c_double) for n in ('resistance_ohm','inductance_h','flux_linkage_wb','wave_number_rad_m','bus_v','maximum_current_a','fault_dump_resistance_ohm')]+[('receivers',Receiver*6)]
class ReceiverOutput(C.Structure):
    _fields_=[('status',C.c_uint32),('physical_output_authorised',C.c_uint32),('receivers',Receiver*6),('longitudinal_force_n',F6)]+[(n,C.c_double) for n in ('dc_j','copper_heat_j','fault_dump_heat_j','emf_work_j','field_change_j','maximum_residual_j')]+[('refused_microsteps',C.c_uint64)]


class ReceiverPlant:
    def __init__(self,lib,a,identity):
        self.function=lib.osr_full_dynamics_receiver_v1;self.function.argtypes=[ReceiverInput];self.function.restype=ReceiverOutput
        self.input=ReceiverInput();i=self.input;i.configuration=(C.c_uint8*32)(*bytes.fromhex(identity));i.step_ns=50000;i.substeps=20
        for key,value in [('resistance_ohm',a['receiver_resistance_ohm']),('inductance_h',a['receiver_inductance_h']),('flux_linkage_wb',a['receiver_flux_linkage_wb']),('wave_number_rad_m',math.pi/a['receiver_pole_pitch_m']),('bus_v',a['receiver_bus_v']),('maximum_current_a',a['receiver_q_current_limit_a']),('fault_dump_resistance_ohm',.5)]:setattr(i,key,value)
        self.step=0
    def tick(self,speed,request,unavailable,*,gates=None):
        i=self.input;i.first_sequence=self.step*i.substeps+1
        bits=15 if gates is None else sum(1<<n for n,key in enumerate(('protected','committed','receiver_ready','resistor_ready')) if gates.get(key) is True)
        for car in range(6):i.receivers[car].speed_m_s=float(speed[car]);i.receivers[car].requested_brake_n=float(request[car]);i.receivers[car].temperature_c=40.;i.receivers[car].unavailable=int(unavailable);i.receivers[car].reserved=bits
        r=self.function(i)
        if r.status or r.physical_output_authorised:raise ValueError('receiver current kernel invalid')
        i.receivers=r.receivers;self.step+=1;return r,np.array(r.longitudinal_force_n)


class Group(C.Structure):
    _fields_=[('state',CurrentState),('current_ab_a',F2)]+[(n,C.c_double) for n in ('resistance_ohm','inductance_h','phase_rad','speed_rad_s','flux_wb','demanded_q_a')]+[('emf_ab_v',F2)]+[(n,C.c_double) for n in ('temperature_c','copper_mass_kg','current_limit_a','bus_v')]+[(n,C.c_uint32) for n in ('mode','gates','unavailable','phase_error_mdeg')]
class GroupInput(C.Structure):
    _fields_=[('configuration',C.c_uint8*32),('first_sequence',C.c_uint64),('step_ns',C.c_uint64),('substeps',C.c_uint32),('count',C.c_uint32)]+[(n,C.c_double) for n in ('kp','ki','dump_resistance_ohm')]+[('groups',Group*200)]
class GroupOutput(C.Structure):
    _fields_=[('status',C.c_uint32),('physical_output_authorised',C.c_uint32),('groups',Group*200),('average_current_ab_a',F2*200)]+[(n,C.c_double) for n in ('dc_j','copper_heat_j','dump_heat_j','emf_work_j','field_change_j','maximum_residual_j','maximum_voltage_v')]+[('refused_microsteps',C.c_uint64)]


class GroupPlant:
    """Actual independent Rust voltage/current state for each active5m group."""
    def __init__(self,lib,identity,count):
        if type(count) is not int or not 1<=count<=200:raise ValueError('bounded explicit active group count required')
        self.function=lib.osr_full_dynamics_groups_v1;self.function.argtypes=[GroupInput];self.function.restype=GroupOutput
        self.input=GroupInput();i=self.input;i.configuration=(C.c_uint8*32)(*bytes.fromhex(identity));i.step_ns=50000;i.substeps=20;i.count=count;i.kp=.25;i.ki=50.;i.dump_resistance_ohm=.5
        names=['current_ab_a','resistance_ohm','inductance_h','phase_rad','speed_rad_s','flux_wb','demanded_q_a','emf_ab_v','temperature_c','copper_mass_kg','current_limit_a','bus_v','mode','gates','unavailable','phase_error_mdeg']
        dtype=np.dtype(dict(names=names,formats=[('f8',2) if n in {'current_ab_a','emf_ab_v'} else 'u4' if n in {'mode','gates','unavailable','phase_error_mdeg'} else 'f8' for n in names],offsets=[getattr(Group,n).offset for n in names],itemsize=C.sizeof(Group)))
        self.view=np.ndarray((count,),dtype=dtype,buffer=i.groups);self.view['temperature_c']=40.;self.step=0;self.count=count
    def tick(self,*,resistance,inductance,phase,omega,flux,targets,emf,copper_mass,current_limit,bus,mode,gates,unavailable=False,phase_error_mdeg=0):
        i=self.input;i.first_sequence=self.step*i.substeps+1
        values=dict(resistance_ohm=resistance,inductance_h=inductance,phase_rad=phase,speed_rad_s=omega,flux_wb=flux,demanded_q_a=targets,emf_ab_v=emf,
            copper_mass_kg=copper_mass,current_limit_a=current_limit,bus_v=bus,mode=mode,gates=gates,unavailable=unavailable,phase_error_mdeg=phase_error_mdeg)
        for name,value in values.items():self.view[name]=value
        out=self.function(i)
        if out.status or out.physical_output_authorised:raise ValueError('actual distributed group current plant refused inputs: '+str(out.status))
        i.groups=out.groups;self.step+=1
        return out,np.ctypeslib.as_array(out.average_current_ab_a)[:self.count].copy()


class MapDomain(ValueError):pass


class MagneticPlant:
    def __init__(self,module=None):
        self.module=magnetics() if module is None else module;self.definition=self.module.definition();d=self.definition
        required={'configuration_sha256','mass_properties','module_placements_m','circuits','pole_half_spacing_m','nominal_gap_m','protection_equipment_sha256'}
        if not required<=set(d):raise ValueError('shared candidate dynamics interface incomplete: '+str(sorted(required-set(d))))
        if d['protection_equipment_sha256']!=digest(PROTECTION.read_bytes()):raise ValueError('shared candidate does not count exact protection revision')
        self.positions=np.asarray(d['module_placements_m'],float);self.mass=d['mass_properties']['mass_kg'];self.cg=np.asarray(d['mass_properties']['cg_m'],float)
        self.inertia=np.asarray(d['mass_properties']['inertia_kg_m2'],float)
        if self.positions.shape!=(24,3) or self.inertia.shape!=(3,3) or not np.isfinite(self.inertia).all() or np.linalg.eigvalsh(self.inertia).min()<=0:raise ValueError('equipment-derived positive inertia and24placements required')
        self.levers=self.positions-self.cg;self.identity=d['configuration_sha256']
        self.copper_mass=np.broadcast_to(np.asarray(d['circuits']['copper_mass_kg'],float),(144,2)).copy()
        self.cooling=np.broadcast_to(np.asarray(d['circuits']['thermal_conductance_w_k'],float),(144,2)).copy()
        self.flux=None;self.inverse_flux={}
        self.wayside=self.module.wayside_field() if hasattr(self.module,'wayside_field') else dict(accepted_for_simulation=False)
    def evaluate(self,gaps,current,temperature):
        result=self.module.evaluate_batch(gaps_m=np.asarray(gaps),current_a=np.asarray(current),temperature_c=np.asarray(temperature),initial_flux_wb=self.flux)
        shapes={'upward_n':(144,),'leftward_n':(144,),'local_moments_nm':(144,3),'flux_linkage_wb':(144,2),'incremental_inductance_h':(144,2,2),'dflux_dgap_wb_m':(144,2,4),'resistance_ohm':(144,2),'stored_energy_j':(144,)}
        for key,shape in shapes.items():
            value=np.asarray(result[key],float)
            if value.shape!=shape or not np.isfinite(value).all():raise MapDomain('finite exact map channels required: '+key)
            result[key]=value
        if not np.all(result['valid']):raise MapDomain('magnetic map domain/saturation/geometry refused')
        self.flux=np.asarray(result['flux_state_wb'],float).copy()
        return result
    def inverse(self,force,gaps,temperature,initial,*,channel='primary'):
        r=self.module.inverse_current(upward_n=force[:,0],leftward_n=force[:,1],gaps_m=gaps,
            temperature_c=temperature,initial_a=initial,initial_flux_wb=self.inverse_flux.get(channel))
        self.inverse_flux[channel]=np.asarray(r['flux_state_wb'],float).copy()
        current=np.asarray(r['current_a'],float);valid=np.asarray(r['converged'],bool)&np.asarray(r['valid'],bool)
        if current.shape!=(144,2) or valid.shape!=(144,) or not np.isfinite(current).all():raise MapDomain('bounded two-circuit inverse required')
        residual=np.asarray(r['force_residual_n'],float)
        if residual.shape!=(144,2) or not np.isfinite(residual).all():raise MapDomain('inverse force residual channels required')
        return current,valid,residual


def modal_step(q,v,force,mass,stiffness,damping,dt):
    denominator=mass+damping*dt/2+stiffness*dt*dt/4
    new_v=((mass-damping*dt/2-stiffness*dt*dt/4)*v+dt*(force-stiffness*q))/denominator
    new_q=q+dt*(v+new_v)/2
    dissipated=damping*((v+new_v)/2)**2*dt
    return new_q,new_v,dissipated


class Guideway:
    """Three first modes/span with force/reaction work retained explicitly."""
    def __init__(self,a,bays):
        self.a=a;self.bays=bays;self.q=np.zeros((bays,3));self.v=np.zeros_like(self.q)
        L=a['span_m'];self.linear_mass=a['distributed_mass_kg_m'];self.polar_mass=a['polar_mass_per_length_kg_m']
        self.mass=np.array([self.linear_mass*L/2]*2+[self.polar_mass*L/2])
        self.k=np.array([a['young_pa']*a['vertical_inertia_m4']*math.pi**4/(2*L**3),a['young_pa']*a['lateral_inertia_m4']*math.pi**4/(2*L**3),a['shear_pa']*a['torsion_constant_m4']*math.pi**2/(2*L)])
        self.c=2*a['damping_fraction']*np.sqrt(self.mass*self.k)
        self.accel=np.zeros_like(self.q);self.dissipated=0.;self.external_work=0.
    def locations(self,x):
        x=np.asarray(x);indices=np.floor(x/self.a['span_m']).astype(int)
        if np.any(indices<0) or np.any(indices>=self.bays):raise MapDomain('train outside defined guideway')
        local=x/self.a['span_m']-indices;return indices,local,np.sin(math.pi*local)
    def pose(self,x,y,z=None):
        indices,_,phi=self.locations(x);q=self.q[indices];v=self.v[indices]
        height=0. if z is None else np.asarray(z)-self.a['beam_centroid_z_m']
        return np.column_stack((phi*(q[:,0]+y*q[:,2]),phi*(q[:,1]-height*q[:,2]),phi*q[:,2])),np.column_stack((phi*(v[:,0]+y*v[:,2]),phi*(v[:,1]-height*v[:,2]),phi*v[:,2]))
    def advance(self,x,y,z,up,left,local_roll,dt,*,vehicle_longitudinal=None,vehicle_pitch_moment=None,vehicle_yaw_moment=None):
        indices,u,phi=self.locations(x);forces=np.zeros_like(self.q)
        height=z-self.a['beam_centroid_z_m'];torque=-(y*up-height*left+local_roll)
        longitudinal=np.zeros_like(up) if vehicle_longitudinal is None else np.asarray(vehicle_longitudinal)
        pitch=-height*longitudinal-(0. if vehicle_pitch_moment is None else np.asarray(vehicle_pitch_moment))
        yaw=y*longitudinal-(0. if vehicle_yaw_moment is None else np.asarray(vehicle_yaw_moment))
        for axis,load in enumerate((-up,-left,torque)):np.add.at(forces[:,axis],indices,phi*load)
        dphi=math.pi/self.a['span_m']*np.cos(math.pi*u)
        np.add.at(forces[:,0],indices,-dphi*pitch);np.add.at(forces[:,1],indices,dphi*yaw)
        old_q=self.q.copy();old_v=self.v.copy();old_energy=self.energy()
        self.q,self.v,diss=modal_step(self.q,self.v,forces,self.mass,self.k,self.c,dt)
        self.accel=(self.v-old_v)/dt;self.dissipated+=float(diss.sum());work=float(np.sum(forces*(self.q-old_q)));self.external_work+=work
        residual=self.energy()-old_energy-work+float(diss.sum())
        reactions=np.zeros(self.bays+1)
        np.add.at(reactions,indices,up*(1-u));np.add.at(reactions,indices+1,up*u)
        np.add.at(reactions,indices,-pitch/self.a['span_m']);np.add.at(reactions,indices+1,pitch/self.a['span_m'])
        inertia=self.linear_mass*self.a['span_m']/math.pi*self.accel[:,0]
        reactions[:-1]+=inertia;reactions[1:]+=inertia
        dead=np.full(self.bays+1,self.linear_mass*self.a['span_m']*self.a['gravity_m_s2']);dead[[0,-1]]/=2
        total=reactions+dead
        lateral=np.zeros(self.bays+1);np.add.at(lateral,indices,left*(1-u)+yaw/self.a['span_m']);np.add.at(lateral,indices+1,left*u-yaw/self.a['span_m'])
        lateral_inertia=self.linear_mass*self.a['span_m']/math.pi*self.accel[:,1];lateral[:-1]+=lateral_inertia;lateral[1:]+=lateral_inertia
        torsion_reactions=np.zeros(self.bays+1);np.add.at(torsion_reactions,indices,-torque*(1-u));np.add.at(torsion_reactions,indices+1,-torque*u)
        return dict(peak_support_reaction_n=float(np.abs(total).max()),minimum_support_reaction_n=float(total.min()),peak_live_support_reaction_n=float(np.abs(reactions).max()),peak_torsion_nm=float(np.abs(torque).max()),peak_lateral_support_reaction_n=float(np.abs(lateral).max()),
            maximum_joint_rotation_rad=float(np.max(np.abs(self.q[:,[0,2]])*np.array([math.pi/self.a['span_m'],1]))),mechanical_energy_residual_j=float(residual),reactions_n=total.tolist(),live_reactions_n=reactions.tolist(),dead_reactions_n=dead.tolist(),
            lateral_reactions_n=lateral.tolist(),torsion_reactions_nm=torsion_reactions.tolist(),applied_pitch_moments_nm=pitch.tolist(),applied_yaw_moments_nm=yaw.tolist(),
            reference='Live modal displacement about dead-load-cambered geometry; concrete/steel dead reactions added exactly once, without applying dead load again to live modal coordinates')
    def energy(self):return float(np.sum((self.mass*self.v*self.v+self.k*self.q*self.q)/2))


def body_gaps(a,plant,state,guideway,x,radius):
    """Four physical pole gaps, including rigid-body curvature/roll mismatch."""
    levers=plant.levers;flat_x=(x[:,None]+plant.positions[:,0]).ravel()
    rail,_=guideway.pose(flat_x,np.tile(plant.positions[:,1],6),np.tile(plant.positions[:,2],6));rail=rail.reshape(6,24,3)
    y,z,roll,pitch,yaw=state.T
    local_z=z[:,None]+roll[:,None]*levers[:,1]-pitch[:,None]*levers[:,0]-rail[:,:,0]
    local_y=y[:,None]+yaw[:,None]*levers[:,0]-roll[:,None]*levers[:,2]-rail[:,:,1]-curve_offsets(plant.positions[:,0],radius)
    differential_roll=roll[:,None]-rail[:,:,2];half=plant.definition['pole_half_spacing_m'];g0=a['nominal_gap_m']
    guide_height=plant.definition.get('module',{}).get('guide_force_z_m',.05)
    local_guide_y=local_y-guide_height*differential_roll
    return np.stack((g0-local_z-half*differential_roll,g0-local_z+half*differential_roll,g0-local_guide_y,g0+local_guide_y),axis=-1).reshape(144,4),local_z,local_y


def measured_modes(plant,gaps):
    gap=np.asarray(gaps).reshape(6,24,4);z=.008-gap[:,:,:2].mean(axis=2);lat=(gap[:,:,3]-gap[:,:,2])/2
    Z=np.column_stack((np.ones(24),plant.levers[:,1],-plant.levers[:,0]));Y=np.column_stack((np.ones(24),plant.levers[:,0]))
    zfit=np.linalg.lstsq(Z,z.T,rcond=None)[0].T;yfit=np.linalg.lstsq(Y,(lat+zfit[:,1,None]*plant.levers[:,2]).T,rcond=None)[0].T
    return np.column_stack((-zfit[:,0],zfit[:,1],zfit[:,2],yfit[:,0],yfit[:,1]))


def _kinetic(state_velocity,mass,inertia):
    return .5*mass*float(np.sum(state_velocity[:,:2]**2))+.5*float(np.einsum('ni,ij,nj->',state_velocity[:,2:],inertia,state_velocity[:,2:]))


def authority_at(events,now_s,identity):
    """Consume an exact retained protocol decision; never invent authority.

    The producer supplies actual Rust authority/berth execution and its receipt.
    These checks bind consistency/freshness, not authentication of a live railway.
    """
    if not events:return dict(permitted=False,reason='no retained Rust authority decision')
    if not math.isfinite(now_s) or now_s<0:raise ValueError('finite nonnegative authority clock required')
    previous=0;last_time=-1.
    for e in events:
        if type(e.get('sequence')) is not int or e['sequence']<=previous or type(e.get('issued_s')) not in (int,float) or type(e.get('expires_s')) not in (int,float) or not math.isfinite(e['issued_s']+e['expires_s']) or not last_time<=e['issued_s']<=e['expires_s'] or e['expires_s']-e['issued_s']>.100000001:
            raise ValueError('bounded ordered authority sequence/time required')
        previous=e['sequence'];last_time=e['issued_s']
    applicable=[e for e in events if e['issued_s']<=now_s]
    if not applicable:return dict(permitted=False,reason='authority not yet issued')
    event=applicable[-1]
    good=(event.get('schema')=='osr-full-dynamics-authority/1' and event.get('configuration_sha256')==identity
          and event.get('actual_rust_protocol') is True and event.get('physical_output_authorised') is False
          and event.get('protected') is True and event.get('committed') is True
          and now_s<=event['expires_s'] and event.get('receiver_ready') is True and event.get('resistor_ready') is True
          and isinstance(event.get('source_receipt_sha256'),str) and len(event['source_receipt_sha256'])==64
          and all(c in '0123456789abcdef' for c in event['source_receipt_sha256']))
    return dict(permitted=good,reason='retained exact protocol decision' if good else 'expired/unprotected/different authority decision',event=event)


class RouteController:
    """Actual-pose four-stop composition, with live Rust decisions and dwell.

    It commands accelerations/current targets only. It never teleports a train,
    clears a berth from a timetable, or treats dispatcher readiness as motion.
    """
    def __init__(self,stops,client,a,identity):
        self.stops=np.asarray(stops,float)
        if self.stops.ndim!=1 or not 2<=len(stops)<=10 or not np.isfinite(self.stops).all() or np.any(np.diff(self.stops)<400):raise ValueError('bounded full-line stops required')
        if client.configuration!=identity or list(client.stops)!=list(stops):raise ValueError('actual authority client candidate/route differs')
        self.client=client;self.a=a;self.identity=identity;self.leg=0;self.arrived=[];self.events=[];self.latest=None;self.last_update=-1.;self.dwell_until=None;self.completed=False;self.prepared=False
        self.initial_energy=a['service_battery_kwh_per_car']*a['service_battery_usable_fraction']*3.6e6*6;self.energy_j=self.initial_energy;self.charged_j=0.;self.last_charge_s=None
    def step(self,now,front,tail,speed,*,reserve_ready,healthy,receiver_failed=False,resistor_ready=True):
        if self.latest is None or now-self.last_update>=self.a['authority_update_s']-1e-10:
            if not self.prepared:
                ready=dict(receiver_ready=not receiver_failed,resistor_ready=bool(resistor_ready),reserve_ready=bool(reserve_ready),doors_closed=True,train_healthy=bool(healthy))
                self.latest=self.client.prepare(self.leg,now,readiness=ready);self.prepared=True
            self.latest=self.client.step(now,front,tail,speed,receiver_failed=bool(receiver_failed),resistor_ready=bool(resistor_ready));self.last_update=now
        permitted=authority_at([self.latest],now,self.identity)['permitted']
        target=float(self.stops[self.leg+1]);remaining=target-front
        if not self.completed and self.dwell_until is None and abs(remaining)<=self.a['berth_tolerance_m'] and abs(speed)<=self.a['stop_speed_m_s']:
            self.arrived.append(dict(station=self.leg+1,time_s=now,front_m=front,tail_m=tail,speed_m_s=speed,energy_j=self.energy_j,configuration_sha256=self.identity))
            self.dwell_until=now+self.a['station_dwell_s'];self.last_charge_s=now
        charging=False
        if self.dwell_until is not None:
            if self.last_charge_s is not None:
                added=min(self.initial_energy-self.energy_j,self.a['station_charge_kw_per_car']*1000*6*(now-self.last_charge_s))
                self.energy_j+=max(0.,added);self.charged_j+=max(0.,added)
            self.last_charge_s=now;charging=True
            if now>=self.dwell_until and self.energy_j>=self.a['minimum_departure_kwh_per_car']*3.6e6*6:
                if self.leg+2==len(self.stops):self.completed=True
                else:self.leg+=1;self.prepared=False;self.dwell_until=None;self.last_charge_s=None
        limit=min(self.a['route_speed_limit_m_s'],math.sqrt(max(0.,2*self.a['route_service_deceleration_m_s2']*max(0.,remaining-self.a['berth_tolerance_m']/2))))
        acceleration=float(np.clip((limit-speed)*self.a['route_speed_gain_s_inv'],-self.a['route_service_deceleration_m_s2'],self.a['route_acceleration_m_s2']))
        if not permitted or charging or self.completed:acceleration=-self.a['route_service_deceleration_m_s2'] if speed>self.a['stop_speed_m_s'] else 0.
        overshoot=remaining < -self.a['berth_tolerance_m']
        return dict(permitted=bool(permitted),target_front_m=target,remaining_m=remaining,acceleration_m_s2=acceleration,hold_brakes=charging or self.completed or not permitted,
            charging=charging,completed=self.completed,leg=self.leg,overshoot=bool(overshoot),energy_j=self.energy_j,latest_authority=self.latest)
    def receipt(self):
        raw=self.client.receipt()
        authority=importlib.import_module('.candidate_authority',__package__)
        authority.verify_receipt(self.client.directory,configuration_sha256=self.identity,replay=True)
        return dict(authority=raw,arrivals=self.arrived,completed=self.completed,charged_j=self.charged_j,service_energy_final_j=self.energy_j,
            dispatch_basis_s=self.a['dispatch_basis_s'],dispatch_scope='One actual train trip;240s timetable basis is not a demonstrated multi-train headway',**FLAGS)


def simulate(case, *, route_stops_m=None, authority_events=None, plant_module=None, kernel_path=None, assumptions=None, guideway_properties=None):
    """Continue all physical states after fault detection to terminal state/hold.

    Route composition is explicit: callers pass ordered stop coordinates and
    source-bound actual Rust protocol decisions. This bounded runner does not
    infer launch authority, terminal fit, dwell or charging acceptance.
    """
    a=load() if assumptions is None else dict(assumptions);input_sha256=digest(encoded(a))
    if isinstance(case,str):case=next(c for c in a['cases'] if c['id']==case)
    case=validate_case(dict(case));plant=MagneticPlant(plant_module);identity=plant.identity
    if abs(a['nominal_gap_m']-plant.definition['nominal_gap_m'])>1e-12:raise ValueError('shared candidate nominal gap differs')
    civil=structures().dynamics_properties(plant.definition) if guideway_properties is None else dict(guideway_properties)
    if civil['configuration_sha256']!=identity or civil['qualified'] is not False:raise ValueError('exact provisional candidate guideway required')
    a['guideway']={**a['guideway'],**civil,'gravity_m_s2':a['gravity_m_s2']}
    axial=structures().axial_properties(plant.definition)
    if axial['configuration_sha256']!=identity:raise ValueError('exact candidate axial series stiffness required')
    coupler_k=axial['body_and_coupler_series_stiffness_n_m'];coupler_c=a['coupler_damping_n_s_m'];coupler_z=a['coupler']['attachment_z_m']-plant.cg[2]
    if kernel_path is None:kernel_path,_=build_kernel()
    controller=RustPlant(kernel_path,a,identity);receiver=ReceiverPlant(controller.lib,a,identity)
    _,equipment=protection();battery=equipment['protection/independent-reserve-battery']['ratings'];power=equipment['protection/reserve-converter-contactors']['ratings']
    shoe=equipment['protection/capture-shoe'];clamp=equipment['protection/independent-guideway-brake'];capture=shoe['ratings'];brake=clamp['ratings']
    dt=a['mechanical_step_s'];duration=case.get('duration_s',a['duration_s']);fault_at=case.get('fault_time_s',a['fault_time_s']);radius=case['curve_radius_m'];curvature=0. if radius==0 else 1/radius
    mass=plant.mass;inertia=plant.inertia.copy();levers=plant.levers.copy()
    if case.get('payload_lateral_offset_m'):
        # Same12t load, explicitly shifted; the case identity binds this changed
        # load distribution. No vehicle part or passenger mass is added twice.
        shift=12000.*case['payload_lateral_offset_m']/mass
        levers[:,1]-=shift
        inertia[0,0]+=12000.*case['payload_lateral_offset_m']**2-mass*shift**2
        inertia[2,2]+=12000.*case['payload_lateral_offset_m']**2-mass*shift**2
        plant.levers=levers;plant.cg=plant.cg+np.array([0.,shift,0.])
    speed=np.full(6,case['speed_m_s']);centres=case.get('initial_front_m',120.)-8.5-np.arange(6)*17.5
    state=np.zeros((6,5));velocity=np.zeros_like(state)
    guide=Guideway(a['guideway'],math.ceil((float(centres.max())+6+float(speed.max())*duration)/a['guideway']['span_m'])+4)
    capacity_sample=plant.module.evaluate_batch([[a['nominal_gap_m']]*4],[[a['current_limit_a']*a['preferred_current_fraction'],0.]],a['ambient_c'])
    nominal_capacity_valid=bool(capacity_sample['valid'][0])
    preferred_cap=min(a['maximum_module_force_n'],float(capacity_sample['upward_n'][0]))
    lower_sample=plant.module.evaluate_batch([[a['nominal_gap_m']]*4],[[-a['current_limit_a']*a['preferred_negative_current_fraction'],0.]],a['ambient_c'])
    nominal_capacity_valid=nominal_capacity_valid and bool(lower_sample['valid'][0])
    if nominal_capacity_valid:preferred=structures().preferred_support_loads(plant.definition,preferred_cap,float(lower_sample['upward_n'][0]))
    else:preferred=dict(configuration_sha256=identity,state='hold-invalid-nominal-magnetic-capacity',passed=False,adopted=False,
        reason='Actual stationary return section/core/demagnetization/domain fails; requested static loads below are hypothetical references only and no forces are applied to a moving plant.')
    preferred['capacity_screen']=dict(nominal_gap_m=a['nominal_gap_m'],current_a=a['current_limit_a']*a['preferred_current_fraction'],maximum_n=preferred_cap,
        scope='Nominal current-limited static LP cap only. Every instantaneous gap/current/demag/BH map is checked again; no guaranteed dynamic capacity credit.')
    if preferred['configuration_sha256']!=identity:raise ValueError('preferred support vector candidate differs')
    static_iterations=[];preferred_hold=not nominal_capacity_valid
    for static_iteration in range(5):
        if not case.get('uniform_support_control',False):
            if not preferred.get('passed',False):preferred_hold=True;controller.preferred=None
            else:controller.preferred=np.asarray(preferred['preferred_loads_n'],float)
        controller.previous_forces[:,:,0]=mass*a['gravity_m_s2']/24 if controller.preferred is None else controller.preferred
        force0,status0=controller.allocation(a,levers,mass,np.zeros((6,5)),np.zeros((6,5)),speed**2*curvature)
        px=(centres[:,None]+plant.positions[:,0]).ravel();indices,_,phi=guide.locations(px);guide.q[:]=0.;state[:]=0.
        for axis,values in enumerate((-force0[:,:,0].ravel(),-force0[:,:,1].ravel(),-(plant.positions[:,1]*force0[:,:,0]-plant.positions[:,2]*force0[:,:,1]).ravel())):
            np.add.at(guide.q[:,axis],indices,phi*values/guide.k[axis])
        rail,_=guide.pose(px,np.tile(plant.positions[:,1],6));Z=np.column_stack((np.ones(24),levers[:,1],-levers[:,0]));fit=np.linalg.lstsq(Z,rail[:,0].reshape(6,24).T,rcond=None)[0].T
        state[:,1]=fit[:,0];state[:,2]=fit[:,1];state[:,3]=fit[:,2]
        gaps,_,_=body_gaps(a,plant,state,guide,centres,radius)
        if controller.preferred is None or np.any(gaps<a['minimum_gap_m']) or np.any(gaps>a['maximum_gap_m']):break
        sample=plant.module.evaluate_batch(gaps,np.tile([a['current_limit_a']*a['preferred_current_fraction'],0.],(144,1)),a['ambient_c'])
        lower_sample=plant.module.evaluate_batch(gaps,np.tile([-a['current_limit_a']*a['preferred_negative_current_fraction'],0.],(144,1)),a['ambient_c'])
        if not np.all(sample['valid']) or not np.all(lower_sample['valid']):preferred_hold=True;break
        caps=np.asarray(sample['upward_n']).reshape(6,24).min(axis=0)
        floors=np.asarray(lower_sample['upward_n']).reshape(6,24).max(axis=0)
        static_iterations.append(dict(iteration=static_iteration,minimum_gap_m=float(gaps.min()),maximum_gap_m=float(gaps.max()),per_module_current_limited_cap_n=caps.tolist(),per_module_residual_lift_minimum_n=floors.tolist(),preferred_sha256=preferred.get('force_vector_sha256')))
        if np.all(controller.preferred<=caps+1.) and np.all(controller.preferred>=floors-1.):break
        if static_iteration==4:preferred_hold=True;break
        preferred=structures().preferred_support_loads(plant.definition,caps.tolist(),floors.tolist())
    preferred['static_capacity_iterations']=static_iterations
    trace=[];events=[];holds=[];terminal=None;fault_seen=False;fault_tick=None;stable=0.;safety_failures=[]
    if preferred_hold:terminal='hold-preferred-current-limited-static-allocation';holds.append('bounded preferred/guideway static iteration infeasible or not converged')
    initial_equilibrium=False;initial_inverse=None;currents=np.zeros((144,2));temperature=np.full((144,2),a['ambient_c'])
    if route_stops_m is not None:
        if (len(route_stops_m)<2 or any(not math.isfinite(float(x)) for x in route_stops_m)
                or any(b<=x for x,b in zip(route_stops_m,route_stops_m[1:]))):raise ValueError('ordered finite route stops required')
        if not authority_events:holds.append('full-line composition requires retained actual Rust authority/berth decisions; no implicit launch')
    if np.any(gaps<a['minimum_gap_m']) or np.any(gaps>a['maximum_gap_m']):
        terminal='hold-initial-curve-or-gap-geometry';holds.append('rigid band/pole geometry outside shared magnetic domain before motion')
    else:
        currents,valid,inverse_residual=plant.inverse(force0.reshape(144,2),gaps,temperature,currents)
        initial_inverse=dict(current_a=currents.tolist(),valid=valid.tolist(),force_residual_n=inverse_residual.tolist(),requested_module_forces_n=force0.tolist(),gaps_m=gaps.tolist(),allocation_status=status0)
        initial_equilibrium=bool(nominal_capacity_valid and np.all(valid) and np.max(np.abs(inverse_residual))<=50.)
        if not initial_equilibrium:
            holds.append('initial support/guidance equilibrium fails common candidate current/field/convergence domain')
            terminal='hold-initial-support-current-or-field-capacity'
    currents*=case.get('current_scale',1.)
    reserve=np.full(6,battery['gross_energy_kwh']*battery['usable_fraction']*3.6e6*case.get('reserve_fraction',1.));initial_reserve=reserve.copy()
    reserve_aux=np.full(6,equipment['protection/independent-sensing-controller']['ratings']['auxiliary_power_w'])
    brake_temperature=np.full(6,a['ambient_c']);receiver_temperature=a['ambient_c'];brake_force_limit=clamp['quantity_per_car']*brake['clamp_normal_n']*brake['friction_coefficient']
    shoe_positions=np.asarray(shoe['positions_m'],float);shoe_force_positions=shoe_positions.copy();shoe_force_positions[:,2]=shoe['contact_interface']['moving_underside_z_m'];shoe_levers=shoe_force_positions-plant.cg
    brake_positions=np.asarray(clamp['positions_m'],float)-plant.cg
    history=deque(maxlen=32);last_modes=np.zeros((6,5));last_reserve_modes=np.zeros((6,5));last_gaps=gaps.copy();depleted_mask=0
    mechanical_initial=.5*mass*float(np.sum(speed**2))+_kinetic(velocity,mass,inertia)+mass*a['gravity_m_s2']*float(state[:,1].sum())+guide.energy()
    energy=dict(primary_dc_j=0.,reserve_dc_j=0.,reserve_draw_j=0.,copper_heat_j=0.,cooling_j=0.,emf_work_j=0.,incremental_field_change_j=0.,
                brake_heat_j=0.,guideway_heat_j=0.,capture_damping_j=0.,receiver_dc_j=0.,receiver_copper_j=0.,receiver_dump_j=0.,receiver_emf_j=0.,receiver_field_j=0.,rolling_drag_heat_j=0.,
                rigid_body_balance_residual_j=0.,guideway_balance_residual_j=0.,coupler_damping_j=0.)
    maximum=dict(current_a=0.,voltage_v=0.,temperature_c=a['ambient_c'],brake_temperature_c=a['ambient_c'],receiver_temperature_c=a['ambient_c'],upward_n=0.,guidance_n=0.,capture_n=0.,capture_compression_m=0.,lateral_capture_n=0.,roll_rad=0.,pitch_rad=0.,yaw_rad=0.,support_reaction_n=0.,torsion_nm=0.,joint_rotation_rad=0.,rl_residual_j=0.,receiver_rl_residual_j=0.,inverse_force_residual_n=0.,reserve_output_kw_per_car=0.,coupler_force_n=0.,coupler_extension_m=0.)
    minimum_gap=float(gaps.min());maximum_gap=float(gaps.max());max_primary_fault=0;reserve_frames=0;completed=0;postfault_steps=0;current_frames=0;postfault_current_frames=0;last_flags=np.zeros(144,dtype='u4')
    last_contact_energy=0.;last_loads={};started=time.monotonic();brake_request_time=None
    magnetic_initial=None;magnetic_final=None;temperature_exchange=0.;receiver_coupled=plant.wayside.get('accepted_for_simulation') is True
    load_peaks={};load_peak_values={};module_force_min=np.full((6,24,3),np.inf);module_force_max=np.full((6,24,3),-np.inf)
    if not receiver_coupled:holds.append('new candidate useful wayside force/normal map not numerically accepted; no wayside braking/propulsion credited in incoming-state safety study')
    if route_stops_m is not None and not authority_events:terminal='hold-authority-composition'
    elif route_stops_m is not None and not receiver_coupled:terminal='hold-wayside-field-map'
    for tick in range(round(duration/dt)) if terminal is None else []:
        now=tick*dt;fault_active=case['fault']!='none' and now>=fault_at
        if fault_active and not fault_seen:
            fault_seen=True;fault_tick=tick;events.append(dict(time_s=now,event='fault-injected',fault=case['fault'],configuration_sha256=identity))
        gaps,local_z,local_y=body_gaps(a,plant,state,guide,centres,radius)
        if np.any(gaps<a['minimum_gap_m']) or np.any(gaps>a['maximum_gap_m']):
            terminal='failed-field-domain-or-pole-contact';safety_failures.append('actual geometric pole gap outside defined field domain');break
        try:fields=plant.evaluate(gaps,currents,temperature)
        except MapDomain as exc:terminal='hold-magnetic-map-domain';holds.append(str(exc));break
        if magnetic_initial is None:magnetic_initial=float(fields['stored_energy_j'].sum());magnetic_final=magnetic_initial
        history.append(gaps.copy());delay=case.get('sensor_delay_s',0.) if fault_active else 0.;sample=history[max(0,len(history)-1-round(delay/dt))].copy()
        if fault_active and case['fault']=='map-errors':
            errors=case.get('map_error_fraction',.1)*np.tile([-1.,1.],72)
            sample+=np.column_stack([errors*.003,errors*.003,errors*.002,-errors*.002])
        modes=measured_modes(plant,sample);mode_velocity=(modes-last_modes)/dt;last_modes=modes.copy()
        high_map=plant.module.evaluate_batch(sample,np.tile([a['current_limit_a']*a['preferred_current_fraction'],0.],(144,1)),temperature,initial_flux_wb=fields['flux_state_wb'])
        low_map=plant.module.evaluate_batch(sample,np.tile([-a['current_limit_a']*a['preferred_negative_current_fraction'],0.],(144,1)),temperature,initial_flux_wb=fields['flux_state_wb'])
        capacity_valid=np.asarray(high_map['valid'])&np.asarray(low_map['valid'])
        controller.physical_limits=np.stack((low_map['upward_n'],np.minimum(a['maximum_module_force_n'],high_map['upward_n'])),axis=-1).reshape(6,24,2)
        requests,allocation_status=controller.allocation(a,levers,mass,modes,mode_velocity,speed**2*curvature)
        target,valid,residual=plant.inverse(requests.reshape(144,2),sample,temperature,currents)
        maximum['inverse_force_residual_n']=max(maximum['inverse_force_residual_n'],float(np.max(np.abs(residual))))
        # Independent local reference is a per-module map/LUT current, then a
        # gap/lateral correction. Its physical map calibration remains open.
        local_ref=np.zeros((144,2));local_ref[:,0]=mass*a['gravity_m_s2']/24
        reserve_target,reserve_valid,_=plant.inverse(local_ref,gaps,temperature,currents,channel='reserve')
        gap_error=gaps[:,:2].mean(axis=1)-a['nominal_gap_m'];gap_rate=(gaps[:,:2].mean(axis=1)-last_gaps[:,:2].mean(axis=1))/dt
        lat=(gaps[:,3]-gaps[:,2])/2;lat_rate=((gaps[:,3]-gaps[:,2])-(last_gaps[:,3]-last_gaps[:,2]))/(2*dt)
        reserve_target[:,0]+=a['reserve_gap_gain_a_m']*gap_error+a['reserve_gap_damping_a_s_m']*gap_rate
        reserve_target[:,1]-=a['reserve_lateral_gain_a_m']*lat+a['reserve_lateral_damping_a_s_m']*lat_rate
        reserve_target=np.clip(reserve_target,-a['current_limit_a'],a['current_limit_a'])
        last_gaps=gaps.copy();flags=np.zeros(144,dtype='u4')
        if fault_active:
            if case['fault'] in {'main-power-loss','reserve-depletion','no-capture'}:flags|=1
            elif case['fault']=='inverter-loss':flags[int(case.get('fault_module',0))]|=8
            elif case['fault']=='sensing-dropout':flags|=2
            elif case['fault']=='sensing-disagreement':flags|=4
            elif case['fault']=='watchdog-delay':flags|=16
            if now<fault_at+a['reserve_transfer_delay_s']:flags|=512
        for car in range(6):
            if depleted_mask&(1<<car):flags[car*24:(car+1)*24]|=128
        flags[~valid|~capacity_valid]|=2;flags[~reserve_valid]|=32
        emf=np.einsum('nij,nj->ni',fields['dflux_dgap_wb_m'],(gaps-history[-2])/dt) if len(history)>1 else np.zeros((144,2))
        temperature_before=temperature.copy()
        try:
            electrical,currents,temperature=controller.current_step(resistance=fields['resistance_ohm'],inductance=fields['incremental_inductance_h'],emf=emf,targets=target,reserve_targets=reserve_target,current=currents,temperature=temperature,copper_mass=plant.copper_mass,cooling=plant.cooling,faults=flags,reserve_energy=reserve,reserve_aux=reserve_aux)
        except ValueError as exc:terminal='failed-current-plant';safety_failures.append(str(exc));break
        current_frames+=1;postfault_current_frames+=bool(fault_active);last_flags=flags.copy()
        reserve_after=np.array(electrical.reserve_remaining_j)
        reserve_power=(reserve-reserve_after)/dt*power['conversion_efficiency']/1000.
        maximum['reserve_output_kw_per_car']=max(maximum['reserve_output_kw_per_car'],float(reserve_power.max()))
        reserve=reserve_after;depleted_mask|=electrical.reserve_depleted_cars
        max_primary_fault=max(max_primary_fault,electrical.primary_fault_channels);reserve_frames+=bool(electrical.reserve_used_channels)
        for key,field in [('primary_dc_j','primary_dc_j'),('reserve_dc_j','reserve_dc_j'),('reserve_draw_j','reserve_draw_j'),('copper_heat_j','copper_heat_j'),('cooling_j','rejected_cooling_j'),('emf_work_j','emf_work_j'),('incremental_field_change_j','field_change_j')]:energy[key]+=float(getattr(electrical,field))
        try:fields=plant.evaluate(gaps,currents,temperature)
        except MapDomain as exc:terminal='hold-magnetic-map-after-current-step';holds.append(str(exc));break
        frozen_temperature=plant.evaluate(gaps,currents,temperature_before)
        temperature_exchange+=float(np.sum(fields['stored_energy_j']-frozen_temperature['stored_energy_j']))
        up=fields['upward_n'].reshape(6,24);left=fields['leftward_n'].reshape(6,24);local_moments=fields['local_moments_nm'].reshape(6,24,3)
        brake_requested=now>=a['receiver_brake_start_s'] or fault_active or any(allocation_status)
        protocol=authority_at(authority_events,now,identity) if route_stops_m is not None else dict(permitted=True)
        if not protocol['permitted']:brake_requested=True
        if brake_requested and brake_request_time is None:brake_request_time=now
        receive_request=np.full(6,a['receiver_brake_force_n_per_car'] if now>=a['receiver_brake_start_s'] and protocol['permitted'] else 0.)
        # Midspan safety never credits an imagined receiving stator at that site.
        if 'midspan' in case['id'] or case['fault']=='no-capture':receive_request[:]=0.
        unavailable=fault_active and case['fault']=='receiver-loss' or not protocol['permitted']
        if receiver_coupled:
            # Replaced below by the geometry-bound distributed group adapter;
            # the historical one-circuit coupon is never promoted by this flag.
            raise ValueError('accepted wayside map requires the distributed group adapter, not the one-circuit receiver coupon')
        receiver_result=ReceiverOutput();receive_force=np.zeros(6)
        shoe_x=(centres[:,None]+shoe_positions[:,0]).ravel();rail,rail_v=guide.pose(shoe_x,np.tile(shoe_positions[:,1],6),np.full(48,shoe['contact_interface']['fixed_top_z_m']));rail=rail.reshape(6,8,3);rail_v=rail_v.reshape(6,8,3)
        shoe_z=state[:,1,None]+state[:,2,None]*shoe_levers[:,1]-state[:,3,None]*shoe_levers[:,0]-rail[:,:,0]
        shoe_y=state[:,0,None]+state[:,4,None]*shoe_levers[:,0]-state[:,2,None]*shoe_levers[:,2]-rail[:,:,1]-curve_offsets(shoe_positions[:,0],radius)
        shoe_vz=velocity[:,1,None]+velocity[:,2,None]*shoe_levers[:,1]-velocity[:,3,None]*shoe_levers[:,0]-rail_v[:,:,0]
        shoe_vy=velocity[:,0,None]+velocity[:,4,None]*shoe_levers[:,0]-velocity[:,2,None]*shoe_levers[:,2]-rail_v[:,:,1]
        penetration=-shoe_z-capture['engagement_drop_m'];normal,contact_energy,capture_diss=contact_force(penetration,-shoe_vz,capture['vertical_stiffness_n_m'],capture['vertical_damping_n_s_m'])
        side_pen=np.abs(shoe_y)-a['contact_lateral_clearance_m'];side_raw,side_energy,side_diss=contact_force(side_pen,np.sign(shoe_y)*shoe_vy,a['contact_lateral_stiffness_n_m'],a['contact_lateral_damping_n_s_m']);side=-np.sign(shoe_y)*side_raw
        if case['fault']=='no-capture':normal[:]=0.;side[:]=0.;contact_energy[:]=0.;side_energy[:]=0.;capture_diss[:]=0.;side_diss[:]=0.
        clamp_engaged=brake_requested and brake_request_time is not None and now>=brake_request_time+brake['engagement_delay_s']
        friction=np.zeros(6)
        if clamp_engaged:
            desired_friction=-np.sign(speed)*brake_force_limit
            stop_force=-mass*speed/dt-receive_force
            friction=np.where(np.abs(stop_force)<=brake_force_limit,stop_force,desired_friction)
        if case['fault']=='no-capture':friction[:]=0.
        drag=-np.sign(speed)*(300.+2.*speed*speed)
        long_force=receive_force+friction+drag
        generalized=np.zeros((6,5));generalized[:,0]=left.sum(axis=1)+side.sum(axis=1)-mass*speed*speed*curvature
        generalized[:,1]=up.sum(axis=1)+normal.sum(axis=1)-mass*a['gravity_m_s2']
        generalized[:,2]=np.sum(levers[:,1]*up-levers[:,2]*left+local_moments[:,:,0],axis=1)+np.sum(shoe_levers[:,1]*normal-shoe_levers[:,2]*side,axis=1)
        generalized[:,3]=np.sum(-levers[:,0]*up+local_moments[:,:,1],axis=1)-np.sum(shoe_levers[:,0]*normal,axis=1)+friction*float(brake_positions[:,2].mean())
        generalized[:,4]=np.sum(levers[:,0]*left+local_moments[:,:,2],axis=1)+np.sum(shoe_levers[:,0]*side,axis=1)-friction*float(brake_positions[:,1].mean())
        extension=centres[:-1]-centres[1:]-17.5+coupler_z*(state[:-1,3]-state[1:,3]);relative_speed=speed[:-1]-speed[1:]+coupler_z*(velocity[:-1,3]-velocity[1:,3])
        coupler_force=coupler_k*extension+coupler_c*relative_speed
        long_force[:-1]-=coupler_force;long_force[1:]+=coupler_force
        generalized[:-1,3]-=coupler_z*coupler_force;generalized[1:,3]+=coupler_z*coupler_force
        energy['coupler_damping_j']+=float(coupler_c*np.sum(relative_speed**2)*dt)
        maximum['coupler_force_n']=max(maximum['coupler_force_n'],float(np.max(np.abs(coupler_force))))
        maximum['coupler_extension_m']=max(maximum['coupler_extension_m'],float(np.max(np.abs(extension))))
        old_state=state.copy();old_velocity=velocity.copy();old_speed=speed.copy();old_ke=_kinetic(velocity,mass,inertia)
        velocity[:,:2]+=generalized[:,:2]/mass*dt
        omega=old_velocity[:,2:];gyro=np.cross(omega,np.einsum('ij,nj->ni',inertia,omega));velocity[:,2:]+=np.linalg.solve(inertia,(generalized[:,2:]-gyro).T).T*dt
        state+=dt*(old_velocity+velocity)/2
        speed+=dt*(long_force/mass+curvature*old_speed*old_velocity[:,0]);centres+=dt*(old_speed+speed)/2
        body_work=float(np.sum(generalized*(state-old_state)));energy['rigid_body_balance_residual_j']+=_kinetic(velocity,mass,inertia)-old_ke-body_work
        heat=np.maximum(0.,-friction*(old_speed+speed)/2*dt);energy['brake_heat_j']+=float(heat.sum());energy['rolling_drag_heat_j']+=float(np.sum(-drag*(old_speed+speed)/2*dt))
        brake_temperature+=heat*brake['vehicle_heat_fraction']/(clamp['quantity_per_car']*brake['thermal_effective_mass_kg']*brake['thermal_specific_heat_j_kg_k'])
        energy['capture_damping_j']+=float(np.sum(capture_diss+side_diss))*dt
        gx=np.concatenate((px,shoe_x));gy=np.tile(np.r_[plant.positions[:,1]],6);gy=np.r_[gy,np.tile(shoe_positions[:,1],6)]
        gz=np.r_[np.tile(plant.positions[:,2],6),np.full(48,shoe['contact_interface']['fixed_top_z_m'])]
        # Brake Fx acts on the rail at its actual height. Keep that reaction
        # distinct from support/capture normal forces and add its pitch/yaw
        # couple to the beam modes and bearing reactions.
        brake_x=(centres[:,None]+np.asarray(clamp['positions_m'])[:,0]).ravel();brake_y=np.tile(np.asarray(clamp['positions_m'])[:,1],6);brake_z=np.tile(np.asarray(clamp['positions_m'])[:,2],6)
        gx=np.r_[gx,brake_x];gy=np.r_[gy,brake_y];gz=np.r_[gz,brake_z]
        normal_up=np.r_[up.ravel(),normal.ravel(),np.zeros(24)];normal_left=np.r_[left.ravel(),side.ravel(),np.zeros(24)]
        last_loads=guide.advance(gx,gy,gz,normal_up,normal_left,np.r_[local_moments[:,:,0].ravel(),np.zeros(72)],dt,
            vehicle_longitudinal=np.r_[np.zeros(192),np.repeat(friction/4,4)],vehicle_pitch_moment=np.r_[local_moments[:,:,1].ravel(),np.zeros(72)],vehicle_yaw_moment=np.r_[local_moments[:,:,2].ravel(),np.zeros(72)])
        world_forces=np.stack((np.zeros_like(up),left,up),axis=-1)
        module_force_min=np.minimum(module_force_min,world_forces);module_force_max=np.maximum(module_force_max,world_forces)
        measures=dict(module_upward_n=float(up.max()),module_lateral_n=float(np.abs(left).max()),capture_n=float(normal.max()),brake_n=float(np.abs(friction).max()),
            roll_rad=float(np.abs(state[:,2]).max()),support_reaction_n=last_loads['peak_support_reaction_n'],torsion_nm=last_loads['peak_torsion_nm'],coupler_force_n=float(np.abs(coupler_force).max()))
        for criterion,value in measures.items():
            if criterion not in load_peak_values or value>load_peak_values[criterion]:
                load_peak_values[criterion]=value
                load_peaks[criterion]=dict(configuration_sha256=identity,tick=tick+1,time_s=(tick+1)*dt,criterion=criterion,value=value,
                    coordinate_frame='World x forward,y left,z up; small-angle lever/wrench model',car_centres_m=centres.tolist(),car_cg_local_m=plant.cg.tolist(),body_modes=state.tolist(),
                    module_positions_local_m=plant.positions.tolist(),module_worldforces_n=world_forces.tolist(),module_local_moments_nm=local_moments.tolist(),
                    car_linear_acceleration_m_s2=np.column_stack(((speed-old_speed)/dt,(velocity[:,:2]-old_velocity[:,:2])/dt)).tolist(),car_angular_acceleration_rad_s2=((velocity[:,2:]-old_velocity[:,2:])/dt).tolist(),
                    inertial_wrench_n_nm=np.column_stack((long_force,generalized)).tolist(),capture_points_local_m=shoe_force_positions.tolist(),capture_worldforces_n=np.stack((np.zeros_like(normal),side,normal),axis=-1).tolist(),
                    brake_points_local_m=np.asarray(clamp['positions_m']).tolist(),brake_force_per_car_n=friction.tolist(),coupler_force_n=coupler_force.tolist(),
                    guideway_x_m=gx.tolist(),guideway_y_m=gy.tolist(),guideway_z_m=gz.tolist(),guideway_applied_upward_reaction_n=(-normal_up).tolist(),guideway_applied_lateral_reaction_n=(-normal_left).tolist(),guideway_applied_longitudinal_reaction_n=(-np.r_[np.zeros(192),np.repeat(friction/4,4)]).tolist(),guideway_reactions=last_loads)
        px=(centres[:,None]+plant.positions[:,0]).ravel()
        energy['guideway_balance_residual_j']+=last_loads['mechanical_energy_residual_j'];energy['guideway_heat_j']=guide.dissipated
        completed+=1;postfault_steps+=fault_active
        minimum_gap=min(minimum_gap,float(gaps.min()));maximum_gap=max(maximum_gap,float(gaps.max()))
        for key,value in [('current_a',electrical.peak_current_a),('voltage_v',electrical.peak_voltage_v),('temperature_c',float(temperature.max())),('brake_temperature_c',float(brake_temperature.max())),('receiver_temperature_c',receiver_temperature),('upward_n',float(up.max())),('guidance_n',float(np.abs(left).max())),('capture_n',float(normal.max())),('capture_compression_m',float(np.maximum(penetration,0.).max())),('lateral_capture_n',float(np.abs(side).max())),('roll_rad',float(np.abs(state[:,2]).max())),('pitch_rad',float(np.abs(state[:,3]).max())),('yaw_rad',float(np.abs(state[:,4]).max())),('support_reaction_n',last_loads['peak_support_reaction_n']),('torsion_nm',last_loads['peak_torsion_nm']),('joint_rotation_rad',last_loads['maximum_joint_rotation_rad']),('rl_residual_j',electrical.maximum_rl_residual_j),('receiver_rl_residual_j',receiver_result.maximum_residual_j)]:maximum[key]=max(maximum[key],value)
        last_contact_energy=float(np.sum(contact_energy+side_energy))
        next_gaps,_,_=body_gaps(a,plant,state,guide,centres,radius)
        if np.all((next_gaps>=a['minimum_gap_m'])&(next_gaps<=a['maximum_gap_m'])):
            try:magnetic_final=float(plant.evaluate(next_gaps,currents,temperature)['stored_energy_j'].sum())
            except MapDomain:magnetic_final=None
        else:magnetic_final=None
        if tick%round(a['trace_interval_s']/dt)==0:
            trace.append(dict(tick=tick+1,time_s=(tick+1)*dt,configuration_sha256=identity,speed_m_s=speed.tolist(),car_centres_m=centres.tolist(),body_modes=state.tolist(),body_mode_velocities=velocity.tolist(),minimum_gap_m=float(gaps.min()),maximum_gap_m=float(gaps.max()),peak_lift_current_a=float(np.abs(currents[:,0]).max()),peak_guidance_current_a=float(np.abs(currents[:,1]).max()),maximum_temperature_c=float(temperature.max()),reserve_remaining_j=reserve.tolist(),capture_reaction_n=normal.sum(axis=1).tolist(),receiver_force_n=receive_force.tolist(),brake_force_n=friction.tolist(),primary_fault_channels=electrical.primary_fault_channels,reserve_used_channels=electrical.reserve_used_channels,guideway_reactions_n=last_loads['reactions_n']))
        if not np.isfinite(state).all() or not np.isfinite(speed).all():terminal='failed-numerical-state';break
        if maximum['capture_n']>capture['maximum_normal_force_n'] or maximum['capture_compression_m']>capture['maximum_compression_m']:
            terminal='failed-capture-capacity';safety_failures.append('declared shoe force/compression screen exceeded');break
        if maximum['temperature_c']>a['temperature_screen_c'] or maximum['brake_temperature_c']>brake['temperature_screen_c']:
            terminal='failed-thermal-capacity';safety_failures.append('declared winding/brake temperature screen exceeded');break
        if maximum['reserve_output_kw_per_car']>battery['peak_output_kw']:
            terminal='failed-reserve-output-power';safety_failures.append('counted independent reserve peak output exceeded');break
        stopped=np.max(np.abs(speed))<=a['stop_speed_m_s'] and np.max(np.abs(velocity))<=a['stop_vertical_speed_m_s']
        supported=stopped and minimum_gap>=a['minimum_gap_m'] and float(normal.sum())==0. and np.all(reserve>0)
        captured=stopped and np.all(normal.sum(axis=1)>0.) and np.all(up.sum(axis=1)+normal.sum(axis=1)>=.95*mass*a['gravity_m_s2'])
        stable=stable+dt if supported or captured else 0.
        if stable>=a['stable_stop_hold_s']:
            terminal='supported-stop' if supported else 'captured-stop';events.append(dict(time_s=(tick+1)*dt,event=terminal,configuration_sha256=identity));break
    if terminal is None:terminal='failed-timeout-without-stable-stop'
    safe=terminal in {'supported-stop','captured-stop'}
    if case['fault']!='none' and (not fault_seen or postfault_steps==0):safe=False;safety_failures.append('fault was not physically continued')
    screens=dict(terminal_supported_or_captured=safe,initial_equilibrium=initial_equilibrium,
        current=float(maximum['current_a'])<=a['current_limit_a'],module_force=maximum['upward_n']<=a['maximum_module_force_n'],
        guidance_force=maximum['guidance_n']<=a['maximum_guidance_force_n'],temperature=maximum['temperature_c']<=a['temperature_screen_c'],
        actual_rust_electrical_balance=maximum['rl_residual_j']<=a['rl_energy_absolute_tolerance_j'],receiver_electrical_balance=maximum['receiver_rl_residual_j']<=a['rl_energy_absolute_tolerance_j'],
        roll=maximum['roll_rad']<=a['maximum_body_roll_rad'],pitch=maximum['pitch_rad']<=a['maximum_body_pitch_rad'],yaw=maximum['yaw_rad']<=a['maximum_body_yaw_rad'],
        joint_rotation=maximum['joint_rotation_rad']<=a['guideway']['joint_rotation_screen_rad'],support_reaction=maximum['support_reaction_n']<=a['guideway']['support_reaction_screen_n'],
        torsion=maximum['torsion_nm']<=a['guideway']['torsion_screen_nm'],complete_route_composition=route_stops_m is None,
        reserve_output_power=maximum['reserve_output_kw_per_car']<=battery['peak_output_kw'],coupler_force=maximum['coupler_force_n']<=a['coupler_force_screen_n'],
        wayside_map_and_group_composition=receiver_coupled)
    coupler_stored=.5*coupler_k*float(np.sum((centres[:-1]-centres[1:]-17.5+coupler_z*(state[:-1,3]-state[1:,3]))**2))
    mechanical_final=.5*mass*float(np.sum(speed**2))+_kinetic(velocity,mass,inertia)+mass*a['gravity_m_s2']*float(state[:,1].sum())+guide.energy()+last_contact_energy+coupler_stored
    dissipated=energy['copper_heat_j']+energy['brake_heat_j']+energy['guideway_heat_j']+energy['capture_damping_j']+energy['rolling_drag_heat_j']+energy['coupler_damping_j']
    supply=energy['primary_dc_j']+energy['reserve_dc_j'];balance=None
    if magnetic_initial is not None and magnetic_final is not None:
        balance=(magnetic_final-magnetic_initial)+(mechanical_final-mechanical_initial)+dissipated-supply-temperature_exchange
    normalizer=max(1000.,abs(mechanical_initial),dissipated,abs(supply))
    screens['nonlinear_electromechanical_energy']=balance is not None and abs(balance)<=a['mechanical_relative_energy_tolerance']*normalizer
    screens={k:bool(v) for k,v in screens.items()}
    contact_qualified=shoe['contact_interface'].get('fit_verified') is True and clamp['contact_interface'].get('fit_verified') is True
    numerical_screens={k:v for k,v in screens.items() if k not in {'wayside_map_and_group_composition','complete_route_composition'}}
    numerical_pass=all(numerical_screens.values())
    screens['counted_contact_geometry_verified']=contact_qualified
    if not contact_qualified:holds.append('Counted contact-plane/hanger/tie geometry, rail anchors, friction and physical strength have not been independently verified; a conditional contact-model stop is not accepted recovery')
    return dict(schema='osr-continued-full-dynamics-run/1',case=case,case_sha256=digest(encoded(case)),configuration_sha256=identity,
        definition_sha256=digest(encoded(plant.definition)),assumptions_sha256=input_sha256,evaluated_assumptions_sha256=digest(encoded(a)),mass_kg_per_car=mass,mass_properties=plant.definition['mass_properties'],effective_case_inertia_kg_m2=inertia.tolist(),
        terminal_state=terminal,study_pass=all(screens.values()),conditional_dynamics_screens_pass=numerical_pass,screens=screens,holds=holds,safety_failures=safety_failures,initial_inverse=initial_inverse,fault_injected=fault_seen,fault_tick=fault_tick,post_fault_steps=postfault_steps,
        executed_steps=completed,executed_s=completed*dt,executed_current_frames=current_frames,executed_current_microsteps=current_frames*round(dt/a['current_step_s']),post_fault_current_frames=postfault_current_frames,
        final_current_state=dict(current_a=currents.tolist(),temperature_c=temperature.tolist(),gap_m=gaps.tolist(),fault_inputs=last_flags.tolist(),reserve_remaining_j=reserve.tolist(),
            scope='The last current frame can precede a refused nonlinear force evaluation. No body force is extrapolated beyond that failed magnetic domain.'),
        requested_s=duration,maximum=maximum,minimum_gap_m=minimum_gap,maximum_gap_m=maximum_gap,
        energy=dict(**energy,initial_mechanical_j=mechanical_initial,final_mechanical_j=mechanical_final,reserve_initial_j=initial_reserve.tolist(),reserve_final_j=reserve.tolist(),
                    reserve_energy_residual_j=float(initial_reserve.sum()-reserve.sum()-energy['reserve_draw_j']),coupler_stored_j=coupler_stored,magnetic_initial_j=magnetic_initial,magnetic_final_j=magnetic_final,
                    magnetic_temperature_exchange_j=temperature_exchange,nonlinear_electromechanical_residual_j=balance,relative_balance_error=abs(balance)/normalizer if balance is not None else None,
                    frozen_geometry_incremental_rl_audit=True,full_nonlinear_magnetic_energy_closed=screens['nonlinear_electromechanical_energy'],physical_energy_model_validated=False),
        current_kernel=dict(actual_rust_drive_evaluate=True,actual_rust_wrench_allocation=True,two_circuits_per_module=True,mutual_inductance_in_plant=True,continued_freewheel_after_refusal=True,primary_fault_channels=max_primary_fault,reserve_frames=reserve_frames),
        guideway_loads=last_loads,load_export=dict(configuration_sha256=identity,step_s=dt,module_worldforce_min_n=module_force_min.tolist() if completed else None,module_worldforce_max_n=module_force_max.tolist() if completed else None,
            peak_frames=load_peaks,scope='Actual computed force extrema from every1ms mechanical frame; peak snapshots preserve simultaneous load combinations. They do not assert every component maximum occurs at once.'),
        guideway_properties=civil,axial_properties=axial,preferred_support_vector=preferred,preferred_support_enabled=controller.preferred is not None,route_stops_m=route_stops_m,authority_events_sha256=digest(encoded(authority_events)) if authority_events else None,
        route_composition_scope='Authority interface is source-bound; full stop/dwell/charge execution and terminal qualification remain held' if route_stops_m else 'Bounded continued-fault segment, not an entire railway service',
        events=events,trace=trace,elapsed_host_s=time.monotonic()-started,scope='Six rigid equipment-derived bodies, actual scalar Rust lift/guidance currents in reciprocal2×2 incrementalRL plants, nonlinear assumed shared magnetic maps, first guideway modes and unilateral capture/friction fixtures. Shell modes, nonlinear bearings/soil/joints, calibrated losses and target hardware timing remain open.',**FLAGS)


def full_line_attempt(route_stops_m=None,*,kernel_path=None,directory=None):
    """Execute real authority-to-current composition; refuse failed field maps.

    An applicable failed map is a launch hold. A zero-command refusal is recorded
    as an unexecuted trip, never as a simulated safe full-line service.
    """
    a=load();stops=a['route_stops_m'] if route_stops_m is None else list(route_stops_m)
    plant=MagneticPlant();identity=plant.identity
    if kernel_path is None:kernel_path,_=build_kernel()
    from . import candidate_authority
    origin=200.;front=stops[0];tail=front-104.5;centres=origin+front-8.5-np.arange(6)*17.5
    groups=[dict(id=f'departure/{i}',start_m=origin+stops[0]-104.5+5*i,end_m=origin+stops[0]-104.5+5*(i+1)) for i in range(70)]
    groups += [dict(id=f'arrival/{i}',start_m=origin+stops[1]-350+5*i,end_m=origin+stops[1]-350+5*(i+1)) for i in range(70)]
    field=plant.module.propulsion_group_map(centres,np.zeros(6),np.full((6,2),a['nominal_gap_m']),groups,np.zeros((140,2)))
    if field['configuration_sha256']!=identity:raise ValueError('full-line field candidate differs')
    group_definition=plant.module.propulsion_group_definition(5.)
    nominal=plant.module.inverse_current([plant.mass*a['gravity_m_s2']/24],[0.],[[a['nominal_gap_m']]*4],a['ambient_c'])
    support_ready=bool(np.all(nominal['valid']) and np.all(nominal['converged']))
    readiness=dict(receiver_ready=field['accepted_for_simulation'] is True,resistor_ready=True,reserve_ready=True,doors_closed=True,train_healthy=support_ready)
    authority=candidate_authority.AuthorityClient(identity,stops,directory=directory)
    try:
        first=authority.prepare(0,0.,readiness=readiness)
        decision=authority.step(.01,front,tail,0.)
        protocol=authority_at([decision],.01,identity)
        permitted=protocol['permitted'] and field['accepted_for_simulation'] is True
        group=GroupPlant(C.CDLL(str(kernel_path)),identity,len(groups))
        lam=np.asarray(field['lambda_wb']).sum(axis=1);phase=np.angle(lam);flux=np.abs(lam)
        result,average=group.tick(resistance=field['group_R_ohm'],inductance=field['group_L_h'],phase=phase,omega=np.zeros(140),flux=flux,
            targets=np.zeros(140),emf=np.zeros((140,2)),copper_mass=field['group_copper_mass_kg'],current_limit=field['group_current_limit_a'],bus=group_definition['dc_bus_v'],
            mode=0,gates=15 if permitted else 0,unavailable=not permitted)
        final_decision=authority.step(.02,front,tail,0.)
    finally:receipt=authority.receipt()
    candidate_authority.verify_receipt(authority.directory,configuration_sha256=identity,replay=True)
    def complex_values(value):
        z=np.asarray(value);return dict(real=z.real.tolist(),imag=z.imag.tolist())
    return dict(schema='osr-full-line-electromechanical-attempt/1',configuration_sha256=identity,route_stops_m=stops,route_length_m=float(stops[-1]-stops[0]),
        front_m=front,tail_m=tail,internal_origin_offset_m=origin,car_centres_m=centres.tolist(),requested_stops=len(stops),arrived_stops=1,
        full_trip_executed=False,study_pass=False,terminal_state='hold-known-propulsion-field-failure' if not field['accepted_for_simulation'] else 'hold-unexecuted-complete-trip',
        actual_rust_authority=True,actual_rust_current_plant=True,actual_protocol_permitted=protocol['permitted'],map_adoption_permitted=bool(field['accepted_for_simulation']),
        nominal_motion_authorised=False,zero_command_is_not_safe_completion=True,first_prepare=first,decision=decision,final_decision=final_decision,authority_execution=receipt,
        group_count=len(groups),groups=groups,group_definition=group_definition,
        field=dict(field_numerically_converged=field['field_numerically_converged'],domain_valid=field['domain_valid'],accepted_for_simulation=field['accepted_for_simulation'],
            demag_margin_after_armature_bound_a_m=field['demag_margin_after_armature_bound_a_m'],hold=field['applicability_hold'],lambda_wb=complex_values(field['lambda_wb']),dpsi_dx_wb_m=complex_values(field['dpsi_dx_wb_m']),
            dpsi_dgap_side_wb_m=complex_values(field['dpsi_dgap_side_wb_m']),group_R_ohm=np.asarray(field['group_R_ohm']).tolist(),group_L_h=np.asarray(field['group_L_h']).tolist()),
        readiness=readiness,static_support=dict(valid=support_ready,requested_upward_n_per_module=plant.mass*a['gravity_m_s2']/24,current_a=np.asarray(nominal['current_a']).tolist(),force_residual_n=np.asarray(nominal['force_residual_n']).tolist()),
        current_execution=dict(virtual_microsteps=20,refused_microsteps=int(result.refused_microsteps),maximum_current_a=float(np.abs(average).max()),dc_j=result.dc_j,rl_residual_j=result.maximum_residual_j,
            retained_current_after_refusal=True,physical_output_authorised=False),dispatch_basis_s=a['dispatch_basis_s'],
        holds=['Applicable refined propulsion demagnetization/convergence failure prevents nominal launch; no old wayside law inherited.',
            'Four-stop travel/dwell/charge not executed.240s dispatch basis is not a proved full-line headway.',
            'Rigid-array terminal curves and counted brake/capture fit/qualification remain open.'],**FLAGS)


def _run_case(arguments):
    case,path,civil=arguments
    return simulate(case,kernel_path=path,guideway_properties=civil)


def study(*, cases=None,workers=3):
    before=sources();a=load();definition=magnetics().definition();path,build=build_kernel()
    cases=a['cases'] if cases is None else cases;civil=structures().dynamics_properties(definition)
    if type(workers) is not int or not 1<=workers<=3:raise ValueError('one through three bounded offline workers required')
    jobs=[(case,path,civil) for case in cases]
    if workers==1:runs=[_run_case(job) for job in jobs]
    else:
        with ProcessPoolExecutor(max_workers=min(workers,len(jobs))) as executor:runs=list(executor.map(_run_case,jobs))
    attempt=full_line_attempt(kernel_path=path)
    folder=ROOT/attempt['authority_execution']['folder'];raw_authority={n:base64.b64encode((folder/n).read_bytes()).decode('ascii') for n in ('init.json','producer.json','decisions.jsonl.gz','receipt.json')}
    attempt['authority_execution']['folder']='authority'
    if before!=sources() or build['binary_sha256']!=digest(path.read_bytes()):raise ValueError('continued simulation source/binary changed')
    return dict(schema=SCHEMA,source_sha256=before,configuration_sha256=definition['configuration_sha256'],
        definition_sha256=digest(encoded(definition)),mass_properties=definition['mass_properties'],runs=runs,execution=build,full_line_attempt=attempt,authority_raw_base64=raw_authority,
        source_unchanged_after_execution=True,io_design=io_design(),reference_sources=SOURCES,
        simulated_cases=len(runs),supported_stop_cases=sum(r['terminal_state']=='supported-stop' for r in runs),captured_stop_cases=sum(r['terminal_state']=='captured-stop' for r in runs),
        study_pass=all(r['study_pass'] for r in runs) and attempt['study_pass'],conditional_dynamics_pass_cases=sum(r['conditional_dynamics_screens_pass'] for r in runs),
        open_gates=['nonlinear map physical correlation','power stages and shared reserve independence','receiver field/phase and distributed-group compatibility',
                    'complete equipment fit and current-density/cooling duty','nonlinear joints/bearings/soil and flexible body modes','full-line protocol/berth/charge composition',
                    'target MCU/SBC timing/EMI and protection hardware','independent engineering and physical acceptance'],
        scope='Source-bound continued-fault digital study. Every actual terminal outcome, including failed capture, timeout and geometric/map hold, is retained. No output disappearance is classified as a safe stop.',**FLAGS)


def overview(value):
    lines=[]
    for i,run in enumerate(value['runs']):
        colour='#087f78' if run['study_pass'] else '#a72a34';y=85+i*32
        lines.append(f'<text x="24" y="{y}" fill="{colour}">{run["case"]["id"]}: {run["terminal_state"]}; {run["executed_s"]:.3f}s; post-fault {run["post_fault_steps"]} frames</text>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="'+str(130+32*len(lines))+'"><rect width="100%" height="100%" fill="#f1f5f9"/><g font-family="sans-serif" font-size="17"><text x="24" y="38" font-size="25">Continued lift/guidance, reserve and capture — provisional outcomes</text>'+''.join(lines)+'</g></svg>').encode()


def readme(value):
    lines=['# Continued six-car fault dynamics','',value['scope'],'',
        'Exact common candidate: `'+value['configuration_sha256']+'`. AW3 mass per car: '+f"{value['mass_properties']['mass_kg']:,.3f} kg"+'. Equipment-derived CG and full inertia tensor include named reserve/capture/brake allocations once.','',
        '| Case | Physical-model terminal state | Continued post-fault frames | Implemented screens |','|---|---|---:|---|']
    lines += [f"| {r['case']['id']} | {r['terminal_state']} | {r['post_fault_steps']} | {r['study_pass']} |" for r in value['runs']]
    lines += ['', 'Every coil is integrated after a controller refusal: current decays in the explicitly declared freewheel path; permanent-magnet and mutual-circuit forces remain in the plant. A separate reserve controller and power/energy state are modelled. Counted unilateral shoes and friction clamps have declared, unqualified capacities, heat and travel limits. Detection alone never passes a stopping test.','',
        'The actual Rust allocation/current kernels provide bounded current demands and bridge voltages. Python integrates the nonlinear shared magnetic network and rigid-body/guideway states; there is no ideal-force substitution. The stationary1kHz/20kHz clocks and host execution observations do not establish target timing.','',
        'The six-body small-angle modes include vertical/lateral translation and roll/pitch/yaw, equipment-derived full inertia, gyroscopic terms, measured-state longitudinal spring/damper coupling, curvature chord errors, per-module asymmetry and per-span vertical/lateral/torsional modes. A rigid band does not automatically follow a tight curve. Guideway deadweight reactions include all counted stock; live modes reference dead-load-cambered geometry. Nonlinear magnetic energy, RL work, modal work, friction and reserve-energy balances are retained separately. Material hysteresis, nonlinear soil/joints and omitted shell modes remain open.','',
        'The actual Rust research allocator starts from source-bound minimax body-load preferences and enforces current-map residual-lift minimum/maximum forces, wrench and slew constraints. Static LP bounds iterate against actual six-car/guideway pole gaps. The previous zero-lift preference is not realizable merely because its force balance passes: permanent magnets still lift and cancellation can violate current/demagnetization limits. Full current inversion and actual bridge/RL dynamics execute every mechanical frame.','',
        'The receiver dq coupon is explicitly hypothetical. Its single .12Wb/4kA equivalent circuit cannot supply20kN: the actual Rust current guard refuses that demand. It must not be represented as a validated70group receiver or as the new magnetic geometry’s useful external field. Shared-core leakage/no-map and dedicated passive propulsion-band alternatives require their own geometry-derived, numerically controlled maps.','',
        'A real source-bound Rust authority producer prepares the complete four-stop fixed line and samples actual front/tail poses. Its decision is composed with the actual140group stationary-alpha-beta current kernel. The refined magnetic-material failure blocks launch: full_trip_executed is false. This is an executed refusal attempt, not completed travel, dwell, charging, terminal turnaround or240s whole-line service. Portable raw protocol records are in [authority/receipt.json](authority/receipt.json). A controller/state-machine prototype for actual-pose dwell/energy/charge holds is present; it has not completed the full-line electromechanical trip.','',
        'Protection contact revision2 counts the named capture pads, steel hanger kits, brake hangers and paired transverse ties in the same vehicle mass/CG/inertia. Two12×200mm wear strips per track add37.68kg/m to the guideway. Contact-plane, magnetic influence, weld/bolt/rail-anchor fit, actuator travel and physical qualification remain holds. In particular,8×50kN pads cannot absorb a whole-car5mm drop within8mm at the present AW3 without sufficient residual/active magnetic support; a failed-capture outcome is preserved. Conditional numerical stopping results never remove these holds.','',
        'Selected development hardware: Raspberry Pi CM5 supervisory SBC and STM32H753XI local MCU. Dual sensing, sequence/configuration/time identity, independent reserve path, watchdog and isolated gate/protection interfaces are specified in interface-spec.json; physical adapters and target deadline measurements remain unexecuted.','',
        'Open gates: '+', '.join(value['open_gates'])+'.','',
        *[f"- [{r['id']}]({r['url']}): {r['scope']}." for r in value['reference_sources']], '',
        'Reproduce explicit study: `tools/automation/osr-python -m engineering.ferrite_maglev.full_dynamics study`. Opening a retained packet never starts a simulation or hardware command.','']
    return '\n'.join(lines)


def publish(output=OUTPUT):
    output=Path(output);value=study();raw=encoded(value)
    if len(raw)>MAX_RAW:raise ValueError('bounded continued dynamics result required')
    files={'study.json.gz':gzip.compress(raw,mtime=0),'overview.svg':overview(value),'interface-spec.json':encoded(value['io_design']),'README.md':readme(value).encode()}
    for name,data in value['authority_raw_base64'].items():files['authority/'+name]=base64.b64decode(data,validate=True)
    output.mkdir(parents=True,exist_ok=True)
    for name,data in files.items():
        (output/name).parent.mkdir(parents=True,exist_ok=True);(output/name).write_bytes(data)
    manifest=dict(schema=SCHEMA,source_sha256=value['source_sha256'],raw_bytes=len(raw),files_sha256={n:digest(v) for n,v in files.items()},**FLAGS)
    (output/'manifest.json').write_bytes(encoded(manifest));return manifest


def verify(output=OUTPUT):
    output=Path(output)
    if output.is_symlink() or any(p.is_symlink() for p in output.parents):raise ValueError('ordinary dynamics packet path required')
    names={'study.json.gz','overview.svg','interface-spec.json','README.md','manifest.json',*('authority/'+n for n in ('init.json','producer.json','decisions.jsonl.gz','receipt.json'))}
    paths=list(output.rglob('*'))
    if any(p.is_symlink() for p in paths) or {p.relative_to(output).as_posix() for p in paths if p.is_file()}!=names or {p.relative_to(output).as_posix() for p in paths if p.is_dir()}!={'authority'}:raise ValueError('exact ordinary continued dynamics inventory required')
    if any(not p.is_file() and not p.is_dir() or p.is_file() and p.stat().st_size>MAX_RAW for p in paths):raise ValueError('bounded ordinary dynamics files required')
    manifest=json.loads((output/'manifest.json').read_bytes())
    if manifest['schema']!=SCHEMA or manifest['source_sha256']!=sources() or any(manifest.get(k) is not False for k in FLAGS):raise ValueError('stale/unqualified dynamics receipt')
    if set(manifest['files_sha256'])!=names-{'manifest.json'} or any(digest((output/n).read_bytes())!=h for n,h in manifest['files_sha256'].items()):raise ValueError('altered continued dynamics payload')
    if type(manifest['raw_bytes']) is not int or not 0<manifest['raw_bytes']<=MAX_RAW:raise ValueError('bounded raw dynamics bytes required')
    with gzip.open(output/'study.json.gz','rb') as stream:raw=stream.read(manifest['raw_bytes']+1)
    if len(raw)!=manifest['raw_bytes']:raise ValueError('dynamics raw size differs')
    value=json.loads(raw);definition=magnetics().definition()
    if value['source_sha256']!=sources() or value['configuration_sha256']!=definition['configuration_sha256'] or value['definition_sha256']!=digest(encoded(definition)) or value['source_unchanged_after_execution'] is not True or any(value.get(k) is not False for k in FLAGS):raise ValueError('dynamics candidate/execution identity differs')
    if [r['case'] for r in value['runs']]!=load()['cases']:raise ValueError('all exact continued fault cases required')
    for r in value['runs']:
        if r['configuration_sha256']!=value['configuration_sha256'] or r['case_sha256']!=digest(encoded(r['case'])) or r['assumptions_sha256']!=digest(encoded(load())) or r['mass_kg_per_car']!=definition['mass_properties']['mass_kg'] or r['study_pass']!=all(r['screens'].values()) or any(r.get(k) is not False for k in FLAGS):raise ValueError('continued run identity/screens differ')
        if r['study_pass'] and (r['terminal_state'] not in {'supported-stop','captured-stop'} or r['case']['fault']!='none' and (not r['fault_injected'] or r['post_fault_steps']==0)):raise ValueError('fault detection cannot stand in for physical continued stop')
        if any(t['configuration_sha256']!=value['configuration_sha256'] for t in r['trace']):raise ValueError('trace candidate differs')
        counts=[r[k] for k in ('executed_steps','executed_current_frames','executed_current_microsteps','post_fault_steps','post_fault_current_frames')]
        if any(type(v) is not int or v<0 for v in counts) or not r['executed_steps']<=r['executed_current_frames']<=r['executed_steps']+1 or r['post_fault_steps']>r['executed_steps'] or r['post_fault_current_frames']>r['executed_current_frames'] or r['post_fault_steps']>r['post_fault_current_frames']:raise ValueError('continued frame counters differ')
        if r['executed_s']!=r['executed_steps']*load()['mechanical_step_s'] or r['executed_current_microsteps']!=20*r['executed_current_frames'] or type(r['fault_injected']) is not bool:raise ValueError('continued clock/counter evidence differs')
        if (not r['fault_injected'] or r['case']['fault']=='none') and (r['post_fault_steps'] or r['post_fault_current_frames'] or r['fault_tick'] is not None):raise ValueError('unexecuted fault cannot earn continuation credit')
        previous_tick=0
        for frame in r['trace']:
            if type(frame['tick']) is not int or not previous_tick<frame['tick']<=r['executed_steps'] or frame['time_s']!=frame['tick']*load()['mechanical_step_s']:raise ValueError('continued trace clock/coverage differs')
            previous_tick=frame['tick']
        if any(type(v) is not bool for v in r['screens'].values()) or r['conditional_dynamics_screens_pass']!=all(v for k,v in r['screens'].items() if k not in {'wayside_map_and_group_composition','complete_route_composition','counted_contact_geometry_verified'}):raise ValueError('conditional numerical screens differ')
        if r['load_export']['configuration_sha256']!=value['configuration_sha256'] or r['guideway_properties']['configuration_sha256']!=value['configuration_sha256'] or r['axial_properties']['configuration_sha256']!=value['configuration_sha256']:raise ValueError('load/civil/axial candidate differs')
        initial=r.get('initial_inverse')
        if initial is not None:
            current=np.asarray(initial['current_a'],float);gaps=np.asarray(initial['gaps_m'],float);request=np.asarray(initial['requested_module_forces_n'],float).reshape(144,2)
            if current.shape!=(144,2) or gaps.shape!=(144,4) or not np.isfinite(current).all() or not np.isfinite(gaps).all() or abs(current).max()>1000 or gaps.min()<=0 or gaps.max()>.1:raise ValueError('bounded initial magnetic screen inputs required')
            independent=magnetics().evaluate_batch(gaps,current,load()['ambient_c']);residual=np.column_stack((independent['upward_n'],independent['leftward_n']))-request
            expected=np.asarray(independent['valid'])&(abs(residual).max(axis=1)<.1)
            if not np.array_equal(expected,np.asarray(initial['valid'])) or not np.allclose(residual,initial['force_residual_n'],atol=.01,rtol=1e-7):raise ValueError('initial force/current/field evidence differs')
            if r['screens']['initial_equilibrium'] and not expected.all():raise ValueError('failed current/return-rail map cannot become passing equilibrium')
        elif r['screens']['initial_equilibrium']:raise ValueError('initial equilibrium lacks exact magnetic evaluation')
    from . import candidate_authority
    attempt=value['full_line_attempt']
    if attempt['configuration_sha256']!=value['configuration_sha256'] or attempt['full_trip_executed'] is not False or attempt['study_pass'] is not False or attempt['nominal_motion_authorised'] is not False:raise ValueError('blocked attempt cannot become completed service')
    if attempt['authority_execution']['folder']!='authority':raise ValueError('portable authority directory required')
    candidate_authority.verify_receipt(output/'authority',configuration_sha256=value['configuration_sha256'],replay=False)
    if set(value['authority_raw_base64'])!={'init.json','producer.json','decisions.jsonl.gz','receipt.json'}:raise ValueError('complete portable authority raw inventory required')
    for name,data in value['authority_raw_base64'].items():
        if name not in {'init.json','producer.json','decisions.jsonl.gz','receipt.json'} or base64.b64decode(data,validate=True)!=(output/'authority'/name).read_bytes():raise ValueError('portable authority raw evidence differs')
    if value['study_pass']!=bool(all(r['study_pass'] for r in value['runs']) and attempt['study_pass']) or value['conditional_dynamics_pass_cases']!=sum(r['conditional_dynamics_screens_pass'] for r in value['runs']):raise ValueError('campaign outcome aggregate differs')
    if value['supported_stop_cases']!=sum(r['terminal_state']=='supported-stop' for r in value['runs']) or value['captured_stop_cases']!=sum(r['terminal_state']=='captured-stop' for r in value['runs']) or value['simulated_cases']!=len(value['runs']):raise ValueError('campaign stop/coverage counts differ')
    if (output/'README.md').read_text()!=readme(value) or (output/'overview.svg').read_bytes()!=overview(value) or json.loads((output/'interface-spec.json').read_bytes())!=io_design():raise ValueError('dynamics presentation differs')
    return manifest


def read_summary(output=OUTPUT):
    verify(output);value=json.loads(gzip.decompress((Path(output)/'study.json.gz').read_bytes()))
    return dict(schema=SCHEMA,configuration_sha256=value['configuration_sha256'],cases=value['simulated_cases'],supported_stops=value['supported_stop_cases'],captured_stops=value['captured_stop_cases'],study_pass=value['study_pass'],conditional_dynamics_pass_cases=value['conditional_dynamics_pass_cases'],full_line_attempt=value['full_line_attempt'],runs=[{k:r[k] for k in ('case','terminal_state','study_pass','conditional_dynamics_screens_pass','maximum','post_fault_steps','executed_s','holds','safety_failures')} for r in value['runs']],open_gates=value['open_gates'],**FLAGS)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('study','publish','verify'),default='verify',nargs='?');args=parser.parse_args()
    value=globals()[args.action]()
    print(json.dumps(value,sort_keys=True,indent=2,allow_nan=False))
