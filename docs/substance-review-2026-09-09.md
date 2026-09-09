# Engineering and delivery substance review — 2026-09-09

This review follows the repository access, persistence and provenance repairs.
It examines what the models actually demonstrate, rather than counting files,
drawings, tests or completed solver runs. The drainage and electrical-screen software defects below have now been
repaired and their evidence regenerated. Physical connection exceedances and
the other engineering and delivery gaps remain open.

The repository has useful reproducible planning models and explicitly open
release registers. The corrected electrical screen exposes insufficient declared connection
capacity. Delivery
cashflow, depot scope and lifecycle cost also need stronger connections to the
physical quantities and operating plan.

## 1. Roof-drainage input and validation repairs completed

**Priority: high. Repository model defects repaired; site design remains open.**

The original [SWMM generator](../engineering/analysis/stations/station_systems.py)
placed width in the imperviousness column. The standard branch represented a
10% impervious roof with a 1 m flow width and 100% slope. Its sparse five-minute
rainfall records supplied only 12.5 mm, half the declared 25 mm storm. The
correct column order and rainfall format are documented in the
[EPA SWMM manual](https://www.epa.gov/system/files/documents/2022-04/swmm-users-manual-version-5.2.pdf).

The investigation also found zero pipe fall. SWMM substituted a minimum
elevation drop; correcting only the roof and storm left a distorted
kinematic-wave peak. The repaired reference model declares a **0.4 m fall over
40 m**, uses dynamic-wave routing, and reduces the runoff/hydraulic steps to
10 s / 1 s. This gradient is an explicit planning assumption requiring survey,
not an approved site level.

All seven regenerated variants pass independent checks for 25 mm rainfall,
zero infiltration, rainfall-volume/runoff balance, C=1 roof peak, conduit peak,
continuity, no flooding and inlet depth. Continuity is captured after SWMM
finalizes the simulation. Runoff-volume error is below **0.02%** across the
family. The standard-station result changes from **5.62 L/s** to **37.77 L/s**
aggregate branch flow, matching the **37.77 L/s** C=1 rational calculation.
The old comparison used C=0.95 despite the intended zero-loss roof.

The [station report](../engineering/analysis/stations/screening-summary.md)
records the assumptions and observed quantities. New solver regressions reject
incorrect roof columns, missing rainfall intervals and the former flat-pipe
kinematic-wave setup; additional cases independently check rainfall × area
and intensity × area at three roof sizes.

**Still required:** local rainfall/return period, surveyed levels, header and
municipal-network capacity, tailwater, blockage and exceedance design. The
model repair does not close those deployment requirements.

## 2. Electrical connection gates repaired; capacity exceedances remain open

**Priority: high. Software omission repaired; physical design correction required.**

The [microgrid model](../engineering/analysis/city_microgrid.py) applies a
97% grid rectifier efficiency. A 500 kW charger requires **515.46 kW AC** before
transformer losses. The original model enlarged the transformer as necessary
and declared a pass on solver convergence without checking the connection.
The initial all-city arithmetic identified **3,976 sites across 262 cities**
with insufficient declared import for the grid-only case.

Each site now records solved HV import/export, its separate declared limits,
and the exceedance in kW. The test includes transformer and converter losses,
with only 0.001 kW numerical tolerance. `solver_passed` records convergence;
`passed` additionally requires no connection, transformer, voltage or climate
findings. The CLI fails a design with unresolved findings, and batch resume
cannot treat it as successful. README tables and engineering plots show the
design result and finding count separately from solver convergence.

The catalogue rerun confirms **3,976 sites across 262 cities** exceed declared
connections. All 266 solvers converge; only four electrical design screens pass.
The [Samawah result](../cities/catalogue/west-asia/Iraq/Samawah/engineering/energy/summary.json)
now fails on **seven grid-only connections** requiring **519.02 kW** each at the
HV connection against a declared 500 kW. Mosul has 26 grid-only exceedances.
Regression tests check import, export, converter and transformer losses,
nonconvergence, and the distinction between design failure and convergence.
All-city provenance and pass consistency are also checked.

**Still required:** resolve each exceedance through a controlled connection
upgrade or charger/schedule change, then reconcile timetable, equipment and
cost. No connection capacity or operating demand has been silently changed.
The common ideal 33 kV bus does not demonstrate feeder routes, upstream network
capacity, protection or utility approval. The stipulated storage snapshot does
not establish state of charge or endurance.

## 3. Reconcile depot energy scope across the physical and operating models

**Priority: high. Conflicting reference definitions.**

The [depot template](../lib/templates/depots.toml) specifies 600 kWp PV and
2,000 kWh storage for `main-heavy`. The [energy-site template](../lib/templates/energy-sites.toml)
specifies **5,000 kWp and 40,000 kWh** for `depot-main`. Samawah's emitted
scenario uses the latter. Its depot CAPEX remains the fixed **$8M** unit,
with a **$250k** depot-terminal charging interface allowance in the
[cost template](../lib/templates/capex-costs.toml).

This does not prove that the total allowance is insufficient. It establishes
that there is no clear, shared quantity contract demonstrating which depot
PV/storage configuration the physical layout, procurement and fixed allowance
represent. A 20-fold storage difference must be a controlled configuration
decision, not an implicit difference between templates.

**Amendments:** introduce one depot energy configuration consumed by the
scenario, site layout, BOM and cost model; distinguish baseline equipment from
capacity additions; price additions from explicit kW/kWh quantities; account
for their footprints, installation and replacement scope.

## 4. Prove that the distributed stabling plan fits the railway

**Priority: high. Missing operating/physical feasibility evidence.**

Reduced depot cost and footprint depend on healthy trains stabling at powered
passenger stations. [RFC 0014](rfcs/0014-depot-design-standard.md) describes
simultaneous morning starts from those locations. However, the
[simulator fleet initializer](../crates/osr-sim/src/sim.rs) distributes trains
round-robin over configured dispatch points, without a stabling-track capacity
allocation.

Samawah has **108 trainsets**, with fleets of **53, 28 and 27**, each assigned
to just **two dispatch points**. The first line consequently initializes
27 and 26 trainsets at its two endpoints. The design includes 17 concurrent
main-depot workshop bays; workshop capacity is not evidence of adequate
overnight parking. The simulator's abstract awaiting-dispatch queue does not
establish that these trains fit on passenger tracks or can reach their morning
starting locations without conflicts.

**Additions:** a track-by-track overnight allocation with usable lengths,
train lengths, clearance points, charger sharing and access; evening run-in,
morning run-out and failed-train recovery schedules; maintenance possessions;
and an occupancy-constrained simulation. Reassess depot savings if additional
sidings or secure service locations are required.

## 5. Make cashflow follow supplier terms and the working calendar

**Priority: high for delivery planning. Model integration gap.**

The [project-twin generator](../tools/automation/project_twin.py) publishes
COTS terms of **30% order / 60% delivery / 10% acceptance** and a 120-day lead
time. Its cashflow calculation does not consume purchase orders. It instead
allocates budget contracts using **10% mobilisation / 55% progress / 30%
completion / 5% retention**, with mobilisation 30 days before task start.
Thus the timing and amount of supplier deposits need not appear in the
published monthly requirement, even though total cash reconciles to CAPEX.

Budget allocation is weighted by task duration rather than derived from each
task's priced quantity. The schedule is labelled in working days, while
cashflow maps offsets to months using `floor(day / 30) + 1`. The six-day
working week in the manufacturing template is not applied by that mapping.
Samawah's example has 1,012 programme working days and 38 cashflow buckets;
these are not yet an approved calendar-month financing schedule.

**Amendments:** derive procurement cash events from quantities, supplier terms
and order dates; allocate labour and other residual budget separately to avoid
double counting; introduce an explicit project start date and work calendars;
map supplier lead times and payment dates consistently. Add a test in which an
early supplier deposit changes the appropriate month's cash requirement.

## 6. Turn the battery renewal allowance into a lifecycle calculation

**Priority: medium. Unsupported sensitivity relationship.**

The [finance generator](../tools/automation/generate-city-finance.py) describes
a **12-year** train-battery renewal cycle, but computes rolling-stock
maintenance as **4% of fleet acquisition cost**. The 12-year value is output
metadata; it does not drive a replacement schedule, reserve calculation or
discounted cash event. Stationary renewals are similarly described as included
in a general fixed-asset maintenance percentage.

This is a transparent planning allowance, not demonstrated lifetime cost.
Changing battery life, utilisation, replacement price or end-of-life capacity
does not currently produce the corresponding renewal cashflow. A cheaper
factory-gate vehicle also reduces the percentage-based maintenance allowance
without proving a proportional reduction in physical maintenance needs.

**Additions:** separate onboard and stationary battery inventories; calendar
and throughput life assumptions with sources; replacement cost, labour and
disposal; capacity degradation in the service-energy case; and explicit
renewal/reserve cashflows. Reconcile the resulting totals with ordinary
maintenance to prevent double counting.

## 7. Distinguish catalogue completeness from pilot evidence completeness

**Priority: medium. Publication status repaired; evidence coverage remains open.**

Before the repair refresh, **264 city manifests** retained a finance-summary
hash that no longer matched their source. Those same 264 cities lacked the
field-evidence brief required by the current package generator, while their
old manifests still reported a passed package. The general repository health
check applies the full package-manifest checks only to Samawah and Mosul.

The repair regenerated all twin/operations outputs and their enclosing manifests.
That first refresh produced **2 complete packages and 264 incomplete packages**.
After the electrical correction, the two pilots also have failed energy
summaries: the current full-package result is **0 complete and 266 incomplete**.
Missing evidence remains listed in each manifest; the catalogue now displays
this distinction alongside its separate topology results. Completeness does
not validate the modelling assumptions identified elsewhere in this review.

The follow-up refresh also found **264 GIS summaries** with stale scenario
hashes. Those GIS packages and all 266 engineering plot sets were regenerated.
It then found **264 native-simulation reports** referencing both older scenarios
and an older validator. These retained reports require full resilience reruns;
their old passing flags are not current operating evidence. The two pilots
retain current native-simulation provenance.

The package generator now checks analysis provenance and records each stale
source separately. Strict README generation still rejects stale evidence.
An explicit `--allow-stale-evidence` audit mode can publish a warning and mark
retained passing rows **unverified** while preserving failed results. That mode
was used for the 264 affected catalogue pages; it does not alter solver reports
or close package gates.

**Amendments:** define explicit catalogue-screening and pilot-evidence scopes;
validate the current scope and generator for every city; extend the catalogue
with resilience/cross-check coverage. The catalogue now exposes each city's
electrical result, number of sites exceeding connection limits, and full-package
status with links to the detailed findings. The current
technical inspection count must not imply equal evidence maturity for all
266 models.

## 8. Extend station analysis from repeatable routes to actual passenger loads

**Priority: medium. Acknowledged gap with a concrete next model.**

The [passenger screen](../engineering/analysis/stations/station_systems.py)
uses 80 people for normal/degraded cases and 120 for egress, with each platform
route simulated independently. The elevated/interchange cases reuse the same
straight-route result where platform length matches. Stairs, lifts, gates,
merging flows and passengers arriving from trains are excluded.

The [rolling-stock profiles](../lib/templates/rolling-stock.toml) span nominal
train capacities up to 720 and crush capacities up to 960. A 120-person route
screen cannot establish evacuation performance for a loaded train plus waiting
passengers. The current report discloses this limitation, but the next useful
addition is a coupled demand/train/station case rather than another identical
route run.

**Additions:** station-specific arrival and interchange demand; simultaneous
train unloading; bottlenecks and platform occupancy; degraded routes and
assisted evacuation; and deployment-specific acceptance criteria. Keep route
benchmark results separate from station-capacity or evacuation acceptance.

## 9. Schedule the shared national factory across city programmes

**Priority: medium. Portfolio delivery assumption not yet enforced.**

The [capital template](../lib/templates/capex-costs.toml) costs one shared
national plant sized to the largest single-city fleet, assuming phased reuse.
Each [city twin](../tools/automation/project_twin.py) independently receives
the default rolling-stock plant and fabrication resource capacities. There is
no country-level resource schedule coordinating concurrent city programmes.

**Additions:** country programme start windows, shared plant/mould/tooling
capacity, supplier bottlenecks, training ramp-up and maintenance downtime;
allocate city orders against that resource pool; compare phased delivery with
expanded-plant scenarios. Until then, the national factory cost assumption and
individual city schedules should be presented as separate planning cases.

## Work order for the next iteration

1. Resolve the connection-capacity findings exposed by the repaired electrical
   screen, including their timetable and cost consequences. The drainage and
   grid-limit software repairs and evidence regeneration are complete.
2. Close the depot energy quantity contract and physical stabling allocation.
3. Connect procurement, calendars, renewal events and shared factory resources
   to the delivery and financial model.
4. Extend passenger/station and junction-conflict cases using controlled demand
   and operating inputs.

Supplier configuration, production drawings, mass/CG measurement, physical
testing, site survey, HIL and independent approvals remain the external gates
already identified in the [roadmap](ROADMAP.md). This review adds specific
repository-side work; it does not replace or satisfy those external gates.

## Review method and limits

The review traced source templates, generators, emitted scenarios and tracked
reports; checked all-city grid-limit arithmetic and manifest coverage; and
replayed the drainage deck with the installed solver using temporary files.
The EPA manual was consulted for the SWMM input definition. It did not include
supplier quotations, field surveys, a complete structural reassessment, a
physical test campaign or an independent railway safety assessment. The original diagnostic replays were followed by the controlled generator
repairs, regression tests and regenerated evidence described above. Full
repository acceptance remains failed while Samawah and Mosul have electrical
findings and therefore failed full-package manifests; those gates were not
weakened to restore a green result.
