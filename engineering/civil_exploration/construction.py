"""Canonical shipping/lifting units and the existing finite-resource CPM."""
from __future__ import annotations
from copy import deepcopy
import math

from tools.automation.project_twin import apply_resource_cpm
from osr_mech.civil.exploration import geometry,foundation_geometry
from .model import takeoff,deck_physics,cement_area,pier_physics

METHODS={'precast-full','segmental','shell-infill','in-situ'}


def units(candidate,study,method,pier_method,cap_method='precast'):
    if method not in METHODS or pier_method not in ('cast-in-place','segmental','shell-infill') or cap_method not in ('precast','cast-in-place'):
        raise ValueError('construction method not registered')
    q=takeoff(candidate,study);g=geometry(candidate['definition']);span=candidate['definition']['deck']['span_m']
    a=candidate['mass_allowances'];pieces=[]
    count=math.ceil(span/5.) if method=='segmental' else 1
    if method!='in-situ':
        for i in range(count):
            lo,hi=span*i/count,span*(i+1)/count;mass=0.;centroid=0.;concrete=0.
            for s in g['deck']:
                l,r=max(lo,s['start_m']),min(hi,s['end_m'])
                if r<=l:continue
                if method=='shell-infill':
                    # Transport the non-concrete structural skeleton, inserts
                    # and the full rebar allowance; site concrete is separate.
                    density=math.fsum(region['width_m']*region['height_m']*candidate['material_records'][role]['density_kg_m3']
                                     for region,role in zip(s['regions'],s['material_roles']) if role not in ('concrete','uhpc'))
                else:density=deck_physics(candidate,s)['mass_kg_m']
                density+=cement_area(s)*a['reinforcement_kg_m3']+a['prestress_kg_m']+a['embedded_kg_per_beam']/span
                dm=(r-l)*density;mass+=dm;centroid+=dm*(r+l)/2;concrete+=(r-l)*cement_area(s)
            pieces.append(dict(unit=i+1,length_m=hi-lo,transport_mass_kg=mass,centre_x_m=centroid/mass,
                               suspended_mass_kg=mass+a['rigging_kg_per_lift'],concrete_service_volume_m3=concrete))
    support=candidate.get('support_material',candidate['material'])
    rebar=a['reinforcement_kg_m3'];pier_lifts=[]
    if pier_method!='cast-in-place':
        height=candidate['definition']['pier']['height_m'];n=math.ceil(height/2.) if pier_method=='segmental' else 1
        for i in range(n):
            mass=0.
            for s in g['pier']:
                overlap=max(0.,min(s['end_m'],height*(i+1)/n)-max(s['start_m'],height*i/n))
                if pier_method=='shell-infill':
                    roles=s.get('material_roles',[])
                    density=sum(r['width_m']*r['height_m']*candidate['material_records'][role]['density_kg_m3'] for r,role in zip(s['regions'],roles) if role=='frp')
                    density+=rebar*cement_area(s)
                else:density=pier_physics(candidate,s)['mass_kg_m']+rebar*cement_area(s)
                mass+=overlap*density
            pier_lifts.append(dict(segment=i+1,transport_mass_kg=mass,suspended_mass_kg=mass+a['rigging_kg_per_lift']))
    cap_mass=g['cap_concrete_m3']*(support['density_kg_m3']+rebar)
    cap_lifts=q['supports'] if cap_method=='precast' else 0
    pile_units=[];fg=foundation_geometry(candidate['foundation'])
    if candidate['foundation'].get('installation_method')=='driven':
        density=candidate.get('foundation_material',support)['density_kg_m3']+rebar
        for pile in fg['piles']:
            n=math.ceil(pile['length_m']/12.)
            for segment in range(n):
                mass=pile['concrete_m3']/n*density
                pile_units.append(dict(pile_id=pile['id'],segment=segment+1,length_m=pile['length_m']/n,
                                       concrete_m3=pile['concrete_m3']/n,transport_mass_kg=mass,suspended_mass_kg=mass+a['rigging_kg_per_lift']))
    masses=[p['suspended_mass_kg'] for p in pieces+pier_lifts+pile_units]+([cap_mass+a['rigging_kg_per_lift']] if cap_lifts else [])
    transport_lengths=[u['length_m'] for u in pieces]
    transport_lengths.extend(u['length_m'] for u in pile_units)
    if pier_lifts:transport_lengths.append(2. if pier_method=='segmental' else candidate['definition']['pier']['height_m'])
    if cap_lifts:transport_lengths.append(g['cap_width_m'])
    return dict(beam_method=method,pier_method=pier_method,cap_method=cap_method,
                per_beam_units=pieces,per_pier_units=pier_lifts,beam_units=len(pieces)*q['beam_lifts'],
                per_support_pile_units=pile_units,pile_delivery_units=len(pile_units)*q['supports'],
                pier_units=len(pier_lifts)*q['supports'],cap_units=cap_lifts,
                total_lifts=len(pieces)*q['beam_lifts']+len(pier_lifts)*q['supports']+cap_lifts,
                maximum_lift_mass_kg=max(masses,default=0.),cap_transport_mass_kg=cap_mass if cap_lifts else 0.,
                maximum_transport_length_m=max(transport_lengths,default=0.),
                service_beam_mass_kg=q['fabricated_beam_mass_kg'],
                logistics_are_conditional=True,construction_release=False,
                gaps=['weighed units and 3D CG','temporary stability/rigging/transport routes','crane/launcher chart and ground pressure','segment joints/anchorage','site curing/bond and formwork qualification'])


