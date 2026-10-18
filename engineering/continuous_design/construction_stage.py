"""Unit handling demands and explicit construction-completion dependencies.

Gross elastic handling screens and scenario restraints are not qualified lift,
early-age strength, joint, temporary works or soil designs.
"""
import math
from . import beam_confirmation,delivery_simulation,qa_traveller


def crane_capacity(chart,radius):
    if type(radius) not in (int,float) or not math.isfinite(radius) or radius<0:raise ValueError('finite lifting radius required')
    if not chart or any(len(p)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in p) for p in chart):
        raise ValueError('finite positive radius/capacity pairs required')
    if any(a[0]>=b[0] or a[1]<b[1] for a,b in zip(chart,chart[1:])):raise ValueError('ordered conservative crane chart required')
    for reach,capacity in chart:
        if radius<=reach:return capacity
    return None


def handling(kit):
    from engineering.civil_exploration.model import deck_physics
    from osr_mech.civil.exploration import geometry
    basis=kit['basis'];lift=basis['lifting'];transport=basis['transport'];records=[];checks={};unknown=[]
    sections=geometry(kit['candidate']['definition'])['deck']
    ei=min(deck_physics(kit['candidate'],s)['effective_EI_nm2'] for s in sections)
    factor=max(deck_physics(kit['candidate'],s)['fibre_stress_per_moment'] for s in sections)
    capacity=crane_capacity(lift['chart'],lift['radius_m'])
    for u in kit['units']:
        uid=u['id'];suspended=u['mass_kg']+lift['rigging_kg'] if u['offsite'] else 0.
        if u['offsite']:
            checks[uid+'/transport-envelope']=all(a<=b+1e-9 for a,b in zip(u['transport_dimensions_m'],transport['maximum_dimensions_m']))
            checks[uid+'/transport-payload']=u['mass_kg']<=transport['payload_kg']
            checks[uid+'/crane-at-radius']=capacity is not None and suspended<=capacity
            pressure=(lift['crane_self_mass_kg']+suspended)*9.81/lift['mat_area_m2']
            checks[uid+'/ground-pressure-hypothesis']=pressure<=lift['ground_pressure_limit_pa']
        else:pressure=None
        locating=u['locating_features'];connection=basis['connections']
        checks[uid+'/fit-tolerance']=locating['guide_clearance_m']>=locating['tolerance_stack_m']
        checks[uid+'/positive-lock-engagement']=locating['lock_engagement_m']>=connection['required_engagement_m']
        stages=[]
        if u['category']=='deck':
            length=u['deck_length_m'];pick=basis['handling']['pick_fraction']
            for stage in ('demould','transport','lifting','temporary-placement'):
                rigidity=ei*(basis['handling']['early_modulus_factor'] if stage=='demould' else 1.)
                loading=u['mass_kg']*9.81*lift['dynamic_factor']/length
                solved=beam_confirmation.solve(length,[pick*length,(1-pick)*length],rigidity,uniform=loading,divisions=16)
                negative=loading*(pick*length)**2/2;positive=loading*length**2/8-loading*length*(pick*length)/2
                moment=max(abs(negative),abs(positive));stress=moment*factor
                checks[uid+'/'+stage+'/equilibrium']=solved['force_balance_relative_error']<1e-7
                limit=basis['handling']['nominal_early_tensile_limit_pa'] if stage=='demould' else basis['handling']['nominal_service_stress_limit_pa']
                if limit is not None:checks[uid+'/'+stage+'/nominal-stress-hypothesis']=stress<=limit
                else:unknown.append(uid+'/'+stage+'/concrete cracking, transfer strength, prestress and resistance')
                stages.append(dict(stage=stage,length_m=length,picks_m=[pick*length,(1-pick)*length],uniform_n_m=loading,ei_nm2=rigidity,
                    maximum_bending_moment_nm=moment,nominal_gross_stress_pa=stress,nominal_limit_pa=limit,
                    maximum_deflection_m=solved['maximum_nodal_deflection_m'],reactions=solved['reactions'],
                    force_balance_relative_error=solved['force_balance_relative_error'],approved=False))
        records.append(dict(unit_id=uid,suspended_mass_kg=suspended,crane_radius_m=lift['radius_m'],
            scenario_chart_capacity_kg=capacity,mat_pressure_pa=pressure,stages=stages,
            temporary_stability='requires designed restraint/falsework; simulated in dependency schedule only'))
    return dict(checks=checks,units=records,unknown=unknown,
        maximum_lift_mass_kg=max([r['suspended_mass_kg'] for r in records]+[u['mass_kg']+lift['rigging_kg'] for u in kit['temporary_units']]),
        lift_count=sum(u['offsite'] for u in kit['units'])+2*len(kit['temporary_units']),physical_release=False)


