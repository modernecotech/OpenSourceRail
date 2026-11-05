"""Quantity-based civil outline templates; no site or structural acceptance."""
from copy import deepcopy
from math import ceil, fsum, isclose, isfinite, pi
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity
from engineering.design_search import line_benchmark_civil
from . import civil_supply

PRODUCER='engineering/outline/city_civil.py'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
    operating_release=False,selected_reference_changed=False,movement_authority=False)
CASES=('low','base','high')
DEFAULTS=dict(version='CITY-CIVIL-OUTLINE-1',precast_scenario='project-make-buy',
    locality_transfer_factors=[.75,1.,1.75],soil_capacity_kpa=[300.,200.,100.],
    at_grade_formation_m3_per_route_m=5.,at_grade_concrete_m3_per_route_m=1.2,
    at_grade_earthwork_usd_m3=[6.,15.,40.],at_grade_drain_fence_usd_route_m=[80.,200.,600.],
    at_grade_protected_crossing_spacing_m=1000.,at_grade_protected_crossing_usd=[100000.,400000.,1500000.],
    bridge_foundation_extra_usd_support=[50000.,200000.,800000.],
    bridge_special_deck_usd_route_m=[500.,1500.,6000.],bridge_temporary_usd_run=[250000.,1000000.,4000000.],
    tunnel_bore_radius_m=3.5,tunnel_lining_m3_per_route_m=15.,
    tunnel_excavation_usd_m3=[75.,150.,400.],tunnel_fitout_usd_route_m=[1000.,3000.,8000.],
    tunnel_portal_usd=[1000000.,3000000.,10000000.],
    ventilation_egress_usd_route_m=[500.,1500.,5000.])


def _num(v,name,zero=False):
    if type(v) not in (int,float) or not isfinite(v) or (v<0 if zero else v<=0):
        raise ValueError('Finite '+('nonnegative ' if zero else 'positive ')+name+' required')
    return float(v)


def _policy(policy):
    p=deepcopy(DEFAULTS);over=(policy or {}).get('civil',{})
    if set(over)-set(p):raise ValueError('Unknown civil policy key')
    p.update(over)
    for k,v in p.items():
        if isinstance(v,list):
            if len(v)!=3:raise ValueError('Three civil sensitivity cases required')
            for n in v:_num(n,k)
        elif type(v) in (int,float):_num(v,k)
    if p['soil_capacity_kpa'] != [300.,200.,100.]:raise ValueError('Current soil template requires300/200/100 kPa scenarios')
    if p['precast_scenario'] not in ('china-bulk-buy','project-make-buy'):raise ValueError('Unknown precast scenario')
    return p


def quantities(city_input,policy=None):
    """Merge contiguous civil classes before rounding repeat-span quantities."""
    p=_policy(policy);lines=city_input['lines'];ids=[z['line_id'] for z in lines]
    if not lines or len(ids)!=len(set(ids)):raise ValueError('Unique nonempty city lines required')
    by={k:[] for k in ids}
    for z in city_input.get('civil_segments',[]):
        if z['line_id'] not in by:raise ValueError('Civil segment has unknown line')
        if z['class'] not in ('at-grade','elevated','bridge','tunnel'):raise ValueError('Unknown civil alignment class')
        by[z['line_id']].append(z)
    runs=[];totals={k:0. for k in ('at-grade','elevated','bridge','tunnel')};spans=supports=0
    for line in lines:
        length=_num(line['route_m'],'mapped route length');prior=0.;merged=[]
        raw=by[line['line_id']] or [dict(line_id=line['line_id'],**{'class':'elevated'},from_m=0.,to_m=length,assumed=True)]
        for z in sorted(raw,key=lambda a:a['from_m']):
            a=_num(z['from_m'],'civil start',True);b=_num(z['to_m'],'civil end')
            if b<=a or not isclose(a,prior,abs_tol=.02) or b>length+.02:raise ValueError('Civil intervals overlap, gap or exceed mapped line')
            if merged and merged[-1]['class']==z['class']:
                merged[-1]['to_m']=b
            else:merged.append(dict(line_id=line['line_id'],**{'class':z['class']},from_m=a,to_m=b,assumed=z.get('assumed',False)))
            prior=b
        if not isclose(prior,length,abs_tol=.02):raise ValueError('Civil intervals do not cover complete line')
        # Ring endpoints with the same class are one physical production run.
        if line['shape']=='ring' and len(merged)>1 and merged[0]['class']==merged[-1]['class']:
            first=merged.pop(0);merged[-1]['extra_wrap_m']=first['to_m']-first['from_m']
        for z in merged:
            L=z['to_m']-z['from_m']+z.get('extra_wrap_m',0.);z['length_m']=L;totals[z['class']]+=L
            if z['class'] in ('elevated','bridge'):
                n=ceil(L/20.);z['span_count']=2*n
                z['supports']=2*(n if line['shape']=='ring' and len(merged)==1 else n+1)
                spans+=z['span_count'];supports+=z['supports']
            runs.append(z)
    route=fsum(z['route_m'] for z in lines)
    if not isclose(fsum(totals.values()),route,abs_tol=.1):raise ValueError('Civil class lengths do not reconcile')
    q=dict(route_m=route,track_m=2*route,rail_m=4*route,rail_kg=4*route*60.21,
        fastener_sets=ceil(4*route/(20/35)),class_route_m=totals,runs=runs,
        span_count=spans,independent_supports=supports,
        at_grade_crossing_packages=sum(ceil(z['length_m']/p['at_grade_protected_crossing_spacing_m']) for z in runs if z['class']=='at-grade'),
        tunnel_portals=2*sum(z['class']=='tunnel' for z in runs),
        bridge_runs=sum(z['class']=='bridge' for z in runs),
        ordinary_foundations_are_necessary_bounds_only=True)
    q['quantity_id']=identity(q);return q


