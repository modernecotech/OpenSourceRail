# Civil reference and numerical evidence workflow

[Civil demonstration A](../../engineering/assurance/civil-reference/README.md) contains two adjoining double-track bays (20 m and 25 m), an at-grade transition, connection briefs, bearing and foundation options, construction hold points, a conventional I-girder/deck comparison, and a connected civil FMEA. Its independent review, site design and construction release are pending. The recorded OpenSees, CalculiX and SWMM exercises demonstrate calculations and rejection cases; they do not qualify the structures.

## Mass, lifting and option selection

`osr_mech.civil.reference.lifting_budget` requires every net member detail and rigging mass plus the reviewed equipment configuration, chart and radius. It compares dynamic hook demand with capacity at that radius and permitted utilisation. A 75 t nominal equipment label is insufficient. Member manufacturing mass and lifted mass are separate values. Additional diaphragm mass is net of the bare section; the CAD design zones overlap and cannot be summed as fabricated concrete. Density-based reinforcement adjustment must have a documented basis.

`foundation_candidates` returns alternative methods with no selected design. `compare_foundations` requires capacity, total/differential settlement, groundwater, chemistry, liquefaction/scour applicability, utilities and access, plus an independently reviewed selection and comparison rationale. The legacy `select_foundation().id` is retained as a planning preference for existing callers; `selected_id` stays empty. It is unsuitable for project release. The ground-design gate now reconciles the reviewed per-support comparison with the schedule's capacity and settlement values. Calcium-based soil treatment needs a chemistry compatibility review. Every ground-treatment selection remains subject to site design.

Both the Pi and conventional-girder candidates need supplier section/prestress/reinforcement details, complete installed quantities, foundations, transport, erection, temporary stability, access and maintenance evidence. Ballast, slipformed slab and panels remain at-grade alternatives. No installed-cost or whole-life-cost winner has been established.

## Civil asset register

Both civil release manifests now require a `civil_asset_register` JSON receipt. Its schema is `osr-civil-assets/1` with:

- `design_sha256`: the received design file digest.
- `review`: `decision=accepted`, different named `producer` and `checker`, `signed_at`, and a `controlled_reference` to the independently reviewed layout.
- `assets`: unique `asset_id`, `line_id`, `asset_type`, `from_station_m`, `to_station_m`, `foundation_ref` matching the submitted structural schedule, and explicit `support_ids`. Spans/at-grade structures include supports at both endpoints. Point piers/abutments/foundations can have equal start/end chainage.
- `supports`: unique `support_id`, `scope_type` (`line` or `station`), `scope_id`, `chainage_m` and `zone_id`, matching the foundation schedule exactly.
- `coverage_intervals`: `line_id`, `coverage_group`, start/end chainage. Associated asset intervals carry the same group, cover its whole extent and have no gap or overlap. Separate track groups allow two tracks over the same chainage.

The [concept register](../../engineering/assurance/civil-reference/reference-system.json) shows the structure with review deliberately pending. Expected IDs must come from the reviewed layout, rather than deriving expectations from the submitted schedule. One row labelled with a line ID cannot satisfy omitted spans or supports.

## Structural numerical exchange

Solver reports retain status, convergence, version, input digest and model revision. They additionally require:

- `output_hashes`: map of actual relative file paths to SHA-256 digests, resolved under the controlled evidence root. Missing, empty, changed or escaping files fail.
- `native_output_paths`: nonempty list of hashed native solver files.
- `numerical_results_path`: a hashed CSV with `asset_id,load_case_id,metric,value,unit`.

The independently reviewed `load_case_register` must bind `civil_asset_register_sha256`, include the same `review` fields as above, and define `required_load_cases` and `criteria`, each keyed by `opensees` and `calculix`. Every criterion has `asset_id`, `load_case_id`, `metric`, `unit`, `stage` (`service` or `construction`), finite `limit` and `operator` (`max`, `min` or `abs-max`). Criteria cover every asset/load-case combination; actual CSV rows match exactly, including metrics and units. Required cases, both lifecycle stages and numerical limits are checked. A negative displacement cannot evade an `abs-max` criterion.