def tasks(kit):
    b=kit['basis'];f=b['factory'];s=b['site'];rows=[];ready={};placed={};connected={}
    def task(uid,hours,after,resources,*,owner=None,site=False,people=0,at_height=False,acquire=None,release=None,location=None):
        rows.append(dict(id=uid,hours=hours,after=list(dict.fromkeys(after)),resources=resources,owner=owner or uid,site=site,
            people=people,at_height=at_height,acquire=acquire or {},release=release or {},location=location or ('site' if site else 'factory')));return uid
    for support in (0,1):
        fnd=kit['candidate']['foundation'];volume=fnd['cap_length_m']*fnd['cap_width_m']*fnd['cap_depth_m']
        task(f'S{support}/excavate',volume/s['excavation_m3_per_hour'],[],{'site_crew':1,'excavator':1},site=True,people=s['people_per_operation'])
    for u in kit['units']:
        if u['category']=='pile' and not u['offsite']:
            task(u['id']+'/bore',s['pile_hours'],[u['id'].split('-')[0]+'/excavate'],{'pile_rig':1},site=True,people=s['people_per_operation'])
    for u in kit['units']:
        uid=u['id'];concrete=u.get('concrete_m3',0.)
        if u['offsite']:
            mould='deck_mould' if u['category']=='deck' else 'support_mould' if u['process']=='precast' else 'steel_bench'
            fabrication=f['setup_hours']+(concrete/f['concrete_m3_per_hour']+u['allocated_mass_kg']/f['steel_kg_per_hour'] if concrete else u['mass_kg']/f['steel_kg_per_hour'])
            # Hold the mould, but release the fabrication crew, during cure.
            made=task(uid+'/factory',fabrication,[],{'factory_crew':1} if u['process']=='precast' else {mould:1,'factory_crew':1},owner=uid,people=2,
                acquire={mould:1} if u['process']=='precast' else {})
            if u['process']=='precast':made=task(uid+'/in-mould-cure',f['in_mould_hours'],[made],{},owner=uid,release={mould:1})
            if u['process']=='precast':made=task(uid+'/yard-cure',f['yard_cure_hours'],[made],{'curing_yard':1},owner=uid)
            qa=task(uid+'/factory-test',f['inspection_hours']*len(qa_traveller.requirements(u)['factory']),[made],{'qa':1},owner=uid,people=1)
            ready[uid]=task(uid+'/transport',b['transport']['hours_per_trip'],[qa]+[parent+'/site-accept' for parent in u['support_ids']]+u.get('site_predecessors',[]),{},owner=uid,people=1,acquire={'storage':1,'truck':1},location='transport')
    falsework=None
    if kit['variables']['architecture']=='segmental':
        shipped=task('falsework/transport',3.,[],{'truck':1},site=False,people=1,location='transport')
        falsework=task('falsework/install',s['falsework_install_hours'],[shipped]+[uid+'/site-accept' for uid in kit['component_coverage']['foundation_caps']],{'falsework':1,'site_crew':1,'crane':1},site=True,people=s['people_per_operation'])
        for track in (1,2):
            members=[uid for uid in kit['component_coverage']['decks'] if uid.startswith(f'deck-T{track}-')]
            task(f'T{track}/post-tension',s['joint_hours']*(len(members)-1),[uid+'/place-and-temporary-lock' for uid in members],{'site_crew':1},site=True,people=s['people_per_operation'],at_height=True)
    for u in kit['units']:
        uid=u['id'];parents=[parent+'/site-accept' for parent in u['support_ids']]+u.get('site_predecessors',[])
        if u['offsite']:
            prerequisites=parents+[ready[uid]]
            if falsework and u['category']=='deck':prerequisites.append(falsework)
            placed[uid]=task(uid+'/place-and-temporary-lock',s['lift_and_temporary_lock_hours'],prerequisites,
                {'crane':1,'site_crew':1},owner=uid,site=True,people=s['people_per_operation'],
                at_height=u['bounds_m'][0][2]>2.,release={'storage':1,'truck':1})
        else:
            duration=max(.1,u.get('concrete_m3',0.)/s['wet_m3_per_hour'])
            deliveries=[]
            for trip in range(math.ceil(u.get('concrete_m3',0.)/s['mixer_capacity_m3'])):
                deliveries.append(task(uid+f'/mixer-{trip}',b['transport']['hours_per_trip'],parents,{'mixer':1},owner=uid,people=1,location='transport'))
            placed[uid]=task(uid+'/site-cast',duration,parents+deliveries,{'concrete_pump':1,'site_crew':1},owner=uid,site=True,people=s['people_per_operation'])
        joint_parents=[placed[uid]]
        if falsework and u['category']=='deck':joint_parents.append(uid.split('-')[1]+'/post-tension')
        connection_count=len(u.get('joint_endpoint_ids',u['support_ids'])) or 1
        joint=task(uid+'/engineered-joint',s['joint_hours']*connection_count,joint_parents,{'site_crew':1},owner=uid,site=True,people=s['people_per_operation'],at_height=u['bounds_m'][0][2]>2.)
        cure=minimum_cure(u,b)
        cured=task(uid+'/connection-strength-wait',cure,[joint],{},owner=uid) if cure else joint
        connected[uid]=task(uid+'/site-accept',s['survey_hours']*len(qa_traveller.requirements(u)['installed']),[cured],{'qa':1},owner=uid,site=True,people=1,at_height=u['bounds_m'][0][2]>2.)
    deck_ready=[connected[u] for u in kit['component_coverage']['decks']]
    if falsework:
        task('falsework/remove',s['falsework_remove_hours'],deck_ready,{'falsework':1,'site_crew':1,'crane':1},site=True,people=s['people_per_operation'])
    task('system/installed-tests',1.,list(connected.values())+(['falsework/remove'] if falsework else []),{'qa':1},site=True,people=2)
    return rows


