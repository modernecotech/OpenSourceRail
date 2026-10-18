"""Manufactured-unit planning for equal-function viaduct kits.

Canonical civil material regions are grouped/split into shipping/erection units.
Defined solids, retained source allowances and new kit additions have separate
mass ledgers. No reinforcement, connection, ground or railway release is implied.
"""
from copy import deepcopy
import math

from engineering.twin_workflow import core
from . import operation_graph,qa_traveller,delivery_simulation

BASIS=core.ROOT/'engineering/continuous_design/data/civil-kit-basis.json'
CONTEXT='kit-20m-two-track-two-supports-fixed-reference'
STATION_CONTEXT=CONTEXT+'-station-package'
ARCHITECTURES={'large-span':('pi',1),'segmental':('segmental-box',4),'light-ribbed':('ribbed-deck',1)}
DOMAINS=dict(architecture=list(ARCHITECTURES),pier_segments=[1,4],cap_segments=[1,2],
    foundation_family=['reference-four','bored-six','hollow-driven-six','square-driven-six'],foundation_cap_segments=[1,2],
    pier_family=['solid','solid-tapered','hollow-tapered','hollow-prismatic','segmental-hollow','double-skin-hybrid'],
    foundation_route=['bored-prefab-cage','precast-driven'],service_length_m=[5.,10.],station_package=[False,True])


def defaults(architecture='large-span'):
    return dict(architecture=architecture,pier_family='solid',pier_segments=1,cap_segments=2,foundation_family='reference-four',foundation_cap_segments=1,foundation_route='bored-prefab-cage',service_length_m=5.,station_package=False)


def validate(parameters):
    if set(parameters)!={'context_id','variables'} or parameters['context_id'] not in (CONTEXT,STATION_CONTEXT):raise ValueError('fixed civil kit context required')
    v=parameters['variables']
    if set(v)!=set(DOMAINS) or any(not any(type(value) is type(choice) and value==choice for choice in DOMAINS[key]) for key,value in v.items()):
        raise ValueError('unregistered civil kit design choice')
    if parameters['context_id']!=(STATION_CONTEXT if v['station_package'] else CONTEXT):
        raise ValueError('station and viaduct-only functions require separate comparison contexts')
    if ('driven' in v['foundation_family'])!=(v['foundation_route']=='precast-driven'):
        raise ValueError('foundation geometry and installation route must be a compatible bundle')


