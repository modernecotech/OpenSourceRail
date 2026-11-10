# Samawah close-stop planning alternative — current body source

This is a source-bound planning alternative that merges the line-1 station markers
`line-1-0485-0464-s009300` and `line-1-0487-0466-s009380` at their along-route midpoint. It leaves the
published city map and active reference untouched. It is not an approved station
relocation or an engineering-accepted corridor.

## Exact candidate and source

- City input: `dd952bf0526a58894757dee67031894cece6cd4fc45c074d711a8c76188405de`; body: `75075df9247dfff7082a78eadc273d3a99f37e5486450621536c43b1bfa2f797` / evaluation `c6c5efe577bd302c507756af53238a8f162c6e2cbeaefd2aa11fecd343b93fb3`.
- Current-source baseline city evaluation: `eaa84ee07efbff5763ec11e490142f88d2701c1196d09c63b7bfc9b18ce61a16`.
- Alternative city candidate/evaluation: `f3e6532304d2a5f56d44e77ab32b523f4ab3a20850bed633741b68eb33861ea2` / `96759ca63bea3f7dff686565185ddd8261ca02f543293f15d7237e8b735f7dd5`.
- Source commit: `57a2cfef259e729cf77aaa371f06d55cccbe52c1`.
- Source marker separation: 79.977 m; midpoint chainage: 9339.174 m.

## Recalculated outline quantities

| Measure | Current map | Midpoint alternative |
|---|---:|---:|
| Route length (m) | 57,873.2 | 57,873.2 |
| Station markers | 26 | 25 |
| 120 m platform-envelope screen failures | 1 | 0 |
| Line-1 one-way kinematic request (s) | 2,041.8 | 1,985.3 |
| Counted vehicle BOM/process subtotal (USD; low / base / high; not complete installed city cost) | $29,152,279 / $88,678,591 / $297,135,615 | $29,152,279 / $88,678,591 / $293,759,074 |
| Total trainsets | 42 / 59 / 88 | 42 / 59 / 87 |

Route, station counts and one-way runtime are single values; the displayed
fleet request and body BOM subtotal retain low/base/high cases. The base BOM
subtotal is unchanged; the high case decreases by $3.377 million. That is a
counted vehicle BOM/process subtotal, not complete installed corridor cost.
The body evaluation and all other line geometries are held constant. The merge removes one local 120 m
platform-envelope definition failure in this outline evaluator; this is only a
geometry screen, not a site-approved platform. It does not establish that
hospital-area access, interchange transfer, passenger catchment, station
footprint, utilities or right-of-way are adequate. Available force, braking,
grade, charging, thermal duty and detailed civil loads remain unknown. Fleet and
journey values are conditional calculations, not a protected timetable or
achieved service.
The evaluator uses the shared 0.4 m/s² calculation control; this does not select
that acceleration for an installed train.

No historical total city cost or NPV is transferred. The complete fourteen-scope
city cost, installed CAPEX and lifecycle NPV remain unknown for this alternate
planning identity. This packet ran no CAD, FEM, native GIS, ERPNext or network
client and does not grant physical, engineering, manufacturing or operating
acceptance.

## Reproduction

From the repository root, run the committed source worker with a fresh private
output directory:

```sh
tools/automation/osr-python docs/design-engine/v06-design-closure/samawah-station-consolidation-current-source-runner-01/run.py --output-dir /tmp/osr-samawah-station-consolidation-replay
```

Attempt 01 stopped before worker launch because the wrapper resolved the wrong
repository root; it is preserved in
`attempt-01-launcher-preflight-failure.json`. Attempt 03 records the exact
worker, request, source hashes, resource limits, stdout/stderr and an integrity
manifest that recursively covers the nested input snapshots. Linux child limits
were 60 CPU seconds and 1 GiB address space with a 60 second parent timeout; the
repository source filesystem remained writable and no OS read-only sandbox is
claimed. See [the independent artifact review](independent-review.md); its
22-file audit preceded the final README clarification and review-note addition.
