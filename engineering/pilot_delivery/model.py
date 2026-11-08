"""Compile counted parts and reviewed-source routes into an unapproved task draft.

No CAD is generated here. Native artifacts, measured process rates, accepted
serials and business transactions cannot be inferred from this planning view.
"""
from collections import Counter, defaultdict
from copy import deepcopy
from math import fsum, isfinite
from pathlib import Path
import json

from engineering.station_rail.common import identity, digest
from engineering.railway_closure.bundle import combine
from . import ROOT, FLAGS

CASES = ('low', 'base', 'high')
POLICY = 'engineering/pilot_delivery/policy.json'
SOURCE_FILES = ('VERSION', 'engineering/station_rail/common.py', POLICY, 'engineering/pilot_delivery/__init__.py',
                'engineering/pilot_delivery/model.py', 'engineering/pilot_delivery/export.py',
                'engineering/pilot_delivery/__main__.py',
                'engineering/railway_closure/bundle.py',
                'services/integration/osr_integration/engineering.py',
                'services/integration/osr_integration/config.py',
                'services/integration/osr_integration/manufacturing.py')
LIMITATIONS = [
    'Calculated planning draft only; no manufacturing, engineering or operating acceptance.',
    'Stock geometry and proposed positions are not controlled finished drawings, mating fits or collision-free installed assemblies.',
    'No actual ERP Item mapping, released BOM, work order, purchase order, serial installation or supplier quotation is created.',
    'Capacity hours are declared Class A proxies; validated hours, actual crew count and calendar dates remain unknown.',
    'Existing direct part/process and full-system cost ledgers remain authoritative. Capacity hours and civil decomposition are non-additive.',
    'Civil decomposition covers the declared running beams and shared bents; terminal structure, turnouts, site services and equipment need further detail.',
    'No CAD, mesh or physical solver is executed by this compiler; numerical agreement does not establish qualified hardware.',
    'Material certificates, process qualification, release dimensions/tolerances, fatigue, electrical protection and independent safety evidence remain open.',
]


def seal(value, key='evaluation_id'):
    value[key] = identity(value)
    return value


def sealed(value, key='evaluation_id'):
    if value.get(key) != identity({k: v for k, v in value.items() if k != key}):
        raise ValueError('Unsealed or changed ' + key)
    return value


def sources(root=ROOT):
    return {n: digest(Path(root) / n) for n in SOURCE_FILES}


