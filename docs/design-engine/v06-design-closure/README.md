# v0.6 design closure

[Vehicle manufacturing-document coverage draft](vehicle-document-coverage.json)

[Three candidate-matched bogie/coupler source-stock drawings](controlled-stock-drawings-run-01/README.md)

[Door-system inventory and assembly-gap audit](door-subassembly-audit-01/README.md)

[Compact-drive current-source regeneration and delivery holds](compact-drive-delivery-audit-01/README.md)

[Samawah Chinese-bulk vs project make/buy costing packet](samawah-china-supply-cost-04/analysis.md)

[Compact-drive corridor attempt and retained evidence](compact-drive-corridor/README.md)

[Installed-vehicle review and compact-drive geometry results](installed-vehicle-review.md)

[Compact-drive split-lane support-family trials and independent review](compact-drive-support-family/README.md)

[Native GIS source-only import prototype and remaining gate work](native-gis-source-only-prototype.md)

[Run07 native GIS readiness audit](native-gis-run07-readiness.md)

[Current run07 disk and memory preflight](native-gis-run07-preflight-20261110.json)

[Post-cleanup run07 resource preflight](native-gis-run07-preflight-20261110-post-cleanup.json)

[Latest post-cleanup disk and memory sample (not execution authorization)](native-gis-resource-preflight-20261110-012922Z.json)

[Samawah historical recalculation](samawah-city-recalculation.md) and its [current-source body/map recalculation](samawah-city-recalculation-current-source.md), with the [corrected source-bound candidate cost bridge](samawah-candidate-cost-bridge-current-source-attempt-03/README.md) and [fourteen-scope cost audit](samawah-fourteen-scope-cost-audit.md)

[Samawah acceleration sensitivity](samawah-acceleration-sensitivity.md)

[Samawah close-station consolidation study](samawah-station-consolidation.md)

[Samawah per-line demand and whole-city cost sensitivity](samawah-line-demand-sensitivity.md)

[Erratum for the sealed all-city audit packet](all-city-audit-errata.md)

The machine-readable gate ledger is [status.json](status.json). Run
`python3 tools/verify-v06-release-closure.py` to check source-bound evidence
and release readiness. It currently reports seven open/partial gates; software
packaging must remain withheld. The verifier checks ledger completeness and
hash integrity, not the engineering meaning of a closure claim.

This is a supplementary, source-linked audit. It does not modify the frozen
reconciled-pilot publication packet. The audit checks controlled references in
that packet's delivery mapping; “missing” does not mean a repository-wide
search. It records the currently held document coverage and does not authorize
manufacturing or ERP release.

Regenerate the report from the repository root with:

```bash
python3 tools/vehicle_document_coverage.py
```

## Release gate status

The v0.6-series release remains withheld until the required digital design and
integration work below is complete. The closure campaign includes the six
candidate-integration gates plus an all-city outline reconciliation gate,
reflecting the requirement to preserve and update the complete city catalogue.
This is a software/design release gate;
physical qualification and operating approval remain separate gates and are
not implied by closure of this work.

