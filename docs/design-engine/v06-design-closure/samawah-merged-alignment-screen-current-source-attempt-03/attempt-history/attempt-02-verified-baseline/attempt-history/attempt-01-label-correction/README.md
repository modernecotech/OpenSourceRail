# Samawah stop-preserving route-straightening screens

This packet compares three **unselected planning geometries** against the
source-bound close-stop consolidation alternative and exact package-07 vehicle body. Each route is
simplified only between its existing stop markers; station coordinates and all
stop IDs are held fixed. The active map is unchanged.

## Candidate and source identities

- Merged city input: `7377b6fc01b0caaefd6f656f966a1902fcde5164ea36a43f5d3b97f6663a8ca0`; station-merge candidate/evaluation ancestry: `f3e6532304d2a5f56d44e77ab32b523f4ab3a20850bed633741b68eb33861ea2` / `96759ca63bea3f7dff686565185ddd8261ca02f543293f15d7237e8b735f7dd5`.
- Re-evaluated merged-parent outline candidate/evaluation: `f3e6532304d2a5f56d44e77ab32b523f4ab3a20850bed633741b68eb33861ea2` / `96759ca63bea3f7dff686565185ddd8261ca02f543293f15d7237e8b735f7dd5`.
- Vehicle body: `75075df9247dfff7082a78eadc273d3a99f37e5486450621536c43b1bfa2f797` / `c6c5efe577bd302c507756af53238a8f162c6e2cbeaefd2aa11fecd343b93fb3`.
- Source commit: `dec41531596c8c2794e954c64393f63aecd8c126`.
- Tolerances are maximum sampled deviation from each original stop-to-stop polyline: 25 m, 50 m and 100 m, measured in a local mean-latitude equirectangular projection.

## Recalculated planning comparison

| Map | Route km | 120 m platform-envelope failures | Geometry points | Conditional total trainsets low/base/high | Line-1 runtime request (s) |
|---|---:|---:|---:|---:|---:|
| Merged-stop parent | 57.873 | 0 | 2633 | [42, 59, 87] | 1985.3 |
| 25 m maximum-deviation screen | 54.514 | 0 | 116 (95.6% fewer) | [39, 57, 84] | 1858.8 |
| 50 m maximum-deviation screen | 54.173 | 0 | 77 (97.1% fewer) | [39, 56, 84] | 1852.2 |
| 100 m maximum-deviation screen | 53.963 | 0 | 62 (97.6% fewer) | [39, 56, 84] | 1851.6 |

### Recalculated guideway quantity screen

| Quantity (not priced) | Current map | 25 m | 50 m | 100 m |
|---|---:|---:|---:|---:|
| Reference 20 m beam units | 5,794 | 5,456 | 5,422 | 5,402 |
| Shared bent positions | 2,902 | 2,733 | 2,716 | 2,706 |
| Running rail metres | 231,493 | 218,055 | 216,693 | 215,853 |
| Complete fastening sets | 385,825 | 363,427 | 361,157 | 359,756 |

These reference quantities are not a complete civil takeoff. Foundations,
joints, reinforcement, bearings, station interfaces and construction quantities
remain unverified.

The results are conditional geometry/runtime/fleet calculations. Route and stop
locations remain within the declared mapped corridor band, but the source OSM
coverage is incomplete. No route has been checked against surveyed right-of-way,
land ownership, road crossings, full building records, utilities, ground,
accessibility paths or local construction constraints. The current civil-class
chainages are proportionally transferred to the revised route length only as a
planning assumption and require reassessment; no civil loads are calculated.

No platform-envelope screen failure remains in these alternatives; this still does not establish a buildable station.

The evaluator's 0.4 m/s² acceleration remains a shared study control, not a
selected train capability. Available propulsion force, braking, curvature,
grade, passenger demand, protected schedules and physical service remain
unverified. All fourteen full city cost scopes remain unknown. The body BOM
subtotal is not complete installed corridor cost.

No tolerance is recommended or selected. A larger tolerance permits more
geometric simplification but can cut across mapped obstacles or unsuitable
land. A route geometry pass is not buildability evidence.

## Reproduction

From the repository root:

```sh
tools/automation/osr-python docs/design-engine/v06-design-closure/samawah-merged-alignment-runner-01/run.py --output-dir /tmp/osr-samawah-merged-alignment-screen
```

The packet contains each derived city and outline evaluation, editable GeoJSON,
the exact worker/runner, source checks, resource usage and a recursive SHA-256
manifest. The worker had 60 CPU seconds and 1 GiB address-space limits with a
60-second parent timeout. The source tree remained writable; no OS-level
read-only sandbox is claimed. No GIS, CAD, FEM, ERPNext or network client was
invoked.