def build(variables,basis=None):
    from .expansion import compile_civil_shape
    from engineering.civil_exploration.workflow import candidate
    from engineering.civil_exploration.model import takeoff
    from engineering.design_engine.design_alternatives import _civil_contract
    from engineering.design_consistency import demonstrators as d
    from engineering.design_consistency.contracts import part,box
    from engineering.design_engine.manufacturing_rules import part_bounds
    basis=deepcopy(basis or core.read(BASIS));family,deck_segments=ARCHITECTURES[variables['architecture']]
    design=compile_civil_shape(dict(deck_family=family,pier_family=variables['pier_family'],material='normal',foundation_family=variables['foundation_family'],geometry_fraction=.5,mould_route='split-reusable'))
    study=deepcopy(design['study']);study['route_length_m']=20
    compiled=candidate(design['civil_candidate']['definition'],study);original,_=_civil_contract(compiled,study);q=takeoff(compiled,study)
    mats=deepcopy(original['materials']);mats['kit-steel']=d.materials()['steel'];mats['kit-concrete']=deepcopy(compiled['material'])
    physical=[];units={};base_mass=sum(p['properties']['mass_kg'] for p in original['parts'])
    def add(identifier,category,parts,*,offsite=True,process='precast',extra_mass=0.,support_ids=(),metadata=None):
        if identifier in units:raise ValueError('duplicate manufactured unit')
        bounds=[part_bounds(p) for p in parts]
        if bounds:
            envelope=[[min(b[0][i] for b in bounds) for i in range(3)],[max(b[1][i] for b in bounds) for i in range(3)]]
        else:envelope=deepcopy(metadata['bounds_m'])
        mass=sum(p['properties']['mass_kg'] for p in parts)
        if mass+extra_mass<=0:raise ValueError('positive unit mass required')
        for p in parts:p['manufacturing_unit_id']=identifier
        physical.extend(parts)
        unit=dict(id=identifier,category=category,physical_part_ids=[p['id'] for p in parts],bounds_m=envelope,
            concrete_m3=sum(p['properties']['mass_kg']/mats[p['material']]['density_kg_m3'] for p in parts if 'concrete' in p['material']),
            defined_mass_kg=mass,allocated_mass_kg=extra_mass,mass_kg=mass+extra_mass,offsite=offsite,process=process,
            support_ids=list(support_ids),lifting_points_fraction=[.2,.8],
            locating_features=dict(guide_clearance_m=basis['connections']['guide_clearance_m'],tolerance_stack_m=basis['connections']['tolerance_stack_m'],
                lock_engagement_m=basis['connections']['lock_engagement_m'],positive_lock='captive bolts/pins or post-tensioned/grouted joint; resistance unqualified'),
            replacement_path=dict(axis='z',required_clearance_m=1.,verified=False),
            unresolved=['actual reinforcement/tendons/embedded detail','qualified lifting points and connection capacity'])
        unit.update(metadata or {});units[identifier]=unit;return unit
    def primitive_copy(p,identifier,axis=None,lo=None,hi=None,trim_cap=False):
        spec=deepcopy(p['manufacturing']);spec['role']+='; grouped manufactured unit research geometry'
        primitives=[]
        for primitive in spec['primitives']:
            if axis is not None:
                if primitive['kind']!='box':raise ValueError('bounded splitting supports rectangular material regions only')
                half=primitive['dimensions_m'][axis]/2;c=primitive['centre_m'][axis]
                left,right=max(lo,c-half),min(hi,c+half)
                if right-left<=1e-10:continue
                primitive['dimensions_m'][axis]=right-left;primitive['centre_m'][axis]=(left+right)/2
            if trim_cap and primitive['kind']=='box':
                bottom=primitive['centre_m'][2]-primitive['dimensions_m'][2]/2
                top=min(primitive['centre_m'][2]+primitive['dimensions_m'][2]/2,9.12)
                if top<=bottom:continue
                primitive['dimensions_m'][2]=top-bottom;primitive['centre_m'][2]=(top+bottom)/2
            primitive['id']=identifier+'/'+str(len(primitives));primitives.append(primitive)
        if not primitives:return None
        spec['primitives']=primitives
        return part(identifier,p['material'],spec,mats)
    def grouped(rows,identifier,category,segments,axis,*,offsite=True,process='precast',trim_cap=False,support_ids=()):
        lo=min(part_bounds(p)[0][axis] for p in rows);hi=max(part_bounds(p)[1][axis] for p in rows)
        result=[]
        for segment in range(segments):
            uid=identifier+f'-U{segment}';pieces=[]
            for p in rows:
                piece=primitive_copy(p,uid+'/'+p['id'],axis,lo+(hi-lo)*segment/segments,lo+(hi-lo)*(segment+1)/segments,trim_cap=trim_cap)
                if piece:pieces.append(piece)
            unit=add(uid,category,pieces,offsite=offsite,process=process,support_ids=support_ids)
            # Retain source reinforcement allowance by concrete material volume.
            volume=sum(p['properties']['mass_kg']/mats[p['material']]['density_kg_m3'] for p in pieces if 'concrete' in p['material'])
            unit['concrete_m3']=volume
            unit['allocated_mass_kg']+=volume*compiled['mass_allowances']['reinforcement_kg_m3']
            unit['mass_kg']=unit['defined_mass_kg']+unit['allocated_mass_kg'];result.append(uid)
        return result
    def steel_box(uid,size,centre):return part(uid,'kit-steel',dict(role='provisional kit hardware/material envelope',primitives=[box(uid,*size,centre)]),mats)
    foundation_units=[];cap_units=[];pier_units=[];pile_units=[]
    for support in (0,1):
        prefix=f'S{support}-';rows=[p for p in original['parts'] if p['id'].startswith(prefix)]
        piles=[p for p in rows if '-pile-' in p['id']]
        local_piles=[]
        for p in piles:
            uid=p['id'];piece=primitive_copy(p,uid+'/material');volume=piece['properties']['mass_kg']/mats[piece['material']]['density_kg_m3'];reinforcement=volume*compiled['mass_allowances']['reinforcement_kg_m3']
            bored=variables['foundation_route']=='bored-prefab-cage'
            parent=[]
            if bored:
                cage=add(uid+'-cage','pile-cage',[],process='steel-fabrication',extra_mass=reinforcement,metadata=dict(bounds_m=part_bounds(piece),site_predecessors=[uid+'/bore'],source='Source reinforcement mass allowance; individual bars/cage geometry unresolved'))
                parent=[cage['id']]
            u=add(uid,'pile',[piece],offsite=not bored,process='site-concrete' if bored else 'precast',extra_mass=0. if bored else reinforcement,support_ids=parent,metadata=dict(concrete_m3=volume,site_predecessors=[] if bored else [f'S{support}/excavate']))
            local_piles.append(uid);pile_units.append(uid)
        found=grouped([p for p in rows if 'FOUND-CAP' in p['id']],prefix+'foundation-cap','foundation-cap',variables['foundation_cap_segments'],0,support_ids=local_piles);foundation_units+=found
        for index,uid in enumerate(found):
            owned=[pile for pile in local_piles if units[uid]['bounds_m'][0][0]-1e-8<=sum(row[0] for row in units[pile]['bounds_m'])/2<=units[uid]['bounds_m'][1][0]+1e-8]
            units[uid]['joint_endpoint_ids']=owned+([found[index-1]] if index else [])
        column=grouped([p for p in rows if '-P' in p['id']],prefix+'column','pier',variables['pier_segments'],2,support_ids=found)
        for previous,next_id in zip(column,column[1:]):units[next_id]['support_ids']=[previous]
        pier_units+=column
        caps=grouped([p for p in rows if p['id'].startswith(prefix+'CAP')],prefix+'pier-cap','pier-cap',variables['cap_segments'],1,trim_cap=True,support_ids=[column[-1]])
        cap_units+=caps
    bearings=[]
    for support,x in enumerate((.2,19.8)):
        for i,y in enumerate((-2.4,-1.1,1.1,2.4)):
            uid=f'S{support}-bearing-{i}'
            add(uid,'bearing',[steel_box(uid+'/body',[.3,.3,.08],[x,y,9.16])],process='purchased',support_ids=[u for u in cap_units if u.startswith(f'S{support}-') and units[u]['bounds_m'][0][1]<=y<=units[u]['bounds_m'][1][1]]);bearings.append(uid)
    deck=[]
    for track in (1,2):
        rows=[p for p in original['parts'] if p['id'].startswith(f'B0-T{track}-')]
        track_bearings=[u for u in bearings if int(u.rsplit('-',1)[1]) in ((0,1) if track==1 else (2,3))]
        groups=grouped(rows,f'deck-T{track}','deck',deck_segments,0,support_ids=track_bearings)
        for index,uid in enumerate(groups):
            if deck_segments>1:
                units[uid]['joint_endpoint_ids']=([v for v in track_bearings if v.startswith('S0-')] if index==0 else [groups[index-1]])+([v for v in track_bearings if v.startswith('S1-')] if index==len(groups)-1 else [])
                units[uid]['site_predecessors']=[groups[index-1]+'/place-and-temporary-lock'] if index else []
        for uid in groups:
            extra=(q['prestress_allowance_kg']+q['embedded_allowance_kg'])/(2*deck_segments)
            units[uid]['allocated_mass_kg']+=extra;units[uid]['mass_kg']+=extra
            units[uid]['deck_length_m']=20/deck_segments
        deck+=groups
    # Canonical allowances not resolved into actual bar/tendon geometry remain
    # mass, never free material-saving credit after the cap seat revision.
    assigned=sum(u['allocated_mass_kg'] for u in units.values())
    retained_allowance=q['reinforcement_allowance_kg']+q['prestress_allowance_kg']+q['embedded_allowance_kg']
    residue=retained_allowance-assigned
    if residue<-1e-5:raise ValueError('source mass allowance allocated twice')
    units[foundation_units[0]]['allocated_mass_kg']+=residue;units[foundation_units[0]]['mass_kg']+=residue
    deck_top=max(part_bounds(p)[1][2] for p in physical if p['manufacturing_unit_id'] in deck)
    def deck_supports(lo,hi,track):
        return [uid for uid in deck if uid.startswith(f'deck-T{track}-') and min(hi,units[uid]['bounds_m'][1][0])-max(lo,units[uid]['bounds_m'][0][0])>1e-8]
    additions=[];track_units=[];service_units=[];station_units=[]
    for track,y in ((1,-1.75),(2,1.75)):
        for index in range(4):
            uid=f'track-T{track}-{index}';p=part(uid+'/plinth','kit-concrete',dict(role='precast track module; rail/fastener details remain allowance',primitives=[box(uid,5.,.8,.18,[2.5+5*index,y,deck_top+.09])]),mats)
            unit=add(uid,'track-support',[p],support_ids=deck_supports(5*index,5*(index+1),track));track_units.append(uid);additions.append(uid)
    track_defined=sum(units[u]['mass_kg'] for u in track_units)
    if track_defined>q['superimposed_dead_allowance_kg']:raise ValueError('track geometry exceeds fixed source track allowance')
    for uid in track_units:
        allowance=(q['superimposed_dead_allowance_kg']-track_defined)/len(track_units)
        units[uid]['allocated_mass_kg']+=allowance;units[uid]['mass_kg']+=allowance
    for side in (-1,1):
        for index in range(4):
            uid=f'walkway-{side}-{index}';x=2.5+index*5
            # Solid envelope material regions model plates, no fictitious solid
            # 5m parapet wall. Support/anchor resistance remains unqualified.
            parts=[steel_box(uid+'/floor',[5.,.65,.008],[x,side*3.6,deck_top+.004]),steel_box(uid+'/rail',[5.,.025,.025],[x,side*3.9,deck_top+1.05])]
            for offset in (-2.475,2.475):parts.append(steel_box(uid+'/post'+str(offset),[.025,.025,1.0295],[x+offset,side*3.9,deck_top+.52275]))
            unit=add(uid,'walkway-parapet',parts,process='steel-fabrication',support_ids=deck_supports(5*index,5*(index+1),1 if side<0 else 2));additions.append(uid)
        length=variables['service_length_m']
        for kind,y in (('power',side*4.05),('data',side*4.35),('drainage',side*4.65)):
            for index in range(round(20/length)):
                uid=f'{kind}-{side}-{index}';p=steel_box(uid+'/carrier',[length,.15,.002],[length*(index+.5),y,deck_top-(.65 if variables['station_package'] else .3)])
                u=add(uid,'service',[p],process='steel-fabrication',support_ids=deck_supports(length*index,length*(index+1),1 if side<0 else 2),metadata=dict(service_type=kind,
                    route=dict(start_m=length*index,end_m=length*(index+1),system=kind,isolated_from=['drainage'] if kind in ('power','data') else ['power','data'],connection_access_m=.15)))
                service_units.append(uid);additions.append(uid)
    if variables['station_package']:
        station_units=station_extension(add,steel_box,part,box,mats,deck,deck_top)
        additions+=station_units
    for unit in units.values():
        size=[b-a for a,b in zip(*unit['bounds_m'])]
        unit['transport_dimensions_m']=sorted(size,reverse=True)
        axis=max(range(3),key=lambda i:size[i]);centre=[(a+b)/2 for a,b in zip(*unit['bounds_m'])]
        points=[]
        for fraction in unit['lifting_points_fraction']:
            point=list(centre);point[axis]=unit['bounds_m'][0][axis]+fraction*size[axis]
            point[1 if axis==2 else 2]=unit['bounds_m'][1][1 if axis==2 else 2];points.append(point)
        unit['lifting_provisions']=dict(proposed_anchor_points_m=points,anchor_geometry=None,qualified_capacity_n=None,
            scope='Proposed surface anchor datums only; inserts/padeyes, sling angles and stability require design and proof')
        category=unit['category']
        if category=='pile' and unit['offsite']:
            unit['pile_installation']=dict(method='driven',segments_m=[size[2]],
                installation_resistance=None,acceptance_criteria=None,
                scope='Full-length precast pile pitching/driving scenario; joints and acceptance require qualified details')
        wet=category in {'foundation-cap','pier','pier-cap','station-foundation','station-stair'} or (category=='pile' and not unit['offsite']) or (category=='deck' and variables['architecture']=='segmental')
        unit['connection_bundle']=dict(mechanism='reinforced cast pile and ground transfer' if category=='pile' and not unit['offsite'] else
            'grouted shear key and post-tensioned mechanical restraint' if wet else 'guided seat and captive mechanical fastening',
            requires_wet_cure=wet,capacity_and_qualification=None)
        unit['locating_features']['positive_lock']=unit['connection_bundle']['mechanism']
        unit['physical_definitions_sha256']={p['id']:core.digest(p) for p in physical if p['id'] in unit['physical_part_ids']}
        unit['revision']=core.digest({k:v for k,v in unit.items() if k!='revision'})
    contract=d.contract('20m manufactured-unit civil kit; every acceptance gate open',physical,mats)
    contract['revision']='CIVIL-KIT-'+core.digest(dict(variables=variables,basis=basis))[:16]
    contract['unresolved_part_allocations']=['reinforcement, prestress and rail hardware retained as explicit source mass allowances',
        'connection internals, qualified lifting anchors, complete service routes/penetrations and stair stringers remain unresolved']
    defined=sum(p['properties']['mass_kg'] for p in physical)
    ledger=dict(canonical_material_mass_kg=base_mass,canonical_installed_study_mass_kg=q['installed_study_mass_kg'],
        retained_reinforcement_prestress_inserts_kg=retained_allowance,retained_track_budget_kg=q['superimposed_dead_allowance_kg'],
        defined_kit_material_mass_kg=defined,allocated_unmodeled_mass_kg=sum(u['allocated_mass_kg'] for u in units.values()),
        installed_study_mass_kg=sum(u['mass_kg'] for u in units.values()),
        mass_balance_residual_kg=sum(u['mass_kg'] for u in units.values())-defined-sum(u['allocated_mass_kg'] for u in units.values()),
        scope='Defined geometry plus explicit retained allowances; new hardware/services/station are gross additions, no unsubstantiated substitution credits')
    kit=dict(schema='osr-civil-manufactured-kit/1',variables=variables,basis=basis,basis_sha256=core.digest(basis),
        study=study,candidate=compiled,physical_contract=contract,units=list(units.values()),mass_ledger=ledger,
        service_routes=[dict(id=kind+str(side),system=kind,side=side,unit_ids=[u for u in service_units if u.startswith(kind+f'-{side}-')]) for kind in ('power','data','drainage') for side in (-1,1)],
        component_coverage=dict(piles=pile_units,foundation_caps=foundation_units,piers=pier_units,pier_caps=cap_units,
            decks=deck,bearings=bearings,track_support=track_units,walkways=[u['id'] for u in units.values() if u['category']=='walkway-parapet'],
            pile_cages=[u['id'] for u in units.values() if u['category']=='pile-cage'],services=service_units,station=station_units),
        temporary_units=[dict(id='falsework-tower-'+str(i),category='temporary-falsework',offsite=True,mass_kg=2000.,
            transport_dimensions_m=[4.,3.,2.],basis='Unqualified reusable-plant mass and transport-envelope hypotheses; individual members, footings and rigging not detailed') for i in range(6)] if variables['architecture']=='segmental' else [],
        unknown=basis['open_evidence']+contract['unresolved_part_allocations'],**core.FLAGS)
    kit['operation_graph']=assembly_graph(kit)
    kit['travellers']=[qa_traveller.template(u) for u in kit['units']]
    return kit


