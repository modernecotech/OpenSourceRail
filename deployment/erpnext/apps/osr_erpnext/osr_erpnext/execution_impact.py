"""Deterministic, read-only engineering exposure from permission-filtered ERP data."""
import hashlib
import json


def revision_review(mapping, fetch_bom, orders, work_orders, movements, visibility, scope):
    """Follow explicit BOM links only; never substitute an Item's current default BOM."""
    nodes, paths, warnings = {}, [], set()
    root = mapping.get('production_bom')

    def walk(name, expected_item, trail):
        if name in trail:
            warnings.add('Cyclic BOM reference: ' + name)
            return
        if len(trail) >= 32 or len(paths) >= 2000:
            warnings.add('BOM traversal limit reached; dependency coverage is incomplete')
            return
        node = fetch_bom(name)
        if not node:
            warnings.add('BOM unavailable to this reader: ' + name)
            return
        if node['item'] != expected_item:
            warnings.add('BOM/Item mismatch: ' + name)
            return
        nodes[name] = node
        path = [*trail, name]
        paths.append(dict(item=expected_item, bom=name, path=path))
        if node['docstatus'] != 1:
            warnings.add('BOM is no longer submitted: ' + name)
        for line in node['items']:
            if line.get('bom'):
                walk(line['bom'], line['item'], path)
            else:
                paths.append(dict(item=line['item'], bom=None, path=path))

    if root:
        walk(root, mapping['erp_item_code'], [])
    else:
        warnings.add('No reviewed production BOM; production dependency coverage is unavailable')
    # A readable parent names its purchased subassembly even if the child's
    # internal BOM cannot be inspected. Do not infer the hidden descendants.
    items = {mapping['erp_item_code'], *(p['item'] for p in paths),
             *(line['item'] for node in nodes.values() for line in node['items'])}
    pairs = {(p['item'], p['bom']) for p in paths if p['bom']}
    production = [r for r in work_orders if (r['item'], r['bom']) in pairs]
    names = {r['name'] for r in production}
    purchase = [dict(r, relationship='potential-item-exposure',
                     revision_assignment='unproven') for r in orders if r['item'] in items]
    stock = [r for r in movements if r['work_order'] in names]
    for dt, status in visibility.items():
        if status != 'visible-to-current-user':
            warnings.add(dt + ': ' + status)
    result = dict(schema='osr-execution-revision-review/1', scope=scope, mapping=mapping,
        bom_dependencies=[nodes[k] for k in sorted(nodes)], dependency_paths=paths,
        purchase_orders=purchase, work_orders=production, stock_movements=stock,
        warnings=sorted(warnings), visibility=visibility,
        coverage='visible-project-records-only',
        limitations=[
            'Purchase matches identify shared Item exposure, not allocation to an engineering revision.',
            'Stock entries are movements linked to matching Work Orders, not available stock or accepted WIP.',
            'Unlinked stock, other projects, drawings, solver reruns and formal evidence supersession require separate review.',
            'No record is changed, held, cancelled, accepted or released by this review.',
        ], automatic_disposition=False, railway_release_authorised=False)
    result['sha256'] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(',', ':'),
                                                allow_nan=False).encode()).hexdigest()
    return result
