"""Sized station-launch alternatives and necessary physical/electrical bounds.

All designs are research revisions. Industrial catalogue facts do not establish
train-level force, contact, control, fatigue, thermal duty or safe passenger use.
No required-force curve is ever presented as an available propulsion map.
"""
from copy import deepcopy
from pathlib import Path
from math import pi,sqrt,fsum,ceil,isfinite
import json
from engineering.component_registry import validate_registry
from engineering.design_search import railway_bundle
from . import ROOT,FLAGS,identity,digest

CODE='engineering/railway_progress/alternatives.py'
DATA='engineering/railway_progress/data/alternatives-sources.json'
KINDS=('five-20m-LIM','six-20m-LIM','ten-20m-LIM','long-distributed-LIM','continuous-LIM',
       'station-pinch-rollers','cable-launch-tug','onboard-rescue-research')
PHYSICAL_KEYS={'bank_starts_m','bank_length_m','roller_pairs_per_bank','roller_diameter_m','roller_width_m','roller_wall_m',
 'motor_count','drive_strip_length_m','drive_strip_height_m','drive_strip_thickness_m','rope_diameter_m','drum_diameter_m',
 'rope_launch_length_m','tug_mass_kg','rescue_motor_count','rescue_storage_kWh','clamp_bore_m','clamp_design_pressure_Pa','grip_design_capacity_N'}


def sources(root=ROOT):return {n:digest(Path(root)/n) for n in (CODE,DATA)}


def catalogue(root=ROOT):
    data=json.loads((Path(root)/DATA).read_bytes())
    if data['schema']!='osr-station-launch-source-facts/1' or any(s.get('supplier_quote') is not False for s in data['sources']):raise ValueError('Unquoted manufacturer fact catalogue required')
    value=dict(schema='osr-station-launch-alternatives/1',kinds=list(KINDS),source_facts=data,
        source_sha256=sources(root),physical_acceptance=False,**FLAGS)
    value['catalogue_id']=identity(value);return value


def _finite(v,name,positive=False):
    if type(v) not in (int,float) or not isfinite(v) or positive and v<=0:raise ValueError('Finite '+name+' required')
    return float(v)


def defaults(kind):
    if kind not in KINDS:raise ValueError('Registered station-launch alternative required')
    count=5 if kind=='five-20m-LIM' else 6 if kind=='six-20m-LIM' else 10
    if kind.endswith('LIM'):
        starts=[-13.+i*100.375 for i in range(count)]
        if kind=='six-20m-LIM':starts=[-13.+i*80. for i in range(6)]
        if kind=='ten-20m-LIM':starts=[-13.+i*45. for i in range(10)]
        length=20.
        if kind=='long-distributed-LIM':starts=[-13.,157.,327.];length=100.
        if kind=='continuous-LIM':starts=[-13.];length=513.
        return dict(bank_starts_m=starts,bank_length_m=length,motor_count=0)
    if kind=='station-pinch-rollers':
        return dict(bank_starts_m=[-12.,91.,194.,297.,400.],bank_length_m=12.,roller_pairs_per_bank=4,
            roller_diameter_m=.5,roller_width_m=.2,roller_wall_m=.04,drive_strip_length_m=16.8,
            drive_strip_height_m=.1,drive_strip_thickness_m=.02,motor_count=8,clamp_bore_m=.1,clamp_design_pressure_Pa=8e6)
    if kind=='cable-launch-tug':return dict(bank_starts_m=[0.],bank_length_m=500.,rope_launch_length_m=500.,rope_diameter_m=.032,
        drum_diameter_m=1.92,motor_count=6,tug_mass_kg=2500.,grip_design_capacity_N=100000.)
    return dict(bank_starts_m=[],bank_length_m=0.,rescue_motor_count=2,rescue_storage_kWh=5.,motor_count=2)


def _parameters(kind,p):
    d=defaults(kind)
    if p:
        if set(p)-set(d):raise ValueError('Only explicitly owned physical revision variables permitted')
        d.update(deepcopy(p))
    for key,v in d.items():
        if key=='bank_starts_m':
            if not isinstance(v,list) or len(v)>30 or len(v)!=len(set(v)) or any(type(x) not in (int,float) or not isfinite(x) for x in v):raise ValueError('Bounded distinct finite bank positions required')
        elif key in ('motor_count','roller_pairs_per_bank','rescue_motor_count'):
            if type(v) is not int or not 0<=v<=80:raise ValueError('Bounded integer drive count required')
        else:_finite(v,key,positive=not(kind=='onboard-rescue-research' and key=='bank_length_m'))
    if kind=='station-pinch-rollers' and (d['motor_count']!=2*d['roller_pairs_per_bank'] or d['roller_wall_m']>=d['roller_diameter_m']/2-.01 or not 0<d['drive_strip_length_m']<=17):raise ValueError('Explicit opposed motor/roller pairs, open roller core and one-car strip required')
    if kind=='cable-launch-tug' and d['rope_diameter_m'] not in (.02,.032):raise ValueError('Owned20/32mm catalogue rope grades only')
    return d


