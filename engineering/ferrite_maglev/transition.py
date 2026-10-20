"""Current maglev system responsibilities, manufacturing obligations and open gates.

A current source allocation is not an engineered detail or an acceptance decision.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(__file__).parent / 'data' / 'systems-inventory.json'
REQUIREMENTS = Path(__file__).parent / 'data' / 'requirements.json'
FLAGS = dict(design_complete=False, physical_validation=False, manufacturing_release=False, physical_release=False)
SCHEMA = 'osr-ferrite-maglev-systems/1'



WORK_PACKAGES = (
    'requirements-profile', 'magnetic-cad', 'magnetic-force-loss', 'vehicle-mass',
    'civil-kit', 'rust-support-control', 'coupled-dynamics', 'sbc-io-timing',
    'switch-free-city', 'local-mbom-cost', 'rig-and-demonstrator',
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
    return json.loads(Path(path).read_text())


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


def _capability_paths():
    paths=[ROOT/'engineering/ferrite_maglev'/name for name in ('geometry.py','field.py','coupled.py','evacuation.py','evacuation.toml','optimisation.py','optimisation.toml','system_development.py','system_development.toml')]
    paths += [ROOT/'engineering/factory_examples/native.py',ROOT/'engineering/factory_examples/models.py',
              ROOT/'engineering/analysis/tests/test_ferrite_maglev_geometry_field.py',
              ROOT/'engineering/analysis/tests/test_ferrite_maglev_coupled.py',
              ROOT/'engineering/analysis/tests/test_ferrite_maglev_evacuation.py',
              ROOT/'engineering/analysis/tests/test_ferrite_maglev_system_development.py',
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
         'engineering/ferrite_maglev/optimisation.py','engineering/analysis/tests/test_ferrite_maglev_evacuation.py',
         'engineering/ferrite_maglev/system_development.py','engineering/ferrite_maglev/system_development.toml',
         'crates/osr-maglev-control/src/egress.rs','engineering/analysis/tests/test_ferrite_maglev_system_development.py'],
        ['CIV-004','OPS-003','OPS-005','GEO-001','GEO-002','MFG-005'],
        ['civil-kit','vehicle-mass','switch-free-city','local-mbom-cost','rig-and-demonstrator'],
        ['Integrated-beam/no-continuous-walkway material alternative, actual native export/reopening adapter and exact part-removal quantities',
         'Slide/chute clearance, discrete-outlet height counterexamples, driverless installation requirements and optimistic flow lower bounds; no pedestrian/device simulation',
         'Dimensioned doorway/entry material model, cap/pier/foundation demand variants and geometry-gated offline Rust egress sequencing; no production or deployed mechanism acceptance',
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


def interfaces():
    """Current data contracts and commissioning obligations, never live bindings."""
    fields=[('gap','m'),('pole_overlap','m'),('current','A'),('estimated_force','N'),
            ('force_reserve','N'),('dc_bus_voltage','V'),('dc_bus_current','A'),
            ('magnet_temperature','degC'),('winding_temperature','degC'),
            ('rail_temperature','degC'),('capture_contact','boolean'),
            ('protection_energy','J'),('support_mode','enum'),('sensor_health','enum')]
    return dict(
        erp=dict(id='interface:erp-lifecycle',state='planned-not-imported',
            source_paths=['engineering/ferrite_maglev/transition.py'],
            requirement_ids=['MFG-002','MFG-003','MFG-004','MFG-005'],work_package_ids=['local-mbom-cost'],
            deliverables=['Separate preliminary engineering Items from production-released Items/BOMs',
                'Revision/hash-linked EBOM→MBOM→routing→work order→inspection→installed serial→maintenance/spares chain',
                'Ferrite batch/orientation/location, winding/firmware/calibration revision and repaired-module trace',
                'Real company, warehouse, operator, supplier and released priced family MBOM before production import'],
            actual_company=None,actual_warehouse=None,actual_operator=None,actual_supplier=None,
            production_import_authorized=False,local_value_added_fraction=None,
            evidence_needed=list(COMMON_EVIDENCE),accepted=False,**FLAGS),
        supervision=dict(id='interface:supervision',state='planned-not-commissioned',
            source_paths=['engineering/ferrite_maglev/coupled.py','crates/osr-maglev-control/'],
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
         'Mesh/domain/refinement and independent force-method studys'],
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
         'Supplier/make-buy/tooling/facility/capacity and recurring/NRE/imported-input study'],
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


def requirement_inputs():
    data=_read(REQUIREMENTS)
    if data.get('schema')!='osr-maglev-requirement-inputs/1':
        raise ValueError('current requirement input schema required')
    records=data['requirements']
    ids=_unique(records,'id','requirement')
    if not ids:raise ValueError('empty requirement inventory')
    for row in records:
        if not row.get('requirement') or row.get('accepted') is not False or row.get('state')!='open':
            raise ValueError('requirements require open independent acceptance')
        if not row.get('work_package_ids') or not set(row['work_package_ids'])<=set(WORK_PACKAGES):
            raise ValueError('requirement allocation missing or unknown')
    return records


def inventory_inputs():
    data=_read(DATA)
    if data.get('schema')!='osr-maglev-systems-inputs/1':
        raise ValueError('current systems input schema required')
    records=data['items'];_unique(records,'id','system item')
    reqs={r['id'] for r in requirement_inputs()}
    for row in records:
        if not row.get('process_route') or not row.get('title'):
            raise ValueError('system needs manufacturing or verification route')
        if not row.get('requirement_ids') or not set(row['requirement_ids'])<=reqs:
            raise ValueError('unknown or missing system requirement allocation')
        if not row.get('work_package_ids') or not set(row['work_package_ids'])<=set(WORK_PACKAGES):
            raise ValueError('unknown or missing system work package allocation')
        source=(ROOT/row['source']).resolve()
        if row['source']!=source.relative_to(ROOT).as_posix() or not source.is_relative_to(ROOT/'engineering/ferrite_maglev') or not source.is_file():
            raise ValueError('system source outside current implementation')
    return records


def sources():
    """Only current inputs and implementations bind this responsibility register."""
    paths={DATA,REQUIREMENTS,Path(__file__),ROOT/'engineering/analysis/tests/test_ferrite_maglev_transition.py'}
    paths.update(_capability_paths())
    paths.update(ROOT/r['source'] for r in inventory_inputs())
    return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def _obligation(row):
    return dict(id='industrial:'+row['id'],system_id=row['id'],
        state='engineering-obligation; production-import-blocked',
        requirement_ids=row['requirement_ids'],work_package_ids=sorted(set(row['work_package_ids'])|{'local-mbom-cost'}),
        process_route=row['process_route'],routing_state='process-plan-unqualified',
        origin_basis='Unknown until input origins, quotations and operation costs are evidenced',
        local_value_added_fraction=None,actual_records={key:None for key in OPEN_FIELDS},
        evidence_needed=list(COMMON_EVIDENCE),accepted=False,**FLAGS)


def _build(requirements=None,work_packages=None):
    canonical=requirement_inputs()
    if requirements is None:requirements=canonical
    if requirements!=canonical:raise ValueError('requirement allocation or input differs')
    if work_packages is not None:
        _equal(_unique(work_packages,'id','provided work package'),WORK_PACKAGES,'primary work packages')
    inputs=inventory_inputs();capabilities=capability_availability();receipt=sources()
    items=[dict(**row,source_sha256=receipt[row['source']],candidate_id=None,
        evidence_needed=list(COMMON_EVIDENCE),accepted=False,**FLAGS) for row in inputs]
    requirements_out=[dict(**r,source=REQUIREMENTS.relative_to(ROOT).as_posix(),
        source_sha256=receipt[REQUIREMENTS.relative_to(ROOT).as_posix()],
        capability_ids=[c['id'] for c in capabilities if r['id'] in c['requirement_ids']],
        new_deliverables=[p+': '+d for p in r['work_package_ids'] for d in WORK_PACKAGE_OUTPUTS[p][0]],
        evidence_needed=['Resolve the exact configuration and quantitative limits before verification',
            'Retain reproducible raw evidence and independently accepted physical correlation where applicable']) for r in requirements]
    ebom=[dict(id=r['id'],title=r['title'],requirement_ids=r['requirement_ids'],
        work_package_ids=r['work_package_ids'],process_route=r['process_route'],
        quantity=None,unit=None,material_grade=None,geometry_revision=None,mass_kg=None,
        unit_cost_usd=None,country_of_origin=None,evidence_needed=list(COMMON_EVIDENCE),
        state='planned-product-responsibility; detailed-part-breakdown-open',accepted=False,**FLAGS) for r in inputs]
    packages=[dict(id=p,new_deliverables=WORK_PACKAGE_OUTPUTS[p][0],evidence_needed=WORK_PACKAGE_OUTPUTS[p][1],
        item_ids=[r['id'] for r in items if p in r['work_package_ids']],
        requirement_ids=[r['id'] for r in requirements_out if p in r['work_package_ids']],
        planned_object_ids=[r['id'] for r in ebom if p in r['work_package_ids']],
        capability_ids=[c['id'] for c in capabilities if p in c['work_package_ids']],
        state='work-allocated; engineering-evidence-open',accepted=False,**FLAGS) for p in WORK_PACKAGES]
    return dict(schema=SCHEMA,family='ferrite-pm-maglev-study',
        coverage_semantics='Current component and process responsibilities only; detailed drawings, manufactured serials and acceptance remain open.',
        source_sha256=receipt,capability_availability=capabilities,items=items,
        requirements=requirements_out,work_packages=packages,planned_ebom=ebom,
        industrialisation=[_obligation(r) for r in inputs],interfaces=interfaces(),
        validation_programme=validation_programme(sorted(r['id'] for r in requirements)),supplier_questions=supplier_questions(),
        inventory_counts=dict(canonical_items=len(items),system_items=len(items),total_source_items=len(items),
            requirements=len(requirements),work_packages=len(packages),primary_work_packages=len(packages),planned_ebom_objects=len(ebom)),
        disposition_counts={'current-system-responsibility':len(items)},
        accepted_item_count=0,accepted_physical_release_count=0,**FLAGS)


def build(requirements=None,work_packages=None):
    """Allocate the current architecture without importing completion evidence."""
    return _build(requirements,work_packages)


def validate(register):
    """Any identity, mapping, receipt or invented acceptance change fails closed."""
    expected=_build()
    if register!=expected:
        raise ValueError('system inventory, coverage, source receipt or acceptance boundary differs')
    return register
