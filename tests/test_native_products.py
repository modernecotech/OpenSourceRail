"""Named Cargo product/cache integrity; fake compiler, no native evaluation."""
from pathlib import Path
from types import SimpleNamespace
import json

import pytest

from engineering.station_pair import native_products as products,native_bridge
from engineering.station_rail.common import digest,encoded


def environment(tmp_path,monkeypatch,mode='normal'):
    root=tmp_path/'source';n=root/native_bridge.NATIVE
    (n/'src').mkdir(parents=True);(n/'tests').mkdir()
    (n/'Cargo.toml').write_text('synthetic package definition')
    (n/'Cargo.lock').write_text('synthetic locked dependencies')
    (n/'src/lib.rs').write_text('synthetic source, never compiled')
    state=tmp_path/'state';calls=[]
    monkeypatch.setattr(products.subprocess,'check_output',lambda *a,**k:'synthetic fixed version\n')
    def compile(command,*,cwd,env,stdout,stderr,timeout):
        calls.append(command)
        target=Path(env['CARGO_TARGET_DIR']);product=command[command.index('--bin')+1]
        f=target/'release'/product;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(('compiled '+product).encode())
        def artifact(path,kind=('bin',),test=False):
            return dict(reason='compiler-artifact',manifest_path=str(n/'Cargo.toml'),
                target=dict(name=product,kind=list(kind),src_path=str(n/products.PRODUCTS[product])),
                profile=dict(test=test),executable=str(path))
        # A prefix or target name alone is insufficient: a lib-test artifact is
        # intentionally present alongside the only selected production binary.
        rows=[artifact(target/'release/deps/ambiguous-prefix',kind=('lib',),test=True),artifact(f)]
        if mode=='ambiguous':rows.append(artifact(f))
        if mode=='escape':rows[1]=artifact(root/'Cargo.lock')
        if mode=='wrong-source':rows[1]['target']['src_path']=str(n/'src/other.rs')
        if mode=='drift':(n/'src/lib.rs').write_text('changed during compiler invocation')
        stdout.write(b''.join(encoded(row) for row in rows));stderr.write(b'synthetic compiler diagnostics\n')
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(products.subprocess,'run',compile)
    return root,state,calls


def test_journey_receipt_cannot_authenticate_stale_adjacent_fleet(tmp_path,monkeypatch):
    root,state,calls=environment(tmp_path,monkeypatch)
    old=state/'native-target/release';old.mkdir(parents=True)
    (old/'osr-journey').write_bytes(b'old trusted journey')
    (old/'osr-station-fleet').write_bytes(b'stale neighbouring fleet')
    (state/'native-build.json').write_bytes(encoded(dict(source_sha256=native_bridge.sources(root),
        tools=dict(cargo='synthetic fixed version',rustc='synthetic fixed version'),binary_sha256=digest(old/'osr-journey'))))
    binary,r=products.build(state,'osr-station-fleet',root)
    assert binary.read_bytes()==b'compiled osr-station-fleet'
    assert r['product']=='osr-station-fleet' and r['cargo_artifact']['profile']['test'] is False
    assert len(calls)==1 and calls[0][calls[0].index('--bin')+1]=='osr-station-fleet'
    assert (old/'osr-station-fleet').read_bytes()==b'stale neighbouring fleet'
    alias=json.loads((state/'native-build.json').read_bytes())
    assert alias['receipt_id']==r['receipt_id'] and alias['binary_sha256']==digest(binary)


def test_sealed_cache_survives_mutable_compiler_product_change(tmp_path,monkeypatch):
    root,state,calls=environment(tmp_path,monkeypatch)
    binary,r=products.build(state,'osr-station-cycle',root)
    (state/'native-product-target/release/osr-station-cycle').write_bytes(b'unreceipted mutable output')
    again,same=products.build(state,'osr-station-cycle',root)
    assert again==binary and same==r and len(calls)==1
    assert binary.read_bytes()==b'compiled osr-station-cycle'


@pytest.mark.parametrize('name',['osr-station-fleet','cargo.stderr.log'])
def test_altered_sealed_product_or_build_log_refuses_without_overwrite(tmp_path,monkeypatch,name):
    root,state,calls=environment(tmp_path,monkeypatch)
    binary,r=products.build(state,'osr-station-fleet',root)
    f=binary.parent/name;f.write_bytes(b'changed sealed artifact')
    with pytest.raises(ValueError,match='cache changed'):
        products.build(state,'osr-station-fleet',root)
    assert len(calls)==1 and f.read_bytes()==b'changed sealed artifact'


def test_changed_source_has_new_product_and_preserves_prior_packet(tmp_path,monkeypatch):
    root,state,calls=environment(tmp_path,monkeypatch)
    binary,old=products.build(state,'osr-station-fleet',root)
    old_receipt=(binary.parent/'receipt.json').read_bytes()
    (root/native_bridge.NATIVE/'src/lib.rs').write_text('revised source')
    other,new=products.build(state,'osr-station-fleet',root)
    assert other!=binary and len(calls)==2 and new['receipt_id']!=old['receipt_id']
    assert (binary.parent/'receipt.json').read_bytes()==old_receipt


@pytest.mark.parametrize('mode,error',[('ambiguous','One exact'),('wrong-source','One exact'),
    ('escape','escaped build target'),('drift','source/artifact changed')])
def test_unproven_product_is_never_published(tmp_path,monkeypatch,mode,error):
    root,state,calls=environment(tmp_path,monkeypatch,mode)
    with pytest.raises(ValueError,match=error):products.build(state,'osr-station-fleet',root)
    assert len(calls)==1 and not (state/'native-build.json').exists()
    assert not list((state/'native-products').glob('*/receipt.json'))
    assert list((state/'native-products').glob('*/execution.json'))


def test_arbitrary_product_cannot_create_a_path(tmp_path,monkeypatch):
    root,state,calls=environment(tmp_path,monkeypatch)
    with pytest.raises(ValueError,match='Known native CLI'):
        products.build(state,'../../payload',root)
    assert not state.exists() and not calls


def test_cycle_wrapper_receipt_names_actual_cycle_not_neighbouring_journey(tmp_path,monkeypatch):
    from engineering.station_cycle import native_bridge as cycle
    root,state,calls=environment(tmp_path,monkeypatch)
    binary,r=cycle.build(state,root)
    assert r['product']=='osr-station-cycle'
    assert r['protocol']=='osr-station-cycle-request/1'
    assert r['binary_sha256']==digest(binary) and 'journey_binary_sha256' not in r
    assert len(calls)==1 and '--bin' in calls[0]
    assert json.loads((state/'cycle-build.json').read_bytes())==r
