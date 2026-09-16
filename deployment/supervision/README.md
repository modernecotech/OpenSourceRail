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
./osr supervision prepare samawah --first-site --first-vehicle --first-plant
./osr supervision prepare mosul --first-site --first-vehicle --first-plant
./osr supervision apply build/supervision/samawah/simulation/package.json
./osr supervision apply build/supervision/mosul/simulation/package.json
./osr supervision preview-fuxa \
  build/supervision/samawah/simulation/package.json \
  build/supervision/mosul/simulation/package.json \
  --output build/supervision/fuxa-import-review.json
./osr supervision import-fuxa \
  build/supervision/samawah/simulation/package.json \
  build/supervision/mosul/simulation/package.json \
  --review build/supervision/fuxa-import-review.json
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
Import is review-bound: the preview records every included city/environment package,
revision, checksum, site, device and view, then lists live devices/views that will
be added, replaced, retained or removed and identifies changes to remaining project
settings such as charts/navigation. Because the current generator has no
separate custom-display input, `reviewed_display_customisations` is explicitly
empty. Move an intentional live edit into a reviewed generator input before import;
otherwise the preview correctly identifies it as a replacement or removal.

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
3. `./osr supervision prepare <slug>` generates every applicable station, depot,
   vehicle, points, declared-crossing and production-method view; `--first-site`
   includes that station's real child switch/plant assets, while `--first-plant`
   can select only the first production asset for a bounded factory pilot. The command
   no longer needs the large compressed operations payload. `./osr supervision
   validate` compiles every real asset register, and the generated
   [catalogue audit](../../docs/operating/readiness.md) records counts and hashes.
4. Review package, devices, source bindings, units, ranges, alarm limits, response
   references and generated screens. Generic limits are **simulation examples**.
5. Extend the private principal city scopes before applying. For an existing
   baseline, run `review-package PACKAGE --output REVIEW`, inspect its exact
   field/category/dependency and affected-record sets, then run
   `apply PACKAGE --expected PREVIOUS_SHA256 --review REVIEW`. The gateway
   regenerates the review inside the apply transaction and rejects changed
   packages, evidence, installations, open cases or pending commands. An
   identical apply does nothing. An omitted simulation position is retained as
   retired history; an installed position cannot be retired automatically and a
   command contract cannot change while a request is pending. Physical mapping
   changes require a separately commissioned migration.
6. Preview the combined set of desired city packages with `preview-fuxa`, review
   its manifest and add/change/remove sets, then supply that exact file to
   `import-fuxa --review`. Any intervening live-project or package change is
   rejected. Import replaces the complete project and privately saves both the
   previous export and applied review first.

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
- A linked commissioned ERP Asset allows a permission-checked maintainer to preview
  parts, city-store availability, technician and expected downtime, then create one
  draft native Asset Repair. ERP completion/stock consumption feeds back to the
  project, but does not close the Issue or alter railway handback state.
- Outbox events persist across restarts, retry with bounded backoff and preserve
  per-incident order. ERP's unique incident key and event hashes protect against
  duplicate requests and lost replies. Reconciliation reads native case status.
- Commands carry request ID, operator identity, parameters, created/expiry times
  and required conditions. Requested/accepted/rejected/completed/failed states are
  recorded separately. The pilot supports simulated facility lighting only. The
  controller checks local enable and bounds; expired requests are never replayed.
- Engineering and commissioning rehearsals are append-only evidence records.
  The native-stack rehearsal replaces the pilot charger serial, proves the removed
  serial remains queryable through `/affected`, and requires a new independent test
  and release. Physical release cannot be granted through this API.

The independent existing OSR assurance records are displayed by Workbench using
its existing authenticated city access. No integration event changes them.

## Prepared change impact

The read-only package review compares a prepared package with the accepted live
city/environment baseline. It lists exact changed paths and classifies design,
asset-topology, embedded-runtime, telemetry, alarm/maintenance, command,
business-execution and operator-display consequences. Existing parent/source
asset IDs, component type, IFC GlobalId, source crates, ERP project/Item/Asset,
installed serials, append-only evidence, open alarm/ERP cases and pending commands
are reused as dependencies rather than copied into a new registry. Workbench's
**Prepared change impact** view adds matching native ERP purchase, receipt and
production feedback when available.

Preview does not mutate the baseline. Apply requires both the expected prior
package hash and the freshly generated review hash, and the audit records both.
Another city/environment is outside the transaction. A component-type
substitution, retirement of a currently installed serial, physical remapping or
pending-command contract change remains blocked for an explicit replacement or
commissioned migration workflow. This is configuration impact control; complete
CAD/BOM dependency graphs, open-order disposition and released-analysis reruns
remain engineering/ERP work.

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

The `integrated-stack` GitHub workflow creates a clean disposable ERPNext site,
imports both pilot baselines, starts the gateway and pinned FUXA release, runs the
native Rust controller bridge and Workbench, then executes the ERP component,
procurement, lifecycle, FUXA, embedded-condition, browser and outage/recovery
checks together. It destroys its evaluation volumes after collecting failure logs.

`node deployment/supervision/tests/verify-outage.mjs` deliberately disconnects the
simulated source, then temporarily stops/restarts the local integration container.
It verifies FUXA's disconnected state and hides cached values on gateway loss.
Use it only against this evaluation deployment. The script restores the simulator
and gateway in its cleanup block.

## Station, vehicle, wayside and factory integration

The simulation source now executes nine existing Rust crates for station energy,
station SCADA, vehicle BMS, auxiliary power, HVAC, condition monitoring, points,
level crossings and fare gates. Use
`prepare CITY --first-site --first-vehicle --first-plant` for the 19-position
Samawah or Mosul pilot: five station views,
four vehicle views, the station's existing switch and nine factory-method views
on the real production-plant identity. Across the catalogue, 9,097 real switch
IDs are reused. Crossing support remains dormant because no tracked city yet has
a `level-crossing` asset; the package builder refuses to invent one. Fare gates
are labelled station aggregates rather than claims about physical gate counts.
See the [native embedded integration contract](../../docs/lifecycle/embedded-integration.md)
for mappings, reproducibility, state lifetime and the controller-to-ERP test.
`simulate` rebuilds the adapter and restarts its user service so source updates
actually take effect. Rebuild/reapply reviewed packages and reimport FUXA views
when changing generic measurement templates; take a backup first.

The factory views are generated from the validated
[`manufacturing-methods.json`](../../design/component-catalogue/catalog/buildable-trainset/manufacturing-methods.json)
rather than a second manually maintained recipe list. They cover the source's
120-product union, nine methods and 30 tooling families, and retain work centre,
crew, cycle, step/hold-point, source and release-boundary metadata. The simulator
defaults to an idle cell. `factory_method`, `factory_cycle_progress_pct`,
`factory_cell_unavailable` and `factory_process_excursion` in the private
`simulator-control.json` are explicit test fixtures; no cure temperature or
performed quality result is invented. Unavailability or quality-hold persistence
can create an ERP Issue. The Workbench lists native Work Orders only when an
immutable reviewed execution mapping joins the method/product identity to its
ERP Item/BOM. A hold does not modify a Work Order, create a Quality Inspection,
accept/reject output or grant manufacturing/railway release.
