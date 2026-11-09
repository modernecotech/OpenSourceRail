"""Explicit part units and disjoint cost ownership for planning, never release.

The input catalogue and prices remain immutable. A conversion re-expresses an
existing direct part/process amount; it does not create a quotation, raw-stock
price, manufacturing route or complete installed account. Unknowns are holds.
"""
from copy import deepcopy
from math import fsum, isclose, isfinite
from pathlib import Path

from engineering.station_rail.common import digest, identity

CASES = ('low', 'base', 'high')
PRODUCER = 'engineering/railway_project/part_accounts.py'
ROUTES = ('local-fabricate', 'buy-standard', 'buy-qualified')
UNITS = {'Nos': 'count', 'kg': 'mass', 'm': 'length', 'm2': 'area', 'm3': 'volume', 'Set': 'pack-count'}


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _text(value, name):
    _require(isinstance(value, str) and bool(value.strip()), 'Explicit '+name+' required')
    return value


def _hash(value, name):
    _require(isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value), 'Exact '+name+' identity required')
    return value


def _sealed(value, name):
    _require(isinstance(value,dict), 'Explicit '+name+' mapping required')
    _require(value.get('evaluation_id') == identity({k:v for k,v in value.items() if k != 'evaluation_id'}), 'Sealed '+name+' required')


def _index(rows, key, name):
    _require(isinstance(rows, list), name+' must be a list')
    result = {}
    for row in rows:
        _require(isinstance(row, dict), 'Explicit '+name+' row required')
        k = _text(row.get(key), name+' '+key)
        _require(k not in result, 'Duplicate '+name+': '+k)
        result[k] = row
    return result


def _cases(values, name, *, positive=False, unknown=False):
    _require(isinstance(values, dict) and set(values) == set(CASES), 'Explicit three-case '+name+' required')
    for value in values.values():
        if value is None and unknown:
            continue
        _require(type(value) in (int, float) and isfinite(value) and (value > 0 if positive else value >= 0), 'Invalid '+name)
    return dict(values)


def _owners(values, name):
    _require(isinstance(values, list) and bool(values), 'Explicit '+name+' required')
    for value in values:
        _text(value, name)
    _require(len(set(values)) == len(values), 'Duplicate '+name)
    return set(values)


def source_cost_identity(body, part, cost_evaluation_id):
    """Identity of exactly the existing priced quantity, basis and source part."""
    return identity(dict(body_candidate_id=body['candidate_id'], body_evaluation_id=body['evaluation_id'],
        source_part_sha256=identity(part), cost_evaluation_id=_hash(cost_evaluation_id, 'source cost evaluation'),
        part_id=part['id'], component_definition_id=part['component_definition_id'], currency='USD',
        source_unit=part['unit'], quantity_per_train=part['quantity_per_train'],
        direct_cost_each_usd=part.get('direct_cost_each_usd'), cost_basis=part.get('cost_basis'), source_ids=part.get('source_ids'),
        pattern_costs=[{k:p.get(k) for k in ('id','count','direct_cost_usd')} for p in body.get('patterns',[]) if p.get('part_id') == part['id']]))


def _stock(value, holds):
    if value is None:
        holds.append('Purchased gross stock, finished net stock and scrap not mapped')
        return None
    _require(isinstance(value, dict), 'Explicit stock mapping required')
    _text(value.get('basis'), 'stock basis'); _text(value.get('source_reference'), 'stock source')
    _require(value.get('quantity_basis') in ('gross-purchase', 'net-finished', 'bounded-component', 'unknown'), 'Explicit stock quantity basis required')
    result = deepcopy(value)
    fields = ('gross_each_kg', 'net_each_kg', 'scrap_each_kg')
    if any(value.get(k) is None for k in fields):
        holds.append('Gross/net/scrap stock relationship unknown; no yield inferred')
        return result
    for k in fields:
        _cases(value[k], k, positive=k != 'scrap_each_kg', unknown=True)
    if any(value[k][c] is None for k in fields for c in CASES):
        holds.append('Gross/net/scrap stock relationship has unknown case bounds; no yield inferred')
        return result
    _require(all(isclose(value['gross_each_kg'][c], value['net_each_kg'][c]+value['scrap_each_kg'][c], rel_tol=1e-10, abs_tol=1e-9) for c in CASES), 'Gross stock must equal net stock plus scrap')
    return result


