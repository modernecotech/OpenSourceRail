"""Transactional identities, telemetry, alarm outbox and command/evidence audit."""
import json
import sqlite3
import time
import uuid
from contextlib import contextmanager, closing
from datetime import datetime

from .config import digest, finite, identifier, validate_package


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError('Timestamp must be ISO 8601 with timezone')
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('Timestamp timezone required')
    return dt.timestamp()


class Store:
    def __init__(self, path):
        self.path = str(path)
        with self.connect() as db:
            db.executescript('''
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS packages (hash TEXT PRIMARY KEY, city TEXT, environment TEXT, body TEXT, actor TEXT, created REAL);
            CREATE TABLE IF NOT EXISTS assets (scope TEXT PRIMARY KEY, city TEXT, environment TEXT, asset_id TEXT, package TEXT, body TEXT, state TEXT DEFAULT 'as-designed');
            CREATE TABLE IF NOT EXISTS readings (id INTEGER PRIMARY KEY, scope TEXT, measurement TEXT, source TEXT, sequence INTEGER, source_time REAL, received REAL, value REAL, quality TEXT, unit TEXT, fingerprint TEXT, UNIQUE(scope,measurement,source,sequence));
            CREATE INDEX IF NOT EXISTS readings_latest ON readings(scope,measurement,id DESC);
            CREATE TABLE IF NOT EXISTS alarms (key TEXT PRIMARY KEY, scope TEXT, rule TEXT, pending REAL, active INTEGER DEFAULT 0, incident TEXT, last_event REAL DEFAULT 0, occurrences INTEGER DEFAULT 0, case_id TEXT, erp_status TEXT, acknowledged_by TEXT);
            CREATE TABLE IF NOT EXISTS outbox (id TEXT PRIMARY KEY, incident TEXT, body TEXT, state TEXT DEFAULT 'pending', attempts INTEGER DEFAULT 0, next_try REAL DEFAULT 0, error TEXT, response TEXT);
            CREATE TABLE IF NOT EXISTS commands (id TEXT PRIMARY KEY, scope TEXT, body TEXT, fingerprint TEXT, actor TEXT, state TEXT, expires REAL, result TEXT);
            CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, at REAL, actor TEXT, action TEXT, scope TEXT, body TEXT);
            CREATE TABLE IF NOT EXISTS evidence (id TEXT PRIMARY KEY, scope TEXT, kind TEXT, actor TEXT, body TEXT, created REAL);
            CREATE TABLE IF NOT EXISTS installations (id TEXT PRIMARY KEY, scope TEXT, serial TEXT, batch TEXT, revision TEXT, evidence TEXT, installed REAL, removed REAL);
            CREATE UNIQUE INDEX IF NOT EXISTS installed_position ON installations(scope) WHERE removed IS NULL;
            CREATE TABLE IF NOT EXISTS deliveries (id TEXT PRIMARY KEY, scope TEXT, body TEXT, actor TEXT, created REAL);
            ''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=30)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def scope(city, environment, asset):
        return '|'.join([identifier(city), identifier(environment), identifier(asset)])

    @staticmethod
    def audit(db, actor, action, scope, body):
        db.execute('INSERT INTO audit(at,actor,action,scope,body) VALUES(?,?,?,?,?)', (time.time(), actor, action, scope, json.dumps(body, allow_nan=False)))

    def apply(self, package, actor, expected=None):
        validate_package(package)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            existing = db.execute('SELECT hash FROM packages WHERE city=? AND environment=? ORDER BY created DESC LIMIT 1', (package['city'], package['environment'])).fetchone()
            if existing and existing['hash'] == package['sha256']:
                return {'created': False, 'sha256': package['sha256']}
            if existing and expected != existing['hash']:
                raise ValueError('Configuration changed: review diff and provide expected previous hash')
            if existing and package['environment'] == 'physical':
                raise ValueError('Physical mapping changes require a separate commissioned migration; no automatic overwrite')
            # Identity rows survive package revisions. Removed positions stay as history.
            for asset in package['equipment']:
                scope = self.scope(asset['city'], asset['environment'], asset['asset_id'])
                old = db.execute('SELECT body FROM assets WHERE scope=?', (scope,)).fetchone()
                if old and json.loads(old['body'])['component_type_id'] != asset['component_type_id']:
                    raise ValueError('Component type substitution requires explicit replacement')
                db.execute('INSERT INTO assets(scope,city,environment,asset_id,package,body) VALUES(?,?,?,?,?,?) ON CONFLICT(scope) DO UPDATE SET package=excluded.package,body=excluded.body', (scope, asset['city'], asset['environment'], asset['asset_id'], package['sha256'], json.dumps(asset)))
            db.execute('INSERT INTO packages VALUES(?,?,?,?,?,?)', (package['sha256'], package['city'], package['environment'], json.dumps(package), actor, time.time()))
            self.audit(db, actor, 'package-applied', package['city'], {'sha256': package['sha256'], 'previous': expected})
            return {'created': True, 'sha256': package['sha256'], 'equipment': len(package['equipment'])}

    def asset(self, db, scope):
        row = db.execute('SELECT body,state FROM assets WHERE scope=?', (scope,)).fetchone()
        if not row:
            raise ValueError('Unknown asset in this city/environment')
        return dict(json.loads(row['body']), lifecycle_state=row['state'])

    def ingest(self, message, principal, now=None):
        now = time.time() if now is None else now
        scope = self.scope(message['city'], message['environment'], message['asset_id'])
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            a = self.asset(db, scope)
            if principal != a['source_id'] or message['source_id'] != principal:
                raise PermissionError('Telemetry source is not bound to asset')
            if a['environment'] == 'physical' and a['binding_status'] != 'commissioned':
                raise ValueError('Physical telemetry requires a commissioned source binding')
            m = a['measurements'].get(message['measurement'])
            if not m or message['unit'] != m['unit']:
                raise ValueError('Unknown measurement or wrong unit')
            seq = message['sequence']
            if type(seq) is not int or seq < 0 or seq > 2**63 - 1:
                raise ValueError('Sequence must be a nonnegative 64-bit integer')
            quality = message['quality']
            if quality not in ('valid', 'stale', 'invalid', 'disconnected'):
                raise ValueError('Invalid quality')
            source_time = timestamp(message['source_timestamp'])
            if source_time > now + 5:
                raise ValueError('Future timestamp')
            value = message.get('value')
            if value is not None:
                finite(value, -1e12, 1e12)
                value = value * m.get('scale', 1) + m.get('offset', 0)
                if not m['min'] <= value <= m['max']:
                    quality = 'invalid'
            elif quality == 'valid':
                raise ValueError('Valid measurements require a value')
            if quality == 'valid' and now - source_time > m['stale_seconds']:
                quality = 'stale'
            fingerprint = digest(message)
            old = db.execute('SELECT * FROM readings WHERE scope=? AND measurement=? AND source=? ORDER BY id DESC LIMIT 1', (scope, message['measurement'], principal)).fetchone()
            if old and seq <= old['sequence']:
                repeated = db.execute('SELECT fingerprint FROM readings WHERE scope=? AND measurement=? AND source=? AND sequence=?', (scope, message['measurement'], principal, seq)).fetchone()
                if repeated and repeated['fingerprint'] == fingerprint:
                    return {'duplicate': True}
                raise ValueError('Replayed or changed sequence')
            if old and source_time < old['source_time']:
                raise ValueError('Out-of-order source timestamp')
            db.execute('INSERT INTO readings(scope,measurement,source,sequence,source_time,received,value,quality,unit,fingerprint) VALUES(?,?,?,?,?,?,?,?,?,?)', (scope, message['measurement'], principal, seq, source_time, now, value, quality, m['unit'], fingerprint))
            for rule in a['alarms']:
                if rule['measurement'] == message['measurement']:
                    self._alarm(db, a, scope, rule, value, quality, source_time, now, old)
            return {'duplicate': False, 'quality': quality}

    def _alarm(self, db, a, scope, rule, value, quality, source_time, now, previous):
        key = scope + '|' + rule['id']
        db.execute('INSERT OR IGNORE INTO alarms(key,scope,rule) VALUES(?,?,?)', (key, scope, rule['id']))
        alarm = dict(db.execute('SELECT * FROM alarms WHERE key=?', (key,)).fetchone())
        if quality != 'valid':
            db.execute('UPDATE alarms SET pending=NULL WHERE key=?', (key,))
            return  # Missing data neither clears a fault nor establishes persistence.
        if value >= rule['high']:
            gap = previous and source_time - previous['source_time'] > a['measurements'][rule['measurement']]['stale_seconds']
            pending = source_time if alarm['pending'] is None or gap else alarm['pending']
            db.execute('UPDATE alarms SET pending=? WHERE key=?', (pending, key))
            if source_time - pending >= rule['delay_seconds'] and (not alarm['active'] or now - alarm['last_event'] >= rule['repeat_seconds']):
                new_case = not alarm['active'] and alarm['erp_status'] in ('Closed', 'Resolved')
                incident = uuid.uuid4().hex if new_case else alarm['incident'] or uuid.uuid4().hex
                occurrence = 1 if new_case else alarm['occurrences'] + 1
                if new_case:
                    db.execute('UPDATE alarms SET case_id=NULL,erp_status=NULL,acknowledged_by=NULL WHERE key=?', (key,))
                db.execute('UPDATE alarms SET active=1,incident=?,last_event=?,occurrences=? WHERE key=?', (incident, now, occurrence, key))
                self.audit(db, a['source_id'], 'alarm-active', scope, {'rule': rule['id'], 'incident': incident, 'occurrence': occurrence})
                if rule.get('maintenance'):
                    self._enqueue(db, a, rule, incident, occurrence, 'active', now)
        elif value <= rule['clear_below']:
            db.execute('UPDATE alarms SET pending=NULL,active=0 WHERE key=?', (key,))
            if alarm['active']:
                self.audit(db, a['source_id'], 'alarm-cleared', scope, {'incident': alarm['incident']})
                self._enqueue(db, a, rule, alarm['incident'], alarm['occurrences'], 'cleared', now)
        # Deadband does not build an activation delay, but preserves an active alarm.
        elif not alarm['active']:
            db.execute('UPDATE alarms SET pending=NULL WHERE key=?', (key,))

    def _enqueue(self, db, a, rule, incident, occurrence, condition, now):
        eid = digest([incident, occurrence, condition])
        body = dict(event_id=eid, incident_id=incident, city=a['city'], environment=a['environment'],
            company=a['company_id'], project=a['erp_project'], asset_id=a['asset_id'],
            erp_asset_id=a['erp_asset_id'], rule=rule['id'], response=rule['response'],
            engineering_revision=a['engineering_revision'], occurrence=occurrence, condition=condition,
            observed_at=now, evidence=f'/docs/lifecycle/?city={a["city"]}&asset={a["asset_id"]}&environment={a["environment"]}')
        db.execute('INSERT OR IGNORE INTO outbox(id,incident,body) VALUES(?,?,?)', (eid, incident, json.dumps(body)))

    def snapshot(self, city=None, environment=None, now=None):
        now = time.time() if now is None else now
        with self.connect() as db:
            rows = db.execute('SELECT * FROM assets WHERE (? IS NULL OR city=?) AND (? IS NULL OR environment=?) ORDER BY scope', (city, city, environment, environment)).fetchall()
            assets = []
            for row in rows:
                a = dict(json.loads(row['body']), lifecycle_state=row['state'], readings={}, alarms=[])
                for name, m in a['measurements'].items():
                    r = db.execute('SELECT * FROM readings WHERE scope=? AND measurement=? ORDER BY id DESC LIMIT 1', (row['scope'], name)).fetchone()
                    reading = dict(r) if r else {'value': None, 'quality': 'disconnected', 'source_time': None, 'received': None, 'unit': m['unit']}
                    if r and now - min(r['source_time'], r['received']) > m['stale_seconds']:
                        reading['quality'] = 'disconnected' if now - r['received'] > m['stale_seconds'] * 3 else 'stale'
                    a['readings'][name] = reading
                a['alarms'] = [dict(r) for r in db.execute('SELECT * FROM alarms WHERE scope=?', (row['scope'],))]
                a['installations'] = [dict(r) for r in db.execute('SELECT * FROM installations WHERE scope=? ORDER BY installed', (row['scope'],))]
                a['evidence'] = [dict(r) for r in db.execute('SELECT * FROM evidence WHERE scope=? ORDER BY created', (row['scope'],))]
                a['commands_audit'] = [dict(r) for r in db.execute('SELECT * FROM commands WHERE scope=? ORDER BY rowid DESC LIMIT 20', (row['scope'],))]
                assets.append(a)
            queue = [dict(r) for r in db.execute('SELECT id,incident,state,attempts,next_try,error,response FROM outbox ORDER BY rowid DESC LIMIT 100')]
            if city or environment:
                incidents = {r['incident'] for a in assets for r in a['alarms']}
                queue = [r for r in queue if r['incident'] in incidents]
            return dict(schema='osr-lifecycle-twin/1', observed_at=now, assets=assets, outbox=queue,
                        authority='OSR evidence references; ERP closure and alarm clearance do not grant railway release')

    def acknowledge(self, city, environment, asset, rule, actor):
        scope = self.scope(city, environment, asset)
        with self.connect() as db:
            result = db.execute('UPDATE alarms SET acknowledged_by=? WHERE key=?', (actor, scope + '|' + identifier(rule)))
            if not result.rowcount:
                raise ValueError('Unknown alarm')
            self.audit(db, actor, 'alarm-acknowledged', scope, {'rule': rule})
        return {'acknowledged': True}

    def command(self, message, actor, allowed, now=None):
        now = time.time() if now is None else now
        cid = identifier(message['request_id'])
        scope = self.scope(message['city'], message['environment'], message['asset_id'])
        fingerprint = digest([message, actor])
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            old = db.execute('SELECT * FROM commands WHERE id=?', (cid,)).fetchone()
            if old:
                if old['fingerprint'] != fingerprint:
                    raise ValueError('Command identity reused with changed request')
                return dict(old)
            state, reason, expires = 'requested', '', now
            try:
                a = self.asset(db, scope)
                rule = a['commands'].get(message['command'])
                if not allowed:
                    raise PermissionError('Operator command permission required')
                if not rule or a['environment'] != 'simulation':
                    raise ValueError('Command not enabled for this commissioned controller')
                created, expires = timestamp(message['created_at']), timestamp(message['expires_at'])
                if created > now + 5 or expires <= now or expires - created > rule['max_ttl_seconds'] or expires <= created:
                    raise ValueError('Command expired or invalid lifetime')
                if set(message['parameters']) != {rule['parameter']}:
                    raise ValueError('Unexpected command parameters')
                finite(message['parameters'][rule['parameter']], rule['min'], rule['max'])
                if message.get('required_conditions') != rule['required_conditions']:
                    raise ValueError('Required operating conditions missing')
            except (ValueError, PermissionError) as exc:
                state, reason = 'rejected', str(exc)
            db.execute('INSERT INTO commands VALUES(?,?,?,?,?,?,?,?)', (cid, scope, json.dumps(message), fingerprint, actor, state, expires, reason))
            self.audit(db, actor, 'command-' + state, scope, {'request_id': cid, 'reason': reason})
            return {'request_id': cid, 'state': state, 'reason': reason}

    def controller_commands(self, principal, now=None):
        now = time.time() if now is None else now
        with self.connect() as db:
            result = []
            for row in db.execute("SELECT * FROM commands WHERE state IN ('requested','accepted')").fetchall():
                a = self.asset(db, row['scope'])
                if a['source_id'] != principal:
                    continue
                if row['expires'] <= now:
                    db.execute("UPDATE commands SET state='failed',result='expired before completion' WHERE id=?", (row['id'],))
                    self.audit(db, principal, 'command-failed', row['scope'], {'request_id': row['id'], 'reason': 'expired'})
                else:
                    result.append(json.loads(row['body']))
            return result

    def controller_result(self, cid, principal, state, result, now=None):
        now = time.time() if now is None else now
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT * FROM commands WHERE id=?', (identifier(cid),)).fetchone()
            if not row or self.asset(db, row['scope'])['source_id'] != principal:
                raise PermissionError('Controller does not own command')
            # Lost replies may cause the same owned controller result to be retried.
            if row['state'] == state and row['result'] == str(result)[:2000] and (state in ('completed', 'failed', 'rejected') or row['expires'] > now):
                return {'state': state}
            transitions = {'requested': ('accepted', 'rejected'), 'accepted': ('completed', 'failed')}
            if state not in transitions.get(row['state'], ()):
                raise ValueError('Invalid controller command transition')
            if row['expires'] <= now:
                state, result = 'failed', 'expired before controller result'
            db.execute('UPDATE commands SET state=?,result=? WHERE id=?', (state, str(result)[:2000], cid))
            self.audit(db, principal, 'command-' + state, row['scope'], {'request_id': cid, 'result': result})
            return {'state': state}

    def evidence(self, message, actor, role):
        scope = self.scope(message['city'], message['environment'], message['asset_id'])
        eid = identifier(message['id'])
        kinds = {'design-review': 'engineer', 'execution-release': 'reviewer', 'installation': 'engineer',
                 'commissioning-test': 'inspector', 'commissioning-release': 'reviewer', 'maintenance': 'maintainer',
                 'renewal': 'reviewer', 'analysis': 'engineer', 'change-proposal': 'engineer'}
        kind = message['kind']
        if kinds.get(kind) != role:
            raise PermissionError('Evidence authority required')
        refs = message.get('references')
        if not isinstance(refs, list) or not 1 <= len(refs) <= 50 or any(
                not isinstance(ref, str) or not ref.strip() or len(ref) > 2048 for ref in refs):
            raise ValueError('Provide 1 to 50 non-empty versioned evidence references')
        if not message.get('engineering_revision'):
            raise ValueError('Versioned source evidence required')
        if kind == 'commissioning-test' and message.get('result') not in {'pass', 'fail'}:
            raise ValueError('Commissioning test result must be pass or fail')
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            a = self.asset(db, scope)
            if message['engineering_revision'] != a['engineering_revision']:
                raise ValueError('Evidence targets a different engineering revision')
            old = db.execute('SELECT body,actor FROM evidence WHERE id=?', (eid,)).fetchone()
            if old:
                if old['body'] != json.dumps(message, sort_keys=True) or old['actor'] != actor:
                    raise ValueError('Evidence is immutable')
                return {'id': eid, 'created': False}
            evidence = [dict(r) for r in db.execute('SELECT * FROM evidence WHERE scope=?', (scope,))]
            current = [r for r in evidence if json.loads(r['body'])['engineering_revision'] == a['engineering_revision']]
            if kind == 'execution-release' and not any(r['kind'] == 'design-review' for r in current):
                raise ValueError('Reviewed design required before execution')
            if kind == 'maintenance' and a['lifecycle_state'] not in ('as-commissioned', 'as-maintained'):
                raise ValueError('Maintenance configuration requires a commissioned asset')
            if kind == 'installation':
                if not any(r['kind'] == 'execution-release' for r in current):
                    raise ValueError('Released execution package required')
                identifier(message['serial']); identifier(message.get('batch') or 'unbatched')
                prefix = a['city'] + '|' + a['environment'] + '|'
                duplicate = db.execute('SELECT scope FROM installations WHERE serial=? AND removed IS NULL AND substr(scope,1,?)=? AND scope!=?', (message['serial'], len(prefix), prefix, scope)).fetchone()
                if duplicate:
                    raise ValueError('Physical serial is already installed at another position')
                existing = db.execute('SELECT * FROM installations WHERE scope=? AND removed IS NULL', (scope,)).fetchone()
                if existing:
                    if message.get('replaces_serial') != existing['serial']:
                        raise ValueError('Explicit replacement serial required')
                    db.execute('UPDATE installations SET removed=? WHERE id=?', (time.time(), existing['id']))
                db.execute('INSERT INTO installations VALUES(?,?,?,?,?,?,?,NULL)', (eid, scope, message['serial'], message.get('batch', ''), a['engineering_revision'], eid, time.time()))
            if kind == 'commissioning-test' and not any(r['kind'] == 'installation' for r in current):
                raise ValueError('Recorded installation required before commissioning test')
            if kind == 'commissioning-release':
                latest_install = max((r['created'] for r in current if r['kind'] == 'installation'), default=0)
                tests = [r for r in current if r['created'] > latest_install and r['kind'] == 'commissioning-test' and json.loads(r['body']).get('result') == 'pass']
                if not tests or tests[-1]['actor'] == actor or message.get('test_id') != tests[-1]['id']:
                    raise ValueError('Independent release must reference a passing commissioning test')
                if a['environment'] == 'physical':
                    raise ValueError('Physical release must be imported from approved OSR assurance; local API cannot grant it')
            states = {'design-review': 'as-designed', 'execution-release': 'released-for-execution', 'installation': 'as-built', 'commissioning-release': 'as-commissioned', 'maintenance': 'as-maintained'}
            db.execute('INSERT INTO evidence VALUES(?,?,?,?,?,?)', (eid, scope, kind, actor, json.dumps(message, sort_keys=True), time.time()))
            if kind in states:
                db.execute('UPDATE assets SET state=? WHERE scope=?', (states[kind], scope))
            self.audit(db, actor, 'evidence-' + kind, scope, {'id': eid})
        return {'id': eid, 'created': True}

    def affected(self, serial=None, batch=None):
        if not serial and not batch:
            raise ValueError('Serial or batch required')
        with self.connect() as db:
            return [dict(r) for r in db.execute('SELECT * FROM installations WHERE (? IS NULL OR serial=?) AND (? IS NULL OR batch=?)', (serial, serial, batch, batch))]

    def prune(self, now=None):
        now = time.time() if now is None else now
        with self.connect() as db:
            # Keep the latest reading even after retention: it must be shown as disconnected.
            for row in db.execute('SELECT scope,package FROM assets').fetchall():
                package = json.loads(db.execute('SELECT body FROM packages WHERE hash=?', (row['package'],)).fetchone()['body'])
                cutoff = now - package['historian']['retention_days'] * 86400
                db.execute('DELETE FROM readings WHERE scope=? AND received<? AND id NOT IN (SELECT MAX(id) FROM readings WHERE scope=? GROUP BY measurement,source)', (row['scope'], cutoff, row['scope']))

    def backup(self, destination):
        with self.connect() as db, closing(sqlite3.connect(str(destination))) as target:
            db.backup(target)
