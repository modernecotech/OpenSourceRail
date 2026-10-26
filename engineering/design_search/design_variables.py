"""Extensible design freedom, distinct from implemented or validated solvers.

Descriptors name variables, dependencies and interface consequences. Examples
are research seeds, never a complete list of possible engineering solutions.
Registering a new material/topology does not provide its physical properties,
generator, native evaluator or evidence. It cannot authorize a release.
"""
from copy import deepcopy
from hashlib import sha256
from math import isfinite
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[2]
PRODUCER='engineering/design_search/design_variables.py'
SCHEMA='osr-design-variable-registry/1'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
           manufacturing_release=False,operating_release=False)
DOMAINS=('materials','body','joints','runninggear','propulsion','braking','fitout','services','operations','civil','station','manufacturing','maintenance','model')
SCOPES=('physical','operational','model-assumption')
KINDS=('number','integer','identifier','sequence','record','boolean')
SUPPORT=('bounded-existing-research-adapter','definition-generator-only','new-adapter-required','evaluation-only')
DESCRIPTOR_KEYS={'id','domain','kind','unit','identity_scope','example_values','example_values_are_exhaustive','trial_bounds',
    'dependencies','requires_compatibility','invalidates','model_support','required_evidence','numerical_properties_supplied','provenance',*FLAGS}


