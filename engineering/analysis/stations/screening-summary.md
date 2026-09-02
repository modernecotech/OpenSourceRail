# Station systems screening

Deterministic design-reference checks for all seven station variants. These are
reproducible engineering screens, not construction release or authority approval.

- Screening execution: **passed**
- Deployment release: **not ready**
- Manifest: `design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json` (`fbb1a453f6f3…`)

## Results

| Domain | Engine | Scope | Result | Remaining gate |
|---|---|---|---|---|
| Structure | OpenSeesPy 3.8.0.0 | 22 m shared canopy truss, gravity + uplift | PASS | Site loads, 3D stability, joints, foundations and code combinations |
| Passenger flow | JuPedSim 1.4.2 | normal, degraded and egress route for 7 variants | PASS | Calibrated demand, conflicts, assisted evacuation and authority criteria |
| Roof drainage | EPA SWMM via PySWMM 2.1.0 | 7 canopy catchments, 75 mm/h input storm | PASS | Local rainfall, survey, tailwater, blockage and exceedance |
| Depot thermal | EnergyPlus | tracked equipment-room design-day deck | input-prepared | Run solver; replace climate, heat loads, envelope and controls |
| Depot fire | FDS | tracked prescribed 250 kW charger-room deck | input-prepared | Credible fire source, refined mesh, tenability/suppression and fire-engineer review |

## Structural cases

| Case | Load kN | Displacement / limit mm | Stress / allowable MPa | Result |
|---|---:|---:|---:|---|
| `gravity` | 205.7 | 18.65 / 91.67 | 62.9 / 213.0 | PASS |
| `wind_uplift` | 224.4 | 20.34 / 91.67 | 68.6 / 213.0 | PASS |

## Passenger-flow cases

| Variant | Normal s | Degraded s | Egress s | Result |
|---|---:|---:|---:|---|
| `halt` | 58.50 | 61.80 | 68.20 | PASS |
| `standard` | 62.75 | 65.15 | 71.35 | PASS |
| `major` | 62.75 | 65.15 | 71.35 | PASS |
| `interchange` | 62.75 | 65.15 | 71.35 | PASS |
| `interchange-elevated` | 62.75 | 65.15 | 71.35 | PASS |
| `terminal` | 62.75 | 65.15 | 71.35 | PASS |
| `depot-terminal` | 62.75 | 65.15 | 71.35 | PASS |

## Drainage cases

| Variant | Catchment / branches | SWMM branch / aggregate L/s | Rational aggregate L/s | Inlet depth m | Result |
|---|---:|---:|---:|---:|---|
| `halt` | 439.0 m² / 11 | 0.16 / 1.73 | 8.69 | 0.067 | PASS |
| `standard` | 1813.0 m² / 27 | 0.21 / 5.62 | 35.88 | 0.078 | PASS |
| `major` | 2100.8 m² / 32 | 0.20 / 6.55 | 41.58 | 0.078 | PASS |
| `interchange` | 2878.0 m² / 50 | 0.19 / 9.67 | 56.96 | 0.075 | PASS |
| `interchange-elevated` | 3252.0 m² / 52 | 0.20 / 10.46 | 64.36 | 0.077 | PASS |
| `terminal` | 2575.6 m² / 38 | 0.21 / 7.95 | 50.98 | 0.079 | PASS |
| `depot-terminal` | 1640.6 m² / 33 | 0.18 / 5.83 | 32.47 | 0.071 | PASS |

## Release boundary

A passing row means only that the deterministic catalogue assumption completed
and met its stated screening threshold. Before procurement or construction, the
deployment team must substitute surveyed/site inputs, local statutory criteria,
supplier performance data, detailed connections and independent competent review.
The EnergyPlus and FDS decks are intentionally reported as pending until those
solvers and project inputs produce reviewed results.
