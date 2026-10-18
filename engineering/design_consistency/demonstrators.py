"""Four research arrangements compiled from one dimensional contract."""
from copy import deepcopy
import math
from osr_mech.engineering_definition import fingerprint
from osr_mech.rolling_stock import composite_panels as panel
from .contracts import box,part,member,validate,summary


def materials():
    return dict(fastener=dict(density_kg_m3=7850,young_pa=210e9,poisson=.3,basis='class 8.8 dimensional design seed; supplier lot, preload and strength acceptance open'),steel=dict(density_kg_m3=7850,young_pa=210e9,poisson=.3,yield_pa=355e6,basis='S355 design seed; heat/certificates not supplied'),
        concrete=dict(density_kg_m3=2500,young_pa=30e9,poisson=.2,compressive_strength_pa=40e6,basis='C40 research seed; mix, curing and cyclic data uncalibrated'),
        gfrp=dict(density_kg_m3=1800,young_pa=20e9,poisson=.25,basis='development laminate; allowables unmeasured'),
        foam=dict(density_kg_m3=80,young_pa=90e6,shear_pa=27e6,poisson=.4,basis='H80 public nominal data at 23 C; project batch unqualified'),
        adhesive=dict(density_kg_m3=1200,young_pa=2e9,poisson=.3,basis='research bond elastic seed; peel/fatigue/creep unmeasured'),
        finish=dict(density_kg_m3=1400,young_pa=1e9,poisson=.3,basis='research finish; complete-stack fire response unknown'))


def contract(name,parts,mats,*,joints=None,stages=None):
    value=dict(schema='osr-engineering-representations/1',revision='DESIGN-CONSISTENCY-1',name=name,parts=parts,materials=mats,
        assembly_joints=joints or [],construction_stages=stages or [],
        mandatory_evidence=['supplier dimensions and certificates','independent strength/fatigue/stability review',
            'measured joint laws','issued drawings and procedures','prototype correlation','physical release'],
        physical_validation=False,production_released=False)
    validate(value);return value


