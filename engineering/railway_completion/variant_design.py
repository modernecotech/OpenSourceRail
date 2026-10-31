"""Propagate wayside motor rewrites through one complete research candidate.

These alternatives retain passive onboard stock, not inherited motor evidence.
The same changed candidate feeds stock/BOM, brake identity, required motion,
guideway dead loads, delivery drafts and explicit unpriced economic scope.
"""
from copy import deepcopy
from math import fsum
from pathlib import Path
import gzip
import json

from engineering.station_rail import ROOT
from engineering.station_rail.common import identity,digest,encoded
from engineering.design_search import wheel_motor,railway_bundle,system_inventory,system_motion,railway_delivery
from engineering.railway_twin import model as twin_model,pipeline as twin_pipeline
from . import FLAGS,motor,experiments,infrastructure

PRODUCER='engineering/railway_completion/variant_design.py'
KINDS=('reference','wide-return','rewound')
MANIFEST='variant-design-manifest.json'


def _bindings(bundle,body,inventory,ledger,infrastructure_result,motion,civil,delivery,bom,power,economics):
    candidate=bundle['candidate_id']
    railway_bundle.validate(bundle)
    for value in (inventory,ledger,ledger['scene'],infrastructure_result,civil,delivery,bom,power,economics,*[r['result'] for r in motion]):
        if value.get('candidate_id')!=candidate:raise ValueError('Variant stage uses another physical candidate')
    if bundle['body_candidate_id']!=body['candidate_id'] or inventory['body_candidate_id']!=body['candidate_id']:
        raise ValueError('Variant body/inventory definition differs')
    brake=bundle['brake_definition']
    for key in ('candidate_id','body_candidate_id','support_component_id','propulsion_component_id'):
        if brake.get(key)!=bundle[key]:raise ValueError('Variant brake plant uses another body/motor/candidate')
    if any(row['candidate_id']!=candidate for row in bom['engineering_BOM']+bom['manufacturing_BOM']):
        raise ValueError('Variant federated BOM uses another candidate')
    if any(row.get('candidate_id')!=candidate for row in delivery['ERPNext']['items']):
        raise ValueError('Variant delivery draft uses another candidate')


