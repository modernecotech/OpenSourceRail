"""Derived research eligibility for exact revisions; immutable results stay intact.

Analytical candidates may be explored while a first confirmation is pending.
A known mandatory failure excludes them; unavailable/interrupted confirmation
holds them. Neither analytical nor confirmed eligibility confers release.
"""
import json
from pathlib import Path
import sqlite3
import time

from engineering.twin_workflow import core
from . import tasks

MANDATORY = ("native_geometry", "numerical_confirmation", "numerical_robustness")


def initialise(store):
    store.db.executescript("""
        CREATE INDEX IF NOT EXISTS confirmation_child ON jobs(baseline,json_extract(task,'$.parameters.child'));
        CREATE TABLE IF NOT EXISTS integration_dispositions (
            key TEXT PRIMARY KEY, baseline TEXT NOT NULL, state TEXT NOT NULL,
            reasons TEXT NOT NULL, evidence_sha256 TEXT NOT NULL, updated REAL NOT NULL);
    """)
    store.db.commit()


class Resolver:
    def __init__(self, store, baseline):
        self.store, self.baseline = store, baseline
        self.rows = {r['key']: r for r in store.db.execute('SELECT * FROM jobs WHERE baseline=?', (baseline,))}
        self.observations = {r['key']: r for r in store.db.execute('SELECT * FROM observations WHERE baseline=?', (baseline,))}
        self.confirmations = {}
        self.cache = {}
        for row in self.rows.values():
            task = json.loads(row['task'])
            if task.get('kind', '').endswith('-confirmation'):
                self.confirmations.setdefault(task['parameters']['child'], []).append(row)

    def dependencies(self, keys):
        values = [self.state(key) for key in keys]
        state = 'failed' if any(v['state']=='failed' for v in values) else 'hold' if any(v['state']!='eligible' for v in values) else 'eligible'
        return dict(state=state, eligible=state=='eligible', children=dict(zip(keys, values)))

    def state(self, key):
        if key in self.cache:
            return self.cache[key]
        row = self.rows.get(key)
        result = dict(state='hold', eligible=False, reasons=[], confirmations=[], analytical_only=True)
        # Also breaks malformed cyclic dependencies conservatively.
        self.cache[key] = result
        if row is None or row['status']!='completed':
            result['reasons'].append('exact candidate is unavailable or unfinished')
            return result
        task = json.loads(row['task'])
        try:
            passed = self.store.result(row)['study_pass']
        except (ValueError, OSError, KeyError, TypeError) as exc:
            result['reasons'].append('candidate evidence unreadable: '+str(exc))
            return result
        if not passed:
            result.update(state='failed', reasons=['original study checks failed'])
            return result
        states = []
        for confirmation in self.confirmations.get(key, []):
            record = dict(key=confirmation['key'], receipt_sha256=confirmation['receipt_sha'], levels={})
            if confirmation['status']!='completed':
                # A first pending experiment is not a known engineering failure.
                state = 'hold' if confirmation['error'] or confirmation['status']=='error' else 'pending'
                record.update(state=state, reason=confirmation['error'] or 'confirmation pending')
            else:
                try:
                    checked = self.store.result(confirmation)
                    levels = checked.get('verification', {}).get('levels', {})
                    record['levels'] = {level: levels.get(level, {}).get('state', 'not_run') for level in MANDATORY}
                    values = list(record['levels'].values())
                    state = 'failed' if 'failed' in values else 'passed' if all(v=='passed' for v in values) and checked['study_pass'] else 'hold'
                    record.update(state=state, reason='mandatory exact-child confirmation '+state)
                except (ValueError, OSError, KeyError, TypeError) as exc:
                    record.update(state='hold', reason='confirmation evidence unreadable: '+str(exc))
            states.append(record['state'])
            result['confirmations'].append(record)
            if record['state'] in {'failed', 'hold'}:
                result['reasons'].append(record['reason'])
        if task.get('kind', '').startswith('integration-') and task['parameters'].get('children'):
            dependencies = self.dependencies(task['parameters']['children'])
            states.append(dependencies['state'])
            result['dependencies'] = dependencies
            if not dependencies['eligible']:
                result['reasons'].append('dependent evidence changed; integration requires re-evaluation with eligible revisions')
            revision=task['parameters'].get('evidence_revision')
            if revision is not None and revision!=core.digest(dependencies):
                states.append('hold')
                result['reasons'].append('integration evidence revision superseded; re-evaluate against current receipts')
        state = 'failed' if 'failed' in states else 'hold' if 'hold' in states else 'eligible'
        result.update(state=state, eligible=state=='eligible', analytical_only=task.get('kind') in tasks.CONFIRMABLE and 'passed' not in states)
        return result


