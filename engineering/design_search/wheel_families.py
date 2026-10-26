"""Common physical wheel/rail/LIM candidates; evaluator hypotheses stay outside IDs."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import json
from . import contracts
from engineering.station_rail import ROOT,vehicle as base_vehicle,civil,bim
from engineering.station_rail.vehicle import box
from engineering.station_rail.common import digest
EYE=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
FAMILY='wheel_rail_station_lim'
PRODUCER='engineering/design_search/wheel_families.py'


def physical(value):
    if isinstance(value,dict):return {k:physical(v) for k,v in value.items() if k not in ('name','label','revision_reason')}
    if isinstance(value,list):return [physical(v) for v in value]
    return value


@lru_cache(maxsize=4)
def _base_cached(epoch):return base_vehicle.build(ROOT)

def _base():
    names=('engineering/station_rail/__init__.py','engineering/station_rail/vehicle.py','engineering/station_rail/common.py','engineering/station_rail/brief.toml','engineering/station_rail/electrical.py','docs/design-engine/ferrite-maglev/comfort-design/design.json.gz','docs/design-engine/ferrite-maglev/comfort-design/manifest.json')
    return deepcopy(_base_cached(tuple(digest(ROOT/n) for n in names)))


def _parameters(candidate):
    p=deepcopy(candidate['architecture']['wheel_parameters'])
    p['motor']=dict(physical=dict(p['motor'],name=candidate.get('label','reference').split('/')[-1]),
        evaluation=deepcopy(candidate['evaluation_plan']['motor']))
    return p


def _materialize(parameters):
    names=('wheel_families.py','wheel_body.py','wheel_motor.py','wheel_brakes.py')
    epoch=tuple(digest(Path(__file__).with_name(n)) for n in names)
    return deepcopy(_materialize_cached(k=contracts.encoded(parameters),epoch=epoch))

@lru_cache(maxsize=16)
def _materialize_cached(k,epoch):
    parameters=json.loads(k)
    from . import wheel_body,wheel_motor,wheel_brakes
    car=wheel_body.materialize(deepcopy(_base()),parameters['body'],root=ROOT)
    brake_before=car['mass']['accounted_tare_kg_per_car']
    car=wheel_brakes.materialize(car,parameters['brakes'])
    brake_delta=car['mass']['accounted_tare_kg_per_car']-brake_before
    if brake_delta:car['inventory'].append(dict(id='revised-brake-housing-stock',system='braking',mass_kg=brake_delta,evidence_class='counted-additional-material'))
    stock=wheel_motor.stock(parameters['motor']);fin=next(p for p in stock if p['installation']=='onboard')
    old={p['id']:p for p in car['geometry_parts']};before=sum(p['mass_kg'] for p in car['geometry_parts'])
    if fin['size_m'][0]!=9. or fin['size_m'][1]!=.015:raise ValueError('Length/thickness revisions require a new mounting family')
    old['station-secondary/active-fin']=deepcopy(fin)
    top=.02+fin['size_m'][2]
    old['station-secondary/upper-neck']=box('station-secondary/upper-neck',[-4.5,-.0075,top],[9.,.015,.34-top],system='passive-secondary')
    car['geometry_parts']=list(old.values());after=sum(p['mass_kg'] for p in car['geometry_parts']);delta=after-before
    for k in ('accounted_tare_kg_per_car','accounted_cap_loaded_kg_per_car','accounted_160_control_kg_per_car'):car['mass'][k]+=delta
    car['mass']['accounted_tare_kg_six_cars']=6*car['mass']['accounted_tare_kg_per_car'];car['mass']['located_material_kg']=after
    car['mass']['CG_m']=car['mass']['inertia_kg_m2']=None
    car['mass']['installed_tare_kg_per_car']=None;car['mass']['installed_loaded_kg_per_car']=None
    car['physical_definition']['propulsion']['secondary_height_m']=fin['size_m'][2]
    car['propulsion']['active_fin_aluminium_mass_kg']=fin['mass_kg']
    secondary_mass=sum(p['mass_kg'] for p in car['geometry_parts'] if p['id'].startswith('station-secondary/'))
    for key in ('secondary_aluminium_mass_kg','accounted_mass_kg','installed_accounted_mass_kg'):car['propulsion'][key]=secondary_mass
    for row in car['inventory']:
        if row['id']=='passive-secondary':row['mass_kg']=secondary_mass
    for load,key in [('empty','accounted_tare_kg_per_car'),('normal','accounted_cap_loaded_kg_per_car'),('crowd_control','accounted_160_control_kg_per_car')]:car['axle_loads'][load+'_kg_per_axle']=car['mass'][key]/4
    car['physical_definition']['geometry_definition_id']=contracts.identity([native_part(p) for p in car['geometry_parts']])
    car['physical_definition']['brake_revision']=deepcopy(parameters['brakes'])
    car['wayside_parts']=[p for p in stock if p['installation']=='wayside']
    guide=parameters['guideway'];beam=civil.alternative(car,guide['span_m'],guide['family'],'crowd_control')
    # Beam geometry is the same explicitly selected physical stock used by its
    # moving-load calculation. Current bounded campaign uses the box family.
    if guide['family']!='box-beam':raise ValueError('Generated non-box BIM requires a registered section exporter')
    beam_parts=bim.parts(dict(civil=dict(selected_reference=beam)))
    for p in beam_parts:
        p.update(kind='box',system='rail-civil',density_kg_m3=beam['concrete_mass_kg']/beam['concrete_m3'] if p['material']=='concrete' else 7850.)
        p['mass_kg']=p['volume_m3']*p['density_kg_m3'];p['cg_m']=[a+b/2 for a,b in zip(p['at_m'],p['size_m'])];p['inertia_kg_m2']=None
    car['civil_parts']=beam_parts;car['selected_civil']=beam
    return car


def native_part(p):
    allowed=('id','kind','at_m','size_m','axis','radius_m','inner_radius_m','length_m','holes','rectangular_cutouts','volume_m3','mass_kg','density_kg_m3','material','system','role','geometry_status','laminate_specification')
    return {key:deepcopy(p[key]) for key in allowed if key in p}


def _parts_contract(car):
    geometry=[];inventory=[];materials={}
    allowed=('id','kind','at_m','size_m','axis','radius_m','inner_radius_m','length_m','holes','rectangular_cutouts',
        'volume_m3','mass_kg','density_kg_m3','material','system','role','geometry_status')
    for frame,scope,parts in [('vehicle','vehicle-per-car',car['geometry_parts']),('station','wayside-per-section',car['wayside_parts']),('guidebeam','guideway-per-span',car['civil_parts'])]:
        for p in parts:
            uid=frame+'/'+p['id'];mat=p.get('material','counted-stock');rho=p['density_kg_m3'];material=contracts.identity(dict(material=mat,density=rho))
            materials[material]=dict(id=material,density_kg_m3=rho,basis='Declared source material/density; acceptance open: '+mat)
            native=native_part(p)
            # A boolean/holed stock must never be reinterpreted as a solid box.
            kind=p['kind'] if p['kind']!='box' or not p.get('holes') else 'native-boolean-solid'
            g=dict(id=uid,kind=kind,frame_id=frame,material_id=material,native_part=native)
            if kind=='box':g.update(at_m=p['at_m'],size_m=p['size_m'])
            geometry.append(g)
            cg=p.get('cg_m')
            if cg is None and 'size_m' in p:cg=[a+b/2 for a,b in zip(p['at_m'],p['size_m'])] if not p.get('rectangular_cutouts') and not p.get('holes') else None
            inventory.append(dict(id=uid,geometry_id=uid,frame_id=frame,scope=scope,quantity=1,status='known',
                unit_mass_kg=p['mass_kg'],cg_m=cg,inertia_kg_m2=p.get('inertia_kg_m2'),basis='Exact generated counted stock; unresolved installation separate'))
    material='unresolved';materials[material]=dict(id=material,density_kg_m3=None,basis='Unlocated reference accounts and unknown equipment')
    residual=car['mass']['accounted_tare_kg_per_car']-sum(p['mass_kg'] for p in car['geometry_parts'])
    if residual<=0:raise ValueError('Reference stock account unexpectedly removed')
    geometry.append(dict(id='reference/unlocated-service-and-bogie-budget',kind='unlocated-mass-budget',frame_id='vehicle',material_id=material))
    inventory.append(dict(id='reference/unlocated-service-and-bogie-budget',geometry_id='reference/unlocated-service-and-bogie-budget',frame_id='vehicle',scope='vehicle-per-car',quantity=1,status='known',unit_mass_kg=residual,cg_m=None,inertia_kg_m2=None,basis='Conservative inherited supplier/reference allocations; overlapping services and installation remain unresolved'))
    for frame,scope,names in [('vehicle','vehicle-per-car',car.get('missing_inventory',[])+['Actual joining hardware and revised brake installation']),('station','wayside-per-section',['Inverter, branch cable, real coil installation, cooling, supports and protection']),('guidebeam','guideway-per-span',['Detailed rebar/tendons, fasteners, bearings, pier/foundation and access'])]:
        for i,name in enumerate(names):
            uid=frame+'/unknown/'+str(i);geometry.append(dict(id=uid,kind='unresolved-equipment',frame_id=frame,material_id=material))
            inventory.append(dict(id=uid,geometry_id=uid,frame_id=frame,scope=scope,quantity=1,status='unknown',unit_mass_kg=None,cg_m=None,inertia_kg_m2=None,basis=name))
    return geometry,inventory,list(materials.values())


def make(parameters,*,requirement_revision,lineage=None,label=''):
    car=_materialize(parameters);geometry,inventory,materials=_parts_contract(car)
    motor=physical(parameters['motor']['physical']);body=physical(parameters['body'])
    architecture=dict(family=FAMILY,cars=6,body_length_m=17.,normal_passengers_per_car=46,crowd_passengers_per_car=160,
        wheel_parameters=dict(body=body,motor=motor,brakes=parameters['brakes'],guideway=parameters['guideway']),
        selected_civil_id=car['selected_civil']['physical_civil_component_id'],no_onboard_traction=True)
    candidate=contracts.make_candidate(requirement_revision=requirement_revision,architecture=architecture,
        frames=[dict(id=name,parent_id=None,origin_m=[0.,0.,0.],rotation_matrix=EYE) for name in ('vehicle','station','guidebeam')],
        materials=materials,geometry=geometry,interfaces=[dict(id='wheel-rail',frame_id='vehicle',gauge_m=1.435,qualified=False),dict(id='station-primary-fin',frame_id='station',gap_m=.015,qualified=False),dict(id='body-bogie',frame_id='vehicle',qualified=False)],
        installed_inventory=inventory,lineage=lineage,label=label,source_bindings=dict(parent_candidate_id=_base()['candidate_id'],source_sha256=_base()['source_sha256']))
    # Operating/mesh inputs are context, never physical candidate identity.
    candidate['evaluation_plan']=dict(motor=deepcopy(parameters['motor']['evaluation']))
    return contracts.validate_candidate(candidate)


def initial_families(requirement_revision):
    from . import wheel_body,wheel_motor,wheel_brakes
    bodies=wheel_body.initial_parameters();motors=wheel_motor.initial_parameters()
    return [make(dict(body=bodies[i],motor=motors[i],brakes=wheel_brakes.default_parameters(),guideway=dict(family='box-beam',span_m=20.)),
        requirement_revision=requirement_revision,label='v06/'+motors[i]['physical']['name'],
        lineage=dict(parent_candidate_ids=[],generation=0,operation='generated-wheel-family',parent_reference_id=_base()['candidate_id'])) for i in range(2)]


def validate_supported(candidate):
    contracts.validate_candidate(candidate)
    expected=make(_parameters(candidate),requirement_revision=candidate['requirement_revision'],lineage=candidate['lineage'],label=candidate['label'])
    if expected!=candidate:raise ValueError('Wheel physical geometry, stock or context differs from generated definition')
    return candidate


def materialize(candidate):
    validate_supported(candidate);car=_materialize(_parameters(candidate));car['parent_candidate_id']=_base()['candidate_id'];car['candidate_id']=candidate['candidate_id']
    # Preserve the exact body physical identity expected by its native adapter.
    car['support_component_id']=contracts.identity(dict(running_gear=_base()['support_component_id'],brakes=candidate['architecture']['wheel_parameters']['brakes']))
    car['propulsion_component_id']=contracts.identity(candidate['architecture']['wheel_parameters']['motor'])
    car['configuration_sha256']=candidate['candidate_id'];return car


def propose_revision(candidate,results,*,trial_index=0):
    from . import wheel_body,wheel_motor,wheel_brakes
    validate_supported(candidate);p=_parameters(candidate);diagnostics={r['request']['evaluator_id']:r['diagnostics'] for r in results if r['purpose']!='confirmation'}
    if not diagnostics:return None
    byname={r['request']['evaluator_id']:r for r in results if r['purpose']!='confirmation'}
    b=byname.get('wheel-body',{});br=next((d.get('native',{}) for d in b.get('diagnostics',[])),{})
    body_diagnostic=dict(engineering_screen=b.get('screen_status'),normal_deflection_m=br.get('metrics',{}).get('normal_deflection_m'))
    m=byname.get('wheel-motor',{});mr=next((d.get('native',{}) for d in m.get('diagnostics',[])),{})
    motor_diagnostic=dict(engineering_screen=m.get('screen_status'),reasons=mr.get('failure_reasons',[]))
    p['body']=wheel_body.revise(p['body'],body_diagnostic,trial_index+1)
    p['motor']=wheel_motor.revise(p['motor'],motor_diagnostic,trial_index+1)
    p['brakes']=wheel_brakes.revise(p['brakes'],diagnostics.get('wheel-brakes',[]),trial_index+1)
    return make(p,requirement_revision=candidate['requirement_revision'],label='v06/revision-'+str(trial_index+1)+'/'+p['motor']['physical'].get('name','motor'),
        lineage=dict(parent_candidate_ids=[candidate['candidate_id']],generation=trial_index+1,operation='failure-driven-wheel-revision',
            trigger_evaluation_ids=[r['evaluation_id'] for r in results if r['screen_status'] in ('fail','unknown')],
            reason='Change generated stock after typed native diagnostics; numerical and evidence gaps remain explicit'))
