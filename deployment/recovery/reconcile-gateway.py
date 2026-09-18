"""Executed only inside an isolated restored gateway, with CONFIG passed on stdin."""
import json
from urllib.parse import urlencode
from osr_integration.server import request_json, deliver
from osr_integration.store import Store

store = Store('/data/integration.sqlite')
config = dict(CONFIG['erp'], url='http://frontend:8080')
headers = {'Authorization': 'token ' + config['key'] + ':' + config['secret']}
with store.connect() as db:
    cases = [r[0] for r in db.execute('SELECT DISTINCT case_id FROM alarms WHERE case_id IS NOT NULL')]
    event = db.execute("SELECT * FROM outbox WHERE state='delivered' ORDER BY rowid DESC LIMIT 1").fetchone()
    pending = [(r['id'], r['next_try']) for r in db.execute("SELECT id,next_try FROM outbox WHERE state='pending'")]
for case in cases:
    result = request_json(config['url'] + '/api/method/osr_erpnext.integration.case_status?' + urlencode({'issue': case}), headers=headers)['message']
    assert result['issue'] == case
assert event is not None, 'A previously delivered maintenance event is required for lost-reply recovery'
expected = json.loads(event['response'])['issue']
with store.connect() as db:
    # Simulate a lost HTTP reply after ERP committed, using the restored event's
    # original identity and body. Defer unrelated queued events for this check.
    db.execute("UPDATE outbox SET next_try=1e30 WHERE state='pending'")
    db.execute("UPDATE outbox SET state='pending',next_try=0,response=NULL WHERE id=?", (event['id'],))
try:
    deliver(store, config)
    with store.connect() as db:
        after = db.execute('SELECT state,response FROM outbox WHERE id=?', (event['id'],)).fetchone()
        result = json.loads(after['response'] or '{}')
        assert after['state'] == 'delivered' and result['issue'] == expected and result['duplicate'] is True
finally:
    with store.connect() as db:
        db.executemany('UPDATE outbox SET next_try=? WHERE id=?', [(due, identity) for identity, due in pending])
print(json.dumps(dict(linked_cases_verified=len(cases), original_pending_events=len(pending),
    lost_reply_replayed=True, original_issue_reused=True, duplicate_acknowledged=True)))