def minimum_cure(unit,basis):
    return basis['connections']['cure_hours'] if unit['connection_bundle']['requires_wet_cure'] else 0.


def verify_schedule(kit,rows,scheduled):
    checks={};by_id={r['id']:r for r in rows};timed={r['id']:r for r in scheduled.get('tasks',[])}
    if not scheduled['passed']:return dict(checks={'resource_schedule':False},held=['schedule could not complete'])
    checks['all_required_stage_ids']={r['id'] for r in tasks(kit)}<=timed.keys()
    if not checks['all_required_stage_ids']:return dict(checks=checks,held=['required construction stage missing'])
    checks['dependency_precedence']=all(timed[p]['end_h']<=timed[r['id']]['start_h']+1e-8 for r in rows for p in r['after'])
    for u in kit['units']:
        uid=u['id'];placed=uid+'/place-and-temporary-lock' if u['offsite'] else uid+'/site-cast'
        checks[uid+'/crane-release-after-temporary-lock']=timed[placed]['end_h']-timed[placed]['start_h']>=kit['basis']['site']['lift_and_temporary_lock_hours']-1e-8 if u['offsite'] else True
        # The required minimum comes from the bound comparison basis, not a
        # possibly edited scheduling task. It is a hypothesis, not strength proof.
        checks[uid+'/connection-strength-wait']=timed[uid+'/site-accept']['start_h']-timed[uid+'/engineered-joint']['end_h']>=minimum_cure(u,kit['basis'])-1e-8
        checks[uid+'/required-parents']=all(timed[parent+'/site-accept']['end_h']<=timed[placed]['start_h']+1e-8 for parent in u['support_ids'])
        checks[uid+'/site-preconditions']=all(timed[parent]['end_h']<=timed[placed]['start_h']+1e-8 for parent in u.get('site_predecessors',[]))
        deliveries=[r for key,r in timed.items() if key.startswith(uid+'/mixer-')]
        if deliveries:
            checks[uid+'/fresh-concrete-arrival-window']=max(r['end_h'] for r in deliveries)-min(r['end_h'] for r in deliveries)<=kit['basis']['site']['maximum_mixer_arrival_spread_h']+1e-8
    if kit['variables']['architecture']=='segmental':
        checks['falsework-before-partial-erection']='falsework/install' in timed and all(timed['falsework/install']['end_h']<=timed[u+'/place-and-temporary-lock']['start_h']+1e-8 for u in kit['component_coverage']['decks'])
        checks['falsework-removal-after-joint-and-test']='falsework/remove' in timed and all(timed[u+'/site-accept']['end_h']<=timed['falsework/remove']['start_h']+1e-8 for u in kit['component_coverage']['decks'])
        for track in (1,2):
            key=f'T{track}/post-tension';members=[u for u in kit['component_coverage']['decks'] if u.startswith(f'deck-T{track}-')]
            checks[key+'/after-complete-segment-assembly']=key in timed and all(timed[u+'/place-and-temporary-lock']['end_h']<=timed[key]['start_h']+1e-8 for u in members)
    return dict(checks=checks,held=['measured early-age/connection strengths','designed temporary supports and anchors','site ground and crane/rigging acceptance'])
