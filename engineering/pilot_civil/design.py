"""Moving-axle civil assemblies with explicit prestress and erection hypotheses.

Gross uncracked service calculations are a screen, not strength acceptance.
No old beam FEM result is inherited by these new installed civil assemblies.
"""
from copy import deepcopy
from math import ceil,fsum,isfinite,pi,sqrt,cos,sin
from pathlib import Path
import gzip,json
from engineering.station_rail.common import identity,digest,encoded
from engineering.design_search import civil_shape_geometry as geometry
from engineering.station_pair import coordinator as pair
from . import ROOT,FLAGS
G=9.80665
CASES=('low','base','high')
POLICY='engineering/pilot_civil/policy.json'


def seal(v,key='evaluation_id'):
    v[key]=identity(v);return v


def sources(root=ROOT):
    names=sorted(str(n.relative_to(root)) for n in (Path(root)/'engineering/pilot_civil').glob('*') if n.suffix in ('.py','.json'))+['engineering/design_search/civil_shape_geometry.py','engineering/station_rail/common.py']
    return {n:digest(Path(root)/n) for n in names}


def specification(root=ROOT):
    p=json.loads((Path(root)/POLICY).read_bytes())
    if p['schema']!='osr-pilot-civil-policy/1' or p['span_m']!=20 or p['tracks']!=2:raise ValueError('Declared common20m two-track pilot required')
    if not 1<=p['moving_positions']<=1000 or not 2<=p['observations']<=201:raise ValueError('Bounded moving-load discretisation required')
    def check(x,path=""):
        if isinstance(x,dict):
            for k,y in x.items():check(y,path+"/"+k)
        elif isinstance(x,list):
            for y in x:check(y,path)
        elif type(x) in (float,int) and (not isfinite(x) or x<0 and not path.endswith(('bearing_longitudinal_offsets_m','bearing_lateral_offsets_m'))):raise ValueError('Finite nonnegative civil hypothesis required')
    # Coordinates may be signed; all other dimensions/rates are nonnegative.
    check({k:v for k,v in p.items() if k!='track_centres_y_m'})
    if not 0<p['prestress']['effective_fraction_of_jack']<=p['prestress']['transfer_fraction_of_jack']<=1:raise ValueError('Explicit prestress losses required')
    return p


def baseline_train(root=ROOT):
    """Current exact parts pilot, not the future installed-body proposal."""
    brief,bundle,mass,variants=pair.variants(root)
    v=next(x for x in variants if x['family']=='powered-wheel' and x['geometry']['driven_axles']==12 and x['physical_definition']['station_spacing_m']==1500)
    loads=[]
    for name in CASES:
        row=next(r for r in mass['mass_scenarios'] if r['case']==name)
        total=row['conditional_accounted_train_mass_kg']+brief['normal_people']*brief['passenger_mass_kg']+v['onboard_added_mass_kg'][name]
        axles=[dict(id=f'car-{c+1}/bogie-{b+1}/axle-{a+1}',x_m=8.5+17.65*c+centre+offset,vertical_force_N=total*G/24) for c in range(6) for b,centre in enumerate((-6.4,6.4)) for a,offset in enumerate((-1.05,1.05))]
        loads.append(dict(name='normal-'+name,train_mass_kg=total,axles=axles,CG_m=[52.625,0.,1.8],lateral_acceleration_m_s2=.5))
    return seal(dict(schema='osr-pilot-axle-loads/1',candidate_id=v['candidate_id'],vehicle_candidate_id=bundle['candidate_id'],mass_evaluation_id=mass['evaluation_id'],load_cases=loads,
        axle_force_basis='Static full axle across both rails; equal share is a provisional baseline only',CG_basis='Explicit1.8m lateral torque sensitivity; not located CG',source_sha256=pair.source_hashes(root),**FLAGS))


def validate_train(train,root=ROOT):
    if train.get('schema')!='osr-pilot-axle-loads/1' or train.get('evaluation_id')!=identity({k:v for k,v in train.items() if k!='evaluation_id'}):raise ValueError('Sealed same-candidate axle input required')
    for key in ('candidate_id','vehicle_candidate_id','mass_evaluation_id'):
        if not isinstance(train.get(key),str) or len(train[key])!=64 or any(c not in '0123456789abcdef' for c in train[key]):raise ValueError('Exact candidate and mass IDs required')
    if not train['load_cases']:raise ValueError('Named load cases required')
    if len({l['name'] for l in train['load_cases']})!=len(train['load_cases']):raise ValueError('Unique load case names required')
    for load in train['load_cases']:
        if not load['axles'] or len(load['axles'])>128 or len({a['id'] for a in load['axles']})!=len(load['axles']):raise ValueError('Bounded unique static axle inventory required')
        for x in [load['train_mass_kg'],load['lateral_acceleration_m_s2'],*load['CG_m'],*[v for a in load['axles'] for v in (a['x_m'],a['vertical_force_N'])]]:
            if type(x) not in (int,float) or not isfinite(x):raise ValueError('Finite SI axle/CG inputs required')
        if load['train_mass_kg']<=0 or min(a['vertical_force_N'] for a in load['axles'])<=0:raise ValueError('Positive masses and full axle loads required')
        if load['lateral_acceleration_m_s2']<0 or load['CG_m'][2]<0 or min(a['x_m'] for a in load['axles'])<0:raise ValueError('Nonnegative lateral magnitude, railhead CG height and nose-to-tail axle x required')
        residual=fsum(a['vertical_force_N'] for a in load['axles'])-load['train_mass_kg']*G
        if abs(residual)>1e-7*load['train_mass_kg']*G:raise ValueError('Full-axle forces do not conserve supplied train mass')
    if any(train.get(k,False) is not False for k in FLAGS):raise ValueError('Load model cannot grant physical acceptance')
    for name,want in train.get('source_sha256',{}).items():
        path=Path(name)
        if path.is_absolute() or '..' in path.parts or digest(Path(root)/path)!=want:raise ValueError('Axle-load upstream source differs')
    return True


