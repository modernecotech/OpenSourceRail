"""Transactional identities, change review, telemetry and lifecycle audit."""
import hmac
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
            CREATE TABLE IF NOT EXISTS assets (scope TEXT PRIMARY KEY, city TEXT, environment TEXT, asset_id TEXT, package TEXT, body TEXT, state TEXT DEFAULT 'as-designed', configuration_status TEXT NOT NULL DEFAULT 'active');
            CREATE TABLE IF NOT EXISTS readings (id INTEGER PRIMARY KEY, scope TEXT, measurement TEXT, source TEXT, sequence INTEGER, source_time REAL, received REAL, value REAL, quality TEXT, unit TEXT, fingerprint TEXT, UNIQUE(scope,measurement,source,sequence));
            CREATE INDEX IF NOT EXISTS readings_latest ON readings(scope,measurement,id DESC);
            CREATE TABLE IF NOT EXISTS alarms (key TEXT PRIMARY KEY, scope TEXT, rule TEXT, pending REAL, active INTEGER DEFAULT 0, incident TEXT, last_event REAL DEFAULT 0, occurrences INTEGER DEFAULT 0, case_id TEXT, erp_status TEXT, acknowledged_by TEXT, acknowledged_at REAL, acknowledged_occurrence INTEGER);
            CREATE TABLE IF NOT EXISTS outbox (id TEXT PRIMARY KEY, incident TEXT, body TEXT, state TEXT DEFAULT 'pending', attempts INTEGER DEFAULT 0, next_try REAL DEFAULT 0, error TEXT, response TEXT);
            CREATE TABLE IF NOT EXISTS commands (id TEXT PRIMARY KEY, scope TEXT, body TEXT, fingerprint TEXT, actor TEXT, state TEXT, expires REAL, result TEXT);
            CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, at REAL, actor TEXT, action TEXT, scope TEXT, body TEXT);
            CREATE TABLE IF NOT EXISTS evidence (id TEXT PRIMARY KEY, scope TEXT, kind TEXT, actor TEXT, body TEXT, created REAL);
            CREATE TABLE IF NOT EXISTS installations (id TEXT PRIMARY KEY, scope TEXT, serial TEXT, batch TEXT, revision TEXT, evidence TEXT, installed REAL, removed REAL);
            CREATE UNIQUE INDEX IF NOT EXISTS installed_position ON installations(scope) WHERE removed IS NULL;
            CREATE TABLE IF NOT EXISTS deliveries (id TEXT PRIMARY KEY, scope TEXT, body TEXT, actor TEXT, created REAL);
            ''')
            # Forward-only migrations keep existing pilot historians usable.
            asset_columns = {row['name'] for row in db.execute('PRAGMA table_info(assets)')}
            if 'configuration_status' not in asset_columns:
                db.execute("ALTER TABLE assets ADD COLUMN configuration_status TEXT NOT NULL DEFAULT 'active'")
            alarm_columns = {row['name'] for row in db.execute('PRAGMA table_info(alarms)')}
            if 'acknowledged_at' not in alarm_columns:
                db.execute('ALTER TABLE alarms ADD COLUMN acknowledged_at REAL')
            if 'acknowledged_occurrence' not in alarm_columns:
                db.execute('ALTER TABLE alarms ADD COLUMN acknowledged_occurrence INTEGER')

            outbox_columns = {row['name'] for row in db.execute('PRAGMA table_info(outbox)')}
            for column in ('city', 'environment', 'asset_id'):
                if column not in outbox_columns:
                    db.execute(f'ALTER TABLE outbox ADD COLUMN {column} TEXT')
            # Existing event payloads retain scope even after an alarm is replaced.
            db.execute("""UPDATE outbox SET city=json_extract(body,'$.city'),
                environment=json_extract(body,'$.environment'), asset_id=json_extract(body,'$.asset_id')
                WHERE city IS NULL AND json_valid(body)""")
            db.executescript("""
                CREATE INDEX IF NOT EXISTS assets_city_environment ON assets(city,environment);
                CREATE INDEX IF NOT EXISTS outbox_city_environment ON outbox(city,environment);
                CREATE INDEX IF NOT EXISTS outbox_pending ON outbox(state,next_try);
                CREATE INDEX IF NOT EXISTS outbox_incident ON outbox(incident,state);
                CREATE INDEX IF NOT EXISTS alarms_scope ON alarms(scope);
                CREATE INDEX IF NOT EXISTS installations_scope ON installations(scope,installed);
                CREATE INDEX IF NOT EXISTS evidence_scope ON evidence(scope);
                CREATE INDEX IF NOT EXISTS commands_scope ON commands(scope);
            """)

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

    @staticmethod
    def _value_changes(before, after, prefix=''):
        """Return exact changed leaves without repeating unchanged package bodies."""
        if before == after:
            return []
        if isinstance(before, dict) and isinstance(after, dict):
            changes = []
            for key in sorted(before.keys() | after.keys()):
                path = f'{prefix}.{key}' if prefix else key
                if key not in before:
                    changes.append({'path': path, 'kind': 'added', 'before': None, 'after': after[key]})
                elif key not in after:
                    changes.append({'path': path, 'kind': 'removed', 'before': before[key], 'after': None})
                else:
                    changes.extend(Store._value_changes(before[key], after[key], path))
            return changes
        return [{'path': prefix, 'kind': 'changed', 'before': before, 'after': after}]

    @staticmethod
    def _change_categories(change_type, changes, asset):
        fields = {row['path'].split('.', 1)[0] for row in changes}
        categories = set()
        mapping = {
            'engineering_revision': 'design-definition',
            'component_type_id': 'design-definition',
            'planned_asset_id': 'asset-topology',
            'parent_asset_id': 'asset-topology',
            'site_id': 'asset-topology',
            'source_asset_ids': 'asset-topology',
            'ifc_global_id': 'asset-topology',
            'source_crates': 'embedded-runtime',
            'measurements': 'telemetry-contract',
            'telemetry_namespace': 'telemetry-contract',
            'source_id': 'telemetry-contract',
            'binding_status': 'telemetry-contract',
            'supplier_binding': 'telemetry-contract',
            'physical_serial_id': 'telemetry-contract',
            'alarms': 'alarm-maintenance',
            'commands': 'command-boundary',
            'manufacturing_method': 'design-definition',
            'company_id': 'business-execution',
            'erp_project': 'business-execution',
            'erp_item_code': 'business-execution',
            'erp_asset_id': 'business-execution',
            'name': 'operator-display',
            'equipment_type': 'operator-display',
            'fuxa_device_id': 'operator-display',
        }
        for field in fields:
            if field in mapping:
                categories.add(mapping[field])
        if 'manufacturing_method' in fields:
            categories.update({'business-execution', 'operator-display'})
        if change_type in ('added', 'removed'):
            categories.update({'design-definition', 'asset-topology', 'operator-display'})
            if asset.get('source_crates'):
                categories.add('embedded-runtime')
            if asset.get('measurements'):
                categories.add('telemetry-contract')
            if asset.get('alarms'):
                categories.add('alarm-maintenance')
            if asset.get('commands'):
                categories.add('command-boundary')
            if any(asset.get(key) for key in ('erp_project', 'erp_item_code', 'erp_asset_id')):
                categories.add('business-execution')
        return sorted(categories)

    @staticmethod
    def _dependencies(before, after):
        values = [value for value in (before, after) if value]
        def unique(field, many=False):
            found = set()
            for value in values:
                item = value.get(field, [] if many else '')
                found.update(item if many else [item])
            return sorted(v for v in found if v)
        methods = [value.get('manufacturing_method') for value in values
                   if isinstance(value.get('manufacturing_method'), dict)]
        return {
            'component_type_ids': unique('component_type_id'),
            'parent_asset_ids': unique('parent_asset_id'),
            'source_asset_ids': unique('source_asset_ids', True),
            'source_crates': unique('source_crates', True),
            'ifc_global_ids': unique('ifc_global_id'),
            'erp_projects': unique('erp_project'),
            'erp_item_codes': unique('erp_item_code'),
            'erp_asset_ids': unique('erp_asset_id'),
            'manufacturing_method_ids': sorted({row.get('method_id') for row in methods if row.get('method_id')}),
            'manufacturing_product_ids': sorted({item for row in methods for item in row.get('product_ids', [])}),
            'manufacturing_tooling_ids': sorted({item for row in methods for item in row.get('tooling_ids', [])}),
        }

    @staticmethod
    def _review_steps(change_type, categories, records):
        steps = set()
        category_steps = {
            'design-definition': 'Review drawings, calculations, quantities and derived engineering evidence.',
            'asset-topology': 'Review CAD/BIM/GIS interfaces, parent assembly and installed-position mapping.',
            'embedded-runtime': 'Rebuild affected source crates and repeat their native and adapter contract tests.',
            'telemetry-contract': 'Review units, ranges, scaling, timestamp, disconnect and invalid-value behaviour.',
            'alarm-maintenance': 'Review alarm persistence, thresholds, response and ERP maintenance routing.',
            'command-boundary': 'Review controller ownership, bounds, expiry and local permissive conditions.',
            'business-execution': 'Review ERP Item/BOM mappings and matching procurement, stock and production records.',
            'operator-display': 'Review FUXA/Workbench labels, navigation and operator task presentation.',
        }
        steps.update(category_steps[c] for c in categories if c in category_steps)
        if records['evidence'] or records['installations']:
            steps.add('Reassess the listed installation, inspection, commissioning and maintenance evidence; do not overwrite it.')
        if change_type == 'added':
            steps.add('Complete the normal execution, installation and commissioning evidence sequence before use.')
        if change_type == 'removed':
            steps.add('Confirm safe retirement, unresolved alarms/cases and replacement or removal evidence.')
        return sorted(steps)

    def _package_review(self, db, package):
        row = db.execute(
            'SELECT hash,body FROM packages WHERE city=? AND environment=? ORDER BY created DESC LIMIT 1',
            (package['city'], package['environment'])).fetchone()
        baseline = json.loads(row['body']) if row else None
        before_assets = {a['asset_id']: a for a in baseline['equipment']} if baseline else {}
        after_assets = {a['asset_id']: a for a in package['equipment']}
        prefix = package['city'] + '|' + package['environment'] + '|'
        scoped = 'substr(scope,1,?)=?'
        scoped_args = (len(prefix), prefix)
        evidence = {}
        for item in db.execute(f'SELECT * FROM evidence WHERE {scoped} ORDER BY scope,created,id', scoped_args):
            body = json.loads(item['body'])
            evidence.setdefault(item['scope'], []).append({
                'id': item['id'], 'kind': item['kind'], 'actor': item['actor'],
                'engineering_revision': body.get('engineering_revision'),
                'references': body.get('references', []), 'result': body.get('result'),
                'created': item['created'], 'review_status': 'requires-review',
            })
        installations = {}
        for item in db.execute(f'SELECT * FROM installations WHERE {scoped} ORDER BY scope,installed,id', scoped_args):
            installations.setdefault(item['scope'], []).append({key: item[key] for key in
                ('id', 'serial', 'batch', 'revision', 'evidence', 'installed', 'removed')})
        alarms = {}
        for item in db.execute(f"SELECT * FROM alarms WHERE {scoped} AND (active=1 OR (case_id IS NOT NULL AND COALESCE(erp_status,'') NOT IN ('Closed','Resolved'))) ORDER BY scope,rule", scoped_args):
            alarms.setdefault(item['scope'], []).append({key: item[key] for key in
                ('rule', 'active', 'incident', 'occurrences', 'case_id', 'erp_status')})
        commands = {}
        for item in db.execute(f"SELECT * FROM commands WHERE {scoped} AND state IN ('requested','accepted') ORDER BY scope,id", scoped_args):
            body = json.loads(item['body'])
            commands.setdefault(item['scope'], []).append({
                'id': item['id'], 'state': item['state'], 'actor': item['actor'],
                'command': body.get('command'), 'expires': item['expires'],
            })

        changes = []
        for asset_id in sorted(before_assets.keys() | after_assets.keys()):
            before, after = before_assets.get(asset_id), after_assets.get(asset_id)
            if before == after:
                continue
            change_type = 'added' if before is None else 'removed' if after is None else 'changed'
            value_changes = [] if change_type != 'changed' else self._value_changes(before, after)
            reference = after or before
            categories = self._change_categories(change_type, value_changes, reference)
            scope = self.scope(package['city'], package['environment'], asset_id)
            records = {
                'installations': installations.get(scope, []),
                'evidence': evidence.get(scope, []),
                'open_alarms_or_cases': alarms.get(scope, []),
                'pending_commands': commands.get(scope, []),
            }
            changes.append({
                'asset_id': asset_id, 'name': reference.get('name', asset_id),
                'change_type': change_type,
                'before_sha256': digest(before) if before else None,
                'after_sha256': digest(after) if after else None,
                'changed_values': value_changes,
                'categories': categories,
                'dependencies': self._dependencies(before, after),
                'affected_records': records,
                'required_reviews': self._review_steps(change_type, categories, records),
            })

        package_changes = self._value_changes(
            {k: v for k, v in (baseline or {}).items() if k not in ('sha256', 'equipment')},
            {k: v for k, v in package.items() if k not in ('sha256', 'equipment')})
        summary = {
            'added': sum(c['change_type'] == 'added' for c in changes),
            'changed': sum(c['change_type'] == 'changed' for c in changes),
            'removed': sum(c['change_type'] == 'removed' for c in changes),
            'unchanged': len(before_assets.keys() & after_assets.keys()) - sum(c['change_type'] == 'changed' for c in changes),
            'package_values_changed': len(package_changes),
            'installed_serials_affected': sum(len(c['affected_records']['installations']) for c in changes),
            'evidence_records_requiring_review': sum(len(c['affected_records']['evidence']) for c in changes),
            'open_alarms_or_cases': sum(len(c['affected_records']['open_alarms_or_cases']) for c in changes),
            'pending_commands': sum(len(c['affected_records']['pending_commands']) for c in changes),
        }
        blockers = []
        if baseline and package['environment'] == 'physical':
            blockers.append('Physical mapping changes require a separately commissioned migration.')
        for change in changes:
            if any(row['path'] == 'component_type_id' for row in change['changed_values']):
                blockers.append(f"{change['asset_id']}: component substitution requires explicit replacement.")
            if change['change_type'] == 'removed' and any(not row['removed'] for row in change['affected_records']['installations']):
                blockers.append(f"{change['asset_id']}: installed serial requires recorded removal or replacement.")
            if change['change_type'] == 'changed' and 'command-boundary' in change['categories'] and change['affected_records']['pending_commands']:
                blockers.append(f"{change['asset_id']}: command contract cannot change while requests are pending.")
        status = 'initial-installation' if baseline is None else 'no-change' if not changes and not package_changes else 'review-required'
        review = {
            'schema': 'osr-supervisory-change-review/1',
            'city': package['city'], 'environment': package['environment'],
            'status': status,
            'baseline_sha256': row['hash'] if row else None,
            'proposed_sha256': package['sha256'],
            'baseline_engineering_revision': baseline.get('engineering_revision') if baseline else None,
            'proposed_engineering_revision': package['engineering_revision'],
            'summary': summary, 'package_changes': package_changes, 'equipment_changes': changes,
            'application': {'automatic_apply_permitted': not blockers, 'blockers': blockers},
            'scope_isolation': {'target': f"{package['city']}|{package['environment']}",
                                'other_city_environments_mutated': False},
            'authority': 'Preview only: the accepted baseline, append-only evidence and other city/environment scopes are unchanged; review is not engineering or railway approval.',
        }
        review['sha256'] = digest(review)
        return review

    def package_review(self, package):
        """Compare a proposal with the live baseline without changing either."""
        validate_package(package)
        with self.connect() as db:
            return self._package_review(db, package)

    def apply(self, package, actor, expected=None, review_sha256=None):
        validate_package(package)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            existing = db.execute('SELECT hash FROM packages WHERE city=? AND environment=? ORDER BY created DESC LIMIT 1', (package['city'], package['environment'])).fetchone()
            if existing and existing['hash'] == package['sha256']:
                return {'created': False, 'sha256': package['sha256']}
            if existing and expected != existing['hash']:
                raise ValueError('Configuration changed: review diff and provide expected previous hash')
            review = self._package_review(db, package) if existing else None
            if existing and (not isinstance(review_sha256, str) or not hmac.compare_digest(review_sha256, review['sha256'])):
                raise ValueError('Package or affected lifecycle records changed after review; preview again')
            if review and review['application']['blockers']:
                raise ValueError('Automatic apply blocked: ' + ' '.join(review['application']['blockers']))
            # Identity rows survive package revisions. Removed positions stay as history.
            package_scopes = {self.scope(a['city'], a['environment'], a['asset_id']) for a in package['equipment']}
            configured = db.execute('SELECT scope,configuration_status FROM assets WHERE city=? AND environment=?',
                                    (package['city'], package['environment'])).fetchall()
            for row in configured:
                if row['scope'] in package_scopes or row['configuration_status'] == 'retired':
                    continue
                db.execute("UPDATE assets SET configuration_status='retired' WHERE scope=?", (row['scope'],))
                commands = db.execute("SELECT id FROM commands WHERE scope=? AND state IN ('requested','accepted')", (row['scope'],)).fetchall()
                db.execute("UPDATE commands SET state='failed',result='asset retired by supervisory package' WHERE scope=? AND state IN ('requested','accepted')", (row['scope'],))
                for command in commands:
                    self.audit(db, actor, 'command-failed', row['scope'],
                               {'request_id': command['id'], 'reason': 'asset retired by supervisory package'})
                self.audit(db, actor, 'asset-retired', row['scope'], {'package': package['sha256']})
            for asset in package['equipment']:
                scope = self.scope(asset['city'], asset['environment'], asset['asset_id'])
                old = db.execute('SELECT body,configuration_status FROM assets WHERE scope=?', (scope,)).fetchone()
                if old and json.loads(old['body'])['component_type_id'] != asset['component_type_id']:
                    raise ValueError('Component type substitution requires explicit replacement')
                db.execute("INSERT INTO assets(scope,city,environment,asset_id,package,body,configuration_status) VALUES(?,?,?,?,?,?,'active') ON CONFLICT(scope) DO UPDATE SET package=excluded.package,body=excluded.body,configuration_status='active'", (scope, asset['city'], asset['environment'], asset['asset_id'], package['sha256'], json.dumps(asset)))
                if old and old['configuration_status'] == 'retired':
                    self.audit(db, actor, 'asset-reactivated', scope, {'package': package['sha256']})
            db.execute('INSERT INTO packages VALUES(?,?,?,?,?,?) ON CONFLICT(hash) DO UPDATE SET actor=excluded.actor,created=excluded.created',
                       (package['sha256'], package['city'], package['environment'], json.dumps(package), actor, time.time()))
            self.audit(db, actor, 'package-applied', package['city'], {
                'sha256': package['sha256'], 'previous': expected,
                'review_sha256': review['sha256'] if review else None})
            return {'created': True, 'sha256': package['sha256'], 'equipment': len(package['equipment']),
                    'review_sha256': review['sha256'] if review else None}

    def asset(self, db, scope):
        row = db.execute('SELECT body,state,configuration_status FROM assets WHERE scope=?', (scope,)).fetchone()
        if not row:
            raise ValueError('Unknown asset in this city/environment')
        return dict(json.loads(row['body']), lifecycle_state=row['state'],
                    configuration_status=row['configuration_status'])

    def ingest(self, message, principal, now=None):
        now = time.time() if now is None else now
        scope = self.scope(message['city'], message['environment'], message['asset_id'])
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            a = self.asset(db, scope)
            if a['configuration_status'] != 'active':
                raise ValueError('Telemetry rejected for retired asset configuration')
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
                new_activation = not alarm['active']
                new_case = not alarm['active'] and alarm['erp_status'] in ('Closed', 'Resolved')
                incident = uuid.uuid4().hex if new_case else alarm['incident'] or uuid.uuid4().hex
                occurrence = 1 if new_case else alarm['occurrences'] + 1
                if new_case:
                    db.execute('UPDATE alarms SET case_id=NULL,erp_status=NULL WHERE key=?', (key,))
                if new_activation:
                    # Acknowledgement applies only to the occurrence an operator saw.
                    db.execute('UPDATE alarms SET acknowledged_by=NULL,acknowledged_at=NULL,acknowledged_occurrence=NULL WHERE key=?', (key,))
                db.execute('UPDATE alarms SET active=1,incident=?,last_event=?,occurrences=? WHERE key=?', (incident, now, occurrence, key))
                self.audit(db, a['source_id'], 'alarm-active', scope, {'rule': rule['id'], 'incident': incident, 'occurrence': occurrence})
                if rule.get('maintenance'):
                    self._enqueue(db, a, rule, incident, occurrence, 'active', now)
        elif value <= rule['clear_below']:
            db.execute('UPDATE alarms SET pending=NULL,active=0 WHERE key=?', (key,))
            if alarm['active']:
                self.audit(db, a['source_id'], 'alarm-cleared', scope, {'incident': alarm['incident']})
                # A display-only alarm must not create an ERP case merely by clearing.
                # Preserve the clear event when a previously enabled rule already queued a case.
                if rule.get('maintenance') or alarm['case_id'] or db.execute(
                        'SELECT 1 FROM outbox WHERE incident=? LIMIT 1', (alarm['incident'],)).fetchone():
                    self._enqueue(db, a, rule, alarm['incident'], alarm['occurrences'], 'cleared', now)
        # Deadband does not build an activation delay, but preserves an active alarm.
        elif not alarm['active']:
            db.execute('UPDATE alarms SET pending=NULL WHERE key=?', (key,))

    def _enqueue(self, db, a, rule, incident, occurrence, condition, now):
        eid = digest([incident, occurrence, condition])
        body = dict(event_id=eid, incident_id=incident, city=a['city'], environment=a['environment'],
            company=a['company_id'], project=a['erp_project'], asset_id=a['asset_id'],
            erp_asset_id=a['erp_asset_id'], rule=rule['id'], response=rule['response'], priority=rule.get('priority', 'medium'),
            engineering_revision=a['engineering_revision'], occurrence=occurrence, condition=condition,
            observed_at=now, evidence=f'/docs/lifecycle/?city={a["city"]}&asset={a["asset_id"]}&environment={a["environment"]}')
        db.execute('INSERT OR IGNORE INTO outbox(id,incident,body,city,environment,asset_id) VALUES(?,?,?,?,?,?)',
                   (eid, incident, json.dumps(body), a['city'], a['environment'], a['asset_id']))

    @staticmethod
    def _filter(city, environment, alias=''):
        clauses, values = [], []
        for column, value in [('city', city), ('environment', environment)]:
            if value is not None:
                clauses.append(f'{alias}{column}=?')
                values.append(identifier(value))
        return ' AND '.join(clauses) or '1=1', values

    @staticmethod
    def _page_args(limit, before):
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError('Page limit must be an integer from 1 to 100')
        if before is not None and (type(before) is not int or not 1 <= before <= 2**63 - 1):
            raise ValueError('Page cursor must be a positive 64-bit integer')

    @staticmethod
    def _readings(db, where, values):
        # One indexed latest-row lookup per configured measurement, in one SQL
        # statement. Old historian rows are not loaded or ranked for every poll.
        return {(r['scope'], r['measurement']): dict(r) for r in db.execute(f"""
            SELECT r.* FROM assets a JOIN json_each(a.body, '$.measurements') m
            JOIN readings r ON r.id=(SELECT id FROM readings
                WHERE scope=a.scope AND measurement=m.key ORDER BY id DESC LIMIT 1)
            WHERE {where}""", values)}

    @staticmethod
    def _asset_view(row, readings, now):
        asset = dict(json.loads(row['body']), lifecycle_state=row['state'],
                     configuration_status=row['configuration_status'], readings={}, alarms=[])
        for name, measurement in asset['measurements'].items():
            latest = readings.get((row['scope'], name))
            reading = dict(latest) if latest else dict(value=None, quality='disconnected',
                source_time=None, received=None, unit=measurement['unit'])
            stale = measurement['stale_seconds']
            if latest and now - min(latest['source_time'], latest['received']) > stale:
                reading['quality'] = 'disconnected' if now - latest['received'] > stale * 3 else 'stale'
            if row['configuration_status'] != 'active':
                reading['quality'] = 'disconnected'
            asset['readings'][name] = reading
        return asset

    def device(self, city, environment, asset_id, now=None):
        """Current active device measurements and alarms; no city/history export."""
        scope = self.scope(city, environment, asset_id)
        now = time.time() if now is None else now
        with self.connect() as db:
            db.execute('BEGIN')
            row = db.execute("SELECT * FROM assets WHERE scope=? AND configuration_status='active'", (scope,)).fetchone()
            if row is None:
                raise ValueError('Unknown active device in this city/environment')
            asset = self._asset_view(row, self._readings(db, 'a.scope=?', [scope]), now)
            asset['alarms'] = [dict(r) for r in db.execute('SELECT * FROM alarms WHERE scope=?', (scope,))]
            return asset

    def _outbox_page(self, db, city, environment, asset_id=None, state=None, limit=100, before=None):
        self._page_args(limit, before)
        where, values = self._filter(city, environment)
        if asset_id is not None:
            where += ' AND asset_id=?'; values.append(identifier(asset_id))
        if state is not None:
            if state not in ('pending', 'delivered'):
                raise ValueError('Unknown outbox state')
            where += ' AND state=?'; values.append(state)
        counts = db.execute(f"SELECT count(*) AS total, coalesce(sum(state='pending'),0) AS pending FROM outbox WHERE {where}", values).fetchone()
        page_where = where + (' AND rowid<?' if before is not None else '')
        rows = [dict(r) for r in db.execute(f"""SELECT rowid AS cursor,id,incident,city,environment,asset_id,
            state,attempts,next_try,error,response FROM outbox WHERE {page_where}
            ORDER BY rowid DESC LIMIT ?""", [*values, *([before] if before is not None else []), limit + 1])]
        return dict(items=rows[:limit], total=counts['total'], pending=counts['pending'],
                    next_before=rows[limit - 1]['cursor'] if len(rows) > limit else None)

    def outbox_page(self, city, environment, **options):
        with self.connect() as db:
            db.execute('BEGIN')
            return self._outbox_page(db, city, environment, **options)

    def evidence_page(self, city, environment, asset_id, limit=20, before=None):
        self._page_args(limit, before)
        scope = self.scope(city, environment, asset_id)
        with self.connect() as db:
            db.execute('BEGIN')
            self.asset(db, scope)
            total = db.execute('SELECT count(*) FROM evidence WHERE scope=?', (scope,)).fetchone()[0]
            rows = [dict(r) for r in db.execute('SELECT rowid AS cursor,* FROM evidence WHERE scope=?' +
                (' AND rowid<?' if before is not None else '') + ' ORDER BY rowid DESC LIMIT ?',
                [scope, *([before] if before is not None else []), limit + 1])]
            return dict(items=rows[:limit], total=total,
                        next_before=rows[limit - 1]['cursor'] if len(rows) > limit else None)

    def snapshot(self, city=None, environment=None, now=None):
        now = time.time() if now is None else now
        where, values = self._filter(city, environment, 'a.')
        with self.connect() as db:
            db.execute('BEGIN')
            rows = db.execute(f'SELECT a.* FROM assets a WHERE {where} ORDER BY scope', values).fetchall()
            readings = self._readings(db, where, values)
            assets = {row['scope']: self._asset_view(row, readings, now) for row in rows}
            for asset in assets.values():
                asset.update(installations=[], evidence=[], commands_audit=[],
                             evidence_page=dict(total=0, next_before=None))
            for table, field, order in [('alarms', 'alarms', 't.key'), ('installations', 'installations', 't.installed')]:
                for row in db.execute(f'SELECT t.* FROM {table} t JOIN assets a ON a.scope=t.scope WHERE {where} ORDER BY {order}', values):
                    assets[row['scope']][field].append(dict(row))
            for table, field in [('evidence', 'evidence'), ('commands', 'commands_audit')]:
                for row in db.execute(f"""SELECT * FROM (SELECT t.rowid AS cursor,t.*,
                    row_number() OVER (PARTITION BY t.scope ORDER BY t.rowid DESC) AS rank,
                    count(*) OVER (PARTITION BY t.scope) AS total
                    FROM {table} t JOIN assets a ON a.scope=t.scope WHERE {where}) WHERE rank<=20
                    ORDER BY scope,cursor DESC""", values):
                    record = dict(row); record.pop('rank'); total = record.pop('total')
                    asset = assets[row['scope']]; asset[field].append(record)
                    if table == 'evidence':
                        asset['evidence_page'] = dict(total=total,
                            next_before=record['cursor'] if total > len(asset[field]) else None)
            queue = self._outbox_page(db, city, environment)
            current = db.execute('SELECT body FROM packages WHERE city=? AND environment=? ORDER BY created DESC LIMIT 1', (city, environment)).fetchone()
            historian = json.loads(current['body'])['historian'] if current else None
            return dict(schema='osr-lifecycle-twin/1', observed_at=now, assets=list(assets.values()),
                        outbox=queue['items'], outbox_page={k:v for k,v in queue.items() if k!='items'}, historian=historian,
                        authority='OSR evidence references; ERP closure and alarm clearance do not grant railway release')

    def acknowledge(self, city, environment, asset, rule, occurrence, actor, now=None):
        scope = self.scope(city, environment, asset)
        if type(occurrence) is not int or occurrence < 1:
            raise ValueError('Alarm occurrence must be a positive integer')
        now = time.time() if now is None else now
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            alarm = db.execute('SELECT * FROM alarms WHERE key=?', (scope + '|' + identifier(rule),)).fetchone()
            if not alarm:
                raise ValueError('Unknown alarm')
            if occurrence != alarm['occurrences']:
                raise ValueError('Alarm occurrence changed; refresh before acknowledging')
            if alarm['acknowledged_by'] is not None:
                return {'acknowledged': True, 'created': False, 'actor': alarm['acknowledged_by'],
                        'occurrence': alarm['acknowledged_occurrence'],
                        'acknowledged_at': alarm['acknowledged_at']}
            db.execute('UPDATE alarms SET acknowledged_by=?,acknowledged_at=?,acknowledged_occurrence=? WHERE key=?',
                       (actor, now, occurrence, alarm['key']))
            self.audit(db, actor, 'alarm-acknowledged', scope, {'rule': rule, 'occurrence': occurrence})
        return {'acknowledged': True, 'created': True, 'actor': actor,
                'occurrence': occurrence, 'acknowledged_at': now}

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
                if a['configuration_status'] != 'active':
                    raise ValueError('Command not enabled for retired asset configuration')
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
                if a['configuration_status'] != 'active':
                    db.execute("UPDATE commands SET state='failed',result='asset retired by supervisory package' WHERE id=?", (row['id'],))
                    self.audit(db, principal, 'command-failed', row['scope'], {'request_id': row['id'], 'reason': 'asset retired'})
                    continue
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