def panel_bay(config,*,span=1,grade_density=80,crown=0,aperture=True,skin=.0015,core=.0246,ply_angles=None):
    c=deepcopy(config);c['core'].update(panel.coupled_core(c,grade_density))
    width=c['panel']['width_m'];height=c['panel']['roof_chord_m'] if crown else c['panel']['side_height_m']
    arc=panel.roof_arc(height,crown);length=arc['arc_length_m'];land=c['panel']['edge_land_m']
    holes=[(.28,1.1,.71,2.25)]if aperture and not crown else []
    network=panel.support_network(c,width,length,span,holes=holes)
    # Trimmed apertures have their own perimeter support frame. The nominal
    # strip remains a screening bound; aperture edge/contact response is open.
    mats=materials();mats['foam'].update(density_kg_m3=grade_density,young_pa=c['core']['young_pa'],shear_pa=c['core']['shear_pa'],
        basis=c['core']['grade']+' public normal/shear properties; project batch and constitutive calibration open',source=c['core']['source'])
    mats['gfrp'].update({k:v for k,v in c['glass'].items()if k in ('density_kg_m3','e1_pa','e2_pa','g12_pa','poisson12')})
    mats['adhesive']['density_kg_m3']=c['bond']['density_kg_m3'];mats['finish']['density_kg_m3']=c['finish']['density_kg_m3']
    panel.positive(skin,'skin');panel.positive(core,'core')
    bond=c['bond']['thickness_m_each'];depth=2*skin+core+2*bond;parts=[]
    if ply_angles is not None and (not isinstance(ply_angles,(list,tuple)) or not 1<=len(ply_angles)<=32 or
            any(type(angle) not in (int,float) or angle not in (-90,-45,0,45,90) for angle in ply_angles)):
        raise ValueError('bounded explicit ply orientation schedule required')
    plies=panel.balanced_skin(skin) if ply_angles is None else tuple(panel.Ply(skin/len(ply_angles),angle) for angle in ply_angles)
    skin_rects=panel.remaining_rectangles(width,length,holes)
    edges=[(0,0,width,land),(0,length-land,width,length),(0,land,land,length-land),(width-land,land,width,length-land)]
    foam_rects=panel.remaining_rectangles(width,length,edges+[(a-land,b-land,z+land,d+land)for a,b,z,d in holes])
    solid_rects=panel.remaining_rectangles(width,length,foam_rects+holes)
    sites=network['panel_attachment_sites_m']
    mats['potting']=dict(density_kg_m3=c['hardware']['potting_density_kg_m3'],young_pa=2e9,poisson=.3,basis='unqualified insert potting seed')
    def contained(rect,radius):
        a,b,d,e=rect
        return [[x-(a+d)/2,y-(b+e)/2]for x,y in sites if a+radius<x<d-radius and b+radius<y<e-radius]
    def layer(identity,material,rect,lower,upper):
        a,b,d,e=rect
        if crown:
            primitive=dict(id=identity,kind='curved-layer',centre_m=[(a+d)/2,0,crown-arc['radius_m']],
                length_m=d-a,radius_m=arc['radius_m'],theta_start=(b-length/2)/arc['radius_m'],theta_end=(e-length/2)/arc['radius_m'],z_lower_m=lower,z_upper_m=upper)
        else:
            primitive=box(identity,d-a,e-b,upper-lower,[(a+d)/2,(b+e)/2,(lower+upper)/2])
            radius=c['panel']['potting_radius_m']if material=='foam'else .00325
            holes_local=contained(rect,radius)if material=='foam' or upper<=-core/2 else []
            if holes_local:primitive.update(kind='perforated-plate',holes_xy_m=holes_local,hole_radius_m=radius)
        parts.append(part(identity,material,dict(role=identity,primitives=[primitive]),mats,
            limits={'minimum_wall_m':.00015,'tolerance_m':None},inspections=['ply angle/thickness','trim and edge land','bond continuity']))
    for side,z0 in [('inner',-depth/2),('outer',core/2+bond)]:
        for i,ply in enumerate(plies if side=='inner' else tuple(reversed(plies))):
            for j,rect in enumerate(skin_rects):
                layer(f'{side}-ply-{i}-{j}','gfrp',rect,z0,z0+ply.thickness_m)
                parts[-1]['laminate_ply']=dict(angle_deg=ply.angle_deg,thickness_m=ply.thickness_m,frame='module x and developed surface tangent')
            z0+=ply.thickness_m
    for j,z0 in enumerate([-core/2-bond,core/2]):
        for k,rect in enumerate(skin_rects):layer(f'bond-{j}-{k}','adhesive',rect,z0,z0+bond)
    for i,rect in enumerate(foam_rects):layer(f'core-{i}','foam',rect,-core/2,core/2)
    for i,rect in enumerate(solid_rects):layer(f'solid-land-{i}','gfrp',rect,-core/2,core/2)
    for i,rect in enumerate(skin_rects):layer(f'finish-{i}','finish',rect,depth/2,depth/2+c['finish']['thickness_m'])
    for rail in network['rails']:
        spec=deepcopy(rail['geometry']);placement=None
        if crown:
            theta=(rail['station_m']-length/2)/arc['radius_m'];r=arc['radius_m']-.045
            for primitive in spec['primitives']:
                primitive['centre_m'][1]-=rail['station_m'];primitive['centre_m'][2]+=.045
            placement=dict(translation_m=[0,r*math.sin(theta),r*math.cos(theta)-arc['radius_m']+crown],
                rotation=[[1,0,0],[0,math.cos(theta),math.sin(theta)],[0,-math.sin(theta),math.cos(theta)]])
        parts.append(part(rail['id'],'steel',spec,mats,section=network['section'],placement=placement,inspections=['wall thickness','bracket and insert fit']))
    # Potted flat inserts replace foam, with a real bore and drilled inner skin.
    # Roof inserts need curved contact lands; their status stays unknown.
    if not crown:
        for i,(x,y)in enumerate(sites):
            for name,material,outer,inner in [('potting','potting',c['panel']['potting_radius_m'],c['panel']['insert_radius_m']),('insert','steel',c['panel']['insert_radius_m'],.00325)]:
                primitive=dict(id=name,kind='tube',centre_m=[x,y,0],radius_m=outer,inner_radius_m=inner,length_m=core,axis='z')
                parts.append(part(f'{name}-{i}',material,dict(role='potted insert material region',primitives=[primitive]),mats))
    for rail in network['rails']:
        a,b=rail['interval_m'];y=rail['station_m'];theta=(y-length/2)/arc['radius_m']if crown else 0
        rotation=[[1,0,0],[0,math.cos(theta),math.sin(theta)],[0,-math.sin(theta),math.cos(theta)]]
        placement=dict(translation_m=[0,arc['radius_m']*math.sin(theta),(arc['radius_m']*math.cos(theta)-arc['radius_m']+crown)]if crown else[0,0,0],rotation=rotation)
        rail_part=next(p for p in parts if p['id']==rail['id'])
        local_sites=[a+(b-a)*f for f in (.2,.8)]
        top=rail_part['manufacturing']['primitives'][0]
        top.update(kind='plate',holes_xy_m=[[x-(a+b)/2,0]for x in local_sites],hole_radius_m=.00325)
        rail_part_new=part(rail_part['id'],'steel',rail_part['manufacturing'],mats,section=network['section'],placement=rail_part['placement'])
        parts[parts.index(rail_part)]=rail_part_new
        for j,x in enumerate(local_sites):
            yy=0 if crown else y
            clip_top=-depth/2-.0001;clip_bottom=-.035
            clip=dict(id='clip',kind='plate',centre_m=[x,yy,(clip_top+clip_bottom)/2],dimensions_m=[.04,.018,clip_top-clip_bottom],holes_xy_m=[[0,0]],hole_radius_m=.00325)
            parts.append(part(f'{rail["id"]}-clip-{j}','steel',dict(role='proposed clip; curved pad/contact open',primitives=[clip]),mats,placement=placement))
            bolt_top=-core/2+.0043;bolt_bottom=-.043
            bolt=dict(id='bolt',kind='cylinder',centre_m=[x,yy,(bolt_top+bolt_bottom)/2],radius_m=.003,length_m=bolt_top-bolt_bottom if not crown else .015,axis='z')
            if crown:bolt['centre_m'][2]=-.039
            parts.append(part(f'{rail["id"]}-clip-bolt-{j}','fastener',dict(role='M6 shank; supplier head/thread configuration open',primitives=[bolt]),mats,placement=placement))
        # Two drilled bracket ears and four complete dimensional fasteners per rail.
        for j,x in enumerate([a-.02,b+.02]):
            yy=0 if crown else y
            bracket=dict(id='ear',kind='plate',centre_m=[x,yy,-.045],dimensions_m=[.04,.04,.0064],holes_xy_m=[[-.01,0],[.01,0]],hole_radius_m=.00325)
            parts.append(part(f'{rail["id"]}-bracket-{j}','steel',dict(role='frame bracket ear; weld/access to vehicle frame open',primitives=[bracket]),mats,placement=placement))
            for k,dx in enumerate([-.01,.01]):
                centre=[x+dx,yy,-.045]
                specs=[dict(id='shank',kind='cylinder',centre_m=centre,radius_m=.003,length_m=.025,axis='z'),
                    dict(id='head',kind='cylinder',centre_m=[x+dx,yy,-.0595],radius_m=.005,length_m=.004,axis='z'),
                    dict(id='nut',kind='tube',centre_m=[x+dx,yy,-.031],radius_m=.005,inner_radius_m=.00325,length_m=.005,axis='z')]
                parts.append(part(f'{rail["id"]}-fastener-{j}-{k}','fastener',dict(role='M6 dimensional fastener assembly; threads simplified',primitives=specs),mats,placement=placement))
    # Aperture frame is offset behind transverse rails, with explicit weld/contact gaps.
    for i,(a,b,d,e)in enumerate(holes):
        for side,x in enumerate([a-.035,d+.035]):
            parts.append(part(f'aperture-post-{i}-{side}','steel',dict(role='aperture support; connecting weld open',primitives=[box('post',.025,e-b+.07,.02,[x,(b+e)/2,-.065])]),mats))
        for side,y in enumerate([b-.035,e+.035]):
            parts.append(part(f'aperture-lintel-{i}-{side}','steel',dict(role='aperture perimeter support; connecting weld open',primitives=[box('lintel',d-a+.045,.025,.02,[(a+d)/2,y,-.065])]),mats))
    result=contract('clipped GFRP roof bay'if crown else'clipped GFRP side bay',parts,mats)
    result['unresolved_part_allocations']=['perimeter seal profile','secondary retention geometry','locking/thread details','local frame weld/contact details']+(['curved insert/contact lands']if crown else[])
    result.update(panel_parameters=dict(width_m=width,height_m=height,skin_m=skin,core_m=core,crown_m=crown,holes=holes),
        core_grade=c['core'],support_network=network,attachment_definition_status='insert/clip local contact and pull-out qualification open',
        thermal_status='failed'if crown and c['screen']['hot_roof_temperature_c']>c['core']['continuous_max_temperature_c']else'unknown',
        ply_schedule=[dict(thickness_m=p.thickness_m,angle_deg=p.angle_deg) for p in plies],
        response=panel.strip_response(panel.laminate_abd(plies,core,bond,c['glass']),c['screen']['pressure_pa'],span,core,c['core']['shear_pa']))
    return result


