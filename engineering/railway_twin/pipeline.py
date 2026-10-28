"""Reproducible complete-scope research packages with semantic replay validation.

Execution, digital consistency, numerical support and physical acceptance are
different results. A package containing explicit unresolved equipment is useful
digital evidence; it cannot satisfy require_complete or become an operating train.
"""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
from collections import Counter
import gzip
import fcntl
import io
import json
import tarfile
import tempfile
import time
import tomllib

from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded, identity, digest
from engineering.development_baseline import selection
from engineering.design_search import railway_campaign, railway_bundle, system_inventory
from engineering.design_search import railway_delivery, system_motion, architecture_demand
from engineering.design_search import fault_response, test_readiness, grammar_shell, requirement_policy
from . import FLAGS, model, geometry, propulsion

SPEC = 'campaigns/end-to-end-digital-twin.toml'
OUTPUT = 'docs/design-engine/digital-twin'
PRODUCER = 'engineering/railway_twin/pipeline.py'


class IncompleteDesign(ValueError):
    def __init__(self, blockers):
        self.blockers = blockers
        super().__init__('Engineering completion held: ' + ', '.join(r['id'] for r in blockers))


def specification(root=ROOT):
    s = tomllib.loads((Path(root) / SPEC).read_text())
    required = dict(schema='osr-end-to-end-digital-twin/1', reference_changes_allowed=False,
        body_families=list(model.FAMILIES), distances_m=[1500.,2000.], maximum_cases=6,
        unknown_is_zero=False, automatic_physical_acceptance=False,
        operating_maps_require_external_authentication=True)
    if any(s.get(k) != v for k,v in required.items()):
        raise ValueError('Explicit non-promoting twin scope and complete request matrix required')
    if not 1 <= s['maximum_seconds'] <= 1800 or not 0 <= s['maximum_native_jobs'] <= 1 or not 1 <= s['native_timeout_s'] <= 240:
        raise ValueError('Bounded twin resources required')
    if s['guideway']['family'] != 'box-beam' or s['guideway']['span_m'] != 20 or s['guideway']['tracks'] != 1:
        raise ValueError('A changed civil family requires its geometry/delivery adapter')
    fixed = dict(cars=6,car_length_m=17.,normal_people_per_car=46,crowd_people_per_car=160,
        speed_cap_m_s=20.,acceleration_m_s2=.4,service_deceleration_m_s2=.6,headway_s=120.,dwell_s=35.)
    if any(s['operations'].get(k) != v for k,v in fixed.items()):
        raise ValueError('Revise the complete experimental interfaces before changing the service context')
    return s


def sources(root=ROOT):
    root = Path(root)
    result = railway_campaign.source_epoch(root)
    reference=selection.load(root)
    result.update(reference['source_sha256'])
    result.update(reference['vehicle']['source_sha256'])
    for path in sorted((root / 'engineering/railway_twin').glob('*.py')):
        result[path.relative_to(root).as_posix()] = digest(path)
    for path in sorted((root/'engineering/design_search/data').rglob('*')):
        if path.is_file() and path.suffix in ('.json','.toml'):
            result[path.relative_to(root).as_posix()]=digest(path)
    for name in (SPEC, 'osr-twin', 'engineering/requirements.txt', OUTPUT+'/README.md',
        'engineering/design_search/station_accelerators.py', 'campaigns/station-accelerator-development.toml',
        'engineering/design_search/railway_delivery.py','engineering/design_search/wheel_twin.py',
        'engineering/design_search/fault_response.py','engineering/design_search/test_readiness.py',
        test_readiness.DEFINITIONS):
        result[name] = digest(root / name)
    if digest(root / PRODUCER) != digest(__file__):
        raise ValueError('Executing twin differs from declared source tree')
    return dict(sorted(result.items()))


def _nonpromoting(value):
    if isinstance(value,dict):
        if any(key in FLAGS and item is not False for key,item in value.items()):
            raise ValueError('Nested twin evidence cannot promote acceptance, release or a physical journey')
        for item in value.values():
            _nonpromoting(item)
    elif isinstance(value,list):
        for item in value:
            _nonpromoting(item)


def _sealed(value, key='evaluation_id'):
    value[key] = identity(value)
    return value


