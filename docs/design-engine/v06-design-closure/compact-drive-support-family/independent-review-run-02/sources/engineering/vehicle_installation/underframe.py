"""Bounded powered-wheel underframe revisions; no roof/shell stiffness credit.

The four-plate girder is continuous except two explicitly compliant welded
splices. Crossmembers transfer the side load into the girder through proposed
counted stud/plate interfaces. All strength and joint properties are hypotheses.
"""
from copy import deepcopy
from pathlib import Path
from math import fsum,pi,prod
import gzip,json
from engineering.station_rail.common import identity,encoded,digest
from . import model,FLAGS,ROOT
from engineering.design_search import requirement_policy

PARENT='b7cac2427635448e2a8845fcc1b8618634543f5025ef666a2fdfb879c5c42350'
PARENT_EVALUATION='efa0e704c9be7fcb5ef19cd74d453f326922a67b4ceb424ff4c295f1d994f474'
FAMILIES=[dict(id='steel-600x650x8',b=.60,h=.65,t=.008,material='body/steel',E=200e9,rho=7850.,nu=.30,stress_limit=120e6),
 dict(id='steel-650x650x10',b=.65,h=.65,t=.010,material='body/steel',E=200e9,rho=7850.,nu=.30,stress_limit=120e6),
 dict(id='steel-650x650x12',b=.65,h=.65,t=.012,material='body/steel',E=200e9,rho=7850.,nu=.30,stress_limit=120e6),
 dict(id='aluminium-650x650x16',b=.65,h=.65,t=.016,material='body/al5083',E=69e9,rho=2660.,nu=.33,stress_limit=55e6)]
ADDITIONS=dict(motors_gears_per_driven_axle_kg=796.,driven_axle_indices=list(range(0,24,2)),
 drive_BOP_train_kg=dict(low=2500.,base=4000.,high=8000.),capture_interface_train_kg=dict(low=300.,base=600.,high=1200.))
ASSUMPTIONS=dict(support_x_m=[2.1,14.9],car_length_m=17.,girder_top_z_m=.9595,
 weld_splice_x_m=[3.3,4.1,12.9,13.7],splice_zone_length_m=.30,splice_local_EI_fraction=.50,
 bogie_connection_stiffness_N_m=50e6,bogie_connection_bearing_slip_m=.001,
 minimum_dynamic_ground_allocation_m=.200,suspension_jounce_m=.040,track_and_tolerance_allocation_m=.020,
 normal_midspan_sag_project_allocation_m=.020,crowd_midspan_sag_project_allocation_m=.040,
 door_jamb_relative_chord_allocation_m=.002,door_jamb_span_m=1.64,
 lateral_acceleration_m_s2=.5,torsion_CG_z_hypothesis_m=2.2,torsion_joint_GJ_fraction=.75,torque_transfer_length_m=6.4,door_roll_offset_y_m=1.315,
 provisional_roll_displacement_allocation_m=.003,
 minimum_pod_joint_gap_m=.020,net_section_I_fraction_hypothesis=.85,bolt_E_Pa=200e9,bolt_tensile_stress_hypothesis_Pa=400e6,
 bolt_shear_stress_hypothesis_Pa=230e6,bolster_studs_per_side=8,floor_studs_per_stub=4,
 crossmember_joint_stiffness_N_m=20e6,crossmember_joint_bearing_slip_m=.0005,
 material_properties_qualified=False,joint_properties_measured=False,targets_are_formal_acceptance_limits=False)


def load_parent(path):
    raw=Path(path).read_bytes();r=json.loads(gzip.decompress(raw))
    if r['candidate_id']!=PARENT or r['evaluation_id']!=PARENT_EVALUATION:raise ValueError('Exact frozen02 parent required')
    if identity(r['physical_definition'])!=PARENT or identity({k:v for k,v in r.items() if k!='evaluation_id'})!=PARENT_EVALUATION:raise ValueError('Parent seals differ')
    return r


def _part(template,name,q,stock,material,p,description,mass=None):
    r=deepcopy(template);r.update(id='underframe/'+name,source_part_id=None,name=name,assembly_id='installation/central-girder',quantity_per_assembly=q,quantity_per_train=q*6,stock=stock,material_id=material)
    if mass is None:
        rho=7850. if material=='body/steel' else 2660. if material=='body/al5083' else 2710.
        volume=prod(stock['size_m']) if stock['kind']=='box' else stock['length_m']*(stock['width_m']*stock['depth_m']-(stock['width_m']-2*stock['wall_m'])*(stock['depth_m']-2*stock['wall_m']))
        mass={c:volume*rho for c in model.CASES}
    r['mass_each_kg']=mass;r['direct_cost_each_usd']=model._price(mass,material,p)
    r['component_definition_id']=identity({k:r[k] for k in ('id','stock','material_id','quantity_per_assembly')})
    r['mass_basis']=dict(kind='calculated-gross-stock' if stock['kind'] in ('box','rhs') else 'bounded-finished-fixing',description=description)
    r['cost_basis']='Declared material/yield plus processing labour, machine/QA and overhead once; no supplier quotation, final-car integration, release testing or tax'
    r['manufacturing']=['Cut/mark stock and heat identity',description,'Fixture, join and survey against controlled datums before closing access', 'Inspect joints, corrosion isolation and retained fasteners; qualification remains open']
    r['joining']=description;r['maintenance_removal']='Support car on rated stands, remove outer pods where required, isolate services, restrain body and release accessible retained joints; girder replacement requires workshop body fixture'
    return r