def compile_accounts(body, contract, fleet, *, cost_evaluation_id):
    """Bind each counted part to an explicit planning UOM/route/account owner.

    Contract schema ``osr-part-account-contract/1`` binds the exact body, cost
    evaluation and fleet. Each row binds part/component/revision/source-cost
    identities, conversion, route, cost coverage and stock basis. Missing rows,
    rates or decisions remain held; contradictory or mixed identities fail.
    """
    _sealed(body, 'source body')
    _require(body.get('schema') == 'osr-vehicle-installation/1' and body.get('candidate_id') == identity(body.get('physical_definition')), 'Exact physical body candidate required')
    _require(type(fleet) is int and fleet > 0, 'Positive integer committed fleet required')
    _hash(cost_evaluation_id, 'cost evaluation')
    _require(isinstance(contract,dict) and contract.get('schema') == 'osr-part-account-contract/1', 'Explicit part account contract required')
    for key, expected in (('body_candidate_id', body['candidate_id']), ('body_evaluation_id', body['evaluation_id']), ('cost_evaluation_id', cost_evaluation_id), ('fleet', fleet)):
        _require(contract.get(key) == expected, 'Mixed part contract '+key)
    parts = _index(body['parts'], 'id', 'source part')
    patterns = _index(body.get('patterns',[]), 'id', 'source pattern')
    _require(all(p.get('part_id') in parts for p in patterns.values()), 'Orphan source cost pattern')
    mapping = _index(contract.get('rows'), 'part_id', 'part mapping')
    _require(not (set(mapping)-set(parts)), 'Orphan mapped part')
    rows = []
    for pid, part in parts.items():
        _hash(part.get('candidate_id'), 'component candidate'); _hash(part.get('component_definition_id'), 'component definition')
        quantity = part.get('quantity_per_train')
        _require(type(quantity) is int and quantity > 0, 'Positive integer counted part quantity required')
        source_id = source_cost_identity(body, part, cost_evaluation_id)
        m = mapping.get(pid); holds = []
        if not isinstance(part.get('cost_basis'),str) or not part['cost_basis'].strip() or not part.get('source_ids'):
            holds.append('Existing source price basis or evidence references missing')
        row = dict(part_id=pid, source_part_sha256=identity(part), source_cost_id=source_id,
            component_definition_id=part['component_definition_id'], component_candidate_id=part['candidate_id'],
            source_unit=part['unit'], source_make_buy=part['make_buy'], quantity_per_train=quantity,
            source_quantity_project=quantity*fleet, currency='USD', additive_to_existing_cost_ledger=False,
            valuation_basis='existing-direct-parts-process-only', procurement_release=False,
            target_unit=None, target_quantity_project=None, target_unit_rate_usd=None,
            project_direct_cost_usd=None, planning_route=None, account_owner=None, conversion=None, stock=None)
        if m is None:
            holds.append('Explicit per-part UOM, make/buy, cost coverage and account mapping missing')
        else:
            for key in ('source_part_sha256', 'source_cost_id', 'component_definition_id', 'component_candidate_id'):
                _require(m.get(key) == row[key], 'Mixed part/revision/cost identity: '+pid+'/'+key)
            row['account_owner'] = _text(m.get('account_owner'), 'component account owner')
            _require(m.get('valuation_basis') == row['valuation_basis'], 'Conversion cannot change the valuation scope')
            coverage = m.get('cost_coverage')
            if coverage is None:
                holds.append('Included/excluded/unknown price coverage missing')
            else:
                _require(isinstance(coverage, dict) and set(coverage) == {'included','excluded','unknown'}, 'Explicit cost coverage categories required')
                groups = [coverage[k] for k in ('included','excluded','unknown')]
                _require(all(isinstance(g,list) for g in groups) and any(groups), 'Explicit cost coverage required')
                flattened = [v for g in groups for v in g]
                _require(all(isinstance(v,str) and bool(v.strip()) for v in flattened) and len(set(flattened)) == len(flattened), 'Ambiguous or duplicate cost coverage')
                if coverage['unknown']:
                    holds.append('Price coverage remains unknown: '+', '.join(coverage['unknown']))
            row['cost_coverage'] = deepcopy(coverage)
            decision = m.get('make_buy')
            _require(decision is None or isinstance(decision,dict), 'Explicit make/buy decision mapping required')
            if decision is None or decision.get('planning_route') is None:
                holds.append('Make/buy route unresolved; no make default')
            else:
                _require(decision.get('planning_route') in ROUTES, 'Unsupported declared make/buy route')
                _text(decision.get('basis'), 'make/buy basis'); _text(decision.get('source_reference'), 'make/buy decision source')
                row['planning_route'] = decision['planning_route']
            row['make_buy_decision'] = deepcopy(decision)
            row['stock'] = _stock(m.get('stock'), holds)
            conversion = m.get('conversion')
            if conversion is None:
                holds.append('Explicit source-to-target UOM conversion missing; no Nos default')
            else:
                _require(isinstance(conversion,dict) and conversion.get('source_unit') == part['unit'], 'Mixed conversion source unit')
                _text(conversion.get('basis'), 'unit conversion basis'); _text(conversion.get('source_reference'), 'unit conversion source')
                target = conversion.get('target_unit')
                _require(target in UNITS, 'Unsupported explicit target UOM')
                factor = conversion.get('target_per_source')
                if factor is None:
                    holds.append('Unknown unit conversion factor')
                else:
                    factor = _cases(factor, 'unit conversion factor', positive=True)
                    basis = conversion.get('measurement_basis')
                    if target == 'kg':
                        field = {'gross-purchase-mass':'gross_each_kg', 'net-finished-mass':'net_each_kg'}.get(basis)
                        _require(field is not None, 'Mass conversion must distinguish gross purchase and net finished mass')
                        stock = row['stock']
                        if stock is None or stock.get(field) is None:
                            holds.append('Mass conversion lacks its declared gross/net stock evidence')
                        elif any(stock[field][c] is None for c in CASES):
                            holds.append('Mass conversion has unknown declared stock case bounds')
                        else:
                            _require(all(isclose(factor[c],stock[field][c],rel_tol=1e-10) for c in CASES), 'Mass conversion differs from declared stock basis')
                    else:
                        _require(basis == UNITS[target], 'Unit conversion measurement basis differs')
                    row['target_unit'] = target
                    row['target_quantity_project'] = {c:quantity*fleet*factor[c] for c in CASES}
                    if target in ('Nos','Set') and any(not isclose(v,round(v),abs_tol=1e-9) for v in row['target_quantity_project'].values()):
                        holds.append('Fractional count/pack requires an explicit purchasing revision; no rounding or extra price inferred')
                    rates = part.get('direct_cost_each_usd')
                    if rates is None:
                        holds.append('Source price unknown; no zero or kit allowance invented')
                    else:
                        rates = _cases(rates, 'source price', unknown=True)
                        if any(rates[c] is None or rates[c] == 0 for c in CASES):
                            holds.append('Source price missing or unsubstantiated zero')
                        else:
                            row['target_unit_rate_usd'] = {c:rates[c]/factor[c] for c in CASES}
                            row['project_direct_cost_usd'] = {c:quantity*fleet*rates[c] for c in CASES}
                            _require(all(isclose(row['target_quantity_project'][c]*row['target_unit_rate_usd'][c],row['project_direct_cost_usd'][c],rel_tol=1e-12) for c in CASES), 'Quantity-price conversion does not conserve cost')
                row['conversion'] = deepcopy(conversion)
        if patterns:
            counted = [p for p in patterns.values() if p['part_id'] == pid]
            _require(all(type(p.get('count')) is int and p['count'] > 0 for p in counted) and
                     sum(p['count'] for p in counted) == quantity, 'Source cost pattern quantity differs: '+pid)
            if any(p.get('direct_cost_usd') is None for p in counted):
                pattern_cost = None
            else:
                values = [_cases(p['direct_cost_usd'],'source pattern price',unknown=True) for p in counted]
                pattern_cost = None if any(v[c] is None for v in values for c in CASES) else {c:fsum(v[c] for v in values) for c in CASES}
            row['source_pattern_cost_per_train_usd'] = pattern_cost
            if pattern_cost is None or (row['project_direct_cost_usd'] is not None and
                any(not isclose(row['project_direct_cost_usd'][c],fleet*pattern_cost[c],rel_tol=1e-10,abs_tol=1e-6) for c in CASES)):
                holds.append('Part each price and counted pattern subtotal unresolved; explicit cost allocation revision required')
                row['project_direct_cost_usd'] = None
                row['target_unit_rate_usd'] = None
        row['holds'] = holds; row['status'] = 'held' if holds else 'ready-for-planning-review'
        row['account_id'] = identity(row); rows.append(row)
    held = [r['part_id'] for r in rows if r['holds']]
    result = dict(schema='osr-part-account-evaluation/1', body_candidate_id=body['candidate_id'],
        body_evaluation_id=body['evaluation_id'], parent_candidate_id=body.get('parent_candidate_id'),
        cost_evaluation_id=cost_evaluation_id, fleet=fleet, contract_id=identity(contract), rows=rows,
        all_source_parts_mapped=not held, held_part_ids=held, cost_addition_authorized=False,
        physical_accepted=False, manufacturing_release=False, operating_release=False,
        source_sha256={PRODUCER:digest(Path(__file__))})
    result['evaluation_id'] = identity(result)
    return result