def identity(value):
    return sha256((json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()


def source_map():
    return {PRODUCER:sha256(Path(__file__).read_bytes()).hexdigest()}


def descriptor(name,domain,kind,unit,*,scope='physical',examples=(),dependencies=(),effects=(),
               compatibility=(),support='new-adapter-required',adapter=None,note='',minimum=None,maximum=None):
    """Construct a declaration; validate_descriptor supplies its content ID."""
    return validate_descriptor(dict(id=name,domain=domain,kind=kind,unit=unit,identity_scope=scope,
        example_values=list(examples),example_values_are_exhaustive=False,
        trial_bounds=dict(minimum=minimum,maximum=maximum,basis='Campaign bounds only; no material/functional allowable inferred'),
        dependencies=list(dependencies),requires_compatibility=list(compatibility),
        invalidates=list(effects),model_support=dict(status=support,adapter=adapter,domain_note=note,
            independently_validated=False,native_dispatch_allowed=False),
        required_evidence=['explicit geometry/material/interface definition','source-bound model and validity domain',
            'complete inventory and installed mass/CG/inertia impact','manufacturing, assembly and maintenance representation'],
        numerical_properties_supplied=False,provenance='Project design-freedom declaration; not supplier or physical evidence',**FLAGS))


def validate_descriptor(row):
    row=deepcopy(row);provided=row.pop('descriptor_id',None)
    if set(row)!=DESCRIPTOR_KEYS:raise ValueError('Explicit descriptor fields required; evaluator/selection fields belong elsewhere')
    if provided is not None and provided!=identity(row):raise ValueError('Variable descriptor identity differs')
    if not isinstance(row.get('id'),str) or re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]+',row['id']) is None:raise ValueError('Stable variable identifier required')
    if row.get('domain') not in DOMAINS or row.get('kind') not in KINDS or row.get('identity_scope') not in SCOPES:raise ValueError('Explicit variable domain/type/identity scope required')
    if not isinstance(row.get('unit'),str) or not row['unit'].strip():raise ValueError('Explicit unit required, including1 or mixed-record')
    for key in ('example_values','dependencies','requires_compatibility','invalidates','required_evidence'):
        if not isinstance(row.get(key),list):raise ValueError('Explicit variable metadata list required: '+key)
    if not row['invalidates'] or not row['requires_compatibility'] or not row['required_evidence']:raise ValueError('Consequences, compatibility and evidence cannot be omitted')
    support=row.get('model_support',{})
    if support.get('status') not in SUPPORT or support.get('independently_validated') is not False or support.get('native_dispatch_allowed') is not False:raise ValueError('A descriptor cannot assert validated native capability')
    if not isinstance(support.get('domain_note'),str) or not support['domain_note']:raise ValueError('Declared model domain required')
    if row.get('numerical_properties_supplied') is not False or row.get('example_values_are_exhaustive') is not False:raise ValueError('Examples cannot supply material properties or close the design space')
    bounds=row.get('trial_bounds',{})
    for key in ('minimum','maximum'):
        x=bounds.get(key)
        if x is not None and (isinstance(x,bool) or not isinstance(x,(float,int)) or not isfinite(x)):raise ValueError('Finite trial bounds required')
    if bounds.get('minimum') is not None and bounds.get('maximum') is not None and bounds['minimum']>bounds['maximum']:raise ValueError('Ordered trial bounds required')
    if any(row.get(n) is not False for n in FLAGS):raise ValueError('Variable declarations cannot grant release')
    if not isinstance(row.get('provenance'),str) or not row['provenance']:raise ValueError('Descriptor provenance required')
    row['descriptor_id']=identity(row);return row


def _checked_registry(value):
    if value.get('schema')!=SCHEMA or value.get('registry_id')!=identity({n:v for n,v in value.items() if n!='registry_id'}):raise ValueError('Source/content-bound registry required')
    if any(value.get(n) is not False for n in FLAGS) or value.get('source_sha256')!=source_map():raise ValueError('Current-source unaccepted registry required')
    for name,row in value.get('variables',{}).items():
        if name!=row.get('id') or validate_descriptor(row)!=row:raise ValueError('Variable descriptor identity differs')
        if name in row['dependencies'] or set(row['dependencies'])-set(value['variables']):raise ValueError('Registered non-self dependency identifiers required')
    return value


def catalogue():
    records=[]
    def add(name,domain,kind,unit,**kw):
        defaults=dict(effects=['geometry','installed-mass-CG-inertia','coupled-dynamics','cost-and-manufacturing'],
            compatibility=['physical interfaces and complete installed envelope'],note='Definition freedom only; candidate-specific generator, model domain and independent evidence required')
        defaults.update(kw);records.append(descriptor(name,domain,kind,unit,**defaults))
    def material(name,examples):
        add(name,'materials','identifier','1',examples=examples,
            effects=['material-property-tables','geometry','mass-CG-inertia','stress-buckling-fatigue','thermal-fire','joints-and-corrosion','manufacturing-and-repair','economics'],
            compatibility=['temperature/moisture/direction and lot-dependent properties','joining, corrosion, fire and repair compatibility'],
            support='definition-generator-only' if name=='material.core_family' else 'new-adapter-required',
            adapter='engineering.design_search.structural_families:material_catalogue' if name=='material.core_family' else None,
            note='Existing core catalogue contains specific foam/honeycomb leads only. Other grades need dedicated data/generator extensions; published leads and synthetic values are not design allowables or a new constitutive model')
    material('material.primary_grade',['6082-T6','GFRP laminate','local steel grade','hybrid construction'])
    material('material.fibre_family',['E-glass','carbon-local-reinforcement','basalt-research'])
    material('material.resin_family',['epoxy','vinylester','phenolic','thermoplastic-research'])
    material('material.core_family',['PET foam','PVC foam','aluminium honeycomb','aramid honeycomb','corrugated core','hollow double skin'])
    material('material.fastener_grade',['steel bolt grade','isolated stainless fastener','structural rivet'])
    material('material.adhesive_grade',['structural epoxy','toughened film adhesive','hybrid bonded/bolted'])
    material('material.electrical_steel_grade',['supplier-specific nonlinear grade'])
    material('material.conductor_grade',['copper','aluminium'])
    material('material.glazing_grade',['rail glazing','hard-coated polymer research'])
    for name,kind,unit,examples in [
        ('body.topology','identifier','1',['spaceframe','semi-monocoque','sandwich monocoque','hybrid load-bearing panels']),
        ('body.section_family','identifier','1',['box','extrusion','corrugated sheet','hat section','closed double skin']),
        ('body.member_positions','sequence','m',[]),('body.crossmember_pitch_m','number','m',[.5,1.,1.5]),
        ('body.roof_floor_loadpath','identifier','1',['integrated closed shell','frame with replaceable panels']),
        ('body.aperture_geometry','record','mixed-record',[]),('body.car_length_m','number','m',[12.,17.,20.]),
        ('body.car_width_m','number','m',[2.4,2.65]),('body.underfloor_depth_m','number','m',[]),
        ('body.face_thickness_m','number','m',[.001,.002,.003]),('body.core_thickness_m','number','m',[.025,.04,.06]),
        ('body.core_cell_direction','identifier','1',['longitudinal','transverse','local-load-aligned']),
        ('body.ply_angles_deg','sequence','deg',[[0,90,90,0],[0,45,-45,90]]),
        ('body.ply_thickness_m','number','m',[.00025,.0005]),('body.local_reinforcement','record','mixed-record',[])]:
        existing=name in ('body.topology','body.crossmember_pitch_m','body.face_thickness_m','body.core_thickness_m','body.core_cell_direction','body.ply_angles_deg','body.ply_thickness_m')
        add(name,'body',kind,unit,examples=examples,dependencies=['material.primary_grade','material.core_family'],
            effects=['body-geometry-and-installed-equipment','mass-CG-inertia','all-axis-structure-and-joints','bogie-and-motor-interfaces','manufacturing','civil-and-journey'],
            compatibility=['supported load-path topology, apertures and installed clearances','anisotropy, buckling, fatigue and environmental data'],
            support='definition-generator-only' if existing else 'new-adapter-required',
            adapter='engineering.design_search.structural_families:generate' if existing else None,
            note='Some local stock generators exist; full new topology, laminate, core, joint and installed assembly require appropriate native adapters')
    for name,examples in [('body.sill.depth_m',[.35,.60,.65]),('body.sill.wall_m',[.008,.012,.016])]:
        add(name,'body','number','m',examples=examples,minimum=0.,dependencies=['body.section_family'],
            support='bounded-existing-research-adapter',adapter='engineering.design_search.joint_body:materialize_finite_body',
            effects=['counted-stock-and-floor-fit','mass-CG-inertia','all-axis-structure-and-joints','civil','motor-thrust-and-braking','manufacturing'],
            compatibility=['Exact existing depth/wall pairs only: (.35,.008),(.60,.012),(.60,.016),(.65,.016)','Floor, bogie, capture and station motor envelope'],
            note='Depth and wall are coupled. Other values/shapes need a generator/domain extension; intact synthetic bonds are unqualified')
    for name,kind,unit,examples in [
        ('joint.family','identifier','1',['bonded overlap','bolted insert','riveted flange','hybrid retained joint','co-cured flange']),
        ('joint.overlap_m','number','m',[.04,.08,.16]),('joint.bond_thickness_m','number','m',[.00025,.0005]),
        ('joint.fastener_layout','record','mixed-record',[]),('joint.insert_geometry','record','mixed-record',[]),
        ('joint.compliance_law','record','mixed-record',[]),('joint.removal_and_retention','record','mixed-record',[])]:
        add(name,'joints',kind,unit,examples=examples,dependencies=['material.adhesive_grade','material.fastener_grade'],
            effects=['geometry-and-hardware-inventory','joint-slip-bearing-peel-fatigue','body-stiffness-and-modes','assembly-inspection-repair'],
            compatibility=['actual six-axis load path and calibrated preload/contact/slip','structural joints distinct from removable service clips'])
    for name,kind,unit,examples in [
        ('runninggear.layout','identifier','1',['two bogies/car','shared articulated bogies','alternative passive support']),
        ('runninggear.bogie_spacing_m','number','m',[10.,12.8,14.]),('runninggear.axle_positions','sequence','m',[]),
        ('runninggear.wheel_diameter_m','number','m',[.68,.76]),('runninggear.frame_material','identifier','1',['steel','aluminium research']),
        ('runninggear.suspension','record','mixed-record',[]),('runninggear.driven_axles','integer','1',[0,2,4]),
        ('runninggear.bearing_and_brake_layout','record','mixed-record',[])]:
        add(name,'runninggear',kind,unit,examples=examples,effects=['runninggear-geometry-and-mass','body-support-reactions','axle-loads-and-wheel-rail-dynamics','curve-and-swept-clearance','braking-and-rescue','civil','maintenance'],
            compatibility=['wheel-rail contact, alignment, curves and suspension travel','changed support positions need actual load paths and new physical component identity'])
    for name,kind,unit,examples in [
        ('motor.topology','identifier','1',['double-sided LIM','single-sided LIM','passive reluctance','onboard wheel traction']),
        ('motor.pole_pitch_m','number','m',[.2,.3,.5]),('motor.tooth_backiron_geometry','record','mixed-record',[]),
        ('motor.winding_layout','record','mixed-record',[]),('motor.conductor_area_m2','number','m2',[]),
        ('motor.fin_geometry','record','mixed-record',[]),('motor.gap_m','number','m',[.015,.020]),
        ('motor.cooling_layout','record','mixed-record',[]),('motor.inverter_configuration','record','mixed-record',[]),
        ('motor.section_locations','sequence','m',[]),('motor.onboard_energy_store','record','mixed-record',[])]:
        existing=name not in ('motor.onboard_energy_store','motor.inverter_configuration','motor.cooling_layout')
        add(name,'propulsion',kind,unit,examples=examples,dependencies=['material.electrical_steel_grade','material.conductor_grade'],
            effects=['primary-secondary-geometry','mass-and-guideway-loads','nonlinear-moving-force-and-loss-map','current-voltage-and-heat','section-handoff-and-protection','journey-and-station-power','cost-and-maintenance'],
            compatibility=['topology-specific current paths and finite overlap','real moving mechanical gap, normal forces, inverter and material-domain limits'],
            support='definition-generator-only' if existing else 'new-adapter-required',
            adapter='engineering.design_search.propulsion_families:expanded_plan' if existing else None,
            note='Existing single-fin finite2D research support is not a validated adapter for arbitrary topology, steel, overlap, circuit or thermal duty')
    for name,unit,examples in [('motor.current_A','A',[]),('motor.frequency_Hz','Hz',[]),('motor.slip','1',[])]:
        add(name,'propulsion','number',unit,scope='operational',examples=examples,
            effects=['force-map-operating-point','current-voltage-thermal-duty','power-and-journey','control-and-protection'],
            compatibility=['inverter/coil/material numerical and measured domain','current cannot compensate for invalid magnetic material formulation'])
    for name,kind,unit,examples in [
        ('brake.disc_geometry','record','mixed-record',[]),('brake.actuator_distribution','record','mixed-record',[]),
        ('brake.independent_channels','integer','1',[2,3,4]),('brake.parking_and_recovery','record','mixed-record',[])]:
        add(name,'braking',kind,unit,examples=examples,effects=['hardware-inventory','axle-load-and-adhesion','stopping-and-fault-envelope','thermal-duty','ATP-authority','maintenance'],
            compatibility=['independent safe stopping and parking remain obligations','validated adhesion/WSP, thermal fade and channel-loss performance'])
    for name,kind,unit,examples in [
        ('fitout.seat_bench_geometry','record','mixed-record',[]),('fitout.seat_mounts','record','mixed-record',[]),
        ('fitout.door_count_sides','record','mixed-record',[]),('fitout.door_leaf_and_drive','record','mixed-record',[]),
        ('fitout.glazing_thickness_m','number','m',[]),('fitout.glazing_retention','record','mixed-record',[]),
        ('fitout.floor_panel','record','mixed-record',[]),('fitout.roof_panel','record','mixed-record',[]),
        ('fitout.solar_mounts_and_sealing','record','mixed-record',[])]:
        add(name,'fitout',kind,unit,examples=examples,effects=['installed-geometry-mass-CG-inertia','local-structure-and-retention','thermal-fire-acoustic','accessibility-egress-door-operation','assembly-removal-and-maintenance'],
            compatibility=['actual passenger protection and accessible routes','replacement, thermal expansion, seals and retained openings'])
    for name,kind,unit,examples in [
        ('services.HVAC_architecture','identifier','1',['packaged modules','distributed modules','integrated ducts']),
        ('services.HVAC_routes','record','mixed-record',[]),('services.insulation_and_solar_control','record','mixed-record',[]),
        ('services.auxiliary_battery','record','mixed-record',[]),('services.cooling_and_wiring','record','mixed-record',[])]:
        add(name,'services',kind,unit,examples=examples,effects=['installed-equipment-and-power','50C-stationary-thermal-duty','fire-and-drainage','emergency-endurance','charging-and-headway','maintenance'],
            compatibility=['actual delivered capacity and ventilation at climate/load','redundancy, service access and essential power reserve'])
    for name,kind,unit,examples in [
        ('service.formation_cars','integer','1',[4,6,8]),('service.passengers_per_car','integer','1',[46,80,120]),
        ('service.seating_layout','record','mixed-record',[]),('service.speed_m_s','number','m/s',[12.,16.,20.]),
        ('service.acceleration_m_s2','number','m/s2',[.25,.3,.4]),('service.headway_s','number','s',[80.,120.,160.]),
        ('service.dwell_s','number','s',[25.,35.,45.]),('service.station_spacing_m','number','m',[1500.,2000.,3000.]),
        ('service.powered_zone_positions','sequence','m',[]),('service.recovery_strategy','identifier','1',['protected tow','creep drive','onboard traction'])]:
        add(name,'operations',kind,unit,scope='physical' if name in ('service.formation_cars','service.seating_layout','service.station_spacing_m','service.powered_zone_positions','service.recovery_strategy') else 'operational',
            examples=examples,effects=['route-and-station-geometry','passenger-load-and-service-capacity','vehicle-mass-and-civil','force-energy-journey','ATP-stopping-headway','fleet-and-power','access-time-and-economics'],
            compatibility=['changed admission does not delete crowd/emergency checks','equal offered service, accessibility, actual protected headway and city-specific access'],
            support='definition-generator-only',adapter='engineering.design_search.railway_architecture:generate',
            note='Analytical architecture-demand comparisons exist at inherited accounted mass, not verified new installed mass or available-force journeys')
    for name,kind,unit,examples in [
        ('civil.section_family','identifier','1',['box','twin beam','U beam','integrated rail section']),
        ('civil.span_m','number','m',[15.,20.,25.]),('civil.concrete_and_prestress','record','mixed-record',[]),
        ('civil.rail_fastening_layout','record','mixed-record',[]),('civil.pier_foundation','record','mixed-record',[]),
        ('civil.containment_and_access','record','mixed-record',[])]:
        add(name,'civil',kind,unit,examples=examples,effects=['moving-axle-loads-and-torsion','site-foundations-and-seismic','precast-lifts-and-erection','rail-alignment','station-power-support','installed-cost-and-maintenance'],
            compatibility=['actual geotechnical/site and load data','track gauge, drainage, thermal movement and derailment containment'],
            support='definition-generator-only',adapter='engineering.station_rail.civil:alternative',note='Longitudinal analytical sections only; complete foundation, torsion, dynamic and construction qualification absent')
    for name,domain,examples in [
        ('station.platform_and_berths','station',[]),('station.transfer_access','station',[]),
        ('manufacturing.process','manufacturing',['extrusion','pultrusion','infusion','bonded modular assembly','formed sheet']),
        ('manufacturing.joining_sequence','manufacturing',[]),('manufacturing.transport_erection','manufacturing',[]),
        ('maintenance.module_replacement','maintenance',[]),('maintenance.recovery_resources','maintenance',[])]:
        add(name,domain,'record' if not examples else 'identifier','mixed-record' if not examples else '1',examples=examples,
            effects=['geometry-interfaces-and-tolerances','tools-labour-supplier-coverage','assembly-inspection-removal','availability-and-whole-life-cost'],
            compatibility=['complete physical access, process tolerances and inspected load paths','unknown price, lead time, labour and failure rate remain unknown'])
    for name,kind,unit,examples in [
        ('model.mesh_settings','record','mixed-record',[]),('model.material_law','identifier','1',['source-bound nonlinear law']),
        ('model.contact_joint_law','record','mixed-record',[]),('model.solver_time_step_s','number','s',[]),
        ('model.material_temperature_data','record','mixed-record',[]),('model.provisional_stiffness_target_m','number','m',[.0256])]:
        add(name,'model',kind,unit,scope='model-assumption',examples=examples,
            effects=['evaluation-identity-and-cache','numerical-validity','criterion-provenance-and-uncertainty','independent-confirmation'],
            compatibility=['model changes cannot alter a physical identity unless physical inputs change','provisional target review cannot weaken an established functional/safety limit'],
            support='evaluation-only',note='An evaluation/assumption change requires a new evaluation/criterion revision and justification; no physical improvement or acceptance inferred')
    value=dict(schema=SCHEMA,revision='ADAPTIVE-VARIABLES-1',source_sha256=source_map(),variables={r['id']:r for r in records},
        extensible=True,complete_universal_design_space_claimed=False,
        support_warning='A named variable is not proof that its generator, material data or native evaluator exists. Unsupported changes create bounded implementation/validation tasks.',
        selected_development_default_changed=False,**FLAGS)
    value['registry_id']=identity(value);return value


def register(row,registry=None):
    """Return a new immutable registry with a validated extension descriptor."""
    value=deepcopy(_checked_registry(catalogue() if registry is None else registry))
    row=validate_descriptor(row)
    if row['id'] in value['variables']:raise ValueError('Existing variable requires an explicit new registry revision, not silent replacement')
    value['variables'][row['id']]=row;value.pop('registry_id');value['registry_id']=identity(value);return value


def validate_changes(changes,registry=None):
    """Validate concrete definition values; never automatically admit a solver."""
    registry=_checked_registry(catalogue() if registry is None else registry)
    if not isinstance(changes,dict) or not changes:raise ValueError('Explicit variable changes required')
    scopes={s:[] for s in SCOPES};effects=set();compatibility=set();adapters=[]
    for name,value in changes.items():
        if name not in registry['variables']:raise ValueError('Register the new variable and its consequences first: '+name)
        d=registry['variables'][name];kind=d['kind'];numeric=isinstance(value,(float,int)) and not isinstance(value,bool)
        if kind in ('number','integer'):
            if not numeric or not isfinite(value) or kind=='integer' and not isinstance(value,int):raise ValueError('Finite typed number required: '+name)
            low=d['trial_bounds']['minimum'];high=d['trial_bounds']['maximum']
            if low is not None and value<low or high is not None and value>high:raise ValueError('Outside declared campaign trial bounds: '+name)
        elif kind=='identifier' and (not isinstance(value,str) or not value.strip()):raise ValueError('Explicit grade/family identifier required: '+name)
        elif kind=='sequence' and (not isinstance(value,list) or not value):raise ValueError('Non-empty explicit sequence required: '+name)
        elif kind=='record' and (not isinstance(value,dict) or not value):raise ValueError('Non-empty explicit record required: '+name)
        elif kind=='boolean' and not isinstance(value,bool):raise ValueError('Boolean required: '+name)
        json.dumps(value,allow_nan=False)
        scopes[d['identity_scope']].append(name);effects.update(d['invalidates']);compatibility.update(d['requires_compatibility'])
        adapters.append(dict(variable=name,**d['model_support']))
    row=dict(schema='osr-variable-change-contract/1',registry_id=registry['registry_id'],changes=deepcopy(changes),
        identity_scopes=scopes,physical_identity_must_change=bool(scopes['physical']),
        requirement_or_operation_revision_required=bool(scopes['operational']),
        evaluation_identity_must_change=True,affected_outputs=sorted(effects),compatibility_checks=sorted(compatibility),
        adapter_requirements=adapters,automatic_native_dispatch=False,physical_performance_estimate=None,**FLAGS)
    row['change_contract_id']=identity(row);return row
