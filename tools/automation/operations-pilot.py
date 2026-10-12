#!/usr/bin/env python3
"""Reproduce the six-item management pilot or run its isolated browser workspace."""
import argparse
import importlib.util
import hashlib
import json
import secrets
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'services/integration'))
from osr_integration.config import digest
from osr_integration.store import Store
from osr_integration.server import GatewayHTTPServer, Handler
from osr_integration.operations.planning import plan
from osr_integration.operations.store import OperationsStore
from osr_integration.operations.exchange import gtfs_realtime, gtfs_schedule, operational_export, passenger_updates


def inputs():
    fixture = ROOT / 'engineering/operations/fixtures'
    return json.loads((fixture / 'pilot.json').read_text()), json.loads((fixture / 'disruptions.json').read_text())


def run(out):
    out.mkdir(parents=True, exist_ok=True)
    package, disruptions = inputs()
    normal = plan(package); recovery = plan(package, disruptions)
    if len(recovery['services']) != 3 or recovery['roster']['uncovered'] or recovery['search_exhausted']:
        raise ValueError('Combined recovery pilot failed')
    for name, result in [('normal', normal), ('recovery', recovery)]:
        (out / (name + '.json')).write_text(json.dumps(result, indent=2) + '\n')
    (out / 'operations.json').write_text(json.dumps(operational_export(package, recovery), indent=2) + '\n')
    (out / 'gtfs.zip').write_bytes(gtfs_schedule(package))
    (out / 'trip-updates.pb').write_bytes(gtfs_realtime(passenger_updates(package, recovery, 1791777600)))
    print(json.dumps(dict(normal_services=len(normal['services']), recovery_services=len(recovery['services']),
        absent_worker_replaced=all(row['worker_id']!='W1' for row in recovery['roster']['assignments']),
        backup_charger_used=any(row.get('charger_id')=='CH-B2' for row in recovery['fleet_diagram']), search_exhausted=recovery['search_exhausted'],
        output=str(out), movement_authority=False)))


def review(check=False):
    package, disruptions = inputs(); normal = plan(package); recovery = plan(package, disruptions)
    flags = dict(all_services_retained=len(recovery['services']) == 3,
        failed_train_not_assigned=all(r['train_id'] != 'T2' for r in recovery['services']),
        absent_worker_not_assigned=all(r['worker_id'] != 'W1' for r in recovery['roster']['assignments']),
        backup_charger_used=any(r.get('charger_id') == 'CH-B2' for r in recovery['fleet_diagram']),
        failed_charger_not_used=all(r.get('charger_id') != 'CH-B1' for r in recovery['fleet_diagram']),
        alternative_physical_path_used=recovery['services'][0]['path_id'] == 'ACB',
        fixed_inspection_retained=any(r['kind'] == 'inspection' for r in recovery['fleet_diagram']),
        all_staff_duties_covered=not recovery['roster']['uncovered'], search_completed=not recovery['search_exhausted'])
    sources = list((ROOT / 'services/integration/osr_integration/operations').glob('*.py'))
    sources += [ROOT / relative for relative in [
        'services/integration/osr_integration/server.py', 'tools/automation/operations-pilot.py',
        'tools/automation/workbench-server.py', 'tools/automation/tests/test_operations_management.py',
        'tools/automation/tests/test_field_operations_native.py',
        'deployment/erpnext/apps/osr_erpnext/osr_erpnext/field_contract.py',
        'deployment/erpnext/apps/osr_erpnext/osr_erpnext/field_operations.py',
        'deployment/workbench/tests/verify-operations.mjs', 'engineering/operations/fixtures/pilot.json',
        'engineering/operations/fixtures/disruptions.json', 'docs/operating/operations/app.js',
        'docs/operating/operations/sw.js', 'docs/operating/operations/index.html']]
    result = dict(schema='osr-operations-pilot-review/1', source_sha256s={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(sources)},
        scope='synthetic management planning; not native ERP delivery, measured prediction or railway acceptance',
        checks=flags, passed=all(flags.values()), normal_plan_sha256=normal['sha256'], recovery_plan_sha256=recovery['sha256'],
        normal_services=len(normal['services']), recovery_services=len(recovery['services']),
        movement_authority=False, native_erp_delivery_exercised=False)
    target = ROOT / 'engineering/operations/pilot-review.json'; text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if check:
        if not target.exists() or target.read_text()!=text: raise ValueError('Operations pilot review is stale')
    else: target.write_text(text)
    if not result['passed']: raise ValueError('Operations pilot review failed')
    print('Operations pilot source-bound recovery review: passed')