The automated exchange checker establishes provenance, coverage and compliance with supplied limits. The engineer and independent checker remain responsible for deriving the numerical exchange correctly from native outputs, selecting sufficient metrics/cases, and validating loads, mesh, soil springs, prestress, reinforcement, railway criteria and construction-stage assumptions. Signed acceptance continues to bind the evidence digests.

## Foundation comparison exchange

`ground_design_verification_report.support_comparisons` is keyed by every scheduled support ID, exactly once. Each entry supplies ground class and actual `vibration_restricted`, `clear_access`, `high_lateral_load` screening conditions; `site` inputs; and a `comparisons` row for every candidate. Site actions are `axial_demand_kN`, `lateral_demand_kN`, `settlement_limit_mm` and `differential_settlement_limit_mm`. Site groundwater, chemistry, liquefaction, scour, utilities and construction access need documented references or reviewed applicability decisions.

Each comparison includes `id`, `axial_capacity_kN`, `lateral_capacity_kN`, `settlement_mm`, `differential_settlement_mm`, `constructable`, `chemistry_compatible`, `liquefaction_checked`, `scour_checked` and `calculation_reference`. `site.selection_review` supplies accepted decision, selected ID, different engineer/checker, signed date, controlled reference and comparison rationale. Schedule `design_capacity` is in kN and settlement in mm. Catalogue foundation concrete is in m³, reconciled against actual finite lengths and integer counts; zero cannot replace a deep-member count. Ground improvement comparisons cover the catalogue alternatives and use the reviewed zone actions/deformations, quantities and compatibility evidence.

## Drainage numerical exchange

The accepted hydrology basis needs independent `review`, `scenario_model_hashes` for `normal`, `blocked-drain` and `backwater`, `scenario_assumptions` describing the adverse cases, and `performance_limits` for each case. The SWMM report's `scenarios` maps those names to `model_path` (relative to the report) and `sha256`; the normal model matches the received SWMM input. Scenario models must be distinct and match the reviewed basis digests.

The initial adverse-model adapter requires dynamic-wave routing, an actual reduction of a conduit opening for blockage, and a fixed tailwater above the normal outfall head for backwater. Comment-only changes and mislabeled cases fail. Other blockage mechanisms or time-varying boundaries need a checkable adapter before using this gate; scenario engineering assumptions still need independent review.

Each set of limits supplies `flow_units` and `system_units` matching replay; `nodes` and `links` keyed by all simulated IDs. Node limits are maximum `peak_head`, `flooding_volume`, `surcharge_duration`, plus `outfall_peak_flow` for outfalls. Conduit limits are `peak_depth` and `surcharge_duration`. Head/depth use m (SI) or ft (US), flooding volume m³ or ft³, duration hours, and flow the SWMM flow units. Results use cumulative engine statistics over every routing step rather than report-interval samples. Continuity is checked for all three cases alongside hydraulic acceptance. All values must be finite.

The hydraulic gate checks numerical performance against the reviewed limits, not the engineering suitability of the storms, freeboard, blockage assumptions or outfall boundary. Site catchments, culverts, discharge consents, erosion/scour, cleaning access and transition settlement still need design. Use additional 2D flood assessment where overflow pathways materially affect the case.

## Reproduction and migration

```bash
.venv/bin/python tools/automation/civil_reference.py --run-solvers
.venv/bin/python tools/automation/civil_reference.py --check
.venv/bin/python -m pytest -q engineering/analysis/tests design/component-catalogue/tests tools/automation/tests
```

Replay requires OpenSeesPy, PySWMM and native CalculiX (`ccx`). Check mode validates the small recorded native outputs and source digests without requiring those solvers. Existing pending city manifests gain the new register role during normal civil-gate regeneration. Previously declaration-only submitted reports need the new exchanges and reviews before they can pass. No existing authority decision is manufactured or carried forward as acceptance of a changed evidence package.