def _physics(m):
    b, contact = m['bundle'], m['contact_geometry']
    motions = []
    contexts = [('empty',dict(load='empty')),('normal',dict(load='normal')),
        ('crowd',dict(load='crowd')),('adverse-normal',dict(load='normal',grade_up_fraction=.02,headwind_m_s=10.,rail_adhesion=.025))]
    for name, overrides in contexts:
        # A missing force map is passed as missing. Self-attested map records are
        # not an input to this producer and cannot reach the older admission API.
        motions.append(dict(name=name,result=system_motion.evaluate(b,available_map=None,scenario_overrides=overrides)))
    faults = []
    starts = b['architecture_case']['physical_definition']['wayside']['bank_starts_from_initial_nose_m']
    from engineering.design_search import sparse_launch
    for disabled in range(len(starts)):
        active = sparse_launch.geometry([x for i,x in enumerate(starts) if i != disabled],20.,initial_nose_m=0.,launch_distance_m=500.)
        demand = architecture_demand.demand(b['architecture_case']['physical_definition']['route']['station_spacing_m'],
            b['mass']['accounted_cap_loaded_kg_per_car'],b['rotating_equivalent_kg_per_car'],cars=6,
            powered_windows=active['required_launch_contact_union_m'],speed_cap_m_s=20.,acceleration_m_s2=.4,deceleration_m_s2=.6)
        demand.pop('trace')
        faults.append(dict(disabled_bank_index=disabled,installed_candidate_id=b['candidate_id'],
            installed_primary_geometry_id=contact['physical_geometry_id'],installed_bank_length_m=100.,
            active_contact=active,conditional_demand=demand,
            dispatch='hold' if not active['initial_geometric_overlap'] else 'degraded-operation-unqualified',
            external_recovery_required=True,**FLAGS))
    return _sealed(dict(schema='osr-railway-twin-physics/1',candidate_id=b['candidate_id'],
        bundle_definition_id=b['definition_id'],loading_cases=motions,failed_banks=faults,
        independent_brake_responses=fault_response.evaluate(b),
        map_admission=dict(admitted=False,available_force_map_id=None,
            reason='No externally authenticated exact-20m motor/branch/interface map; supported strings and hash-shaped review IDs are not evidence'),
        actual_electrical_energy_kWh=None,actual_repeated_thermal_duty=None,**FLAGS))


def _construction(b, ledger, selected):
    D = b['architecture_case']['physical_definition']['route']['station_spacing_m']
    spans = int((D+120)/20)
    names = ('survey-and-utilities','ground-investigation','foundation-design-release','foundations',
        'piers-headstocks-bearings','precast-inspect-transport','temporary-works-and-erection',
        'rails-fasteners-drainage-containment','wayside-power-cooling-and-protection','platform-access-evacuation',
        'alignment-configuration-and-brake-tests','independent-handback')
    operations = [dict(id=name,predecessors=[] if i==0 else [names[i-1]],
        duration_h=None,crew=None,tooling=None,engineering_release=False) for i,name in enumerate(names)]
    return _sealed(dict(schema='osr-railway-twin-construction/1',candidate_id=b['candidate_id'],
        counted_track_length_m=D+120,interstation_distance_m=D,departure_berth_extension_m=120.,
        spans=spans,rail_length_m=2*(D+120),support_positions_m=[-120.+20*i for i in range(spans+1)],
        support_position_scope='Geometric stationing only; not counted piers, pile lengths or a site structural design',
        counted_span_quantities={key:selected[key]*spans for key in ('concrete_m3','concrete_mass_kg','running_rail_kg','direct_fastener_sets',
            'direct_fastener_kg','reinforcement_kg','prestress_kg','prestress_anchorage_kg')},
        crane_hook_mass_hypothesis_kg=selected['construction']['minimum_crane_hook_capacity_kg_hypothesis'],
        foundation_quantities=None,station_complete_quantities=None,operations=operations,
        unlocated_account_ids=[r['id'] for r in ledger['unlocated_accounts'] if not r['system'].startswith('vehicle/')],**FLAGS))


def _controls(b, physics):
    gates = ['correct-candidate-and-route','all-required-banks-healthy','doors-locked-and-integrity-proved',
        'independent-brake-and-essential-reserve','protected-route-and-receiving-berth','localisation-and-gap-budgets',
        'available-force-current-temperature-envelope','external-recovery-and-egress-provision']
    return _sealed(dict(schema='osr-railway-twin-controls/1',candidate_id=b['candidate_id'],
        brake_definition_id=b['brake_definition']['brake_definition_id'],
        primary_component_id=b['propulsion_component_id'],normal_capacity_pphpd=8280.,
        target_headway_s=120.,qualified_headway_s=None,operating_authority=False,
        states=['held','berthed','ready','launch','coast','independent-braking','stopped','protected-recovery'],
        dispatch_gates=[dict(id=g,supported=False,evidence_id=None) for g in gates],
        failed_bank_responses=[dict(bank=r['disabled_bank_index'],dispatch=r['dispatch']) for r in physics['failed_banks']],
        onboard_traction=False,traction_store=False,auxiliary_and_ATP_power_retained=True,
        authority_scope='Generated interface and test contract; not live ATP/interlocking or a safety approval',**FLAGS))


