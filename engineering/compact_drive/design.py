"""Counted new compact-drive body; no legacy producer or receipt is changed."""
from copy import deepcopy
from math import prod,pi,sin,cos,fsum,sqrt
from engineering.vehicle_installation import model
from . import ROOT,FLAGS,PARENT
from .common import parent as load_parent,policy,vendor,sources,seal,validate
from .gears import train

KEEP_POWERED={'powered-bogie/side-rhs','powered-bogie/transom-rhs','powered-bogie/end-tie'}
RY=[[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]]
RNEG=[[0.,1.,0.],[-1.,0.,0.],[0.,0.,1.]]


def stock_volume(s):
    if s['kind']=='box':return prod(s['size_m'])
    if s['kind']=='rhs':return s['length_m']*(s['width_m']*s['depth_m']-(s['width_m']-2*s['wall_m'])*(s['depth_m']-2*s['wall_m']))
    if s['kind'] in ('cylinder','annulus'):return pi*(s.get('radius_m',s.get('outer_radius_m'))**2-s.get('inner_radius_m',0.)**2)*s['length_m']
    raise ValueError('Uncounted stock shape')


def build(parent=None,config_id='compact-737-h100',*,root=ROOT):
    p=policy(root);v=vendor(root);before=sources(root);old=deepcopy(parent or load_parent(root))
    if old['candidate_id']!=PARENT:raise ValueError('Exact powered-body ancestry required')
    validate(old);config=next((c for c in p['configs'] if c['id']==config_id),None)
    if config is None:raise ValueError('Outside three-config contract')
    lift=config['body_lift_m'];gear=train(config);result=deepcopy(old)
    pol=result['policy'];pol['layout']['floor_top_m']+=lift;pol['layout']['roof_z_m']+=lift
    # Old reference drive additions lived outside this BOM. They are explicitly
    # superseded, never silently retained or subtracted from unrelated reserves.
    removed={r['id'] for r in old['parts'] if r['id'].startswith('powered-bogie/') and r['id'] not in KEEP_POWERED}
    welds={r['id'] for r in old['parts'] if r['id']=='underframe/girder-weld-deposit'}
    removed|=welds
    parts=[deepcopy(r) for r in old['parts'] if r['id'] not in removed]
    bypart={r['id']:r for r in parts};patterns=[];changes=[];entities=[]
    for pat in old['patterns']:
        if pat['part_id'] in removed:continue
        row=deepcopy(pat);positions=deepcopy(row['positions_m'])
        if row['bogie_index'] is None:
            for pos in positions:pos[2]+=lift
        # Move complete brake functional groups, not just their visual disc.
        if row['assembly_id']=='running/bogie-brakes' or row['part_id']=='running/disc-guard':
            n=len(positions);bi=row['bogie_index'];bx=8.5+(bi//2)*17.65+(-6.4 if bi%2==0 else 6.4)
            for j,pos in enumerate(positions):
                axle=0 if pos[0]<bx else 1;side=-1 if axle else 1
                # Preserve each original member's lane association and radial position.
                lane=0 if pos[1]<0 else 1;new_y=(-.02,.20)[lane]*side
                pos[1]+=new_y-pos[1]
            changes.append(dict(pattern_id=row['id'],reason='Whole retained brake group relaid into explicit axle lanes; guards/hoses/WSP counterparts remain required',old_positions_m=row['positions_m'],new_positions_m=positions))
        a=dict(id=row['assembly_occurrence_id'],car_allocation=row['car_allocation'],bogie_index=row['bogie_index'])
        new=model._moments_for_pattern(bypart[row['part_id']],a,positions,row['rotation'],row['geometry'],pol)
        # Preserve origin/mass/cost exactly; only locations and moments change.
        patterns.append(new)
    template=deepcopy(old['parts'][0]);newparts=[];part_index={};new_assemblies={}
    def add(name,stock,placements,*,material='body/steel',mass=None,cost=None,R=model.I,role='solid',frame='bogie',group=None,metadata=None):
        """Placements are explicit train-world centres with car/bogie/axle tags."""
        pid='compact-drive/'+name
        if pid in part_index:raise ValueError('Duplicate component definition')
        if not placements:raise ValueError('Positive count required')
        m=stock_volume(stock)*(2660. if 'al5083' in material else 2700. if 'aluminium' in material else 8960. if 'copper' in material else 7850.) if mass is None else mass
        masses={c:float(m) for c in model.CASES} if isinstance(m,(int,float)) else dict(zip(model.CASES,m))
        if min(masses.values())<=0:raise ValueError('Unknown mass cannot become zero')
        prices=model._price(masses,material,pol) if cost is None else dict(zip(model.CASES,cost))
        extra_h=5. if group=='geartrain' else 2. if group in ('shaft','case') else .5 if group in ('mount','support','weld') else 0.
        if cost is None:
            prices={c:prices[c]+extra_h*pol['rates']['labour_usd_h'][i]*(1+pol['rates']['overhead_fraction'][i])+(20.,50.,150.)[i] if group=='geartrain' else prices[c]+extra_h*pol['rates']['labour_usd_h'][i]*(1+pol['rates']['overhead_fraction'][i]) for i,c in enumerate(model.CASES)}
        row=deepcopy(template);row.update(id=pid,source_part_id=None,name=name,assembly_id='research/compact-drive/'+str(group),quantity_per_train=len(placements),quantity_per_assembly=1,stock=deepcopy(stock),material_id=material,mass_each_kg=masses,direct_cost_each_usd=prices,make_buy='make' if mass is None else 'bounded-purchase-or-process',BOP_partition=False)
        row.update(mass_basis=dict(kind='calculated-gross-stock' if mass is None else 'positive-bounded-component',description='Gross stock/explicit bounds; not measured installed mass'),cost_basis='Declared Chinese/bulk source material/yield/process/labour/QA/overhead rates or positive equipment allowance; no quotation, final integration or qualification',manufacturing=['Identify material and stock; machine/drill stated interfaces','Fixture and assemble with retained fasteners, documented tools and access','Inspect geometry, torque, balance, insulation/pressure as appropriate; record finished mass'],joining='Explicit proposed axes, holes and mating interfaces; strength/fatigue not qualified',maintenance_removal='Isolate and support machine, remove named guards and flexible services, retain fasteners and use supported finite removal path',component_definition_id='pending')
        row.update(source_ids=['emrax/268-v1.7-C'] if name=='vendor-motor' else ['osr/compact-drive-calculated'],mounting='Explicit'+str(frame)+' frame; proposed stock/hole/retention interfaces require independent verification',finish='Declared corrosion/isolation protection; actual specification open',inspection=['Source/material identity and nominal dimensions','Bore/shaft/pilot/bolt-axis survey and fit record','Gear tooth/root/hardness/runout or pressure/insulation checks as applicable; acceptance limits pending'],open_tasks=['Detailed tolerance, contact/fatigue, actual capacity, access and release evidence'],tolerance_and_fits='Nominal research geometry with explicit policy uncertainty/tolerance; no approved manufacturing fit or safety limit',process_quantities=dict(extra_labour_h_each=extra_h,gear_heat_treatment_allowance_usd=[20,50,150] if group=='geartrain' else None,allowance_not_quotation=True),unit='item')
        row['component_definition_id']=model.identity({k:row[k] for k in ('id','stock','material_id','mass_each_kg','quantity_per_train')})
        row['candidate_id']=row['component_definition_id']
        row['research_geometry']=dict(role=role,frame=frame,group=group,**(metadata or {}));parts.append(row);newparts.append(row);part_index[pid]=row
        buckets={}
        for place in placements:buckets.setdefault((place['car'],place.get('bogie'),place.get('axle'),place.get('side',1)),[]).append(place)
        for (car,bi,axle,side),places in buckets.items():
            aid=f'compact/{car}/{bi}/{axle}/{group}';a=dict(id=aid,car_allocation=[[car,1.]],bogie_index=bi if frame!='body' else None,at_m=[8.5+car*17.65,0.,0.])
            new_assemblies.setdefault(row['assembly_id'],{})[aid]=deepcopy(a)
            row['quantity_per_assembly']=len(places)
            rotation=R if side==1 else RNEG if R==RY else [[-R[0][j] for j in range(3)],[-R[1][j] for j in range(3)],R[2][:]]
            # MirroredX/Y is a proper180degree rotation, never a reflection.
            if side==-1 and R!=RY:rotation=[[-R[0][j] for j in range(3)],[-R[1][j] for j in range(3)],R[2][:]]
            pat=model._moments_for_pattern(row,a,[x['at_m'] for x in places],rotation,model.geometry(row),pol);patterns.append(pat)
            for j,(pos,place) in enumerate(zip(pat['positions_m'],places)):
                entities.append(dict(id=pat['id']+'/'+str(j),part_id=pid,component_definition_id=row['component_definition_id'],at_m=pos,rotation=rotation,geometry=deepcopy(pat['geometry']),role=role,frame=frame,car=car,bogie=bi,axle=axle,side=side,group=group,uncertainty_m=p['supplier_terminal_uncertainty_m'] if role=='equipment-envelope' else p['own_position_uncertainty_m'],metadata=deepcopy(metadata or {})))
        return row
    # Explicit repeated anchors for24independently identified driven axles.
    drives=[]
    for bi in range(12):
        car=bi//2;bx=8.5+17.65*car+(-6.4 if bi%2==0 else 6.4)
        for j,s in enumerate((1,-1)):drives.append(dict(car=car,bogie=bi,axle=2*bi+j,side=s,bx=bx))
    def places(local,subset=drives):
        out=[]
        for d in subset:
            for x,y,z in local:out.append(dict(car=d['car'],bogie=d['bogie'],axle=d['axle'],side=d['side'],at_m=[d['bx']+d['side']*x,d['side']*y,z]))
        return out
    motor=gear['axes']['input'];mc=[motor[0],-.38,.43]
    add('vendor-motor',dict(kind='envelope',size_m=[.308,.18,.308]),places([mc]),material='running/mixed-module',mass=22.3,cost=[2500,5000,9000],role='equipment-envelope',metadata=dict(vendor=v,scope='Official casing dimensions plus explicit terminal/shaft required-space provision; actual privateSTEP import and revision compatibility pending. No fabricated supplier housing.',internal_bearings=2,internal_bearings_mass_owned=True),group='motor')
    # Gear blanks are material before tooth hobbing; mating meshes have their
    # own pitch/contact obligations and are not silently ignored as clashes.
    for g in gear['gears']:
        axis=gear['axes'][g['axis']];at=[axis[0],g['y_m'],axis[2]]
        add(g['id'],dict(kind='annulus',outer_radius_m=g['addendum_diameter_m']/2,inner_radius_m=g['bore_m']/2,length_m=g['face_m']),places([at]),R=RY,frame='gear',group='geartrain',metadata=dict(tooth=g,axis=g['axis'],finished_teeth=False,material_grade_hypothesis='42CrMo4 case-hardening route to be specified/verified'))
    for name,axis,diam,L in [('input-shaft','input',.045,.25),('intermediate-shaft','middle',.065,.25)]:
        a=gear['axes'][axis];add(name,dict(kind='cylinder',radius_m=diam/2,length_m=L),places([a]),R=RY,frame='gear',group='shaft',metadata=dict(axis=axis,shoulders_keys_retention_not_final=True))
    # Fabricated split case: ten actual plates, not an opaque filled box.
    cx,cy,cz=gear['case_centre_m'];L,W,H=gear['case_size_m'];t=.010
    for name,size,local in [
        ('case-top',[L,W,t],[[cx,cy,cz+(H-t)/2]]),('case-bottom',[L,W,t],[[cx,cy,cz-(H-t)/2]]),
        ('case-long-side',[L-2*t,t,(H-2*t)/2],[[cx,cy+s*(W-t)/2,cz+z*(H-2*t)/4] for s in (-1,1) for z in (-1,1)]),
        ('case-end',[t,W-2*t,(H-2*t)/2],[[cx+s*(L-t)/2,cy,cz+z*(H-2*t)/4] for s in (-1,1) for z in (-1,1)])]:
        add(name,dict(kind='box',size_m=size),places(local),material='running/aluminium',frame='gear',group='case',metadata=dict(split_plane_z_m=cz,shaft_bores=[dict(axis=k,centre_m=a,diameter_m=.2001 if k=='output' else .0651 if k=='middle' else .0451) for k,a in gear['axes'].items()],gross_blank_holes_not_mass_deducted=True))
    for axis,ro,ri,length,mass in [('input',.045,.02255,.020,[.8,1.2,1.8]),('middle',.065,.03255,.025,[1.5,2.5,4.]),('output',.14,.10005,.030,[10.,16.,25.])]:
        a=gear['axes'][axis];pos=[[a[0],y,a[2]] for y in (.405,.595)]
        add('bearing-'+axis,dict(kind='annulus',outer_radius_m=ro,inner_radius_m=ri,length_m=length),places(pos),mass=mass,cost=[80,180,450] if axis!='output' else [250,500,1000],R=RY,frame='gear',role='equipment-envelope',group='bearing',metadata=dict(capacity_known=False,required_dynamic_capacity_N=None,axis=axis))
        add('bearing-carrier-'+axis,dict(kind='annulus',outer_radius_m=ro+.010,inner_radius_m=ro,length_m=length+.010),places(pos),material='running/aluminium',R=RY,frame='gear',group='case',metadata=dict(split_halves=2,removable_caps=True,axis=axis))
    # Real oil/seal/retention items remain positive even before detailed supplier selection.
    for name,size,mass,price,local in [
        ('oil',[.30,.10,.12],[2.,3.,4.],[8,15,30],[[cx,cy,cz-.1]]),
        ('shaft-seal',[.22,.01,.22],[.12,.20,.35],[8,20,50],[[gear['axes']['output'][0],y,.38] for y in (.37,.63)]),
        ('input-seal',[.06,.01,.06],[.03,.05,.09],[5,12,30],[[motor[0],.37,.43]]),
        ('fill-drain-breather',[.025,.025,.035],[.03,.06,.10],[3,8,20],[[cx,cy,cz+.20],[cx,cy,cz-.20],[cx+.2,cy,cz+.2]]),
        ('coupling',[.06,.08,.06],[1.,2.,3.5],[100,250,600],[[motor[0],y,.43] for y in (-.24,.32)])]:
        add(name,dict(kind='envelope',size_m=size),places(local),mass=mass,cost=price,frame='gear' if name!='coupling' else 'bogie',role='allocation' if name=='oil' else 'equipment-envelope',group='lubrication' if name!='coupling' else 'coupling',metadata=dict(actual_shape_capacity_unknown=True))
    add('coupling-shaft',dict(kind='cylinder',radius_m=.0225,length_m=.56),places([[motor[0],.04,.43]]),R=RY,group='coupling',metadata=dict(two_flexible_ends=True,misalignment_capacity_known=False))
    add('shaft-guard',dict(kind='annulus',outer_radius_m=.043,inner_radius_m=.040,length_m=.61),places([[motor[0],.04,.43]]),material='running/aluminium',R=RY,group='guard',metadata=dict(split_halves=2,remove_before_mount_tools=True))
    add('motor-face-mount',dict(kind='annulus',outer_radius_m=.085,inner_radius_m=.03755,length_m=.012),places([[motor[0],-.320,.43]]),R=RY,group='mount',metadata=dict(mount_PCD_m=.094,mount_count=6,thread='M10',axis=[0,1,0],pilot_fit_unverified=True))
    add('motor-mount-stem',dict(kind='box',size_m=[.08,.012,.10]),places([[motor[0],-.320,.55]]),group='mount')
    add('motor-carrier-arm',dict(kind='rhs',length_m=.68,width_m=.08,depth_m=.08,wall_m=.006),places([[motor[0]+dx,-.64,.60] for dx in (-.15,.15)]),R=RY,group='mount')
    add('motor-carrier-post',dict(kind='rhs',length_m=.18,width_m=.08,depth_m=.08,wall_m=.006),places([[motor[0]+dx,-.98,.55] for dx in (-.15,.15)]),R=model.ZAXIS,group='mount')
    foot=[[motor[0]+.047*cos(2*pi*j/6),-.305,.43+.047*sin(2*pi*j/6)] for j in range(6)]
    add('M10-motor-screw',dict(kind='cylinder',radius_m=.005,length_m=.035),places(foot),R=RY,group='fastener',metadata=dict(axis=[0,1,0],thread_into_motor=True,bolt_head_tool_radius_m=p['foot_socket_radius_m'],tool_approach=[0,1,0],remove_guard_and_coupling_before_tool=True))
    add('M10-motor-washer',dict(kind='annulus',outer_radius_m=.010,inner_radius_m=.0053,length_m=.002),places([[x,y+.02,z] for x,y,z in foot]),R=RY,group='fastener')
    # FourY-axis torque-joint sets per gearbox; case and frame bush plates explicit.
    torque=[[cx+dx,.73,.49] for dx in (-.15,.15)]
    add('case-torque-lug',dict(kind='box',size_m=[.16,.12,.025]),places([[cx-.15,.69,.49]]),material='running/aluminium',frame='gear',group='case')
    add('frame-torque-outrigger',dict(kind='rhs',length_m=.29,width_m=.08,depth_m=.08,wall_m=.006),places([[cx+.15,.875,.49]]),R=RY,group='mount')
    add('torque-plate',dict(kind='box',size_m=[.16,.012,.12]),places(torque),group='mount',metadata=dict(axis_normal=[0,1,0]))
    add('torque-bush',dict(kind='annulus',outer_radius_m=.028,inner_radius_m=.0085,length_m=.025),places(torque),mass=[.25,.4,.7],cost=[8,20,50],R=RY,role='equipment-envelope',group='mount',metadata=dict(misalignment_stiffness_known=False))
    add('M16-torque-bolt',dict(kind='cylinder',radius_m=.008,length_m=.080),places(torque),R=RY,group='fastener',metadata=dict(axis=[0,1,0],tool_approach=[0,1,0],tool_radius_m=p['torque_socket_radius_m']))
    add('M16-torque-nut',dict(kind='annulus',outer_radius_m=.014,inner_radius_m=.008,length_m=.014),places([[x,y+.052,z] for x,y,z in torque]),R=RY,group='fastener',metadata=dict(finished_hex_unknown=True))
    add('M16-torque-washer',dict(kind='annulus',outer_radius_m=.016,inner_radius_m=.0085,length_m=.003),places([[x,y+dy,z] for x,y,z in torque for dy in (-.042,.042)]),R=RY,group='fastener')
    add('torque-link',dict(kind='box',size_m=[.30,.012,.050]),places([[cx,.73,.49]]),group='mount',metadata=dict(two_bushed_ends=True,load_and_fatigue_unknown=True))
    # Splitcase and cap fasteners, all explicitly retained.
    split=[[cx+dx,cy+dy,cz] for dx in (-.28,-.1,.1,.28) for dy in (-.10,.10)]
    add('M10-case-bolt',dict(kind='cylinder',radius_m=.005,length_m=.045),places(split),R=model.ZAXIS,frame='gear',group='fastener')
    add('M10-case-nut',dict(kind='annulus',outer_radius_m=.009,inner_radius_m=.005,length_m=.009),places([[x,y,z+.03] for x,y,z in split]),R=model.ZAXIS,frame='gear',group='fastener')
    add('M10-case-washer',dict(kind='annulus',outer_radius_m=.010,inner_radius_m=.0053,length_m=.002),places([[x,y,z+dz] for x,y,z in split for dz in (-.023,.023)]),R=model.ZAXIS,frame='gear',group='fastener')
    # Secondary retention, stops and services are not free abstractions.
    add('motor-retention-strap',dict(kind='box',size_m=[.34,.04,.006]),places([[motor[0],y,.26] for y in (-.44,-.30)]),group='retention',metadata=dict(secondary_catch_not_static_support=True))
    add('motor-retention-stop',dict(kind='box',size_m=[.06,.08,.025]),places([[motor[0]+dx,-.38,.275] for dx in (-.18,.18)]),group='retention')
    for name,size,mass,cost,local in [
        ('motor-power-cable',[.6,.02,.2],2.4*.00007*8960+.38,[20,40,80],[[motor[0],-.55+.025*j,.62] for j in range(3)]),
        ('motor-bond',[.5,.025,.10],1.2*.000025*8960,[8,15,30],[[motor[0],-.62,.50]]),
        ('coolant-hose',[.6,.02,.20],[.25,.4,.7],[10,20,40],[[motor[0],-.58+dy,.57] for dy in (-.025,.025)]),
        ('motor-air-duct',[.5,.12,.24],[.8,1.5,3.],[20,45,100],[[motor[0],-.62,.62]]),
        ('service-clamp',[.035,.030,.025],[.03,.05,.08],[.5,1,3],[[motor[0]+dx,-.62,.62] for dx in (-.15,-.05,.05,.15)])]:
        add(name,dict(kind='envelope',size_m=size),places(local),mass=mass,cost=cost,role='equipment-envelope',group='service',metadata=dict(routed_finite_tube_not_verified=True,cut_length_m=2.4 if name=='motor-power-cable' else 1.4 if name=='motor-air-duct' else 1.2,min_bend_radius_m=.16 if name=='motor-power-cable' else .15))
    add('M6-service-fixing',dict(kind='cylinder',radius_m=.003,length_m=.025),places([[motor[0]+dx,-.62,.64] for dx in (-.15,-.05,.05,.15)]),R=model.ZAXIS,group='fastener')
    # Retention/service/cap fixings and mount/case weld metal remain counted.
    rr=[[motor[0]+dx,y,.26] for dx in (-.15,.15) for y in (-.44,-.30)]
    add('M12-retention-bolt',dict(kind='cylinder',radius_m=.006,length_m=.05),places(rr),R=model.ZAXIS,group='fastener')
    add('M12-retention-nut',dict(kind='annulus',outer_radius_m=.0105,inner_radius_m=.006,length_m=.011),places([[x,y,z+.032] for x,y,z in rr]),R=model.ZAXIS,group='fastener')
    add('M12-retention-washer',dict(kind='annulus',outer_radius_m=.012,inner_radius_m=.0065,length_m=.0025),places([[x,y,z+dz] for x,y,z in rr for dz in (-.027,.027)]),R=model.ZAXIS,group='fastener')
    service=[[motor[0]+dx,-.62,.64] for dx in (-.15,-.05,.05,.15)]
    add('M6-service-nut',dict(kind='annulus',outer_radius_m=.0055,inner_radius_m=.003,length_m=.005),places([[x,y,z+.018] for x,y,z in service]),R=model.ZAXIS,group='fastener')
    add('M6-service-washer',dict(kind='annulus',outer_radius_m=.006,inner_radius_m=.0033,length_m=.0015),places([[x,y,z+dz] for x,y,z in service for dz in (-.014,.014)]),R=model.ZAXIS,group='fastener')
    cap=[]
    for axis,ro in [('input',.045),('middle',.065),('output',.14)]:
        aa=gear['axes'][axis]
        for y in (.375,.625):
            cap += [[aa[0]+(ro+.015)*cos(j*pi/2),y,aa[2]+(ro+.015)*sin(j*pi/2)] for j in range(4)]
    add('M8-bearing-cap-bolt',dict(kind='cylinder',radius_m=.004,length_m=.035),places(cap),R=RY,frame='gear',group='fastener',metadata=dict(threaded_case_insert_required=True))
    add('M8-bearing-cap-washer',dict(kind='annulus',outer_radius_m=.008,inner_radius_m=.0043,length_m=.0015),places([[x,y+.02,z] for x,y,z in cap]),R=RY,frame='gear',group='fastener')
    bead=sqrt(.006**2/2)
    add('new-mount-weld',dict(kind='box',size_m=[.68,bead,bead]),places([[motor[0]+dx,-.64,z] for dx in (-.15,.15) for z in (.56,.64)]),R=RY,group='weld',metadata=dict(declared6mm_fillet=True,strength_not_verified=True))
    add('new-case-weld',dict(kind='box',size_m=[.68,bead,bead]),places([[cx,cy+dy,cz+dz] for dy in (-.125,.125) for dz in (-.18,.18)]),material='running/aluminium',frame='gear',group='weld',metadata=dict(splitcase_accessible_seam_hypothesis=True,strength_not_verified=True))
    # New body supports bridge the exact100/150mm rise without changing spring travel.
    bogies=[dict(car=bi//2,bogie=bi,axle=None,side=1,bx=8.5+(bi//2)*17.65+(-6.4 if bi%2==0 else 6.4)) for bi in range(12)]
    for name,size,z,ys in [('pedestal-cap',[.46,.46,.010],.76+lift-.005,(-.75,.75)),('pedestal-base',[.46,.46,.010],.765,(-.75,.75)),('emergency-cap',[.20,.20,.010],.76+lift-.005,(-.40,.40))]:
        add(name,dict(kind='box',size_m=size),places([[0.,y,z] for y in ys],bogies),material='body/al5083',frame='body',group='support')
    add('pedestal-X-wall',dict(kind='box',size_m=[.46,.006,lift-.020]),places([[0.,y+dy,.76+lift/2] for y in (-.75,.75) for dy in (-.227,.227)],bogies),material='body/al5083',frame='body',group='support')
    add('pedestal-Y-wall',dict(kind='box',size_m=[.006,.448,lift-.020]),places([[dx,y,.76+lift/2] for y in (-.75,.75) for dx in (-.227,.227)],bogies),material='body/al5083',frame='body',group='support')
    add('emergency-riser',dict(kind='rhs',length_m=lift-.010,width_m=.20,depth_m=.20,wall_m=.006),places([[0.,y,.76+(lift-.01)/2] for y in (-.40,.40)],bogies),material='body/al5083',R=model.ZAXIS,frame='body',group='support')
    add('kingpin-extension',dict(kind='cylinder',radius_m=.05,length_m=lift),places([[0.,0.,.70+lift/2]],bogies),R=model.ZAXIS,frame='body',group='support',metadata=dict(load_fit_retention_unknown=True))
    add('body-anti-lift-extension',dict(kind='box',size_m=[.08,.012,lift+.08]),places([[0.,y,.72+lift/2] for y in (-.9,.9)],bogies),frame='body',group='retention')
    support_bolts=[[dx,y+dy,.76+lift/2] for y in (-.75,.75) for dx in (-.15,.15) for dy in (-.15,.15)]
    add('M16-support-stud',dict(kind='cylinder',radius_m=.008,length_m=lift+.06),places(support_bolts,bogies),R=model.ZAXIS,frame='body',group='fastener')
    add('M16-support-nut',dict(kind='annulus',outer_radius_m=.014,inner_radius_m=.008,length_m=.014),places([[x,y,z+dz] for x,y,z in support_bolts for dz in (-(lift+.04)/2,(lift+.04)/2)],bogies),R=model.ZAXIS,frame='body',group='fastener')
    # Eachdrive has a positive inverter allowance in body space. Chiller, feed,
    # protection and integration reserve remain separately mass/cost owned.
    for name,size,mass,cost,locations in [('inverter',[.45,.25,.20],[18,30,50],[800,1600,3200],[[4.0,-.9,.65+lift],[13.,.9,.65+lift]]),('integration-reserve',[1.2,1.,.5],[200,400,800],[4000,10000,25000],[[8.5,0.,1.9+lift]])]:
        pp=[dict(car=car,bogie=None,axle=None,side=1,at_m=[car*17.65+x,y,z]) for car in range(6) for x,y,z in locations]
        # Fourinverters/car (one per drivenaxle), two mirrored bogies.
        if name=='inverter':pp=[dict(car=car,bogie=None,axle=None,side=1,at_m=[car*17.65+x,y+dy,z]) for car in range(6) for x,y,z in locations for dy in (-.18,.18)]
        add(name,dict(kind='envelope',size_m=size),pp,mass=mass,cost=cost,role='allocation' if name=='integration-reserve' else 'equipment-envelope',frame='body',group='integration',metadata=dict(capacity_not_verified=True,remaining_positive_unknown=True))
    # Replace criticalweld mass allocations by located seam bead geometry. The
    # parent nominal mass survives exactly; it is not dropped by clash filtering.
    weld_source=[r for r in old['parts'] if r['id'] in welds or r['id']=='powered-bogie/frame-weld-deposit']
    weld_ledger=[]
    def axis_rotation(a,b):
        u=[b[i]-a[i] for i in range(3)];L=sqrt(sum(v*v for v in u));x=[v/L for v in u]
        ref=[0.,0.,1.] if abs(x[2])<.9 else [0.,1.,0.]
        y=[ref[1]*x[2]-ref[2]*x[1],ref[2]*x[0]-ref[0]*x[2],ref[0]*x[1]-ref[1]*x[0]];ny=sqrt(sum(v*v for v in y));y=[v/ny for v in y]
        z=[x[1]*y[2]-x[2]*y[1],x[2]*y[0]-x[0]*y[2],x[0]*y[1]-x[1]*y[0]]
        return L,[[x[i],y[i],z[i]] for i in range(3)]
    for row in weld_source:
        isbody=row['id'].startswith('underframe/');segments=[]
        if isbody:
            #Actualweb/flange edges, taperedhaunches and bothfacesof each
            #diaphragm. Gross weldmass is retained through declared beadarea.
            for pat in old['patterns']:
                if pat['car_allocation']!=[[0,1.]]:continue
                name=pat['part_id'];size=pat['geometry']['size_m'];R=pat['rotation']
                local=[]
                if name.startswith(('underframe/girder-web-','underframe/girder-tapered-web-')):
                    profile=pat['geometry'].get('finished_profile_xz_m')
                    if profile:
                        edges=[(profile[0],profile[1]),(profile[2],profile[3])]
                        local=[([a[0],0.,a[1]],[b[0],0.,b[1]]) for a,b in edges]
                    else:local=[([-size[0]/2,0.,z],[size[0]/2,0.,z]) for z in (-size[2]/2,size[2]/2)]
                elif name.startswith('underframe/internal-diaphragm-'):
                    for xx in (-size[0]/2,size[0]/2):
                        local += [([xx,-size[1]/2,z],[xx,size[1]/2,z]) for z in (-size[2]/2,size[2]/2)]
                        local += [([xx,y,-size[2]/2],[xx,y,size[2]/2]) for y in (-size[1]/2,size[1]/2)]
                for at in pat['positions_m']:
                    for aa,bb in local:
                        segments.append(([at[i]+sum(R[i][j]*aa[j] for j in range(3)) for i in range(3)],[at[i]+sum(R[i][j]*bb[j] for j in range(3)) for i in range(3)]))
            #Fourdeclaredfull-sectionsplice perimeter paths at source stations.
            for xx,depth in ((3.3,.34),(4.1,.65),(12.9,.65),(13.7,.34)):
                for z in (.9595,.9595-depth):segments.append(([xx,-.325,z],[xx,.325,z]))
                for y in (-.325,.325):segments.append(([xx,y,.9595-depth],[xx,y,.9595]))
        else:
            #Fourreal transom-to-side RHS joint perimeters. Otherretained
            #frameweld allowance is distributed across these declared joints;
            #endtie gap/HAZ/weldstrength remains an explicit researchhold.
            for xx in (-1.54,.42):
                for yy in (-.93,.93):
                    for z in (.30,.52):segments.append(([xx-.09,yy,z],[xx+.09,yy,z]))
                    for x in (xx-.09,xx+.09):segments.append(([x,yy,.30],[x,yy,.52]))
        lengths=[axis_rotation(a,b)[0] for a,b in segments];totalL=fsum(lengths)
        per_module={c:row['mass_each_kg'][c] for c in model.CASES};area=per_module['base']/(7850*totalL);bead=sqrt(area)
        groups={}
        for (aa,bb),L in zip(segments,lengths):
            _,R=axis_rotation(aa,bb);key=(round(L,10),tuple(round(x,10) for rr in R for x in rr))
            groups.setdefault(key,dict(L=L,R=R,centres=[]))['centres'].append([(aa[i]+bb[i])/2 for i in range(3)])
        for j,item in enumerate(groups.values()):
            L=item['L'];pp=[]
            if isbody:
                for car in range(6):
                    for at in item['centres']:pp.append(dict(car=car,bogie=None,axle=None,side=1,at_m=[at[0]+car*17.65,at[1],at[2]+lift]))
            else:pp=places(item['centres'],bogies)
            add('retained-weld-'+('body' if isbody else 'frame')+'-'+str(j),dict(kind='box',size_m=[L,bead,bead]),pp,mass=[per_module[c]*L/totalL for c in model.CASES],cost=[row['direct_cost_each_usd'][c]*L/totalL for c in model.CASES],R=item['R'],frame='body' if isbody else 'bogie',group='weld',metadata=dict(parent_part_id=row['id'],seam_map_is_hypothesis=True,source_edge_segments=True,base_cross_section_area_m2=area,retained_mass_exactly=True))
        weld_ledger.append(dict(parent_part_id=row['id'],mass_before_kg={c:row['mass_each_kg'][c]*row['quantity_per_train'] for c in model.CASES},mass_after_kg={c:per_module[c]*row['quantity_per_train'] for c in model.CASES},located_segments_per_module=len(segments),located_length_m=totalL,geometry_scope='Actualsourceweb/flange/diaphragm/splice edge paths or declared RHSjoint perimeters. Base beadarea preserves priornominalmass; weldprocess,geometryandstrengthremainunqualified.'))
    # Assemblymass, componentquantity and ancestororigin controls.
    for row in parts:
        actual=sum(q['count'] for q in patterns if q['part_id']==row['id'])
        if actual!=row['quantity_per_train']:raise ValueError('Occurrence coverage differs: '+row['id'])
    result['assembly_occurrences'].update({k:list(v.values()) for k,v in new_assemblies.items()})
    result.update(parts=parts,patterns=patterns,proposed_component_types=len(parts),total_occurrences=sum(q['count'] for q in patterns),
        nominal_part_mass_kg={c:fsum(r['mass_kg'][c] for r in patterns) for c in model.CASES},
        direct_parts_process_usd={c:fsum(r['direct_cost_usd'][c] for r in patterns) for c in model.CASES},source_sha256=before,
        removed_parts=deepcopy(old.get('removed_parts',[]))+[dict(part_id=r['id'],source_part_id=r['source_part_id'],reason='Explicitly superseded by compact drive, source-located seams or retained support functions',quantity_per_train=r['quantity_per_train'],mass_kg={c:r['quantity_per_train']*r['mass_each_kg'][c] for c in model.CASES}) for r in old['parts'] if r['id'] in removed],
        parent_candidate_id=old['candidate_id'],parent_evaluation_id=old['evaluation_id'],external_drive_placements=[],BOP_partition=None,**FLAGS)
    contract=dict(schema='osr-compact-drive-interface-contract/1',config=config,geartrain=gear,vendor=v,assembly_entities=entities,body_lift_m=lift,retained_weld_ledger=weld_ledger,
        retained_brake_count_per_bogie={name:sum(q['count'] for q in patterns if q['bogie_index']==0 and q['part_id']=='running/'+name) for name in ('brake-disc','caliper-body','service-actuator','parking-actuator','friction-pad')},
        changes=changes,mass_ownership=dict(all_new_drive_components_in_body_BOM=True,additional_external_drive_mass_kg=0.,zero_is_exact_no_external_addition_not_unknown_equipment=True,legacy_external_motor_gear9552kg_superseded=True,legacy_BOP_partition_and_reserve_superseded=True,remaining_unknown_mass_positive=True,original_body_installation_reserve_retained=True),
        residual_issues=['SupplierSTEP modelB/datasheetC andshaft/mount/terminal compatibility notverified','Actual contact/curve/wheelprofiles, suspension and bearing capacities open','Gear flanks, keys, tooth/contactfatigue, lubrication andcasebearing seats unqualified','Body pedestal/kingpin/endstop/anti-lift loadpaths, welding and fatigue open','Inverter,50Ccooling/chiller repeated duty and actual availableforce map require coordinator model','Finite tool/removal/service paths are hypotheses, not physical access acceptance'])
    physical=dict(schema='osr-compact-drive-body-physical/1',parent_candidate_id=old['candidate_id'],track_interface=deepcopy(old['physical_definition']['track_interface']),layout=deepcopy(pol['layout']),config=config,geartrain=gear,vendor_source=v,part_revisions=changes,
        replaced_part_ids=sorted(removed),parts=[{k:r[k] for k in ('id','source_part_id','component_definition_id','quantity_per_train','material_id','stock','mass_each_kg')} for r in parts],
        occurrence_patterns=[{k:q[k] for k in ('id','part_id','count','positions_m','rotation','geometry','car_allocation','bogie_index')} for q in patterns],compact_assembly_entities=entities,mass_ownership=contract['mass_ownership'])
    result['physical_definition']=physical;result['candidate_id']=model.identity(physical);contract['candidate_id']=result['candidate_id'];contract['contract_id']=model.identity(contract);result['compact_drive_contract']=contract
    scenarios=[]
    for kind in ('tare','normal','crowd-control'):
        rows=deepcopy(model._scenario_rows(patterns,'crowd' if kind=='crowd-control' else kind,pol))
        for row in rows:
            if row['assembly_id'] in ('passengers','installation-reserve'):row['centroid_m'][2]+=lift
        for c in model.CASES:
            moments=model.mass_properties(rows,c);loads=model.reactions(rows,c,pol)
            scenarios.append(dict(name=kind+'-'+c,case=c,train_mass_kg=moments['mass_kg'],CG_m=moments['CG_m'],inertia_about_CG_kg_m2=moments['inertia_about_CG_kg_m2'],axles=loads['axles'],force_residual_N=loads['force_residual_N'],moment_residual_Nm=loads['moment_residual_Nm'],lateral_acceleration_m_s2=pol['evaluation']['lateral_acceleration_m_s2']))
    result['mass_scenarios']=scenarios;result['mass_uncertainty']=dict(status='Parent installed intervals invalidated; positive partmass/position bounds retained, new conservative rebound required');result['interface_screens']=dict(status='HOLD new compactdrive interfaces; parentchecks are ancestry only');result['selection']=dict(purpose='Unselected bounded research comparison',independently_selected_for_baseline=False);result['installed_mass_complete']=False;result['assembly_plans']['compact_drive']=dict(operations=['Machine/heat-treat/count gear blanks, shafts and caseplates with source identities','Trialmeasure actualvendor motor, align shaft/pilot and mount bolt datums','Fit gear bearings, retainedcaps, seals, lubrication and torquereaction withYaxis bolts','Install counted bodypedestals and independentlycheck load/retention before support changes','Fit services and guards; remove guard/coupling before motorfoot tools','Retain independent brakes, WSP, sensors and verify full finite removal/service paths'],manufacturing_release=False);result['structural_comparison']=dict(status='Invalidated: new compact drive and raisedbody supports; no parentstrength admission')
    if sources(root)!=before:raise ValueError('Producer source changed duringbuild')
    return seal(result)
