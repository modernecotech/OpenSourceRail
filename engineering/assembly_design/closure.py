"""Full-plan work orders and independently queryable completion contracts.

This is an adapter into assembly_design's existing queue and publication, not a
new workflow. Code implementation, digital specification and externally accepted
engineering are deliberately separate states.
"""
from copy import deepcopy
from pathlib import Path
import math

from engineering.twin_workflow import core

PLAN = Path(__file__).parent/'data/closure-plan.json'
PILOTS = {
    'service-cassette': {
        'parts': ['tray', 'runners', 'positive-lock', 'secondary-retention', 'cover', 'duct-seals',
                  'clamp-lining-and-retention', 'bond-conductor', 'mating-connectors', 'solder-contacts', 'harness'],
        'interfaces': ['vehicle-mount', 'locking-indication', 'LV-mate', 'earth-bond', 'air-flanges', 'maintenance-access'],
        'operations': ['bench-assembly', 'transport-restraint', 'insertion', 'positive-lock', 'service-connection',
                       'installed-tests', 'safe-isolation', 'disconnection', 'unlock', 'removal'],
        'analyses': ['loads-and-joints', 'tolerance-and-thermal-stack', 'insertion-and-tool-path',
                     'electrical-derating-protection', 'bond-fault-duty', 'duct-flow-seal-drain', 'environment-and-fire'],
        'physical': ['pull-lock', 'bond-resistance', 'leak-flow', 'vibration-thermal-fire', 'installed-acceptance']},
    'structural-bay': {
        'parts': ['underframe', 'floor', 'side-roof-panels', 'panel-inserts', 'equipment-mounts', 'joints'],
        'interfaces': ['adjacent-bays', 'body-bogie', 'equipment', 'doors-and-gauge', 'services'],
        'operations': ['fabrication', 'join', 'inspect', 'assemble', 'equipment-install', 'repair', 'teardown'],
        'analyses': ['global-and-local-loads', 'buckling', 'fatigue', 'modal', 'lifting-jacking', 'degraded',
                     'joint-resistance', 'hot-wet-composite', 'fire-and-crash-applicability'],
        'physical': ['material-process-coupons', 'joint-panel-correlation', 'measured-mass', 'weld-bond-capability', 'vehicle-validation']},
    'viaduct-bay': {
        'parts': ['deck', 'reinforcement-prestress', 'anchors-diaphragms', 'bearings', 'caps', 'piers',
                  'foundations', 'trackform', 'walkway-parapet', 'services', 'lifting-and-jacking'],
        'interfaces': ['train-track', 'deck-bearing', 'bearing-cap', 'cap-pier', 'pier-foundation', 'ground', 'corridor'],
        'operations': ['manufacture', 'prestress-transfer', 'transport', 'temporary-stability', 'erection',
                       'joint-completion', 'strength-release', 'survey', 'installed-tests', 'bearing-replacement'],
        'analyses': ['complete-load-reactions', 'construction-stages', 'local-global-resistance', 'crack-creep-losses',
                     'fatigue', 'bearing-restraint-rotation', 'wind-seismic', 'ground-settlement-group', 'transport-crane-at-radius'],
        'physical': ['site-investigation', 'materials', 'connection-mockups', 'temporary-works-acceptance', 'asbuilt-installed-tests']},
}