def evaluate(kind='reference',root=ROOT):
    if kind not in KINDS:raise ValueError('Explicit reference, wide-return or rewound primary required')
    root=Path(root)
    base=twin_model.materialize('gfrp_semimonocoque',2000.,root)
    parent=base['bundle']
    if kind=='reference':bundle=deepcopy(parent)
    elif kind=='wide-return':bundle=motor.variant(parent,backiron_m=.1)
    else:bundle=motor.rewound_variant(parent)
    # The old reference-only twin.calculate contract remains untouched. These
    # new physical wayside compositions use its pure ledger/BOM adapters only.
    materialized=deepcopy(base)
    materialized['bundle']=bundle
    parameters=deepcopy(bundle['motor_parameters']);definition=deepcopy(bundle['motor_definition'])
    stock=[p for p in wheel_motor.stock(parameters) if p['installation']=='wayside']
    materialized['propulsion']=dict(parameters=parameters,motor_definition=definition,wayside_stock=stock,
        wiring_hypothesis=motor.wiring_definition(parameters['physical']),
        stock_scope='Bare steel and equivalent-volume copper; full mounted/cooled/converter installation remains unknown',
        available_force_map=None,complete_installed_mass_kg=None,**FLAGS)
    body=materialized['body'];candidate=bundle['candidate_id']
    if bundle['mass']!=parent['mass'] or bundle['support_component_id']!=parent['support_component_id']:
        raise ValueError('Wayside-only rewrite must retain actual onboard stock/mass/support definition')
    inventory=system_inventory.evaluate(body,bundle_id=candidate,source_root=root)
    ledger=twin_model.ledger(materialized,inventory,root)
    scene=ledger['scene']
    infrastructure_result=infrastructure.derive(scene,bundle,ledger)
    contexts=[('empty',dict(load='empty')),('normal',dict(load='normal')),('crowd',dict(load='crowd')),
        ('adverse-normal',dict(load='normal',grade_up_fraction=.02,headwind_m_s=10.,rail_adhesion=.025))]
    motion=[dict(name=name,result=system_motion.evaluate(bundle,available_map=None,scenario_overrides=values)) for name,values in contexts]
    # This is explicitly the old bare-beam stock/load hypothesis plus a new
    # dead-load overlay. Do not relabel it as a complete resized structure.
    bare_civil=railway_bundle.assess_civil(bundle)
    civil=dict(candidate_id=candidate,body_candidate_id=body['candidate_id'],
        bare_beam_hypothesis=bare_civil,guideway_stock_component_id=materialized['selected_civil']['physical_civil_component_id'],
        same_candidate_known_deadload_evaluation_id=infrastructure_result['evaluation_id'],
        base_beam_deadload_scope='Retained analytical template sizes itself for vehicle load and its own counted civil/rail allowances; it omits the new wayside plant',
        complete_beam_reassessment_includes_wayside_plant=False,
        required_reassessment='Use exact new station-primary and account load distributions to revise section, tendons, shear/torsion, bearings, piers, foundations and erection; propagate any physical stock change',**FLAGS)
    delivery=railway_delivery.compile(bundle,body,inventory)
    bom=twin_pipeline._federated_bom(materialized,inventory,scene,ledger)
    request=motor.request(bundle,start_m=0.,speed_m_s=0.,voltage_peak_V=375.,frequency_Hz=30.,steps=4)
    power=experiments.electrical_bound(request)
    bank_count=len(bundle['architecture_case']['physical_definition']['wayside']['bank_starts_from_initial_nose_m'])
    if bank_count!=5 or len(stock)!=486 or any(p['installation']!='wayside' for p in stock):
        raise ValueError('Five physical banks with counted two-sided stock required')
    bare_per_bank=fsum(p['mass_kg'] for p in stock)
    baseline_stock=[p for p in wheel_motor.stock(parent['motor_parameters']) if p['installation']=='wayside']
    baseline_per_bank=fsum(p['mass_kg'] for p in baseline_stock)
    actual_way_rows=[r for r in scene['occurrences'] if r['system']=='wayside/primary']
    if len(actual_way_rows)!=bank_count*len(stock) or abs(fsum(r['mass_kg'] for r in actual_way_rows)-bank_count*bare_per_bank)>1e-6:
        raise ValueError('Installed wayside stock inventory differs from actual variant geometry')
    train_stock=fsum(r['mass_kg'] for r in scene['occurrences'] if r['system'].startswith('vehicle/'))
    residual=fsum(r['accounted_mass_kg'] for r in ledger['unlocated_accounts']
        if r['system'].startswith('vehicle/') and r['accounted_mass_kg'] is not None)
    mass_residual=train_stock+residual-6*bundle['mass']['accounted_tare_kg_per_car']
    if abs(mass_residual)>1e-6:raise ValueError('Wayside rewrite changed the vehicle accounting scope')
    quantities=dict(candidate_id=candidate,motor_component_id=bundle['propulsion_component_id'],
        bank_count=bank_count,primary_face_count=2*bank_count,bank_stock_occurrences=len(stock),
        total_primary_stock_occurrences=len(actual_way_rows),bare_primary_mass_kg_per_bank=bare_per_bank,
        bare_primary_mass_kg_all_banks=bank_count*bare_per_bank,
        added_bare_primary_mass_kg_all_banks=bank_count*(bare_per_bank-baseline_per_bank),
        bare_copper_mass_kg_all_banks=bank_count*fsum(p['mass_kg'] for p in stock if p['role']=='copper-stock'),
        bare_steel_mass_kg_all_banks=bank_count*fsum(p['mass_kg'] for p in stock if p['role']!='copper-stock'),
        accounted_vehicle_mass_kg_per_car=deepcopy(bundle['mass']),unchanged_onboard_stock=True,
        train_account_reconciliation_residual_kg=mass_residual,
        complete_installed_primary_mass_kg=None,complete_installed_train_mass_kg=None,**FLAGS)
    economics=dict(candidate_id=candidate,body_candidate_id=body['candidate_id'],
        federated_BOM_evaluation_id=bom['evaluation_id'],deadload_evaluation_id=infrastructure_result['evaluation_id'],
        propulsion_geometry_id=bundle['propulsion_component_id'],known_bare_primary_mass_kg=bank_count*bare_per_bank,
        unpriced_occurrence_ids=[r['id'] for r in bom['engineering_BOM']],quoted_occurrences=0,
        unit_prices_USD=None,manufacturing_labour_h=None,installed_converter_cooling_and_mount_cost_USD=None,
        complete_installed_CAPEX_USD=None,purchased_energy_kWh=None,whole_life_cost_USD=None,economic_winner=None,
        equal_service_context=dict(cars=6,car_length_m=17.,station_spacing_m=2000.,target_headway_s=120.,normal_capacity_pphpd=8280.),**FLAGS)
    _bindings(bundle,body,inventory,ledger,infrastructure_result,motion,civil,delivery,bom,power,economics)
    producers={PRODUCER:Path(__file__),motor.CODE:Path(motor.__file__),experiments.PRODUCER:Path(experiments.__file__),
        infrastructure.PRODUCER:Path(infrastructure.__file__),twin_model.PRODUCER:Path(twin_model.__file__),
        twin_pipeline.PRODUCER:Path(twin_pipeline.__file__),wheel_motor.PRODUCER:Path(wheel_motor.__file__),
        system_inventory.PRODUCER:Path(system_inventory.__file__),system_motion.PRODUCER:Path(system_motion.__file__),
        railway_bundle.PRODUCER:Path(railway_bundle.__file__),railway_delivery.PRODUCER:Path(railway_delivery.__file__)}
    # The source set must cover the full twin materialization path. A candidate
    # can keep its physical ID while its source-bound definition/evaluation ID
    # changes, so bundle-local hashes alone are not a complete replay contract.
    sources={**twin_pipeline.sources(root),**bundle['source_sha256'],**inventory['source_sha256']}
    for name,loaded in producers.items():
        sources[name]=digest(root/name)
        if sources[name]!=digest(loaded):raise ValueError('Executing variant producer differs from declared source root')
    result=dict(schema='osr-coupled-wayside-variant-design/1',kind=kind,candidate_id=candidate,
        parent_reference_bundle_id=parent['bundle_id'],body_candidate_id=body['candidate_id'],
        support_component_id=bundle['support_component_id'],motor_component_id=bundle['propulsion_component_id'],
        brake_definition_id=bundle['brake_definition']['brake_definition_id'],bundle=bundle,
        inventory=inventory,ledger=ledger,infrastructure=infrastructure_result,motion=motion,civil=civil,
        delivery=delivery,federated_BOM=bom,electrical_bound=power,quantities=quantities,economics=economics,
        stage_bindings=dict(candidate_id=candidate,stage_candidate_ids={name:candidate for name in
            ('stock','inventory','scene','BOM','brakes','required-motion','civil-deadload','delivery','power-bound','economics')},
            body_projection_id=body['candidate_id'],motor_geometry_id=bundle['propulsion_component_id'],
            physical_ancestry_is_not_an_evaluation_or_release=True),
        operating_map_id=None,available_propulsion_verified=False,
        integrated_selection=None,
        open_tasks=['Converge and independently validate actual nonlinear moving force, branch current, steel field and loss maps',
            'Resolve current control, converter limits, section handoff and repeated thermal/cooling duty',
            'Complete 3D coil leads, insulation, mountings, wiring, protection and maintenance access',
            'Reevaluate fin/hanger/coupler force paths and motor normal-force wheel loads for the new primary',
            'Resize/recheck actual civil structure with the changed wayside dead stock, not just the old bare-beam template',
            'Close complete equipment, braking/protection/recovery, site, manufacturing and equal-service whole-life prices'],
        source_sha256=dict(sorted(sources.items())),**FLAGS)
    result['evaluation_id']=identity(result)
    return result