def validate_kit(kit):
    units={u['id']:u for u in kit['units']};parts={p['id']:p for p in kit['physical_contract']['parts']}
    refs=[identity for u in units.values() for identity in u['physical_part_ids']]
    checks=dict(unique_manufactured_units=len(units)==len(kit['units']),
        region_to_unit_bijection=len(refs)==len(set(refs)) and set(refs)==parts.keys(),
        graph_unit_identity={p['id'] for p in kit['operation_graph']['parts']}==units.keys(),
        unit_mass_accounted=abs(sum(u['mass_kg'] for u in units.values())-kit['mass_ledger']['installed_study_mass_kg'])<1e-6)
    for uid,u in units.items():
        physical={p:core.digest(parts[p]) for p in u['physical_part_ids'] if p in parts}
        checks[uid+'/geometry_revision']=physical==u['physical_definitions_sha256'] and u['revision']==core.digest({k:v for k,v in u.items() if k!='revision'})
        checks[uid+'/mass_ledger']=set(u['physical_part_ids'])<=parts.keys() and abs(u['mass_kg']-u['allocated_mass_kg']-sum(parts[p]['properties']['mass_kg'] for p in u['physical_part_ids'] if p in parts))<1e-6
        checks[uid+'/support_identities']=set(u['support_ids'])<=units.keys()
    kinds={'piles':'pile','pile_cages':'pile-cage','foundation_caps':'foundation-cap','piers':'pier','pier_caps':'pier-cap','decks':'deck','bearings':'bearing','track_support':'track-support','walkways':'walkway-parapet','services':'service'}
    for key,category in kinds.items():
        checks['coverage/'+key]=set(kit['component_coverage'][key])=={u['id'] for u in units.values() if u['category']==category}
        if key!='pile_cages':checks['nonempty/'+key]=bool(kit['component_coverage'][key])
    for route in kit['service_routes']:
        sequence=sorted((units[uid]['route'] for uid in route['unit_ids'] if uid in units),key=lambda r:r['start_m'])
        checks['routing/'+route['id']]=bool(sequence) and sequence[0]['start_m']==0 and sequence[-1]['end_m']==20 and all(a['end_m']==b['start_m'] for a,b in zip(sequence,sequence[1:])) and all(r['system']==route['system'] for r in sequence)
    checks['station_scope']=bool(kit['component_coverage']['station'])==kit['variables']['station_package']
    checks['station_identity']=set(kit['component_coverage']['station'])=={u['id'] for u in units.values() if u['category'].startswith('station-')}
    if kit['variables']['station_package']:
        checks['station_required_packages']={'station-foundation','station-column','station-crosshead','station-stringer','station-platform','station-canopy','station-stair'}<={u['category'] for u in units.values()}
    checks['required_service_routes']=len(kit['service_routes'])==6 and {r['id'] for r in kit['service_routes']}=={kind+str(side) for kind in ('power','data','drainage') for side in (-1,1)}
    checks['qa_identity_and_plan']=len(kit['travellers'])==len(units) and {t['unit_id'] for t in kit['travellers']}==units.keys() and all(t['unit_id'] in units and t['unit_revision']==units[t['unit_id']]['revision'] and t['required']==qa_traveller.requirements(units[t['unit_id']]) for t in kit['travellers'])
    return checks


