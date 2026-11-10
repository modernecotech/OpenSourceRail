# Independent Baghdad route-study audit — attempt 05

Review completed 10 November 2026. Two read-only reviewers checked the sealed attempt-05 package and corridor-risk calculation. They inspected the archive, identities, route and cost records, the regenerated published Baghdad record, and the 266-city outline replay receipt. No city workflow or physical solver was rerun. The review sessions and numerical execution were not OS-sandboxed; process limits are recorded in the package.

## Package and identity checks

- Attempt archive SHA256: `db6cc59ec2309353cb7e69dae31beded0f878c33dd3ebf623e845581b7c00e71`; source commit `bfa3cbd3abb8336e3c35981cf5991811662b1065`.
- Attempt manifest `fe2717b4d53a406e15f14d595378bee34751f6478ef2fb1d95bd2ace288037cb`; comparison `e66df4f4a78b32a0c98e7d6c24056c9ee0215906d11ac8e53a26c0b703166a2d`; route generation `ec9f4d9ca4eceda0670ecf72757f64ef66667715f15ca48159e4faa03f9959aa`.
- Root manifest identity and all 45 root payload hashes verify. The archive contains 50 files: root manifest, 45 payloads, and four nested study/business manifests. Their identities and payload hashes verify.
- The two studies use the same physical vehicle/body IDs `756a6887…` / `9489e4f2…`. Baseline `27fba762275d0e63d57a7b4bcf6483b7` and revised `c8cbb21fc69edce7d84b89b58cf00093` are exact source/request-matched cached evaluations in attempt 05; both replay-verify. Attempt 04 had freshly calculated and replay-verified the revised city study. Tracked source hashes match the pinned commit, and the revised study's generated-baseline dependencies match the sealed baseline artifacts.
- Attempt 05 uses the project-pinned Shapely 2.2.0 for route-geometry regeneration. Its baseline and revised `alignments.geojson` payload hashes match attempt 04 exactly; the route-generation identity differs because the recorded geometry engine version changed. The deterministic distance-kernel differential check reports 0 m observed error against the declared 1e-7 m tolerance.
- The baseline binding was cross-checked against the companion outline publication and replay records: published manifest `332e3362c179462fd000af41965dfc1b75096ff11d00b7c109521d5c6bd166b5`, 266-city replay run manifest `c2bf7569ac00a14d74fda0117a4474aad1943280e9d3a4d77f65924e8d3ead33`, Baghdad outline evaluation `f1715c1fc8212bb0d107a0e06cf8fbb8fbada7fe7889b5aa8182d8e21c585561`, and selected alignment `e2ed6966088ef33bdfa6086eefcd37ecb7d6becf015784fc442221ea5144a500` (`anchor-preserving-chord-research`). These companion artifacts are separately hash-referenced; the route archive does not contain the full 266-city publication packet.

## Route and service checks

- Thirteen radial alignments change; the closed 26-stop ring on line 9 remains identical. All 157 operational stop IDs and coordinates are conserved. The city source has 159 markers; two existing close-stop pairs are represented as 157 operational station complexes. The route edit adds no further merges.
- Maximum sampled deviation is 18.113–19.960 m using 5 m bidirectional samples, within the declared 20 m route-geometry screen only. This is not a survey, continuous clearance proof or engineering limit.
- Both cases retain 14 lines, the six-car vehicle and common planning inputs: 200 s headway, 20 m/s speed cap, 4,000 pphpd/line, 85% planning occupancy and 99% assumed availability. Dwell is derived and changes on eight lines. The same powered-axle research family is overlaid on each line, but no physically supported available-force map exists.
- Route length changes 494.431060 → 489.415444 km (−5.015616 km, −1.0144%); requested fleet changes 511 → 508. The 392,629.248 m in the corridor-risk calculation is the sum of the 13 revised radial route lengths, not the net route reduction.

## Cost and corridor-risk checks

- Base installed CAPEX changes $8.248074bn → $9.109483bn (+$861.410m); base 30-year NPV changes $15.889554bn → $16.713650bn (+$824.095m).
- Each case has 14 low/base/high lifecycle scopes; totals reproduce NPV and direct capital lines reproduce CAPEX. Base construction NPV rises $890.023m, offset by $65.928m net across the other scopes.
- The independent civil-risk check reproduced all nine ROW/bridge sensitivity cells from the source terms. At 20 m assumed ROW and 5% assumed bridge risk, the new-route quantities are 7,852,584.964 m² ROW and 19,631.462 m bridge-risk route. Incremental base reserve is $704.132m; the prior $340.609m baseline reserve remains, so the revised cumulative risk line is $1.044741bn. Baseline and revised reserve line IDs and low/base/high amounts match the archived study outputs.
- Rates and quantities are Class C planning assumptions, not observed land, utility, crossing, ground or supplier evidence. The sensitivity table varies assumptions; it is not a full city recalculation.

## Disposition and limits

No identity, route, cost or reserve-arithmetic discrepancy was found in attempt 05. Attempt 01 (CPU limit) and attempt 03 (duplicate endpoint) remain preserved as failures. Attempt 02 remains preserved as superseded original-geometry evidence. Attempt 04 is retained as the prior successful route calculation using Shapely 2.1.2. Attempt 05 resolves the route-geometry version mismatch, but both city-study results were cache-reused; a fresh uncached city recalculation under Shapely 2.2.0 remains open.

The attempt is an unselected calculated sensitivity under an unsupported powered-axle propulsion overlay, with unsurveyed routes and demand. It does not demonstrate available propulsion force, a physical journey or engineering acceptance. Physical, engineering, manufacturing, operating and movement-authority flags remain false. The execution recorded 600 CPU seconds, 3 GiB address space, 32 MiB per-file and 256 open-file limits; these do not imply OS sandbox enforcement.
