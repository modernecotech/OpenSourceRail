# Baghdad assembly development

This programme enriches source requirements and executes provisional assembly
experiments. Its supported scope is one LV/ventilation cassette, one
replaceable bearing seat, a provisional 1.2 m structural floor bay and an executable cassette interlock. It does not
complete the train, civil works or all remaining component generators.

The input registry separates published supplier/reference facts, repository
planning values and proposed pilot assumptions. Every fact has a source,
locator, unit, scope and non-approved status. Country climate observations do
not establish a site design extreme. Supplier headline limits do not establish
combined performance or an offered railway configuration. Proposed manufacturing
tolerances, loads, stress screens and productivity values are not approved limits.

The 345 pre-existing records retain their identities and architecture boundaries;
246 have the LM3 namespace. The 69 Baghdad reference-part records are separately
allocated, giving 414 scoped records without claiming physical BOM completeness.
Four Baghdad records currently connect to three pilot generators. Remaining
records produce family-specific generator/evaluator work orders; the crosswalk
groups all 414 records by architecture/function and flags duplicate records.

Cassette definitions include a perforated tray, individual rail plates/webs,
mount pads and fasteners, duct walls/feet, eight conductors and jackets, drilled
clamp bars/standoffs, earth hardware and an exact GB-origin Harwin reference
connector. The connector is a coordination envelope with published mass, not a
reconstruction of its internals. Mating/termination geometry, clamp retention,
seals, bond conductors, insulation/derating, vibration and whole-car HVAC remain
open. The software trials test a latching permission interface, not train control.

Bearing-seat studies include drilled plates, guide members, grout, anchor
hardware envelopes, local uniform-bedding/plate-strip and elastic bolt-group
screens, and thermal travel. One revision-bound complete reference-kit reaction
ledger includes the formerly omitted 60,000 kg track-support allocation and all
retained permanent units. Signed bearing and downstream support resultants are
reconciled; the represented seat replaces the prior bearing mass once. Six-car
uniform planning cases remain explicit provisional hypotheses. Axle loads, dynamic interaction, contact,
prying, fatigue, local concrete/anchor resistance, offered bearing configurations
and the fixed/guided/free arrangement still require their own verification.

Candidate revisions cover the actual generated geometry, interfaces, materials
and metadata. A source/runtime-bound SQLite queue deduplicates trials, recovers
sealed results after interrupted database writes, retains partial evidence and
vetoes failed native confirmations. Native checks reopen FCStd, reconcile mass,
CG/inertia and STEP, and screen static solid intersections. They do not verify
moving paths, welds, threads, anchor development or physical performance.

```bash
tools/automation/osr-python tools/automation/design-assemblies.py qualify
tools/automation/osr-python tools/automation/design-assemblies.py run --budget 50
tools/automation/osr-python tools/automation/design-assemblies.py cycle --budget 6
tools/automation/osr-python tools/automation/design-assemblies.py install
tools/automation/osr-python tools/automation/design-assemblies.py status
tools/automation/osr-python tools/automation/design-assemblies.py develop
tools/automation/osr-python tools/automation/design-assemblies.py plan
tools/automation/osr-python tools/automation/design-assemblies.py verify-cycle --budget 6
```

The five-minute timer runs six pending experiments per cycle and retains a
portable local report at `~/.local/state/opensourcerail/assembly-design/latest/`.
The current bounded domain has 48 physical recipes and two software implementations.
After exhaustion it explicitly waits for new requirements or capabilities; it
does not repeat identical trials. A separate hourly capability service assigns
missing Baghdad component work to an isolated developer and a separate critic.
It retains proposed source, declared assumptions, native evidence and the exact
review, with two provider calls per hour and at most two attempts per component.
A known native failure or unavailable tool cannot become a successful research
improvement. Reviewed proposals are not automatically imported into the runner;
independent numerical benchmarks and adapter/interface registration remain
required before a new evaluator becomes trusted research infrastructure. Resource limits are 2 GiB of programme output, a 20 GiB
free-space reserve, 2 GiB service memory and a 15-minute service timeout.

Exports contain exact original receipts/evidence, the requirements and fact
registry, qualification log, candidate CAD, drawings, BOM/process data, unexecuted
QA plans and software tests. Verification compares exported copies and report
metrics with archived originals, including after outer checksums are regenerated.
XY inspection layouts and native previews are explicitly unissued. The initial
repository snapshot is under `docs/design-engine/assembly-design`; subsequent
automatic reports remain local until a reviewed repository publication.

The capability worker reuses the already configured proposal executable/model.
It writes only to an owned sparse Git worktree, checks that protected tracked
source remains unchanged, executes the proposed generator with bounded time and
output, and runs the trusted native-contract checks. A separate read-only critic
reviews exact proposal/source digests. Git worktrees isolate source changes, not
the operating system. All qualification/release flags remain false. The worker
preserves private source/output before deleting reproducible clean checkouts;
failed protected-source edits remain held for inspection. It does not contact
suppliers, send messages, merge code or claim an approved design.

