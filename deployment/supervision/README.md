# Equipment supervision and lifecycle integration

ERPNext owns business execution; FUXA displays equipment; OSR owns engineering,
controller behaviour and railway assurance. The integration joins their identities
without treating a delivery, alarm clearance or ERP case closure as railway release.

## Run the local pilot

Start the existing ERP stack first (`./osr erp up`). Then:

```sh
./osr supervision init
./osr supervision up
./osr supervision setup-fuxa
./osr supervision connect-erp samawah mosul
./osr supervision prepare samawah --first-site
./osr supervision prepare mosul --first-site
./osr supervision apply build/supervision/samawah/simulation/package.json
./osr supervision apply build/supervision/mosul/simulation/package.json
./osr supervision import-fuxa build/supervision/samawah/simulation/package.json build/supervision/mosul/simulation/package.json
./osr supervision simulate
```

- Workbench lifecycle: <http://127.0.0.1:8090/docs/lifecycle/>
- FUXA: <http://127.0.0.1:1881/home>
- ERPNext: <http://127.0.0.1:8080/app/opensourcerail>
- Integration health: <http://127.0.0.1:8092/health>

`var/supervision/fuxa.json` contains editor (`admin`) and operator (`operator`)
passwords. Private integration tokens are in `var/supervision/integration.json`.
No credentials are included in generated FUXA project exports. The operator cannot
change the project. Workbench reads use a scoped viewer token kept on the server.
All published ports bind to loopback. This is a local deployment; remote operation
requires the organisation's TLS, identity, network and access configuration.

FUXA 1.3.4 and the Python runtime are pinned by image digest. The adapter generates
FUXA's project export format and imports it through `/api/project`, also used by
its UI. It does not modify FUXA's database. Global tag IDs are unique across cities.
FUXA's native connection-status tags hide values when the gateway is stale/offline.

## ERP integration principal

`./osr supervision connect-erp <city> [<city> ...]` reads each city's configured
ERP project, validates the city/project pairing, creates a dedicated Support
Team/Projects User and copies its credentials privately into the gateway config.
It extends the gateway's simulation city scopes and restarts it.
`osr_integration_users` in ERP site config restricts the service principal to those
projects and **simulation**. The service URL is `http://frontend:8080` on the
existing ERP network. Neither account is an ERP administrator.

## Reproduce for another city

1. Use its tracked operations asset register and compact project-twin revision.
   Regenerate the city with `./osr city <slug>` only when those sources are stale.
2. Edit `cities/catalogue/.../<city>/operations/supervision.json`. Omitted fields
   inherit [shared templates](config/generic.json); dictionaries merge and lists
   replace. Set company/project and, optionally, site IDs and equipment bindings.
3. `./osr supervision prepare <slug>` generates every applicable station, depot
   and vehicle equipment view; `--first-site` makes a bounded pilot. The command
   no longer needs the large compressed operations payload. `./osr supervision
   validate` compiles every real asset register, and the generated
   [catalogue audit](../../docs/operating/readiness.md) records counts and hashes.
4. Review package, devices, source bindings, units, ranges, alarm limits, response
   references and generated screens. Generic limits are **simulation examples**.
5. Extend the private principal city scopes before applying. Existing package
   changes require `apply --expected <previous-sha256>`; an identical apply does
   nothing. An omitted simulation equipment position is retained as retired
   history: its pending commands fail and new telemetry/commands are rejected.
   Reintroducing the same reviewed identity reactivates it. Physical mapping
   changes cannot silently overwrite commissioned data.
6. Import the combined set of desired city packages into each FUXA instance.
   Import replaces its project; the CLI saves the previous project first.

`--environment physical` produces a commissioning-required package. The service
rejects telemetry and commands for those uncommissioned bindings. Vendor register
maps, verified limits, real device adapters and OSR operational release must be
supplied before physical activation. No railway or protection command is exposed.

## Data and failure behaviour

- Stable key: **city + environment + planned asset ID**. Design revision, ERP
  project baseline, physical serial, IFC GlobalId and supplier device mapping are
  separate references. Registry history survives revision changes.
