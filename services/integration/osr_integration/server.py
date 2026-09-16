"""Authenticated local integration API and private FUXA read-only adapter."""
import hmac
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, urlopen

from .store import Store


def request_json(url, data=None, headers=None, method=None):
    req = Request(url, data=json.dumps(data).encode() if data is not None else None,
                  headers={'Content-Type': 'application/json', **(headers or {})}, method=method)
    with urlopen(req, timeout=15) as response:
        raw = response.read()
        return json.loads(raw) if raw else {}


def deliver(store, config, now=None):
    """One durable outbox batch. Remote transaction idempotency covers lost replies."""
    now = time.time() if now is None else now
    with store.connect() as db:
        rows = db.execute("SELECT o.* FROM outbox o WHERE o.state='pending' AND o.next_try<=? AND NOT EXISTS (SELECT 1 FROM outbox earlier WHERE earlier.incident=o.incident AND earlier.state='pending' AND earlier.rowid<o.rowid) ORDER BY o.rowid LIMIT 25", (now,)).fetchall()
    for row in rows:
        try:
            result = request_json(config['url'] + '/api/method/osr_erpnext.integration.condition_event',
                {'event': json.loads(row['body'])}, {'Authorization': 'token ' + config['key'] + ':' + config['secret']})['message']
            with store.connect() as db:
                db.execute("UPDATE outbox SET state='delivered',response=?,error=NULL WHERE id=?", (json.dumps(result), row['id']))
                db.execute('UPDATE alarms SET case_id=?,erp_status=? WHERE incident=?', (result['issue'], result['status'], row['incident']))
        except (HTTPError, URLError, OSError, ValueError, KeyError):
            # Never persist credentials, response bodies or authentication traces.
            with store.connect() as db:
                db.execute('UPDATE outbox SET attempts=attempts+1,next_try=?,error=? WHERE id=?', (now + min(300, 2 ** min(row['attempts'] + 1, 8)), 'ERP delivery unavailable; retry scheduled', row['id']))