def station_extension(add,steel_box,part,box,mats,deck,deck_top):
    """Optional station package with its own footings; full station acceptance open."""
    ids=[];supports=[];column_height=deck_top-.45;platform_top=deck_top+.1
    def rhs(uid,length,width,height,centre,axis='x'):
        x,y,z=centre;wall=.008;pieces=[]
        for side in (-1,1):
            pieces.append(steel_box(uid+'/flange'+str(side),[length,width,wall] if axis=='x' else [width,length,wall],[x,y,z+side*(height-wall)/2]))
            pieces.append(steel_box(uid+'/web'+str(side),[length,wall,height-2*wall] if axis=='x' else [wall,length,height-2*wall],
                [x,y+side*(width-wall)/2,z] if axis=='x' else [x+side*(width-wall)/2,y,z]))
        return pieces
    for side in (-1,1):
        for end,x in enumerate((.15,19.85)):
            uid=f'station-{side}-footing-{end}'
            p=part(uid,'kit-concrete',dict(role='station independent reference footing, ground unqualified',primitives=[box(uid,2.,2.,1.,[x,side*5.5,-.5])]),mats)
            add(uid,'station-foundation',[p],offsite=False,process='site-concrete',extra_mass=480.,metadata=dict(concrete_m3=4.));ids.append(uid)
            column=uid+'-column'
            pieces=[steel_box(column+f'/web-{j}',size,[x+dx,side*5.5+dy,column_height/2]) for j,(size,dx,dy) in enumerate((([.25,.012,column_height],0,-.119),([.25,.012,column_height],0,.119),([.012,.226,column_height],-.119,0),([.012,.226,column_height],.119,0)))]
            add(column,'station-column',pieces,process='steel-fabrication',support_ids=[uid]);ids.append(column)
            cross=column+'-crosshead';add(cross,'station-crosshead',rhs(cross,2.,.2,.35,[x,side*5.5,deck_top-.275],axis='y'),process='steel-fabrication',support_ids=[column]);ids.append(cross);supports.append(cross)
        beams=[]
        for edge in (-1,1):
            uid=f'station-{side}-platform-edge-{edge}'
            add(uid,'station-stringer',rhs(uid,19.5,.15,.3,[10.,side*5.5+edge*.9,deck_top-.25]),process='steel-fabrication',support_ids=list(supports[-2:]));ids.append(uid);beams.append(uid)
        for index in range(4):
            uid=f'station-{side}-platform-{index}';p=part(uid,'kit-concrete',dict(role='reference platform plank; reinforcement and crowd-load qualification open',primitives=[box(uid,5.,2.,.2,[2.5+5*index,side*5.5,deck_top])]),mats)
            add(uid,'station-platform',[p],extra_mass=240.,support_ids=beams);ids.append(uid)
            roof=uid+'-canopy';roof_parts=[steel_box(roof,[5.,2.,.002],[2.5+5*index,side*5.5,deck_top+2.6])]
            for j,(dx,dy) in enumerate(((-2.4,-.9),(-2.4,.9),(2.4,-.9),(2.4,.9))):
                roof_parts.append(steel_box(roof+'/post'+str(j),[.04,.04,2.499],[2.5+5*index+dx,side*5.5+dy,deck_top+1.3495]))
            add(roof,'station-canopy',roof_parts,process='steel-fabrication',support_ids=[uid]);ids.append(roof)
        # Stair flights have actual individual treads, while their stringers,
        # landings, guarding and station egress design remain explicit gaps.
        for flight in range(4):
            uid=f'station-{side}-stairs-{flight}';pieces=[]
            rise=platform_top/60
            for step in range(15):
                x=21.+(.3*step if flight%2==0 else .3*(14-step));y=side*(5.0+.7*(flight%2));z=rise*(15*flight+step+.5)
                pieces.append(part(uid+f'/tread-{step}','kit-concrete',dict(role='reference stair tread; supporting flight structure unresolved',primitives=[box(uid+str(step),.3,1.2,rise,[x,y,z])]),mats))
            extra=500.+sum(p['properties']['mass_kg']/2500 for p in pieces)*120
            add(uid,'station-stair',pieces,extra_mass=extra,support_ids=beams,metadata=dict(additional_allowance_basis='Unqualified 500kg stringer/landing allowance plus reference reinforcement allowance per flight; not a detailed supporting structure'));ids.append(uid)
    return ids


