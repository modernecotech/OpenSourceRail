"""Site-scoped Workbench navigation; no arbitrary parent-origin trust."""
from urllib.parse import urlsplit
import frappe

DEFAULT_ORIGINS = ['http://127.0.0.1:8090', 'http://localhost:8090', 'http://127.0.0.1:4177']


def boot_session(bootinfo):
    origins = frappe.conf.get('osr_workbench_origins', DEFAULT_ORIGINS)
    if not isinstance(origins, list) or not origins:
        frappe.throw('Configure a non-empty list of Workbench origins')
    for origin in origins:
        if not isinstance(origin, str): frappe.throw('Invalid Workbench origin')
        parsed = urlsplit(origin)
        if (parsed.scheme not in {'http', 'https'} or not parsed.hostname or parsed.username or
                parsed.password or parsed.path or parsed.query or parsed.fragment):
            frappe.throw('Workbench origin must have no path or credentials')
    bootinfo.osr_workbench_origins = origins
