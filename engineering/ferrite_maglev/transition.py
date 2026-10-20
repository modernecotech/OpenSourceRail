"""Exhaustive source-identity migration obligations for the primary ferrite family.

This is an allocation register. It creates no drawings, production ERP records,
accepted supplier data, qualified controls or physical test evidence.
"""
from collections import Counter
from copy import deepcopy
import gzip
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(__file__).parent / 'data' / 'transition-plan.json'
GRAPH = ROOT / 'docs/design-engine/baghdad-digital-twin-2026-10-17/specifications.json.gz'
REFERENCE = ROOT / 'engineering/data/baghdad-reference-parts.json'
SCOPE = ROOT / 'engineering/generative_design/data/system-scope.json'
SPEC = ROOT / 'OpenSourceRail_Ferrite_Maglev_Rework_Specification.md'
FLAGS = dict(design_complete=False, physical_validation=False, manufacturing_release=False, physical_release=False)
WORK_PACKAGES = (
    'requirements-profile', 'magnetic-cad', 'magnetic-force-loss', 'vehicle-mass',
    'civil-kit', 'rust-support-control', 'coupled-dynamics', 'sbc-io-timing',
    'switch-free-city', 'local-mbom-cost', 'rig-and-demonstrator',
)
DISPOSITIONS = {'replace', 'redesign', 'retain-shared-with-interface-revalidation', 'retire-wheel-specific'}


def _profile(disposition, requirements, packages, deliverables, evidence):
    return dict(disposition=disposition, requirement_ids=requirements.split(),
                work_package_ids=packages.split(), new_deliverables=deliverables,
                engineering_evidence_needed=evidence)


PROFILES = {
    'running-gear-retirement': _profile('retire-wheel-specific',
        'SYS-004 MAG-054 OPS-004', 'magnetic-cad vehicle-mass coupled-dynamics local-mbom-cost rig-and-demonstrator',
        ['Wheel/bogie/axle-specific design and purchase scope retirement with preserved comparator identity',
         'Replacement allocation for magnetic support/guidance, capture, emergency braking, parking and recovery',
         'Removed maintenance/spares and replacement cartridge maintenance comparison'],
        ['No double-counted cost/mass deletion; replacement support, brake and recovery loads and energy paths',
         'G1–G5 replacement tests, measured reliability/repair time and approved retirement impact assessment']),
    'capture-redesign': _profile('redesign', 'SYS-004 PWR-003 PWR-004 OPS-003 MAG-054',
        'magnetic-cad coupled-dynamics sbc-io-timing rig-and-demonstrator local-mbom-cost',
        ['Fixed capture/support/parking/emergency braking assembly, load path and friction/thermal energy budget',
         'Suspension-aware stop, independent protection power and damaged-vehicle recovery interface'],
        ['Hazard-derived stopping/capture sequence and limits, all-speed/grade/battery-full energy path',
         'Measured support, brake, retention and recovery tests under credible combined faults']),
    'propulsion-replacement': _profile('replace', 'SYS-003 SYS-004 MAG-040 MAG-041 MAG-042 MAG-043 MAG-044 PWR-003',
        'magnetic-cad magnetic-force-loss vehicle-mass rust-support-control local-mbom-cost',
        ['Onboard linear propulsion topology decision and separately controllable winding/core CAD',
         'External reaction interface, thrust/lift/drag/loss maps and regeneration/dump-braking paths'],
        ['Nonlinear force/loss maps, hot continuous-current/thermal limits and passive-rail material tests',
         'Total ferrite/iron/copper/carrier mass ledger without shared-volume credit before proof']),
    'body-redesign': _profile('redesign', 'SYS-001 SYS-007 MASS-001 GEO-001 GEO-002 GEO-003 MFG-001 MAG-033',
        'magnetic-cad vehicle-mass coupled-dynamics local-mbom-cost',
        ['17 m structural frame, beam intrusion, floor, equipment and positive-retention interface drawings',
         'New load paths, structural joints, swept/service envelopes and component mass/CG/inertia ledger'],
        ['Crash/fatigue/thermal loads, flexible-body FEA, released material/process allowables and tolerance stack',
         'Weighed first article, retention after crack/debond and independent exact-revision acceptance']),
    'shared-passenger': _profile('retain-shared-with-interface-revalidation', 'SYS-001 MFG-001 OPS-005 GEO-001 MASS-001',
        'vehicle-mass coupled-dynamics switch-free-city local-mbom-cost',
        ['Passenger-function continuity and revised mount/clearance/service-access interface pack',
         'Supplier-neutral door/glazing/interior/lighting configuration with revised mass and fire obligations'],
        ['17 m car/beam section, accessibility/egress/fire/EMC/load interface revalidation',
         'Actual configured supplier data, installed mass, first-article fit and door/platform tests']),
    'train-interface': _profile('redesign', 'SYS-001 GEO-001 MASS-001 OPS-003 OPS-005',
        'magnetic-cad vehicle-mass coupled-dynamics switch-free-city rig-and-demonstrator',
        ['Coupler/gangway/jumper and train-end drawings for 17 m rigid cars and declared consist',
         'Rescue load paths, crash/anti-lift interfaces and articulation/charging mechanism disclosure'],
        ['Consist pitch/length, curve/end sweep, rescue/coupling/braking loads and six-car capacity reconciliation',
         'Instrumented multi-car, emergency egress and recovery acceptance evidence']),
    'battery-thermal': _profile('redesign', 'SYS-010 MASS-001 PWR-001 PWR-002 PWR-003 PWR-004 MAG-044',
        'vehicle-mass magnetic-force-loss switch-free-city sbc-io-timing local-mbom-cost',
        ['Matched 225 kWh/car and separate 150 kWh option electrical/thermal BOM and energy paths',
         'Protected support supply, charge interfaces, cooling and hot/EOL/missed-charge duty model'],
        ['Cells/BMS voltage/current/charge limits, cooling data, fire/EMC qualification and actual auxiliary loads',
         'Route duty, no-regen/full-SOC/failed-channel tests and hazard-derived protected reserve']),
    'controls-protection': _profile('redesign', 'CTL-001 CTL-002 CTL-003 CTL-004 CTL-005 CTL-006 CTL-007 PWR-004',
        'rust-support-control sbc-io-timing coupled-dynamics rig-and-demonstrator',
        ['Rust/SBC supervision and local control architecture with independent protection and isolated physical I/O',
         'Gap/current/force/temperature/odometry contracts, calibration and support-aware fault actions'],
        ['Measured target deadlines/jitter, sensor bias/quality/staleness, validated actuator maps and hardware faults',
         'Independence/common-cause analysis, permitted-movement invariants and G2–G5 physical correlation']),
    'civil-guideway': _profile('redesign', 'CIV-001 CIV-002 CIV-003 CIV-005 CIV-006 CIV-007 GEO-001 GEO-002',
        'civil-kit magnetic-cad magnetic-force-loss coupled-dynamics local-mbom-cost',
        ['Passive functional faces/capture/adjustment interface and narrow-beam/support/erection drawing pack',
         'Dual-direction BoQ including end details, reinforcement/prestress, bearings, joints and metrology'],
        ['Actual magnetic rail kg/m, B-H/loss/material data, local opposing magnetic/capture forces and rail tests',
         'Wind/seismic/lateral/torsional/fatigue/geotechnical analysis and coupled local-gap acceptance']),
    'evacuation-station': _profile('redesign', 'CIV-004 OPS-003 OPS-005 GEO-001 GEO-002',
        'civil-kit switch-free-city coupled-dynamics local-mbom-cost rig-and-demonstrator',
        ['Platform/door/protection/disabled evacuation cross-sections through normal and captured states',
         'Retained walkway comparator versus integrated-beam/onboard evacuation target; alternatives require independent egress/fire/rescue acceptance'],
        ['Swept envelope and load-dependent floor height; safe landing/accessibility/assistance, weather, fire/fault and responder/maintenance access proof',
         'Operator-approved egress limits, constrained-section evacuation and recovery demonstration']),
    'station-shared': _profile('retain-shared-with-interface-revalidation', 'CIV-001 CIV-004 OPS-002 OPS-005 MFG-005',
        'civil-kit switch-free-city local-mbom-cost',
        ['Station/access/canopy/services quantity and configuration crosswalk for equal transport capacity',
         'Revalidated interfaces for loads, charging/grid, earthing, fire, passenger systems and maintenance'],
        ['Site/platform/consist requirements, surveyed interfaces, supplier data and first-article checks',
         'Station electrical simultaneous-arrival duty and commissioning evidence where applicable']),
    'depot-routing': _profile('replace', 'SYS-008 OPS-001 OPS-002 OPS-003 OPS-004',
        'switch-free-city civil-kit rust-support-control local-mbom-cost rig-and-demonstrator',
        ['Mainline turnout scope removed from candidate route; depot-only magnetic switching exception recorded',
         'Explicit loop/shuttle alternatives, terminal footprints, dispatch and blocked-line recovery model',
         'Depot guidance/switch/capture/interlocking design; old wheel turnout geometry is inapplicable'],
        ['Accepted no-mainline-switch topology and capacity/fleet/timetable/land study',
         'Qualified depot mechanism, detection/locking/protection and failed-car recovery demonstration']),
    'depot-maintenance': _profile('redesign', 'OPS-003 OPS-004 MFG-002 MFG-003 MFG-004 MFG-005',
        'local-mbom-cost switch-free-city civil-kit rig-and-demonstrator',
        ['Magnet-handling/support stands, retained-cartridge service and field/gap/current calibration layout',
         'Wheel-service retirement separated from retained cranes, lifting, wash, rescue and workshop functions'],
        ['Actual assembly/removal paths, tooling capacities, handling risk, calibration and observed repair time',
         'First-article workshop process, repaired serial traceability and recovery trials']),
    'factory-equipment': _profile('retain-shared-with-interface-revalidation', 'SYS-009 MFG-002 MFG-003 MFG-004 MFG-005 OPS-004',
        'local-mbom-cost magnetic-cad civil-kit rig-and-demonstrator',
        ['Configured equipment capability review for new body/cartridge/winding/rail processes',
         'Fixture/gauge/control plan and new equipment-gap/RFQ list with no inherited capacity claim'],
        ['Actual machine envelope, load/force/power limits, tools, cycle time, fixtures and calibration records',
         'Supplier capability audit, process qualification, yield and measured first-article routing']),
    'factory-industrialisation': _profile('redesign', 'SYS-009 MFG-001 MFG-002 MFG-003 MFG-004 MFG-005',
        'local-mbom-cost magnetic-cad civil-kit rig-and-demonstrator',
        ['Magnet/core/winding/cartridge/rail make-buy plan, factory flows, handling, utilities and test stations',
         'Origin-traced EBOM/MBOM, routing, travellers, spare/repair plan and separate recurring/NRE budget'],
        ['Configured equipment/site/facility capacities, process qualification and real supplier/input origins',
         'Released drawings, labour/yield/rework/scrap, actual prices and measured production rates']),
    'system-requirements': _profile('redesign', 'SYS-001 SYS-003 SYS-004 SYS-005 SYS-008 SYS-009 SYS-010 MASS-001',
        'requirements-profile vehicle-mass civil-kit switch-free-city local-mbom-cost',
        ['New architecture/load/environment/consist/profile and source-linked acceptance baseline',
         'All-variant mass/force/cost/energy and exact-revision evidence crosswalk; comparator retained'],
        ['Operator/design-authority approved service/route/load/standards and configuration responsibilities',
         'Unresolved force maps, CAD, source qualifications and physical tests remain open']),
    'system-assurance': _profile('redesign', 'MAG-050 MAG-051 MAG-052 MAG-053 MAG-054 MAG-055 CTL-005 CIV-005',
        'requirements-profile coupled-dynamics sbc-io-timing rig-and-demonstrator',
        ['Architecture-specific RAMS/hazard/FMEA/standards and integration verification matrix',
         'G0–G5 plan with limits fixed before testing, independent correlation and authenticated acceptance'],
        ['Grade/force maps, target hardware, guideway and train physical tests for exact configuration',
         'Independent assessment, closed NCRs and signed acceptance; old wheel evidence does not transfer']),
}

