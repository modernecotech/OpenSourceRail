"""Located civil stock, exact longitudinal plant loads and erection hypotheses."""
from math import ceil,pi,fsum,isfinite
from copy import deepcopy
from engineering.design_search import wheel_motor
from engineering.railway_twin import model
from engineering.railway_completion import motor
from . import FLAGS,identity

G=9.80665


def rectangular_load(start,end,total_weight,span_start,span_end):
    """Integrate a uniform finite stock solid against simple-support influence lines."""
    if end<=start or span_end<=span_start or total_weight<0:raise ValueError('Positive stock/span lengths and nonnegative weight required')
    lo=max(start,span_start);hi=min(end,span_end)
    if hi<=lo:return (0.,0.)
    force=total_weight*(hi-lo)/(end-start);center=(hi+lo)/2
    return force*(span_end-center)/(span_end-span_start),force*(center-span_start)/(span_end-span_start)


def point_response(points,start,end):
    L=end-start
    if L<=0:raise ValueError('Positive span required')
    inside=[(x-start,F) for x,F in points if start<=x<=end]
    left=fsum(F*(L-x)/L for x,F in inside);right=fsum(F*x/L for x,F in inside)
    moment=max([0.]+[left*x-fsum(F*(x-y) for y,F in inside if y<x) for x,_ in inside])
    return dict(left_N=left,right_N=right,maximum_bending_Nm=moment)


def moving_envelope(axles,L=20.):
    """Exact quasi-static positive-point-load extrema over each membership interval."""
    if L<=0 or not axles or any(F<0 or not isfinite(o+F) for o,F in axles):raise ValueError('Finite positive axle system required')
    events=sorted({o+t for o,F in axles for t in (0.,L)});fronts=set(events)
    for a,b in zip(events,events[1:]):
        mid=(a+b)/2;active=[(o,F) for o,F in axles if 0<mid-o<L]
        S=fsum(F for o,F in active)
        if S<=0:continue
        A=S+fsum(o*F for o,F in active)/L;B=S/L
        for o,F in active:
            critical=(A+B*o)/(2*B)
            if a<critical<b:fronts.add(critical)
    rows=[point_response([(x-o,F) for o,F in axles],0.,L) for x in sorted(fronts)]
    return dict(maximum_end_reaction_N=max(max(v['left_N'],v['right_N']) for v in rows),
                maximum_bending_Nm=max(v['maximum_bending_Nm'] for v in rows),samples=len(fronts),
                method='piecewise-quadratic moving-point-load extrema',axle_offsets_m=[o for o,F in axles])