def section(family,revision='source'):
    p=geometry.generate(family,'reference')
    parent=p['candidate_id']
    if revision=='thick-web':
        if family!='folded_plate':raise ValueError('Only folded web revision supported')
        for s in p['cells'][0]['sections']:
            if 'web' in s['id']:
                if 'left' in s['id']:s['polygon_yz_m']=[[-.8,-.16],[-.35,-1.24],[-.15,-1.24],[-.6,-.16]]
                else:s['polygon_yz_m']=[[.8,-.16],[.35,-1.24],[.15,-1.24],[.6,-.16]]
        p['cells'][0]['sections'][0]['polygon_yz_m']=[[-1.,-.16],[1.,-.16],[1.,0.],[-1.,0.]]
        p['cells'][0]['sections'][1]['polygon_yz_m']=[[-.35,-1.4],[.35,-1.4],[.35,-1.24],[-.35,-1.24]]
        p['provenance']['method']='Physical foldeddepth1250→1400mm, flanges140→160mm, webs140→200mm; stiffness and duct-cover revision'
        p.pop('candidate_id');p=seal(p,'candidate_id');geometry.validate(p)
    elif revision!='source':raise ValueError('Explicit source or physical thick-web revision required')
    q=geometry.quantities(p);z=q['centroid_m'][2];Iy=q['by_material']['research_concrete']['I_y_m4'];Iz=q['by_material']['research_concrete']['I_z_m4'];area=q['total_nominal_volume_m3']/20
    zmin=min(z for c in p['cells'] for s in c['sections'] for _,z in s['polygon_yz_m'])
    if family=='reference_box':
        wall=.18;bm=2-wall;hm=1.4-wall;J=4*(bm*hm)**2/(2*(bm+hm)/wall);webcover=wall/2-.03;Am=bm*hm;sheararea=2*wall*(1.4-2*wall);thinwall=wall
    else:
        wall=.20 if revision=='thick-web' else .14
        depth=1.4 if revision=='thick-web' else 1.25;flange=.16 if revision=='thick-web' else .14
        web_height=depth-2*flange;web_length=sqrt(.45**2+web_height**2);normal_width=wall*web_height/web_length
        midheight=depth-flange;midtop=1.6-wall;midbottom=.7-wall;Am=(midtop+midbottom)/2*midheight
        J=4*Am*Am/(midtop/flange+midbottom/flange+2*sqrt(.45**2+midheight**2)/normal_width);webcover=normal_width/2-.03;sheararea=2*normal_width*web_height;thinwall=min(normal_width,flange)
    return dict(physical=p,parent_geometry_candidate_id=parent,quantities=q,area_m2=area,I_y_m4=Iy,I_z_m4=Iz,centroid_z_m=z,zmin_m=zmin,top_distance_m=-z,bottom_distance_m=z-zmin,torsion_J_thinwall_m4=J,
        duct_normal_cover_m=webcover,torsion_enclosed_median_area_m2=Am,effective_web_shear_area_m2=sheararea,minimum_normal_wall_m=thinwall,torsion_basis='Closed single-cell thin-wall approximation; local distortional/warping response and FEM torsion remain open')


def reinforcement(s,p):
    r=p['reinforcement'];span=p['span_m'];depth=-s['zmin_m'];cover=p['prestress']['concrete_cover_m']
    # Two match-cast segments: each has two overlapping bar pieces. No bar
    # lap crosses the 2 mm dry/epoxy joint; continuous PT carries that interface.
    segment_bar_length=span/2-2*cover+r['lap_length_m']
    longlength=r['longitudinal_bars']*2*segment_bar_length
    count=ceil((span-2*cover)/r['stirrup_pitch_m'])+1
    # Four bends with explicit bend arc and straight legs, two hook tails.
    R=r['bend_radius_to_diameter']*r['stirrup_diameter_m'];centre_cover=cover+r['stirrup_diameter_m']/2;h=depth-2*centre_cover
    if s['physical']['family']=='folded_plate':
        top=1.6-2*centre_cover;bottom=.7-2*centre_cover
        perimeter=top+bottom+2*sqrt(h*h+((top-bottom)/2)**2)
        cage=[[-top/2,-centre_cover],[top/2,-centre_cover],[bottom/2,-depth+centre_cover],[-bottom/2,-depth+centre_cover]]
    else:
        w=2-2*centre_cover;perimeter=2*(w+h)
        cage=[[-w/2,-centre_cover],[w/2,-centre_cover],[w/2,-depth+centre_cover],[-w/2,-depth+centre_cover]]
    # Fillet allowance is a cut-stock estimate. Exact bend geometry and bar
    # anchorage require a controlled bending schedule before fabrication.
    stirruplength=perimeter-8*R+2*pi*R+2*r['bend_tail_m']
    mass=p['steel_density_kg_m3']*(longlength*pi*r['longitudinal_bar_diameter_m']**2/4+count*stirruplength*pi*r['stirrup_diameter_m']**2/4)
    return dict(longitudinal_bars=r['longitudinal_bars'],longitudinal_cut_length_m=segment_bar_length/2,longitudinal_cut_pieces=4*r['longitudinal_bars'],longitudinal_total_m=longlength,
        stirrup_count=count,stirrup_cut_length_m=stirruplength,stirrup_pitch_m=(span-2*cover)/(count-1),bar_bend_radius_m=R,
        longitudinal_diameter_m=r['longitudinal_bar_diameter_m'],stirrup_diameter_m=r['stirrup_diameter_m'],mass_kg=mass,
        cage_path_yz_m=cage,stock_basis='Cut/bend stock; bar fit, anchorage and congestion not qualified',
        material='B500-class reinforcement research specification; certificates, anchorage, congestion and fatigue open')


