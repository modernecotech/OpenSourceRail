#!/usr/bin/env python3
"""Bounded canonical-byte parity and sampled full-coordinator measurements.

Bulk corpus bytes live in a private output directory. common.encoded remains
the unchanged oracle. Phase times are inclusive, sampled and not additive.
"""
from __future__ import annotations

import argparse
from collections import deque
from functools import wraps
import gzip
from hashlib import sha256
import io
import json
import math
import os
from pathlib import Path
import random
import resource
import struct
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from engineering.station_rail import common

MAX_BYTES=256*1024**2
READ_RECORD_BYTES=1024**2


def _json(raw):
    def bad(value):raise ValueError("Nonfinite JSON input: "+value)
    return json.loads(raw,parse_constant=bad)


def source_files(root,exclude):
    """Prefer retained 2k-program outputs before broad current documentation."""
    seen=set()
    for directory in (root/"build/processor-profile-20261104/optimized-state/stock-cost",
                      root/"build/search-delivery-complete-reference-20261104",
                      root/"docs/design-engine",root/"build/processor-profile-20261104"):
        if not directory.is_dir():continue
        for path in sorted(directory.rglob("*")):
            if (path in seen or exclude==path or exclude in path.parents or path.is_symlink()
                    or not path.is_file() or not (path.name.endswith(".json") or path.name.endswith(".json.gz"))):continue
            seen.add(path);yield path


def subrecords(value,maximum=40):
    """Breadth-first, bounded container representatives; retain origin paths."""
    queue=deque([(value,"")]);count=0
    while queue and count<maximum:
        item,origin=queue.popleft()
        if type(item) not in (dict,list) or not item:continue
        yield origin,item;count+=1
        children=sorted(item.items()) if type(item) is dict else enumerate(item)
        for key,child in children:
            if type(child) in (dict,list) and child:
                queue.append((child,origin+"/"+str(key).replace("~","~0").replace("/","~1")))


def _small(value,maximum_nodes=512):
    """Reject giant parent containers cheaply before canonical re-encoding."""
    stack=[value];nodes=0;characters=0
    while stack:
        item=stack.pop();nodes+=1
        if nodes>maximum_nodes:return False
        if type(item) is dict:
            if len(item)>maximum_nodes:return False
            characters+=sum(len(key) for key in item);stack.extend(item.values())
        elif type(item) in (list,tuple):
            if len(item)>maximum_nodes:return False
            stack.extend(item)
        elif type(item) is str:characters+=len(item)
        if characters>8192:return False
    return True


def create_corpus(root,output,*,count=10_000,byte_budget=MAX_BYTES):
    root=Path(root).resolve();output=Path(output).absolute()
    if type(count) is not int or not 1<=count<=100_000:raise ValueError("Bounded positive record count required")
    if type(byte_budget) is not int or not 1024<=byte_budget<=MAX_BYTES:raise ValueError("At most256MiB corpus required")
    output.mkdir(parents=True,exist_ok=False)
    entries=[];sources={};seen=set();written=0;read_bytes=0;skipped=[];root_types={}
    with (output/"corpus.jsonl").open("xb") as stream:
        for path in source_files(root,output):
            if path.stat().st_size>READ_RECORD_BYTES:continue
            raw=path.read_bytes()
            try:
                if path.name.endswith(".gz"):
                    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as data:
                        decoded=data.read(READ_RECORD_BYTES+1)
                else:decoded=raw
                if len(decoded)>READ_RECORD_BYTES or read_bytes+len(decoded)>byte_budget:continue
                value=_json(decoded)
            except (OSError,ValueError,UnicodeError) as exc:
                skipped.append(dict(path=str(path.relative_to(root)),reason=type(exc).__name__));continue
            read_bytes+=len(decoded)
            relative=str(path.relative_to(root));source_sha=sha256(raw).hexdigest()
            for pointer,item in subrecords(value,maximum=160):
                if not _small(item):continue
                try:encoded=common.encoded(item)
                except (ValueError,TypeError,RecursionError):continue
                key=sha256(encoded).hexdigest()
                if key in seen or len(encoded)>16*1024 or written+len(encoded)>byte_budget:continue
                stream.write(encoded);seen.add(key);written+=len(encoded)
                kind=type(item).__name__;root_types[kind]=root_types.get(kind,0)+1
                entries.append(dict(path=relative,pointer=pointer,bytes=len(encoded),sha256=key))
                sources[relative]=source_sha
                if len(entries)==count:break
            if len(entries)==count:break
    if len(entries)!=count:raise ValueError(f"Corpus coverage {len(entries)} below requested {count}; partial bytes retained")
    if any(common.digest(root/path)!=sha for path,sha in sources.items()):raise ValueError("Corpus source changed during read")
    manifest=dict(schema="osr-native-canonical-corpus/1",records=len(entries),canonical_bytes=written,
        source_decoded_bytes_read=read_bytes,source_sha256=sources,entries=entries,skipped=skipped,
        corpus_sha256=common.digest(output/"corpus.jsonl"),oracle_sha256=common.digest(common.__file__),
        tool_sha256=common.digest(__file__),byte_budget=byte_budget,record_root_type_histogram=root_types,
        decoded_object_domain='JSON parser produces only exact builtins; NumPy/subclass objects cannot be represented by source JSON and require separate direct-object tests',
        scope="Saved JSON/gz container records and nested representatives; no qualification claims")
    manifest["corpus_id"]=common.identity(manifest)
    (output/"manifest.json").write_bytes(common.encoded(manifest))
    return manifest