# Evidence links describe scoped implementation. They cannot close a WP's
# engineering exit. Unlisted tasks remain explicit, actionable work orders.
IMPLEMENTATION = {
    'WP00-prototype': ('contracts.py', 'prototype_configuration', 'provisional named configuration; layout/route/duty adoption remains open'),
    'WP00-architecture': ('contracts.py', 'crosswalk', 'architecture boundaries enforced; physical duplicate reconciliation requires review'),
    'WP00-sources': ('contracts.py', 'source_card', 'typed and hash-aware source contract; missing licensed/supplier hashes held'),
    'WP00-standards': ('contracts.py', 'standards_register', 'edition/chemistry impact register; adoption/licences open'),
    'WP01-crosswalk': ('contracts.py', 'crosswalk', 'all source identities retained; inferred family/type mappings require confirmation'),
    'WP01-component': ('contracts.py', 'component_bundle', 'typed wrapper over existing geometry authority'),
    'WP01-interfaces': ('contracts.py', 'interface', 'typed endpoints and applicability; full railway interface population open'),
    'WP01-invalidation': ('contracts.py', 'regenerate', 'revision-bound dependent-adapter invalidation; production CAD/BIM adapters incomplete'),
    'WP01-consolidation': ('workflow.py', 'run', 'existing queue, qualification, native confirmation and portable publication extended'),
    'WP01-bim': ('bim.py', 'export', 'native tessellation to stable-ID IFC and executed IDS information tests; issued BIM placement and engineering performance remain open'),
    'WP02-bearing-omission': ('reactions.py', 'envelope', 'complete reference load allocation replaces parallel deck-only estimate'),
    'WP02-permanent': ('reactions.py', 'envelope', 'all reference-kit allocations accounted; unresolved allowances remain explicit'),
    'WP02-actions': ('reactions.py', 'envelope', 'signed reference actions and explicit unquantified mandatory action holds'),
    'WP02-load-path': ('reactions.py', 'envelope', 'equilibrium resultants through reference supports; stiffness and resistance unqualified'),
    'WP03-connected-bay': ('structural_bay.py', 'build', 'isolated floor/frame/equipment pilot with actual joints; side/roof/bogie/whole-body scope open'),
    'WP03-local-joints': ('structural_detail.py', 'report', 'actual bolt stack and local bearing/net/tearout/block-shear/prying sensitivities; contact/preload and applicable fatigue qualification held'),
    'WP03-welds': ('structural_detail.py', 'weld_register', 'proposed weld register, throat/direct-load screen and inspection/WPS requirements; qualified procedure, distortion and NDT evidence absent'),
    'WP03-structural-checks': ('structural_bay.py', 'evaluate', 'native mass properties and independent longitudinal elasticity/boundary controls; local/modal/fatigue criteria held'),
    'WP03-build-pack': ('workflow.py', 'tables', 'editable CAD/STEP, unissued layout, BOM/joints/QA; issued drawings and process qualification open'),
    'WP04-process': ('cassette_system.py', 'process_graph', 'process/access/teardown model; measured installation not performed'),
    'WP04-cassette-details': ('cassette_detail.py', 'build', 'owned detailed cover, seals, bonding, routed conductors and retention alternative; supplier internals and complete prototype acceptance held'),
    'WP04-lock': ('cassette_detail.py', 'evaluate', 'guided host/positive retention and access sensitivities; forces/wear/environmental correlation held'),
    'WP04-stages': ('cassette_system.py', 'process_graph', 'controlled installation/removal states; executed physical states absent'),
    'WP04-tolerance': ('cassette_system.py', 'report', 'worst-case dimensional and thermal hypotheses; measured distributions absent'),
    'WP05-harwin': ('cassette_system.py', 'report', 'exact solder-contact kits; derating and complete native mating geometry open'),
    'WP05-single-line': ('system_design.py', 'electrical_architecture', 'six-car hierarchical HV/LV, charge, isolation, bond and signal net definition; selected devices, routes and protection held'),
    'WP05-harness': ('cassette_system.py', 'report', 'active pin nets and termination BOM; routing/process qualification open'),
    'WP05-ratings': ('cassette_system.py', 'report', 'cable voltage/heat screens; supplier ampacity/selectivity/EMC unresolved'),
    'WP05-lv-faults': ('cassette_system.py', 'report', 'offline fault and power controls; bench/SIL/HIL unexecuted'),
    'WP05-battery-duty': ('system_design.py', 'simulate', 'existing battery solver coupled to repeated synthetic duty, HVAC and fault permissions; measured LFP maps and actual route duty held'),
    'WP05-circuits': ('system_design.py', 'circuit_benchmark', 'independent IVP and exact RC control; ngspice/electrothermal protection adapter not executed'),
    'WP06-whole-car': ('system_design.py', 'defaults', 'template-bound occupancy/climate plus explicit whole-car sensible/moisture planning assumptions; adopted duty/maps/air-quality criteria held'),
    'WP06-level1': ('system_design.py', 'simulate', 'temporal air, sensible energy and water balances coupled to battery auxiliary draw; refrigeration circuit and spatial distribution remain open'),
    'WP06-faults': ('system_design.py', 'report', 'ten temporal nominal/degraded cases and refinement; actual comfort, supplier maps and physical correlation held'),
    'WP07-kit-details': ('civil_detail.py', 'build', 'native-compatible actual cap cage, embedded lift/jacking and spacer detail; complete bay reinforcement/prestress/services and qualified connections held'),
    'WP07-resistance': ('civil_detail.py', 'evaluate', 'hollow cap fibre section and shared-reaction/handling screens; shear/fatigue/early strength/anchor/restraint and qualified resistance held'),
    'WP07-ground-input': ('site_screening.py', 'snapshot', 'actual open-data terrain/population/land/water/infrastructure estimates and investigation priorities; surveyed ground and physical tests remain open'),
    'WP08-kit-interface': ('integration.py', 'snapshot', 'exact child revision interface and ledger; full dynamic passage unexecuted'),
    'WP08-adapters': ('integration.py', 'snapshot', 'existing physics adapters indexed; source-bound dynamic requalification pending'),
    'WP08-cosimulation': ('system_design.py', 'simulate', 'sampled controller/HVAC/battery transient with independent energy/water ledgers; coupled vehicle/track/structure physics and hardware timing held'),
    'WP09-two-loops': ('development.py', 'run', 'isolated developer/critic separate from trusted family registry and design loop'),
    'WP09-families': ('families.py', 'registry', 'family domains, existing adapters and explicit unregistered-family work orders'),
    'WP09-material-bundle': ('contracts.py', 'material_bundle', 'inseparable sourced bundles, scope and density consistency guards'),
    'WP09-grammar': ('structural_bay.py', 'candidates', 'stock RHS wall/floor thickness and crossmember assembly grammar; laminate/topology grammars remain separate'),
    'WP09-reproducibility': ('workflow.py', 'seal', 'source/runtime/recipe identities, retained failures/native correspondence; surrogate qualification not implemented'),
    'WP09-objectives': ('families.py', 'pareto', 'constraint-first multiobjective frontier; null costs excluded from dominance claims'),
    'WP09-fairness': ('workflow.py', 'run', 'least-served family scheduling and finite-domain stop; missing-data work stays open'),
    'WP10-test-pyramid': ('closure.py', 'completion', 'separate research/digital/physical/production gates'),
    'WP10-authentication': ('acceptance.py', 'ingest', 'pinned-key signed raw/calibration and independent applicable review; no release authority inferred'),
    'WP10-ci': ('workflow.py', 'qualify', 'fast CI and weekly equipped-runner exact-source qualification; skipped required native checks veto qualification'),
    'WP10-negative-controls': ('reactions.py', 'envelope', 'omission/architecture/revision/electrical/duct/tolerance/source controls; local panel/prestress/ground detail controls remain open'),
    'WP10-fixtures': ('closure.py', 'requests', 'data/fixture/holdout specifications generated; fixture manufacture/calibration not performed'),
    'WP11-common-ui': ('publication.py', 'report', 'one offline closure/coverage/source/pilot index with RTL companion view'),
    'WP11-publication': ('workflow.py', 'summary', 'new source/result/task links in existing portable report; historical epochs preserved'),
    'WP11-part-links': ('design_studies.py', 'build', 'exact detailed-part to joint, manufacturing, analysis and QA handoff; full railway and issued manufacturing/ERP handoff held'),
    'WP11-recovery': ('workflow.py', 'recover', 'existing receipt recovery and publication-copy regressions retained'),
    'WP12-rfq': ('closure.py', 'requests', 'three pilot RFQ/data packs, no outreach, availability or quotation claim'),
}