def positive(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value <= 0:
        raise ValueError('Positive finite ' + name + ' required')
    return value


def ranges(values, *, positive_only=True):
    if not isinstance(values, dict) or set(values) != set(CASES):
        raise ValueError('Explicit low/base/high bounds required')
    for c in CASES:
        if positive_only:
            positive(values[c], c)
        elif not isinstance(values[c], (float, int)) or isinstance(values[c], bool) or not isfinite(values[c]) or values[c] < 0:
            raise ValueError('Nonnegative finite bound required')
    if not values['low'] <= values['base'] <= values['high']:
        raise ValueError('Unordered bounds')
    return values


def guard_draft(value):
    """Fail closed on release, execution and control requests, including re-sealed input."""
    forbidden = {'movement_authority', 'safety_command', 'safety_commands', 'control_commands',
                 'gateway_commands', 'commands', 'automatic_approval', 'automatic_order_release',
                 'manufacturing_release', 'operating_release', 'physical_accepted',
                 'engineering_accepted', 'selected_reference_changed', 'transactions_performed',
                 'construction_release',
                 'serial_number_assigned', 'installation_accepted', 'production_instruction_released',
                 'approval', 'approval_request', 'release_requests', 'safety_command_request'}
    if isinstance(value, dict):
        for key, item in value.items():
            if (key in forbidden or key.endswith('_approved')) and item not in (None, False, {}, []):
                raise ValueError('Draft cannot request release or safety commands: ' + key)
            if key == 'docstatus' and (type(item) is not int or item != 0):
                raise ValueError('Only draft docstatus 0 is permitted')
            if key == 'status' and isinstance(item, str) and item.lower() in {'approved', 'released', 'submitted', 'installed', 'accepted'}:
                raise ValueError('Accepted business status is not a planning draft')
            guard_draft(item)
    elif isinstance(value, list):
        for item in value:
            guard_draft(item)


def _source_map(study, body, root):
    result = {}
    for owner in (study, body, study['installed'], study['civil']):
        for name, expected in owner['source_sha256'].items():
            path = Path(name)
            if path.is_absolute() or '..' in path.parts:
                raise ValueError('Source path escapes repository')
            if name in result and result[name] != expected:
                raise ValueError('Conflicting source identities: ' + name)
            if digest(Path(root) / path) != expected:
                raise ValueError('Upstream source changed: ' + name)
            result[name] = expected
    for name, expected in sources(root).items():
        if name in result and result[name] != expected:
            raise ValueError('Compiler conflicts with input source')
        result[name] = expected
    return dict(sorted(result.items()))


def _input_validation(study, body, service_id, root):
    if study.get('schema') != 'osr-railway-closure-study/1' or body.get('schema') != 'osr-vehicle-installation/1':
        raise ValueError('Sealed railway closure study and installed body required')
    sealed(study, 'study_id'); sealed(body)
    if identity(body['physical_definition']) != body['candidate_id']:
        raise ValueError('Body physical identity differs')
    installed, civil, bundle = study['installed'], study['civil'], study['bundle']
    sealed(installed); sealed(civil); sealed(bundle)
    canonical = combine(installed, civil)
    if bundle != canonical:
        raise ValueError('Mixed canonical railway bundle')
    if (body['candidate_id'] != study['body_candidate_id'] or body['evaluation_id'] != study['body_evaluation_id']
            or body['candidate_id'] != installed['vehicle_candidate_id'] or body['evaluation_id'] != installed['body_evaluation_id']
            or body['evaluation_id'] != bundle['body_evaluation_id']):
        raise ValueError('Mixed body candidate or engineering revision')
    for packet in (study, body, installed, civil, bundle):
        for flag in ('engineering_accepted', 'physical_accepted', 'manufacturing_release', 'operating_release',
                     'movement_authority', 'selected_reference_changed'):
            if packet.get(flag) is not False:
                raise ValueError('Explicit research-only flag required: ' + flag)
    records = [r for r in study['records'] if r['experiment'] == 'nominal' and r['service']['evaluation_id'] == service_id]
    if len(records) != 1:
        raise ValueError('Select one explicit nominal service evaluation, not a fault record or implicit default')
    record = records[0]; service = record['service']; cost = record['cost']
    for value in (service, cost['core'], cost['full_scope']):
        sealed(value)
        if value['candidate_id'] != bundle['candidate_id']:
            raise ValueError('Mixed service or cost candidate')
    if record['request']['candidate_id'] != bundle['candidate_id'] or record['result']['candidate_id'] != bundle['candidate_id']:
        raise ValueError('Mixed native journey candidate')
    if (cost['canonical_bundle'] != bundle or cost['civil_cost_evaluation_id'] != civil['evaluation_id']
            or cost['installed_mass_evaluation_id'] != installed['evaluation_id']):
        raise ValueError('Mixed civil or mass cost evaluation')
    for value in (cost['core'], cost['full_scope']):
        if (value['body_candidate_id'] != body['candidate_id'] or value['mass_evaluation_id'] != installed['evaluation_id']
                or value['body_bundle_id'] != body['parent_bundle_id']):
            raise ValueError('Mixed cost body bundle or mass revision')
    if cost['full_scope']['input_cost_evaluation_id'] != cost['core']['evaluation_id']:
        raise ValueError('Lifecycle belongs to another cost evaluation')
    if record.get('energy') is not None:
        energy = sealed(record['energy'])
        if (energy['candidate_id'] != bundle['candidate_id'] or energy['service_evaluation_id'] != service_id
                or cost['core']['journey_evaluation_id'] != energy['evaluation_id']):
            raise ValueError('Mixed energy or service evaluation')
    fleet = positive(service['total_trainsets'], 'fleet')
    if type(fleet) is not int or fleet != service['active_trainsets'] + service['spare_trainsets']:
        raise ValueError('Integer fleet count must include active and spare trains exactly once')
    p = civil['parts']; physical = civil['physical_definition']; span = physical['beam_stock']['span_m']
    route_m = cost['full_scope']['route_km'] * 1000
    if (p['civil_candidate_id'] != civil['civil_candidate_id'] or p['beam_instances'] * span != 2 * route_m
            or p['shared_bent_instances'] != p['beam_instances'] // 2 + 1
            or p['beam_instances'] % 2 or physical['segment_count'] != 2):
        raise ValueError('Mixed civil beams, spans, bents or route quantities')
    if p.get('additive_mass_or_cost_ledger') is not False:
        raise ValueError('Civil parts are a non-additive decomposition of existing owners')
    return record, _source_map(study, body, root)


def _binding(study, body, record):
    return dict(candidate_id=study['bundle']['candidate_id'],
        bundle_evaluation_id=study['bundle']['evaluation_id'], study_id=study['study_id'],
        engineering_revision=body['evaluation_id'], body_candidate_id=body['candidate_id'],
        source_body_bundle_id=body['parent_bundle_id'],
        installed_component_candidate_id=study['installed']['candidate_id'],
        installed_mass_evaluation_id=study['installed']['evaluation_id'],
        civil_candidate_id=study['civil']['civil_candidate_id'], civil_evaluation_id=study['civil']['evaluation_id'],
        service_evaluation_id=record['service']['evaluation_id'],
        cost_evaluation_id=record['cost']['core']['evaluation_id'],
        lifecycle_evaluation_id=record['cost']['full_scope']['evaluation_id'])


def _make_buy_mapping(source):
    mappings = {
        'local-fabricate': ('local-fabricate', False),
        'buy-standard': ('buy-standard', False),
        'buy-qualified': ('buy-qualified', False),
        'make': ('local-fabricate', True),
        'bounded-purchased-or-processed': ('unresolved-buy-or-process', True),
    }
    if source not in mappings:
        raise ValueError('Unclassified make/buy route: ' + source)
    route, review = mappings[source]
    return dict(source_category=source, planning_route=route, requires_route_review=review,
                basis='Explicit planning-category conversion only; no supplier, process qualification or release inferred')


def _hours(part, patterns, fleet, policy):
    q = part['quantity_per_train'] * fleet
    route = _make_buy_mapping(part['make_buy'])['planning_route']
    if route == 'local-fabricate':
        values = {c: policy['fabricate_setup_person_h_per_type'][c]
                  + fleet * fsum(r['mass_kg'][c] for r in patterns) * policy['fabricate_person_h_per_gross_kg'][c]
                  + q * policy['fabricate_handling_person_h_per_piece'][c] for c in CASES}
    elif route in ('buy-standard', 'buy-qualified'):
        values = {c: policy['purchased_setup_person_h_per_type'][c]
                  + q * policy['purchased_inspect_handle_person_h_per_piece'][c] for c in CASES}
    else:
        return dict(provisional_person_h=None, validated_person_h=None, additive_cost=False,
            basis=policy['basis'], hold_reason='Bounded component mass/cost does not determine whether it is purchased or processed, or establish process hours; review route first')
    return dict(provisional_person_h=ranges(values), validated_person_h=None,
                additive_cost=False, basis=policy['basis'], hold_reason=None)


def _task(binding, task_id, kind, subject, operation, holds=()):
    return dict(id=task_id, identities=binding, kind=kind, subject=subject, operation=operation,
                status='held' if holds else 'ready-for-planning-review', holds=list(holds),
                docstatus=0, automatic_order_release=False)


def _parts(body, binding, fleet, policy):
    materials = {r['id']: r for r in body['materials']}
    groups = defaultdict(list)
    ids = set()
    for p in body['patterns']:
        if p['id'] in ids:
            raise ValueError('Repeated occurrence-pattern identity')
        ids.add(p['id']); positive(p['count'], 'pattern count')
        if type(p['count']) is not int:
            raise ValueError('Integer occurrence count required')
        ranges(p['mass_kg']); ranges(p['direct_cost_usd'])
        groups[p['part_id']].append(p)
    items=[]; tasks=[]; occurrence_index=[]
    for p in body['parts']:
        rows=groups.pop(p['id'], [])
        if p['material_id'] not in materials or sum(r['count'] for r in rows) != p['quantity_per_train']:
            raise ValueError('Missing material or occurrence/part quantity mismatch: ' + p['id'])
        q=positive(p['quantity_per_train'], 'part quantity')
        item = dict(id=p['id'], identities=binding, component_definition_id=p['component_definition_id'],
            source_component_candidate_id=p['candidate_id'], source_part_id=p['source_part_id'],
            name=p['name'], assembly_id=p['assembly_id'], material_id=p['material_id'],
            quantity_per_train=q, project_fleet=fleet, quantity_project=q*fleet, unit=p['unit'],
            stock=deepcopy(p['stock']), mass_basis=deepcopy(p['mass_basis']),
            counted_pattern_mass_kg_per_train={c:fsum(r['mass_kg'][c] for r in rows) for c in CASES},
            counted_direct_parts_process_usd_per_train={c:fsum(r['direct_cost_usd'][c] for r in rows) for c in CASES},
            make_buy=p['make_buy'], make_buy_mapping=_make_buy_mapping(p['make_buy']), manufacturing=deepcopy(p['manufacturing']),
            inspection=deepcopy(p['inspection']), joining=p['joining'], mounting=p['mounting'],
            maintenance_removal=p['maintenance_removal'], finish=p['finish'], tolerance_and_fits=p['tolerance_and_fits'],
            source_ids=deepcopy(p['source_ids']), open_tasks=deepcopy(p['open_tasks']),
            drawing_reference=None, inspection_release_reference=None, qualified_supplier=None,
            cost_basis=p['cost_basis'], capacity=_hours(p,rows,fleet,policy),
            stock_definition_complete=all(r['geometry']['exact_stock'] for r in rows),
            finished_geometry_verified=all(r['geometry'].get('finished_geometry_verified') is True for r in rows),
            serial_plan=dict(mode='lot plus occurrence record; serialise safety/repair-critical assemblies after reviewed allocation',
                component_definition_id=p['component_definition_id'], engineering_revision=body['evaluation_id'],
                occurrence_pattern_ids=[r['id'] for r in rows], serial_number=None,
                lot_number=None, serial_number_assigned=False, installation_accepted=False),
            BOP_partition=bool(p.get('BOP_partition',False)))
        items.append(item)
        if item['capacity']['provisional_person_h'] is None:
            tasks.append(_task(binding,'hold/time-route/'+p['id'],'process-time-review',p['id'],
                'Resolve make/buy/process route and obtain bounded process-time evidence',
                [item['capacity']['hold_reason']]))
        tasks.append(_task(binding,'review/part/'+p['id'],'manufacturing-planning',p['id'],
            'Review stock, local make/buy route, process, inspection and supplier evidence request; no order issue'))
        tasks.append(_task(binding,'hold/part/'+p['id'],'manufacturing-release',p['id'],
            'Convert engineering definition to controlled drawing, native ERP Item and reviewed production route',
            ['Controlled finished drawing, datums, tolerances and material/process evidence missing',*p['open_tasks']]))
        occurrence_index.extend(dict(id=r['id'], identities=binding, component_definition_id=p['component_definition_id'],
            part_id=p['id'], assembly_occurrence_id=r['assembly_occurrence_id'], count_per_train=r['count'],
            positions_m=deepcopy(r['positions_m']), rotation=deepcopy(r['rotation']),
            project_identity_rule='proposal train index + source occurrence-pattern ID + local ordinal; not an installed serial',
            proposed_position_not_measurement=True) for r in rows)
    if groups or len({p['id'] for p in items}) != len(items):
        raise ValueError('Orphan or repeated part definition')
    if sum(p['quantity_per_train'] for p in items) != body['total_occurrences']:
        raise ValueError('Body occurrence total mismatch')
    for c in CASES:
        actual=fsum(p['counted_direct_parts_process_usd_per_train'][c] for p in items)
        if abs(actual-body['direct_parts_process_usd'][c]) > max(1e-6,1e-10*abs(actual)):
            raise ValueError('Parts do not reconcile to existing direct cost subtotal')
    return items, occurrence_index, tasks, list(materials.values())


def _assemblies(body, binding, fleet, policy):
    rows=[]; tasks=[]
    parts_by_assembly=defaultdict(list)
    for part in body['parts']:
        parts_by_assembly[part['assembly_id']].append(part)
    original_routes={r['assembly_id']: r for r in body['assembly_plans']['plans']}
    if len(original_routes)!=len(body['assembly_plans']['plans']):
        raise ValueError('Repeated source assembly route')
    all_part_ids={p['id'] for p in body['parts']}
    for assembly_id, current_parts in parts_by_assembly.items():
        source=original_routes.get(assembly_id)
        current_ids=sorted(p['id'] for p in current_parts)
        source_ids=[] if source is None else deepcopy(source['component_type_ids'])
        source_steps=[] if source is None else deepcopy(source['source_assembly_steps'])
        pattern_assembly_ids=sorted({p['assembly_occurrence_id'] for p in body['patterns']
                                     if p['part_id'] in current_ids})
        anchors=body['assembly_occurrences'].get(assembly_id,[])
        occurrences=sorted(a['id'] for a in anchors)
        if not occurrences or len(occurrences)!=len(set(occurrences)) or not pattern_assembly_ids:
            raise ValueError('Current assembly requires explicit unique body anchors and counted patterns')
        missing=sorted((set(source_ids)|{i for step in source_steps for i in step.get('part_ids',[])})-all_part_ids)
        steps=deepcopy(source_steps)
        for step in steps:
            named=step.get('part_ids',[])
            step['source_part_ids']=deepcopy(named)
            step['part_ids']=[i for i in named if i in current_ids]
            step['unresolved_source_part_ids']=[i for i in named if i not in current_ids]
            step['route_status']='held-source-route-needs-revision' if step['unresolved_source_part_ids'] else 'proposed-source-route'
        added=sorted(set(current_ids)-set(source_ids))
        # New current definitions receive preparation proposals from their own
        # process records. They do not inherit approval from an ancestral route.
        part_byid={p['id']:p for p in current_parts}
        for part_id in added:
            part=part_byid[part_id]
            steps.append(dict(sequence=len(steps)+1,part_ids=[part_id],source_part_ids=[],
                unresolved_source_part_ids=[],operation='Prepare and review the current component process proposal',
                process_proposal=deepcopy(part['manufacturing']),inspection=deepcopy(part['inspection']),
                tools=None,route_status='held-current-part-route-needs-detail'))
        open_tasks=sorted({t for p in current_parts for t in p['open_tasks']})
        if source is not None:
            open_tasks=sorted(set(open_tasks)|set(source['open_tasks']))
        source_categories={} if source is None else deepcopy(source['inventory_categories'])
        categories={}
        for key, category in source_categories.items():
            category=deepcopy(category)
            category['part_ids']=[i for i in category.get('part_ids',[]) if i in current_ids]
            category['quantity_per_train']=sum(p['quantity_per_train'] for p in current_parts if p['id'] in category['part_ids'])
            categories[key]=category
        route=dict(id=assembly_id,identities=binding,occurrences_per_train=len(occurrences),
            occurrences_project=len(occurrences)*fleet,assembly_occurrence_ids=occurrences,
            source_pattern_assembly_ids=pattern_assembly_ids,
            occurrence_basis='Explicit sealed-body assembly anchors; constructive pattern groups are retained separately, not counted as extra assemblies',
            source_occurrences_per_train=None if source is None else source['occurrences'],
            component_type_ids=current_ids,source_component_type_ids=source_ids,
            operations=steps,source_operations=source_steps,source_route_unresolved_part_ids=missing,
            current_part_ids_needing_route_detail=added,
            workstation_proposal='Dedicated assembly cell for '+assembly_id,
            tools_and_fixtures_proposal=deepcopy([step.get('tools') for step in steps]),
            interfaces=[] if source is None else deepcopy(source['interfaces']),
            inventory_categories=categories,source_inventory_categories=source_categories,
            component_removal_proposals={p['id']:p['maintenance_removal'] for p in current_parts},
            removal_sequence=[] if source is None else deepcopy(source.get('source_removal_sequence',[])),
            tool_and_lifting_access=None if source is None else deepcopy(source.get('tool_and_lifting_access')),
            open_tasks=open_tasks,controlled_route_reference=None,validated_person_h=None,
            provisional_person_h={c:len(occurrences)*fleet*policy['assembly_person_h_per_occurrence'][c] for c in CASES},
            capacity_scope='Assembly-cell allowance in addition to part processing; not an additive price or critical-path duration',
            installation_accepted=False)
        rows.append(route)
        if missing or added or source is None:
            holds=[]
            if missing: holds.append('Source-only part IDs absent from current body: '+', '.join(missing))
            if added: holds.append('Current definitions need controlled route detail: '+', '.join(added))
            if source is None: holds.append('No source assembly route exists for this current assembly group')
            tasks.append(_task(binding,'hold/source-route/'+assembly_id,'source-route-revision',assembly_id,
                'Revise source assembly steps against the exact current component definitions',holds))
        tasks.append(_task(binding,'review/assembly/'+assembly_id,'assembly-planning',assembly_id,
            'Review source operations, fixtures, material flow, isolation/removal and inspection hold points'))
        tasks.append(_task(binding,'hold/assembly/'+assembly_id,'installation-release',assembly_id,
            'Issue controlled assembly instructions only after interface, movement and access checks',
            ['Qualified joints, fits, tooling capacity, mating drawing and approved inspection plan required',*open_tasks]))
    return rows,tasks


def _external(study, items, binding, fleet):
    rows=[];tasks=[];inventory=study['installed']['variant']['inventory'];byid={r['id']:r for r in inventory}
    if len(byid)!=len(inventory):
        raise ValueError('Duplicate integrated inventory owner')
    partition={c:fsum(p['counted_pattern_mass_kg_per_train'][c] for p in items if p['BOP_partition']) for c in CASES}
    for source in inventory:
        p=deepcopy(source);p['source_inventory_quantity']=p['quantity']
        q=positive(p['quantity'],'external quantity')
        location=p.get('location','')
        on_train=location.startswith('train')
        if p['id']=='conductor-protection-feeder':
            # Original parent inventory is running-track only; exact installed terminal geometry owns the total.
            q=study['installed']['terminal_geometry']['track_quantities']['total_track_m']
        p.update(identities=binding,quantity_per_train=q if on_train else None,
                 quantity_project=q*fleet if on_train else q,
                 ownership='external integrated inventory; not body part stock',
                 drawing_reference=None,validated_person_h=None,provisional_person_h=None,
                 supplier=None,procurement_status='planning-only',additional_to_body=True,
                 hour_hold_reason='Unresolved supplier packages, drawings and process rates; hours remain unknown')
        if p.get('included_in'):
            if p['included_in'] not in byid or p.get('additional_mass_not_added') is not True:
                raise ValueError('External partition must reference an existing positive owner')
            p.update(additional_to_body=False,additive_procurement=False,
                     ownership='Functional partition of '+p['included_in']+'; no second mass or package price')
        else:
            p['additive_procurement']=True
        if p['id']=='inverter-cooling-mounting-collector-reserve':
            accounting=p.get('BOP_partition',p)
            if any(partition.values()):
                required=('previous_external_reserve_kg','explicit_parts_already_in_body_kg','remaining_unknown_external_reserve_kg')
                if not all(k in accounting for k in required):
                    raise ValueError('Body BOP partition requires explicit external gross/partition/residual ownership')
                gross=ranges(accounting['previous_external_reserve_kg'])
                if any(abs(accounting['explicit_parts_already_in_body_kg'][c]-partition[c])>1e-6 for c in CASES):
                    raise ValueError('Body BOP partition differs from counted parts')
                remainder={c:gross[c]-partition[c] for c in CASES}
                if any(abs(accounting['remaining_unknown_external_reserve_kg'][c]-remainder[c])>1e-6 for c in CASES):
                    raise ValueError('External BOP remainder is not gross minus counted body stock')
                if not any(all(abs(p['mass_hypothesis_kg'][c]-option[c])<=1e-6 for c in CASES) for option in (gross,remainder)):
                    raise ValueError('Inventory BOP mass is neither declared gross nor residual')
            else:
                gross=ranges(p['mass_hypothesis_kg']);remainder=dict(gross)
            ranges(remainder)
            p.update(body_counted_BOP_partition_kg_per_train=partition,
                     remaining_unlocated_mass_kg_per_train=remainder,
                     ownership='Gross external BOP reserve less explicit body-owned BOP partition, counted once')
        if p['id'] in ('traction-motor','gearbox-including-couplings'):
            p['scope_note']='Known catalogue mass only; supplier housing/mount drawing, duty and qualification remain open. Gear internal bearings/couplings are included, not separate purchases.'
        rows.append(p)
        tasks.extend([_task(binding,'review/external/'+p['id'],'procurement-planning',p['id'],
                      'Prepare specification and supplier information request against declared mass, interface and duty assumptions'),
                      _task(binding,'hold/external/'+p['id'],'procurement-release',p['id'],
                      'Complete approved drawings, supplier evidence, compatibility, unit conversion and native ERP mapping before ordering',
                      ['Unverified installed package, supplier and controlled drawing; no purchase order authorised'])])
    return rows,tasks


def _civil(study,record,binding):
    civil=study['civil'];parts=civil['parts'];rows=[];tasks=[]
    for p in parts['items']:
        count=parts['shared_bent_instances'] if p['scope']=='each shared bent' else parts['beam_instances']
        if p['scope'] not in ('each shared bent','each beam','each beam; included in civil dead load once'):
            raise ValueError('Unknown civil quantity scope')
        row=dict(id=p['id'],identities=binding,source_part=deepcopy(p),
            instance_count=count,quantity_project=p['quantity_each_beam_or_bent']*count,
            quantity_basis=p['scope'],span_m=civil['physical_definition']['beam_stock']['span_m'],
            additive_mass_or_cost_ledger=False,validated_person_h=None,provisional_person_h=None,
            controlled_drawing_reference=None,workstation_proposal='Precast/rebar yard' if p['id'].startswith('beam/') else 'Controlled site workfront',
            tooling_proposal='Select qualified tooling and lifting equipment from released drawings and actual load/radius',
            inspection=p['inspection'],cost_source_evaluation_id=civil['evaluation_id'])
        rows.append(row)
        tasks.extend([_task(binding,'review/civil/'+p['id'],'construction-planning',p['id'],
                      'Review counted stock, fabrication/installation sequence, transport and inspection proposal'),
                      _task(binding,'hold/civil/'+p['id'],'construction-release',p['id'],
                      p['process'],['Controlled design, joints, site evidence, temporary works and inspected release required'])])
    tasks.append(_task(binding,'hold/terminal-detail','construction-detail','terminal geometry',
        'Detail terminal structures, four turnouts and equipment quantities separately from the running-span proof',
        ['Terminal extra track '+str(record['cost']['terminal_extra_track_m'])+' m is priced as a positive allowance; full parts, loads and erection drawings remain open']))
    return rows,tasks


def compile_proposal(study, body, service_id, *, root=ROOT, policy=None):
    """Return sealed deterministic proposals for one explicit same-schema research candidate."""
    root=Path(root);record,source_map=_input_validation(study,body,service_id,root)
    policy=deepcopy(policy if policy is not None else json.loads((root/POLICY).read_bytes()))
    if policy.get('schema')!='osr-pilot-delivery-policy/1' or policy.get('automatic_bulk_discount') is not False:
        raise ValueError('Explicit delivery policy without assumed purchasing discounts required')
    for k,v in policy.items():
        if isinstance(v,dict):ranges(v)
    binding=_binding(study,body,record);fleet=record['service']['total_trainsets']
    items,occurrences,tasks,materials=_parts(body,binding,fleet,policy)
    assemblies,at=_assemblies(body,binding,fleet,policy);tasks+=at
    external,et=_external(study,items,binding,fleet);tasks+=et
    civil,ct=_civil(study,record,binding);tasks+=ct
    ledgers=record['cost']['full_scope']
    cost_views=[dict(identities=binding,method=m['method'],scope_totals_usd=deepcopy(m['scope_totals_usd']),
        installed_capital_usd=deepcopy(m['installed_capital_usd']),whole_life_NPV_usd=deepcopy(m['whole_life_NPV_usd']),
        site_specific_prices_verified=m['site_specific_prices_verified']) for m in ledgers['methods']]
    for scope in ledgers['required_cost_scopes']:
        tasks.append(_task(binding,'review/scope/'+scope,'cost-scope-review',scope,
            'Review existing same-candidate cost owner, exclusions, quantity evidence and source rate; do not add delivery decomposition again'))
    tasks.append(_task(binding,'hold/ERP-conversion','business-review','ERPNext conversion',
        'Supply actual reviewed ERP Item codes, unit conversion, inspection references and controlled drawings',
        ['Generic engineering.execution_proposal intentionally refuses this draft until reviewed native mappings exist']))
    incomplete_time_ids=[p['id'] for p in items if p['capacity']['provisional_person_h'] is None]
    known_person={c:fsum(p['capacity']['provisional_person_h'][c] for p in items if p['capacity']['provisional_person_h'] is not None)
                  +fsum(a['provisional_person_h'][c] for a in assemblies) for c in CASES}
    person=None if incomplete_time_ids else known_person
    material_requirements=[]
    for material in materials:
        matched=[p for p in items if p['material_id']==material['id']]
        material_requirements.append(dict(id=material['id'],identities=binding,
            counted_body_mass_kg_project={c:fleet*fsum(p['counted_pattern_mass_kg_per_train'][c] for p in matched) for c in CASES},
            component_types=len(matched),procurement_stock_mass_kg=None,
            basis='Counted part/pattern mass only; yield, net/gross differences and purchased assemblies are not an ordered raw-material mass'))
    construction=dict(identities=binding,source_evaluation_id=study['civil']['construction']['evaluation_id'],
        erection_sequence=deepcopy(study['civil']['construction']['erection_sequence']),
        handling=deepcopy(study['civil']['construction']['handling']),
        temporary_works=deepcopy(study['civil']['construction']['midspan_tower']),
        lifting=deepcopy(study['civil']['lifting']),construction_release=False,
        hours=None,capacity=None,hold='Actual crane chart, attachments, transport, temporary works, site and controlled drawings required')
    tasks.sort(key=lambda t:t['id'])
    result=dict(schema='osr-pilot-delivery-proposal/1',identities=binding,
        planning_selection=dict(purpose='Manufacturing planning review only; not integrated architecture or prototype selection',
            selected_service_evaluation_id=service_id,selection_id=identity(dict(identities=binding,purpose='manufacturing-planning-review'))),
        status='DRAFT',docstatus=0,source_sha256=source_map,policy=policy,policy_id=identity(policy),
        materials=materials,material_requirements=material_requirements,items=items,occurrence_patterns=occurrences,assembly_routes=assemblies,
        external_inventory=external,civil_requirements=civil,construction_route=construction,tasks=tasks,cost_views=cost_views,
        assembly_revision_proposals=deepcopy({k:v for k,v in body['assembly_plans'].items() if k!='plans'}),
        retired_source_routes=deepcopy([r for r in body['assembly_plans']['plans'] if r['assembly_id'] not in {p['assembly_id'] for p in body['parts']}]),
        capacity=dict(provisional_vehicle_person_h=person,known_provisional_vehicle_person_h_subtotal=known_person,
            part_process_hours_complete=not incomplete_time_ids,unknown_part_process_hour_ids=incomplete_time_ids,validated_vehicle_person_h=None,
            equivalent_16h_resource_days=None if person is None else {c:person[c]/(policy['shifts_per_day']*policy['hours_per_shift']*policy['productive_fraction'][c]) for c in CASES},
            basis='Vehicle part processing + assembly proxy only; not elapsed days. Actual crew, parallel cells, shifts per worker, procurement, cure, site, external packages and critical path remain unresolved.',
            actual_crew_count=None,calendar_duration_days=None,external_and_civil_hours_unknown=True),
        execution_mapping_draft=dict(identities=binding,review_reference=None,engineering_sha256=None,
            items=[dict(component_type_id=p['component_definition_id'],source_part_id=p['id'],erp_item_code=None,
                        uom=p['unit'],inspection_reference=None,drawing_reference=None,
                        production_bom=None,conversion_rule=None) for p in items],
            status='held',automatic_order_release=False),
        manufacturing_drawings_complete=False,qualified_factory_route=False,
        measured_installed_mass=False,limitations=LIMITATIONS,**FLAGS)
    result['summary']=dict(component_types=len(items),occurrence_patterns=len(occurrences),
        body_occurrences_per_train=sum(p['quantity_per_train'] for p in items),
        body_occurrences_project=sum(p['quantity_project'] for p in items),project_trainsets=fleet,
        assembly_types=len(assemblies),source_routes_with_missing_parts=sum(bool(a['source_route_unresolved_part_ids']) for a in assemblies),external_inventory_owners=len(external),civil_requirement_types=len(civil),
        cost_scopes=len(ledgers['required_cost_scopes']),task_status_counts=dict(Counter(t['status'] for t in tasks)),
        make_buy_counts=dict(Counter(p['make_buy'] for p in items)),
        direct_part_process_usd_per_train=deepcopy(body['direct_parts_process_usd']),
        unknown_process_time_types=len(incomplete_time_ids),engineering_release_held=True,ERP_mapping_ready=False)
    seal(result,'proposal_id');validate_proposal(result)
    return result


def validate_proposal(proposal):
    sealed(proposal,'proposal_id');guard_draft(proposal)
    if proposal.get('schema')!='osr-pilot-delivery-proposal/1' or proposal.get('status')!='DRAFT':
        raise ValueError('Expected explicit DRAFT manufacturing proposal')
    binding=proposal['identities']
    for k,v in binding.items():
        if not isinstance(v,str) or len(v)!=64 or any(c not in '0123456789abcdef' for c in v):
            raise ValueError('Explicit candidate/evaluation identity required: '+k)
    for section in ('items','material_requirements','occurrence_patterns','assembly_routes','external_inventory','civil_requirements','tasks','cost_views'):
        rows=proposal[section]
        if section!='cost_views' and len({r['id'] for r in rows})!=len(rows):
            raise ValueError('Repeated '+section+' identity')
        for row in rows:
            if row.get('identities')!=binding:
                raise ValueError('Mixed candidate, evaluation or bundle in '+section)
    if proposal['construction_route']['identities']!=binding:
        raise ValueError('Mixed construction route identity')
    if proposal['execution_mapping_draft']['identities']!=binding:
        raise ValueError('Mixed ERP mapping identity')
    if proposal['planning_selection']['selected_service_evaluation_id']!=binding['service_evaluation_id']:
        raise ValueError('Mixed planning selection service')
    fleet=proposal['summary']['project_trainsets']
    counts=Counter();part_byid={p['id']:p for p in proposal['items']}
    for row in proposal['occurrence_patterns']:
        positive(row['count_per_train'],'occurrence count')
        if row['part_id'] not in part_byid or row['component_definition_id']!=part_byid[row['part_id']]['component_definition_id']:
            raise ValueError('Mixed component definition or orphan occurrence')
        counts[row['part_id']]+=row['count_per_train']
    for row in proposal['items']:
        positive(row['quantity_per_train'],'part quantity')
        if row['serial_plan']['serial_number'] is not None or row['serial_plan']['lot_number'] is not None:
            raise ValueError('Draft cannot assign serial or lot identities')
        if counts.pop(row['id'],None)!=row['quantity_per_train'] or row['quantity_project']!=row['quantity_per_train']*fleet:
            raise ValueError('Part/project quantity differs from counted patterns')
        proposed=row['capacity']['provisional_person_h']
        if proposed is None:
            if not row['capacity'].get('hold_reason'):
                raise ValueError('Unknown hours require explicit route/time hold')
        else:
            ranges(proposed)
        if row['make_buy_mapping']!=_make_buy_mapping(row['make_buy']):
            raise ValueError('Make/buy mapping differs from explicit source category')
        if row['capacity']['validated_person_h'] is not None:
            raise ValueError('Proxy hours cannot become validated process times')
    if counts:
        raise ValueError('Orphan exported occurrence')
    unknown=[p['id'] for p in proposal['items'] if p['capacity']['provisional_person_h'] is None]
    if proposal['capacity']['unknown_part_process_hour_ids']!=unknown or (unknown and proposal['capacity']['provisional_vehicle_person_h'] is not None):
        raise ValueError('Unknown process times cannot become a complete or zero-hour total')
    for route in proposal['assembly_routes']:
        expected={p['id'] for p in proposal['items'] if p['assembly_id']==route['id']}
        if set(route['component_type_ids'])!=expected or any(i not in expected for step in route['operations'] for i in step['part_ids']):
            raise ValueError('Assembly route uses removed or different-assembly part definitions')
    if proposal['summary']['task_status_counts']!=dict(Counter(t['status'] for t in proposal['tasks'])):
        raise ValueError('Task completion summary differs')
    return True
