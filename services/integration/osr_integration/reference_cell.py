"""Candidate-bound research delivery bridge; no live production submission."""
from copy import deepcopy
from engineering.station_rail.common import identity


def delivery_drafts(report,*,active_orders=()):
    """Export immutable drafts; active orders remain bound to their released revision."""
    candidate=report['candidate_id'];m=report['manufacturing']
    if m['candidate_id']!=candidate or report['bundle']['candidate_id']!=candidate:
        raise ValueError('Delivery must bind the exact integrated cell')
    drafts=deepcopy(m['ERPNext'])
    if drafts['external_transactions_performed'] or drafts['production_orders'] or any(i.get('disabled')!=1 for i in drafts['items']):
        raise ValueError('Research bridge cannot activate items or issue production orders')
    changes=[]
    for order in active_orders:
        if not order.get('order_id') or not order.get('candidate_id') or not order.get('released_revision_id'):
            raise ValueError('Active production orders need immutable released bindings')
        if order['candidate_id']!=candidate:
            changes.append(dict(order_id=order['order_id'],released_candidate_id=order['candidate_id'],proposed_candidate_id=candidate,
                action='human-change-control-review',active_order_mutated=False))
    value=dict(schema='osr-reference-cell-delivery-bridge/1',candidate_id=candidate,body_candidate_id=report['body_candidate_id'],
        part_registry_revision_id=report['bundle']['mass_registry_revision_id'],drafts=drafts,
        construction_sequence=deepcopy(report['civil']['construction_sequence']),change_reviews=changes,
        active_orders_mutated=False,assets_activated=False,equipment_commissioned=False,live_movement_authority=False,
        required_handovers=['Approved Item/BOM/route/resource revisions','Released manufacturing batches and inspections',
            'Surveyed and approved civil erection/QA','Serial installed asset and maintained configuration','Authenticated commissioning and GoA4 hardware/safety evidence'])
    value['bridge_id']=identity(value);return value