def definitions(parent,family):
    p=parent['policy'];b,h,t=family['b'],family['h'],family['t'];top=ASSUMPTIONS['girder_top_z_m'];template=parent['parts'][0]
    parts=[];placements={};revisions=[];removed=[]
    def add(name,q,stock,material,positions,R=model.I,mass=None,description='Counted proposed stock; fitted holes and weld strength require detailed drawing'):
        r=_part(template,name,q,stock,material,p,description,mass);parts.append(r);placements[r['id']]=(positions,R);return r
    # Deep midspan, shallow bogie ends and inclined haunch bottom flanges.
    # Top flange uses one8.8m middle plate and two4.1m outer plates; the
    # longest assumed obtainable blank is8.8m, not an uncounted17m extrusion.
    add('girder-top-middle',1,dict(kind='box',size_m=[8.8,b,t]),family['material'],[[0.,0.,top-t/2]])
    add('girder-top-outer',2,dict(kind='box',size_m=[4.1,b,t]),family['material'],[[-6.45,0.,top-t/2],[6.45,0.,top-t/2]])
    add('girder-bottom-middle',1,dict(kind='box',size_m=[8.8,b,t]),family['material'],[[0.,0.,top-h+t/2]])
    add('girder-bottom-outer',2,dict(kind='box',size_m=[3.3,b,t]),family['material'],[[-6.85,0.,top-.34+t/2],[6.85,0.,top-.34+t/2]])
    add('girder-web-middle',2,dict(kind='box',size_m=[8.8,t,h-2*t]),family['material'],[[0.,side*(b-t)/2,top-h/2] for side in (-1,1)])
    add('girder-web-outer',4,dict(kind='box',size_m=[3.3,t,.34-2*t]),family['material'],[[x,side*(b-t)/2,top-.17] for x in (-6.85,6.85) for side in (-1,1)])
    angle=__import__('math').atan2(h-.34,.8);length=(.8**2+(h-.34)**2)**.5
    for side in (-1,1):
        c=__import__('math').cos(angle);ss=-side*__import__('math').sin(angle)
        R=[[c,0.,ss],[0.,1.,0.],[-ss,0.,c]]
        add('girder-inclined-bottom-'+str(side),1,dict(kind='box',size_m=[length,b,t]),family['material'],[[side*4.8,0.,top-(h+.34)/2+t*c/2]],R,
            description='Inclined haunch flange blank, mitred butt ends; full-penetration welds and local fatigue/HAZ require verification')
        row=add('girder-tapered-web-'+str(side),2,dict(kind='box',size_m=[.8,t,h-2*t]),family['material'],[[side*4.8,y*(b-t)/2,top-h/2] for y in (-1,1)],
            description='Rectangular procurement blank; cut specified trapezoidal profile. Gross stock mass retained as conservative allowance, not finished net mass')
        row['finished_profile_xz_m']=[[-.4,(h-2*t)/2],[.4,(h-2*t)/2],[.4,-(h-2*t)/2+(h-.34 if side>0 else 0)],[-.4,-(h-2*t)/2+(h-.34 if side<0 else 0)]]
    # Crossmember stations copied from frozen02 rather than choosing an
    # artificially favourable equally-spaced load transfer.
    cross=next(r for r in parent['patterns'] if r['part_id']=='body/floor-crossmember')
    xs=[x[0]-8.5 for x in cross['positions_m']]
    stations=sorted(set(xs+[-6.4,6.4]));n=len(stations)
    for i,x in enumerate(stations):
        height=depth_at(x+8.5,family)
        add('internal-diaphragm-'+str(i),1,dict(kind='box',size_m=[.008,b-2*t,height-2*t]),family['material'],[[x,0.,top-height/2]],description='Individually sized internal shear diaphragm, fit before closure; no free lightening holes assumed')
    # Dissimilar-material or same-material interface still uses positive
    # isolation and retention mass. Endplates remain accessible from outside.
    inner=b/2+.010+.0015+.025;stub=1.145-inner;yc=(1.145+inner)/2
    replacements={
      'body/floor-crossmember':('floor-crossmember-stub',48,dict(kind='rhs',length_m=stub,width_m=.10,depth_m=.18,wall_m=.006),'body/al6005a',[[x,side*yc,top-.09] for x in xs for side in (-1,1)],model.RZ90),
      'body/body-bolster':('body-bolster-stub',4,dict(kind='rhs',length_m=stub,width_m=.30,depth_m=.1895,wall_m=.016),'body/al5083',[[x,side*yc,top-.1895/2] for x in (-6.4,6.4) for side in (-1,1)],model.RZ90),
      'body/floor-stringer':('outer-floor-stringer',4,dict(kind='rhs',length_m=16.5,width_m=.06,depth_m=.10,wall_m=.003),'body/al6005a',[[0.,y,top-.21] for y in (-.9,-.54,.54,.9)],model.I),
      'body/bolster-doubler':('bolster-joint-doubler',4,dict(kind='box',size_m=[.42,.025,.36]),'body/al5083',[[x,side*(b/2+.024),top-.18] for x in (-6.4,6.4) for side in (-1,1)],model.I)}
    for source,(name,q,stock,mat,pos,R) in replacements.items():
        old=next(r for r in parent['parts'] if r['id']==source);new=add(name,q,stock,mat,pos,R,description='Revised local stub/plate transfers shear and local moment into central girder through counted isolated stud joint; HAZ, bearing and prying require verification')
        new['source_part_id']=source;new['assembly_id']='body/underframe'
        revisions.append(dict(source_part_id=source,old_part_id=source,new_part_id=new['id'],old_quantity_per_train=old['quantity_per_train'],new_quantity_per_train=new['quantity_per_train'],reason='Replace physical intersection with girder and provide explicit load-transfer joint',old_mass_kg={c:old['mass_each_kg'][c]*old['quantity_per_train'] for c in model.CASES},new_mass_kg={c:new['mass_each_kg'][c]*new['quantity_per_train'] for c in model.CASES}))
    add('bolster-air-spring-seat',4,dict(kind='box',size_m=[.46,.46,.010]),'body/al5083',[[x,side*.75,.765] for x in (-6.4,6.4) for side in (-1,1)],description='Counted load spreading seat from retained spring top z=.760m to new bolster underside z=.770m; bearing/retention qualification open')
    add('crossmember-joint-cleat',48,dict(kind='box',size_m=[.20,.010,.18]),family['material'],[[x,side*(b/2+.005),top-.09] for x in xs for side in (-1,1)],description='External load-spreading cleat with four M16 through-stud positions; isolated captive steel backing plate, no steel-to-aluminium weld; hole-zone fatigue/HAZ not qualified')
    add('crossmember-endplate',48,dict(kind='box',size_m=[.20,.025,.18]),'body/al5083',[[x,side*(b/2+.024),top-.09] for x in xs for side in (-1,1)],description='Aluminium stub endplate joined before assembly, isolated from girder cleat; weld HAZ/prying to test')
    add('bolster-joint-cleat',4,dict(kind='box',size_m=[.42,.010,.36]),family['material'],[[x,side*(b/2+.005),top-.18] for x in (-6.4,6.4) for side in (-1,1)])
    for name,q,size,pos in (
      ('crossmember-joint-isolator',48,[.20,.0015,.18],[[x,s*(b/2+.01075),top-.09] for x in xs for s in (-1,1)]),
      ('bolster-joint-isolator',4,[.42,.0015,.36],[[x,s*(b/2+.01075),top-.18] for x in (-6.4,6.4) for s in (-1,1)])):
        m=prod(size)*1400.;add(name,q,dict(kind='box',size_m=size),'body/polymer',pos,mass={c:m*f for c,f in zip(model.CASES,(.8,1,1.3))},description='Nonconductive compression/creep-qualified interface material required; density1400kg/m3 is a sizing hypothesis')
    # Captive steel studs are welded only to their steel backing plate, never
    # directly to an aluminium girder. Fit backplates and both isolation layers
    # before closing the top flange; replacement needs workshop access.
    add('crossmember-steel-backing',48,dict(kind='box',size_m=[.20,.010,.18]),'body/steel',
        [[x,s*(b/2-t-.0065),top-.09] for x in xs for s in (-1,1)],description='Captive steel M16 stud/backing plate behind isolated girder web; holes/retention and plate prying require detail')
    add('bolster-steel-backing',4,dict(kind='box',size_m=[.42,.010,.36]),'body/steel',
        [[x,s*(b/2-t-.0065),top-.18] for x in (-6.4,6.4) for s in (-1,1)],description='Captive steel M20 stud plate installed before top closure; no steel-to-aluminium weld')
    for name,q,size,pos in (
      ('crossmember-inner-isolator',48,[.20,.0015,.18],[[x,s*(b/2-t-.00075),top-.09] for x in xs for s in (-1,1)]),
      ('bolster-inner-isolator',4,[.42,.0015,.36],[[x,s*(b/2-t-.00075),top-.18] for x in (-6.4,6.4) for s in (-1,1)])):
        m=prod(size)*1400.;add(name,q,dict(kind='box',size_m=size),'body/polymer',pos,mass={c:m*k for c,k in zip(model.CASES,(.8,1,1.3))},description='Inner galvanic isolation; compression, creep, fire, sealing and fastener shoulder insulation remain gates')
    # New floor joint fixings; parent bolster fasteners are explicitly replaced
    # below, not counted a second time as a new set.
    stud_positions=[[x+dx,s*(b/2+.045),top+dz] for x in xs for s in (-1,1) for dx in (-.06,.06) for dz in (-.14,-.04)]
    for name,mass,q,size in (('floor-joint-M16-stud',.16,192,[.09,.024,.024]),('floor-joint-M16-nut',.035,192,[.024,.024,.014]),('floor-joint-M16-washer',.020,384,[.03,.03,.003])):
        if 'stud' in name:pos=[[x[0],(1 if x[1]>0 else -1)*(b/2-t-.0115+.045),x[2]] for x in stud_positions];R=model.RZ90
        elif 'nut' in name:pos=[[x[0],(1 if x[1]>0 else -1)*(b/2+.0495),x[2]] for x in stud_positions];R=model.RX90
        else:pos=[[x[0],(1 if x[1]>0 else -1)*(b/2+d),x[2]] for x in stud_positions for d in (.038,.041)];R=model.RX90
        add(name,q,dict(kind='envelope',size_m=size),'body/steel',pos,R,mass={c:mass*f for c,f in zip(model.CASES,(.8,1,1.25))},description='M16 nominal finished fixing envelope and bounded mass; steel-backplate stud weld grade, isolated shoulder, effective area, locking and retention must be specified/tested')
    bp=[[x+dx,s*(b/2+.045),top+dz] for x in (-6.4,6.4) for s in (-1,1) for dx in (-.15,-.05,.05,.15) for dz in (-.30,-.06)]
    for source,name,mass,q,size in (
      ('body/bolster-joint-bolt','bolster-joint-M20-stud',.30,32,[.10,.03,.03]),
      ('body/bolster-joint-nut','bolster-joint-M20-nut',.065,32,[.03,.03,.018]),
      ('body/bolster-joint-washer','bolster-joint-M20-washer',.04,64,[.037,.037,.004])):
        old=next(r for r in parent['parts'] if r['id']==source)
        if 'stud' in name:pos=[[x[0],(1 if x[1]>0 else -1)*(b/2-t-.0115+.05),x[2]] for x in bp];R=model.RZ90
        elif 'nut' in name:pos=[[x[0],(1 if x[1]>0 else -1)*(b/2+.0535),x[2]] for x in bp];R=model.RX90
        else:pos=[[x[0],(1 if x[1]>0 else -1)*(b/2+d),x[2]] for x in bp for d in (.0385,.0425)];R=model.RX90
        new=add(name,q,dict(kind='envelope',size_m=size),'body/steel',pos,R,mass={c:mass*f for c,f in zip(model.CASES,(.8,1,1.25))});new.update(source_part_id=source,assembly_id='body/underframe')
        revisions.append(dict(source_part_id=source,old_part_id=source,new_part_id=new['id'],old_quantity_per_train=old['quantity_per_train'],new_quantity_per_train=new['quantity_per_train'],reason='Specified M20 stud joint replaces prior ungraded bolt mass/envelope, no duplicated hardware',old_mass_kg={c:old['mass_each_kg'][c]*old['quantity_per_train'] for c in model.CASES},new_mass_kg={c:new['mass_each_kg'][c]*new['quantity_per_train'] for c in model.CASES}))
    # Explicit deposited weld metal for corner, diaphragm and longitudinal
    # butt seams; no implicit free weld or double-counted existing filler.
    weld_length=4*17+2*fsum(2*((b-2*t)+(depth_at(x+8.5,family)-2*t)) for x in stations)+4*2*(b+h)
    deposit=weld_length*(.006**2/2)*family['rho']
    add('girder-weld-deposit',1,dict(kind='envelope',size_m=[17,b,h]),family['material'],[[0.,0.,top-h/2]],mass={c:deposit*f for c,f in zip(model.CASES,(.8,1,1.5))},description='Separate retained weld deposit for proposed6mm fillets and butt seams; procedure, throat, distortion and NDT are open')
    replaced={v['old_part_id'] for v in revisions}
    for old in parent['parts']:
        if old['assembly_id']=='services/secondary':removed.append(dict(part_id=old['id'],source_part_id=old['source_part_id'],quantity_per_train=old['quantity_per_train'],mass_kg={c:old['mass_each_kg'][c]*old['quantity_per_train'] for c in model.CASES},reason='Unused passive secondary explicitly removed only in powered-wheel research configuration'))
    removed_ids={r['part_id'] for r in removed}
    unchanged=[deepcopy(r) for r in parent['parts'] if r['id'] not in replaced|removed_ids]
    return unchanged+parts,placements,revisions,removed,dict(stub_length_m=stub,diaphragms_per_car=n,weld_length_m=weld_length,weld_deposit_base_kg=deposit,pod_joint_gap_m=.425-(b/2-t-.0115+.100))