def reconcile(store, config):
    with store.connect() as db:
        rows = db.execute('SELECT DISTINCT case_id FROM alarms WHERE case_id IS NOT NULL').fetchall()
    for row in rows:
        from urllib.parse import urlencode
        try:
            result = request_json(config['url'] + '/api/method/osr_erpnext.integration.case_status?' + urlencode({'issue': row['case_id']}), headers={'Authorization': 'token ' + config['key'] + ':' + config['secret']})['message']
            with store.connect() as db:
                db.execute('UPDATE alarms SET erp_status=? WHERE case_id=?', (result['status'], row['case_id']))
        except (HTTPError, URLError, OSError, ValueError, KeyError):
            continue


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send(self, status, body):
        raw = json.dumps(body, allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers(); self.wfile.write(raw)

    def principal(self):
        token = self.headers.get('Authorization', '').removeprefix('Bearer ')
        for entry in self.server.config['principals']:
            if hmac.compare_digest(token, entry['token']):
                return entry
        raise PermissionError('Authentication required')

    def authorize(self, principal, data, roles=None):
        if roles and principal['role'] not in roles:
            raise PermissionError('Role does not permit this operation')
        for field, allowed in [('city', principal['cities']), ('environment', principal['environments'])]:
            if data.get(field) not in allowed:
                raise PermissionError('City/environment outside authenticated scope')

    def do_GET(self):
        try:
            parsed = urlsplit(self.path)
            query = {k: v[0] for k, v in parse_qs(parsed.query).items()}
            if parsed.path == '/health':
                return self.send(200, {'status': 'ok', 'schema': 'osr-integration/1'})
            p = self.principal()
            if parsed.path == '/controller/commands':
                if p['role'] != 'controller':
                    raise PermissionError('Controller required')
                return self.send(200, self.server.store.controller_commands(p['subject']))
            self.authorize(p, query)
            if parsed.path == '/snapshot':
                return self.send(200, self.server.store.snapshot(query['city'], query['environment']))
            if parsed.path == '/history':
                scope = self.server.store.scope(query['city'], query['environment'], query['asset_id'])
                with self.server.store.connect() as db:
                    self.server.store.asset(db, scope)
                    rows = db.execute('SELECT source_time,received,value,quality,unit FROM readings WHERE scope=? AND measurement=? ORDER BY id DESC LIMIT 1000', (scope, query['measurement'])).fetchall()
                return self.send(200, [dict(r) for r in rows])
            if parsed.path == '/affected':
                rows = self.server.store.affected(query.get('serial'), query.get('batch'))
                return self.send(200, [r for r in rows if r['scope'].startswith(query['city'] + '|' + query['environment'] + '|')])
            self.send(404, {'error': 'Unknown endpoint'})
        except PermissionError as exc:
            self.send(403, {'error': str(exc)})
        except (ValueError, KeyError) as exc:
            self.send(400, {'error': str(exc)})

    def do_POST(self):
        try:
            p = self.principal()
            size = int(self.headers.get('Content-Length', 0))
            if not 0 < size <= 4_000_000:
                raise ValueError('Request size outside limit')
            data = json.loads(self.rfile.read(size))
            path = urlsplit(self.path).path
            store = self.server.store
            if path == '/packages/preview':
                self.authorize(p, data['package'])
                result = store.package_review(data['package'])
            elif path == '/packages':
                self.authorize(p, data['package'], ['engineer'])
                result = store.apply(data['package'], p['subject'], data.get('expected'), data.get('review_sha256'))
            elif path == '/telemetry':
                self.authorize(p, data, ['controller'])
                result = store.ingest(data, p['subject'])
            elif path == '/commands':
                self.authorize(p, data)
                result = store.command(data, p['subject'], p['role'] == 'operator')
            elif path == '/controller/result':
                if p['role'] != 'controller':
                    raise PermissionError('Controller required')
                result = store.controller_result(data['request_id'], p['subject'], data['state'], data.get('result', ''))
            elif path == '/evidence':
                self.authorize(p, data)
                result = store.evidence(data, p['subject'], p['role'])
            elif path == '/alarms/acknowledge':
                self.authorize(p, data, ['operator', 'maintainer'])
                result = store.acknowledge(data['city'], data['environment'], data['asset_id'], data['rule'],
                                           data['occurrence'], p['subject'])
            else:
                return self.send(404, {'error': 'Unknown endpoint'})
            self.send(200, result)
        except PermissionError as exc:
            self.send(403, {'error': str(exc)})
        except (ValueError, KeyError, TypeError) as exc:
            self.send(400, {'error': str(exc)})


class FuxaReadHandler(Handler):
    """Unpublished container-network port: only filtered tag reads, no mutation."""
    def do_GET(self):
        parts = urlsplit(self.path).path.strip('/').split('/')
        if len(parts) != 4 or parts[0] != 'tags':
            return self.send(404, {})
        _, city, environment, asset = parts
        try:
            a = next(a for a in self.server.store.snapshot(city, environment)['assets']
                     if a['asset_id'] == asset and a['configuration_status'] == 'active')
            tags = []
            for name, r in a['readings'].items():
                for suffix, value, dtype in [('', r['value'] if r['quality'] == 'valid' else 'unavailable', 'Double'),
                        ('_quality', r['quality'], 'String'), ('_timestamp', __import__('datetime').datetime.fromtimestamp(r['source_time'], __import__('datetime').timezone.utc).isoformat() if r['source_time'] else 'not received', 'String')]:
                    tags.append({'id': a['fuxa_device_id'] + '__' + name + suffix, 'value': value, 'type': dtype})
            for rule in a['alarms']:
                tags.append({'id': a['fuxa_device_id'] + '__alarm_' + rule['rule'], 'value': rule['active'], 'type': 'Bool'})
            return self.send(200, tags)
        except (ValueError, StopIteration):
            return self.send(404, {})

    def do_POST(self):
        self.send(405, {'error': 'Read only'})


def main():
    config = json.loads(Path(os.environ.get('OSR_INTEGRATION_CONFIG', '/run/secrets/integration.json')).read_text())
    store = Store(os.environ.get('OSR_INTEGRATION_DB', '/data/integration.sqlite'))
    public = ThreadingHTTPServer(('0.0.0.0', 8092), Handler)
    private = ThreadingHTTPServer(('0.0.0.0', 8093), FuxaReadHandler)
    for server in (public, private):
        server.store, server.config = store, config
    threading.Thread(target=private.serve_forever, daemon=True).start()
    def worker():
        tick = 0
        while True:
            try:
                if config.get('erp'):
                    deliver(store, config['erp'])
                    if tick % 6 == 0:
                        reconcile(store, config['erp'])
                if tick % 60 == 0:
                    store.prune()
            except Exception as exc:
                print('Integration worker failure:', type(exc).__name__, flush=True)
            tick += 1
            time.sleep(5)
    threading.Thread(target=worker, daemon=True).start()
    public.serve_forever()


if __name__ == '__main__':
    main()
