# Buildable Civil Release Catalogue

This generated catalogue reconciles all **19 reusable IFC types** (138 occurrences) into **6 bounded release packages** and **9 drawing-definition briefs**. It distinguishes the 9 civil-owned geometry types from 10 track, station, vehicle, and coordination interfaces.

Nothing here is issued for fabrication or construction. Site survey, geotechnics, per-span structural analysis, reinforcement/prestress, supplier certification, erection engineering, permits, independent check, and signed release remain open.

## Outputs

| File | Purpose |
|---|---|
| [`reusable-type-release-register.md`](reusable-type-release-register.md) | Exact one-to-one accountability for every deterministic IFC type |
| [`factory-release-work-packages.md`](factory-release-work-packages.md) | Outputs, tools/gauges, and open hold points for six release packages |
| [`factory-drawings/index.md`](factory-drawings/index.md) | Nine controlled, non-issued drawing-definition briefs |
| [`evidence/civil-release-record-template.json`](evidence/civil-release-record-template.json) | Empty evidence record that project authorities must complete |
| [`reusable-type-release-register.json`](reusable-type-release-register.json) | Machine-readable register, packages, briefs, and validation flags |

## Regenerate

```bash
tools/automation/buildable-civil.sh
```

The generator deliberately fails if the reference IFC type hashes change without a corresponding ownership and release-path decision.
