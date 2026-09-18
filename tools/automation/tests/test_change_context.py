import hashlib
import importlib.util
from datetime import datetime, timezone
from pathlib import Path
import copy

import pytest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('change_context',ROOT/'tools/automation/change_context.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
NOW=datetime(2026,9,18,12,tzinfo=timezone.utc)


def fixture(root):
    p=root/'design/model.ifc';p.parent.mkdir();p.write_text('geometry')
    package=dict(city='samawah',environment='simulation',engineering_revision='r1',sha256='package',equipment=[dict(erp_project='P1',company_id='Company')])
    engineering=dict(city='samawah',engineering_revision='r1',artifacts=[dict(path='design/model.ifc',sha256=hashlib.sha256(p.read_bytes()).hexdigest())])
    portfolio=dict(snapshots=[dict(city='samawah',project='P1',company='Company',engineering_revision='r1',observed_at=NOW.isoformat(),execution=dict(production=[]))])
    return package,engineering,portfolio


def test_current_observation_does_not_grant_engineering_release(tmp_path):
    args=fixture(tmp_path);result=c.assess(tmp_path,*args,now=NOW)
    assert result['observations_current']
    assert result['engineering_release_ready'] is False
    changed=copy.deepcopy(args);changed[2]['snapshots'][0]['execution']['production'].append(dict(name='WO1'))
    assert c.assess(tmp_path,*changed,now=NOW)['sha256']!=result['sha256']


@pytest.mark.parametrize('change',['city','company','project','revision','old','future','naive','missing','duplicate','engineering-revision','artifact','escape'])
def test_invalid_context_cannot_be_presented_as_current(tmp_path,change):
    package,engineering,portfolio=fixture(tmp_path);row=portfolio['snapshots'][0]
    if change in {'city','company','project'}:row[change]='wrong'
    if change=='revision':row['engineering_revision']='r0'
    if change=='old':row['observed_at']='2026-09-18T11:54:59Z'
    if change=='future':row['observed_at']='2026-09-18T12:01:01Z'
    if change=='naive':row['observed_at']='2026-09-18T12:00:00'
    if change=='missing':portfolio['snapshots']=[]
    if change=='duplicate':portfolio['snapshots'].append(row.copy())
    if change=='engineering-revision':engineering['engineering_revision']='r0'
    if change=='artifact':(tmp_path/'design/model.ifc').write_text('changed geometry')
    if change=='escape':engineering['artifacts'][0]['path']='../outside'
    result=c.assess(tmp_path,package,engineering,portfolio,now=NOW)
    assert not result['observations_current'] and result['blockers']
