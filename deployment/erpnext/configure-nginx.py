"""Adapt the pinned upstream proxy for a single site on a local published port."""
from pathlib import Path

path = Path("/templates/nginx/frappe.conf.template")
template = path.read_text()
upstream = '''\t\tproxy_set_header Origin $proxy_x_forwarded_proto://${FRAPPE_SITE_NAME_HEADER};
\t\tproxy_set_header Host $host;'''
local = '''\t\t# Validate the browser origin before translating the internal auth address.
\t\tset $osr_socket_origin $http_origin;
\t\tif ($osr_socket_origin = "") {
\t\t\tset $osr_socket_origin "$scheme://$http_host";
\t\t}
\t\tif ($osr_socket_origin != "$scheme://$http_host") {
\t\t\treturn 403;
\t\t}
\t\t# Socket.IO authenticates through this address inside the Compose network.
\t\tproxy_set_header Origin http://frontend:8080;
\t\tproxy_set_header Host frontend:8080;'''
assert template.count(upstream) == 1, "Review the upstream Socket.IO proxy template"
template = template.replace(upstream, local)
path.write_text(template)
headers_path = Path("/etc/nginx/snippets/security_headers.conf")
headers = headers_path.read_text()
framing = 'add_header X-Frame-Options "SAMEORIGIN" always;'
assert headers.count(framing) == 1, "Review upstream frame protection"
headers_path.write_text(headers.replace(framing,
    "add_header Content-Security-Policy \"frame-ancestors 'self' http://127.0.0.1:8090 http://localhost:8090 http://127.0.0.1:4177\" always;"))