# Planned new engineering BOM objects. Quantities and specifications are outputs
# of design, not invented as a side effect of assigning migration coverage.
NEW_OBJECTS = (
    ('FM-FERRITE', 'Grade-controlled hard-ferrite blocks', 'factory-industrialisation'),
    ('FM-CARTRIDGE', 'Retained, keyed, replaceable ferrite cartridge', 'body-redesign'),
    ('FM-CORE', 'Lift/guidance/propulsion poles and magnetic cores', 'propulsion-replacement'),
    ('FM-LIFT-WINDING', 'Onboard lift stabilisation winding', 'propulsion-replacement'),
    ('FM-GUIDANCE-WINDING', 'Onboard short guidance winding', 'propulsion-replacement'),
    ('FM-THRUST-WINDING', 'Onboard linear propulsion winding', 'propulsion-replacement'),
    ('FM-INVERTER', 'Module current driver/inverter and DC link', 'controls-protection'),
    ('FM-SENSOR', 'Independent gap/current/temperature sensing', 'controls-protection'),
    ('FM-PROTECTION', 'Independent support-aware protection channel', 'controls-protection'),
    ('FM-SUPPORT-POWER', 'Protected support/protection power domain', 'battery-thermal'),
    ('FM-MAGNET-COOLING', 'Magnetic assembly cooling and services', 'battery-thermal'),
    ('FM-CAPTURE', 'Fixed capture/landing/parking/emergency-brake system', 'capture-redesign'),
    ('FM-ODOMETRY', 'Contactless odometry and guideway markers', 'controls-protection'),
    ('FM-REACTION-RAIL', 'Passive lift/guidance/propulsion reaction surfaces', 'civil-guideway'),
    ('FM-RAIL-MOUNT', 'Adjustable replaceable rail mounting cassette', 'civil-guideway'),
    ('FM-GUIDEBOX', 'New guidebox including end details and reinforcement', 'civil-guideway'),
    ('FM-WALKWAY', 'Walkway/bracket comparator; removal conditional on accepted alternative evacuation', 'evacuation-station'),
    ('FM-ONBOARD-EVACUATION', 'Door-mounted spiral-chute candidate with variable-height outlet, structural entry, driverless assistance, inspection and accessible alternative', 'evacuation-station'),
    ('FM-MAGNET-FIXTURE', 'Controlled retained-magnet assembly fixture', 'factory-industrialisation'),
    ('FM-WINDING-FIXTURE', 'Winding/impregnation/insulation test fixtures', 'factory-industrialisation'),
    ('FM-FIELD-RIG', 'Force/gap/field/thermal end-of-line test station', 'factory-industrialisation'),
    ('FM-METROLOGY', 'Guideway surface/gap and installed datum metrology', 'factory-industrialisation'),
    ('FM-DEPOT-SERVICE', 'Safe support, cartridge removal and calibration equipment', 'depot-maintenance'),
)

