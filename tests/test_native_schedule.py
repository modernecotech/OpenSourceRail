"""Rust delivery scheduling is an explicit, differentially verified backend."""
import importlib.util
import os
from pathlib import Path
import random
import pytest

spec=importlib.util.spec_from_file_location('native_schedule',Path(__file__).parents[1]/'engineering/outline/native_schedule.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)


def fixtures(seed=0):
    rng=random.Random(seed)
    resources=[dict(resource_id='a',capacity_by_case={c:3 for c in ('low','base','high')}),
               dict(resource_id='b',capacity_by_case={c:2 for c in ('low','base','high')})]
    tasks=[]
    for i in range(20):
        predecessors=[f't{j:02}' for j in range(i) if rng.random()<.15]
        tasks.append(dict(task_id=f't{i:02}',ordinal=rng.randrange(4),predecessors=predecessors,
            duration_workdays={c:rng.choice([.1,.3,1.,1.0000000000000002,2.75]) for c in ('low','base','high')},
            resource_requests=[dict(resource_id=rng.choice(['a','b','unknown']),units=rng.randrange(0,5))]))
    return tasks,resources


def engine():
    binary=os.environ.get('OSR_SCHEDULE_BINARY');root=os.environ.get('OSR_SCHEDULE_ROOT')
    if not binary or not root:pytest.skip('Explicit prebuilt scheduler required; tests never build implicitly')
    return native.NativeSchedule(root,binary)


def test_typed_bridge_preserves_unknown_and_refuses_fractional_units():
    tasks,resources=fixtures();tasks[0]['resource_requests'][0]['units']=1.5
    with pytest.raises(ValueError,match='Integer resource units'):native.request(tasks,resources,'base')
    tasks[0]['resource_requests'][0]['units']=1
    tasks[0]['duration_workdays']['base']=None
    with pytest.raises(ValueError,match='Numeric duration'):native.request(tasks,resources,'base')


@pytest.mark.parametrize('seed',range(20))
def test_seeded_resource_dags_match_python_exactly(seed):
    from engineering.outline.delivery_plan import _schedule
    tasks,resources=fixtures(seed);rust=engine()
    for case in ('low','base','high'):
        assert rust.schedule(tasks,resources,case)==_schedule(tasks,resources,case)


def test_partial_start_before_invalid_request_and_overlap_error():
    from engineering.outline.delivery_plan import _schedule
    rust=engine();tasks,resources=fixtures();tasks=tasks[:2]
    tasks[0].update(ordinal=0,predecessors=[],resource_requests=[dict(resource_id='a',units=3)])
    tasks[1].update(ordinal=1,predecessors=[],resource_requests=[dict(resource_id='a',units=1),dict(resource_id='missing',units=1)])
    assert rust.schedule(tasks,resources,'base')==_schedule(tasks,resources,'base')
    tasks=tasks[:1];tasks[0]['resource_requests']=[dict(resource_id='b',units=2),dict(resource_id='b',units=2)]
    with pytest.raises(ValueError,match='Overlapping'):_schedule(tasks,resources,'base')
    with pytest.raises(ValueError,match='Overlapping'):rust.schedule(tasks,resources,'base')


def test_cycles_rejected_without_fallback():
    rust=engine();tasks,resources=fixtures();tasks=tasks[:1];tasks[0]['predecessors']=['t00']
    with pytest.raises(ValueError,match='Cyclic'):rust.schedule(tasks,resources,'base')