def _blockers(b, ledger):
    descriptions = {
      'installed-equipment':'Locate and count all equipment, residual accounts, joints, fasteners, wiring, cooling and access; close mass, CG and inertia',
      'body-structure':'Correlate directional materials and joints; close strength, buckling, fatigue, thermal, fire and crowd/accidental loads',
      'moving-force-map':'Solve and independently validate the exact40-period/20m motor with finite fin entry and actual branch connections',
      'electrical-and-thermal':'Resolve converters, feeders, isolation and per-bank repeated120s electrical/thermal/cooling duty',
      'independent-brakes':'Validate installed independent brake supplies, WSP/fade, precise stop, parking and safety limits',
      'protected-journey':'Complete force-driven1.5/2km journeys, failed banks/power, protected stopping, recovery and headway',
      'civil-and-site':'Resolve torsion, bearings, piers, foundations, route/site, drainage, containment, construction and station/access design',
      'manufacturing':'Resolve net cuts, joining, process plans, tooling, yields, labour, inspection, repair and supplier configurations',
      'whole-life-economics':'Price the complete equal-service vehicle, stations, infrastructure, factories, fleet, energy, maintenance and renewals',
      'physical-qualification':'Authenticate as-built articles, measurements, approved limits and independent reviews in the qualification workflow'}
    return [dict(id=name,task_id=identity(dict(candidate_id=b['candidate_id'],obligation=name)),
        candidate_id=b['candidate_id'],status='open',required=description,
        completion_evidence_id=None) for name,description in descriptions.items()]


def _federated_bom(m, inventory, scene, ledger):
    """Whole-cell quantities; source body MBOMs remain explicitly per car."""
    b=m['bundle'];candidate=b['candidate_id']
    solids={r['id']:r for r in scene['occurrences']}
    engineering=[]
    for name,row in solids.items():
        part=row['geometry']
        engineering.append(dict(id=name,candidate_id=candidate,component_definition_id=row['component_definition_id'],
            system=row['system'],scope=row['scope'],quantity=1,unit='stock-occurrence',
            accounted_mass_kg=row['mass_kg'],nominal_stock_volume_m3=part['volume_m3'],
            geometry_id=identity(part),translation_m=row['translation_m'],
            material=part.get('material_id',part.get('material')),origin_country=None,
            unit_price_USD=None,installed_mass_complete=False))
    for row in ledger['unlocated_accounts']:
        engineering.append(dict(id=row['id'],candidate_id=candidate,component_definition_id=row['component_definition_id'],
            system=row['system'],scope='unlocated-account-or-obligation',
            quantity=None,unit='unresolved-physical-occurrence',accounted_mass_kg=row['accounted_mass_kg'],
            nominal_stock_volume_m3=None,geometry_id=None,translation_m=None,material=None,origin_country=None,
            unit_price_USD=None,installed_mass_complete=False))
    groups={}
    for car in range(6):
        for item in inventory['manufacturing_BOM']:
            groups['car/'+str(car)+'/'+item['id']]=['car/'+str(car)+'/'+name for name in item['engineering_stock_ids']]
    grouped={name for names in groups.values() for name in names}
    for name,row in solids.items():
        if name in grouped:
            continue
        parts=name.split('/')
        if parts[0]=='bank':
            group='/'.join(parts[:2])+('/copper-stock' if row['geometry'].get('role')=='copper-stock' else '/steel-stock')
        elif parts[0]=='span':
            group='/'.join(parts[:2])+('/concrete' if row['system']=='civil/concrete' else '/'+parts[2]+'/'+parts[3])
        else:
            group=name
        groups.setdefault(group,[]).append(name)
    coverage=[name for names in groups.values() for name in names]
    if len(coverage)!=len(set(coverage)) or set(coverage)!=set(solids):
        raise ValueError('Federated manufacturing groups must cover every stock occurrence exactly once')
    manufacturing=[]
    for name,ids in sorted(groups.items()):
        group_id=identity(dict(candidate_id=candidate,name=name,engineering_ids=ids))
        manufacturing.append(dict(id=name,group_id=group_id,candidate_id=candidate,
            engineering_occurrence_ids=ids,known_gross_stock_mass_kg=sum(solids[key]['mass_kg'] for key in ids),
            net_fabricated_mass_kg=None,purchased_stock_quantity=None,yield_fraction=None,
            process_qualification=None,labour_h=None,tooling=None,inspection_procedure=None,
            repair_and_removal_route=None,unit_price_USD=None,origin_country=None))
    procurement=[dict(id='procure/'+g['group_id'],manufacturing_group_id=g['group_id'],
        supplier=None,price_USD=None,lead_time_days=None,earliest_material_consumption=None,
        source_quote_id=None,ready_for_order=False,material_release_required=True) for g in manufacturing]
    operations=[dict(id='make-inspect/'+g['group_id'],manufacturing_group_id=g['group_id'],
        predecessors=['procure/'+g['group_id']],labour_h=None,duration_h=None,
        inspection_release=False) for g in manufacturing]
    erp=dict(items=[dict(doctype='Item',item_code='OSR-RESEARCH-'+g['group_id'],item_name=g['id'],
        disabled=1,is_stock_item=0,unit_price=None,candidate_id=candidate) for g in manufacturing],
        BOM=dict(doctype='BOM',docstatus=0,is_active=0,is_default=0,total_cost=None),posted=False,ready_for_import=False)
    return _sealed(dict(schema='osr-federated-railway-BOM/1',candidate_id=candidate,
        engineering_BOM=engineering,manufacturing_BOM=manufacturing,procurement=procurement,
        manufacturing_operations=operations,ERPNext=erp,
        unresolved_occurrence_ids=[r['id'] for r in ledger['unlocated_accounts']],
        located_stock_occurrences=len(solids),complete_installed_BOM=False,complete_installed_price_USD=None,
        scope='Six cars plus five banks plus counted directional civil cell; every stock occurrence assigned exactly once. Unknown equipment, net cuts, purchased stock, yield and joints remain unresolved.',**FLAGS))


