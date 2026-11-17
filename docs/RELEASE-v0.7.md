# v0.7 controlled release gate

**Status: development, not released.** The [published v0.6.1 release](releases/v0.6.1/README.md)
remains intact. v0.7's public result is one coherent, priced reference corridor
and a prototype-production package for one car, viaduct span and station
equipment module. Physical qualification for passenger service is a later gate.

The [architecture](ARCHITECTURE.md), [engineering status](ENGINEERING-STATUS.md)
and [cost baseline](COST-BASELINE.md) are the four current decision entrypoints.
The detailed [execution history](design-engine/v07-execution/README.md) and
[affordable-corridor packet](design-engine/v07-affordable-corridor/README.md)
remain evidence, not competing scope authorities.

## Finite backlog

| ID | Deliverable | Acceptance evidence | State |
|---|---|---|---|
| V07-01 | CI and version ownership | Current fast checks pass; published tag, source epoch and development version are distinguished | Package metadata set to 0.7.0; current packet refreshed locally, CI pending |
| V07-02 | Canonical candidate chain | One physical candidate, separate evaluation and selection IDs through service, vehicle, civil, BOM and cost; changed inputs invalidate dependants | [Joined quotation candidate](reference-v07/integration/README.md) has separate IDs, interfaces and quantities; joined native evaluation and installed account open |
| V07-03 | Propulsion and braking decision | Defined surveyed demonstrator envelope, independent stop and rescue, force/current/thermal limits and named physical tests | Overhead-fed powered bogies advanced for research prototype; [independent brake force and energy test](design-engine/v07-independent-brake/README.md) defined; measured adhesion, protected brake supply, thermal duty and surveyed site open |
| V07-04 | Representative car | Controlled general arrangement, installed mass/CG, bogie, door, HVAC/electrical and six-car interfaces, BOM and removal access | [Joined arrangement](reference-v07/integration/README.md) and [manufacturing BOM](reference-v07/manufacturing/README.md) added; weighed mass/CG, full sweeps and supplier drawings open |
| V07-05 | Civil span and station | Joint/bearing/rail/foundation and station equipment interfaces, erection stages, site limits and test plan | 10 m beam and station quotation interfaces counted; structural detail, surveyed ground and approved erection method open |
| V07-06 | Local manufacturing | Candidate-specific BOM, routing, make/buy value and hours, tooling, QA, ERPNext receipt and repair handback | 41-row BOM, 18-step route, local-work basis and unposted ERPNext draft added; receipt and repair handback open |
| V07-07 | Cost | Same-candidate fourteen-scope installed capital, fleet/energy and 30-year lifecycle inputs | [Concept budget](reference-v07/cost/README.md) gives fourteen priced scopes, operation, renewal and 43 months; supplier and site priced installed candidate open |
| V07-08 | Incremental processing | Correct source invalidation and measured time, peak memory and disk on one corridor edit | Current selected rebuild measured 5m04s, 659 MiB peak RSS and about 52 MiB net disk; unchanged book check cached; target improvements open |
| V07-09 | Workbench journey | Clean design edit through service, energy, quantities, cost, dossier, assembly and production handoff | Samawah browser edit and 14-scope single-estimate display pass; joined candidate, BOM, routing and ERP draft linked; joined-candidate recalculation and live ERP receipt/repair open |
| V07-10 | Release | Clean install, current CI, acceptance report, limitations and versioned artifacts | Open |

V07-01's version rule: package metadata is `0.7.0` in `VERSION`, npm and the
Cargo workspace. The v0.6.1 tag is immutable and historical source identities
retain their original version. Regenerate and check affected current packets
before a v0.7 tag; package metadata alone is not a release declaration.

The normal v0.7 checks exercise the current reference, bounded contracts and
the Samawah Workbench journey. Retained frame, reconciled-pilot and engineering
closure replays are explicitly dispatched research jobs. Their saved packets
remain intact and source-bound: the closure source map differs on
`railway_delivery.py` and `engineering/requirements.txt`; the old viaduct
publication differs on three native-backend sources; the archived v0.6 closure
ledger points to an older outline manifest. These are recorded replay holds,
not repaired by editing a receipt or inferred physical failures. A new current
evaluation needs regeneration against the actual source and separate review.

## Execution and release rules

Use the synthetic 30 km case for equal-service economics, a surveyed 1.5–2 km
site for the physical demonstrator, Samawah for its distinct city journey and
Baghdad for strategic planning. Keep their physical and price assumptions
separate. A research alternative does not inherit selected-reference results.

Complete existing modules before adding another. Every task must change an
engineering, production, user or measured performance output. After two
repeats of one failure, record the cause and change the design, assumption or
tool before another run. Run historical source replay explicitly; keep current
checks focused on affected work. Maintain 20 GiB free space before and during
large materialisation or solver work.

Release acceptance requires the ten items above and explicit open physical
tests. It does **not** imply serial-production approval, passenger-operation
authority, an accepted Baghdad financing estimate or physical test results
that have not been obtained.

The 17 November architecture screen resolves the **next prototype research
direction**: a separate powered-bogie child with protected overhead supply is
advanced for measurement and quotation because the tested station-only and
single-booster layouts stall on material uphill sensitivities. Its electrical
configuration and mechanical car now form one [source-bound research bundle](design-engine/v07-prototype-bundle/README.md),
with a nominal IFC interface model and a high-mass service demand. The separate
[10 m civil option](design-engine/v07-simple-span/README.md) has its own
powered-load study but is not an installed site selection. The original
passive-wheel reference remains selected for v0.6. The changed-candidate
capital and lifecycle **planning totals are now defined** in the [single-estimate
cost baseline](COST-BASELINE.md). Supplier and site costs remain to be obtained.
This is a development decision, not completion of V07-03 or authority to
publish v0.7 as a prototype-production package.
