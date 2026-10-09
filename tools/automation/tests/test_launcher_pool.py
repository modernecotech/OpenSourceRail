"""Queued fronts conserve actual machine and support-release-team capacity."""
import importlib.util
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('launcher_pool_study',ROOT/'tools/automation/connected-build-study.py')
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
from osr_mech.civil.supply import ErectionFront
from osr_mech.civil.shift_schedule import ShiftCycle,simulate_erection


def test_queued_fronts_complete_without_creating_extra_machines_or_foundation_teams():
    fronts=[ErectionFront(f'f{i}',f'line-{i}',0.,50.,1,f'old-{i}',f'access-{i}',f'path-{i}',0,
                          relocation_days=1,work_intervals_m=((0.,50.),)) for i in range(6)]
    queued=module.bind_launcher_pool(fronts,2)
    assert len({f.launcher for f in queued})==2
    assert queued[2].predecessors==('f0',) and queued[4].predecessors==('f2',)
    cycle=ShiftCycle()
    releases=module.foundation_release_calendar(queued,cycle,{'foundation_release_supports_day_per_front':1},30)
    assert all(sum(day.values())<=2 for day in releases.values())
    result=simulate_erection(queued,cycle,accepted_beams_day={1:24},
                            delivered_beams_day={1:{f.id:4 for f in queued}},
                            supports_released_day=releases,buffer_capacity={f.id:4 for f in queued},maximum_days=30)
    assert result['complete']
    for front in queued:
        if front.predecessors:
            parent=front.predecessors[0]
            first_work=next(d['day'] for d in result['daily'] if any(r['front']==front.id and r['limiting_resource']=='erection' for r in d['fronts']))
            assert first_work>result['finish_days'][parent]
