"""SOURCE-only Alheader/retained-Alendplate/steelcleat mechanical alternative.

No ordinary Al-to-steel weld, source adapter, actual joint/body producer or
native tool is called. Actual use requires an independently reviewed exact
request, complete existing-cut/weld provenance and explicit load/material data.
All records are proposals, not installed assembly or safety acceptance.
"""
from copy import deepcopy
from hashlib import sha256
from math import pi,sqrt,fsum
import json

BASE='823b2b25afddb8e429d0adf99f72f766f311b2fa'
FINDING='f9cd493337fdee43e4cb1a0d5f6fa8cba9624b15617b8b28fe764bae158b4487'
FAMILY='research/header-Al-endplate-isolated-blind-steel-joint/1'
NOMINAL_ENGAGEMENT_M=.006
COMBINED_AXIAL_TOLERANCE_M=.0003
MINIMUM_ENGAGEMENT_M=NOMINAL_ENGAGEMENT_M-COMBINED_AXIAL_TOLERANCE_M
P6=dict(physical_id='ce1b8b222b06a6479f7738d9409d74a5333514b79b7baf5dffc7c8510b73e044',evaluation_id='8fffa3254dab9b737e8785de7d781325dde3cec028a89b14a3e8371b04cc6289',raw_sha256='3984b2a7ad9966b8d74fec2da9d0530cea66d3557071e964816f55fefebb9df5')
I=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
HEADER_R=[[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]]
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False,selected_reference_changed=False,native_evaluator_admitted=False,installed_mass_complete=False)