def green(x,a,L):
    """Positive simply-supported Euler–Bernoulli displacement per P/EI."""
    if x>a:x,a=L-x,L-a
    b=L-a
    return b*x*(L*L-b*b-x*x)/(6*L)


def _response(points,w,a,b,EI):
    """Macaulay beam with free overhangs and two exact zero-displacement supports."""
    L=20.;span=b-a
    Ra=(w*L*(b-L/2)+fsum(P*(b-x) for x,P in points))/span
    Rb=w*L+fsum(P for x,P in points)-Ra
    def F(x):return (Ra*max(0.,x-a)**3/6+Rb*max(0.,x-b)**3/6-w*x**4/24-fsum(P*max(0.,x-xp)**3/6 for xp,P in points))/EI
    C1=-(F(b)-F(a))/span;C0=-F(a)-C1*a
    def y(x):return C0+C1*x+F(x)
    def moment(x):return Ra*max(0.,x-a)+Rb*max(0.,x-b)-w*x*x/2-fsum(P*max(0.,x-xp) for xp,P in points)
    return Ra,Rb,y,moment


def _moving(s,load,p,dead_mass_kg):
    L=p['span_m'];E=p['young_Pa'];EI=E*s['I_y_m4'];Gmod=E/(2*(1+p['poisson']));xs=[L*i/(p['observations']-1) for i in range(p['observations'])]
    a,b=p['support']['bearing_lines_x_m'];offsets=[q['x_m'] for q in load['axles']];start=-max(offsets);end=L-min(offsets)
    shifts=[start+(end-start)*i/(p['moving_positions']-1) for i in range(p['moving_positions'])]
    w=dead_mass_kg*G/L;env=dict(moment_Nm=0.,hogging_moment_Nm=0.,shear_N=0.,reaction_N=0.,deflection_m=0.,lateral_deflection_m=0.,torsion_Nm=0.,twist_rad=0.)
    critical={};moment_max=[-float('inf')]*len(xs);moment_min=[float('inf')]*len(xs);bearing_min=float('inf')
    for shift in shifts:
        points=[(q['x_m']+shift,q['vertical_force_N']*p['dynamic_axle_factor'],q['vertical_force_N']/G*load['lateral_acceleration_m_s2']) for q in load['axles'] if 0<=q['x_m']+shift<=L]
        Ra,Rb,y,M=_response([(x,P) for x,P,Fy in points],w,a,b,EI)
        _,_,ylat,_=_response([(x,Fy) for x,P,Fy in points],0.,a,b,E*s['I_z_m4'])
        obs=sorted(set(xs+[a,b]+[x for x,P,Fy in points]));knots=sorted(set([0.,a,b,L]+[x for x,P,Fy in points]))
        for lo,hi in zip(knots,knots[1:]):
            mid=(lo+hi)/2;zero=((Ra if mid>a else 0)+(Rb if mid>b else 0)-fsum(P for x,P,Fy in points if x<=mid))/w
            if lo<=zero<=hi:obs.append(zero)
        for j,x in enumerate(xs):moment_max[j]=max(moment_max[j],M(x));moment_min[j]=min(moment_min[j],M(x))
        torques=[(x,Fy*(load['CG_m'][2]+p['railhead_above_deck_m'])+P*p['vertical_load_eccentricity_m']) for x,P,Fy in points]
        TA=fsum(T*max(0.,min(b-x,b-a))/(b-a) for x,T in torques);TB=fsum(T for x,T in torques)-TA
        def twist(x):return (TA*max(0.,x-a)+TB*max(0.,x-b)-fsum(T*max(0.,x-xp) for xp,T in torques)+fsum(T*max(0.,a-xp) for xp,T in torques))/(Gmod*s['torsion_J_thinwall_m4'])
        spacing=abs(p['support']['bearing_lateral_offsets_m'][1]-p['support']['bearing_lateral_offsets_m'][0])
        bearing_min=min(bearing_min,Ra/2-abs(TA)/spacing,Rb/2-abs(TB)/spacing)
        values=dict(moment_Nm=max(M(x) for x in obs),hogging_moment_Nm=max(0.,-min(M(x) for x in obs)),shear_N=max(abs(Ra),abs(Rb)),reaction_N=max(Ra,Rb),
            deflection_m=max(abs(y(x)) for x in xs),lateral_deflection_m=max(abs(ylat(x)) for x in xs),torsion_Nm=max(abs(TA),abs(TB)),twist_rad=max(abs(twist(x)) for x in xs))
        for key,value in values.items():
            if value>env[key]:env[key]=value;critical[key]=shift
    shift_step=(end-start)/(p['moving_positions']-1);observe_step=L/(p['observations']-1);forces=fsum(q['vertical_force_N'] for q in load['axles'])*p['dynamic_axle_factor']
    # Conservative point-load Green sensitivity bound within the declared small
    # overhang construction domain; gross beam, not a bound on real bridge response.
    deflection_allowance=forces*L*L/(9*sqrt(3)*EI)*(shift_step+observe_step)/2+w*L**3/(24*EI)*observe_step/2
    return dict(**env,deflection_model_upper_m=env['deflection_m']+deflection_allowance,critical_train_translation_m=critical,
        moment_envelope_curve=[dict(x_m=x,moment_Nm=M,minimum_moment_Nm=mn) for x,M,mn in zip(xs,moment_max,moment_min)],
        minimum_bearing_compression_N=bearing_min,dead_udl_N_m=w,dead_mass_kg=dead_mass_kg,bearing_lines_x_m=[a,b],effective_support_span_m=b-a,
        sampled_translations=len(shifts),observations=len(xs),dynamic_factor_applied_once=p['dynamic_axle_factor'],
        force_scope='Full axle across both rails. Gross elastic Macaulay beam with actual0.35/19.65m bearing lines and20m nominalstock; free overhangs included. Neither cracked/connection/fatigue response nor physical approval',
        between_sample_upper_allowance=dict(moment_Nm=forces*shift_step/2,deflection_m=deflection_allowance,
            scope='Conservative model-only load/observation-position sensitivity allowances; not evidence for cracking or support flexibility'),numerical_sampling_converged=False)