| Required work | Current state | Evidence / remaining closure |
| --- | --- | --- |
| Installed vehicle | Open | The detailed 9f6d research candidate still lacks complete installed mass, verified supplier-fit interfaces, measured or verified installed inertia, tool/removal paths and downstream force/civil consequences. Five child geometry configurations have been screened, including two corrected split-lane support variants; all remain on HOLD with thousands of nominal/interface findings unresolved, and no matched journey/civil study closes the parent. The LED, inter-car, coupler and gangway audit finds no verified articulation envelope or full installed service fit. The original 9f6d archive has now been replayed as a corrected child evaluation: physical candidate `9f6d2230…` is unchanged, evaluation `a7a9ee09…` corrects all 24 door-motion vectors, and the frozen parent remains unchanged. This corrects evaluation data only; the geometry screen is still HOLD and supplier fit, installed mass and downstream loads remain open. A separate current-bundle installation run for source body 907da… corrects the same coordinate representation for its distinct candidate 17ce. The six-car passive-wheel development reference in `engineering/development-baseline.toml` remains unchanged. See the [split-lane support-family record](compact-drive-support-family/README.md), [vehicle subassembly audit](vehicle-services-coupler-gangway-audit.md), [9f6d door-motion correction](door-motion-vector-fix-9f6d/README.md) and [907da door-motion correction](door-motion-vector-fix-01/README.md). |
| Controlled research documents | Open | The supplementary audit of the retained 668-part delivery map finds 41 assemblies with 82 missing assembly-document slots and 4,676 missing part-document slots; all delivery document references are null. Three source-bound gross-stock SVGs now cover a bogie seat blank, bolster RHS blank and coupler clevis blank, but they have no finished geometry, inspection limits or process times and are not controlled part documents. The lighting, flexible inter-car services, coupler and gangway parts also lack controlled drawings, inspection limits and complete assembly evidence. Whole-vehicle document coverage and manufacturing release remain open. |
| Mapped corridors | Open | Baghdad's revised 205 m maximum-deviation geometry pass is still on the older candidate and has no candidate-specific service or price. Samawah has a five-line, 57.873 km quantity and conditional fleet outline bound to the current-source package-07 body; 0.4/0.6/0.8 m/s² acceleration hypotheses remain separate calculations. A new current-source midpoint alternative merges one 79.977 m line-1 marker pair, preserves route length, reduces markers from 26 to 25 and line-1's kinematic request from 2,041.8 to 1,985.3 seconds, and removes one 120 m platform-envelope definition failure. Base fleet and counted vehicle BOM/process subtotal are unchanged; high fleet falls from 88 to 87. It is unselected, with station access, transfer paths, catchment and site suitability unverified; the alternate has no complete city scope totals, installed CAPEX or NPV. Force/braking/grade and detailed civil loads remain unknown. The earlier fourteen-scope China-bulk/project make-buy sensitivity belongs to physical candidate `756a6887…` / body `9489e4f2…`. The current `9f37c5d8…` city / `75075df9…` body has only a candidate-linked body BOM/process subtotal plus five quantity-matched Class C infrastructure-rate fragments; no complete scope totals, installed CAPEX or NPV. See the [current-source station alternative](samawah-station-consolidation-current-source-attempt-03/README.md), [corrected current-source cost bridge](samawah-candidate-cost-bridge-current-source-attempt-03/README.md) and [current calculation report](samawah-city-recalculation-current-source.md). |
| Native GIS return path | Open | The source now has a single `reprice --refreshed-output` CLI path that verifies the retained edit/request, runs the bounded city job, then exports and verifies a study-bound RustGIS project. Synthetic CLI and importer tests pass (29 total). No fresh native edit → city recalculation → export has been run on this source epoch. The latest post-cleanup resource sample narrowly passes the 8 GiB disk reserve, but run07 remains source-stale and unadmitted; no current-source run08 plan, supervisor, independent review or authorization exists. The gate stays open pending a separately reviewed current-source round trip. See the [CLI refresh-loop audit](native-gis-cli-refresh-loop.md), [source-only importer prototype](native-gis-source-only-prototype.md), and [run07 readiness audit](native-gis-run07-readiness.md). |
| Candidate business lifecycle | Open | A sealed delivery proposal exists for the 9f6d body and is identity-matched to that body. The distinct 75075 compact-drive child cannot inherit it and was correctly refused as a mixed identity; it still needs its own canonical downstream bundle. The 9f6d proposal has no complete controlled document set/review pack or native lifecycle evidence. See the [candidate lifecycle audit](../v06-business-lifecycle-audit/README.md). |
| Unified Workbench | Partial | A source-bound view covers the reconciled 1.5 km pilot, with its own candidate identity. It does not yet cover the closure campaign's full city-brief-to-compatible-alternatives path, same-candidate journey/cost/delivery, drawing/BOM/manufacturing review or reconciled downloadable dossier. See [`campaigns/v06-design-integration-closure.toml`](../../../campaigns/v06-design-integration-closure.toml). |
| All-city outline reconciliation | Open | The evaluator accepts exact per-line demand inputs, and a source-bound five-line Samawah sensitivity now propagates those inputs through fleet and fourteen-scope costs. Its 1,200 pphpd perturbations are planning sensitivities, not surveyed demand. The published 266-city catalogue still uses the shared 4,000 pphpd / 200 s study control and transferred reference rates; city forecasts, final alignments, China-volume versus local-manufacture cases and same-candidate recomputation across the catalogue remain open. See the [Samawah sensitivity](samawah-line-demand-sensitivity.md). |

