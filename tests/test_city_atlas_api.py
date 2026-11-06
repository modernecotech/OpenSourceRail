from pathlib import Path
import json
import pytest
from engineering.outline import city_atlas_api as api

ROOT=Path(__file__).resolve().parents[1]


def test_current_calculations_are_bound_to_city_map():
    packet=api.published(ROOT,'samawah')
    assert packet['city']['slug']=='samawah'
    assert packet['summary']['lines']==len(packet['lines'])==5
    assert packet['summary']['total_trainsets']==sum(r['service']['total_trainsets'] for r in packet['lines'])
    assert len(packet['costs']['scope_totals_usd'])==14
    assert packet['physical_accepted'] is False
    assert packet['sources']['calculation_sha256'][packet['map_context']['path']]==packet['map_context']['sha256']


def test_ui_assets_are_owned_and_checked_separately_from_calculations(tmp_path):
    for name in api.ASSETS:
        source=tmp_path/'engineering/development_baseline/web'/name
        source.parent.mkdir(parents=True,exist_ok=True);source.write_text('source '+name)
    p=tmp_path/api.PRODUCER;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('publisher')
    (tmp_path/'docs/workbench/current').mkdir(parents=True)
    api.publish_assets(tmp_path)
    target=tmp_path/'docs/workbench/current'/api.ASSETS[0]
    api.verify_asset(tmp_path,api.ASSETS[0],target)
    target.write_text('changed')
    with pytest.raises(ValueError,match='asset differs'):api.verify_asset(tmp_path,api.ASSETS[0],target)


class Handler:
    root=ROOT
    command='GET'
    def respond(self,status,value):self.status,self.value=status,value


def test_failed_or_pending_study_cannot_replace_map(monkeypatch):
    class Pending:
        def artifact(self,*args):raise ValueError('City study is not complete')
    h=Handler();h.path='/api/city-atlas/study/'+'a'*32
    h.server=type('Server',(),{'city_studies':Pending()})()
    monkeypatch.setattr(api,'_loopback',lambda *a,**k:True)
    assert api.handle_api(h) and h.status==503
    assert h.value['physical_accepted'] is False
    h.path='/api/city-atlas/../../private'
    assert api.handle_api(h) and h.status==503
    h.command='POST';h.path='/api/city-atlas'
    assert api.handle_api(h) and h.status==405
