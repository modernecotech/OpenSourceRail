# v0.6 design closure

[Vehicle manufacturing-document coverage draft](vehicle-document-coverage.json)

[Compact-drive corridor attempt and retained evidence](compact-drive-corridor/README.md)

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
| Installed vehicle | Open | The detailed 9f6d research candidate still needs one reconciled, complete located installed inventory with interfaces, clearances, mass properties and downstream force/civil consequences. The six-car passive-wheel development reference in `engineering/development-baseline.toml` remains unchanged. The compact-drive build is a further unselected candidate with no matching canonical railway study. |
| Controlled research documents | Open | The supplementary audit of the retained 668-part delivery map finds 41 assemblies with 82 missing assembly-document slots and 4,676 missing part-document slots; all delivery document references are null. It does not assert a repository-wide search. No manufacturing release is authorized. |
| Mapped corridors | Open | Baghdad's revised 205 m maximum-deviation route has a passing geometry screen, but no corridor-specific protected service, fleet, energy, site quantities or fourteen-scope costs. Samawah retains its earlier geometry-only result. |
| Native GIS return path | Open | The last one-shot attempt failed before application launch because the sealed wrapper referenced absent overlay files. The consumed authorization and failed run are retained; a corrected attempt needs a new sealed plan, independent review and fresh resource preflight. |
| Candidate business lifecycle | Open | The available ERPNext delivery proposal is bound to an older body. A new compact-drive candidate was correctly refused as a mixed identity. No candidate-matched controlled documents, review pack or native lifecycle evidence exist yet. See the [candidate lifecycle audit](../v06-business-lifecycle-audit/README.md). |
| Unified Workbench | Partial | A source-bound view covers the reconciled 1.5 km pilot, with its own candidate identity. It does not yet cover the closure campaign's full city-brief-to-compatible-alternatives path, same-candidate journey/cost/delivery, drawing/BOM/manufacturing review or reconciled downloadable dossier. See [`campaigns/v06-design-integration-closure.toml`](../../../campaigns/v06-design-integration-closure.toml). |
| All-city outline reconciliation | Open | Current manifests cover 266 cities, 1,565 lines and 13,580 station-table rows, but all lines use the shared 4,000 pphpd / 200 s study control and local rates are transferred reference estimates. City-specific service, alignment choices, China-volume versus local-manufacture scenarios and same-candidate recomputation remain required. |

The all-city audit confirmed the catalogue and v0.4 front-door field coverage,
not the correctness of local demand, rates or physical alignments. The
mapped-corridor and native-GIS execution artifacts are retained under the
private, source-bound run record. Their limitations and identities must be
carried into any new plan. A geometry pass is not an operating route, and a
UI upload alone would not close the GIS round-trip gate.

### All-city baseline audit

The read-only audit was bound to closure commit
`edfbff55ff20303ce0ea244ac645251d89eec28d`. It found 266 city outlines,
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

The [root README](../../../README.md#models-from-cad-and-analysis)
already includes renderings from the SolidCraft and FieldCraft engineering
work: vehicle and bogie assemblies, launch shuttle and coupling, viaduct
assembly and a FieldCraft displacement result, plus manufacturable component
details. Those images support inspection of the research models; they are not
manufacturing drawings or qualification evidence.