def interface():
    mats=materials();parts=[]
    for side,y in enumerate([-.45,.45]):
        parts.append(member(f'sill-{side}',2,.16,.28,.008,'steel',mats,(0,y,0),inspections=['section wall','weld NDT','mount datum']))
    for sill in parts:
        top=sill['manufacturing']['primitives'][0]
        top.update(kind='plate',holes_xy_m=[[x,0]for x in [-.9,-.6,.6,.9]],hole_radius_m=.007)
        parts[parts.index(sill)]=part(sill['id'],'steel',sill['manufacturing'],mats,section=sill['analysis']['section'])
    for end,x in enumerate([-.75,.75]):
        # Transverse plate bridge has real fastener holes and net volume.
        holes=[[-.15,-.45],[-.15,.45],[.15,-.45],[.15,.45]]
        spec=dict(role='bolster interface',primitives=[dict(id='plate',kind='plate',centre_m=[x,0,.148],dimensions_m=[.5,1.2,.016],holes_xy_m=holes,hole_radius_m=.007)])
        parts.append(part(f'bolster-plate-{end}','steel',spec,mats,inspections=['hole position','flatness','net ligament']))
        for i,(a,b)in enumerate(holes):
            bolt=dict(id='bolt',kind='cylinder',centre_m=[x+a,b,.144],radius_m=.006,length_m=.04,axis='z')
            head=dict(id='head',kind='cylinder',centre_m=[x+a,b,.1675],radius_m=.01,length_m=.007,axis='z')
            nut=dict(id='nut',kind='tube',centre_m=[x+a,b,.128],radius_m=.01,inner_radius_m=.007,length_m=.008,axis='z')
            parts.append(part(f'bolt-{end}-{i}','fastener',dict(role='M12 simplified shank/head/nut; threads not modelled',primitives=[bolt,head,nut]),mats,inspections=['bolt traceability','preload verification']))
    for i,y in enumerate([-.22,.22]):
        parts.append(member(f'battery-carrier-{i}',1.2,.08,.05,.003,'steel',mats,(0,y,-.19)))
    joint=dict(id='bogie-underframe-mount',kind='bolted',hole_pattern_m=[[-.15,-.45,0],[-.15,.45,0],[.15,-.45,0],[.15,.45,0]],
        grip_stack_m=[.016,.008],fastener_specification='M12 class 8.8 design seed; supplier/configuration unselected',
        clearance_m=.001,preload_range_n=[30000,42000],locking='provisional prevailing-torque nut plus witnessed preload',
        contact_surfaces='machined steel pad; assumed friction .15, surface calibration required',
        member_thickness_m=.016,bolt_tensile_area_m2=84.3e-6,weld_size_m=.006,
        manufacturing_limits={'hole_position_tolerance_m':.0002,'contact_flatness_m':.0001},
        inspection_characteristics=['preload','locking witness','surface condition','weld NDT','fatigue-critical toes'],
        instance_groups=[dict(id=f'mount-{end}',physical_part_ids=[f'bolster-plate-{end}','sill-0','sill-1',*[f'bolt-{end}-{i}'for i in range(4)]])for end in range(2)],
        material_evidence=None,production_released=False)
    result=contract('bogie-underframe interface',parts,mats,joints=[joint])
    result['unresolved_part_allocations']=['equipment supplier kit','fluids and cable inventory','carrier connecting brackets','weld preparations and thread locking details']
    result['equipment_distribution']=dict(battery_mass_kg=None,supplier_cg_m=None,supplier_inertia_kg_m2=None,fluid_inventory_kg=None,whole_vehicle_modal_transfer_accepted=False)
    result['suspension_law']=dict(displacement_m=[-.04,0,.04],force_n=[-80000,0,80000],velocity_m_s=[-1,0,1],damping_force_n=[-20000,0,20000],basis='design curve, not supplier/test calibration')
    return result


