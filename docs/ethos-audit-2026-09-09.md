# Audit of today's corrections against the OpenSourceRail design

Reviewed revision: `b5e3b301a`. Scope: all 13 commits dated 9 September 2026,
from `3515839c1` through `b5e3b301a`, compared with `5d5f25b43`.
This audit examines changed source logic, templates, tests and report consumers;
generated city results were checked by aggregation and against their inputs.
It is not a new physical design or a complete verification of every subsystem.

The controlling rationale is in [Architecture §2 and D7](ARCHITECTURE.md),
[RFC 0002](rfcs/0002-energy-sizing.md),
[RFC 0021](rfcs/0021-battery-traction.md), and the user's operating instructions:
solar generation on railway land, local stationary storage, brief train top-ups,
grid backup for residual demand, repeatable components, domestic design and
manufacturing capability, two revenue sets per selected station, overflow
storage on each train's own line, and no interline depot connections.

## Repairs completed

The findings below describe the audited revision. The subsequent repair:

- accepts station storage/source capability with any positive installed charging
  rating; grid import and a 150 kW minimum are no longer prerequisites;
- caps low-C top-ups by installed station and shared cabinet/source limits;
- checks current battery/source availability during charger reachability, while
  retaining onboard reserve checks and metering actual shared charging;
- separates grid-only contingency findings from solar/storage snapshot results,
  includes charger DC/DC efficiency, and prevents battery discharge into a PV
  surplus; full operating-energy validation remains explicitly open;
- retains historical stabling experiments and their hashes as diagnostics,
  including source drift, without using them to accept or reject the selected
  line-local hybrid configuration;
- permits a deployment-specific mobilisation scope, role IDs, management systems,
  work packages and evidence requirements, validating their references and
  dependencies rather than fixed job titles or arbitrary document counts;
- checks package-status honesty and selected-evidence provenance in repository
  health, while leaving incomplete physical deployment packages visible.

All 266 energy snapshots were regenerated. The same 3,976 grid-only connection
exceedances remain visible; all 266 coordinated solar/storage snapshots pass.
Samawah, Uíge, Quelimane and Edéa pass new continuous two-day hybrid replays.
The Rust simulator/controller suites pass 127 tests with one ignored test.
Focused regressions cover off-grid lower-power stabling, battery-backed grid
outages versus empty storage/failed pads, diagnostic package scope and a small
workshop's tailored mobilisation record. City equipment and fleet inputs are
unchanged. Native converter/transformer energy-boundary reconciliation and
complete solar/storage endurance remain modelling limitations, not mandates
for grid expansion.

## Confirmed drift at the audited revision

| Finding | What changed or was misinterpreted | Required correction |
|---|---|---|
| Grid-only contingency became a general design failure | Today's electrical connection gates feed both snapshots into `passed = solver_passed and not findings`. The grid-only case explicitly sets PV and battery discharge to zero. The review then recommended connection upgrades from those results. | Retain connection measurements, distinguish contingency requirements from normal solar/storage operation, and evaluate the actual buffered duty. The blanket upgrade recommendation is withdrawn. |
| Station stabling requires a grid connection | Today's Python candidate selector and Rust loader require `grid_import_kw > 0`; the new Python regression even treats removal of grid import as removal of all power. The template's pre-existing `requires_grid_connection = true` was propagated into executable logic. | Station eligibility must use the declared charging/storage capability. A grid connection cannot be a universal prerequisite for a solar/storage station. |
| Grid outage is treated as charger outage | Today's `can_reach_stabling_charger` rejects a destination when `grid_disabled_at(next)` is true, regardless of the station battery. The energy subsystem itself can still deliver battery energy during a grid outage. | Evaluate usable charging energy and equipment availability separately from grid status, preserving onboard reserve and deterministic allocation. Do not promise future battery energy without accounting for competing train demand. |
| Superseded station-only experiments still block the adopted plan's package | The package generator adds every present stabling screen to `required`, then treats any `passed: false` as a package failure. Samawah's passing hybrid replay coexists with three failed station-only/redistribution experiments in `failed_summaries`. | Separate historical diagnostics from acceptance of the selected operating configuration. A rejected experiment must not become a requirement to enlarge stations or alter the adopted station/depot split. |

