"""Actual local Rust decisions consumed/replayed with synthetic plant poses."""
from copy import deepcopy
import gzip
import json
import pytest
from engineering.ferrite_maglev import candidate_authority as a

READY=dict(receiver_ready=True,resistor_ready=True,reserve_ready=True,doors_closed=True,train_healthy=True)

def test_real_protocol_gates_then_retains_occupied_final_arrival(tmp_path):
    with a.AuthorityClient('a'*64,[0.,2013.,4027.,6042.],tmp_path/'run') as client:
        no=client.step(0,0,-104.5,0);assert not no['protected'] and not no['committed']
        yes=client.prepare(0,0,READY);assert yes['protected'] and yes['committed']
        sample=client.step(.01,100,-4.5,12);assert sample['protected']
        failed=client.step(20,1000,895.5,20,receiver_failed=True)
        assert failed['protected'] and failed['committed'] and not failed['receiver_ready']
        assert not client.step(21,1019.5,915.,19)['receiver_ready']
    receipt=a.verify_receipt(client.directory,configuration_sha256='a'*64,replay=True)
    assert receipt['verified'] and receipt['replayed'] and not receipt['physical_release']

def test_receiver_or_reserve_refusal_never_invents_a_commit(tmp_path):
    for key in ('receiver_ready','reserve_ready','doors_closed'):
        with a.AuthorityClient('b'*64,[0.,2000.],tmp_path/key) as c:
            e=c.prepare(0,0,dict(READY,**{key:False}));assert not e['protected'] and not e['committed']
        assert a.verify_receipt(c.directory,replay=True)['verified']

def test_live_tail_only_releases_after_departing_previous_station(tmp_path):
    with a.AuthorityClient('c'*64,[0.,2000.,4000.],tmp_path/'run') as c:
        assert c.prepare(0,0,READY)['committed']
        e=c.step(140,2000,1895.5,0);assert e['protected']
        assert c.prepare(1,200,READY)['committed']
        c.step(210,2200,2095.5,10)
        c.step(220,2400,2295.5,10)
    raw=[json.loads(line) for line in gzip.decompress((c.directory/'decisions.jsonl.gz').read_bytes()).splitlines()]
    assert not raw[-2]['response']['cleared_previous_legs']
    assert raw[-1]['response']['cleared_previous_legs']==[0]
    assert a.verify_receipt(c.directory,replay=True)['verified']

def test_wrong_pose_stale_time_and_coherently_rehashed_event_are_held(tmp_path):
    with a.AuthorityClient('d'*64,[0.,2000.],tmp_path/'run') as c:
        c.prepare(0,0,READY);bad=c.step(1,100,0,10);assert not bad['protected']
        with pytest.raises(ValueError,match='nonmonotone'):c.step(.5,100,-4.5,10)
    p=c.directory/'decisions.jsonl.gz';records=[json.loads(line) for line in gzip.decompress(p.read_bytes()).splitlines()]
    records[-1]['event']['protected']=True;p.write_bytes(gzip.compress(b'\n'.join(json.dumps(r).encode() for r in records)+b'\n',mtime=0))
    receipt=json.loads((c.directory/'receipt.json').read_bytes());receipt['files_sha256'][p.name]=a.sha256(p.read_bytes()).hexdigest();(c.directory/'receipt.json').write_bytes(a.platform.encoded(receipt))
    with pytest.raises(ValueError,match='does not match'):a.verify_receipt(c.directory)

def test_bad_route_and_first_leg_order_are_refused(tmp_path):
    with pytest.raises(ValueError):a.deployment('z'*64,[0.,2000.])
    with pytest.raises(ValueError):a.deployment('a'*64,[0.,100.])
    with a.AuthorityClient('a'*64,[0.,2000.,4000.],tmp_path/'run') as c:
        e=c.prepare(1,0,READY);assert not e['committed']
