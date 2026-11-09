"""One-terminal material/owner transaction plan; never an installed candidate.

Consumes already-sealed source-specific normal forms and a finite-weld proposal.
No upstream producer, solver or composer is imported.  Local material occurrences
are replaced once; train-end transforms are deployment records, never multipliers.
Unresolved cut unions, density contexts and source contracts remain explicit.
"""
from copy import deepcopy
from hashlib import sha256
from math import fsum, isfinite
import json

CASES = ('low', 'base', 'high')
FRAME = 'terminal-local-UVW'
FLAGS = dict(canonical_admitted=False, installed_assembly_accepted=False,
             native_eligible=False, physical_accepted=False,
             engineering_accepted=False, manufacturing_release=False,
             operating_release=False, selected_reference_changed=False,
             release_approved=False)
SCHEMAS = {'terminal': 'osr-terminal-canonical-normalization-packet/1',
           'weld': 'osr-terminal-finite-full-revision-proposal/1',
           'hardware': 'osr-terminal-hardware-component-normalization/1'}


def identity(value):
    return sha256((json.dumps(value, sort_keys=True, separators=(',', ':'),
                              allow_nan=False) + '\n').encode()).hexdigest()


def seal(value):
    return dict(deepcopy(value), evaluation_id=identity(value))


def _hex(value, length=64):
    if not isinstance(value, str) or len(value) != length or any(c not in '0123456789abcdef' for c in value):
        raise ValueError('Explicit hexadecimal identity required')
    return value


def _name(value):
    if not isinstance(value, str) or not value or len(value) > 512:
        raise ValueError('Explicit bounded identifier required')
    return value


def _number(value, nonnegative=False):
    if type(value) not in (float, int) or not isfinite(value) or nonnegative and value < 0:
        raise ValueError('Finite nonboolean scalar required')
    return float(value)


def _count(value):
    if type(value) is not int or value < 0:
        raise ValueError('Explicit nonboolean nonnegative occurrence count required')
    return value


def _vector(value):
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError('Explicit three-coordinate SI vector required')
    return [_number(x) for x in value]


def _pose(entity):
    _vector(entity['at_m'])
    R = entity['rotation']
    if not isinstance(R, list) or len(R) != 3:
        raise ValueError('Explicit proper local rotation required')
    for row in R:
        _vector(row)
    if any(abs(fsum(R[k][i] * R[k][j] for k in range(3)) - (i == j)) > 1e-10
           for i in range(3) for j in range(3)):
        raise ValueError('Nonrigid local rotation refused')
    det = (R[0][0] * (R[1][1] * R[2][2] - R[1][2] * R[2][1])
           - R[0][1] * (R[1][0] * R[2][2] - R[1][2] * R[2][0])
           + R[0][2] * (R[1][0] * R[2][1] - R[1][1] * R[2][0]))
    if abs(det - 1) > 1e-10:
        raise ValueError('Reflected local rotation refused')


def _index(rows, label, limit=2500):
    if not isinstance(rows, list) or not rows or len(rows) > limit:
        raise ValueError('Explicit bounded ' + label + ' roster required')
    out = {}
    for row in rows:
        key = _name(row['id'])
        if key in out:
            raise ValueError('Duplicate ' + label + ' identity: ' + key)
        out[key] = row
    return out


def _cases(value):
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != set(CASES):
        raise ValueError('Explicit low/base/high or unknown cases required')
    values = [_number(value[c], True) for c in CASES]
    if values != sorted(values):
        raise ValueError('Ordered nonnegative case labels required')
    return deepcopy(value)


def _digest(value, label):
    _hex(value['evaluation_id'])
    if identity({k: v for k, v in value.items() if k != 'evaluation_id'}) != value['evaluation_id']:
        raise ValueError('Stale ' + label + ' evaluation identity')


def _ownership(groups, entities, label):
    covered = {}
    for gid, group in groups.items():
        ids = group['entity_ids']
        if not isinstance(ids, list) or not ids or len(ids) != len(set(ids)):
            raise ValueError('Nonempty once-only stock constituent list required')
        for eid in ids:
            if eid not in entities or eid in covered:
                raise ValueError('Missing/reused ' + label + ' material occurrence: ' + str(eid))
            covered[eid] = gid
    if set(covered) != set(entities):
        raise ValueError('Incomplete ' + label + ' material/paid-stock coverage')
    return covered


def _physical_terminal(terminal, entities):
    """Use the upstream source-specific physical projection, not cost records."""
    p = terminal['source_physical_definition']
    out = {}
    for value in p['exact_legacy_CSG']:
        eid = 'legacy/' + _name(value['id'])
        if eid in out:
            raise ValueError('Duplicate physical legacy record')
        out[eid] = deepcopy(value)
    for value in p['added_entities']:
        eid = _name(value['id'])
        if eid in out:
            raise ValueError('Duplicate physical terminal record')
        out[eid] = deepcopy(value)
    if not set(entities) <= set(out):
        raise ValueError('Missing physical terminal source record')
    # Some authenticated source CSG is ancestry-only (e.g. removed end beam).
    return {eid: dict(id=eid, material_id=_name(e['material_id']),
                     domain='source-unresolved-finished-material' if e.get('unknown_finished_geometry') else 'source-material-record',
                     physical_record=out[eid]) for eid, e in entities.items()}


