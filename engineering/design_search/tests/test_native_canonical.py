"""Canonical bytes remain exactly CPython JSON, inside an explicit native domain."""
from copy import deepcopy
from hashlib import sha256
import importlib.util
from itertools import islice
import json
import math
import os
from pathlib import Path
import random
import shutil
import struct
import sysconfig

import numpy as np
import pytest

from engineering.station_rail import ROOT,common


@pytest.fixture(scope='module')
def native():
    target=ROOT/'build/rust-canonical-target/python'/sysconfig.get_config_var('SOABI')/'current.json'
    if not target.is_file():
        if os.environ.get('OSR_TEST_NATIVE_CANONICAL')=='1':
            pytest.fail('OSR_TEST_NATIVE_CANONICAL=1 requires an explicitly built current-ABI native canonical receipt')
        pytest.skip('Explicit current-ABI native canonical build is unavailable; run native_canonical build before the parity suite')
    from engineering.design_search.native_canonical import NativeCanonical
    engine=NativeCanonical(root=ROOT)
    with engine.session() as backend:yield backend


def parity(native,value):
    expected=common.encoded(value);expected_id=sha256(expected).hexdigest()
    assert native.encoded(value)==expected
    assert native.identity(value)==expected_id
    assert native.encoded_with_identity(value)==(expected,expected_id)


@pytest.mark.parametrize('value',[None,True,False,0,1,-1,2**4096,-2**4096,0.0,-0.0,
    5e-324,-5e-324,float.fromhex('0x1.fffffffffffffp+1023'),1e-7,1e-6,1e-5,1e-4,1e15,1e16,1e17,
    1.0000000000000002,9.999999999999999e-5,[],{},[{},[],[1]],(1,2,{'a':(False,None)})])
def test_exact_builtin_scalar_and_nested_parity(native,value):
    parity(native,value)


def test_unicode_escapes_sorting_surrogates_and_non_bmp_match_ascii_json(native):
    values=['\x00\b\f\n\r\t\\\"/\u2028\u2029\U0001f680\ud800\udfff',
        {'\ud800':1,'\udfff':2,'\U0001f600':3,'\ufffd':4,'a':5},
        {'\U00010000':'\ud800\udc00','\ue000':'\udfff','\u0000':'control'}]
    for value in values:parity(native,value)


def test_every_byte_range_codepoint_including_del_is_escaped_like_python(native):
    parity(native,''.join(chr(i) for i in range(256)))
    parity(native,{chr(i):i for i in range(256)})


def test_legacy_surrogate_pair_keys_and_unicode_normalisation_are_not_reinterpreted(native):
    # Compatibility follows Python's codepoint ordering and escaping, including
    # distinct keys that happen to share an escaped spelling. No NFC or JSON
    # round-trip is substituted for the original in-memory object.
    parity(native,{'\ud800\udc00':'pair','\U00010000':'scalar','é':1,'e\u0301':2,'العراق':3})


def test_fifty_thousand_deterministic_finite_float64_bit_patterns(native):
    rng=random.Random(20261104);values=[]
    while len(values)<50_000:
        value=struct.unpack('>d',rng.getrandbits(64).to_bytes(8,'big'))[0]
        if math.isfinite(value):values.append(value)
    # Batch plus individual samples catch the representation and scalar paths.
    parity(native,values)
    for value in values[::127]:parity(native,value)


def test_shared_acyclic_aliases_are_not_treated_as_cycles(native):
    shared={'x':[1.,-0.0,'\ud800']}
    value={'a':[shared,shared],'b':(shared,)}
    before=common.encoded(value);parity(native,value)
    assert common.encoded(value)==before


@pytest.mark.parametrize('value',[float('nan'),float('inf'),-float('inf'),{'a':float('nan')},
    {1:'numeric key'},{False:'boolean key'},{None:'null key'},{'a':1,2:3},b'bytes',{1,2},object()])
def test_unknown_or_outside_strict_domain_is_explicitly_rejected(native,value):
    for function in (native.encoded,native.identity,native.encoded_with_identity):
        with pytest.raises((TypeError,ValueError,RecursionError)):function(value)


def test_common_broader_nonstring_key_domain_is_preserved_without_native_id_substitution(native):
    for value in ({1:'int',2:'two'},{False:'bool'},{None:'null'}):
        assert isinstance(common.encoded(value),bytes)
        with pytest.raises((TypeError,ValueError)):native.encoded(value)


def test_numpy_and_builtin_subclasses_are_not_coerced_silently(native):
    class Float(float):pass
    class Integer(int):pass
    class String(str):pass
    class List(list):pass
    class Dict(dict):pass
    broader=(np.float64(1.25),Float(1.25),Integer(123),String('text'),List([1]),Dict(a=1))
    assert all(isinstance(common.encoded(value),bytes) for value in broader)
    for value in broader:
        with pytest.raises((TypeError,ValueError)):native.encoded(value)


def test_list_and_mapping_cycles_are_rejected(native):
    cyclic=[];cyclic.append(cyclic)
    mapping={};mapping['self']=mapping
    for value in (cyclic,mapping):
        for function in (native.encoded,native.identity,native.encoded_with_identity):
            with pytest.raises((TypeError,ValueError,RecursionError)):function(value)