def validate_productivity(p):
    required={'basis','capacities','beam_m3_day','shell_kg_day','pier_m3_day','cap_m3_day','pile_m_day',
              'foundation_cap_m3_day','cure_days','site_cure_days','joint_days','lift_units_day','transport_units_day',
              'procurement_days','mobilisation_days','inspection_days','track_m_day','working_hours_per_day','pile_m3_day'}
    if set(p)!=required or not p['basis']:raise ValueError('productivity contract incomplete')
    for key in required-{'basis','capacities','pile_m_day','procurement_days'}:
        if type(p[key]) not in (int,float) or not math.isfinite(p[key]) or p[key]<=0:raise ValueError('productivity must be positive and finite: '+key)
    if set(p['pile_m_day'])!={'bored','CFA','displacement','driven','shallow'}:raise ValueError('installation productivity coverage incomplete')
    for v in list(p['pile_m_day'].values())+list(p['procurement_days'].values()):
        if type(v) not in (int,float) or not math.isfinite(v) or v<=0:raise ValueError('invalid production rate/lead time')
    if set(p['procurement_days'])!={'concrete','uhpc','frp','steel'}:raise ValueError('material lead time coverage incomplete')
    required_resources={'foundation-rig','foundation-cap','pier-crew','precast-bed','pile-bed','curing-yard','cap-bed','transport','erection','infill','site-deck','qa','track','procurement-wait'}
    if set(p['capacities'])!=required_resources or any(type(v) is not int or not 1<=v<=64 for v in p['capacities'].values()):
        raise ValueError('resource capacities must be positive whole numbers with complete scope')


