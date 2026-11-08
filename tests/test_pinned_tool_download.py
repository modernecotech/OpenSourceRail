"""Small transport fixtures only; these bytes are not native engineering evidence."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

SOURCE=Path(__file__).resolve().parents[1]/'tools/automation/download-pinned-tool.py'
spec=importlib.util.spec_from_file_location('pinned_tools',SOURCE)
tools=importlib.util.module_from_spec(spec);spec.loader.exec_module(tools)


@pytest.fixture
def fixture_pin(monkeypatch):
    raw=b'official fixture archive\n'
    pin=dict(version='fixture',repository='owner/repo',tag='vfixture',asset='fixture.tar.gz',asset_id=123,
             bytes=len(raw),sha256=sha256(raw).hexdigest())
    monkeypatch.setitem(tools.PINS,'fixture',pin)
    monkeypatch.setattr(tools.shutil,'disk_usage',lambda _:SimpleNamespace(free=100*1024**3))
    return raw,pin


def runner_for(responses,calls):
    def run(command,**kwargs):
        calls.append(command)
        response=responses[len(calls)-1]
        target=Path(command[command.index('--output')+1])
        if isinstance(response,BaseException): raise response
        code,raw=response
        if raw is not None:target.write_bytes(raw)
        kwargs['stderr'].write(b'fixture response\n')
        return SimpleNamespace(returncode=code)
    return run


def test_api_fallback_retains_failed_attempt_and_publishes_only_verified_bytes(tmp_path,fixture_pin):
    raw,pin=fixture_pin;calls=[];out=tmp_path/'archive'
    receipt=tools.download('fixture',out,runner=runner_for([(22,None),(0,raw)],calls),sleep=lambda _:None)
    assert out.read_bytes()==raw and len(calls)==2
    assert calls[0][-1]=='https://api.github.com/repos/owner/repo/releases/assets/123'
    assert calls[1][-1]=='https://github.com/owner/repo/releases/download/vfixture/fixture.tar.gz'
    assert receipt['attempts'][0]['returncode']==22 and receipt['attempts'][1]['sha256']==pin['sha256']
    assert receipt['credentials_sent'] is False
    assert calls[0][:2]==['curl','--disable']
    assert (tmp_path/'archive.attempts/attempt-01.stderr.log').read_bytes()==b'fixture response\n'
    assert json.loads((tmp_path/'archive.download.json').read_text())==receipt
    assert '--location' in calls[0] and calls[0][calls[0].index('--max-time')+1]=='180'
    assert calls[0][calls[0].index('--proto-redir')+1]=='=https'
    assert not any('Authorization' in x or 'location-trusted' in x for x in calls[0])


@pytest.mark.parametrize('bad',[b'bad',b'official fixture archive!'])
def test_mismatched_archive_is_retained_and_never_falls_back_to_hide_corruption(tmp_path,fixture_pin,bad):
    calls=[];out=tmp_path/'archive'
    with pytest.raises(ValueError,match='size/SHA256'):
        tools.download('fixture',out,runner=runner_for([(0,bad)],calls),sleep=lambda _:None)
    assert not out.exists() and len(calls)==1
    assert (tmp_path/'archive.attempts/attempt-01.part').read_bytes()==bad


def test_three_network_failures_exhaust_bound_without_output(tmp_path,fixture_pin):
    calls=[];out=tmp_path/'archive'
    with pytest.raises(RuntimeError,match='three bounded attempts'):
        tools.download('fixture',out,runner=runner_for([(22,None)]*3,calls),sleep=lambda _:None)
    assert len(calls)==3 and not out.exists()
    assert len(list((tmp_path/'archive.attempts').glob('attempt-*.json')))==3


def test_partial_byte_budget_prevents_an_unbounded_retry(tmp_path,fixture_pin):
    raw,_=fixture_pin;calls=[];out=tmp_path/'archive'
    with pytest.raises(RuntimeError,match='byte budget'):
        tools.download('fixture',out,runner=runner_for([(22,raw),(22,raw)],calls),sleep=lambda _:None)
    assert len(calls)==2 and not out.exists()


def test_valid_cache_is_rechecked_and_bad_cache_is_not_replaced(tmp_path,fixture_pin):
    raw,_=fixture_pin;out=tmp_path/'archive';out.write_bytes(raw)
    def no_request(*a,**kw):raise AssertionError('cache must not download')
    assert tools.download('fixture',out,runner=no_request)['cached']
    out.write_bytes(b'bad cache')
    with pytest.raises(ValueError,match='cached tool bytes differ'):tools.download('fixture',out,runner=no_request)
    assert out.read_bytes()==b'bad cache'


def test_fresh_attempts_and_ordinary_paths_required(tmp_path,fixture_pin):
    target=tmp_path/'target';target.mkdir();(tmp_path/'link').symlink_to(target,target_is_directory=True)
    with pytest.raises(ValueError,match='symlinks'):tools.download('fixture',tmp_path/'link/archive')
    (tmp_path/'archive.attempts').mkdir()
    with pytest.raises(FileExistsError):tools.download('fixture',tmp_path/'archive')


def test_disk_reserve_is_checked_before_network(tmp_path,fixture_pin,monkeypatch):
    monkeypatch.setattr(tools.shutil,'disk_usage',lambda _:SimpleNamespace(free=0))
    calls=[]
    with pytest.raises(RuntimeError,match='disk reserve'):
        tools.download('fixture',tmp_path/'archive',runner=runner_for([],calls))
    assert not calls


def test_supervisor_timeout_remains_a_failed_attempt(tmp_path,fixture_pin):
    raw,_=fixture_pin;calls=[];out=tmp_path/'archive'
    receipt=tools.download('fixture',out,runner=runner_for([subprocess.TimeoutExpired('curl',185),(0,raw)],calls),sleep=lambda _:None)
    assert receipt['attempts'][0]['returncode'] is None
    assert receipt['attempts'][0]['failure']=='supervisor-timeout'


def test_current_freecad_and_kani_release_pins_stay_exact():
    old=SOURCE.with_name('install-historical-freecad.py')
    s=importlib.util.spec_from_file_location('freecad_install',old);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    assert tools.PINS['freecad']['version']==m.VERSION
    assert tools.PINS['freecad']['sha256']==m.SHA256
    assert tools.PINS['freecad']['asset']==m.ASSET
    assert tools.PINS['kani']['version']=='0.67.0'
    assert tools.PINS['kani']['sha256']=='3b5f7afd3b51603ee720db7bc1bc4fe46b5a4f5d36daad9939c4b4c658b51ac0'