def _source_density(group):
    value = group.get('source_account', {}).get('density_cases_kg_m3')
    if value is None:
        V = group.get('net_m3')
        mass = group.get('net_mass_kg')
        if V is None or mass is None:
            return None
        if _number(V) <= 0 or set(mass) != set(CASES):
            raise ValueError('Explicit positive source material volume required')
        value = [_number(mass[c], True) / V for c in CASES]
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError('Explicit source density case context required')
    for x in value:
        if _number(x) <= 0:
            raise ValueError('Positive source density required')
    return list(value)


def _material_density(policy, material):
    value = policy.get(material)
    if value is None:
        return None
    if 'density_bounds_kg_m3' in value:
        result = [value['density_bounds_kg_m3'][0], value['density_kg_m3'], value['density_bounds_kg_m3'][1]]
    else:
        result = value.get('density_kg_m3')
    if result is None:
        return None
    if not isinstance(result, list) or len(result) != 3 or any(_number(x) <= 0 for x in result):
        raise ValueError('Explicit positive density context required')
    return list(result)


def _hardware_materials(hardware):
    prototypes = hardware['source_original_definition']['prototypes']
    if not isinstance(prototypes, dict) or not prototypes:
        raise ValueError('Explicit hardware material-policy contexts required')
    result = None
    for prototype in prototypes.values():
        current = prototype['materials']
        if result is None:
            result = current
        elif current != result:
            raise ValueError('Hardware prototype material-policy contexts disagree')
    return result


def _physical_parent(row):
    """Finite weld physical rows are already a source-specific price-free form."""
    for key in ('id', 'material_id', 'geometry', 'at_m', 'rotation'):
        if key not in row:
            raise ValueError('Incomplete explicit revised physical parent')
    _pose(row)
    return deepcopy(row)


