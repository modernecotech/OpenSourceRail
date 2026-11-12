# v0.7 execution and evidence

The [task ledger](../../../campaigns/v07-execution.json) records implementation,
research controls and remaining holds separately. v0.7 is in development; these
results do not constitute a completed installed railway or a released v0.7.
The [agent plan](../../plans/v0.7-agent-delivery-plan.md) remains the scope.

The [closing software verification record](software-ci-final.json) pins code
`8d1833f74c`: 480 selected Python tests pass (four optional skips), and the full
wheel/station workflow passes its supported browser and Samawah journey. All
five retained-method/shared correction workflows pass `bce9d27892`; earlier
Rust, Workbench and reconciled results retain their own source identities, with
unchanged production objects verified. R01 now has a reviewed bounded corridor
baseline. The isolated source tree is about 0.94 GiB and the closing host reading
has 21.71 GiB free; shared Git storage is separate.

The subsequent repository review confirmed main `88f5ecc88b` and the successful
[Workbench journey on that exact commit](https://github.com/modernecotech/OpenSourceRail/actions/runs/43254678158).
The agent plan now prioritises P01/C01 mated door integration, M01 controlled
manufacturing data and L01 actual module custody/persistence. Completed GIS,
profiling and reservation work is retained; Rust changes must follow the measured
hotspots. Original plan and execution identities remain in the ledger.

## Implemented and exercised

The Workbench compares the Samawah station merge, preserves all fourteen cost
scopes and exposes a project envelope that rejects mixed candidates and stale
upstream stages. Station changes preserve unrelated vehicle/manufacturing
results; cost-rate changes invalidate costs, delivery and dossier. Missing
installed stages stay visible. A source-bound door panel exposes the 74 part
definitions, assembly proposals, inspection gaps and removal/maintenance basis.

City workers now share cooperative CPU, memory and disk reservations, use a
resumable bounded queue and admit at most two analytic workers. The server
retains a 20 GiB host disk reserve. The [controlled comparison](analytic-capacity.json)
observed real two-worker overlap: a fresh pair took 31.02 seconds versus 45.80
seconds with one worker, a 32.27% reduction. Exact numerical metrics and all
fourteen cost scopes matched. Warm repeats took about 1.7 seconds. This is one
pair per mode on one host, not a general performance guarantee. Reservations
are cooperative; they are not an aggregate filesystem quota.
The two workers used 37.31 combined worker CPU-seconds versus 32.47 serially,
about 14.9% more CPU in that trial. The benefit is lower waiting time. Set
`OSR_CITY_STUDY_WORKERS=1` to retain serial admission when CPU use matters more.
Individual worker RSS is recorded; simultaneous aggregate RSS was not measured.
Nine retained engineering workflow filters now exclude isolated changes to the
new force-gap report and execution receipts. Core vehicle/physics changes still
trigger their existing jobs; mixed report/core changes are covered by regression
checks. No solver job definition was removed.

The profiled delivery scheduling kernel has a source/tool/binary-verified Rust
implementation. Twenty-four actual before/after low/base/high comparisons
matched canonical output exactly. Measured kernel reductions were 43–59%,
including the boundary cost. It remains opt-in; no end-to-end Rust pipeline
speedup was claimed for that kernel experiment. The production compiler now
offers an explicit Rust backend through
[the delivery CLI](../../guides/delivery-scheduler.md). It verifies an existing
current city-study publication before and after compilation, uses a prebuilt
source/tool/binary-bound executable and records three bounded helper calls with
zero solver jobs. The analytic city workers retain their zero-helper Python path.
A fresh Samawah study produced 4,170 tasks with the same physical candidate and
configuration. Three full CLI pairs matched all numerical and policy output:
median time fell from 12.49 to 10.79 seconds, or 13.64%. This includes input
verification, complete compilation, sealing and writing; it excludes building
the executable and is not a whole-city speedup. Python remains the default.
The [comparison record](delivery-scheduler.json) lists the exact source/evaluation
metadata exclusions and all additional Rust bindings. The canonical encoder benchmark made 48 exact byte/identity
comparisons but gained only 1.72% in the guarded warm batch. That result does
not justify moving more production callers to Rust.

Native GIS uses external import custody and verified parent planning snapshots.
Samawah and Baghdad each completed a headless native station edit, canonical
import, repricing, refreshed native export and second dwell edit. These are
programmatic `.rgis` edits reopened by the native application, not GUI tests.
The final acceptance used source `3ba09cf9ac` for both cities: eight native calls
each, 41.18 seconds for Samawah and 103.67 seconds for Baghdad. Eligible city
calculations were reused with their original identities; native executions and
export receipts were fresh. All other four Samawah and thirteen Baghdad lines
retained exact protected geometry and assumptions. Each record retains its
actual source revision. The Samawah failed attempts
(dwell projection and parent lookup) and Baghdad terminal-chainage failure
remain preserved alongside the fixes and successful runs.

The [current-source revalidation](native-gis-current.json) then repeated both
journeys on `7516359c40`: sixteen fresh native calls, six legitimate new studies
and exact offline replay of both final children. Historical baseline numerical
controls and all fourteen cost-scope totals matched exactly. The work took
352.11 seconds and retained about 325 MiB. All other complete line records,
route coordinates and protected stop IDs/chainages/dwell inputs remained exact.
Twelve unedited Baghdad stops on the selected line reconstruct latitude by
1–3 float ULP; the same differences exist in the earlier run. Exact before/after
values are recorded, rather than claiming byte-identical derived coordinates
or changing a tolerance.

## CAD and mechanics controls

The door definition counts 694 pieces per opening and twelve openings per train.
Its nominal 50.433 kg stock/allowance subtotal per opening is not installed mass.
SolidCraft generated and reopened a representative header stock blank, including
STEP export; independent FreeCAD import reproduced the solid geometry. The
blank is not a fully detailed, installed door operator. STEP lost material/source
metadata, so the source sidecar remains required.

The existing installed-layout generator was also run analytically against current
sources. Physical child `17ce7a…` stayed unchanged; evaluation
`123896d4014fd00bc11fc755f132aa8769ebfd217f06d6f34b2fe8342d62c4f1` is new.
All 74 operator definitions and expanded counts match the manufacturing parent.
A compact one-opening attachment retains proposed transforms and instructions.
Eleven operator types still occupy the same generic header-centre zone, and a
2 m route envelope does not represent the full 2.9 m guide stock. These are
specific assembly-design gaps; copying those coordinates into accepted installed
fields would not resolve them. The regeneration took 12.59 seconds, used about
133 MiB peak RSS and executed no native tool.

Civil controls derive 24 axle positions from the six-car reference and keep
normal 46-person and crowd 160-person cases distinct. The fresh normal 3D
experiment ran seven native processes: one geometry import, two fresh meshes
and FieldCraft/CalculiX solves on each mesh. Fine FieldCraft displacement was
−9.989130 mm; relative cross-solver disagreement was about 1.01×10⁻⁸. The
2.7255% displacement refinement passes the declared 5% diagnostic but does not
establish mesh independence. Offline verification exactly reconstructed both
mesh/load records and both solvers' raw readbacks.

That FEM control includes a 1.3 dynamic multiplier, an explicit non-CAD reserve
and finite bearing patches. Its ±0.6 m load-spreading patches are an unverified
hypothesis, not the selected 1.435 m rail interface. It is not a direct numerical
comparison with the different static analytical moving-load model. Old crowd
mesh/load replay did not match exactly and remains held; no old solve was reused.

The force/braking compiler reuses existing interpolation, counted rotating stock
and independent stopping methods. Named 2,000 m controls require approximately
11.10 kN/car normal and 14.73 kN/car crowd launch force. Actual installed thrust,
current/voltage limits and repeated-duty temperature remain unknown. Valid
synthetic map samples do not establish installed propulsion performance.

The [bounded Samawah performance baseline](performance-baseline.json) now
covers a fresh ordinary worker and three steady API cache hits. Its complete
25,623,859-byte encoded result matches the retained control without exclusions;
all 65 source bindings match. Read-only peer review confirmed the ordinary
job status flow, untouched function implementations and exact phase accounting.
The publication envelope took 16.58 seconds; exclusive delivery, serialization
and business-draft time were 4.06, 3.60 and 2.72 seconds. Three post-warmup
cache hits took 66.48, 65.44 and 65.50 ms with no additional worker starts.
These are API retrievals, not full browser timings or recomputations.

R01 is closed for this bounded corridor inventory. Read/decode and
write/orchestration remain combined categories; per-stage RSS/physical I/O
and aggregate scratch highwater are not established. Browser/build receipts
retain their original epochs. Monitoring overhead is uncalibrated, the OS
page cache was uncontrolled, and no optimization or all-workload claim is
made. The failed probe initialization is preserved; both attempts used
35.98 seconds and about 24.65 MB, with no builds or native solves.

## Door route proxy and retained analytical child

A read-only audit of the existing sealed installation packet found 830
cut-length patterns, including 24 door guide/belt patterns. The guide's
2.9 m stock and belt's 5.8 m cut length each appear as a 2 m straight display
proxy. The stock lengths remain in source data, but the proxy does not show
that a routed part fits, clears adjacent hardware or can be removed.
The belt loop must not be interpreted as a straight 5.8 m part.

The [audit receipt](evidence-index.json) verifies the original packet seal,
physical candidate `17ce7a724fcd661e5c4f195cde19b68377c0968e4e7d7dbb5d6ac7c8d4074ad4`,
evaluation `123896d4014fd00bc11fc755f132aa8769ebfd217f06d6f34b2fe8342d62c4f1`,
and all eleven current source bindings. The installed model's original bytes
remain in use. Intermediate experiments with changed model sources are retained
in the evidence index under their own historical identities; their outputs are
not current installation evidence. The mated positions, controlled dimensions,
full route fit, installed mass and physical acceptance remain open.

## One-opening interface and custody handoff

The [candidate-bound door handoff](door-interface-handoff.json) inventories all
74 mechanical and electrical part types for `car-0/door-0`, with their component
identities, source stock, make/buy policy and counted quantities. It binds the
manufacturing child `907da368…` to the existing analytical installed child
`17ce7a…` and keeps the source proposal's `accepted_installed_transform_m`
empty. The opening centre at car-local x = −4.5 m and proposed 0.72 m leaf
travel establish a layout frame, not an accepted installation datum.

One opening has 694 pieces: 97 locally fabricated, 568 bought to standard and
29 bought to qualification. Thus 597 purchased pieces across 35 part types need
receipt and lot/serial custody. Current assembly lifecycle code supports only
manufactured individually serialized children. The handoff identifies the
header/body, rail/carriage, belt/pulley, motor/reducer, leaf/stop and sensor
interfaces that need controlled datums and dimensions. Every part's installed
transform, mating datum and approved inspection limit remains unknown. The
packet was generated without native CAD or ERP execution. Its source-bound ID is
`a2114619675858be7bba0a44655761b1feb45698a25181aa9f2f1ec3744e1908`.

Rebuild it with `python -m tools.automation.door_interface_handoff --attachment
<verified-one-opening-attachment> --installation <sealed-installation-packet>
--output <new-file>` after relevant source
changes. The compiler checks both records against the same sealed installed candidate and
current source bindings. It rejects mixed candidate/counts, a broken attachment
seal, missing source bindings and an asserted accepted transform. The first next engineering input is a
controlled header-to-body datum and guide/carriage/drive mating definition;
the first software input is typed purchased receipt/lot custody and incoming QA.

## Integration still required

The published reference `756a…` and manufacturing child `907d…` differ physically,
including intercar gap. The child cannot inherit the reference's fleet, costs,
installed vehicle or engineering results. The current analytical child evaluation
is recorded above; a complete mated installation, matching civil/station
interfaces and lifecycle package are still needed before those stages can be
composed into a complete dossier.

Door installed transforms, clearances, mating datums, tolerances, inspection
limits and maintenance intervals remain incomplete. Actual drive/brake/thermal
data, bearings, foundations, construction stability and a crane chart at the
installation radius are also missing. These are specific engineering inputs,
not permission to invent zero mass, prices, limits or passing test results.

The existing disposable ERPNext/FUXA fixture exercises a discrete workpiece.
It does not yet demonstrate the counted 694-piece module assembly lifecycle.
The existing candidate-delivery protocol now supports source-derived assembly
groups and nonexploding parent BOM drafts. It preserves all thirteen identity
requirements and verifies source counts, context bindings and child-draft
provenance. The conversion uses reviewed source estimates, USD-company and
precision guards, and leaves assembly process cost unknown. See the
[API and conversion limits](../../../engineering/pilot_delivery/README.md#counted-assembly-drafts).
Twenty-three focused synthetic tests and independent review cover the extension;
actual native persistence and the full module lifecycle remain unverified. The
[typed assembly lifecycle API](../../integration/v07-assembly-lifecycle.md)
now adds installation, replacement, condition events and business handback for
manufactured, individually serialized children. It checks own assembly documents,
native voucher/serial provenance and latest child QA. A different accepted child
QA record invalidates the previous handback review. Twenty new assembly tests
and 56 compatibility tests passed; an independent reviewer reproduced the new
twenty. Purchased/lot custody remains unsupported. A
matching candidate package and controlled document coverage are still required
for the actual door run. Controlled research documents can support software tests
without claiming physical qualification.

## Tool migration and replay

The [consumer inventory](tool-inventory.json) records pinned tools and source
consumers. The [operation matrix](tool-capabilities.md) records supported,
unsupported and untested domains, entry points, resource limits, installation
size unknowns and individual retirement decisions. The light door CAD path uses SolidCraft; FreeCAD is an optional
independent control. RustGIS supplies the demonstrated native return path.
QGIS is not required to run that path; retained lightweight project readers
remain useful. Gmsh is still required for the demonstrated conformal meshes,
and CalculiX supplies an independent mechanics comparison. Other active native
consumers have not passed the retirement gates. No global tool uninstall,
historical evidence deletion or Git history rewrite has occurred.

Raw numerical outputs stay outside Git. The [local evidence index](evidence-index.json)
records exact receipt bytes, hashes and locations; it is not an online artifact
store. Existing source-bound records retain their original identities. Failed
and interrupted attempts are retained. Repository changes were integrated from
isolated worktrees while preserving unrelated user changes in the main checkout.

All three required software workflows passed on `3ba09cf9ac`:
[311 Python tests](https://github.com/modernecotech/OpenSourceRail/actions/runs/43202814038),
[Rust contracts and scheduler parity](https://github.com/modernecotech/OpenSourceRail/actions/runs/43202813880),
and the [clean Workbench installation and journeys](https://github.com/modernecotech/OpenSourceRail/actions/runs/43202814101).
That clean sparse checkout installed SciPy, npm dependencies and Chromium;
it ran frontend contracts, two retained Journey A cases and the new station
comparison. Its new comparison took 16.84 seconds cold and 0.94 seconds warm on
the CI host, which is separate from the controlled local worker comparison.
The [CI record](clean-software-ci.json) includes artifact IDs and download digests.
This verifies the supported software slice, not the missing module lifecycle
or a complete v0.7 release.

The later [software checkpoint](software-ci-952b7d9.json) passed all five required
and retained workflows on exact source `952b7d953f`: 387 selected Python tests,
Rust contracts, Workbench journeys, shared contracts and reconciled research.
The reconciled lane passed 158 tests plus 13 subtests. The subsequent Rust CLI
and assembly lifecycle additions have their own checkpoints below; earlier green
checks are not relabelled as evidence for those additions.

Checkpoint `a41c280544` then passed 430 selected Python contracts (four optional
skips), Rust compilation/parity, Workbench, reconciled research and the retained
native business-platform fixture. The latter remains flat-part compatibility,
not native assembly validation. Shared CI identified an outdated presentation
policy pin to the delivery compiler. The complete `DEFAULTS` syntax tree and
every policy value are unchanged; only the current policy's producer hash was
refreshed. No historical packet or receipt was rewritten. Sixteen analysis and
five routing checks pass. Exact standalone policy/test edits now run in the
bounded Python lane; mixed engineering edits still trigger retained workflows.
The existing Shared filter excludes edits to its own workflow file. The explicit
final-source Shared run `43229288557` passed on `7516359c40`; no duplicate run
was launched. The same `7516359c40` checkpoint passed 447 Python tests
(four optional skips), Rust contracts, Workbench and reconciled research.

The later `e2a7ef8055` checkpoint passed 470 selected Python contracts (four
optional skips), Rust contracts, Workbench, reconciled research and the twin
workflow, including actual native placement controls. Its Shared guard caught
an unintended edit to the pinned retired job; that entire job is restored byte
for byte, preserving its original ordered command hash. The current-checkout
job alone uses historical compact/line integrity checks. The twin architecture
guard now checks the exact historical commands and separately requires native
placement export/reopen tests after the pinned CAD install. All 42 architecture
tests pass. A subsequent variant-publication hold is resolved by the explicit
same-epoch check below; no original result was rewritten.
The [production source comparison](production-source-e2-bce.json) confirms that
the Rust, outline, Workbench, integration and GIS runner objects are unchanged
between that checkpoint and `bce9d27892`. Prior CI retains its original commit.

The later wheel-reference job passed its numerical, native-adapter and comparison
contracts, then stopped because strict `./osr verify` correctly holds the
excluded integrated dossier. Current CI now explicitly checks the documented
workflow-source hold, all five false authority flags and absence of a published
result. The reader verifies every declared payload before that first source
hold; this does not claim currency or authenticate later source bindings. The
actual packet check passed, and six unrelated/tampered/current/authority cases
were rejected. The strict verifier remains unchanged.

Those checks, documentation and frontend contracts now precede expensive
wheel tests. The generated index was rebuilt for 236 maintained documents;
the local README check passes for 771 materialized files. Index-only changes run in the bounded lane before
dependency installation, using the existing Markdown policy and one batched
sparse expansion. A fresh local-Git test used 2,072,576 allocated bytes and
0.40 seconds; no cold-network timing claim is made. Seven routing and 42
architecture tests pass. [Production source objects](production-source-e2-4f.json)
remain unchanged from `e2a7ef8055` through correction `4f0a0ace7a`.

The owned evaluation working tree was then reduced from 8.45 GiB to about
0.91 GiB, retaining project agent instructions, plans, CI contracts and the bound
city inputs. Shared Git storage is separate. Reflink sharing kept host free space
around 22.4 GiB during that checkpoint. The final owned bytecode cleanup removed
83 generated files (2.22 MiB logical bytes), leaving 21.81 GiB free; this does not
claim exclusive physical reclamation for shared/reflink data. In that compact tree, 53 focused tests and the actual Samawah
browser replay passed; Baghdad's existing source-bound packet also verified with
zero new calculations. The browser reused eligible jobs: its 11.22-second first
click is not a cold calculation, and its warm repeat took 1.69 seconds.
The [compact-checkout record](compact-checkout.json) preserves the environment
and the initial missing-default-browser-cache failure. The successful run used
the existing shared Chromium installation. The grouped/flat delivery and CI
routing checks separately passed 60 tests after integration.

Retained-research CI found two source-epoch mismatches after these changes.
The older engineering ledger now references exact archived bytes for three
implementation files authenticated against published `5cfe894`; all seven gate
states, blockers and authority flags are preserved. The original ledger and
relocation manifest remain in
[the source-context archive](../../archives/v06-closure-source-context/README.md).

The three reconciled dossiers now have explicit historical verification. It
authenticates each complete publication and its source/input union against one
original Git commit, then runs the unchanged original checker in a bounded
source context. All three checks passed in 52.56, 42.24 and 49.20 seconds, with
no new native solver executions. This authenticates source, data and methods;
it uses the installed Python/scientific environment and does not restore the
historical operating system. Current strict verification remains unchanged and
refuses these source-stale dossiers. Their numerical Workbench routes stay held.

In a research checkout with the original publication and pinned Git objects
available, the reference dossier can be checked explicitly:

```sh
./osr design closure verify --retained-source f990fc24ba9c1c2adcd8afb4456ded5c4753209a
```

The result distinguishes `retained_verified` from `current_source_valid`.
The wrapper refuses oversized/tampered inputs, replacement Git objects, foreign
project imports and native subprocess execution. Its import/process guards are
cooperative controls, not an operating-system sandbox.

Three other retained publications bind the earlier braking implementation.
Their unchanged original checkers were run against source epoch
`946f1772540d07af85b57b0d13cac08a3293b140`: twin analytical/materialisation replay
covered six non-native cases; reference-cell replay covered ten cases; motor
verification checked the recorded tool/source/payload/trace without a new field
solve. All passed in 81.65, 190.27 and 5.58 seconds respectively. Two earlier
cell attempts hit their 120/150-second CPU limits and remain preserved. The
successful cell request explicitly used 300 CPU/360 wall seconds; no model,
tolerance or original input changed.

The same original epoch also verifies the three retained wayside variants.
All 73 declared source bindings and three payloads were independently
authenticated. The unchanged original variant checker passed in 24.43 seconds;
the current strict reader still rejects the stale reference result. There was
no field/native solve or new operating-map evidence. Twenty-nine boundary
tests pass after integration.

The coordinator lives outside calculation-source discovery at
`tools/automation/verify_retained_publications.py`. It authenticates the exact
original manifests, declared payloads and source/import closure, stages private
copies and invokes the unchanged checker. Unindexed historical twin/native
archives remain untouched and outside the claim. Current strict readers still
refuse these stale publications; the result records `current_source_valid=false`.
An independent review matched 95 source bindings, authenticated all three
receipt/manifest pairs and passed 21 boundary tests in 1.56 seconds. It checked
resource guards, retained failures and staging cleanup without rerunning the
historical methods. No CAD/native/field processes ran. Read the retained packet explicitly with:

```sh
python -m tools.automation.verify_retained_publications prefetch twin
python -m tools.automation.verify_retained_publications verify twin --state /external/fresh-twin-check
```

In a partial clone, the separate CI prefetch selects object IDs without asking
Git for sizes of absent blobs. It fetches only those selected objects explicitly;
verification retains its no-network rule and refuses missing selected blobs.
A real partial-clone regression reproduced the `BAD` size failure, fetched the
selected objects successfully and left an unrelated payload absent. The three
pinned selections total 156.01, 123.22 and 131.36 MiB respectively; their bytes
match the prior authenticated checks. The 512 MiB size limit is checked after
fetch, not enforced as a network-transfer quota. After integration, 42 scheduler
and retained-verifier tests and four workflow-filter tests passed. The refreshed
Rust scheduler build receipt binds the formatting-only source correction; old
benchmark binaries and receipts remain unchanged.

Use the existing [Samawah comparison instructions](../v07-project-continuity/README.md)
for the browser entry point. New bounded native runs require a clean source
checkout, explicit source/tool/candidate/load/resource identity and a fresh
external output directory. The headless GIS runner is
`tools/automation/tests/verify-v07-native-gis.py`; force requirements use
`python -m engineering.station_rail.force_evidence --help`. Heavy native tools
are optional for the analytic browser workflow.
