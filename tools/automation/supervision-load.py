#!/usr/bin/env python3
"""Repeatable isolated full-city HTTP load rehearsal using production gateway handlers.

Exercises the FUXA polling API, telemetry writes and concurrent operator reads.
It does not start FUXA/ERP browsers or certify production throughput.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import ExitStack
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'services/integration'))
from osr_integration.store import Store
from osr_integration.server import Handler, FuxaReadHandler, GatewayHTTPServer


def request(base, path, data=None, token=None):
    headers = {'Content-Type':'application/json'}
    if token: headers['Authorization'] = 'Bearer ' + token
    req = Request(base + path, data=json.dumps(data).encode() if data else None, headers=headers)
    with urlopen(req, timeout=60) as response:
        return json.load(response)


def run(city, rounds, workers, operators, output, batch_size=128):
    output.mkdir(parents=True, exist_ok=False)
    spec = importlib.util.spec_from_file_location('load_supervision', ROOT / 'tools/automation/supervision.py')
    supervisor = importlib.util.module_from_spec(spec); spec.loader.exec_module(supervisor)
    package = supervisor.city_package(city)
    (output / 'package.json').write_text(json.dumps(package, indent=2) + '\n')
    samples = [(asset, name, measurement) for asset in package['equipment'] for name, measurement in asset['measurements'].items()]
    measurements = len(samples)
    # Fixture values exercise persistence, freshness and alarm processing; they are not physical telemetry.
    with tempfile.TemporaryDirectory(prefix='osr-supervision-load-') as directory, ExitStack() as cleanup:
        store = Store(Path(directory) / 'gateway.sqlite'); store.apply(package, 'load-engineer')
        config = {'principals': [dict(token='operator',role='viewer',subject='load-viewer',cities=[city],environments=['simulation'])]}
        sources = sorted({a['source_id'] for a in package['equipment']})
        config['principals'] += [dict(token='controller-'+source,role='controller',subject=source,cities=[city],environments=['simulation']) for source in sources]
        servers=[]
        for handler in (Handler, FuxaReadHandler):
            server=GatewayHTTPServer(('127.0.0.1',0),handler);server.store=store;server.config=config
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            cleanup.callback(thread.join);cleanup.callback(server.server_close);cleanup.callback(server.shutdown)
            servers.append('http://127.0.0.1:'+str(server.server_port))
        public,private=servers
        results=[]; errors=[]; cycles=[]
        def measured(kind, operation):
            start=time.monotonic()
            value=operation()
            return dict(kind=kind,seconds=time.monotonic()-start),value
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for cycle in range(rounds):
                start=time.monotonic(); futures=[]; pending={}
                def submit_batch(source):
                    readings=pending.pop(source)
                    def publish():
                        stamp=datetime.now(timezone.utc).isoformat()
                        messages=[{**data,'source_timestamp':stamp} for data in readings]
                        if batch_size==1:
                            return request(public,'/telemetry',messages[0],'controller-'+source)
                        return request(public,'/telemetry/batch',{'readings':messages},'controller-'+source)
                    futures.append(executor.submit(measured,'telemetry',publish))
                # Interleave device polls, measurement writes and operator reads in the same pool.
                for index,asset in enumerate(package['equipment']):
                    path='/tags/'+city+'/simulation/'+quote(asset['asset_id'],safe=':')
                    futures.append(executor.submit(measured,'fuxa-poll',lambda path=path:request(private,path)))
                    for name,m in asset['measurements'].items():
                        value=m['min']+(m['max']-m['min'])*(0.25 if cycle%2==0 else 0.75)
                        data=dict(city=city,environment='simulation',asset_id=asset['asset_id'],measurement=name,
                            source_id=asset['source_id'],sequence=cycle+1,value=value,quality='valid',unit=m['unit'])
                        pending.setdefault(asset['source_id'],[]).append(data)
                        if len(pending[asset['source_id']])==batch_size:
                            submit_batch(asset['source_id'])
                    if index<operators:
                        path='/snapshot?'+urlencode(dict(city=city,environment='simulation'))
                        futures.append(executor.submit(measured,'operator-snapshot',lambda path=path:request(public,path,token='operator')))
                        path='/outbox?'+urlencode(dict(city=city,environment='simulation',state='pending',limit=20))
                        futures.append(executor.submit(measured,'operator-queue',lambda path=path:request(public,path,token='operator')))
                for source in list(pending): submit_batch(source)
                for future in as_completed(futures):
                    try:
                        metric,_=future.result();results.append(metric)
                    except Exception as exc:
                        errors.append(type(exc).__name__+': '+str(exc))
                cycles.append(time.monotonic()-start)
        with store.connect() as db:
            actual=db.execute('SELECT count(*) FROM readings').fetchone()[0]
            integrity=db.execute('PRAGMA integrity_check').fetchone()[0]
            last={ (r['scope'],r['measurement']):dict(r) for r in db.execute('SELECT * FROM readings WHERE sequence=?',(rounds,)) }
        expected_values=True
        for asset,name,m in samples:
            row=last.get((store.scope(city,'simulation',asset['asset_id']),name))
            raw=m['min']+(m['max']-m['min'])*(0.25 if (rounds-1)%2==0 else 0.75)
            expected=raw*m.get('scale',1)+m.get('offset',0)
            expected_values &= row is not None and row['value']==expected
        timings={}
        for kind in sorted({r['kind'] for r in results}):
            values=sorted(r['seconds'] for r in results if r['kind']==kind)
            timings[kind]=dict(requests=len(values),p50_seconds=values[len(values)//2],
                p95_seconds=values[min(len(values)-1,int(len(values)*.95))],max_seconds=max(values))
        source_paths=['services/integration/osr_integration/'+name+'.py' for name in ('store','server','config')]+['tools/automation/supervision-load.py']
        report=dict(schema='osr-supervision-load/1',city=city,
            working_tree_dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),
            checkout_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in source_paths},
            package_sha256=package['sha256'],equipment=len(package['equipment']),measurements=measurements,
            rounds=rounds,workers=workers,operators=operators,telemetry_batch_size=batch_size,cycle_seconds=cycles,request_timings=timings,
            readings_expected=measurements*rounds,readings_actual=actual,latest_values_match=bool(expected_values),
            errors=errors,sqlite_integrity=integrity,functional_passed=not errors and actual==measurements*rounds and expected_values and integrity=='ok',
            polling_target_seconds=2,polling_target_met=all(seconds<=2 for seconds in cycles),
            scope='Isolated HTTP gateway: synthetic telemetry, FUXA adapter polls and operator API reads; no FUXA browser/ERP transaction/physical controller load.',
            production_capacity_accepted=False)
        (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report,indent=2))
        return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--city',default='samawah');parser.add_argument('--rounds',type=int,default=3)
    parser.add_argument('--workers',type=int,default=16);parser.add_argument('--operators',type=int,default=4)
    parser.add_argument('--batch-size',type=int,default=128,help='1 uses the original single-reading endpoint; 2..128 uses atomic batches')
    parser.add_argument('--require-polling-target',action='store_true',help='Also fail when any complete city cycle exceeds two seconds')
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if not 1<=args.rounds<=100 or not 1<=args.workers<=64 or not 1<=args.operators<=32 or not 1<=args.batch_size<=128:
        parser.error('rounds 1..100, workers 1..64, operators 1..32, batch-size 1..128')
    result=run(args.city,args.rounds,args.workers,args.operators,args.output,args.batch_size)
    if not result['functional_passed']:raise SystemExit(1)
    if args.require_polling_target and not result['polling_target_met']:raise SystemExit(2)


if __name__=='__main__':main()