The all-city audit confirmed the catalogue and v0.4 front-door field coverage,
not the correctness of local demand, rates or physical alignments. The
mapped-corridor and native-GIS execution artifacts are retained under the
private, source-bound run record. Their limitations and identities must be
carried into any new plan. A geometry pass is not an operating route, and a
UI upload alone would not close the GIS round-trip gate. The refreshed CLI
workflow is documented separately; the complete native execution remains
unrun on the current source epoch.

### Bounded vehicle stock-drawing packet

Three A3 research SVGs have now been generated from exact source-stock
geometry for body candidate `9f6d2230…`, engineering revision `dfb48ca3…`,
and its identity-matched delivery proposal. The packet records all source and
output hashes, the command/resource limits, and the execution boundary. It is
explicitly a gross-stock geometry draft: the source marks all three finished
geometries unverified, and no tolerances, mating interfaces, inspection limits,
or measured routing times were invented. The generator consequently reports
zero documented part IDs and leaves the controlled-document gate open. See
the [packet and individual SVGs](controlled-stock-drawings-run-01/README.md).

### Vehicle services, couplers and articulation

The 9f6d body proposal has counted LED lighting, five inter-car couplers,
five gangways and flexible electrical services, with allowance-based mass and
direct-cost rows. It does not yet have verified LED loads, rated/flex-tested
inter-car wiring, a moving articulation envelope, complete SolidCraft/FEM
subassemblies, or controlled manufacturing and inspection documents. The
[source-pinned subassembly audit](vehicle-services-coupler-gangway-audit.md)
records its bounded BOM totals and exact closure work.

### All-city baseline audit

The read-only audit was bound to closure commit
`ebeb3b769a9b416180c64124debc1f23317ca277`. It found 266 city outlines,
1,565 lines, 13,580 station-table rows, 14 cost scopes and priced energy cases
for all 266 cities. The v0.4 front-door categories—maps, line/service, energy,
capital/funding, local-evidence and regeneration headings—are present in all
266 city entries. The audit checked 5,586 declared payload hashes (492,192,548
bytes) and found no manifest identity/hash failures.

Those are coverage and integrity results, not proof that the estimates are
locally accurate. All 1,565 lines share the same 4,000 passengers/hour/direction,
200-second headway and 276 normal places/train study controls; all-city local
rates are `transferred-reference-estimates`. The city studies remain
resource-envelope outlines, not executable schedules or dated calendars.
All 266 are linked to reference vehicle candidate
`756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3` and body
`9489e4f2666fd3b3c73232c86df3f12adf42a5531eb27373834cf3fecb1a3117`; none is
bound to the detailed `9f6d…` research body. No supplier quote, surveyed city
demand, site geotechnics or physical acceptance is implied.

Audit anchors: city-dossier manifest
`a9337870a1a5db059a65b2b083011d66ec1ee56f69f2c0cec76f53c172443893`, dossier
index `8661b6456bb4931fa0f67e6060eec6e37be5738fc50eca092523a381fa74b1ab`,
city-atlas manifest
`6f814ccc64a572921aece16a219eb231fbf8ecadfb453a3b92742200956d4c8c`, outline
manifest `f53a8b924834679b3937ad4a2da24bdb89b65c26ee5861ae6c65b77986d2e694`,
and ordered city-manifest-set digest
`a6f85d8f4ee021261962db872ca30bdb458ce6f0885840a8288276800384c402`.

## Research images

The Samawah acceleration sensitivity keeps the 0.4 m/s² reference control and
evaluates 0.6 and 0.8 m/s² as unselected hypotheses. The larger values raise
the calculated inertial force and power terms; no available drive map or
achieved-acceleration evidence is present. See the [separate calculation note](samawah-acceleration-sensitivity.md).

