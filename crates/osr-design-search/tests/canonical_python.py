"""Explicit optional-extension parity/failure smoke; no automatic backend adoption.

Run with this Python interpreter's extension:
  python canonical_python.py --extension /absolute/libosr_design_search.so
An optional --payload JSON file adds an indicative encoder-only benchmark.
"""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import random
import statistics
import struct
import time


def reference(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)+"\n").encode()


def rejected(call, exception):
    try:
        call()
    except exception:
        return
    raise AssertionError("Expected bounded canonical input rejection")


def sealed_smoke(native):
    shared=[None,False,-0.0,2**2000,{"nested":[1,2.5]}]
    records=[{}, {"a":shared,"z":shared}, {"\ud800":1,"\ue000":2,"\U00010000":3},
        {"quote\"\\\n":shared,"evaluation_id-nested":{"evaluation_id":None}}]
    keys=["0","evaluation_id","m","zz","\udfff","\U00010001","\"\\\n"]
    count=0
    for value in records:
        original=reference(value)
        expected_seal=hashlib.sha256(original).hexdigest()
        for key in keys:
            expected=reference(dict(value,**{key:expected_seal}))
            assert native.sealed_record(value,key)==(expected,expected_seal)
            assert native.sealed_record(value,key,max_bytes=len(expected))==(expected,expected_seal)
            rejected(lambda:native.sealed_record(value,key,max_bytes=len(expected)-1),ValueError)
            assert reference(value)==original
            count+=1
    value={"nested":[[0]]}
    seal=hashlib.sha256(reference(value)).hexdigest()
    assert native.sealed_record(value)==(reference(dict(value,evaluation_id=seal)),seal)
    rejected(lambda:native.sealed_record(value,max_depth=2),RecursionError)
    rejected(lambda:native.sealed_record({},max_depth=0),RecursionError)
    for key in (None,0,True,b"key"):
        rejected(lambda:native.sealed_record({},key),TypeError)
    rejected(lambda:native.sealed_record({},""),ValueError)
    rejected(lambda:native.sealed_record({"evaluation_id":"old"}),ValueError)
    rejected(lambda:native.sealed_record({"\ud800":1},"\ud800"),ValueError)
    for value in (None,[],(),1):
        rejected(lambda:native.sealed_record(value),TypeError)
    for value in ({"x":float("inf")},{"x":float("nan")}):
        rejected(lambda:native.sealed_record(value),ValueError)
    class Key(str):
        pass
    class Record(dict):
        pass
    rejected(lambda:native.sealed_record({},Key("key")),TypeError)
    rejected(lambda:native.sealed_record(Record()),TypeError)
    rejected(lambda:native.sealed_record({Key("key"):0}),TypeError)
    loop={}
    loop["loop"]=loop
    rejected(lambda:native.sealed_record(loop),ValueError)
    return count


def smoke(native):
    shared=[None,True,False,-0.0,2**2000]
    cases=[None,True,False,0,1,-1,-0.0,1e-5,1e-4,1e15,1e16,2**2000,
        "".join(map(chr,range(256))),"\ud800Ω\udfff🛤",
        {"\U00010000":0,"\ue000":1,"\ud800":2,"\udfff":3},(1,2,None),[shared,shared]]
    randomizer=random.Random(734)
    for _ in range(50_000):
        value=struct.unpack(">d",randomizer.getrandbits(64).to_bytes(8,"big"))[0]
        if math.isfinite(value):
            cases.append(value)
    for value in cases:
        expected=reference(value)
        identity=hashlib.sha256(expected).hexdigest()
        assert native.encoded(value)==expected
        assert native.identity(value)==identity
        assert native.encoded_with_identity(value)==(expected,identity)
    for value in (float("nan"),float("inf"),-float("inf")):
        rejected(lambda:native.encoded(value),ValueError)
    callbacks=[]
    class Unsupported:
        def __repr__(self):
            callbacks.append("repr")
            raise AssertionError("User callback must not run")
    for base in (int,float,str,list,tuple,dict):
        subclass=type("UnsupportedSubclass",(base,),{})
        value=subclass()
        rejected(lambda:native.encoded(value),TypeError)
    rejected(lambda:native.encoded(Unsupported()),TypeError)
    rejected(lambda:native.encoded({Unsupported():0}),TypeError)
    assert callbacks==[]
    rejected(lambda:native.encoded({1:"numeric-key"}),TypeError)
    loop=[]
    loop.append(loop)
    rejected(lambda:native.encoded(loop),ValueError)
    immutable=[1,{},shared]
    before=reference(immutable)
    assert native.encoded(immutable)==before==reference(immutable)
    value={"s":"Ω🛤"}
    size=len(reference(value))
    assert native.encoded(value,max_bytes=size)==reference(value)
    rejected(lambda:native.encoded(value,max_bytes=size-1),ValueError)
    for limit in (0,64*1024**2+1):
        rejected(lambda:native.encoded(value,max_bytes=limit),ValueError)
    rejected(lambda:native.encoded(value,max_depth=257),ValueError)
    rejected(lambda:native.encoded([[[0]]],max_depth=2),RecursionError)
    assert native.encoded([[[0]]],max_depth=3)==b"[[[0]]]\n"
    assert native.encoded({},max_depth=0)==b"{}\n"
    return len(cases)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extension",type=Path,required=True)
    parser.add_argument("--payload",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    if args.output and args.output.exists():
        raise SystemExit("Refusing to replace a retained smoke report")
    spec=importlib.util.spec_from_file_location("osr_design_native",args.extension.resolve())
    native=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(native)
    report=dict(schema="osr-native-canonical-smoke/1",parity_cases=smoke(native),sealed_record_cases=sealed_smoke(native),backend=native.backend_info(),
        extension_sha256=hashlib.sha256(args.extension.read_bytes()).hexdigest(),
        scope="Canonical encoder method control only; no engineering or native-physics evidence")
    if args.payload:
        value=json.loads(args.payload.read_bytes())
        expected=reference(value)
        assert native.encoded_with_identity(value)==(expected,hashlib.sha256(expected).hexdigest())
        methods={"python_encoded":lambda:reference(value),"rust_encoded":lambda:native.encoded(value),
            "python_identity":lambda:hashlib.sha256(reference(value)).hexdigest(),"rust_identity":lambda:native.identity(value)}
        timings={}
        for name,call in methods.items():
            call()
            samples=[]
            for _ in range(3):
                start=time.perf_counter();call();samples.append(time.perf_counter()-start)
            timings[name]=dict(median_seconds=statistics.median(samples),samples=samples)
        report.update(payload_sha256=hashlib.sha256(args.payload.read_bytes()).hexdigest(),canonical_bytes=len(expected),timings=timings,
            benchmark_caveat="One warm and three measured calls; encoder-only smoke, no full-campaign speed claim")
    raw=reference(report)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open("xb") as handle:
            handle.write(raw)
    print(json.dumps(report))


if __name__=="__main__":
    main()