def evaluate(city_input,context,policy=None,root=ROOT):
    """Price actual alignment quantities with one network production comparison."""
    root=Path(root);p=_policy(policy);q=quantities(city_input,policy);s=deepcopy(context['spec']);fx=s['currency']['iqd_per_usd']
    # Pricing reference has precisely the network's committed repeat-beam count.
    # It is not a replacement city geometry or a claim that all routes are elevated.
    r=deepcopy(s['requirements']);r.update(route_km=max(20.,q['span_count']*10.)/1000,stations=2)
    d=deepcopy(s['design']);d.update(platform_continuity_cost_assumption=False)
    reference=line_benchmark_civil.evaluate(r,d,context['vehicle'],root=root)
    supply_spec=deepcopy(s);supply_spec['requirements']=r;supply_spec['design']=d
    supply=civil_supply.revalue(reference,supply_spec,p['precast_scenario'],root=root)
    beam_dec=next(z for z in supply['decisions'] if z['item']=='structural-precast-beam')
    owns=q['span_count']>0 and beam_dec['selected_route']=='make'
    rows=[]
    def add(key,scope,quantity,amounts,basis,life=[60.,50.,40.]):
        row=dict(key=key,scope=scope,quantity=quantity,costs_usd=dict(zip(CASES,amounts)),basis=basis,source_class='C',life_years=life)
        row['line_id']=identity(row);rows.append(row)
    rails=[];fasteners=[];beams=[];foundations=[];erection=[];surface=[];bridge=[];tunnel=[];walk=[];fixed=[];floor=[];yard=[]
    for i,case in enumerate(CASES):
        transfer=p['locality_transfer_factors'][i];u=supply['civil']['unit_rates'][case];rates=reference['statistical_rates_iqd']
        rails.append(q['rail_kg']*u['rail_factory_iqd_kg']/fx)
        # Buy complete fasteners at citywide route quantity; local fastener
        # factory from the beam-only comparison is never silently charged.
        purchase=next(z for z in supply['decisions'] if z['item']=='complete-fasteners')['comparison']['cases'][case]['purchase']['per_unit']
        fasteners.append(q['fastener_sets']*purchase)
        bc=beam_dec['comparison']['cases'][case]
        unit=bc['make']['variable_total']/bc['make']['quantity'] if owns else bc['purchase']['per_unit']
        beams.append(q['span_count']*unit*transfer)
        # Geotechnical scenarios affect quantities; each is explicitly a bounded
        # outline case, not three verified designs with common installed mass.
        soil=reference['soil_gravity_necessary_bounds'][i]
        concrete=(soil['footing_concrete_m3']+soil['pier_concrete_m3'])*q['independent_supports']
        cu=u['concrete_ingredient_iqd_m3']/fx;rebar=supply['assumptions']['rebar_selected_usd_kg'][i]
        foundation=(concrete*cu+concrete*160*rebar/[.98,.95,.9][i]
            +q['independent_supports']*(reference['process_assumptions']['substructure_formwork_excavation_other_plant_iqd_per_support'][i]/fx
                +reference['process_assumptions']['support_field_h_each'][i]*u['productive_two_shift_wage_iqd_h']/fx))
        foundations.append(foundation*transfer)
        process=reference['process_assumptions'];n=q['span_count'];mass=reference['beam']['total_counted_span_mass_kg']/1000
        erection.append((n*mass*d.get('haul_km',50)*process['transport_iqd_per_tonne_km'][i]/fx
            +ceil(n/process['spans_per_crane_shift'][i])*process['crane_iqd_per_shift'][i]/fx
            +n*process['erection_h_per_span'][i]*u['productive_two_shift_wage_iqd_h']/fx
            +q['track_m']*u['rail_field_install_iqd_track_m']/fx
            +sum(4*max(0,ceil(line['route_m']/20)-1) for line in city_input['lines'])*process['butt_weld_complete_iqd_each'][i]/fx)*transfer)
        L=q['class_route_m']['at-grade']
        surface.append((L*(p['at_grade_formation_m3_per_route_m']*p['at_grade_earthwork_usd_m3'][i]
            +p['at_grade_concrete_m3_per_route_m']*(cu+160*rebar)
            +p['at_grade_drain_fence_usd_route_m'][i])+q['at_grade_crossing_packages']*p['at_grade_protected_crossing_usd'][i])*transfer)
        n_bridge=sum(z.get('supports',0) for z in q['runs'] if z['class']=='bridge')
        bridge.append((n_bridge*p['bridge_foundation_extra_usd_support'][i]
            +q['class_route_m']['bridge']*p['bridge_special_deck_usd_route_m'][i]
            +q['bridge_runs']*p['bridge_temporary_usd_run'][i])*transfer)
        L=q['class_route_m']['tunnel']
        tunnel.append((L*(2*pi*p['tunnel_bore_radius_m']**2*p['tunnel_excavation_usd_m3'][i]
            +p['tunnel_lining_m3_per_route_m']*(cu+200*rebar)+p['tunnel_fitout_usd_route_m'][i]
            +p['ventilation_egress_usd_route_m'][i])+q['tunnel_portals']*p['tunnel_portal_usd'][i])*transfer)
        walk.append((q['class_route_m']['elevated']+q['class_route_m']['bridge'])*2*process['protected_walkway_iqd_per_track_m'][i]/fx*transfer)
        fixed.append((bc['make']['fixed_total']-bc['make']['fixed_components']['building'])*transfer if owns else 0.)
        floor.append(supply['precast_floor_m2'][i] if owns else 0.);yard.append(supply['precast_yard_m2'][i] if owns else 0.)
    add('route-running-rails','guideway',dict(kg=q['rail_kg']),rails,'Same 60E1 finished profile at explicit landed rates; no GB43 substitution.')
    add('route-complete-fasteners','guideway',dict(sets=q['fastener_sets']),fasteners,'Complete assemblies bought; no second fastener factory capital.')
    add('repeat-box-beams','guideway',dict(spans=q['span_count']),beams,'Selected 20 m crowd-control box quantity and local fabrication template; bridge extras separate.')
    add('piers-and-foundations','construction',dict(supports=q['independent_supports'],soil_cases_kpa=p['soil_capacity_kpa']),foundations,'300/200/100 kPa necessary gravity-closed scenarios; no geotechnical design acceptance.')
    add('transport-crane-erection-track-install','construction',dict(track_m=q['track_m']),erection,'Explicit haul, crane shifts at unverified radius, two-shift erection, track-m installation and rail welds.')
    add('surface-formation-drainage-crossings','construction',dict(route_m=q['class_route_m']['at-grade'],crossings=q['at_grade_crossing_packages']),surface,'Slab/formation/fencing/drainage and protected crossing packages; mapped crossings remain unverified.')
    add('bridge-special-foundations-deck-temporary','construction',dict(route_m=q['class_route_m']['bridge'],runs=q['bridge_runs']),bridge,'Nonzero special water/scour/temporary-work and deck reserves in addition to ordinary repeat spans; no crossing geometry approval.')
    add('tunnels-portals-lining-ventilation-egress','construction',dict(route_m=q['class_route_m']['tunnel'],portals=q['tunnel_portals']),tunnel,'Two-bore excavation volume, lining steel/concrete, systems, portals and evacuation reserve; no geology acceptance.')
    add('protected-elevated-walkways','construction',dict(track_m=2*(q['class_route_m']['elevated']+q['class_route_m']['bridge'])),walk,'Continuous protected route retained; no platform-footprint credit without demonstrated continuity.')
    # Explicit nonzero bearings/end details are not lost when stripping old beam cost.
    for key,unit in [('bearing-pads',[4*v for v in reference['process_assumptions']['bearing_complete_iqd_per_pad']]),('beam-joints-drains-lifting',reference['process_assumptions']['end_joint_drains_lifting_hardware_iqd_per_span'])]:
        add(key,'guideway',dict(spans=q['span_count']),[q['span_count']*unit[i]/fx*p['locality_transfer_factors'][i] for i in range(3)],'Bounded complete bearing/joint/drain/lifting package; no zero detail allowance.')
    source={**context.get('sources',{}),**city_input.get('source_sha256',{}),**supply['source_sha256'],PRODUCER:digest(root/PRODUCER)}
    value=dict(schema='osr-city-civil-outline/1',city_input_id=city_input['input_id'],quantities=q,capital_lines=rows,
        owned_factory_capital_usd=dict(zip(CASES,fixed)),precast_floor_m2=floor,precast_yard_m2=yard,
        factory_decision=dict(selected_route='make' if owns else 'local-contractor',comparison=beam_dec['comparison'],committed_spans=q['span_count']),
        unit_rates={case:{**supply['civil']['unit_rates'][case], 'complete_8kg_fastener_factory_iqd_set': next(z for z in supply['decisions'] if z['item']=='complete-fasteners')['comparison']['cases'][case]['purchase']['per_unit']*fx} for case in CASES},source_sha256=source,assumptions=dict(policy=p,
            pricing_basis='Iraq CSO/China supply and explicit local-process Class C transfer scenarios; no foreign locality is claimed to have verified Iraqi rates.',
            beam_reference_is_pricing_template_only=True,ordinary_mass_and_magnetic_clearance_unqualified=True,
            prestress_transfer_handling_temporary_stability_foundation_torsion_moving_loads_unqualified=True,
            work_shifts=2,production_shifts=2,native_solvers=0),**FLAGS)
    value['evaluation_id']=identity(value);return value