Sources:
[electrical generator](../engineering/analysis/city_microgrid.py),
[candidate selector](../design/city-generation/src/osr_scenario/stabling.py),
[native loader](../crates/osr-sim/src/scenario_file.rs),
[reachability logic](../crates/osr-sim/src/sim.rs),
[candidate tests](../design/city-generation/tests/test_station_stabling.py),
[package generator](../tools/automation/generate-city-package-manifest.py),
[Samawah package](../cities/catalogue/west-asia/Iraq/Samawah/package-manifest.json).

## Defaults that must not become universal requirements

- **150 kW stabling eligibility:** the new selectors turn the existing low-C
  top-up rate into a hard minimum installed rating. A target charging rate is
  not by itself evidence that a lower-rated station cannot meet its overnight
  duty. This needs an energy/time check, without inventing a replacement rate.
- **Depot size:** today's quantity reconciliation carries the already-existing
  5,000 kWp / 40,000 kWh main-depot scenario into the physical scope register.
  This removed conflicting quantities; it did not prove that every deployment
  needs that equipment. The area and cost differences are conditional on those
  retained inputs. They must not drive a larger central depot by default.
- **Fixed organisational template:** the new mobilisation validator locks
  thirteen role IDs, eleven management-system IDs and eighteen work packages,
  with minimum counts of documents. Accountable responsibilities and actual
  inspection evidence support domestic capability. Fixed job titles, committee
  structures and document counts need deployment tailoring; they are not
  universal requirements for independently adopting a small subsystem. This
  validator currently checks the reference template, not train dispatch. It
  does not establish that thirteen separate executives must be hired.
- **Reference drainage levels:** correcting SWMM columns and rainfall totals
  was valid. The added 0.4 m pipe fall over 40 m is explicitly a planning
  assumption, not a measured site correction or mandatory civil layout.

Sources: [depot quantity model](../design/component-catalogue/src/osr_mech/depot/energy.py),
[depot scope](../tools/automation/generate-depot-scope.py),
[mobilisation validator](../tools/automation/validate-owner-builder-operator-mobilisation.py),
[drainage model](../engineering/analysis/stations/station_systems.py).

## Corrections that remain consistent with the project

| Change group | Assessment |
|---|---|
| Local Ops Core persistence, revision conflicts, latest-inspection/approval checks, private-file protection and visible failed saves | Keep. They protect accountable local records using the existing SQLite/browser stack. The loopback restriction covers unauthenticated Workbench mutation routes; it does not introduce a cloud dependency. |
| SWMM rainfall, imperviousness and mass-balance repairs | Keep the arithmetic/input fixes and independent checks. Preserve the disclosed planning boundary for levels, rainfall and outfall. |
| Converter/transformer loss measurements and separate import/export limits | Keep the measurements. Correct their operating interpretation and reconcile the separate DC/DC loss. |
| Depot quantity source consolidation | Keep one quantity contract with explicit site overrides. It must remain subordinate to verified distributed operating needs. |
| Two station homes, reserve inventory, continuous battery/position state, same-line home returns and station launch priority | Keep. They implement the user's operating model with explicit deterministic rules. Yard geometry and reserve activation remain incomplete. |
| Final removal of interline depot assignments | Keep. The current allocator uses an existing powered service location on the train's own line and assigns no additional heavy workshop to the overflow storage locations. |
| Source hashes, stale-result labels and repeatability tests | Keep provenance checks. Correct which evidence is applicable before aggregating pass/fail; a hash cannot validate a wrong requirement. |
| Local production data, inspection plans and actual measurement fields | Keep. These make domestic fabrication inspectable and reproducible. Blank records must remain blank until work is done; supplier-exact bought-in interfaces do not require foreign turnkey delivery. |
| Cashflow/calendar, battery renewal, passenger demand and shared-factory scheduling findings | Retain as model-integration gaps. They do not prescribe new rolling stock, enterprise software, interline tracks or imported management systems. |

The active architecture and conservative pilot signalling profile were not
changed by these 13 commits. This audit does not attribute those earlier
decisions to today's corrections or remove physical safety evidence merely
because it is also needed by other railway designs.

## Rechecked power figures

All 266 energy reports match their current scenario and electrical-generator
hashes. They contain 9,328 sites, with 16 distinct combinations of the electrical
inputs used by this snapshot model.

| Existing model result | Verified result |
|---|---:|
| Sites exceeding import limits with PV and storage disabled | 3,976 across 262 cities |
| Those flagged sites with stationary storage installed | 3,976 |
| Connection exceedances with the existing coordinated daylight dispatch | 0 across 266 cities |
| Samawah exceedances in the grid-only contingency | 7 |
| Mosul exceedances in the grid-only contingency | 26 |