_MOVING_CACHE={}
def moving(s,load,p,dead_mass_kg):
    # Invocation-local exact-input reuse; independent soil evaluations do not
    # change a beam's axle/stock model. Source changes invalidate this cache.
    key=identity(dict(section=s,load=load,policy=p,dead_mass_kg=dead_mass_kg,source_sha256=digest(__file__)))
    if key not in _MOVING_CACHE:
        if len(_MOVING_CACHE)>=64:_MOVING_CACHE.pop(next(iter(_MOVING_CACHE)))
        _MOVING_CACHE[key]=_moving(s,load,p,dead_mass_kg)
    return deepcopy(_MOVING_CACHE[key])


def prestress(s,demands,p,strands=None):
    ps=p['prestress'];e=ps['eccentricity_m'];A=s['area_m2'];I=s['I_y_m4'];cb=s['bottom_distance_m'];ct=s['top_distance_m']
    M=max(d['moment_Nm']+d['between_sample_upper_allowance']['moment_Nm'] for d in demands)
    needed=[]
    for d in demands:
        allowance=d['between_sample_upper_allowance']['moment_Nm']
        for row in d['moment_envelope_curve']:
            x=row['x_m'];local_e=e*4*x*(p['span_m']-x)/p['span_m']**2
            needed.append((row['moment_Nm']+allowance)*cb/I/(1/A+local_e*cb/I))
    need=max(needed)
    per=ps['strand_area_m2']*ps['strand_ultimate_Pa']*ps['jack_fraction']*ps['effective_fraction_of_jack']
    n=max(ps['minimum_strands'],ceil(need/per/ps['strand_group_multiple'])*ps['strand_group_multiple']) if strands is None else strands
    if n>ps['maximum_strands']:raise ValueError('Prestress strand construction budget exceeded; new family required')
    area=n*ps['strand_area_m2'];jack=area*ps['strand_ultimate_Pa']*ps['jack_fraction'];effective=jack*ps['effective_fraction_of_jack']
    bottom=[];bottom_max=[];top=[];top_min=[]
    for d in demands:
        for row in d['moment_envelope_curve']:
            x=row['x_m'];local_e=e*4*x*(p['span_m']-x)/p['span_m']**2;moment=row['moment_Nm']+d['between_sample_upper_allowance']['moment_Nm']
            bottom.append(effective/A+effective*local_e*cb/I-moment*cb/I)
            top.append(effective/A-effective*local_e*ct/I+moment*ct/I)
            top_min.append(effective/A-effective*local_e*ct/I+(row['minimum_moment_Nm']-d['between_sample_upper_allowance']['moment_Nm'])*ct/I)
            bottom_max.append(effective/A+effective*local_e*cb/I-(row['minimum_moment_Nm']-d['between_sample_upper_allowance']['moment_Nm'])*cb/I)
    sigma_bottom=min(bottom);sigma_top=max(top)
    transfer_force=jack*ps['transfer_fraction_of_jack']
    transfer_values=[]
    # Exact gross final two-bearing geometry. Prop-restrained secondary PT
    # effects are a separate unresolved construction stage, never admitted here.
    transfer_w=(s['quantities']['total_nominal_stock_mass_kg']+reinforcement(s,p)['mass_kg']+area*p['span_m']*p['steel_density_kg_m3']+n*ps['anchorage_kg_per_strand'])*G/p['span_m']
    _,_,_,Mtransfer=_response([],transfer_w,*p['support']['bearing_lines_x_m'],p['young_Pa']*I)
    for j in range(201):
        x=p['span_m']*j/200;local_e=e*4*x*(p['span_m']-x)/p['span_m']**2
        transfer_values.extend([transfer_force/A+transfer_force*local_e*cb/I-Mtransfer(x)*cb/I,transfer_force/A-transfer_force*local_e*ct/I+Mtransfer(x)*ct/I])
    transfer=max(transfer_values)
    length=p['span_m']*(1+8*e*e/(3*p['span_m']**2))
    mass=area*length*p['steel_density_kg_m3'];anchor=n*ps['anchorage_kg_per_strand']
    # Parabolic profile gives a uniform upward load8Pe/L² in the gross beam.
    camber=5*(8*effective*e/p['span_m']**2)*p['span_m']**4/(384*p['young_Pa']*I)
    return dict(strands=n,ducts=ps['ducts'],strand_area_m2=ps['strand_area_m2'],jack_force_N=jack,effective_force_N=effective,
        eccentricity_midspan_m=e,profile='z(x)=centroid_z - e*4*x*(L-x)/L²; smooth flexible ducts, chairsat1m',
        tendon_length_m_each=length,strand_stock_cut_length_m_each=length+1.2,strand_procurement_mass_kg=area*(length+1.2)*p['steel_density_kg_m3'],jacking_tail_stock_each_end_m=.6,active_steel_mass_kg=mass,anchorage_mass_kg=anchor,
        service_midspan_bottom_compression_Pa=sigma_bottom,service_midspan_top_compression_Pa=sigma_top,
        service_maximum_bottom_compression_Pa=max(bottom_max),service_minimum_top_compression_Pa=min(top_min),
        transfer_compression_upper_Pa=transfer,transfer_minimum_compression_Pa=min(transfer_values),gross_camber_m=camber,
        service_no_tension_hypothesis_met=sigma_bottom>=-1e-6 and min(top_min)>=-1e-6,
        compression_targets_met=max(max(bottom_max),sigma_top)<=p['service_compression_target_Pa'] and transfer<=p['transfer_compression_target_Pa'] and min(transfer_values)>=0,
        duct_cover_target_met=s['duct_normal_cover_m']>=ps['concrete_cover_m']-1e-9,
        end_zone_bursting_verified=False,loss_model='25%jacking loss hypothesis; time/creep/shrinkage/relaxation not qualified',
        profile_and_joint_local_stresses_verified=False,prop_restrained_secondary_prestress_verified=False)