def section(f):
    b,h,t=f['b'],f['h'],f['t'];I=(b*h**3-(b-2*t)*(h-2*t)**3)/12
    A=b*h-(b-2*t)*(h-2*t);J=4*((b-t)*(h-t))**2/(2*(b-t)/t+2*(h-t)/t)
    return dict(area_m2=A,I_vertical_m4=I,J_thinwall_m4=J,EI_Nm2=f['E']*I,GJ_Nm2=f['E']/(2*(1+f['nu']))*J,
        ideal_flange_elastic_buckling_Pa=4*pi*pi*f['E']/(12*(1-f['nu']**2))*(t/(b-2*t))**2,
        buckling_derating_hypothesis=.5)


def depth_at(x,f):
    a=abs(x-8.5)
    return f['h'] if a<=4.4 else .34 if a>=5.2 else f['h']-(f['h']-.34)*(a-4.4)/.8


def beam(q,EI,n=1700,section_family=None):
    """Trapezoidal curvature integration, finite compliant splice regions."""
    a,b=ASSUMPTIONS['support_x_m'];L=17.;dx=L/n;xs=[i*dx for i in range(n+1)];R=q*L/2
    moment=[R*max(x-a,0)+R*max(x-b,0)-q*x*x/2 for x in xs]
    curvature=[]
    for x,m in zip(xs,moment):
        factor=ASSUMPTIONS['splice_local_EI_fraction'] if any(abs(x-v)<=.15+1e-10 for v in ASSUMPTIONS['weld_splice_x_m']) else 1.
        if section_family is not None:
            h=depth_at(x,section_family);width=section_family['b'];t=section_family['t']
            I=(width*h**3-(width-2*t)*(h-2*t)**3)/12
            factor*=I/section(section_family)['I_vertical_m4']
        curvature.append(m/(EI*factor))
    slope=[0.];u=[0.]
    for i in range(n):slope.append(slope[-1]+(curvature[i]+curvature[i+1])*dx/2);u.append(u[-1]+(slope[-1]+slope[-2])*dx/2)
    ua=u[round(a/dx)];ub=u[round(b/dx)];c1=-(ub-ua)/(b-a);c0=-ua-c1*a
    y=[v+c0+c1*x for x,v in zip(xs,u)]
    maximum_stress=None
    if section_family is not None:
        width=section_family['b'];t=section_family['t'];maximum_stress=max(abs(m)*depth_at(x,section_family)/2/((width*depth_at(x,section_family)**3-(width-2*t)*(depth_at(x,section_family)-2*t)**3)/12)/ASSUMPTIONS['net_section_I_fraction_hypothesis'] for x,m in zip(xs,moment))
    return dict(variable_section_max_stress_Pa=maximum_stress,maximum_bending_moment_Nm=max(abs(x) for x in moment),maximum_relative_deflection_m=max(abs(v) for x,v in zip(xs,y) if a<=x<=b),midspan_relative_deflection_m=abs(y[n//2]),
        maximum_curvature_1_m=max(abs(v) for v in curvature),support_reaction_N=R,
        finite_splice_extra_rotation_rad=[abs(moment[round(v/dx)])*.30/EI for v in ASSUMPTIONS['weld_splice_x_m']],
        vertical_support_settlement_m=R/ASSUMPTIONS['bogie_connection_stiffness_N_m']+ASSUMPTIONS['bogie_connection_bearing_slip_m'])



def torsion_compliance(f):
    # Integrate 1/GJ over the half support span; full lateral torque is a
    # conservative constant along this path. No free rigid haunch is assumed.
    values=[]
    for i in range(641):
        d=depth_at(8.5+i*.01,f);t=f['t'];b=f['b'];J=4*((b-t)*(d-t))**2/(2*(b-t)/t+2*(d-t)/t)
        values.append(1/(f['E']/(2*(1+f['nu']))*J))
    return fsum((a+b)*.005 for a,b in zip(values,values[1:]))

def _stock_mass(parts,c):return fsum(r['quantity_per_train']*r['mass_each_kg'][c] for r in parts)


def screen(parent,f):
    parts,positions,revisions,removed,detail=definitions(parent,f);s=section(f);cases=[]
    parent_bogie={c:fsum(p['mass_kg'][c] for p in parent['patterns'] if p['bogie_index'] is not None) for c in model.CASES}
    for kind in ('normal','crowd-control'):
        for c in model.CASES:
            old=next(r for r in parent['mass_scenarios'] if r['name']==kind+'-'+c)
            delta=_stock_mass(parts,c)-parent['nominal_part_mass_kg'][c]
            body=(old['train_mass_kg']+delta-parent_bogie[c]+ADDITIONS['drive_BOP_train_kg'][c]+ADDITIONS['capture_interface_train_kg'][c])/6
            for loading in ('body-mounted-additions','all-added-on-body-conservative'):
                m=body+(9552/6 if loading.startswith('all') else 0);b=beam(m*9.80665/17,s['EI_Nm2'],section_family=f);stress=b['variable_section_max_stress_Pa']
                buckling_limit=s['ideal_flange_elastic_buckling_Pa']*.5;ground=.9595-f['h']-b['maximum_relative_deflection_m']-b['vertical_support_settlement_m']-.04-.02
                chord=b['maximum_curvature_1_m']*1.64**2/8
                # Upper bound: full lateral body force at z=2.2m, 1m above
                # the girder shear centre, transferred for half support span.
                torque=m*.5*(2.2-(.9595-f['h']/2));twist=torque*torsion_compliance(f)/.75;roll=twist*1.315
                F=b['support_reaction_N']/2;M=F*(.75-(f['b']/2+.0365));T=M/(.24*4);V=F/8
                bolt_interaction=(T/(245e-6*400e6))**2+(V/(245e-6*230e6))**2
                stub_force=m*9.80665/48;I=(.10*.18**3-.088*.168**3)/12
                stub_stress=stub_force*detail['stub_length_m']*.09/I
                stub_delta=stub_force*detail['stub_length_m']**3/(3*69e9*I)+stub_force/20e6+.0005
                floor_T=stub_force*detail['stub_length_m']/(2*.10);floor_V=stub_force/4
                bolster_I=(.30*.1895**3-.268*.1575**3)/12
                bolster_stress=M*(.1895/2)/bolster_I
                bolster_delta=F*(.75-(f['b']/2+.0365))**3/(3*69e9*bolster_I)
                ground-=bolster_delta
                floor_interaction=(floor_T/(157e-6*400e6))**2+(floor_V/(157e-6*230e6))**2
                floor_plate_stress=floor_T*.03/(.20*.025**2/6)
                bolster_plate_stress=T*.03/(.42*.025**2/6)
                sag_limit=.020 if kind=='normal' else .040
                passes=dict(material_stress=stress<=f['stress_limit'],local_flange_buckling=stress<=buckling_limit,
                    provisional_ground_allocation=ground>=.200,provisional_sag_allocation=b['maximum_relative_deflection_m']<=sag_limit,
                    local_door_chord=chord<=.002,provisional_torsion_roll=roll<=.003,bolster_stud_interaction=bolt_interaction<=1.,
                    floor_stub_stress=stub_stress<=55e6,bolster_stub_stress=bolster_stress<=55e6,bolster_local_deflection=bolster_delta<=.005,bogie_known_stock_clearance=(.9595-.34-.539-.04-b['vertical_support_settlement_m'])>=.02,inner_axle_clearance=(.9595-.34-.47-.04-b['vertical_support_settlement_m'])>=.02,M16_stud_interaction=floor_interaction<=1.,floor_endplate_strip_stress=floor_plate_stress<=55e6,bolster_endplate_strip_stress=bolster_plate_stress<=55e6,floor_stub_local_deflection=stub_delta<=.005,pod_joint_gap=detail['pod_joint_gap_m']>=.020)
                cases.append(dict(name=kind+'-'+c+'/'+loading,body_supported_mass_kg=m,beam=b,max_stress_Pa=stress,buckling_screen_limit_Pa=buckling_limit,
                    minimum_dynamic_ground_allocation_m=ground,door_chord_deviation_m=chord,door_roll_displacement_m=roll,
                    bolster_stud_tension_N=T,bolster_stud_shear_N=V,bolt_interaction=bolt_interaction,
                    bolster_stub_stress_Pa=bolster_stress,bolster_local_deflection_m=bolster_delta,floor_stub_force_N=stub_force,floor_stud_tension_N=floor_T,floor_stud_shear_N=floor_V,floor_stud_interaction=floor_interaction,floor_endplate_strip_stress_Pa=floor_plate_stress,bolster_endplate_strip_stress_Pa=bolster_plate_stress,floor_stub_stress_Pa=stub_stress,floor_stub_displacement_m=stub_delta,
                    screens=passes,passed_under_declared_hypotheses=all(passes.values()),engineering_accepted=False))
    return dict(family=f,section=s,geometry=detail,cases=cases,nominal_mass_kg={c:_stock_mass(parts,c) for c in model.CASES},
        direct_parts_process_usd={c:fsum(r['quantity_per_train']*r['direct_cost_each_usd'][c] for r in parts) for c in model.CASES},
        passed_under_declared_hypotheses=all(c['passed_under_declared_hypotheses'] for c in cases),**FLAGS)


def _scenario(patterns,p,kind,case,additions=False):
    rows=model._scenario_rows(patterns,'crowd' if kind=='crowd-control' else kind,p)
    if additions:
        for car in range(6):
            for key,z in (('drive_BOP_train_kg',.7),('capture_interface_train_kg',.45)):
                rows.append(dict(id=f'root-allowance/{key}/{car}',mass_kg={c:ADDITIONS[key][c]/6 for c in model.CASES},
                    centroid_m=[8.5+17.65*car,0.,z],uncertainty_m=[3.,.8,.4],shape_I_per_kg=[[0.]*3 for _ in range(3)],car_allocation=[[car,1.]],bogie_index=None))
            for bogie in range(2):
                bx=8.5+17.65*car+(-6.4 if bogie==0 else 6.4);x=bx-1.05
                rows.append(dict(id=f'root-allowance/drive-axle/{car}/{bogie}',mass_kg={c:796. for c in model.CASES},
                    centroid_m=[x,0.,.5],uncertainty_m=[.5,.7,.3],shape_I_per_kg=[[0.]*3 for _ in range(3)],car_allocation=[[car,1.]],bogie_index=car*2+bogie))
    props=model.mass_properties(rows,case);load=model.reactions(rows,case,p);cars=[]
    for car in range(6):
        own=[]
        for r in rows:
            share=next((f for c,f in r['car_allocation'] if c==car),0.)
            if share:own.append(dict(r,mass_kg={c:r['mass_kg'][c]*share for c in model.CASES}))
        cars.append(dict(car=car,**model.mass_properties(own,case)))
    return dict(name=kind+'-'+case,case=case,load_kind=kind,train_mass_kg=props['mass_kg'],CG_m=props['CG_m'],inertia_about_CG_kg_m2=props['inertia_about_CG_kg_m2'],cars=cars,
        axles=load['axles'],static_supports=load['cars'],force_residual_N=load['force_residual_N'],moment_residual_Nm=load['moment_residual_Nm'],
        minimum_axle_force_N=load['minimum_axle_force_N'],lateral_acceleration_m_s2=.5,hardware_additions_included=additions,
        hardware_geometry_and_mounts_admitted=False,physical_accepted=False)


def build(parent,*,family_id=None):
    if parent.get('candidate_id')!=PARENT or identity(parent['physical_definition'])!=PARENT or identity({k:v for k,v in parent.items() if k!='evaluation_id'})!=parent['evaluation_id']:raise ValueError('Sealed same-physical parent required')
    before=model.sources();parent=deepcopy(parent)
    parent['policy']['track_interface']=model.track_interface(model.policy())
    parent['policy']['layout']['battery_y_m']=[-.975,-.575,.575,.975];parent['policy']['layout']['battery_service_slack_m']=.275;trials=[screen(parent,f) for f in FAMILIES]
    if family_id is None:
        eligible=[r for r in trials if r['passed_under_declared_hypotheses']]
        if not eligible:raise ValueError('No screened family: preserve failures and request refinement')
        family_id=min(eligible,key=lambda r:r['direct_parts_process_usd']['base'])['family']['id']
    trial=next((r for r in trials if r['family']['id']==family_id),None)
    if trial is None or not trial['passed_under_declared_hypotheses']:raise ValueError('Only a screened hypothesis may proceed to detailing')
    f=trial['family'];parts,placements,revisions,removed,detail=definitions(parent,f);new_ids=set(placements)
    deleted={r['old_part_id'] for r in revisions}|{r['part_id'] for r in removed}
    patterns=[deepcopy(r) for r in parent['patterns'] if r['part_id'] not in deleted and r['assembly_id']!='services/battery']
    # Preserve frozen parent evidence, but explicitly revise its mistaken wheel
    # envelope orientation and gauge-vs-contact-centre placement in this child.
    by_part={part['id']:part for part in parts}
    for i,old in enumerate(patterns):
        if old['part_id']!='running/wheel':continue
        part=by_part[old['part_id']]
        a=next(a for a in parent['assembly_occurrences'][part['assembly_id']] if a['id']==old['assembly_occurrence_id'])
        wheel=[model.placement(part,a,j,parent['policy'],'thin-distributed') for j in range(part['quantity_per_assembly'])]
        patterns[i]=model._moments_for_pattern(part,a,[v[0] for v in wheel],wheel[0][1],model.geometry(part),parent['policy'])
    # Explicit25mm outward shift of the two inner pod rows clears the counted
    # joint stud/nut envelopes. No battery/module count or capacity change.
    for part in parts:
        if part['assembly_id']!='services/battery':continue
        for a in parent['assembly_occurrences']['services/battery']:
            placements_b=[model.placement(part,a,j,parent['policy'],'thin-distributed') for j in range(part['quantity_per_assembly'])]
            patterns.append(model._moments_for_pattern(part,a,[v[0] for v in placements_b],placements_b[0][1],model.geometry(part),parent['policy']))
    anchors=[]
    for car in range(6):anchors.append(dict(id=f'installation/central-girder/{car}',at_m=[8.5+car*17.65,0.,0.],car_allocation=[[car,1.]],local_origin_m=[0.,0.,0.]))
    for part in parts:
        if part['id'] not in new_ids:continue
        positions,R=placements[part['id']];g=model.geometry(part)
        if 'finished_profile_xz_m' in part:g['finished_profile_xz_m']=part['finished_profile_xz_m'];g['finished_cut_scope']='Taper cut from gross rectangular blank; mass accounting remains conservative gross stock'
        for anchor in anchors:
            world=[[at[k]+anchor['at_m'][k] for k in range(3)] for at in positions]
            patterns.append(model._moments_for_pattern(part,anchor,world,R,g,parent['policy']))
    for part in parts:
        if sum(r['count'] for r in patterns if r['part_id']==part['id'])!=part['quantity_per_train']:raise ValueError('Revision occurrence coverage differs')
    present={p['source_part_id'] for p in parts if p['source_part_id']};removed_origins={p['source_part_id'] for p in removed}
    expected={p['source_part_id'] for p in parent['parts'] if p['source_part_id']}
    if present&removed_origins or present|removed_origins!=expected:raise ValueError('Ancestor source origin must appear once or have explicit removal')
    physical=dict(schema='osr-underframe-revision-physical/1',parent_candidate_id=parent['candidate_id'],
        research_architecture='Powered-wheel body revision, no retained passive aluminium secondary; motor housings/mounts remain outside body admission',
        coordinate_frame=deepcopy(parent['physical_definition']['coordinate_frame']),layout=deepcopy(parent['policy']['layout']),battery_revision='Inner pod rows moved25mm outward, service slack0.3→0.275m; same75modules and fifteenpods/car, connectors/route qualification pending',
        track_interface=model.track_interface(parent['policy']),
        running_interface_revision=dict(parent_wheel_centres_y_m=[-.7175,.7175],
            parent_wheel_rotation=model.RZ90,new_wheel_rotation=model.I,
            reason='Correct nominal rail-head contact datums and the 135 mm-wide wheel blank axle direction. Actual wheel tread/flange design remains unverified.'),
        structural_family={k:f[k] for k in ('id','b','h','t','material')},
        removed_source_parts=removed,part_revisions=revisions,
        proposed_components=[{k:r[k] for k in ('id','source_part_id','component_definition_id','quantity_per_train','material_id','stock')} for r in parts],
        occurrence_patterns=[{k:r[k] for k in ('id','part_id','count','positions_m','rotation','geometry','car_allocation','bogie_index')} for r in patterns])
    cid=identity(physical);scenarios=[];outer={}
    for kind in ('tare','normal','crowd-control'):
        rows=model._scenario_rows(patterns,'crowd' if kind=='crowd-control' else kind,parent['policy'])
        outer[kind]=dict(CG_outer_box_m=[[model._cg_bound(rows,a,False),model._cg_bound(rows,a,True)] for a in range(3)],
            mass_interval_kg=[fsum(r['mass_kg'][c] for r in rows) for c in ('low','high')],scope='Independent bounded material/position/reserve hypotheses; not measured physical limits')
        for c in model.CASES:scenarios.append(_scenario(patterns,parent['policy'],kind,c))
    uncertainty=dict()
    # Material/position intervals remain active; diagonal inertia is additionally
    # bounded above by all point masses at the farthest declared zone radius.
    for kind in outer:
        rows=model._scenario_rows(patterns,'crowd' if kind=='crowd-control' else kind,parent['policy']);box=outer[kind]['CG_outer_box_m']
        outer[kind]['inertia_diagonal_outer_intervals_kg_m2']=[[0.,fsum(r['mass_kg']['high']*(3*r['shape_I_per_kg'][a][a]+sum((max(abs(r['centroid_m'][j]-box[j][0]),abs(r['centroid_m'][j]-box[j][1]))+r['uncertainty_m'][j])**2 for j in range(3) if j!=a)) for r in rows)] for a in range(3)]
    interfaces=model.interfaces(parent['policy']);interfaces['passive_aluminium_secondary']='All nine source secondary part types explicitly removed in this powered-wheel research revision; passive development reference unchanged'
    interfaces['central_girder']=dict(width_m=f['b'],depth_m=f['h'],top_z_m=.9595,bottom_z_m=.9595-f['h'],outer_depth_m=.34,taper_local_x_m=[4.4,5.2],bogie_secondary_clearance_after_jounce_m=.9595-.34-.539-.04,inner_axle_clearance_after_jounce_m=.9595-.34-.47-.04,pod_joint_gap_m=detail['pod_joint_gap_m'],
        motor_or_gear_installation_clearance_verified=False,actual_body_joint_qualification=False)
    selection=dict(purpose='Next experiment and research detailing, not integrated baseline',selected_family=family_id,
        rationale='Lowest calculated direct factory cost among families passing all declared bounded screens; failed lighter aluminium remains a refinement task, not admitted Pareto selection',
        nondominated_families=[r['family']['id'] for r in trials if r['passed_under_declared_hypotheses'] and not any(o['passed_under_declared_hypotheses'] and o['nominal_mass_kg']['base']<=r['nominal_mass_kg']['base'] and o['direct_parts_process_usd']['base']<=r['direct_parts_process_usd']['base'] and o['family']['id']!=r['family']['id'] for o in trials)],
        independently_selected_for_baseline=False)
    res=dict(schema='osr-vehicle-installation/1',candidate_id=cid,physical_definition=physical,parent_candidate_id=parent['candidate_id'],parent_evaluation_id=parent['evaluation_id'],parent_bundle_id=parent['parent_bundle_id'],
        source_component_types=605,proposed_component_types=len(parts),materials=deepcopy(parent['materials']),parts=parts,patterns=patterns,
        assembly_occurrences=dict({k:v for k,v in parent['assembly_occurrences'].items() if k!='services/secondary'},**{'installation/central-girder':anchors}),
        removed_parts=removed,revisions=revisions,mass_scenarios=scenarios,mass_uncertainty=outer,nominal_part_mass_kg={c:_stock_mass(parts,c) for c in model.CASES},
        source_part_mass_kg=deepcopy(parent['nominal_part_mass_kg']),direct_parts_process_usd=trial['direct_parts_process_usd'],source_direct_parts_process_usd=deepcopy(parent['direct_parts_process_usd']),
        exact_stock_types=sum(model.geometry(r)['exact_stock'] for r in parts),unknown_finished_geometry_types=sum(not model.geometry(r)['exact_stock'] for r in parts),
        total_occurrences=sum(r['count'] for r in patterns),source_part_coverage_complete=True,source_origins_explicitly_removed=len(removed_origins),layout_definition_complete=True,
        interface_screens=interfaces,assembly_plans=dict(revised_plans(parent,parts,revisions),underframe_revision=dict(
            operations=['Cut/mark 3 longitudinal blanks per flange/web and prepare full-penetration butt grooves',
                'Fit shallow ends and tapered haunch before bogie axle envelope; jig bottom flange and webs; fit/weld all internal diaphragms, steel backing/stud plates and both isolation layers',
                'Inspect/record accessible internal seams and backing retention before closing top flange',
                'Close/weld top flange under distortion-controlled sequence; NDT butt seams and survey bogie/door datums',
                'Attach isolated stub crossmembers and bolsters; torque/lock/mark all stud nuts with retained access',
                'Attach side sills/floor stringers, then fit pods with required joint access clearance and removal sequencing'],
            inspection=['Material/heat identity and qualified weld coupons','Stud/plate prying and bearing proof','Weld NDT, straightness, support datum and corrosion isolation','Loaded door/clearance measurement, fatigue and thermal cycling'],
            joins=dict(M16_floor_studs_per_train=1152,M20_bolster_studs_per_train=192,internal_diaphragms_per_train=detail['diaphragms_per_car']*6,
                backing_plates_per_train=312,bolts_are_counted_in_parts=True,steel_to_aluminium_welds_prohibited=True),
            tool_access_verified=False,manufacturing_release=False)),
        structural_comparison=dict(assumptions=ASSUMPTIONS,trials=trials,selection=selection,
            original_sill_control=_original_control(parent),
            limits='Provisional functional allocations and unqualified material/joint bounds; no full-body, local shell, crash, fatigue, welding or physical acceptance'),
        powered_wheel_load_envelope=dict(assumptions=ADDITIONS,load_cases=[_scenario(patterns,parent['policy'],k,c,True) for k in ('tare','normal','crowd-control') for c in model.CASES],
            scope='Conditional mass/load evaluation only. Motors/gears, BOP and capture interface have no admitted installed geometry or actual force envelope'),
        policy=deepcopy(parent['policy']),source_sha256=before,
        assumptions=parent['assumptions']+['Central-girder-only stiffness, finite welded-splice compliance and support/joint slip; no side-sill or roof participation credited',
            'Both side sills are retained; new crossmember stubs transfer their local load into the central girder through counted joints',
            'Steel captive stud/backing plates and both isolation layers are fitted before aluminium box closure; steel-to-aluminium welds are prohibited',
            'Loads use body-only additions; all9552kgof bogie-mounted motor/gears on body is a separately retained conservative sensitivity',
            'Gross stock intersections and proposed joints need final cut/mating drawings; exact native stock volumes do not qualify final assembly'],**FLAGS)
    criteria=deepcopy(requirement_policy.catalogue()['criteria'])
    for uid,observable,limit,operator in (('target.underframe_sag','maximum_normal_sag_m',.020,'max'),('target.underframe_roll','maximum_crowd_roll_m',.003,'max'),('target.underframe_ground','minimum_allocated_ground_m',.200,'min')):
        criterion=deepcopy(criteria['target.global_deflection']);criterion.update(id=uid,observable=observable,limit=limit,operator=operator,
            basis='Explicit preliminary door/underfloor/ride allocation for this bounded study; no approved physical limit or independently authenticated evidence',provenance=None)
        criteria[uid]=criterion
    normal=[c for c in trial['cases'] if c['name'].startswith('normal')]
    res['requirement_assessment']=requirement_policy.assess(dict(maximum_normal_sag_m=max(c['beam']['maximum_relative_deflection_m'] for c in normal),
        maximum_crowd_roll_m=max(c['door_roll_displacement_m'] for c in trial['cases']),minimum_allocated_ground_m=min(c['minimum_dynamic_ground_allocation_m'] for c in trial['cases'])),criteria,candidate_id=cid)
    res['powered_wheel_load_envelope']['evaluation_id']=identity(res['powered_wheel_load_envelope'])
    if model.sources()!=before:raise ValueError('Sources changed during bounded structural revision')
    return model.seal(res,'evaluation_id')


def _original_control(parent):
    b,h,t=.18,.35,.008;I=2*(b*h**3-(b-2*t)*(h-2*t)**3)/12;EI=69e9*I
    out=[]
    for kind in ('normal','crowd-control'):
        old=next(r for r in parent['mass_scenarios'] if r['name']==kind+'-base');m=old['train_mass_kg']/6;q=m*9.80665/17
        L=12.8;a=2.1;d=(5*q*L**4/384-q*a*a*L*L/16)/EI
        out.append(dict(name=kind+'-base',midspan_deflection_m=d,historical_L_over_500_comparison_m=L/500,
            historical_comparison_passed=d<=L/500,scope='Historical isolated two-sill UDL reference using whole-car mass; retained failure, not a universal body rejection criterion'))
    return out


def cad_case(result):
    """First-car new underframe gross stock, no motor or guessed finished weld."""
    entities=[];expected={};wanted={'body/underframe','installation/central-girder'}
    for p in result['patterns']:
        if p['assembly_id'] not in wanted or p['car_allocation']!=[[0,1.]] or not p['geometry']['exact_stock']:continue
        g=p['geometry'];s=g['source_stock'];R=p['rotation'];L,b,h=g['size_m'];pieces=[([L,b,h],[0.,0.,0.])]
        profile=g.get('finished_profile_xz_m')
        if profile is None and any(abs(v) not in (0.,1.) for row in R for v in row):
            profile=[[R[0][0]*x+R[0][2]*z,R[2][0]*x+R[2][2]*z] for x,z in ((-L/2,-h/2),(L/2,-h/2),(L/2,h/2),(-L/2,h/2))]
        if profile is not None:
            pts=profile;area,cx,cz=polygon(pts)
            for i,at in enumerate(p['positions_m']):
                name=p['id']+f'/{i}/profile';entities.append(dict(id=name,shape='xz-profile-prism',at_m=at,points_xz_m=pts,thickness_m=b,material=p['material_id']))
                expected[name]=dict(volume_m3=area*b,centroid_m=[at[0]+cx,at[1],at[2]+cz],bounds_m=[[at[0]+min(v[0] for v in pts),at[1]-b/2,at[2]+min(v[1] for v in pts)],[at[0]+max(v[0] for v in pts),at[1]+b/2,at[2]+max(v[1] for v in pts)]],gross_stock_volume_m3=L*b*h)
            continue
        if s['kind']=='rhs':
            t=s['wall_m'];pieces=[]
            for side in (-1,1):pieces.extend((([L,t,h],[0.,side*(b-t)/2,0.]),([L,b-2*t,t],[0.,0.,side*(h-t)/2])))
        elif s['kind']!='box':raise ValueError('Underframe stock CAD only admits boxes and RHS')
        for i,at in enumerate(p['positions_m']):
            for j,(size,delta) in enumerate(pieces):
                centre=[at[a]+fsum(R[a][k]*delta[k] for k in range(3)) for a in range(3)];world=model.transformed_size(size,R);corner=[centre[a]-world[a]/2 for a in range(3)]
                name=p['id']+f'/{i}/wall-{j}';entities.append(dict(id=name,shape='box',at_m=corner,size_m=world,material=p['material_id']))
                expected[name]=dict(volume_m3=prod(size),centroid_m=centre,bounds_m=[corner,[corner[a]+world[a] for a in range(3)]])
    spec=dict(entities=entities,units='m')
    return dict(schema='osr-installed-underframe-stock-cad/1',case_id='powered-wheel-central-girder-and-stubs',candidate_id=result['candidate_id'],component_geometry_id=identity(spec),
        entities=entities,materials={m['id']:m for m in result['materials']},expected=dict(part_count=len(entities),part_measures=expected),
        scope='First-car gross plate/RHS stock plus explicit trapezoidal web cuts and proposed placements, each occurrence counted once; no finished holes/weld shape, fitted joint, motor housing or installed assembly qualification',**FLAGS)


def main(argv=None):
    import argparse,time
    from . import export
    a=argparse.ArgumentParser();a.add_argument('--parent',required=True,type=Path);a.add_argument('--output',required=True,type=Path);a.add_argument('--family',choices=[f['id'] for f in FAMILIES]);a.add_argument('--cad',action='store_true');args=a.parse_args(argv)
    start=time.monotonic();r=build(load_parent(args.parent),family_id=args.family);metadata=export.write(r,args.output)
    if args.cad:
        case=cad_case(r);export.native_cad(r,args.output/'native-cad',case=case,commands=cad_script(case))
    print(json.dumps(dict(candidate_id=r['candidate_id'],evaluation_id=r['evaluation_id'],manifest_id=metadata['manifest_id'],nominal_mass_kg=r['nominal_part_mass_kg'],elapsed_s=time.monotonic()-start),indent=2))
    return 0




def polygon(points):
    terms=[a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1])];signed=fsum(terms)/2
    if signed==0:raise ValueError('Nonzero closed profile area required')
    cx=fsum((a[0]+b[0])*v for a,b,v in zip(points,points[1:]+points[:1],terms))/(6*signed)
    cz=fsum((a[1]+b[1])*v for a,b,v in zip(points,points[1:]+points[:1],terms))/(6*signed)
    return abs(signed),cx,cz


