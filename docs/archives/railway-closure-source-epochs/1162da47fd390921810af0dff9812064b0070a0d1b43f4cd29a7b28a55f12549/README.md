# Candidate-to-journey closure

Three distinct body definitions feed 12 same-candidate railway bundles over 1.5 km and 2 km, with station-only P1 and separately identified P4 recovery-drive research. 48 empty, normal, crowd and adverse loading calculations propagate accounted mass to required force, independent brake hypotheses, civil loads and quantity coefficients. 36 full fault journeys remain explicitly not-run. 72 separate brake-response calculations use declared initial states, command latency, pressure rise, lost channels/pressure and adhesion. Static holding and rollback are resolved without reverse propulsion from a brake command. These are unqualified hypotheses, not completed fault journeys.

**Zero complete installed vehicles, validated operating maps or physically supported journeys.** These are conditional calculations. Unlocated equipment accounts, GFRP/joint properties, actual electrical/thermal duty, brake hardware, site data and prices remain open. No preferred railway or physical release is selected.

## Candidate comparison matrix

Each row is one exact body/architecture/route bundle under the same closure contract. Accounted masses are partial ledger values. Required force and power summarize demand across the four declared loads; they are not supplied propulsion performance. Adverse reachability applies only to the analytical demand path. A missing force map, installed mass or whole-life cost remains unknown.

| Body family | Drive family | Route | Candidate | Accounted tare kg/car | Max required force kN/train | Max required power MW/train | Adverse demand path | Available force map | Complete mass | Whole-life cost |
|---|---|---:|---|---:|---:|---:|---|---|---|---|
| aluminium_frame | P1 | 1.5 km | `c9004e9fee27` | 14099.1 | 75.35 | 1.507 | reached (demand only) | unknown | unknown | unknown |
| aluminium_frame | P1 | 2 km | `217500ae85b4` | 14099.1 | 75.35 | 1.507 | missed (demand only) | unknown | unknown | unknown |
| aluminium_frame | P4 | 1.5 km | `604f3672bfc3` | 14099.1 | 75.35 | 1.507 | reached (demand only) | unknown | unknown | unknown |
| aluminium_frame | P4 | 2 km | `4856bf0f38ef` | 14099.1 | 75.35 | 1.507 | missed (demand only) | unknown | unknown | unknown |
| aluminium_stressed_skin | P1 | 1.5 km | `7118dc034ea9` | 14371.2 | 76.04 | 1.521 | reached (demand only) | unknown | unknown | unknown |
| aluminium_stressed_skin | P1 | 2 km | `217ff51063de` | 14371.2 | 76.04 | 1.521 | missed (demand only) | unknown | unknown | unknown |
| aluminium_stressed_skin | P4 | 1.5 km | `dbf0c8ddb9e2` | 14371.2 | 76.04 | 1.521 | reached (demand only) | unknown | unknown | unknown |
| aluminium_stressed_skin | P4 | 2 km | `6698d86c9876` | 14371.2 | 76.04 | 1.521 | missed (demand only) | unknown | unknown | unknown |
| gfrp_semimonocoque | P1 | 1.5 km | `7989a9ef6ca4` | 13551.4 | 73.95 | 1.479 | reached (demand only) | unknown | unknown | unknown |
| gfrp_semimonocoque | P1 | 2 km | `c494ae4f6ed7` | 13551.4 | 73.95 | 1.479 | missed (demand only) | unknown | unknown | unknown |
| gfrp_semimonocoque | P4 | 1.5 km | `02c67192d9e6` | 13551.4 | 73.95 | 1.479 | reached (demand only) | unknown | unknown | unknown |
| gfrp_semimonocoque | P4 | 2 km | `d3f79a00c12f` | 13551.4 | 73.95 | 1.479 | missed (demand only) | unknown | unknown | unknown |

The full machine-readable report preserves complete IDs, per-load force/power/energy and runtime, brake hypotheses, civil alternatives, quantity coefficients, source evaluations and acceptance flags in [comparison.json](comparison.json).

The [required test programme](required-tests.json.gz) specifies ten test families with exact candidate/component bindings, conditions, measured channels and units, prerequisites, calibration/authentication needs and criterion derivations. Physical records are unavailable for this programme revision. Every test is unexecuted, every approval limit remains unassigned, and physical changes require a new as-built identity. These plans cannot admit a solver or qualify an article.

The moving-conductor LIM method is a separate numerical component experiment; its benchmark, refinement and domain limitations remain separate from operating-map admission.

Run `./osr design railway demonstrate --max-bundles 12`; resume the same command for pending cases. Use `./osr design railway demonstration-publish` and `./osr design railway demonstration-verify` to regenerate/check this packet.

[Summary](summary.json) · [Candidate comparison](comparison.json) · [Executed cases](cases.json.gz) · [Bodies and equipped projections](equipped.json.gz) · [Sources](source-epochs.json)