def test_record_corpus_iterator_and_float_edges_are_deterministic():
    path=ROOT/'tools/automation/benchmark-native-canonical.py'
    spec=importlib.util.spec_from_file_location('benchmark_native_canonical_test',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    value={'z':[{'a':1}], 'a':{'x':[1,2]}}
    records=list(module.subrecords(value))
    assert [path for path,_ in records]==['','/a','/z','/a/x','/z/0']
    assert list(islice(module.float_values(5),21))==list(islice(module.float_values(5),21))
    for value in module.edge_values():assert isinstance(common.encoded(value),bytes)


def test_repository_json_examples_match(native):
    paths=[ROOT/'docs/design-engine/current/manifest.json',ROOT/'engineering/sourcing/data/iraq-domestic-2026-july.json']
    used=0
    for path in paths:
        if path.is_file():parity(native,json.loads(path.read_bytes()));used+=1
    assert used>=1


def test_byte_and_depth_limits_cover_trailing_newline_and_reject_bool_limits(native):
    value={'a':[1,2,'text']};size=len(common.encoded(value))
    assert native.encoded(value,max_bytes=size)==common.encoded(value)
    with pytest.raises((ValueError,RecursionError)):native.encoded(value,max_bytes=size-1)
    value=0
    for _ in range(12):value=[value]
    parity(native,value)
    with pytest.raises((ValueError,RecursionError)):native.encoded(value,max_depth=8)
    for limits in ({'max_bytes':True},{'max_bytes':0},{'max_bytes':64*1024**2+1},
                   {'max_depth':True},{'max_depth':0},{'max_depth':257}):
        with pytest.raises(ValueError):native.encoded(None,**limits)


def test_session_cannot_be_reused_after_guarded_context_exit(native):
    with native.engine.session() as backend:assert backend.encoded(1)==b'1\n'
    for function in (backend.encoded,backend.identity,backend.encoded_with_identity):
        with pytest.raises((ValueError,RuntimeError)):function(1)


@pytest.mark.parametrize('kind',['binary','source','ABI','build-command','receipt-seal'])
def test_current_source_abi_binary_and_receipt_tampering_is_rejected(native,tmp_path,kind):
    from engineering.design_search.native_canonical import NativeCanonical
    engine=native.engine;copy=tmp_path/engine.extension.name
    shutil.copyfile(engine.extension,copy)
    receipt=deepcopy(engine.provenance()['receipt'])
    if kind=='binary':
        with copy.open('r+b') as stream:
            stream.seek(-1,2);value=stream.read(1);stream.seek(-1,2);stream.write(bytes([value[0]^1]))
    elif kind=='source':receipt['sources'][next(iter(receipt['sources']))]='0'*64
    elif kind=='ABI':receipt['abi']['SOABI']='forged-ABI'
    elif kind=='build-command':receipt['build_command']=['cargo','build','--unlocked']
    if kind=='receipt-seal':receipt['receipt_id']='0'*64
    elif kind!='binary':receipt['receipt_id']=common.identity({k:v for k,v in receipt.items() if k!='receipt_id'})
    copy.with_name(copy.name+'.receipt.json').write_bytes(common.encoded(receipt))
    with pytest.raises(ValueError,match='differs|changed|rebuild'):NativeCanonical(root=ROOT,extension=copy)


def test_symlink_extension_and_loaded_producer_epoch_are_rejected(native,tmp_path,monkeypatch):
    from engineering.design_search import native_canonical as module
    link=tmp_path/native.engine.extension.name;link.symlink_to(native.engine.extension)
    shutil.copyfile(native.engine.receipt_path,link.with_name(link.name+'.receipt.json'))
    with pytest.raises(ValueError):module.NativeCanonical(root=ROOT,extension=link)
    monkeypatch.setitem(module.LOADED,module.PRODUCER,'0'*64)
    with pytest.raises(ValueError,match='source|changed'):module.NativeCanonical(root=ROOT,extension=native.engine.extension)


def test_cargo_tool_epoch_mismatch_is_rejected(native,monkeypatch):
    from engineering.design_search import native_canonical as module
    tools=module.native_search._tools()
    monkeypatch.setattr(module.native_search,'_tools',lambda:dict(tools,unexpected_tool_epoch='forged'))
    with pytest.raises(ValueError,match='tool|differs'):module.NativeCanonical(root=ROOT,extension=native.engine.extension)


def test_scoped_campaign_aliases_restore_on_error_and_other_thread_keeps_python(native):
    from concurrent.futures import ThreadPoolExecutor
    from engineering.design_search import native_canonical as module,native_campaign
    reference=common.encoded;identity_reference=common.identity;alias=native_campaign.encoded
    broader=np.float64(1.25);expected=reference(broader)
    with pytest.raises(RuntimeError,match='intentional test'):
        with module.campaign_backend('rust',root=ROOT):
            with pytest.raises(TypeError):common.encoded(broader)
            with ThreadPoolExecutor(max_workers=1) as pool:
                assert pool.submit(common.encoded,broader).result(timeout=5)==expected
            assert common.encoded({'a':-0.0})==reference({'a':-0.0})
            raise RuntimeError('intentional test')
    assert common.encoded is reference and common.identity is identity_reference
    assert native_campaign.encoded is alias
    assert common.encoded(broader)==expected