def plan():
    value = core.read(PLAN)
    pdf = core.ROOT/value['source_pdf']
    if core.sha(pdf) != value['source_sha256']:
        raise ValueError('closure plan PDF differs from controlled task inventory')
    ids = {t['id'] for t in value['tasks']}
    if len(ids) != len(value['tasks']) or not set(IMPLEMENTATION) <= ids:
        raise ValueError('closure task inventory mismatch')
    return value


def completion(pilot, revision, records=None):
    """Require every frozen exit characteristic; missing/skipped is a hold.

    Records must already have passed the evidence adapter's identity/hash/tool
    verification. This evaluates completeness, not authenticity or acceptance.
    No empty arrays or arbitrary renamed requirements can vacuously close a gate.
    """
    required = PILOTS[pilot]
    if not isinstance(revision, str) or not revision:
        raise ValueError('exact pilot revision required')
    records = records or {}
    coverage = {}
    for group, items in required.items():
        coverage[group] = {}
        for identity in items:
            row = records.get(group, {}).get(identity, {})
            current = row.get('revision') == revision and row.get('receipt_verified') is True
            state = row.get('state', 'unknown') if current else 'unknown'
            if state not in {'passed', 'failed', 'unknown', 'skipped', 'held'}:
                raise ValueError('unknown gate evidence state')
            coverage[group][identity] = state
    failed = [g+'/'+k for g, rows in coverage.items() for k, state in rows.items() if state == 'failed']
    missing = [g+'/'+k for g, rows in coverage.items() for k, state in rows.items() if state != 'passed']
    digital = all(s == 'passed' for g, rows in coverage.items() if g != 'physical' for s in rows.values())
    return dict(pilot=pilot, revision=revision, coverage=coverage, failed=failed, missing=missing,
        research_shortlist_eligible=not failed and all(s == 'passed' for s in coverage['analyses'].values()),
        digital_specification_complete=digital,
        physical_records_complete=digital and all(s == 'passed' for s in coverage['physical'].values()),
        scope='Coverage evaluation only. Authenticated external evidence and appointed authority release are separate.', **core.FLAGS)