def float_values(count=50_000,seed=20261104):
    """IEEE754 bit-pattern coverage, including subnormals and CPython cutovers."""
    yield from (5e-324,-5e-324,sys.float_info.max,-sys.float_info.max,-0.0,0.0,
                1e-7,1e-6,1e-5,1e-4,1e15,1e16,1e17,1.0000000000000002,
                9.999999999999999e-5,1.0000000000000001e18)
    rng=random.Random(seed);emitted=0
    while emitted<count:
        value=struct.unpack('>d',rng.getrandbits(64).to_bytes(8,'big'))[0]
        if math.isfinite(value):yield value;emitted+=1


def edge_values():
    shared={"a":[1,-0.0,"\ud800"]}
    return [None,True,False,0,1,-1,2**4096,-2**4096,
        "\x00\b\f\n\r\t\\\"\u2028\u2029\U0001f680\ud800\udfff",
        {"\ud800":1,"\udfff":2,"\U0001f600":3,"\ufffd":4,"a":5},
        (1,"tuple",{"nested":(2,3)}),[shared,shared],{"z":[{},[]],"a":None}]


def rejected_values():
    circular=[];circular.append(circular)
    cyclic={};cyclic['self']=cyclic
    return [("NaN",float('nan')),("positive-infinity",float('inf')),
            ("negative-infinity",-float('inf')),("cycle-list",circular),("cycle-dict",cyclic),
            ("mixed-string-int-keys",{"a":1,2:3}),("set",{1,2}),("bytes",b'bytes')]


def compare_corpus(corpus,backend,*,floats=50_000):
    corpus=Path(corpus);manifest=_json((corpus/"manifest.json").read_bytes())
    if (manifest['corpus_id']!=common.identity({k:v for k,v in manifest.items() if k!='corpus_id'})
            or common.digest(corpus/'corpus.jsonl')!=manifest['corpus_sha256']
            or common.digest(common.__file__)!=manifest['oracle_sha256']):raise ValueError("Corpus identity or oracle differs")
    counts=dict(records=0,random_and_edge_floats=0,edge_objects=0,rejected=0)
    timings=dict(python_encoded_s=0.,native_encoded_s=0.,native_identity_s=0.,native_fused_s=0.)
    def check(value):
        start=time.perf_counter();expected=common.encoded(value);timings['python_encoded_s']+=time.perf_counter()-start
        start=time.perf_counter();actual=backend.encoded(value);timings['native_encoded_s']+=time.perf_counter()-start
        if actual!=expected:raise AssertionError('Canonical byte mismatch: '+repr(value)[:300])
        expected_id=sha256(expected).hexdigest()
        start=time.perf_counter();actual_id=backend.identity(value);timings['native_identity_s']+=time.perf_counter()-start
        if actual_id!=expected_id:raise AssertionError('Canonical identity mismatch')
        start=time.perf_counter();fused=backend.encoded_with_identity(value);timings['native_fused_s']+=time.perf_counter()-start
        if fused!=(expected,expected_id):raise AssertionError('Fused canonical bytes/identity mismatch')
    with (corpus/'corpus.jsonl').open('rb') as stream:
        for number,line in enumerate(stream):
            entry=manifest['entries'][number]
            if len(line)!=entry['bytes'] or sha256(line).hexdigest()!=entry['sha256']:raise ValueError('Corpus line changed')
            check(_json(line));counts['records']+=1
    if counts['records']!=manifest['records']:raise ValueError('Corpus record coverage differs')
    for value in float_values(floats):check(value);counts['random_and_edge_floats']+=1
    for value in edge_values():check(value);counts['edge_objects']+=1
    for name,value in rejected_values():
        try:common.encoded(value)
        except (TypeError,ValueError,RecursionError):pass
        else:raise AssertionError('Invalid test input is accepted by the Python oracle: '+name)
        for function in (backend.encoded,backend.identity,backend.encoded_with_identity):
            try:function(value)
            except (TypeError,ValueError,RecursionError):pass
            else:raise AssertionError('Native encoder accepted rejected input: '+name)
        counts['rejected']+=1
    # CPython allows some homogeneous nonstring keys. Native mode must declare
    # them unsupported, rather than silently producing another candidate ID.
    broader=[{1:'integer-key',2:'two'},{False:'boolean-key'},{None:'null-key'}]
    for value in broader:
        common.encoded(value)
        try:backend.encoded(value)
        except (TypeError,ValueError):pass
        else:raise AssertionError('Strict native domain silently broadened to nonstring keys')
    return dict(schema='osr-native-canonical-parity/1',all_parity=True,corpus_id=manifest['corpus_id'],counts=counts,
        timings=timings,broader_python_key_cases_explicitly_rejected=len(broader),
        method='One call per method/object, full Python object crossing included; no statistical timing confidence',
        physical_accepted=False,engineering_accepted=False)


