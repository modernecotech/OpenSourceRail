"""Connected, manufactured representative bay on the existing civil-kit baseline.

Source concrete is retained except an equal-volume redistribution of each track
plinth into two rail seats. Added steel has its own gross mass. Bearing internals,
embedded anchorage, reinforcement/tendons and geotechnics remain explicit holds.
"""
from copy import deepcopy
import itertools
import math

from engineering.twin_workflow import core
from engineering.continuous_design import civil_kit, beam_confirmation
from engineering.design_consistency import contracts, demonstrators
from . import baseline

DOMAINS=dict(architecture=['large-span','segmental','light-ribbed'],bracket_wall_m=[.004,.006,.008])
DEFAULTS=dict(architecture='segmental',bracket_wall_m=.006)
RAIL_SOURCE=dict(url='https://www.britishsteel.co.uk/wp-content/uploads/2026/02/british-steel-rail-profiles-and-grades-datasheet.pdf',
    locator='60E1 / UIC60 row; UK-manufactured rail profile range',retrieved='2026-10-20',document_sha256='2a66c232e244c245331802b88cf8d1ba972eca517645b69e0c97c6386c82fcf7',document_bytes_retained=False,
    manufacturing_reference='https://www.britishsteel.co.uk/wp-content/uploads/2026/03/British-Steel-product-brochure-03.03.26-3.pdf',
    published=dict(height_m=.172,head_width_m=.072,web_m=.0165,foot_width_m=.150,mass_kg_m=60.21),
    scope='Published overall dimensions only; three-rectangle native coordination substitute is not the rolled profile or manufacturer CAD',
    offered_configuration_accepted=False)
HOLDS=['Adopted Baghdad ground investigation, groundwater, scour and pile resistance/settlement',
    'Issued reinforcement, tendons, duct routing, prestress losses and concrete stage strengths',
    'Rated bearing internals, movement, restraints and fatigue/seismic resistance',
    'Deck-web embedded sockets/anchor continuation, edge distances, local concrete breakout and bracket weld qualification',
    'Exact rolled rail profile, rail fastening/pad/insulation, gauge datum and thermal/continuity arrangement',
    'Full railway vertical/lateral/braking/fatigue/dynamic and train-track-ground acceptance',
    'Service contents, drainage falls/outlets, electrical segregation/fire and maintainable connections',
    'Qualified lifting inserts, rigging, temporary towers and construction-stage stability',
    'Actual transport access/permits, crane chart and ground support at each erection position',
    'Authenticated manufactured serial records and independent engineering/physical acceptance']


def candidates(policy=None):
    return [dict(zip(DOMAINS,values)) for values in itertools.product(*DOMAINS.values())]


def _policy(policy):
    value=policy['policy'] if 'policy' in policy else policy
    baseline.validate(value)
    return value


def source_kit(variables):
    choices=civil_kit.defaults(variables['architecture'])
    # Same foundation/pier subdivisions for each deck architecture. Subdivision
    # is a construction hypothesis, not qualified joints or reduced material.
    choices.update(pier_segments=4,foundation_cap_segments=2,cap_segments=2)
    return civil_kit.build(choices)


