"""The retained history of a removed position must not stop active telemetry."""
import importlib.util
import json
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'services/integration'))
SPEC = importlib.util.spec_from_file_location('supervision_simulator', ROOT / 'tools/automation/supervision-simulator.py')
SIM = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SIM)


def test_retired_factory_history_does_not_interrupt_active_equipment(monkeypatch, tmp_path):
    config = tmp_path / 'var/supervision/integration.json'
    config.parent.mkdir(parents=True)
    config.write_text(json.dumps({'principals':[{'role':'controller','subject':'simulator','token':'test-only','cities':['test']}]}))
    monkeypatch.setattr(SIM, 'ROOT', tmp_path)
    monkeypatch.setattr(sys, 'argv', ['supervision-simulator'])
    sent = []
    class Bridge:
        def evaluate(self, *args):
            return {('vehicle-bms','soc_pct'):72}
        def close(self):
            pass
    monkeypatch.setattr(SIM, 'EmbeddedBridge', Bridge)
    def request(url, data=None, headers=None):
        if '/snapshot?' in url:
            return {'assets':[
                {'configuration_status':'retired','manufacturing_method':{'old_metadata':True}},
                {'configuration_status':'active','asset_id':'T-RS-001:vehicle-bms','site_id':'T-RS-001',
                 'equipment_type':'vehicle-bms','measurements':{'soc_pct':{'unit':'%'}}}]}
        if url.endswith('/telemetry'):
            sent.append(data)
            return {}
        if url.endswith('/controller/commands'):
            return []
        raise AssertionError(url)
    monkeypatch.setattr(SIM, 'request_json', request)
    def stop_after_one_cycle(_):
        raise KeyboardInterrupt
    monkeypatch.setattr(SIM.time, 'sleep', stop_after_one_cycle)
    with pytest.raises(KeyboardInterrupt):
        SIM.main()
    assert len(sent) == 1
    assert sent[0]['asset_id'] == 'T-RS-001:vehicle-bms'
    assert sent[0]['value'] == 72 and sent[0]['quality'] == 'valid'


def test_sampling_setting_changes_telemetry_without_delaying_commands(monkeypatch,tmp_path):
    config=tmp_path/'integration.json'
    config.write_text(json.dumps({'principals':[{'role':'controller','subject':'simulator','token':'test','cities':['test']}]}))
    monkeypatch.setattr(sys,'argv',['sim','--config',str(config),'--controls',str(tmp_path/'controls.json'),'--url','http://example.test:8192'])
    clock=[0];samples=[];polls=[]
    class Bridge:
        def evaluate(self,*args):return {('vehicle-bms','soc_pct'):72}
        def close(self):pass
    monkeypatch.setattr(SIM,'EmbeddedBridge',Bridge)
    monkeypatch.setattr(SIM.time,'monotonic',lambda:clock[0])
    def request(url,data=None,headers=None):
        assert url.startswith('http://example.test:8192/')
        if '/snapshot?' in url:
            return {'historian':{'sampling_seconds':4},'assets':[{'asset_id':'T:vehicle','site_id':'T',
                'equipment_type':'vehicle-bms','measurements':{'soc_pct':{'unit':'%'}}}]}
        if url.endswith('/telemetry'):samples.append(clock[0]);return {}
        if url.endswith('/controller/commands'):polls.append(clock[0]);return []
        raise AssertionError(url)
    monkeypatch.setattr(SIM,'request_json',request)
    def advance(seconds):
        clock[0]+=seconds
        if clock[0]>8:raise KeyboardInterrupt
    monkeypatch.setattr(SIM.time,'sleep',advance)
    with pytest.raises(KeyboardInterrupt):SIM.main()
    assert samples==[0,4,8]
    assert len(polls)==17