def requests(configuration):
    """Build reviewable pilot RFQ/test/fixture data requests, without outreach."""
    return [dict(id='RFQ-'+pilot, pilot=pilot, configuration_revision=configuration['revision'],
        component_revision=None, issued=False, supplier=None, quotation=None, selected=False,
        contact_scope='Request for data/test scoping only; not issued',
        inputs=['exact component/unit/interface revision', 'approved load/duty/environment envelope',
                'sample count and destructive-test allocation agreed with reviewer'],
        fixture=dict(definition_revision=None, drawings=None, load_path_review=None, calibration=None,
            required=['instrument and fixture identities/revisions', 'calibration coverage and uncertainty',
                      'controlled boundary conditions', 'adverse and repeatability cases']),
        tests=details['physical'],
        outputs=['raw time series and units', 'calibration certificates', 'method and standard edition',
                 'temperature/humidity/supply/loading conditions', 'measurement uncertainty',
                 'signed lab report and separate applicable review', 'NCRs and retest disposition',
                 'parameter/calibration/untouched holdout split', 'data retention/publication rights',
                 'lead time, complete quotation and responsibilities'],
        destinations={'service-cassette':['NPL metrology', 'qualified electrical/flow and environmental lab'],
                      'structural-bay':['NCC material/joint/panel scope', 'Huddersfield IRR dynamics scope'],
                      'viaduct-bay':['COSQC/appointed Iraqi labs', 'competent ground investigation team', 'qualified precast/lifting team']}[pilot],
        **core.FLAGS) for pilot, details in PILOTS.items()]


def tasks_for(item, controlled_plan):
    """Allocate plan work to reusable families, not one new adapter per record."""
    pilot=item.get('pilot')
    packages={'service-cassette':{'WP04','WP05','WP06','WP10'},
              'bearing-seat':{'WP02','WP07','WP08','WP10'},
              'structural-bay':{'WP02','WP03','WP04','WP08','WP10'}}.get(pilot, {'WP00','WP01','WP09'})
    return [t['id'] for t in controlled_plan['tasks'] if t['wp'] in packages]


def snapshot(prepared):
    """Source-bound actionable view; a source file alone never completes design."""
    from . import contracts
    value = deepcopy(prepared.get('closure_plan') or plan())
    for task in value['tasks']:
        task['implementation'] = 'external-input' if task['kind']=='external' else 'not-implemented'
        task['evidence'] = []
        if task['id'] in IMPLEMENTATION:
            name, entry, scope = IMPLEMENTATION[task['id']]
            path = 'engineering/assembly_design/'+name
            if path in prepared['source_sha256']:
                task.update(implementation='partial-provisional', implementation_scope=scope,
                    evidence=[dict(source=path, source_sha256=prepared['source_sha256'][path], entrypoint=entry,
                        evidence_level='implementation-source; executed tests in qualification receipt')])
        task['next_action'] = ('obtain externally authenticated evidence and appointed review' if task['kind']=='external'
                               else 'finish remaining scope and execute the exact engineering exit cases')
        task['engineering_exit'] = 'open'
    config = prepared.get('prototype') or contracts.prototype_configuration()
    result=dict(schema='osr-full-design-closure-progress/1', source_pdf=value['source_pdf'],
        source_pdf_sha256=value['source_sha256'], packages=value['packages'], tasks=value['tasks'],
        task_count=len(value['tasks']), engineering_closed_tasks=0,
        prototype=config, pilot_contracts={p:completion(p, config['revision']) for p in PILOTS},
        requests=requests(config),
        scope='All plan tasks retained. Partial implementation is not a completed digital specification or accepted physical design.', **core.FLAGS)
    if prepared.get('site'):
        result['site_screening_revision']=prepared['site']['screening']['revision']
        for request in result['requests']:
            if request['pilot']=='viaduct-bay':
                request['desktop_site_evidence']=dict(context_revision=prepared['site']['context']['revision'],
                    infrastructure_revision=prepared['site']['screening']['revision'],
                    investigation_quantity_scenarios='Per-route 250/500 m chainage spacing plus mapped water/infrastructure hotspots; provisional quantities in site/summary.json',
                    actual_ground_investigation_complete=False)
    return result