def build(policy,variables=None):
    policy=_policy(policy);variables=dict(DEFAULTS if variables is None else variables)
    if variables not in candidates():raise ValueError('controlled connected-bay variables required')
    kit=source_kit(variables)
    if not all(civil_kit.validate_kit(kit).values()):raise ValueError('valid source civil kit required')
    mats=deepcopy(kit['physical_contract']['materials']);parts=[];joints=[];original_parts={p['id']:p for p in kit['physical_contract']['parts']}
    units={u['id']:deepcopy(u) for u in kit['units']};groups={}
    # The adopted template gauge is read rather than inferred from a narrow
    # centreline plinth. Preserve the original concrete section volume exactly.
    import tomllib
    gauge=tomllib.loads((core.ROOT/'lib/templates/track-geometry.toml').read_text())['presets']['standard-metro']['gauge_mm']/1000.
    for old in kit['physical_contract']['parts']:
        uid=old['manufacturing_unit_id'];category=units[uid]['category']
        if category=='track-support':
            source_unit=units.pop(uid)
            for side in (-1,1):
                primitives=[]
                for p in old['manufacturing']['primitives']:
                    if p['kind']!='box':raise ValueError('source plinth must have exact rectangular material')
                    L,W,H=p['dimensions_m'];x,y,z=p['centre_m']
                    primitives.append(contracts.box(p['id']+'/rail-seat-'+str(side),L,W/2,H,[x,y+side*(gauge+RAIL_SOURCE['published']['head_width_m'])/2,z]))
                pid=old['id']+'/rail-seat-'+str(side);new_uid=uid+'/rail-seat-'+str(side)
                item=contracts.part(pid,old['material'],dict(role='One independently manufactured rail-seat strip; half exact source material',primitives=primitives),mats,
                    limits=dict(tolerance_m=.002,tolerance_status='proposed; unqualified'),inspections=['concrete batch/strength','rail-seat separation and level','embedded interfaces'])
                item.update(manufacturing_unit_id=new_uid,source_part_id=old['id'],geometric_role='manufactured-solid',process_route='Precast one rail-seat strip; reinforcement/anchors unissued',procurement=None)
                parts.append(item);groups.setdefault(category,[]).append(pid)
                unit=deepcopy(source_unit);unit.update(id=new_uid,source_unit_id=uid,source_unit_revision=source_unit['revision'],
                    allocated_mass_kg=source_unit['allocated_mass_kg']/2,physical_part_ids=[pid])
                units[new_uid]=unit
        else:
            item=deepcopy(old);item.setdefault('process_route',units[uid]['process']+'; exact reinforcement/connection/strength gates open')
            item.setdefault('geometric_role','source-material-region');item.setdefault('procurement',None);parts.append(item)
            groups.setdefault(category,[]).append(item['id'])
    deck_top=max(max(p['centre_m'][2]+p['dimensions_m'][2]/2 for p in original_parts[pid]['manufacturing']['primitives']) for u in units.values() if u['category']=='deck' for pid in u['physical_part_ids'])
    t=variables['bracket_wall_m'];added_ids=[];support_frames=[];rail_ids=[]
    def add(pid,primitives,*,unit,route,role='manufactured-solid',placement=None):
        item=contracts.part(pid,'kit-steel',dict(role=pid,primitives=primitives),mats,placement=placement,
            limits=dict(tolerance_m=.002,tolerance_status='proposed; production capability unmeasured'),
            inspections=['heat/part trace','dimensions/datums','weld or connection inspection','coating/isolated interfaces'])
        item.update(manufacturing_unit_id=unit,process_route=route,geometric_role=role,procurement=None)
        parts.append(item);added_ids.append(pid);return item
    def member(pid,L,W,H,wall,centre,unit,rotation=None):
        item=contracts.member(pid,L,W,H,wall,'kit-steel',mats,placement=dict(translation_m=list(centre),rotation=rotation or [[1,0,0],[0,1,0],[0,0,1]]))
        result=add(pid,item['manufacturing']['primitives'],unit=unit,placement=item['placement'],route='Cut RHS; prepare and qualify welded connection, drain/vent holes and corrosion system')
        result['analysis']['section']=item['analysis']['section'];return result
    def joint(pid,ends,mechanism):
        joints.append(dict(id=pid,endpoints=ends,mechanism=mechanism,fastener_ids=[],tolerance_m=.002,
            load_case_ids=['self-weight','walkway-5kPa-scenario','service-carrier-scenario','erection'],
            inspection=['fit and engagement','weld or torque/locking','independent disposition'],capacity_evidence=None,qualified=False))
    # One manufactured frame at each module end and midpoint. End frames are
    # inset125mm to keep all stock within the20m cell and avoid joint collisions.
    for side in (-1,1):
        deck_prefix='deck-T'+str(1 if side<0 else 2)+'-'
        for module in range(4):
            for index,x in enumerate((5*module+.125,5*module+2.5,5*module+4.875)):
                uid=f'outer-frame-{side}-{module}-{index}';ids=[]
                back=contracts.box('plate',.18,.6,.012,[0,0,0]);back.update(kind='perforated-plate',holes_xy_m=[[sx*.06,sz*.22] for sx in (-1,1) for sz in (-1,1)],hole_radius_m=.011)
                rot=[[1,0,0],[0,0,side],[0,-side,0]]
                ids.append(add(uid+'/backplate',[back],unit=uid,placement=dict(translation_m=[x,side*3.206,deck_top-.35],rotation=rot),route='Cut/drill12mm backplate; four22mm holes, proposed20mm interface').get('id'))
                rotation=[[0,-side,0],[side,0,0],[0,0,1]]
                ids.append(member(uid+'/arm',1.513,.08,.16,t,[x,side*3.9685,deck_top-.42],uid,rotation)['id'])
                for edge,y in enumerate((3.3,3.9)):
                    # RHS post from the arm top to the longitudinal bearer bottom.
                    rotation_post=[[0,0,-1],[0,1,0],[1,0,0]]
                    ids.append(member(uid+'/post-'+str(edge),.24,.06,.06,.004,[x,side*y,deck_top-.22],uid,rotation_post)['id'])
                # Three carrier seats physically bridge the original below-deck
                # service plates to the arm top. Contents are not invented here.
                seats=[contracts.box('seat-'+str(i),.08,.15,.039,[x,side*y,deck_top-.3205]) for i,y in enumerate((4.05,4.35,4.65))]
                ids.append(add(uid+'/service-seats',seats,unit=uid,route='Cut/fabricate carrier seats and inspect fit; isolate services as issued')['id'])
                # Exposed bolt geometry fits the actual plate holes. Shanks stop
                # at the concrete face; unknown embedded anchors are a hold,
                # rather than overlapping uncut concrete and pretending success.
                bolts=[]
                for j,(dx,dz) in enumerate(itertools.product((-.06,.06),(-.22,.22))):
                    bolts.extend([dict(id='shank-'+str(j),kind='cylinder',radius_m=.010,length_m=.012,axis='y',centre_m=[x+dx,side*3.206,deck_top-.35+dz]),
                        dict(id='head-'+str(j),kind='cylinder',radius_m=.018,length_m=.014,axis='y',centre_m=[x+dx,side*3.219,deck_top-.35+dz])])
                ids.append(add(uid+'/interface-bolt-stubs',bolts,unit=uid,route='Purchased nominalM20 interface stubs; exact anchor continuity/grade/thread/locking not represented',role='hardware-coordination-envelope')['id'])
                owning=[u['id'] for u in units.values() if u['id'].startswith(deck_prefix) and u['bounds_m'][0][0]<=x<=u['bounds_m'][1][0]]
                joint(uid+'/deck-interface',[ids[0],ids[-1],*[pid for own in owning for pid in units[own]['physical_part_ids']]],'Perforated plate at outer deck web; embedded anchor continuation and local resistance unresolved')
                joint(uid+'/fabricated-frame',ids[:-1],'Qualified RHS-to-plate/post/seat welds and accessible inspection required')
                support_frames.append(dict(id=uid,part_ids=ids,x_m=x,side=side,deck_unit_ids=owning,arm_length_m=1.513,maximum_tributary_length_m=2.5))
        # Bearers make the8mm walkway plate a650mm transverse strip, rather than
        # treating an unsupported5m plate as a complete footway.
        for module in range(4):
            uid=f'walkway-{side}-{module}'
            for edge,y in enumerate((3.3,3.9)):
                item=member(uid+'/longitudinal-bearer-'+str(edge),5.,.06,.10,.004,[2.5+5*module,side*y,deck_top-.05],uid)
                joint(item['id']+'/support',[item['id'],uid+'/floor',*[f['id']+'/post-'+str(edge) for f in support_frames if f['side']==side and int(f['id'].split('-')[-2])==module]],'Bearing/contact plus issued positive retention; local plate and weld resistance unresolved')
    # Four purchased rail coordination sections on the now correctly separated
    # rail seats. Overall envelope follows British Steel60E1; roll radii, taper,
    # contact and clip geometry are deliberately not substituted by this profile.
    plinth_top=deck_top+.18
    for track,cy in ((1,-1.75),(2,1.75)):
        for side in (-1,1):
            y=cy+side*(gauge+RAIL_SOURCE['published']['head_width_m'])/2;pid=f'rail-T{track}-{side}';base=plinth_top
            primitives=[contracts.box('foot',20.,.15,.02,[10.,y,base+.01]),
                contracts.box('web',20.,.0165,.107,[10.,y,base+.0735]),
                contracts.box('head',20.,.072,.045,[10.,y,base+.1495])]
            item=add(pid,primitives,unit=pid,route='Procure exact British-manufactured rail profile; this rectangular coordination shape is not a rolling/manufacturing drawing',role='supplier-coordination-envelope')
            item['procurement']=dict(manufacturer='British Steel',reference_profile='60E1',offered_part=None,origin='Published UK-manufactured range; offered heat/product certificate required',supplier_source=RAIL_SOURCE)
            rail_ids.append(pid)
            joint(pid+'/track-interface',[pid,*groups['track-support']], 'Foot contact at paired plinth datum; pads, fasteners and rail continuity/temperature details unresolved')
    # Original source support edges are retained in the physical connection graph.
    for uid,u in units.items():
        if not u['physical_part_ids']:continue
        ends=u['physical_part_ids']+[pid for support in u['support_ids'] for pid in units[support]['physical_part_ids']]
        if len(ends)>1:joint(uid+'/retained-support',ends,u['connection_bundle']['mechanism']+'; original internal connection and acceptance gates retained')
    source_revision=core.digest(kit);policy_revision=core.digest(policy)
    revision=core.digest(dict(kind='civil-connected-bay',variables=variables,source_kit_revision=source_revision,policy_revision=policy_revision,parts=parts,joints=joints,rail_source=RAIL_SOURCE))
    for p in parts:p.update(revision=revision,joints=[j['id'] for j in joints if p['id'] in j['endpoints']])
    contract=demonstrators.contract('Connected20m two-track representative civil bay; provisional physical units',parts,mats)
    contract.update(revision=revision,assembly_joints=joints,mandatory_evidence=HOLDS,
        unresolved_part_allocations=kit['physical_contract']['unresolved_part_allocations']+['Unknown rail fastening/pad/anchor continuation masses are additional; no deletion credit'])
    contracts.validate(contract)
    categories=[('piles','pile'),('foundation-caps','foundation-cap'),('piers','pier'),('pier-caps','pier-cap'),('bearings','bearing'),('decks','deck'),('track-plinths','track-support')]
    sequence=[];previous=[]
    for identity,category in categories:
        sequence.append(dict(id=identity,title='Install '+category+' units; strength, survey and engineered locks held',part_ids=groups[category],requires=previous))
        previous=[identity]
    sequence.append(dict(id='frames',title='Fit exposed deck-web frames; qualify embedded anchors before load transfer',part_ids=[pid for f in support_frames for pid in f['part_ids']],requires=['decks']))
    sequence.append(dict(id='walkways',title='Fit bearers, walkway plates and parapets; inspect retention',part_ids=groups['walkway-parapet']+[p['id'] for p in parts if '/longitudinal-bearer-' in p['id']],requires=['frames']))
    sequence.append(dict(id='services',title='Fit segregated service carriers; contents and commissioning held',part_ids=groups['service'],requires=['frames']))
    sequence.append(dict(id='rails',title='Coordinate purchased rails on paired plinths; fastening and gauge acceptance held',part_ids=rail_ids,requires=['track-plinths']))
    defined=sum(p['properties']['mass_kg'] for p in parts);old_defined=sum(p['properties']['mass_kg'] for p in original_parts.values())
    ledger=dict(source_defined_mass_kg=old_defined,source_allowances_kg=kit['mass_ledger']['allocated_unmodeled_mass_kg'],
        gross_added_represented_mass_kg=defined-old_defined,defined_mass_kg=defined,
        retained_allowance_study_mass_kg=defined+kit['mass_ledger']['allocated_unmodeled_mass_kg'],complete_installed_mass_kg=None,removal_credit_kg=0.)
    from engineering.design_engine.manufacturing_rules import part_bounds
    manufactured_units=[]
    for uid in sorted(set(units)|{p['manufacturing_unit_id'] for p in parts}):
        owned=[p for p in parts if p['manufacturing_unit_id']==uid]
        unit=deepcopy(units[uid]) if uid in units else dict(id=uid,category='purchased-rail' if uid in rail_ids else 'outer-support-frame',
            allocated_mass_kg=0.,offsite=True,process='purchased' if uid in rail_ids else 'steel-fabrication',support_ids=[])
        unit['source_unit_revision']=unit.get('source_unit_revision',unit.get('revision'))
        unit['physical_definitions_sha256']={p['id']:core.digest(p) for p in owned}
        if owned:
            bounds=[part_bounds(p) for p in owned]
            unit['bounds_m']=[[min(b[0][i] for b in bounds) for i in range(3)],[max(b[1][i] for b in bounds) for i in range(3)]]
        unit['physical_part_ids']=[p['id'] for p in owned]
        unit['defined_mass_kg']=sum(p['properties']['mass_kg'] for p in owned)
        unit['mass_kg']=unit['defined_mass_kg']+unit['allocated_mass_kg']
        unit['transport_dimensions_m']=sorted([hi-lo for lo,hi in zip(*unit['bounds_m'])],reverse=True)
        unit['revision']=core.digest({k:v for k,v in unit.items() if k!='revision'})
        manufactured_units.append(unit)
    value=dict(schema='osr-civil-connected-bay/1',kind='civil-connected-bay',variables=variables,revision=revision,contract=contract,
        source_kit_revision=source_revision,policy_revision=policy_revision,metadata=dict(architecture='baghdad-six-car',
            assembly_sequence=sequence,source_units=deepcopy(kit['units']),manufactured_units=manufactured_units,support_frames=support_frames,
            original_part_revisions={p['id']:core.digest(p) for p in original_parts.values()},deck_top_m=deck_top,gauge_m=gauge,
            plinth_volume_preserved=True,rail_seat_centres_m=gauge+RAIL_SOURCE['published']['head_width_m'],full_pilot_scope=False,complete_installed_system=False,mass_ledger=ledger,
            rail_source=RAIL_SOURCE,rail_profile_is_coordination_only=True),
        assembly_steps=[s['title'] for s in sequence],qa_plan=[dict(unit_id=p['id'],unit_revision=revision,serial=None,required=p['inspection_characteristics'],records=[],accepted=False) for p in parts],
        source_scope='One connected20m two-track cell: exact inherited foundation/pier/cap/deck solids and allowances; paired equal-volume plinths; added contacting outer support frames/bearers/service seats; purchased bearing and rail coordination only. Complete reinforcement, anchorage, rail fastening, services and ground acceptance remain open.',
        open_requirements=HOLDS,**core.FLAGS)
    value['definition_sha256']=core.digest(value);return value