def champions(store, baseline, resolver=None):
    """Choose the best eligible alternative, including formerly dominated ones."""
    resolver = resolver or Resolver(store, baseline)
    groups = {}
    for row in sorted(resolver.observations.values(), key=lambda r: (r['mass'] if r['mass'] is not None else float('inf'),
            r['effort'] if r['effort'] is not None else float('inf'), r['key'])):
        if row['kind'] not in (tasks.CONFIRMABLE|{'integration-coupling','integration-protocol'}):
            continue
        group = row['kind'], row['context']
        if row['study_pass'] and row['mass'] is not None and group not in groups and resolver.state(row['key'])['eligible']:
            groups[group] = row
    selected = []
    for (kind, context), observation in sorted(groups.items()):
        record = store.db.execute('SELECT * FROM champions WHERE baseline=? AND key=? ORDER BY id DESC LIMIT 1',
            (baseline, observation['key'])).fetchone()
        item = dict(record) if record else dict(id=None, baseline=baseline, kind=kind, context=context,
            key=observation['key'], predecessor=None, reason='Next eligible research alternative',
            parent_checks='{}', created=observation['finished'])
        item['parent_checks'] = json.loads(item['parent_checks'])
        if record is None:
            checked=store.result(resolver.rows[observation['key']])
            item['parent_checks']=dict(checks=checked.get('checks',{}),children=checked.get('children',[]),level=observation['level'])
        item['eligibility'] = resolver.state(observation['key'])
        selected.append(item)
    return selected


def refresh(store, baseline):
    """Persist descendant disposition and versioned fallback selections atomically."""
    resolver = Resolver(store, baseline)
    from .research import dominates
    peers={}
    for observation in resolver.observations.values():
        if observation['study_pass'] and observation['mass'] is not None and resolver.state(observation['key'])['eligible']:
            peers.setdefault((observation['kind'],observation['context'],observation['concept']),[]).append(observation)
    frontier={r['key'] for group in peers.values() for r in group if not any(dominates(p,r) for p in group)}
    for observation in resolver.observations.values():
        value=int(observation['key'] in frontier)
        if observation['pareto']!=value:
            store.db.execute('UPDATE observations SET pareto=? WHERE key=?',(value,observation['key']))
    for row in resolver.rows.values():
        task = json.loads(row['task'])
        if not task.get('kind', '').startswith('integration-') or not task['parameters'].get('children'):
            continue
        state = resolver.dependencies(task['parameters']['children'])
        disposition = 'superseded' if state['state']=='failed' else 'hold' if not state['eligible'] else 'eligible'
        revision=task['parameters'].get('evidence_revision')
        if state['eligible'] and revision is not None and revision!=core.digest(state):
            disposition='superseded'
        digest = core.digest(state)
        prior = store.db.execute('SELECT evidence_sha256 FROM integration_dispositions WHERE key=?', (row['key'],)).fetchone()
        if prior is None or prior[0]!=digest:
            store.db.execute('INSERT OR REPLACE INTO integration_dispositions VALUES(?,?,?,?,?,?)',
                (row['key'], baseline, disposition, json.dumps(state), digest, time.time()))
    for champion in champions(store, baseline, resolver):
        prior = store.db.execute('SELECT * FROM champions WHERE baseline=? AND kind=? AND context=? ORDER BY id DESC LIMIT 1',
            (baseline, champion['kind'], champion['context'])).fetchone()
        if prior and prior['key']!=champion['key']:
            store.db.execute('INSERT INTO champions(baseline,kind,context,key,predecessor,reason,parent_checks,created) VALUES(?,?,?,?,?,?,?,?)',
                (baseline, champion['kind'], champion['context'], champion['key'], prior['key'],
                 'Evidence eligibility changed; select next eligible research alternative', json.dumps(champion['parent_checks']), time.time()))


def live_dependencies(envelope):
    """Recheck live evidence in workers, even if their dispatch envelope is older."""
    workspace = envelope.get('evidence_workspace')
    if workspace is None:
        for dependency in envelope['dependencies']:
            workspace = next((p for p in Path(dependency['folder']).parents if (p/'queue.sqlite').is_file()), None)
            if workspace:
                break
    if workspace is None:
        return dict(state='hold', eligible=False, reason='live evidence ledger unavailable')
    workspace = Path(workspace).resolve()
    db = sqlite3.connect((workspace/'queue.sqlite').as_uri()+'?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    try:
        from .service import Store
        from types import SimpleNamespace
        db.execute('BEGIN')
        store = SimpleNamespace(db=db, workspace=workspace, result=lambda row: Store.result(None, row))
        return Resolver(store, envelope['baseline_sha256']).dependencies([d['key'] for d in envelope['dependencies']])
    finally:
        db.close()
