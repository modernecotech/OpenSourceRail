# Engineering Baseline Assurance

> Deterministic software/toolchain regression evidence only. This is not physical validation, design approval, certification, or authority acceptance.

- Overall result: **PASS**
- Analytical benchmarks: **7**
- Interchange checks: **3**

## Analytical Benchmarks

| ID | Case | Expected | Actual | Tolerance | Result |
|---|---|---:|---:|---:|---|
| `BENCH-STRUCT-001` | cantilever tip displacement | 0.0642857143 m | 0.0642857143 m | 1e-12 | **PASS** |
| `BENCH-THERM-001` | thermal block midpoint | 40 degC | 40 degC | 1e-12 | **PASS** |
| `BENCH-DRAIN-001` | simple drainage mass balance | 33.3333333 m3 | 33.3333333 m3 | 1e-12 | **PASS** |
| `BENCH-ENERGY-001` | one-zone steady-state temperature | 45 degC | 45 degC | 1e-09 | **PASS** |
| `BENCH-ELEC-001` | four-bus terminal voltage | 694.75 V | 694.75 V | 1e-09 | **PASS** |
| `BENCH-EGRESS-001` | corridor evacuation clearance | 85.5384615 s | 85.5384615 s | 1e-09 | **PASS** |
| `BENCH-TIME-001` | one-line timetable traversal | 1050 s | 1050 s | 1e-12 | **PASS** |

## Interchange Drift

| ID | Contract | Result |
|---|---|---|
| `XCHG-ALN-001` | LandXML to OSR-ALN units/CRS/golden round trip | **PASS** |
| `XCHG-IFC-001` | IFC asset identity and finite analysis envelope | **PASS** |
| `XCHG-DUTY-001` | Duty-cycle battery/grid/traffic semantic projection | **PASS** |

The duty fixture is deliberately marked planning-only. Conversion cannot make it acceptance-eligible; measured data still requires controlled instrumentation and source evidence.
