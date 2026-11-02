"""Current fixture transport contracts; mocks are not engineering evidence."""
from functools import lru_cache
import pytest
from engineering.sourced_case import coordinator,FLAGS
from engineering.sourced_redesign import bolster
from engineering.station_rail.common import digest,identity,encoded
from engineering.sourced_case.tests import portable_fixtures as f


@pytest.fixture
def generated(monkeypatch):
    # Unit mocks get a private cache, preserving costly real fixtures shared by other modules.
    monkeypatch.setattr(f,'_current_bytes',lru_cache(maxsize=3)(f._current_bytes.__wrapped__));calls=[]
    def vehicle(kind):
        cid=f.EXPECTED[kind]
        value=dict(candidate_id=cid,registry=dict(candidate_id=cid,physical_journey_completed=False,complete_installed_design=False,**{k:v for k,v in FLAGS.items() if k!='selected_reference_changed'}),
            physical_journey_completed=False,mass_complete=False,complete_installed_vehicle_mass_kg=None,
            source_sha256={'engineering/sourced_case/equipment.py':digest(f.ROOT/'engineering/sourced_case/equipment.py')},nested=dict(values=[1,2]),**FLAGS)
        value['evaluation_id']=identity(value);return value
    def revise(name,*,root):
        assert root==f.ROOT;calls.append(('equipped',name));return dict(vehicle=vehicle('equipped-'+name.lower()))
    def revise_bolster(parent,*,root):
        assert root==f.ROOT and parent['candidate_id']==f.EXPECTED['equipped-v4'];calls.append(('bolstered',parent['candidate_id']))
        parent['nested']['values'].append('generator-local mutation')
        return vehicle('bolstered-v4')
    monkeypatch.setattr(coordinator,'revised',revise);monkeypatch.setattr(bolster,'revision',revise_bolster)
    def no_archive(*a,**kw):raise AssertionError('Current fixture must not read or reseal published inputs')
    monkeypatch.setattr(f,'published',no_archive)
    yield calls,vehicle
    f._current_bytes.cache_clear()


def test_current_generates_each_kind_once_and_returns_independent_copies(generated):
    calls,vehicle=generated
    first=f.current('equipped-v4');before=encoded(first);first['nested']['values'].append('caller mutation')
    again=f.current('equipped-v4');assert encoded(again)==before and first is not again
    result=f.current('bolstered-v4');result['nested']['values'].append('another caller')
    assert encoded(f.current('bolstered-v4'))==encoded(vehicle('bolstered-v4'))
    assert encoded(f.current('equipped-v4'))==before
    assert f.current('equipped-v1')['candidate_id']==f.EXPECTED['equipped-v1']
    assert calls==[('equipped','V4'),('bolstered',f.EXPECTED['equipped-v4']),('equipped','V1')]
    assert all(isinstance(value,bytes) for value in (f._current_bytes(kind) for kind in f.EXPECTED))


@pytest.mark.parametrize('change', ['candidate','release','mass','source','evaluation'])
def test_current_rejects_changed_candidate_holds_or_stale_generator_result(generated,monkeypatch,change):
    calls,vehicle=generated;value=vehicle('equipped-v4')
    if change=='candidate':value['candidate_id']='0'*64
    elif change=='release':value['physical_accepted']=True
    elif change=='mass':value['complete_installed_vehicle_mass_kg']=123.
    elif change=='source':value['source_sha256']['engineering/sourced_case/equipment.py']='0'*64
    if change=='evaluation':value['evaluation_id']='0'*64
    else:value.pop('evaluation_id');value['evaluation_id']=identity(value)
    original=encoded(value);monkeypatch.setattr(coordinator,'revised',lambda *a,**kw:dict(vehicle=value))
    with pytest.raises(ValueError):f.current('equipped-v4')
    assert encoded(value)==original