def generate(candidate_id,*,distance_m=2000.,section='box',bank_starts_m=(-13.,87.375,187.75,288.125,388.5),
             bank_length_m=20.,car_mass_upper_kg=None,primary_stock=None,axle_positions_m=(2.15,3.65,13.35,14.85),platform_height_above_rail_m=1.,door_side=-1,site=None):
    if distance_m not in (1500.,2000.) or section not in ('box','twin','u'):
        raise ValueError('Explicit reference-cell distance and owned civil family required')
    if not isinstance(candidate_id,str) or len(candidate_id)!=64 or any(c not in '0123456789abcdef' for c in candidate_id):raise ValueError('Exact candidate identity required')
    if not bank_starts_m or len(set(bank_starts_m))!=len(bank_starts_m) or any(type(x) not in (int,float) or not isfinite(x) for x in bank_starts_m) or not isfinite(bank_length_m) or bank_length_m<=0:raise ValueError('Finite distinct bank geometry required')
    if len(axle_positions_m)!=4 or any(not isfinite(x) or not 0<x<17 for x in axle_positions_m):raise ValueError('Four actual axle positions per17mcar required')
    if not isfinite(platform_height_above_rail_m) or platform_height_above_rail_m<=0 or door_side not in (-1,1):raise ValueError('Actual floor datum and door side required')
    stock=[]
    def part(name,kind,at,size,volume,material,density,process,assembly):
        v=dict(id=name,candidate_id=candidate_id,assembly=assembly,kind=kind,at_m=at,size_m=size,
            net_volume_m3=volume,material=material,density_kg_m3=density,mass_kg=volume*density,
            manufacturing_method=process,dimensional_tolerance_m=None,origin=None,
            structural_qualified=False,**FLAGS);v['definition_id']=identity({k:x for k,x in v.items() if k not in ('id','at_m','assembly','candidate_id')});stock.append(v)
    begin=-120.;end=distance_m+20.;span=20.;n=int(round((end-begin)/span));rho=2500.
    # The geometry is a testable design hypothesis, not a verified tendon/cover schedule.
    if section=='box':area=1.8*.8-1.5*.5;I=(1.8*.8**3-1.5*.5**3)/12
    elif section=='twin':area=2*(.5*.9);I=2*.5*.9**3/12
    else:area=1.8*.18+2*.18*.8;I=None
    for i in range(n):
        x=begin+i*span;assembly=f'span/{i}'
        part(assembly+'/concrete',section,[x,0.,8.],[span,1.8,.98 if section=='u' else .8],area*span,'research-concrete-C40/50',rho,'precast-prestressed-mould',assembly)
        for k in range(12):
            part(assembly+f'/strand/{k}','cylinder',[x,-.65+k*.118,8.08],[span,.0152,.0152],.00014*span,'prestressing-strand-hypothesis',7850.,'tension-cast-cure-release',assembly)
        # Individual longitudinal bars; stirrup centreline length counts all four legs.
        for k in range(8):part(assembly+f'/bar/{k}','cylinder',[x,-.7+k*.2,8.12],[span,.016,.016],pi*.016**2/4*span,'rebar-hypothesis',7850.,'cut-bend-tie',assembly)
        for k in range(101):part(assembly+f'/stirrup/{k}','closed-bar-path',[x+k*.2,0.,8.],[.012,1.6,.64],pi*.012**2/4*(2*1.6+2*.64),'rebar-hypothesis',7850.,'cut-bend-tie',assembly)
        for rail in (-.7175,.7175):part(assembly+f'/rail/{rail}','equivalent-rail',[x,rail,8.95-.172],[span,.172,.172],60.*span/7850.,'rail-grade-pending',7850.,'purchased-rail-and-installed-fasteners',assembly)
        for side in (-1,1):
            for k in range(34):part(assembly+f'/rail-fastening/{side}/{k}','box',[x+k*span/34,side*.7175,8.9],[.25,.18,.018],.25*.18*.018,'rail-fastener-steel-hypothesis',7850.,'cast-in-baseplate-drill-anchor-inspect',assembly)
        for side in (-1,1):part(assembly+f'/bearing/{side}','box',[x,side*.55,7.94],[.35,.35,.06],.35*.35*.06,'bearing-equivalent-envelope-unqualified',4000.,'purchased-inspected-replaceable',assembly)
    for i in range(n+1):
        x=begin+i*span;assembly=f'support/{i}'
        for name,at,size in [('foundation',[x-2.,-2.,-1.2],[4.,4.,1.2]),('pier',[x-.45,-.45,0.],[.9,.9,7.4]),('headstock',[x-.6,-1.3,7.4],[1.2,2.6,.54])]:
            part(assembly+'/'+name,'box',at,size,size[0]*size[1]*size[2],'research-concrete-C40/50',rho,'form-rebar-cast-cure-survey',assembly)
    for s,x in enumerate((-110.,distance_m-110.)):
        part(f'station/{s}/platform','box',[x,1.45 if door_side==1 else -5.95,8.95+platform_height_above_rail_m-.25],[110.,4.5,.25],110*4.5*.25,'research-concrete-C40/50',rho,'precast-accessible-platform',f'station/{s}')
    loads=[];primary_instances=[];unknown=[]
    if bank_length_m==20.:
        if primary_stock is None:
            b=motor.rewound_variant(model.materialize()['bundle'])
            primary=[p for p in wheel_motor.stock(b['motor_parameters']) if p['installation']=='wayside']
        else:
            primary=deepcopy(primary_stock)
            if not primary or any(p.get('installation')!='wayside' for p in primary):raise ValueError('Actual wayside stock required')
        primary_ids={p['motor_component_id'] for p in primary}
        if len(primary_ids)!=1:raise ValueError('Mixed primary stock identities')
        for bank,start in enumerate(bank_starts_m):
            for p in primary:
                placed=deepcopy(p);placed.update(id=f'bank/{bank}/'+p['id'],candidate_id=candidate_id,
                    at_m=[start+p['at_m'][0],p['at_m'][1],8.95+p['at_m'][2]],placement_frame='global-elevated-cell; rail-top-z8.95m')
                primary_instances.append(placed)
                # Every tooth/coil/backiron keeps its actual longitudinal extent.
                loads.append(dict(id=f'bank/{bank}/'+p['id'],start_m=start+p['at_m'][0],end_m=start+p['at_m'][0]+p['size_m'][0],weight_N=p['mass_kg']*G,
                                  motor_component_id=p['motor_component_id'],stock_scope=p['geometry_status']))
    else:unknown.append('New motor length requires its own winding, mounted/cooling stock and exact longitudinal load model')
    reactions=[0.]*(n+1);beam_rows=[]
    for i in range(n):
        x=begin+i*span;rows=[p for p in stock if p['assembly']==f'span/{i}'];dead=fsum(p['mass_kg'] for p in rows)*G
        left=right=dead/2
        for p in loads:
            a,c=rectangular_load(p['start_m'],p['end_m'],p['weight_N'],x,x+span);left+=a;right+=c
        reactions[i]+=left;reactions[i+1]+=right
        beam_rows.append(dict(id=f'span/{i}',start_m=x,end_m=x+span,known_dead_left_N=left,known_dead_right_N=right,
            concrete_I_m4=I,known_stock_mass_kg=dead/G,vehicle_moving_reaction=None,qualified_bending_capacity_Nm=None))
    plant_total=fsum(p['weight_N'] for p in loads);dead_total=fsum(p['mass_kg']*G for p in stock if p['assembly'].startswith('span/'))+plant_total
    moving=None
    if car_mass_upper_kg is not None:
        if len(car_mass_upper_kg)!=6 or any(not isfinite(m) or m<=0 for m in car_mass_upper_kg):raise ValueError('Six finite conservative car mass bounds required')
        offsets=[(car*17.5+offset,car_mass_upper_kg[car]*G/4*1.3) for car in range(6) for offset in axle_positions_m]
        moving=dict(equal_axle_share_is_hypothesis=True,dynamic_factor_hypothesis=1.3,
                    **moving_envelope(offsets,20.),actual_wheel_rail_dynamics_validated=False)
    site_result=dict(state='missing-survey-and-geotechnics',allowable_bearing_Pa=None,settlement_m=None)
    if site is not None:
        if site.get('candidate_id')!=candidate_id or site.get('site_record_authenticated') is not True:
            raise ValueError('Site calculations require authenticated same-candidate site inputs')
        # External authentication belongs to the completion evidence adapter; a
        # caller-provided boolean alone is never accepted as an approval here.
        site_result=dict(state='requires-completion-evidence-adapter',allowable_bearing_Pa=None,settlement_m=None)
    production=[]
    for i,r in enumerate(beam_rows):
        crane=r['known_stock_mass_kg'];production.append(dict(id='erect/'+r['id'],candidate_id=candidate_id,asset_id=r['id'],
            predecessors=[] if i==0 else [f'erect/span/{i-1}'],process=['mould-and-rebar','cast','cure-to-tested-release-strength','inspect','transport','lift','survey-and-grout'],
            curing_hours=None,transport_width_m=1.8,transport_length_m=20.,known_hook_mass_kg=crane,
            rigging_mass_kg=None,required_crane_capacity_kg=None,crew_hours=None,production_slot=None,QA_record=None))
    value=dict(schema='osr-reference-cell-civil/1',candidate_id=candidate_id,distance_m=distance_m,
        counted_interval_m=[begin,end],section=section,span_count=n,support_count=n+1,stations=2,
        platform_intervals_m=[[-110.,0.],[distance_m-110.,distance_m]],
        platform_top_above_rail_m=platform_height_above_rail_m,platform_side=door_side,boarding_gap_hypothesis_m=.05,boarding_accessibility_qualified=False,stock=stock,
        known_material_mass_kg=fsum(p['mass_kg'] for p in stock),concrete_volume_m3=fsum(p['net_volume_m3'] for p in stock if p['material'].startswith('research-concrete')),
        primary_loads=loads,primary_instances=primary_instances,rail_top_global_z_m=8.95,known_primary_weight_N=plant_total,support_known_superstructure_reactions_N=reactions,
        support_force_residual_N=fsum(reactions)-dead_total,beam_loads=beam_rows,moving_load_screen=moving,site=site_result,
        construction_sequence=production,complete_installed_mass_kg=None,
        open_items=unknown+['Actual prestress losses/anchorages, full rebar/cover, lateral/torsional/seismic/erection checks',
            'Ground, utilities, piles, settlement, scour/flood and actual foundation design',
            'Station roof/supports, lifts/stairs/accessibility, evacuation/containment/drainage and platform interfaces',
            'Actual plant mounts/cooling/cabling, crane/rigging/transport route/crew and QA procedures'],**FLAGS)
    value['evaluation_id']=identity(value);return value