def planning_body(body, accounts):
    """A labelled, nonphysical projection for the retained planning compiler.

    Only the planning make/buy category is adapted. Original source unit,
    physical quantities, costs and source definitions are retained verbatim in
    the original body and the account identity. The retained compiler requires
    evaluation_id as a source engineering-revision alias for serial planning;
    this labelled projection has no physical candidate and is never resealed.
    """
    _sealed(accounts, 'part account evaluation')
    _require(accounts['body_candidate_id'] == body['candidate_id'] and accounts['body_evaluation_id'] == body['evaluation_id'], 'Mixed planning body revision')
    mapping = _index(accounts['rows'], 'part_id', 'part account')
    _require(set(mapping) == {p['id'] for p in body['parts']}, 'Complete planning projection required')
    projected = {k:deepcopy(body[k]) for k in ('parts','patterns','materials','total_occurrences','direct_parts_process_usd')}
    projected.update(schema='osr-unsealed-part-planning-projection/1',evaluation_id=body['evaluation_id'],
        evaluation_id_role='Source body engineering revision alias only; not this projection identity',
        part_accounts_evaluation_id=accounts['evaluation_id'])
    for p in projected['parts']:
        row = mapping[p['id']]
        _require(row['source_part_sha256'] == identity(p), 'Changed source part after mapping')
        p['make_buy'] = row['planning_route'] or 'bounded-purchased-or-processed'
    return projected


