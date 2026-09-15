from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'deployment/erpnext/apps/osr_erpnext'))
from osr_erpnext.automation_rules import procurement_input, task_readiness


@pytest.mark.parametrize('qty', [0, -1, 'NaN', 'Infinity', 'two', 1000000001, None])
def test_request_rejects_invalid_quantities(qty):
    with pytest.raises(ValueError):
        procurement_input('candidate', 'item', qty, '2030-01-01', 'store')


def test_request_requires_explicit_item_date_warehouse_and_keeps_fractional_units():
    assert procurement_input('c', 'i', '2.5', '2030-01-01', 'w')['quantity'] == 2.5
    for args in [('c', '', 1, '2030-01-01', 'w'), ('c', 'i', 1, '', 'w'), ('c', 'i', 1, '2030-02-30', 'w')]:
        with pytest.raises(ValueError):
            procurement_input(*args)


def test_readiness_excludes_closed_work_and_does_not_invent_due_dates():
    tasks = [dict(status='Open', exp_end_date=None, _assign='[]'),
             dict(status='Working', exp_end_date='2026-01-01', _assign='["worker"]'),
             dict(status='Completed', exp_end_date='2026-01-01'),
             dict(status='Cancelled', exp_end_date=None),
             dict(status='Open', exp_end_date='2026-01-02', _assign='broken')]
    assert task_readiness(tasks, '2026-01-02') == dict(open_tasks=3, overdue=1, undated=1, unassigned=2)