def _manifest(results,files):
    epoch=results[KINDS[0]]['source_sha256']
    if any(r['source_sha256']!=epoch for r in results.values()):
        raise ValueError('Cannot publish a mixed variant source epoch')
    entries=[]
    for kind in KINDS:
        r=results[kind]
        entries.append(dict(kind=kind,candidate_id=r['candidate_id'],evaluation_id=r['evaluation_id'],
            motor_component_id=r['motor_component_id'],brake_definition_id=r['brake_definition_id'],
            body_candidate_id=r['body_candidate_id'],quantities=r['quantities'],electrical_bound=r['electrical_bound'],
            scene_id=r['infrastructure']['scene_id'],infrastructure_evaluation_id=r['infrastructure']['evaluation_id'],
            federated_BOM_evaluation_id=r['federated_BOM']['evaluation_id'],
            infrastructure_span_count=r['infrastructure']['span_count'],
            whole_life_cost_USD=None,operating_map_id=None,**FLAGS))
    value=dict(schema='osr-coupled-wayside-variant-publication/1',kinds=list(KINDS),source_sha256=epoch,
        files_sha256=files,entries=entries,
        scope='Three counted wayside physical compositions with the same passive train. Bare stock, conditional demand, electrical ceilings and guideway deadload overlays do not demonstrate available propulsion, resized civil works, installed price or a qualified railway.',
        integrated_selection=None,**FLAGS)
    value['publication_id']=identity(value)
    return value