def serve(out, port, gateway_port):
    """Dedicated test DB/config/ports; never reconfigure an installed city stack."""
    out.mkdir(parents=True, exist_ok=True)
    package, _ = inputs(); store = Store(out / 'gateway.sqlite'); ops = OperationsStore(store)
    try: baseline = ops.baseline('samawah', 'simulation')
    except ValueError: baseline = ops.register(package, 'pilot-engineer', None)
    if not ops.packs('samawah', 'simulation', 'tech'):
        asset = dict(asset_id='A:charger', city='samawah', environment='simulation', engineering_revision=package['revision'],
                     erp_asset_id='PILOT-ASSET', erp_project='PILOT-PROJECT', company_id='PILOT-COMPANY')
        with store.connect() as db:
            db.execute('INSERT OR IGNORE INTO assets(scope,city,environment,asset_id,package,body) VALUES(?,?,?,?,?,?)',
                       ('samawah|simulation|A:charger','samawah','simulation','A:charger',baseline['sha256'],json.dumps(asset)))
        ops.issue_work(dict(id='PILOT-WORK',city='samawah',environment='simulation',asset_id='A:charger',assigned_to='tech',
            method_revision='PILOT-METHOD',erp_task='PILOT-TASK',erp_asset='PILOT-ASSET',native_modified='2026-10-12 06:00:00',
            expires_at='2099-01-01T00:00:00Z',requires_photo=True,readings=[dict(id='voltage',kind='number',unit='V',min=0,max=1000,required=True),dict(id='isolated',kind='boolean',required=True)]),
            'pilot-engineer',baseline['sha256'])
    tokens = {role: secrets.token_urlsafe(32) for role in ('engineer', 'operator', 'maintainer', 'viewer')}
    credentials = out / 'credentials.json'; credentials.write_text(json.dumps(tokens)); credentials.chmod(0o600)
    principals = [dict(token=token, role=role, subject='tech' if role=='maintainer' else role,
                       cities=['samawah'], environments=['simulation']) for role, token in tokens.items()]
    gateway = GatewayHTTPServer(('127.0.0.1', gateway_port), Handler); gateway.store = store; gateway.config = dict(principals=principals)
    module_spec = importlib.util.spec_from_file_location('operations_workbench', ROOT / 'tools/automation/workbench-server.py')
    module = importlib.util.module_from_spec(module_spec); module_spec.loader.exec_module(module)
    module.INTEGRATION_URL = f'http://127.0.0.1:{gateway_port}'
    class Workspace(module.WorkbenchHandler):
        def log_message(self, *args): pass
    web = module.OPS.ThreadingHTTPServer(('127.0.0.1', port), Workspace)
    worker = threading.Thread(target=gateway.serve_forever, daemon=True); worker.start()
    print(f'Isolated workspace: http://127.0.0.1:{port}/docs/operating/operations/; scoped credentials: {credentials}', flush=True)
    try: web.serve_forever()
    finally:
        gateway.shutdown(); gateway.server_close(); web.server_close(); worker.join()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / 'build/operations-pilot')
    parser.add_argument('--review', action='store_true'); parser.add_argument('--check', action='store_true')
    parser.add_argument('--serve', action='store_true'); parser.add_argument('--port', type=int, default=8197)
    parser.add_argument('--gateway-port', type=int, default=8198)
    args=parser.parse_args()
    if args.review or args.check: review(args.check)
    elif args.serve: serve(args.out,args.port,args.gateway_port)
    else: run(args.out)


if __name__=='__main__': main()
