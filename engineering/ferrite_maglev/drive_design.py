"""Construction quantities and executed offline winding-current design studies.

An assumed reluctance circuit is not a magnetic map. The new loops do not
replace the ideal-force moving plant or enable any physical output.
"""
from hashlib import sha256
from copy import deepcopy
from pathlib import Path
import csv
import gzip
import io
import json
import math
import re
import subprocess
import tomllib
import numpy as np
from . import configuration, corridor, model, station

ROOT=model.ROOT
INPUT=Path(__file__).with_name('drive-design.toml')
SUPPLIERS=Path(__file__).parent/'data/drive-suppliers.json'
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/drive-construction'
TEST=ROOT/'engineering/analysis/tests/test_ferrite_maglev_drive_design.py'
SCHEMA='osr-drive-construction/1'
FILES={'study.json.gz','bom.csv','winding-schedule.csv','connections.csv','architecture.svg','construction.svg','README.md','execution.json.gz'}
MAX_FILE=16*1024*1024
MAX_RAW=64*1024*1024
API=['cargo','test','--locked','-p','osr-maglev-control','--test','drives']
RUN=['cargo','run','--locked','-p','osr-maglev-control','--example','winding_replay']
HOLDS=[
 'PM support needs active gap/guidance correction; permanent magnets do not provide qualified passive stability or a guaranteed safe residual after power loss.',
 'SBC supervision, local fast MCU current/gap loops and independent protection are different responsibilities. No hardware adapter, gate drive, target timing or authenticated field transport is implemented.',
 'Support reluctance/force and LSM fundamental flux/R/L are explicit hypotheses. Saturation, shared flux, end effects, normal-force disturbance, eddy losses, temperature and demagnetisation require measured maps.',
 'The local current-loop RL coupons are separate from the retained ideal-force moving train. No actuator-lag stability or complete electromagnetic/vehicle integration is claimed.',
 'The compact coil passes declared volume/depth screens only; conductor routing, insulation, lead exits, magnetic steel, clearances, fastening and cooling remain open. The larger rejected pack is retained.',
 'Long fixed groups need multi-kA bridges and voltage/inductance confirmation. Parallel unequal-back-EMF branches are not accepted as a free current reduction.',
 'The 2400 V corridor bus cannot use a lone 1700 V device as a two-level switch. Catalog industrial drives and the 40 A software coupon do not qualify a full station converter.',
 'Station supply, protection coordination, fault clearing, chopper/resistor redundancy, EMC, fire, cooling and physical acceptance remain open.',
 'All quantities are purchasing/construction candidates, not a released PCB/Gerber or production drawing set. Unit quotations, complete installed cost and local-value percentages remain unknown.',
]