def plan_revision(terminal, weld, hardware, *, input_pin, request_id,
                  combined_cut_unions=None):
    """Return an immutable-value LOCAL transaction draft, always unadmitted.

    Inputs must be exact source-specific sealed records. A proposed cut union
    may bind all physical operands, but this planner never solves that Boolean
    or claims its material moments/strength; that remains a named obligation.
    All output objects are copies; every refusal leaves inputs unchanged.
    """
    _hex(request_id)
    # Reject NaN/infinity/non-JSON content before traversing source contracts.
    for value in (terminal, weld, hardware, input_pin, combined_cut_unions):
        identity(value)
    inputs = dict(terminal=terminal, weld=weld, hardware=hardware)
    if input_pin.get('schema') != 'osr-terminal-local-revision-input-pin/1':
        raise ValueError('Explicit local revision input-pin schema required')
    if set(input_pin) != {'schema', 'sources', 'expected_counts'} or set(input_pin['sources']) != set(inputs):
        raise ValueError('Complete exact source binding required')
    for name, value in inputs.items():
        if value.get('schema') != SCHEMAS[name]:
            raise ValueError('Unsupported source-specific ' + name + ' schema')
        _digest(value, name)
        pin = input_pin['sources'][name]
        if set(pin) != {'evaluation_id', 'raw_sha256', 'source_commit'}:
            raise ValueError('Exact evaluation/file/source binding required')
        _hex(pin['evaluation_id']); _hex(pin['raw_sha256']); _hex(pin['source_commit'], 40)
        if pin['evaluation_id'] != value['evaluation_id']:
            raise ValueError('Input evaluation pin differs')
        if any(value.get(k) is True for k in FLAGS):
            raise ValueError('This source API accepts unadmitted research records only')
    if weld['canonical_definition'] is not None or hardware['canonical_definition'] is not None or weld['accounting']['transaction_applied'] or hardware['source_owner_transactions_applied']:
        raise ValueError('Already applied/canonical source transaction refused')
    _digest(weld['source_proposal'], 'original local terminal')
    original_hardware = hardware['source_original_definition']
    if sha256(json.dumps({k:v for k,v in original_hardware.items() if k != 'evaluation_id'}, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest() != original_hardware['evaluation_id']:
        raise ValueError('Stale original no-LF hardware source identity')
    if original_hardware['candidate_id'] != hardware['source_candidate_id'] or original_hardware['evaluation_id'] != hardware['source_evaluation_id']:
        raise ValueError('Hardware original source ancestry differs')
    hardware_physical_id = sha256(json.dumps(original_hardware['physical_definition'], sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    if hardware_physical_id != original_hardware['candidate_id']:
        raise ValueError('Original hardware no-LF physical candidate identity differs')
    common = terminal['source_pin']
    if not isinstance(common, dict) or set(common) != {'candidate_id', 'evaluation_id', 'raw_sha256'}:
        raise ValueError('Exact original local source epoch required')
    for v in common.values():
        _hex(v)
    if common != weld['source_pin'] or common != hardware['source_original_definition']['parent']:
        raise ValueError('Mixed local candidate/source epochs refused')
    if weld['source_proposal']['candidate_id'] != common['candidate_id'] or weld['source_proposal']['evaluation_id'] != common['evaluation_id']:
        raise ValueError('Weld original source ancestry differs')
    if identity(terminal['source_physical_definition']) != common['candidate_id']:
        raise ValueError('Terminal physical projection differs from common local candidate')
    if terminal['source_physical_definition'] != weld['source_proposal']['physical_definition']:
        raise ValueError('Terminal and original weld source physical projections differ')
    if identity(weld['physical_definition']) != weld['physical_definition_id'] or identity(hardware['physical_definition']) != hardware['component_geometry_id']:
        raise ValueError('Upstream physical projection identity differs')
    draft = terminal['canonical_draft']
    entities = _index(draft['entities'], 'terminal material')
    groups = _index(draft['stock_groups'], 'terminal stock')
    original_owners = _ownership(groups, entities, 'terminal')
    local_physical = _physical_terminal(terminal, entities)
    new_entities = deepcopy(entities)
    new_groups = deepcopy(groups)
    ledger = []
    pending = []
    def hold(kind, subject, detail):
        pending.append(dict(id=kind + '/' + subject, kind=kind, subject=subject,
                            resolved=False, detail=deepcopy(detail)))

    # Deployment is preserved but not applied to coordinates or local quantities.
    bindings = draft['bindings']
    if not isinstance(bindings, list) or not bindings or len({b['id'] for b in bindings}) != len(bindings):
        raise ValueError('Explicit unique deployment binding roster required')
    for binding in bindings:
        _pose(binding)
    # Weld dispositions: every old owner is retained or replaced exactly once.
    routes = weld['source_routes']
    defined = weld['defined_welds']
    held = weld['held']
    if len(defined) != len(set(defined)) or len({x['source_weld_id'] for x in held}) != len(held):
        raise ValueError('Duplicate weld route disposition')
    defined = set(defined); held_ids = {x['source_weld_id'] for x in held}
    if defined & held_ids or defined | held_ids != set(routes):
        raise ValueError('Incomplete weld route disposition')
    WA = weld['accounting']
    old_weld_rows = WA['old_weld_dispositions']
    if len(old_weld_rows) != len(routes) or len({x['source_weld_id'] for x in old_weld_rows}) != len(routes) or len({x['old_owner_id'] for x in old_weld_rows}) != len(routes):
        raise ValueError('Every old weld needs one disposition')
    phys_fillers = _index(weld['physical_definition']['filler'], 'finite filler')
    owner_fillers = WA['filler_replacement_owners']
    if set(owner_fillers) != defined or set(weld['parent_preparation_receipts']) != defined:
        raise ValueError('Defined filler owner/receipt coverage differs')
    filler_seen = set()
    for row in old_weld_rows:
        wid = row['source_weld_id']; oid = row['old_owner_id']
        if wid not in entities or oid not in groups or original_owners[wid] != oid:
            raise ValueError('Unknown original weld material/stock owner')
        if identity(groups[oid]) != row['old_owner_sha256']:
            raise ValueError('Stale original weld owner epoch')
        if wid in held_ids:
            hrow = next(h for h in held if h['source_weld_id'] == wid)
            if not hrow['old_source_retained'] or row['replacement_owner_id'] is not None or 'held' not in row['status']:
                raise ValueError('Held original weld must remain live exactly once')
            local_physical[wid]['domain'] = 'held-source-weld-not-an-oriented-filled-box'
            ledger.append(dict(kind='retain-held-weld', old_owner_id=oid, old_entity_ids=[wid], new_owner_ids=[oid], new_entity_ids=[wid]))
            hold('held-source-weld', wid, hrow)
            continue
        if row['status'] != 'defined-one-for-one-replacement' or row['replacement_owner_id'] != oid:
            raise ValueError('Finite weld must replace the original owner once')
        replacement = deepcopy(owner_fillers[wid])
        if replacement['id'] != oid or _count(replacement.get('quantity')) != 1 or set(groups[oid]['entity_ids']) != {wid}:
            raise ValueError('Weld paid-owner quantity/constituent scope differs')
        ids = replacement['entity_ids']
        if not ids or len(ids) != len(set(ids)) or any(x not in phys_fillers or x in filler_seen or x in entities for x in ids):
            raise ValueError('Duplicate/missing finite filler material')
        receipt_ids = {x['id'] for x in weld['parent_preparation_receipts'][wid]['pieces']}
        if set(ids) != receipt_ids:
            raise ValueError('Filler owner and finite receipt differ')
        del new_entities[wid]; del local_physical[wid]
        for eid in ids:
            p = deepcopy(phys_fillers[eid]); new_entities[eid] = dict(id=eid, scope='installed', frame=FRAME,
                finite_material_record=p, mass_properties=None, source_owner_id=oid)
            local_physical[eid] = dict(id=eid, domain='finite-source-weld-polyhedron', physical_record=p)
        filler_seen.update(ids); new_groups[oid] = replacement
        ledger.append(dict(kind='replace-weld-once', old_owner_id=oid, old_entity_ids=[wid], new_owner_ids=[oid], new_entity_ids=list(ids)))
    if filler_seen != set(phys_fillers):
        raise ValueError('Unowned or omitted finite filler')

    # Revised parent material shares the original paid blank and price owner.
    physical_parents = _index(weld['physical_definition']['changed_parents'], 'revised parent')
    changed = weld['final_changed_parent_entities']
    if set(physical_parents) != set(changed):
        raise ValueError('Revised parent physical/full-record roster differs')
    changed_seen = set()
    density_contexts = []
    for oid, revision in WA['parent_stock_owner_revisions'].items():
        if oid not in groups or groups[oid] != revision['source_owner'] or _count(revision['paid_gross_count']) != 1:
            raise ValueError('Parent paid stock source epoch/ownership differs')
        replacement = revision['replacement_owner']
        if replacement['id'] != oid or set(replacement['entity_ids']) != set(groups[oid]['entity_ids']):
            raise ValueError('Parent revision cannot invent or drop paid constituents')
        if any(_number(x, True) != 0 for x in revision['material_purchase_delta_USD'].values()):
            raise ValueError('Same retained parent blank cannot be purchased again')
        for eid in revision['changed_parent_ids']:
            if eid not in changed or eid not in entities or eid in changed_seen or original_owners[eid] != oid or eid not in new_entities:
                raise ValueError('Missing, duplicated or retired revised parent')
            e = changed[eid]; p = _physical_parent(physical_parents[eid])
            if any(e[k] != p[k] for k in ('id', 'material_id', 'geometry', 'at_m', 'rotation')):
                raise ValueError('Changed parent material/pose projection differs')
            new_entities[eid] = deepcopy(e); local_physical[eid] = dict(id=eid, domain='revised-source-parent', physical_record=p)
            changed_seen.add(eid)
            old_rho = _source_density(groups[oid]); cut = weld['parent_cut_unions'].get(eid)
            applied = None
            if cut is not None:
                V = _number(cut['new_removed_volume_m3'])
                if V <= 0:
                    raise ValueError('Positive applied cut-union volume required')
                applied = [_number(cut['cases'][c]['removed_mass_kg'], True) / V for c in CASES]
            density_contexts.append(dict(source_entity_id=eid, source_owner_id=oid,
                source_density_cases_kg_m3=old_rho, applied_cut_density_cases_kg_m3=applied,
                global_policy_for_future_cuts_only=_material_density(weld['source_policy']['materials'], e['material_id']),
                scope='No new density debit is inferred from a dormant global policy. Only an actual returned cut-union debit is compared.'))
            if applied is not None and (old_rho is None or any(abs(a-b) > 1e-7 for a,b in zip(old_rho, applied))):
                hold('applied-cut-density-context-unresolved', eid, density_contexts[-1])
        new_groups[oid] = deepcopy(replacement)
        ledger.append(dict(kind='revise-retained-paid-parent', old_owner_id=oid,
                           old_entity_ids=list(groups[oid]['entity_ids']), new_owner_ids=[oid],
                           new_entity_ids=list(replacement['entity_ids']), paid_gross_count=1))
    if changed_seen != set(changed):
        raise ValueError('Incomplete final revised parent ownership')
    new_parts = _index(weld['physical_definition']['new_parts'], 'new connector')
    if set(new_parts) != set(weld['new_part_entities']):
        raise ValueError('New part physical/full roster differs')
    for eid, e in weld['new_part_entities'].items():
        if eid in new_entities:
            raise ValueError('New weld connector duplicates existing material')
        p = _physical_parent(new_parts[eid])
        if any(e[k] != p[k] for k in ('id', 'material_id', 'geometry', 'at_m', 'rotation')):
            raise ValueError('New connector physical/full projection differs')
        new_entities[eid] = deepcopy(e); local_physical[eid] = dict(id=eid, domain='new-source-connector', physical_record=p)
    for oid, group in WA['new_stock_owners'].items():
        if oid in new_groups or group['id'] != oid or _count(group.get('quantity')) != 1 or not set(group['entity_ids']) <= set(new_parts):
            raise ValueError('New connector stock/material scope duplicates')
        new_groups[oid] = deepcopy(group)
        ledger.append(dict(kind='new-connector-stock', old_owner_id=None, old_entity_ids=[], new_owner_ids=[oid], new_entity_ids=deepcopy(group['entity_ids'])))

    # Hardware replaces local descendants; P1 retirement stays terminal-owned.
    H = hardware['canonical_draft']; Hentities = _index(H['entities'], 'hardware material')
    Hgroups = _index(H['stock_groups'], 'hardware stock')
    _ownership(Hgroups, Hentities, 'hardware')
    Hphysical = _index(hardware['physical_definition']['entities'], 'physical hardware')
    if set(Hphysical) != set(Hentities):
        raise ValueError('Hardware physical/full material roster differs')
    occurrence_map = hardware['mapping']; mapped_pieces = [x for ids in occurrence_map.values() for x in ids]
    if len(mapped_pieces) != len(set(mapped_pieces)) or set(mapped_pieces) != set(Hentities):
        raise ValueError('Hardware occurrence/piece mapping is not once-only')
    retired_owners = set(); retired_entities = set(); used_placements = set()
    leaf_rows = terminal['old_leaf_replacements_train_once']
    leaf = {x['source_part_id']:x for x in leaf_rows}
    if len(leaf) != len(leaf_rows):
        raise ValueError('Duplicate original P1 retirement group')
    for row in leaf_rows:
        keys = row['source_ids']
        if not isinstance(keys, list) or not keys or len(keys) != len(set(keys)) or _count(row['old_count']) != len(keys):
            raise ValueError('Exact once-only inherited P1 source-key roster required')
        for key in keys:
            if not isinstance(key, str) or not key.startswith('source/'):
                raise ValueError('Explicit inherited canonical P1 source key required')
            _hex(key[7:])
    retirement_inheritance = []
    for row in H['old_stock_owner_dispositions']:
        oid = row['source_owner_id']; src = row['source']
        if oid in retired_owners or oid not in groups or src['source_group'] != groups[oid] or src['source_group_id'] != oid or row['canonical_source_key_map'] is not None or row['status'] != 'REQUIRED_NOT_APPLIED':
            raise ValueError('Hardware old owner source epoch/duplicate/key map differs')
        old_ids = src['old_entity_ids']; successors = src['successor_ids']
        if set(old_ids) != set(groups[oid]['entity_ids']) or len(old_ids) != len(set(old_ids)) or not src['once_only'] or src['applied'] or not src['source_price_not_added']:
            raise ValueError('Hardware original material/price must retire once')
        if any(eid in retired_entities or eid in changed or eid in defined or eid in held_ids for eid in old_ids):
            raise ValueError('Hardware and weld revisions overlap without a replacement contract')
        group_placements = {gid:g for gid,g in Hgroups.items() if g['source_owner_group_id'] == oid}
        if {g['old_occurrence_id'] for g in group_placements.values()} != set(old_ids) or len(group_placements) != len(old_ids):
            raise ValueError('One new hardware stock owner per old local occurrence required')
        if set(successors) != {'hardware/' + x for x in old_ids} or not set(successors) <= set(occurrence_map):
            raise ValueError('Exact local hardware successor identity required')
        for gid, g in group_placements.items():
            if g['old_material_or_price_added'] or _count(g['procurement_quantity']) != 1 or gid in new_groups or set(g['entity_ids']) != set(occurrence_map['hardware/' + g['old_occurrence_id']]):
                raise ValueError('Duplicate hardware purchase/material or missing piece ownership')
            used_placements.add('hardware/' + g['old_occurrence_id']); new_groups[gid] = deepcopy(g)
        pid = groups[oid]['source_account']['part_id']
        if pid.startswith('body/'):
            if pid not in leaf or type(leaf[pid]['retained_original_price_once']) is not bool:
                raise ValueError('Explicit inherited P1 retirement/price-basis metadata required')
            # True records the old local owner's borrowed P1 price basis. That
            # old local owner is removed below and each new H group is paid once.
            # The inherited P1 metadata stays intact, never a second invoice or
            # another P1 retirement. False is also valid provenance, not a waiver.
            inheritance = dict(source_part_id=pid, source_keys=deepcopy(leaf[pid]['source_ids']),
                owner='terminal-old-leaf-replacement-only', new_P1_retirement_count=0,
                inherited_retained_original_price_once=leaf[pid]['retained_original_price_once'],
                inherited_price_metadata_added_as_new_hardware_charge=False,
                price_scope='Inherited old-local-group price provenance only; replaced local owner removed, new hardware groups paid once')
        elif pid.startswith('research/'):
            if pid in leaf:
                raise ValueError('Local research group cannot invent a P1 predecessor')
            inheritance = dict(source_part_id=pid, source_keys=[], owner='local-terminal-research-only', new_P1_retirement_count=0)
        else:
            raise ValueError('Unsupported hardware predecessor lineage')
        retirement_inheritance.append(inheritance)
        for eid in old_ids:
            del new_entities[eid]; del local_physical[eid]
        del new_groups[oid]; retired_entities.update(old_ids); retired_owners.add(oid)
        ledger.append(dict(kind='replace-local-hardware-owner', old_owner_id=oid, old_entity_ids=deepcopy(old_ids),
                           new_owner_ids=list(group_placements), new_entity_ids=[x for s in successors for x in occurrence_map[s]],
                           P1_retirement=deepcopy(inheritance)))
    if used_placements != set(occurrence_map) or set(Hgroups) != {g for row in ledger if row['kind'] == 'replace-local-hardware-owner' for g in row['new_owner_ids']}:
        raise ValueError('Extra or unowned hardware purchase/placement')
    for eid, e in Hentities.items():
        if eid in new_entities:
            raise ValueError('Hardware material occurrence duplicates another revision')
        p = Hphysical[eid]
        _pose(p)
        if e['frame'] != FRAME or p['frame'] != FRAME or any(e[k] != p[k] for k in ('id', 'material_id', 'at_m', 'rotation')):
            raise ValueError('Hardware local frame/pose/material differs')
        new_entities[eid] = deepcopy(e); local_physical[eid] = dict(id=eid, domain='hardware-source-bounded-material', physical_record=deepcopy(p))

    # Preserve every complete machining operand.  An overlap requires an exact
    # symbolic union contract, never whichever adapter happened to run last.
    finish = _index(H['required_source_finishing'], 'finishing operation')
    physical_finish = _index(hardware['physical_definition']['source_finishing'], 'physical finishing operation')
    if set(physical_finish) != set(finish):
        raise ValueError('Physical finishing operation coverage differs')
    finish_owner_rows = H['source_finishing_owner_dispositions']; finish_seen = set(); paid_finish = set()
    finish_records = []; conflicts = []; union_map = _index(combined_cut_unions, 'combined cut union') if combined_cut_unions else {}
    union_used = set(); hp_policy = _hardware_materials(hardware)
    for row in finish_owner_rows:
        oid = row['source_owner_id']
        if oid in paid_finish or oid not in new_groups or oid in retired_owners or groups[oid] != row['source'] or _count(row['paid_blank_count']) != 1 or _count(row['stock_purchase_count']) != 0 or row['source_mass_and_moment_update_applied']:
            raise ValueError('Finishing must retain its exact original paid group once')
        paid_finish.add(oid)
        for opid in row['operation_ids']:
            if opid in finish_seen or opid not in finish:
                raise ValueError('Missing or duplicated finishing operation')
            op = finish[opid]; eid = op['source_entity_id']; finish_seen.add(opid)
            if eid not in entities or original_owners[eid] != oid or eid in retired_entities or op['source_stock_owner_id'] != oid or op['frame'] != FRAME or op['units'] != 'm':
                raise ValueError('Finishing source member/owner/frame differs')
            if entities[eid]['exact_CSG_entity'] != op['source_operation']['source_geometry'] or not op['paid_blank_retained_once'] or op['remaining_net_mass_and_CG'] is not None:
                raise ValueError('Finishing source epoch or unproved properties differ')
            for key in ('incremental_removed_mass_bounds_kg', 'incremental_removed_volume_bounds_m3'):
                values = op[key]
                if not isinstance(values, list) or len(values) != 2 or not 0 < _number(values[0]) <= _number(values[1]):
                    raise ValueError('Explicit positive finishing residual bounds required')
            physical_op = physical_finish[opid]
            if physical_op is None or physical_op['source_entity_id'] != eid or physical_op['source_stock_owner_id'] != oid or physical_op['complete_void_union'] != op['source_complete_void_union']:
                raise ValueError('Physical complete finishing void union differs')
            f = dict(operation_id=opid, source_entity_id=eid, paid_owner_id=oid,
                     physical_operation=deepcopy(physical_op), source_record=deepcopy(op),
                     mass_moment_application='unapplied; exact final material union and density required',
                     remaining_net_mass_and_CG=None, inertia=None)
            finish_records.append(f)
            hold('finishing-material-properties-pending', opid, dict(source_entity_id=eid, bounds=op['incremental_removed_mass_bounds_kg']))
            old_rho = _source_density(groups[oid]); material = op['source_operation']['material']; new_rho = _material_density(hp_policy, material)
            density_contexts.append(dict(source_entity_id=eid, source_owner_id=oid, source_density_cases_kg_m3=old_rho, finishing_density_cases_kg_m3=new_rho))
            if old_rho is None or new_rho is None or old_rho != new_rho:
                hold('density-context-unresolved', opid, density_contexts[-1])
            if eid in changed:
                conflicts.append(dict(source_entity_id=eid, operation_id=opid, paid_owner_id=oid))
            # Always preserve layered set operands. No material gets silently
            # replaced by the finishing operation's original parent snapshot.
            current = local_physical[eid]
            local_physical[eid] = dict(id=eid, material_id=entities[eid]['material_id'],
                domain='prospective-finished-source-material-set', base_material=current,
                machining_union_operands=[deepcopy(physical_op)], exact_material_properties=None)
    if finish_seen != set(finish):
        raise ValueError('Finishing operation/paid-owner coverage incomplete')
    # Aggregate once per parent so multiple finishing operands cannot nest/drop
    # an earlier operation or double-debit the same retained through void.
    for eid in {f['source_entity_id'] for f in finish_records}:
        relevant = [f['physical_operation'] for f in finish_records if f['source_entity_id'] == eid]
        base = local_physical[eid]
        while 'base_material' in base:
            base = base['base_material']
        local_physical[eid] = dict(id=eid, material_id=entities[eid]['material_id'],
            domain='prospective-finished-source-material-set', base_material=deepcopy(base),
            machining_union_operands=deepcopy(relevant), exact_material_properties=None)
        if eid in changed:
            expected = dict(source_entity_id=eid, source_parent_physical_sha256=identity(_physical_terminal(terminal, {eid: entities[eid]})[eid]),
                weld_parent_physical_sha256=identity(physical_parents[eid]),
                finishing_operand_sha256s=sorted(identity(x) for x in relevant))
            if eid not in union_map:
                hold('combined-cut-union-required', eid, expected)
            else:
                union = union_map[eid]
                if set(union) != {'id', 'schema', 'source_entity_id', 'source_parent_physical_sha256', 'weld_parent_physical_sha256', 'finishing_operand_sha256s', 'set_operation'} or union['schema'] != 'osr-terminal-explicit-cut-union/1' or any(union[k] != v for k,v in expected.items()) or union['set_operation'] != 'weld-revised-material minus union-of-complete-finishing-voids':
                    raise ValueError('Combined cut union operands/source epoch differ')
                union_used.add(eid); local_physical[eid]['explicit_cut_union'] = deepcopy(union)
                hold('combined-cut-union-evaluation-pending', eid, union)
    if union_used != set(union_map):
        raise ValueError('Extraneous combined cut union has no matching parent conflict')
    for eid in {f['source_entity_id'] for f in finish_records}:
        before_finishing = new_entities[eid]
        new_entities[eid] = dict(id=eid, material_id=before_finishing['material_id'], frame=FRAME,
            scope='prospective-local-installed-material', at_m=deepcopy(before_finishing['at_m']),
            rotation=deepcopy(before_finishing['rotation']),
            material_set_definition=deepcopy(local_physical[eid]),
            source_material_before_finishing=deepcopy(before_finishing),
            mass_kg=None, center_of_gravity_m=None, inertia_kg_m2=None,
            properties_status='Unapplied complete-void union and density context; old property proxies are ancestry only')
    for oid in paid_finish:
        before_finishing = new_groups[oid]
        new_groups[oid] = dict(deepcopy(before_finishing),
            source_paid_group_before_finishing=deepcopy(before_finishing),
            net_mass_kg=None, scrap_mass_kg=None,
            finished_material_property_status='Unknown until source finishing union/density/moments are evaluated; gross blank and direct source price retained once')
    _ownership(new_groups, new_entities, 'prospective local')
    if set(local_physical) != set(new_entities):
        raise ValueError('Final material projection/ledger coverage differs')

    # Known group prices are one payable row, never part subtotals + group again.
    prices = []
    for oid, group in new_groups.items():
        value = group.get('direct_cost_usd', group.get('direct_cost_label_cases_USD'))
        if value is None:
            hold('unknown-price-component', oid, 'No price is inserted as zero; retained partial owner scope')
        prices.append(dict(owner_id=oid, scope='one-local-terminal-group',
                           direct_cost_label_cases_USD=_cases(value), source_group=deepcopy(group)))
    for f in finish_records:
        value = f['source_record']['source_operation']['cost_USD']
        prices.append(dict(owner_id='finishing-operation/' + f['operation_id'], scope='one-local-machining-operation-no-new-blank',
                           direct_cost_label_cases_USD=_cases(value), source_operation_id=f['operation_id']))
    if len({x['owner_id'] for x in prices}) != len(prices):
        raise ValueError('Duplicate local payable owner')
    lifecycle = hardware['lifecycle_allocations']
    if len({x['id'] for x in lifecycle}) != len(lifecycle) or any(x['charged_in_installed_stock'] is not False for x in lifecycle):
        raise ValueError('Lifecycle tools cannot be installed or charged twice')
    for x in lifecycle:
        if 'count_per_train' in x and _count(x['count_per_train']) != 1:
            raise ValueError('Shared hardware service kit remains once per train')
    measured = dict(terminal_entities=len(entities), terminal_stock_groups=len(groups),
                    weld_routes=len(routes), defined_welds=len(defined), held_welds=len(held_ids),
                    filler_pieces=len(phys_fillers), revised_parents=len(changed),
                    new_connectors=len(new_parts), old_hardware_owners=len(retired_owners),
                    hardware_placements=len(occurrence_map), hardware_material_pieces=len(Hentities),
                    hardware_stock_groups=len(Hgroups), finishing_operations=len(finish),
                    finishing_paid_groups=len(paid_finish),
                    finishing_source_occurrences=len({f['source_entity_id'] for f in finish_records}),
                    paid_backing_ring_groups=len({f['paid_owner_id'] for f in finish_records if f['source_record']['source_operation']['kind'] == 'ring-access-port-enlargement'}),
                    shared_service_tool_pieces=sum(_count(x['source'].get('piece_count', 0)) for x in lifecycle),
                    inherited_P1_owner_groups=sum(bool(x['source_keys']) for x in retirement_inheritance),
                    local_research_hardware_owner_groups=sum(not x['source_keys'] for x in retirement_inheritance),
                    local_material_occurrences=len(new_entities),
                    local_stock_groups=len(new_groups))
    expected = input_pin['expected_counts']
    if set(expected) != set(measured) or any(type(v) is not int or v < 0 for v in expected.values()) or expected != measured:
        raise ValueError('Explicit source/local count contract differs')
    hc = hardware['counts']
    for value in hc.values():
        _count(value)
    if any(hc[k] != n for k,n in [('material_pieces',len(Hentities)),('placements',len(occurrence_map)),('new_stock_groups',len(Hgroups)),('old_owner_groups',len(retired_owners)),('finishing_paid_owner_groups',len(paid_finish)),('finishing_source_occurrences',len({f['source_entity_id'] for f in finish_records})),('source_finishing_operations',len(finish)),('paid_backing_rings',measured['paid_backing_ring_groups']),('shared_service_tool_pieces',measured['shared_service_tool_pieces'])]):
        raise ValueError('Hardware declared source counts differ')
    hold('inherited-source-contracts', 'terminal', terminal.get('source_holds', []))
    hold('inherited-source-contracts', 'hardware', hardware['original_source_contracts_and_holds'])
    hold('weld-load-WPS-and-neighbouring-domains', 'local', weld['holds'])
    hold('canonical-source-transactions-not-applied', 'local', 'Local prospective ledger only; no whole-body/canonical transaction or deployment generated')
    physical = dict(schema='osr-terminal-local-material-revision-physical/1', units='m', frame=FRAME,
        material_occurrences=[local_physical[k] for k in sorted(local_physical)],
        material_owner_graph=[dict(owner_id=k, entity_ids=sorted(new_groups[k]['entity_ids'])) for k in sorted(new_groups)])
    return seal(dict(schema='osr-terminal-local-revision-plan/1', request_id=request_id,
        source_input_pin=deepcopy(input_pin), source_local_epoch=deepcopy(common),
        ancestry=dict(terminal_evaluation_id=terminal['evaluation_id'], weld_evaluation_id=weld['evaluation_id'],
                      hardware_evaluation_id=hardware['evaluation_id']),
        physical_definition=physical, local_component_geometry_id=identity(physical),
        counts=measured, replacement_ledger=ledger,
        inherited_P1_retirements=retirement_inheritance,
        P1_old_leaf_retirement_ledger_owned_once_by_terminal=deepcopy(leaf_rows),
        source_finishing_records=finish_records, finishing_paid_owner_ids=sorted(paid_finish),
        overlay_conflicts=conflicts, density_context_records=density_contexts,
        canonical_local_draft=dict(schema='osr-terminal-local-material-draft/1', entities=[new_entities[k] for k in sorted(new_entities)],
            stock_groups=[new_groups[k] for k in sorted(new_groups)], material_projection=physical),
        canonical_definition=None, pending_contracts=pending,
        held_weld_records=deepcopy(held), deployment_data_unapplied=deepcopy(bindings),
        deployment_quantity_multiplier_applied=1,
        pricing=dict(rows=prices, complete_installed_cost=False, accounting_applied=False,
            common_source_residual_account=deepcopy(draft['source_account_coverage']),
            residual_scope='Original common consumable/process/QA/overhead source residual retained once; no regenerated complete cost or lost unknowns'),
        mass_properties=dict(aggregate_mass_kg=None, aggregate_CG_m=None, aggregate_inertia_kg_m2=None,
            reason='Source mass/CG/inertia hypotheses and unapplied finishing/union/density contexts remain bounded or unknown; no point properties invented'),
        lifecycle_allocations=dict(terminal=deepcopy(terminal['lifecycle_workshop']), hardware=deepcopy(lifecycle),
            scope='Original project/train/workshop/event scopes retained once; never local installed material or two-end multiplier'),
        source_transactions_applied=False, complete_installed_mass=False, complete_installed_cost=False, **FLAGS))