- Telemetry: asset/measurement/source IDs, sequence, source UTC timestamp, reception
  time, engineering unit, normalized value and quality. Replay conflicts, unknown
  sources/units, non-finite values and future timestamps are rejected. Stale data
  cannot activate or clear an alarm.
- SQLite is the pilot's **single telemetry historian**, sampled every two seconds,
  retained for seven days; latest values remain marked stale/disconnected. FUXA DAQ
  is disabled. ERP receives actionable events, never the measurement stream.
- Alarm delay, hysteresis and repeat suppression are persisted. One incident maps
  to one native Issue. Clearing the signal preserves the case. A later new fault
  after case closure starts a new incident. Acknowledgement is immutable for one
  occurrence; a fresh activation resets it, and a stale browser cannot
  accidentally acknowledge the newer occurrence. Acknowledgement is separate.
- Outbox events persist across restarts, retry with bounded backoff and preserve
  per-incident order. ERP's unique incident key and event hashes protect against
  duplicate requests and lost replies. Reconciliation reads native case status.
- Commands carry request ID, operator identity, parameters, created/expiry times
  and required conditions. Requested/accepted/rejected/completed/failed states are
  recorded separately. The pilot supports simulated facility lighting only. The
  controller checks local enable and bounds; expired requests are never replayed.
- Engineering and commissioning rehearsals are append-only evidence records.
  Installation replacement keeps the old serial/batch history; `/affected` supports
  batch/serial lookup. Physical release cannot be granted through this API.

The independent existing OSR assurance records are displayed by Workbench using
its existing authenticated city access. No integration event changes them.

## Backup and recovery

```sh
./osr supervision backup
./osr erp backup
```

The first command uses SQLite's consistent backup API, exports the FUXA project and
copies private deployment credentials/settings into a private timestamped folder.
Restore the SQLite backup into the `integration-data` volume with integration
stopped, restore the private settings, then start and import the saved FUXA project.
Recreate its users with `setup-fuxa`; they are declared in private configuration.
The default pilot uses built-in graphics; separately back up the `fuxa-images`
volume if operators add images. FUXA logs are diagnostic, not the command audit;
the authoritative command/event audit is in the integration backup.

Database restore equivalence and pending-event survival are covered by tests.
FUXA export/import and editor/operator permissions are also exercised against the
running pinned version. ERP retains its separate native backup/recovery process.

## Sources

- [FUXA 1.3.4 source](https://github.com/frangoteam/FUXA/tree/v1.3.4)
- [FUXA project import/export](https://github.com/frangoteam/FUXA/blob/v1.3.4/docs/HowTo-save-load-Project.md)
- [Frappe REST API](https://docs.frappe.io/framework/user/en/guides/integration/rest_api)

## Validation commands

```sh
tools/automation/osr-python -m pytest -q tools/automation/tests/test_supervision.py
cargo test -p osr-energy-site --all-targets
npx playwright test tests/frontend/lifecycle.spec.mjs
node deployment/supervision/tests/verify-fuxa.mjs
python3 deployment/supervision/tests/verify-pilot.py
```

`node deployment/supervision/tests/verify-outage.mjs` deliberately disconnects the
simulated source, then temporarily stops/restarts the local integration container.
It verifies FUXA's disconnected state and hides cached values on gateway loss.
Use it only against this evaluation deployment. The script restores the simulator
and gateway in its cleanup block.

## Station and vehicle embedded integration

The simulation source now executes six existing Rust crates for station energy,
station SCADA, vehicle BMS, auxiliary power, HVAC and condition monitoring. Use
`prepare CITY --first-site --first-vehicle` for an eight-position city pilot.
See the [native embedded integration contract](../../docs/lifecycle/embedded-integration.md)
for mappings, reproducibility, state lifetime and the controller-to-ERP test.
`simulate` rebuilds the adapter and restarts its user service so source updates
actually take effect. Rebuild/reapply reviewed packages and reimport FUXA views
when changing generic measurement templates; take a backup first.
