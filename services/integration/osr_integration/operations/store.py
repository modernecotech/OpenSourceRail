"""Atomic plan baselines and idempotent offline execution outbox in the gateway DB."""
import json
import time
from datetime import datetime
from ..config import digest, identifier
from .contracts import validate
from .field import Conflict, validate_completion, validate_work
from .planning import plan


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


class OperationsStore:
    def __init__(self, store):
        self.store = store
        with store.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS operations_baselines (
                    scope TEXT PRIMARY KEY, hash TEXT NOT NULL, body TEXT NOT NULL, actor TEXT NOT NULL, updated REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS operations_plans (
                    id TEXT PRIMARY KEY, scope TEXT NOT NULL, baseline TEXT NOT NULL, body TEXT NOT NULL, actor TEXT NOT NULL, created REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS field_work (
                    id TEXT PRIMARY KEY, scope TEXT NOT NULL, baseline TEXT NOT NULL, body TEXT NOT NULL, state TEXT NOT NULL, actor TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS field_events (
                    id TEXT PRIMARY KEY, work_id TEXT NOT NULL UNIQUE, scope TEXT NOT NULL, hash TEXT NOT NULL,
                    body TEXT NOT NULL, actor TEXT NOT NULL, state TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
                    next_try REAL NOT NULL DEFAULT 0, response TEXT, error TEXT, created REAL NOT NULL);
                CREATE INDEX IF NOT EXISTS field_pending ON field_events(state,next_try);
                CREATE INDEX IF NOT EXISTS operations_plans_scope ON operations_plans(scope,created);
            ''')

    @staticmethod
    def scope(city, environment):
        return identifier(city) + '|' + identifier(environment)

    def baseline(self, city, environment):
        with self.store.connect() as db:
            row = db.execute('SELECT * FROM operations_baselines WHERE scope=?', (self.scope(city, environment),)).fetchone()
        if not row: raise ValueError('No controlled operations baseline for selected scope')
        return dict(sha256=row['hash'], package=json.loads(row['body']))

    def register(self, package, actor, expected):
        p = validate(package); scope = self.scope(p['city'], p['environment']); sha = digest(p)
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            current = db.execute('SELECT hash FROM operations_baselines WHERE scope=?', (scope,)).fetchone()
            if expected != (current['hash'] if current else None): raise Conflict('Operations baseline changed; refresh before replacing')
            db.execute('INSERT INTO operations_baselines VALUES(?,?,?,?,?) ON CONFLICT(scope) DO UPDATE SET hash=excluded.hash,body=excluded.body,actor=excluded.actor,updated=excluded.updated',
                       (scope, sha, encoded(p), actor, time.time()))
            self.store.audit(db, actor, 'operations-baseline', scope, dict(sha256=sha, previous=expected))
        return dict(sha256=sha, revision=p['revision'], movement_authority=False)

    def create_plan(self, city, environment, expected, actor, disruptions=None):
        baseline = self.baseline(city, environment)
        if baseline['sha256'] != expected: raise Conflict('Operations baseline changed')
        result = plan(baseline['package'], disruptions)
        scope = self.scope(city, environment)
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT hash FROM operations_baselines WHERE scope=?', (scope,)).fetchone()['hash'] != expected:
                raise Conflict('Operations baseline changed during planning')
            db.execute('INSERT OR IGNORE INTO operations_plans VALUES(?,?,?,?,?,?)',
                (result['sha256'], scope, expected, encoded(result), actor, time.time()))
            self.store.audit(db, actor, 'operations-plan', scope, dict(sha256=result['sha256']))
        return result

    def get_plan(self, city, environment, plan_id):
        with self.store.connect() as db:
            row = db.execute('SELECT body,baseline FROM operations_plans WHERE id=? AND scope=?',
                (plan_id, self.scope(city, environment))).fetchone()
        if not row: raise ValueError('Plan not found in authenticated scope')
        result = json.loads(row['body'])
        result['current_baseline'] = row['baseline'] == self.baseline(city, environment)['sha256']
        return result

    def issue_work(self, work, actor, expected):
        validate_work(work)
        expiry = datetime.fromisoformat(work['expires_at'].replace('Z', '+00:00'))
        if expiry.tzinfo is None or expiry.timestamp() <= time.time(): raise ValueError('Work pack expiry must be in the future')
        baseline = self.baseline(work['city'], work['environment'])
        if expected != baseline['sha256']: raise Conflict('Work pack baseline is stale')
        scope = self.scope(work['city'], work['environment'])
        asset_scope = self.store.scope(work['city'], work['environment'], work['asset_id'])
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT hash FROM operations_baselines WHERE scope=?', (scope,)).fetchone()['hash'] != expected:
                raise Conflict('Work pack baseline changed during issue')
            asset = self.store.asset(db, asset_scope)
            if asset['configuration_status'] != 'active': raise Conflict('Asset configuration needs disposition')
            data = asset
            if data['erp_asset_id'] != work['erp_asset']: raise ValueError('Work pack/native asset binding mismatch')
            installation = db.execute('SELECT serial FROM installations WHERE scope=? AND removed IS NULL', (asset_scope,)).fetchone()
            pack = dict(work, baseline_sha256=expected, engineering_revision=data['engineering_revision'],
                        physical_serial=installation['serial'] if installation else '', issued_by=actor,
                        operational_release=False)
            pack['sha256'] = digest(pack)
            old = db.execute('SELECT body FROM field_work WHERE id=?', (work['id'],)).fetchone()
            if old:
                if old['body'] != encoded(pack): raise Conflict('Work identity reused with changed pack')
                return json.loads(old['body'])
            db.execute('INSERT INTO field_work VALUES(?,?,?,?,?,?)', (work['id'], scope, expected, encoded(pack), 'issued', actor))
            self.store.audit(db, actor, 'field-pack-issued', asset_scope, dict(id=work['id'], sha256=pack['sha256']))
        return pack

    def packs(self, city, environment, actor, manager=False):
        with self.store.connect() as db:
            rows = db.execute('SELECT body,state FROM field_work WHERE scope=? ORDER BY id LIMIT 500', (self.scope(city, environment),)).fetchall()
        return [dict(json.loads(row['body']), state=row['state']) for row in rows if manager or json.loads(row['body'])['assigned_to'] == actor]

    def revoke(self, city, environment, work_id, actor):
        with self.store.connect() as db:
            changed = db.execute("UPDATE field_work SET state='revoked' WHERE id=? AND scope=? AND state='issued'", (work_id, self.scope(city, environment))).rowcount
            if not changed: raise Conflict('Only currently issued work can be revoked')
            self.store.audit(db, actor, 'field-pack-revoked', self.scope(city, environment), dict(id=work_id))
        return dict(id=work_id, state='revoked')

    def complete(self, city, environment, event, actor):
        scope = self.scope(city, environment); fingerprint = digest(dict(event=event, actor=actor, scope=scope))
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            known = db.execute('SELECT * FROM field_events WHERE id=?', (event['id'],)).fetchone()
            if known:
                if known['hash'] != fingerprint: raise Conflict('Offline event identity reused with changed data')
                return dict(id=event['id'], state=known['state'], duplicate=True, response=json.loads(known['response']) if known['response'] else None)
            row = db.execute('SELECT * FROM field_work WHERE id=? AND scope=?', (event['work_id'], scope)).fetchone()
            if not row: raise ValueError('Work pack not found in authenticated scope')
            work = json.loads(row['body'])
            if work['assigned_to'] != actor: raise PermissionError('Work is assigned to another technician')
            if row['state'] != 'issued': raise Conflict('Work was revoked or already performed')
            if db.execute('SELECT hash FROM operations_baselines WHERE scope=?', (scope,)).fetchone()['hash'] != row['baseline']:
                raise Conflict('Planning baseline changed while device was offline')
            if datetime.fromisoformat(work['expires_at'].replace('Z', '+00:00')).timestamp() <= time.time(): raise Conflict('Work pack expired')
            asset_scope = self.store.scope(city, environment, work['asset_id'])
            asset = self.store.asset(db, asset_scope); data = asset
            if asset['configuration_status'] != 'active' or data['engineering_revision'] != work['engineering_revision'] or data['erp_asset_id'] != work['erp_asset']:
                raise Conflict('Engineering revision or native binding changed')
            installation = db.execute('SELECT serial FROM installations WHERE scope=? AND removed IS NULL', (asset_scope,)).fetchone()
            if (installation['serial'] if installation else '') != work['physical_serial']: raise Conflict('Installed serial changed')
            validate_completion(work, event)
            packet = dict(schema='osr-field-completion/1', city=city, environment=environment,
                work=work, event=event, actor=actor, company=data['company_id'], project=data['erp_project'],
                idempotency_sha256=fingerprint, operational_release=False)
            db.execute('INSERT INTO field_events(id,work_id,scope,hash,body,actor,state,created) VALUES(?,?,?,?,?,?,?,?)',
                (event['id'], work['id'], scope, fingerprint, encoded(packet), actor, 'pending', time.time()))
            db.execute("UPDATE field_work SET state='performed-awaiting-inspection' WHERE id=?", (work['id'],))
            self.store.audit(db, actor, 'field-completion-queued', asset_scope, dict(event_id=event['id'], work_id=work['id']))
        return dict(id=event['id'], state='pending', duplicate=False, operational_release=False)

    def events(self, city, environment, actor, manager=False):
        with self.store.connect() as db:
            rows = db.execute('SELECT id,work_id,actor,state,error,response FROM field_events WHERE scope=? ORDER BY created DESC LIMIT 500', (self.scope(city, environment),)).fetchall()
        return [dict(row, response=json.loads(row['response']) if row['response'] else None) for row in rows if manager or row['actor'] == actor]