def _merge(intervals,a=0.,b=500.):
    rows=sorted((max(a,x),min(b,y)) for x,y in intervals if min(b,y)>max(a,x));out=[]
    for x,y in rows:
        if out and x<=out[-1][1]+1e-10:out[-1][1]=max(out[-1][1],y)
        else:out.append([x,y])
    return out


def _contact(parts,train_length,positions,limit=500.):
    """Exact piecewise contact count for point rollers against finite train strips."""
    intervals=[]
    for bank,index,x in positions:
        for a,b in parts:intervals.append((x+train_length-b,x+train_length-a,bank,index))
    events=sorted({0.,limit,*[x for a,b,_,_ in intervals for x in (a,b) if 0<x<limit]})
    counts=[];segments=[]
    for a,b in zip(events,events[1:]):
        mid=(a+b)/2;active={(bank,index) for lo,hi,bank,index in intervals if lo<mid<hi}
        segments.append(dict(front_interval_m=[a,b],active_roller_pairs=len(active)));counts.append(len(active))
    # Edge entry is separately retained; do not silently create a launch impulse.
    initially={(bank,index) for lo,hi,bank,index in intervals if lo<=0.<hi}
    coverage=_merge([(a,b) for a,b,_,_ in intervals],0.,limit)
    return dict(covered_front_intervals_m=coverage,powered_distance_m=fsum(b-a for a,b in coverage),
        minimum_active_pairs=min(counts) if counts else 0,maximum_active_pairs=max(counts) if counts else 0,
        initial_active_pairs=len(initially),segments=segments)


def _vehicle(v,bundle):
    if v.get('schema')!='osr-equipped-reference-cell-vehicle/1' or v.get('evaluation_id')!=identity({k:x for k,x in v.items() if k!='evaluation_id'}):raise ValueError('Exact equipped vehicle result required')
    validate_registry(v['registry'])
    if v.get('candidate_id')!=v['registry']['candidate_id']:raise ValueError('Vehicle/registry physical identity differs')
    req=v['requirements']
    if any(req.get(k)!=x for k,x in dict(cars=6,car_length_m=17.,fixed_seats_per_car=44,wheelchair_places_per_car=2,passenger_normal_per_car=46).items()):raise ValueError('Equal six-car17m44+2 comfort requirements required')
    if bundle is not None:
        railway_bundle.validate(bundle)
        if bundle['body_candidate_id']!=v['candidate_id']:raise ValueError('Bundle uses another physical vehicle')
        rotating=6*bundle['rotating_equivalent_kg_per_car']
    else:
        parts={p['physical_definition_id']:p for p in v['registry']['parts']};rotating=0.
        for o in v['registry']['occurrences']:
            p=parts[o['part_definition_id']];name=p['part_id'].lower()
            if not any(k in name for k in ('wheel-rim','wheel-web','friction-brake-disc','-axle-')) or 'bearing' in name:continue
            d=p['geometry']['dimensions_m'];r=d.get('outer_radius',d.get('radius'));ri=d.get('inner_radius',0.)
            if p['mass']['calculated_kg'] is not None:rotating+=.5*p['mass']['calculated_kg']*(r*r+ri*ri)/.320**2
    return v['summary'].get('mass_lower_bound_kg'),v['summary'].get('mass_upper_bound_kg'),rotating