COMMON_EVIDENCE = (
    'Released exact-revision material/grade/finish and qualified process specification',
    'Dimensioned native drawings, datums/tolerances, installation/removal envelope and approved ICD',
    'Origin/supplier/cost and make-buy evidence for every input; local assembly is not material origin',
    'Revision-compatible EBOM/MBOM/routing/traveller and configured equipment/fixture/calibration evidence',
    'Inspection plan, acceptance limits, measured first article, NCR closure and installed serial trace',
    'Independent exact-revision acceptance; allocation is not design completion or release',
)
OPEN_FIELDS = (
    'material_grade', 'material_source', 'material_certificate', 'drawing_revision', 'native_drawing',
    'configured_equipment', 'qualified_process', 'fixture_revision', 'supplier', 'country_of_origin',
    'imported_input_usd', 'finished_value_usd', 'local_operation_cost_usd', 'labour_hours',
    'yield_fraction', 'scrap_fraction', 'inspection_result', 'calibration_certificate',
    'first_article_record', 'physical_test_record', 'installed_serial', 'accepted_by',
)


def _read(path):
    data=path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def _digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _unique(records, key, label):
    values=[r[key] for r in records]
    if len(set(values)) != len(values):
        raise ValueError('duplicate '+label)
    return set(values)


def _equal(actual, expected, label):
    actual=set(actual);expected=set(expected)
    if actual != expected:
        raise ValueError(label+' differs; missing='+str(sorted(expected-actual))+
                         '; unexpected='+str(sorted(actual-expected)))


def _collection(data, expression):
    values=[data]
    for part in expression.split('.'):
        flatten=part.endswith('[]'); key=part[:-2] if flatten else part
        values=[child for value in values for child in (value[key] if flatten else [value[key]])]
    return [record for value in values for record in (value if isinstance(value,list) else [value])]


