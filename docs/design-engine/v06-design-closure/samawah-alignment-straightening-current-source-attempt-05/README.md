# Samawah stop-preserving route-straightening screens

This packet compares three **unselected planning geometries** against the current
Samawah five-line source map and exact package-07 vehicle body. Each route is
simplified only between its existing stop markers; station coordinates and all
stop IDs are held fixed. The active map is unchanged.

## Candidate and source identities

- Current city input: `dd952bf0526a58894757dee67031894cece6cd4fc45c074d711a8c76188405de`; source outline evaluation: `eaa84ee07efbff5763ec11e490142f88d2701c1196d09c63b7bfc9b18ce61a16`.
- Vehicle body: `75075df9247dfff7082a78eadc273d3a99f37e5486450621536c43b1bfa2f797` / `c6c5efe577bd302c507756af53238a8f162c6e2cbeaefd2aa11fecd343b93fb3`.
- Source commit: `1aaacf5dac8bfd57648d47c30eca75b7db6a6514`.
- Tolerances are maximum sampled deviation from each original stop-to-stop polyline: 25 m, 50 m and 100 m, measured in a local mean-latitude equirectangular projection.

## Recalculated planning comparison

| Map | Route km | 120 m platform-envelope failures | Geometry points | Conditional total trainsets low/base/high | Line-1 runtime request (s) |
|---|---:|---:|---:|---:|---:|
| Current source | 57.873 | 1 | 2633 | [42, 59, 88] | 2041.8 |
| 25 m maximum-deviation screen | 54.518 | 1 | 116 (95.6% fewer) | [41, 57, 85] | 1913.0 |
| 50 m maximum-deviation screen | 54.203 | 1 | 78 (97.0% fewer) | [41, 57, 85] | 1907.7 |
| 100 m maximum-deviation screen | 53.993 | 1 | 63 (97.6% fewer) | [41, 57, 85] | 1907.1 |

The results are conditional geometry/runtime/fleet calculations. Route and stop
locations remain within the declared mapped corridor band, but the source OSM
coverage is incomplete. No route has been checked against surveyed right-of-way,
land ownership, road crossings, full building records, utilities, ground,
accessibility paths or local construction constraints. The current civil-class
chainages are proportionally transferred to the revised route length only as a
planning assumption and require reassessment; no civil loads are calculated.

All three alternatives still have one 120 m platform-envelope definition failure. The close line-1 stop pair is 56.552 m apart after simplification; route straightening alone does not resolve it.

The evaluator's 0.4 m/s² acceleration remains a shared study control, not a
selected train capability. Available propulsion force, braking, curvature,
grade, passenger demand, protected schedules and physical service remain
unverified. All fourteen full city cost scopes remain unknown. The body BOM
subtotal is not complete installed corridor cost.

No tolerance is recommended or selected. A larger tolerance permits more
geometric simplification but can cut across mapped obstacles or unsuitable
land. A route geometry pass is not buildability evidence.

## Independent review and run history

The final run was independently checked; see [review findings and isolation limits](independent-review.md). Earlier failed executions and their requests/logs are retained in [attempt history](attempt-history.md).

## Reproduction

From the repository root:

```sh
tools/automation/osr-python docs/design-engine/v06-design-closure/samawah-alignment-straightening-runner-01/run.py --output-dir /tmp/osr-samawah-alignment-screen
```

The packet contains each derived city and outline evaluation, editable GeoJSON,
the exact worker/runner, source checks, resource usage and a recursive SHA-256
manifest. The worker had 60 CPU seconds and 1 GiB address-space limits with a
60-second parent timeout. The source tree remained writable; no OS-level
read-only sandbox is claimed. No GIS, CAD, FEM, ERPNext or network client was
invoked.
