"""Pure rules for operating exceptions and explicit procurement inputs."""
from datetime import date
from decimal import Decimal, InvalidOperation
import json


def procurement_input(requirement_id, item_code, quantity, schedule_date, warehouse):
    for value in [requirement_id, item_code, schedule_date, warehouse]:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Requirement, Item, required date and city warehouse are required")
    try:
        number = Decimal(str(quantity))
    except InvalidOperation as exc:
        raise ValueError("Quantity must be a positive finite number") from exc
    if not number.is_finite() or number <= 0 or number > Decimal('1000000000'):
        raise ValueError("Quantity must be positive, finite and at most one billion")
    day = date.fromisoformat(schedule_date).isoformat()
    return dict(requirement_id=requirement_id, item_code=item_code,
                quantity=float(number), schedule_date=day, warehouse=warehouse)


def task_readiness(tasks, today):
    """Counts visible unfinished work; undated work is never labelled overdue."""
    result = dict(open_tasks=0, overdue=0, undated=0, unassigned=0)
    anchor = date.fromisoformat(str(today))
    for row in tasks:
        if row['status'] in {'Completed', 'Cancelled'}:
            continue
        result['open_tasks'] += 1
        end = row.get('exp_end_date')
        if not end:
            result['undated'] += 1
        elif date.fromisoformat(str(end)) < anchor:
            result['overdue'] += 1
        try:
            assignees = json.loads(row.get('_assign') or '[]')
        except (ValueError, TypeError):
            assignees = []
        if not isinstance(assignees, list) or not assignees:
            result['unassigned'] += 1
    return result