def _source_inventory(plan):
    if plan.get('schema')!='osr-ferrite-maglev-transition-plan/1':
        raise ValueError('explicit transition plan schema required')
    graph=_read(GRAPH); reference=_read(REFERENCE); scope=_read(SCOPE)
    for path in (GRAPH, REFERENCE, SCOPE, SPEC):
        if sha256(path.read_bytes()).hexdigest() != plan['inventory_sha256'][path.relative_to(ROOT).as_posix()]:
            raise ValueError('transition inventory changed; explicit disposition reconciliation required: '+str(path.relative_to(ROOT)))
    graph_ids=_unique(graph['items'],'id','canonical source identity')
    baghdad_ids=_unique(reference['parts'],'id','Baghdad source identity')
    _equal(graph_ids, plan['items'], 'canonical item disposition coverage')
    _equal(('baghdad:'+i for i in baghdad_ids), plan['baghdad_items'], 'Baghdad disposition coverage')
    graph_packages=_unique(graph['packages'],'id','canonical package identity')
    _equal(graph_packages, plan['packages'], 'legacy package disposition coverage')
    _equal(graph_packages, (p['id'] for p in scope['work_packages']), 'source scope packages')
    for row in scope['source_inventory']:
        path=ROOT/row['path']
        if sha256(path.read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('authoritative source hash changed: '+row['path'])
        for coll in row['inventory_collections']:
            ids={r[coll['id_field']] for r in _collection(_read(path),coll['collection'])}
            _equal(ids,coll['expected_ids'],'authoritative collection '+row['path']+':'+coll['collection'])
            allocated={i for p in scope['work_packages'] for s in p['authoritative_sources']
                       if s['path']==row['path'] for i in s['ids']}
            if not ids <= allocated: raise ValueError('unallocated authoritative source identities: '+row['path'])
    for item in graph['items']:
        if sha256((ROOT/item['source']).read_bytes()).hexdigest()!=item['source_sha256']:
            raise ValueError('canonical item source hash changed: '+item['source'])
        if not set(item['package_ids']) <= graph_packages:raise ValueError('unknown legacy package')
    return graph,reference,scope


def _capability_paths():
    paths=[ROOT/'engineering/ferrite_maglev'/name for name in ('geometry.py','field.py','coupled.py','evacuation.py','evacuation.toml','optimisation.py','optimisation.toml')]
    paths += [ROOT/'engineering/factory_examples/native.py',ROOT/'engineering/factory_examples/models.py',
              ROOT/'engineering/analysis/tests/test_ferrite_maglev_geometry_field.py',
              ROOT/'engineering/analysis/tests/test_ferrite_maglev_coupled.py',
              ROOT/'engineering/analysis/tests/test_ferrite_maglev_evacuation.py',
              ROOT/'crates/osr-maglev-control/Cargo.toml']
    paths += sorted((ROOT/'crates/osr-maglev-control').rglob('*.rs'))
    return paths


def capability_availability():
    """Implemented numerical/native subsets; execution receipts never close gates."""
    from . import geometry
    native_paths=['engineering/ferrite_maglev/geometry.py','engineering/factory_examples/native.py',
                  'engineering/factory_examples/models.py','engineering/analysis/tests/test_ferrite_maglev_geometry_field.py']
    rust_paths=[p.relative_to(ROOT).as_posix() for p in _capability_paths()
                if 'osr-maglev-control' in p.parts]
    definitions=[
        ('native-development-solids',native_paths,
         ['SYS-001','SYS-007','MASS-001','GEO-001','GEO-002','GEO-003','CIV-001','CIV-002','CIV-003','CIV-004','CIV-006','MFG-001','MFG-005','MAG-033','MAG-034'],
         ['magnetic-cad','vehicle-mass','civil-kit'],
         ['geometry.interface(variant="recessed-retainer") and geometry.civil_bay() generate dimensioned material regions and part identities',
          'geometry.publish_native(output) invokes actual FreeCAD solid construction, FCStd/STEP export and reopening/identity/interference checks',
          'Flat-retainer and recessed-retainer geometry alternatives expose nominal fastener clearances and separate material ledgers'],
         ['Exact exported variant and successful checks require the source-bound native receipt; geometry availability does not assert that an export ran',
          'Default geometry uses supplier-ground ferrite edge recesses; crack/demagnetisation/process/fastener/retention qualification remains open',
          'Partial interface/frame and civil envelopes omit full cabin systems, functional propulsion, structural joints, reinforcement and qualified foundations',
          'Nominal 8 mm head clearance is not an accepted error budget, crash/fatigue/load case or physical manufacture']),
        ('two-dimensional-field-hypothesis',
         ['engineering/ferrite_maglev/field.py','engineering/analysis/tests/test_ferrite_maglev_geometry_field.py'],
         ['MAG-010','MAG-011','MAG-020','MAG-021','MAG-030','MAG-031','MAG-040','MAG-041','MAG-042','MAG-043','MAG-050','MAG-051'],
         ['magnetic-force-loss'],
         ['Variable-reluctivity conservative finite-difference A_z solver with a manufactured sine PDE solution and second-order refinement controls',
          'Artificial nonlinear iron saturation hypothesis, air Maxwell-stress contours and coupon gap/temperature/current sensitivities'],
         ['Manufactured-solution error reduction near four verifies numerical order for that PDE test; it does not establish physical magnetic force',
          'Assumed ferrite recoil/Br and artificial iron law have no adopted supplier/material grade',
          'No 3D finite-end/winding circuit, vehicle force, speed-dependent rail/core loss or demagnetisation qualification',
          'Contour agreement and linear residuals require further mesh/domain/interface studies and independent physical correlation']),
        ('rust-multimodule-study',rust_paths,
         ['CTL-001','CTL-002','CTL-003','CTL-004','CTL-005','CTL-007','PWR-004','MAG-052','MAG-053','MAG-054'],
         ['rust-support-control','sbc-io-timing'],
         ['Rust 24-module force-allocation/current-control and support-aware fault policy with explicit I/O contracts',
          'Offline replay and Rust bridge accept bounded virtual sensor/plant states with independent logical protection modelling'],
         ['Rust execution/replay is not measured SBC WCET/latency/jitter or an isolated physical output adapter',
          'Ideal instantaneous actuator hypotheses have no qualified force/current/thermal maps',
          'Protection independence, physical common causes, sensors/power domains and actual capture/braking require hardware evidence']),
        ('two-way-beam-control-demonstrator',
         ['engineering/ferrite_maglev/coupled.py','engineering/analysis/tests/test_ferrite_maglev_coupled.py',*rust_paths],
         ['GEO-002','GEO-004','CIV-005','CTL-001','CTL-002','CTL-003','CTL-005','MAG-023','MAG-024','MAG-025','MAG-052','MAG-053'],
         ['coupled-dynamics','rust-support-control'],
         ['Two-way Python flexible-guideway/Rust 24-module controller numerical coupling at 1 ms virtual step',
          'Default 50-element pinned Euler-Bernoulli beam retains six vertical modes; reaction forces update beam movement and subsequent controller gaps',
          'Three-second virtual demonstrator and independent static point-load/beam numerical controls are available'],
         ['Stationary single rigid car and ideal instantaneous force channels; no qualified actual electromagnetic plant',
          'No torsion, soil/support dynamics, lateral beam flexibility, moving loads, train coupling, flexible carbody or local reaction-surface compliance',
          'Assumed stiffness/mass/damping are not structural/material release; virtual time is not measured hardware timing',
          'Numerical coupling does not establish all-axis stability, ride, complete fault acceptance or route service performance']),
    ]
    definitions.append(('beam-only-evacuation-research',
        ['engineering/ferrite_maglev/evacuation.py','engineering/ferrite_maglev/evacuation.toml',
         'engineering/ferrite_maglev/optimisation.py','engineering/analysis/tests/test_ferrite_maglev_evacuation.py'],
        ['CIV-004','OPS-003','OPS-005','GEO-001','GEO-002','MFG-005'],
        ['civil-kit','vehicle-mass','switch-free-city','local-mbom-cost','rig-and-demonstrator'],
        ['Integrated-beam/no-continuous-walkway material alternative, actual native export/reopening adapter and exact part-removal quantities',
         'Slide/chute clearance, discrete-outlet height counterexamples, driverless installation requirements and optimistic flow lower bounds; no pedestrian/device simulation',
         'Gross civil avoidance is separated from unknown added onboard mass/lifetime cost; held alternatives cannot replace reference research champions'],
        ['No approved alternative to CIV-004 reference walkway; constrained-route accessible evacuation and physical tests remain open',
         'Necessary ferromagnetic reaction faces, supports/foundations, connections, rescue and maintenance access remain',
         'Safe landing at every stop position, fire/wind/heat/fault/assistance, measured flow and supplier device acceptance unproved']))
    records=[]
    for identity,paths,reqs,packages,available,holds in definitions:
        records.append(dict(id=identity,state='implemented-bounded-development-capability',available=True,
            source_sha256={path:sha256((ROOT/path).read_bytes()).hexdigest() for path in sorted(set(paths))},
            requirement_ids=reqs,work_package_ids=packages,available_scope=available,
            evidence_needed=holds,execution_receipt=None,physical_tests_performed_by_this_register=False,
            closes_acceptance_gate=False,accepted=False,**FLAGS))
    native=records[0]
    native['geometry_variants']=[dict(variant=variant,
        planned_solid_count=len(definition['parts']),
        nominal_magnet_gap_m=definition['clearances']['nominal_magnet_to_lift_face_m'],
        nominal_fastener_head_gap_m=definition['clearances']['bolt_head_to_face_m'],
        full_error_budget_accepted=False,exact_export_receipt=None)
        for variant in ('flat-retainer','recessed-retainer') for definition in [geometry.interface(variant)]]
    return records


def sources():
    """All migration source paths and live hashes for the parent's source receipt."""
    scope=_read(SCOPE);graph=_read(GRAPH)
    paths={DATA,GRAPH,REFERENCE,SCOPE,SPEC,Path(__file__),Path(__file__).parent/'model.py',
           ROOT/'engineering/assembly_design/baseline.py',
           ROOT/'engineering/analysis/tests/test_ferrite_maglev_transition.py',
           ROOT/'services/integration/osr_integration/manufacturing.py',
           ROOT/'services/integration/osr_integration/engineering.py',
           ROOT/'services/integration/osr_integration/store.py',
           ROOT/'services/integration/osr_integration/fuxa.py',
           ROOT/'services/integration/osr_integration/embedded.py',
           ROOT/'deployment/supervision/config/generic.json'}
    paths.update(_capability_paths())
    paths.update(ROOT/i['source'] for i in graph['items'])
    paths.update(ROOT/p['source'] for p in _read(REFERENCE)['parts'])
    paths.update(ROOT/s['path'] for s in scope['source_inventory'])
    return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def _obligations(identity, profile_id):
    profile=PROFILES[profile_id]
    return dict(id='industrial:'+identity,transition_id=identity,
        state='engineering-obligation; production-import-blocked',profile_id=profile_id,
        disposition=profile['disposition'],requirement_ids=profile['requirement_ids'],
        work_package_ids=sorted(set(profile['work_package_ids'])|{'local-mbom-cost'}),
        routing_state='retirement-impact-review' if profile['disposition']=='retire-wheel-specific' else 'new-or-revalidated-routing-required',
        origin_basis='unknown until priced origin-traced inputs and supplier returns exist',
        local_value_added_fraction=None,actual_records={key:None for key in OPEN_FIELDS},
        evidence_needed=list(COMMON_EVIDENCE),accepted=False,**FLAGS)


def interfaces():
    """Migration contracts and commissioning obligations, never live bindings."""
    fields=[('gap','m'),('pole_overlap','m'),('current','A'),('estimated_force','N'),
            ('force_reserve','N'),('dc_bus_voltage','V'),('dc_bus_current','A'),
            ('magnet_temperature','degC'),('winding_temperature','degC'),
            ('rail_temperature','degC'),('capture_contact','boolean'),
            ('protection_energy','J'),('support_mode','enum'),('sensor_health','enum')]
    return dict(
        erp=dict(id='interface:erp-lifecycle',state='planned-not-imported',
            source_paths=['deployment/erpnext/apps/osr_erpnext/',
                          'services/integration/osr_integration/manufacturing.py',
                          'services/integration/osr_integration/engineering.py',
                          'services/integration/osr_integration/store.py'],
            requirement_ids=['MFG-002','MFG-003','MFG-004','MFG-005'],work_package_ids=['local-mbom-cost'],
            deliverables=['Separate preliminary engineering Items from production-released Items/BOMs',
                'Revision/hash-linked EBOM→MBOM→routing→work order→inspection→installed serial→maintenance/spares chain',
                'Ferrite batch/orientation/location, winding/firmware/calibration revision and repaired-module trace',
                'Real company, warehouse, operator, supplier and released priced family MBOM before production import'],
            actual_company=None,actual_warehouse=None,actual_operator=None,actual_supplier=None,
            production_import_authorized=False,local_value_added_fraction=None,
            evidence_needed=list(COMMON_EVIDENCE),accepted=False,**FLAGS),
        supervision=dict(id='interface:supervision',state='planned-not-commissioned',
            source_paths=['deployment/supervision/config/generic.json',
                          'services/integration/osr_integration/fuxa.py',
                          'services/integration/osr_integration/embedded.py','crates/osr-supervision-contract/'],
            requirement_ids=['CTL-003','CTL-004','CTL-005','CTL-006','CTL-007'],
            work_package_ids=['rust-support-control','sbc-io-timing','coupled-dynamics'],
            tags=[dict(name=name,unit=unit,lower_bound=None,upper_bound=None,
                       validity_limit_ms=None,source_binding=None,calibration_ref=None,
                       common_fields=['configuration_hash','vehicle_id','module_id','channel_id',
                                      'timestamp','sequence','quality','uncertainty','provenance'],
                       state='bounds-and-physical-binding-open') for name,unit in fields],
            boundary='FUXA displays/alarms/maintenance only; local suspension and independent protection do not depend on supervisory communications',
            deliverables=['Source-bound tag schema and versioned physical device mapping',
                'Derived limits/staleness/sensor-disagreement alarms and support-aware local fault matrix',
                'Target WCET/latency/jitter and lost-supervision tests; formal invariants with physical limits'],
            physical_bindings_commissioned=False,grants_movement_authority=False,closes_support_loop=False,
            evidence_needed=['Validated force/current/thermal bounds, hazard-derived validity limits and isolated I/O',
                'Target calibration, independent protection and controlled commissioning evidence'],accepted=False,**FLAGS))


WORK_PACKAGE_OUTPUTS = {
    'requirements-profile': (
        ['Accepted family/consist/service/environment baseline and architecture decision register',
         'Source-linked parameter, standards-applicability, hazard and acceptance-limit register'],
        ['Obtain operator/design-authority adoption and independent review of open thresholds']),
    'magnetic-cad': (
        ['Native dimensioned magnet/core/winding/carrier/rail and 17 m car interface definition',
         'Positive retention, polarity, maintenance envelope and tolerance/datum drawings'],
        ['Replace envelopes with engineered joints/materials; check crash/fatigue/thermal/clearance cases']),
    'magnetic-force-loss': (
        ['Revision-identified 2D/3D force/moment/stiffness/loss/thermal/demagnetisation maps',
         'Mesh/domain/refinement and independent force-method comparisons'],
        ['Obtain actual grade curves and rig correlation; numerical manufactured-solution checks do not validate vehicle force']),
    'vehicle-mass': (
        ['Component quantities, material/CAD/supplier mass, CG/inertia and support-position ledger',
         '3/4 t ferrite × 150/225 kWh variants with uncertainty and separate growth reserve'],
        ['Reconcile all covers/cables/cooling/retainers once; weigh exact-config first article']),
    'civil-kit': (
        ['Guidebeam/reaction surfaces/support/foundation/bearing/joint/walkway design and dual-route BoQ',
         'Erection/transport/metrology/replacement and relative-gap tolerance plans'],
        ['Resolve magnetic kg/m, lateral/torsional/geotechnical/temporary loads and physical rail alignment']),
    'rust-support-control': (
        ['Rust local support/current/force allocation with bounded support-aware fault actions',
         'Versioned sensing/actuator/odometry/supervisory contracts and protection invariants'],
        ['Use mapped actuator limits and independently reviewed hazards; correlate multi-module hardware faults']),
    'coupled-dynamics': (
        ['Flexible vehicle/guideway six-DOF and mode-coupled simulation with mapped actuators',
         'Curve/joint/wind/passenger/fault and sensor-delay/saturation response envelopes'],
        ['Derive ride/gap/failure limits, correlate structural modes and instrumented closed-loop tests']),
    'sbc-io-timing': (
        ['Exact SBC/I/O/power-isolation and independent protection implementation',
         'WCET/latency/jitter/staleness/calibration/diagnostic and fault-injection reports'],
        ['Measure target hardware with loaded communications and credible common causes; no timing inference from replay']),
    'switch-free-city': (
        ['Explicit loop/shuttle/depot topology, footprint, equal-capacity timetable/fleet/spares model',
         'Hot/EOL/no-regen/missed-charge energy, grid concurrency, access/egress and blocked-line recovery plan'],
        ['Obtain surveyed route and operator service requirements, demonstrate recovery and sustained route performance']),
    'local-mbom-cost': (
        ['Priced origin-traced EBOM/MBOM/BoQ/routings, drawings, fixtures, inspection and repair dossiers',
         'Supplier/make-buy/tooling/facility/capacity and recurring/NRE/imported-input comparison'],
        ['Collect actual supplier returns, material origin, process yield/time and first-article production records']),
    'rig-and-demonstrator': (
        ['G0–G5 calibrated rig/demonstrator procedures with predefined quantitative limits',
         'Raw data/configuration receipt, independent correlations, NCRs and authenticated gate decisions'],
        ['Perform instrumented physical tests, close deviations and obtain independent exact-revision acceptance']),
}


def validation_programme(requirement_ids):
    """Unperformed tests with threshold decisions required before execution."""
    gate_specs=[
        ('G0','Requirements, geometry and configuration', 'requirements/geometry review and surveyed route model',
         ['Freeze family/consist/load/environment and topology alternatives; run full 3D curve/crest/sag/twist sweep',
          'Review mass, cost, energy, interface, hazard and source inventories; name owners for all limits'],
         [('minimum_clearance','m','swept envelope, uncertainty and accepted collision/egress envelope'),
          ('minimum_route_radius','m','surveyed horizontal/vertical route fit and overlap budget'),
          ('required_capacity','passengers/hour/direction','operator service baseline at equal capacity')],
         list(requirement_ids), ['requirements-profile','magnetic-cad','switch-free-city']),
        ('G1','Material, winding and magnetic module rigs','coupon/block, coil bench and restrained static force/moment rig',
         ['Verify hard-ferrite grade/batch/axis/defects and temperature-dependent Br/Hc/recoil curves',
          'Inspect retention and winding build; perform insulation, resistance, inductance and cooling tests',
          'Map six-axis forces/moments versus gap/offset/current/temperature; compare independent force methods and solver predictions',
          'Test cold reverse-field demagnetisation, hot steady duty, leakage fields and retention after debond/crack'],
         [('force_map_error','fraction','independent correlation uncertainty required by control margin'),
          ('minimum_lift_force','N','governing AW3/asymmetric/fault/dynamic force allocation'),
          ('maximum_winding_temperature','degC','qualified insulation, cooling and material allowables'),
          ('demagnetisation_margin','A/m','supplier grade curves and worst reverse fields'),
          ('insulation_test_voltage','V','approved electrical insulation/test specification')],
         ['SYS-002','SYS-003','MFG-002','MFG-003','MFG-004','MAG-010','MAG-030','MAG-031','MAG-032','MAG-033','MAG-034','MAG-050','MAG-051'],
         ['magnetic-cad','magnetic-force-loss','local-mbom-cost','rig-and-demonstrator']),
        ('G2','Restrained multi-module stationary support','guarded multi-module loaded rigid/flexible rig with independent capture/support',
         ['Demonstrate zero-speed lift and guidance across AW0/AW2/AW3 and eccentric load',
          'Apply passenger steps, disturbances, sensor bias/loss/staleness, missing/short/open coil and stuck inverter faults',
          'Inject bus/protection-power interruption and lost supervision; measure redistribution, current/thermal saturation and safe support sequence',
          'Measure target SBC and I/O execution/latency/jitter during simultaneous fault/communications loads'],
         [('minimum_dynamic_gap','m','G0 tolerance budget and hazard analysis'),
          ('maximum_gap_tracking_error','m','force-gradient stability and disturbance budget'),
          ('maximum_fault_response_time','s','unstable mode growth and capture/support safe state'),
          ('maximum_target_latency','s','delay-robustness analysis and exact power/sensor hardware'),
          ('minimum_protected_support_energy','J','controlled-stop/hold/capture hazard-derived reserve')],
         ['SYS-005','SYS-006','GEO-002','GEO-004','PWR-004','CTL-001','CTL-002','CTL-003','CTL-004','CTL-005','CTL-007','MAG-020','MAG-021','MAG-022','MAG-023','MAG-024','MAG-025','MAG-052','MAG-053','MAG-054'],
         ['rust-support-control','coupled-dynamics','sbc-io-timing','rig-and-demonstrator']),
        ('G3','Moving sled and representative guideway','instrumented representative beam/rail, joints, curve and moving sled',
         ['Survey surface/datum/adjustment stack, joints and thermal offsets before dynamic runs',
          'Increase speed within an approved restrained test envelope; map propulsion/lift coupling, drag, ripple and passive-rail heating',
          'Measure relative magnet/rail gap, beam bending/twist, surface loss, contact/capture loads and joint faults',
          'Include debris/sand/water/corrosion/covers, reverse running and hot/weak-magnet cases'],
         [('maximum_rail_joint_step','m','coupled gap budget and manufactured alignment capability'),
          ('maximum_rail_loss','W/beam-m','measured energy/thermal and route duty allocation'),
          ('maximum_beam_relative_motion','m','coupled vehicle/guideway gap and protection margin'),
          ('maximum_rail_temperature','degC','qualified materials/joints, field map and maintenance envelope')],
         ['GEO-001','CIV-001','CIV-002','CIV-003','CIV-005','CIV-006','CIV-007','MAG-040','MAG-041','MAG-042','MAG-043','MAG-044','MAG-050','MAG-052','MAG-053'],
         ['civil-kit','magnetic-force-loss','coupled-dynamics','rig-and-demonstrator']),
        ('G4','Loaded complete vehicle','full 17 m car with calibrated ballast, beam, charger and recovery rig',
         ['Weigh all assemblies/car and measure CG/inertia/support distribution and structural modes',
          'Run AW0/AW2/AW3 boarding/ride/door/level-boarding, hot/end-of-life/weak-voltage and charge-taper cases',
          'Test braking with full battery/no regeneration, downgrade, traction faults, capture, power loss and recovery',
          'Demonstrate cartridge/power-module removal, repair/recalibration and installed serial trace'],
         [('maximum_tare_mass','kg','approved full-vehicle variant ledger; study target is not acceptance'),
          ('maximum_ride_acceleration','m/s2','operator ride requirements and approved evaluation method'),
          ('maximum_stopping_distance','m','route speed/grade/hazard and protected brake/capture strategy'),
          ('minimum_energy_reserve','J','actual route/charger availability and protected support reserve'),
          ('maximum_module_repair_time','s','availability and qualified depot handling/repair requirement')],
         ['SYS-001','SYS-004','SYS-007','SYS-010','MASS-001','GEO-003','PWR-001','PWR-002','PWR-003','PWR-004','OPS-004','OPS-005','MFG-001','MFG-005','MAG-002','MAG-003','MAG-004','MAG-054'],
         ['vehicle-mass','sbc-io-timing','local-mbom-cost','rig-and-demonstrator']),
        ('G5','Multi-car route and service demonstrator','declared consist on controlled switch-free route with depot/charging/egress access',
         ['Demonstrate consist/platform/coupler/trainline interactions and selected loop/shuttle topology',
          'Run equal-capacity timetable/headway/fleet, simultaneous charging and adverse missed-charge/weather operation',
          'Block the most constrained elevated location; time support-aware stop, accessible evacuation, recovery and reopening',
          'Observe sustained failures/repair/availability and alternative supplier repaired-module substitution'],
         [('maximum_headway','s','accepted capacity, timetable and protection requirements'),
          ('minimum_availability','fraction','operator measured-service reliability and duration requirement'),
          ('maximum_recovery_time','s','constrained-route failure blocking and evacuation plan'),
          ('maximum_charging_grid_demand','W','site grid/protection and concurrent arrival limits'),
          ('minimum_reliability_test_duration','h','assessor confidence and deployment requirements')],
         ['SYS-008','SYS-009','OPS-001','OPS-002','OPS-003','OPS-004','OPS-005','CIV-004','CTL-006','MAG-012','MAG-055'],
         ['switch-free-city','civil-kit','local-mbom-cost','rig-and-demonstrator']),
    ]
    prerequisites=[
        'Approved procedure, hazards, independent safe restraint/capture and exclusion/access plan',
        'Revision/hash-locked drawings, geometry/material curves, EBOM/MBOM, wiring/firmware and test article serials',
        'Traceable raw material/ferrite batch/axis/location, winding/insulation/retention records and prior gate NCR closure',
        'Qualified traveller with named operator/inspector, calibrated instruments/fixtures and uncertainty budget',
        'Quantitative acceptance limits approved before test; unresolved limit blocks gate decision',
        'Synchronized raw data, environmental states, calibration receipt, configuration hash and independent witness record',
    ]
    gates=[]
    for index,(identity,title,rig,procedure,limits,reqs,packages) in enumerate(gate_specs):
        gates.append(dict(id=identity,title=title,rig=rig,requires_gate_ids=[] if index==0 else ['G'+str(index-1)],
            requirement_ids=reqs,work_package_ids=packages,procedure=procedure,prerequisites=prerequisites,
            limits=[dict(id=identity+':'+name,characteristic=name,unit=unit,value=None,
                derivation_needed=derivation,status='unresolved; must be approved before test',approved_by=None)
                for name,unit,derivation in limits],
            evidence_records=['procedure_revision','article_configuration_hash','material_batch_records',
                'instrument_calibration_and_uncertainty','raw_synchronized_measurements','environmental_conditions',
                'model_revision_and_correlation_residuals','deviations_and_ncr_closure','independent_witness','authenticated_decision'],
            actual_evidence=None,decision='hold; physical evidence and approved limits absent',accepted=False,**FLAGS))
    return dict(state='protocol-planned; no-tests-performed',gates=gates,
        planning_targets_are_acceptance_limits=False,unknown_threshold_is_pass=False,
        traveller=dict(state='template-prerequisites-only; no-production-traveller-issued',
            prerequisites=prerequisites,
            hold_points=['Incoming ferrite grade/batch/axis/defect acceptance',
                'Carrier/joint datum inspection and positive retention before enclosed assembly',
                'Winding conductor/turns/insulation/impregnation/cooling and electrical test acceptance',
                'Polarity/orientation and complete field map before module release',
                'Calibrated gap/current/force/thermal end-of-line test before installation',
                'Installed position/orientation/serial, firmware/calibration and datum survey before vehicle test',
                'Closed NCRs, independent signed disposition and revision-compatible handover before acceptance'],
            actual_traveller=None,accepted=False,**FLAGS),**FLAGS)


def supplier_questions():
    prompts=[
        ('manufacturing-location','Identify the legal manufacturer and physical factory for each ferrite/core/winding/rail/electronics process; distinguish manufacturing country from distributor/export/supply country. Is any offered UK scope manufactured in the UK, or supplied through a UK distributor?',
         'Factory address, process ownership/subcontract chain, country-of-origin evidence and audit access; a UK invoice/address does not prove UK manufacture'),
        ('ferrite-grade','Give exact hard-ferrite grade, dimensions/axis, Br/Hc/recoil curves by temperature, chip/crack limits, lot traceability and reverse-field demagnetisation bounds.',
         'Grade datasheet, certified batch measurements, drawing tolerances, defect/sampling and material qualification records'),
        ('magnetic-material','Specify magnetic/structural rail/core material, B-H/hysteresis/conductivity/loss evidence, laminations if required, saliency, coatings and thermal joints.',
         'Actual material certificates and field/loss measurements over selected geometry, speed and temperature'),
        ('winding-power','Define conductor/insulation/impregnation/cooling and current/voltage/thermal ratings, power stage isolation and protection, electrical tests and repair limits.',
         'Revision-controlled electrical/thermal/interface data and measured end-of-line results'),
        ('manufacturing-capability','Show configured machine/fixture envelope, forces/tolerances, cycle times, metrology, calibration, yield/scrap/rework and first-article controls.',
         'Actual shop audit, equipment configurations, process qualification and measured production records'),
        ('interchangeability-repair','Can drawings, winding/polarity maps, firmware builds, test fixture/calibration procedures and repair data support qualified alternative suppliers?',
         'Controlled native product definition, rights/availability, substitution acceptance tests and demonstrated repaired serial trace'),
        ('commercial-boundary','Quote manufactured assemblies against declared quantity/revision; separate bought inputs, imported value, local operations, tooling/NRE, test, warranty, spares, transport, taxes and currency basis.',
         'Dated signed quote with inclusions/exclusions and input origins; no raw-ferrite-only cost or local-content assertion'),
    ]
    return [dict(id='RFQ-'+name,question=question,evidence_requested=evidence,
        supplier=None,response=None,quote=None,manufacture_country=None,supply_country=None,
        uk_manufacture_verified=False,requirement_ids=['SYS-009','MFG-002','MFG-003','MFG-004','MFG-005'],
        work_package_ids=['local-mbom-cost'],state='unanswered; no supplier/origin/price claim',accepted=False,**FLAGS)
        for name,question,evidence in prompts]


def build(requirements=None, work_packages=None):
    """Build and audit migration allocations against all current authoritative IDs."""
    if requirements is None:
        from .model import requirement_register
        requirements=requirement_register()
    plan=_read(DATA);graph,reference,scope=_source_inventory(plan)
    capabilities=capability_availability()
    req_ids=_unique(requirements,'id','ferrite requirement')
    _equal(req_ids,plan['requirements'],'ferrite requirement allocation')
    if work_packages is not None:_equal(_unique(work_packages,'id','provided work package'),WORK_PACKAGES,'primary work packages')
    items=[]
    for item in graph['items']:
        decision=plan['items'][item['id']];profile=PROFILES[decision['profile_id']]
        items.append(dict(id=item['id'],catalogue_id=item['catalogue_id'],title=item['title'],
            source=item['source'],source_sha256=item['source_sha256'],
            source_records=deepcopy(item['source_records']),source_package_ids=item['package_ids'],
            profile_id=decision['profile_id'],**deepcopy(profile),
            candidate_id=None,new_geometry_created=False,legacy_evidence_transferred=False,
            evidence_needed=list(profile['engineering_evidence_needed'])+list(COMMON_EVIDENCE),
            state='disposition-assigned; engineering-and-acceptance-open',accepted=False,**FLAGS))
    for part in reference['parts']:
        identity='baghdad:'+part['id'];decision=plan['baghdad_items'][identity];profile=PROFILES[decision['profile_id']]
        items.append(dict(id=identity,catalogue_id=part['id'],title=part['title'],source=REFERENCE.relative_to(ROOT).as_posix(),
            source_sha256=sha256(REFERENCE.read_bytes()).hexdigest(),
            source_records=[dict(pointer='/parts/id='+part['id'],record=deepcopy(part))],source_package_ids=[],
            architecture_scope='additional Baghdad six-car requirement; capacity/formation not transferred',
            profile_id=decision['profile_id'],**deepcopy(profile),candidate_id=None,
            new_geometry_created=False,legacy_evidence_transferred=False,
            evidence_needed=list(profile['engineering_evidence_needed'])+list(COMMON_EVIDENCE),
            state='disposition-assigned; engineering-and-acceptance-open',accepted=False,**FLAGS))
    packages=[]
    for package in graph['packages']:
        decision=plan['packages'][package['id']];profile=PROFILES[decision['profile_id']]
        packages.append(dict(id=package['id'],title=package['title'],
            source='engineering/generative_design/data/system-scope.json',
            source_package_ids=[package['id']],source_dependencies=package['dependencies'],
            source_item_ids=[i['id'] for i in items if package['id'] in i['source_package_ids']],
            profile_id=decision['profile_id'],**deepcopy(profile),
            source_completion_artifacts=package.get('completion_artifacts',[]),
            evidence_needed=list(profile['engineering_evidence_needed'])+list(COMMON_EVIDENCE),
            state='migration-scope-assigned; engineering-open',accepted=False,**FLAGS))
    requirements_out=[dict(**r,source=SPEC.relative_to(ROOT).as_posix(),
        source_sha256=sha256(SPEC.read_bytes()).hexdigest(),work_package_ids=plan['requirements'][r['id']],
        capability_ids=[cap['id'] for cap in capabilities if r['id'] in cap['requirement_ids']],
        new_deliverables=[identity+': '+deliverable for identity in plan['requirements'][r['id']]
            for deliverable in WORK_PACKAGE_OUTPUTS[identity][0]],
        evidence_needed=['Resolve '+r['id']+' against exact-revision allocated outputs; derive and approve unresolved limits',
                         'Exact-revision output from allocated work packages; quantitative limits before testing',
                         'Physical correlation and independent acceptance where required; source trace is not compliance']) for r in requirements]
    new_items=[dict(id=identity,title=title,profile_id=profile_id,
        requirement_ids=PROFILES[profile_id]['requirement_ids'],
        work_package_ids=PROFILES[profile_id]['work_package_ids'],quantity=None,unit=None,
        material_grade=None,geometry_revision=None,mass_kg=None,unit_cost_usd=None,country_of_origin=None,
        deliverables=PROFILES[profile_id]['new_deliverables'],evidence_needed=list(COMMON_EVIDENCE),
        state='planned-engineering-BOM-object; not-a-released-part',accepted=False,**FLAGS)
        for identity,title,profile_id in NEW_OBJECTS]
    industrial=[_obligations(i['id'],i['profile_id']) for i in items+new_items]
    all_packages=[]
    for identity in WORK_PACKAGES:
        all_packages.append(dict(id=identity,new_deliverables=WORK_PACKAGE_OUTPUTS[identity][0],
            capability_ids=[cap['id'] for cap in capabilities if identity in cap['work_package_ids']],
            capability_coverage_semantics='Implemented bounded subsets only; all exact engineering/physical evidence obligations remain open',
            evidence_needed=WORK_PACKAGE_OUTPUTS[identity][1],
            legacy_item_ids=[i['id'] for i in items if identity in i['work_package_ids']],
            legacy_package_ids=[p['id'] for p in packages if identity in p['work_package_ids']],
            requirement_ids=[r['id'] for r in requirements_out if identity in r['work_package_ids']],
            planned_object_ids=[r['id'] for r in new_items if identity in r['work_package_ids']],
            state='work-allocated; engineering-evidence-open',accepted=False,**FLAGS))
    result=dict(schema='osr-ferrite-maglev-transition/1',family='ferrite-pm-maglev-study',
        coverage_semantics='Identity allocation only; no geometry, engineering acceptance, manufacturing release or legacy evidence adoption is implied.',
        source_sha256=sources(),profiles=deepcopy(PROFILES),capability_availability=capabilities,items=items,legacy_packages=packages,
        requirements=requirements_out,work_packages=all_packages,planned_ebom=new_items,
        industrialisation=industrial,interfaces=interfaces(),
        validation_programme=validation_programme(sorted(req_ids)),supplier_questions=supplier_questions(),
        inventory_counts=dict(canonical_items=len(graph['items']),additional_baghdad_items=len(reference['parts']),
            total_source_items=len(items),legacy_work_packages=len(packages),requirements=len(requirements_out),
            primary_work_packages=len(all_packages),planned_ebom_objects=len(new_items)),
        disposition_counts=dict(sorted(Counter(i['disposition'] for i in items).items())),
        accepted_item_count=0,accepted_physical_release_count=0,**FLAGS)
    return validate(result)


def validate(register):
    """Reject missing/new items, source changes, false acceptance and unknown maps."""
    plan=_read(DATA);graph,reference,scope=_source_inventory(plan)
    if register.get('schema')!='osr-ferrite-maglev-transition/1' or register.get('family')!='ferrite-pm-maglev-study':
        raise ValueError('explicit ferrite transition schema/family required')
    if register.get('source_sha256') != sources():raise ValueError('transition source receipt changed')
    if register.get('profiles') != PROFILES:raise ValueError('transition profile definitions differ')
    capabilities=capability_availability()
    if register.get('capability_availability')!=capabilities:raise ValueError('capability scope/source/acceptance boundary differs')
    expected_items=set(plan['items'])|set(plan['baghdad_items'])
    _equal(_unique(register['items'],'id','transition item'),expected_items,'transition item inventory')
    _equal(_unique(register['legacy_packages'],'id','legacy package'),plan['packages'],'legacy package inventory')
    _equal(_unique(register['requirements'],'id','requirement'),plan['requirements'],'requirement inventory')
    _equal(_unique(register['work_packages'],'id','primary work package'),WORK_PACKAGES,'primary work package inventory')
    _equal(_unique(register['planned_ebom'],'id','planned object'),(r[0] for r in NEW_OBJECTS),'planned new objects')
    _equal(_unique(register['industrialisation'],'transition_id','industrial obligation'),
           expected_items|{r[0] for r in NEW_OBJECTS},'industrial obligation coverage')
    expected_dispositions=dict(sorted(Counter(i['disposition'] for i in register['items']).items()))
    if register.get('disposition_counts')!=expected_dispositions:raise ValueError('disposition counts differ')
    source_by_id={i['id']:i for i in graph['items']}
    source_by_id.update({'baghdad:'+p['id']:dict(catalogue_id=p['id'],title=p['title'],
        source=REFERENCE.relative_to(ROOT).as_posix(),source_sha256=sha256(REFERENCE.read_bytes()).hexdigest(),
        source_records=[dict(pointer='/parts/id='+p['id'],record=p)]) for p in reference['parts']})
    for item in register['items']:
        source=source_by_id[item['id']]
        if any(item.get(key)!=source[key] for key in ('catalogue_id','title','source','source_sha256','source_records')):
            raise ValueError('source identity/record changed: '+item['id'])
        if item['source_package_ids']!=source.get('package_ids',[]):raise ValueError('source package allocation changed')
        decisions=plan['baghdad_items'] if item['id'].startswith('baghdad:') else plan['items']
        if item['profile_id']!=decisions[item['id']]['profile_id']:raise ValueError('item disposition plan changed')
        profile=PROFILES[item['profile_id']]
        if any(item.get(key)!=value for key,value in profile.items()):raise ValueError('item profile differs')
        if item.get('new_geometry_created') is not False or item.get('legacy_evidence_transferred') is not False:
            raise ValueError('allocation cannot assert geometry/evidence transfer')
    for row in register['items']+register['legacy_packages']+register['requirements']+register['planned_ebom']+register['industrialisation']:
        if not row.get('evidence_needed'):raise ValueError('open evidence obligations required')
        reqs=row.get('requirement_ids',[])
        if not set(reqs)<=set(plan['requirements']):raise ValueError('unknown ferrite requirement mapping')
        if not row.get('work_package_ids') or not set(row['work_package_ids'])<=set(WORK_PACKAGES):
            raise ValueError('unknown/missing primary work package mapping')
    graph_packages={p['id']:p for p in graph['packages']}
    for row in register['legacy_packages']:
        if row['profile_id']!=plan['packages'][row['id']]['profile_id']:raise ValueError('legacy package allocation differs')
        if any(row.get(key)!=value for key,value in PROFILES[row['profile_id']].items()):
            raise ValueError('legacy package profile differs')
        if row['source_dependencies']!=graph_packages[row['id']]['dependencies']:
            raise ValueError('legacy dependencies differ')
        _equal(row['source_item_ids'],(i['id'] for i in register['items'] if row['id'] in i['source_package_ids']),
               'legacy package reverse item coverage')
    from .model import requirement_register
    canonical_requirements={r['id']:r for r in requirement_register()}
    for row in register['requirements']:
        if row['work_package_ids']!=plan['requirements'][row['id']]:raise ValueError('requirement allocation differs')
        if any(row.get(key)!=value for key,value in canonical_requirements[row['id']].items()):
            raise ValueError('source requirement record differs')
        expected_outputs=[identity+': '+deliverable for identity in plan['requirements'][row['id']]
                          for deliverable in WORK_PACKAGE_OUTPUTS[identity][0]]
        if row.get('new_deliverables')!=expected_outputs:raise ValueError('requirement deliverables differ')
        _equal(row.get('capability_ids',[]),(cap['id'] for cap in capabilities if row['id'] in cap['requirement_ids']),
               'requirement capability scope')
    for row in register['work_packages']:
        identity=row['id']
        _equal(row.get('capability_ids',[]),(cap['id'] for cap in capabilities if identity in cap['work_package_ids']),
               'work package capability scope')
        if row.get('new_deliverables')!=WORK_PACKAGE_OUTPUTS[identity][0] or row.get('evidence_needed')!=WORK_PACKAGE_OUTPUTS[identity][1]:
            raise ValueError('primary work package deliverables/evidence differ')
        for key,collection,field in [('legacy_item_ids','items','work_package_ids'),
            ('legacy_package_ids','legacy_packages','work_package_ids'),('requirement_ids','requirements','work_package_ids'),
            ('planned_object_ids','planned_ebom','work_package_ids')]:
            _equal(row[key],(r['id'] for r in register[collection] if identity in r[field]),'reverse allocation '+identity+':'+key)
        if not row['requirement_ids']:raise ValueError('primary work package lacks requirements')
    profile_by_id={i['id']:i['profile_id'] for i in register['items']+register['planned_ebom']}
    for row in register['industrialisation']:
        if row!=_obligations(row['transition_id'],profile_by_id[row['transition_id']]):
            raise ValueError('planned migration manufacturing/routing/origin obligation differs')
    new_object_definitions={r[0]:r[1:] for r in NEW_OBJECTS}
    for row in register['planned_ebom']:
        title,profile_id=new_object_definitions[row['id']]
        if row['title']!=title or row['profile_id']!=profile_id:raise ValueError('planned new object definition differs')
        if any(row.get(k) is not None for k in ('quantity','unit','material_grade','geometry_revision',
            'mass_kg','unit_cost_usd','country_of_origin')):
            raise ValueError('planned EBOM cannot assert actual part specifications')
    if register['interfaces']!=interfaces():raise ValueError('planned interface/commissioning boundary changed')
    if register['validation_programme']!=validation_programme(sorted(plan['requirements'])):
        raise ValueError('validation protocol/unknown acceptance thresholds changed')
    if register['supplier_questions']!=supplier_questions():raise ValueError('supplier/manufacture/supply evidence boundary changed')
    expected_counts=dict(canonical_items=len(graph['items']),additional_baghdad_items=len(reference['parts']),
        total_source_items=len(expected_items),legacy_work_packages=len(graph['packages']),requirements=len(plan['requirements']),
        primary_work_packages=len(WORK_PACKAGES),planned_ebom_objects=len(NEW_OBJECTS))
    if register['inventory_counts']!=expected_counts:raise ValueError('inventory counts differ')
    if register['accepted_item_count']!=0 or register['accepted_physical_release_count']!=0:
        raise ValueError('transition has no engineering/physical acceptance evidence')
    def no_release(value):
        if isinstance(value,dict):
            for key,child in value.items():
                if key in {*FLAGS,'accepted'} and child is not False:raise ValueError('transition cannot assert acceptance/release')
                no_release(child)
        elif isinstance(value,list):
            for child in value:no_release(child)
    # Source records are historic immutable evidence, not new acceptance claims.
    clean=deepcopy(register)
    for row in clean['items']:row.pop('source_records',None)
    no_release(clean)
    return register