def foundation(demands,beam_mass,p,soil_case,width=None):
    s=p['support'];N=4*max(d['reaction_N'] for d in demands)
    Hx=4*max(d['reaction_N'] for d in demands)*s['braking_force_fraction'];Hy=4*max(d['torsion_Nm'] for d in demands)/max(1.,s['column_height_m'])
    capvol=s['cap_size_m'][0]*s['cap_size_m'][1]*s['cap_size_m'][2]
    diameter=s['column_diameter_m']
    while sqrt(Hx*Hx+Hy*Hy)*s['column_height_m']**3/(3*p['young_Pa']*(pi*diameter**4/64))>s['pier_deflection_target_m'] and diameter<2.4:diameter=round(diameter+.2,6)
    colvol=pi*diameter**2/4*s['column_height_m'];fixed=(capvol+colvol)*p['concrete_density_kg_m3']*G
    def check(B):
        volume=B*B*s['footing_thickness_m'];total=N+fixed+volume*p['concrete_density_kg_m3']*G
        Mx=Hy*s['column_height_m'];My=Hx*s['column_height_m'];ex=My/total;ey=Mx/total
        q0=total/(B*B);qmax=q0*(1+6*(abs(ex)+abs(ey))/B);qmin=q0*(1-6*(abs(ex)+abs(ey))/B)
        slide=total*s['base_friction_hypothesis']/sqrt(Hx*Hx+Hy*Hy)
        overturn=total*B/2/(abs(Mx)+abs(My))
        return dict(width_m=B,thickness_m=s['footing_thickness_m'],volume_m3=volume,vertical_N=total,longitudinal_N=Hx,lateral_N=Hy,
            average_contact_Pa=q0,maximum_contact_Pa=qmax,minimum_contact_Pa=qmin,sliding_ratio=slide,overturning_ratio=overturn,
            soil_target_Pa=s['soil_bearing_Pa'][soil_case],soil_assumption_satisfied=qmax<=s['soil_bearing_Pa'][soil_case] and qmin>=0 and slide>=1 and overturn>=s['overturning_ratio_target'])
    if width is not None:result=check(width)
    else:
        result=None;count=round((s['footing_width_max_m']-s['footing_width_min_m'])/s['footing_width_step_m'])+1
        for i in range(count):
            result=check(s['footing_width_min_m']+i*s['footing_width_step_m'])
            if result['soil_assumption_satisfied']:break
    result.update(soil_case=soil_case,column_diameter_m=diameter,cap_concrete_m3=capvol,pier_concrete_m3=colvol,
        pier_gross_lateral_deflection_m=sqrt(Hx*Hx+Hy*Hy)*s['column_height_m']**3/(3*p['young_Pa']*(pi*diameter**4/64)),
        basis='Four independently maximised beam-end loads on shared two-track bent; deliberately conservative adjacent-span coincidence, gross elastic pier and no-tension rigid-footing contact; soil/water/seismic/settlement unverified')
    return result


