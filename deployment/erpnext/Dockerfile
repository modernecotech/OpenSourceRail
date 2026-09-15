FROM frappe/erpnext:v15.121.2@sha256:d2605a65e15be0c5adc943b16fa7cdc445cb4f3f3a9acbeaf3af6915397bc116

RUN bench get-app --branch v15.64.0 --skip-assets https://github.com/frappe/hrms
# The upstream runtime image stores its prebuilt assets outside sites. Seed the
# manifests before a partial build so Frappe/ERPNext bundle mappings survive.
RUN mkdir -p sites/assets && cp -a assets/. sites/assets/ \
    && bench build --app hrms && cp -a sites/assets/. assets/
COPY --chown=frappe:frappe apps/osr_erpnext /home/frappe/frappe-bench/apps/osr_erpnext
RUN env/bin/pip install --no-cache-dir -e apps/osr_erpnext \
    && printf '\nosr_erpnext\n' >> sites/apps.txt \
    && bench build --app osr_erpnext \
    && cp -a sites/assets/. assets/ \
    && env/bin/python -c 'import json; from pathlib import Path; manifest = json.loads(Path("assets/assets.json").read_text()); required = ["desk.bundle.js", "libs.bundle.js", "form.bundle.js", "erpnext.bundle.js", "hrms.bundle.js", "desk.bundle.css"]; missing = [key for key in required if key not in manifest or not Path("sites" + manifest[key]).is_file()]; assert not missing, f"Missing core or installed-app assets: {missing}"'

USER root
COPY configure-nginx.py /tmp/osr-configure-nginx.py
RUN python /tmp/osr-configure-nginx.py && rm /tmp/osr-configure-nginx.py
USER frappe