def calculate(materialized, root=ROOT):
    m = materialized
    b, body = m['bundle'], m['body']
    railway_bundle.validate(b)
    distance=b['architecture_case']['physical_definition']['route']['station_spacing_m']
    if m!=model.materialize(body['parameters']['family'],distance,root):
        raise ValueError('Twin materialization differs from its physical generator inputs')
    inv = system_inventory.evaluate(body,bundle_id=b['candidate_id'],source_root=root)
    if abs(inv['known_accounted_mass_subtotal_kg']-b['mass']['accounted_tare_kg_per_car'])>1e-7:
        raise ValueError('Inventory and physics mass scopes differ')
    ledger = model.ledger(m,inv,root)
    scene = ledger.pop('scene')
    ledger.pop('ledger_id')
    ledger['scene_id'] = identity(scene)
    ledger['ledger_id'] = identity(ledger)
    properties = geometry.validate_scene(scene)
    vehicle_stock = sum(r['mass_kg'] for r in scene['occurrences'] if r['system'].startswith('vehicle/'))
    vehicle_residual = sum(r['accounted_mass_kg'] for r in ledger['unlocated_accounts'] if r['system'].startswith('vehicle/') and r['accounted_mass_kg'] is not None)
    residual = vehicle_stock+vehicle_residual-6*b['mass']['accounted_tare_kg_per_car']
    if abs(residual)>1e-6:
        raise ValueError('Federated located stock plus disjoint account residuals do not reconcile with train demand')
    mass = dict(candidate_id=b['candidate_id'],located_stock=properties,
        train_located_stock_kg=vehicle_stock,train_retained_unlocated_subtotal_kg=vehicle_residual,
        train_accounted_mass_subtotal_kg=6*b['mass']['accounted_tare_kg_per_car'],account_reconciliation_residual_kg=residual,
        unknown_mass_occurrences=sum(r['accounted_mass_kg'] is None for r in ledger['unlocated_accounts']),
        complete_installed_mass_kg=None,complete_installed_CG_m=None,complete_installed_inertia_kg_m2=None,**FLAGS)
    physics = _physics(m)
    civil_result = railway_bundle.assess_civil(b)
    construction = _construction(b,ledger,m['selected_civil'])
    delivery = railway_delivery.compile(b,body,inv)
    all_ids = [r['id'] for r in scene['occurrences']] + [r['id'] for r in ledger['unlocated_accounts']]
    if len(all_ids) != len(set(all_ids)):
        raise ValueError('Duplicated federated physical occurrence')
    economics = _sealed(dict(schema='osr-railway-twin-economics/1',candidate_id=b['candidate_id'],
        priced_occurrences=0,total_occurrences=len(all_ids),unpriced_occurrence_ids=all_ids,
        known_quoted_subtotal_USD=None,installed_CAPEX_USD=None,purchased_energy_kWh=None,
        OPEX_USD_per_year=None,whole_life_cost_USD=None,discount_basis=None,
        physical_service_qualified=False,economic_winner=None,
        boundary='Directional interstation cell only. Full line, fleet, depot, station access, factories, construction, energy, maintenance, renewals and reliability remain required',**FLAGS))
    closure = _sealed(dict(schema='osr-railway-twin-completion/1',candidate_id=b['candidate_id'],
        digital_execution='completed',engineering_complete=False,physical_design_complete=False,
        integrated_selection=None,blockers=_blockers(b,ledger),
        next_action_policy='Fix a physical shortfall by a physical revision; unsupported model requires evaluator work; missing supplier/test/site data requires evidence. Do not weaken mandatory obligations.',
        physical_test_record_count=0,available_operating_map_count=0,physically_supported_journeys=0,**FLAGS))
    structural = dict(candidate_id=b['candidate_id'],body_candidate_id=body['candidate_id'],
        numerical_plan=grammar_shell.plan(body),executed_native_evaluation=None,
        prior_body_evidence_inherited=False,complete_strength_buckling_fatigue=False,**FLAGS)
    return {'candidate.json.gz':m,'inventory.json.gz':inv,'ledger.json.gz':ledger,'scene.json.gz':scene,
        'federated-bom.json.gz':_federated_bom(m,inv,scene,ledger),
        'mass-properties.json':mass,'propulsion.json.gz':propulsion.requirements(b,m['contact_geometry'],root=root),
        'physics.json.gz':physics,'structure.json':structural,'civil.json.gz':civil_result,
        'manufacturing.json.gz':delivery,'construction.json':construction,'controls.json':_controls(b,physics),
        'economics.json.gz':economics,'required-tests.json.gz':test_readiness.build(b,root=root),'completion.json':closure}