def evaluate(vehicle,bundle=None,*,kind='station-pinch-rollers',distance_m=2000.,parameters=None,hypotheses=None,root=ROOT):
    if distance_m not in (1500.,2000.):raise ValueError('Explicit same-service1.5/2km comparison required')
    lower,upper,rotating=_vehicle(vehicle,bundle);p=_parameters(kind,parameters)
    h=dict(acceleration_m_s2=.4,speed_m_s=20.,headway_s=120.,rho_air_kg_m3=1.2,CdA_m2=8.,rolling_coefficient=.003,
        grade_fraction=0.,wind_m_s=0.,contact_friction_coefficient=.2,slip_fraction=.02,transmission_efficiency=.94,
        converter_efficiency=.97,rope_preload_N=20000.,rope_static_factor_hypothesis=5.,reset_acceleration_m_s2=.4,
        reset_speed_cap_m_s=20.,attachment_detachment_time_s=20.)
    if hypotheses:
        if set(hypotheses)-set(h):raise ValueError('Owned evaluation hypotheses required')
        h.update(deepcopy(hypotheses))
    for key,x in h.items():_finite(x,key)
    if (h['speed_m_s'],h['acceleration_m_s2'],h['headway_s'])!=(20.,.4,120.) or not 0<h['contact_friction_coefficient']<=1 or not 0<h['transmission_efficiency']<=1 or not 0<h['converter_efficiency']<=1 or not 0<=h['slip_fraction']<1 or h['reset_acceleration_m_s2']<=0 or h['reset_speed_cap_m_s']<=0 or h['rope_static_factor_hypothesis']<=1 or h['rope_preload_N']<0 or h['wind_m_s']<0 or h['grade_fraction']<0 or h['attachment_detachment_time_s']<0 or h['rolling_coefficient']<0 or h['CdA_m2']<0 or h['rho_air_kg_m3']<=0:raise ValueError('Physical coefficient/current-service domains required')
    facts=catalogue(root);motor=facts['source_facts']['sources'][0]['facts'];inventory=[];onboard=[];unknown=[]
    def solid(name,where,shape,dimensions,volume,density,count=1,at=None,source='explicit-research-geometry'):
        row=dict(part_id=name,installation=where,shape=shape,dimensions_m=dimensions,net_volume_m3=volume,density_kg_m3=density,
            calculated_mass_kg=volume*density,count=count,at_m=at,source=source,manufacturing='cut/form/machine/assemble/inspect; route unqualified')
        row['physical_definition_id']=identity({k:row[k] for k in ('part_id','installation','shape','dimensions_m','net_volume_m3')});inventory.append(row);return row
    def purchased(name,where,count,mass=None,source=None,at=None):
        row=dict(part_id=name,installation=where,shape='purchased-assembly-envelope',dimensions_m=None,net_volume_m3=None,
            calculated_mass_kg=None,catalogue_mass_kg=mass,mass_bounds_kg=None,count=count,at_m=at,source=source,
            manufacturing='qualified procurement, mounting and inspection pending')
        row['physical_definition_id']=identity({k:row[k] for k in ('part_id','installation','shape','dimensions_m','net_volume_m3')});inventory.append(row);return row
    contact=None;mechanism={};extra_train=0.;extra_rotating=0.;conditional_model=None
    if kind=='station-pinch-rollers':
        R=p['roller_diameter_m']/2;core_R=R-.01;inner=core_R-p['roller_wall_m'];width=p['roller_width_m'];banks=len(p['bank_starts_m']);pairs=p['roller_pairs_per_bank']
        strip_v=p['drive_strip_length_m']*p['drive_strip_height_m']*p['drive_strip_thickness_m'];strip=solid('passive-steel-drive-strip','onboard','box',[p['drive_strip_length_m'],p['drive_strip_thickness_m'],p['drive_strip_height_m']],strip_v,7850.,6)
        mounts=solid('drive-strip-mounting-brackets','onboard','box',[.08,.05,.008],.08*.05*.008,7850.,6*24)
        solid('strip-bolt-nut-washer-equivalent','onboard','equivalent-fastener',[.012,.06],.000009,7850.,6*24*4)
        extra_train=sum(x['calculated_mass_kg']*x['count'] for x in inventory)
        solid('hollow-steel-roller-core','wayside','tube',[core_R,inner,width],pi*(core_R**2-inner**2)*width,7850.,banks*2*pairs)
        solid('replaceable-elastomer-tread','wayside','tube',[R,core_R,width],pi*(R*R-core_R*core_R)*width,1200.,banks*2*pairs)
        solid('roller-shaft','wayside','cylinder',[.04,.5],pi*.04**2*.5,7850.,banks*2*pairs)
        solid('pinch-frame-steel-plate','wayside','box',[1.8,.8,.04],1.8*.8*.04,7850.,banks*pairs)
        bore=p['clamp_bore_m'];wall=max(.008,p['clamp_design_pressure_Pa']*bore/(2*100e6))
        solid('clamp-cylinder-barrel','wayside','tube',[bore/2+wall,bore/2,.25],pi*((bore/2+wall)**2-(bore/2)**2)*.25,7850.,banks*pairs)
        solid('clamp-piston','wayside','cylinder',[bore/2,.025],pi*(bore/2)**2*.025,7850.,banks*pairs)
        solid('clamp-piston-rod','wayside','cylinder',[.025,.35],pi*.025**2*.35,7850.,banks*pairs)
        solid('clamp-end-plate','wayside','box',[bore+.06,bore+.06,.02],(bore+.06)**2*.02,7850.,banks*pairs*2)
        solid('frame-retention-bolt-nut-washer-equivalent','wayside','equivalent-fastener',[.016,.08],.00002,7850.,banks*pairs*24)
        purchased('ABB-M3BP355MLB6-K','wayside',banks*p['motor_count'],motor['catalogue_mass_kg'],'abb-m3bp-355mlb-6-K')
        for name,n in [('roller-bearing-housing',banks*4*pairs),('geared-transmission',banks*2*pairs),('clamp-force-sensor-valve-and-flexible-hose-kit',banks*pairs),('VFD-protection-cooling-cabling',banks*2*pairs)]:purchased(name,'wayside',n)
        strips=[(17.5*i+(17-p['drive_strip_length_m'])/2,17.5*i+(17+p['drive_strip_length_m'])/2) for i in range(6)]
        positions=[(i,j,start+(j+.5)*p['bank_length_m']/pairs) for i,start in enumerate(p['bank_starts_m']) for j in range(pairs)]
        contact=_contact(strips,104.5,positions);active=2*contact['minimum_active_pairs']
        clamp_N=pi*p['clamp_bore_m']**2/4*p['clamp_design_pressure_Pa']
        conditional_model=dict(kind='pinch-roller-nameplate-and-design-clamp',positions=[list(x) for x in positions],
            train_drive_segments_m=[list(x) for x in strips],train_length_m=104.5,roller_radius_m=R,
            torque_per_motor_Nm=motor['rated_torque_Nm'],power_per_motor_W=motor['shaft_power_W'],
            gear_ratio=motor['rated_speed_rpm']/(20./R*60/(2*pi)),transmission_efficiency=h['transmission_efficiency'],
            normal_force_per_roller_bounds_N=[.8*clamp_N,clamp_N],friction_bounds=[h['contact_friction_coefficient'],max(.5,h['contact_friction_coefficient'])],
            shaft_rotor_inertia_per_motor_kg_m2=11.3,instantaneous_spinup_and_speed_matching_verified=False,
            source_class='C-design-clamp-and-contact;B-industrial-nameplate',railway_control_or_thermal_validated=False)
        mechanism=dict(active_motor_lower_count=active,roller_speed_at20m_s_rpm=20./R*60/(2*pi),
            gear_ratio_motor_to_roller=motor['rated_speed_rpm']/(20./R*60/(2*pi)),
            conditional_nameplate_shaft_power_W=active*motor['shaft_power_W']*h['transmission_efficiency'],
            actual_clamping_capacity_N=None,actual_contact_friction_model=None,available_force_map=None,
            balanced_lateral_clamp_reactions_required=True)
    elif kind=='cable-launch-tug':
        rope=facts['source_facts']['sources'][1]['facts']['32mm' if p['rope_diameter_m']==.032 else '20mm'];D=p['drum_diameter_m'];L=p['rope_launch_length_m'];rope_length=2*L+pi*D
        purchased('HYFLEX-6x36-1770-rope','wayside',1,rope_length*rope['mass_kg_per_m'],'brunton-hyflex-6x36-1770')
        solid('rope-driving-return-drum-shell','wayside','tube',[D/2,D/2-.04,.4],pi*((D/2)**2-(D/2-.04)**2)*.4,7850.,2)
        purchased('ABB-M3BP355MLB6-K','wayside',p['motor_count'],motor['catalogue_mass_kg'],'abb-m3bp-355mlb-6-K')
        for name,n in [('return-tug-assembly',1),('tensioner-and-termination',2),('drum-bearing-gearbox-mount',2),('protected-detachable-grip',1),('guide-return-roller',int(ceil(L/5.))*2),('VFD-protection-cooling-cabling',p['motor_count'])]:purchased(name,'wayside',n,p['tug_mass_kg'] if name=='return-tug-assembly' else None)
        mechanism=dict(rope_length_m=rope_length,rope_mass_kg=rope_length*rope['mass_kg_per_m'],rope_minimum_breaking_force_N=rope['minimum_breaking_force_N'],
            drum_speed_at20m_s_rpm=20./(D/2)*60/(2*pi),drum_to_rope_diameter_ratio=D/p['rope_diameter_m'],
            conditional_nameplate_shaft_power_W=p['motor_count']*motor['shaft_power_W']*h['transmission_efficiency'],
            actual_bend_fatigue_or_grip_verified=False,rope_powered_length_m=L,manufacturer_APM_speed_domain_m_s=15.,reference20m_s_exceeds_published_APM_domain=True,
            cable_APM_catalogue_is_not_station_launch_qualification=True,available_force_map=None)
        conditional_model=dict(kind='cable-nameplate-and-design-grip',launch_front_window_m=[0.,L],drum_radius_m=D/2,
            motor_count=p['motor_count'],torque_per_motor_Nm=motor['rated_torque_Nm'],power_per_motor_W=motor['shaft_power_W'],
            gear_ratio=motor['rated_speed_rpm']/(20./(D/2)*60/(2*pi)),transmission_efficiency=h['transmission_efficiency'],
            rope_tension_limit_N=rope['minimum_breaking_force_N']/h['rope_static_factor_hypothesis']-h['rope_preload_N'],
            grip_design_capacity_N=p['grip_design_capacity_N'],source_class='C-grip-and-passenger-rope-factor;B-industrial-nameplate',
            detachment_return_and_grip_verified=False,railway_control_or_thermal_validated=False)
        contact=dict(powered_distance_m=min(500.,L),covered_front_intervals_m=[[0.,min(500.,L)]],initial_active_pairs=None)
    elif kind=='onboard-rescue-research':
        purchased('onboard-rescue-motor-and-transmission','onboard',p['rescue_motor_count'])
        purchased('onboard-rescue-energy-store-and-protection','onboard',1)
        mechanism=dict(storage_nameplate_kWh=p['rescue_storage_kWh'],actual_rescue_mass_kg=None,actual_available_force_N=None,
            recovery_traction_changes_reference=False,normal_launch_model_supported=False,available_force_map=None)
        unknown.append('Separate onboard recovery architecture needs driven wheelset, mass, capacity/fault/fire and protection design; it does not become the selected reference')
    else:
        fin_parts=[];defs={x['physical_definition_id']:x for x in vehicle['registry']['parts']}
        for o in vehicle['registry']['occurrences']:
            x=defs[o['part_definition_id']]
            if 'passive-aluminium-fin' in x['part_id'].lower():
                L=x['geometry']['dimensions_m'][0];center=o['transform'][0][3];fin_parts.append((center-L/2,center+L/2))
        intervals=[(start+104.5-b,start+p['bank_length_m']+104.5-a) for start in p['bank_starts_m'] for a,b in fin_parts]
        covered=_merge(intervals);contact=dict(covered_front_intervals_m=covered,powered_distance_m=fsum(b-a for a,b in covered),
            available_force_map=None,contact_geometry_is_not_available_thrust=True)
        if bundle is not None and p['bank_length_m']==20.:
            primary=bundle.get('wayside_primary_stock',[])
            for bank,start in enumerate(p['bank_starts_m']):
                for item in primary:
                    row=deepcopy(item);row.update(part_id=f'bank/{bank}/'+item['id'],installation='wayside',count=1,calculated_mass_kg=item['mass_kg'],
                        at_m=[start+item['at_m'][0],item['at_m'][1],item['at_m'][2]],physical_definition_id=identity(item));inventory.append(row)
        else:
            purchased('new-LIM-primary-coils-teeth-backiron','wayside',len(p['bank_starts_m']))
            unknown.append('New/uncounted primary geometry requires winding/slot/backiron/lead/cooling definition;20m evidence is not scaled to100/513m')
        purchased('inverter-feeder-switchgear-cooling-bank','wayside',len(p['bank_starts_m']))
        mechanism=dict(installed_primary_length_m=len(p['bank_starts_m'])*p['bank_length_m'],actual_available_force_N=None,
            available_force_map=None,actual_converter_limits=None,unconverged_moving_EM_is_not_validation=True)
    # Prototype mounting centres, not a claim that purchased envelope/tolerance
    # or full six-degree-of-freedom installation clearance is qualified.
    for item in inventory:
        if item['installation']=='wayside' and kind=='station-pinch-rollers':
            banks=len(p['bank_starts_m']);per=item['count']//banks
            local=[(j+.5)*p['bank_length_m']/p['roller_pairs_per_bank'] for j in range(p['roller_pairs_per_bank'])]
            item['longitudinal_instance_centres_m']=[start+local[min(len(local)-1,int(k*len(local)/per))] for start in p['bank_starts_m'] for k in range(per)]
            item['placement_basis']='Prototype pinch-pair mounting centres; purchased widths, vertical/lateral coordinates and civil interfaces unqualified'
        elif item['installation']=='wayside' and kind=='cable-launch-tug':
            if item['part_id']=='HYFLEX-6x36-1770-rope':
                item['distributed_mass_model']=dict(straight_return_legs=2,start_m=0.,end_m=p['rope_launch_length_m'],end_wrap_length_m=pi*p['drum_diameter_m'],mass_kg_per_m=rope['mass_kg_per_m'])
            elif item['part_id']=='guide-return-roller':
                item['longitudinal_instance_centres_m']=[(k+.5)*p['rope_launch_length_m']/item['count'] for k in range(item['count'])]
            else:item['longitudinal_instance_centres_m']=[0. if k<max(1,item['count']//2) else p['rope_launch_length_m'] for k in range(item['count'])]
            item['placement_basis']='Prototype drive/return/tug arrangement; actual foundation, grip, rope support and safety geometry unqualified'
    physical=dict(schema='osr-station-launch-physical-alternative/1',base_vehicle_id=vehicle['candidate_id'],kind=kind,geometry=p,
        onboard_existing_secondary_retained=True,inventory_definitions=[{k:r.get(k) for k in ('part_id','physical_definition_id','installation','count','at_m','longitudinal_instance_centres_m','distributed_mass_model')} for r in inventory],
        service=dict(cars=6,car_length_m=17.,seats_per_car=44,wheelchair_places_per_car=2,distance_m=distance_m,headway_s=120.,speed_m_s=20.,acceleration_m_s2=.4),
        normal_traction_onboard=kind=='onboard-rescue-research')
    candidate=identity(physical)
    for row in inventory:row['candidate_id']=candidate
    scopes=[]
    for label,passengers in [('empty',0),('normal',276),('crowd-control',960)]:
        m=None if upper is None else upper+extra_train+75*passengers
        if kind=='cable-launch-tug' and m is not None:m+=p['tug_mass_kg']+mechanism['rope_mass_kg']
        if m is None:scopes.append(dict(load=label,mass_kg=None,required_force_N=None,required_mechanical_power_W=None));continue
        force=(m+rotating+extra_rotating)*.4+m*9.80665*(h['rolling_coefficient']+h['grade_fraction'])+.5*h['rho_air_kg_m3']*h['CdA_m2']*(20+h['wind_m_s'])**2
        energy_kinetic=.5*(m+rotating)*20**2;work=(m+rotating)*.4*500+m*9.80665*(h['rolling_coefficient']+h['grade_fraction'])*500+.5*h['rho_air_kg_m3']*h['CdA_m2']*(.4*500**2+(4/3)*h['wind_m_s']*sqrt(.8)*500**1.5+h['wind_m_s']**2*500)
        row=dict(load=label,mass_kg=m,known_rotating_equivalent_kg=rotating,required_force_N=force,required_mechanical_power_W=force*20,
            kinetic_energy_J=energy_kinetic,launch_work_J=work,launch_work_kWh=work/3.6e6,
            minimum_launch_distance_at_declared_acceleration_m=500.,launch_time_s=50.,energy_is_conditional_lower_scope=True,
            mechanical_power_screen_passed=None if mechanism.get('conditional_nameplate_shaft_power_W') is None else mechanism['conditional_nameplate_shaft_power_W']>=force*20)
        route_bounds=[]
        for case_grade in sorted({h['grade_fraction'],.02}):
            coast=distance_m-500.;rise=coast*case_grade;potential=m*9.80665*rise
            rolling=m*9.80665*h['rolling_coefficient']*coast
            residual=energy_kinetic-potential-rolling
            route_bounds.append(dict(coast_grade_fraction=case_grade,unpowered_coast_distance_m=coast,
                conditional_unpowered_start_front_m=500.,rise_during_unpowered_coast_m=rise,
                point_mass_zero_loss_maximum_rise_m=20**2/(2*9.80665),
                counted_rotor_inclusive_zero_loss_maximum_rise_m=energy_kinetic/(m*9.80665),
                kinetic_energy_at_launch_cap_J=energy_kinetic,potential_energy_required_J=potential,
                rolling_loss_lower_scope_J=rolling,remaining_energy_before_aerodynamic_and_braking_J=residual,
                fails_even_zero_drag_energy_bound=energy_kinetic<potential,
                fails_declared_rolling_energy_bound=residual<0,
                maximum_coast_distance_with_declared_grade_rolling_m=None if case_grade+h['rolling_coefficient']==0 else energy_kinetic/(m*9.80665*(case_grade+h['rolling_coefficient'])),
                failure_class='physical-necessary-bound' if residual<0 else 'necessary-bound-only-not-journey-proof',
                required_revision_if_failed='Add powered distribution/recovery energy or revise actual route/grade/speed/spacing as a new architecture; mass reduction alone cannot erase specific-energy limit'))
        row['route_energy_bounds']=route_bounds
        if kind=='station-pinch-rollers':
            n=mechanism['active_motor_lower_count'];row.update(required_total_normal_force_N=force/h['contact_friction_coefficient'],
                required_normal_per_active_roller_N=None if n==0 else force/(h['contact_friction_coefficient']*n),
                required_torque_per_active_roller_Nm=None if n==0 else force*p['roller_diameter_m']/2/n,
                slip_heat_per_launch_J=work*h['slip_fraction']/(1-h['slip_fraction']),
                stationary_drive_average_shaft_power_at_headway_W=work/h['headway_s'],
                input_energy_lower_scope_kWh=work/(h['transmission_efficiency']*h['converter_efficiency']*motor['full_load_efficiency'])/3.6e6,
                required_frame_longitudinal_reaction_N=force,opposed_clamp_force_each_side_N=force/(2*h['contact_friction_coefficient']),
                equivalent_clamp_hydraulic_pressure_Pa=None)
        if kind=='cable-launch-tug':
            tight=force+h['rope_preload_N'];row.update(rope_tight_side_tension_N=tight,
                minimum_breaking_force_ratio=mechanism['rope_minimum_breaking_force_N']/tight,
                passes_declared_static_rope_factor=mechanism['rope_minimum_breaking_force_N']/tight>=h['rope_static_factor_hypothesis'],
                drive_drum_torque_Nm=force*p['drum_diameter_m']/2,
                upper_coupler_tension_hypothesis_N=force,drive_foundation_resultant_rope_load_N=tight+h['rope_preload_N'],
                fatigue_termination_sheave_and_passenger_safety_factor_approved=False)
        scopes.append(row)
    reset=None
    if kind=='cable-launch-tug':
        L=p['rope_launch_length_m'];a=h['reset_acceleration_m_s2'];v=h['reset_speed_cap_m_s'];reset=2*sqrt(L/a) if L<v*v/a else 2*v/a+(L-v*v/a)/v
        mechanism.update(minimum_rest_to_rest_reset_time_s=reset,launch_attach_reset_cycle_lower_s=50+reset+h['attachment_detachment_time_s'],
            cycle_fits120s_hypothesis=50+reset+h['attachment_detachment_time_s']<=120.,safe_detachment_and_tug_stop_verified=False)
    known=fsum(r.get('calculated_mass_kg',r.get('mass_kg',0.))*r['count'] for r in inventory if r.get('calculated_mass_kg',r.get('mass_kg')) is not None)
    supplier=fsum(r['catalogue_mass_kg']*r['count'] for r in inventory if r.get('catalogue_mass_kg') is not None)
    unknown_mass=[r['part_id'] for r in inventory if r.get('calculated_mass_kg',r.get('mass_kg')) is None and r.get('catalogue_mass_kg') is None]
    missing=unknown+['Actual force/current/voltage/control, repeated heat/cooling and passenger-safe failure response',
        'Couplers, mounting fatigue, pinch/entanglement containment, tolerances, maintenance and emergency access',
        'Prototype strip/roller/cylinder envelope interference with retained bogies, secondary hangers and body remains unverified; rematerialize attachments before physical use',
        'Independent braking/stranded-train rescue, qualified headway and real supplier/manufacturing/whole-life prices']
    if contact is not None and contact['powered_distance_m']<500.-1e-8:missing.append('Insufficient geometric powered contact within500m at0.4m/s2, even before real force limits')
    value=dict(schema='osr-station-launch-alternative-evaluation/1',candidate_id=candidate,body_candidate_id=vehicle['candidate_id'],kind=kind,
        physical_definition=physical,parameters=p,hypotheses=h,conditional_force_model=conditional_model,inventory=inventory,known_geometry_stock_mass_kg=known,
        published_catalogue_mass_subtotal_kg=supplier,unknown_installed_mass_items=unknown_mass,complete_installed_mass_kg=None,
        added_counted_onboard_mass_kg=extra_train,contact_geometry=contact,mechanism=mechanism,load_cases=scopes,
        complete_journey_simulated=False,numerical_arrivals=0,available_operating_map=None,
        installed_CAPEX_usd=None,whole_life_cost_usd=None,actual_supplier_quotes=0,
        source_sha256=sources(root),source_fact_ids=[s['id'] for s in facts['source_facts']['sources']],
        next_experiment_priority='contact/clamp/drive duty rig' if kind=='station-pinch-rollers' else 'rope/grip/return-cycle rig' if kind=='cable-launch-tug' else 'moving-field/converter/cooling method' if kind.endswith('LIM') else 'separate recovery hardware definition',
        open_tasks=missing,integrated_winner=None,**FLAGS)
    value['evaluation_id']=identity(value);return value


def revise(vehicle,previous,changes,bundle=None,*,root=ROOT):
    if previous.get('evaluation_id')!=identity({k:v for k,v in previous.items() if k!='evaluation_id'}) or previous.get('body_candidate_id')!=vehicle['candidate_id']:
        raise ValueError('Exact parent alternative and same vehicle required')
    if not changes or set(changes)-PHYSICAL_KEYS:raise ValueError('Explicit supported physical hardware revision required')
    parameters=dict(previous['parameters'],**changes)
    out=evaluate(vehicle,bundle,kind=previous['kind'],distance_m=previous['physical_definition']['service']['distance_m'],parameters=parameters,hypotheses=previous['hypotheses'],root=root)
    if out['candidate_id']==previous['candidate_id']:raise ValueError('A hardware revision must actually change physical definition')
    out['ancestry']=dict(parent_candidate_id=previous['candidate_id'],parent_evaluation_id=previous['evaluation_id'],physical_changes=deepcopy(changes),
        invalidated_stages=['inventory','propulsion','thermal','couplers','civil-reactions','manufacturing','cost','controls','journey'])
    out['evaluation_id']=identity({k:v for k,v in out.items() if k!='evaluation_id'});return out


def compare(results):
    if not results:raise ValueError('Explicit same-service alternatives required')
    services=[r['physical_definition']['service'] for r in results]
    if any(s!=services[0] for s in services):raise ValueError('Compare distance/headway/formation/speed equally')
    if any(r.get('evaluation_id')!=identity({k:v for k,v in r.items() if k!='evaluation_id'}) for r in results):raise ValueError('Alternative evaluation identity differs')
    # Ranking chooses which supported necessary-bound experiment to perform next;
    # no amount of catalogue arithmetic selects a physically accepted railway.
    rows=sorted([dict(candidate_id=r['candidate_id'],kind=r['kind'],necessary_power_holds=sum(x.get('mechanical_power_screen_passed') is False for x in r['load_cases']),
        unknown_mass_items=len(r['unknown_installed_mass_items']),next_experiment=r['next_experiment_priority']) for r in results],key=lambda r:(r['necessary_power_holds'],r['unknown_mass_items'],r['kind']))
    value=dict(schema='osr-station-launch-next-experiment-comparison/1',service=services[0],ranking=rows,
        ranking_purpose='next-experiment-only; unsupported force, safety and whole-life cost prevent integrated selection',integrated_winner=None,cheapest_candidate=None,**FLAGS)
    value['evaluation_id']=identity(value);return value


def force_bounds(result,front_m,speed_m_s,*,condition='nominal',power_enabled=True,failed_banks=()):
    """Conditional mechanical capacity caps, never an admitted operating map.

    Instantaneous speed matching and clamp/grip design values are hypotheses.
    Spin-up/handoff and opposing passive drag require separate dynamic states.
    """
    if result.get('evaluation_id')!=identity({k:v for k,v in result.items() if k!='evaluation_id'}):raise ValueError('Exact alternative evaluation required')
    return _force_bounds_owned(result,front_m,speed_m_s,condition=condition,power_enabled=power_enabled,failed_banks=failed_banks)


def _force_bounds_owned(result,front_m,speed_m_s,*,condition='nominal',power_enabled=True,failed_banks=()):
    count=len(result['parameters']['bank_starts_m'])
    if not isinstance(failed_banks,(list,tuple)) or len(failed_banks)!=len(set(failed_banks)) or any(type(b) is not int or not 0<=b<count for b in failed_banks):raise ValueError('Explicit distinct in-range failed bank identities required')
    x=_finite(front_m,'train-front position');v=_finite(speed_m_s,'speed')
    if v<0 or v>20. or condition not in ('nominal','wet','low-friction') or type(power_enabled) is not bool:raise ValueError('Declared force-model domain required')
    model=result.get('conditional_force_model')
    if model is None:return dict(state='held-no-owned-conditional-force-model',force_N=None,available_operating_map=None,physical_accepted=False)
    if not power_enabled:return dict(state='known-commanded-power-off',force_N=[0.,0.],active_motor_count=0,passive_drag_N=None,available_operating_map=None,physical_accepted=False)
    if model['kind'].startswith('pinch'):
        active=0
        for bank,index,pos in model['positions']:
            if bank in failed_banks:continue
            if any(a+x-model['train_length_m']<=pos<=b+x-model['train_length_m'] for a,b in model['train_drive_segments_m']):active+=2
        R=model['roller_radius_m'];mu=model['friction_bounds'];normal=model['normal_force_per_roller_bounds_N']
        torque=active*model['torque_per_motor_Nm']*model['gear_ratio']*model['transmission_efficiency']/R
        power=active*model['power_per_motor_W']*model['transmission_efficiency']
        if condition=='low-friction':mu=[mu[0]/2,mu[0]]
        elif condition=='wet':mu=[mu[0],mu[0]]
        caps=[min(torque,power/max(v,1e-12),active*mu[i]*normal[i]) for i in range(2)]
    else:
        active=model['motor_count'] if 0 not in failed_banks and model['launch_front_window_m'][0]<=x<=model['launch_front_window_m'][1] else 0
        torque=active*model['torque_per_motor_Nm']*model['gear_ratio']*model['transmission_efficiency']/model['drum_radius_m']
        power=active*model['power_per_motor_W']*model['transmission_efficiency']
        capacity=min(torque,power/max(v,1e-12),max(0.,model['rope_tension_limit_N']),model['grip_design_capacity_N']) if active else 0.
        caps=[capacity,capacity]
    return dict(state='conditional-unqualified-capacity-caps',force_N=caps,active_motor_count=active,
        shaft_power_upper_W=power,torque_force_cap_N=torque,passive_drag_N=None,
        source_class=model['source_class'],instantaneous_contact_and_controller_response_verified=False,
        available_operating_map=None,physical_accepted=False)


def force_model(result):
    """Validate once, then evaluate an owned immutable conditional model copy."""
    if result.get('evaluation_id')!=identity({k:v for k,v in result.items() if k!='evaluation_id'}):raise ValueError('Exact alternative evaluation required')
    owned=deepcopy(result)
    def evaluator(front_m,speed_m_s,*,condition='nominal',power_enabled=True,failed_banks=()):
        return _force_bounds_owned(owned,front_m,speed_m_s,condition=condition,power_enabled=power_enabled,failed_banks=failed_banks)
    return evaluator