def viaduct(*,length=20,pier_height=8,pile_length=15,pile_spacing=2):
    mats=materials();mats['elastomer']=dict(density_kg_m3=1100,young_pa=10e6,poisson=.45,basis='unmeasured bearing design seed')
    parts=[];deck_bottom=pier_height+.5
    # Longitudinal reinforcing bars and two straight ducts displace concrete.
    from osr_mech.section_contract import rhs
    sec=rhs(2.9,1.155,.15,density_kg_m3=2500);wall=.15;h=1.155;w=2.9;regions=[];bars=[]
    for face,z in [('top',(h-wall)/2),('bottom',-(h-wall)/2)]:
        ys=[-.95,-.45,0,.45,.95];holes=[[y,0]for y in ys]
        # One hole radius per primitive keeps net-volume/inertia integration exact.
        regions.append(dict(id=face,kind='plate',centre_m=[0,z,0],dimensions_m=[w,wall,length],holes_xy_m=holes,hole_radius_m=.01))
        bars.extend((y,z)for y in ys)
    for face,y in [('left',-(w-wall)/2),('right',(w-wall)/2)]:
        zs=[-.3,0,.3];regions.append(dict(id=face,kind='plate',centre_m=[y,0,0],dimensions_m=[wall,h-2*wall,length],holes_xy_m=[[0,z]for z in zs],hole_radius_m=.01));bars.extend((y,z)for z in zs)
    placement=dict(translation_m=[length/2,0,deck_bottom+h/2],rotation=[[0,0,1],[1,0,0],[0,1,0]])
    # Section record is the gross outer shape; local bar/duct response is explicit
    # unresolved reinforcement analysis, never a homogenised capacity assertion.
    parts.append(part('deck','concrete',dict(role='deck matrix with longitudinal bar regions removed',primitives=regions),mats,section=sec,placement=placement))
    for i,(y,z)in enumerate(bars):
        bar=dict(id='bar',kind='cylinder',centre_m=[length/2,y,deck_bottom+h/2+z],radius_m=.01,length_m=length,axis='x')
        parts.append(part(f'deck-rebar-{i}','steel',dict(role='longitudinal research reinforcement; transverse cage/anchorage open',primitives=[bar]),mats))
    for end,x in enumerate([0,length]):
        local=member(f'pier-{end}',pier_height,1.2,1.0,.2,'concrete',mats)
        placement=dict(translation_m=[x,0,pier_height/2],rotation=[[0,0,1],[0,1,0],[-1,0,0]])
        parts.append(part(local['id'],'concrete',local['manufacturing'],mats,section=local['analysis']['section'],placement=placement))
        parts.append(part(f'pier-cap-{end}','concrete',dict(role='pier cap',primitives=[box('cap',.8,2.9,.4,[x,0,pier_height+.2])]),mats))
        cap_width=pile_spacing+.8;cap_depth=.8
        parts.append(part(f'foundation-cap-{end}','concrete',dict(role='pile cap',primitives=[box('cap',cap_width,cap_width,cap_depth,[x,0,-cap_depth/2])]),mats))
        for i,(dx,y)in enumerate([(-pile_spacing/2,-pile_spacing/2),(-pile_spacing/2,pile_spacing/2),(pile_spacing/2,-pile_spacing/2),(pile_spacing/2,pile_spacing/2)]):
            # Embedded longitudinal bars replace concrete; no double-counted material.
            holes=[[.3*math.cos(angle),.3*math.sin(angle)]for angle in [0,math.pi/2,math.pi,3*math.pi/2]]
            matrix=dict(id='pile',kind='perforated-cylinder',centre_m=[x+dx,y,-cap_depth-pile_length/2],radius_m=.4,length_m=pile_length,axis='z',holes_xy_m=holes,hole_radius_m=.01)
            parts.append(part(f'pile-{end}-{i}','concrete',dict(role='pile matrix minus four bar regions',primitives=[matrix]),mats))
            for j,(hx,hy)in enumerate(holes):
                bar=dict(id='bar',kind='cylinder',centre_m=[x+dx+hx,y+hy,-cap_depth-pile_length/2],radius_m=.01,length_m=pile_length,axis='z')
                parts.append(part(f'pile-{end}-{i}-rebar-{j}','steel',dict(role='embedded research longitudinal bar; transverse cage/bond/cap anchorage open',primitives=[bar]),mats))
        for i,y in enumerate([-.7,.7]):
            for j,z in enumerate([pier_height+.41,pier_height+.49]):
                parts.append(part(f'bearing-plate-{end}-{i}-{j}','steel',dict(role='bearing plate',primitives=[box('plate',.4,.35,.02,[x,y,z])]),mats))
            parts.append(part(f'bearing-core-{end}-{i}','elastomer',dict(role='bearing body',primitives=[box('core',.3,.25,.06,[x,y,pier_height+.45])]),mats))
    # Tendon reservations are separate, with anchorage and prestress losses open.
    for i,y in enumerate([-.7,.7]):
        strand=dict(id='strand',kind='cylinder',centre_m=[length/2,y,deck_bottom+.3],radius_m=.015,length_m=length,axis='x')
        parts.append(part(f'tendon-{i}','steel',dict(role='straight tendon inside deck void; deviators/anchorage open',primitives=[strand]),mats))
    stages=[dict(id='lifting',parts=['deck'],supports=[{'position_m':[length*.2,0,0]},{'position_m':[length*.8,0,0]}],loads=[{'kind':'gravity','dynamic_factor':1.3}],open_evidence=['crane chart','lifting inserts','lateral restraint']),
        dict(id='service',parts=[p['id']for p in parts],supports=[{'kind':'two four-pile groups','calibrated':False}],loads=[{'kind':'two-track train','source':'LM3 planning reference','accepted':False}],open_evidence=['soil layers','axle distribution','bearing law','cyclic resistance']),
        dict(id='bearing-replacement',parts=['deck'],supports=[{'kind':'synchronized jacks','position_m':[0,0,pier_height+.5]},{'kind':'remaining support','position_m':[length,0,pier_height+.5]}],loads=[{'kind':'gravity'}],open_evidence=['jack chart','local deck capacity','stability'])]
    result=contract('viaduct research bay',parts,mats,stages=stages)
    result['unresolved_part_allocations']=['transverse deck/pile cages','pier and cap reinforcement','tendon duct/anchor/deviator assembly','grout and bearing connection details']
    return result