def _raw(value,name):
    raw = encoded(value)
    return gzip.compress(raw,mtime=0) if name.endswith('.gz') else raw


def _read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def _ordinary_files(folder):
    result = {}
    for path in sorted(Path(folder).rglob('*')):
        if path.is_symlink():
            raise ValueError('Linked twin payload refused')
        if path.is_file() and path.name != 'manifest.json':
            result[path.relative_to(folder).as_posix()] = digest(path)
        elif path.is_file() and path.parent != Path(folder):
            result[path.relative_to(folder).as_posix()] = digest(path)
    return result


def _input_archive(root,epoch):
    data = io.BytesIO()
    with tarfile.open(fileobj=data,mode='w') as stream:
        size = 0
        for name,expected in epoch.items():
            path = Path(root) / name
            if Path(name).is_absolute() or '..' in Path(name).parts or path.is_symlink():
                raise ValueError('Ordinary source paths required')
            raw = path.read_bytes()
            if sha256(raw).hexdigest() != expected:
                raise ValueError('Source changed during immutable input retention')
            size += len(raw)
            if size>64*1024**2:
                raise ValueError('Source package budget exceeded')
            item = tarfile.TarInfo(name); item.size=len(raw);item.mtime=0;item.mode=0o644
            stream.addfile(item,io.BytesIO(raw))
    return gzip.compress(data.getvalue(),mtime=0)


def generate(root=ROOT, *, family='gfrp_semimonocoque',distance_m=2000.,output=None,native=False):
    root=Path(root).resolve();spec=specification(root);epoch=sources(root)
    materialized=model.materialize(family,distance_m,root)
    request=dict(family=family,distance_m=distance_m,native=native,specification=spec,
        candidate_id=materialized['bundle']['candidate_id'],source_sha256=epoch)
    request_id=identity(request)
    target=Path(output) if output is not None else root/'build/railway-twin/runs'/request_id
    if target.exists():
        result=verify(target,root=root)
        manifest=_read(target/'manifest.json')
        if manifest['request']!=request:
            raise ValueError('Existing output belongs to another exact twin request')
        return dict(result,cached=True,output=str(target))
    target.mkdir(parents=True)
    artifacts=calculate(materialized,root)
    for name,value in artifacts.items():
        (target/name).write_bytes(_raw(value,name))
    (target/'input-sources.tar.gz').write_bytes(_input_archive(root,epoch))
    status=dict(requested=native,execution='not-run',complete_installed_geometry=False,**FLAGS)
    if native:
        status['IFC']=geometry.write_ifc(artifacts['scene.json.gz'],target/'IFC')
        status['CAD']=geometry.export_native(artifacts['scene.json.gz'],target/'CAD',timeout_s=spec['native_timeout_s'])
        status['execution']='completed' if status['CAD'].get('execution')=='completed' else 'partial-or-failed'
    (target/'native-status.json').write_bytes(encoded(status))
    if sources(root)!=epoch:
        raise ValueError('Twin sources changed during generation; retain partial output, rerun in a fresh directory')
    manifest=dict(schema='osr-end-to-end-digital-twin-package/1',request=request,request_id=request_id,
        candidate_id=materialized['bundle']['candidate_id'],body_candidate_id=materialized['body']['candidate_id'],
        files_sha256=_ordinary_files(target),**FLAGS)
    manifest['evaluation_id']=identity(manifest)
    (target/'manifest.json').write_bytes(encoded(manifest))
    return dict(verify(target,root=root),cached=False,output=str(target))


