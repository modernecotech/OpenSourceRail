"""Delivery sidecars for the optional CAD pilot, without repricing a railway.

Analytical material regions are not purchase orders.  Selected subsets link the
existing same-candidate delivery packet; the standalone shuttle inherits none of
its costs or IFC.  All process routes below are unqualified design hypotheses.
"""
from copy import deepcopy
from hashlib import sha256
from math import fsum
from pathlib import Path
import gzip
import io
import json
import tomllib

from .cases import ROOT, FLAGS, identity, measures, verify_case


SCHEMA = 'osr-craft-delivery-sidecar/1'
PRODUCER = 'engineering/design_search/craft_backends/handoff.py'
_LOADED = sha256(Path(__file__).read_bytes()).hexdigest()
POLICY = 'engineering/outline/supply-policy.toml'
SUPPLY = 'docs/design-engine/supply-economics'
EXPORTS = 'docs/design-engine/current/exports'
_EXPORT_FILES = {
    'engineering-bom.json.gz': 'engineering-bom',
    'manufacturing.json': 'manufacturing',
    'procurement.json.gz': 'procurement',
    'assembly.json': 'assembly',
    'civil.json': 'civil',
    'selected-vehicle-cost.json': 'vehicle-cost',
    'selected-system-cost.json': 'system-cost',
    'bim.json': 'bim-scope',
    'selected-interface.ifc': 'existing-interface-ifc',
}


def _file(root, name):
    relative = Path(name)
    if relative.is_absolute() or '..' in relative.parts or not relative.parts:
        raise ValueError('Ordinary relative source path required')
    target = root / relative
    for part in (target, *target.parents):
        if part == root:
            break
        if part.is_symlink():
            raise ValueError('Linked delivery source is not admitted')
    if not target.is_file() or target.stat().st_size > 64 * 1024**2:
        raise ValueError('Bounded ordinary delivery source required: ' + name)
    return target


def _hash(root, name):
    return sha256(_file(root, name).read_bytes()).hexdigest()


def _json(root, name):
    raw = _file(root, name).read_bytes()
    if name.endswith('.gz'):
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(32 * 1024**2 + 1)
    if len(raw) > 32 * 1024**2:
        raise ValueError('Delivery source exceeds decompression budget')
    return json.loads(raw)


def _identity(value, field):
    if value.get(field) != identity({k:v for k,v in value.items() if k != field}):
        raise ValueError('Delivery publication identity differs: ' + field)


def _unreleased(value):
    for key in FLAGS:
        if key in value and value[key] is not False:
            raise ValueError('Delivery sidecar cannot inherit promotion: ' + key)


def _supply(root):
    policy = tomllib.loads(_file(root, POLICY).read_text())
    if (policy.get('schema') != 'osr-project-supply-policy/1'
            or policy.get('physical_reference_changed') is not False):
        raise ValueError('Explicit non-promoting supply policy required')
    data_name = policy['evidence']
    data = _json(root, data_name)
    _identity(data, 'dataset_id')
    manifest_name = SUPPLY+'/manifest.json'
    summary_name = SUPPLY+'/summary.json'
    manifest = _json(root, manifest_name)
    summary = _json(root, summary_name)
    _identity(manifest, 'manifest_id')
    _unreleased(manifest); _unreleased(summary)
    if (manifest['files_sha256']['summary.json'] != _hash(root, summary_name)
            or manifest['source_sha256'][POLICY] != _hash(root, POLICY)
            or manifest['source_sha256'][data_name] != _hash(root, data_name)
            or summary['evaluation_id'] != manifest['evaluation_id']
            or summary['policy'] != policy):
        raise ValueError('Supply policy, observations or comparison binding differs')
    refs = {name:_hash(root,name) for name in (POLICY,data_name,manifest_name,summary_name)}
    return dict(
        policy=deepcopy(policy),
        policy_path=POLICY, observations_path=data_name,
        observations_dataset_id=data['dataset_id'],
        comparison_manifest_path=manifest_name,
        comparison_manifest_id=manifest['manifest_id'],
        comparison_evaluation_id=manifest['evaluation_id'],
        comparison_summary_path=summary_name,
        use='Policy and comparison evidence only; no rates, totals or procurement approval transferred to this component',
        additional_blanket_discount=None,
        factory_capital_allocation=None,
        cost_recalculated=False,
        source_validation='Direct payload hashes, canonical IDs and matching policy/data inputs; full historical supply run not replayed',
    ), refs


