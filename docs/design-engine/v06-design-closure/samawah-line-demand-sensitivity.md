# Samawah line-demand sensitivity

This is a reproducible demonstration of per-line demand propagation into
service, fleet and whole-city costs. It is not a local demand forecast or a
replacement for the published Samawah city study.

## Source-bound run

- Source commit: `ec4711e5f2d9d131c11241e76f6b4d35c542e7ba` (`Keep demand provenance out of line service identities`).
- City input: `dd952bf0526a58894757dee67031894cece6cd4fc45c074d711a8c76188405de`.
- Physical reference: vehicle `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`, body `9489e4f2666fd3b3c73232c86df3f12adf42a5531eb27373834cf3fecb1a3117`.
- Request ID: `f28495c9b0415d0fcd11b8ea6ccaa95d7daca6a4a1e73a7ab2e7f6568a097d9a`.
- Run manifest ID: `3b40f15994f98cb2adcfdc3d373a3c8a5f0d27993e333809869dfa93cb4350fc`.
- Manifest file SHA-256: `b216776c1a3daa0dbbcb8b6dd764d7a7152399d12e25fb0684b54bf5c1f650ad`.
- Independent read-only review SHA-256: `a94086d603c7ff6b8d6aab23c30a67229f2d62b28109292d6c2c5dd4ad933697`.
- Four calculations: **2.72 s wall**, **2.71 s process CPU**, **269,572 KiB maximum RSS**; 60 s CPU, 1 GiB address-space and 120 s wall limits.
- The sealed packet contains 9 payloads and 60 source-file hashes. Captured shell logs and the mutable status file are outside the manifest.
- The independent review checked 80 canonical identities and 204 cost-ledger/route-kilometre arithmetic relations; all survey, achieved-performance and release flags remain false.
- No CAD, FEM, GIS edits or external business transactions ran. Acceptance and release flags remain false.

The 4,000 passengers/hour/direction value is the existing shared outline
control. The 1,200 value is a one-line lower sensitivity, not a measured
Samawah demand. The two lower cases perturb the longest and shortest mapped
lines independently while holding the other four at the 4,000 control. The
scenario-specific demand-source labels are recorded with each result.

## Calculated scenarios

| Scenario | Demand map | Total trainsets | Installed CAPEX, low / base / high | Lifecycle NPV, low / base / high |
| --- | --- | ---: | ---: | ---: |
| Existing scalar control | 4,000 on all five lines | 81 | $315m / $1.141bn / $6.858bn | $629m / $2.258bn / $13.161bn |
| Exact per-line control | 4,000 mapped to each line | 81 | $315m / $1.141bn / $6.858bn | $629m / $2.258bn / $13.161bn |
| Longest-line sensitivity | `line-1`: 1,200; others: 4,000 | 72; `line-1` falls from 28 to 19 | $299m / $1.093bn / $6.651bn | $580m / $2.106bn / $12.538bn |
| Shortest-line sensitivity | `line-5`: 1,200; others: 4,000 | 79; `line-5` falls from 7 to 5 | $312m / $1.131bn / $6.806bn | $621m / $2.230bn / $13.023bn |

The uniform mapped case reproduces the scalar case's complete per-line
evaluation identities, CAPEX and NPV. In each one-line perturbation, only the
changed line's service identity changes; the other four line evaluations are
unchanged. Costs follow the existing provisional assumptions. These results do
not establish that either lower service frequency is suitable for local demand.

The run demonstrates the input and calculation path for line-specific
planning scenarios. It does not provide surveyed demand, revised alignments,
local supplier prices, site-specific rates, or a recalculated 266-city
catalogue. Costs remain provisional Class C estimates with unverified local
rates. Candidate-specific available propulsion force, actual grades,
availability and physical journey performance are not established. The
all-city reconciliation gate remains open.

## Integrity notes

The first attempt completed its calculations but failed post-run manifest
verification because captured stdout changed after the runner sealed its hash
list. Run 02 was superseded after review found that its lower-demand results
carried the baseline demand-source label. Both attempts remain in the private
run archive. Run 03 corrects the packaging and scenario labels. Its manifest
verifies the request, case records, summary, runner and execution record; its
recorded source hashes match the closure checkout.

This is a calculated research sensitivity on the published reference. It does
not change the selected development reference or imply engineering,
manufacturing or operating acceptance.