def _ordinary(folder,name):
    folder=Path(folder)
    if folder.is_symlink() or (folder/name).is_symlink():
        raise ValueError('Ordinary variant publication paths required')
    return folder/name


def publish(output,root=ROOT):
    """Retain three full deterministic research results without native/ERP effects."""
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    results={kind:evaluate(kind,root=root) for kind in KINDS}
    files={}
    for kind,result in results.items():
        name=kind+'.json.gz';path=_ordinary(output,name)
        path.write_bytes(gzip.compress(encoded(result),mtime=0))
        files[name]=digest(path)
    manifest=_manifest(results,files)
    _ordinary(output,MANIFEST).write_bytes(encoded(manifest))
    return manifest


def verify_publication(output,root=ROOT):
    """Regenerate actual stock and all linked stages, not a resealed receipt."""
    output=Path(output);path=_ordinary(output,MANIFEST)
    manifest=json.loads(path.read_bytes())
    if (manifest.get('schema')!='osr-coupled-wayside-variant-publication/1'
        or manifest.get('publication_id')!=identity({k:value for k,value in manifest.items() if k!='publication_id'})
        or any(manifest.get(flag) is not False for flag in FLAGS)
        or set(manifest.get('files_sha256',{}))!={kind+'.json.gz' for kind in KINDS}):
        raise ValueError('Variant publication schema, identity, inventory or disposition differs')
    results={};files={}
    for kind in KINDS:
        name=kind+'.json.gz';path=_ordinary(output,name)
        if digest(path)!=manifest['files_sha256'][name]:raise ValueError('Variant publication payload bytes differ')
        with gzip.open(path,'rb') as stream:
            raw=stream.read(128*1024**2+1)
        if len(raw)>128*1024**2:raise ValueError('Bounded variant research payload required')
        actual=json.loads(raw);expected=evaluate(kind,root=root)
        if encoded(actual)!=encoded(expected):raise ValueError('Variant semantic replay differs: '+kind)
        results[kind]=expected;files[name]=digest(path)
    if encoded(manifest)!=encoded(_manifest(results,files)):
        raise ValueError('Variant publication source or semantic index differs')
    return dict(verified=True,publication_id=manifest['publication_id'],variants=3,
        candidate_ids=[results[k]['candidate_id'] for k in KINDS],
        operating_maps=0,integrated_selection=None,**FLAGS)
