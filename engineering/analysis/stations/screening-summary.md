# Station systems screening

Deterministic design-reference checks for all seven station variants. These are
reproducible engineering screens, not construction release or authority approval.

- Screening execution: **passed**
- Deployment release: **not ready**
- Manifest: `design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json` (`f90e31c14898…`)

## Results

| Domain | Engine | Scope | Result | Remaining gate |
|---|---|---|---|---|
| Structure | OpenSeesPy 3.8.0.0 | 22 m shared canopy truss, gravity + uplift | PASS | Site loads, 3D stability, joints, foundations and code combinations |
| Passenger flow | JuPedSim 1.4.2 | normal, degraded and egress route for 7 variants | PASS | Calibrated demand, conflicts, assisted evacuation and authority criteria |
| Roof drainage | EPA SWMM via PySWMM 2.1.0 | 7 canopy catchments, 75 mm/h input storm | PASS | Local rainfall, survey, tailwater, blockage and exceedance |
| Depot thermal | EnergyPlus | baseline room + separated/cooled controls-room comparison | mitigation-screen-pass | Project climate, supplier losses, detailed HVAC, controls and commissioning |
| Depot fire | FDS | enclosed room + separated/open compound comparison at prescribed 250 kW | mitigation-screen-pass | Supplier fire data, separation/wind cases, suppression and fire-engineer acceptance |

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

The storm supplies 25 mm over 20 minutes. The roof and rational check both use C=1 (no losses).
Each 300 mm branch assumes a 0.4 m fall over 40 m; these are planning levels requiring site survey.
Dynamic-wave routing uses a 1 s hydraulic step and 10 s runoff step. Rainfall, zero infiltration,
runoff volume/peak, conduit peak, continuity and no flooding are separate pass gates.

| Variant | Catchment / branches | SWMM branch / aggregate L/s | Rational aggregate L/s | Rain mm / volume error % | Inlet depth m | Result |
|---|---:|---:|---:|---:|---:|---|
| `halt` | 439.0 m² / 11 | 0.83 / 9.15 | 9.15 | 25.00 / 0.019 | 0.020 | PASS |
| `standard` | 1813.0 m² / 27 | 1.40 / 37.77 | 37.77 | 25.00 / -0.009 | 0.025 | PASS |
| `major` | 2100.8 m² / 32 | 1.37 / 43.77 | 43.77 | 25.00 / -0.007 | 0.025 | PASS |
| `interchange` | 2878.0 m² / 50 | 1.20 / 59.96 | 59.96 | 25.00 / 0.001 | 0.023 | PASS |
| `interchange-elevated` | 3252.0 m² / 52 | 1.30 / 67.75 | 67.75 | 25.00 / -0.004 | 0.024 | PASS |
| `terminal` | 2575.6 m² / 38 | 1.41 / 53.66 | 53.66 | 25.00 / -0.010 | 0.025 | PASS |
| `depot-terminal` | 1640.6 m² / 33 | 1.04 / 34.18 | 34.18 | 25.00 / 0.009 | 0.022 | PASS |

## Depot thermal and fire design response

- EnergyPlus baseline: **52.6 °C** (FAIL) with charger losses indoors and ventilation only. Proposed response: move charger power stages outdoors, retain a 10 kW controls/switchgear load in a cooled room, and install 2 × 30 kW packaged DX units (one duty, one standby). The one-unit-available screen reaches **35.0 °C**, draws at most **13.4 kW** and passes the 40 °C screen.
- FDS enclosed-room baseline: **170.9 °C / 1.0 m visibility** (FAIL). In the proposed physically separated, open-sided charging compound, the same prescribed ~251 kW source gives **21.0 °C / 30.0 m** at the screening devices and passes the provisional 60 °C / 10 m comparison. This is a layout screen, not a fire strategy or battery propagation approval.

## Release boundary

A passing row means only that the deterministic catalogue assumption completed
and met its stated screening threshold. Before procurement or construction, the
deployment team must substitute surveyed/site inputs, local statutory criteria,
supplier performance data, detailed connections and independent competent review.
EnergyPlus/FDS solver completion and a mitigation screen pass confirm only
input execution and the direction of the catalogue design response. The baseline
findings, supplier evidence, project-specific design and independent approvals
remain open release gates.