def verify(output, *, root=ROOT,require_complete=False):
    root=Path(root).resolve();target=Path(output)
    if target.is_symlink():
        raise ValueError('Linked twin directory refused')
    manifest=_read(target/'manifest.json')
    if (manifest.get('schema')!='osr-end-to-end-digital-twin-package/1'
        or manifest.get('evaluation_id')!=identity({k:v for k,v in manifest.items() if k!='evaluation_id'})
        or any(manifest.get(k) is not v for k,v in FLAGS.items())):
        raise ValueError('Twin manifest identity, schema or release disposition differs')
    request=manifest['request']
    if request.get('source_sha256')!=sources(root) or request.get('specification')!=specification(root):
        raise ValueError('Twin source epoch or input specification is stale')
    if manifest['request_id']!=identity(request) or manifest['files_sha256']!=_ordinary_files(target):
        raise ValueError('Twin payload or request identity differs')
    m=model.materialize(request['family'],request['distance_m'],root)
    candidate=m['bundle']['candidate_id']
    if candidate!=request['candidate_id'] or candidate!=manifest['candidate_id'] or m['body']['candidate_id']!=manifest['body_candidate_id']:
        raise ValueError('Mixed physical twin identity')
    artifacts=calculate(m,root)
    for name,value in artifacts.items():
        if not (target/name).is_file() or (target/name).read_bytes()!=_raw(value,name):
            raise ValueError('Twin semantic replay differs: '+name)
    if (target/'input-sources.tar.gz').read_bytes()!=_input_archive(root,request['source_sha256']):
        raise ValueError('Retained source input bytes differ')
    native=_read(target/'native-status.json')
    _nonpromoting(native)
    if (type(request['native']) is not bool or native.get('requested') is not request['native']
        or any(native.get(k) is not v for k,v in FLAGS.items())):
        raise ValueError('Native evidence request or disposition differs')
    expected=set(artifacts)|{'input-sources.tar.gz','native-status.json'}
    if request['native']:
        geometry.verify_ifc(artifacts['scene.json.gz'],target/'IFC',native['IFC'])
        geometry.verify_native(artifacts['scene.json.gz'],target/'CAD',native['CAD'])
        execution='completed' if native['CAD'].get('execution')=='completed' else 'partial-or-failed'
        if native!=dict(requested=True,execution=execution,complete_installed_geometry=False,
                        IFC=native['IFC'],CAD=native['CAD'],**FLAGS):
            raise ValueError('Native stage status differs from actual executed scope')
        expected.update(k for k in manifest['files_sha256'] if k.startswith(('IFC/','CAD/')))
    elif native!=dict(requested=False,execution='not-run',complete_installed_geometry=False,**FLAGS):
        raise ValueError('Unrequested native execution cannot assert evidence')
    if set(manifest['files_sha256'])!=expected:
        raise ValueError('Unexpected or missing twin artifacts')
    completion=artifacts['completion.json']
    blockers=deepcopy(completion['blockers'])
    if not request['native'] or native['execution']!='completed':
        blockers.append(dict(id='native-geometry',task_id=identity(dict(candidate_id=candidate,task='native-geometry')),
            candidate_id=candidate,status='not-run',required='Generate and reopen actual IFC/CAD/STEP stock assembly',completion_evidence_id=None))
    if require_complete and blockers:
        raise IncompleteDesign(blockers)
    return dict(schema='osr-end-to-end-twin-validation/1',verified=True,software_consistent=True,
        candidate_id=candidate,evaluation_id=manifest['evaluation_id'],request_id=manifest['request_id'],
        body_candidate_id=m['body']['candidate_id'],family=request['family'],distance_m=request['distance_m'],
        occurrences=len(artifacts['scene.json.gz']['occurrences']),
        unlocated_accounts=len(artifacts['ledger.json.gz']['unlocated_accounts']),
        engineering_complete=False,physical_design_complete=False,integrated_selection=None,
        available_force_maps=0,physically_supported_journeys=0,blockers=blockers,
        native_requested=request['native'],native_execution=native['execution'],**FLAGS)