def front(bay,*,span_count=4,truck_payload_kg=40000,crane_capacity_kg=80000):
    from .contracts import summary
    if type(span_count)is not int or span_count<1 or min(truck_payload_kg,crane_capacity_kg)<=0:raise ValueError('positive front/equipment configuration required')
    assembly=[p for p in bay['parts']if p['id']=='deck'or p['id'].startswith(('deck-rebar-','tendon-'))]
    mass=sum(p['properties']['mass_kg']for p in assembly);lifts=[];tasks=[]
    # Declared calendar: one mould held for seven curing days, one shared truck,
    # one erection crew/crane. Durations are research seeds, not tender commitments.
    for i in range(span_count):
        start=8*i
        tasks.extend([dict(id=f'cast-{i}',start_day=start,end_day=start+1,resources=['mould-1','casting-crew']),
            dict(id=f'cure-{i}',start_day=start+1,end_day=start+7,resources=['mould-1']),
            dict(id=f'transport-{i}',start_day=start+7,end_day=start+8,resources=['truck-1','transport-crew']),
            dict(id=f'erect-{i}',start_day=start+8,end_day=start+9,resources=['crane-1','erection-crew'])])
        lifts.append(dict(id=f'span-{i}',working_day=start+8,mass_kg=mass,rigging_mass_kg=1000,suspended_mass_kg=mass+1000,
            physical_part_ids=[p['id']for p in assembly],transport_eligible=mass<=truck_payload_kg,
            lifting_eligible=1.3*(mass+1000)<=crane_capacity_kg,crane_configuration_accepted=False))
    for i,task in enumerate(tasks):
        for other in tasks[i+1:]:
            if set(task['resources'])&set(other['resources']) and max(task['start_day'],other['start_day'])<min(task['end_day'],other['end_day']):raise ValueError('resource calendar conflict')
    return dict(schema='osr-repeatable-construction-front/1',revision='RESEARCH-1',physical_bay_sha256=fingerprint(bay),
        lifts=lifts,schedule_status='blocked'if any(not r['transport_eligible']or not r['lifting_eligible']for r in lifts)else'unknown',resource_schedule=tasks,
        schedule_basis='proposed seven-day mould hold and one-day transport/erection; strength, access and weather uncalibrated',
        truck_payload_kg=truck_payload_kg,crane_capacity_kg=crane_capacity_kg,
        temporary_stability_accepted=False,quoted_installed_cost_usd=None,production_released=False,physical_validation=False)
