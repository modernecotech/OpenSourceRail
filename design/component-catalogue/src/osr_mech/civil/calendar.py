"""Explicit project working calendars; permission and named relief remain evidence."""
from dataclasses import dataclass
from datetime import date,timedelta
import math


@dataclass(frozen=True)
class WorkingCalendar:
    start_date: str
    weekdays: tuple[int,...] = (0,1,2,3,4,5,6)
    holidays: tuple[str,...] = ()
    maintenance_days: tuple[str,...] = ()
    permitted_hours_by_date: tuple[tuple[str,float],...] = ()
    night_shift_permitted: bool = True
    night_permission_record: str | None = None
    relief_roster_record: str | None = None
    qualified: bool = False

    def __post_init__(self):
        date.fromisoformat(self.start_date)
        if not self.weekdays or len(set(self.weekdays))!=len(self.weekdays) or any(type(d) is not int or not 0<=d<=6 for d in self.weekdays):
            raise ValueError('calendar weekdays must be distinct Monday=0 through Sunday=6')
        for value in (*self.holidays,*self.maintenance_days):date.fromisoformat(value)
        if len({d for d,_ in self.permitted_hours_by_date})!=len(self.permitted_hours_by_date):
            raise ValueError('duplicate calendar work-window overrides')
        for value,hours in self.permitted_hours_by_date:
            date.fromisoformat(value)
            if not math.isfinite(hours) or not 0<=hours<=24:raise ValueError('calendar hours must be in [0,24]')
        if self.qualified and (not self.relief_roster_record or (self.night_shift_permitted and not self.night_permission_record)):
            raise ValueError('qualified calendar requires relief and permitted-night evidence')

    def day_date(self,day):
        if day<1:raise ValueError('calendar days start at one')
        return date.fromisoformat(self.start_date)+timedelta(days=day-1)

    def hours(self,day,cycle):
        day_date=self.day_date(day);key=day_date.isoformat()
        if day_date.weekday() not in self.weekdays or key in self.holidays or key in self.maintenance_days:
            return 0.0
        scheduled=cycle.shifts_day*cycle.hours_shift if self.night_shift_permitted else cycle.hours_shift
        window=min(cycle.permitted_hours_day,dict(self.permitted_hours_by_date).get(key,24),scheduled)
        handover=(cycle.shifts_day-1)*cycle.handover_hours if self.night_shift_permitted else 0
        return max(0,window-handover-cycle.maintenance_hours_day)*cycle.productive_fraction*cycle.weather_availability
