"""Counted fixed booster and independently equipped rescue-node candidates.

The rope table is a primary-manufacturer baseline. Design factors, termination,
soil, material, access, essential loads and prices are declared study inputs.
No passenger station, qualified route, installed rate or safety release is implied.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip
import json
import math
import tomllib

ROOT=Path(__file__).resolve().parents[2]
INPUT=Path(__file__).with_name('booster-kit.toml')
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/booster-kit'
FILES={'result.json.gz','definition.json','overview.svg','README.md'}
FLAGS=dict(design_complete=False,physical_validation=False,manufacturing_release=False,physical_release=False)
MAX=16*1024*1024


def positive(value,name,zero=False):
    if type(value) not in (int,float) or not math.isfinite(value) or (value<0 if zero else value<=0):
        raise ValueError('finite positive '+name+' required')
    return value


def load():
    a=tomllib.loads(INPUT.read_text())
    if a['schema']!='osr-fixed-booster-and-recovery-kit/1':raise ValueError('fixed booster kit schema required')
    if any(v is not False for v in a['validation'].values()) or a['cost']['costs_are_quotes'] is not False:
        raise ValueError('qualification and prices remain unaccepted')
    for group in ('booster','recovery','cost'):
        for key,value in a[group].items():
            if type(value) in (int,float):positive(value,group+'/'+key)
            if isinstance(value,list):
                if not 1<=len(value)<=12:raise ValueError('bounded alternatives required')
                for entry in value:positive(entry,group+'/'+key)
    r=a['recovery']
    for key in ('termination_efficiency_assumption','winch_efficiency','rope_packing_fraction','soil_friction_assumption'):
        if r[key]>1:raise ValueError('bounded fraction required')
    if not 100<=r['maximum_node_spacing_m']<=2500 or r['drum_skin_m']>=r['selected_rope_diameter_m']*r['drum_diameter_ratio']/2:
        raise ValueError('bounded node and drum dimensions required')
    if type(r['anchor_bolts']) is not int or r['anchor_bolts']%2 or not 4<=r['anchor_bolts']<=32:raise ValueError('even bounded anchor quantity required')
    if 2*r['portal_wall_m']>=r['portal_box_side_m']:raise ValueError('portal wall consumes bore')
    for key in ('faces_per_direction','mounts_per_face','cabinet_pads'):
        if type(a['booster'][key]) is not int or not 1<=a['booster'][key]<=8:raise ValueError('bounded integer quantities required')
    return a


def takeoff(length_m=375.,directions=2):
    from . import configuration,geometry
    a=load();b=a['booster'];positive(length_m,'booster length')
    if length_m>1000 or type(directions) is not int or not 1<=directions<=2:raise ValueError('bounded fixed-zone quantity required')
    # The final cassette is shortened, never charged as an extra complete length.
    lengths=[min(b['cassette_length_m'],length_m-i*b['cassette_length_m']) for i in range(math.ceil(length_m/b['cassette_length_m']))]
    faces=b['faces_per_direction']*directions;count=faces*len(lengths);bolts=count*b['mounts_per_face']
    steel=geometry.MATERIALS['steel'];cv=configuration.selected().civil
    plate_mass=faces*sum(lengths)*b['mount_width_m']*b['mount_thickness_m']*steel
    bolt_mass=bolts*math.pi*b['mount_bolt_diameter_m']**2/4*b['mount_bolt_length_m']*steel
    cabinet_shell=2*b['cabinet_skin_m']*(b['cabinet_length_m']*b['cabinet_width_m']+b['cabinet_length_m']*b['cabinet_height_m']+b['cabinet_width_m']*b['cabinet_height_m'])
    pad=b['cabinet_pads']*b['cabinet_pad_length_m']*b['cabinet_pad_width_m']*b['cabinet_pad_depth_m']
    return dict(kind='fixed-midway-accelerator',length_per_direction_m=length_m,directions=directions,passenger_station=False,
        face_cassettes=count,cassette_lengths_per_face_m=lengths,face_metres=faces*length_m,
        mount_bolts=bolts,addressable_sections=directions*math.ceil(length_m/b['section_length_m']),
        ordinary_beam_bays_occupied_per_direction=math.ceil(length_m/cv.span_m),additional_ordinary_beams_credited=0,
        material_quantities=dict(mount_plate_steel_kg=plate_mass,mount_bolt_stock_kg=bolt_mass,
            cabinet_shell_steel_kg=b['cabinet_pads']*cabinet_shell*steel,cabinet_pad_concrete_m3=pad),
        mount_and_cabinet_stock_target_usd=(plate_mass+bolt_mass+b['cabinet_pads']*cabinet_shell*steel)*a['cost']['steel_fabricated_usd_kg']+pad*a['cost']['concrete_cast_usd_m3'],
        winding_core_cooling_and_power_hardware_mass_kg=None,complete_installed_cost_usd=None,supplier_quote=False,
        no_double_count='Ordinary beams/bearings/supports stay in route civil bill; stock target does not include a second motor electrical allowance',
        interfaces=['2.5m datum-controlled face cassettes; segmented mounts clear beam joints','One fixed and one guided bearing per ordinary span; actual traction reactions allocated spatially',
            'Separately protected feeder, earth, isolation, converter, resistor and cooling interfaces','Independent ground access, cabinet pads and replaceable lifting/maintenance provisions'],
        open=['Measured normal/thrust/loss map and repeated thermal duty','Embedded anchor breakout, torsion, prying, fatigue and rail/gap alignment',
            'No automatic refuge, charging, recovery winch or passenger boarding function'],**FLAGS)


def span_reactions(forces,*,span_m=25.):
    positive(span_m,'bearing span');rows={};total=0.
    if not isinstance(forces,list) or len(forces)>100000:raise ValueError('bounded force locations required')
    for point in forces:
        x=positive(point['chainage_m'],'chainage',True);force=point['force_n']
        if type(force) not in (int,float) or not math.isfinite(force):raise ValueError('finite signed force required')
        bay=math.floor(x/span_m);rows[bay]=rows.get(bay,0.)+force;total+=force
    return dict(bearing_spec='one anchored fixed end and one guided end per span; exact half-open force allocation',
        fixed_bearing_reactions_n={str(k):-v for k,v in rows.items()},total_applied_force_n=total,
        equilibrium_residual_n=total-sum(rows.values()),connection_accepted=False,**FLAGS)


def electrical_duty(samples,*,headway_s):
    positive(headway_s,'headway')
    if not isinstance(samples,list) or not 2<=len(samples)<=100000:raise ValueError('bounded sampled electrical duty required')
    times=[];loss=[]
    for row in samples:
        times.append(positive(row['time_s'],'sample time',True));i=row['current_a'];res=positive(row['resistance_ohm'],'resistance')
        if type(i) not in (int,float) or not math.isfinite(i):raise ValueError('finite equivalent current required')
        loss.append(i*i*res)
    if any(b<=a for a,b in zip(times,times[1:])) or times[-1]-times[0]>headway_s:raise ValueError('ordered nonoverlapping duty required')
    energy=sum((b-a)*(x+y)/2 for a,b,x,y in zip(times,times[1:],loss,loss[1:]))
    return dict(equivalent_copper_heat_j=energy,mean_repeated_copper_heat_w=energy/headway_s,
        peak_copper_heat_w=max(loss),switching_core_and_inactive_losses_j=None,
        winding_temperature_c=None,thermal_acceptance=False,
        scope='Equivalent circuit I²R integration; actual three-phase current distribution and thermal network remain unqualified',**FLAGS)


def _tube(side,wall):
    return dict(area_m2=side**2-(side-2*wall)**2,inertia_m4=(side**4-(side-2*wall)**4)/12)


def recovery(c=None,*,cars=None,distance_m=5000.,runtime_s=300.,post_spacing_m=1000.,speed_m_s=.5,pack_kwh=30.,dwell_s=None,connected_fraction=None):
    from . import model,configuration,geometry
    c=c or model.load()[1]
    if cars is not None:
        if type(cars) is not int or not 1<=cars<=12:raise ValueError('bounded recovery formation required')
        c=deepcopy(c);c['vehicle']['cars_per_train']=cars
    a=load();r=a['recovery'];rate=a['cost'];cv=configuration.selected(c).civil
    for name,value in locals().copy().items():
        if name in {'distance_m','runtime_s','post_spacing_m','speed_m_s','pack_kwh'}:positive(value,name)
    if distance_m>20000 or post_spacing_m>distance_m or speed_m_s>2 or pack_kwh>120 or runtime_s>1800:
        raise ValueError('bounded recovery study required')
    cars=c['vehicle']['cars_per_train'];mass=model.mass(c,c['mass']['ferrite_base'],pack_kwh)['aw3_kg']*cars
    reach=min(post_spacing_m,distance_m)/2;rope_length=reach+r['rope_tail_m'];rope_mass=rope_length*r['selected_rope_mass_kg_m']
    grade=.05;grade_force=mass*9.81*grade/math.sqrt(1+grade*grade)
    drag=cars*c['power']['passive_rail_drag_study_n_per_car']
    cable_drag=rope_mass*9.81*r['cable_drag_fraction'];pull=(grade_force+drag+cable_drag)*r['working_pull_factor']
    rope_capacity=r['selected_rope_minimum_breaking_force_n']*r['termination_efficiency_assumption']/r['rope_design_factor']
    negative_rope=r['negative_rope_minimum_breaking_force_n']*r['termination_efficiency_assumption']/r['rope_design_factor']
    time=r['deployment_s']+reach/speed_m_s;essential=r['critical_services_kw_per_car']*time/3600
    p=c['power']
    dwell=p['station_dwell_seconds'] if dwell_s is None else positive(dwell_s,'actual incoming dwell')
    fraction=p['charger_effective_seconds']/p['station_dwell_seconds'] if connected_fraction is None else positive(connected_fraction,'connected fraction',True)
    if dwell>600 or not 0<=fraction<=1:raise ValueError('bounded actual dwell/connected fraction required')
    disconnected=dwell*(1-fraction)
    incoming=p['hot_hotel_kw_per_car']*(runtime_s+disconnected)/3600
    usable=pack_kwh*p['eol_capacity_fraction']*(p['normal_soc_high']-p['normal_soc_low']);available=usable-incoming
    d=r['selected_rope_diameter_m'];core=d*r['drum_diameter_ratio'];width=r['drum_width_m'];skin=r['drum_skin_m']
    cable_volume=math.pi*d*d/4*rope_length/r['rope_packing_fraction'];outer=2*math.sqrt((core/2)**2+cable_volume/(math.pi*width))
    flange=outer+2*r['flange_radial_margin_m'];shaft=r['shaft_diameter_m'];steel=geometry.MATERIALS['steel']
    barrel_volume=math.pi*((core/2)**2-(core/2-skin)**2)*width
    flange_volume=2*math.pi*((flange/2)**2-(shaft/2)**2)*skin
    shaft_volume=math.pi*shaft*shaft/4*r['shaft_length_m'];drum_mass=(barrel_volume+flange_volume+shaft_volume)*steel
    torque=pull*outer/2*r['holding_torque_multiplier'];shaft_shear=16*torque/(math.pi*shaft**3)
    height=cv.pier_height_m+.9+cv.depth_m+.3;section=_tube(r['portal_box_side_m'],r['portal_wall_m']);bay=r['portal_leg_spacing_m']
    levels=math.ceil(height/r['portal_brace_pitch_m']);brace=_tube(r['portal_brace_side_m'],r['portal_brace_wall_m'])
    brace_length=4*levels*math.hypot(height/levels,bay)
    tie_length=(levels+1)*(bay+r['portal_box_side_m'])
    portal_mass=((2*height+tie_length)*section['area_m2']+brace_length*brace['area_m2'])*steel
    moment=pull*height;leg_force=moment/bay+pull/2+(portal_mass+drum_mass)*9.81/2
    leg_stress=leg_force/section['area_m2'];euler=math.pi**2*r['steel_e_pa']*section['inertia_m4']/(height/levels)**2
    input_kw=pull*speed_m_s/r['winch_efficiency']/1000
    rated_input_kw=math.ceil(input_kw/25)*25
    power_scale=max(1.,rated_input_kw/100)
    drive_mass=rate['motor_gearbox_brakes_controls_mass_allowance_kg']*power_scale
    anchor_tension_capacity=r['anchor_bolts']/2*r['anchor_thread_area_m2']*r['anchor_tension_screen_pa']
    anchor_shear_capacity=r['anchor_bolts']*r['anchor_thread_area_m2']*r['anchor_shear_screen_pa']
    anchor_demand=moment/bay+pull/2
    foundation=[]
    for side in r['foundation_sides_m']:
        volume=side*side*r['foundation_depth_m'];normal=(volume*geometry.MATERIALS['concrete']+portal_mass+drum_mass+drive_mass)*9.81+pull
        eccentricity=moment/normal;low=normal/(side*side)*(1-6*eccentricity/side);high=normal/(side*side)*(1+6*eccentricity/side)
        passed=low>=0 and high<=r['soil_bearing_screen_pa'] and r['soil_friction_assumption']*normal>=pull
        foundation.append(dict(side_m=side,depth_m=r['foundation_depth_m'],concrete_m3=volume,minimum_pressure_pa=low,maximum_pressure_pa=high,
            sliding_capacity_n=r['soil_friction_assumption']*normal,moment_nm=moment,screen_pass=passed,ground_accepted=False))
    selected=next((row for row in foundation if row['screen_pass']),None)
    steel_mass=portal_mass+drum_mass+r['anchor_bolts']*math.pi*r['anchor_diameter_m']**2/4*r['anchor_length_m']*steel
    quantities=dict(rope_m=rope_length,rope_kg=rope_mass,drum_and_shaft_kg=drum_mass,portal_structural_steel_kg=portal_mass,
        fabricated_steel_with_anchor_stock_kg=steel_mass,motor_gearbox_brakes_controls_mass_allowance_kg=drive_mass,
        foundation_concrete_m3=selected['concrete_m3'] if selected else None,
        reinforcing_kg=selected['concrete_m3']*rate['reinforcement_kg_m3'] if selected else None)
    cost_rows=[dict(id='rope',quantity=rope_mass,unit='kg',rate=rate['rope_finished_usd_kg']),
        dict(id='fabricated-drum-tower-anchor-stock',quantity=steel_mass,unit='kg',rate=rate['steel_fabricated_usd_kg'])]
    if selected:cost_rows.extend([dict(id='foundation-concrete',quantity=selected['concrete_m3'],unit='m3',rate=rate['concrete_cast_usd_m3']),dict(id='foundation-reinforcement',quantity=quantities['reinforcing_kg'],unit='kg',rate=rate['reinforcement_usd_kg']),dict(id='foundation-excavation',quantity=(selected['side_m']+1)**2*(selected['depth_m']+.4),unit='m3',rate=rate['excavation_usd_m3'])])
    for key in ('rescue_motor_gearbox_brakes_controls_usd','independent_power_interface_usd','access_platform_hardstand_usd','installation_and_proof_test_usd'):
        cost_rows.append(dict(id=key,quantity=power_scale if key in {'rescue_motor_gearbox_brakes_controls_usd','independent_power_interface_usd'} else 1.,unit='target package',rate=rate[key]))
    for row in cost_rows:row.update(amount_usd=row['quantity']*row['rate'],supplier_quote=False)
    energy_ok=available>=essential;strength_ok=pull<=rope_capacity and shaft_shear<=r['shaft_shear_screen_pa'] and leg_stress<=r['steel_stress_screen_pa'] and leg_force<=euler and anchor_tension_capacity>=anchor_demand and anchor_shear_capacity>=pull and selected is not None
    return dict(schema='osr-recovery-kit-study/1',distance_m=distance_m,runtime_s=runtime_s,dwell_s=dwell,connected_fraction=fraction,disconnected_dwell_s=disconnected,cars=cars,pack_kwh_per_car=pack_kwh,
        gross_train_mass_if_other_allocations_held_kg=mass,pack_mass_increment_kg_per_car=(pack_kwh-r['reference_pack_kwh'])*1000/p['installed_pack_specific_energy_wh_kg'],
        maximum_rescue_node_spacing_m=post_spacing_m,maximum_unobstructed_towing_reach_m=reach,rescue_node_count_including_endpoints=math.ceil(distance_m/post_spacing_m)+1,
        tow_speed_m_s=speed_m_s,recovery_time_s=time,essential_services_kwh_per_car=essential,incoming_hot_services_kwh_per_car=incoming,
        eol_soc_window_kwh_per_car=usable,available_after_incoming_kwh_per_car=available,battery_margin_kwh_per_car=available-essential,battery_energy_screen_pass=energy_ok,
        working_line_pull_n=pull,winch_input_kw=input_kw,winch_candidate_input_rating_kw=rated_input_kw,
        rope=dict(source_url=r['rope_source_url'],diameter_m=d,minimum_breaking_force_n=r['selected_rope_minimum_breaking_force_n'],termination_efficiency=r['termination_efficiency_assumption'],design_factor=r['rope_design_factor'],
            capacity_after_project_factors_n=rope_capacity,screen_pass=pull<=rope_capacity,shorter_diameter_negative_control_capacity_n=negative_rope,negative_control_pass=pull<=negative_rope,uk_manufacture_confirmed=False,assembly_accepted=False),
        drum=dict(core_diameter_m=core,rope_pack_outer_diameter_m=outer,flange_diameter_m=flange,width_m=width,skin_m=skin,
            shaft_diameter_m=shaft,shaft_length_m=r['shaft_length_m'],holding_design_torque_nm=torque,shaft_shear_pa=shaft_shear,shaft_screen_pass=shaft_shear<=r['shaft_shear_screen_pa']),
        portal=dict(height_m=height,leg_spacing_m=bay,levels=levels,brace_count=4*levels,brace_total_length_m=brace_length,tie_count=levels+1,tie_total_length_m=tie_length,leg_axial_stress_pa=leg_stress,leg_euler_load_n=euler,leg_force_n=leg_force,
            section=section,screen_pass=leg_stress<=r['steel_stress_screen_pa'] and leg_force<=euler),
        anchors=dict(quantity=r['anchor_bolts'],tension_capacity_per_leg_n=anchor_tension_capacity,tension_demand_per_leg_n=anchor_demand,shear_capacity_n=anchor_shear_capacity,shear_demand_n=pull,steel_screen_pass=anchor_tension_capacity>=anchor_demand and anchor_shear_capacity>=pull,concrete_breakout_bond_and_pedestal_accepted=False),
        foundation_cases=foundation,conditional_foundation=selected,qualified_foundation_selection=None,quantities=quantities,cost_rows=cost_rows,
        listed_kit_target_usd=sum(row['amount_usd'] for row in cost_rows),complete_installed_price_usd=None,costs_are_quotes=False,
        numerical_feasible=energy_ok and strength_ok,physical_rescue_accepted=False,
        exclusions=['Road/water/building access and cable deployment','Rope sag, rollers, joints, terminations, drums, braking/gear/bearing fatigue and proof','Independent power duration, evacuation and passenger assistance',
            'Portal connections, pulley reaction eccentricity, lateral/wind/seismic loads and real soils','Larger pack support/gap/thermal/crash and charger qualification'],**FLAGS)


def recovery_cases(c=None,*,distance_m=5000.,runtime_s=300.):
    r=load()['recovery']
    return [recovery(c,distance_m=distance_m,runtime_s=runtime_s,post_spacing_m=min(spacing,distance_m),speed_m_s=speed,pack_kwh=pack)
        for spacing in r['spacing_cases_m'] for speed in r['speeds_m_s'] for pack in r['pack_cases_kwh']]


def definition():
    from . import geometry
    a=load();b=a['booster'];r=a['recovery'];rec=recovery();parts=[];stages=[]
    def add(identity,size,at,material,**kw):parts.append(geometry.part(identity,size,at,material,**kw))
    for side in (-1,1):
        y=side*.4;holes=[]
        for i,x in enumerate((.25,.90,1.60,2.25)):
            holes.append(dict(axis='z',x_m=x,y_m=b['mount_width_m']/2,diameter_m=.018))
            add(f'cassette/face-{side}/bolt-{i}',[.016,.016,.1],[x-.008,y+b['mount_width_m']/2-.008,-.04],'steel',kind='cylinder')
        add(f'cassette/face-{side}/mount-plate',[b['cassette_length_m'],b['mount_width_m'],b['mount_thickness_m']],[0,y,0],'steel',holes=holes)
    stages.append(dict(id='booster-mount-stock',parts=[p['id'] for p in parts]));start=len(parts)
    height=rec['portal']['height_m'];side=r['portal_box_side_m'];pitch=r['portal_leg_spacing_m'];levels=rec['portal']['levels']
    for i,x in enumerate((4.,4.+pitch)):
        add(f'rescue/portal-leg-{i}',[side,side,height],[x,0,0],'steel',kind='tube',axis=2,wall_m=r['portal_wall_m'])
    for i in range(levels+1):
        add(f'rescue/tie-{i}',[pitch+side,side,side],[4.,0,i*height/levels],'steel',kind='tube',axis=0,wall_m=r['portal_wall_m'])
    for i in range(4*levels):
        add(f'rescue/brace-cut-stock-{i}',[math.hypot(height/levels,pitch),r['portal_brace_side_m'],r['portal_brace_side_m']],[8.,i*.13,0.],'steel',kind='tube',axis=0,wall_m=r['portal_brace_wall_m'])
    for leg,x in enumerate((4.,4.+pitch)):
        for i in range(r['anchor_bolts']//2):
            add(f'rescue/anchor-{leg}-{i}',[r['anchor_diameter_m'],r['anchor_diameter_m'],r['anchor_length_m']],[x+(i%4)*.07,-.12+(i//4)*.24,-r['anchor_length_m']+.1],'steel',kind='cylinder')
    # Shaft and flanges are actual material regions; gears, rope, sheaves and
    # winding internals remain a separately counted unmodelled allowance.
    drum=rec['drum'];D=drum['flange_diameter_m'];width=drum['width_m'];shaft=drum['shaft_diameter_m']
    add('rescue/drum-shaft',[shaft,shaft,drum['shaft_length_m']],[4.,2.,1.],'steel',kind='cylinder',cylinder_axis='x')
    core=drum['core_diameter_m']
    add('rescue/drum-barrel',[core,core,width],[4.2+drum['skin_m'],2.+shaft/2-core/2,1.+shaft/2-core/2],'steel',kind='cylinder',cylinder_axis='x',holes=[dict(axis='x',y_m=core/2,z_m=core/2,diameter_m=core-2*drum['skin_m'],length_m=width)])
    for i,x in enumerate((4.2,4.2+width+drum['skin_m'])):
        add(f'rescue/drum-flange-{i}',[D,D,drum['skin_m']],[x,2.+shaft/2-D/2,1.+shaft/2-D/2],'steel',kind='cylinder',cylinder_axis='x',holes=[dict(axis='x',y_m=D/2,z_m=D/2,diameter_m=shaft,length_m=drum['skin_m'])])
    selected=rec['conditional_foundation']
    if selected:add('rescue/foundation',[selected['side_m'],selected['side_m'],selected['depth_m']],[3.,-selected['side_m']/2,-selected['depth_m']],'concrete')
    stages.append(dict(id='rescue-portal-drum-foundation-stock',parts=[p['id'] for p in parts[start:]]))
    d=geometry.finish('OSR-FIXED-BOOSTER-RESCUE-KIT',parts,stages,scope='One2.5mpaired booster mount and partial rescue stock scene; no passenger station or train-routing switch',
        holds=['Untrimmed portal tie/brace/node assembly; no interference authority','No winding/core/cooling, rope, sheaves, bearings, gearbox/brake internals or qualified anchor/soil model'])
    d.update(interference_roles=[],modelled_cg_m=None,complete_kit_modelled=False,**FLAGS);return d


def study():
    return dict(schema='osr-fixed-booster-recovery-study/1',configuration=load(),booster_cases=[takeoff(L) for L in (150.,200.,300.,350.,375.)],
        suburban_5km_300s_recovery_cases=recovery_cases(),selected_policy='Compare independent accessible rescue nodes at≤1km with faster winches or larger services packs; no automatic physical acceptance',
        passenger_junction='Transfers between independent fixed lines only. No train-routing switch or movable guideway.',
        qa=['Serialised material/rope certificates and termination identity','Cassette/anchor datum, preload, insulation and continuity','Proof pull and redundant holding brake','Power-loss and failed winch recovery','Full route access and assisted evacuation rehearsal'],**FLAGS)


def source_paths():
    from . import configuration
    return sorted({Path(__file__),INPUT,ROOT/'engineering/analysis/tests/test_ferrite_maglev_booster_kit.py',
        ROOT/'engineering/ferrite_maglev/model.py',ROOT/'engineering/ferrite_maglev/geometry.py',
        *configuration.source_paths()})

def _encoded(value):return (json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
def _sources():return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in source_paths()}


def publish(output=OUTPUT):
    output=Path(output);before=_sources();r=study();r['source_sha256']=before
    rows=''.join(f'<text x="30" y="{100+i*32}">{row["maximum_rescue_node_spacing_m"]:g}m nodes;{row["tow_speed_m_s"]:g}m/s;{row["pack_kwh_per_car"]:g}kWh: battery margin{row["battery_margin_kwh_per_car"]:.2f}kWh/car; numerical pass={row["numerical_feasible"]}</text>' for i,row in enumerate(r['suburban_5km_300s_recovery_cases']))
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="560"><rect width="1200" height="560" fill="#f1f5f9"/><g font-family="sans-serif" fill="#17394c"><text x="30" y="40" font-size="24">Fixed booster hardware and independently equipped recovery comparisons</text><text x="30" y="70">Declared five-km/300s hot-services case; structural/material/access gates remain open</text>'+rows+'</g></svg>'
    readme=('# Fixed booster and independent rescue kit study\n\n[Quantities, recovery comparisons and QA](result.json.gz) · [Partial material geometry](definition.json) · [Receipt](manifest.json)\n\nPassenger junctions are transfers between independent fixed lines; no physical train routing or switch is inferred. Fixed accelerator modules do not create a passenger station or rescue facility without its independently priced equipment.\n\nRope mass and minimum breaking force use the manufacturer [Bridon6Series table](https://ropes.bekaert.com/au/en/home/products/6-series). Termination efficiency and design factors are project assumptions; no railway rope assembly or UK manufacture is confirmed. Prices are unquoted targets.\n\nComplete active winding/force/thermal design, embedded anchors, portal connections, certified winch/gear/brake/rope assemblies, soils, independent power, located access, evacuation and physical acceptance remain open.\n').encode()
    payload={'result.json.gz':gzip.compress(_encoded(r),mtime=0),'definition.json':_encoded(definition()),'overview.svg':svg.encode(),'README.md':readme}
    if _sources()!=before:raise ValueError('booster kit sources changed')
    if output.is_symlink() or output.exists() and any(p.name not in FILES|{'manifest.json'} or p.is_symlink() or not p.is_file() for p in output.iterdir()):raise ValueError('owned kit packet required')
    output.mkdir(parents=True,exist_ok=True)
    for name,raw in payload.items():(output/name).write_bytes(raw)
    (output/'manifest.json').write_bytes(_encoded(dict(schema='osr-booster-kit-publication/1',source_sha256=before,files_sha256={n:sha256(raw).hexdigest() for n,raw in payload.items()},**FLAGS)))
    return verify(output)


def verify(output=OUTPUT):
    output=Path(output)
    if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()}!=FILES|{'manifest.json'}:raise ValueError('exact kit inventory required')
    for p in output.iterdir():
        if p.is_symlink() or not p.is_file() or p.stat().st_size>MAX:raise ValueError('bounded ordinary kit files required')
    m=json.loads((output/'manifest.json').read_text())
    if m.get('schema')!='osr-booster-kit-publication/1' or m.get('source_sha256')!=_sources() or set(m.get('files_sha256',{}))!=FILES:raise ValueError('kit source or inventory differs')
    if any(sha256((output/name).read_bytes()).hexdigest()!=h for name,h in m['files_sha256'].items()):raise ValueError('kit payload differs')
    with gzip.open(output/'result.json.gz','rb') as stream:raw=stream.read(MAX+1)
    if len(raw)>MAX:raise ValueError('bounded kit result required')
    expected=study();expected['source_sha256']=_sources()
    if json.loads(raw)!=expected or json.loads((output/'definition.json').read_text())!=definition():raise ValueError('kit calculation/definition differs')
    if any(m.get(k) is not False for k in FLAGS):raise ValueError('kit release remains open')
    return m