## Full design closure plan

The controlled source is
[`OpenSourceRail_Full_Design_Closure_Plan_2026-10-19.pdf`](../../OpenSourceRail_Full_Design_Closure_Plan_2026-10-19.pdf).
Its 88 deliverables and 13 work packages are tracked in
[`data/closure-plan.json`](data/closure-plan.json). Every engineering exit remains
open. `partial-provisional` in the report describes implemented code and its
limited evidence, not a completed engineering task. Named engineering owners,
independent reviewers and acceptance authority remain unappointed.

The existing programme now carries a named provisional configuration, source and
standards registers, a 414-record family crosswalk, typed component/interface
contracts and dependency invalidation. Door/low-floor/route/charging adoption and
conflicting mass definitions remain explicit holds. IEC 61373:2026 requires an
edition impact review; the lithium-ion scope of IEC 62928 is enforced rather
than transferred to another chemistry.

The cassette supplement uses exact Harwin solder-contact female/male kits,
eight active and two reserved positions, and different-gauge harness halves. It
executes DC power/fault controls, a precharge energy control, air/heat/moisture
balances, a process/removal dependency graph and worst-case tolerance stacks.
The initial guide/connector fit and some airflow scenarios fail. Missing
simultaneous derating, protection coordination, installed access and physical
evidence keep the complete chain out of system acceptance. Assumed fan curves
and circuit disconnects are identified as hypotheses.

The structural pilot includes RHS rails and crossmembers, a drilled floor,
four bolted equipment mounts and a steel test block. Independent analytical/FEM,
mesh, equilibrium, acceleration and support-fixity controls check only the
equivalent longitudinal elastic model. Local floor/joint resistance, buckling,
fatigue, modal transfer and the complete carbody remain unresolved.

The shared integration adapter propagates represented mass, CG and inertia,
power/heat and complete reference reactions, with exact source/configuration
identities and child-failure vetoes. It references existing spatial/flexible
physics adapters. A full, converged six-car passage has not been executed for
these new pilot revisions.

The local weekly `osr-assembly-verification.timer` re-runs the complete test
profile, including native checks, before running a cycle. A required native
skip prevents qualification. Fast adverse tests also run in the existing
design-twin CI workflow. Each export includes its actual test log and receipt.

External evidence can be checked with `design-assemblies.py ingest --record ...
--calibration ... --review ... --trust ... --expected ... --evidence-root ...`.
The operator supplies pinned public keys and authorised roles in a separate
trust configuration. Measurement, calibration and independent applicable review
are Ed25519-signed envelopes; raw files, instrument/fixture revisions, calibrated
ranges, method edition, uncertainty and exact serial/interface revision must
agree. No private keys or invented laboratory records are provided. Successful
authentication does not issue a manufacturing or railway release.

Three unissued RFQ/test data requests identify fixture/calibration requirements,
raw-data and holdout outputs, scope and data rights. Laboratory availability,
commercial terms and supplier qualification require actual responses. No
outreach has been performed.

## Baghdad desktop investigations

The site supplement uses actual open data, with retained samples and hashes:
WorldPop 2026 native population counts; separately scoped GHSL 2025 and WorldPop
2020 comparisons; SRTM-derived terrain; ESA WorldCover 2021 land/water samples;
a fresh 7,045-feature OSM snapshot; and existing proposed routes, roads and
building extracts. It produces a detailed GeoJSON/SVG map, 80 context cells,
route-level water/infrastructure exposure, land-use investigation candidates and
250/500 m chainage investigation scenarios. These are planning quantities, not
an adopted borehole programme or a declaration that land is available.

Context estimates cover 44.1–44.6°E, 33.1–33.5°N. Population corridor estimates
use a different retained extent, 44.2–44.75°E, 33.05–33.5°N, and count each native
pixel once in the network union. They measure proximity to concept lines, not
station walking access or ridership. The ±25 m line-sampling bound, separate
pixel-footprint sensitivity, unknown route accuracy and population-model
uncertainty remain explicit. Different model vintages are not measured growth.

WorldCover lacks the requested western strip. Road/building coverage also has
limits. OSM way water polygons are incomplete and omit multipolygon relations;
river centrelines support investigation priorities but do not establish bank
positions or flood risk. Terrain is not a surveyed ground profile. Groundwater,
design flood level, soil resistance, parcel ownership and buried utility
clearance remain unknown. The estimates can scope surveys, investigations and
supplier enquiries; physical design must retain the corresponding holds.

`site_context.verify`, `site_catchments.verify` and `site_screening.snapshot`
verify or recompute the retained estimates. `site_bundle` adds their raw inputs
to the existing portable publication, which independently checks displayed
quantities and rebuilds the map outside the original GIS paths. Online GIS
extraction is separate from offline reporting and requires Shapely/pyproj;
raster cropping additionally needs rasterio. Ordinary report replay downloads
no data.