def assembly_graph(kit):
    inventory=[dict(id=u['id'],mass_kg=u['mass_kg'],bounds_m=u['bounds_m']) for u in kit['units']]
    graph=operation_graph.simple(inventory,capacity_kg=1e9)
    graph['fixtures'][0]['load_scope']='current_operation'
    by_id={u['id']:u for u in kit['units']}
    graph['joints']=[]
    for index,p in enumerate(graph['parts']):
        child=p['id'];unit=by_id[child]
        endpoints=unit.get('joint_endpoint_ids',unit['support_ids']) or ['world']
        if unit['category']=='pile':endpoints=list(dict.fromkeys([*endpoints,'world']))
        links=[]
        for endpoint in endpoints:
            joint_id='retention/'+child+'/'+endpoint;links.append(joint_id)
            graph['joints'].append(dict(id=joint_id,endpoints=[child,endpoint],process='fasten',operation=f'join-{index}',
                lock_state='simulated-positive-lock',locating_features=unit['locating_features'],connection_bundle=unit['connection_bundle'],capacity_evidence=None))
        p['required_joints']=links
        graph['operations'][2*index+1].pop('joint',None)
        graph['operations'][2*index+1]['joints']=links
    # Reorder installation by explicit support dependencies, not dictionary order.
    installed=[];remaining=set(by_id)
    while remaining:
        ready=sorted(uid for uid in remaining if set(by_id[uid]['support_ids']+by_id[uid].get('joint_endpoint_ids',[]))<=set(installed))
        if not ready:raise ValueError('civil unit support cycle')
        installed+=ready;remaining-=set(ready)
    ops={op['id']:op for op in graph['operations']};index={p['id']:i for i,p in enumerate(graph['parts'])}
    previous=[]
    for uid in installed:
        i=index[uid];ops[f'install-{i}']['after']=list(previous);previous=[f'join-{i}']
    ops['inspect']['after']=previous
    return graph