def sources(root=ROOT):
    """Direct shared policy sources; selected delivery files are added by build.

    Keeping the shared catalogue separate prevents a research component from
    acquiring the selected train's cost or IFC bindings merely by using a policy.
    """
    root = Path(root).resolve()
    if sha256(Path(__file__).read_bytes()).hexdigest() != _LOADED:
        raise ValueError('Delivery sidecar producer changed during execution')
    _, refs = _supply(root)
    refs[PRODUCER] = _LOADED
    return dict(sorted(refs.items()))


def _ids(value):
    return {k:deepcopy(v) for k,v in value.items()
            if k.endswith('_id') or k in ('input_evaluation_ids',)}


def _selected(case, root):
    """Read only already-published same-candidate packages, never regenerate."""
    manifest_name = EXPORTS+'/manifest.json'
    manifest = _json(root, manifest_name)
    _identity(manifest, 'manifest_id'); _unreleased(manifest)
    for key, expected in (
            ('candidate_id',case['candidate_id']),
            ('selection_id',case['source_selection_id']),
            ('evaluation_id',case['source_evaluation_id'])):
        if manifest.get(key) != expected:
            raise ValueError('Mixed selected delivery '+key)
    refs = {manifest_name:_hash(root,manifest_name)}
    # Record and verify implementation inputs as well as generated payloads.
    for name, expected in manifest['source_sha256'].items():
        if _hash(root,name) != expected:
            raise ValueError('Selected delivery implementation source changed: '+name)
        refs[name] = expected
    links = []
    records = {}
    for name, role in _EXPORT_FILES.items():
        path = EXPORTS+'/'+name
        actual = _hash(root,path)
        if actual != manifest['files_sha256'].get(name):
            raise ValueError('Selected delivery payload differs: '+name)
        refs[path] = actual
        if name.endswith('.ifc'):
            continue
        value = _json(root,path); _unreleased(value)
        for key in ('candidate_id','body_candidate_id','selection_id',
                    'support_component_id','propulsion_component_id'):
            if value.get(key) != manifest.get(key):
                raise ValueError('Mixed '+role+' '+key)
        if 'evaluation_id' in value and value['evaluation_id'] != manifest['evaluation_id']:
            raise ValueError('Mixed '+role+' evaluation_id')
        records[role] = value
        links.append(dict(role=role, path=path, sha256=actual,
                          schema=value['schema'], ids=_ids(value),
                          relationship='existing selected-candidate packet, not a new component charge'))
    bim = records['bim-scope']
    links.append(dict(role='existing-interface-ifc', path=EXPORTS+'/selected-interface.ifc',
                      sha256=refs[EXPORTS+'/selected-interface.ifc'],
                      ids={**_ids(bim),'delivery_manifest_id':manifest['manifest_id']},
                      scope=bim['scope'], complete_vehicle_IFC=bim['complete_vehicle_IFC'],
                      complete_civil_IFC=bim['complete_civil_IFC'],
                      relationship='Existing interface export only; no new case geometry has been exported or independently reopened here'))
    # The system report intentionally carries a different evaluation candidate.
    # Preserve that field and its original line IDs, rather than relabelling it.
    system = records['system-cost']; vehicle = records['vehicle-cost']
    for line in system['cost_line_items']:
        if line['candidate_id'] != system['evaluation_candidate_id']:
            raise ValueError('Mixed system-cost evaluation candidate')
    for line in vehicle['lines']:
        if line['candidate_id'] != case['candidate_id']:
            raise ValueError('Mixed vehicle-cost physical candidate')
    return dict(manifest_path=manifest_name, manifest_id=manifest['manifest_id'],
                ids=_ids(manifest), links=links), records, refs


