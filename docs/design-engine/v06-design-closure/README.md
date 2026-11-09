# v0.6 design closure

[Vehicle manufacturing-document coverage draft](vehicle-document-coverage.json)

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
integration work below is complete. This is a software/design release gate;
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

The mapped-corridor and native-GIS execution artifacts are retained under the
private, source-bound run record. Their limitations and identities must be
carried into any new plan. A geometry pass is not an operating route, and a
UI upload alone would not close the GIS round-trip gate.

## Research images

The [root README](../../../README.md#models-from-cad-and-analysis)
already includes renderings from the SolidCraft and FieldCraft engineering
work: vehicle and bogie assemblies, launch shuttle and coupling, viaduct
assembly and a FieldCraft displacement result, plus manufacturable component
details. Those images support inspection of the research models; they are not
manufacturing drawings or qualification evidence.