def compare_large_records(backend):
    """Full crossing/timing for retained big records, in addition to small cases."""
    base=ROOT/'build/processor-profile-20261104/optimized-state'
    paths=[]
    for folder,pattern in ((base/'geometry','*.json.gz'),(base/'runs','*.json')):
        if folder.is_dir():paths.extend(sorted(folder.glob(pattern))[:1])
    rows=[]
    for path in paths:
        source=path.read_bytes()
        if path.name.endswith('.gz'):
            with gzip.GzipFile(fileobj=io.BytesIO(source)) as stream:source=stream.read(16*1024**2+1)
        if len(source)>16*1024**2:raise ValueError('Large control exceeds16MiB input budget')
        value=_json(source);start=time.perf_counter();expected=common.encoded(value);python_s=time.perf_counter()-start
        start=time.perf_counter();actual=backend.encoded(value);native_s=time.perf_counter()-start
        if actual!=expected:raise AssertionError('Large retained record bytes differ')
        start=time.perf_counter();fused=backend.encoded_with_identity(value);fused_s=time.perf_counter()-start
        if fused!=(expected,sha256(expected).hexdigest()):raise AssertionError('Large retained record identity differs')
        rows.append(dict(path=str(path.relative_to(ROOT)),source_sha256=common.digest(path),canonical_bytes=len(expected),
            python_encoded_s=python_s,native_encoded_s=native_s,native_fused_s=fused_s,all_parity=True))
    return rows