def shear_detail(s,demands,p):
    """Conservative 45 degree truss link sizing without concrete shear credit.

    This is a nominal research link demand, not a code strength calculation.
    Longitudinal torsion reinforcement, bond and compression struts stay open.
    """
    V=max(d['shear_N'] for d in demands);T=max(d['torsion_Nm'] for d in demands)
    steel=p['reinforcement'];fy=steel['truss_design_stress_hypothesis_Pa'];leg=pi*steel['stirrup_diameter_m']**2/4;z=.9*(-s['zmin_m']-.12)
    inverse_pitch=V/(2*leg*fy*z)+T/(2*s['torsion_enclosed_median_area_m2']*leg*fy)
    required=1/inverse_pitch;step=steel['stirrup_pitch_step_m'];chosen=max(steel['minimum_stirrup_pitch_m'],int(required/step)*step)
    return dict(shear_demand_N=V,torsion_demand_Nm=T,truss_lever_arm_m=z,link_design_stress_hypothesis_Pa=fy,
        maximum_link_pitch_hypothesis_m=required,proposed_pitch_m=min(steel['stirrup_pitch_m'],chosen),
        actual_pitch_m=reinforcement(s,p)['stirrup_pitch_m'],link_screen_passed=reinforcement(s,p)['stirrup_pitch_m']<=required,
        gross_shear_stress_estimate_Pa=1.5*V/s['effective_web_shear_area_m2']+T/(2*s['torsion_enclosed_median_area_m2']*s['minimum_normal_wall_m']),
        concrete_shear_strength_credit_N=0.,strength_and_strut_anchorage_verified=False,
        basis='Nominal 45-degree truss shear-plus-torsion link demand; no concrete shear credit, no ultimate-load/code resistance claim')