def bridge_accounts(accounts, legacy, replacements, *, additions=()):
    """Return a declared disjoint research ledger, never apply an implicit credit.

    Legacy accounts are sealed, project-quantity USD accounts with explicit
    coverage_owner_ids. A credit requires matching account bytes, direct
    candidate ancestry (or the identical candidate), exact replacement parts,
    ownership coverage and explicit low/base/high amounts. Unrelated candidates,
    reused credits or overlapping uncredited owners are rejected.
    """
    _sealed(accounts, 'part accounts'); _sealed(legacy, 'legacy account ledger')
    _hash(legacy.get('candidate_id'), 'legacy candidate')
    _require(legacy['candidate_id'] == accounts['body_candidate_id'] or
             (accounts.get('parent_candidate_id') is not None and legacy['candidate_id'] == accounts['parent_candidate_id']),
             'Unrelated candidate accounts cannot enter the bridge')
    _require(legacy.get('schema') == 'osr-legacy-part-accounts/1' and legacy.get('currency') == 'USD' and legacy.get('quantity_basis') == 'project' and legacy.get('fleet') == accounts['fleet'], 'Explicit same-project legacy account scope required')
    named = _index(accounts['rows'], 'part_id', 'named part account')
    old = _index(legacy['accounts'], 'account_id', 'legacy account')
    credits = _index(replacements, 'legacy_account_id', 'replacement credit')
    _require(not (set(credits)-set(old)), 'Unknown legacy replacement account')
    coverage = {}; old_total = {}; holds = []
    for aid, row in old.items():
        _cases(row['cost_usd'], 'legacy account cost', unknown=True)
        coverage[aid] = _owners(row.get('coverage_owner_ids'), 'legacy coverage owners')
        _text(row.get('basis'), 'legacy cost basis')
    _require(not any(coverage[a]&coverage[b] for i,a in enumerate(old) for b in list(old)[i+1:]), 'Overlapping legacy account ownership')
    used = set(); credit_rows = []
    for aid, credit in credits.items():
        row = old[aid]
        _require(credit.get('legacy_account_sha256') == identity(row) and credit.get('legacy_evaluation_id') == legacy['evaluation_id'], 'Mixed legacy account/revision credit')
        for k in ('body_candidate_id','body_evaluation_id','cost_evaluation_id'):
            _require(credit.get(k) == accounts[k], 'Mixed replacement '+k)
        _require(credit.get('part_accounts_evaluation_id') == accounts['evaluation_id'], 'Mixed replacement part account evaluation')
        ancestor = legacy.get('candidate_id')
        same = ancestor == accounts['body_candidate_id']
        _require(same or (accounts.get('parent_candidate_id') is not None and ancestor == accounts['parent_candidate_id']), 'Unrelated candidate allowance cannot be credited')
        _require(credit.get('ancestry') == ('same-candidate' if same else 'direct-parent-revision'), 'Explicit supported replacement ancestry required')
        _text(credit.get('basis'), 'replacement basis'); _text(credit.get('source_reference'), 'replacement ownership source')
        pids = _owners(credit.get('part_ids'), 'replacement part IDs')
        _require(pids <= set(named) and not(pids&used), 'Orphan or duplicate replacement part')
        owners = _owners(credit.get('replaced_owner_ids'), 'replaced owners')
        _require(owners <= coverage[aid] and {named[p]['account_owner'] for p in pids} == owners, 'Replacement component/account ownership differs')
        expected = {p for p,r in named.items() if r['account_owner'] in owners}
        _require(pids == expected, 'Replacement ownership omits named parts')
        kept = set(credit.get('retained_owner_ids', []))
        _require(kept == coverage[aid]-owners, 'Unreplaced legacy ownership must remain explicit')
        amounts = _cases(credit.get('replacement_credit_usd'), 'explicit replacement credit', positive=True)
        remainder = {}
        for c in CASES:
            if row['cost_usd'][c] is None:
                holds.append('Unknown legacy price cannot support bounded credit: '+aid+'/'+c)
                remainder[c] = None
            else:
                remainder[c] = row['cost_usd'][c]-amounts[c]
                _require(remainder[c] >= 0 and (remainder[c] > 0 if kept else isclose(remainder[c],0,abs_tol=1e-9)), 'Credit exceeds ownership or erases an unreplaced reserve')
        used |= pids
        credit_rows.append(dict(legacy_account_id=aid,part_ids=sorted(pids),retained_owner_ids=sorted(kept),replacement_credit_usd=amounts,retained_cost_usd=remainder,source_credit_id=identity(credit)))
    added = set(); addition_rows = []
    _require(isinstance(additions, (list,tuple)), 'Explicit disjoint additions list required')
    for declaration in additions:
        _require(isinstance(declaration,dict), 'Explicit disjoint addition required')
        _require(declaration.get('legacy_evaluation_id') == legacy['evaluation_id'] and
                 declaration.get('body_candidate_id') == accounts['body_candidate_id'] and
                 declaration.get('body_evaluation_id') == accounts['body_evaluation_id'] and
                 declaration.get('cost_evaluation_id') == accounts['cost_evaluation_id'] and
                 declaration.get('part_accounts_evaluation_id') == accounts['evaluation_id'], 'Mixed disjoint addition revision')
        _require(declaration.get('legacy_accounts_sha256') == {k:identity(v) for k,v in old.items()}, 'Complete legacy account scope required for disjoint addition')
        _text(declaration.get('basis'), 'disjoint addition basis'); _text(declaration.get('source_reference'), 'disjoint addition ownership source')
        pids = _owners(declaration.get('part_ids'), 'disjoint addition part IDs')
        _require(pids <= set(named) and not (pids&(used|added)), 'Orphan or duplicate disjoint addition part')
        _require(all(named[p]['account_owner'] not in owners for p in pids for owners in coverage.values()), 'Disjoint addition overlaps legacy coverage')
        added |= pids
        addition_rows.append(dict(part_ids=sorted(pids),source_declaration_id=identity(declaration)))
    for pid, row in named.items():
        if row['account_owner'] is None or row['project_direct_cost_usd'] is None or row['holds']:
            holds.append('Named part mapping/price held: '+pid)
        overlaps = [a for a in old if row['account_owner'] in coverage[a]]
        _require(not overlaps or pid in used, 'Named part overlaps an uncredited legacy residual: '+pid)
        if pid not in used|added:
            holds.append('Named part needs explicit disjoint addition ownership declaration: '+pid)
    for c in CASES:
        old_total[c] = None if any(r['cost_usd'][c] is None for r in old.values()) else fsum(r['cost_usd'][c] for r in old.values())
    known = {c:fsum(r['project_direct_cost_usd'][c] for r in named.values() if r['project_direct_cost_usd'] is not None) for c in CASES}
    credit_total = {c:fsum(r['replacement_credit_usd'][c] for r in credit_rows) for c in CASES}
    total = {c:None if holds or old_total[c] is None else old_total[c]+known[c]-credit_total[c] for c in CASES}
    result = dict(schema='osr-part-account-bridge/1',body_candidate_id=accounts['body_candidate_id'],
        body_evaluation_id=accounts['body_evaluation_id'],part_accounts_evaluation_id=accounts['evaluation_id'],
        legacy_evaluation_id=legacy['evaluation_id'],legacy_candidate_id=legacy['candidate_id'],
        legacy_project_cost_usd=old_total,known_named_cost_subtotal_usd=known,
        explicit_replacement_credit_usd=credit_total,credits=credit_rows,disjoint_additions=addition_rows,project_direct_cost_usd=total,
        holds=holds,status='held' if holds else 'declared-disjoint-planning-ledger',
        additive_to_existing_cost_ledger=False,physical_accepted=False,manufacturing_release=False,
        limitations=['Declared account coverage and direct parent ancestry are checked, not authenticated physical or supplier evidence.',
            'Only declared project-quantity direct costs; complete installation, final assembly, tooling, financing, delivery and lifecycle remain separate scopes.'])
    result['evaluation_id'] = identity(result)
    return result