def schedule(candidate,study,construction,productivity):
    validate_productivity(productivity);p=deepcopy(productivity);q=takeoff(candidate,study);g=geometry(candidate['definition'])
    tasks=[]
    def task(uid,days,resource,predecessors=(),external=''):
        # Reuse the repository's integer-slot CPM with working-hour slots.
        tasks.append(dict(manufacturing_uid=uid,duration_days=max(1,math.ceil(days*p['working_hours_per_day'])),work_center=resource,
                          predecessor_uids='; '.join(predecessors),external_predecessors=external,
                          sequence=len(tasks),asset_id=uid,package_id='civil-system'))
        return uid
    role=set(q['deck_material_volumes_m3'])|set(q['pier_material_volumes_m3'])
    procurement=task('procurement',max(p['procurement_days'].get(r,p['procurement_days']['concrete']) for r in role),'procurement-wait',
                     external='supplier quotations and capacity; accepted material/connection designs')
    mobilisation=task('mobilise',p['mobilisation_days'],'foundation-rig',external='accepted survey/soil/utilities; land/access; funding')
    method=candidate['foundation'].get('installation_method','bored')
    f=candidate['foundation'];supports=[]
    for i in range(q['supports']):
        deliveries=[]
        for j,u in enumerate(construction['per_support_pile_units']):
            production=task(f'S{i}-PILE{j}-produce',u['concrete_m3']/p['pile_m3_day'],'pile-bed',[procurement])
            cured=task(f'S{i}-PILE{j}-cure',p['cure_days'],'curing-yard',[production])
            deliveries.append(task(f'S{i}-PILE{j}-deliver',1/p['transport_units_day'],'transport',[cured]))
        qty=f['pile_count']*f['pile_length_m']
        days=(qty/p['pile_m_day'][method] if qty else f['cap_length_m']*f['cap_width_m']*.75/p['pile_m_day']['shallow'])
        if deliveries:days+=max(0,len(construction['per_support_pile_units'])-f['pile_count'])*p['joint_days']/4
        install=task(f'S{i}-ground',days,'foundation-rig',[mobilisation,*deliveries])
        test=task(f'S{i}-ground-qa',p['inspection_days'],'qa',[install],external='representative pile/ground tests and geotechnical acceptance')
        cap=task(f'S{i}-foundation-cap',f['cap_length_m']*f['cap_width_m']*f['cap_depth_m']/p['foundation_cap_m3_day'],'foundation-cap',[test,procurement])
        ready=task(f'S{i}-foundation-cure',p['site_cure_days'],'curing-yard',[cap])
        if construction['pier_method']=='cast-in-place':
            column=task(f'S{i}-pier',q['pier_concrete_m3']/q['supports']/p['pier_m3_day'],'pier-crew',[ready,procurement])
            column=task(f'S{i}-pier-cure',p['site_cure_days'],'curing-yard',[column])
        else:
            shipped=[]
            for j,u in enumerate(construction['per_pier_units']):
                production=task(f'S{i}-P{j}-produce',u['transport_mass_kg']/p['shell_kg_day'] if construction['pier_method']=='shell-infill' else q['pier_concrete_m3']/q['supports']/len(construction['per_pier_units'])/p['pier_m3_day'],'precast-bed',[procurement])
                cured=task(f'S{i}-P{j}-cure',p['cure_days'],'curing-yard',[production])
                delivered=task(f'S{i}-P{j}-transport',1/p['transport_units_day'],'transport',[cured])
                shipped.append(task(f'S{i}-P{j}-place',1/p['lift_units_day'],'erection',[ready,delivered,*shipped[-1:]]))
            column=task(f'S{i}-pier-joint',p['joint_days'],'pier-crew',shipped)
            if construction['pier_method']=='shell-infill':
                column=task(f'S{i}-pier-infill',q['pier_concrete_m3']/q['supports']/p['pier_m3_day'],'infill',[column])
                column=task(f'S{i}-pier-infill-cure',p['site_cure_days'],'curing-yard',[column])
        cap=task(f'S{i}-cap-produce',g['cap_concrete_m3']/p['cap_m3_day'],'cap-bed' if construction['cap_method']=='precast' else 'pier-crew',[procurement] if construction['cap_method']=='precast' else [column])
        cap=task(f'S{i}-cap-cure',p['cure_days'] if construction['cap_method']=='precast' else p['site_cure_days'],'curing-yard',[cap])
        if construction['cap_method']=='precast':
            cap=task(f'S{i}-cap-deliver',1/p['transport_units_day'],'transport',[cap])
            cap=task(f'S{i}-cap-place',1/p['lift_units_day'],'erection',[cap,column])
        supports.append(task(f'S{i}-support-qa',p['inspection_days'],'qa',[cap,column]))
    bays=[]
    for bay in range(q['spans']):
        completed=[]
        for track in range(2):
            if construction['beam_method']=='in-situ':
                form=task(f'B{bay}-T{track}-form',2.,'site-deck',[supports[bay],supports[bay+1]])
                cast=task(f'B{bay}-T{track}-cast',q['deck_concrete_m3']/q['beam_lifts']/p['beam_m3_day'],'site-deck',[form,procurement])
                completed.append(task(f'B{bay}-T{track}-cure',p['site_cure_days'],'curing-yard',[cast]))
                continue
            placed=[]
            for j,u in enumerate(construction['per_beam_units']):
                predecessors=[procurement]
                if construction['beam_method']=='precast-full' and set(q['deck_material_volumes_m3'])-{'concrete','uhpc'}:
                    skeleton_mass=sum(volume*candidate['material_records'][role]['density_kg_m3'] for role,volume in q['deck_material_volumes_m3'].items() if role not in ('concrete','uhpc'))/q['beam_lifts']/len(construction['per_beam_units'])
                    predecessors=[task(f'B{bay}-T{track}-U{j}-skeleton',skeleton_mass/p['shell_kg_day'],'precast-bed',[procurement])]
                production=task(f'B{bay}-T{track}-U{j}-produce',u['transport_mass_kg']/p['shell_kg_day'] if construction['beam_method']=='shell-infill' else u['concrete_service_volume_m3']/p['beam_m3_day'],'precast-bed',predecessors)
                cured=task(f'B{bay}-T{track}-U{j}-cure',p['cure_days'],'curing-yard',[production])
                shipped=task(f'B{bay}-T{track}-U{j}-transport',1/p['transport_units_day'],'transport',[cured])
                placed.append(task(f'B{bay}-T{track}-U{j}-place',1/p['lift_units_day'],'erection',[shipped,supports[bay],supports[bay+1],*placed[-1:]]))
            finish=placed[-1]
            if construction['beam_method'] in ('segmental','shell-infill'):
                finish=task(f'B{bay}-T{track}-connect',p['joint_days'],'infill',placed)
            if construction['beam_method']=='shell-infill':
                finish=task(f'B{bay}-T{track}-concrete',q['deck_concrete_m3']/q['beam_lifts']/p['beam_m3_day'],'infill',[finish])
                finish=task(f'B{bay}-T{track}-site-cure',p['site_cure_days'],'curing-yard',[finish])
            completed.append(finish)
        bays.append(task(f'B{bay}-bay-qa',p['inspection_days'],'qa',completed,external='load path/temporary works/rigging and engineer inspection'))
    closures=[]
    if study.get('connection_scheme','simple-span')!='simple-span':
        for i in range(q['spans']-1):
            cast=task(f'J{i}-continuity',p['joint_days'],'infill',bays[i:i+2],external='engineer-accepted staged joint/tendon design')
            closures.append(task(f'J{i}-cure',p['site_cure_days'],'curing-yard',[cast]))
    track=task('track-walkways-drainage',study['route_length_m']*2/p['track_m_day'],'track',bays+closures)
    task('package-inspection',p['inspection_days'],'qa',[track],external='physical validation; independent acceptance; railway commissioning')
    summary=apply_resource_cpm(tasks,p['capacities'])
    occupancy={resource:sum(t['duration_days'] for t in tasks if t['work_center']==resource) for resource in p['capacities']}
    summary['programme_working_hours']=summary['programme_working_days']
    summary['programme_working_days']/=p['working_hours_per_day']
    for t in tasks:
        for key in ('duration_days','planned_start_day','planned_finish_day','late_start_day','late_finish_day','total_float_days'):
            t[key.replace('_days','_hours').replace('_day','_hour')]=t.pop(key)
        t['planned_start_basis']='working_hour_'+str(t['planned_start_hour'])
        t['planned_finish_basis']='working_hour_'+str(t['planned_finish_hour'])
    occupancy={k:v/p['working_hours_per_day'] for k,v in occupancy.items()}
    return dict(schema='osr-civil-construction-scenario/1',**summary,tasks=tasks,resource_working_days=occupancy,
                quantities=construction,input_basis=p['basis'],conditional_start_after_external_gates=True,
                time_basis='working-hour slots, finite resources, conservative whole-hour rounding; curing represented as working-day waits; no adopted Baghdad calendar',
                site_duration_is_not_delivery_promise=True,construction_release=False)