def evaluate(train,*,family='reference_box',revision='source',soil_case='base',foundation_width_m=None,root=ROOT,upstream_root=None):
    validate_train(train,upstream_root or root);p=specification(root)
    # The folded bottom flange is only 700 mm wide. Two 250 mm bearings
    # centred at +/-200 mm fit; copying the box's +/-700 mm layout does not.
    if family=='folded_plate':
        p['support']['bearing_lateral_offsets_m']=[-.20,.20]
        p['support']['bearing_size_m']=[.45,.25,.18]
    if soil_case not in p['support']['soil_bearing_Pa']:raise ValueError('Named declared soil scenario required')
    s=section(family,revision);rebar=reinforcement(s,p)
    fastening_count=2*ceil(p['span_m']/p['fastener_pitch_m'])
    plate_mass=p['steel_density_kg_m3']*p['fastener_plate_size_m'][0]*p['fastener_plate_size_m'][1]*p['fastener_plate_size_m'][2]
    anchor_mass=p['anchor_count_per_plate']*p['steel_density_kg_m3']*pi*p['anchor_diameter_m']**2/4*p['anchor_length_m']
    rail_mass=2*p['rail_mass_kg_m']*p['span_m'];fastening_mass=fastening_count*(plate_mass+anchor_mass)
    # Prestress adds gravity; iterate the integer tendon design to fixed point.
    tend=None;demands=[];previous=None
    for iteration in range(6):
        tendon_mass=0 if tend is None else tend['active_steel_mass_kg']+tend['anchorage_mass_kg']
        dead=s['quantities']['total_nominal_stock_mass_kg']+rebar['mass_kg']+rail_mass+fastening_mass+tendon_mass+fastening_count*p['fastener_other_hardware_kg_each']+p['drainage_mass_kg_per_beam']+p['walkway_mass_kg_per_beam_share']+p['guard_mass_kg_per_beam']+p['joint_duct_grout_reserve_kg_per_beam']
        demands=[dict(name=l['name'],**moving(s,l,p,dead)) for l in train['load_cases']]
        tend=prestress(s,demands,p)
        shear=shear_detail(s,demands,p);changed=not shear['link_screen_passed']
        if changed:
            p['reinforcement']['stirrup_pitch_m']=shear['proposed_pitch_m'];rebar=reinforcement(s,p)
        if tend['strands']==previous and not changed:break
        previous=tend['strands']
    else:raise ValueError('Reinforcement/prestress/gravity fixed point did not converge within six revisions')
    foot=foundation(demands,dead,p,soil_case,foundation_width_m)
    nominal=s['quantities']['total_nominal_stock_mass_kg'];lift_mass=nominal+rebar['mass_kg']+tend['active_steel_mass_kg']+tend['anchorage_mass_kg']
    hook_whole=(lift_mass+p['lifting']['rigging_kg'])*(1+p['lifting']['contingency_fraction'])
    hook_piece=(lift_mass/2+p['lifting']['rigging_kg'])*(1+p['lifting']['contingency_fraction'])
    lifting=dict(whole_lift_piece_kg=lift_mass,whole_required_hook_kg=hook_whole,segmented_piece_length_m=10.,segmented_piece_kg=lift_mass/2,
        segmented_required_hook_kg=hook_piece,provisional_radius_m=p['lifting']['radius_m'],provisional_capacity_at_radius_kg=p['lifting']['provisional_capacity_at_radius_kg'],
        whole_fits_provisional_chart=hook_whole<=p['lifting']['provisional_capacity_at_radius_kg'],segmented_fits_provisional_chart=hook_piece<=p['lifting']['provisional_capacity_at_radius_kg'],
        whole_transport_payload_pass=lift_mass<=p['lifting']['transport_payload_kg'],segmented_transport_payload_pass=lift_mass/2<=p['lifting']['transport_payload_kg'],
        actual_lift_admitted=False,verified_chart_available=False)
    segment=not lifting['whole_fits_provisional_chart'] or not lifting['whole_transport_payload_pass']
    # Segmenting changes the manufactured assembly, not an analysis-only flag.
    physical=dict(schema='osr-pilot-civil-physical/1',beam_stock=s['physical'],reinforcement=rebar,
        prestress_geometry={k:tend[k] for k in ('strands','ducts','strand_area_m2','eccentricity_midspan_m','profile','tendon_length_m_each')},
        segment_count=2 if segment else 1,segment_joint=dict(at_x_m=10.,method='match-cast shear keys + epoxy closure + continuous post-tension',closure_width_m=.002,local_joint_verified=False) if segment else None,
        bearing_layout=dict(each_beam_end=2,size_m=p['support']['bearing_size_m'],offset_y_m=p['support']['bearing_lateral_offsets_m']),
        support_geometry=dict(column_height_m=p['support']['column_height_m'],column_diameter_m=foot['column_diameter_m'],cap_size_m=p['support']['cap_size_m'],footing_width_m=foot['width_m'],footing_thickness_m=foot['thickness_m']),
        drainage=dict(pipes=2,diameter_m=.10,material='HDPE candidate',clip_pitch_m=2.),maintenance_walkway=dict(width_m=1.,scope='Inspection path only; passenger evacuation/accessibility unresolved'),
        rail_interface=dict(rails=2,rail_kg_m=p['rail_mass_kg_m'],fastenings=fastening_count,anchors_per_set=p['anchor_count_per_plate']),
        complete_installed_geometry=False,**FLAGS)
    cid=identity(physical)
    screens=dict(gross_vertical_deflection_target=all(d['deflection_model_upper_m']<=p['deflection_target_m'] for d in demands),
        prestress_no_tension=tend['service_no_tension_hypothesis_met'],prestress_compression=tend['compression_targets_met'],duct_cover=tend['duct_cover_target_met'],
        shear_torsion_links=shear['link_screen_passed'],
        lateral_deflection=all(d['lateral_deflection_m']<=p['lateral_deflection_target_m'] for d in demands),torsion=all(d['twist_rad']<=p['twist_target_rad'] for d in demands),
        bearing_no_uplift=all(d['minimum_bearing_compression_N']>=0 for d in demands),soil_scenario=foot['soil_assumption_satisfied'],pier_lateral_deflection=foot['pier_gross_lateral_deflection_m']<=p['support']['pier_deflection_target_m'],
        provisional_erection= lifting['segmented_fits_provisional_chart'] if segment else lifting['whole_fits_provisional_chart'])
    quantities=dict(concrete_beam_m3=s['quantities']['total_nominal_volume_m3'],nominal_concrete_mass_kg=nominal,reinforcement_mass_kg=rebar['mass_kg'],prestress_active_kg=tend['active_steel_mass_kg'],prestress_procurement_kg=tend['strand_procurement_mass_kg'],anchorage_kg=tend['anchorage_mass_kg'],rail_kg=rail_mass,fastener_steel_kg=fastening_mass,
        fastening_other_hardware_kg=fastening_count*p['fastener_other_hardware_kg_each'],drainage_access_misc_reserve_kg=p['drainage_mass_kg_per_beam']+p['walkway_mass_kg_per_beam_share']+p['guard_mass_kg_per_beam'],joint_duct_grout_reserve_kg=p['joint_duct_grout_reserve_kg_per_beam'],accounted_superstructure_kg=dead,complete_installed_mass_kg=None)
    costs=estimate(quantities,foot,segment,p)
    result=dict(schema='osr-pilot-civil-evaluation/1',system_candidate_id=train['candidate_id'],vehicle_candidate_id=train['vehicle_candidate_id'],mass_evaluation_id=train['mass_evaluation_id'],input_load_evaluation_id=train['evaluation_id'],
        civil_candidate_id=cid,physical_definition=physical,parent_geometry_candidate_id=s['parent_geometry_candidate_id'],section=s,reinforcement=rebar,prestress=tend,load_demands=demands,
        foundation=foot,lifting=lifting,shear_detail=shear,quantities=quantities,cost=costs,screens=screens,advisory_screen_passed=all(screens.values()),
        fatigue_duty=dict(headway_s=p['headway_s'],passes_per_track_year=3600/p['headway_s']*p['operating_hours_day']*p['operating_days_year'],
            full_axle_cycles_per_track_30years=3600/p['headway_s']*p['operating_hours_day']*p['operating_days_year']*24*p['design_life_years'],fatigue_resistance_verified=False),
        purpose='next-experiment only',source_sha256=sources(root),policy=p,
        engineering_holds=['Uncrackedsection and ideal prestress/shear-transfer models are not strength/fatigue/buckling proof',
            'Joint shear keys, anchor bursting, bond, shear reinforcement, bearings and rail fixings require detailed checks',
            'Actual soil, groundwater, settlement, seismic/wind and utility/site constraints require evidence',
            'Crane capacity at12mradius is a provisional input, not a measured or manufacturer-confirmed chart',
            'Vehicle axle loads/CG are input hypotheses until installed assembly and dynamic vehicle response verified',
            'Central inspection walkway is not an approved passenger evacuation/accessibility system'],**FLAGS)
    from .assembly import construction,parts
    result['construction']=construction(result)
    result['screens'].update(handling=result['construction']['handling']['gross_handling_target_met'],temporary_tower_elastic=result['construction']['midspan_tower']['elastic_capacity_screen'])
    result['advisory_screen_passed']=all(result['screens'].values())
    result['parts']=parts(result)
    result['interface_feedback']=dict(rail_vertical_displacement_model_m=max(d['deflection_model_upper_m'] for d in demands),rail_lateral_displacement_model_m=max(d['lateral_deflection_m'] for d in demands),rail_twist_model_rad=max(d['twist_rad'] for d in demands),pier_lateral_displacement_model_m=foot['pier_gross_lateral_deflection_m'],magnetic_gap_model_applicable=False,magnetic_gap_reason='Wheel-supported candidate. Any candidate-specific LIM airgap requires actual stator/secondary relative-displacement geometry; no gap clearance inferred from bridge deflection.')
    return seal(result)


