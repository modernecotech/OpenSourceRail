"""Spawned city jobs preserve deterministic packets and fail-closed indexing."""
from concurrent.futures import Future
import json
from pathlib import Path

import pytest
from engineering.ferrite_maglev import cities


def designs():
    root=cities.ROOT/'cities/catalogue'
    return [root/'west-africa/Cameroon/Edea/city.json',root/'east-africa/Mozambique/Quelimane/city.json']


def bytes_under(folder):
    return {p.relative_to(folder).as_posix():p.read_bytes() for p in folder.rglob('*') if p.is_file()}


def old_index(folder):
    folder.mkdir();(folder/'city-index.json').write_bytes(b'previous JSON receipt\n')
    (folder/'city-index.md').write_bytes(b'previous Markdown index\n')
    return {name:(folder/name).read_bytes() for name in ('city-index.json','city-index.md')}


def unchanged(folder,before):
    assert {name:(folder/name).read_bytes() for name in before}==before
    assert not list(folder.glob('.*.tmp'))


def fake_pool(monkeypatch,*,fail_on=None,tamper=None):
    instances=[]
    class Pool:
        def __init__(self,**kwargs):
            self.calls=0;self.shutdown_calls=[];self.maximum=kwargs['max_workers'];instances.append(self)
            assert kwargs['mp_context'].get_start_method()=='spawn'
            kwargs['initializer'](*kwargs['initargs'])
        def submit(self,fn,job):
            index=self.calls;self.calls+=1;future=Future()
            try:
                if index==fail_on:raise ValueError('synthetic worker failure')
                value=fn(job)
                if tamper is not None:tamper(value,job)
                future.set_result(value)
            except Exception as exc:future.set_exception(exc)
            return future
        def shutdown(self,**kwargs):self.shutdown_calls.append(kwargs)
    monkeypatch.setattr(cities,'ProcessPoolExecutor',Pool)
    return instances


def test_spawned_workers_reproduce_serial_packet_and_index_bytes(monkeypatch,tmp_path):
    monkeypatch.setattr(cities,'_catalogue_designs',designs)
    output=tmp_path/'packets';serial=cities.generate_all(output,workers=1);before=bytes_under(output)
    original=cities.ProcessPoolExecutor;constructed=[]
    def executor(**kwargs):
        constructed.append((kwargs['max_workers'],kwargs['mp_context'].get_start_method()))
        return original(**kwargs)
    monkeypatch.setattr(cities,'ProcessPoolExecutor',executor)
    parallel=cities.generate_all(output,workers=2)
    assert constructed==[(2,'spawn')]
    assert parallel==serial
    assert bytes_under(output)==before
    assert [row['city'] for row in parallel['cities']]==['edea','quelimane']
    assert all(not any(key.startswith('_') for key in row) for row in parallel['cities'])


def test_failed_worker_does_not_schedule_rest_or_advance_old_index(monkeypatch,tmp_path):
    third=cities.ROOT/'cities/catalogue/east-africa/Uganda/Soroti/city.json'
    monkeypatch.setattr(cities,'_catalogue_designs',lambda:[*designs(),third])
    output=tmp_path/'failed';before=old_index(output)
    pools=fake_pool(monkeypatch,fail_on=1)
    with pytest.raises(ValueError,match='synthetic worker failure'):cities.generate_all(output,workers=2)
    assert pools[0].calls==2
    assert pools[0].shutdown_calls==[dict(wait=True,cancel_futures=True)]
    unchanged(output,before)


def test_completed_packet_tamper_holds_batch_before_index_publication(monkeypatch,tmp_path):
    monkeypatch.setattr(cities,'_catalogue_designs',lambda:designs()[:1])
    output=tmp_path/'tampered';before=old_index(output)
    def tamper(row,job):
        path=Path(job[1])/'summary.json';path.write_bytes(path.read_bytes()+b'\n')
    fake_pool(monkeypatch,tamper=tamper)
    with pytest.raises(ValueError,match='packet changed'):cities.generate_all(output,workers=2)
    unchanged(output,before)


def test_changed_per_city_input_revision_holds_batch(monkeypatch,tmp_path):
    monkeypatch.setattr(cities,'_catalogue_designs',lambda:designs()[:1])
    output=tmp_path/'input-change';before=old_index(output)
    def tamper(row,job):row['_source_sha256'][Path(job[0]).relative_to(cities.ROOT).as_posix()]='0'*64
    fake_pool(monkeypatch,tamper=tamper)
    with pytest.raises(ValueError,match='source changed'):cities.generate_all(output,workers=2)
    unchanged(output,before)


def test_changed_shared_calculation_inputs_hold_batch(monkeypatch,tmp_path):
    monkeypatch.setattr(cities,'_catalogue_designs',lambda:designs()[:1])
    output=tmp_path/'shared-change';before=old_index(output)
    original=cities._city_calculation_snapshot;calls=[]
    def snapshot():
        result=original();calls.append(1)
        if len(calls)>1:result[next(iter(result))]='0'*64
        return result
    monkeypatch.setattr(cities,'_city_calculation_snapshot',snapshot)
    fake_pool(monkeypatch)
    with pytest.raises(ValueError,match='calculation inputs changed'):cities.generate_all(output,workers=2)
    unchanged(output,before)


def test_alternate_output_defaults_serial_and_json_is_last_receipt(monkeypatch,tmp_path):
    monkeypatch.setattr(cities,'_catalogue_designs',lambda:designs()[:1])
    def no_pool(**kwargs):raise AssertionError('alternate output must default serial')
    monkeypatch.setattr(cities,'ProcessPoolExecutor',no_pool)
    original=cities.os.replace;replaced=[]
    def replace(source,target):
        assert Path(source).is_file()
        replaced.append(Path(target).name);return original(source,target)
    monkeypatch.setattr(cities.os,'replace',replace)
    output=tmp_path/'serial';result=cities.generate_all(output)
    assert result['city_count']==1
    assert replaced[-2:]==['city-index.md','city-index.json']
    assert json.loads((output/'city-index.json').read_text())==result
    assert not list(output.glob('.*.tmp'))


@pytest.mark.parametrize('workers',[0,5,True,1.5])
def test_worker_count_is_bounded_without_touching_outputs(tmp_path,workers):
    with pytest.raises(ValueError,match='workers'):cities.generate_all(tmp_path/'untouched',workers=workers)
    assert not (tmp_path/'untouched').exists()