def cad_script(case):
    from engineering.design_search.craft_backends import solidcraft
    basic=deepcopy(case);basic['entities']=[e for e in case['entities'] if e['shape']!='xz-profile-prism'];script=solidcraft.script_for(basic);script['commands'].pop()
    for e in case['entities']:
        if e['shape']!='xz-profile-prism':continue
        x,y,z=e['at_m'];t=e['thickness_m']
        script['commands'] += [dict(command='sketch.create',params=dict(plane=dict(origin=[1000*x,1000*(y+t/2),1000*z],x_dir=[1,0,0],y_dir=[0,0,1]),name=e['id'])),
            dict(command='sketch.line',params=dict(points=[[1000*v for v in p] for p in e['points_xz_m']],closed=True,infer=False)),dict(command='sketch.finish',params={}),
            dict(command='solid.extrude',params=dict(distance=1000*t,operation='new',body_name=e['id'])),
            dict(command='material.assign',params=dict(bodies=[e['id']],material='OSR '+e['material']))]
    script['commands'].append(dict(command='inspect.measure',params={}));return script




def revised_plans(parent,parts,revisions):
    plans=deepcopy(parent['assembly_plans']);mapping={r['old_part_id']:r['new_part_id'] for r in revisions}
    plans['plans']=[p for p in plans['plans'] if p['assembly_id']!='services/secondary']
    for plan in plans['plans']:
        selected=[p for p in parts if p['assembly_id']==plan['assembly_id']]
        plan['component_type_ids']=[p['id'] for p in selected]
        for step in plan['source_assembly_steps']:step['part_ids']=[mapping.get(v,v) for v in step['part_ids']]
        for label,spec in plan['inventory_categories'].items():
            spec['part_ids']=[mapping.get(v,v) for v in spec['part_ids']]
            spec['quantity_per_train']=sum(p['quantity_per_train'] for p in selected if p['id'] in spec['part_ids'])
    new=[p for p in parts if p['assembly_id']=='installation/central-girder']
    plans['plans'].append(dict(assembly_id='installation/central-girder',occurrences=6,component_type_ids=[p['id'] for p in new],
        source_assembly_steps=[dict(sequence=1,operation='Prepare counted flanges, tapered webs and diaphragms',part_ids=[p['id'] for p in new if any(v in p['id'] for v in ('girder-','diaphragm'))],tools='Controlled cutting, weld fixture, survey and NDT'),
            dict(sequence=2,operation='Fit and isolate captive backing/stud plates before closure',part_ids=[p['id'] for p in new if any(v in p['id'] for v in ('backing','isolator','stud'))],tools='Assembly jig, insulation check and torque tools'),
            dict(sequence=3,operation='Attach stubs and air-spring seats, inspect bearing and restraint',part_ids=[p['id'] for p in new if p['id'].endswith(('cleat','endplate','seat'))],tools='Body stands, retained support, survey and torque tooling')],
        interfaces=[dict(mates_with='body/underframe',description='Counted studs, cleats, isolation and captive backing plates; both bending and local load transfer screened under hypotheses'),dict(mates_with='running/secondary-support',description='Four0.46m seats per car touch spring topz.760m, bolster undersidez.770m; measured jounce/roll/fatigue gates open')],
        inventory_categories={},source_removal_sequence='Workshop support and datum fixture required; isolate services and remove obstructing pods before access; no unsupported body or live disconnection',
        tool_and_lifting_access=dict(required=True,verified=False,lifting_points_and_load_rating_verified=False),open_tasks=['Weld fatigue, residual stress and local hole/plate shell FEM; thermal protection/temperature records for preinstalled isolation during closure welding','Stud/backing prying and isolator creep proof','Measured axle/spring/body kinematics and clearance'],installation_accepted=False))
    plans['battery_service']['connector_slack_m']=.275
    return plans


if __name__=='__main__':raise SystemExit(main())