The [root README](../../../README.md#models-from-cad-and-analysis)
already includes renderings from the SolidCraft and FieldCraft engineering
work: vehicle and bogie assemblies, launch shuttle and coupling, viaduct
assembly and a FieldCraft displacement result, plus manufacturable component
details. Those images support inspection of the research models; they are not
manufacturing drawings or qualification evidence.

The [current-source Samawah station-consolidation alternative](samawah-station-consolidation-current-source-attempt-03/README.md)
recalculates the close 79.977 m stop pair using the current compact-drive body
and preserves the mapped route. Its result is a planning screen only: it reduces
one marker-envelope definition failure, while access, catchment, transfer paths,
site feasibility and full corridor cost remain open. Attempt 02 is retained with
an explicit warning because its manifest omitted nested input snapshots.

A stop-preserving [route screen from the unmerged map](samawah-alignment-straightening-current-source-attempt-06/README.md) tests 25, 50 and 100 m simplification tolerances. It shortens the map from 57.873 km to 54.518–53.993 km, but retains the close-stop platform-envelope hold (56.552 m gap). A separate [chained station-merge plus route screen](samawah-merged-alignment-screen-current-source-attempt-03/README.md) starts from the midpoint alternative with 25 markers and no envelope-screen failure, then tests the same tolerances: 54.514/54.173/53.963 km, with conditional total fleet requests 39/57/84, 39/56/84 and 39/56/84. Its unpriced guideway screen reduces reference 20 m beam units 5,794→5,456/5,422/5,402, shared bent positions 2,902→2,733/2,716/2,706, running rail 231,493→218,055/216,693/215,853 m and fastening sets 385,825→363,427/361,157/359,756. The combined options are unselected. Their four shared evaluator holds are absent exact-body propulsion/braking/thermal/charging/service evidence, unevaluated civil and station assemblies, unknown full costs/NPV, and an unresolved roster for the 18-hour operating day. Civil classes are proportionally transferred as a planning assumption; site/access feasibility and physical civil design remain open.

### Native GIS prototype status

The source-only importer and bootstrap regressions are now part of the shared
software workflow, with local and independent checks recorded in the
[prototype report](native-gis-source-only-prototype.md). This is code-level
evidence only. There is no run-07 GIS authorization or execution, and the
native-GIS return-path gate remains open until the complete project edit and
recalculation round trip is generated, independently checked and reconciled to
the same candidate. The retained browser-upload proposal is not a substitute:
it is stale against the closure source tree, has no admitted supervisor, and
does not exercise the native editor. See the [readiness audit](native-gis-run07-readiness.md).

### Door-system inventory audit

A candidate-matched read-only review covers 93 proposed part types and 10,296
listed pieces across the door openings, leaves, glazing and electrical operator
sets. Its counted six-car allowance is 1,180.332 kg and $33,260 base direct
parts/process cost, with substantial low/high bounds. Finished geometry is
unverified for every item; the existing GLB is static presentation geometry.
The installation proposal contains finite travel and swept-box hypotheses.
The original 9f6d archive preserves its historical vector mismatch, while a
separate source-bound child evaluation corrects all 24 door travel vectors
without changing the physical candidate or rewriting the old receipt. The
motion data is internally consistent, but the result is not a kinematic CAD
assembly or an integrated collision, clearance, supplier-fit, service/removal
or door-safety proof. A distinct 907da source-body evaluation is also corrected
and remains separately identified. See
the [part-level audit and
source hashes](door-subassembly-audit-01/README.md). This advances component
accounting while leaving the installed-vehicle and controlled-document gates
open.

### Candidate-specific procurement sensitivity

A source-matched Samawah five-line scenario compares project make/buy and
Chinese bulk purchase across fourteen cost scopes. Under unquoted Class C rate,
freight, duty, QA and factory assumptions, the China-bulk case is +$5.224m
base CAPEX and +$9.448m base NPV relative to project make/buy. No project
volume discount or binding supplier offer supports a lower-price claim. The
scenario uses planning demand and cannot be transferred to the remaining city
studies. See the [complete source-pinned packet](samawah-china-supply-cost-04/README.md).

[A regenerated compact-drive body](compact-drive-source-replay-01.md) reproduces
the 75075 physical candidate ID under current source pins with a distinct
evaluation ID. The current-source city adapter accepts that exact evaluation
and emits a held Samawah outline. The corrected [cost bridge](samawah-candidate-cost-bridge-current-source-attempt-03/README.md)
prices candidate BOM/guideway fragments and separate auxiliary-energy and
corrective/disruption sensitivities. The fourteen-scope audit records what
remains unpriced. An earlier bridge source map pointed to a historical body;
that packet and its correction trail remain preserved. None of this closes
service, installed mass, civil loads, complete delivery or lifecycle pricing.
The geometry screen remains HOLD. The earlier city packet and its source-refusal
log remain preserved as historical evidence. See the [body replay](compact-drive-source-replay-01.md),
[current-source city report](samawah-city-recalculation-current-source.md),
[corrected current-source cost bridge](samawah-candidate-cost-bridge-current-source-attempt-03/README.md)
and [retained earlier delivery audit](compact-drive-delivery-audit-01/README.md).