def _route(case, entity):
    """One route hypothesis per material region, not an asserted bought part."""
    cid = case['case_id']; eid = entity['id']
    if cid == 'selected-beam20m':
        return dict(group_id='one-monolithic-20m-precast-span',
                    representation='material region of one beam; six regions are not six fabricated beams',
                    stock='Concrete mix plus separately designed reinforcement, prestress, anchors and inserts',
                    operations=['Prepare reusable mould and cage/tendon layout',
                                'Batch, place, compact and cure concrete',
                                'Stress and release only under an engineered procedure',
                                'Inspect dimensions, material results and lifting interfaces'],
                    qa=['Concrete batch/cure traceability', 'Reinforcement cover and tendon/anchor inspection',
                        'Verify lifting, bearings and temporary stability before erection'])
    if cid == 'selected-side-sill':
        return dict(group_id='one-side-sill-hollow-profile',
                    representation='Four wall regions of one sill; do not order four complete extrusions',
                    stock='6082-T6 hollow extrusion is a hypothesis; welded alternative needs a separate joint and heat-affected-zone evaluation',
                    operations=['Select feasible hollow-profile supplier/process and cut to length',
                                'Machine mounting features and fixture installed datums',
                                'Join under an engineered procedure and inspect distortion'],
                    qa=['Alloy/temper and dimensions', 'Joint qualification and attachment load paths',
                        'Twist, end interfaces, corrosion isolation and maintenance access'])
    if cid == 'asymmetric-si-control':
        return dict(group_id='analytic-unit-control', representation='Calibration box, not a railway part',
                    stock='Hypothetical aluminium coupon', operations=['Verify SI dimensions and placement only'],
                    qa=['Compare analytical volume, centroid and AABB; no manufacture claimed'])
    if entity['material'].endswith('unresolved'):
        stock = 'Material and grade unresolved; no density or price substituted'
        operations = ['Define function, material, actual section, attachment and production method before routing']
    elif '/guide-wheel/' in eid or '/guide-axle/' in eid or 'parking-pin' in eid:
        stock = 'Proposed steel stock; grade, heat treatment, bearing fits and net section unresolved'
        operations = ['Select stock and grade', 'Turn/machine or procure an independently specified item',
                      'Finish and inspect interfaces before assembly']
    else:
        stock = 'Proposed fabricated steel stock; the rendered box is an envelope, not a plate/cut list'
        operations = ['Resolve wall thickness, joints and stock forms',
                      'Cut/form/machine and fixture using a qualified future procedure',
                      'Join, protect and inspect']
    return dict(group_id='standalone-research-launch-shuttle',
                representation='Source-layout material/envelope occurrence; overlaps and net fabrication stock unresolved',
                stock=stock, operations=operations,
                qa=['Material traceability, geometry and attachment inspection',
                    'Define contact wear, fatigue, containment and release/parking verification before service'])


def _cost_links(case, entity, records):
    if not records:
        return []
    source_id = entity['source_entity'].get('source_part_id')
    result = []
    for line in records['vehicle-cost']['lines']:
        if source_id is not None and source_id in line.get('occurrence_ids',[]):
            result.append(dict(role='vehicle-cost', path=EXPORTS+'/selected-vehicle-cost.json',
                               line_id=line['line_id'], line_key=line['line_key'],
                               source_occurrence_id=source_id,
                               coverage='Existing grouped line includes this occurrence; no prorated amount assigned'))
    for line in records['system-cost']['cost_line_items']:
        match = source_id is not None and source_id in line.get('physical_part_ids',[])
        concrete = case['case_id']=='selected-beam20m' and line['line_key']=='precast-beam-concrete-recipe'
        if match or concrete:
            result.append(dict(role='system-cost', path=EXPORTS+'/selected-system-cost.json',
                               line_id=line['line_id'], line_key=line['line_key'],
                               source_occurrence_id=source_id,
                               coverage=('Existing whole-route concrete recipe; no per-region cost or new quantity charged'
                                         if concrete else 'Existing physical-occurrence line; no new charge'),
                               evaluation_candidate_id=line['candidate_id']))
    return result


