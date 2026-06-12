# OSR Operations Portal

Static browser portal for city-level operations data:

- OSR Ops Core work orders, inspection evidence, defects/NCR, and audit
  trail stored locally in the browser.
- Construction QA gates and asset-level QA actions.
- Maintenance schedule expanded to trainsets, stations, track sections,
  switches, structures, energy sites, signalling/comms nodes, depots,
  and production-plant tools.
- Asset register with stable ids.
- Launch/status panels for existing OCC, simulator, CBM, AFC, historian,
  and QA/maintenance tooling.

The simplified operating model is documented in
[`ops-core.md`](ops-core.md).

## Generate Data

```bash
python3 scripts/generate-qa-maintenance-data.py
```

The default input is the generated Samawah design and scenario:

- `designs/west-asia/Iraq/Samawah/design.toml`
- `designs/west-asia/Iraq/Samawah/samawah.toml`

Outputs land in `docs/operations-portal/data/`:

- `samawah-operations.json`
- `samawah-assets.csv`
- `samawah-maintenance-schedule.csv`
- `samawah-qa-register.csv`

## Run With SQLite

Serve the repository root and persist Ops Core work orders, inspections,
defects, and audit events to SQLite:

```bash
python3 scripts/ops-core-server.py --port 8008
```

The server creates the database and schema automatically if they do not
exist. The default database path is:

```text
var/ops-core.sqlite3
```

Then open:

```text
http://127.0.0.1:8008/docs/operations-portal/
```

## Static Fallback

The portal can still run as a static site:

```bash
python3 -m http.server 8008
```

In that mode the Ops Core tab falls back to browser local storage. Use
the SQLite server for real operations, shared consoles, backup, or handover
evidence.

## Reconcile Local Records

If a console was used in static/local mode before SQLite was available,
open the portal through `ops-core-server.py` and use **Storage
Reconciliation** in the Ops Core tab. It compares SQLite with the
browser-local fallback records and can merge local-only records into
SQLite while keeping the newest record when ids conflict.

Open:

```text
http://127.0.0.1:8008/docs/operations-portal/
```