def run(root=ROOT, *, state=None,maximum_new_cases=None,native_jobs=0):
    folder=Path(state) if state is not None else Path(root)/'build/railway-twin'
    folder.mkdir(parents=True,exist_ok=True)
    with (folder/'campaign.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        return _run(root,state=folder,maximum_new_cases=maximum_new_cases,native_jobs=native_jobs)


def _run(root=ROOT, *, state=None,maximum_new_cases=None,native_jobs=0):
    root=Path(root);spec=specification(root);epoch=sources(root)
    if (type(native_jobs) is not int or not 0<=native_jobs<=spec['maximum_native_jobs']
        or maximum_new_cases is not None and (type(maximum_new_cases) is not int or not 0<=maximum_new_cases<=spec['maximum_cases'])):
        raise ValueError('Explicit bounded case/native request required')
    folder=Path(state) if state is not None else root/'build/railway-twin'
    folder.mkdir(parents=True,exist_ok=True)
    contract=dict(specification=spec,source_sha256=epoch,native_jobs=native_jobs)
    rows=[];pending=[];failed=[];started=time.monotonic();new=0
    for family in spec['body_families']:
        for distance in spec['distances_m']:
            native=(family==spec['body_families'][0] and distance==2000. and native_jobs==1)
            request=dict(family=family,distance_m=distance,native=native,contract_id=identity(contract))
            output=folder/'cases'/identity(request)
            if not output.exists() and (maximum_new_cases is not None and new>=maximum_new_cases or time.monotonic()-started>=spec['maximum_seconds']):
                pending.append(request);continue
            existed=output.exists()
            try:
                row=generate(root,family=family,distance_m=distance,output=output,native=native)
            except (OSError,ValueError,RuntimeError) as error:
                if sources(root)!=epoch:
                    raise ValueError('Campaign source changed; retained partial inputs must not be published') from error
                failure=dict(request=request,output=output.relative_to(folder).as_posix(),
                    execution='failed-or-interrupted',error_type=type(error).__name__,reason=str(error),**FLAGS)
                failed.append(failure);pending.append(request)
                (folder/('failure-'+identity(request)+'.json')).write_bytes(encoded(failure))
                new+=int(not existed)
                continue
            stable={k:v for k,v in row.items() if k not in ('cached','output')}
            rows.append(dict(request=request,output=output.relative_to(folder).as_posix(),validation=stable))
            new+=int(not existed)
    value=dict(schema='osr-end-to-end-twin-campaign/1',contract=contract,contract_id=identity(contract),
        cases=rows,pending=pending,failed=failed,new_cases=new,integrated_selection=None,**FLAGS)
    value['campaign_id']=identity({k:v for k,v in value.items() if k!='new_cases'})
    temporary=folder/'latest.pending.json'
    temporary.write_bytes(encoded(value));temporary.replace(folder/'latest.json')
    return value


def _check_campaign(value,root):
    spec=specification(root);contract=value.get('contract',{})
    jobs=contract.get('native_jobs')
    if type(jobs) is not int or not 0<=jobs<=spec['maximum_native_jobs']:
        raise ValueError('Campaign native budget differs')
    if contract!=dict(specification=spec,source_sha256=sources(root),native_jobs=jobs):
        raise ValueError('Campaign input/source contract differs')
    contract_id=identity(contract)
    expected=[(f,d) for f in specification(root)['body_families'] for d in specification(root)['distances_m']]
    actual=[(r['request']['family'],r['request']['distance_m']) for r in value['cases']]+[(r['family'],r['distance_m']) for r in value['pending']]
    if (value.get('schema')!='osr-end-to-end-twin-campaign/1' or sorted(expected)!=sorted(actual)
        or value['campaign_id']!=identity({k:v for k,v in value.items() if k not in ('new_cases','campaign_id')})
        or value['contract_id']!=contract_id):
        raise ValueError('Campaign coverage or source epoch differs')
    _nonpromoting(value)
    for request in [r['request'] for r in value['cases']]+value['pending']:
        native=(request['family']==spec['body_families'][0] and request['distance_m']==2000. and jobs==1)
        if request!=dict(family=request['family'],distance_m=request['distance_m'],native=native,contract_id=contract_id):
            raise ValueError('Campaign request contract, native scope or identity differs')
    for row in value['cases']:
        if row['output']!='cases/'+identity(row['request']):
            raise ValueError('Ordinary exact-request campaign output path required')
        validation=row['validation'];request=row['request']
        if (validation.get('family')!=request['family'] or validation.get('distance_m')!=request['distance_m']
                or validation.get('native_requested') is not request['native']):
            raise ValueError('Campaign case validation differs from its exact physical/native request')
    if any(r['request'] not in value['pending'] or r['output']!='cases/'+identity(r['request']) for r in value['failed']):
        raise ValueError('Failed execution must retain its exact pending request')
    return value


def publish(root=ROOT, *, state=None,output=None):
    root=Path(root);folder=Path(state) if state is not None else root/'build/railway-twin'
    value=_check_campaign(_read(folder/'latest.json'),root)
    target=Path(output) if output is not None else root/OUTPUT
    target.mkdir(parents=True,exist_ok=True)
    files={};summaries=[]
    for row in value['cases']:
        request=row['request']
        if request.get('contract_id')!=value['contract_id'] or row['output']!='cases/'+identity(request):
            raise ValueError('Ordinary exact-request campaign output path required')
        source=folder/row['output']
        result=verify(source,root=root)
        if result!=row['validation']:
            raise ValueError('Campaign execution differs from regenerated validation')
        name=result['request_id']+'.tar.gz'
        buffer=io.BytesIO()
        with tarfile.open(fileobj=buffer,mode='w') as archive:
            for path in sorted(source.rglob('*')):
                if path.is_file():
                    raw=path.read_bytes();item=tarfile.TarInfo(path.relative_to(source).as_posix())
                    item.size=len(raw);item.mtime=0;item.mode=0o644;archive.addfile(item,io.BytesIO(raw))
        (target/name).write_bytes(gzip.compress(buffer.getvalue(),mtime=0))
        files[name]=digest(target/name);summaries.append(dict(archive=name,**result))
    manifest=dict(schema='osr-end-to-end-twin-publication/1',source_sha256=sources(root),
        campaign_id=value['campaign_id'],campaign_record=value,contract=value['contract'],cases=summaries,pending=value['pending'],failed=value['failed'],files_sha256=files,**FLAGS)
    manifest['publication_id']=identity(manifest)
    (target/'manifest.json').write_bytes(encoded(manifest))
    return manifest


def verify_publication(root=ROOT, *, output=None):
    root=Path(root);target=Path(output) if output is not None else root/OUTPUT
    manifest=_read(target/'manifest.json')
    if (manifest.get('schema')!='osr-end-to-end-twin-publication/1'
        or manifest.get('publication_id')!=identity({k:v for k,v in manifest.items() if k!='publication_id'})
        or manifest.get('source_sha256')!=sources(root)):
        raise ValueError('Twin publication source or identity differs')
    _nonpromoting(manifest)
    campaign=_check_campaign(manifest.get('campaign_record',{}),root)
    if any(manifest.get(key)!=campaign[key] for key in ('campaign_id','contract','pending','failed')):
        raise ValueError('Publication differs from exact retained campaign execution')
    indexed={row['validation']['request_id']:row for row in campaign['cases']}
    if len(indexed)!=len(campaign['cases']) or len(indexed)!=len(manifest['cases']):
        raise ValueError('Publication campaign case coverage differs')
    expected=[(f,d) for f in specification(root)['body_families'] for d in specification(root)['distances_m']]
    actual=[(r['family'],r['distance_m']) for r in manifest['cases']+manifest['pending']]
    if sorted(expected)!=sorted(actual):
        raise ValueError('Twin publication request coverage differs')
    for row in manifest['cases']:
        name=row['archive']
        if name!=row['request_id']+'.tar.gz' or Path(name).name!=name or digest(target/name)!=manifest['files_sha256'].get(name):
            raise ValueError('Twin publication archive bytes/path differ')
        summary={k:v for k,v in row.items() if k!='archive'}
        if summary!=indexed.get(row['request_id'],{}).get('validation') or verify_archive(target/name,root=root)!=summary:
            raise ValueError('Twin archive semantic validation differs from publication')
    if set(manifest['files_sha256'])!={r['archive'] for r in manifest['cases']}:
        raise ValueError('Twin archive inventory differs')
    return dict(verified=True,publication_id=manifest['publication_id'],cases=len(manifest['cases']),
        pending=len(manifest['pending']),failed=len(manifest['failed']),engineering_complete=False,**FLAGS)


def verify_archive(path, *, root=ROOT,require_complete=False):
    path=Path(path)
    with tempfile.TemporaryDirectory(prefix='osr-twin-verify-') as temporary:
        with tarfile.open(path,'r:gz') as archive:
            members=archive.getmembers();names=[p.name for p in members]
            if len(names)!=len(set(names)) or len(names)>100 or sum(p.size for p in members)>512*1024**2:
                raise ValueError('Archive count/size budget or unique paths exceeded')
            if any(not p.isfile() or Path(p.name).is_absolute() or '..' in Path(p.name).parts for p in members):
                raise ValueError('Ordinary bounded archive files required')
            archive.extractall(temporary,filter='data')
        return verify(temporary,root=root,require_complete=require_complete)