def gravity_context(policy,candidate,kit):
    """Exact gross additions through the inherited signed gravity distributor.

    This preserves the original allowances (including the rail budget), with no
    subtraction for the newly represented rails. Resultants are equilibrium,
    not resistance, contact or railway-dynamic verification.
    """
    from . import reactions
    facts=baseline.facts(policy);a=policy['pilots']['bearing-seat']['assumptions']
    train=reactions.revisioned(dict(architecture='baghdad-six-car',mass_cases_kg=facts['train.mass_cases'],
        cars=6,car_length_m=facts['train.car_length'],tracks=2,span_m=20.,gravity_m_s2=a['gravity_m_s2'],
        permanent_factor=a['vertical_factor'],variable_factor=a['vertical_factor']))
    source={p['id']:p for p in kit['physical_contract']['parts']}
    bearing_units=[u for u in kit['units'] if u['category']=='bearing']
    if len({u['mass_kg'] for u in bearing_units})!=1:raise ValueError('equal exact reference bearing masses required')
    seat=reactions.revisioned(dict(candidate_revision=core.digest([source[pid] for u in bearing_units for pid in u['physical_part_ids']]),mass_kg=bearing_units[0]['mass_kg']))
    retained=reactions.envelope(kit,train,seat,expected_kit_revision=core.digest(kit),expected_train_revision=train['revision'])
    bearing_points={u['id']:[(lo+hi)/2 for lo,hi in zip(*u['bounds_m'])] for u in bearing_units}
    supports={track:[dict(id=uid,position_m=point) for uid,point in bearing_points.items() if (point[1]<0)==(track==1)] for track in (1,2)}
    additions=[dict(id=p['id'],mass_kg=p['properties']['mass_kg'],point_m=p['properties']['cg_m']) for p in candidate['contract']['parts'] if p['id'] not in source and p.get('source_part_id') not in source]
    def wrench(force,point,origin=(0.,0.,0.)):
        x,y,z=[v-o for v,o in zip(point,origin)];return [0.,0.,force,y*force,-x*force,0.]
    cases=[]
    for original in retained['combinations']:
        case=deepcopy(original);increment={uid:0. for uid in bearing_points};applied=[];extra=[]
        for row in additions:
            force=row['mass_kg']*train['gravity_m_s2']*case['G'];point=row['point_m']
            distribution=reactions.distribute_vertical(force,point,supports[1 if point[1]<0 else 2])
            for uid,value in distribution.items():increment[uid]+=value
            applied.append(wrench(-force,point));extra.append(dict(load_id='G/new/'+row['id'],force_down_n=force,point_m=point,bearing_contributions_n=distribution))
        if case['Q']:
            # Same explicit walkway/service scenario as local frame evaluation,
            # evaluated separately from the full provisional two-track train.
            for side in (-1,1):
                for label,y,total in [('walkway',3.6,5000.*.65*20.),('service-content',4.35,3*1000.*20/2.5)]:
                    point=[10.,side*y,candidate['metadata']['deck_top_m']];force=total*case['Q']
                    distribution=reactions.distribute_vertical(force,point,supports[1 if side<0 else 2])
                    for uid,value in distribution.items():increment[uid]+=value
                    applied.append(wrench(-force,point));extra.append(dict(load_id='Q/'+label+'/'+str(side),force_down_n=force,point_m=point,bearing_contributions_n=distribution))
        for row in case['bearing_reactions']:row['force_n'][2]+=increment[row['bearing_id']]
        for section in case['section_resultants']:
            demand=section['downstream_demand_wrench']
            for uid,force in increment.items():
                if uid.startswith(section['support_id']+'-'):
                    delta=wrench(-force,bearing_points[uid],section['origin_m']);demand[:]=[v+d for v,d in zip(demand,delta)]
        case['loads']+=extra
        delta_applied=[sum(w[i] for w in applied) for i in range(6)]
        delta_reactions=[sum(wrench(force,bearing_points[uid])[i] for uid,force in increment.items()) for i in range(6)]
        case['global_applied_wrench']=[x+y for x,y in zip(case['global_applied_wrench'],delta_applied)]
        case['global_reaction_wrench']=[x+y for x,y in zip(case['global_reaction_wrench'],delta_reactions)]
        case['equilibrium_residual']=[x+y for x,y in zip(case['global_applied_wrench'],case['global_reaction_wrench'])]
        scale=max(1.,max(abs(x) for x in case['global_applied_wrench']))
        case['equilibrium_pass']=max(abs(x) for x in case['equilibrium_residual'])<=1e-10*scale
        case['negative_reaction_bearing_ids']=[row['bearing_id'] for row in case['bearing_reactions'] if row['force_n'][2]<0.]
        cases.append(case)
    result=dict(schema='osr-connected-civil-gravity/1',candidate_revision=candidate['revision'],source_envelope_revision=retained['revision'],
        train=train,added_part_mass_ledger=additions,combinations=cases,complete_installed_equipment_map=False,
        scope='Original civil gravity and uniform two-track six-car planning loads plus every new steel part and explicit walkway/service scenario; no removed rail allowance credit, no dynamics or contact qualification',**core.FLAGS)
    result['revision']=core.digest(result);return result


