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


@pytest.mark.parametrize('asset_count', [1, 129])
def test_retired_factory_history_does_not_interrupt_active_equipment(monkeypatch, tmp_path, asset_count):
    config = tmp_path / 'var/supervision/integration.json'
    config.parent.mkdir(parents=True)
    config.write_text(json.dumps({'principals':[{'role':'controller','subject':'simulator','token':'test-only','cities':['test']}]}))
    monkeypatch.setattr(SIM, 'ROOT', tmp_path)
    monkeypatch.setattr(sys, 'argv', ['supervision-simulator'])
    sent, batches = [], []
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
                *[{'configuration_status':'active','asset_id':f'T-RS-{i:03d}:vehicle-bms','site_id':f'T-RS-{i:03d}',
                 'equipment_type':'vehicle-bms','measurements':{'soc_pct':{'unit':'%'}}} for i in range(1, asset_count + 1)]]}
        if url.endswith('/telemetry/batch'):
            sent.extend(data['readings'])
            batches.append(len(data['readings']))
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
    assert len(sent) == asset_count
    assert batches == ([1] if asset_count == 1 else [128, 1])
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
        if url.endswith('/telemetry/batch'):samples.append(clock[0]);return {}
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


@pytest.mark.parametrize('gate', ['local_remote_disabled', 'disconnected'])
def test_command_reads_local_gate_after_telemetry_and_poll(monkeypatch, tmp_path, gate):
    config, controls = tmp_path/'integration.json', tmp_path/'controls.json'
    config.write_text(json.dumps({'principals': [
        {'role': 'controller', 'subject': 'simulator', 'token': 'test', 'cities': ['test']}]}))
    controls.write_text('{}')
    monkeypatch.setattr(sys, 'argv', ['sim', '--config', str(config), '--controls', str(controls)])
    evaluations, results = [], []
    class Bridge:
        def evaluate(self, key, level, local):
            evaluations.append(level)
            return {('facilities', 'lighting_pct'): level}
        def close(self): pass
    monkeypatch.setattr(SIM, 'EmbeddedBridge', Bridge)
    def request(url, data=None, headers=None):
        if '/snapshot?' in url:
            return {'assets': [{'asset_id': 'T:facilities', 'site_id': 'T',
                'equipment_type': 'facilities', 'measurements': {'lighting_pct': {'unit': '%'}}}]}
        if url.endswith('/telemetry/batch'): return {}
        if url.endswith('/controller/commands'):
            # The local input changes after this cycle's telemetry was computed.
            controls.write_text(json.dumps({'cities': {'test': {gate: True}}}))
            return [{'city': 'test', 'asset_id': 'T:facilities', 'command': 'set_lighting',
                     'parameters': {'level': 50}, 'request_id': 'gate-race'}]
        if url.endswith('/controller/result'): results.append(data); return {}
        raise AssertionError(url)
    monkeypatch.setattr(SIM, 'request_json', request)
    def stop(_): raise KeyboardInterrupt
    monkeypatch.setattr(SIM.time, 'sleep', stop)
    with pytest.raises(KeyboardInterrupt): SIM.main()
    assert [r['state'] for r in results] == ['rejected']
    assert evaluations == [80]  # Telemetry only; no command applied to the evaluator.