def estimate(q,foot,segmented,p):
    rates=p['cost'];beams=2*ceil(p['route_m']/p['span_m']);bents=ceil(p['route_m']/p['span_m'])+1;rows=[]
    def add(owner,quantity,unit,prices,basis):rows.append(dict(owner=owner,quantity=quantity,unit=unit,cost_usd={c:quantity*prices[i] for i,c in enumerate(CASES)},basis=basis))
    factory=[]
    for i in range(3):
        material=q['concrete_beam_m3']*rates['concrete_usd_m3'][i]+q['reinforcement_mass_kg']*rates['reinforcement_usd_kg'][i]+(q['prestress_procurement_kg']+q['anchorage_kg'])*rates['prestress_usd_kg'][i]
        process=q['concrete_beam_m3']*rates['precast_labour_h_m3'][i]*rates['loaded_wage_usd_h'][i]
        tooling=rates['mould_setup_usd'][i]/rates['mould_reuses'][i]
        factory.append((material+process+tooling)*(1+rates['overhead_fraction'][i]))
    add('civil/precast-factory',beams,'20mspans',factory,'Concrete+cut/bentbars+prestress/anchorstock+labour+mouldamortisation+declaredoverhead')
    pieces=2 if segmented else 1
    add('civil/transport',beams*pieces,'pieces',rates['transport_piece_usd'],'Payloadgeometry/craneaccessunverified; no nominaltonnageadmission')
    add('civil/erection',beams*pieces,'pieces',rates['erect_piece_usd'],'Priceperpieceatdeclaredradius hypothesis; actualchartapprovalpending')
    if segmented:
        add('civil/segment-joints',beams,'matchcastclosures',rates['joint_preparation_usd'],'Matchcasting,epoxyjoint andposttensionclosure provision; qualifiedkeys/bondpending')
        add('civil/temporary-props',p['lifting']['temporary_support_reused_sets'],'reusedsets',rates['temporary_support_set_usd'],'Temporarymidspanpropuntilcontinuityandprestressestablished; foundation/stabilitydesignpending')
    vol=foot['volume_m3']+foot['cap_concrete_m3']+foot['pier_concrete_m3'];support=[]
    for i in range(3):support.append(vol*rates['site_concrete_usd_m3'][i]+vol*rates['site_reinforcement_kg_m3'][i]*rates['reinforcement_usd_kg'][i]+foot['volume_m3']*1.4*rates['foundation_excavation_usd_m3'][i])
    add('civil/shared-pier-foundation',bents,'two-trackbents',support,'Sharedinteriorsupports countedonce; exactfootgeometry, sitebar/excavationreserves')
    add('civil/ducts-grout-chairs-endzone',beams,'beam packages',rates['joint_duct_grout_usd_per_beam'],'Positive duct, grout, chair and end-zone provision; exact detailing pending, included gravity reserve separate from concrete stock')
    add('civil/bearings',beams*4,'bearings',rates['bearing_usd_each'],'Twobearingsperbeamend, replaceability and horizontalrestraintsunverified')
    add('civil/rails',beams*q['rail_kg'],'kg',[.65,.9,1.4],'Two60.21kg/mrailspertrack, no installationoverlapwithsourcepilot budgets')
    add('civil/fastening-steel',beams*q['fastener_steel_kg'],'kg',rates['fabricated_steel_usd_kg'],'Pricedplatesandanchorstock; completeclips/pads/nuts/washersremainwithinpositivehardwareallowance')
    add('civil/fastening-clips-pads-nuts-washers',beams*q['fastening_other_hardware_kg']/p['fastener_other_hardware_kg_each'],'sets',rates['fastener_other_hardware_usd_each'],'Positivefinishedhardwarepackageprovision; steelplate/anchorspricedseparately')
    add('civil/inspection-walkway-guard',beams*(p['walkway_mass_kg_per_beam_share']+p['guard_mass_kg_per_beam']),'kg',rates['walkway_guard_usd_kg'],'Inspectiononly; newgrating,guard,postsandfixingsscope, notpassengerevacuationapproval')
    add('civil/drainage',beams*40,'m',rates['drainage_usd_m'],'Two20mdrainsperbeam plusclipprocessallowance')
    known={c:fsum(row['cost_usd'][c] for row in rows) for c in CASES}
    total={c:known[c]*(1+rates['contingency_fraction'][i]) for i,c in enumerate(CASES)}
    return dict(currency='USD',route_m=p['route_m'],tracks=2,beams=beams,shared_bents=bents,accounts=rows,direct_subtotal_usd=known,
        contingency_usd={c:total[c]-known[c] for c in CASES},scoped_installed_usd=total,scoped_per_route_km_usd={c:total[c]/(p['route_m']/1000) for c in CASES},
        scope='Civilonly; replaceoriginalcivilowners, neveraddthiswholeamountontopoforiginalguideway/foundation/erectionaccounts. Stations, vehicles, power, land/utilities, operations and completewholelife costs separate',supplier_quotes_received=False)


def evaluate_portfolio(train,*,root=ROOT,upstream_root=None):
    return [evaluate(train,family=f,revision=r,soil_case=soil,root=root,upstream_root=upstream_root) for f,r in [('reference_box','source'),('folded_plate','source'),('folded_plate','thick-web')] for soil in ('weak','base','firm')]
