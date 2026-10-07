from dataclasses import replace
import pytest
from osr_mech.civil.calendar import WorkingCalendar
from osr_mech.civil.shift_schedule import ShiftCycle,simulate_erection
from osr_mech.civil.supply import ErectionFront


def test_weekend_holiday_and_maintenance_closures_do_not_create_progress():
    calendar=WorkingCalendar('2027-01-01',weekdays=(0,1,2,3,4),holidays=('2027-01-04',),maintenance_days=('2027-01-05',))
    front=ErectionFront('a','line',0,50,1,'launcher','route','path',3)
    result=simulate_erection([front],ShiftCycle(),accepted_beams_day={1:4},delivered_beams_day={1:{'a':4}},
        supports_released_day={},buffer_capacity={'a':4},calendar=calendar,maximum_days=10)
    assert result['complete'] and result['finish_days']['a']==6
    assert all(r['cumulative_erected_beams']==2 for r in result['daily'][1:5])
    assert all(r['fronts'][0]['limiting_resource']=='working-calendar' for r in result['daily'][1:5])


def test_night_permission_and_dated_work_windows_limit_productivity():
    cycle=ShiftCycle(shifts_day=2,handover_hours=.5,maintenance_hours_day=.5)
    calendar=WorkingCalendar('2027-01-01',night_shift_permitted=False)
    assert calendar.hours(1,cycle)==7.5
    assert replace(calendar,permitted_hours_by_date=(('2027-01-01',4),)).hours(1,cycle)==3.5
    with pytest.raises(ValueError,match='evidence'):
        WorkingCalendar('2027-01-01',qualified=True)