The coordinated case stipulates 60% PV nameplate and 50% battery discharge
rating. These are existing model inputs, not a newly proposed operating policy
or a measured state of charge. Its passing snapshot does not prove endurance.

Each flagged Samawah station has 500 kWh gross stationary storage, 500 kW
maximum battery discharge, 300 kWp PV and a 500 kW grid-import limit. The
existing snapshot calculates 519.020 kW import with solar/storage disabled,
versus 73.213 kW under its coordinated dispatch. Calling these installations
"grid-only sites" was incorrect.

The snapshot omits the configured 98% train-charger DC/DC loss. Holding the
existing transformer ratings and dispatch fractions fixed, applying that loss
changes those two figures to 529.647 kW and 83.748 kW respectively. Replaying
all sixteen electrical configurations with that correction leaves the counts
unchanged: 3,976 grid-only exceedances, zero coordinated-daylight exceedances.
These are conditional calculations, not a revised equipment specification.

For the station battery alone, 500 kW of source discharge for 60 seconds uses
8.333 kWh and delivers about 8.167 kWh at 98% charger efficiency. This is
consistent with the RFC's approximately 8 kWh top-up. Two contacts share the
cabinet/source budget; neither receives an independent 500 kW allowance.

The native simulator includes charger efficiency but does not separately
apply the electrical screen's rectifier and transformer losses. Its controller
uses PV/storage before residual grid import; grid-to-storage refill is not
implemented. That absence is not a reason to add routine grid charging by
default. Reconcile the energy boundaries with the solar/storage architecture.

The retained Samawah 48-hour-30-minute hybrid run reports 128.400 MWh station
PV generation, 254.418 MWh grid import and 345.252 MWh delivered from sites to
trains. Initial station storage is 29.000 MWh; at the end all nineteen ordinary
station batteries are effectively empty while main-depot storage is at 84.24%.
These are outputs of the existing model, not new grid requirements. They show
that the current replay cannot establish the intended solar/storage energy
balance. Its passing stabling result only establishes its declared home and
morning-start checks. The raw JSON hash matches the
[tracked hybrid report](../cities/catalogue/west-asia/Iraq/Samawah/engineering/stabling/hybrid-cycle-screen.json).
Its duration field is 174,601 seconds, including the final sampled second.

The architecture also includes generation along the railway right-of-way.
The city energy screen consumes declared site PV values; it does not calculate
additional generation from route length. Additional ROW energy must be traced
to declared site inputs and physical quantities before it can be credited.
This audit adds no assumed PV acreage, grid duty, station battery or depot.

## Audit coverage and change status

| Today's commits | Subject reviewed |
|---|---|
| `3515839c1` | Mobilisation records, exact role/system/work-package validation, template versus deployment scope |
| `aae98e42c`, `5205c40d2` | Civil/trainset inspection plans, manufacturing records and per-part production data |
| `a1248699b` | Portal integrity/access fixes, drainage, electrical checks, provenance and CI |
| `2b5038b72` | Depot energy quantity contract, conditional area/cost scope and regenerated reports |
| `7d999e075`, `565f7d978` | Station stabling candidates, native holding, charging eligibility and allocations |
| `255b99148`, `596e9d92a`, `614bfe96c` | Continuous cycles, reserve roles, morning coverage and charger reachability |
| `482adf174`, `53ebc6136`, `b5e3b301a` | Two-train capacity, depot storage, actual home returns, line independence and repeatability |

No city design/scenario TOML files changed across this commit range. Today's
review therefore did not install larger grids, add solar arrays or increase
the retained city fleet inputs. The drift is in requirements, software gates
and interpretation; those can still steer later design decisions incorrectly.

The written review, runtime gates, candidate selector, package aggregation and
mobilisation validator have now been repaired as described above. Historical
experiments retain their original fail results and source hashes; current
selected evidence was regenerated using the repaired software.

Checks during this audit: catalogue energy/source aggregation, pandapower
replay of the sixteen independent electrical configurations, raw hybrid-output
hash verification, and 19 filtered simulator energy/stabling tests passed.
The audit exposed a candidate test that expected solar/storage stations without
grid import to be rejected. That expectation has been replaced with regressions
accepting stored-energy operation and rejecting sites without usable capability.
