# Baghdad assembly development

This programme enriches source requirements and executes provisional assembly
experiments. Its supported scope includes an LV/ventilation cassette,
replaceable bearing seat, a provisional 1.2 m structural floor bay, connected
whole-carbody and representative civil-bay geometry, and an executable cassette
interlock. Connected geometry expands the available packaging/manufacturing
definition; it does not complete the train's engineering or physical acceptance.

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
tools/automation/osr-python tools/automation/design-assemblies.py run --budget 64
tools/automation/osr-python tools/automation/design-assemblies.py cycle --budget 6
tools/automation/osr-python tools/automation/design-assemblies.py install
tools/automation/osr-python tools/automation/design-assemblies.py status
tools/automation/osr-python tools/automation/design-assemblies.py develop
tools/automation/osr-python tools/automation/design-assemblies.py plan
tools/automation/osr-python tools/automation/design-assemblies.py verify-cycle --budget 6
```

The five-minute timer runs six pending experiments per cycle and retains a
portable local report at `~/.local/state/opensourcerail/assembly-design/latest/`.
The current bounded domain has 90 physical recipes and two software implementations.
Once these finish, the same runner executes a bounded companion study: twelve
detailed cassette variants, twenty-seven civil cap-cage variants and the same
fifty-four structural variants. The expanded structural grammar includes two
crossmembers nearer the equipment feet; it counts both feet on each loaded
strip and independently checks the added support beams. Replayed structural variants are not additional
unique designs. A registered companion also compares 172 aluminium/GFRP panel
hypotheses and confirms six explicitly scoped owned-section CAD exhibits.
Two further registered companions compare six complete carbody stock recipes
and nine connected civil-bay recipes. They retain all alternatives and known
failures, rather than counting repeated runs as new designs. Carbody studies use
the controlled 18.5 m length, with historical transverse dimensions and a new
1.0 m floor datum explicitly unadopted. Their actual door/window voids, frame,
floor, cladding, glazing and door-leaf envelopes have individual part identities.
Missing bogie/crash details, sheet fasteners, service equipment and qualified
welds remain visible. The original sill-only independent beam diagnostic remains
available. A connected 3D Timoshenko frame adapter additionally uses the actual
RHS members and explicit eccentric rigid-joint assumptions, with refinement,
equilibrium, independent element controls and adverse loading. Its original
slender alternatives fail the elastic research filters and remain rejected.
The nominal S355 stress and length/1000 displacement filters are explicitly
provisional comparisons, not adopted railway design acceptance. Sheets add mass
without unverified shell stiffness; joint/local-buckling, crash/fatigue and
physical correlation remain open even for a passing elastic frame screen.

The selected carbody also has a finite six-axis connection-stiffness study.
Distinct member ends remain separate even at coincident splice coordinates;
eccentric connector arms preserve force/moment transfer. Stiffness factors are
unmeasured hypotheses derived dimensionally from the participating sections,
not offered or qualified weld properties. The high-stiffness limit is compared
with the rigid baseline, while softer cases retain their displacements, joint
movements, simultaneous resultants and any failed provisional filters.

Declared sill and roof splices have revision-bound, simultaneous member-cut
demands from every retained rigid-frame load case. A separate offcut coupon
compares full represented penetration with deliberate half/three-quarter
penetration defects. Its gap filler solids do not specify a production bevel,
backing, weld procedure, access method, strength or fatigue class. Partial
penetration cases are adverse controls. [TWI's joint-design guidance](https://www.twi-global.com/technical-knowledge/job-knowledge/design-part-4-093)
explains the importance of root access, backing and fatigue; exact source cards
remain in `data/carbody-connection-sources.json`. [Tata Steel UK's Celsius page](https://www.tatasteeluk.com/construction/products/tube/structural-hollow-sections/celsius)
provides a procurement reference. Exact stock sizes, corner geometry, heat,
production location and British manufacture still need confirmation.

The connected civil model preserves its source material/allowance ledger,
redistributes track plinth material into gauge-spaced rail supports and adds
physical walkway/service support frames. Its crane checks reject some large
lifts under the same provisional chart. Concrete reinforcement/prestress,
embedded anchorage, real ground, rail fastening and temporary-works resistance
remain mandatory open requirements.

`studies/systems/index.html` provides an offline English/Arabic explorer with
searchable part/material/process schedules, native-derived images, original
CAD/STEP/IFC downloads and a construction-stage slider. The fast slider displays
projected outer envelopes: holes and depth occlusion are not represented. The
assembly videos use retained native triangles at final coordinates, appearing in
the explicit dependency order. These are construction-stage illustrations;
they do not prove insertion motion, collisions or stage strength. The separate
cassette fixture video retains its existing rigid insertion/withdrawal scope.

Full installed panels, formed roofs and qualification remain open. It confirms the best analytical alternatives in native CAD,
retaining failed confirmations and trying up to three alternatives per family.
Tool unavailability holds the family instead of spending this fallback budget.
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
Portable assembly publication has a 64 MiB cap, including retained site inputs
and the panel, carbody and civil CAD/IFC/image/video exhibits. The companion's
share is bounded at 32 MiB, including full frame load-case evidence for every
alternative. Raw evidence is
preserved; no result gains engineering acceptance through publication.

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

The tracker now consumes the controlled `data/closure-evidence.json` index and
separately pinned `data/closure-trust.json` keys. Original digital-author and
independent digital-review signatures bind each task's required scope,
component/interface revisions, engineering inputs, drawings, analyses and
inspection/process artifacts. Missing, failed or stale evidence cannot close a
gate. Original referenced bytes are included in portable publications. Historical
records are retained; a new valid revision can replace stale coverage, while a
known failure on the current revision remains a veto. Digital specification,
physical-record coverage and manufacturing release are reported separately.
The current index is empty, so no accepted completion is invented.
When a physical unit and adopted method exist, its serial, component/interface
revision and method/standard applicability belong in that controlled task's
`physical_expected` field in `data/closure-plan.json`. A submission cannot set
its own applicability; original measurement/calibration and independent review
envelopes still pass the existing authenticated-record adapter.

`data/equipment-layout.json` is the shared provisional instance layout: eight
complete LV/ventilation cassettes and three refrigeration boundaries per car.
The detailed mass/inertia, pigtail/conductor quantities, known fan/LV model
power, thermal counts and electrical group mappings derive from the same
definition. All48cassettes are counted. Refrigeration mass, trunk routes, actual
vehicle packaging, maintenance access and costs remain unknown; gross additions
earn no removal credit and do not revise the adopted planning train mass.

Site catchment replay uses the existing numerical-reproduction utility with a
local whitelist for sub-micrometre sampling diagnostics. Report self-hashes,
source/geometry bytes, population values, integer counts and decisions remain
exact. These replay tolerances do not relax engineering acceptance limits.

The cap companion retains six round bent-link/hook/coupler schedules, including
mandrel radii, hook arcs/tails, congestion checks and manufacturing/inspection
steps. They are excluded from cap selection while curved native geometry,
development, anchorage, coupler ratings and resistance remain unconfirmed.

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

Supplemental cassette failures propagate into its parent result and downstream
integration eligibility. A failed candidate can still have valid native geometry
for inspection. Such evidence is published under `diagnostics/`, with explicit
exclusion from shortlists; its CAD image is not a successful design selection.

The structural pilot includes RHS rails and crossmembers, a drilled floor,
four bolted equipment mounts and a steel test block. Independent analytical/FEM,
mesh, equilibrium, acceleration and support-fixity controls check only the
equivalent longitudinal elastic model. Local floor/joint resistance, buckling,
fatigue, modal transfer and the complete carbody remain unresolved.

### Additional closure-plan executions

`design_studies.py` extends the existing epoch, qualification and publication
paths. Its source-bound `studies/` report adds:

- A detailed cassette and proposed host fixture, with routed conductors,
  solder-cup envelopes, cover, seals, bond, guides, retention and actual rigid
  insertion/removal/tool-envelope checks. Original failed guide/connector
  assumptions remain in the original evidence. Replacement checks identify
  exactly which revised interfaces supersede them. Carrier/mount loads include
  the newly represented mass.
- Structural mount bearing washers and adaptive bolt stacks, local floor/joint
  checks, proposed weld details, modal/refinement controls and manufacturing
  instructions. Thin floors fail the new local screens. A 16 mm floor is a heavy
  research sensitivity; it does not establish an optimal complete carbody.
- Actual round bars, welded links, embedded lift/jacking parts and spacers in
  a hollow pier-cap segment. Concrete is not counted again in this cage model.
  The retained complete cap mass and unresolved allowance remain visible.
  Construction checks use the actual asymmetric permanent mass distribution.
- Hierarchical six-car electrical nets and isolation/bond/signal boundaries,
  twelve coupled HVAC/battery/controller duty cases, independent RC and heat
  balances, electrical cooling demand, and separate cabin/battery cooling
  failures. Synthetic equipment maps remain uncalibrated. A complementary
  cassette campaign retains I²t, electrothermal, CO₂ and map sensitivities.
- Native FreeCAD/STEP/IFC, unissued inspection layouts, exact part/joint/QA
  handoffs, revision-specific unissued prototype test requests, native previews,
  a rigid fixture-motion video and an animation of executed thermal traces.
  These are distinct from a force/contact simulation or an installed vehicle.

All 88 PDF tasks remain tracked individually. Missing full carbody/bogie,
refrigeration/CFD, complete prestress/reinforcement, ground, coupled train passage,
physical correlation, production and authority exits are not closed by these
software executions. Named engineering reviewers, offered equipment data,
manufactured samples and calibrated test results remain external work.

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
