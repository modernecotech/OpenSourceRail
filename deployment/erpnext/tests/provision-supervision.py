"""Local provisioning: a dedicated integration principal scoped to evaluation projects."""
import json
import os
import secrets
import frappe
from frappe.installer import update_site_config

os.chdir('/home/frappe/frappe-bench/sites')
frappe.init(site='osr.localhost'); frappe.connect()
frappe.flags.mute_emails = True
try:
    email = 'osr-supervision@example.invalid'
    if not frappe.db.exists('User', email):
        frappe.get_doc(dict(doctype='User', email=email, first_name='OSR supervision integration', enabled=1,
            user_type='System User', send_welcome_email=0,
            roles=[dict(role='Support Team'), dict(role='Projects User')])).insert()
    user = frappe.get_doc('User', email)
    if not user.api_key:
        user.api_key = secrets.token_hex(16)
        user.api_secret = secrets.token_hex(24)
        user.save()
    policy = dict(frappe.conf.get('osr_integration_users') or {})
    policy[email] = dict(cities=['samawah', 'mosul'], environments=['simulation'], projects=['PROJ-0001', 'PROJ-0002'])
    update_site_config('osr_integration_users', policy)
    for project in policy[email]['projects']:
        frappe.share.add('Project', project, email, read=1, notify=0)
    frappe.db.commit()
    with open('/tmp/osr-integration-credentials.json', 'w') as stream:
        json.dump(dict(url='http://frontend:8080', key=user.api_key, secret=user.get_password('api_secret')), stream)
    os.chmod('/tmp/osr-integration-credentials.json', 0o600)
    print('Dedicated simulation-only ERP integration principal provisioned')
finally:
    frappe.destroy()