def build(case, root=ROOT):
    """Return a deterministic, immutable-by-convention delivery draft in SI.

    No solver, CAD regeneration, ERP write, supplier request or financial total
    is executed.  Unknown or unallocated costs remain null, never free.
    """
    root = Path(root).resolve()
    verify_case(case,root)
    refs = sources(root)
    policy, _ = _supply(root)
    refs.update(case['source_sha256'])
    selected = case['source_candidate_id'] is not None
    delivery = None; records = {}
    if selected:
        delivery, records, linked_sources = _selected(case,root)
        refs.update(linked_sources)
    parts = []
    for entity in case['entities']:
        material = case['materials'][entity['material']]
        quantity = measures(entity)
        density = material['density_kg_m3']
        mass = None if density is None else quantity['volume_m3']*density
        route = _route(case,entity)
        parts.append(dict(
            occurrence_id=entity['id'], candidate_id=case['candidate_id'],
            component_geometry_id=case['component_geometry_id'],
            material_id=entity['material'], material_basis=deepcopy(material),
            volume_m3=quantity['volume_m3'], density_kg_m3=density,
            material_mass_kg=mass,
            quantity_scope='Analytical occurrence material/envelope volume; not net purchased stock or complete installed mass',
            installed_geometry=deepcopy(entity['geometry']),
            source_entity_id=entity['source_entity']['id'],
            render_offset_applied=False,
            stock_and_process_hypothesis={**route, 'qualified_process':False,
                                          'purchase_stock_quantity':None,
                                          'labour_hours':None,'machine_hours':None},
            assembly_notes=['Retain source installed coordinates; do not use exploded render offsets',
                            'Connections, fasteners, tolerances, interference and removal paths require detailed design'],
            existing_cost_line_links=_cost_links(case,entity,records),
            allocated_component_cost=None,
            cost_status=('Existing selected estimate referenced; this subset has no additional charge or allocation'
                         if selected else 'Not estimated for this standalone component; no selected costs inherited'),
        ))
    unknowns = [p['occurrence_id'] for p in parts if p['material_mass_kg'] is None]
    missing = [
        'Complete installed hardware: joints, fasteners, protection, wiring, services and access envelopes',
        'Verified material grades, strengths, joints, fatigue/buckling and accepted load limits',
        'Executable manufacturing routing, tooling, operators, scrap/rework, inspection and measured production times',
        'Per-component purchased stock, process, tooling, QA, logistics and installation cost allocation',
    ]
    if not selected:
        missing += ['Standalone component BOM, procurement and current component cost estimate',
                    'Component-specific CAD/BIM interchange and independent geometry verification']
    if case['case_id']=='research-launch-shuttle':
        missing += ['Train coupling/contact geometry, available force, controlled engagement and independent braking',
                    'Storage, actuator, cable/hydraulic, reset and repeated-duty dynamics',
                    'Guards, bearings, foundation reactions, control protection and maintenance/recovery hardware',
                    'Manufactured, installed and 30-year maintenance/renewal costs for a complete station system']
    value = dict(
        schema=SCHEMA, case_id=case['case_id'], case_definition_id=case['case_definition_id'],
        candidate_id=case['candidate_id'], component_geometry_id=case['component_geometry_id'],
        source_candidate_id=case['source_candidate_id'], source_evaluation_id=case['source_evaluation_id'],
        source_selection_id=case['source_selection_id'], source_study_id=case['source_study_id'],
        units=deepcopy(case['units']), scope=case['scope'], assumptions=deepcopy(case['assumptions']),
        occurrences=parts,
        quantities=dict(occurrence_count=len(parts),
                        summed_occurrence_volume_m3=fsum(p['volume_m3'] for p in parts),
                        known_material_mass_subtotal_kg=fsum(p['material_mass_kg'] for p in parts if p['material_mass_kg'] is not None),
                        total_material_mass_kg=(None if unknowns else fsum(p['material_mass_kg'] for p in parts)),
                        unknown_material_mass_occurrences=unknowns,
                        gross_stock_not_installed_qualification=True,
                        net_purchase_stock_quantity=None),
        selected_delivery=delivery, supply_policy=policy,
        cost_accounting=dict(
            mode='reference-existing-only' if selected else 'standalone-estimate-pending',
            additive_cost=False, incremental_cost=None, allocated_component_cost=None,
            totals_recalculated=False, currency=None,
            reason='No new component amounts are added; published vehicle/system reports have overlapping scopes and must never be summed',
            selected_costs_referenced=selected, selected_costs_inherited=False,
            supply_comparison_is_selected_cost_replacement=False),
        manufacturing_status='Unqualified route hypotheses; no work order or production release',
        assembly_status='Source material regions/layout preserved; assembly and interfaces not verified',
        missing_engineering_and_cost_scope=missing,
        source_sha256=dict(sorted(refs.items())),
        erp_records_written=False, native_tools_executed=False,
        **FLAGS,
    )
    if records:
        value['selected_packet_scope'] = dict(
            complete_installed_BOM=records['engineering-bom']['complete_installed_BOM'],
            procurement_price_USD=records['procurement']['total_price_USD'],
            procurement_prices_current=records['procurement']['prices_current'],
            production_shift_basis=deepcopy(records['vehicle-cost']['shifts']['production_per_day']),
            production_schedule_id=records['manufacturing']['line_linked_process_hour_schedule']['schedule_id'],
            vehicle_cost_estimate_id=records['vehicle-cost']['cost_estimate_id'],
            system_cost_estimate_id=records['system-cost']['cost_estimate_id'],
            system_evaluation_candidate_id=records['system-cost']['evaluation_candidate_id'],
            vehicle_cost_scope=deepcopy(records['vehicle-cost']['scope_status']),
            system_cost_scope=deepcopy(records['system-cost']['cost_scope_status']),
            system_missing_cost_scopes=deepcopy(records['system-cost']['missing_cost_scopes']),
            system_propulsion_selected=records['system-cost']['active_installed_propulsion_selected'],
            component_cost_allocation_complete=False,
            note='Draft source packet retained as-is; cost completeness applies only to its declared model and not this component or an installed railway',
        )
    value['handoff_id'] = identity(value)
    return value