def _capacity(chart,radius):
    # Planning chart: conservative next-wider radius, never extrapolate beyond it.
    values=sorted(chart)
    return next((capacity for at,capacity in values if at>=radius),None)


def evaluate(policy,candidate,*,walkway_load_factor=1.,crane_radius_m=None):
    policy=_policy(policy)
    if candidate!=build(policy,candidate['variables']):raise ValueError('connected bay differs from exact controlled reconstruction')
    if type(walkway_load_factor) not in (int,float) or not math.isfinite(walkway_load_factor) or walkway_load_factor<=0:raise ValueError('positive finite adverse load factor required')
    kit=source_kit(candidate['variables']);parts={p['id']:p for p in candidate['contract']['parts']};m=candidate['metadata'];ledger=m['mass_ledger']
    stageparts=[pid for stage in m['assembly_sequence'] for pid in stage['part_ids']]
    checks=dict(exact_source_kit=candidate['source_kit_revision']==core.digest(kit),
        physical_part_coverage=len(stageparts)==len(set(stageparts)) and set(stageparts)==set(parts),
        gross_mass_conservation=abs(ledger['retained_allowance_study_mass_kg']-kit['mass_ledger']['installed_study_mass_kg']-ledger['gross_added_represented_mass_kg'])<1e-6)
    original={p['id']:p for p in kit['physical_contract']['parts']}
    checks['rail_inner_head_gauge']=all(math.isclose(parts['rail-T'+str(track)+'-1']['manufacturing']['primitives'][2]['centre_m'][1]-.036-(parts['rail-T'+str(track)+'--1']['manufacturing']['primitives'][2]['centre_m'][1]+.036),m['gauge_m'],abs_tol=1e-12) for track in (1,2))
    checks['paired_plinth_equal_material']=all(abs(sum(row['properties']['mass_kg'] for row in parts.values() if row.get('source_part_id')==pid)-p['properties']['mass_kg'])<1e-8 for pid,p in original.items() if pid.startswith('track-'))
    checks['source_concrete_and_hardware_preserved']=all(parts[pid]['manufacturing']==p['manufacturing'] and parts[pid]['properties']==p['properties'] for pid,p in original.items() if not pid.startswith('track-'))
    section=next(p['analysis']['section'] for p in parts.values() if p['id'].endswith('/arm'))
    I=section['inertia_x_m4'] if 'inertia_x_m4' in section else section.get('iy_m4')
    if I is None:
        b,h,t=.08,.16,candidate['variables']['bracket_wall_m'];I=(b*h**3-(b-2*t)*(h-2*t)**3)/12
    E=210e9;L=1.513
    gravity=9.81
    loads=[(.388,5000.*.65*2.5*walkway_load_factor)]
    for part in parts.values():
        if part['manufacturing_unit_id']=='walkway-1-0':
            loads.append((part['properties']['cg_m'][1]-3.212,.5*part['properties']['mass_kg']*gravity))
    for name in ('post-0','post-1','service-seats'):
        part=parts['outer-frame-1-0-0/'+name]
        loads.append((part['properties']['cg_m'][1]-3.212,part['properties']['mass_kg']*gravity))
    carrier_dead_per_service=original['power-1-0/carrier']['properties']['mass_kg']*.5
    loads.extend((x,1000.*walkway_load_factor+carrier_dead_per_service*gravity) for x in (.838,1.138,1.438))
    # Coalesce algebraically identical nominal load stations before FE mesh
    # assembly; sub-picometre float differences otherwise create singular sliver
    # elements. The same explicit station list feeds both independent solutions.
    stations={}
    for at,force in loads:stations[round(at,12)]=stations.get(round(at,12),0.)+force
    loads=sorted(stations.items())
    # Retained carrier + pipe/cable content scenario:3x1kN per frame. Unknown
    # actual service inventory remains a hold even if this scenario passes.
    own_per_m=7850*(.08*.16-(.08-2*candidate['variables']['bracket_wall_m'])*(.16-2*candidate['variables']['bracket_wall_m']))*9.81
    M=sum(x*force for x,force in loads)+own_per_m*L*L/2
    deflection=sum(force*x*x*(3*L-x)/(6*E*I) for x,force in loads)+own_per_m*L**4/(8*E*I)
    numerical=beam_confirmation.solve(L,[0.],E*I,points=loads,uniform=own_per_m,divisions=12,clamp=True)
    doubled=beam_confirmation.solve(L,[0.],E*I,points=[(x,2*f) for x,f in loads],uniform=2*own_per_m,divisions=12,clamp=True)
    checks.update(bracket_gross_elastic_355MPa_screen=M*.08/I<=355e6,
        bracket_tip_L250_scenario=deflection<=L/250,
        bracket_independent_beam=math.isclose(numerical['maximum_nodal_deflection_m'],deflection,rel_tol=1e-7),
        bracket_force_equilibrium=numerical['force_balance_relative_error']<1e-7,
        bracket_adverse_load_scaling=math.isclose(doubled['maximum_nodal_deflection_m'],2*numerical['maximum_nodal_deflection_m'],rel_tol=1e-7))
    # The transverse8mm steel floor spans600mm between the two added bearers.
    floor_span=.6;floor_I=.008**3/12;floor_q=5000.*walkway_load_factor
    floor_d=5*floor_q*floor_span**4/(384*E*floor_I);floor_sigma=floor_q*floor_span**2/8*.004/floor_I
    # Each bearer carries half the walkway width and half source selfweight.
    b,h,t=.06,.10,.004;bearer_I=(b*h**3-(b-2*t)*(h-2*t)**3)/12;bearer_L=2.375
    bearer_q=5000.*.65/2*walkway_load_factor+(.65*.008*7850*9.81/2)+7850*(b*h-(b-2*t)*(h-2*t))*9.81
    bearer_d=5*bearer_q*bearer_L**4/(384*E*bearer_I)
    checks.update(walkway_floor_L250_scenario=floor_d<=floor_span/250,walkway_floor_355MPa_screen=floor_sigma<=355e6,
        longitudinal_bearer_L250_scenario=bearer_d<=bearer_L/250,longitudinal_bearer_355MPa_screen=bearer_q*bearer_L**2/8*.05/bearer_I<=355e6)
    radius=kit['basis']['lifting']['radius_m'] if crane_radius_m is None else crane_radius_m
    if type(radius) not in (int,float) or not math.isfinite(radius) or radius<=0:raise ValueError('finite positive crane radius required')
    lifting=kit['basis']['lifting'];capacity=_capacity(lifting['chart'],radius);lifts=[]
    for unit in m['manufactured_units']:
        if not unit['offsite']:continue
        suspended=unit['mass_kg']*lifting['dynamic_factor']+lifting['rigging_kg']
        passed=capacity is not None and suspended<=capacity
        checks[unit['id']+'/crane-at-radius-scenario']=passed
        transport=kit['basis']['transport']
        checks[unit['id']+'/transport-envelope-scenario']=all(actual<=limit for actual,limit in zip(unit['transport_dimensions_m'],transport['maximum_dimensions_m']))
        checks[unit['id']+'/transport-payload-scenario']=unit['mass_kg']<=transport['payload_kg']
        lifts.append(dict(unit_id=unit['id'],unit_revision=unit['revision'],mass_kg=unit['mass_kg'],suspended_scenario_kg=suspended,
            crane_radius_m=radius,chart_capacity_kg=capacity,scenario_pass=passed,actual_rating_accepted=False))
    gravity=gravity_context(policy,candidate,kit)
    checks['full_added_mass_gravity_equilibrium']=all(c['equilibrium_pass'] for c in gravity['combinations'])
    checks['no_signed_gravity_uplift_in_scenario']=all(not c['negative_reaction_bearing_ids'] for c in gravity['combinations'])
    for hold in HOLDS:checks['hold/'+hold]=None
    result=dict(schema='osr-civil-connected-bay-assessment/1',candidate_revision=candidate['revision'],checks=checks,
        failed_checks=[k for k,v in checks.items() if v is False],held_checks=[k for k,v in checks.items() if v is None],
        metrics=dict(mass_ledger=ledger,lifts=lifts,gravity_context=gravity,maximum_lift_mass_kg=max(row['mass_kg'] for row in lifts),
            bracket=dict(inertia_m4=I,root_moment_nm=M,gross_stress_pa=M*.08/I,tip_deflection_m=deflection,independent=numerical,
                loading='5kPa walkway over2.5m tributary length plus three1kN service-content hypotheses and represented walkway/bearer/post/seat/carrier and arm selfweights; 355MPa/L250 screens are provisional research bounds',
                adverse_2x=doubled),walkway=dict(floor_transverse_deflection_m=floor_d,bearer_deflection_m=bearer_d),
            load_factor=walkway_load_factor,crane_radius_m=radius),scope='Independent elastic support/frame and conservation/lift scenario checks; these do not qualify deck reinforcement, railway load paths, connections, ground or construction-stage stability.',**core.FLAGS)
    result['revision']=core.digest(result);return result