def profile_campaign(output,*,sample_stride=64,instrumented=True,canonical_backend='python'):
    """One fresh default campaign, resource-bounded and with native jobs zero."""
    if type(instrumented) is not bool or type(sample_stride) is not int or sample_stride<1:raise ValueError('Explicit profile policy required')
    if canonical_backend not in ('python','rust'):raise ValueError('Explicit canonical backend required')
    for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
        if os.environ.get(name)!='1':raise ValueError(name+'=1 required before imports')
    resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3));resource.setrlimit(resource.RLIMIT_CPU,(85,85))
    from engineering.design_search import native_campaign as c,frame_analysis,grammar_structure,native_search
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    sources=c._sources(ROOT);measurements={};originals=[]
    snapshot=output/'producer-before';snapshot.mkdir()
    (snapshot/'native_campaign.py').write_bytes(Path(c.__file__).read_bytes())
    def instrument(owner,name,label,stride=1):
        original=getattr(owner,name);row=measurements.setdefault(label,dict(calls=0,sampled_calls=0,failed=0,sampled_inclusive_wall_s=0.,sample_stride=stride))
        @wraps(original)
        def timed(*args,**kwargs):
            row['calls']+=1
            sampled=row['calls']<=8 or row['calls']%stride==0
            if not sampled:return original(*args,**kwargs)
            row['sampled_calls']+=1;start=time.perf_counter()
            try:return original(*args,**kwargs)
            except BaseException:row['failed']+=1;raise
            finally:row['sampled_inclusive_wall_s']+=time.perf_counter()-start
        setattr(owner,name,timed);originals.append((owner,name,original));return timed
    if instrumented:
        for owner,name,label in ((c,'_materialise','geometry_materialisation'),(c,'_evaluate','nominal_stock_cost'),
            (c,'_check_epoch','campaign_source_checks'),(c,'_runtime','runtime_identity_checks'),
            (c,'_verify_frontier','frontier_reconstruction'),(c,'_read_cache','record_readback'),
            (c,'_checkpoint','checkpoint_write'),(c,'_sealed_record','record_sealing'),
            (grammar_structure,'_system','axial_matrix_assembly'),(frame_analysis,'_assemble','frame_matrix_assembly'),
            (native_search,'_run','rust_process_tool_communication'),(c.np.linalg,'svd','compiled_svd'),
            (c.np.linalg,'solve','compiled_linear_solve'),(c.np.linalg,'eigvalsh','compiled_frame_eigenvalues')):
            instrument(owner,name,label)
        for helper,label in (('identity','canonical_identity'),('encoded','canonical_encoding')):
            original=getattr(common,helper)
            aliases=[module for name,module in list(sys.modules.items()) if name.startswith('engineering.') and getattr(module,helper,None) is original]
            wrapped=instrument(common,helper,label,sample_stride)
            for module in aliases:
                if module is common:continue
                originals.append((module,helper,getattr(module,helper)));setattr(module,helper,wrapped)
        if canonical_backend=='rust':
            for name in ('encoded','identity','encoded_with_identity'):
                instrument(c.native_canonical._Session,name,'rust_session_'+name,sample_stride)
    started=time.perf_counter()
    try:summary=c.run(state=output/'state',native_jobs=0,frame_native_jobs=0,section_torsion_jobs=0,canonical_backend=canonical_backend)
    finally:
        for owner,name,original in reversed(originals):setattr(owner,name,original)
    elapsed=time.perf_counter()-started
    if summary['numerical_solver_dispatch_count'] or summary['section_jobs_new']:raise AssertionError('Profile dispatched a prohibited numerical job')
    if c._sources(ROOT)!=sources:raise ValueError('Campaign sources changed during profiling')
    for row in measurements.values():
        row['estimated_inclusive_wall_s']=row['sampled_inclusive_wall_s']*row['calls']/max(1,row['sampled_calls'])
    report=dict(schema='osr-sampled-coordinator-profile/1',source_sha256=sources,runtime=c._runtime(),
        instrumented=instrumented,canonical_backend=canonical_backend,full_call_wall_s=elapsed,measurements=measurements,summary=summary,
        maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,tool_sha256=common.digest(__file__),
        limitations=['Inclusive nested phases are not additive','Systematic samples estimate canonical helper times, not a statistical confidence interval',
            'One fresh run per invocation; actual coordinator, object conversion and file IO included','No CCX, CAD or section worker jobs',
            'RLIMIT_AS1GiB/CPU85s; caller must enforce90s wall; no OS sandbox'],
        physical_accepted=False,engineering_accepted=False)
    report['profile_id']=common.identity(report);(output/'report.json').write_bytes(common.encoded(report));return report


def main():
    parser=argparse.ArgumentParser(description=__doc__);commands=parser.add_subparsers(dest='command',required=True)
    corpus=commands.add_parser('corpus');corpus.add_argument('--output',type=Path,required=True);corpus.add_argument('--records',type=int,default=10_000)
    profile=commands.add_parser('profile');profile.add_argument('--output',type=Path,required=True);profile.add_argument('--uninstrumented',action='store_true')
    profile.add_argument('--backend',choices=('python','rust'),default='python')
    parity=commands.add_parser('parity');parity.add_argument('--corpus',type=Path,required=True);parity.add_argument('--output',type=Path,required=True);parity.add_argument('--floats',type=int,default=50_000)
    args=parser.parse_args()
    if args.command=='corpus':result=create_corpus(ROOT,args.output,count=args.records);print(json.dumps({k:result[k] for k in ('corpus_id','records','canonical_bytes','source_decoded_bytes_read')}))
    elif args.command=='profile':
        result=profile_campaign(args.output,instrumented=not args.uninstrumented,canonical_backend=args.backend)
        print(json.dumps({k:result[k] for k in ('profile_id','full_call_wall_s','maxrss_kib','measurements')}))
    else:
        resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3));resource.setrlimit(resource.RLIMIT_CPU,(85,85))
        from engineering.design_search.native_canonical import NativeCanonical
        engine=NativeCanonical(root=ROOT);provenance=engine.provenance();started=time.perf_counter()
        with engine.session() as backend:
            result=compare_corpus(args.corpus,backend,floats=args.floats)
            result['large_records']=compare_large_records(backend)
        result.update(wall_s=time.perf_counter()-started,maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            backend_provenance=provenance,tool_sha256=common.digest(__file__),runtime=dict(python=sys.version,executable=sys.executable))
        result['report_id']=common.identity(result)
        with args.output.open('xb') as stream:stream.write(common.encoded(result))
        print(json.dumps(dict(report_id=result['report_id'],counts=result['counts'],timings=result['timings'],wall_s=result['wall_s'])))


if __name__=='__main__':main()