def identity(v):return sha256((json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()
def seal(v):
    if 'evaluation_id' in v:raise ValueError('New evaluation required')
    return dict(deepcopy(v),evaluation_id=identity(v))

def number(v,*,positive=False):
    if type(v) not in (int,float) or not __import__('math').isfinite(v) or (v<=0 if positive else v<0):raise ValueError('Finite nonboolean positive/nonnegative SI input required')
    return float(v)

def near(a,b):return len(a)==len(b) and all(abs(float(x)-float(y))<1e-9 for x,y in zip(a,b))
def proper(R):
    if len(R)!=3 or any(len(r)!=3 or any(type(x) not in (int,float) or not __import__('math').isfinite(x) for x in r) for r in R):raise ValueError('Finite proper frame required')
    if any(abs(sum(R[k][i]*R[k][j] for k in range(3))-(1 if i==j else 0))>1e-10 for i in range(3) for j in range(3)):raise ValueError('Rigid frame required')
    det=R[0][0]*(R[1][1]*R[2][2]-R[1][2]*R[2][1])-R[0][1]*(R[1][0]*R[2][2]-R[1][2]*R[2][0])+R[0][2]*(R[1][0]*R[2][1]-R[1][1]*R[2][0])
    if abs(det-1)>1e-10:raise ValueError('Reflection refused')
    return R

def transform(p,origin,R):return [origin[i]+sum(R[i][j]*p[j] for j in range(3)) for i in range(3)]
def inverse(p,origin,R):return [sum(R[k][j]*(p[k]-origin[k]) for k in range(3)) for j in range(3)]


def validate_context(ctx):
    """Read-only exact known faces; record identity is not manufacturing proof."""
    if ctx['source_p6']!=P6:raise ValueError('Exact source P6 evaluation/raw required')
    h=ctx['header'];side=1 if h['at_m'][1]>0 else -1;hx=h['at_m'][0]
    if not any(abs(hx-v)<1e-9 for v in (-.4,.5)):raise ValueError('Exact four header stations only')
    specs=dict(header=('body/al5083','rhs',[.7285,.120,.180],[hx,side*.72575,1.0195],HEADER_R),
      endplate=('body/al5083','box',[.200,.025,.180],[hx,side*.349,1.0195],I),
      cleat=('body/steel','box',[.200,.010,.180],[hx,side*.330,1.0195],I),
      main_wall=('body/steel','box',[3.300,.010,.320],[-.45,side*.320,.9395],I),
      diaphragm=('body/steel','box',[.008,.630,.320],[hx,0.,.9395],I))
    for key,(mat,kind,size,at,R) in specs.items():
        c=ctx[key];proper(c['rotation'])
        if c['material_id']!=mat or c['frame']!='body' or c['geometry']['kind']!=kind or not near(c['geometry']['size_m'],size) or not near(c['at_m'],at) or c['rotation']!=R:raise ValueError('Changed actual material/stock/frame: '+key)
        if ctx['source_record_ids'].get(c['id'])!=identity(c):raise ValueError('Stale source record: '+key)
    if abs(h['geometry']['wall_m']-.008)>1e-10:raise ValueError('Actual header8mm wall required')
    gap=abs(h['at_m'][1])-.7285/2-(abs(ctx['cleat']['at_m'][1])+.005)
    free=abs(ctx['endplate']['at_m'][1])-.0125-(abs(ctx['cleat']['at_m'][1])+.005)
    if abs(gap-.0265)>1e-9 or abs(free-.0015)>1e-9:raise ValueError('Actual26.5mm gap/25mm retainedendplate/1.5mm isolation land differs')
    return dict(origin_m=[hx,side*.335,1.0195],rotation=I if side==1 else [[-1.,0.,0.],[0.,-1.,0.],[0.,0.,1.]],side=side,
      gap_m=gap,endplate_occupies_gap_m=[.0015,.0265],remaining_isolation_gap_m=free,
      central_diaphragm_not_a_header_adapter=True,source_geometry_unchanged=True)


def cylinder_union(cuts):
    """Exact finite coaxial/disjoint cylinder union, with unknown other overlaps.

    Source-local axes required. Cross-axis or overlapping noncoaxial removals
    are unsupported and must not be silently summed. Cut lists are not receipts
    of actual source machining or credits.
    """
    if not cuts:return 0.
    unique={identity(c):c for c in cuts};cs=list(unique.values())
    for c in cs:
        if type(c['axis']) is not int or c['axis']!=1:raise ValueError('Only explicit sourceY wall operations supported')
        if len(c['at_m'])!=3:raise ValueError('Explicit3coordinate cutter centre required')
        for v in c['at_m']:
            if type(v) not in (int,float) or not __import__('math').isfinite(v):raise ValueError('Finite cutter centre required')
        number(c['radius_m'],positive=True);number(c['length_m'],positive=True)
    centres={tuple(c['at_m'][k] for k in (0,2)) for c in cs};total=0.
    for a in cs:
        for b in cs:
            if a is b:continue
            d=sqrt((a['at_m'][0]-b['at_m'][0])**2+(a['at_m'][2]-b['at_m'][2])**2)
            overlap=min(a['at_m'][1]+a['length_m']/2,b['at_m'][1]+b['length_m']/2)-max(a['at_m'][1]-a['length_m']/2,b['at_m'][1]-b['length_m']/2)
            if d>0 and d<a['radius_m']+b['radius_m'] and overlap>0:raise ValueError('Noncoaxial bore union requires a new exact model')
    for X,Z in centres:
        group=[c for c in cs if (c['at_m'][0],c['at_m'][2])==(X,Z)]
        ends=sorted({c['at_m'][1]+s*c['length_m']/2 for c in group for s in (-1,1)})
        for a,b in zip(ends,ends[1:]):
            radii=[c['radius_m'] for c in group if c['at_m'][1]-c['length_m']/2<=a+1e-14 and c['at_m'][1]+c['length_m']/2>=b-1e-14]
            if radii:total+=pi*max(radii)**2*(b-a)
    return total


def machining(ctx,frame,existing):
    """Four Althroughbores, four flatbottom steelpilots, bounded thread removal."""
    rows=[]
    for key,D,L,offset in [('endplate',.0122,.025,0.),('cleat',.0068,.009,frame['side']*.0005)]:
        c=ctx[key];size=c['geometry']['size_m'];cuts=[];majors=[]
        for u in (-.080,.080):
            for w in (-.050,.050):
                world=transform([u,.014 if key=='endplate' else -.0045,w],frame['origin_m'],frame['rotation'])
                p=inverse(world,c['at_m'],c['rotation']);cut=dict(axis=1,at_m=p,radius_m=D/2,length_m=L)
                ext=[D/2,L/2,D/2]
                if any(abs(p[k])+ext[k]>size[k]/2+1e-10 for k in range(3)):raise ValueError('Cutter outside actual source stock')
                cuts.append(cut)
                if key=='cleat':
                    Q=transform([u,-.0035,w],frame['origin_m'],frame['rotation']);majors.append(dict(axis=1,at_m=inverse(Q,c['at_m'],c['rotation']),radius_m=.004,length_m=.007))
        old=existing.get(c['id'])
        if old is None:removal=None;state='held-existing-bore-roster-unknown; no actual credit'
        else:
            #All priorcuts must themselves be real contained source operations.
            for cut in old:
                r=cut['radius_m'];ext=[r,cut['length_m']/2,r]
                if any(abs(cut['at_m'][k])+ext[k]>size[k]/2+1e-10 for k in range(3)):raise ValueError('Existing bore outside source stock')
            before=cylinder_union(old);low=cylinder_union(old+cuts)-before;high=cylinder_union(old+cuts+majors)-before
            removal=[max(0.,low),max(0.,high)];state='planned exact-coaxial union bounds only; unapplied'
        rows.append(dict(part_id=c['id'],source_record_id=ctx['source_record_ids'][c['id']],source_material=c['material_id'],
          new_pilots_or_through_cuts=cuts,major_thread_envelopes=majors,incremental_removed_volume_bounds_m3=removal,
          source_credit_key=identity([P6,c['id'],'four-isolated-M8-operations']),existing_roster_state=state,
          paid_source_gross_retained=True,source_mass_cost_credit_applied=False,exact_helix_or_full_major_removal_claimed=False,
          process_h=.50 if key=='cleat' else .25,QA_h=.20 if key=='cleat' else .15))
    return rows


def line_weld(width,bottom,top,leg,plane_v,material,parents):
    paths=[[[-width/2,plane_v,bottom],[width/2,plane_v,bottom]],
      [[-width/2,plane_v,bottom],[-width/2,plane_v,top]],[[width/2,plane_v,bottom],[width/2,plane_v,top]]]
    L=width+2*(top-bottom)
    #BottomAlfaces areflush:an externalbutt reinforcement triangle,not
    #a fictitiousfillet backed bymissingAlbelowtheendplate. Steelwall extends
    #belowitscleat,so itsbottom is atruecornerfillet.
    bottom_section=([[plane_v-leg/2,bottom],[plane_v+leg/2,bottom],[plane_v,bottom-leg]] if material.startswith('Al') else [[plane_v,bottom],[plane_v+leg,bottom],[plane_v,bottom-leg]])
    profiles=[dict(extrusion_axis=0,interval_m=[-width/2,width/2],section_axes=[1,2],vertices_m=bottom_section),
      dict(extrusion_axis=2,interval_m=[bottom,top],section_axes=[0,1],vertices_m=[[-width/2,plane_v],[-width/2-leg,plane_v],[-width/2,plane_v+leg]]),
      dict(extrusion_axis=2,interval_m=[bottom,top],section_axes=[0,1],vertices_m=[[width/2,plane_v],[width/2+leg,plane_v],[width/2,plane_v+leg]])]
    return dict(material=material,parents=parents,profiles=profiles,paths_m=paths,leg_m=leg,length_m=L,net_volume_m3=.5*leg**2*L,gross_volume_m3=1.2*.5*leg**2*L,
      contact='Finite bottom+side external corner seams; no topweld in floor plane. Exact trianglerunout/WPS/HAZ and priorseam retirement held.',
      ordinary_dissimilar_weld=False,top_omitted=True,side_top_m=top,process_h=.55,QA_h=.20,qualified=False)


def weld_bound(weld,F,M):
    """Conservative line-throat stress sum; not fatigue, penetration or validation."""
    if any(x is None for x in F+M):return dict(stress_bound_Pa=None,scope='held-actual action envelope unknown')
    for x in F+M:
        if type(x) not in (int,float) or not __import__('math').isfinite(x):raise ValueError('Finite declared action required')
    lines=weld['paths_m'];L=weld['length_m'];a=weld['leg_m']/2 if weld['material'].startswith('Al') else weld['leg_m']/sqrt(2)
    lengths=[sqrt(sum((Q[k]-P[k])**2 for k in range(3))) for P,Q in lines]
    centre=[fsum(lengths[i]*(P[k]+Q[k])/2 for i,(P,Q) in enumerate(lines))/L for k in range(3)]
    moments=[]
    for k in (0,2):
        moments.append(a*fsum(lengths[i]*(((P[k]+Q[k])/2-centre[k])**2+(Q[k]-P[k])**2/12) for i,(P,Q) in enumerate(lines)))
    Iu,Iw=moments[1],moments[0];J=Iu+Iw
    ru=max(abs(P[0]-centre[0]) for line in lines for P in line);rw=max(abs(P[2]-centre[2]) for line in lines for P in line)
    #Actions were supplied at(U0,planeV,W0); shift toactualUgroupcentroid.
    du=-centre[0];dw=-centre[2]
    Mc=[M[0]-dw*F[1],M[1]+dw*F[0]-du*F[2],M[2]+du*F[1]]
    stress=sqrt(sum(x*x for x in F))/(a*L)+abs(Mc[0])*rw/Iu+abs(Mc[2])*ru/Iw+abs(Mc[1])*sqrt(ru*ru+rw*rw)/J
    return dict(stress_bound_Pa=stress,moments_at_group_centroid_Nm=Mc,throat_area_m2=a*L,centroid_m=centre,Iu_m4=Iu,Iw_m4=Iw,
      effective_throat_basis='Unmeasuredminimum2mmAlbutt/sidehypothesis orleg/sqrt2steelcorner;fusionquality isnotinferredfrombeadvolume',scope='Ideal uniform throat linegroup; triangle-inequality force/moment stress sum. WPS/HAZ/contact/penetration/fatigue/rootwall remain unqualified')


def capacity(actions,strengths,welds):
    """Required explicit actions/hypotheses; actual missing demands stay unknown.

    No division byfour bolts or wall/friction/loadsharing credit. Per-fastener
    envelopes are caller-owned and must include all moment reactions. A weld
    line bound cannot qualify the unsupported whole-wall/diaphragm load path.
    """
    if actions.get('frame')!='joint-local-UVW' or actions.get('reference_point_m')!=[0.,.0265,0.]:raise ValueError('Explicit joint-local actions atactualAlweldplane reference required')
    F=actions['header_force_N'];M=actions['header_moment_Nm']
    if len(F)!=3 or len(M)!=3:raise ValueError('Explicit force/moment vectors required')
    if any(v is not None and (type(v) not in (int,float) or not __import__('math').isfinite(v)) for v in F+M):raise ValueError('Finite declared actions orNone unknown required')
    shear=actions['one_fastener_shear_N'];tension=actions['one_fastener_tension_N'];preload=actions['preload_each_N']
    for x in (shear,tension,preload):
        if x is not None:number(x)
    if all(x is not None for x in F):
        if shear is not None and shear+1e-9<sqrt(F[0]**2+F[2]**2) or tension is not None and tension+1e-9<abs(F[1]):raise ValueError('No unearned per-fastener load sharing')
    Athread=strengths['effective_bolt_thread_area_m2'];Athreadshear=strengths['minimum_receiver_thread_shear_area_m2']
    if Athread is not None and Athread>pi*.004**2:raise ValueError('Bolt effectivearea exceeds declaredmajorstock')
    if Athreadshear is not None and Athreadshear>pi*.008*MINIMUM_ENGAGEMENT_M:raise ValueError('Receiverthreadsheararea exceeds toleranced minimum engagement surface envelope')
    for x in strengths.values():
        if x is not None:number(x,positive=True)
    checks=[]
    def add(name,demand,area,allow):
        cap=None if area is None or allow is None else area*allow
        checks.append(dict(name=name,demand_N=demand,area_m2=area,allowable_hypothesis_Pa=allow,capacity_N=cap,
          residual_N=None if cap is None or demand is None else cap-demand,required_stress_Pa=None if demand is None or area is None else demand/area,
          physical_accepted=False))
    combined=None if tension is None or preload is None else tension+preload
    add('fullythreaded bolt shear,no smoothshank credit',shear,Athread,strengths['bolt_shear_Pa'])
    add('bolt axial+preload',combined,Athread,strengths['bolt_tension_Pa'])
    add('steel blindthread strip,explicit minimumarea required',combined,Athreadshear,strengths['steel_thread_shear_Pa'])
    add('Alendplate projectedbore bearing',shear,.012*.025,strengths['Al_bearing_Pa'])
    add('GFRPbush projectedbearing',shear,.008*.025,strengths['GFRP_bearing_Pa'])
    add('Alendplate singleedge shearout',shear,(.100-.080-.0061)*.025,strengths['Al_shear_Pa'])
    add('steelreceiver projectedbearing',shear,.008*MINIMUM_ENGAGEMENT_M,strengths['steel_bearing_Pa'])
    add('steelcleat singleedge shearout',shear,(.100-.080-.004)*.010,strengths['steel_shear_Pa'])
    add('GFRPisolation compression,no loadspread credit',combined,pi*(.008**2-.0061**2),strengths['GFRP_compression_Pa'])
    rootM=[None]*3 if any(x is None for x in F+M) else [M[0]+.0365*F[2],M[1],M[2]-.0365*F[0]]
    bounds=[weld_bound(welds[0],F,M),weld_bound(welds[1],F,rootM)]
    for bound,key in zip(bounds,('Al_weld_Pa','steel_weld_Pa')):
        bound['allowable_hypothesis_Pa']=strengths[key];bound['residual_Pa']=None if strengths[key] is None or bound['stress_bound_Pa'] is None else strengths[key]-bound['stress_bound_Pa']
    return dict(fastener_checks=checks,weld_bounds=bounds,header_actions=deepcopy(actions),grade_and_strength_hypotheses=deepcopy(strengths),
      bolt_count=4,friction_credit=0.,fastener_load_divisor=1,diaphragm_loadsharing_credit=False,
      nominal_receiver_engagement_m=NOMINAL_ENGAGEMENT_M,combined_axial_tolerance_hypothesis_m=COMBINED_AXIAL_TOLERANCE_M,
      minimum_receiver_engagement_hypothesis_m=MINIMUM_ENGAGEMENT_M,minimum_engagement_physically_verified=False,
      declared_action_vectors_complete=all(x is not None for x in F+M),actual_header_demands_known=False,caller_fastener_moment_reaction_bound_validated=False,
      mainwall_local_bending_buckling_rootweld_and_preload_loss='held-fullstructural/evidence model required; no averagearea qualification',
      engineering_screen='held',**FLAGS)


def part(name,material,geometry,at,net,gross,process,qa,**metadata):
    lo,hi=net if isinstance(net,list) else (net,net)
    if not 0<lo<=hi<=gross:raise ValueError('Positive net/gross material with explicit bounds required')
    return dict(id=name,material=material,quantity=1,frame='joint-local-UVW',geometry=geometry,at_m=at,rotation=I,
      net_volume_bounds_m3=[lo,hi],gross_volume_m3=gross,process_h=process,QA_h=qa,metadata=metadata,
      role='mass-allocation' if geometry['kind'].startswith('noncollision') or geometry['kind']=='route-allowance' else 'physical-proposal',exact_installed_mass=False)


def materials_account(parts,policy):
    """Calculated stock/process bounds if supplied; missing rates areunknown."""
    rows=[]
    for p in parts:
        m=None if policy is None else policy.get(p['material']);rho=None if m is None else m.get('density_kg_m3');price=None if m is None else m.get('USD_kg');labour=None if policy is None else policy.get('labour_USD_h')
        for v in (rho,price,labour):
            if v is not None:
                if len(v)!=3:raise ValueError('Three explicit material/process bounds required')
                for x in v:number(x,positive=True)
                if list(v)!=sorted(v):raise ValueError('Ordered low/base/high material/process bounds required')
        vols=[p['net_volume_bounds_m3'][0],sum(p['net_volume_bounds_m3'])/2,p['net_volume_bounds_m3'][1]]
        rows.append(dict(part_id=p['id'],mass_bounds_kg=None if rho is None else [v*d for v,d in zip(vols,rho)],
          gross_material_USD=None if rho is None or price is None else [p['gross_volume_m3']*d*r for d,r in zip(rho,price)],
          process_QA_USD=None if labour is None else [(p['process_h']+p['QA_h'])*v for v in labour],
          paid_once=True,basis='Declared rawstock+process/QA,not a supplierquote or physicalinstalledweight'))
    return dict(rows=rows,price_policy=deepcopy(policy),unknowns_remain_unknown=True,complete_factory_installed_cost=False)


def comparison(ctx,frame):
    """Function-first source alternatives, not a baseline/price ranking."""
    return dict(next_experiment='isolated blindreceivers inretainedsteelcleat,retainedAlendplate',
      alternatives=[dict(id='isolated-blind-receiver',state='primary research sourceproposal',
        reason='Uses real25mmAlendplate alreadyin26.5mmgap; no newshoe, no throughmainwallnut, no relocatedheader',
        root_risks=['10mmcleat blindthread/1mmbackweb andload/grade remainunknown','Alendplate/header andsteelcleat/mainwall welds need ownedgeometry/provenance/strength','Preload/creep/corrosion/lockpair andactualtoolclearance unqualified']),
      dict(id='reversible-bypass-fork',state='retained outline requiring a separate completejoint/fastener/loadpath definition',
        concept='Bypass200mmAlendplate Xedges; rootsteel spacer8mm thenouterrail atabsX108..116mm; crossplate onlyafterabsY369.5mm; innerboltedcheek atabsX62.5..70.5mm',
        counted_required_stock_per_header=dict(root_spacers=2,outer_rails=2,crossplates=2,inner_cheeks=2),
        steel_stock_outline_m=[[.008,.010,.120],[.008,.0445,.120],[.0535,.008,.120],[.008,.084,.120]],
        steel_net_volume_before_bores_m3=2*(.008*.010*.120+.008*.0445*.120+.0535*.008*.120+.008*.084*.120),
        bolts_sleeves_isolation_welds_andtooling_complete=False,installed_mass_kg=None,cost_USD=None,
        reason='Avoids thinblindreceiver butadds at least8steelblanks/header,more weldedinterfaces,offsetloadpaths andthrough-headerisolation/sleeve operations. Notselectedor silentlytreatedasfailed.'),
      dict(id='qualified-bimetal-transition',state='source/supplier/qualification task',mass_kg=None,cost_USD=None,
        reason='Specific certifiedtransition/material/geometry/WPS/HAZ/fatigue records required; ordinaryAl5356-to-steel route isnot a substitute')],
      failed_retained=dict(source_commit=BASE,independent_finding=FINDING,ordinary_Alshoe_route_supported=False,
        material_pair='Al5083 shoe ordinaryAl5356 into body/steelcleat unsupported',
        existing_endplate_obstruction=dict(size_m=[.200,.025,.180],gap_position_m=[.0015,.0265],
          prior_shoe_nominal_gross_overlap_m3=.120*.025*.180,scope='Declared nominalgrossstock witness,not measuredinstalledmaterial acceptance'),
        failed_twistdrill=dict(cyl_depth_m=.0085,chosen_tip_length_m=.0021,total_m=.0106,cleat_thickness_m=.010,wall_breakthrough_m=.0006,
          reason='Chosen conventionaltip hypothesis entersmainwall beforetolerance. Newproposal uses explicitflatbottom milling andthreadmilling instead.')),baseline_selected=False)


def outline(ctx,*,existing_cuts,actions,strengths,material_policy,source_binding):
    """Future LOCAL outline producer. Do not call onactual records yet.

    Only invented fixtures are authorized during source development. This API
    does not open P6, alter source stock, apply machining, price a railway or
    produce CAD/body/native records. Exact4contexts remain a later request.
    """
    frame=validate_context(ctx)
    if source_binding.get('base_commit')!=BASE or source_binding.get('context_id')!=identity(ctx) or source_binding.get('finding_id')!=FINDING:raise ValueError('Exact new source/context/review binding required')
    requestid=source_binding.get('request_id','')
    if not isinstance(requestid,str) or len(requestid)!=64 or any(c not in '0123456789abcdef' for c in requestid):raise ValueError('Bound64hex request identity required')
    #Both sourcecuts must be explicitly known orNone(unknown),neverdefault[].
    targets={ctx[k]['id'] for k in ('endplate','cleat')}
    if set(existing_cuts)!=targets:raise ValueError('Both actualsource existing-cut rosters required,withNone forunknown')
    mach=machining(ctx,frame,existing_cuts);parts=[]
    holes=[dict(axis=1,at_m=[u,0.,w],radius_m=.0061,length_m=.0015) for u in (-.080,.080) for w in (-.050,.050)]
    padV=.200*.0015*.180-4*pi*.0061**2*.0015
    parts.append(part('isolation-pad','GFRP',dict(kind='drilled-box',size_m=[.200,.0015,.180],holes=holes),[0.,.00075,0.],padV,.204*.0015*.184,.25,.15,
      function='Full1.5mm nominalgap isolation; sourcefit/flatness/compression/fire/creep unqualified'))
    layers=[('GFRPwasher','GFRP',.0265,.0285,.010,.00425),('steelwasher','steel',.0285,.030,.008,.00425),
      ('spacer','steel',.030,.032,.008,.00425),('lock0','steel',.032,.033,.008,.00425),('lock1','steel',.033,.034,.008,.00425)]
    for u in (-.080,.080):
      for w in (-.050,.050):
        key=f'{u}/{w}'
        bushV=pi*(.006**2-.00425**2)*.0265
        parts.append(part('bush/'+key,'GFRP',dict(kind='annulus',axis=1,length_m=.0265,outer_radius_m=.006,inner_radius_m=.00425),[u,.01325,w],bushV,pi*(.006**2-.00425**2)*.0305,.10,.06,
          function='Continuousshaftisolation throughAlendplate andpad;0.1mmnominalradialboreclearance,not bondedorcrushstrengthproof'))
        for name,mat,a,b,ro,ri in layers:
            V=pi*(ro*ro-ri*ri)*(b-a);net=[.70*V,V] if name.startswith('lock') else V
            parts.append(part(name+'/'+key,mat,dict(kind='annulus-or-supplier-lock-envelope' if name.startswith('lock') else 'annulus',axis=1,length_m=b-a,outer_radius_m=ro,inner_radius_m=ri),[u,(a+b)/2,w],net,1.2*V,.04,.03,
              actual_lock_wedge_serrations_grade_preload_function_verified=False if name.startswith('lock') else None))
        #Oneownedfinishedboltallowance. Fullthreadroot/socket geometryunknown;
        #bounds cannotbe promotedas an exactfilledcylinder/head solid.
        head=pi*.0065**2*.008;socket=3*sqrt(3)/2*(.0062/sqrt(3))**2*.004
        shaftlo=pi*.003**2*.040;shafthi=pi*.004**2*.040
        parts.append(part('M8x40/'+key,'steel',dict(kind='fullythreaded-bolt-envelope',axis=1,direction=-1,reference='underhead-plane',bounds_m=[[-.0065,-.040,-.0065],[.0065,.008,.0065]],major_diameter_m=.008,underhead_length_m=.040,
          head_OD_m=.013,head_height_m=.008,hex_socket_AF_m=.0062,hex_socket_depth_m=.004),[u,.034,w],
          [head-socket+shaftlo,head-socket+shafthi],pi*.007**2*.059,.25,.15,
          function='M8-pitch1.25 requestedhypothesis; actualsupplierthreadroot/grade/head/drivingcapability unknown; no smoothshank strengthcredit'))
        parts.append(part('head-weathercap/'+key,'elastomer',dict(kind='supplier-envelope',size_m=[.016,.009,.016]),[u,.0385,w],
          [.3e-6,.9e-6],1.2e-6,.02,.02,function='Removebefore driver; actualretention/fire/watercompound andcapgeometryunknown'))
    #Only compatiblemetal pairs:Alheader->existingAlendplate,steelcleat->steelwall.
    welds=[line_weld(.120,-.090,.080,.004,.0265,'Al5356-hypothesis',[ctx['header']['id'],ctx['endplate']['id']]),
      line_weld(.200,-.090,.080,.004,-.010,'steel-filler-hypothesis',[ctx['cleat']['id'],ctx['main_wall']['id']])]
    for i,wl in enumerate(welds):
        parts.append(part('weld/'+str(i),wl['material'],dict(kind='finite-triangular-weld-drawing',paths_m=wl['paths_m'],profiles=wl['profiles'],leg_m=wl['leg_m']),[0.,0.,0.],wl['net_volume_m3'],wl['gross_volume_m3'],wl['process_h'],wl['QA_h'],
          prior_seam_provenance_or_removal_credit_required=True,actual_WPS_HAZ_and_finishedtriangle_unknown=True))
    #Positiveconsumables; bottomdrainbreak andopeninneredge remainvisible.
    sealL=2*(.200+2*.180);sealV=sealL*.002*.002/2
    parts.append(part('seal-top-and-sides','sealant',dict(kind='route-allowance',length_m=sealL,cross_section_m2=.002**2/2),[0.,0.,0.],sealV,1.5*sealV,.12,.08,
      bottom_unsealed_drain_break_m=.004,actual_seal_geometry_groove_coverage_andtool_interface_held=True,compound_adhesion_fire_andcreep_unknown=True))
    coatA=2*(.200*.180)+2*(.200+.180)*.010;coatV=coatA*.00008
    parts.append(part('steel-weld-repair-finish','coating',dict(kind='noncollision-surface-allocation',reference_surface_m2=coatA,film_m=.00008),[0.,-.010,0.],coatV,1.2*coatV,.20,.12,
      masked_bearing_thread_andisolationfaces=True,coverage_grade_unknown=True))
    parts.append(part('thread-compound','compound',dict(kind='noncollision-mass-allocation'),[0.,0.,0.],[1e-6,4e-6],5e-6,.08,.05,
      amount_basis='Positive4boltapplicationplanningallowance; actualcompatibility/torque/preload unqualified'))
    cap=capacity(actions,strengths,welds)
    #No source mass/cost is copied into newstock or credited twice.
    physical=dict(family=FAMILY,parent_physical_id=P6['physical_id'],source_geometry={k:{n:deepcopy(ctx[k][n]) for n in ('id','geometry','at_m','rotation','frame','material_id')} for k in ('header','endplate','cleat','main_wall','diaphragm')},
      frame={k:deepcopy(frame[k]) for k in ('origin_m','rotation','side')},new_parts=[{k:deepcopy(p[k]) for k in ('id','material','quantity','frame','geometry','at_m','rotation','role')} for p in parts],
      planned_source_machining=[{k:deepcopy(x[k]) for k in ('part_id','new_pilots_or_through_cuts','major_thread_envelopes')} for x in mach],welds=[{k:deepcopy(w[k]) for k in ('material','parents','paths_m','profiles','leg_m')} for w in welds])
    source_process_hours=sum(r['process_h']+r['QA_h'] for r in mach)
    source_process_USD=None if material_policy is None or material_policy.get('labour_USD_h') is None else [source_process_hours*number(v,positive=True) for v in material_policy['labour_USD_h']]
    value=dict(schema='osr-header-isolated-blind-joint-source-outline/1',units='m,kg,N,Nm,Pa,USD',actual_source_machining_applied=False,source_context_id=identity(ctx),source_binding=deepcopy(source_binding),source_p6=deepcopy(P6),
      physical_definition=physical,physical_definition_id=identity(physical),parts=parts,machining=mach,welds=welds,materials=materials_account(parts,material_policy),capacity=cap,source_machining_process=dict(hours=source_process_hours,cost_USD=source_process_USD,paid_rawstock_again=False),
      source_ownership=dict(retained_endplate_once=True,retained_header_cleat_mainwall_anddiaphragm_once=True,no_new_Alshoe=True,
        source_material_mass_price_copied_to_newstock=False,source_credit_application=False,
        missing_existingweld_or_cut_inventory_remainsheld=True,
        new_steel_root_weld='Whollynew proposedownedfiller/process;notreplacementofanynamedP6girderseam',
        retained_P6_joinery_ids=['retained/underframe/girder-weld-deposit@installation/central-girder/0/0/seam'+str(i) for i in range(4)],
        all_retained_joinery_mass_cost_unchanged=True,old_joinery_overlap_amount=None,old_joinery_mass_credit=None,
        joinery_overlap_scope='Unknownunlocatedaggregatejoineryreservemayoverlap;needs source-specificreconciliation,no exactinstalledsaving orzeroreserveclaim',global_credit_keys=[x['source_credit_key'] for x in mach]),
      stack=dict(bolt_count=4,nut_count=0,nut_absence_reason='Fourblindsteelreceivers; no phantomnut orrearaccess assumed',
        bearing_layer_intervals_m=layers,grip_m=.034,bolt_underhead_m=.040,nominal_engagement_m=.006,usable_thread_m=.007,
        minimum_engagement_after_0p3mm_budget_m=MINIMUM_ENGAGEMENT_M,
        pilot_depth_m=.009,combined_depth_bolt_pad_washer_tolerance_m=.0003,threadmill_cutting_head_axial_m=.001,
        nominal_threadmill_bottom_clearance_m=.001,threadmill_bottom_clearance_after_budget_m=.0007,pilot_tip='Flatbottom6mmendmill interpolatedto6.8mm,then5mmthreadmill; no twister-tip assumption',
        thread_bottom_clearance_m=.001,thread_bottom_clearance_after_0p3mm_budget_m=.0007,
        pilot_tip_clearance_m=.003,backweb_m=.001,backweb_after_0p3mm_budget_m=.0007,
        flatbottom_corner_threadrunout_depth_andactualfit_qualified=False,locking_washerpair_count=4,locking_function_qualified=False),
      source_preservation=dict(central_diaphragm_size_m=[.008,.630,.320],mainwall_thickness_m=.010,header_new_bores=0,mainwall_new_bores=0,
        header_R4_P7_interfaces_moved=False,extra_body_lift_m=0.,source_existingbores_andnewunion_required=True),
      tools_and_sequence=dict(frame=frame,
        machining='MachineAlendplateoffvehicle beforeAlweld/headerjoin; flatmill/threadmillsteelcleat beforeisolation/Alinstallation. Never drillthroughAlintosteel.',
        assembly=['Surveyactualpriorseams/bores; retain exactsource IDs,sourcegrades andonceonlygross/credits',
          'Establishsteelcleat/mainwallrootseam withsteelcompatiblefiller beforeisolation; priorseamoverlap/removalrequiresnewownedrecord',
          'FixtureAlheader+existingAlendplate; applyAl-to-Albottom/sidesUbeforeGFRP/bolts; omitfloor-topweld; inspectcoolandrepairfinish',
          'Fitmeasured1.5mmnominalGFRPpad,continuousbushes andwashers; holdpreload/creep/flatnessunknown; assemblefrontaccessibleM8x40/spacers/lockpairs',
          'Verifyactualengagement/depth/torque/locking/isolation/drain; onlythenfitcountedheadcaps'],
        removal=['Supportandunloadheader; isolate/releaseallP7services/R4chairs/floorinterfaces usingtheir ownedsequences,not silentlydelete them',
          'Remove4headcaps,driverandbackout40mmbolts; captureall8lockwashers/4spacers/4steelwashers/4GFRPwashers beforeheadertranslation',
          'Releaseactualoldexternalattachments; withdrawAlheader+Alendplategroup150mmoutwardVwithfixture; retainsteelcleat/mainwallanddiaphragm',
          'CaptureGFRPpad/bushes; inspectthreads,corrosionandallfits beforehandback'],
        tool=dict(driver_hex_AF_m=.006,head_socket_AF_m=.0062,hex_insertion_m=.004,driver_body_radius_m=.005,driver_full_stroke_m=.100,
          driver_origin_m='each(u=+/-80,w=+/-50),v=.042;approachfrom+V',counterhold='No nut. Rootsteelreceiverandtemporaryfixtureprovide reaction; actualrootstiffness unqualified'),
        bolt_fullwithdrawal_path_m=[[0.,0.,0.],[0.,.060,0.]],header_group_path_m=[[0.,0.,0.],[0.,.150,0.]],
        nominal_tool_header_gap_m=.080-.005-.060-.004,mainwall_drill_remaining_stock_m=.001,
        drain_path_m=[[0.,.013,-.090],[0.,.013,-.110]],
        shared_fixture=dict(quantity_per_family=1,installed=False,mass_bounds_kg=[2.,4.,8.],price_USD=None,WLL_N=None,
          role='Support/counterreaction/surveyjig beforeacceptedattachment; realgeometry/payload/rigging requiredevidence'),
        shared_tools=dict(flat_endmill6mm=1,threadmill5mm=1,hex_driver6mm=1,depth_gauge=1,torque_instrument=1,
          actualsupplier_toolgeometry_mass_cost_origin_andlife_unknown=True),
        continuous_fullbody_tool_lifting_or_translational_acceptance=False),
      alternatives=comparison(ctx,frame),complete_factory_or_installed_cost=False,
      holds=['Actualfourheaderload/moment/reaction/preload envelopes andallsource/purchasedmaterialgrades unknown',
        'ExistingAlendplate/header andsteelcleat/mainwall weldprovenance; no contactalone qualifiesaloadpath',
        '10mmcleatthreads/1mmbackweb/localwall/bolt/head/lock/GFRP bearing/creep/fire andcorrosion requireindependentstructural/physicalevidence',
        'Allroot/WPS/HAZ/fatigue/prestress/rub/torque/retention/differentialexpansion andsealeddrainperformance unqualified',
        'Actualexistingcuts mustbeunionedoncewithnewoperations beforeanysourcecredit; unsupportednoncoaxialunions stop',
        'ThreadCSG/finiteweldtriangles/supplierlocks/headcaps/tool/counterhold/lifting andwholebodysweeps areopen'],**FLAGS)
    return seal(value)
