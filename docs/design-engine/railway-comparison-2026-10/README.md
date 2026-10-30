# Candidate comparison and domestic fabrication screen

This generated report joins the exact candidate-to-journey comparison with the candidate-bound Iraqi civil material and base-wage screen. It covers 12 bundles (three body families × two drive families × two routes) and all 36 matched 20 m beam alternatives.

**No candidate is selected or physically accepted.** Complete installed vehicle mass, available station-drive force maps, completed fault journeys, supplier-installed costs, complete civil installed costs and whole-life cost remain open. The domestic civil values below price only the declared concrete ingredients and reinforcement allowance plus assumed labour, with a 20% planning uplift.

Closure evaluation `feb1672bbc9f4feb41d87044e05e66dd45d08f340f7b180a2a2e81cff083006e` · comparison `a3372ffb6ce67ef49f7e99b4723cec0d47d1ba63a9fa57f244ec26345d7392f8` · civil cost packet `382205dc83d09a11c2f628a62b1978f3ff80244d65553765b20fd7ee563c89fa` · report `c013acf23dd543a9d78cf8f5fa2063b5f44ebb5fb9552459c6a8a941a3cf7aca`.

## Candidate matrix

Costs are per span, not per route. The 2026 range covers the three civil alternatives and the Baghdad/Al-Muthanna wage cases at 4 assumed person-hours per m³ concrete and 8 per tonne reinforcement. The 2025 column uses the same hours with the CSO skilled-wage sensitivity and annual governorate material rates. Those vintages differ in geographic aggregation and must not be read as a pure inflation comparison.

| Body | Drive | Route | Physical candidate | Accounted tare kg/car | Max required force kN/train | Max required power MW/train | Adverse demand runtime s | Civil screen 2026 IQD m/span | CSO annual 2025 IQD m/span | Complete mass / force map / whole-life cost |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| aluminium_frame | P1 | 1.5 km | `c9004e9fee27` | 14099.1 | 75.35 | 1.507 | 130.9 | 5.40–6.69 | 5.07–6.89 | unknown |
| aluminium_frame | P1 | 2 km | `217500ae85b4` | 14099.1 | 75.35 | 1.507 | 182.1 | 5.40–6.69 | 5.07–6.89 | unknown |
| aluminium_frame | P4 | 1.5 km | `604f3672bfc3` | 14099.1 | 75.35 | 1.507 | 130.9 | 5.40–6.69 | 5.07–6.89 | unknown |
| aluminium_frame | P4 | 2 km | `4856bf0f38ef` | 14099.1 | 75.35 | 1.507 | 182.1 | 5.40–6.69 | 5.07–6.89 | unknown |
| aluminium_stressed_skin | P1 | 1.5 km | `7118dc034ea9` | 14371.2 | 76.04 | 1.521 | 130.7 | 5.40–6.69 | 5.07–6.89 | unknown |
| aluminium_stressed_skin | P1 | 2 km | `217ff51063de` | 14371.2 | 76.04 | 1.521 | 182.5 | 5.40–6.69 | 5.07–6.89 | unknown |
| aluminium_stressed_skin | P4 | 1.5 km | `dbf0c8ddb9e2` | 14371.2 | 76.04 | 1.521 | 130.7 | 5.40–6.69 | 5.07–6.89 | unknown |
| aluminium_stressed_skin | P4 | 2 km | `6698d86c9876` | 14371.2 | 76.04 | 1.521 | 182.5 | 5.40–6.69 | 5.07–6.89 | unknown |
| gfrp_semimonocoque | P1 | 1.5 km | `7989a9ef6ca4` | 13551.4 | 73.95 | 1.479 | 131.3 | 5.40–6.69 | 5.07–6.89 | unknown |
| gfrp_semimonocoque | P1 | 2 km | `c494ae4f6ed7` | 13551.4 | 73.95 | 1.479 | 181.5 | 5.40–6.69 | 5.07–6.89 | unknown |
| gfrp_semimonocoque | P4 | 1.5 km | `02c67192d9e6` | 13551.4 | 73.95 | 1.479 | 131.3 | 5.40–6.69 | 5.07–6.89 | unknown |
| gfrp_semimonocoque | P4 | 2 km | `d3f79a00c12f` | 13551.4 | 73.95 | 1.479 | 181.5 | 5.40–6.69 | 5.07–6.89 | unknown |

The force and power columns are required demand, not available motor output. Adverse runtime is from the analytical demand path only. All body, brake, thermal, foundation and propulsion models retain their source limitations in the machine-readable row.

## Scope and evidence

Each machine-readable candidate row preserves the original closure comparison row, all four load cases, the candidate's BOM and manufacturing coverage, economics, risks, outstanding evidence, and three exact civil alternatives with their complete regional and labour-hour sensitivity details. Every civil row is bound to candidate, bundle, physical civil component and alternative IDs.

The September 2026 model applies the generic Iraqi material rates and base-wage recipes. The 2025 cross-check uses the CSO's annual governorate material averages and six separate wage-category sensitivities. An 8-hour day converts published daily wages to assumed hourly base wages. Neither source provides validated factory charge-out rates, crew mix, production yield, tooling, QC, overhead, or a supplier quote. The 20% uplift is unallocated and applied once to the screen's direct material plus assumed labour.

The displayed cost is not a precast beam price, an installed span price or a route CAPEX estimate. Prestress, anchorage, rails, fasteners, moulds, factory utilities, QA, scrap, transport, cranes, foundations, erection, taxes and maintenance remain outside this screen. The CSO annual series and September 2026 national rates use different periods and geographic aggregation.

## Reproduction and verification

```sh
./osr source report candidate-comparison --output docs/design-engine/railway-comparison-2026-10
./osr source report candidate-comparison --output docs/design-engine/railway-comparison-2026-10 --check
```

[Candidate comparison JSON](candidate-comparison.json) · [Publication manifest](manifest.json) · [source closure dossier](../railway-closure/README.md) · [Iraqi civil rate and fabrication dossier](../sourcing/README.md)
