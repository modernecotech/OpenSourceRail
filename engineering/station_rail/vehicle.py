"""A wheel-supported 17 m comfort car, with explicit stock and unresolved accounts.

Coordinates are SI; z=0 is top of rail. The retained v0.5 shell is raised to a
1 m floor. New underframe/bogie geometry is a design proposal, not a supplier
model, and no unlocated allowance is used to calculate an installed inertia.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import gzip
import json
import math
import subprocess

from . import ROOT, FLAGS
from .common import brief, identity, source_map

PARENT = 'docs/design-engine/ferrite-maglev/comfort-design/design.json.gz'
PARENT_REVISION = '92e1385e03dcd5c6f76a5b0a9dd5ba348f50d164'
PRODUCER = 'engineering/station_rail/vehicle.py'
ALUMINIUM_DENSITY = 2710.
STEEL_DENSITY = 7850.


def _read_parent(root):
    path = Path(root)/PARENT
    raw = path.read_bytes() if path.is_file() else subprocess.check_output(['git','show',PARENT_REVISION+':'+PARENT], cwd=root)
    # The immutable publication itself binds the compressed design bytes.
    receipt_path=Path(root)/'docs/design-engine/ferrite-maglev/comfort-design/manifest.json'
    receipt_raw=receipt_path.read_bytes() if receipt_path.is_file() else subprocess.check_output(['git','show',PARENT_REVISION+':docs/design-engine/ferrite-maglev/comfort-design/manifest.json'],cwd=root)
    expected=json.loads(receipt_raw)['files_sha256']['design.json.gz']
    if sha256(raw).hexdigest()!=expected:raise ValueError('Retained comfort stock differs from source publication')
    return _parent(raw),expected


@lru_cache(maxsize=2)
def _parent(raw):
    return json.loads(gzip.decompress(raw))['vehicle']


def box(part_id, at, size, density=ALUMINIUM_DENSITY, material='6082-T6-proposed', system='underframe'):
    if min(size)<=0:raise ValueError('Positive physical stock required')
    mass=math.prod(size)*density
    return dict(id=part_id,kind='box',at_m=list(at),size_m=list(size),density_kg_m3=density,
        volume_m3=math.prod(size),mass_kg=mass,material=material,system=system,
        cg_m=[a+s/2 for a,s in zip(at,size)])


def cylinder(part_id, at, radius, length, axis=(0,1,0), inner=0.,system='bogies'):
    if not 0<=inner<radius or length<=0:raise ValueError('Positive annular stock required')
    volume=math.pi*(radius**2-inner**2)*length
    return dict(id=part_id,kind='annular-cylinder' if inner else 'cylinder',at_m=list(at),radius_m=radius,
        inner_radius_m=inner,length_m=length,axis=list(axis),density_kg_m3=STEEL_DENSITY,
        material='steel-reference',system=system,volume_m3=volume,mass_kg=volume*STEEL_DENSITY,
        cg_m=[a+b*length/2 for a,b in zip(at,axis)])


def tube(parts, part_id, at, length, width, depth, wall, along='x',system='underframe'):
    # Four disjoint walls; hollow stock is never represented as solid material.
    sizes=[(length,wall,depth),(length,wall,depth),(length,width-2*wall,wall),(length,width-2*wall,wall)]
    offsets=[(0,0,0),(0,width-wall,0),(0,wall,0),(0,wall,depth-wall)]
    for i,(size,offset) in enumerate(zip(sizes,offsets)):
        if along=='y':size=(size[1],size[0],size[2]);offset=(offset[1],offset[0],offset[2])
        parts.append(box(part_id+'/'+str(i),[a+b for a,b in zip(at,offset)],size,system=system))


def _retained_geometry(parent, floor_height):
    selected=[]
    for old in parent['geometry_parts']:
        prefix=old['id'].split('/')[0]
        keep=(prefix in ('replacement-frame','floor','roof','seat-unit','door','fixed-window','door-window','infill') or
              (prefix=='retained' and old.get('role') in ('panel-side','panel-end','corner-bonds','corner-laps')))
        if not keep or 'replacement-frame/extrusion/frame/lower-stringer' in old['id']:continue
        p=deepcopy(old);p['id']='comfort-shell/'+p['id'];p['kind']=p.get('kind',p.get('primitive','box'));p['system']='body-fitout'
        p['at_m'][2]+=floor_height;p['cg_m'][2]+=floor_height
        if p['kind']=='cylinder':
            p['axis']=p.get('axis',[0,0,1]);p['radius_m']=p.get('radius_m',p.get('diameter_m',0)/2)
        if prefix=='roof' and p.get('density_kg_m3')==60:
            p['material']='Divinycell-HP60-proposed'
        selected.append(p)
    return selected


def running_gear(config):
    parts=[];s=config['support'];r=s['wheel_new_diameter_m']/2; halfg=s['track_gauge_m']/2
    for b,c in enumerate(s['bogie_centres_x_m']):
        for a,dx in enumerate((-s['bogie_wheelbase_m']/2,s['bogie_wheelbase_m']/2)):
            x=c+dx
            parts.append(cylinder(f'bogie/{b}/axle/{a}',(x,-1.,r),.075,2.))
            for side in (-1,1):
                y=side*(halfg+.03)
                parts.append(cylinder(f'bogie/{b}/wheel/{a}/{side}/rim',(x,y-.065,r),r,.13,inner=.26))
                parts.append(cylinder(f'bogie/{b}/wheel/{a}/{side}/web',(x,y-.0125,r),.26,.025,inner=.13))
                parts.append(cylinder(f'bogie/{b}/wheel/{a}/{side}/hub',(x,y-.09,r),.13,.18,inner=.075))
                # Brake-disc stock is on axle, clear of primary winding envelope.
                parts.append(cylinder(f'bogie/{b}/brake/{a}/{side}/disc',(x,side*.38-.018,r),.30,.036,inner=.11))
        for side in (-1,1):
            tube(parts,f'bogie/{b}/sideframe/{side}',(c-1.25,side*.94-.06,.42),2.5,.12,.14,.010,system='bogies')
        tube(parts,f'bogie/{b}/bolster',(c-.16,-.88,.42),1.76,.32,.17,.010,along='y',system='bogies')
    # Tube() uses aluminium; bogie frames are explicitly changed to steel.
    for p in parts:
        if p['kind']=='box':
            p['density_kg_m3']=STEEL_DENSITY;p['mass_kg']=p['volume_m3']*STEEL_DENSITY;p['material']='steel-reference'
    return parts


def underframe(config):
    parts=[]
    # Two deep side sills carry body to two concentrated bogie reactions. Upper
    # retained frame is not credited with global bending stiffness in the screen.
    for side in (-1,1):
        tube(parts,f'wheel-underframe/sill/{side}',(-8.5,side*1.10-.09,.50),17.,.18,.35,.008)
    for b,c in enumerate(config['support']['bogie_centres_x_m']):
        tube(parts,f'wheel-underframe/bolster/{b}',(c-.15,-1.01,.72),2.02,.30,.13,.010,along='y')
        for side in (-1,1):
            parts.append(box(f'wheel-underframe/load-spreader/{b}/{side}',(c-.3,side*1.10-.09,.85),(.6,.18,.015)))
    # Continuous roof chords make the intended body participation explicit.
    # The retained side posts and their joints must transfer shear between the
    # separated chords; a flange-only stiffness calculation is a necessary bound.
    for side in (-1,1):
        tube(parts,f'wheel-underframe/roof-chord/{side}',(-8.5,side*1.13-.06,3.51),17.,.12,.14,.006)
    # Retained floor ribs remain; new overlapping ties are deliberately omitted.
    # Connections from their underside to the deeper sills require new brackets.
    return parts


def secondary(config):
    p=config['propulsion'];length=p['secondary_length_m'];height=p['secondary_height_m'];thick=p['secondary_thickness_m'];bottom=p['secondary_bottom_above_rail_m']
    parts=[box('station-secondary/active-fin',(-length/2,-thick/2,bottom),(length,thick,height),system='passive-secondary')]
    # An elevated spreader is linked by 10 hangers. It adds thermal stock, but
    # no credit is claimed for an unverified transient heat-transfer coefficient.
    parts.append(box('station-secondary/spreader',(-length/2,-.15,.24),(length,.30,.012),system='passive-secondary'))
    for i in range(10):
        x=-4.05+.9*i
        for side in (-1,1):
            parts.append(box(f'station-secondary/hanger/{i}/{side}',(x-.025,side*.06-.006,.252),(.05,.012,.298),system='passive-secondary'))
    for i in range(31):
        parts.append(box(f'station-secondary/heat-fin/{i}',(-length/2,-.145+i*.0094,.195),(length,.0015,.045),system='passive-secondary'))
    return parts


def _section_screen(mass_kg):
    b,h,t=.18,.35,.008
    I=2*(b*h**3-(b-2*t)*(h-2*t)**3)/12
    A=2*(b*h-(b-2*t)*(h-2*t))
    # Symmetric overhung Euler beam under uniformly distributed whole-car load.
    # Applying whole mass is conservative with respect to bogie self-weight;
    # joints, torsion and the stiffness of the shell remain unqualified.
    g=9.80665;L=12.8;overhang=(17.-L)/2;q=mass_kg*g/17
    M_mid=q*(L*L/8-overhang*overhang/2);M_support=-q*overhang*overhang/2
    stress=max(abs(M_mid),abs(M_support))*h/2/I
    # Centre deflection for overhang end moments is reduced by q*a²*L²/(16EI).
    deflection=(5*q*L**4/384-q*overhang**2*L**2/16)/(69e9*I)
    return dict(support_spacing_m=L,uniform_load_N_m=q,section_I_m4=I,section_area_m2=A,
        max_bending_moment_Nm=max(abs(M_mid),abs(M_support)),face_stress_Pa=stress,
        midspan_deflection_m=deflection,stress_limit_Pa_hypothesis=120e6,
        deflection_limit_m_hypothesis=L/500,stress_screen='pass' if stress<=120e6 else 'fail',
        deflection_screen='pass' if deflection<=L/500 else 'fail',
        scope='Two new side sills only; uniform load and ideal supports, no shell stiffness credited. Not a whole-body, joint, buckling, fatigue or crash acceptance.')


def _ideal_body_coupling_screen(mass_kg):
    lower_A=2*(.18*.35-(.18-.016)*(.35-.016))
    upper_A=2*(.12*.14-(.12-.012)*(.14-.012))
    lower_z=.675;upper_z=3.58
    neutral=(lower_A*lower_z+upper_A*upper_z)/(lower_A+upper_A)
    I_lower=2*(.18*.35**3-(.18-.016)*(.35-.016)**3)/12
    I_upper=2*(.12*.14**3-(.12-.012)*(.14-.012)**3)/12
    I=I_lower+I_upper+lower_A*(lower_z-neutral)**2+upper_A*(upper_z-neutral)**2
    sill=_section_screen(mass_kg)
    return dict(ideal_I_m4=I,neutral_axis_m=neutral,
        ideal_midspan_deflection_m=sill['midspan_deflection_m']*sill['section_I_m4']/I,
        maximum_chord_stress_Pa=sill['max_bending_moment_Nm']*max(neutral-.50,3.65-neutral)/I,
        engineering_screen='unknown',shear_transfer_and_joints_demonstrated=False,
        scope='Necessary ideal fully-coupled chord bound only. Side posts, door openings, local buckling, connections and torsion must develop this stiffness in a real structure.')


def build(root=ROOT):
    root=Path(root);config=brief(root);parent,parent_sha=_read_parent(root)
    retained=[deepcopy(r) for r in parent['inventory'] if r['system'] not in ('magnetics','propulsion','protection','hardpoints') and 'replacement-frame/extrusion/frame/lower-stringer' not in r['id']]
    retained_mass=sum(r['mass_kg'] for r in retained)
    parts=_retained_geometry(parent,config['vehicle']['floor_top_above_rail_m'])
    bogie=running_gear(config);frame=underframe(config);fin=secondary(config)
    bogie_material=sum(p['mass_kg'] for p in bogie)
    bogie_account=config['support']['reference_bogie_pair_mass_kg']
    if bogie_material>bogie_account:raise ValueError('Bogie stock exceeds retained reference account; resize or increase the reference explicitly')
    # Service pack is an independent proposal. Its whole installed mass is an
    # explicit allowance until cell/case/cooling/mounts are all located.
    battery_mass=1345.
    battery_basis='1345kg service-pack account:75Type3-20 modules1050kg plus295kg enclosure, BMS, cooling, DC/DC, contactors, wiring and mounts; supplier freeze and complete placement open'
    try:
        from .electrical import battery_definition
        battery=battery_definition(root)
        battery_mass=battery['mass_kg'];battery_basis=battery
    except ImportError:
        battery=None
    coating_mass=17*2.65*.0008*1326.56
    inventory=[dict(id='retained-comfort/'+system,evidence_class='mixed-counted-stock-and-retained-account',mass_kg=sum(r['mass_kg'] for r in retained if r['system']==system),
        system=system,basis='Source-bound comfort stock excluding every magnetic, old propulsion, old hardpoint and old capture occurrence; body and service residuals are still unresolved') for system in sorted({r['system'] for r in retained})]
    for label,stock in (('wheel-underframe',frame),('passive-secondary',fin)):
        inventory.append(dict(id=label,system=label,evidence_class='located-proposed-material',mass_kg=sum(p['mass_kg'] for p in stock),parts=len(stock)))
    inventory += [dict(id='passive-bogie-pair',system='bogies',evidence_class='reference-account-with-partial-proposed-material',mass_kg=bogie_account,
        located_stock_kg=bogie_material,unlocated_remainder_kg=bogie_account-bogie_material,basis='v0.4 two-bogie category includes wheels, frames, suspension and brakes; no traction motor or gear credited'),
        dict(id='service-battery',system='services',evidence_class='supplier-cell-and-installed-pack-account',mass_kg=battery_mass,basis=battery_basis),
        dict(id='white-roof-finish',system='roof-thermal',evidence_class='counted-coating-stock',mass_kg=coating_mass,thickness_m=.0008,density_kg_m3=1326.56),
        dict(id='new-frame-joints-and-fin-retention',system='attachments',evidence_class='explicit-unlocated-allocation',mass_kg=180.,basis='New bogie-pivot/secondary suspension/body joints, fin positive-retention and flexible thermal joints; not counted as already located material')]
    mass=sum(r['mass_kg'] for r in inventory)
    definition=dict(schema='osr-station-rail-physical/1',revision=config['revision'],vehicle=config['vehicle'],support=config['support'],propulsion=config['propulsion'],
        source_body_candidate_id=parent['body_candidate_id'],body_retained_mass_kg=retained_mass,
        roof=dict(core='Divinycell-HP60-proposed',core_density_kg_m3=60.,core_continuous_temperature_reference_C=80.,white_finish_kg=coating_mass,
            manufacturer_url='https://www.diabgroup.com/media/juzhmx0h/diab-divinycell-hp-april-2022-rev26-imp.pdf',hot_loaded_structure_qualified=False),
        equipment_inventory=inventory,geometry_definition_id=identity(parts+bogie+frame+fin))
    body_id=identity(dict(body=definition['source_body_candidate_id'],floor_height_m=1.,frame=frame,roof=definition['roof']))
    support_id=identity(dict(support=config['support'],stock=bogie,accounted_mass_kg=bogie_account))
    propulsion_id=identity(dict(propulsion=config['propulsion'],stock=fin))
    candidate=identity(dict(physical_definition=definition,body_candidate_id=body_id,support_component_id=support_id,propulsion_component_id=propulsion_id))
    axle_bottom=config['support']['wheel_new_diameter_m']/2-.075
    primary_top=.20
    min_x=min(abs(c)-config['support']['bogie_wheelbase_m']/2 for c in config['support']['bogie_centres_x_m'])
    sources=source_map(ROOT,(PRODUCER,));sources[PARENT]=parent_sha
    allparts=parts+bogie+frame+fin
    located_mass=sum(p['mass_kg'] for p in allparts)
    cg=[sum(p['mass_kg']*p['cg_m'][i] for p in allparts)/located_mass for i in range(3)]
    value=dict(schema='osr-station-rail-vehicle/1',candidate_id=candidate,body_candidate_id=body_id,support_component_id=support_id,propulsion_component_id=propulsion_id,
        physical_definition=definition,inventory=inventory,geometry_parts=allparts,seating_layout=deepcopy(parent['seating_layout']),
        mass=dict(accounted_tare_kg_per_car=mass,accounted_cap_loaded_kg_per_car=mass+46*75,
            accounted_160_control_kg_per_car=mass+160*75,accounted_tare_kg_six_cars=mass*6,
            installed_tare_kg_per_car=None,installed_loaded_kg_per_car=None,CG_m=None,inertia_kg_m2=None,
            located_material_kg=located_mass,located_material_CG_m=cg,unlocated_or_reference_account_kg=mass-located_mass,
            old_maglev_accounted_tare_kg_per_car=parent['mass']['accounted_tare_kg_per_car'],
            v04_traction_removed_arithmetic_kg_per_car=23680.,mass_change_from_v04_arithmetic_kg_per_car=mass-23680.),
        propulsion=dict(secondary_aluminium_mass_kg=sum(p['mass_kg'] for p in fin),active_fin_aluminium_mass_kg=fin[0]['mass_kg'],
            accounted_mass_kg=sum(p['mass_kg'] for p in fin),installed_accounted_mass_kg=sum(p['mass_kg'] for p in fin),station_primary_geometry_qualified=False),
        support_counts=dict(bogies_per_car=2,axles_per_car=4,wheels_per_car=8,bogies_per_train=12,axles_per_train=24,wheels_per_train=48),
        axle_loads=dict(empty_kg_per_axle=mass/4,normal_kg_per_axle=(mass+3450)/4,crowd_control_kg_per_axle=(mass+12000)/4,
            basis='Symmetric four-axle static averages; longitudinal, roll, unequal passenger and dynamic wheel loads remain open'),
        clearance=dict(fin_to_nearest_axle_x_m=min_x-config['propulsion']['secondary_length_m']/2,
            axle_bottom_above_station_primary_top_m=axle_bottom-primary_top,station_primary_top_above_rail_m=primary_top,
            floor_underside_m=min(p['at_m'][2] for p in parts if p['id'].startswith('comfort-shell/floor/')),
            wheel_top_m=.76,nominal_station_side_gap_m=.015,
            nominal_necessary_screen='pass' if min_x>4.5 and axle_bottom>primary_top else 'fail',
            swept_curves_suspension_travel_wheel_wear_and_turnouts_qualified=False),
        underframe_screens={name:_section_screen(m) for name,m in [('empty',mass),('normal',mass+3450),('crowd_control',mass+12000)]},
        ideal_body_coupling_screens={name:_ideal_body_coupling_screen(m) for name,m in [('empty',mass),('normal',mass+3450),('crowd_control',mass+12000)]},
        assembly_plan=[dict(operation='Factory body and equipment assembly',fixed_floor_datum_m=1.,supplier_interfaces_frozen=False),
            dict(operation='Roll passive bogies under supported car, lower body onto suspension/centre bearings, set ride height',jacks_and_lifting_tools_qualified=False),
            dict(operation='Install bolted passive fin cassette between bogies and set station clearance using surveyed datum',sweep_and_thermal_joint_verified=False)],
        missing_inventory=['Supplier bogies/suspension/brake/WSP detail and complete drawings','Unallocated body/services and interior residuals','Complete service-pack enclosure/cooling and installation','Bogie pivots and new underframe joints/fatigue','Fin expansion joints, crosswind and swept-station clearance','Couplers, buffers, emergency access and rescue qualification'],
        source_sha256=sources,**FLAGS)
    for row in value['inventory']:
        row['part_id']=row['id'];row['subsystem']=row['system']
    value['body_candidate_ancestry']={'retained_parent_body_candidate_id':parent['body_candidate_id'],'new_support_loadpath_requires_new_body_candidate':True}
    value['service_pack_fit']={'state':'unknown','reason':'Single central pack envelope intersects passive-fin hangers/floor ties; split-cassette routing, mounts and removal require design before installed mass properties can be claimed'}
    value['evaluation_id']=identity(value)
    return value