def encoded(v):return (json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def digest(b):return sha256(b).hexdigest()
def sources():
    paths={Path(__file__),INPUT,SUPPLIERS,TEST,ROOT/'Cargo.toml',ROOT/'Cargo.lock',
        ROOT/'crates/osr-maglev-control/Cargo.toml',ROOT/'crates/osr-maglev-control/tests/drives.rs',
        ROOT/'crates/osr-maglev-control/examples/winding_replay.rs',
        *(ROOT/'crates/osr-maglev-control/src').glob('*.rs'),
        *(ROOT/n for n in station.sources()),Path(corridor.__file__),corridor.INPUT,
        *configuration.source_paths()}
    return {p.relative_to(ROOT).as_posix():digest(p.read_bytes()) for p in sorted(paths)}

def load():
    a=tomllib.loads(INPUT.read_text())
    if a['schema']!='osr-drive-construction-input/1':raise ValueError('drive input schema required')
    def positive(value):
        if isinstance(value,list):return all(positive(v) for v in value)
        return type(value) in (int,float) and math.isfinite(value) and value>0
    if not all(positive(v) for name in ('support','launch','material') for v in a[name].values()):raise ValueError('finite positive drive assumptions required')
    s=a['support'];l=a['launch']
    if (s['modules_per_car']!=24 or s['circuits_per_module']!=2 or s['physical_coils_per_module']!=3
        or s['modules_per_car']%s['zone_modules'] or s['peak_current_a']<s['continuous_current_a']
        or s['maximum_fill']>1 or any(i>=o for i,o in zip(s['coil_inner_m'],s['coil_outer_m']))
        or l['faces']!=2 or l['groups_per_direction']!=2 or l['slots_per_pole_per_phase']!=1
        or not math.isclose(l['cassette_m']/l['pole_pitch_m'],10)
        or l['turn_alternatives']!=[1,2,4] or l['primary_zone_m_per_direction']!=350.):
        raise ValueError('bounded declared winding architecture required')
    return a

def copper(a,turns,mean_length,area_mm2,temperature):
    m=a['material'];length=turns*mean_length;area=area_mm2*1e-6
    r20=m['copper_resistivity_20_ohm_m']*length/area
    return dict(turns=turns,length_m=length,area_mm2=area_mm2,volume_m3=length*area,
        copper_kg=length*area*m['copper_density_kg_m3'],resistance_20_ohm=r20,
        resistance_hot_ohm=r20*(1+m['copper_temperature_coefficient_per_k']*(temperature-20.)))

def support(a=None):
    a=load() if a is None else a;s=a['support'];mu=4*math.pi*1e-7
    coil=copper(a,s['turns_per_coil'],s['mean_turn_length_m'],s['conductor_area_mm2'],s['hot_copper_temperature_c'])
    pack=(math.prod(s['coil_outer_m'])-math.prod(s['coil_inner_m']))*s['coil_height_m']
    path=s['series_gaps']*s['gap_m'];b0=s['bias_flux_t'];area=s['pole_area_m2'];n=s['turns_per_coil']
    # Two lift faces in one series-gap circuit; two separately opposed guide
    # faces. The shared flux, steel/ferrite reluctance and mutual L are omitted.
    inductance=mu*n*n*area/path
    def lift_current(force):return (math.sqrt(force*mu/area)-b0)*path/(mu*n)
    c=station.load()['vehicle'];cars=c['cars'];_,cfg,_=model.load()
    rows=[]
    for label,mass in [('tare',model.mass(cfg,cfg['mass']['ferrite_base'],50.)['tare_kg']),
                       ('AW2',model.mass(cfg,cfg['mass']['ferrite_base'],50.)['aw2_kg']),
                       ('AW3',model.mass(cfg,cfg['mass']['ferrite_base'],50.)['aw3_kg'])]:
        force=mass*9.81/s['modules_per_car'];current=lift_current(force)
        rows.append(dict(load=label,car_mass_kg=mass,lift_n_per_module=force,current_a=current,
            lift_copper_w_per_car=s['modules_per_car']*current**2*coil['resistance_hot_ohm'],
            continuous_current_screen=abs(current)<=s['continuous_current_a']))
    guide_slope=2*area*b0*n/path
    lift_peak=area/mu*(b0+mu*n*s['peak_current_a']/path)**2
    voltage=.9*s['bus_v'];at_limit=lift_current(20000.)
    di=max(0.,voltage-coil['resistance_hot_ohm']*abs(at_limit))/inductance
    b20=math.sqrt(20000.*mu/area);slope=2*area*b20*n/path
    return dict(coil=coil,pack_extent_m=[*s['coil_outer_m'],s['coil_height_m']],pack_hole_m=s['coil_inner_m'],
        pack_volume_m3=pack,packing_fraction=coil['volume_m3']/pack,
        packing_screen=coil['volume_m3']/pack<=s['maximum_fill'],lift_inductance_hypothesis_h=inductance,
        guide_series_inductance_without_mutual_h=2*inductance,guide_force_slope_n_a=guide_slope,
        guide_current_for_4kn_a=4000./guide_slope,lift_peak_force_hypothesis_n=lift_peak,
        lift_current_for_20kn_a=at_limit,lift_slew_at_20kn_n_s=di*slope,
        allocator_slew_comparison_n_s=2000000.,allocator_slew_screen=di*slope>=2000000.,
        physical_coils_per_car=s['modules_per_car']*3,circuits_per_car=s['modules_per_car']*2,
        copper_kg_per_car=coil['copper_kg']*s['modules_per_car']*3,
        copper_kg_per_train=coil['copper_kg']*s['modules_per_car']*3*cars,
        peak_10s_adiabatic_c=s['peak_current_a']**2*coil['resistance_hot_ohm']*10/(coil['copper_kg']*a['material']['copper_specific_heat_j_kg_k']),
        legacy_window_depth_m=.060,new_pack_depth_m=s['coil_height_m'],legacy_depth_fit=s['coil_height_m']<=.060,
        loads=rows,independent_support_energy_lower_bound_kwh=rows[-1]['lift_copper_w_per_car']*cars*s['independent_support_seconds']/3600000.,
        independent_energy_scope='Lift copper only. Guidance, drives, sensing, control, temperature margin, conversion, power path and capture remain additional.',
        magnetic_map_qualified=False,actuator_dynamics_connected_to_moving_twin=False,
        added_to_existing_mass_ledger=False,**model.FLAGS)

def support_alternatives(a):
    result=[]
    for label,n,area,height in [('compact-primary',50,16.,.060),('larger-pack',60,20.,.085),('lower-turn',35,25.,.060)]:
        candidate=deepcopy(a);candidate['support'].update(turns_per_coil=n,conductor_area_mm2=area,coil_height_m=height)
        v=support(candidate)
        result.append(dict(id=label,inputs=candidate['support'],result=v,
            provisional_screens_pass=v['packing_screen'] and v['legacy_depth_fit'] and v['allocator_slew_screen']
                and v['lift_current_for_20kn_a']<=candidate['support']['peak_current_a']
                and abs(v['guide_current_for_4kn_a'])<=candidate['support']['continuous_current_a']
                and all(r['continuous_current_screen'] for r in v['loads']),accepted=False))
    return result

def winding(a=None,zone=None,turns=None,bar_area=None):
    a=load() if a is None else a;l=a['launch'];zone=l['primary_zone_m_per_direction'] if zone is None else zone
    turns=l['turns_per_coil'] if turns is None else turns;bar_area=l['bar_area_mm2'] if bar_area is None else bar_area
    if not 25<=zone<=400 or turns not in l['turn_alternatives'] or bar_area not in l['bar_area_alternatives_mm2']:raise ValueError('bounded winding variation required')
    slots=round(l['cassette_m']/l['pole_pitch_m']*3);coils=slots//2
    mean=2*(l['face_width_m']+l['pole_pitch_m']);wire=copper(a,turns,mean,bar_area,l['hot_copper_temperature_c'])
    group=zone/l['groups_per_direction'];cassettes=2*l['faces']*zone/l['cassette_m']
    if not cassettes.is_integer() or not math.isclose(group/l['cassette_m'],round(group/l['cassette_m'])):raise ValueError('whole cassette groups required')
    # One single-layer full-pitch coil joins slots k and k+3 in each six-slot belt.
    schedule=[dict(coil=f'C{block*3+i+1:02d}',phase=('A','C','B')[i],start_slot=block*6+i+1,
        return_slot=block*6+i+4,forward_sign=(1,-1,1)[i],turns=turns,bar_area_mm2=bar_area) for block in range(slots//6) for i in range(3)]
    per_phase_group=group/l['cassette_m']*l['faces']*coils/3
    return dict(zone_m_per_direction=zone,groups_per_direction=l['groups_per_direction'],group_length_m=group,
        bridges_per_station=2*l['groups_per_direction'],electrical_sections_per_station=round(2*zone/l['electrical_section_m']),
        face_cassettes_per_station=int(cassettes),slots_per_face_cassette=slots,coils_per_face_cassette=coils,
        coils_per_station=int(cassettes)*coils,phase_belts=['A+','C-','B+','A-','C+','B-'],schedule=schedule,
        copper_per_coil=wire,copper_kg_per_station=wire['copper_kg']*int(cassettes)*coils,
        resistance_hot_per_phase_group_ohm=wire['resistance_hot_ohm']*per_phase_group,
        phase_group_series_coils=per_phase_group,turns=turns,bar_area_mm2=bar_area,
        winding_origin_index_m=2*l['pole_pitch_m'],parallel_unequal_emf_branches_accepted=False,
        measured_inductance_h=None,measured_flux_linkage_wb=None,**model.FLAGS)

def phase_budget(a=None,speed=80/3.6):
    a=load() if a is None else a;l=a['launch'];wave=2*l['pole_pitch_m']*1e6
    sources_um=dict(position=l['position_uncertainty_um'],timestamp=speed*l['time_uncertainty_ns']/1000.,
        registration=l['registration_uncertainty_um'],thermal=l['thermal_index_uncertainty_um'])
    values={k:v/wave*360000 for k,v in sources_um.items()};values['mechanical']=l['mechanical_phase_allowance_mdeg']
    total=sum(values.values())
    return dict(speed_m_s=speed,contributions_mdeg=values,total_mdeg=total,limit_mdeg=l['maximum_total_phase_mdeg'],
        screen_pass=total<=l['maximum_total_phase_mdeg'],method='Worst-case sum; not root-sum-square. Mechanical allowance is unqualified and is not added to a second body-derived phase allowance.',accepted=False)

def sampled(profile):
    raw=corridor._motion_samples(corridor.encoded(profile).decode())
    # Exact phase boundaries can differ from uniform sample times by roundoff.
    # Do not divide by their femtosecond separation when differentiating.
    keep=np.concatenate(([True],np.diff(raw['times'])>1e-7))
    return {k:val[keep] for k,val in raw.items() if isinstance(val,np.ndarray)}

def dc_system(a,profile):
    l=a['launch'];s=sampled(profile);power=s['force']*s['speed']
    arrival=np.where(s['zone']=='arrival',np.maximum(0.,-power),0.)
    departure=np.where(s['zone']=='departure',np.maximum(0.,power),0.)
    cap=4*l['local_bus_capacitance_f'];v=l['dc_bus_v'];upper=l['bus_upper_screen_v']
    # Loss-free mechanical arrival is a conservative resistor sizing envelope,
    # not a claimed recovery efficiency. Full redundant paths each retain it.
    peak=float(arrival.max());event=float(np.trapezoid(arrival,s['times']))
    increment=.5*cap*(upper*upper-v*v)
    return dict(common_bus_capacitance_f=cap,nominal_capacitor_energy_j=.5*cap*v*v,
        voltage_headroom_energy_j=increment,mechanical_arrival_peak_w=peak,
        mechanical_arrival_energy_j=event,minimum_each_independent_resistor_pulse_j=event,
        minimum_each_independent_resistor_peak_w=peak,clamp_resistance_upper_ohm=upper*upper/peak,
        two_simultaneous_arrivals_peak_w=2*peak,two_arrivals_heat_j=2*event,
        two_arrivals_average_w_at_180s_headway=2*event/180.,
        capacitor_headroom_at_two_arrivals_s=increment/(2*peak),
        capacitor_covers_assumed_clearance=increment>=2*peak*l['brake_pulse_clearance_s'],
        assumed_clearance_s=l['brake_pulse_clearance_s'],
        loss_free_departure_peak_w=float(departure.max()),
        services_charger_input_w_per_train=profile['inputs']['cars']*1000.*({'urban':400.,'suburban':600.}[profile['mode']]),
        services_charging_scope='Reference input rating: urban 400 kW/car; suburban 600 kW/car. Actual connection time, energy and grid diversity require their own checks.',
        minimum_bus_rating_above_nominal=l['switch_voltage_class_v']>v,
        lone_1700v_two_level_switch_eligible=1700.>upper,
        supply_losses_copper_reactive_power_not_included=True,qualified=False)

def electrical_screen(a,profile,*,turns=1,inductance=.00015):
    l=a['launch'];w=winding(a,turns=turns);s=sampled(profile)
    times=s['times'];pos=s['position'];force=s['force'];speed=s['speed'];cars=profile['inputs']['cars'];v=station.load()['vehicle']
    bands=np.array([[-(v['body_length_m']-v['magnetic_band_m_per_car'])/2-v['magnetic_band_m_per_car']-j*(v['body_length_m']+v['coupling_gap_m']),
                     -(v['body_length_m']-v['magnetic_band_m_per_car'])/2-j*(v['body_length_m']+v['coupling_gap_m'])] for j in range(cars)])
    group_count=4;psi=np.zeros((group_count,len(pos)))
    flux_pole=l['useful_fundamental_flux_t']*2*l['pole_pitch_m']/math.pi*l['face_width_m']
    zones=corridor._zones(profile,corridor.load());start_zone=zones[0];end_zone=zones[-1]
    groups=[]
    for zone in (start_zone,end_zone):
        # Each terminal's two fixed groups are independent. A suburban midway
        # booster is a separate asset and is explicitly excluded from this bill.
        for j in range(2):
            start=zone['start_m']+j*(zone['end_m']-zone['start_m'])/2
            end=start+(zone['end_m']-zone['start_m'])/2
            index=len(groups);mask=s['zone']==zone['id']
            ov=station._overlap(pos,bands,start,end)
            psi[index]=np.where(mask,ov* l['faces']/l['cassette_m']*5*turns*flux_pole,0.)
            groups.append(dict(zone=zone['id'],start_m=start,end_m=end))
    total=psi.sum(axis=0);k=math.pi/l['pole_pitch_m'];active=(total>1e-9)&(np.abs(force)>1e-6)
    iq=np.divide(force,1.5*k*total,out=np.zeros(len(pos)),where=active)
    omega=k*speed;limit=l['dc_bus_v']/math.sqrt(3)*.95
    records=[];total_loss=np.zeros(len(pos));max_error=0.
    for i,g in enumerate(groups):
        # Both terminal groups carry the commanded phase current during that
        # terminal's powered interval, including an empty group's copper loss.
        # Do not credit cost-free pre-excitation or instantaneous current removal
        # at each overlap edge. Whole-event switching transients remain open.
        engaged=active&(s['zone']==g['zone']);current=np.where(engaged,iq,0.);di=np.gradient(current,times)
        r=w['resistance_hot_per_phase_group_ohm'];L=inductance*turns*turns
        psi_dot=np.gradient(psi[i],times)
        vd=np.where(engaged,-omega*L*current+psi_dot,0.)
        vq=np.where(engaged,r*current+L*di+omega*psi[i],0.)
        voltage=np.hypot(vd,vq);loss=1.5*r*current*current;total_loss+=loss
        mech=1.5*k*psi[i]*current*speed;airgap=1.5*omega*psi[i]*current
        max_error=max(max_error,float(np.max(np.abs(mech-airgap))))
        records.append(dict(**g,peak_current_a=float(np.max(np.abs(current))),peak_phase_voltage_v=float(voltage.max()),
            peak_copper_w=float(loss.max()),copper_heat_j=float(np.trapezoid(loss,times)),
            current_screen=bool(np.max(np.abs(current))<=l['maximum_phase_peak_a']),voltage_screen=bool(voltage.max()<=limit)))
    uncovered=(np.abs(force)>1e-6)&~active
    # The suburban booster is deliberately outside a terminal station BOM; its
    # nonzero demand must be visible rather than counted as a zero-current pass.
    return dict(turns=turns,one_turn_group_inductance_hypothesis_h=inductance,groups=records,
        winding_zone_m_per_direction=w['zone_m_per_direction'],whole_profile_peak_speed_m_s=float(speed.max()),
        voltage_limit_v=limit,total_peak_copper_w=float(total_loss.max()),total_copper_heat_j=float(np.trapezoid(total_loss,times)),
        force_power_identity_residual_w=max_error,omitted_powered_samples=int(uncovered.sum()),
        omitted_asset='suburban midpoint booster' if uncovered.any() else None,
        current_voltage_screen=all(g['current_screen'] and g['voltage_screen'] for g in records),
        scope='Both terminal groups excited during each powered event, including empty-group copper. Constant assumed Ld=Lq; sinusoidal fundamental; Id=0. Event enable/discharge transients, end effects, saturation, position-varying inductance, mutual/shared fields, switching and iron losses omitted. Terminal groups only.',
        qualified=False)

def bom(a=None):
    a=load() if a is None else a;s=a['support'];cars=station.load()['vehicle']['cars'];n=s['modules_per_car'];w=winding(a);rows=[]
    def row(id,description,unit,car=0,train=None,st=0,source=None,parent=None):
        rows.append(dict(id=id,description=description,unit=unit,per_car=car,per_six_car_train=cars*car if train is None else train,
            per_two_direction_station=st,supplier_reference=source,accounting_parent=parent,unit_price_usd=None,
            ordered_part=None,manufacturing_origin_confirmed=False,accepted=False))
    row('SUP-COIL',f'{s["turns_per_coil"]}-turn rectangular copper coil: one lift and two opposed guide coils/module','coil',3*n,source='rotary')
    row('SUP-COPPER','Bare copper conductor; material inside SUP-COIL, not extra mass','m',3*n*s['turns_per_coil']*s['mean_turn_length_m'],parent='SUP-COIL')
    row('SUP-FORMER','Insulating former, interlayer insulation and impregnation kit','kit',3*n,parent='SUP-COIL')
    row('SUP-YOKE','Lift/guide pole and return-path assembly; new magnetic fit unresolved','assembly',n)
    row('SUP-BRIDGE','96 V bipolar full H-bridge current circuit','bridge',2*n)
    row('SUP-SWITCH','200 V-class MOSFET position; exact die/parallel count requires SOA and layout','position',8*n,parent='SUP-BRIDGE')
    row('SUP-GATE','Dual isolated gate-driver IC; gate peak amps are not winding amps','IC',4*n,source='gate-driver',parent='SUP-BRIDGE')
    row('SUP-GATE-SUPPLY','Isolated driver power domain; two per H-bridge','domain',4*n,parent='SUP-BRIDGE')
    row('SUP-HALL','Isolated primary current measurement','channel',2*n)
    row('SUP-SHUNT','Independent shunt/isolated conversion measurement','channel',2*n)
    row('SUP-GAP','Two lift and two lateral gap chains/module; exact full-range probe unselected','chain',4*n,source='gap-sensor')
    row('SUP-MCU','Local acquisition/current/gap controller board, not complete released PCB','board',n,source='stm32')
    row('SUP-TRIP','Independent comparator/watchdog/latched driver-disable network','network',n)
    row('SUP-TEMP','One embedded temperature sensor per physical coil','sensor',3*n)
    row('SUP-PROTECTION','Local fused branch, DC capacitor, clamp and discharge kit','kit',n)
    row('SUP-ZONE','Six-module isolated-power/protection/cooling distribution zone','zone',n//s['zone_modules'])
    row('SUP-SBC','SBC supervisor per car, excluding one train standby','SBC',1,source='raspberry-pi-5')
    row('SUP-STANDBY','Train supervisory standby, not a proven automatic transfer','SBC',train=1,source='raspberry-pi-5')
    row('SUP-NETWORK','Segregated local control link and supervisory network harness','set',1)
    row('SUP-COOLING','Coldplate, insulated mounts, coolant/air fittings and service connections','set',n)
    row('SUP-INDEPENDENT-POWER','Independent support/capture power path; capacity not sized by copper alone','system',train=1)
    row('LSM-CASSETTE','2.5 m face cassette with 30 slots and 15 full-pitch coils','cassette',st=w['face_cassettes_per_station'])
    row('LSM-COIL','One-turn 350 mm2 copper bar coil; N alternatives retained','coil',st=w['coils_per_station'],parent='LSM-CASSETTE')
    row('LSM-COPPER','Bare bar length inside LSM-COIL; no second copper-mass credit','m',st=w['coils_per_station']*w['copper_per_coil']['length_m'],parent='LSM-COIL')
    row('LSM-INSULATION','Slot liner, phase separator, former, potting and stress-relief kit','kit',st=w['face_cassettes_per_station'],parent='LSM-CASSETTE')
    row('LSM-CONNECTION','Phase terminals and indexed series links; creepage/clearance unqualified','set',st=w['face_cassettes_per_station'])
    row('LSM-BRIDGE','Custom 3-phase 2400 V DC group converter; not a catalogue drive rating','bridge',st=4,source='nidec')
    row('LSM-IGBT','3.3 kV-class single-switch modules, 4 parallel/position, 6 positions/group; unselected','module',st=4*6*4,source='igbt',parent='LSM-BRIDGE')
    row('LSM-DRIVER','Module-specific isolated gate/protection assembly','assembly',st=4*6*4,parent='LSM-BRIDGE')
    row('LSM-CURRENT','Two independent chains for each of three group phase currents','chain',st=4*3*2)
    row('LSM-LOCAL-MCU','Per-group local sensored dq/current controller','board',st=4,source='stm32')
    row('LSM-POSITION','Independent position/phase reference chains per direction; outdoor hardware unselected','chain',st=4)
    row('LSM-DC-VOLTAGE','Dual independent DC sensing chains per group','chain',st=8)
    row('LSM-DC-CAP','Per-group assumed 20 mF film-capacitor bank; ripple/fault design open','bank',st=4,source='api')
    row('LSM-DC-PROTECTION','Precharge, isolators, fuses, discharge, IMD and protection coordination','system',st=1)
    row('LSM-RESISTOR','Independent braking chopper/resistor path per direction; common-bus losses not sole sink','path',st=2,source='cressall')
    row('LSM-SUPPLY','Transformer, supply converter and supply protection; rated grid study required','system',st=1)
    row('LSM-CHARGE','Separately rated train services charger/interface per direction','interface',st=2)
    row('LSM-SBC','Station supervision and standby; field authority remains a separate function','SBC',st=2,source='raspberry-pi-5')
    row('LSM-THERMAL','Group liquid cooling, earth bonding, cabinet and field harness','system',st=4)
    return rows

def connections():
    return [dict(net=net,from_terminal=src,to_terminal=dst,requirement=req) for net,src,dst,req in (
        ('SUP-96V','segregated support-power zone','local fused H-bridge DC input','Independent protection energy; no direct SBC GPIO power control'),
        ('SUP-COIL-LIFT','H-bridge L+ / L-','configured lift winding','Bipolar regulation; inductive clamp and temperature observation'),
        ('SUP-COIL-GUIDE','H-bridge G+ / G-','two guidance windings in series opposition','Polarity checked with low-energy field and force measurements'),
        ('SUP-ADC','dual current and four gap chains','local MCU synchronous acquisition','Individual timestamp/sequence/calibration; independent chain qualification'),
        ('SUP-TRIP','independent comparators/watchdog','latched local driver disable / fallback request','Protection does not establish safe levitation; capture/power path needs qualification'),
        ('SUP-SBC','car supervisor','local 1 kHz setpoint/health interface','20 kHz current timing stays local; stale supervisory demand invokes qualified local fallback'),
        ('LSM-DC','supply/DC protection','four isolated group converters and film banks','2400 V hypothesis; fault clearing, discharge and insulation design required'),
        ('LSM-ABC','group A/B/C outputs','indexed series cassette phases A/B/C','No arbitrary parallel unequal-back-EMF circuits; continuity/polarity test every cassette'),
        ('LSM-PHASE','independent absolute position plus magnetic registration','local group FOC MCU','Zero-speed phase and total uncertainty budget; back-EMF-only startup rejected'),
        ('LSM-BRAKE','common DC bus','independent chopper/resistor paths','Peak power, event energy and repeated duty including simultaneous arrivals'),
        ('LSM-AUTHORITY','interlocking and receiver protection','launch/receive admission','Current command or timetable is not route authority'),
        ('SUP-SEPARATION','wayside propulsion fault','onboard support stop/recovery interface','Never interpret zero station thrust as permission to remove onboard support'))]

def tools(args):
    result=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=180)
    if result.returncode:raise ValueError('drive tool failed: '+result.stderr[-3000:])
    return dict(command=args,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)

def api_signature(stdout):
    """Exact executed test identities/states, ignoring only order and elapsed time."""
    lines=[line for line in stdout.splitlines() if line]
    cases=sorted(line for line in lines if re.fullmatch(r'test [A-Za-z0-9_:]+ \.\.\. ok',line))
    summary=r'test result: ok\. 9 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in [0-9.]+s'
    if len(lines)!=11 or lines[0]!='running 9 tests' or len(cases)!=9 or len(set(cases))!=9 or not re.fullmatch(summary,lines[-1]):
        raise ValueError('complete exact drive test identities and successful states required')
    return cases

def study():
    before=sources();a=load();api=tools(API);execution=tools(RUN)
    api_signature(api['stdout'])
    replay=list(csv.DictReader(io.StringIO(execution['stdout'])))
    if len(replay)!=17 or any(r['control_pass']!='true' or r['physical_output_authorised']!='false' for r in replay):raise ValueError('complete actual current/commutation replay required')
    _,cfg,_=model.load();mass=model.mass(cfg,cfg['mass']['ferrite_base'],50.)['aw3_kg'];profiles={};dc={}
    for mode,distance,runtime in [('urban',2000.,140.),('suburban',5000.,375.)]:
        p=corridor.profile(distance_m=distance,runtime_s=runtime,cars=6,car_mass_kg=mass,mode=mode)
        if not p['study_pass']:raise ValueError('current exact profile required')
        profiles[mode]=[electrical_screen(a,p,turns=n,inductance=L) for n in a['launch']['turn_alternatives'] for L in a['launch']['group_inductance_alternatives_h']]
        dc[mode]=dc_system(a,p)
    if sources()!=before:raise ValueError('drive source changed during study')
    return dict(schema=SCHEMA,source_sha256=before,support=support(a),support_alternatives=support_alternatives(a),launch=winding(a),benchmark_200m=winding(a,zone=200.),
        copper_alternatives=[winding(a,bar_area=area) for area in a['launch']['bar_area_alternatives_mm2']],
        phase_budget=phase_budget(a),profiles=profiles,dc_system=dc,bom=bom(a),connections=connections(),
        suppliers=json.loads(SUPPLIERS.read_bytes()),software_replays=replay,
        independent_stopping_mandatory=True,hardware_io_enabled=False,default_design_changed=False,
        open_gates=HOLDS,study_pass=True,**model.FLAGS),dict(api=api,replay=execution)

def csv_bytes(rows):
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows);return out.getvalue().encode()

def architecture_svg():
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="660" viewBox="0 0 1200 660"><rect width="1200" height="660" fill="#f3f8fc"/><g font-family="sans-serif" fill="#15384c"><text x="25" y="40" font-size="26">Separate support/guidance and station launch control</text><g fill="#d7eaf3" stroke="#376178"><rect x="30" y="90" width="330" height="115" rx="10"/><rect x="430" y="90" width="330" height="115" rx="10"/><rect x="830" y="90" width="330" height="115" rx="10"/><rect x="30" y="300" width="330" height="135" rx="10"/><rect x="430" y="300" width="330" height="135" rx="10"/><rect x="830" y="300" width="330" height="135" rx="10"/></g><g font-size="18"><text x="45" y="120">Car SBC: force allocation / logging</text><text x="45" y="151">Rust supervisor; 1 kHz study frame</text><text x="45" y="181">No direct power-gate operation</text><text x="445" y="120">24 local MCU boards / car</text><text x="445" y="151">48 current circuits at 20 kHz</text><text x="445" y="181">Dual current + gap acquisition</text><text x="845" y="120">PM-biased support / guidance</text><text x="845" y="151">72 physical trim coils / car</text><text x="845" y="181">288 H-bridges / six-car train</text><text x="45" y="332">Wayside authority + phase</text><text x="45" y="363">Protected receiver and DC sink</text><text x="45" y="394">Independent onboard recovery</text><text x="445" y="332">Four local converter controllers</text><text x="445" y="363">Clarke / Park + bounded PI</text><text x="445" y="394">2400 V hypothesis: no hardware</text><text x="845" y="332">350 m motor / direction</text><text x="845" y="363">560 face cassettes / station</text><text x="845" y="394">Three-phase fixed winding groups</text></g><g stroke="#376178" stroke-width="4"><path d="M360 148H430M760 148H830M360 360H430M760 360H830"/></g><g font-size="18"><text x="30" y="490">Local independent protection: overcurrent / temperature / bus / watchdog / capture and support energy</text><text x="30" y="530">A wayside launch or receive fault must not remove onboard support.</text><text x="30" y="575">Executed software uses synthetic frames and average-voltage RL plants. No PWM/ADC adapter or real-time qualification.</text><text x="30" y="620">All engineering, manufacturing and physical release gates remain open.</text></g></g></svg>\n'''.encode()

def construction_svg(v):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="680" viewBox="0 0 1200 680"><rect width="1200" height="680" fill="#f3f8fc"/><g font-family="sans-serif" fill="#15384c"><text x="25" y="40" font-size="26">Candidate winding construction — dimensions and interfaces, not release drawings</text><path d="M70 100H418V368H70Z M124 154V314H364V154Z" fill="#b96e41" fill-rule="evenodd" stroke="#522e1a"/><g font-size="19"><text x="50" y="405">Support coil: 174 x 134 x {v['support']['new_pack_depth_m']*1000:g} mm envelope</text><text x="50" y="437">120 x 80 mm clear inner rectangle</text><text x="50" y="469">{v['support']['coil']['turns']} turns, {v['support']['coil']['area_mm2']:g} mm² copper, {v['support']['coil']['length_m']:.2f} m / coil</text><text x="50" y="501">One lift + two opposed guide coils / module</text><text x="50" y="533">{v['support']['coil']['copper_kg']:.3f} kg copper / coil; former / insulation extra</text><text x="50" y="565">Compact pack passes depth; winding layout still open.</text><text x="640" y="120">Launch face cassette: 2500 mm / 10 poles</text><text x="640" y="155">30 slots; 15 single-layer full-pitch coils</text><text x="640" y="190">Coil span 250 mm; A+, C-, B+, A-, C+, B-</text><text x="640" y="225">One-turn 350 mm² bar candidate</text><text x="640" y="260">Five cassettes / face / 12.5 m section</text><text x="640" y="295">Two 175 m fixed groups / direction</text><text x="640" y="330">{v['launch']['copper_kg_per_station']/1000:.3f} t copper / two-direction station</text><text x="640" y="380">Make: bend bars / formers / laminate stack</text><text x="640" y="414">Join: qualified phase links and insulated terminals</text><text x="640" y="448">Test: polarity, R/L, insulation, force and heating</text><text x="640" y="482">Measure shared support/thrust disturbance</text><text x="640" y="516">No current, voltage or thermal rating is approved.</text><text x="25" y="615">These drawings define research units and counted material.</text><text x="25" y="650">Saturation, winding fit, connections and complete equipment remain open.</text></g></g></svg>\n'''.encode()

def readme(v):
    s=v['support'];w=v['launch']
    rows='\n'.join(f'| {r["id"]} | {r["description"]} | {r["per_car"]} | {r["per_six_car_train"]} | {r["per_two_direction_station"]} |' for r in v['bom'])
    suppliers='\n'.join(f'- [{r["name"]}]({r["url"]}): {r["role"]}. Origin: {r["origin"]}.' for r in v['suppliers']['suppliers'])
    electrical='\n'.join(f'| {mode} | {r["turns"]} | {r["one_turn_group_inductance_hypothesis_h"]*1e6:g} | {max(g["peak_current_a"] for g in r["groups"]):.0f} | {max(g["peak_phase_voltage_v"] for g in r["groups"]):.0f} | {r["total_copper_heat_j"]/3.6e6:.2f} | {r["current_voltage_screen"]} |' for mode,rows in v['profiles'].items() for r in rows)
    dc=v['dc_system']['urban']
    alternative_rows='\n'.join(f'| {r["id"]} | {r["inputs"]["turns_per_coil"]} | {r["inputs"]["conductor_area_mm2"]:g} | {r["inputs"]["coil_height_m"]*1000:g} | {r["result"]["copper_kg_per_train"]:.1f} | {r["result"]["loads"][-1]["lift_copper_w_per_car"]:.0f} | {r["provisional_screens_pass"]} |' for r in v['support_alternatives'])
    return f'''# Active support/guidance and station launch construction

This package develops the electrical path missing from the ideal-force train model. It is a provisional construction and purchasing design, with actual Rust current/commutation tests. It does not qualify a complete magnetic actuator or an installed controller.

## What actively holds and guides the train

Ferrite magnets supply bias flux. Attraction changes with gap and is not passively stable. Two measured lift gaps and two lateral measurements per cartridge feed local gap/position feedback. Car-level Rust allocation requests forces and moments; a calibrated gap/current/temperature/shared-flux map must turn these into winding-current requests. A local MCU samples current and controls each H-bridge. Semiconductor switches regulate coil current; they are electrical switches, not rotating traction motors.

There are 24 cartridge positions per car. This candidate adds one lift winding and two opposed guidance windings at each position. The two guidance windings form one series-opposed circuit: **72 physical coils and 48 independently controlled current circuits per car; 432 coils and 288 circuits per six-car train**. A physical magnetic design must establish that the proposed independent lift and lateral functions are achievable together.

The SBC handles supervision, car-level allocation and recording. Local MCU boards own the proposed 20 kHz current loop and 1 kHz local gap loop. Independent comparators, driver interlocks, watchdogs and segregated support power remain separate. Ordinary Linux scheduling is not a current-loop deadline guarantee. A lost supervisory computer must invoke an engineered local support/controlled-stop arrangement; zeroing an LSM command or stale PWM is not a levitation fallback.

## Support coil and power assembly

The compact coil candidate has {s['coil']['turns']} turns of {s['coil']['area_mm2']:g} mm² rectangular copper, a 508 mm mean turn length, 120 x 80 mm inner clearance and 174 x 134 x {s['new_pack_depth_m']*1000:g} mm envelope. Each coil contains **{s['coil']['copper_kg']:.3f} kg copper**. Copper alone totals **{s['copper_kg_per_car']:.1f} kg/car** and **{s['copper_kg_per_train']:.1f} kg/train**. These are child quantities within support equipment, not additional mass silently added to the existing vehicle allowance. Formers, insulation, yokes, drivers, harnesses and cooling remain additional quantities to close.

At the assumed 8 mm gap, 0.55 T bias and ideal two-gap circuit, the AW3 lift-current screen gives {s['loads'][-1]['current_a']:.2f} A per lift circuit. These values derive from an ideal reluctance equation, not a measured PM module. The 96 V bus, 60 A continuous / 120 A pulse envelope and coil thermal screen are design candidates. The calculated current slew is checked against the allocator's old ideal 2 MN/s force slew; a current limit or a passed arithmetic screen does not establish closed-loop vehicle stability.

The **compact 60 mm pack passes the declared depth and packing screens**. The retained 85 mm/60-turn version fails cavity depth; the 35-turn version exceeds continuous current and the 20 kN pulse-current limit. Compact winding reduces copper but increases heat; it is a provisional construction choice without changing the operating vehicle's mass ledger. A 4 x 4 mm bare conductor is a starting forming reference for 16 mm²: enamel, bend radii, layer arrangement, leads, former and creepage still need actual drawings and winding trials. Material volume alone does not establish complete fit. Machine and inspect the former, wind with controlled tension and counted turns, join qualified leads, impregnate, fit temperature sensing and strain relief, then measure resistance, inductance, insulation, polarity, force and heating. Fixed capture, essential-load power and residual PM force after drive loss need separate qualification.

| Support variant | Turns | Copper mm² | Depth mm | Copper kg/train | AW3 lift copper W/car | Declared screens |
|---|---:|---:|---:|---:|---:|---|
{alternative_rows}

## Launch / receive hardware

The current urban/suburban studies use **350 m powered station zones per direction**. The supplied 200 m proposal remains a separate 1 km benchmark; it is not substituted for the current corridor. At 250 mm pole pitch and 2.5 m cassette length, a face cassette contains 30 slots and 15 single-layer full-pitch coils, five per phase. The supplied winding schedule pairs every slot exactly once. Magnetic origins must be indexed to the 500 mm electrical wavelength.

Two fixed 175 m groups per direction require four independently controlled three-phase bridges per two-direction station. The primary counted bill is **{w['face_cassettes_per_station']} face cassettes, {w['electrical_sections_per_station']} jointed 12.5 m sections and {w['coils_per_station']} bar coils**. A section has five cassettes per face; it is not a separately switched converter. One-turn 350 mm² copper gives **{w['copper_kg_per_station']/1000:.3f} t copper/station** before joints, terminals and production waste. The 200 m benchmark retains 320 face cassettes and 32 sections. More turns reduce required current but increase back-EMF and inductive voltage; the retained 1/2/4-turn and R/L/material alternatives show the actual trade-offs.

One long series group must carry its real phase current. Parallel branches with unequal magnetic overlap have unequal back-EMF and cannot be assumed to share current from one bridge. The study calculates each group's overlap, periodic flux linkage, phase current, dq voltage, copper heat and power identity on the exact 2 km/140 s and 5 km/375 s AW3 trajectories. Inductance is an explicit sensitivity, not a solved winding map. The suburban booster is outside this terminal-station bill and its nonzero powered demand is reported as omitted scope.

The corridor's **2400 V DC hypothesis exceeds a single 1700 V switch rating**. The purchasing envelope therefore counts a custom higher-voltage converter, with semiconductor class, parallel positions and isolated gate/protection assemblies explicit. The cited catalogue drives are integration references, not selected 2400 V products. Before ordering, establish transient blocking, current sharing, SOA, diode/recovery, switch losses, cooling, creepage/clearance and fault isolation.

The common DC system needs rectification/supply conversion, protected film-capacitor banks, precharge, fuses/isolators, discharge, insulation monitoring and independently available braking sinks. Receiving requires the resistor/chopper ready even when no other train can absorb energy. Capacitor energy and MW braking duty are not interchangeable; a small DC link cannot absorb a complete arrival. Services charging is a separately rated load. No train battery or grid saving is credited merely through common-bus energy exchange.

For the urban trajectory, the loss-free arrival envelope is {dc['mechanical_arrival_peak_w']/1e6:.3f} MW and {dc['mechanical_arrival_energy_j']/1e6:.3f} MJ per train. Each independent resistor path must retain that event rating; two simultaneous arrivals require {dc['two_simultaneous_arrivals_peak_w']/1e6:.3f} MW common-bus handling. Four proposed 20 mF banks provide only {dc['voltage_headroom_energy_j']/1000:.1f} kJ between 2400 and 2550 V, equivalent to {dc['capacitor_headroom_at_two_arrivals_s']*1000:.2f} ms at the two-arrival peak. That does not establish protection clearing or an energy sink. The study retains suburban duties too; grid sizing must include winding losses, conversion, charging and diversity without assuming a receptive departing train.

### Winding alternatives on the exact current trajectories

Here L is the one-turn whole-group assumption, scaled by turns squared. Voltage is phase peak against the {v['profiles']['urban'][0]['voltage_limit_v']:.0f} V modulation screen. These are fixed-group electrical screens, not motor acceptance; failed alternatives remain visible. Terminal observations are two departure groups and two arrival groups, not simultaneous operation of four directions. Midway booster equipment requires its own quantities.

| Duty | Turns | One-turn L (µH) | Peak phase A | Peak phase V | Terminal copper kWh | Current/voltage screen |
|---|---:|---:|---:|---:|---:|---|
{electrical}

## Software and evidence

`crates/osr-maglev-control/src/drives.rs` supplies allocation-free bipolar PI, Clarke/Park transforms, bounded dq current regulation, phase uncertainty admission, average-voltage duty calculation, anti-windup and latched sensor/current/time/temperature/bus/authority/receiver faults. It compares dual current chains and checks three-phase current residuals. Reset needs fresh healthy, stopped/secured, zero-demand inputs. A wayside fault never requests onboard support shutdown. These Boolean facts still need authenticated physical sources.

Actual execution: three 4000-frame current-tracking runs and fourteen adverse controls, plus nine Rust regression tests. The independent RL/alpha-beta plant uses a standard-library trigonometric oracle. The 40 A commutation coupon is **not the multi-kA station converter**. Neither that RL plant nor the assumed reluctance screen has been substituted into the moving rigid-car/beam model. Rust hardware adapters, ADC timing, PWM/deadtime, protection trip timing, HIL and magnetic/load rigs remain required.

```sh
./osr design drives
cargo test --locked -p osr-maglev-control --test drives
cargo run --locked -p osr-maglev-control --example winding_replay
```

## Construction BOM

Quantities are purchasing families, not released PCB components. Parents and material children overlap; do not sum them as separate mass. Quoted prices and confirmed origins remain null/unconfirmed. Local assembly, winding, copper forming, cabinets, wiring, Rust and test processes are candidates; semiconductor and sensor origins retain their real imported content.

| ID | Construction / purchasing item | Per car | Per six-car train | Per two-direction station |
|---|---|---:|---:|---:|
{rows}

## British manufacture and specialist references

Primary sources checked {v['suppliers']['checked_date']}. UK capability does not establish the origin of a particular order. No supplier has quoted or endorsed this railway design.

{suppliers}

## Verification and release gates

The [full study](study.json.gz), [executed output](execution.json.gz), [BOM](bom.csv), [winding schedule](winding-schedule.csv), [connections](connections.csv) and [source receipt](manifest.json) retain exact inputs and results. The [architecture](architecture.svg) and [construction drawing](construction.svg) are generated from this package. Verification repeats the Rust execution and independently recomputes the quantities and screens; rehashed altered results are rejected.

'''+ '\n'.join('- '+g for g in HOLDS)+'\n\nAll engineering/physical release flags remain false. No city cost, mass, headway or hardware acceptance is promoted.\n'

def payload(v,e):return {'study.json.gz':gzip.compress(encoded(v),mtime=0),'execution.json.gz':gzip.compress(encoded(e),mtime=0),
    'bom.csv':csv_bytes(v['bom']),'winding-schedule.csv':csv_bytes(v['launch']['schedule']),'connections.csv':csv_bytes(v['connections']),
    'architecture.svg':architecture_svg(),'construction.svg':construction_svg(v),'README.md':readme(v).encode()}

def publish(output=OUTPUT):
    output=Path(output).absolute()
    if output.resolve()!=output:raise ValueError('ordinary drive output required')
    v,e=study();data=payload(v,e);output.mkdir(parents=True,exist_ok=True)
    if output.is_symlink() or any(p.is_symlink() for p in output.iterdir()) or set(p.name for p in output.iterdir())-FILES-{'manifest.json'}:raise ValueError('owned drive inventory required')
    for n,b in data.items():(output/n).write_bytes(b)
    m=dict(schema=SCHEMA,source_sha256=v['source_sha256'],files_sha256={n:digest(b) for n,b in data.items()},**model.FLAGS)
    (output/'manifest.json').write_bytes(encoded(m));return verify(output)

def read_json(p,compressed=False):
    if p.is_symlink() or not p.is_file() or p.stat().st_size>MAX_FILE:raise ValueError('bounded ordinary drive file required')
    raw=p.read_bytes()
    if compressed:
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:raw=stream.read(MAX_RAW+1)
        if len(raw)>MAX_RAW:raise ValueError('drive inflate limit exceeded')
    return json.loads(raw)

def verify(output=OUTPUT):
    output=Path(output).absolute()
    if output.resolve()!=output or not output.is_dir() or set(p.name for p in output.iterdir())!=FILES|{'manifest.json'}:raise ValueError('exact drive inventory required')
    m=read_json(output/'manifest.json')
    if m.get('schema')!=SCHEMA or m.get('source_sha256')!=sources() or any(m.get(k) is not False for k in model.FLAGS) or set(m.get('files_sha256',{}))!=FILES:raise ValueError('drive sources or scope differ')
    for name,h in m['files_sha256'].items():
        p=output/name
        if p.is_symlink() or not p.is_file() or p.stat().st_size>MAX_FILE or digest(p.read_bytes())!=h:raise ValueError('drive payload differs')
    retained=read_json(output/'study.json.gz',True);execution=read_json(output/'execution.json.gz',True)
    fresh,actual=study()
    # Tool stderr contains host build timing; compare the actual result streams
    # and API group, not nondeterministic compiler wall-clock text.
    if retained!=fresh or execution['api']['command']!=API or execution['api']['returncode']!=0 or api_signature(execution['api']['stdout'])!=api_signature(actual['api']['stdout']) or execution['replay']['command']!=RUN or execution['replay']['returncode']!=0 or execution['replay']['stdout']!=actual['replay']['stdout']:
        raise ValueError('drive execution or recomputed design differs')
    expected=payload(fresh,execution)
    if any((output/n).read_bytes()!=b for n,b in expected.items()):raise ValueError('drive presentation differs')
    return m

def read_summary():
    verify();v=read_json(OUTPUT/'study.json.gz',True)
    return dict(schema=SCHEMA,software_cases=len(v['software_replays']),support_circuits_per_train=288,
        support_coils_per_train=432,station_face_cassettes=v['launch']['face_cassettes_per_station'],
        station_copper_kg=v['launch']['copper_kg_per_station'],phase_budget=v['phase_budget'],
        hardware_io_enabled=False,default_design_changed=False,**model.FLAGS)
